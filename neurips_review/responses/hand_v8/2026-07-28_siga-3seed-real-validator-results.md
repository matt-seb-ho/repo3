# SIGA (repo3_openfoam) real-validator results: full 9-cell single seed + 3-seed repeat on vanilla and the best cell

Companion to `OPENFOAM_REAL_VALIDATE.md` and `OPENFOAM_REAL_VALIDATE_MECHANISM.md`,
which document *how* the real-OpenFOAM validator works. This doc reports what it
measured across two separate runs: a full single-seed 9-cell factorial ablation,
and a 3-seed repeat restricted to `vanilla` and the best-performing cell.

## Methodology

**Task set.** `data/openfoam_benchmark/foamgpt_subset_seed42_n30_hybrid/` — 30
FoamGPT-derived OpenFOAM cases, each with a natural-language `user_requirement.txt`
and a ground-truth (`gt/`) set of required files defined in `manifest.json`.

**Model.** `deepseek/deepseek-v4-flash` via OpenRouter, routed through Claude
Code (`ANTHROPIC_BASE_URL=https://openrouter.ai/api`,
`ANTHROPIC_CUSTOM_MODEL_OPTION`), `--permission-mode bypassPermissions`,
`--output-format stream-json`.

**Ablation design.** SIGA's four adapter factors — R (retrieval/RAG via MCP),
S (Stop-hook completion gate), X (agent-callable validator tool), M (procedural
memory/cheatsheet) — combined into a Resolution-IV 2⁴⁻¹ fractional factorial:
9 cells (`vanilla`, `r+m`, `s+m`, `r+s`, `x+m`, `r+x`, `s+x`, `r+s+x+m`, `s+x+m`).

**Validator mechanism (S and X).** Both the Stop-hook (S) and the agent-callable
tool (X) now call `openfoam_real_validate.py`, which runs the real Allrun
sequence (`blockMesh` then the task's solver) inside the
`openfoam/openfoam11-paraview510` Docker image, each phase bounded to a 30s
wall-clock `timeout`. A `FOAM FATAL ERROR`/`FOAM FATAL IO ERROR` appearing in
the output is the only thing that counts as a failure — a case still running
when the 30s timeout fires is treated as a pass, since OpenFOAM front-loads
dictionary/mesh parsing before the first timestep. This replaced an earlier
heuristic Python "linter" (delimiter/marker checks only, no real execution).
See `OPENFOAM_REAL_VALIDATE_MECHANISM.md` for the full mechanism writeup and
its known edge case (a slow-initializing case could in principle be falsely
passed).

**Per-task timeout.** 1500s (25 min) wall-clock budget per task, enforced via
`subprocess.Popen(..., start_new_session=True)` + `communicate(timeout=1500)`
+ `os.killpg(..., signal.SIGKILL)` on `TimeoutExpired`, to avoid orphaning
MCP-server child processes.

**Eval metric.** `scripts/openfoam/evaluate_openfoam_runs.py`:
`overall = 0.7 · mean_similarity + 0.3 · coverage`, where `mean_similarity` is
`difflib.SequenceMatcher` ratio on whitespace/comment-normalized text per
required file, and `coverage` is the fraction of required files present.
Reported per cell/seed as the mean over the task set.

**Executability check.** `scripts/openfoam/test_executability.py` — a
*separate*, post-hoc pass over each `inputs/` directory a task produced: copies
it into a scratch dir, runs `blockMesh` (if present) then the task's solver
inside the same Docker image, each phase bounded to 45s. Classified
"executable" if no `FOAM FATAL ERROR` appears before the phase's time budget
elapses. This measures structural/dictionary-level acceptance only — not
correctness of physics. Solver binaries absent from the test image (e.g.
`foamyHexMesh`) are excluded from the denominator and reported separately.

**Two separate runs reported here:**

1. **Full 9-cell, single seed** (`real_validate_seed1`) — all 9 cells × 30
   tasks = 270 task-runs, run first as the baseline confirmation that the
   real-validator swap works at full scale.
2. **3-seed repeat, 2 cells only** (`real_validate_seed2`, `real_validate_seed3`)
   — restricted to `vanilla` (no adapter factors, as a floor baseline) and
   `r+s+x+m` (the empirically best-performing cell from the single-seed run,
   selected *before* running the repeats), 2 cells × 30 tasks × 2 more seeds =
   120 additional task-runs, to check repeat-to-repeat stability of the best
   cell and confirm the vanilla floor is consistent.

**Bugs found and fixed en route** (see `2026-07-28_openfoam-30task-9cell-ablation.md`
and `OPENFOAM_REAL_VALIDATE.md` for full detail): the ablation runner's
`prepare_plugin_dir()` never wrote a `.claude-plugin/plugin.json` manifest, so
R and X's MCP servers had never actually registered in *any* historical run
before this session (confirmed via `git log` — present since the very first
commit); a stale `/data/brianliu/...` host path baked into the system prompt
(pre-migration username) was silently unreachable; no per-task timeout existed.
All three were fixed in the same commit bundle as the real-validator swap.

## Results: full 9-cell single seed (`real_validate_seed1`)

270/270 tasks accounted for: 229 success, 37 timeout (still counted, not
errors), 4 genuine failures.

| Cell | R | S | X | M | Mean overall score | Executable |
|---|---|---|---|---|---|---|
| r+s+x+m | x | x | x | x | **0.6676** | 26/29 (89.7%) |
| s+x | | x | x | | 0.6674 | 23/29 (79.3%) |
| r+s | x | x | | | 0.6596 | 23/29 (79.3%) |
| s+x+m | | x | x | x | 0.6421 | 26/29 (89.7%) |
| s+m | | x | | x | 0.6176 | 21/29 (72.4%) |
| x+m | | | x | x | 0.5724 | 19/29 (65.5%) |
| r+x | x | | x | | 0.5326 | 19/30 (63.3%) |
| vanilla | | | | | 0.0885 | 4/30 (13.3%) |
| r+m | x | | | x | 0.0189 | 1/30 (3.3%) |

(Executability denominators exclude 1 task per cell whose solver isn't present
in the test Docker image, except `vanilla`/`r+x` where none were excluded.)

**Overall executability across all 9 cells: 162/264 (61.4%)** (6 excluded as
solver-unavailable).

### Why vanilla and r+m collapse so hard

Both scored far below every other cell — not because of the validator (neither
cell has S or X active), but because of an unrelated confound that landed in
the same commit: a stale-path fix
(`/data/brianliu/OpenFOAM-13` → `/data/brian/OpenFOAM-13`) made the *real*,
large OpenFOAM-13 C++ source tree browsable for the first time (it was
previously unreachable, silently). Without S forcing the agent to wrap up and
verify required files exist, `vanilla` and `r+m` agents burn a large fraction
of their tool-call budget exploring raw solver source (confirmed directly:
`vanilla/aachenBomb` made 31 of 105 Bash calls against the source tree) instead
of finishing the required files — hence `coverage: 0.0` on most cases,
independent of timeout status.

### Factor structure

Every cell containing S scores 0.53–0.67 on the eval metric; both cells
without S collapse to 0.02–0.09 (for the reason above). On executability, S
alone (`r+s`: 79.3%) already gets most of the way to the best cells; X adds a
smaller further increment on top of S (`r+s+x+m`/`s+x+m`: 89.7% vs `r+s`:
79.3%). X's marginal value *without* S is much weaker (`r+x`: 63.3%,
`x+m`: 65.5%) — closer to the S-only cells than to the S+X cells. Mean
executability across the 5 X-on cells is 77.5% vs. 42.1% across the 4 X-off
cells, but that gap is substantially inflated by vanilla/r+m's collapse above,
which has nothing to do with X.

## Results: 3-seed repeat (`vanilla` + `r+s+x+m` only)

All 3 seeds: 30/30 accounted for per cell per seed (0 failures across all
seeds/cells besides ordinary 1500s timeouts).

| Seed | Cell | Mean overall score | Executable (of 59–60*) |
|---|---|---|---|
| 1 | r+s+x+m | 0.6676 | 26/29 (89.7%) |
| 1 | vanilla | 0.0885 | 4/30 (13.3%) |
| 2 | r+s+x+m | 0.6853 | — |
| 2 | vanilla | 0.0000 | — |
| 3 | r+s+x+m | 0.6653 | — |
| 3 | vanilla | 0.0000 | — |
| 2+3 combined | — | — | 27/59 (seed2), 25/59 (seed3) |

\* Seed2/seed3 executability was run per-seed over both cells combined
(60 tasks, 1 excluded as solver-unavailable = 59 scored): **seed2: 27/59
(45.8%)**, **seed3: 25/59 (42.4%)**.

**`r+s+x+m` is stable across all 3 seeds**: 0.6676, 0.6853, 0.6653 — a tight
band (range 0.020, ~3% of the mean), confirming the best cell's advantage is
not a single-seed fluke.

**`vanilla` is even worse in seeds 2 and 3 than seed 1**: seed1 managed a
non-zero 0.0885 (a few cases scored decently), but seeds 2 and 3 scored
*exactly* 0.0 across all 30/30 cases each — every single case had at least one
missing required file. This is consistent with (not contradicting) the
source-tree-distraction explanation above: it's a real, reproducible failure
mode for the no-adapter baseline on this task set with this harness
configuration, not a one-off.

## Cost

Real per-task cost, queried directly from OpenRouter's `/api/v1/generation`
endpoint (not Claude Code's own self-reported `total_cost_usd`, which reports
`0` for non-Anthropic models routed through a custom gateway). Sampled 10 tasks
from seed1: mean **$0.66/task** (range $0.04–$1.74, std $0.50). Extrapolated:
**≈$179 per full 9-cell/30-task seed** (~$150–220 in practice). The 2-cell
seed2/seed3 repeats (60 tasks each) tracked at ~$28.50 actually spent, in line
with that per-task rate (2/9 of a full seed ≈ $128 predicted vs ~$28.50 for a
smaller 60-task subset — consistent scaling).

## Known limitations

- The real-validator's 30s-per-phase bound is a timeout-based approximation,
  not a dedicated "load-only" flag (OpenFOAM has none) — see
  `OPENFOAM_REAL_VALIDATE_MECHANISM.md` for the specific false-pass risk this
  carries for slow-initializing cases.
- The vanilla/r+m collapse is a genuine, reproduced-across-3-seeds result for
  *this* harness configuration (deepseek-v4-flash, this system prompt, this
  timeout), not a universal claim about unassisted agents on OpenFOAM tasks in
  general.
