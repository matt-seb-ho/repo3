"""Catch name references GEOS resolves lazily, past `--validate-input`.

`docs/GEOSX_VALIDATE.md` records a direct test against the real binary: of the
four dangling-reference classes tried, three are caught by
`geosx -i <entry> --validate-input` (unknown attribute, hallucinated element
tag, load-time `targetRegions` -> `CellElementRegion`), and one is not —
`discretization="TPFA_DOES_NOT_EXIST"` with no matching `NumericalMethods`
child exits 0, because GEOS does not link a solver to its discretization scheme
until an actual solve step. xmllint cannot close it either: the relevant
attribute types (`groupNameRef`) carry no `xsd:key`/`xsd:keyref` constraint
anywhere in `schema.xsd`, so the XSD has no machinery to express it.

This is the reference plugin: a ~40-line check that closes a confirmed,
narrowly-scoped residual gap in the shipped validator.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from evolve.checks import CheckContext, Deck, Finding  # noqa: E402

#: (attribute, tag whose named children the attribute must reference)
LAZY_REF_ATTRS: tuple[tuple[str, str], ...] = (
    ("discretization", "NumericalMethods"),
    ("flowSolverName", "Solvers"),
    ("solidSolverName", "Solvers"),
    ("surfaceGeneratorName", "Solvers"),
)


def _named_descendants(deck: Deck, container_tag: str) -> set[str]:
    names: set[str] = set()
    for _, container in deck.iter_elements(container_tag):
        for el in container.iter():
            n = el.get("name")
            if n:
                names.add(n)
    return names


def check(deck: Deck, ctx: CheckContext) -> list[Finding]:
    findings: list[Finding] = []
    for attr, container_tag in LAZY_REF_ATTRS:
        defined = _named_descendants(deck, container_tag)
        if not defined:
            # Nothing declared that container at all; required_sections owns
            # that failure. Silence here avoids double-reporting.
            continue
        for fname, root in deck.roots.items():
            for el in root.iter():
                ref = el.get(attr)
                if not ref:
                    continue
                for token in re.split(r"[\s,{}]+", ref):
                    if token and token not in defined:
                        findings.append(
                            Finding(
                                "lazy_refs",
                                "error",
                                f"<{el.tag}> {attr}={token!r} does not name any "
                                f"<{container_tag}> entry. Defined: {sorted(defined)}",
                                location=f"{fname}:{el.get('name') or el.tag}",
                            )
                        )
    return findings
