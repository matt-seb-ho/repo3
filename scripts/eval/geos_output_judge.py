#!/usr/bin/env python3
"""Compare generated and ground-truth GEOS run outputs with a tool-using agent."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from eval.geos_output_judge import (
    DEFAULT_COMMAND_TIMEOUT,
    DEFAULT_MAX_TURNS,
    DEFAULT_MODEL,
    evaluate_output_directories,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--ground-truth", type=Path, required=True)
    parser.add_argument(
        "--flat",
        action="store_true",
        help="Treat the two supplied directories as one simulation pair.",
    )
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--max-turns", type=int, default=DEFAULT_MAX_TURNS)
    parser.add_argument(
        "--command-timeout", type=int, default=DEFAULT_COMMAND_TIMEOUT
    )
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    report = evaluate_output_directories(
        args.candidate,
        args.ground_truth,
        flat=args.flat,
        model=args.model,
        max_turns=args.max_turns,
        command_timeout=args.command_timeout,
    )
    rendered = json.dumps(report, indent=2)
    print(rendered)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(rendered + "\n")
    return 0 if report["all_same"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
