"""Check plugins: the one place the search loop is allowed to author code.

Rationale for fencing this hard: arXiv:2603.05578 (Tool-Genesis) finds that
autonomous one-shot tool creation fails and that interface errors compound.
So a candidate may not rewrite ``hooks/verify_outputs.py``; it may only add a
``check`` behind a fixed interface, with a mandatory sibling test:

    hooks/checks/<name>.py         def check(deck: Deck, ctx: CheckContext) -> list[Finding]
    hooks/checks/<name>_test.py    REQUIRED -- candidate rejected without it

A plugin that has no test, fails its own test, raises, or exceeds its time
budget is rejected **before any rollout is spent**. Free rejections are where
most bad proposals should die.

Built-ins live here as the reference implementations the proposer sees.
``constraints`` is the interesting one: it is the executable half of the
negative-constraint artifact class (``memory/constraints.yaml``), whose other
half is prose in the cheatsheet. The paper's recommendation (iii) is that
cheatsheets enumerating "for physics X use solver Y" must be paired with
explicit negative constraints ("exactly k Constitutive children, no more"),
because without them adapters trade ``missing_block`` for ``extra_block`` and
``hallucinated_extras``. Stating a constraint in prose and enforcing the same
constraint at the stop interface is the whole point: arXiv:2605.30621 finds
that weak-tier models fail by activating a harness artifact and then not
following it.
"""

from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Sequence

#: Per-plugin wall-clock budget. A check that cannot answer in five seconds is
#: not a check, it is a second agent.
CHECK_TIMEOUT_S = 5.0


@dataclass(frozen=True)
class Finding:
    """One problem with a deck, as reported to the agent by the stop hook."""

    check: str
    severity: str  # "error" | "warn"
    message: str
    location: str = ""

    def render(self) -> str:
        where = f" at {self.location}" if self.location else ""
        return f"[{self.severity}] {self.check}{where}: {self.message}"


@dataclass
class Deck:
    """The agent's workspace output, parsed once and shared by every check."""

    files: dict[str, str] = field(default_factory=dict)
    roots: dict[str, ET.Element] = field(default_factory=dict)
    parse_errors: dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_dir(cls, inputs_dir: Path) -> "Deck":
        deck = cls()
        inputs_dir = Path(inputs_dir)
        if not inputs_dir.is_dir():
            return deck
        for p in sorted(inputs_dir.glob("*.xml")):
            text = p.read_text(errors="replace")
            deck.files[p.name] = text
            try:
                deck.roots[p.name] = ET.fromstring(text)
            except ET.ParseError as exc:
                deck.parse_errors[p.name] = str(exc)
        return deck

    def iter_elements(self, tag: str):
        for name, root in self.roots.items():
            if root.tag == tag:
                yield name, root
            for el in root.iter(tag):
                yield name, el

    def count(self, parent_tag: str, child_tag: str | None = None) -> int:
        """Count ``parent_tag`` elements, or its ``child_tag`` children."""
        total = 0
        for _, el in self.iter_elements(parent_tag):
            total += len(list(el)) if child_tag == "*" else (
                sum(1 for c in el if c.tag == child_tag) if child_tag else 1
            )
        return total

    def names_of(self, tag: str) -> set[str]:
        out: set[str] = set()
        for _, el in self.iter_elements(tag):
            n = el.get("name")
            if n:
                out.add(n)
        return out


@dataclass
class CheckContext:
    """Everything a check may read besides the deck itself."""

    inputs_dir: Path
    constraints: list[dict[str, Any]] = field(default_factory=list)
    geosx_executable: str | None = None
    schema_path: Path | None = None
    extra: dict[str, Any] = field(default_factory=dict)


CheckFn = Callable[[Deck, CheckContext], Sequence[Finding]]


# ---------------------------------------------------------------------------
# built-in checks
# ---------------------------------------------------------------------------

#: Top-level GEOS sections a complete deck is expected to define.
REQUIRED_SECTIONS: tuple[str, ...] = (
    "Solvers", "Mesh", "Events", "NumericalMethods",
    "ElementRegions", "Constitutive",
)


def check_parse(deck: Deck, ctx: CheckContext) -> list[Finding]:
    """Cheapest gate: something exists and it parses."""
    if not deck.files:
        return [Finding("parse", "error", "no .xml files in the workspace inputs dir")]
    return [
        Finding("parse", "error", f"XML does not parse: {err}", location=name)
        for name, err in sorted(deck.parse_errors.items())
    ]


def check_required_sections(deck: Deck, ctx: CheckContext) -> list[Finding]:
    """Coverage gate. Targets ``missing_block``, the category adapters do fix.

    The OpenFOAM transfer suggests this generalises to any end-of-turn
    completeness check, not just XSD validation -- so it is deliberately
    schema-free.
    """
    present = {root.tag for root in deck.roots.values()}
    for root in deck.roots.values():
        present |= {c.tag for c in root if isinstance(c.tag, str)}
    missing = [s for s in REQUIRED_SECTIONS if s not in present]
    return [
        Finding(
            "required_sections",
            "error",
            f"deck defines no <{s}> section",
        )
        for s in missing
    ]


def check_cross_section_refs(deck: Deck, ctx: CheckContext) -> list[Finding]:
    """``<ElementRegion materialList>`` entries must name real ``<Constitutive>`` blocks.

    Kept as a built-in even though ``geosx --validate-input`` now catches the
    load-time cases, because it is (a) two orders of magnitude cheaper than
    booting GEOS and (b) still catches the class the loader resolves lazily and
    therefore misses (see docs/GEOSX_VALIDATE.md).
    """
    constitutive_names: set[str] = set()
    for _, el in deck.iter_elements("Constitutive"):
        constitutive_names |= {c.get("name") for c in el if c.get("name")}
    if not constitutive_names:
        return []
    findings = []
    for _, regions in deck.iter_elements("ElementRegions"):
        for region in regions:
            raw = region.get("materialList")
            if not raw:
                continue
            for mat in re.split(r"[\s,{}]+", raw):
                if mat and mat not in constitutive_names:
                    findings.append(
                        Finding(
                            "cross_section_refs",
                            "error",
                            f"materialList names {mat!r}, which is not a "
                            f"<Constitutive> child. Defined: "
                            f"{sorted(constitutive_names)}",
                            location=region.get("name") or region.tag,
                        )
                    )
    return findings


def check_constraints(deck: Deck, ctx: CheckContext) -> list[Finding]:
    """Enforce the negative constraints declared in ``memory/constraints.yaml``.

    Supported forms (deliberately few -- each must be checkable and each must
    have a natural prose rendering, since the same entry is also emitted into
    the cheatsheet)::

        - {kind: count, parent: Constitutive, child: "*", max: 3}
        - {kind: forbid_attr, tag: SolidMechanicsLagrangianFEM, attr: gravityVector}
        - {kind: require_attr, tag: FieldSpecification, attr: component}
    """
    findings: list[Finding] = []
    for c in ctx.constraints:
        kind = c.get("kind")
        if kind == "count":
            parent, child = c.get("parent"), c.get("child", "*")
            if not parent:
                continue
            n = deck.count(parent, child)
            lo, hi = c.get("min"), c.get("max")
            if hi is not None and n > hi:
                findings.append(
                    Finding(
                        "constraints", "error",
                        f"<{parent}> has {n} {child} children; at most {hi} expected",
                        location=parent,
                    )
                )
            if lo is not None and n < lo:
                findings.append(
                    Finding(
                        "constraints", "error",
                        f"<{parent}> has {n} {child} children; at least {lo} expected",
                        location=parent,
                    )
                )
        elif kind == "forbid_attr":
            tag, attr = c.get("tag"), c.get("attr")
            for name, el in deck.iter_elements(tag or ""):
                if attr and el.get(attr) is not None:
                    findings.append(
                        Finding(
                            "constraints", "error",
                            f"<{tag}> must not set {attr!r}",
                            location=f"{name}:{tag}",
                        )
                    )
        elif kind == "require_attr":
            tag, attr = c.get("tag"), c.get("attr")
            for name, el in deck.iter_elements(tag or ""):
                if attr and el.get(attr) is None:
                    findings.append(
                        Finding(
                            "constraints", "error",
                            f"<{tag}> is missing required attribute {attr!r}",
                            location=f"{name}:{tag}",
                        )
                    )
    return findings


BUILTIN_CHECKS: dict[str, CheckFn] = {
    "parse": check_parse,
    "required_sections": check_required_sections,
    "cross_section_refs": check_cross_section_refs,
    "constraints": check_constraints,
}


def render_constraints_prose(constraints: Sequence[dict[str, Any]]) -> str:
    """Prose rendering of the same constraints, for the cheatsheet.

    One source, two surfaces: the model reads this, the hook enforces the other.
    """
    lines = []
    for c in constraints:
        kind = c.get("kind")
        if kind == "count":
            parent, child = c.get("parent"), c.get("child", "*")
            lo, hi = c.get("min"), c.get("max")
            what = "children" if child == "*" else f"<{child}> children"
            if lo is not None and hi is not None and lo == hi:
                lines.append(f"- `<{parent}>` has exactly {lo} {what}, no more.")
            elif hi is not None:
                lines.append(f"- `<{parent}>` has at most {hi} {what}. Do not add more.")
            elif lo is not None:
                lines.append(f"- `<{parent}>` needs at least {lo} {what}.")
        elif kind == "forbid_attr":
            lines.append(
                f"- Do NOT set `{c.get('attr')}` on `<{c.get('tag')}>`; it is not used here."
            )
        elif kind == "require_attr":
            lines.append(
                f"- Every `<{c.get('tag')}>` must set `{c.get('attr')}`."
            )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# plugin loading and validation
# ---------------------------------------------------------------------------


@dataclass
class PluginReport:
    name: str
    loaded: bool
    has_test: bool
    test_passed: bool | None = None
    error: str | None = None

    @property
    def ok(self) -> bool:
        return self.loaded and self.has_test and self.test_passed is True


def load_plugin(path: Path) -> tuple[CheckFn | None, str | None]:
    """Import a check plugin by path, returning ``(check_fn, error)``."""
    path = Path(path)
    spec = importlib.util.spec_from_file_location(f"_check_{path.stem}", path)
    if spec is None or spec.loader is None:
        return None, "could not create module spec"
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except Exception as exc:
        return None, f"{type(exc).__name__}: {exc}"
    fn = getattr(mod, "check", None)
    if not callable(fn):
        return None, "module defines no callable 'check'"
    return fn, None


def validate_plugins(checks_dir: Path, *, timeout: float = CHECK_TIMEOUT_S) -> list[PluginReport]:
    """Load every plugin and run its mandatory sibling test.

    Runs each test in a subprocess so a plugin that hangs, segfaults, or calls
    ``sys.exit`` cannot take the search down with it.
    """
    checks_dir = Path(checks_dir)
    reports: list[PluginReport] = []
    if not checks_dir.is_dir():
        return reports
    for p in sorted(checks_dir.glob("*.py")):
        if p.name.startswith("_") or p.name.endswith("_test.py"):
            continue
        fn, err = load_plugin(p)
        test_path = p.with_name(f"{p.stem}_test.py")
        rep = PluginReport(
            name=p.stem,
            loaded=fn is not None,
            has_test=test_path.exists(),
            error=err,
        )
        if rep.loaded and rep.has_test:
            try:
                proc = subprocess.run(
                    [sys.executable, str(test_path.resolve())],
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=str(checks_dir.resolve()),
                )
                rep.test_passed = proc.returncode == 0
                if proc.returncode != 0:
                    rep.error = (proc.stderr or proc.stdout or "").strip()[:500]
            except subprocess.TimeoutExpired:
                rep.test_passed = False
                rep.error = f"test exceeded {timeout}s budget"
        elif not rep.has_test:
            rep.error = "missing required sibling test file"
        reports.append(rep)
    return reports


def run_checks(
    deck: Deck,
    ctx: CheckContext,
    enabled: Sequence[str],
    *,
    plugins: dict[str, CheckFn] | None = None,
) -> list[Finding]:
    """Run the enabled checks in order, collecting findings.

    A check that raises yields a ``warn`` finding rather than killing the hook:
    a broken check must never be able to block the agent forever.
    """
    registry: dict[str, CheckFn] = {**BUILTIN_CHECKS, **(plugins or {})}
    findings: list[Finding] = []
    for name in enabled:
        fn = registry.get(name)
        if fn is None:
            findings.append(
                Finding("registry", "warn", f"enabled check {name!r} is not registered")
            )
            continue
        try:
            findings.extend(fn(deck, ctx))
        except Exception as exc:
            findings.append(
                Finding(name, "warn", f"check raised {type(exc).__name__}: {exc}")
            )
    return findings


def render_feedback(findings: Sequence[Finding], shape: str = "structured_errors") -> str:
    """Render findings as the repair feedback the stop hook returns.

    ``shape`` is a searchable field of the stop policy. This is the surface the
    paper's recommendation (vi) is about ("static hooks only raise the floor;
    closed-loop retries driven by validator output are needed to raise the
    ceiling") and the natural place an Effective-Feedback-Compute objective
    would bite.
    """
    errors = [f for f in findings if f.severity == "error"]
    if not errors:
        return ""
    if shape == "minimal":
        return f"{len(errors)} validation error(s); fix them before finishing."
    lines = [f"{len(errors)} validation error(s) must be fixed before you finish:"]
    lines += [f"  {f.render()}" for f in errors]
    if shape == "errors_plus_tables":
        lines.append(
            "\nWhere a validator printed the valid attribute or tag table, use it "
            "verbatim -- do not guess a replacement name."
        )
    return "\n".join(lines)
