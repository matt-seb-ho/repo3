#!/usr/bin/env python3
"""Audit which models actually served each eval run.

Motivated by the 2026-07-29 finding that `Agent(subagent_type="Explore")`
sidechains in the DeepSeek-v3.2 ablation were served by
`anthropic/claude-4.5-haiku-20251001` (Amazon Bedrock) while the main chain ran
DeepSeek: Claude Code's built-in agent types pin their own small-fast model
instead of inheriting `--model`, and OpenRouter happily serves the Anthropic
slug. `eval_metadata.json` records only the *requested* model, so nothing in
the result tree flags the substitution.

Usage:
    python scripts/analysis/audit_model_provenance.py /data/shared/geophysics_agent_data/data/eval
    python scripts/analysis/audit_model_provenance.py data/eval --json report.json

Exit code is 1 if any run served a model family other than the requested one,
so this can gate a campaign in CI.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path


def _family(model: str) -> str:
    """Coarse vendor/family key: 'anthropic/claude-4.5-haiku-20251201' -> 'anthropic'."""
    m = model.lower()
    if "/" in m:
        return m.split("/", 1)[0]
    for vendor in ("claude", "deepseek", "minimax", "gpt", "gemini", "qwen"):
        if vendor in m:
            return "anthropic" if vendor == "claude" else vendor
    return m


def _iter_events(path: Path):
    with path.open(encoding="utf-8", errors="replace") as fh:
        for line in fh:
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def audit_run(events_path: Path) -> dict:
    """Return per-chain model/provider counts plus the subagent types involved."""
    by_chain: dict[str, Counter] = defaultdict(Counter)
    providers: dict[str, set[str]] = defaultdict(set)
    subagent_types: Counter = Counter()
    # tool_use_id -> subagent_type, so sidechain messages can be attributed.
    spawn: dict[str, str] = {}
    records = list(_iter_events(events_path))

    for rec in records:
        msg = rec.get("message")
        if not isinstance(msg, dict):
            continue
        for block in msg.get("content") or []:
            if not isinstance(block, dict) or block.get("type") != "tool_use":
                continue
            # The Agent tool has been named both `Task` and `Agent` across CC versions.
            if block.get("name") in ("Agent", "Task"):
                st = (block.get("input") or {}).get("subagent_type", "?")
                spawn[block.get("id")] = st
                subagent_types[st] += 1

    for rec in records:
        msg = rec.get("message")
        if not isinstance(msg, dict) or not msg.get("model"):
            continue
        parent = rec.get("parent_tool_use_id")
        chain = f"sidechain:{spawn.get(parent, '?')}" if parent else "main"
        by_chain[chain][msg["model"]] += 1
        if msg.get("provider"):
            providers[msg["model"]].add(msg["provider"])

    meta_path = events_path.parent / "eval_metadata.json"
    requested = None
    base_url = None
    if meta_path.exists():
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8", errors="replace"))
            requested = meta.get("claude_model")
            base_url = meta.get("anthropic_base_url")
        except json.JSONDecodeError:
            pass

    served = {m for counts in by_chain.values() for m in counts}
    req_family = _family(requested) if requested else None
    off_model = sorted(
        m for m in served if req_family and _family(m) != req_family
    )

    return {
        "run_dir": str(events_path.parent),
        "requested_model": requested,
        "anthropic_base_url": base_url,
        "by_chain": {k: dict(v) for k, v in sorted(by_chain.items())},
        "providers": {k: sorted(v) for k, v in sorted(providers.items())},
        "subagent_types": dict(subagent_types),
        "off_model_served": off_model,
        "clean": not off_model,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root", type=Path, help="directory to scan for events.jsonl")
    ap.add_argument("--json", type=Path, default=None, help="write the full report here")
    ap.add_argument("--quiet", action="store_true", help="only print contaminated runs")
    args = ap.parse_args()

    if not args.root.exists():
        print(f"error: {args.root} does not exist", file=sys.stderr)
        return 2

    reports = [audit_run(p) for p in sorted(args.root.rglob("events.jsonl"))]
    if not reports:
        print(f"no events.jsonl found under {args.root}", file=sys.stderr)
        return 2

    dirty = [r for r in reports if not r["clean"]]
    no_meta = [r for r in reports if r["requested_model"] is None]

    for rep in reports:
        if args.quiet and rep["clean"]:
            continue
        flag = "OK  " if rep["clean"] else "DIRTY"
        print(f"[{flag}] {rep['run_dir']}")
        print(f"        requested: {rep['requested_model']}  base_url: {rep['anthropic_base_url']}")
        for chain, counts in rep["by_chain"].items():
            for model, n in sorted(counts.items(), key=lambda kv: -kv[1]):
                prov = ",".join(rep["providers"].get(model, [])) or "?"
                print(f"        {chain:28s} {model:44s} n={n:<6d} via {prov}")
        if rep["subagent_types"]:
            print(f"        subagents spawned: {rep['subagent_types']}")

    print()
    print(f"scanned {len(reports)} runs: {len(reports) - len(dirty)} clean, {len(dirty)} contaminated")
    if no_meta:
        print(f"warning: {len(no_meta)} runs have no eval_metadata.json — requested model unknown, "
              f"cannot verify")
    if dirty:
        fams = Counter(m for r in dirty for m in r["off_model_served"])
        print("off-model served:")
        for model, n in fams.most_common():
            print(f"  {model}  (in {n} runs)")

    if args.json:
        args.json.write_text(json.dumps(reports, indent=2))
        print(f"full report -> {args.json}")

    return 1 if dirty else 0


if __name__ == "__main__":
    raise SystemExit(main())
