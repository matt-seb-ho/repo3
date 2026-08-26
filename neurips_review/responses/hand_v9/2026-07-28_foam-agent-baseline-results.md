# Foam-Agent baseline results (1 seed, 10-task combined set)

Baseline comparison run for SIGA's OpenFOAM ablation, using
[Foam-Agent 2.0.0](https://github.com/csml-rpi/Foam-Agent) rather than the
repo3_openfoam SIGA harness.

## Methodology

**Task set.** Same `data/openfoam_benchmark/foamgpt_subset_seed42_n10_combined/`
10-task set used for the MetaOpenFOAM baseline (see that doc for how it was
built).

**Model.** `deepseek/deepseek-v4-flash` via OpenRouter, called directly through
Foam-Agent's own LangGraph-based agent loop (not through Claude Code).

**Validation mechanism.** Foam-Agent already had a built-in real-execution path
(`local_runner_node` → `run_allrun_and_collect_errors` → `run_command`), bounded
by a configurable `max_time_limit` (default 3600s), with process-group SIGKILL
on timeout — architecturally almost identical to SIGA's own real-validator
mechanism, already implemented. The only change needed: added a
`FOAMAGENT_MAX_TIME_LIMIT` environment-variable override (mirroring the
existing `FOAMAGENT_EXECUTION_MODE` override pattern in `config.py`) so this
run could bound each individual `Allrun` execution attempt to 30s, matching
SIGA's and MetaOpenFOAM's mechanism, instead of the 3600s default meant for
full physical simulations. `--execution-mode execute` (not `lint_only`, which
is Foam-Agent's own separate static-checker path — deliberately not used here).

**A note on what was *not* changed.** Foam-Agent's structured-output JSON
parsing (`_invoke_structured_via_json_prompt`, used for the openai-compatible
model-provider path) has no retry on malformed/incomplete JSON responses —
only throttling errors are retried; a validation error or truncated JSON
crashes the task immediately. This was identified as the direct cause of
several of the failures below. A retry-on-parse-error patch was drafted and
tested, then explicitly reverted at the user's direction: this baseline run
reports Foam-Agent's authentic out-of-box reliability with this model, not a
patched version, so the comparison against SIGA and MetaOpenFOAM reflects each
system's real behavior as shipped.

**Per-task timeout.** 1500s (25 min) overall wall-clock budget per task — a
gap fixed during this session: `run_foam_agent_eval.py`'s task-launching
`subprocess.run()` previously had **no timeout at all** (unlike SIGA's and
MetaOpenFOAM's runners, which already had one). Fixed by switching to
`subprocess.Popen(..., start_new_session=True)` + `communicate(timeout=1500)`
+ `os.killpg(..., SIGKILL)` on `TimeoutExpired`, matching the pattern already
used elsewhere in this session.

**Eval metric / executability check / cost tracking.** Same as MetaOpenFOAM's
doc — identical `evaluate_openfoam_runs.py` metric, identical standalone
`test_executability.py` post-hoc check (uniform across all three systems), and
newly-added local cost tracking (`estimate_openrouter_cost()`, same OpenRouter
pricing constants) parsing real token counts from Foam-Agent's own
`"Total prompt tokens:"` / `"Total completion tokens:"` stdout lines (Foam-Agent
already logged these; only the $ conversion was missing).

## Results

**2 success / 3 timeout / 5 failed** out of 10 (by Foam-Agent's own
returncode-based definition; "timeout" = hit the 1500s outer budget mid-loop,
not a crash).

**Text-similarity eval (mean overall score): 0.5647.**

| Case | Coverage | Similarity | Overall | Missing files |
|---|---|---|---|---|
| cavityClipped | 1.00 | 0.913 | 0.939 | — |
| simpleShapes | 1.00 | 0.817 | 0.872 | — |
| damBreakWithObstacle | 1.00 | 0.660 | 0.762 | — |
| boundaryWallFunctionsProfile | 0.75 | 0.735 | 0.740 | constant/physicalProperties.template |
| damBreak | 1.00 | 0.645 | 0.751 | — |
| helmholtzResonance | 1.00 | 0.581 | 0.707 | — |
| periodicCubeWater | 1.00 | 0.572 | 0.701 | — |
| Grossetete | 0.33 | 0.109 | 0.176 | 0/T.liquid, constant/physicalProperties.gas |
| aachenBomb | 0.00 | 0.000 | 0.000 | 0/Ydefault, constant/fvModels |
| externalCoupledCavity | 0.00 | 0.000 | 0.000 | 0/nut, 0/p, constant/pRef, constant/physicalProperties, system/blockMeshDict |

**Executability: 1/10 (10%)** — only `simpleShapes` ran without a fatal error.
Everything else hit a real `FOAM FATAL ERROR` (mostly during `blockMesh`, one
during `icoFoam`, one during `rhoPimpleFoam`) or a segfault (`boundaryWallFunctionsProfile`,
exit 139 during `blockMesh`); `aachenBomb` and `externalCoupledCavity` produced
no `inputs/` directory at all.

**Foam-Agent's own success/failure label does not track real executability**:
`Grossetete` was marked "success" (returncode 0) but still failed real
execution (`FOAM FATAL ERROR` during `blockMesh`). Conversely `simpleShapes` —
the *only* case that actually executed — was marked "timeout" (hit the 1500s
cap mid-loop, likely still iterating on a later refinement when killed). This
mirrors the same success-label-vs-real-executability mismatch seen in the
MetaOpenFOAM results.

### Root cause of the failures

All 5 outright "failed" tasks trace to the same underlying issue: Foam-Agent's
structured-output JSON parsing threw either a `pydantic.ValidationError`
(model's JSON response missing a required field) or a `ValueError` from
`_extract_json_object` ("Could not find a complete JSON object in response" /
"Empty response; expected JSON") — i.e. deepseek-v4-flash did not reliably
produce well-formed JSON matching the expected schema via this fallback
JSON-prompt method, and Foam-Agent has no retry path for that failure mode
(see Methodology note above; deliberately left unpatched for this baseline).

## Cost

**$0.1258 total** for the full 10-task run (1,133,561 tokens: 988,048 prompt +
145,513 completion — notably higher token usage than MetaOpenFOAM's run,
consistent with Foam-Agent's longer review loops: mean 6.2 review loops/task
vs MetaOpenFOAM's 0.9). Mean wall time 966s/task.
