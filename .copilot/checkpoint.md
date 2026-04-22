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
