# `scripts/self_evolving/` — the v1 loop (superseded)

**Status: superseded by `scripts/siga_evolve/` + `src/evolve/`. Kept in place,
not moved, because `docs/` and the paper reference these paths.**

Full analysis: `docs/2026-08-19_method-adoption-plan.md`.

## What it produced

`plugin_evolving/v0 → v1 → v2 → v3`. `v3` is the paper's **SE** cell
(`scripts/efficiency_table.py:234`, `launch_icl_v0_v3.sh`).

## The defect that matters

**The reflection loop never received a reward signal.**

`run_full_evolution.sh:24-45` alternates `run_round.sh` and `reflect.py` with no
scoring step in between. `run_round.sh:59-73` invokes `scripts/run_experiment.py`
only, and the runner does not score — the only thing that writes
`<task>_eval.json` is `scripts/eval/batch_evaluate.py:68`, which is never called.
So `reflect.py:104-128 gather_round()` found no eval files, `treesim` was `None`
for every task, and `reflect.py:312` set `mean_ts = 0`.

The proposer's prompt therefore read:

```
RECENT ROUND RESULTS (mean treesim 0.0000, n=7):

--- AdvancedExampleDruckerPrager (treesim N/A) ---
R: /geos_lib/inputFiles/...
B: grep -rn ...
```

Corroborated on disk: `plugin_evolving/v{1,2,3}/.reflection_meta.json` all record
`"round_mean_treesim": 0`.

Compounding it, `reflect.py:196-197` told the proposer *"If the current plugin is
already working well (≥0.85 mean treesim), it's fine to make small additions or
no changes"* — a branch that, with `0.0000` rendered, could never fire. Content
grew monotonically: `PRIMER.md` 270 B → 1883 → 2488 → 3159; `cheatsheet.md`
→ 2838 → 4843 → 4526.

So Eq. (2)'s `argmax` was not weakly approximated. There was no reward in the
loop at all, and `v3` is not a *selected* candidate — it is the last link in a
chain of three unconditioned rewrites.

## Other confirmed defects

| Where | Defect |
|---|---|
| `reflect.py:284-296,337` | writes `v{N+1}` unconditionally; no accept/reject, no rollback |
| `reflect.py:69-101` | evidence is a 2500-char list of tool names; no scores, errors, or validator output — while `scripts/bottleneck/extract.py:278` already computes all of it |
| `reflect.py:240-243,257-263` | search space is prose-only; hooks/validators/MCP are untouchable scaffolding |
| `reflect.py:248-249` | hygiene is an `.xml`-only regex; `.geos` leaks straight through (and did, into `v3`) |
| `reflect.py:113` | iterates every subdirectory as a task (`v1` meta: `round_n_tasks: 7` for a 6-task round) |
| `reflect.py:49,51`; `run_round.sh:12` | hardcoded `/home/matt/sci/repo3` and `/data/shared/...` |
| `reflect.py:55` | proposer is the inference model (self-distillation confound) |
| `run_round.sh:29-50` | `CHEATSHEET_ARG` is computed and never used; M is concatenated into the primer, so the lineage has no separable M |
| `run_full_evolution.sh:17-19` | rounds use disjoint task thirds, confounding adapter quality with task difficulty |
| `plugin_evolving/v*/hooks/` | `copy_scaffolding()` froze the pre-`geosx --validate-input` validator; 274 lines of drift from `plugin/`, zero mentions of `geosx` |
| `analyze_evolution.py:67` | invalid f-string format spec raised on every line into a bare `except: pass`, so the version log always rendered empty — **fixed 2026-08-19**, and it now prints the `round_mean_treesim = 0` that was invisible for months |

## Reproducing the paper's SE

These scripts still do it, with two caveats: the hardcoded paths must be
updated, and `copy_scaffolding()` will hand the lineage the retired
`xmllint --schema` validator rather than the `geosx --validate-input` one the
repo now ships (`docs/GEOSX_VALIDATE.md`).
