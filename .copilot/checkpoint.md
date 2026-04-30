# Sleep checkpoint — overnight 2026-04-30 (Cycle 0)

**Sleep started:** 2026-04-30T11:08:00Z
**Phase:** TEST
**Cycle:** 0
**Max hours:** 6
**Overnight instructions:** `/home/matt/sci/repo3/misc/apr30_overnight_instructions.md`

## What just landed (Task 0 done)

DSv4 ablation campaign C0-C11, 12 cells × 3 seeds × 17 tasks done.
Big summary: `docs/2026-04-30_dsv4-ablation-SESSION-SUMMARY.md`.
- Best cell: **C6** (xmllint hook, no RAG, no memory) at **0.921 ± 0.006**.
- Best q/$: **C9** (drop plugin-prefix) at **11.2 treesim/$**.
- Memory adds nothing on DSv4 (C5/C10/C11 all null over baselines).
- RAG hurts on DSv4 (-0.02 to -0.04, mechanism: replaces filesystem search).

## Currently running

- Smoketest: `abl_cMP_b_memp_on_c7` on `ExampleMandel`. Container
  `distracted_khayyam`. Started 11:05Z, ~7 min wall expected.
- Verifies the per-task `cheatsheet_path_template` wiring works.

## Tasks remaining (in order)

### Task 1: MemP (active — paper notes + library + 17 per-task primers DONE)

Already done:
- MemP paper notes at `docs/literature/LN-002_memp.md`
- Cloned `misc/memp_external/MemP/`
- Distiller `scripts/memory/distiller_memp.py` ran → 18-entry library
  at `misc/memory_artifacts/memp_dsv4/library.json`
- Renderer `scripts/memory/render_memp_per_task.py` ran → 17
  per-task primers at `plugin/memp_per_task/<task>.md`
- Agent variants `abl_cMP_a_memp_on_c2` and `abl_cMP_b_memp_on_c7`
- Runner support for `cheatsheet_path_template` with `{task}` substitution
- Launcher script handles `cMPa` and `cMPb`

Remaining:
1. Wait for cMP-b smoketest to verify wiring works
2. Launch cMPa + cMPb × 3 seeds in parallel (workers=6, ~25 min wall)
3. Score via `bash scripts/score_all_dsv4_ablation.sh`
4. Run analyzer pairs:
   - cMPa vs C5 (MemP per-task vs M1-u monolithic, both no-xmllint)
   - cMPb vs C11 (MemP per-task vs M1-u monolithic, both with full xmllint)
   - cMPa vs C2 (does any memory help, no-xmllint baseline?)
   - cMPb vs C7 (does any memory help, full-xmllint baseline?)
5. Write big summary `docs/2026-04-30_TASK1_memp.md`
6. Write small handoff `docs/2026-04-30_HANDOFF_TASK2_orchestrator.md`
7. Set Cycle=1, move to Task 2

### Task 2: Multi-agent orchestrator refresh

Background reads:
- `docs/2026-04-30_subagent-orchestrator-handoff.md`
- `.copilot/reviews/RN-005_adversarial_orchestrator-17task.md` (3 P1 blockers)

Required updates:
- Adopt xmllint hook (DSv4 best practice)
- Decide on RAG (drop based on DSv4 findings — RAG hurts -0.02 to -0.04)
- Fix the 3 P1 blockers from RN-005:
  1. Cross-test-task GT leakage — wire union_xml into blocklist
  2. `--disallowedTools Write` enforcement (was multi-flag, should be comma-joined)
  3. analyze_17task.py token-sum double-counting
- 3-seed eval

Compare against single-agent best (C6) and orchestrator-prior to claim
multi-agent value.

### Task 3: Self-evolving agent

Design decisions (committed early per overnight):
- Init: BLANK plugin (start from absolute-min primer)
- Schedule: ONLINE periodic update every 6 tasks
- Versioning: per-edit filesystem snapshot at
  `/data/shared/.../self_evolving_v{N}/`

Implementation needed:
- Extend memory pipeline to produce skills + subagents (not just notes)
- Plugin versioning + version→path map
- 17-task eval with periodic agent self-update
- Compare to C6 (human-designed best) and to its own prior versions

CC docs to consult:
- https://code.claude.com/docs/en/sub-agents
- https://code.claude.com/docs/en/agent-sdk/custom-tools

## Cycle counter rules

After each major task completes:
1. Increment Cycle
2. Reset Consecutive_no_improvement and Consecutive_errors to 0 if no incident
3. Update this checkpoint

## Big summary docs to deliver tomorrow

The user wants a list of these in my last message. Plan:
- `docs/2026-04-30_dsv4-ablation-SESSION-SUMMARY.md` (DONE — Task 0)
- `docs/2026-04-30_TASK1_memp.md` (after Task 1)
- `docs/2026-04-30_TASK2_orchestrator.md` (after Task 2)
- `docs/2026-04-30_TASK3_self_evolving.md` (after Task 3)
- `docs/2026-04-30_OVERNIGHT_SUMMARY.md` — master index (write LAST)

## Stopping rules

- max_hours: 6 (target: 17:08Z)
- max_experiments: 20 (cycles)
- diminishing_returns: 3 cycles with <2pp improvement
- circuit_breaker: 3 consecutive errors

## Key paths and ops

- Test: `/data/shared/.../experiments_test36_template/` + GT at `experiments_gt/`
- Output: `/data/shared/geophysics_agent_data/data/eval/dsv4_ablation_2026-04-29/`
- DSv4: `ANTHROPIC_BASE_URL=https://api.deepseek.com/anthropic` + `ANTHROPIC_AUTH_TOKEN=$DEEPSEEK_API_KEY` (in `.env`)
- Always: `--strip-baked-primer`, `--tmp-geos-parent /data/matt/geos_eval_tmp`
- Workers: 6 default
- Scoring helpers: `scripts/score_dsv4_ablation.sh <c> <s>`, `scripts/score_all_dsv4_ablation.sh`
- Analyzer: `scripts/analysis/ablation_analyzer.py`

## Reference table (for context)

Final Task 0 cells of interest:
- C2 (parse-only SR, no RAG): 0.913 ± 0.015
- C5 (C2 + M1-u memory): 0.912 ± 0.003
- C6 (xmllint hook, no RAG, no memory): 0.921 ± 0.006 ← winner
- C7 (xmllint hook + MCP tool, no RAG): 0.914 ± 0.008
- C11 (C7 + M1-u memory): 0.920 ± 0.009

MemP cells will compare to C5 / C7 / C11 directly.
