"""Score Liam's full-run buckleyLeverett deck (post-1h-cutoff completion).

Liam returned to the assignment and produced both XML files (base + benchmark)
in a total wall time of 2h 59m 43s. We score:
  1. file-only TreeSim of his base.xml vs GT base.xml
  2. file-only TreeSim of his benchmark.xml vs GT benchmark.xml
  3. directory TreeSim of his {base, benchmark} vs GT directory
"""

import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path("/home/matt/sci/repo3")
sys.path.insert(0, str(ROOT / "src"))

from eval.judge_geos import evaluate_directories, evaluate_files

LIAM_FIN = ROOT / "data/human_baseline/liam_fin_folder"
LIAM_BASE = LIAM_FIN / "liam_fin_buckleyLeverett_base.xml"
LIAM_BENCH = LIAM_FIN / "liam_fin_buckleyLeverett_benchmark.xml"

GT_DIR = ROOT / "data/GEOS/inputFiles/compositionalMultiphaseFlow/benchmarks/buckleyLeverettProblem"
GT_BASE = GT_DIR / "buckleyLeverett_base.xml"
GT_BENCH = GT_DIR / "buckleyLeverett_benchmark.xml"


def file_score(gt: Path, gen: Path) -> dict:
    res = evaluate_files(gt, gen)
    return {
        "treesim": res.get("treesim"),
        "section_summary": {
            s: round(d, 3)
            for s, d in (res.get("treesim_per_section") or {}).items()
        },
    }


def dir_score() -> dict:
    """Score Liam's two-file submission as a directory against the GT directory.
    GT has 3 files (base, benchmark, smoke). Mirror what the agent gets:
    only the two requested files (base + benchmark) need to be present."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        shutil.copy(LIAM_BASE, tmp_path / "buckleyLeverett_base.xml")
        shutil.copy(LIAM_BENCH, tmp_path / "buckleyLeverett_benchmark.xml")

        # Variant 1: against full GT directory (includes smoke.xml the human did not produce)
        partial_against_full = evaluate_directories(GT_DIR, tmp_path)

        # Variant 2: against GT directory restricted to the two requested files
        gt_two = tmp_path / "gt_two"
        gt_two.mkdir()
        shutil.copy(GT_BASE, gt_two / "buckleyLeverett_base.xml")
        shutil.copy(GT_BENCH, gt_two / "buckleyLeverett_benchmark.xml")
        partial_against_two = evaluate_directories(gt_two, tmp_path)

    return {
        "treesim_full_gt": partial_against_full.get("treesim"),
        "treesim_two_file_gt": partial_against_two.get("treesim"),
    }


def main() -> None:
    out = {}
    out["base_only"] = {
        k: (round(v, 3) if isinstance(v, float) else v)
        for k, v in file_score(GT_BASE, LIAM_BASE).items()
        if k == "treesim"
    }
    out["base_only"]["per_section"] = file_score(GT_BASE, LIAM_BASE)["section_summary"]

    out["benchmark_only"] = {
        k: (round(v, 3) if isinstance(v, float) else v)
        for k, v in file_score(GT_BENCH, LIAM_BENCH).items()
        if k == "treesim"
    }
    out["benchmark_only"]["per_section"] = file_score(GT_BENCH, LIAM_BENCH)["section_summary"]

    d = dir_score()
    out["directory"] = {
        "treesim_full_gt": round(d["treesim_full_gt"], 3) if d["treesim_full_gt"] is not None else None,
        "treesim_two_file_gt": round(d["treesim_two_file_gt"], 3) if d["treesim_two_file_gt"] is not None else None,
    }

    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
