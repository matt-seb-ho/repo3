#!/usr/bin/env python3
"""Retro-audit adapter directories for ground-truth leakage.

Runs the SIGA-Evolve hygiene gate (a superset of the `.xml`-only regex in
`reflect.py:248` and `scripts/memory/hygiene_audit.py:41`) over any set of
adapter directories. Written to make the v1 lineage's actual leaks visible:

    $ python3 scripts/siga_evolve/audit_lineage.py --adapter-dir plugin_evolving/v3 \
          --task-list-from scripts/self_evolving/legacy/run_full_evolution.sh
    [warn] filename in skills/triaxial-driver-setup.md: references 'time.geos'
    ...

With `--ground-truth-dir` pointed at the real GT tree, filename findings that
match a blocked basename are promoted from `warn` to `block`, and the content
and numeric-literal rules become active.

Exit 1 if anything blocks.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from evolve.hygiene import GroundTruthCorpus, audit_dir  # noqa: E402

TASK_RE = re.compile(r"^TASKS?_\w+=\((.*?)\)", re.MULTILINE | re.DOTALL)


def tasks_from_shell(path: Path) -> set[str]:
    """Scrape task ids out of a `TASKS_R0=(...)`-style launcher."""
    text = Path(path).read_text()
    out: set[str] = set()
    for m in TASK_RE.finditer(text):
        out |= {t.strip().strip('"') for t in m.group(1).split() if t.strip()}
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--adapter-dir", type=Path, action="append", required=True)
    ap.add_argument("--ground-truth-dir", type=Path)
    ap.add_argument("--task-list-from", type=Path, action="append", default=[])
    ap.add_argument("--task", action="append", default=[])
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    if args.ground_truth_dir and args.ground_truth_dir.exists():
        corpus = GroundTruthCorpus.from_ground_truth_dir(args.ground_truth_dir)
        print(
            f"corpus: {len(corpus.task_ids)} tasks, "
            f"{len(corpus.blocked_basenames)} blocked basenames, "
            f"{len(corpus.numeric_literals)} GT numeric literals"
        )
    else:
        if args.ground_truth_dir:
            print(
                f"WARNING: ground truth dir {args.ground_truth_dir} not found; "
                "filename findings stay at 'warn' and the content/numeric rules "
                "are inert",
                file=sys.stderr,
            )
        corpus = GroundTruthCorpus()

    for p in args.task_list_from:
        corpus.task_ids |= tasks_from_shell(p)
    corpus.task_ids |= set(args.task)
    print(f"checking against {len(corpus.task_ids)} known task ids")

    reports = {}
    blocked = False
    for d in args.adapter_dir:
        report = audit_dir(d, corpus)
        reports[str(d)] = report.to_dict()
        n_block = sum(1 for f in report.findings if f.severity == "block")
        n_warn = len(report.findings) - n_block
        print(f"\n=== {d}: {len(report.checked_paths)} files, "
              f"{n_block} BLOCK, {n_warn} warn ===")
        for f in report.findings:
            print(f"  {f}")
        blocked = blocked or report.blocked

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(reports, indent=2))
        print(f"\nreport written to {args.out}")
    return 1 if blocked else 0


if __name__ == "__main__":
    raise SystemExit(main())
