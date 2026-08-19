"""Layered evidence corpus for the proposer (AHE "experience observability").

What v1 gave the proposer (``reflect.py:69-101``) was a 2500-character list of
tool names with truncated arguments::

    R: /geos_lib/inputFiles/poromechanics/...
    B: grep -rn "ThermoPoro" /geos_lib/src | head -40
    GR: SinglePhasePoromechanics

No observations, no errors, no diffs, no validator output, no failure
classification, no per-section scores -- and, because the round was never
scored before reflection, no reward either (every task rendered
``treesim N/A`` and the header read ``mean treesim 0.0000``).

Everything needed to fix this already exists in the repo. ``scripts/bottleneck/
extract.py`` computes per-section TreeSim, the k worst failing subtrees,
missing/extra element types, mined trajectory features, and a tail excerpt;
``scripts/bottleneck/llm_per_task.py`` assigns the failure category. This module
does not reimplement any of that -- it wires it into four layers the proposer
can consume top-down:

  L0  aggregate   -- cell mean, sigma, zero-rate, efficiency vs parent
  L1  per-task    -- score, section scores, status, delta vs parent
  L2  failure     -- worst subtrees, missing/extra element types, category
  L3  drill-down  -- tail excerpt, verbatim validator output, hook events

L3 is served **on request** for a named (task, run) rather than dumped, which is
what keeps the proposer prompt bounded without reintroducing a character cap.
"""

from __future__ import annotations

import importlib.util
import json
import statistics
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Sequence

REPO_ROOT = Path(__file__).resolve().parents[2]

#: Failure categories used by the bottleneck classifier.
FAILURE_CATEGORIES: tuple[str, ...] = (
    "missing_block", "extra_block", "hallucinated_extras", "structural_mismatch",
    "bad_attribute_value", "partial_implementation", "wrong_constitutive", "no_failure",
)


def _load_extract_module() -> Any | None:
    """Import ``scripts/bottleneck/extract.py`` without making it a package.

    It is a standalone CLI script, not an importable module; loading it by path
    keeps this a wiring job rather than a refactor of working code.
    """
    path = REPO_ROOT / "scripts" / "bottleneck" / "extract.py"
    if not path.exists():
        return None
    spec = importlib.util.spec_from_file_location("_bottleneck_extract", path)
    if spec is None or spec.loader is None:
        return None
    mod = importlib.util.module_from_spec(spec)
    sys.modules.setdefault("_bottleneck_extract", mod)
    try:
        spec.loader.exec_module(mod)
    except Exception:
        return None
    return mod


@dataclass
class TaskEvidence:
    """L1 + L2 for one (task, run)."""

    task: str
    run: str
    treesim: float | None = None
    status: str | None = None
    section_scores: dict[str, float] = field(default_factory=dict)
    worst_subtrees: list[dict[str, Any]] = field(default_factory=list)
    missing_element_types: list[str] = field(default_factory=list)
    extra_element_types: list[str] = field(default_factory=list)
    category: str | None = None
    n_extra_top: int = 0
    tool_calls: int | None = None
    wall_seconds: float | None = None
    validator_blocks: int = 0
    error: str | None = None
    _raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @property
    def is_zero(self) -> bool:
        """A failures-as-zero termination -- the thing the adapters exist to prevent."""
        return self.treesim is not None and self.treesim <= 1e-9

    def render_l1(self) -> str:
        ts = f"{self.treesim:.3f}" if self.treesim is not None else "N/A"
        return f"{self.task}: treesim={ts} status={self.status or '?'}"

    def render_l2(self, max_subtrees: int = 5) -> str:
        lines = [self.render_l1()]
        if self.category:
            lines.append(f"  category: {self.category}")
        if self.section_scores:
            worst = sorted(self.section_scores.items(), key=lambda kv: kv[1])[:5]
            lines.append(
                "  weakest sections: "
                + ", ".join(f"{k}={v:.2f}" for k, v in worst)
            )
        if self.missing_element_types:
            lines.append(
                f"  missing element types: {', '.join(self.missing_element_types[:10])}"
            )
        if self.extra_element_types:
            lines.append(
                f"  extra element types: {', '.join(self.extra_element_types[:10])}"
            )
        for st in self.worst_subtrees[:max_subtrees]:
            path = st.get("path") or st.get("tag") or "?"
            score = st.get("score")
            score_s = f"{score:.2f}" if isinstance(score, (int, float)) else "?"
            lines.append(f"  weak subtree {path} score={score_s}")
        return "\n".join(lines)


@dataclass
class RoundEvidence:
    """The full corpus for one candidate evaluation."""

    candidate_id: str
    tasks: list[TaskEvidence] = field(default_factory=list)
    parent_scores: dict[str, float] = field(default_factory=dict)

    # -- L0 ---------------------------------------------------------------
    @property
    def scores(self) -> dict[str, float]:
        return {t.task: t.treesim for t in self.tasks if t.treesim is not None}

    @property
    def mean(self) -> float:
        vals = list(self.scores.values())
        return statistics.mean(vals) if vals else 0.0

    @property
    def stdev(self) -> float:
        vals = list(self.scores.values())
        return statistics.stdev(vals) if len(vals) > 1 else 0.0

    @property
    def zero_rate(self) -> float:
        if not self.tasks:
            return 0.0
        return sum(1 for t in self.tasks if t.is_zero) / len(self.tasks)

    @property
    def total_tool_calls(self) -> int:
        return sum(t.tool_calls or 0 for t in self.tasks)

    def deltas(self) -> dict[str, float]:
        """Per-task delta vs the parent candidate. Empty if no parent scores."""
        return {
            task: score - self.parent_scores[task]
            for task, score in self.scores.items()
            if task in self.parent_scores
        }

    def category_counts(self) -> dict[str, int]:
        counts = {c: 0 for c in FAILURE_CATEGORIES}
        for t in self.tasks:
            if t.category in counts:
                counts[t.category] += 1
        return {k: v for k, v in counts.items() if v}

    # -- rendering --------------------------------------------------------
    def render_l0(self) -> str:
        lines = [
            f"candidate {self.candidate_id}: n={len(self.tasks)} "
            f"mean={self.mean:.4f} sd={self.stdev:.4f} "
            f"zero_rate={self.zero_rate:.2f} tool_calls={self.total_tool_calls}"
        ]
        d = self.deltas()
        if d:
            regress = sorted(d.items(), key=lambda kv: kv[1])[:3]
            lines.append(
                "  vs parent: mean delta="
                f"{statistics.mean(d.values()):+.4f}, worst per-task="
                + ", ".join(f"{k}{v:+.3f}" for k, v in regress)
            )
        cc = self.category_counts()
        if cc:
            lines.append(
                "  failure categories: "
                + ", ".join(f"{k}={v}" for k, v in sorted(cc.items()))
            )
        return "\n".join(lines)

    def render(self, level: int = 2, max_tasks: int | None = None) -> str:
        """Render the corpus at ``level`` (0..2). L3 is fetched per task."""
        parts = [self.render_l0()]
        if level >= 1:
            ordered = sorted(self.tasks, key=lambda t: (t.treesim is None, t.treesim or 0))
            if max_tasks:
                ordered = ordered[:max_tasks]
            for t in ordered:
                parts.append(t.render_l2() if level >= 2 else t.render_l1())
        return "\n".join(parts)

    def drill_down(self, task: str, max_chars: int = 6000) -> str:
        """L3 for one task: tail excerpt + verbatim validator output.

        Deliberately not part of :meth:`render` -- the proposer asks for this
        by name, which is what lets us drop v1's 2500-char global cap without
        the prompt exploding.
        """
        te = next((t for t in self.tasks if t.task == task), None)
        if te is None:
            return f"(no evidence for task {task!r})"
        raw = te._raw
        parts = [f"=== L3 drill-down: {task} ===", te.render_l2(max_subtrees=8)]
        excerpt = raw.get("trajectory_excerpt")
        if excerpt:
            parts.append("--- last turns ---")
            parts.append(json.dumps(excerpt, indent=1, default=str))
        traj = raw.get("trajectory")
        if traj:
            parts.append("--- mined trajectory features ---")
            parts.append(json.dumps(traj, indent=1, default=str))
        hook = raw.get("hook_events")
        if hook:
            parts.append("--- validator / stop-hook events (verbatim) ---")
            parts.append(json.dumps(hook, indent=1, default=str))
        out = "\n".join(parts)
        return out[:max_chars]


# ---------------------------------------------------------------------------
# builders
# ---------------------------------------------------------------------------


def _read_hook_events(run_dir: Path, limit: int = 20) -> list[dict[str, Any]]:
    """Read the stop-hook's own JSONL event log if the run produced one.

    This is where ``geosx --validate-input`` output lands, including the inline
    valid-attribute table -- the single richest signal the harness produces and
    the one v1 threw away entirely.
    """
    events: list[dict[str, Any]] = []
    for name in ("hook_events.jsonl", ".verify_events.jsonl", "verify_events.jsonl"):
        p = run_dir / name
        if not p.exists():
            continue
        for line in p.read_text(errors="replace").splitlines()[-limit:]:
            try:
                events.append(json.loads(line))
            except Exception:
                continue
        break
    return events


def build_task_evidence(
    task: str,
    *,
    traj_root: Path,
    eval_root: Path,
    agent: str,
    run: str,
    categories: dict[str, str] | None = None,
) -> TaskEvidence:
    """Build L1+L2 for one task, delegating to ``bottleneck/extract.py``."""
    extract = _load_extract_module()
    if extract is None:
        return TaskEvidence(task=task, run=run, error="bottleneck/extract.py unavailable")

    diag = extract.diagnostic_for_task(
        Path(traj_root), Path(eval_root), agent, run, task
    )
    if diag is None:
        return TaskEvidence(task=task, run=run, error="no diagnostic produced")
    if diag.get("error"):
        return TaskEvidence(task=task, run=run, error=str(diag["error"]), _raw=diag)

    traj = diag.get("trajectory") or {}
    run_dir = Path(traj_root) / agent / run / task
    hook_events = _read_hook_events(run_dir)
    diag["hook_events"] = hook_events

    return TaskEvidence(
        task=task,
        run=run,
        treesim=diag.get("treesim"),
        status=diag.get("status"),
        section_scores=diag.get("section_scores") or {},
        worst_subtrees=diag.get("worst_subtrees") or [],
        missing_element_types=diag.get("missing_element_types") or [],
        extra_element_types=diag.get("extra_element_types") or [],
        category=(categories or {}).get(task),
        n_extra_top=int(diag.get("gen_n_extra_top") or 0),
        tool_calls=traj.get("n_tool_calls") or traj.get("tool_calls"),
        wall_seconds=traj.get("wall_seconds"),
        validator_blocks=sum(
            1 for e in hook_events if str(e.get("decision", "")).lower() == "block"
        ),
        _raw=diag,
    )


def build_round_evidence(
    candidate_id: str,
    tasks: Sequence[str],
    *,
    traj_root: Path,
    eval_root: Path,
    agent: str,
    run: str,
    parent_scores: dict[str, float] | None = None,
    categories: dict[str, str] | None = None,
) -> RoundEvidence:
    return RoundEvidence(
        candidate_id=candidate_id,
        tasks=[
            build_task_evidence(
                t,
                traj_root=traj_root,
                eval_root=eval_root,
                agent=agent,
                run=run,
                categories=categories,
            )
            for t in tasks
        ],
        parent_scores=dict(parent_scores or {}),
    )


def load_categories(bottleneck_out_dir: Path) -> dict[str, str]:
    """Load per-task failure categories from a bottleneck classifier run."""
    out: dict[str, str] = {}
    d = Path(bottleneck_out_dir)
    if not d.is_dir():
        return out
    for p in sorted(d.glob("*.json")):
        try:
            data = json.loads(p.read_text())
        except Exception:
            continue
        rows: Iterable[dict[str, Any]]
        rows = data if isinstance(data, list) else [data]
        for row in rows:
            if isinstance(row, dict) and row.get("task") and row.get("category"):
                out[str(row["task"])] = str(row["category"])
    return out
