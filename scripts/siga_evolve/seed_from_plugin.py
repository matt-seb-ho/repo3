#!/usr/bin/env python3
"""Build the seed candidate for a SIGA-Evolve search from the live plugin.

The seed is the *hand-designed* adapter (`plugin/`), not a blank one. v1 seeded
from `plugin_evolving/v0`, a 270-byte stub, so the loop spent its whole budget
rediscovering the hand-designed adapter's content rather than improving on it —
and the resulting SE cell landed within noise of the untouched S+X+M cell
(0.789 +/- 0.012 vs 0.783 +/- 0.022 on held-out-eval).

Starting from `plugin/` makes the baseline the thing we have to beat, which is
what the evaluation protocol requires anyway (see
docs/2026-08-19_method-adoption-plan.md, section 4.1, baseline B3).

Usage:
    python3 scripts/siga_evolve/seed_from_plugin.py \
        --plugin-dir plugin \
        --primer plugin/memory_primer_m1u.md \
        --out .evolve/seed
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from evolve.candidate import Candidate  # noqa: E402
from evolve.checks import render_constraints_prose  # noqa: E402
from evolve.manifest import ComponentSpec, Manifest, StopPolicy  # noqa: E402

try:
    from runner.constants import DEFAULT_GEOS_PRIMER_PATH as DEFAULT_PRIMER
except Exception:  # runner imports are environment-dependent; fall back by path
    DEFAULT_PRIMER = REPO_ROOT / "plugin" / "GEOS_PRIMER_absolute_min.md"

SEED_MANIFEST = Manifest(
    components={
        "primer": ComponentSpec("primer", "prose", path="PRIMER.md", budget_tokens=400),
        # M stays a separate component. run_round.sh concatenated the cheatsheet
        # into the primer at run time, so the v1 lineage had no separable M and
        # no way to budget it independently.
        # 900, not 800: the paper's M (plugin/memory_primer_m1u.md) is a
        # 775-token artifact and the estimator here is deliberately biased ~6%
        # high, so a budget of 800 would reject the seed itself. Headroom is
        # deliberate and small -- the point of the budget is that growth has to
        # be argued for, not that it is impossible.
        "memory": ComponentSpec(
            "memory", "itemized", path="memory/cheatsheet.md", budget_tokens=900
        ),
        "constraints": ComponentSpec(
            "constraints", "checked", path="memory/constraints.yaml", budget_tokens=300
        ),
        "stop_policy": ComponentSpec("stop_policy", "config"),
        "checks": ComponentSpec("checks", "code", dir="hooks/checks/"),
    },
    stop_policy=StopPolicy(
        retries=2,
        feedback_shape="structured_errors",
        checks=("parse", "geosx_validate", "required_sections"),
    ),
)

SEED_CONSTRAINTS = """\
# Negative constraints. Each entry is BOTH prose in the cheatsheet AND a check
# run at the stop interface, so "the model was told but did not comply" is not
# a possible outcome (arXiv:2605.30621's weak-tier failure mode).
#
# Seeded deliberately empty of task-specific counts: a constraint mined from a
# specific ground-truth deck is a leak, not a constraint. The search is expected
# to add generalisable ones.
constraints: []
"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--plugin-dir", type=Path, default=REPO_ROOT / "plugin")
    ap.add_argument("--primer", type=Path,
                    help=f"primer file to seed from (default: {DEFAULT_PRIMER.name})")
    ap.add_argument("--cheatsheet", type=Path,
                    help="cheatsheet to seed from (default: memory_primer_m1u.md, the paper's M)")
    ap.add_argument("--out", type=Path, default=REPO_ROOT / ".evolve" / "seed")
    args = ap.parse_args()

    # Defaults mirror what the harness and the paper actually use:
    #   primer  -> runner.constants.DEFAULT_GEOS_PRIMER_PATH
    #              (plugin/GEOS_PRIMER_absolute_min.md -- byte-for-byte what
    #               plugin_evolving/v0/PRIMER.md was seeded from)
    #   memory  -> plugin/memory_primer_m1u.md, the paper's M
    primer_src = args.primer or DEFAULT_PRIMER
    cheatsheet_src = args.cheatsheet or (args.plugin_dir / "memory_primer_m1u.md")

    if not primer_src.exists():
        candidates = sorted(args.plugin_dir.glob("*primer*.md"))
        print(f"ERROR: primer not found at {primer_src}", file=sys.stderr)
        if candidates:
            print("  candidates:", file=sys.stderr)
            for c in candidates:
                print(f"    {c}", file=sys.stderr)
        return 2

    files = {
        "PRIMER.md": primer_src.read_text(),
        "memory/cheatsheet.md": (
            cheatsheet_src.read_text() if cheatsheet_src and cheatsheet_src.exists()
            else "# GEOS authoring notes\n\n" + render_constraints_prose([])
        ),
        "memory/constraints.yaml": SEED_CONSTRAINTS,
    }

    seed = Candidate(manifest=SEED_MANIFEST, files=files)
    try:
        seed.validate()
    except Exception as exc:
        print(f"ERROR: seed candidate is invalid: {exc}", file=sys.stderr)
        print(
            "  (a primer over budget is the usual cause -- raise budget_tokens "
            "deliberately rather than by accident)",
            file=sys.stderr,
        )
        return 1

    seed.materialize(args.out, scaffolding_from=args.plugin_dir, overwrite=True)
    print(f"seed candidate {seed.cid} written to {args.out}")
    for path, n in sorted(seed.metadata()["estimated_tokens"].items()):
        print(f"  {path}: ~{n} tokens")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
