"""Contamination gate for candidate adapters.

v1's gate was one line (``reflect.py:248-249``)::

    re.sub(r"\\b([a-z0-9_][a-z0-9_\\-]*\\.xml)\\b", "<file>", body, flags=re.IGNORECASE)

and ``scripts/memory/hygiene_audit.py:41`` uses the identical ``.xml``-only
pattern, so the durable audit gate has the same blind spot. Three holes, one of
which fired in the shipped artifact:

1. ``.geos`` is not matched. ``plugin_evolving/v3`` -- the adapter the paper
   reports as SE -- contains ``tables/time.geos``, ``tables/radialStress.geos``
   and ``tables/axialStrain.geos``, ground-truth dependency filenames mined
   from trajectories, in three separate files.
2. Directory components survive: ``poromechanics/Foo_base.xml`` becomes
   ``poromechanics/<file>``, preserving the physics-family directory name.
3. Content leaks are not addressed at all -- it is a filename filter.
   ``plugin_evolving/v4/memory/cheatsheet.md`` is what that looks like when it
   goes wrong: a task-name -> canonical-XML table covering all 17 validation
   tasks (that file did not come through this gate, but nothing here would have
   caught its *content* if it had).

This module is a superset. It is **blocking, not advisory**, and it runs before
any rollout is spent on a candidate.
"""

from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Sequence

#: Simulator-relevant extensions whose basenames must never appear in an
#: adapter. ``.geos`` is the one v1 missed.
LEAKY_EXTENSIONS: tuple[str, ...] = (
    "xml", "geos", "msh", "vtk", "vtu", "rst", "yaml", "yml", "hdf5", "csv",
)

FILENAME_RE = re.compile(
    r"\b([A-Za-z0-9_][A-Za-z0-9_.\-]*\.(?:" + "|".join(LEAKY_EXTENSIONS) + r"))\b"
)

#: Numeric literal, including LaTeX-ish and unicode-superscript forms.
_NUM_RE = re.compile(
    r"""(?<![A-Za-z0-9_.])
        [-+]?
        (?:\d+\.?\d*|\.\d+)
        (?:\s*(?:[eEdD]\s*[-+]?\d+|
                \\times\s*10\s*\^?\s*\{?\s*[-+]?\d+\s*\}?|
                x\s*10\s*\^\s*[-+]?\d+))?
    """,
    re.VERBOSE,
)

_SUPERSCRIPTS = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁺", "0123456789-+")

#: Numbers this common carry no information about a specific ground truth.
_TRIVIAL_NUMERICS: frozenset[str] = frozenset(
    {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "100", "1000",
     "0.5", "0.1", "0.01", "-1", "0.0", "1.0", "2.0", "3.0"}
)

DEFAULT_MIN_NGRAM = 8


class HygieneError(ValueError):
    """Raised when a candidate fails the contamination gate."""


@dataclass
class Finding:
    """One hygiene violation."""

    rule: str
    path: str
    detail: str
    severity: str = "block"

    def __str__(self) -> str:
        return f"[{self.severity}] {self.rule} in {self.path}: {self.detail}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "rule": self.rule,
            "path": self.path,
            "detail": self.detail,
            "severity": self.severity,
        }


@dataclass
class HygieneReport:
    findings: list[Finding] = field(default_factory=list)
    checked_paths: list[str] = field(default_factory=list)
    rules_run: list[str] = field(default_factory=list)

    @property
    def blocked(self) -> bool:
        return any(f.severity == "block" for f in self.findings)

    @property
    def passed(self) -> bool:
        return not self.blocked

    def raise_if_blocked(self) -> None:
        if self.blocked:
            blocks = [f for f in self.findings if f.severity == "block"]
            raise HygieneError(
                f"{len(blocks)} blocking hygiene finding(s):\n  "
                + "\n  ".join(str(f) for f in blocks)
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "passed": self.passed,
            "n_blocking": sum(1 for f in self.findings if f.severity == "block"),
            "findings": [f.to_dict() for f in self.findings],
            "checked_paths": self.checked_paths,
            "rules_run": self.rules_run,
        }


# ---------------------------------------------------------------------------
# corpus
# ---------------------------------------------------------------------------


@dataclass
class GroundTruthCorpus:
    """Everything a candidate must not reveal.

    Built once per search run from the ground-truth tree, then reused for every
    candidate. ``blocked_basenames`` comes from
    ``runner.contamination.get_blocked_files_for_task`` where available so the
    two gates cannot drift apart.
    """

    blocked_basenames: set[str] = field(default_factory=set)
    blocked_path_parts: set[str] = field(default_factory=set)
    deck_texts: dict[str, str] = field(default_factory=dict)
    numeric_literals: set[str] = field(default_factory=set)
    task_ids: set[str] = field(default_factory=set)

    @classmethod
    def from_ground_truth_dir(
        cls,
        gt_dir: Path,
        *,
        tasks: Sequence[str] | None = None,
        collect_numerics: bool = True,
    ) -> "GroundTruthCorpus":
        gt_dir = Path(gt_dir)
        corpus = cls()
        task_dirs = [gt_dir / t for t in tasks] if tasks else sorted(
            p for p in gt_dir.iterdir() if p.is_dir()
        )
        for td in task_dirs:
            if not td.is_dir():
                continue
            corpus.task_ids.add(td.name)
            for f in td.rglob("*"):
                if not f.is_file():
                    continue
                corpus.blocked_basenames.add(f.name.lower())
                for part in f.relative_to(gt_dir).parts[:-1]:
                    if len(part) > 4:
                        corpus.blocked_path_parts.add(part.lower())
                if f.suffix.lower() in (".xml", ".geos"):
                    try:
                        text = f.read_text(errors="replace")
                    except OSError:
                        continue
                    key = f.relative_to(gt_dir).as_posix()
                    corpus.deck_texts[key] = text
                    if collect_numerics:
                        corpus.numeric_literals |= canonical_numerics(text)
        return corpus

    def extend_from_contamination(
        self, tasks: Iterable[str], ground_truth_dir: Path, **kw: Any
    ) -> "GroundTruthCorpus":
        """Fold in ``runner.contamination``'s blocklist, including variants."""
        try:
            from runner.contamination import get_blocked_files_for_task
        except Exception:  # pragma: no cover - runner import is environment-dependent
            return self
        for task in tasks:
            try:
                blocked = get_blocked_files_for_task(task, ground_truth_dir, **kw)
            except Exception:
                continue
            self.blocked_basenames |= {
                b.lower() for b in blocked.get("blocked_xml_filenames", [])
            }
            for rst in blocked.get("blocked_rst_paths", []):
                self.blocked_basenames.add(Path(rst).name.lower())
                for part in Path(rst).parts[:-1]:
                    if len(part) > 4:
                        self.blocked_path_parts.add(part.lower())
        return self


def canonicalize_number(raw: str) -> str | None:
    """Canonicalize a numeric token so ``1.0e-4``, ``1e-4`` and ``$1.0\\times10^{-4}$`` agree."""
    s = raw.translate(_SUPERSCRIPTS).strip().strip("$")
    s = re.sub(r"\\times\s*10\s*\^?\s*\{?\s*([-+]?\d+)\s*\}?", r"e\1", s)
    s = re.sub(r"x\s*10\s*\^\s*([-+]?\d+)", r"e\1", s)
    s = s.replace("D", "e").replace("d", "e").replace("E", "e")
    s = re.sub(r"\s+", "", s)
    try:
        val = float(s)
    except ValueError:
        return None
    if val == 0:
        return "0"
    return f"{val:.6g}"


def canonical_numerics(text: str) -> set[str]:
    """All canonicalized, non-trivial numeric literals in ``text``."""
    out: set[str] = set()
    for m in _NUM_RE.finditer(text):
        raw = m.group(0)
        if raw.strip() in _TRIVIAL_NUMERICS:
            continue
        canon = canonicalize_number(raw)
        if canon is None or canon in _TRIVIAL_NUMERICS:
            continue
        # Bare small integers carry no ground-truth signal.
        if re.fullmatch(r"-?\d{1,3}", canon):
            continue
        out.add(canon)
    return out


def _normalize_for_ngrams(text: str) -> list[str]:
    text = unicodedata.normalize("NFKC", text).lower()
    return re.findall(r"[a-z0-9_]+", text)


def ngram_overlap(candidate_text: str, reference: str, n: int = DEFAULT_MIN_NGRAM) -> int:
    """Number of distinct ``n``-grams shared between candidate and reference."""
    a = _normalize_for_ngrams(candidate_text)
    b = _normalize_for_ngrams(reference)
    if len(a) < n or len(b) < n:
        return 0
    a_grams = {tuple(a[i : i + n]) for i in range(len(a) - n + 1)}
    b_grams = {tuple(b[i : i + n]) for i in range(len(b) - n + 1)}
    return len(a_grams & b_grams)


# ---------------------------------------------------------------------------
# rules
# ---------------------------------------------------------------------------


def _rule_filenames(path: str, text: str, corpus: GroundTruthCorpus) -> list[Finding]:
    """Rule 1: no simulator-artifact filenames at all.

    Superset of v1: every extension in :data:`LEAKY_EXTENSIONS`, not just
    ``.xml``. This is the rule that catches ``tables/time.geos``.
    """
    findings = []
    for m in FILENAME_RE.finditer(text):
        name = m.group(1)
        sev = "block" if name.lower() in corpus.blocked_basenames else "warn"
        findings.append(
            Finding("filename", path, f"references artifact filename {name!r}", sev)
        )
    return findings


def _rule_path_parts(path: str, text: str, corpus: GroundTruthCorpus) -> list[Finding]:
    """Rule 2: no ground-truth directory components.

    v1 stripped the basename and left ``poromechanics/<file>`` behind.
    """
    findings = []
    lowered = text.lower()
    for part in sorted(corpus.blocked_path_parts):
        if re.search(rf"\b{re.escape(part)}\b", lowered):
            findings.append(
                Finding("path_part", path, f"references GT path component {part!r}", "warn")
            )
    return findings


def _rule_task_ids(path: str, text: str, corpus: GroundTruthCorpus) -> list[Finding]:
    """Rule 2b: no task identifiers.

    A task-name-keyed lookup table is the highest-value leak an adapter can
    carry, because it converts the agent's search problem into a table lookup.
    Two or more task ids in one file is the ``plugin_evolving/v4`` signature.
    """
    hits = sorted(t for t in corpus.task_ids if re.search(rf"\b{re.escape(t)}\b", text))
    if len(hits) >= 2:
        return [
            Finding(
                "task_id_table",
                path,
                f"names {len(hits)} task ids ({', '.join(hits[:4])}...): "
                "looks like a task->answer lookup table",
                "block",
            )
        ]
    return [Finding("task_id", path, f"names task id {t!r}", "block") for t in hits]


def _rule_blocklist(path: str, text: str, corpus: GroundTruthCorpus) -> list[Finding]:
    """Rule 3: substring match against the runner's own blocklist."""
    lowered = text.lower()
    return [
        Finding("blocklist", path, f"contains blocked basename {b!r}", "block")
        for b in sorted(corpus.blocked_basenames)
        if b and b in lowered
    ]


def _rule_content(
    path: str, text: str, corpus: GroundTruthCorpus, *, n: int, threshold: int
) -> list[Finding]:
    """Rule 4: n-gram overlap with any ground-truth deck.

    The capability v1 lacked entirely -- it could only see filenames.
    """
    findings = []
    for key, ref in corpus.deck_texts.items():
        shared = ngram_overlap(text, ref, n=n)
        if shared >= threshold:
            findings.append(
                Finding(
                    "content_overlap",
                    path,
                    f"shares {shared} distinct {n}-grams with GT deck {key}",
                    "block",
                )
            )
    return findings


def _rule_numerics(
    path: str, text: str, corpus: GroundTruthCorpus, *, threshold: int
) -> list[Finding]:
    """Rule 5: canonicalized ground-truth numeric literals.

    Catches the ``bad_attribute_value``-shaped leak: an adapter that memorises
    "use 1e-12 for permeability on this task family" is teaching the answer, not
    the interface. Canonicalization follows the LaTeX-aware scheme the spec
    relaxation hygiene check uses.
    """
    found = canonical_numerics(text) & corpus.numeric_literals
    if len(found) >= threshold:
        sample = ", ".join(sorted(found)[:6])
        return [
            Finding(
                "numeric_leak",
                path,
                f"{len(found)} GT numeric literals present ({sample}...)",
                "block",
            )
        ]
    return []


# ---------------------------------------------------------------------------
# entry point
# ---------------------------------------------------------------------------


def check_texts(
    texts: dict[str, str],
    corpus: GroundTruthCorpus,
    *,
    ngram_n: int = DEFAULT_MIN_NGRAM,
    ngram_threshold: int = 3,
    numeric_threshold: int = 3,
) -> HygieneReport:
    """Run every rule over ``texts`` (adapter-relative path -> content)."""
    report = HygieneReport(
        rules_run=[
            "filename", "path_part", "task_id", "blocklist",
            "content_overlap", "numeric_leak",
        ]
    )
    for path in sorted(texts):
        text = texts[path]
        report.checked_paths.append(path)
        report.findings += _rule_filenames(path, text, corpus)
        report.findings += _rule_path_parts(path, text, corpus)
        report.findings += _rule_task_ids(path, text, corpus)
        report.findings += _rule_blocklist(path, text, corpus)
        report.findings += _rule_content(
            path, text, corpus, n=ngram_n, threshold=ngram_threshold
        )
        report.findings += _rule_numerics(
            path, text, corpus, threshold=numeric_threshold
        )
    return report


def check_candidate(candidate: Any, corpus: GroundTruthCorpus, **kw: Any) -> HygieneReport:
    """Convenience wrapper for a :class:`~evolve.candidate.Candidate`."""
    return check_texts(dict(candidate.files), corpus, **kw)


def audit_dir(adapter_dir: Path, corpus: GroundTruthCorpus, **kw: Any) -> HygieneReport:
    """Audit an on-disk adapter (used to retro-audit ``plugin_evolving/v*``)."""
    adapter_dir = Path(adapter_dir)
    texts: dict[str, str] = {}
    for f in sorted(adapter_dir.rglob("*")):
        if not f.is_file() or f.suffix.lower() not in (".md", ".yaml", ".yml", ".toml"):
            continue
        rel = f.relative_to(adapter_dir).as_posix()
        if rel.startswith(("hooks/", "scripts/", ".claude-plugin/")):
            continue
        texts[rel] = f.read_text(errors="replace")
    return check_texts(texts, corpus, **kw)


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Audit an adapter for GT leakage.")
    ap.add_argument("--adapter-dir", required=True, type=Path)
    ap.add_argument("--ground-truth-dir", required=True, type=Path)
    ap.add_argument("--out", type=Path, help="write the JSON report here")
    ap.add_argument("--warn-ok", action="store_true", help="exit 0 on warnings")
    args = ap.parse_args()

    corpus = GroundTruthCorpus.from_ground_truth_dir(args.ground_truth_dir)
    report = audit_dir(args.adapter_dir, corpus)
    payload = report.to_dict()
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(payload, indent=2))
    for f in report.findings:
        print(f)
    print(
        f"\n{len(report.checked_paths)} file(s) checked, "
        f"{payload['n_blocking']} blocking finding(s)"
    )
    return 1 if report.blocked else 0


if __name__ == "__main__":
    raise SystemExit(main())
