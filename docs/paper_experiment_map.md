# Paper ⇄ Experiment Map

*Index linking each section of the NeurIPS/arXiv paper to the experiment
documentation that backs it (run commands, output directories, scores,
takeaways). Maintained by hand; update when a paper section's evidence
changes.*

- **Paper source**: `writing/arxiv/neurips_2026.tex` (newest; `writing/neurips/`
  and `writing/prev_neurips/` are older snapshots).
- **Method name in paper**: SIGA (Simulator-Interface Grounding Adapter).
  Factors: **R** retrieval, **S** stop-hook, **X** xmllint MCP, **M** memory.
- **Backbone for all headline runs**: `deepseek-v4-flash` via DeepSeek's
  Anthropic-compatible endpoint (`https://api.deepseek.com/anthropic`).

## Canonical references

| Thing | Location |
|---|---|
| Shared data root | `/data/shared/geophysics_agent_data/data/eval/` |
| Repo-local eval data | `/home/matt/sci/repo3/data/eval/` |
| Per-run config (resolved) | `<run>/<task>/eval_metadata.json` (model, base_url, primer, plugin, blocklist) |
| Per-run quality summary | `_results/<run>/<agent>/_summary.json` (TreeSim, per-task scores) |
| Per-run wall-clock | `<run>/<task>/status.json` → `elapsed_seconds` |
| Per-run tokens / SDK cost | `<run>/<task>/events.jsonl` result event (`usage`, `total_cost_usd`) |
| Cell → factor mapping | `scripts/analyze_autocamp.py` (`F_FACTORS`) |
| **DeepSeek cost constants** | `scripts/oh_dsv4_compare.py:56` — see Cost section below |
| Per-simulation cost/wall tool | `scripts/paper_sim_cost.py` (added 2026-05-27) |

## Section-by-section map

### §3 Background — GEOS as a DSL
- **Docs**: `plugin/GEOS_PRIMER_contract.md`, `docs/xmllint_validation.md`,
  `docs/2026-04-27_xmllint-validation-summary.md`.
- **Data/output**: ground-truth decks `…/data/eval/experiments_gt/`.

### §4 Method — design-space components (R/S/X/M)
- **Docs**: `docs/2026-04-28_plugin-reconciliation-and-bottlenecks.md`,
  `docs/xmllint_validation.md`, plugin primer/hook sources under `plugin/`.
- **Component cell definitions**: paper App. "Cell definitions"; code in
  `scripts/analyze_autocamp.py` `F_FACTORS`.

### §4.2 Self-evolved adapter (SE) — "can the adapter be discovered automatically?"
- **Docs**: `docs/2026-04-30_TASK3_self_evolving.md` (results),
  `docs/2026-04-30_TASK3_self_evolving_DESIGN.md`,
  `docs/2026-05-02_v4_design_proposal.md`,
  `docs/2026-05-02_F0_vs_SE_trajectory_diff.md`.
- **Artifact**: `plugin_evolving/v3` (the DSv4-validated self-evolved plugin).
- **Data**: SE cell = `autocamp_2026-05-01/dsv4/autocamp_SE/` (see Table 1 below).

### §5 Evaluation setup — benchmark, splits, metric
- **Docs**: `docs/evaluation.md`, `docs/XN-011_failures-as-zero-reframe.md`
  (failures-as-zero convention), `docs/2026-05-03_icl10-gap-investigation.md`
  (val vs held-out split rationale).
- **Splits**: `…/data/eval/split.json`; 46-task pool → 17 val + 10 held-out (ICL) + 18 distillation.
- **Metric**: TreeSim (`metric: judge_geos`/`treesim` in `_summary.json`).

### §6.1 Main results — Resolution-IV factorial (Table 1) — THE headline experiment
- **Cells (Table 1 order → autocamp dir)**: Vanilla=`F0`, R+M=`F1`, S+M=`F2`,
  R+S=`F3`, X+M=`F4`, R+X=`F5`, S+X=`F6`, R+S+X+M=`F7`, S+X+M=`F8`,
  SE-prose=`F11`, SE=`SE`.
- **Docs**: `docs/2026-05-02_autonomous-campaign-results.md` (scores + analysis),
  `docs/2026-05-02_autocamp_metrics.md`,
  `docs/2026-04-30_dsv4-ablation-final-v2.md` (earlier C0–C9 campaign that drove
  cell selection — note: superseded pricing, see Cost section),
  `docs/2026-04-30_dsv4-ablation-runbook.md` (exact run commands),
  `docs/2026-05-03_harness-sequencing.md` (which commit produced the results).
- **Data (val 17 × 3 seeds)**: `…/autocamp_2026-05-01/dsv4/autocamp_{F0,F1,F2,F3,F4,F5,F6,F7,F8,F11,SE}/`.
- **Data (held-out-eval 10)**: `…/autocamp_followup_2026-05-02/icl/` (results in `_results_icl/`).
- **Run commands**: `scripts/launch_autocamp_phase2.sh` (F0–F7),
  `scripts/launch_autocamp_followup_derisk.sh` (F8, F11).
- **Headline**: val cluster 0.857–0.921; held-out-eval 0.720 (Vanilla) → 0.789 (SE), Δ=+0.069.

### §6.2 Bottleneck analysis
- **Docs**: `docs/2026-05-02_bottleneck-analysis-pipeline.md`.
- **Code**: `scripts/bottleneck/{extract.py,aggregate.py,run_scaleup.sh}`.
- **Classifier models**: `deepseek-v4-flash` (per-task), `deepseek-v4-pro` (synthesis).

### §6.2 Efficiency + cost
- **Docs**: `docs/2026-05-02_efficiency-table.md` (tools/turns/wall per cell).
- **Code**: `scripts/efficiency_table.py` (efficiency), `scripts/paper_sim_cost.py` (cost/wall).
- **Headline (per individual simulation setup, 561 runs = 11 cells × 3 seeds × 17 val tasks)**:
  wall-clock **≈ 314 s (5.2 min)** median 286 s; DeepSeek API cost **≈ $0.012/run**
  off-peak (~$0.025 on-peak). See Cost section for pricing.

### §6.2 Memory-as-retrieval — clean negative result
- **Docs**: `docs/XN-015_memory-ablation-results.md`,
  `docs/XN-003_memory-experiment-negative.md`,
  `docs/2026-04-30_TASK1_memp.md`, `docs/ablation_C11_vs_cMPb.md`,
  `docs/ablation_C7_vs_cMPb.md`, `docs/ablation_C5_vs_cMPa.md`.

### §6.3 Human baseline
- **Docs**: `docs/human_study_protocol.md` (protocol),
  `docs/2026-05-04_human-baseline-browser-analysis.md` (browser-history breakdown),
  `writing/prev_neurips/2026-05-07_human-baseline-update.md`.
- **Data**: participant browser-history exports + submitted decks (P1, P2);
  agent comparison on `buckleyLeverettProblem`.
- **Headline**: 1h participants timed out at ~47–48 min (deck-level 0.540/0.527);
  agent ~5–7 min; P1 no-cap ~3 h (0.931) ≈ 36× agent wall-clock.

### §6.4 Agent autonomy — consult_supervisor / difficulty ramp
- **Docs**: `docs/2026-05-04_interactive-autonomy-results.md` (+ `_autotable.md`),
  `docs/2026-05-03_interactive-autonomy-{design,plan,status}.md`.
- **Data**: `/home/matt/sci/repo3/data/eval/interactive_autonomy_2026-05-03/`,
  `…/experiments_relaxed_{medium,hard}/`.
- **Cost/wall (from paper App.)**: 64 runs ≈ $4.20 (off-peak) ~2 h; +V1 rerun ≈ $2 ~55 min.
- **Headline**: supervisor invoked 2/64 (3.1%); on-disk example library substitutes for consultation.

### §6.5 + App — Cross-simulator transfer (OpenFOAM) — IN SIBLING REPO
- **Repo**: `/home/matt/sci/repo3_openfoam/` (separate from this repo).
- **Docs**: `repo3_openfoam/docs/openfoam/2026-05-07_openfoam_methods_experiments_results_analysis.md`,
  `…/2026-05-07_openfoam_latex_integration.md`.
- **Data**: `repo3_openfoam/data/openfoam_runs/repo3_openfoam_ablations/`.
- **Headline**: best cell R+S 0.871 vs vanilla CC 0.466 vs Foam-Agent (lint-only) 0.569; S dominates.

### App — Cross-model & cross-harness panels
- **Docs**: `docs/2026-05-04_cross-cutting-paper-section.md` (paper-ready, with provenance),
  `docs/2026-05-03_cross-model-results.md`, `docs/2026-05-03_cross-harness-results.md`,
  `docs/2026-05-03_cross-cutting-summary.md`, `docs/XN-016_openhands-baseline.md`,
  `docs/2026-05-03_minimax-pseudo-tool-call-analysis.md`.
- **Data (cross-model, CC × {minimax, gemini})**: `…/cross_model_2026-05-03/{minimax,gemini}/`
  (⚠ some raw aggregates were in ephemeral `/tmp/cm_*.json` — see Gaps).
- **Data (cross-harness, OpenHands × DSv4)**: `/home/matt/sci/repo3/data/eval/openhands_no_plugin/oh_{vanilla,xm}_test17_s{1,2,3}/`.

### App — Native-plugin-prefix bug (contaminates R main effect)
- **Docs**: `docs/2026-04-27_vanilla-cc-stale-plugin-call-bug.md`,
  `docs/2026-05-03_minimax-pseudo-tool-call-analysis.md`, `docs/ablation_C2_vs_C9.md`.
- **Fix**: `src/runner/orchestrator.py:276` (commit `000b4ba`).

## Cost & token accounting (read before quoting any $ figure)

**Canonical DeepSeek V4-flash pricing** (`scripts/oh_dsv4_compare.py:56`):

| Token type | $/1M (off-peak) |
|---|---|
| Input, cache-miss | **0.14** |
| Input, cache-read (cache hit) | **0.0028** |
| Output | **0.28** |

Cost per run = `(input − cache_read)·0.14 + cache_read·0.0028 + output·0.28` per 1M.
On-peak (standard) is ~2× these. Cache-reads dominate token *volume* (~914k/run vs
~33k fresh input) but, at $0.0028/M, contribute only ~20% of cost. Of the ~$0.0124
mean run cost: fresh input ~37%, output ~43%, cache-reads ~20%.

**Two traps that produced wrong numbers in earlier docs:**
1. `docs/2026-04-30_dsv4-ablation-final-v2.md` quotes `$0.27/$0.07/$1.10`
   (cache-miss / cache-hit / output). These are **stale V3-era prices** and
   over-estimate cost ~8×. Use the constants above.
2. The `total_cost_usd` field logged in `events.jsonl` is computed by Claude
   Code at **Anthropic/Claude rates** (~$0.77/run here), NOT DeepSeek. The
   OpenRouter cost-patcher (`src/runner/cost.py`) only corrects OpenRouter runs;
   DeepSeek-direct runs were never re-priced, so their `total_cost_usd` is wrong
   for DeepSeek. Recompute from `usage` token counts.

**Token-recording / pricing modules that exist today** (scattered — candidate for consolidation):
- `src/eval/token_usage.py` / `scripts/eval/sum_billed_tokens.py` — sums billed
  input/output from OpenAI-format `usage` logs (no $ pricing).
- `scripts/oh_dsv4_compare.py` — the only place with correct DeepSeek $ constants.
- `scripts/analyze_autocamp.py` — records per-task `(input, cache_create, cache_read, output)`.
- `scripts/paper_sim_cost.py` — per-simulation cost/wall over the Table 1 runs.

→ **Recommendation**: factor the constants + `events.jsonl`/`status.json` token
extraction into one `src/eval/pricing.py` so every cost figure derives from a
single source of truth instead of hand-typed numbers in markdown.

## Gaps / caveats
- **OpenFOAM** lives in the sibling repo `repo3_openfoam/`, not here.
- **Cross-model raw aggregates** were partly written to `/tmp/cm_*.json` (ephemeral;
  may no longer exist). Per-run trajectories under `cross_model_2026-05-03/` persist.
- **OpenHands cross-harness runs lack token/cost data** (harness wrapper does not
  preserve usage); paper omits OH cost.
- **Cross-model is single-seed**; held-out-10 cross-model not run.
