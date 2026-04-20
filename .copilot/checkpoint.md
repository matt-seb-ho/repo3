# Checkpoint

## Current state (2026-04-20 late afternoon)

- **E03 plugin win on deepseek (POSITIVE):** +0.178 TreeSim paired. XN-001.
- **E04 long cheatsheet on deepseek (NEGATIVE):** -0.322, 3 redacted_thinking failures. XN-003.
- **E05 short cheatsheet on deepseek (NEGATIVE):** -0.270, same failure pattern. XN-004.
- **E06 cross-model minimax (POSITIVE):** +0.102 paired on 15 tasks. XN-005.
- **E07 filetree on deepseek (RUNNING):** in flight, 12 tasks started, ~30-45 min to finish.
- Advisor brief XN-006 drafted.
- Reviewer audit RN-001 addressed (5 majors fixed).
- CC native memory confirmed no-op.

## In-progress
- tree_run1 bg task (filetree injection test on 17 test tasks, deepseek-v3.2, workers=12)

## Plan if time after E07
- Multi-seed E03 replication — firms up main claim (~40 min at workers=12)
- Pre-advisor hub SoK final refresh (10 min)

## Key paths
- DAG: `.copilot/method_tree.jsonl` (17 nodes: 4 Assumed, 7 exploring, 4 good, 2 negative)
- Notes: docs/XN-001 through XN-006; D-001; RN-001
- Cheatsheets: plugin/cheatsheet.md (long, E04), plugin/cheatsheet_short.md (E05), plugin/filetree.md (E07)
- Scoring results:
  - E03: /data/shared/.../results/repo3_eval_run4/claude_code_repo3_plugin/
  - E04: /data/shared/.../results/mem_run1/claude_code_repo3_plugin_mem/
  - E05: /data/shared/.../results/memshort_run1/claude_code_repo3_plugin_memshort/
  - E06: /data/shared/.../results/mm_noplug_run1/claude_code_no_plugin/
- Compare outputs: misc/e03_vs_e01.txt, misc/e04_vs_e03_test17.txt, misc/e06_vs_e02.txt

## Operational findings
- workers=12 safe on this machine (128 CPU, 900GB RAM, 3 L40S GPUs idle)
- OpenRouter: no 429s at workers=12 for either deepseek or minimax
- Minimax is ~3x faster per task than deepseek (17 tasks in 17 min wall)

## Known gaps / issues
- Single seed everywhere
- ExampleSPE11b timeout (E03) — mis-framed earlier as parse error, now corrected
- 2 XML ParseErrors in E06 (minimax no-plugin): ExampleThermalLeakyWell, TutorialPoroelasticity
- Opus 4.6 cross-model: not tested (cost-deferred)
- Plugin attribution I11 (skill vs MCP): not tested
- Difficulty-tier extension: not tested

## Open blockers
None.
