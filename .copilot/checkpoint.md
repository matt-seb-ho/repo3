# Checkpoint — autocamp followup + bottleneck analysis (2026-05-02 17:35Z, COMPLETE)

## Status
**All scheduled work done.** Researcher returns to:
- 6 derisk runs scored (F8 + F11 × 3 seeds × 17 tasks)
- 18 ICL-10 cell-seed runs scored (6 cells × 3 seeds × 10 tasks)
- 6 train-19 cell-seed runs scored (2 memory-free cells × 3 seeds × 19 tasks)
- Bottleneck pipeline run on Phase 2 (255 tasks), derisk (102), ICL-10 (179),
  train-19 (114), with paper-grade DSv4-pro syntheses.

## Headline numbers

| set | F0 | F4 | F6 | F8 | F11 | SE |
|---|---:|---:|---:|---:|---:|---:|
| test-17 (Phase 2, n=51) | 0.910 | **0.921** | 0.917 | 0.911 | 0.897 | 0.919 |
| ICL-10 scaleup (n=30)   | 0.720 | 0.768 | 0.781 | 0.783 | 0.775 | **0.789** |
| train-19 scaleup (n=57) | 0.867 | — | 0.869 | — | — | — |

**Key finding**: ICL-10 (out-of-distribution) is where adapter wins
emerge. test-17 and train-19 show <1pp F0→best deltas; ICL-10 shows
+6.9pp. The "no plugin needed" claim is benchmark-specific.

## Documents (all under /home/matt/sci/repo3/docs/)
- `XN-019` Phase 2 bottleneck analysis (paper-ready, with case studies)
- `XN-020` Phase 2 + derisk combined (paper-ready, with caveats)
- `XN-021` ICL-10 bottleneck analysis (paper-ready, with caveats)
- `XN-022` train-19 bottleneck analysis (paper-ready)
- `2026-05-02_bottleneck-analysis-pipeline.md` pipeline design doc
- `2026-05-02_autocamp-followup-plan.md` updated with derisk numbers
- `2026-05-02_autonomous-campaign-results.md` updated with REVISED TL;DR

## Pipeline scripts (under /home/matt/sci/repo3/scripts/bottleneck/)
- `extract.py` Stage 1: mine treesim_detail + trajectory features
- `llm_per_task.py` Stage 2: per-task DSv4-flash diagnosis
- `aggregate.py` Stage 3: aggregate + DSv4-pro narrative
- `run_phase2.sh` end-to-end Phase 2
- `run_scaleup.sh` end-to-end scaleup (ICL + train)

Total cost: ~$5-7 of DeepSeek API spend (650 DSv4-flash calls + 4 DSv4-pro narratives).

## Possible follow-ups (not done)
- Run bottleneck pipeline on cross-model data (minimax/gpt-oss) — interesting
  but lower priority for the paper since model-capability is the dominant
  story there.
- Cross-task delta analysis (which specific tasks does F8 fix that F4 doesn't?)
  — would refine the "what does SR-hook add" question.
- Adversarial review of the bottleneck pipeline (DSv4-flash labels are
  not adjudicated; recall the 10% parse-error rate at 2000 max_tokens,
  fixed by bumping to 4000).
