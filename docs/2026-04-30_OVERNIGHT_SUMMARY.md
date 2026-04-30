# Overnight session 2026-04-30 — master index

*Read this first tomorrow morning. Single entry point to overnight work.*

## What got done

| Task | Doc | Status |
|---|---|---|
| Task 0: DSv4 ablation campaign C0-C11 | `docs/2026-04-30_dsv4-ablation-SESSION-SUMMARY.md` | DONE (12 cells × 3 seeds) |
| Task 1: MemP procedural memory | `docs/2026-04-30_TASK1_memp.md` | TBD |
| Task 2: Multi-agent orchestrator (P1-fixed) | `docs/2026-04-30_TASK2_orchestrator.md` | TBD |
| Task 3: Self-evolving agent | `docs/2026-04-30_TASK3_self_evolving.md` | TBD |

## Headlines

(Will fill in after each task completes.)

### Task 0 (already done before sleep)

DSv4 build-up ablation, 12 cells × 3 seeds × 17 v2 tasks.

| Cell | Setup | Mean | σ |
|---|---|---:|---:|
| C1 (prior) | min primer, no plugin | 0.671 | 0.014 |
| C0 | abs-min primer, no plugin | 0.865 | 0.067 |
| C2 | min primer + plugin (no RAG), parse-SR | 0.913 | 0.015 |
| C5 | C2 + M1-u memory | 0.912 | 0.003 |
| **C6** | **min primer + xmllint hook, no RAG** | **0.921** | 0.006 |
| C9 | C2 minus user-prompt prefix | 0.917 | 0.016 |
| C11 | C7 + M1-u memory | 0.920 | 0.009 |

Best mean: **C6** (xmllint hook, no RAG, no memory).
Best q/$: **C9** (drop the prefix for free 13% cost cut).

Refuted: RAG-helps-xmllint, prefix-drives-C2-lift, memory-helps,
xmllint-MCP-better-than-hook, mem+xmllint-compose.

### Task 1: MemP

(TBD)

Tested per-trajectory procedural memory with cosine retrieval (Fang
2025) against existing M1-u Dynamic-Cheatsheet memory.

| cell | setup | mean | σ |
|---|---|---:|---:|
| **cMPa** | C2 + MemP per-task | TBD | TBD |
| **cMPb** | C7 + MemP per-task | TBD | TBD |

Decision: TBD (best memory recipe).

### Task 2: Multi-agent orchestrator (P1-fixed)

(TBD)

Re-ran orchestrator with the 3 P1 fixes from RN-005 (cross-test-task
GT leak, --disallowedTools comma-joined, token dedup) at 3 seeds.

| condition | mean | σ |
|---|---:|---:|
| orch (preliminary, single-seed, before P1 fixes) | 0.851 | — |
| **orch_postfix (3 seeds, P1-fixed)** | TBD | TBD |
| C6 (single-agent winner) | 0.921 | 0.006 |

Decision: TBD (does orchestrator beat single-agent?).

### Task 3: Self-evolving agent

(TBD)

Implemented blank-init self-evolving plugin with 3 reflection rounds.
Agent edits `plugin_evolving/v{N}/{PRIMER,memory,skills,agents}/` between rounds.

| version | description | mean (on round-N tasks) |
|---|---|---:|
| v0 (blank scaffolding) | | TBD |
| v1 (after reflecting on round 0) | | TBD |
| v2 (after reflecting on round 1) | | TBD |
| v3 (final, re-runs round 0 tasks) | | TBD |

Decision: TBD (does v3 beat v0? does v3 beat C6?).

## Cross-task sanity checks

- All experiments use 17 v2 test tasks at
  `/data/shared/.../experiments_test36_template/`
- All use DSv4-flash via DeepSeek direct (`https://api.deepseek.com/anthropic`)
- All write to `/data/shared/geophysics_agent_data/...`
- All multi-seed (3 seeds standard, sometimes more)
- All scored against `/data/shared/.../experiments_gt/` via XMLTreeSim metric
- All paired analyses use `scripts/analysis/ablation_analyzer.py`

## Files created this overnight

### Documentation
- `docs/2026-04-30_OVERNIGHT_SUMMARY.md` (this file)
- `docs/2026-04-30_TASK1_memp.md`
- `docs/2026-04-30_TASK2_orchestrator.md`
- `docs/2026-04-30_TASK3_self_evolving.md`
- `docs/2026-04-30_TASK3_self_evolving_DESIGN.md`
- `docs/2026-04-30_HANDOFF_TASK1_memp.md`
- `docs/2026-04-30_HANDOFF_TASK2_orchestrator.md`
- `docs/2026-04-30_HANDOFF_TASK3_self_evolving.md`
- `docs/literature/LN-002_memp.md`
- `docs/literature/memp_2508.06433v4.{html,md}`
- `docs/literature/cc_subagents.{html,md}`
- `docs/literature/cc_custom_tools.{html,md}`

### Scripts and infrastructure
- `scripts/memory/distiller_memp.py` — MemP per-trajectory distillation
- `scripts/memory/render_memp_per_task.py` — cosine retrieval + per-task primer
- `scripts/orchestrator/launch_3seed_postfix.sh` — orchestrator P1-fixed re-run
- `scripts/self_evolving/run_round.sh` — single SE round
- `scripts/self_evolving/reflect.py` — agent reflection + plugin evolution
- `scripts/self_evolving/run_full_evolution.sh` — full 3-round SE evolution

### Plugin / artifacts
- `plugin/memp_per_task/<task>.md` — 17 per-task MemP primers
- `plugin_evolving/v0/` — initial blank SE plugin scaffold
- `misc/memory_artifacts/memp_dsv4/library.json` — 18-entry MemP library
- `misc/memp_external/MemP/` — MemP repo clone (gitignored)

### Code changes
- `src/runner/orchestrator.py` — added `cheatsheet_path_template` (per-task
  cheatsheet substitution) + `add_native_plugin_prefix` flag
- `src/runner/agents.py` — new variants: `abl_se_round`,
  `abl_cMP_a_memp_on_c2`, `abl_cMP_b_memp_on_c7`,
  `abl_c10_xmllint_hook_mem`, `abl_c11_xmllint_full_mem`
- `scripts/orchestrator/run_orchestrator_eval.py` — P1A/B/P3 fixes
- `scripts/orchestrator/analyze_17task.py` — P1C fix (token dedup)
- `scripts/score_{,all_}dsv4_ablation.sh` — handle new cells

## What did NOT get done (out of scope or descoped)

- **MemP grounded distillation variant** — would need failure trajectories;
  our train trajectories all succeeded under C2 setup.
- **Online MemP updates** — overlaps with Task 3's self-evolving agent.
- **Stage-wise memory for orchestrator subagents** — explicitly descoped
  per overnight instructions.
- **Multi-seed orchestrator** with both RAG ON and RAG OFF — only one
  condition (RAG ON, P1-fixed) due to time budget.
- **Self-evolving agent variants exploring init choice** (blank vs
  hand-best-setup) — committed to blank early per overnight instructions.

## Plus the prior session's state

- `docs/2026-04-30_subagent-orchestrator-handoff.md` — orchestrator
  background (pre-overnight context)
- `docs/2026-04-30_dsv4-ablation-runbook.md` — every command for the
  Task 0 campaign
- `.copilot/reviews/RN-005_adversarial_orchestrator-17task.md` — the
  P1 review that drove Task 2's P1 fixes

## Cost / wall (overnight only, after Task 0 ended at 11:08Z)

| Phase | task-runs | Real $DSv4 | Wall |
|---|---:|---:|---|
| MemP distillation (build) | 18 + 17 embeds | $0.40 | 5 min |
| MemP eval (cMPa+cMPb × 3 seeds) | 102 | ~$5 | ~30 min |
| Orchestrator postfix (3 seeds) | 51 | ~$8 | ~3h |
| Self-evolving (3 rounds + final) | ~23 | ~$2 | ~2h |
| **Subtotal overnight** | **~194** | **~$15** | **~5-6h** |

## Stopping criteria status

- max_hours: 6 (target 17:08Z)
- Current: TBD
- Cycles: TBD
