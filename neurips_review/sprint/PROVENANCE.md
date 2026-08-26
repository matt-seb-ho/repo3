# Provenance table — every number destined for a reviewer

**Rule (hard):** a number may not enter a response text until it has a row here whose *Source* is a path on disk that someone opened, plus the command or script that produced it. No number from a summary doc, a memory, or a subagent's report without opening the file.

Status: `VERIFIED` (re-derived from raw this sprint) · `PROVISIONAL` (verified but a known bug may move it) · `EXCLUDED` (will not be quoted) · `⚠ RETRACTED`.

Root paths, abbreviated below as `$VAL` and `$HO`:
- `$VAL` = `/data/shared/geophysics_agent_data/data/eval/autocamp_2026-05-01`
- `$HO` = `/data/shared/geophysics_agent_data/data/eval/autocamp_followup_2026-05-02`

---

## Verified — safe to quote

| # | Number | Supports | Source | How derived | Status |
|---|---|---|---|---|---|
| **🛑** | **EVERY VAL ROW BELOW IS CONTESTED — the val scoring pass raced the val campaign (finding F52).** Published val numbers cannot be reproduced from the decks now on disk. The *convention* analysis (failures-as-zero vs drop-nulls) stands; the *inputs* do not. **HELD-OUT ROWS ARE UNAFFECTED** — `published == strict` on all 180 runs, worst diff 0.00e+00, cross-verified by two independently written scorers. | | | | **⚠ CONTESTED** |
| 1 | ~~F3 (R+S) val = 0.857, σ 0.045~~ — **raced. True value ≈ 0.887 ± 0.011** | ~~the main-effects correction~~ — **do not publish (H3 = no)** | `$VAL/_results/autocamp_F3_s{1,2,3}/…/_summary.json` scored 14:25:28; its decks written 14:25:41 → 14:32:37 | mtime audit verified by main thread; `artifacts/K2_rescored_val.jsonl` | **⚠ RACED** |
| 1a | **All 11 Table-1 val cells, mean ± σ, exact to 3 dp** | Table 1 is sound | `$VAL/_results/<cell>_s{1,2,3}/<cell>/_summary.json` | same script, 11/11 match | **VERIFIED** ×2 (P0 + D) |
| 1b | **Corrected main effects R −0.037 · S −0.008 · X +0.011 · M +0.008** | the correction, if H3 = yes | derived from #1a's eight cell means | mean(on) − mean(off) over F0–F7, **computed from Table 1's printed 3-dp means** so gep1 reproduces it by hand | **VERIFIED** |
| 1c | Stale published effects −0.032 / −0.003 / +0.007 / +0.004 | what the appendix says | `writing/neurips/neurips_2026.tex:412` | reproduces exactly from the **index-grouped** drop-nulls variant (`analyze_autocamp.py:203-212`) | **VERIFIED as stale** |
| 1d | `S+X+M = autocamp_F8`, `SE-prose = autocamp_F11` | cell-identity map for all later work | matched recomputed mean+σ to Table 1 rows | `artifacts/P0_f3_recompute.py` | **VERIFIED** |
| 2 | **Rung 2: Vanilla 24/30, five adapter cells 30/30** | AC primary objection | `artifacts/A1_rungs12_perfile.csv` (486 rows) ← `$HO/icl/<cell>/…/inputs/*.xml` | `xmllint --noout`, then `--schema data/GEOS/src/coreComponents/schema/schema.xsd`; all-files framing | **VERIFIED** |
| 2a | Denominator exactly 30/cell; exactly 81 XML files/cell | no normalising-away | same | task names byte-identical across all 18 seed dirs | **VERIFIED** |
| 2b | Framing robustness: Vanilla 24 (all files) / 26 (roots) / 28 (scorer entries); adapters 30/30 in all three | pre-empts "why this framing?" | same | three aggregations off one artifact | **VERIFIED** |
| 2c | 3 unparseable + 3 schema-invalid; **0 missing, 0 empty** across all 180 runs | say "unparseable" for held-out, never the full triad | same | per-run worst category | **VERIFIED** |
| 2d | 5/5 unparseable files = `--` inside an XML comment | the mechanism story | `artifacts/A1_rungs12_perfile.log` (verbatim stderr) | — | **VERIFIED** |
| 2e | 6 Vanilla rung-2 failures span 4 distinct tasks; 4 in s3, 2 in s1, 0 in s2 | effective-n caveat | same | — | **VERIFIED** |
| 2f | Scorer silently drops unparseable decks; bias **inflates Vanilla** | volunteered disclosure | `src/eval/judge_geos.py:119-123, 138-140` | code read (A1, corroborated by B) | **VERIFIED** |
| 3 | Invented attribute `initialTimeStep` on `Hydrofracture`; two tensor-attribute type errors | rung-2 failure classes | `artifacts/A1_rungs12_perfile.log` | verbatim `xmllint` stderr | **VERIFIED** |
| 4 | **Claude Code `2.1.119`, all 903 autocamp `system/init` events, zero exceptions** | nBNe Q3 | `$VAL/dsv4/autocamp_F0/autocamp_F0_s1/ExampleThermalLeakyWell/events.jsonl` + campaign sweep | grep; `artifacts/C_recompute/sweep_versions_followup.txt` | **VERIFIED** |
| 4a | Unpinned install | the honest concession | `run/Dockerfile:32` — `RUN npm install -g @anthropic-ai/claude-code` | file read; unchanged since `ef51fbf` | **VERIFIED** |
| 5 | **C2→C6 (S) = +0.00765**, sd 0.02901, t(16)=+1.088, CI [−0.0073, +0.0226] | S/X isolation | raw eval JSONs; `artifacts/C_recompute/recompute_buildup.py` + 378-file manifest | per-task paired, 3 seeds × 17 tasks | **VERIFIED** |
| 5a | **C6→C7 (X) = −0.00720**, sd 0.02887, t(16)=−1.028, CI [−0.0220, +0.0076] | "X buys nothing once S is on" — **not** "X hurts" | same | same | **VERIFIED** |
| 5b | C2→C7 (S+X) = +0.00045 | cleanest single number | same | same | **VERIFIED** |
| 5c | **`n_failed = 0` in all 21 build-up run-cells** | replaces the false "val is at ceiling" | same | count | **VERIFIED** |
| 6 | **C2 0.913398 vs C9 0.916965, Δ = +0.003567**, 0 big-swing tasks, per-task Δ ∈ [−0.0356, +0.0743] | prefix magnitude bound | raw eval JSONs; `artifacts/C_recompute/recompute_autocamp.py` | 3 seeds × 17 tasks | **VERIFIED** |
| 6a | Erroring `geos-rag` calls/task-run: **Vanilla 0.00, SE 0.00**; R− plugin cells F2 0.45, F6 1.96, F11 2.02, F4 2.25, F8 2.61; R+ cells 12–13.5 with ~0 errors | the headline contrast is **prefix-free on both sides** | `events.jsonl` campaign-wide; `artifacts/C_recompute/count_rag_calls.py` | counted independently by C **and** D | **VERIFIED** ×2 |
| 6b | Fix `000b4ba` = 2026-05-03T23:01:37Z; autocamp ran 2026-05-01 12:30 → 2026-05-02 16:28 (**31 h before**) | Table 1 is pre-fix | `git log`/`git show` | — | **VERIFIED** |
| 6c | C1 0.671333 → C0 0.864884 → C2 0.913398, so **C1→C2 = +0.242065** | what "+0.24" actually was | raw eval JSONs | `artifacts/C_recompute/` | **VERIFIED** |
| 7 | **Per-cell held-out σ: Vanilla 0.0809 · X+M 0.0054 · S+X 0.0018 · S+X+M 0.0215 · SE-prose 0.0242 · SE 0.0123** | the σ table; never pair cross-cell mean+σ | `$HO/_results_icl/…/_summary.json` | `artifacts/D_recompute.py`; matches Table 1 | **VERIFIED** |
| 8 | **Vanilla 0.7196 → SE 0.7891, Δ = +0.0695** | headline held-out gain | same | same | **VERIFIED** ×2 (D + A2 to 4 dp) |
| 8a | **Bootstrap: task-clustered 95% CI [−0.0085, +0.1663], P(Δ≤0) = 0.052**; (task,seed) i.i.d. [+0.0008, +0.1550], P = 0.023 | the AC's uncertainty request | same | percentile bootstrap, n_boot = 20,000, `random.Random(31642)`, paired on resampled tasks | **VERIFIED** |
| 8b | SE higher on 7/10 tasks, tied 1, lower 2; **median Δ +0.0221** vs mean +0.0695 | the two rescues carry the mean | same | paired per-task | **VERIFIED** |
| 8c | Per-task: ThermoPoro 0.355→0.761; ProppantTest 0.541→0.825; TutorialHydraulicFracture 0.013 in every cell; other 7 tasks Vanilla mean 0.898 vs val 0.910 | hard-tail representativeness | same | same | **VERIFIED** |
| 9 | Completeness: 561 val + 180 held-out task-runs, **0 missing**; all 51 `_summary.json` aggregates match independent re-derivation to <1e-9 | no silent gaps | same | `artifacts/D_recompute.py` | **VERIFIED** |
| 9a | Factor gating correct in all 11 cells × 3 seeds (`mcp_server_statuses` matches declared R,S,X,M) | rebuts implementation-fidelity doubts | `events.jsonl` `system/init` | D | **VERIFIED** |
| 10 | **Clean-subset null: on the 24 (task,seed) pairs where all six cells are schema-valid, all pairwise Δ within ±0.014, all p ≥ 0.85** — for TreeSim *and* the judge | the separation is failure-driven, not quality-driven | `artifacts/B_deck_scores.csv`, `B_analysis.json` | B | **VERIFIED** |
| 11 | **TreeSim subtree annihilation: 31/90 held-out decks (34%) affected, worst for SE (12/30)** | metric defect, biases against us | `artifacts/B_treesim_annihilation.json`; `src/eval/judge_geos.py` `_bipartite_match` | deterministic scan | **VERIFIED** |
| 11a | `TutorialHydraulicFractureWithAdvancedXML`: reference expands to ~3333 elements vs ~50 generated; costs every cell ≈0.099 identically | common-mode, contrast unaffected | same | — | **VERIFIED** |
| 12 | **At TreeSim 0.963–0.999, 11 of 17 runs differ from reference by 40–99% on primary QoI**; the 2 runs with byte-identical `tables/*.geos` give exactly 0% | **TreeSim never reads the files that set the physics** | `artifacts/A2_qoi_per_run.csv`, `A2_grid_qoi.jsonl` | injected identical `<VTK>` + final-time event in reference *and* generated; mesh-independent reductions; no interpolation | **VERIFIED** |
| 12a | One L4-clean run is **99.97% wrong** (16-cell mesh) | convergence ≠ correctness | same | — | **VERIFIED** |
| 12b | One schema-valid, TreeSim-0.99 deck GEOS refuses: `ElasticIsotropic` with no elastic constants | schema-valid ≠ loadable | `artifacts/A2_scratch/` run logs | — | **VERIFIED** |
| 12c | ThermoPoro QoI errors take only 3 values: 0.00%, 10.47%, 99.97%. Exact reproduction SE 2/3, Vanilla 1/3, F11 1/3, others 0/3 | **tolerance-sensitive — always state the threshold** | `artifacts/A2_qoi_per_run.csv` | 10% tolerance falls between clusters; at ≤15% every cell ≥2/3 | **VERIFIED** |
| 12d | Reference gate: ThermoPoro usable; ProppantTest L0–L3+L5 only; ViscoExtDruckerPrager usable; **ExampleMCCWellbore excluded** (reference hits 600 s cap) | disclosable finding | `artifacts/A2_ref_gate.jsonl` | reference decks run first | **VERIFIED** |
| 12e | **GEOS is bitwise deterministic** (16/16 statistics identical across two runs) | justifies one run/deck; supports "sufficient statistic" | `artifacts/A2_determinism_check.json` | — | **VERIFIED** |
| 13 | **`F0/s3/ExampleProppantTest` root deck loads: `geosx -v` exit 0** despite failing `xmllint` | ⚠ the flagship σ=0.081 failure is a **metric artifact** | `$HO/icl/autocamp_F0/F0_icl_s3/ExampleProppantTest/inputs/` | run by main thread; `benchmark.xml` `<Included>`s `base.xml`; offending text is `Proppant Slot Test -- Base Case` | **VERIFIED** |
| 13a | Vanilla ProppantTest per-seed rung 3: s1 exit 1 (`m_defaultComponentDensity.size() != NC`), s2 exit 0, s3 exit 0 | = 2/3, contradicting A1's 1/3 | same | main thread, root deck only | **VERIFIED** |
| 14 | Hook telemetry: **0 interventions in 410 val invocations; 32 firings in 123 held-out invocations** | mechanistic S/X answer | `.verify_hook_events.jsonl` campaign-wide; `scripts/launch_autocamp_phase2.sh:41-53,64-73,79-90` | F, corroborated by a second independent agent (counts matched exactly) | **VERIFIED** ×2 |
| 14a | S-only cells (F2, F3) ran `GEOS_HOOK_XMLLINT=0` → parse-check only; **the S treatment is not constant across cells** | sharper statement of the construct overlap | `plugin/hooks/verify_outputs.py:331`; `tex:312` | code + launcher read | **VERIFIED** |
| 15 | Real brief: 3672 B, 569 words, md5 `7c34ddc9503378cabd5b8da86515e920`; briefs run 2.2k–6.7k, median ≈4.2k | kEdh worked example | `…/eval/experiments_test36_template/buckleyLeverettProblem/instructions.txt` | **every quoted fragment re-verified verbatim by main thread via `grep -F`** | **VERIFIED** |
| 16 | Real repair-feedback instance; 2-stage repair **succeeded in ~45 s** | kEdh worked example | `…/eval/se_icl_2026-04-30/abl_c6_xmllint_hook/c6_icl_s2/ExampleVerticalPoroElastoPlasticWellbore/events.jsonl` | provenance confirmed `deepseek-v4-flash` (paper's backbone), held-out task; **all fragments re-verified verbatim by main thread** | **VERIFIED** |
| 17 | Resolution-IV alias structure: main effects alias only with 3-factor interactions; pairs {R×S, X×M}, {R×X, S×M}, **{R×M, S×X}** | kEdh + gep1 Q2b | `scripts/analyze_autocamp.py` `F_FACTORS` | machine-checked ±1 coding, 8 runs; `M == R*S*X` True, `I = RSXM` True | **VERIFIED** |
| 17a | Saving: 8 cells × 3 seeds = 24 runs vs 16 × 3 = 48 → **exactly 50% (2×)** | kEdh concrete cost | same | — | **VERIFIED** |
| 18 | "deck" first used `tex:67` (abstract), first defined `tex:111`; **11 uses before definition** | kEdh item 2 | `writing/neurips/neurips_2026.tex` | F, line-by-line | **VERIFIED** |
| 18a | "Resolution-IV" first used `tex:67` (abstract), explained only `tex:157` | kEdh item 1 | same | same | **VERIFIED** |
| 18b | `buckleyLeverettProblem` first used `tex:167`, glossed only `tex:237` (70 lines later, in a parenthetical) | kEdh item 4 | same | same | **VERIFIED** |
| 18c | "strictly perfect" first used `tex:86`, operationalised only `tex:216` as TreeSim ≥ 0.999 | kEdh item 2 | same | same | **VERIFIED** |

## PROVISIONAL — verified but a known bug may move them

| # | Number | Why provisional |
|---|---|---|
| 19 | **Rung 3: Vanilla 18/30 · X+M 21/30 · S+X 20/30 · S+X+M 21/30 · SE-prose 23/30 · SE 23/30**; GT-passable subset 17/21 vs best 21/21; authoring-only 21/30 vs 24–27/30 | A1's root detection misclassifies `<Included>` fragments as roots when the parent fails strict XML parsing (#13a shows 2/3 where A1 reports 1/3). **Can only penalise Vanilla**, so it inflates our gap. A1 re-deriving with GEOS-tolerant include recovery. **Do not post until corrected.** |
| 20 | `missing_external_asset` = 32/273 deck-runs, largest category, distribution F6 9 · F8 9 · F4 7 · F0 4 · F11 2 · SE 1 | A1 said my "adapter cells write more faithful decks" hypothesis is wrong and the real explanation differs; awaiting it. A2 had the *same* failure mode as its own harness bug. |
| 21 | ProppantTest rung-5 QoI | A2 flags it `qoi_provenance` — pre-bug-fix pass. Needs re-run before quoting. |

## ⚠ RETRACTED — reported to the user earlier, must not be used

| Claim | Why retracted |
|---|---|
| "Vanilla 1/3 vs adapters 3/3 — first execution-level evidence for the reliability claim" | A2's pre-fix table. After fixing three of its own harness bugs, Vanilla is **2/3** and the contrast is indistinguishable at n=3. **No execution-level rescue may be claimed.** Never entered a draft. |
| "The ceiling control worked — execution outcomes are identical where TreeSim is at ceiling" | **The opposite is true** (#12). Both oddities were A2 harness bugs. Never entered a draft. |
| "An unparseable file does not run in any simulator under any metric" | GEOS's pugixml tolerates `--` in comments where `xmllint` and ElementTree do not (#13). Was in all four drafts; corrected everywhere. |
| "Val is at ceiling for every cell" | False — means 0.913–0.921, worst task 0.77, only 3/17 tasks ≥0.99. Replaced with `n_failed = 0` (#5c). Was in drafts; corrected. |

## Numbers FORBIDDEN in any response

| Forbidden | Why | Correct alternative |
|---|---|---|
| "+0.24" for the prefix effect | mis-citation; it was the C1→C2 lift being *explained* | **+0.004** (#6, #6c) |
| "Table 1 is post-prefix-fix" | fix landed 2026-05-03, factorial ran 2026-05-01/02 | pre-fix; only minimax × X+M was re-run |
| "the bug fix produced the arXiv main-effects numbers" | no re-run occurred | a derived table computed under the wrong convention (#1c) |
| a mean from one cell paired with a σ from another | abstract pairs +7 pp (SE) with 40× (S+X); S+X is 44.5× at +0.061, SE is 6.56× at +0.069 | print the per-cell σ table (#7); do not volunteer |
| schema validity as "the execution evaluation" | rung 2 of 5, and rung 3 is much weaker | name the ladder and the rung reached |
| the execution plan's TreeSim description (§4.4) | wrong — actual scorer is `|matching attrs| / |union of attr keys|`, no name bonus, no 0.6 scaling; greedy not optimal; root attrs excluded | say only "a tree match at 1e-6 tolerance" |
| "+0.19 for stripping the workflow primer" | C0→C2 changes primer *and* plugin together | do not quote until re-checked (H14) |
| "4× the runs" for a full factorial | arithmetic error in the arXiv draft (`arxiv:282`) | **2×** — 8 of 16 corners (#17a) |
| the LMaaJ score table | fails four reliability checks; one judge reverses our central contrast | report as built-tested-rejected (H15) |
| any verbatim arXiv sentence | preprint may be public → anonymity risk | paraphrase; all kEdh replacement prose written fresh |
| a delivery date for pending experiments | a missed promise lands right before Phase 3 | "we will post what lands" |
