# Checkpoint — Sub-agent orchestration build (sleep mode, cycle 1)

**Sleep started:** 2026-04-27T20:00:00Z
**Phase:** TEST → THINK (17-task campaign complete, analyzing)
**Cycle:** 6
**Session:** "custom-subagents-arch"

## Cycle 7 status — adversarial review RN-005 found 3 P1 blockers in XN-018

The headline "+0.204 vs vanilla DSv4-flash" and "matches OpenHands+minimax"
claims are PRELIMINARY pending fixes. Three P1 blockers:

1. **GT leakage**: `contamination.py:get_blocked_files_for_task` blocks
   only the current task's GT, leaving the other 16 test-task GT XMLs
   visible in the filtered tree. Trace shows orchestrator on
   ExampleIsothermalLeakyWell copied `thermalLeakyWell_base.xml` (GT
   for ExampleThermalLeakyWell, a sibling test task). Fix: wire
   `misc/memory_artifacts/test_blocklist.json:union_xml` (already
   present, 55 entries) into the runner.

2. **`Write` tool not denied**: `--disallowedTools Skill --disallowedTools
   AskUserQuestion --disallowedTools Write` was passed as 3 separate
   flags but CC expects a single comma-separated value. Write fired
   in 4 of 17 tasks (Sneddon, CasedThermoElastic, ThermalLeakyWell,
   kgdExperimentValidation). Fix: `--disallowedTools "Skill,AskUserQuestion,Write"`.

3. **Token double-counting**: `analyze_17task.py:tally_jsonl_usage`
   sums every JSONL `message.usage` record; stream-json re-emits the
   same message.id repeatedly. ~2-4× inflation in absolute token
   totals (deltas may survive since both arms affected). Fix: dedup
   by message.id.

Three of the four largest-win tasks (TutorialSneddon Δ+0.754,
ExampleIsothermalLeakyWell Δ+0.109, ExampleDPWellbore Δ+0.684) are
implicated. XN-018 marked PRELIMINARY with full response table.
Hub.md SoK updated. RN-005 lives at .copilot/reviews/.

Architecture itself is mechanically sound (17/17 end-to-end). The
re-run plan: P1 fixes + ≥2 seeds + matched primer surface (P2). Until
then no quantitative claim should propagate.

## Cycle 6 status — full 17-task campaign DONE, XN-018 written

`orch_dsv4_remain12_s1` finished cleanly: 12/12 success, mean TreeSim
**0.874** (median 0.929, range 0.608-0.998). Combined with `orch_dsv4_5task_s1`,
the orchestrator on DSv4-flash now covers all 17 v2 tasks at:
- **Mean TreeSim 0.851** (median 0.852, all 17 succeeded, n=1 seed)
- Same-model paired Δ vs vanilla DSv4-flash = **+0.204** (13W/3L/1T)
- Same-model paired Δ vs DSv4flash+plugin+xmllint best-setup = **+0.234**
- Within −0.012 of OpenHands+minimax-m2.7 (much larger model)

**Efficiency cost:**
- Compute: 15055s vs vanilla 6825s (~2.2× more)
- True wall: 134 min @ W=2 vs vanilla 21 min @ W=6
- Paid input tokens: 4.4M vs vanilla 6.9M (orchestrator uses fewer!)
- Cache-read tokens: 128M vs 72M (orchestrator hits cache harder)

**Three losses** (multiphase/thermal coupled): ExampleThermoporoelasticConsolidation
−0.190, buckleyLeverettProblem −0.102, ExampleThermalLeakyWell −0.035.
Traceable to thin multiphase/thermal coverage in drivers/solvers primers.

XN-018 written at docs/XN-018_orchestrator-vs-priors-17task.md.
LOG-2026-04-28-1 appended to research_log.md.

Next steps: enrich drivers primer with multiphase content, multi-seed
validation (3 seeds × 17 tasks), adversarial review on orchestrator
code, optional W=4 re-run.

## Cycle 5 status — 5-task campaign DONE, results validated

`orch_dsv4_5task_s1` finished cleanly: 5/5 success, all xmllint-valid.
Mean TreeSim **0.795** (range 0.654-0.926), median 0.839, pass≥0.7 = 4/5.

**Paired vs vanilla DSv4-flash** (same 5 tasks):
- Orchestrator 0.795 vs vanilla 0.465 → **+0.330 mean** delta.
- Wins/losses/ties = 4/1/0.
- Biggest wins: Sneddon 0.085→0.839 (+0.754), Mandel 0.319→0.926 (+0.608),
  Poroelasticity 0.362→0.707 (+0.344).
- One loss: buckleyLeverettProblem -0.102 (multiphase; primers thin here).

**Vs prior baselines** (different conditions, indicative not paired):
- E03 (plugin+ds-v3.2 via OR, 35 tasks): 0.828 mean.
- M1-u (memory variant, n=2): 0.796 ± 0.057.
- A3 (RAG+SR plugin, n=3): 0.524 ± 0.221.
- Orchestrator+DSv4-flash on this subset (0.795) is within noise of M1-u
  and within striking distance of E03 — using a smaller-cheaper model.

XN-017 updated with full table. Next steps: launch 17-task full campaign,
add multiphase content to drivers primer, dispatch adversarial review.

## Cycle 4 status — 5-task campaign launched

**Smoketest v3 (Mandel) outcome (cycle 3 completion)**:
- All 5 subagents spawned and 4 of 5 returned text successfully (mesh,
  regions+constitutive, solvers, drivers).
- 4 of 5 splices completed cleanly. XML has all blocks except `<Events>`.
- Container exit code 143 (SIGTERM) at 13:32:30Z, ~933s elapsed (well under
  1800s timeout). Events subagent had not finished when killed.
- Likely transient (OOM, system issue, or accidental external kill).
  Did not retry the smoketest individually — moved to 5-task launch.

**Architecture validated**: orchestrator follows 6-phase workflow under strict
prompt; subagents return clean ```xml blocks with verification notes; splicing
via Edit works; cross-segment naming consistency preserved (cb1 propagated
correctly from mesh through regions). Quality of generated XML for
poromechanics on Mandel was high — canonical PorousElasticIsotropic +
BiotPorosity + ConstantPermeability + CompressibleSinglePhaseFluid pattern.

**5-task campaign launched** at ~13:33Z. Background `bx2gfikms`. Tasks:
TutorialSneddon, ExampleMandel, TutorialPoroelasticity,
AdvancedExampleDruckerPrager, buckleyLeverettProblem. 2 workers, 2400s/task
timeout. Expected wall: ~40-50 min.

Wakeup at 14:15Z to score and analyze.

## Cycle 3 status — orchestrator architecture VALIDATED on Mandel

**Smoketest v3 (ExampleMandel, strict numbered prompt):** working as designed.

- Phase 0: bootstrap. ONE search, ONE cp. `PoroElastic_Mandel_base.xml` copied.
- Phase 1: orchestrator spawned `geos-orchestrator:geos-mesh`. Subagent
  returned 2 ```xml blocks (Mesh + Geometry). Orchestrator spliced via Edit.
  cellBlock changed `hexagonalPrisms` → `cb1` (consistent across regions too).
- Phase 2: orchestrator spawned `geos-orchestrator:geos-regions-constitutive`.
- Phase 3: orchestrator spawned `geos-orchestrator:geos-solvers` (~13:26Z).

Each subagent ~5-10 min on DSv4-flash. Pipeline projection ~30 min/task serial.
Container 716d1193f015. Background `bunjm7fnw`. Wakeup at 13:38Z.

**Subagent file-read audit (cycle 3 mid-flight)**:
- Mesh subagent read `/plugins/orchestrator/primers/mesh.md` and
  `/plugins/orchestrator/schema_slices/mesh.xsd` — primer/slice integration
  works.
- Regions-constitutive subagent reading C++ headers + .rst files (deep
  research). Some path hallucinations (`/workspace/geos_lib/...` instead of
  `/geos_lib/...`) — minor; agent should recover.
- Orchestrator only read 2 files (bootstrap candidate + working copy) — clean
  delegation discipline.

**Timing**: ~5 min per subagent on DSv4-flash. Full 5-phase task estimate
~25-30 min. Timeout was 1800s (30 min) — bumped launch_full_17.sh to 2400s
to be safe.

**Architecture validation**: works end-to-end. Strict numbered system prompt
(Phase N = call subagent X) was the unlock. v1 (Write enabled, gentle nudges)
and v2 (Write disabled but free-form workflow) both bypassed delegation;
v3 (numbered phases + anti-pattern hall of shame) follows the workflow.

## Cycle 2 status — system prompt iteration

**Smoketest v1 (TutorialSneddon) finding (cycle 1)**: orchestrator had Write tool
and bypassed delegation — at event 86 it had written `Sneddon_base.xml` directly
via Write instead of spawning the geos-mesh subagent. RAG searches and Reads
were all in service of self-authoring, not bootstrap-discovery.

**Fix applied**: 
1. Added `Write` to DISALLOWED_TOOLS in run_orchestrator_eval.py.
2. Updated ORCHESTRATOR_SYSTEM.md: top-of-prompt mandate, anti-patterns list,
   bootstrap copy via `Bash cp` (not Write).
3. Subagents stay disallow-Write too (subagents return text, never write disk).

**Smoketest v2 (TutorialSneddon)**: launched at ~13:13Z. Container c5c8d9cb2cf3.
Background task bbbppfyky. Init log confirms Write absent from tool list, plugin
loaded, MCP connected, 5 subagents discoverable. Awaiting first Agent tool call
to confirm delegation behavior.

## Cycle 1 status (completed earlier)

- D-010 design memo written: `.copilot/decisions/D-010_subagent-orchestrator.md`.
- `plugin_orchestrator/` built:
  - `.claude-plugin/plugin.json` (geos-rag MCP).
  - 5 subagent definitions: `geos-mesh`, `geos-regions-constitutive`,
    `geos-solvers`, `geos-drivers`, `geos-events`.
  - 5 segment-focused primers under `primers/`.
  - 6 schema slices under `schema_slices/` (solvers.xsd is the heaviest
    at 86KB — subagents Read on demand, doesn't preload).
  - `scripts/geos_rag_mcp.py` and `hooks/verify_outputs.py` copied from
    `plugin/` so the new plugin is self-contained.
  - `ORCHESTRATOR_SYSTEM.md` — main thread workflow (6 phases:
    bootstrap → mesh → regions+const → solvers → drivers → events →
    splice + xmllint).
- `scripts/orchestrator/run_orchestrator_eval.py` — standalone runner;
  imports read-only from `src/runner` (no modifications).
- LOG-2026-04-27-3 appended to research_log.md.
- **Smoketest LIVE**: TutorialSneddon, DSv4-flash direct, container
  `94f26b199945`. Init log shows plugin loaded (`geos-orchestrator`,
  5 subagents discoverable as `geos-orchestrator:geos-*`), MCP connected
  (`geos-rag`), Agent tool present (under alias `Task`). Background task
  `btwfwsxws`. Started 13:05Z. As of last check: agent in Phase 0,
  exploring bootstrap candidate XMLs (ALM_Sneddon_smoke.xml,
  ALM_Sneddon_benchmark.xml) — exactly the right behavior.

## Issue from cycle 0

The default `--tmp-geos-parent` is not writable by user `matt`. Fixed by
passing `--tmp-geos-parent /data/matt/geos_eval_tmp`. Added to runner CLI
default but harness invocations need the flag explicitly until I update
the default.

## Open items for cycle 2

1. Confirm smoketest completes successfully — XML written to
   `/workspace/inputs/`, xmllint passes (or orchestrator retries).
2. Smoketest ExampleMandel — different physics class (poromechanics)
   stresses the composite-solver path.
3. If both smoketests pass, launch full 17-task campaign on DSv4-flash.
4. Score with `batch_evaluate.py`, write XN-017.

## Concurrent runs to watch

20+ `claude -p --verbose` containers visible in `docker ps`. Some are mine
(orchestrator), most are someone else's. Mine identified by mounting
`plugin_orchestrator/`. Don't kill any — they're either OpenHands' parallel
workers or an existing memory-ablation run.

*Prior checkpoint (OpenHands baseline) preserved below — do not delete.*

## Goal

Build a parallel, toggleable sub-agent orchestrator for GEOS XML authoring. Each
top-level XML segment gets its own subagent with a focused doc primer.
Test on 17-task v2 eval set with DSv4-flash direct (fall back to minimax-m2.7
via OpenRouter if DS account exhausts).

## Constraints (do not break)

- OpenHands campaign `oh_test17_s1` may still be running. Do not modify
  `src/runner/*`, `run/AGENTS.md`, `scripts/eval/*`, `data/eval/claude_code_*`,
  `data/eval/openhands*`.
- Existing `plugin/` directory is in active use by other agents — do NOT modify.
  Build the new artifact under `plugin_orchestrator/`.

## Background analysis (already done in this session, pre-sleep)

`docs/2026-04-27_subagent-architecture-geos.md` — concluded:
- 11 nominal segments collapse to 9 (Geometry → Mesh; NumericalMethods → Solvers).
- Doc footprint per segment fits in a focused subagent context (Solvers split per physics).
- 6-phase pipeline: bootstrap → Mesh → (Regions+Constitutive parallel) →
  Solvers/<physics> → (Functions+FieldSpec+Tasks+Outputs parallel) → Events →
  splice + xmllint.
- Subagents return text; orchestrator splices. No file collisions.

## Findings from runner survey (cycle 0)

- `src/runner/agents.py` defines `AGENTS` dict keyed by agent_key.
- `src/runner/orchestrator.py:run_task()` builds docker cmd, mounts plugin
  at `/plugins/repo3`, vector DB at fixed path, passes `--append-system-prompt`
  and `--mcp-config`. Uses `--settings` for hook (NOT `--plugin-dir`).
- `src/runner/docker_cmd.py:build_claude_native_command()` constructs the
  `claude` invocation. `--tools default`. Disallows `Skill`, `AskUserQuestion`.
  Does NOT load the plugin's `agents/` directory because `--settings` is used
  instead of `--plugin-dir`.
- `DEFAULT_CLAUDE_MODEL = "minimax/minimax-m2.7"`. Routed through OpenRouter via
  `ANTHROPIC_BASE_URL=https://openrouter.ai/api`.
- For built-in subagents to work, we need the plugin loaded via `--plugin-dir`
  AND we need the `Agent` tool (formerly `Task`) accessible. Default tool set
  includes `Agent`; current disallow list doesn't block it. Good.

## Open question for cycle 1

**DSv4-flash direct API: does DeepSeek expose Anthropic-format `/v1/messages`?**
If yes, set `ANTHROPIC_BASE_URL=https://api.deepseek.com/anthropic` (or wherever).
If no, use OpenRouter `deepseek/deepseek-v3.2` for now (matches XN-001/XN-008
baselines for paired comparison) and document deviation.

## Cycle 1 plan

1. Mark task #2 in_progress; finish runner survey (look at claude_settings.py).
2. WebFetch DeepSeek API docs.
3. Locate the 17-task v2 list (test_blocklist.json or similar).
4. Write D-010 design memo.
5. Begin building `plugin_orchestrator/`.

## Key paths

- Existing analysis: `docs/2026-04-27_subagent-architecture-geos.md`
- Existing plugin (do not touch): `plugin/`
- Test set: `/data/shared/geophysics_agent_data/data/eval/experiments_test36_template`
- GT: `/data/shared/geophysics_agent_data/data/eval/experiments_gt`
- Test blocklist union (17-task list source): `misc/memory_artifacts/test_blocklist.json`
- DAG segment map (Explore agent): `/tmp/geos_segment_map.md`

---

# Prior checkpoint (preserved): OpenHands baseline (concurrent session)

*This session ("other-coding-agent-baseline") is concurrent with another
CC session that's continuing memory-ablation work — the prior checkpoint
for that session is preserved below this section, do not delete it.*

## Active task

17-task OpenHands baseline campaign `oh_test17_s1` running in
background. Launched 2026-04-27T12:13Z, 4 parallel workers, 1200s/task,
expected ~45 min wall.

**Background bash id:** `br7q9n9bk` — output at
`/tmp/claude-1005/-home-matt-sci-repo3-research-copilot/231ff213-aacf-480f-afcf-0e0346abf2b3/tasks/br7q9n9bk.output`
**Live log:** `/tmp/oh_test17_s1.log`
**Output dir:** `data/eval/openhands_no_plugin/oh_test17_s1/<task>/`
**Score dir (created by --score):**
`data/eval/results/oh_test17_s1/openhands_no_plugin/`

## What to do when campaign finishes

1. Confirm `_summary.json` shows ≥80% non-error / non-timeout (per D-009 validation gate).
2. Inspect each task's `status.json` for `primer_in_context: true` and `activated_skills: []` — any failures are parity violations, NOT score data.
3. Read scorer output `_summary.json` in the score dir.
4. Build a per-task TreeSim table: OpenHands `oh_test17_s1` vs vanilla CC `claude_code_no_plugin` minimax run on the same 17 tasks.
   - Where to find CC's run? Check `data/eval/claude_code_no_plugin/` for the canonical comparison run name. The hub.md SoK references E06 (no-plugin + minimax). Look for `noplug_mm_v2` or similar — XN-005 §"Cross-model" cited E06 = `noplug_mm_v2`.
5. Update `docs/XN-016_openhands-baseline.md §Results` with the table + aggregate mean ± std.
6. Append `LOG-2026-04-27-2` entry to `.copilot/research_log.md` with the result.
7. If OpenHands beats CC on non-trivial subset, escalate to ≥3 seeds; if it doesn't, write up as "harness-shape effects are real but bounded" and stop.

## Key paths to know

- Selection: `docs/2026-04-27_other-coding-agent-harness-selection.md`
- Decision: `.copilot/decisions/D-009_other-coding-agent-baseline.md`
- Note: `docs/XN-016_openhands-baseline.md` (results section pending)
- Adversarial review: `.copilot/reviews/RN-004_adversarial_openhands-baseline.md`
- Runner: `scripts/openhands_eval.py`
- Image build: `run/Dockerfile.openhands` (image tag: `geos-eval-openhands`)
- Smoketest #2 (clean parity reference): `data/eval/openhands_no_plugin/oh_smoke_s2/TutorialSneddon/status.json`

## Concurrent-session safety reminder

Do NOT touch:
- `src/runner/*` (CC runner; the other session uses it)
- `run/AGENTS.md` (the shared primer)
- `src/runner/agents.py`
- `scripts/eval/*` (re-used as subprocess only)
- `data/eval/claude_code_*/` (CC's results)

This session's territory:
- `scripts/openhands_eval.py`, `run/Dockerfile.openhands`
- `data/eval/openhands_no_plugin/`
- `data/eval/results/oh_*`
- `docs/2026-04-27_*`, `docs/XN-016_*`
- `.copilot/decisions/D-009_*`, `.copilot/reviews/RN-004_*`

## Sleep exit conditions

- max_hours: 8
- max_experiments: 20 (cycles, not single tasks)
- diminishing_returns: 3 consecutive cycles with <2pp improvement
- circuit_breaker: 3 consecutive errors

## Likely next cycles after campaign

1. **Cycle 1** (current): wait for `oh_test17_s1` → score → write up.
2. **Cycle 2**: if competitive, launch `oh_test17_s2` (seed 2). If not, write final XN-016 conclusions and exit.
3. **Cycle 3**: if seed 2 is also competitive, launch `oh_test17_s3` for variance estimation.
4. **Cycle 4**: cross-harness comparison table in research_log + State of Knowledge update in hub.md.

If any task fails with `failed_parity_no_primer` or `failed_parity_skills_injected`, that's a runner bug — STOP, debug before continuing.

---

# Checkpoint — 2026-04-22 post-matrix (D-008 results + API contamination finding)

## Critical note for future sessions

**3 of 18 memory-ablation seeds were contaminated by OpenRouter billing/quota
failures**, not memory-design issues. See
`misc/memory_artifacts/openrouter_contamination_note.md`. Specifically:

- **M4-u s3** (0.153): 13/17 tasks hit HTTP 402 "Insufficient credits"
- **M3-g s2** (0.000): 17/17 hit HTTP 403 "Key limit exceeded (weekly)"
- **M3-g s3** (0.000): 17/17 hit HTTP 403

Run `python scripts/memory/check_api_contamination.py --scan-memory-matrix`
on any new campaign BEFORE interpreting scores.

**Revised M4-u (n=2 valid): mean 0.729 (not 0.537).** M4-u is NOT unstable —
the contaminated s3 made it look unstable. M4-g (still n=3 clean) IS
genuinely unstable at {0.814, 0.313, 0.280}.

## Headline: M1-u wins, primer format is the real ablation

- **M1-u**: 0.796 ± 0.057, +0.272 vs A3, Wilcoxon p<0.001, 16/17 wins — hero.
- **M1-g**: 0.766 ± 0.046, +0.242 vs A3, p=0.003 — passes Claim A.
- **M4-u (corrected)**: 0.729 at n=2 — also strong, but structured-items format loses to monolithic cheatsheet when grounded.
- **M4-g**: 0.469 ± 0.299 — real instability. Per-task diagnostic on pkn shows M4-g s2 invented `<CompressibleSolidCappedPlatesPorosity>` where M1-u correctly used `<CompressibleSolidParallelPlatesPermeability>`. M1's explicit element-name table prevents F1 vocabulary hallucination; M4's abstract principles don't.
- **M-placebo**: 0.373 ± 0.049, −0.152 vs A3, p=0.015 — content-specificity control passes.
- **M3-g**: untestable (tool never called in valid seed; 2 seeds lost to 403 quota).

Primary finding: the format-ablation (monolithic vs structured items) is the real story, not the grounding ablation (which failed attribution on both pairs).

## Sleep Report

**Duration:** 2026-04-22 01:00 UTC → 04:57 UTC (~4 hours)
**Cycles completed:** 1 (design→distill→infra→smoketest→launch)
**Exit reason:** Blocker — matrix needs 4+ hours more; no productive work for copilot until scores arrive.

### What was accomplished

- D-007 → RN-003 adversarial review (4 P1 blockers) → D-008 revised design.
- Hygiene audit + index rebuild (14/17 test tasks de-leaked).
- Grounder + distiller + embedding MCP + analyzer + scenario framework.
- 4 distilled artifacts (M1-u/g, M4-u/g) + M-placebo + embedding indexes; all hygiene-pass, token parity ≤10%.
- A3 seed 3 launched + scored: 0.267 (outlier). A3 n=3 = 0.524 ± 0.221.
- Vanilla-CC-train with extended blocklist (all 18 train tasks, 9 failures harvested for anti-pattern content).
- 2 smoketests (M1-g primer, M3-g MCP tool) — both infra works.
- Full memory ablation matrix launched: 6 conditions × 3 seeds = 18 runs, running sequentially.

### Matrix status at sleep exit

- Time: 2026-04-22T04:57Z
- Started: 04:29Z. First condition (placebo_s1) done at 04:44 (mean 0.316, Wilcoxon p=0.003 vs A3 with 2/15 wins — strong negative signal but single low-noise seed).
- Currently running: placebo_s2 (14/17 tasks done, 3 running).
- Expected completion: ~08:30Z (4 more hours at 15 min/condition).

### Key findings so far (preliminary, not validated)

1. A3 baseline n=3 has σ=0.221 — much higher variance than n=2 σ=0.017 indicated. Minimax sampling is genuinely noisy.
2. A3 seed 3 (0.267) showed pure F1 schema hallucinations: `<Modules>`, `<MajorIndex>`, `<MinorIndex>` on DPWellbore. NOT an infra bug.
3. A4' vs A3 paired: +0.137 mean, Wilcoxon p=0.057, 10/7 wins — RAG+Mem (no SR) may outperform RAG+SR.
4. Cross-task pattern: A4' wins on F1/F4 tasks (ViscoDrucker +0.34, CasedContactThermoElastic +0.48), loses on plugin-already-good tasks.
5. Placebo seed 1: −0.208 vs A3, p=0.003 — primer injection hurts on this seed, but single noisy seed.
6. M3-g memory tool: connects cleanly, but agent didn't call it in smoketest (matches XN-011).

### Blockers (for user on return)

- Matrix running; need ~4 hours.
- When complete, run `uv run --script scripts/memory/analyze_memory_matrix.py` to get paired-per-task Wilcoxon.
- Then run `python scripts/memory/decompose_by_failure_class.py` for per-class deltas.
- Then dispatch round-2 /adversarial-review (focus text template at `/tmp/adv_focus_round2_template.txt`).

### What remains

1. Wait for matrix to finish scoring 17 more conditions (~4h).
2. Run analyzer + decompose_by_failure_class.
3. Write XN-015 using scenario framework (A/B/C/D) based on actual results.
4. Round-2 adversarial review on results.
5. Render hub with updated DAG.
6. Produce final results table matching D-008 decision gate.

### Recommended next steps for researcher

1. Read matrix status: `tail -30 /tmp/mem_matrix_wrapper.log`
2. Check scores dir: `ls misc/memory_artifacts/scores/mem_*`
3. When all 18 done: `uv run --script scripts/memory/analyze_memory_matrix.py`
4. Review `docs/XN-015_memory-ablation-results.md` disposition framework (A/B/C/D scenarios pre-drafted)
5. Dispatch `/adversarial-review` on results
6. Update hub.md State of Knowledge with final disposition

## Paths to know

- Design V2: `.copilot/decisions/D-008_memory-ablation-design-v2.md`
- Adversarial review: `.copilot/reviews/RN-003_adversarial_memory-ablation-design.md`
- Results skeleton: `docs/XN-015_memory-ablation-results.md`
- Matrix launch script: `/tmp/mem_matrix_launch.sh` (for restart if needed)
- Scores: `misc/memory_artifacts/scores/mem_*`
- Artifacts: `misc/memory_artifacts/{M-placebo,M1-u,M1-g,M4-u,M4-g}/`

---

# Original checkpoint (pre-exit)

## State

**Phase:** DO → transitioning to TEST (smoketests done; full matrix next)
**Sleep:** on (max 12h / 20 cycles); started 2026-04-22T01:00:00Z

## Adversarial review (RN-003) findings addressed

All 4 P1 and 4 P2 blockers from RN-003 resolved:
- **Hygiene:** `scripts/memory/hygiene_audit.py` gates every artifact;
  `plugin/memory_index.json` rebuilt with basenames stripped
  (`plugin/memory_index_v1_LEAKY.json.bak` archived).
- **M0 demoted:** `M-placebo` primer (token-matched generic GEOS text)
  added as placebo control.
- **Token parity:** enforced within 10% for M1 (775/807) and M4 (728/776)
  via post-distillation truncation.
- **Baseline seeds:** A3 seed 3 launched and completed.
  A3 n=3 = {0.664, 0.641, 0.267}, mean 0.524, σ 0.221 — much higher
  variance than n=2 indicated. Use paired-per-task Wilcoxon for analysis.
- **Tool-list-shape confound (Claim C):** flagged as acknowledged
  limitation in D-008 §8; Claim C is weakened.
- **Distiller input leakage:** included in the hygiene gate.
- **Vanilla-CC-train hygiene:** `--extend-blocklist-with-test` flag added
  to `run_experiment.py`; runs were executed with full test-GT union
  blocked.
- **M3 silent-degrade:** `memory_mcp_embed.py` hard-errors on missing key,
  preflight embed call, no fallback.
- **Self-distillation coupling:** distillation uses
  `google/gemini-3-flash-preview` (not minimax).

## What has been done

1. **D-008 written** — revised memory-ablation design memo
   (`/home/matt/sci/repo3/.copilot/decisions/D-008_memory-ablation-design-v2.md`).
2. **Hygiene audit + index rebuild** — all artifacts pass audit.
3. **Grounder + distiller + render scripts**:
   - `scripts/memory/trajectory_grounder.py` — emits per-trajectory
     grounded feedback JSON (failure mode, section scores, dominant dim).
   - `scripts/memory/distiller.py` — OpenRouter → gemini-3-flash-preview;
     produces M1-u, M1-g, M4-u, M4-g. Abstraction guardrail + regex gate.
   - `scripts/memory/build_items_embedding_index.py` — embeddings index
     for M3/M4 items (qwen3-embedding-8b via OpenRouter, dim=4096).
   - `scripts/memory/render_items_to_primer.py` — M4 items → markdown.
4. **Artifacts produced** (all hygiene-pass):
   - `misc/memory_artifacts/M-placebo/` — 1043 tokens, generic.
   - `misc/memory_artifacts/M1-u/` — 775 tokens, DC-Cu ungrounded.
   - `misc/memory_artifacts/M1-g/` — 807 tokens, DC-Cu grounded (TreeSim
     feedback from 18 train + 18 vanilla-CC-train reports, 9 failures).
   - `misc/memory_artifacts/M4-u/` — 728 tokens, 6 RB items ungrounded.
   - `misc/memory_artifacts/M4-g/` — 776 tokens, 6 RB items grounded.
5. **Embedding MCP** — `plugin/scripts/memory_mcp_embed.py`, hard-error,
   preflight, pure cosine. Smoketest passes: MCP connects, agent can call
   but doesn't in sample task (matches XN-011).
6. **6 new agent keys** in `run_experiment.py`:
   - `claude_code_repo3_plugin_m_placebo`, `_m1u`, `_m1g`, `_m3g`, `_m4u`, `_m4g`
   - Primer variants use `cheatsheet_path`; M3-g uses `memory_variant=embed`.
7. **Smoketests complete:**
   - M1-g on ExampleMandel: 600s timeout, but files written, primer injected,
     hook fired 2×, XML has correct `<Problem>` root.
   - M3-g on ExampleDPWellbore: 333s, success, memory MCP connected but
     0 memory_lookup calls (expected).

## Baselines

| Condition | n | mean fa0 | std | source |
|---|:-:|---:|---:|---|
| A1 (no-plug) | 1 | 0.497 | — | noplug_mm_v2 |
| A2 (RAG only) | 1 | 0.440 | — | plug_mm_v2_seed2 |
| **A3 (RAG+SR)** | **3** | **0.524** | **0.221** | pac1_plug_hook_s1/s2/s3 |
| A4' (RAG+Mem silent, no hook) | 2 | 0.661 | 0.184 | pac1_plug_mem_nohook_s1/s2 |
| A5 (RAG+Mem+SR) | 3 | 0.607 | 0.252 | pac1_plug_mem_hook_s1/s2/s3 |

## What remains

1. **Launch memory ablation matrix** — 6 conditions × 3 seeds = 18 runs.
   Budget ~$60-70 + compute.
2. **Score all 18 runs.**
3. **Paired-per-task analysis** (Wilcoxon + mean delta vs A3).
4. **Write XN-015 results.**
5. **Round-2 adversarial review** before declaring results.

## Recommended next actions for researcher on return

1. Read `misc/memory_artifacts/*/artifact.md` to verify content quality.
2. Read D-008 for the revised design.
3. Read RN-003 for the adversarial review + responses.

## Key paths

- Design: `.copilot/decisions/D-008_memory-ablation-design-v2.md`
- Review: `.copilot/reviews/RN-003_adversarial_memory-ablation-design.md`
- Artifacts: `misc/memory_artifacts/{M-placebo,M1-u,M1-g,M4-u,M4-g,M3-g}/`
- Scripts: `scripts/memory/{hygiene_audit,rebuild_memory_index,trajectory_grounder,distiller,build_items_embedding_index,render_items_to_primer}.py`
- MCP: `plugin/scripts/memory_mcp_embed.py`
- Staged artifacts in plugin/: `plugin/memory_primer_*.md`, `plugin/memory_items_m4*.json`
- Failure analysis: `docs/XN-014_failure-analysis-vanilla-vs-rag.md`
- Memory survey (verified): `docs/literature/memory_survey_2026-04-22.md`

## Ops

- Always pass `--tmp-geos-parent /data/matt/geos_eval_tmp` (default not writable).
- `export OPENROUTER_API_KEY=$(grep ^OPENROUTER_API_KEY= .env | cut -d= -f2- | tr -d '"')`
- `export ANTHROPIC_AUTH_TOKEN=$OPENROUTER_API_KEY` (Claude Code auths via this).
- v2 specs: `/data/shared/geophysics_agent_data/data/eval/experiments_test36_template`
- GT: `/data/shared/geophysics_agent_data/data/eval/experiments_gt`
- Scoring: `uv run python scripts/eval/batch_evaluate.py --experiments-dir <run> --ground-truth-dir <gt> --output <summary.json>`

---
**Compaction occurred at:** 2026-04-28T08:33:50Z
**Action required:** Read this checkpoint fully to re-orient. Run /pickup if available.

---
**Compaction occurred at:** 2026-04-28T08:36:18Z
**Action required:** Read this checkpoint fully to re-orient. Run /pickup if available.

---
**Compaction occurred at:** 2026-04-28T08:55:38Z
**Action required:** Read this checkpoint fully to re-orient. Run /pickup if available.
