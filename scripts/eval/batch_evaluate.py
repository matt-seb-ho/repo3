#!/usr/bin/env python3
"""Batch evaluate agent-generated XML experiments against ground truth.

Uses the XMLTreeSim headline metric (``src.eval.judge_geos``) by default.
Pass ``--legacy`` to fall back to the earlier weighted-dimension scorer
in ``src.eval.lxml_xml_eval``.

Expected directory layout:

    experiments_dir/
      <task_name>/inputs/*.xml     # agent output
    ground_truth_dir/
      <task_name>/inputs/*.xml     # reference
    results_dir/
      <task_name>_eval.json        # per-task result

Usage:
    uv run python scripts/eval/batch_evaluate.py \\
        --experiments-dir data/eval/claude_code/experiment_run1 \\
        --ground-truth-dir data/eval/experiments_gt \\
        --results-dir data/eval/results/experiment_run1
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.eval import judge_geos, lxml_xml_eval


def evaluate_one(
    name: str,
    experiments_dir: Path,
    gt_dir: Path,
    results_dir: Path | None,
    save: bool,
    legacy: bool,
) -> dict:
    gen = experiments_dir / name / "inputs"
    gt = gt_dir / name / "inputs"

    result: dict = {"experiment": name}
    if not gt.exists():
        return {**result, "status": "error", "error": f"gt missing: {gt}"}
    if not gen.exists():
        return {**result, "status": "error", "error": f"generated missing: {gen}"}

    try:
        if legacy:
            eval_result = lxml_xml_eval.evaluate_directories(gt, gen)
        else:
            eval_result = judge_geos.evaluate_directories(gt, gen)
        result.update(eval_result)
        result["status"] = "success"
    except Exception as exc:  # noqa: BLE001
        return {**result, "status": "error", "error": f"{type(exc).__name__}: {exc}"}

    if save and results_dir is not None:
        results_dir.mkdir(parents=True, exist_ok=True)
        (results_dir / f"{name}_eval.json").write_text(
            json.dumps(result, indent=2, default=str)
        )
    return result


def print_summary(results: list[dict]) -> None:
    ok = [r for r in results if r["status"] == "success"]
    bad = [r for r in results if r["status"] != "success"]
    print(f"\n{'=' * 60}")
    print(f"  Batch evaluation: {len(ok)}/{len(results)} succeeded")
    print(f"{'=' * 60}")
    if ok:
        scores = [r.get("overall_score", 0.0) for r in ok]
        print(f"  Mean  : {statistics.mean(scores):.2f}")
        print(f"  Median: {statistics.median(scores):.2f}")
        print(f"  Range : {min(scores):.2f} – {max(scores):.2f}")
        print(f"  Pass ≥7: {sum(1 for s in scores if s >= 7.0)}/{len(scores)}")
        print()
        for r in sorted(ok, key=lambda x: x.get("overall_score", 0.0), reverse=True):
            s = r.get("overall_score", 0.0)
            ts = r.get("treesim")
            ts_str = f"  treesim={ts:.3f}" if ts is not None else ""
            print(f"  {s:5.2f}/10  {r['experiment']}{ts_str}")
    if bad:
        print("\n  Failed:")
        for r in bad:
            print(f"    {r['experiment']}: {r.get('error')}")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--experiments-dir", "-d", type=Path, required=True)
    p.add_argument("--ground-truth-dir", "-g", type=Path, required=True)
    p.add_argument("--results-dir", "-r", type=Path, default=None,
                   help="Where to write per-task <name>_eval.json. Omit to skip saving.")
    p.add_argument("--experiments", "-e", nargs="+", metavar="NAME",
                   help="Restrict to these task names (default: all)")
    p.add_argument("--legacy", action="store_true",
                   help="Use lxml_xml_eval (weighted dimensions) instead of judge_geos (XMLTreeSim).")
    p.add_argument("--output", "-o", type=Path, default=None,
                   help="Aggregate results JSON")
    args = p.parse_args()

    if not args.experiments_dir.exists():
        print(f"error: missing experiments dir {args.experiments_dir}", file=sys.stderr)
        return 1
    if not args.ground_truth_dir.exists():
        print(f"error: missing ground-truth dir {args.ground_truth_dir}", file=sys.stderr)
        return 1

    all_dirs = sorted(d for d in args.experiments_dir.iterdir() if d.is_dir())
    names = [d.name for d in all_dirs]
    if args.experiments:
        names = [n for n in names if n in args.experiments]
    if not names:
        print("no experiments found")
        return 1

    save = args.results_dir is not None
    results: list[dict] = []
    for i, name in enumerate(names, 1):
        print(f"[{i:3d}/{len(names)}] {name}", end="  ", flush=True)
        r = evaluate_one(name, args.experiments_dir, args.ground_truth_dir,
                         args.results_dir, save, args.legacy)
        results.append(r)
        if r["status"] == "success":
            print(f"{r.get('overall_score', 0):.2f}/10")
        else:
            print(f"FAILED: {r.get('error')}")

    print_summary(results)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps({
            "timestamp": datetime.now().isoformat(),
            "experiments_dir": str(args.experiments_dir),
            "ground_truth_dir": str(args.ground_truth_dir),
            "metric": "lxml_xml_eval" if args.legacy else "judge_geos",
            "results": results,
        }, indent=2, default=str))
        print(f"\nWrote {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
