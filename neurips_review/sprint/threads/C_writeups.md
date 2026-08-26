# Thread C — Verification and writeups (C1 S/X, C2 prefix probe, C3 +0.24 fix, C4 CC version)

Started 2026-07-26. Working dir `/home/matt/sci/repo3`.
Artifacts: `neurips_review/sprint/artifacts/C_recompute/`

**Standing rule for this thread:** every number below traces to a file on disk that
I opened in this session. Doc-derived numbers are labelled as such and are used
only as *targets to check against*, never as sources.

---

## 0. Context read first

- `neurips_review/siga_neurips_reviews_clean.md` — gep1 Q2 (score-moving: rerun
  prefix-bug cells + separate S from X), gep1 Q3 (OpenFOAM), nBNe Q3 (exact
  Claude Code version).
- `neurips_review/SIGA_rebuttal_execution_plan.md` §2 (prefix bug) and §3 (S/X confound).
- `neurips_review/MASTER_TODO.md` items 6, 7, 8, 9.

Claims to be checked (all from summary docs — **targets, not sources**):
- C2→C6 = +0.008 (S), C6→C7 = −0.007 (X)
- C2 = 0.9134, C9 = 0.9170, Δ = +0.0036, big-swing = 0
- +0.24 mis-citation; real prefix effect +0.004
- Claude Code `2.1.119`

---

## 1. Locating the raw data

```
ls /data/shared/geophysics_agent_data/data/eval/
ls -la /data/shared/geophysics_agent_data/data/eval/dsv4_ablation_2026-04-29/
ls /data/shared/geophysics_agent_data/data/eval/dsv4_ablation_2026-04-29/_results/
```

Build-up ablation lives at
`/data/shared/geophysics_agent_data/data/eval/dsv4_ablation_2026-04-29/`.
Cell dirs `abl_c0_true_vanilla` … `abl_cMP_b_memp_on_c7`.
Scored output at `_results/<cell>_dsv4_s<seed>/<agent_dir>/<task>_eval.json`
plus a `_summary.json` per run.

Raw per-task record structure (from
`_results/c2_dsv4_s1/abl_c2_min_sr_no_rag/_summary.json`):
`results[i]` has `experiment`, `overall_score`, `overall_01`, `treesim`,
`treesim_section_scores`, `status`, `gt_dir`, `gen_dir`, …
`summary` has `n_total`, `n_scored`, `n_failed`, `failed_names`,
`treesim.scored_mean`, `treesim.with_failures_as_zero_mean`.

### Estimator used by the project's own analyzer (read, then reimplemented)

`/home/matt/sci/repo3/scripts/analysis/ablation_analyzer.py`, lines 103–121 and 340–371:

```
per_task[t]  = mean over seeds of eval.json["treesim"]
cell_mean    = mean over tasks of per_task[t]
delta(A->B)  = cell_mean(B) - cell_mean(A), over the task intersection
big-swing    = |per-task delta| >= threshold (default 0.10)
```

Note: `_per_task_treesim` reads only `*_eval.json` files that exist and have a
non-null `treesim`. **Failures are dropped, not zeroed.** For the build-up
ablation this is moot — see §2, `n_failed = 0` in all 21 run-cells — but it is
*not* the same convention as the paper's headline "failures-as-zero" numbers.
Stated here so nobody assumes the two are interchangeable.

### Task set — 17 tasks, hardcoded

`/home/matt/sci/repo3/scripts/launch_dsv4_ablation.sh` line 62 (`--include`):

```
AdvancedExampleCasedContactThermoElasticWellbore AdvancedExampleDeviatedElasticWellbore
AdvancedExampleDruckerPrager AdvancedExampleExtendedDruckerPrager
AdvancedExampleModifiedCamClay AdvancedExampleViscoDruckerPrager
buckleyLeverettProblem ExampleDPWellbore ExampleEDPWellbore
ExampleIsothermalLeakyWell ExampleMandel ExampleThermalLeakyWell
ExampleThermoporoelasticConsolidation kgdExperimentValidation
pknViscosityDominated TutorialPoroelasticity TutorialSneddon
```

All 17 come from `--experiments-dir .../experiments_test36_template` and all 17
appear in `eval_examples` of
`/data/shared/geophysics_agent_data/data/eval/table1_partition/partition_seed42.json`
(none is an `icl_examples` entry). Model: `--claude-model deepseek-v4-flash`.
So this is a 17-task subset of the 36-task eval pool used as the **harness
development set** — see §6 for why "val-only" is the right caveat but "at
ceiling" needs rewording.

---

## 2. Task C1 — S/X separation. RECOMPUTED FROM RAW. Reproduces exactly.

Script: `neurips_review/sprint/artifacts/C_recompute/recompute_buildup.py`
Output: `.../recompute_buildup.md`, `.../recompute_buildup.json`
File manifest (378 raw files opened): `.../recompute_buildup_files.txt`

```
cd /home/matt/sci/repo3/neurips_review/sprint/artifacts/C_recompute
python3 recompute_buildup.py recompute_buildup.md
```

### Cell means (mean over 17 tasks of per-task mean over 3 seeds)

| cell | agent dir | n_tasks | n_seeds | mean treesim | sd over tasks | per-seed cell means s1, s2, s3 | sd over seeds | n_failed/seed |
|---|---|---:|---:|---:|---:|---|---:|---|
| C0 | abl_c0_true_vanilla | 17 | 3 | 0.864884 | 0.1521 | 0.791182, 0.921906, 0.881565 | 0.0669 | 0,0,0 |
| C2 | abl_c2_min_sr_no_rag | 17 | 3 | **0.913398** | 0.0743 | 0.922759, 0.896706, 0.920729 | 0.0145 | 0,0,0 |
| C5 | abl_c5_dsv4_mem | 17 | 3 | 0.912090 | 0.0718 | 0.909724, 0.911312, 0.915235 | 0.0028 | 0,0,0 |
| C6 | abl_c6_xmllint_hook | 17 | 3 | **0.921051** | 0.0656 | 0.917306, 0.918300, 0.927547 | 0.0056 | 0,0,0 |
| C7 | abl_c7_xmllint_full_no_rag | 17 | 3 | **0.913851** | 0.0761 | 0.912459, 0.922041, 0.907053 | 0.0076 | 0,0,0 |
| C8 | abl_c8_xmllint_full_rag | 17 | 3 | 0.877735 | 0.0969 | 0.878847, 0.884900, 0.869459 | 0.0078 | 0,0,0 |
| C9 | abl_c9_no_prefix | 17 | 3 | **0.916965** | 0.0669 | 0.922165, 0.899118, 0.929612 | 0.0159 | 0,0,0 |

### The two contrasts

| contrast | isolates | mean A | mean B | Δ | sd of per-task Δ | paired t(16) | 95% CI | sign split | big-swing |
|---|---|---:|---:|---:|---:|---:|---|---|---:|
| C2 → C6 | **S** = hook-enforced `xmllint --schema` | 0.913398 | 0.921051 | **+0.00765** | 0.02901 | +1.088 | [−0.0073, +0.0226] | 10 up / 7 down | 0 |
| C6 → C7 | **X** = voluntary agent-callable `xmllint` on top of S | 0.921051 | 0.913851 | **−0.00720** | 0.02887 | −1.028 | [−0.0220, +0.0076] | 7 up / 10 down | 0 |
| C2 → C7 | S+X together | 0.913398 | 0.913851 | +0.00045 | 0.02516 | +0.074 | [−0.0125, +0.0134] | 7 up / 9 down / 1 tie | 0 |

Per-task Δ range: C2→C6 [−0.0735, +0.0477]; C6→C7 [−0.0734, +0.0351].

**Verdict:** +0.008 and −0.007 both reproduce, and match the project's own
sidecars to full float precision (`docs/ablation_C2_vs_C6.json`
mean_a=0.9133980392156863, mean_b=0.9210509803921568; `docs/ablation_C6_vs_C7.json`
mean_b=0.9138509803921568 — identical to my independent recompute).

**Is −0.007 distinguishable from zero? No.** sd of the per-task paired Δ is
0.029, ~4× the effect; t(16) = −1.03; the 95% CI straddles zero. The honest
statement is *"X produces no measurable improvement once S is on, and the
data cannot exclude a small effect of either sign up to ~±0.02"* — not
"X hurts." Same for S: +0.008 with CI [−0.007, +0.023] is a directionally
consistent but individually non-significant lift. The *joint* reading
(C2→C7 = +0.0005, i.e. S+X together buys nothing net on this set) is the
cleaner sentence.

**Caveat, stated not hidden:** this is the development set, not the hard
held-out tail. `n_failed = 0` in every one of the 21 run-cells, so the
mechanism by which S helps in the paper's headline result — suppressing empty,
unparseable, and missing-output decks — has *zero* opportunity to express
itself here. The S/X separation is therefore established on the regime where
neither component has much to do. See §6.

---

## 3. Task C2 — Prefix-bug probe. RECOMPUTED FROM RAW. Reproduces exactly.

Same script/manifest as §2 (`recompute_buildup.py`).

| | value |
|---|---|
| C2 (native-plugin prefix ON) | **0.913398** |
| C9 (`add_native_plugin_prefix=False`) | **0.916965** |
| Δ (C9 − C2) | **+0.003567** → **+0.004** |
| n_seeds | 3 |
| n_tasks | 17 (paired, full intersection) |
| big-swing tasks (\|Δ\| ≥ 0.10) | **0** |
| per-task Δ: sd / se / t(16) / 95% CI | 0.02892 / 0.00702 / +0.508 / [−0.0113, +0.0184] |
| sign split | 6 tasks up, 11 tasks down |
| per-task Δ range | [−0.0356, +0.0743] |
| per-seed cell means C2 | 0.922759, 0.896706, 0.920729 |
| per-seed cell means C9 | 0.922165, 0.899118, 0.929612 |
| n_failed | 0 in all 6 run-cells |

Per-task table matches `docs/ablation_C2_vs_C9.md` row-for-row
(e.g. ExampleIsothermalLeakyWell 0.772 → 0.846 = +0.074;
AdvancedExampleModifiedCamClay 0.935 → 0.991 = +0.056;
ExampleEDPWellbore 0.997 → 0.961 = −0.036). Cell means match
`docs/ablation_C2_vs_C9.json` to full float precision
(mean_a=0.9133980392156863, mean_b=0.9169647058823529).

**Note on sign convention:** Δ is *B − A* with A=C2 (prefix on).
So +0.004 means removing the prefix *helps* by 0.004 — i.e. prefix-bearing
cells are mildly handicapped. Direction matters for the bias argument below.

### 3a. Direct log-level evidence — stronger than the magnitude bound

Prompted by Thread D, re-verified independently by me from raw `events.jsonl`.
Script: `artifacts/C_recompute/count_rag_calls.py`, output `count_rag_calls.md`.
Metric definitions (they change the number, so they are stated):
`attempted` = assistant `tool_use` blocks named `mcp__geos-rag__*`;
`errored` = `tool_result` blocks containing `No such tool available`;
`connected` = `mcp_servers` in the `system/init` event.

| cell | task-runs | mcp servers connected | attempted geos-rag calls / task-run | errored / task-run | task-runs with ≥1 error |
|---|---:|---|---:|---:|---:|
| F0 Vanilla | 51 | `[]` | **0.00** | **0.00** | 0 / 51 |
| F1 R+M | 51 | geos-rag | 13.51 | 0.02 | 1 / 51 |
| F2 S+M | 51 | `[]` | 0.45 | 0.49 | 9 / 51 |
| F3 R+S | 51 | geos-rag | 12.10 | 0.00 | 0 / 51 |
| F4 X+M | 51 | xmllint | 2.25 | 2.25 | 39 / 51 |
| F5 R+X | 51 | geos-rag, xmllint | 12.31 | 0.00 | 0 / 51 |
| F6 S+X | 51 | xmllint | 1.96 | 1.98 | 35 / 51 |
| F7 R+S+X+M | 51 | geos-rag, xmllint | 12.86 | 0.02 | 1 / 51 |
| F8 S+X+M | 51 | xmllint | 2.61 | 2.65 | 46 / 51 |
| F11 SE-prose | 51 | xmllint | 2.02 | 2.02 | 38 / 51 |
| SE | 51 | xmllint | **0.00** | **0.00** | 0 / 51 |
| v4 | 49 | xmllint | **0.00** | **0.00** | 0 / 51 |

Three things this establishes *mechanistically*, not by inference:

1. **No retrieval leaked into R− cells.** In every R− cell the `geos-rag`
   server is absent from `mcp_servers` and every attempted call errors with
   `No such tool available`. R was genuinely off. The R main effect is not
   contaminated by *accidental retrieval*; it is contaminated by *wasted turns
   on an impossible instruction*, which depresses R− and therefore makes the
   measured R effect **less negative than truth**. Bias favours the paper.
2. **Vanilla (F0) and SE both emit exactly 0.** Any Vanilla-vs-SE contrast is
   prefix-free on both sides.
3. **The prefix-handicapped cells are X+M, S+X, S+X+M and SE-prose.** Their
   lifts over Vanilla are therefore **understated**, not inflated. Bias favours
   the paper. Magnitude bound from the C2/C9 probe: ≈ 0.004.

Caveat on metric 1 vs Thread D's report: Thread D quoted 0.45–2.73 erroring
calls per task; I measure 0.45–2.65 depending on cell and on whether you count
`attempted` or `errored`. Same phenomenon, slightly different counting rule.
I also count 13 assistant *text* blocks mentioning `mcp__geos-rag__` across all
608 DSv4 task-runs — a superset of "pseudo tool calls", so I cannot confirm
"pseudo_tool_calls == 0" as an exact statement; what I can say is the count is
13/608 and negligible, versus the severe minimax pathology.

### 3b. Bias direction (a) — R− cells told to call an absent server

Confirmed at three levels:
- **Config**, `src/runner/agents.py`: F2/F4/F6/F8/F11 all have
  `plugin_enabled: True` with no `add_native_plugin_prefix` override.
- **Pre-fix gate**, `git show 000b4ba -- src/runner/orchestrator.py`:
  removed line was `_add_prefix = bool(agent.get("add_native_plugin_prefix", enable_plugin))`
  — i.e. the default was `plugin_enabled`, so every plugin-on cell got the prefix.
  Replaced by `_add_prefix = bool(agent.get("add_native_plugin_prefix", _rag_on))`
  at `src/runner/orchestrator.py:276`.
- **Prefix text**, `src/runner/prompts/native_plugin_prefix.txt`, verbatim:
  > Do not call the Skill tool. Use the GEOS RAG MCP tools directly:
  > mcp__geos-rag__search_navigator, mcp__geos-rag__search_schema, and
  > mcp__geos-rag__search_technical. Before writing XML, call at least one of
  > the plugin RAG tools: search_navigator, search_schema, or search_technical.
- **Effect in logs**: §3a, R− plugin-on cells only.

→ **Bias favours the paper.** Measured R main effect is less negative than truth.

### 3c. Bias direction (b) — Vanilla had no prefix, SIGA cells did

`src/runner/agents.py:571-578`: `autocamp_F0` has `plugin_enabled: False`, so
`enable_plugin` is false, so under the pre-fix gate F0 never received the prefix.
Verified in logs: F0 `mcp_servers: []`, 0 geos-rag references across 51 runs.
All plugin-on SIGA cells did receive it (except SE / v4 / abl_c9 / abl_se_round,
which set `add_native_plugin_prefix: False` — lines 393, 437, 702, 717).

→ **Bias favours the paper.** SIGA cells were handicapped; the true SIGA
advantage over Vanilla is *larger* than reported. Bounded at ≈ 0.004.

### 3d. ⚠ SE vs SE-prose: the "0.022 gap" does NOT hold under both conventions

Script: `artifacts/C_recompute/recompute_se_vs_f11.py`, output `recompute_se_vs_f11.md`.
`autocamp_SE` sets `add_native_plugin_prefix: False` (agents.py:702);
`autocamp_F11` ("SE-prose", F6 harness + v3 PRIMER + v3 cheatsheet, agents.py:678)
does **not** override, so under the pre-fix gate F11 carried the prefix. Verified
in logs: SE 0 geos-rag calls, F11 2.02/task-run all erroring.

Raw bookkeeping (verbatim from `_summary.json`):

| cell | seed | n_total | n_scored | n_failed | failed_names | scored_mean | with_failures_as_zero_mean |
|---|---:|---:|---:|---:|---|---:|---:|
| SE | s1 | 17 | 17 | 0 | – | 0.909676 | 0.909676 |
| SE | s2 | 17 | 17 | 0 | – | 0.942159 | 0.942159 |
| SE | s3 | 17 | 17 | 0 | – | 0.905535 | 0.905535 |
| F11 | s1 | 17 | 17 | 0 | – | 0.928094 | 0.928094 |
| F11 | s2 | 17 | 16 | **1** | `['pknViscosityDominated']` | 0.918931 | **0.864876** |
| F11 | s3 | 17 | 17 | 0 | – | 0.896671 | 0.896671 |

| convention | SE (prefix OFF) | F11 SE-prose (prefix ON) | gap SE − F11 |
|---|---:|---:|---:|
| scored-only, mean of seed means | 0.919124 | 0.914565 | **+0.0046** |
| scored-only, mean of task means | 0.919124 | 0.915993 | **+0.0031** |
| failures-as-zero (either order) | 0.919124 | 0.896547 | **+0.0226** |

**This is the one place a doc claim does not survive contact with the raw data
in the form it was stated.** `SIGA_rebuttal_execution_plan.md` §2 says the prefix
asymmetry is "0.004 against a 0.022 gap — doesn't explain it." That is true only
under **failures-as-zero**, and under failures-as-zero the *entire* 0.0226 gap is
one unscorable task-run (`pknViscosityDominated`, F11 seed 2): 0.918931 × 16/17
= 0.864876. Under the scored-only convention — which is the convention the
prefix probe itself (+0.004) was measured under, since C2/C9 had zero failures —
the SE-vs-SE-prose gap is **+0.003 to +0.005**, i.e. the *same magnitude* as the
prefix effect. So the honest statement is: *the prefix asymmetry plausibly
accounts for all of the structural (scored-only) SE-vs-SE-prose gap, and ~18% of
the failures-as-zero gap, whose remainder is a single unscorable run.*
Do not write "0.004 against 0.022" without naming the convention.

I verified the `_summary.json` `with_failures_as_zero_mean` field is a correct
failures-as-zero implementation (`scored_mean × n_scored / n_total`):
F11 s2 0.918931×16/17 = 0.864876; F3 s1 0.855981×16/17 = 0.805629;
v4 s1 0.935227×15/17 = 0.825200. All match.

**Byproduct — MASTER_TODO P0 #1 resolved.** F3 (R+S) is **0.873504 scored-only**
and **0.856720 failures-as-zero**. Same data, two conventions. F3 seed 1 lost
`TutorialSneddon` (1 of 17). It is not a re-score, not a re-run, not a replaced
seed. Numbers straight from
`autocamp_2026-05-01/_results/autocamp_F3_s{1,2,3}/autocamp_F3/_summary.json`.

### 3e. Git chronology — all three claims confirmed

```
git log -1 --format="%H%n%aI%n%s" 000b4ba
git log -1 --format="%H%n%aI%n%s" 4c668d9
git show 000b4ba -- src/runner/orchestrator.py
ls -la --time-style=long-iso /data/shared/geophysics_agent_data/data/eval/autocamp_2026-05-01/dsv4/
```

| claim | verified value | source |
|---|---|---|
| fix commit `000b4ba` landed 2026-05-03 | `2026-05-03T23:01:37+00:00`, "[FIX] Gate native_plugin_prefix on rag_enabled, not plugin_enabled" | `git log` |
| autocamp factorial ran 2026-05-01/02 | phase-1 dirs 2026-05-01 12:30/12:58; F0–F8 2026-05-02 00:39–02:40; F8/F11 2026-05-02 11:41/11:55; SE 02:40; v4 16:28 | dir mtimes |
| Table 1 is pre-fix | factorial finished 2026-05-02 16:28, fix landed 2026-05-03 23:01 — **31 h later**. Confirmed pre-fix. | above two |
| only minimax × X+M re-run post-fix, `4c668d9`, 0.392 → 0.867 | `2026-05-03T23:37:33+00:00`, "[CAMPAIGN] minimax × X+M with prefix-gate fix — fa0 0.392 → 0.867 (+47.5pp)" | `git log` |

⚠ The commit message of `000b4ba` itself contains the "+0.24" mis-citation
("The team's `abl_c9_no_prefix` cell already showed a +0.24 surprise on DSv4
attributable to this prefix"). Commit messages are immutable; reported, not fixed.

---

## 4. Task C3 — the "+0.24" mis-citation. Verified, then edited.

### Gate cleared first
Rule from the brief: do not edit unless C2 reproduces +0.004. It does (§3,
+0.003567). Additionally I re-derived from raw what "+0.24" actually *was*:

| cell | mean | source |
|---|---:|---|
| C1 (`claude_code_no_plugin_minprimer`, min primer + workflow text, no plugin) | **0.671333** | `/home/matt/sci/repo3/data/eval/results/dsv4_min_primer_s{1,2,3}/claude_code_no_plugin_minprimer/*_eval.json` — 17 tasks × 3 seeds, per-seed means 0.687029 / 0.666024 / 0.660947 |
| C0 (`abl_c0_true_vanilla`, absolute-min primer, no plugin) | **0.864884** | `dsv4_ablation_2026-04-29/_results/c0_dsv4_s{1,2,3}/` |
| C2 (`abl_c2_min_sr_no_rag`) | **0.913398** | as §2 |

- C1 → C0 = **+0.193551** (doc says +0.194 ✓)
- C0 → C2 = **+0.048514** (doc says +0.049 ✓)
- **C1 → C2 = +0.242065 ≈ +0.24** ← this is the number that got mis-attributed.

So: **+0.24 is the C1→C2 build-up lift that C9 was constructed to explain.
The prefix's own effect is +0.004.** Confirmed, from raw, both halves.

C1 file manifest: `artifacts/C_recompute/c1_files.txt`; per-task means
`artifacts/C_recompute/c1_per_task.json`.

### Grep for every site

```
grep -rn "0\.24\b\|+0\.24\b\|0\.243\|0\.242" --include="*.py" --include="*.md" \
  --include="*.txt" --include="*.sh" --include="*.json" . \
  | grep -v "^./writing/" | grep -v "^./research-copilot/" | grep -v node_modules
```

Six sites assert or restate the prefix effect as +0.24. Four were in the brief;
**two were not.** Everything else matching `0.24` is unrelated (memory-ablation
M1-g +0.242, per-section TreeSim scores, PAC1 similarity values).

| # | site | in brief? | action |
|---|---|---|---|
| 1 | `src/runner/agents.py:425` | yes | **edited** |
| 2 | `docs/2026-05-03_minimax-pseudo-tool-call-analysis.md:78` | yes | **edited** |
| 3 | `docs/2026-05-04_cross-cutting-paper-section.md:150` | yes | **edited** |
| 4 | `docs/2026-05-04_remaining-todos.md:21` | yes | **edited** |
| 5 | `docs/2026-05-03_cross-cutting-summary.md:122` | **no — extra site** | **edited** (same doc class, same quoting hazard) |
| 6 | `.copilot/reviews/RN-006_adversarial_minimax-pseudo-mcp-leakage.md:343` | **no — extra site, and this is the origin** | **not edited** — RN-NNN review notes are immutable audit artifacts. Reported for a human to decide. |
| 7 | git commit message of `000b4ba` | no | **cannot be edited.** Reported. |

Not touched: `writing/`, the submitted paper, `neurips_review/` planning docs
(they already flag +0.24 as an error, correctly).

### Before / after

**1. `src/runner/agents.py:424-428`**

Before:
```
    # C9: C2 with the native-plugin-prefix suppressed in user prompt.
    # Isolates the "phantom RAG instruction" effect (the +0.24 surprise
    # from the C0-C5 ablation). Same primer + same plugin loading as C2,
    # only difference is the absence of the "use mcp__geos-rag__* tools"
    # prefix prepended to the user prompt.
```
After:
```
    # C9: C2 with the native-plugin-prefix suppressed in user prompt.
    # Isolates the "phantom RAG instruction" effect. Same primer + same
    # plugin loading as C2, only difference is the absence of the
    # "use mcp__geos-rag__* tools" prefix prepended to the user prompt.
    # MEASURED RESULT (3 seeds x 17 tasks, docs/ablation_C2_vs_C9.md):
    # C2 0.9134 -> C9 0.9170, delta = +0.0036, zero big-swing tasks. Null.
    # This cell was built to test whether the prefix explained the +0.24
    # C1->C2 lift (C1 0.6713 -> C0 0.8649 -> C2 0.9134); it does not.
    # Do not cite "+0.24" as the prefix effect -- that was the lift being
    # explained, not this cell's result.
```

**2. `docs/2026-05-03_minimax-pseudo-tool-call-analysis.md:78`**

Before (excerpt): *"The team's existing `abl_c9_no_prefix` cell (autocamp_v4 too
has the opt-out) was created precisely because someone noticed a $+0.24$ surprise
from this prefix on DSv4. The bug's effect is bounded but non-zero on DSv4 and
severe on minimax."*

After: *"…was created to test whether this prefix explained the $+0.24$
C1$\to$C2 lift seen in the build-up ablation. **It did not:**
`docs/ablation_C2_vs_C9.md`, 3 seeds $\times$ 17 tasks, gives C2 $0.9134 \to$ C9
$0.9170$, $\Delta = +0.0036$ with zero big-swing tasks. The prefix effect on DSv4
is $+0.004$ (null); the $+0.24$ figure is the C1$\to$C2 lift that was *being
explained* ($0.6713 \to 0.8649 \to 0.9134$), not this cell's result. Do not cite
$+0.24$ as the prefix effect. The bug's effect is therefore bounded at
$\approx 0.004$ on DSv4 and severe only on minimax."*

**3. `docs/2026-05-04_cross-cutting-paper-section.md:150`**

Before (excerpt): *"The team's \texttt{abl\_c9\_no\_prefix} cell had previously
surfaced a $+0.24$ DSv4 anomaly attributable to this prefix, consistent with our
finding."*

After: *"The team's \texttt{abl\_c9\_no\_prefix} cell measured the prefix's effect
on DSv4 directly over 3 seeds $\times$ 17 tasks: C2 (prefix) $0.9134$ vs C9 (no
prefix) $0.9170$, $\Delta = +0.0036$, with zero big-swing tasks
($|\Delta| \geq 0.10$). So on DSv4 the prefix is \emph{null} at
${\approx}+0.004$, and the contamination of any DSv4 number is bounded at that
magnitude. (Earlier internal notes cited a "$+0.24$ DSv4 anomaly attributable to
this prefix"; that is a mis-citation. $+0.24$ is the C1$\to$C2 build-up lift that
C9 was constructed to explain, $0.6713 \to 0.8649 \to 0.9134$, and the prefix
hypothesis for it was refuted.)"*

**4. `docs/2026-05-04_remaining-todos.md:21`**

Before: *"**Why**: The autocamp $R = -0.033$ main effect was contaminated by the
buggy prefix on $R^{-}$ cells (F2, F4, F6, F8, F11). The team's own
`abl_c9_no_prefix` already showed a $+0.24$ DSv4 anomaly attributable to this
prefix on a single seed. A clean re-run replaces these contaminated headline
numbers with bug-fixed equivalents."*

After: same first and last sentence, with the middle sentence replaced by a new
**"How large is the contamination?"** paragraph giving C2 0.9134 / C9 0.9170 /
Δ = +0.0036 / zero big-swing / 3 seeds × 17 tasks, explicitly correcting both
errors in the old sentence (the magnitude *and* "on a single seed" — it was
three seeds), and stating that +0.24 was the C1→C2 lift.

**5. `docs/2026-05-03_cross-cutting-summary.md:120-124`** (extra site)

Before: *"The `abl_c9_no_prefix` cell was created specifically because the team
had previously detected a $+0.24$ DSv4 anomaly attributable to this prefix —
consistent with our finding."*

After: *"The `abl_c9_no_prefix` cell was created to test whether this prefix
explained the $+0.24$ C1$\to$C2 build-up lift ($0.6713 \to 0.8649 \to 0.9134$).
**It did not.** `docs/ablation_C2_vs_C9.md`, 3 seeds $\times$ 17 tasks: C2
(prefix) $0.9134$ vs C9 (no prefix) $0.9170$, $\Delta = +0.0036$, zero big-swing
tasks. The prefix effect on DSv4 is $+0.004$ — null. Do not cite $+0.24$ as the
prefix effect; that number is the lift that was being explained, not the
finding."*

### 4b. Sixth edit — SE's MCP surface (flagged by Thread D, verified by me)

`docs/2026-05-04_cross-cutting-paper-section.md:57` explained SE's gemini
regression with *"its plugin includes both geos-rag and xmllint MCP servers, so
the agent has more tools to invoke."* **False.** Verified from `system/init`
events in raw `events.jsonl` — SE registers **only** `xmllint`:

| SE run set | `mcp_servers` in every init event | `mcp__geos-rag__` references |
|---|---|---|
| DSv4 val, `autocamp_2026-05-01/dsv4/autocamp_SE/autocamp_SE_s{1,2,3}` | `[{"name":"xmllint","status":"connected"}]` (51/51) | 0 |
| DSv4 held-out, `autocamp_followup_2026-05-02/icl/autocamp_SE/SE_icl_s{1,2,3}` | same (30/30) | 0 |
| gemini, `cross_model_2026-05-03/google_gemini-3-flash-preview/autocamp_SE/..._SE_s1` | same (17/17) | 0 |
| minimax, `cross_model_2026-05-03/minimax_minimax-m2.7/autocamp_SE/..._SE_s1` | same (17/17) | 0 |

And the asymmetry runs the *other* way on gemini: `..._F4_s1` (X+M) shows
`[{"name":"xmllint","status":"connected"}]` with **150** `mcp__geos-rag__`
references — i.e. X+M carried the buggy prefix there and SE did not, so X+M was
handicapped relative to SE and still beat it.

Edit made: replaced the false mechanism with "we have no supported explanation",
the verified `mcp_servers` evidence, and the reversed-asymmetry note. Full after
text is in the file at line 57.

---

## 5. Task C4 — Claude Code version

### The verbatim field

Path read:
`/data/shared/geophysics_agent_data/data/eval/autocamp_2026-05-01/dsv4/autocamp_F0/autocamp_F0_s1/ExampleThermalLeakyWell/events.jsonl`

The `type: "system", subtype: "init"` event contains, verbatim:

```json
"claude_code_version": "2.1.119",
"model": "deepseek-v4-flash",
"permissionMode": "bypassPermissions",
"apiKeySource": "none",
"mcp_servers": [],
"plugins": []
```

### Is it the same in every autocamp run? YES — zero exceptions.

Sweeps: `artifacts/C_recompute/sweep_events.sh` → `sweep_events.txt`;
`artifacts/C_recompute/sweep_versions_followup.txt`;
`artifacts/C_recompute/count_rag_calls.py` → `count_rag_calls.md`.

| run set | task-runs / init events | distinct `claude_code_version` |
|---|---:|---|
| `autocamp_2026-05-01/dsv4` — F0,F1,F2,F3,F4,F5,F6,F7,F8,F11,SE,v4,p_contract,p_method (all seeds) | 608 | **`2.1.119`** only |
| `autocamp_followup_2026-05-02/icl` — F0,F4,F6,F8,F11,SE × 3 seeds × 10 tasks | 180 | **`2.1.119`** only |
| `autocamp_followup_2026-05-02/train` — F0,F6 × 3 seeds × 19 tasks | 115 | **`2.1.119`** only |
| `cross_model_2026-05-03` — gemini F0/F4/SE, minimax SE (spot-checked) | 68 | **`2.1.119`** only |

Total **903 autocamp init events, all `2.1.119`**. One quirk worth noting for
honesty: `train/autocamp_F6/F6_train_s3` has 20 init events for 19 tasks — one
task emitted two (a session restart). Both report `2.1.119`.

### The honest concession — the version was never pinned

`/home/matt/sci/repo3/run/Dockerfile:32`, verbatim:

```
RUN npm install -g @anthropic-ai/claude-code
```

No version specifier, no lockfile for this package. So the installed CLI version
was whatever npm's `latest` resolved to at **image build time**, not something the
experiment configuration controlled. `git log -- run/Dockerfile` shows this line
has not changed since `ef51fbf`. The reason every logged run agrees on `2.1.119`
is that they all ran from the same cached image, not because the version was
constrained. This should be disclosed and fixed for the camera-ready
(`@anthropic-ai/claude-code@2.1.119`).

---

## 6. The "val is at ceiling" caveat — needs rewording

`SIGA_rebuttal_execution_plan.md` §3 says to caveat C1 with "val is at ceiling
for every cell." Taken literally that is **not** what the raw data shows. Per-task
mean distributions (from `recompute_buildup.md`):

| cell | min | median | max | tasks ≥ 0.95 (of 17) | tasks ≥ 0.99 |
|---|---:|---:|---:|---:|---:|
| C2 | 0.7719 | 0.9355 | 0.9978 | 6 | 3 |
| C6 | 0.8086 | 0.9311 | 0.9977 | 7 | 3 |
| C7 | 0.7664 | 0.9288 | 0.9983 | 7 | 3 |
| C9 | 0.7760 | 0.9454 | 0.9914 | 7 | 1 |

There is ~0.08 of headroom in the mean and the worst task sits near 0.77. So it
is *not* a ceiling in TreeSim terms. The accurate caveat, and the one to use:

> **`n_failed = 0` in all 21 build-up run-cells.** No cell produced a single
> empty, unparseable, or missing-output deck on this task set. The mechanism S is
> credited with in the paper's headline result — catastrophic-failure suppression
> — therefore has *no opportunity to act here*. The remaining ~0.08 gap is
> attribute-level and semantic error, which the paper's own bottleneck analysis
> says no adapter fixes. That is why the S/X separation, though clean on this set,
> does not transfer automatically to the hard held-out tail.

Say "no failures to suppress", not "at ceiling". A reviewer who recomputes will
see 0.913 and 0.921 and will not accept "ceiling".

---

## 7. Discrepancies between docs and raw data — full list

| # | claim | raw data | severity |
|---|---|---|---|
| 1 | C2→C6 = +0.008, C6→C7 = −0.007 | +0.00765, −0.00720 | ✅ reproduces |
| 2 | C2 0.9134, C9 0.9170, Δ +0.0036, 0 big-swing, 3×17 | identical to 6 d.p. | ✅ reproduces |
| 3 | C1→C0 +0.194, C0→C2 +0.049, ≈+0.243 | +0.193551, +0.048514, +0.242065 | ✅ reproduces |
| 4 | Claude Code 2.1.119 | 903/903 init events | ✅ reproduces |
| 5 | fix `000b4ba` 2026-05-03; factorial 05-01/02; only minimax×X+M re-run (`4c668d9`, 0.392→0.867) | all confirmed | ✅ reproduces |
| 6 | prefix effect is +0.24 (six sites) | +0.004 | ❌ **mis-citation, fixed in 5 of 7 sites** |
| 7 | "SE-vs-SE-prose gap is 0.022" (used to dismiss a 0.004 asymmetry) | 0.0226 **only** under failures-as-zero, and driven entirely by one unscorable run; **0.003–0.005 under scored-only** | ⚠ **claim survives only with the convention named** |
| 8 | "val is at ceiling for every cell" | means 0.91–0.92, worst task 0.77; the true fact is `n_failed = 0` | ⚠ **reword** |
| 9 | `abl_c9_no_prefix` showed the anomaly "on a single seed" (`2026-05-04_remaining-todos.md`) | 3 seeds | ❌ fixed |
| 10 | "SE's plugin includes both geos-rag and xmllint MCP servers" (`2026-05-04_cross-cutting-paper-section.md:57`) | only `xmllint`, on all 4 run sets; 0 geos-rag calls | ❌ **fixed** |
| 11 | C0→C2 described as "load plugin" | `launch_dsv4_ablation.sh` gives C0 `GEOS_PRIMER_absolute_min.md` and C2 `GEOS_PRIMER_minimal_vanilla.md` — the contrast changes **primer and plugin together** | ⚠ **new, unresolved — see §9** |

---

## 8. Rebuttal-ready prose

### C1 — S/X separation (for gep1 Q2, second half)

> S and X can be separated from data already in hand. Alongside the
> Resolution-IV design we ran a one-factor-at-a-time build-up ablation (3 seeds ×
> 17 tasks, DeepSeek-v4-flash). Adding the hook-enforced validator to the
> parse-check baseline (S): 0.9134 → 0.9211, Δ = +0.008. Adding the voluntary
> agent-callable validator on top (X): 0.9211 → 0.9139, Δ = −0.007. Both: +0.000.
> The stop-hook does the work; X adds nothing once S is present — the comparison
> the fractional design cannot make, as S×X aliases with R×M. Two caveats we state
> rather than hide. Per-task paired variability is ±0.029, so neither contrast
> alone is distinguishable from zero; the supportable claim is "X buys nothing on
> top of S", not "X hurts". And this ran on our development set, where no cell
> produced a single unscorable deck — so the failure-suppression mechanism S is
> credited with on the hard tasks had no room to act.

*(831 characters)*

### C2 — Prefix bug (for gep1 Q2, first half)

> We can bound this bug from logs rather than argue from chronology. The prefix
> named RAG MCP tools; when the server was absent, each call is recorded in
> `events.jsonl` as `No such tool available`. Counting them: Vanilla shows 0 and
> SE shows 0, so our headline Vanilla-vs-SE contrast is prefix-free on both
> sides. The affected cells are X+M, S+X, S+X+M and SE-prose (0.5–2.7 erroring
> calls per task-run) — i.e. the adapter cells, so their reported lifts are
> understated, not inflated. In R+ cells the server is registered and the calls
> succeed, so no retrieval leaked into R− cells; the R main effect is depressed
> on the R− side, making it less negative than truth. For magnitude we ran a
> dedicated probe (3 seeds × 17 tasks) toggling only the prefix: 0.9134 vs
> 0.9170, Δ = +0.004, zero tasks moving by ≥0.10. Every bias runs against us.

*(896 characters)*

### C4 — Claude Code version (for nBNe Q3)

> Claude Code **2.1.119**, identical across every run. Each trajectory's
> `system/init` event records `claude_code_version`, and all 903 init events —
> across the factorial, the held-out follow-up, and the cross-model panel —
> report `2.1.119` with no exceptions. The backbone is DeepSeek-v4-flash unless
> stated; the cross-model panel adds minimax-m2.7 and gemini-3-flash-preview on
> the same harness version. One process caveat we should state plainly: our
> container installed the CLI via `npm install -g @anthropic-ai/claude-code`
> with no version pin, so the version tracked image build time rather than being
> fixed by configuration. It is identical everywhere only because all runs came
> from one cached image. We will pin it explicitly for the camera-ready, and we
> agree the harness version belongs in the reproducibility section alongside the
> model.

*(831 characters)*

---

## 9. New, unresolved: the C0→C2 primer confound (for a human)

Not part of my brief; found while re-deriving "+0.24" and it touches how that
lift is described. `scripts/launch_dsv4_ablation.sh` lines 26-36:

```
c0) AGENT="abl_c0_true_vanilla";   PRIMER="plugin/GEOS_PRIMER_absolute_min.md"
c2) AGENT="abl_c2_min_sr_no_rag";  PRIMER="plugin/GEOS_PRIMER_minimal_vanilla.md"
```

`docs/2026-04-30_dsv4-ablation-final-v2.md` presents the chain as
C1 (min primer + workflow text) → C0 (strip workflow text, +0.194) → C2
(load plugin, +0.049), and headlines "stripping the workflow-step primer" as the
single largest effect. But C2 uses `GEOS_PRIMER_minimal_vanilla.md` — the *same*
workflow-text primer as C1. So C0→C2 adds the plugin **and puts the workflow
text back**, and the decomposition of +0.242 into "+0.194 primer + +0.049 plugin"
is not a clean additive split; C0 is off the C1→C2 path in primer terms.

Consequences: (a) the correct, safe description of +0.242 is "the C1→C2 lift from
loading the plugin infrastructure onto a no-plugin baseline" — which is what my
C3 edits say, so they are unaffected; (b) any claim of the form "stripping the
workflow primer is worth +0.19" needs re-checking before it goes anywhere near a
reviewer. I have not investigated further. Flagging for whoever owns the
build-up ablation narrative.

---

## 10. Artifact index

All under `neurips_review/sprint/artifacts/C_recompute/`:

| file | what |
|---|---|
| `recompute_buildup.py` / `.md` / `.json` | C1 + C2 core recompute: cell means, per-seed, per-task, all four contrasts |
| `recompute_buildup_files.txt` | manifest of the 378 raw files opened for the above |
| `c1_files.txt`, `c1_per_task.json` | C1 cell (0.671333) raw file list + per-task means |
| `recompute_autocamp.py` / `.md` / `_files.txt` | all 12 autocamp dsv4 cells, both conventions, plus prefix-carry column |
| `recompute_se_vs_f11.py` / `.md` | the SE-vs-SE-prose convention problem, and F3's 0.874/0.857 |
| `sweep_events.sh` / `sweep_events.txt` | grep-level sweep: versions, mcp servers, geos-rag refs, `No such tool available` per run |
| `count_rag_calls.py` / `count_rag_calls.md` | JSON-level per-task-run attempted/errored geos-rag call counts |
| `sweep_versions_followup.txt` | version sweep over `autocamp_followup_2026-05-02` |

Reproduce everything: `cd` to the directory and run
`python3 recompute_buildup.py recompute_buildup.md`,
`python3 recompute_autocamp.py`, `python3 recompute_se_vs_f11.py`,
`python3 count_rag_calls.py count_rag_calls.md`, `bash sweep_events.sh`.
Runtime: the first three are seconds; `count_rag_calls.py` and `sweep_events.sh`
are a few minutes each (they read ~600 trajectory logs).

Nothing was committed to git. Nothing under `/data/shared/`, `writing/`, or any
`_`-prefixed directory was written.
