# SIGA @ NeurIPS 2026 — Rebuttal Triage v1

**Submission 31642.** Scores 5 (nBNe, conf 5) / 4 (gep1, conf 3) / 2 (kEdh, conf 4). AC GKRj: borderline.

**Sources.** Reviews: `/home/matt/sci/repo3/siga_neurips_reviews_clean.md`. Paper: `/home/matt/sci/repo3/writing/neurips/neurips_2026.tex` (745 lines, 2026-05-07) + `checklist.tex`. All line references below are to that `.tex`.

**Verification legend.** Everything marked **[VERIFIED]** I ran or read on disk during this triage. Everything marked **[GUESS]** is an estimate I could not confirm. Numbers I computed fresh in this session are marked **[NEW — computed today]**.

---

## 0. Headline: three things you already own and have not used

Before the triage, the three facts that reorganize the whole plan. All three are on disk, cost $0, and each maps onto a score-moving ask.

### 0.1 A schema-validity ladder already discriminates Vanilla from SIGA, on the hard tail **[NEW — computed today]**

The eval container ships `xmllint` (`/home/matt/sci/repo3/run/Dockerfile:14`, `libxml2-utils`) and the canonical GEOS XSD is checked into the source tree at `/home/matt/sci/repo3/data/GEOS/src/coreComponents/schema/schema.xsd` (632 KB) — **no GEOS build required**. Every generated deck from every campaign is still on disk (~8,600 XML files). I re-validated the held-out-eval campaign (`/data/shared/geophysics_agent_data/data/eval/autocamp_followup_2026-05-02/icl/`, 10 tasks × 3 seeds × 6 cells):

| Cell | runs | XML files | well-formed | schema-valid | **runs where every file is schema-valid** |
|---|---:|---:|---:|---:|---:|
| Vanilla (F0) | 30 | 81 | 76 | 73 | **24 / 30 (80%)** |
| X+M (F4) | 30 | 81 | 81 | 81 | **30 / 30** |
| S+X (F6) | 30 | 81 | 81 | 81 | **30 / 30** |
| S+X+M (F8) | 30 | 81 | 81 | 81 | **30 / 30** |
| SE-prose (F11) | 30 | 81 | 81 | 81 | **30 / 30** |
| SE | 30 | 81 | 81 | 81 | **30 / 30** |

Fisher exact on 24/30 vs 30/30: one-sided p = 0.0119, two-sided p = 0.024 (caveat: 3 seeds × 10 tasks, so runs are clustered by task and the nominal p is optimistic — report it as descriptive).

Val split (17 tasks × 3 seeds, `autocamp_2026-05-01/dsv4/`): Vanilla 49/51, S+M 49/51, X+M 51/51, S+X 51/51, SE 50/51 (one SE run wrote no XML at all). Near-ceiling on val, discriminating on held-out — **exactly the paper's own thesis, reproduced on a non-TreeSim, execution-adjacent metric.**

Sanity check: all **118/118** ground-truth deck files pass `xmllint --schema`. The bar is real and passable; the schema is the right one.

The six Vanilla failures are individually nameable:

```
F0_icl_s1 / AdvancedExampleThermoPoroElasticWellbore  -> not well-formed (ThermoPoroElasticWellbore_smoke.xml)
F0_icl_s1 / TutorialHydraulicFractureWithAdvancedXML  -> schema-invalid (walshQuarterNoChombo_smoke.xml)
F0_icl_s3 / AdvancedExampleCasedThermoElasticWellbore -> schema-invalid (CasedThermoElasticWellbore_base.xml)
F0_icl_s3 / AdvancedExampleThermoPoroElasticWellbore  -> not well-formed (base.xml, benchmark.xml)
F0_icl_s3 / ExampleProppantTest                       -> not well-formed (base.xml, benchmark.xml)
F0_icl_s3 / TutorialHydraulicFractureWithAdvancedXML  -> schema-invalid (walshQuarterNoChombo_base.xml)
```

These land on precisely the hard-tail tasks the paper already singles out at L209 and L385–386.

**Honesty requirement, and you must state it yourself before a reviewer does:** rung 2 is *partly enforced by construction* for S and X cells, since those adapters run `xmllint --schema` (`plugin/hooks/verify_outputs.py:200–231`; MCP tool `plugin/scripts/xmllint_mcp.py:89`). That does not make the number worthless — it makes it a *guarantee* claim rather than an *emergent* claim, and the interesting question becomes whether the guarantee costs anything upstream (it does not: TreeSim rises too). Say it in one sentence and move on.

### 0.2 A 30-task OpenFOAM campaign with **two** native baselines already exists, unreported **[VERIFIED]**

`/home/matt/sci/repo3/docs/openfoam_n30/openfoam_n30_hybrid_aggregate_results_20260530.md`, dated 2026-05-30, three weeks after submission. 30 tasks (vs the paper's 5), 9 SIGA cells, same metric, and it adds **MetaOpenFOAM** as a second OpenFOAM-native baseline that is not in the paper at all:

| Row | Mean score | Full coverage | Zero-score |
|---|---:|---:|---:|
| repo3 `r+s` (best) | 0.8704 | 30/30 | 0/30 |
| repo3 `s+x` | 0.8664 | 30/30 | 0/30 |
| repo3 `vanilla` | 0.6809 | 30/30 | 0/30 |
| Foam-Agent 2.0 lint-only | 0.5157 | 19/30 | 8/30 |
| MetaOpenFOAM lint-only | 0.3794 | 10/30 | 12/30 |

Stop-hook (`s`) appears in all top-5 cells — the paper's central transfer claim, at 6× scale, with a second baseline. Fully scored, token- and cost-instrumented. Artifacts under `/home/brianliu/repo3_openfoam/data/openfoam_runs/`. **This single paragraph answers gep1 W2/Q3, nBNe W4, and half of the AC's "limited experimental scale" bullet at zero compute cost.**

Caveats to state: still single-seed, still a coverage/text metric rather than TreeSim, still lint-only for both baselines. Note the score shift from the 5-task run (`r+s` 0.887 → 0.870) — disclose it as run-to-run variance rather than letting a reviewer find it.

### 0.3 The S-vs-X isolation gep1 asks for is already measured, with 3 seeds **[VERIFIED]**

`/home/matt/sci/repo3/docs/2026-04-30_dsv4-ablation-final-v2.md` (17 val tasks × 3 seeds, cells defined in `src/runner/agents.py:262–380`):

| Contrast | What it adds | Δ TreeSim | big-swing tasks |
|---|---|---:|---:|
| C2 → C6 | schema validation **inside the stop hook** (S with `xmllint`) | **+0.008** | 0 |
| C6 → C7 | the **agent-callable** validator on top (X) | **−0.007** | 0 |
| C2 → C9 | remove the native-plugin prefix | **+0.004** | 0 |
| C2 → C4 | add RAG to the parse-check hook | **−0.039** | 3 (3 degradations) |
| C7 → C8 | add RAG to the full xmllint stack | **−0.036** | 2 (2 degradations) |

This is a clean, prefix-matched, build-up ablation that decomposes exactly what gep1 says is confounded in the Resolution-IV design. It is **not in the paper.** Adding it as an appendix table is a two-hour job.

---

## 1. Situation assessment

### Where the votes are

**gep1 (4, conf 3) is the winnable score and the entire rebuttal should be organized around him.** He is the only reviewer who wrote a conditional score commitment, twice:

- *"My score would increase if the reliability gains persist under execution or physical-validity checks."* (Q1)
- *"My confidence would increase if the stop-hook effect remains dominant after removing this confound."* (Q2)

Both conditions are satisfiable. §0.1 is a validity check that is not TreeSim; §0.3 shows the stop-hook effect (C2→C6, +0.008 hook-time schema validation) survives with the confound removed and that the *agent-callable* validator is the null component, not the hook. A 4→5 from gep1 gives the AC 5/2/5 with the reject held by the only reviewer whose complaint is about writing, which is the one complaint you can actually fix inside the window.

**nBNe (5, conf 5) is locked.** Absolutely-certain accept. Do not spend words defending against W1 ("no new architecture") — he raised it and still gave a 5, and arguing it invites him to reconsider. Give him exactly three things: the Claude Code version he asked for (**2.1.119**, see §3.6), the validity ladder, and an explicit, gracious narrowing of the human-baseline claim. Budget ≤ 250 words.

**kEdh (2, conf 4, "wrong venue") is not winnable to an accept, and you should stop trying.** A confidence-4 reviewer who wrote "this paper needs to be significantly re-written" and "may be better directed to eScience" is not going to move to 4 off a rebuttal. The realistic ceiling is 2→3, and even that is optional. **kEdh's actual function in this decision is as ammunition for the AC**, because the AC independently endorsed the clarity complaint in their own words ("I see the same issue with the writing of the paper… it would be hard for a NeurIPS reader to fully understand many things"). So the clarity work is an **AC-facing deliverable, not a kEdh-facing one.**

Optimal play with kEdh:
1. **Do the rewrite for real and upload a revised PDF.** Every one of his four complaints is a specific, enumerable sentence-level fix (§6). Show him a before/after table. This is the single most credible thing you can do with a "not written well" reviewer: don't argue, ship diffs.
2. **Do not litigate venue.** Do not cite the CFP at him, do not point out that two other reviewers rated significance 3 and 4. One neutral sentence maximum, addressed to the AC rather than to kEdh, positioned at the end and not the start.
3. **Do not concede that the paper is unclear "in general."** Concede the *specific* items, fix them, and let the diff speak.

The AC's decision letter tells you the weighting explicitly: *"The decision will likely depend on whether the rebuttal can establish that the structural improvements translate to executable and scientifically valid simulations and whether the authors can put significant efforts towards improving the clarity."* Two conditions, joined by "and". You must deliver on **both**, and execution evidence alone will not carry it.

### Score-moving vs nice-to-have

**Score-moving (gep1 states this literally):**
- A1 GEOS execution / validity evidence
- A2 rerun of prefix-bug-contaminated cells
- A3 S-vs-X isolation

**Score-moving by AC weighting (not a reviewer's stated condition, but named as a decision criterion):**
- A10–A14 the clarity fixes

**Nice-to-have (improve credibility, do not move a score):** human-baseline narrowing, OpenFOAM scale-up, seed counts, CC version. Note that the human-baseline and OpenFOAM narrowings are *cheap* and the reviewers explicitly invited them — take those wins.

---

## 2. Triage table

Effort assumes one competent person working the item; wallclock assumes `workers=4` on the existing 128-core host.

| ID | Ask | Raised by | Score impact | Effort | New compute? | Feasible in window? | Verdict |
|---|---|---|---|---|---|---|---|
| **A1a** | Validity ladder rungs 1–2 (well-formed → schema-valid) on existing decks | gep1 Q1 (score-moving), nBNe Q1, **AC primary** | **High** | 4–6 h | **No** | Yes — *already computed*, §0.1 | **DO NOW** |
| **A1b** | Rung 3: `geosx --validate-input` on decks (real GEOS loader) | same | **High** | 1–3 days, build-risk | Yes (CPU only, no API) | ~55% | **DO IF TIME** (time-box 3 days) |
| **A1c** | Rung 4–5: deck runs N timesteps / converges | nBNe Q1, AC | High | 3–7 days | Yes | ~20% | **DEFER-and-argue** |
| **A2** | Rerun prefix-bug-contaminated cells (F2,F4,F6,F8,F11) | gep1 Q2 (**score-moving**) | **High** | 2 h setup + 2 h run | Yes, ~$4 | Yes | **DO NOW** |
| **A2b** | Rerun gemini × X+M so the cross-model table is uniformly post-fix | gep1 Q2 | Med | 30 min + 20 min run | Yes, ~$0.2 | Yes | **DO NOW** |
| **A3** | Separate S from X | gep1 Q2 (**score-moving**), paper L157/L272 | **High** | 2 h (data exists) | **No** | Yes — §0.3 | **DO NOW** |
| **A4a** | OpenFOAM: more tasks | gep1 Q3, nBNe W4, AC | **High** | 3 h writeup | **No** — 30-task run exists | Yes — §0.2 | **DO NOW** |
| **A4b** | OpenFOAM: multiple seeds | gep1 Q3, AC | Med | 1 day + ~$25 | Yes | Yes | **DO IF TIME** |
| **A4c** | Foam-Agent in full execute mode | gep1 Q3 | Med | 2–5 days, previously failed | Yes | ~25% | **DECLINE-and-reframe** |
| **A5** | Narrow / recontextualize human baseline | gep1 Q4, nBNe W3, AC | Med (credibility) | 2 h | **No** | Yes | **DO NOW** (concede) |
| **A6** | Human baseline: multiple expertise levels + human-agent collaborative mode | nBNe Q2 | Low | 2–4 weeks + IRB | Yes (human subjects) | **No** | **DECLINE-and-reframe** |
| **A7a** | More seeds on headline cells (n=3 → n=5) | gep1 W2, nBNe W4, AC | Med | 1 day + ~$5 | Yes | Yes | **DO IF TIME** |
| **A7b** | Larger / more diverse GEOS benchmark | nBNe W4, AC | Med | 2–4 weeks (GT curation) | Yes | **No** | **DEFER-and-argue** |
| **A7c** | Uncertainty estimates on existing numbers (CIs, paired tests) | AC | Med | 4 h | **No** | Yes | **DO NOW** |
| **A8** | Limitations must say "structural authoring reliability, not validated simulator correctness" | gep1 | Med | 15 min | **No** | Yes | **DO NOW** (concede) |
| **A9** | Report exact Claude Code version | nBNe Q3 | Low | 10 min | **No** | Yes — **2.1.119** | **DO NOW** |
| **A10** | Define "deck" early | kEdh 2, **AC** | Med | 30 min | **No** | Yes | **DO NOW** |
| **A11** | Explain Resolution-IV factorial in plain language | kEdh 1, **AC** | Med | 30 min | **No** | Yes | **DO NOW** |
| **A12** | Explain `buckleyLeverettProblem` | kEdh 1, **AC** | Low | 15 min | **No** | Yes | **DO NOW** |
| **A13** | Concrete examples of "brief" and "structured repair feedback" | kEdh 3, **AC** | Med | 1 h | **No** | Yes | **DO NOW** |
| **A14** | Rewrite failures-as-zero + "strictly perfect decks" sentences | kEdh 2, **AC** | Med | 30 min | **No** | Yes | **DO NOW** |
| **A15** | Venue fit (eScience vs NeurIPS) | kEdh 4 | Low | 15 min | **No** | n/a | **DECLINE-and-reframe** (1 sentence, to the AC) |
| **A16** | "No fundamentally new architecture" | nBNe W1 | Low | 0 | **No** | n/a | **DECLINE** — do not respond |
| **A17** | Representativeness of the 10 held-out tasks | AC | Med | 3 h | **No** | Yes | **DO NOW** |
| **A18** | Recover the lost cross-model score panel (165 runs, evals deleted from `/tmp`) | internal | Low-Med | 3 h | **No** (decks on disk) | Yes | **DO IF TIME** |

---

## 3. Tier 1 — Low-hanging fruit (hours, no new experiments)

Ordered by value. All of these should be finished in the first 48 hours so the remaining time can go to A1b.

### 3.1 The validity ladder (A1a) — the centerpiece of the rebuttal

**What to do.** Formalize §0.1 as a new results subsection and a new table. Extend the script beyond the 6 held-out cells to all 11 val cells and to the cross-model decks. The scoring harness already has a component for this: `/home/matt/sci/repo3/scripts/analysis/treesim_xmllint_analyzer.py` (`_xmllint_one`, line ~53) runs exactly this check per file and already knows the schema path.

**Files and numbers to cite.** Schema `/home/matt/sci/repo3/data/GEOS/src/coreComponents/schema/schema.xsd`; decks under `/data/shared/geophysics_agent_data/data/eval/autocamp_followup_2026-05-02/icl/<cell>/<run>/<task>/inputs/*.xml`.

**Where it goes in the paper.** New §5.1 subsection immediately after "Reliability is the largest visible adapter effect" (currently L211), plus a new appendix table. It also lets you delete the future-work bullet at L551 and replace it with a result.

**Rebuttal text would claim:**

> We agree that structural similarity alone does not establish that a deck is usable, and we have added a *staged validity ladder* that is independent of TreeSim. Rung 1 is XML well-formedness; rung 2 is validation against the canonical GEOS XSD (`src/coreComponents/schema/schema.xsd`), the same schema the simulator itself consumes. On the 10 held-out tasks × 3 seeds, vanilla Claude Code produces a fully schema-valid deck in 24/30 runs (three runs emit XML that does not even parse; three emit parseable but schema-invalid decks), while every SIGA cell we evaluate — X+M, S+X, S+X+M, SE-prose and SE — reaches 30/30 (Fisher exact, two-sided p = 0.024; runs are clustered by task, so we report this descriptively). All 118 ground-truth deck files pass the same check, so the bar is both real and attainable. On the validation split, where the paper already reports a ceiling effect, the ladder shows the same near-saturation (49/51 vs 51/51), which is a consistency check on both the metric and the paper's central claim that adapters matter only on the hard tail. We note explicitly that rung 2 is partly enforced by construction in the S and X cells, since those adapters invoke `xmllint --schema`; we therefore read this as evidence that the adapter *delivers the guarantee it promises at no upstream cost*, rather than as an emergent property.

**Why this is worth more than it looks.** It converts the AC's "structural-only evaluation" from an unaddressed weakness into a two-rung ladder with a stated plan for rungs 3–5, and it is the specific thing gep1 tied his score to.

### 3.2 The S/X isolation (A3)

**What to do.** Lift the C2/C6/C7 build-up ablation from `docs/2026-04-30_dsv4-ablation-final-v2.md` into a new appendix table. It is 3 seeds × 17 tasks, already scored (`/data/shared/geophysics_agent_data/data/eval/dsv4_ablation_2026-04-29/`, 689 runs, all `success`). Cell definitions: `src/runner/agents.py:273` (`abl_c2_min_sr_no_rag`), `:319` (`abl_c6_xmllint_hook`), `:332` (`abl_c7_xmllint_full_no_rag`).

**Sentence to change.** L157 currently says only *"Because S and X both use `xmllint`, the X main effect partly conflates agent-callable validation with hook-time schema validation when S is also enabled."* Add after it:

> A separate build-up ablation on the same backbone and validation set (App. \ref{app:sx-isolation}; 17 tasks × 3 seeds) disentangles the two. Starting from a parse-check-only stop hook (0.913), adding schema validation *inside the hook* gives +0.008 (0.921) while adding the *agent-callable* validator on top of it gives −0.007 (0.914). The active ingredient is the mandatory hook-time check, not the optional tool.

And L272's limitation sentence should be replaced (see §5.4).

**Rebuttal claim:** the stop-hook effect not only remains dominant after separating S from X — the agent-callable validator is the null component. That is a stronger statement than gep1 asked for.

### 3.3 The prefix-bug contamination bound (A2, analysis half)

Even before you rerun anything, you can bound the contamination from data already on disk. `docs/ablation_C2_vs_C9.md` is a paired 3-seed × 17-task contrast of the identical cell with and without the native-plugin prefix on the headline backbone: **Δ = +0.0036, zero big-swing tasks (|Δ| ≥ 0.10)**.

Two consequences, both favorable:

1. The contamination magnitude on `deepseek-v4-flash` is ~0.004 TreeSim, roughly **8× smaller than the R main effect it allegedly contaminates** (−0.032, L412).
2. **The sign works against the paper's own conclusion.** The bug injected a prompt instructing the agent to call three unregistered MCP tools (`src/runner/prompts/native_plugin_prefix.txt`), and it was gated on `plugin_enabled` rather than `rag_enabled` (`src/runner/orchestrator.py`, fixed in commit `000b4ba`, 2026-05-03). It therefore affected only cells with the plugin loaded and **RAG off** — i.e. the R⁻ arm. Depressing the R⁻ arm biases the estimated R effect *upward* (toward zero). The debiased R effect is therefore approximately −0.032 − 0.004 ≈ −0.036: the "retrieval hurts" conclusion is **conservative**, not inflated.

> ⚠️ **Do not repeat the "+0.24" figure.** `.copilot/reviews/RN-006_...md:343`, `docs/2026-05-03_cross-cutting-summary.md`, `docs/2026-05-04_cross-cutting-paper-section.md:150` and `docs/2026-05-04_remaining-todos.md:21` all assert the prefix probe showed a "+0.24 DSv4 anomaly." The actual measured contrast in `docs/ablation_C2_vs_C9.md` is **+0.0036**. The +0.24 number appears to be an error introduced in RN-006 and propagated into three downstream docs. Citing it in a rebuttal would be a self-inflicted wound; citing +0.004 is both correct and helpful.

### 3.4 The OpenFOAM 30-task upgrade (A4a)

Rewrite §5.4 (L222–225) and App. F (L452–536) around the n=30 campaign in `docs/openfoam_n30/`. Concretely:

- L225 currently: *"the best cell (R+S) reaches mean 0.871, versus 0.466 for vanilla Claude Code and 0.569 for Foam-Agent"* on 5 tasks → replace with the 30-task row: R+S 0.870, Vanilla 0.681, Foam-Agent 2.0 lint 0.516, **MetaOpenFOAM lint 0.379**.
- Replace "Every S-enabled cell achieves full required-file coverage; Vanilla covers 3/5 and R+X covers 1/5" with the 30-task coverage story: every SIGA cell 30/30 full coverage and 0 zero-score, Foam-Agent 19/30 with 8 zero-score, MetaOpenFOAM 10/30 with 12 zero-score.
- Add the cost column (already computed in that doc: SIGA $23.20 across 9 cells / 270 task-runs, ~10× the baselines per task). Volunteering the cost disadvantage buys a lot of credibility and preempts a reviewer finding it.
- Keep the "transfer evidence, not a second benchmark" framing (L536) — it is still single-seed.

**Rebuttal claim:** the transfer study is now 30 tasks with two OpenFOAM-native baselines rather than 5 tasks with one, and the conclusion is unchanged and strengthened (stop-hook in all top-5 cells).

### 3.5 Uncertainty estimates and task representativeness (A7c, A17)

The AC asked for two things you can produce from `_summary.json` files without any new runs:

- **Per-seed values are already persisted** (`<campaign>/_results_icl/<run>/<agent>/_summary.json`, field `with_failures_as_zero_mean`). Verified held-out per-seed means: Vanilla 0.741 / 0.788 / 0.630; X+M 0.762 / 0.773 / 0.770; S+X 0.780 / 0.781 / 0.783; S+X+M 0.802 / 0.786 / 0.760; SE-prose 0.747 / 0.792 / 0.785; SE 0.797 / 0.795 / 0.775. Report **paired-by-task** bootstrap CIs on the Vanilla→SE delta rather than the seed std — with n=3 seeds the std is nearly uninformative, but you have 10 tasks × 3 seeds = 30 paired observations, which is a defensible resampling unit.
- **Representativeness (AC, A17):** the 10 held-out tasks are named at L303 and each maps to a distinct physics family. Add one sentence and a small appendix table stating the split protocol (46-task pool → 10 held-out / 18 distillation / 17 validation, index-parity split on training-run TreeSim, L303) and the physics coverage (thermo-poroelastic, hysteretic multiphase injection, modified Cam-Clay, proppant transport, fracture compression, hydraulic fracture, visco-plastic). Explicitly state that the held-out set was chosen to be *harder*, not random, and that this is why val is at ceiling and held-out is not — that is a design choice, and saying so out loud converts a perceived weakness into a stated method.

### 3.6 Free factual answers

**Claude Code version (A9, nBNe Q3).** **`2.1.119`** — **[VERIFIED]** present in the `system/init` event of every `events.jsonl`, e.g. `/data/shared/geophysics_agent_data/data/eval/autocamp_followup_2026-05-02/icl/autocamp_SE/SE_icl_s2/AdvancedExamplePureThermalDiffusionWellbore/events.jsonl`. The same event also records the exact tool list, the MCP servers registered and their connection status, `permissionMode: bypassPermissions`, and `model: deepseek-v4-flash`. Add to §4 "Baselines, models, and runs" (L171) and to the checklist — `checklist.tex:174` literally instructs "the authors should state which version of the asset is used," so this is a checklist gap as well as a reviewer request.

Suggested insertion at L171: *"All runs use Claude Code v2.1.119 with `permissionMode=bypassPermissions`; the exact harness version, registered tool list, and MCP server status are recorded in the `system/init` event of every run's `events.jsonl` and are included in the supplement."*

### 3.7 Cheap concessions that read as strength

See §5 for the drafted language. Do these in Tier 1 — they take minutes and they are what the reviewers explicitly invited.

---

## 4. Tier 2 — New work that takes real time

Ranked by (score impact) / (effort).

### 4.1 [RANK 1] Prefix-bug clean rerun (A2) — best ratio in the whole plan

**Design.** Rerun the contaminated cells with the post-fix code. Contaminated ⇔ `plugin_enabled=True ∧ rag_enabled=False ∧ no opt-out` ⇒ **F2 (S+M), F4 (X+M), F6 (S+X), F8 (S+X+M), F11 (SE-prose)**. F0 (plugin off), the R⁺ cells (F1/F3/F5/F7) and SE/v4 (explicit `add_native_plugin_prefix: False`, `src/runner/agents.py:702,717`) are clean.

Two scopes:
- **Minimum (recommended):** all 5 contaminated val cells × 3 seeds × 17 tasks = 15 runs / 255 task-runs. This is what actually lets you recompute the Resolution-IV main effects cleanly. *Note the plan currently written into the paper at L547 (F0/F4/F6/SE) is under-specified — it omits F2, F8, F11, so the R/S/X/M coefficients cannot be recomputed from it.*
- **Complete:** add the 4 contaminated held-out cells × 3 seeds × 10 tasks = 12 runs / 120 task-runs.

**Cost [VERIFIED from `events.jsonl` token sums via `scripts/paper_sim_cost.py`].** $0.0124/task-run mean at off-peak DeepSeek V4-flash pricing ($0.14/M cache-miss input, $0.0028/M cache-read, $0.28/M output; constants at `scripts/oh_dsv4_compare.py:56`), 314 s mean wall. So: 255 task-runs ≈ **$3.2**, ~2 h at `workers=4`. Both scopes together ≈ **$4.7**, ~3 h. Add ~$0.2 / 20 min for the gemini × X+M rerun (A2b).

> **Cost trap to avoid:** the `total_cost_usd` field Claude Code writes into `events.jsonl` is computed at Anthropic rates (~$0.77/run) and is *not* your DeepSeek bill. Documented at `docs/paper_experiment_map.md:144–152`. Do not quote it in the rebuttal.

**What satisfies gep1.** Recomputed main effects where R remains clearly negative and S/X/M remain within noise, plus the statement that the qualitative conclusion is unchanged. Given the C2-vs-C9 bound of 0.004 (§3.3), this is a very safe bet.

**Risk if negative.** Low but real: if the clean R effect collapses to ~0, the sentence at L86 ("the only main effect that clearly exceeds run-to-run variability is generic retrieval; however, it decreases performance") and L207/L401 must be softened to "no main effect clears the seed-noise floor on val." That is *survivable* — the paper's headline is the held-out reliability result, not the R effect — but it does cost you the "negative findings are valuable" strength gep1 praised. Mitigation: run it early so you know the answer before you write the response, and have both versions of the paragraph drafted.

### 4.2 [RANK 2] The GEOS execution ladder (A1b) — the AC's headline ask

This deserves the deepest treatment, so here is the full picture.

#### What exists on disk **[VERIFIED]**

- **No GEOS binary anywhere on this machine.** `which geosx` → nothing. `/opt/geos3.6.9` is libgeos (the geometry library), not the LLNL simulator.
- The checkout at `/home/matt/sci/repo3/data/GEOS` (→ `/data/shared/geophysics_agent_data/data/GEOS`, Feb 2026 snapshot) is **source-only**: no `build*`, no `bin/`, no TPLs, and **submodules are not populated** (`src/coreComponents/LvArray` and `src/cmake/blt` are empty directories).
- The eval container deliberately excludes the simulator: `run/Dockerfile` installs `libxml2-utils` and nothing else simulator-related, and `run/AGENTS.md:6-9` tells the agent *"You do not have access to simulation execution tools in this evaluation run. Do not try to run GEOS."*
- **Prior attempts stalled at the same place.** `/home/matt/sci/initial_geos_agent/geos-agent-image/Dockerfile` starts `FROM geosx/ubuntu22.04-gcc11:<TPL_TAG>` but the GEOS build lines are commented out with the note *"TPL dependencies from docker hub may be incomplete."* A docker image `geos-claude-runner:latest` on this host already contains the injection scaffolding (`COPY /geos-export/ /opt/` + a `ln -sf "$d/bin/geosx" /usr/local/bin/geosx` layer) but both layers are 0 B — it was built without a GEOS export. So the harness-side plumbing exists and the *build* is the entire risk.
- Environment is favorable: Docker 27.5.1, **128 cores**, 55 TB free on `/data`, and outbound network works (github.com → 200, Docker registry reachable). `GEOS_TPL_TAG` and the image repos are in `data/GEOS/.github/workflows/ci_tests.yml:139–207` (`geosx/ubuntu22.04-gcc11`, `-gcc12`, etc.).

#### The critical discovery that makes rung 3 cheap **[VERIFIED]**

`data/GEOS/src/coreComponents/mainInterface/initialization.cpp:123`:

```
{ VALIDATE_INPUT, 0, "v", "validate-input", Arg::None,
  "\t-v, --validate-input, \t Only do the loading phase, and not actual simulation. Useful to validate 'input'." },
```

and line 132: `{ ERRORSOUTPUT, 0, "e", "errorsOutput", ... "Output path for the errors file (\".yaml\" supported)" }`.

**GEOS has a built-in input-validation mode that loads and constructs the whole problem without simulating, and emits a machine-readable YAML error file.** This is exactly rung 3, it costs seconds per deck rather than hours, it needs no mesh partitioning or MPI, and it catches the entire class of errors `xmllint` cannot: unresolved cross-section name references (`materialList` entries that name no `<Constitutive>` block, `targetRegions` that name no region, `setNames` that name no `<Box>`), wrong attribute *values* on the right attributes, missing required sub-objects. Those are precisely the `bad_attribute_value` and cross-section-consistency failures the paper's own bottleneck analysis (L216, L270 (iii), L660-ish appendix) identifies as adapter-resistant.

#### The staged ladder to propose (use these exact rung names in the paper)

| Rung | Check | Tool | Needs GEOS build? | Status |
|---|---|---|---|---|
| **1** | XML well-formed | `xmllint --noout` | No | **Done** (§0.1) |
| **2** | Schema-valid against GEOS XSD | `xmllint --schema` | No | **Done** (§0.1) |
| **3** | GEOS loader accepts the deck (all objects constructed, all cross-references resolve) | `geosx --validate-input -e errors.yaml` | **Yes** | Tier 2 target |
| **4** | Deck initializes and completes N timesteps | `geosx -i deck.xml` with `<Events maxTime>` clamped | Yes | Stretch |
| **5** | Nonlinear solver converges / output is physically sensible | parse solver log + compare to GT run | Yes | Camera-ready / future work |

Rung 4 has a free accelerator you should exploit: the benchmark's decks come in `*_base.xml` / `*_smoke.xml` / `*_benchmark.xml` triples (verified in `experiments_gt/`), where the *smoke* variant is by convention the cheap short run. Grade rung 4 on the smoke deck only.

#### Build plan and honest odds

1. Read `GEOS_TPL_TAG` from `data/GEOS/.github/workflows/ci_tests.yml`; `docker pull geosx/ubuntu22.04-gcc11:$TAG`.
2. Populate submodules: `git submodule update --init --recursive` in a *writable copy* of the tree (the shared copy is read-only-ish and LFS may be unpopulated — check `git lfs pull`).
3. Configure with `scripts/config-build.py` against a `host-configs/` entry; build serial CPU-only, no CUDA, no GPU. On 128 cores expect a 1–3 h compile once configured.
4. Export `bin/geosx` into the existing `geos-claude-runner` image via its already-wired `--build-arg GEOS_IMAGE=` path — no new harness code needed.
5. Run rung 3 over the held-out decks: 6 cells × 30 runs × ~2.7 files = ~490 deck-loads, seconds each. Parallelize trivially across 128 cores.

**Odds [GUESS, but informed]:** ~55% that a usable `geosx` binary exists inside 3 days. The build itself is standard; the risks are (a) an unpopulated/LFS-incomplete submodule tree, (b) TPL tag drift between the Feb 2026 snapshot and the published image, (c) the exact failure the prior attempt hit. **Time-box it to 3 days and hand it to whoever is most comfortable with CMake/BLT.** Do not let it eat the clarity rewrite.

**Cost:** $0 API. CPU-hours only.

#### What result satisfies the reviewer

gep1: any monotone ladder where SIGA ≥ Vanilla at rung 3. AC: the existence of rung 3 at all, plus honest reporting.

#### Risk if rung 3 comes out negative — plan for this now

The realistic bad outcome is **not** "SIGA is worse." It is **"rung 3 pass rate is near zero for everyone,"** because a deck can be schema-valid and still fail to load (missing external table files like `buckleyLeverett_table/pvdg.txt`, referenced meshes, unresolved `<Included>` paths). The paper itself flags this at App. K: *"the deck parses but fails to construct the fluid model at runtime."*

Three pre-commitments that make a negative result survivable:

1. **Ship the file dependencies.** Copy the GT task's auxiliary directories (`*_table/`, external `.geos` tables, mesh files) alongside the generated deck before invoking `geosx`, exactly as the harness does for GT. Otherwise you are measuring your own harness, not the agent.
2. **Report the failure taxonomy, not just the pass rate.** The `-e errors.yaml` output gives you a per-deck error class. "0% pass, but 60% of failures are missing-external-asset and 40% are unresolved cross-section references, and SIGA halves the latter" is a *publishable and interesting* result that directly extends the bottleneck analysis.
3. **The paper is already insulated.** L272 states *"TreeSim is structural, not physical: a 0.8 deck is not guaranteed to run."* You never claimed runnability. A negative rung-3 result confirms your own stated limitation and sharpens the "harm-reduction, not correctness" thesis (L281). It *does* cost you gep1's conditional score bump, which is why rungs 1–2 must be delivered regardless and framed as the primary answer.

**Sequencing rule:** rungs 1–2 are the answer you promise. Rung 3 is upside. **Do not mention rung 3 in the rebuttal as work-in-progress unless it has landed** — a promise of future evidence is worth nothing in a rebuttal and invites the AC to defer. If it does not land, use the §5.1 concession language instead.

### 4.3 [RANK 3] Extra seeds on headline cells (A7a)

n=3 → n=5 on Vanilla, X+M, S+X, SE on held-out-eval = 4 cells × 2 extra seeds × 10 tasks = 80 task-runs ≈ **$1.0**, ~1 h at `workers=4`. Cheap, and it directly answers "provide uncertainty estimates" from the AC. Do it in the same batch as A2 to avoid a second launch cycle.

**Risk:** the +0.069 Vanilla→SE gap is driven by two task-level rescues (L209). Extra seeds could shrink or widen it. Given Vanilla's held-out σ = 0.081 comes from a single zero-score seed, more seeds will most likely *increase* Vanilla's mean and *shrink* the gap. **This is a real risk and it is why A7a is rank 3, not rank 2.** If you run it, you are committed to reporting it. Consider running it and only including it if it holds — which is legitimate only if you decide the inclusion rule *before* looking. Safer alternative: skip A7a and answer the uncertainty ask with the paired bootstrap in §3.5, which uses only data already reported.

### 4.4 [RANK 4] OpenFOAM multi-seed (A4b)

3 seeds × 9 cells × 30 tasks on OpenRouter DeepSeek. The n=30 doc records **$23.20 for a single seed across 9 cells**; three seeds ≈ **$70** and ~1–2 days wall. Only worth it if budget is ample and A1b has already landed or failed. The 30-task single-seed result (§0.2) already answers the ask well enough.

### 4.5 [RANK 5 — do not do] Foam-Agent execute mode (A4c)

Previously attempted and abandoned; `/home/matt/sci/repo3_openfoam/docs/openfoam/2026-05-07_openfoam_methods_experiments_results_analysis.md:343-352` records *"Execute-mode runs were not used for the final comparison table because they failed in this environment and produced unusable benchmark outputs."* Additionally, OpenFOAM 13 at `/data/brianliu/OpenFOAM-13` **is not compiled** (`platforms/linux64GccDPInt32Opt/` has no `bin/`, no `lib/`, zero executables). Making this work means building OpenFOAM *and* debugging a third-party agent inside a rebuttal window. **Decline and reframe** (§5.3).

---

## 5. Tier 3 — Cannot do; concede or reframe

The reviewers explicitly invited three of these narrowings. Narrowing is cheap and buys credibility with an AC who is looking for a reason to trust you. Treat these as **wins**.

### 5.1 If the GEOS build does not land (A1b/A1c fallback)

> On execution: we were not able to obtain a working GEOS build within the rebuttal window — the simulator requires a full third-party-library toolchain that our evaluation containers deliberately exclude, and our task decks additionally depend on external asset files that must be staged per task. Rather than promise future evidence, we report the two rungs we could complete without the simulator (well-formedness and validation against GEOS's own XSD, §5.1 of the revised paper), and we specify the remaining ladder precisely so that it is reproducible by others and by us for the camera-ready: rung 3 is `geosx --validate-input`, GEOS's built-in load-only mode, which constructs every object and resolves every cross-section reference without simulating and emits a machine-readable error file; rung 4 is completion of N timesteps on the short "smoke" variant of each deck; rung 5 is nonlinear convergence. We have revised every claim in the paper to be explicit that our evidence supports **structural authoring reliability, not validated simulator correctness**.

### 5.2 Human baseline (A5, A6) — concede fully and gracefully

gep1 Q4 and nBNe W3/Q2 both ask for this; nBNe additionally wants multiple expertise levels and a human-agent collaborative mode. A new human study needs recruitment, scheduling and plausibly IRB — **not feasible**, and no additional participant data exists on disk (`/home/matt/sci/repo3/data/human_baseline/` holds exactly P1, P2, and Dr. Sherman's written estimate).

Draft concession:

> We agree, and we have narrowed the claim rather than defended it. Two participants on one task is a calibration anchor, not a study of human authoring competence, and we have removed all comparative language from the abstract and introduction. Concretely, we replace "geoscience-domain-expert volunteers new to GEOS take between 8 and 36 times as long as the agent" (abstract) and the corresponding introduction sentence with: *"As an informal anchor on the scale of the authoring effort, two domain-expert volunteers new to GEOS did not complete a two-file deck for one of the easier benchmark tasks within a one-hour budget (n = 2, single task); we report this as a calibration point, not as a human-vs-agent comparison."* Section 5.6 now opens by stating the design limits (n = 2, one task, participants who are subsurface modellers rather than GEOS users, self-reported wall-clock) before any number appears, and the "36×" extended-budget figure is moved to the appendix as a single-participant observation. We also disclose there that the extended session included one navigation to an LLM chatbot, a deviation from the study instructions. Reviewer nBNe's suggestion of stratifying by GEOS experience level and adding a human–agent collaborative condition is, we think, the right design for a proper study; it needs participant recruitment we cannot complete in the rebuttal window, and we now name it as the specific follow-up.

*(Note: the disclosure at App. J currently argues the ChatGPT visit "strengthens the human-baseline anchor." That reads as advocacy. Delete the editorializing and just disclose.)*

### 5.3 Foam-Agent execute mode (A4c)

> Foam-Agent's native execute-and-review mode requires a compiled OpenFOAM installation that we could not bring up reliably in our environment; execute-mode runs failed to produce usable benchmark outputs, which is why we constrained both Foam-Agent and MetaOpenFOAM to lint-only mode. We agree this makes the comparison a constrained one and we have relabelled it throughout as **Foam-Agent (lint-only)**, stated in the caption and in the text that it is a lower bound on Foam-Agent's intended capability, and removed any claim of a head-to-head win. What the comparison does support is narrower and we now say only that: under a matched lint-only protocol on 30 tasks, the SIGA-wrapped general-purpose harness achieves complete required-file coverage on every task while both OpenFOAM-native systems do not.

### 5.4 Limitations rewrite (A8) — gep1 asked for this explicitly; give him the exact sentence

Replace the opening of the Limitations paragraph (L272) so the concession is the *first* thing, not buried mid-paragraph:

> **Limitations.** Our evidence supports **structural authoring reliability, not validated simulator correctness**. TreeSim measures agreement with a reference deck's structure, and the validity ladder of §5.1 establishes that adapter-produced decks are well-formed and schema-valid; neither establishes that a deck loads in GEOS, completes timesteps, converges, or produces physically meaningful output. Every claim in this paper about "reliability" should be read as reliability of the authoring process, not of the resulting simulation. Additional limitations: […existing text…]

### 5.5 Larger GEOS benchmark (A7b)

> We agree the 10-task held-out set is small. It is small by construction: the ten tasks are the compound multi-physics decks in our 46-task pool, reserved before any tuning and never used for distillation, self-evolution, or cell selection (App. A). Expanding it means hand-validating new ground-truth decks, which is the rate-limiting step and not something we can do responsibly in two weeks. We have instead (i) added the 30-task OpenFOAM benchmark to the paper in place of the 5-task subset, which triples the total number of distinct authoring tasks the claims rest on, and (ii) reported paired per-task uncertainty rather than seed standard deviation so that the 10-task result carries an honest interval.

### 5.6 Venue (A15) — one sentence, addressed to the AC, placed last

> On venue: we defer to the AC. We wrote the paper for the NeurIPS agents / AI-for-science audience because its contributions are about *agent design* — which wrapper-level interventions make a general coding harness reliable, and a component-wise factorial plus failure-mode decomposition that answers that question — rather than about geophysics methodology. We are glad to further foreground that framing if it would help.

Then stop. Do not add a second sentence.

### 5.7 "No new architecture" (A16) — do not respond at all

nBNe raised it and gave a 5 anyway. Responding invites reconsideration. If you feel you must acknowledge it, fold it into the global response as a single clause about the paper being deliberately a wrapper-level study of an existing harness — which gep1 lists as a *strength*.

---

## 6. Clarity / writing fixes

kEdh's complaints are enumerable, and **the AC independently endorsed them in their own words**, so treat this as an AC deliverable. Every item below is a specific line in `neurips_2026.tex`. I have written the replacement text; adapt tone as you like but do not water down the concreteness — the whole point is that a reader can see the diff.

Two structural moves first:

**(0a) Add a "Terminology" box at the end of §1.** Six definitions in one place: *deck*, *TreeSim*, *cell*, *factor*, *failures-as-zero*, *brief*. This is the single highest-leverage change for the "hard for a NeurIPS reader to follow" complaint, because it gives the reader one place to go back to.

**(0b) Move the GEOS deck definition from §3 to §1.** kEdh's item 2 is literally "Section 3 does explain what a 'deck' is, but this comes too late in the narrative."

### 6.1 Define "deck" early (A10 — kEdh 2, AC)

At L82, replace:

> *"Modern simulators are configured through executable interfaces such as XML decks, input scripts, and namelists, which are effectively domain-specific languages whose vocabulary and constraints are tied to a particular codebase."*

with:

> "Modern simulators are configured through an **input deck**: a text file, or small set of files, that completely specifies one simulation run — the computational mesh, the material models, which physics equations to solve, the boundary and initial conditions, the time-stepping schedule, and what output to write. GEOS decks are XML; other simulators call the same artifact an input script or a namelist. A deck is not a configuration file in the ordinary sense: its element names refer to specific classes inside the simulator's source code, and names introduced in one part of the deck must be referenced consistently in others, so it behaves more like a small program written in a language defined by one codebase."

Then at L111 (§3), cut the first two sentences, which now repeat this, and keep only the four difficulty items.

### 6.2 Explain the Resolution-IV factorial in one plain sentence (A11 — kEdh 1, AC)

At L84, after *"Our main experiment is a Resolution-IV $2^{4-1}$ factorial over four binary factors"*, insert:

> "In plain terms: rather than testing all $2^4 = 16$ on/off combinations of the four components, we run a carefully chosen half of them — 8 configurations — selected so that each component's individual effect can still be estimated separately from every two-component interaction. *Resolution IV* is the standard name for a fraction with that guarantee. It halves the compute, at the cost of not being able to separate certain pairs of two-component interactions from each other."

Add a one-line pointer at L157 as well: *"App. B lists the eight cells; readers unfamiliar with fractional designs can read Table 1 simply as eleven system configurations."* That last clause matters — it tells a reader who does not want to learn design-of-experiments that they can still read the results table.

### 6.3 Explain `buckleyLeverettProblem` (A12 — kEdh 1)

At its first appearance (L167, in the benchmark paragraph), add a parenthetical:

> "(e.g. `ExampleDPWellbore`, `ExampleMandel`, `buckleyLeverettProblem` — the last of these is a one-dimensional core-flood in which injected CO₂ displaces brine through a rock sample, a classical verification problem with a known analytical solution, and one of the easier tasks in our set)"

And at L237 in the human-baseline section, where it is the study task, keep the existing gloss but lead with the plain-English version rather than "1D immiscible CO₂/brine displacement."

### 6.4 Give an example of a "brief" and of "structured repair feedback" (A13 — kEdh 3)

**Brief.** The term appears at L230 and L594 without ever being shown. Add to §4 (after L167) a short quoted excerpt from a real task specification — the file is `/data/shared/geophysics_agent_data/data/eval/experiments_test36_template/buckleyLeverettProblem/instructions.txt`:

> "Each task supplies the agent with a **brief**: a natural-language specification of the simulation to set up, written in the language a researcher would use rather than in GEOS vocabulary. An excerpt from the `buckleyLeverettProblem` brief:
>
> > *'I need to set up a simulation to model a 1D Buckley–Leverett CO₂ core flood experiment… Since the numerical scheme requires a 3D grid, please create a hexahedral mesh of length 0.1 m in the x-direction… Permeability is 9.0e-13 m² in all directions. The reference porosity is 0.2 at a reference pressure of 10 MPa… Use a Brooks–Corey relative permeability model for the gas and water phases.'*
>
> The brief states physics and numbers; it never names a GEOS XML element. Translating it into `<CompositionalMultiphaseFVM>`, `<BrooksCoreyRelativePermeability>` and the rest is the agent's task. The complete briefs for all tasks are in the supplement."

**Structured repair feedback.** At L139, replace *"...and either allows termination or returns structured repair feedback"* with:

> "…and either allows the agent to stop or returns **structured repair feedback**: instead of the termination the agent requested, it receives a short generated message naming the offending file, the specific violation, and the action required. For example: *'Stop blocked by verify_outputs hook: XML parse error in `base.xml`: mismatched tag, line 84. Open the file, fix the syntax, then end your turn.'* The agent's turn therefore continues rather than ending, and a per-task counter caps the number of such re-prompts at two."

*(The quoted string is the real message template, `plugin/hooks/verify_outputs.py:313–320`; the missing-output variant is at `:303–308`.)*

### 6.5 Rewrite the failures-as-zero sentence (A14 — kEdh 2, quoted verbatim by him)

Replace L169 in full:

> "**Metric: TreeSim.** We score each generated deck with **TreeSim**, a similarity score in $[0,1]$ that compares the tree structure of the generated XML against the reference deck, reported separately for each of the ten canonical GEOS sections. A run can also fail in ways that leave nothing to score: the agent writes no XML file at all, writes a file that is not valid XML, or exceeds the time limit. We assign every such run a score of 0 and keep it in the average — we call this **failures-as-zero**. The alternative, averaging only over runs that produced a scorable file, would reward a system for failing loudly, because its worst outputs would simply drop out of the average."

### 6.6 Rewrite the "strictly perfect decks" sentence (A14 — kEdh 2)

At L86, replace *"The number of strictly perfect decks does not increase under any adapter"* with:

> "No configuration we tested produced more *exactly correct* decks (TreeSim ≥ 0.999) than the bare harness did: the adapters remove catastrophic failures without producing more perfect answers."

Same fix at L216 item (4) and at L281 in the conclusion, where the phrase recurs.

### 6.7 Other jargon a NeurIPS reader will trip on (not raised, but the AC said "many things")

Sweep these while you are in there — each costs one clause:

- **"cell"** — used ~40 times before it is ever defined. Define it in the Terminology box: *"a **cell** is one experimental configuration, i.e. one on/off setting of the four components."*
- **"hard tail" / "held-out-eval"** — say once, plainly, that held-out-eval is the deliberately harder set.
- **`failed_no_outputs`** — a raw status string exposed to readers at L169; replace with "the agent produced no output files."
- **"stop hook"** — one clause on first use: *"a callback the harness invokes when the agent tries to end its turn, which can refuse."*
- **"Resolution-IV generator D = ABC"** (L157) — move to the appendix; it means nothing to this audience in the main text.
- **`m1u`** (L312, L330, App. L) — an internal artifact codename. Replace with "the distilled cheatsheet" throughout.
- **`\sys` / `\textsc{GeoAgent}`** macro at L47 — dead macro from an earlier title. Remove before it renders somewhere unexpected.

---

## 7. Proposed rebuttal skeleton

**Assumed format [GUESS — verify against this year's instructions]:** a per-reviewer response box with a character limit around 5–6k (≈800–1000 words), plus the ability to upload a revised PDF. If a single global response is required instead, use the "Common response" block and cut the per-reviewer sections to ~200 words each of pointers.

### Common response (~450 words) — post first, reference from every reply

1. **(120 w) The validity ladder.** §3.1 text. Lead with it; it is the AC's headline concern and gep1's score condition.
2. **(90 w) The OpenFOAM study is now 30 tasks with two native baselines.** §3.4 numbers.
3. **(80 w) Clarity.** State that a revised PDF is uploaded, list the seven concrete changes by name (deck defined in §1, plain-English factorial, brief shown, repair-feedback example, failures-as-zero rewritten, terminology box, jargon sweep), and say the diff is visible in the revision.
4. **(80 w) Narrowed claims.** Human baseline, OpenFOAM transfer, Foam-Agent lint-only, and the new opening sentence of Limitations. Frame as "we have narrowed rather than defended."
5. **(80 w) Changes to the paper** — the shared block below.

### To gep1 (~700 words) — the score you are buying

Order by his own numbering, because he wrote conditionals and will check them.

1. **(220 w) Q1, execution.** Full ladder result with the 24/30 vs 30/30 table and the p-value. State the by-construction caveat yourself. If rung 3 landed, add 80 words with the `geosx --validate-input` pass rates. If not, use §5.1 and name the rung-3 protocol precisely.
2. **(200 w) Q2, prefix bug + S/X.** Three moves: (a) the direct measurement bounding prefix contamination at **+0.004** on the headline backbone, 3 seeds × 17 tasks; (b) the sign argument — the bug affected only R⁻ cells, so it biases the R estimate *toward zero* and the paper's conclusion is conservative; (c) the clean rerun of F2/F4/F6/F8/F11 with recomputed main effects. Then the C2→C6 (+0.008, hook-time schema check) vs C6→C7 (−0.007, agent-callable tool) decomposition: **the stop-hook effect is not merely dominant, the optional validator is the null component.**
3. **(120 w) Q3, OpenFOAM.** 30 tasks, MetaOpenFOAM added, Foam-Agent relabelled lint-only, claims narrowed to what a matched lint-only protocol supports.
4. **(90 w) Q4, human baseline.** The §5.2 concession, and the specific abstract/intro sentences that were cut.
5. **(70 w) Limitations.** Quote the new opening sentence verbatim — he asked for this specific statement, so give it to him in his own words.

### To kEdh (~600 words)

1. **(60 w) Open by accepting the premise.** "You are right that several core concepts are introduced too late or not at all. We have revised the paper rather than argued the point." No defensiveness, no "we believe the paper is clear."
2. **(400 w) A four-row before/after table**, one row per numbered complaint, with the actual replacement sentences from §6.1–§6.6. This is the whole response — a reviewer who wrote "not written well" responds to visible diffs, not to promises.
3. **(80 w) The changes he did not ask for**: terminology box, deck definition moved to §1, jargon sweep list. This signals the rewrite is systematic rather than a patch of his four items.
4. **(40 w) Venue**, §5.6, last, one sentence, addressed to the AC.
5. **Do not** mention the execution ladder to him beyond one clause — he did not raise it and it is not what he is voting on.

### To nBNe (~250 words)

1. **(60 w) Q3, Claude Code version 2.1.119**, plus the note that the harness version, tool list and MCP status are recorded per-run in `events.jsonl` and shipped in the supplement. He is the reproducibility-minded reviewer; this is the answer that pleases him most per word.
2. **(90 w) Q1, convergence/output validation.** The ladder, plus the explicit rung 3–5 roadmap with `geosx --validate-input` named. He asked about numerical stability and physical meaningfulness specifically — acknowledge that rungs 1–2 do not reach that and say exactly which rung would.
3. **(60 w) W3/Q2, human baseline.** The narrowing, and agreement that stratified expertise + a collaborative condition is the right design.
4. **(40 w) W4, scale.** 30-task OpenFOAM; paired per-task intervals on the GEOS result.
5. **Do not respond to W1.**

### To the AC (~300 words, if a separate channel exists; otherwise fold into the common response)

Mirror the AC's own four bullets in the AC's own order, one short paragraph each: structural-only evaluation → the ladder; clarity → the enumerated rewrite plus the revised PDF; experimental scale → 30-task OpenFOAM, representativeness of the 10 held-out tasks by construction, paired intervals; human comparison → narrowed. Close by stating plainly which of the AC's two conditions you believe you met and which you only partially met. An AC who is looking for a reason to trust the authors responds well to authors who mark their own limits.

### Shared "Changes to the paper" block

Put this once, verbatim, in the common response and reference it everywhere.

```
Revision summary (revised PDF uploaded):
 §1   Terminology box; "deck" defined on first use; plain-language gloss of the
      Resolution-IV design; buckleyLeverettProblem explained.
 §4   Failures-as-zero rewritten; an example task brief quoted; Claude Code
      version 2.1.119 and harness provenance reported.
 §3   Structured repair feedback shown with a real example message.
 §5.1 NEW: staged validity ladder (rungs 1-2 reported; rungs 3-5 specified).
 §5.4 OpenFOAM transfer replaced with the 30-task study; MetaOpenFOAM added as
      a second native baseline; Foam-Agent relabelled "lint-only" throughout.
 §5.6 Human baseline narrowed to a calibration anchor; comparative claims
      removed from the abstract and introduction.
 §6   Limitations now opens: "Our evidence supports structural authoring
      reliability, not validated simulator correctness."
 App. NEW: S-vs-X build-up ablation isolating hook-time from agent-callable
      validation; prefix-bug clean re-run with recomputed main effects;
      held-out task representativeness; paired per-task uncertainty.
```

### Suggested schedule (10 working days)

| Day | Work |
|---|---|
| 1 | Launch A2 + A2b reruns (background, ~3 h). Start the GEOS build (A1b) in parallel — this is the long pole. Formalize the ladder script (A1a). |
| 2 | Ladder table finalized across all cells. S/X appendix table written (A3). Rerun results in; recompute main effects. |
| 3 | OpenFOAM 30-task rewrite (A4a). Paired bootstrap intervals (A7c). Representativeness paragraph (A17). |
| 4–5 | Clarity rewrite (A10–A14 + §6.7 sweep). This is a full two days if done properly; do not compress it. |
| 6 | GEOS build check-in. **Go/no-go on rung 3.** If no-go, switch to the §5.1 concession and stop spending time on it. |
| 7 | If go: rung 3 run + failure taxonomy. If no-go: A7a extra seeds, or A18 cross-model recovery. |
| 8 | Draft all four responses. Rebuild PDF. |
| 9 | Internal adversarial read: does every number in the response match a file on disk? Cross-check the revised PDF against the rebuttal claims. |
| 10 | Submit. |

---

## 8. Open questions for the human

Ordered by how much they change the plan.

1. **Is there a working GEOS build on *any* machine you have access to — a cluster module, a collaborator's install, LLNL/Dr. Sherman's environment?** This is the single biggest fork in the plan. **[VERIFIED]** there is none on this host and the local source tree has unpopulated submodules. If Dr. Sherman (LLNL, already a contact per `data/human_baseline/dr_sherman_on_human_baseline.md`) can run `geosx --validate-input` on ~500 decks and return the YAML error files, that is a few hours of his time and it converts the AC's headline ask from "maybe" to "done." **Ask him on day 1.** Note the anonymity constraint — sending decks to a named external collaborator during review may or may not be acceptable; check the NeurIPS policy before doing it.
2. **What is the remaining API budget?** All my cost figures assume off-peak DeepSeek V4-flash at $0.0124/task-run **[VERIFIED from token sums]**. The full plan is ~$5–10; adding OpenFOAM multi-seed pushes it to ~$80. If the budget is effectively zero, drop A4b and A7a — nothing else in the plan needs money.
3. **Exact rebuttal format this year:** per-reviewer boxes or one global response? character limit? is a revised PDF upload actually permitted, and is there a page-count constraint on it? The §7 word budgets assume per-reviewer boxes of ~800–1000 words plus an unrestricted revised PDF. If a revised PDF is *not* permitted, the clarity work becomes far less valuable and the whole plan should shift weight toward A1b.
4. **Do you want to run A7a (extra seeds)?** It is cheap and answers the AC, but §4.3 explains why it plausibly *shrinks* the headline +0.069 gap, and once run you are committed to reporting it. My recommendation: **skip it**, and answer the uncertainty ask with paired per-task bootstrap intervals on existing data.
5. **Is the n=30 OpenFOAM campaign trustworthy enough to put in the paper?** It postdates submission by three weeks, lives under `/home/brianliu/`, and I read only its summary docs — I did not audit the scoring code or re-derive the numbers. Someone should spot-check `n30_hybrid_scores.json` against a couple of case directories before it goes in. Also confirm whether it is genuinely 30 tasks × 1 seed (the doc mentions "9 cells × 15 tasks" in its parallelization note, which I could not reconcile with the 30/30 coverage column).
6. **Who owns the CMake/BLT build?** A1b is the only item with real technical risk and it needs an owner on day 1, time-boxed to 3 days. If nobody can own it, decide *now* to go with the §5.1 concession and reallocate those days to the clarity rewrite.
7. **The "+0.24" discrepancy.** `.copilot/reviews/RN-006`, `docs/2026-05-03_cross-cutting-summary.md`, `docs/2026-05-04_cross-cutting-paper-section.md:150` and `docs/2026-05-04_remaining-todos.md:21` all claim the prefix probe showed a +0.24 anomaly; the measured contrast in `docs/ablation_C2_vs_C9.md` is +0.0036. Which is right? I believe the ablation file (it is generated output with a full per-task table), but you know the history. Correct the internal docs either way so nobody quotes +0.24 into the response.
8. **Version drift in the arXiv line.** **[VERIFIED]** the native-plugin-prefix disclosure is present in `writing/neurips/neurips_2026.tex:272,427,444,547` but has been silently dropped from `writing/arxiv/jun7_v0.tex` onward, including the current `writing/arxiv/siga_arxiv_2.tex` — while the still-uncorrected R⁻ numbers remain in that draft's Table 1. Whatever you do for the rebuttal, re-add the disclosure to the arXiv line. Removing a known-contamination caveat while keeping the contaminated numbers is the kind of thing that is very hard to explain later.
9. **The `gemini × X+M = 0.797` entry** in Table 5 (L438) is a pre-fix number sitting next to a post-fix minimax number in the same table. Confirm you want to rerun it (~$0.2, 20 min) rather than footnote it. I recommend rerunning — a table with one corrected cell and one uncorrected cell is exactly what a careful reviewer notices.
