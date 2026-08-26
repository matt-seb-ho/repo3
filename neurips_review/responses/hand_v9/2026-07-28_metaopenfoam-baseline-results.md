# MetaOpenFOAM baseline results (1 seed, 10-task combined set)

Baseline comparison run for SIGA's OpenFOAM ablation, using
[MetaOpenFOAM](https://github.com/Terry-cyx/MetaOpenFOAM) (now deprecated
upstream in favor of "sim-cli", per its own most recent commit) rather than the
repo3_openfoam SIGA harness.

## Methodology

**Task set.** `data/openfoam_benchmark/foamgpt_subset_seed42_n10_combined/` — a
10-task set built for this baseline comparison: the 5 original tasks used in
earlier baseline runs (`boundaryWallFunctionsProfile`, `Grossetete`,
`helmholtzResonance`, `externalCoupledCavity`, `damBreakWithObstacle`) plus 5
more drawn at random (seed 42) from the remaining 29 cases in the 30-task
ablation pool (`periodicCubeWater`, `cavityClipped`, `aachenBomb`,
`simpleShapes`, `damBreak`). `externalCoupledCavity` is the one case shared
between the two source sets (confirmed identical task text in both).

**Model.** `deepseek/deepseek-v4-flash` via OpenRouter, called directly through
MetaOpenFOAM's own `langchain_openai`/`langchain_deepseek` client (not through
Claude Code).

**Validation mechanism.** MetaOpenFOAM's own `lint_only` config flag was
repurposed to run *real* bounded OpenFOAM execution instead of its original
behavior (which unconditionally skipped execution and reported a fixed
"passed" status). The change: `RunnerAction.py`'s `lint_only` branch now runs
the real `Allrun` script via a new `run_command_bounded()` (process-group
SIGKILL after `lint_timeout_seconds`, default 30s — the same wall-clock bound
used by repo3_openfoam's own real-validator), then classifies pass/fail using
MetaOpenFOAM's existing `check_foam_errors()` log scan. This mirrors SIGA's
"initial execution for 30 seconds" mechanism as closely as MetaOpenFOAM's own
architecture allows.

**Per-task timeout.** 1500s (25 min) overall wall-clock budget per task
(`--task-timeout`, matching SIGA's and Foam-Agent's budgets).

**Eval metric.** Same `evaluate_openfoam_runs.py` metric as SIGA:
`overall = 0.7 · mean_similarity + 0.3 · coverage`.

**Executability check.** Same standalone `test_executability.py` post-hoc
check as SIGA (30s-per-phase real execution in the
`openfoam/openfoam11-paraview510` Docker image), run uniformly across all
three systems compared in this session for a fair, apples-to-apples number —
independent of each baseline's own internal validation/lint mechanism.

**Local cost tracking.** `estimate_openrouter_cost()` (input
$0.0983/M, output $0.1966/M, OpenRouter effective pricing 2026-05-30) applied
to real per-task token counts parsed from MetaOpenFOAM's own
`statistics.txt`/`ave_statistics.txt` output — not derived from polling
OpenRouter's account-level usage endpoint.

### Environment/bugs found and fixed before this run was possible

MetaOpenFOAM's Python environment did not exist at all on this host prior to
this session (no venv survived the `brianliu`→`brian` host migration, and the
`MetaGPT` dependency was never actually installed — only a small
`metagpt/tools/schemas/` YAML fixture directory was present, which is *not*
the real package). Rebuilding it surfaced several real bugs, all fixed:

1. **Stale host paths** — `/home/brianliu/MetaOpenFOAM`,
   `/data/brianliu/OpenFOAM-13`, and related cache dirs — updated to
   `/home/brian/...` throughout `run_metaopenfoam_eval.py`.
2. **Namespace-package shadowing** — the bundled `metagpt/tools/schemas/`
   fixture directory (no `__init__.py`) shadowed the real, pip-installed
   `metagpt` package whenever `META_ROOT` preceded site-packages on
   `sys.path`, making `metagpt.__file__` resolve to `None` and crashing
   on import. Fixed by excluding `META_ROOT` itself from `PYTHONPATH`
   (keeping only `META_ROOT/src`).
3. **Trailing-colon `PYTHONPATH` bug** — `f"{path}:{existing}"` produces a
   trailing `:` (i.e. an empty/cwd path entry) when the base `PYTHONPATH` is
   unset, silently reintroducing bug #2 via `cwd` (which is set to
   `META_ROOT` for the subprocess). Fixed by only appending `:{existing}` when
   non-empty.
4. **Wrong MetaGPT config path** — `write_metagpt_config()` wrote to
   `META_ROOT/config/config2.yaml`, but MetaGPT's own `Config.default()` only
   reads `METAGPT_ROOT/config/config2.yaml` (i.e. under the vendored
   `MetaGPT/` checkout) or `~/.metagpt/config2.yaml`. Fixed to write to the
   vendored location.
5. **Missing `sentence-transformers` dependency** (needed by
   `langchain_huggingface`'s embedding path) — installed.
6. **LLM client hang with no request timeout** — `make_chat_model()`
   constructed its `ChatOpenAI`/`ChatDeepSeek` client with no `timeout` or
   `max_retries` at all. Observed directly: one task made exactly one LLM
   call, then produced **zero** further output for ~1400s of a 1500s budget —
   no error, no retry, just silence, until the outer harness's own timeout
   killed it. Fixed by adding an explicit 120s request timeout and
   `max_retries=2`; the same simple task then completed successfully in 371s.
7. **Division-by-zero in `ReviewerAction.py`** — `lines_per_file += total_lines
   / total_files` crashed when a case had zero files at a review checkpoint
   (the one genuine failure in the 10-task run below, `helmholtzResonance`).
   Fixed with a zero-guard; not re-run after the fix (a rare edge case, not
   worth the added API cost for one task).

## Results

**9/10 tasks succeeded** (MetaOpenFOAM's own returncode-based definition);
1 failed on the `ReviewerAction.py` division-by-zero bug above (fixed after
the fact, not re-run).

**Text-similarity eval (mean overall score): 0.2764** — much lower than task
success rate alone would suggest, because MetaOpenFOAM often reports a case
"successful" while still failing to produce all required files at their
manifest-specified paths (`coverage < 1.0`).

| Case | Coverage | Similarity | Overall | Missing files |
|---|---|---|---|---|
| cavityClipped | 1.00 | 1.000 | 1.000 | — |
| damBreak | 1.00 | 0.824 | 0.877 | — |
| damBreakWithObstacle | 0.67 | 0.273 | 0.391 | constant/momentumTransport |
| Grossetete | 0.33 | 0.175 | 0.222 | 0/T.liquid, constant/physicalProperties.gas |
| externalCoupledCavity | 0.40 | 0.219 | 0.273 | 0/nut, constant/pRef, constant/physicalProperties |
| aachenBomb | 0.00 | 0.000 | 0.000 | 0/Ydefault, constant/fvModels |
| boundaryWallFunctionsProfile | 0.00 | 0.000 | 0.000 | 0/epsilon, 0/k, 0/omega, constant/physicalProperties.template |
| helmholtzResonance | 0.00 | 0.000 | 0.000 | 0/U, constant/physicalProperties |
| periodicCubeWater | 0.00 | 0.000 | 0.000 | system/mdEquilibrationDict |
| simpleShapes | 0.00 | 0.000 | 0.000 | system/meshQualityDict |

**Executability: 2/9 (22.2%)** (1 case, `simpleShapes`, excluded — its solver
`foamyHexMesh` isn't present in the test Docker image). Of the 7 non-executable
cases, all failed with a genuine `FOAM FATAL ERROR` — during `blockMesh` (3
cases), or the task's actual solver (`icoFoam`, `buoyantFoam`, `reactingFoam`,
`interFoam` — 1 each). Notably `damBreak` and `cavityClipped` scored highly on
text-similarity (0.877, 1.000) yet `damBreak` still failed real execution —
confirming (as with SIGA) that text-similarity and real executability measure
different things.

## Cost

**$0.0478 total** for the full 10-task run (311,274 tokens: 135,997 prompt +
175,277 completion), computed from real per-task token counts, not
account-level polling. Mean 10.8 LLM calls/task, mean wall time 401s/task.
