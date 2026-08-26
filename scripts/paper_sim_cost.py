#!/usr/bin/env python3
"""Average API cost + wall-clock per individual GEOS simulation-setup run,
over the cells included in the NeurIPS paper's main DSv4-flash factorial (Table 1).

Cost is recomputed from raw token usage with DeepSeek V4-flash published pricing,
because the logged `total_cost_usd` is computed by Claude Code with Anthropic rates.
"""
import json, os, glob, statistics as st

ROOT = "/data/shared/geophysics_agent_data/data/eval/autocamp_2026-05-01/dsv4"

# Table 1 cells -> autocamp dir. (R,S,X,M) factorial F0-F7, F8=S+X+M, F11=SE-prose, SE.
CELLS = {
    "Vanilla (F0)": "autocamp_F0", "R+M (F1)": "autocamp_F1", "S+M (F2)": "autocamp_F2",
    "R+S (F3)": "autocamp_F3", "X+M (F4)": "autocamp_F4", "R+X (F5)": "autocamp_F5",
    "S+X (F6)": "autocamp_F6", "R+S+X+M (F7)": "autocamp_F7", "S+X+M (F8)": "autocamp_F8",
    "SE-prose (F11)": "autocamp_F11", "SE": "autocamp_SE",
}

# DeepSeek V4-flash pricing ($/1M tokens). Canonical constants from
# scripts/oh_dsv4_compare.py:56 (INP_C, INP_H, OUT = 0.14e-6, 0.0028e-6, 0.28e-6),
# i.e. $0.14/M cache-miss input, $0.0028/M cache-read, $0.28/M output (off-peak).
# (Supersedes the stale $0.27/$0.07/$1.10 V3-era figure in 2026-04-30_dsv4-ablation-final-v2.md.)
P_IN_MISS, P_CACHE_HIT, P_OUT = 0.14, 0.0028, 0.28

def run_result(task_dir):
    ev = os.path.join(task_dir, "events.jsonl")
    if not os.path.exists(ev):
        return None
    last = None
    with open(ev) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
            except Exception:
                continue
            if d.get("type") == "result" or "total_cost_usd" in d:
                last = d
    return last

def ds_cost(u):
    return ((u.get("input_tokens", 0) + u.get("cache_creation_input_tokens", 0)) / 1e6 * P_IN_MISS
            + u.get("cache_read_input_tokens", 0) / 1e6 * P_CACHE_HIT
            + u.get("output_tokens", 0) / 1e6 * P_OUT)

rows = []          # per-run records
per_cell = {}
for label, d in CELLS.items():
    cell_dir = os.path.join(ROOT, d)
    if not os.path.isdir(cell_dir):
        continue
    seed_dirs = sorted(glob.glob(os.path.join(cell_dir, f"{d}_s*")))
    crun = []
    for sd in seed_dirs:
        for task in sorted(os.listdir(sd)):
            tdir = os.path.join(sd, task)
            stj = os.path.join(tdir, "status.json")
            if not os.path.isdir(tdir) or not os.path.exists(stj):
                continue
            status = json.load(open(stj))
            res = run_result(tdir)
            u = (res or {}).get("usage", {}) or {}
            wall = status.get("elapsed_seconds")
            rec = {
                "cell": label, "seed": os.path.basename(sd), "task": task,
                "status": status.get("status"), "wall": wall,
                "ds_cost": ds_cost(u) if u else None,
                "anthropic_cost": (res or {}).get("total_cost_usd"),
                "in": u.get("input_tokens", 0), "cache_read": u.get("cache_read_input_tokens", 0),
                "cache_create": u.get("cache_creation_input_tokens", 0), "out": u.get("output_tokens", 0),
            }
            rows.append(rec); crun.append(rec)
    per_cell[label] = crun

def mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else float("nan")

print(f"Cells: {len([c for c in per_cell if per_cell[c]])}  Total runs: {len(rows)}")
ok = [r for r in rows if r["status"] == "success"]
print(f"Successful runs: {len(ok)}  Non-success: {len(rows)-len(ok)}\n")

print(f"{'cell':<16}{'n':>4}{'wall_s':>9}{'ds_$':>9}{'anth_$':>9}{'in_tok':>9}{'cache_rd':>11}{'out_tok':>9}")
for label in CELLS:
    rs = per_cell.get(label, [])
    if not rs:
        continue
    print(f"{label:<16}{len(rs):>4}{mean([r['wall'] for r in rs]):>9.0f}"
          f"{mean([r['ds_cost'] for r in rs]):>9.4f}{mean([r['anthropic_cost'] for r in rs]):>9.4f}"
          f"{mean([r['in'] for r in rs]):>9.0f}{mean([r['cache_read'] for r in rs]):>11.0f}"
          f"{mean([r['out'] for r in rs]):>9.0f}")

print("\n=== AVERAGE OVER ALL PAPER MAIN-TABLE RUNS (per individual simulation setup) ===")
walls = [r["wall"] for r in rows if r["wall"] is not None]
dsc = [r["ds_cost"] for r in rows if r["ds_cost"] is not None]
anc = [r["anthropic_cost"] for r in rows if r["anthropic_cost"] is not None]
print(f"n runs with wall-clock: {len(walls)}; with token data: {len(dsc)}")
print(f"Wall-clock:  mean {mean(walls):.0f} s ({mean(walls)/60:.1f} min)  "
      f"median {st.median(walls):.0f} s  min {min(walls):.0f}  max {max(walls):.0f}")
print(f"DeepSeek cost/run: mean ${mean(dsc):.4f}  median ${st.median(dsc):.4f}  "
      f"min ${min(dsc):.4f}  max ${max(dsc):.4f}")
print(f"  (constants are off-peak; standard on-peak rate is ~2x -> ~${mean(dsc)*2:.4f})")
print(f"Anthropic-rate cost/run (as logged, NOT deepseek): mean ${mean(anc):.4f}")
print(f"\nMean tokens/run: in={mean([r['in'] for r in rows]):.0f}  "
      f"cache_read={mean([r['cache_read'] for r in rows]):.0f}  "
      f"cache_create={mean([r['cache_create'] for r in rows]):.0f}  "
      f"out={mean([r['out'] for r in rows]):.0f}")
