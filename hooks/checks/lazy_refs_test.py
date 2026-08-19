"""Mandatory sibling test for lazy_refs.py. Exit 0 == pass."""

from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from evolve.checks import CheckContext, Deck  # noqa: E402
from lazy_refs import check  # noqa: E402

GOOD = """
<Problem>
  <Solvers><SinglePhaseFVM name="flow" discretization="tpfa"/></Solvers>
  <NumericalMethods><FiniteVolume><TwoPointFluxApproximation name="tpfa"/></FiniteVolume></NumericalMethods>
</Problem>
"""

BAD = """
<Problem>
  <Solvers><SinglePhaseFVM name="flow" discretization="TPFA_DOES_NOT_EXIST"/></Solvers>
  <NumericalMethods><FiniteVolume><TwoPointFluxApproximation name="tpfa"/></FiniteVolume></NumericalMethods>
</Problem>
"""

NO_CONTAINER = """
<Problem>
  <Solvers><SinglePhaseFVM name="flow" discretization="tpfa"/></Solvers>
</Problem>
"""


def _deck(xml: str) -> Deck:
    return Deck(files={"base.xml": xml}, roots={"base.xml": ET.fromstring(xml)})


def main() -> int:
    ctx = CheckContext(inputs_dir=Path("."))

    assert check(_deck(GOOD), ctx) == [], "valid deck must produce no findings"

    bad = check(_deck(BAD), ctx)
    assert len(bad) == 1, f"expected 1 finding, got {len(bad)}"
    assert "TPFA_DOES_NOT_EXIST" in bad[0].message
    assert bad[0].severity == "error"

    # Missing container is required_sections' job, not ours — stay quiet.
    assert check(_deck(NO_CONTAINER), ctx) == []

    print("lazy_refs: 3/3 assertions passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
