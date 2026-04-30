# Task 2: Multi-agent orchestrator (P1-fixed re-run)

*2026-04-30 — overnight Task 2. Per `misc/apr30_overnight_instructions.md`.
Companion to `docs/2026-04-30_subagent-orchestrator-handoff.md` (the
prior preliminary writeup).*

## TL;DR

(To fill in once orch_dsv4_postfix_s{1,2,3} land.)

Re-ran the multi-agent orchestrator with the 3 P1 blockers from RN-005
fixed (cross-test-task GT leakage; --disallowedTools comma-joined;
token tally dedup), 3 seeds. The preliminary single-seed +0.204 lift
over vanilla survives / shrinks / inverts: TBD.

## What changed since RN-005

P1A — cross-test-task GT leakage. The orchestrator's bootstrap step
("ONE search, ONE cp") could copy a sibling test-task's GT XML into
the workspace, conflating physics-class similarity with explicit
GT exposure. Fixed in `scripts/orchestrator/run_orchestrator_eval.py`:
union_xml + union_rst from `misc/memory_artifacts/test_blocklist.json`
are now in every per-task blocklist.

P1B — `--disallowedTools` enforcement. Three repeated `--disallowedTools <name>`
flags were silently ignored by Claude Code; comma-joined value is
enforced. Write fired in 4/17 tasks of the preliminary run; this fix
should bring it to 0.

P1C — analyze_17task.py token dedup. JSONL `message.id` re-emission
under subagent fan-out was inflating sums 2–4×. Fixed by deduplicating
on `message.id` before summing.

P3 — status.json now records `started`/`ended` ISO timestamps instead
of falling back to fs mtimes for campaign-wall computation.

## Setup

- 3 seeds: `orch_dsv4_postfix_s{1,2,3}` (parallel, workers=3 per seed = ~9 task-batches concurrent)
- Same plugin (`plugin_orchestrator/` with 5 subagents + per-segment primers + schema slices)
- Same model (DSv4-flash via DeepSeek direct)
- RAG ON (geos-rag MCP loaded for subagents — kept ON to isolate the P1-fix effect; cross-comparison
  with RAG-OFF deferred to follow-up)
- 17 v2 test tasks
- Output: `data/eval/orchestrator_dsv4flash/orch_dsv4_postfix_s{1,2,3}/`

## Results

(TBD)

| condition | mean | σ | n_seeds |
|---|---:|---:|---:|
| orch (preliminary, before P1 fixes) | 0.851 | — | 1 |
| **orch_postfix (3 seeds, P1-fixed)** | **TBD** | **TBD** | 3 |
| C6 (single-agent winner from Task 0) | 0.921 | 0.006 | 3 |
| C2 (single-agent, parse-SR) | 0.913 | 0.015 | 3 |

### Effect of P1A (GT leakage fix)

Tasks where the preliminary run's bootstrap copied a sibling test-task's
GT (per RN-005 trace evidence):
- ExampleIsothermalLeakyWell — copied `thermalLeakyWell_base.xml`
- (others suspected but not enumerated)

Post-fix score on these tasks: TBD.

### Effect of P1B (Write disallowed)

Preliminary run had Write fire on 4 tasks (TutorialSneddon, CCThermo,
ThermalLeakyWell, kgdExperimentValidation). Post-fix Write count
should be 0; resulting scores on those tasks TBD.

### Effect of P1C (token dedup) — accounting only

Doesn't affect treesim. Updated efficiency table:

| metric | orchestrator (post-fix) | C6 single-agent |
|---|---|---|
| compute (Σ per-task elapsed) | TBD | ~6500 s (3 seeds × 17 tasks × 381 s/task / 3 seeds) |
| true wall (start→end) | TBD | TBD |
| paid input tokens (deduped) | TBD | TBD |

## Per-task pattern

(TBD: which tasks does the orchestrator still win on after P1 fixes?
Which lose? Compare to C6's per-task scores.)

## Decision

(TBD)

If post-fix orchestrator ≥ 0.92, multi-agent has merit beyond what
single-agent xmllint achieves. If post-fix ∈ [0.85, 0.92], honest
preliminary number was overstated and the architecture is competitive
but not winning. If post-fix <0.85, the prior +0.204 was driven by
the P1 violations.

## Followups

1. Multi-agent + RAG-off: does dropping the RAG MCP help orchestrator
   the way it helps single-agent? Cross-validates the C0-C5 finding
   on a different harness.
2. Multi-agent + xmllint hook + memory: stack the components from C6
   onto orchestrator subagents.
3. Stage-specific memory: per-subagent memory primer (deferred per
   overnight instructions).

## Cross-references

- Prior preliminary writeup: `docs/2026-04-30_subagent-orchestrator-handoff.md`
- RN-005 review: `.copilot/reviews/RN-005_adversarial_orchestrator-17task.md`
- D-010 design: `.copilot/decisions/D-010_subagent-orchestrator.md`
- Single-agent best (C6) from Task 0: `docs/2026-04-30_dsv4-ablation-SESSION-SUMMARY.md`
