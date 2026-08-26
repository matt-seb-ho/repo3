# Rebuttal revision brief — handoff for a fresh session

**Purpose.** Everything decided in the 2026-07-26/27 discussion that bears on **revising the four response texts**. Written so a new session can pick up the drafting work without re-reading the experiment logs.

**Scope boundary.** This document is about *revising responses*. The new overnight experiments (J1/J2/J3) are running in a separate session and are **not** load-bearing for the Jul 27 initial response. Fold them in later as follow-up comments if they land.

**Read alongside:** `HANDOFF.md` (sprint state, done/not-done), `SPRINT_LOG.md` (42 findings, 19 open decisions), `PROVENANCE.md` (number → source path, plus a retracted list and a forbidden-numbers list).

---

## 1. Where the drafts are

| File | Post as | prose chars | open slots | headroom to 10k |
|---|---|---:|---:|---:|
| `responses/gep1.md` | Rebuttal to gep1 | 9,550 | 0 | 450 |
| `responses/gep1_post2.md` | Official Comment, same day | 9,698 | 2 | 302 |
| `responses/kEdh.md` | Rebuttal to kEdh | 8,528 | 1 | 1,472 |
| `responses/nBNe.md` | Rebuttal to nBNe | 5,609 | 0 | 4,391 |
| `responses/AC.md` | Official Comment to AC | 9,987 | 2 | **13** |
| `responses/AC_post2.md` | Official Comment to AC | 6,507 | 3 | 3,493 |

All eight open slots are `[[BLOCKED: human decision …]]` markers, each naming its own fallback. **No slot is missing data.** Counts exclude HTML comments and the markers, both stripped before posting.

⚠ **`AC.md` has 13 characters of headroom.** Anything added must be paid for by trimming. `gep1_post2.md` has 302.

**Researcher feedback so far:** writing style concerns on `gep1.md`, to be addressed in the new session. Content was discussed and is captured below.

---

## 2. Decisions taken in the discussion

### 2.1 Reframe the headline: "bad-run prevention," not "catastrophic-failure elimination"

The researcher's position: reliability is the main selling point, but *a single catastrophic failure is too weak to carry it*. Add small efficiency gains as a second axis.

**Why the reframe is necessary — the per-seed data.** The two rescue tasks work by *different* mechanisms:

| task | Vanilla seeds | SE seeds | Δ |
|---|---|---|---:|
| ExampleProppantTest | 0.806, 0.817, **0** | 0.819, 0.829, 0.827 | +0.284 |
| AdvancedExampleThermoPoroElasticWellbore | 0.235, 0.772, **0.058** | 0.815, 0.729, 0.739 | +0.406 |

- ProppantTest **is** a true unscorable-output rescue — Vanilla's two *scored* seeds are statistically identical to SE's, so the whole gap is the one zero. But that zero is the double-hyphen deck **GEOS loads fine** (exit 0).
- ThermoPoro is **graded collapse**, not a zero-score failure. 0.058 and 0.235 are terrible decks, but present and parseable.

Only **1 of 180** held-out runs was actually unscorable. So "catastrophic" overstates it.

**Supporting evidence that the effect is nonetheless failure-driven** (four independent threads):

| source | evidence |
|---|---|
| Thread B | on the 24/30 (task,seed) pairs where every cell is schema-valid, **no metric separates the cells** — all Δ ≤ 0.014, all p ≥ 0.85 |
| Thread D | bootstrap on the mean lift: **[−0.009, +0.166]**, P(Δ≤0) = 0.052; median Δ +0.022 vs mean +0.069 |
| Thread C | `n_failed = 0` in all 21 val build-up run-cells |
| Thread F | 0 hook interventions in 410 val invocations vs 32/123 on held-out |

**Recommended claim:** *the adapter's effect is concentrated on runs where the baseline emits a deck that fails validation and is also structurally poor — bad-run prevention, not uniform quality improvement.* That survives the metric-artifact problem, doesn't lean on the word "catastrophic," and doesn't rest on a zero count of one.

Also true and worth not hiding: **Vanilla beats SE on 2 of 10 tasks** (PureThermalDiffusion −0.083, IsothermalHystInjection −0.039).

### 2.2 Add efficiency as a second axis — but anchor it correctly

| Cell | held-out tools/task | vs Vanilla | held-out wall s/task | vs Vanilla |
|---|---:|---:|---:|---:|
| Vanilla | 90.5 | — | 416.5 | — |
| X+M | 75.0 | **−17.1%** | 339.5 | **−18.5%** |
| S+X | 74.7 | **−17.5%** | 345.1 | **−17.2%** |
| S+X+M | 82.9 | −8.4% | 358.1 | −14.0% |
| SE-prose | 70.9 | **−21.6%** | 362.1 | −13.1% |
| SE | 97.4 | **+7.7%** | 389.8 | −6.4% |

On val the same gains are much smaller (X+M −2.4% tools, −6.2% wall). **Efficiency gains are larger exactly where the reliability gains are** — a coherent joint story: on hard tasks Vanilla thrashes and the adapter stops the thrashing.

⚠ **Two cautions.** SE is the one cell using *more* tool calls on held-out. And the **abstract's "~16% fewer tool calls" is SE-on-val (−15.5%) and reverses on held-out** — if efficiency is emphasised, that claim needs re-anchoring, and the hand-designed cells (X+M, S+X) are the ones to quote.

### 2.3 Researcher's framing for the paper's *positioning*

Not yet written into the drafts — decide whether it belongs in the responses or only in camera-ready:

> The current benchmark is relatively easy because the brief supplies most of the information. The main challenge as posed is learning the *organisation/structure* of the input deck, which vanilla Claude Code already handles fairly well. The setting where SIGA should shine is a harder one requiring more of the agent and less specification from the user.

For this submission: **emphasise reliability plus small efficiency gains**, and treat "raise task difficulty / reduce user specification" as the natural next step.

### 2.4 xmllint vs `geosx --validate-input` — a finding, not just an annoyance

GEOS's own documentation (`data/GEOS/src/coreComponents/fileIO/doc/InputXMLFiles.rst`) says *"Using a validation tool is highly recommended for all users"* and recommends exactly `xmllint --schema /path/to/schema.xsd input_file.xml`. **We followed the simulator's documented advice.** That reframes this from our error to an observation about GEOS's docs.

It is non-equivalent in **both** directions:

| Cell | xmllint OK | geosx OK | xmllint OK / **geosx FAIL** | xmllint FAIL / geosx OK |
|---|---:|---:|---:|---:|
| Vanilla | 24 | 19 | **7** | 2 |
| X+M | 30 | 21 | **9** | 0 |
| S+X | 30 | 20 | **10** | 0 |
| S+X+M | 30 | 21 | **9** | 0 |
| SE-prose | 30 | 23 | **7** | 0 |
| SE | 30 | 23 | **7** | 0 |

**49 of 180 task-runs (27%) pass `xmllint --schema` but are rejected by `geosx -v`.** `xmllint` misses 49 real defects and over-flags 2. Every adapter cell reports a perfect 30/30 while GEOS refuses 7–10 of the same decks — **our stop hook certifies decks the simulator will not load.**

What `xmllint` cannot see: cross-reference and arity errors — `PVT model PhillipsBrineDensity not found in input files`, `coupled solid constitutive model not found on subregion cb1`, `elementRegionsGroup has no child named rock`, component-count mismatches. **Exactly the residual failure class the paper's bottleneck analysis says no adapter fixes.**

**Proposed improvement to state in the responses:** replace the in-loop `xmllint` gate with `geosx --validate-input` (~2.5 s/deck). Reinforced by: **loading is the bottleneck, not solving** — on the two tasks whose reference converges, every deck GEOS accepted also converged (**31 of 31**). So the cheap check captures essentially all the execution signal.

⚠ **Frame as proposed future work + a documentation finding. Do not imply we ran it in-loop** (Thread J3 is testing it now; not load-bearing for Jul 27).

⚠ **Attach one failure mode when making this recommendation.** In J3's treatment arm, an in-loop GEOS validator with a **wrong root rule** induced the agent to **fabricate physics**: handed an orphan `<Included>` fragment that could never pass standalone validation, the agent invented a `standaloneDummyMesh` and a `dummyWell` and injected them into two base files — including one that legitimately needed neither.

**Scale, stated precisely: 1 fabricated task-run out of 20 completed.** A first pass over raw token counts looked like far more, but the ground-truth deck for a *different* task legitimately contains a 1×1×1 dummy mesh (TriaxialDriver needs no real mesh), and 2 of the 3 flagged runs were reproducing correct behaviour. A differential test against both ground truth and control isolates the single genuine case.

**The cause was our own root rule, not GEOS validation as such.** So this is evidence that a *mis-specified* in-loop validator can induce fabrication — an existence proof of the failure mode, not evidence that the approach is unsound. Whether a correctly-specified validator avoids it entirely is untested (a ~$0.52 A/B would settle it; decision H21).

**How to use it:** the lesson is **"unreferenced is not the same as root"** — an in-loop simulator validator must distinguish a standalone problem from an orphan fragment. Recommend the swap **with** this caveat attached. It is a stronger position than recommending it naively: it shows we implemented it, measured it, and found its failure mode ourselves. Do **not** inflate it into "in-loop validation backfires" — the evidence does not support that.

### 2.5 External data files — declared out of scope

The briefs **name the files but not their contents**. Verbatim: *"`strainFunction`: A table reading time coordinates from `tables/time.geos` and target values from `tables/axialStrain.geos`."* The same brief gives in-XML parameters explicitly (density 2700 kg/m³, shear modulus 50 MPa, …).

**Scope: 4 of 10 held-out tasks reference external data files** — ceiling control (3 refs), IsothermalHystInjection (19), singleFracCompression (1 `.vtu`), TutorialHydraulicFracture (22 refs / 35 non-XML files — the task scoring 0.013 in every cell).

**Researcher's decision: treat these values as provided / out of scope for the benchmark.** TreeSim stays positioned as a fast, scalable, deterministic, ground-truth-checked proxy. State the limitation; do not solve it in this submission.

### 2.6 Physical plausibility — propose a judge, but disclose the failed attempt

**Equivalence-to-ground-truth does NOT cover plausibility, and we should not claim it does.** It is sufficient where the deck *matches*, but decks sit at ~0.78, so roughly a fifth of the structure differs and TreeSim says nothing about whether those differences are material. Measured: **63–67% of the differences TreeSim scores as total mismatches are judged physically immaterial.**

**Recommended posture:** propose an LLM/agent judge for the semantic residual **as future work, while disclosing that our first attempt failed its reliability checks** (α = 0.21, position effects as large as the between-cell effect, one judge reversing Vanilla vs best cell). More credible than proposing it untried, and it pre-empts "why didn't you just do this?"

**Lead with execution-grounded checking rather than the judge**, because our own data says the judge adds nothing TreeSim doesn't already give: it correlated with loading at r = 0.61, but TreeSim matched or beat it on 3 of 5 rungs at zero cost.

**Position to take on value-level plausibility (researcher's decision, 07-27).** Judging individual deck *values* for physical plausibility needs a purpose-built benchmark and **domain-expert coordination** — a longer effort than this response window. Say we are working on it and that it will take longer; do **not** imply the section-level judge covers it. This is a clean, honest answer to "why not just have an LLM check the physics."

**What the judge experiment is actually doing now (J1, revised):** section-level, not value-level. The judge compares candidate against reference **one canonical GEOS section at a time** (`Constitutive`, `Mesh`, `Solvers`, …), which is the granularity TreeSim already reports via `treesim_section_scores`. That makes LLM-vs-TreeSim directly comparable per section, keeps enough context for a physical judgment, and cuts the judged units from ~34,000 value differences to ~900 sections. Judge is **`tencent/hy3`** via OpenRouter — similar intelligence-cost frontier to `deepseek-v4-flash` but a **different family**, which removes the self-preference objection.

---

## 2.7 🛑 READ THIS BEFORE TOUCHING ANYTHING ABOUT MAIN EFFECTS

**H3 is answered: DO NOT volunteer the main-effects correction. Cut that slot.**

The val scoring pass **raced the val campaign**. Verified directly: `autocamp_F3_s1`'s `_summary.json` finished scoring at 14:25:28, while the decks it was meant to score were written at 14:25:41, 14:25:51, and — for `TutorialSneddon` — 14:30:01 through 14:32:37, up to **7 minutes later**. `TutorialSneddon` is published as `treesim=None, status='error'`; **it did not fail, the scorer looked before the agent had written anything.** `TutorialPoroelasticity`'s 0.2371 came from one file with the smoke and benchmark decks absent.

**The published val numbers cannot be reproduced from the decks now on disk.** That is the defensible statement and it needs no theory of the mechanism.

**What this means for drafting:**

| | status |
|---|---|
| The planned correction (R −0.037 · S −0.008 · X +0.011 · M +0.008) | **rests on raced scores — do not publish** |
| De-raced values | R −0.0313 · S −0.0002 · X +0.0054 · M +0.0023 |
| F3 (R+S) val | **≈0.887 ± 0.011**, not 0.857 ± 0.045 |
| §5.1's *"X, M and S all fall within ±0.007"* | **TRUE on clean data** — so **H9 dissolves**; the correction would have broken a correct sentence |
| **All held-out numbers** | **UNAFFECTED** — `published == strict` on all 180 runs, worst diff 0.00e+00, cross-verified by two independently written scorers |

**So every headline claim in the drafts is safe** — the +0.069 contrast, the per-cell σ table, the reliability story, all the execution work. Only val is contaminated, and only the appendix main-effects table depends on val. No draft prose needs changing: the correction lived solely in a `[[BLOCKED]]` slot awaiting H3. **Delete that slot in `gep1_post2.md` and `AC_post2.md` and say nothing about main effects.**

If a reviewer raises the −0.032 vs −0.033 discrepancy in Phase 2, the honest answer is that we found a scoring-pipeline race affecting the validation split, we are re-deriving those numbers, and we will report them in the camera-ready — rather than offering a correction we cannot yet stand behind.

## 2.8 🛑 THE RUNG-2 NUMBER IN THE PAPER IS WRONG BY 2.3× — corrected in the drafts

We re-ran to **17 seeds**. The paper's three-seed sample happened to contain **the two lowest draws of seventeen**.

| | k/n | rate |
|---|---|---|
| published (3 seeds) | 24/30 | 0.800 |
| **pooled (17 seeds)** | **155/170** | **0.912** |

Adapter cells: **F6 170/170, F4 100/100 — 270 runs, zero failures.** Only the baseline moved.

**Real gap 8.8 points, not 20.** But the corrected claim is *better supported*: Fisher p < 0.0001 and a **task-clustered bootstrap [+2.9, +16.5] points, p = 0.0006** — a cluster-valid test the original never ran.

**Three consequences for drafting:**
1. **Lead with the self-correction.** With an AC probing execution validity, volunteering "we re-ran at 17 seeds and corrected our own number downward" is worth more than any p-value. Already drafted that way in `gep1.md`.
2. **Rename the rung.** 10 of Vanilla's 15 failures are **well-formedness**, not schema — chiefly *nested* XML comments. Call it "**well-formed and schema-valid**" and note that two-thirds of the deficit is a lexical bug, not schema knowledge.
3. **Rung 3 is a firm negative.** 133/170 vs 132/170, p = 1.0000, CI **[−5.3, +2.9]** — the interval *excludes* any adapter advantage above ~3 points. Not "underpowered", not "absence of evidence". **Do not revive it at any n.**

**⚡ A limitation worth putting in the paper.** For a mechanism that fires 3–6 times in 30 runs, power at n = 3 is ~0.00 — and in the infinite-seed limit the **task-clustered p converges to 0.0660 regardless of effect size**, because the effect enters as a pure scale factor that cancels. **No number of seeds can make such a mechanism cluster-significant on this 10-task benchmark; only more tasks can.** This is a real methodological point about our own benchmark and we should make it ourselves.

**⚠ H33 — open confound:** the published campaign is 86 days older, `deepseek-v4-flash` has no version string, and Vanilla's tool calls rose 21% (p = 0.038) between May and July with token production unchanged. Every new comparison is within-campaign and same-day so the headline is safe, **but the absolute May numbers are not reproducible in July.** Decide whether to disclose.

## 3. Concrete edits the drafts still need

1. **Reframe "catastrophic failure" → "bad-run prevention"** everywhere it appears (`gep1.md` opening, `AC.md` §1, `nBNe.md`, `gep1_post2.md`). Keep the σ numbers; change the interpretation.
2. **Add the efficiency axis** — held-out tools/wall for X+M and S+X, explicitly *not* SE. Currently absent from all four texts.
3. **Add the validator finding + proposed improvement** — the 27% cross-tab and the GEOS-docs point. Strongest placement is gep1 (score-moving execution question) and AC §1. Watch `AC.md`'s 13-char headroom.
4. **Add "loading is the bottleneck, not solving" (31/31 converged)** — currently only implied.
5. **Re-anchor or drop the abstract's "~16% fewer tool calls"** if efficiency is emphasised.
6. **Style pass on `gep1.md`** per the researcher's feedback.
7. Resolve the eight human-decision slots (H1, H2 ×2, H3, H3+H9, H7, H10 — see `SPRINT_LOG.md`).

---

## 4. Traps — do not undo these

Every item below was verified this sprint; several were falsified *after* being drafted. Full list in `PROVENANCE.md`.

| Do not write | Why | Correct version |
|---|---|---|
| "an unparseable file does not run in any simulator" | GEOS's pugixml tolerates `--` in comments; `xmllint` and our scorer don't. **The flagship zero-score deck loads with exit 0.** | distinguish *unscorable by our metric* from *unrunnable by the simulator*; call these **portability defects** |
| "val is at ceiling for every cell" | means are 0.913–0.921, worst task 0.77, only 3/17 tasks ≥ 0.99 | **`n_failed = 0`** — no failures for S or X to prevent |
| rungs 1→3 as a nested ladder | different parsers; overlapping, not nested | "overlapping checks on different parsers" |
| the `missing_external_asset` failures as "a fairness bug penalising adapter cells" | **refuted** — all six cells reference identical assets; only *staging* varies | measurement noise on 2 of 10 tasks, excluded from the primary denominator |
| "the hook fired 32 times in 123 invocations on held-out" / "on the hard tail the hook catches what self-validation missed" | **refuted** — those 32 blocks are from a *different campaign* (`se_icl_2026-04-30`), and Thread F's cell mapping was inferred, not confirmed. On the actual held-out F6 campaign the hook fired **0 times in 30 runs**. Already corrected in `gep1.md` Q2b | the hook never intervenes on **either** split when X is present (0/410 val, 0/30 held-out); the components are **substitutes**; this does **not** establish stop-hook dominance on the hard tail |
| "+0.24" for the prefix effect | mis-citation; that was the C1→C2 lift being explained | **+0.004** |
| "Table 1 is post-prefix-fix" | fix landed 2026-05-03; factorial ran 2026-05-01/02 | pre-fix; only minimax × X+M re-run |
| a mean from one cell with a σ from another | abstract pairs +7 pp (SE) with 40× (S+X); S+X is 44.5× at +0.061, SE is 6.56× at +0.069 | print the per-cell σ table; do not volunteer |
| schema validity as "the execution evaluation" | rung 2 of 5, and rung 3 is not significant | name the rung reached |
| the execution plan's TreeSim description (§4.4) | wrong — actual scorer is `|matching attrs| / |union of attr keys|`; greedy matching; root attrs excluded | say only "a tree match at 1e-6 tolerance" |
| "4× the runs" for a full factorial | arithmetic error in the arXiv draft | **2×** — 8 of 16 corners |
| the LMaaJ score table | fails four reliability checks; one judge reverses our contrast | report as built-tested-rejected |
| any verbatim arXiv sentence | preprint may be public → anonymity risk | paraphrase; all kEdh replacement prose is already written fresh |
| a delivery date for pending experiments | a missed promise lands right before Phase 3 | "we will post what lands" |

**Rung-3 figures are final**: Vanilla **19/30**, best 23/30; primary denominator (n=24) Vanilla 18/24, best 22/24. **None of the differences is statistically significant** — per-cell Fisher p 0.27–0.79, against p = 0.024 at rung 2.

**M = +0.008, not +0.009**, when quoting corrected main effects — computed from Table 1's printed means so gep1's own arithmetic agrees. Full precision is +0.0087 if asked.

---

## 5. Overnight experiment results (J1/J2 complete, J3 finishing) — none load-bearing for Jul 27

**All 28 human decisions (H1–H28) are defined in `SPRINT_LOG.md`'s "Open questions for the human" table**, each with a recommendation and the finding it derives from. The four that most change what gets posted: **H19** (how far to walk back the reliability framing), **H22** (volunteer ρ ≈ 0.40), **H23** (correct A2's stale CSVs — not optional), **H26/H27** (ship the per-section audit and the zero-LLM argument).

| Thread | What | Status at handoff |
|---|---|---|
| **J1** | Section-level LLM judge ("soft-TreeSim") | **DONE — FAILED its pre-registered bar; do not ship the metric.** Three components *are* shippable — see below. |
| **J2** | Simulation-output-side metric — continuous, mesh-independent, scale-free; headline is the TreeSim-vs-output-similarity correlation. | **headline landed** (see below); extending 3 → 6 tasks |
| **J3** | Re-run F6 (S+X) held-out with `geosx -v` in the stop hook instead of `xmllint`. | **Feasible**; hook implemented (additive, 286 insertions / 0 deletions); smoketest shows block → repair → allow on a real cross-reference defect; **cost estimate $0.58** vs a $60 gate. Zero-block control finding **confirmed and reconciled** (see below). Treatment arm running: seed 1 complete, seeds 2–3 in flight. |

### ⚠⚠ K3 SUPERSEDES J2 — n = 489 across 18 tasks. **Use these numbers, not J2's.**

| scope | n | ρ | 95% CI |
|---|---:|---:|---|
| **held-out (clean on both axes)** | 126 | **0.362** | [0.197, 0.505] |
| val (staged + re-scored) | 363 | 0.283 | [0.181, 0.379] |
| **POOLED** | **489** | **0.310** | **[0.227, 0.391]** |

**The estimate falls with power — J2's 0.402 (n = 108) → 0.310 (n = 489).** Still clearly non-zero. Per-task range is wide and must always accompany it: held-out 0.109 → 0.735, val −0.118 → 0.706.

**⚠ Reporting either aggregator alone would be indefensible.** Under the worst-reduction aggregator, held-out gives **ρ = 0.121, p = 0.176 — not significant** (val 0.303, pooled 0.261). On the only split clean on both axes, whether structure predicts simulation depends on the choice of summary statistic. **If ρ is quoted at all, quote both.**

**⚡ The result I would lead with instead — it is favourable and it is robust.** Conditional on the deck actually running, **the physics is usually right**: held-out SOF|ran mean **0.958** with 46% of runs at ≥0.999; val SOF|ran **0.913** with 66% at ≥0.999. **The physics gap is concentrated in decks that fail to run, not in decks that run wrong.** That is a direct, independent argument for the reliability-first framing — what matters is whether a deck runs at all, which is exactly the axis our reliability claim occupies.

**Cell separation: not detectable on any split**, and the held-out point estimate favours Vanilla (Δ = −0.0073, p = 0.409; 56,162 per arm needed). Fourth independent corroboration after B, D and J2. Always **"not detectable"**, never "no difference."

⚠ **Do not quote val per-cell SOF means** until someone checks a possible staging remnant: SE (0.910) and F11 (0.918) sit far above F0 (0.784), and those are precisely the two cells K1 found had zero unstaged-asset failures on val. K3 staged and re-proved the fairness invariant, so it *should* be clean — but the pattern matches the confound too closely to accept unverified (H32).

### ~~J2 (6 tasks, 108 runs)~~ — superseded by K3 above; retained for the method description only

**Use these numbers. An earlier 3-task version circulated with ρ = 0.29 and the opposite decomposition; it was underpowered, not wrong, and is superseded.**

| scope | n | ρ | p | 95% CI |
|---|---:|---:|---:|---|
| **Pooled (within-task ranks)** | **108** | **0.402** | **<1e-4** | **[0.23, 0.55]** |
| Meta-analysis (Fisher-z, 6 tasks) | 108 | 0.411 | 1e-4 | [0.22, 0.57] |
| Conditional on the deck running | 91 | 0.450 | <1e-4 | [0.26, 0.61] |
| **TreeSim vs runnability (0/1)** | 108 | **0.150** | **0.119 (n.s.)** | [−0.02, 0.32] |

**TreeSim is a *fidelity* signal, not a *runnability* signal** — the correlation strengthens conditional on running, and the runnability association is non-significant. **ρ² ≈ 0.17–0.25**: it explains a sixth to a quarter of the rank variance, leaving three quarters unexplained. **Per-task ρ spans 0.11 → 0.83** (2 of 6 tasks at ~0.11, I² = 42%) — **never quote the pooled number without the range.**

**Cell separation: none, and the point estimate now favours Vanilla.** SIGA (n = 90, 0.8054) vs Vanilla (n = 18, **0.8140**), Δ = −0.0086, Mann–Whitney p = 0.292; pooled Kruskal–Wallis p = 0.468. Third independent corroboration of Thread B and Thread D.

**J2's framing, recommended verbatim:**
> *Does structure track simulation?* → partly (ρ ≈ 0.41). *Do SIGA's structural gains produce better simulations?* → **not detectably.**

**Must disclose if the number is used:** under a worst-case aggregator instead of mean-over-reductions, ρ drops to 0.148 (p = 0.127, non-significant). That is the largest analytic sensitivity in the study; 11 of 13 other arms hold at ρ 0.28–0.40. Interpolation does not drive anything (ρ = 0.91–0.95 agreement with an interpolated variant).

**Power:** min detectable |ρ| ≈ 0.27 at n = 108. The SIGA-vs-Vanilla output contrast would need **n ≈ 26,000 per arm** — not merely unproven but unprovable at any realistic scale. Say "not detectable," never "no difference."

**H22 — volunteer ρ ≈ 0.40 or not?** Lean **yes, with the per-task range and the aggregator sensitivity.** It answers the AC's decision criterion with a real instrument, and it is more favourable than the 3-task version suggested. Mitigations already in the drafts: the **common-mode** argument, and the fact that the reliability claim does not depend on TreeSim's semantics at all.

### J1 FINAL — the judge metric is not shippable, but three findings from it are

**Do not ship the soft-TreeSim cell score table.** It failed 4 of 5 pre-registered criteria (thresholds fixed *before* any judge call; rubric hash-verified). **Two independently designed judge metrics have now failed their own reliability tests** — that is itself the honest thing to report, and it pre-empts "why didn't you just use an LLM judge?"

Nuance to carry if the reliability number is ever quoted: **α = 0.391 is a prevalence artifact, not disagreement.** Raw exact agreement is 70.3% (vs v1's 41.5%), but 74–94% of verdicts are `equivalent`, so α collapses (kappa paradox); **Gwet's AC1 = 0.811**. The correct phrasing is *"chance-corrected reliability cannot be established on this label distribution,"* never *"the judges disagreed."* Report both statistics.

**Three things from J1 that ARE shippable:**

1. **The per-section audit of TreeSim (recommended).** The judge is systematically more lenient than TreeSim on `Outputs` (+0.100), `Events` (+0.101), `ElementRegions` (+0.069) and harsher on `Solvers` (−0.050), `Constitutive` (−0.031). And `Outputs` correlates with TreeSim at r = 0.098 while `Constitutive` reaches r = 0.751. **This audits the metric, not the systems, so it does not require the judge to discriminate cells reliably** — which is exactly what failed.
2. **The zero-LLM execution argument (strongly recommended).** 10 decks fail to load as `missing_external_asset` — **0 of 10 load, yet TreeSim scores them 0.840, above the 0.763 held-out mean.** The cleanest demonstration available that an input-side structural metric cannot answer the execution objection, and it needs no LLM at all.
3. **The deterministic fix beats the LLM panel.** 79.4% of comparison units have no candidate counterpart, and the section judge cannot help there because matching stays hard. A **3-line deterministic change to `_bipartite_match`** lifts that subgroup 0.661 → 0.727 and rung-3 AUC 0.803 → **0.830** — **more than the entire four-judge, $12.70 LLM panel delivers, for free.** This is the honest headline of the judge work.

**One caution if soft-TreeSim is mentioned at all:** it does **not** reproduce the σ-collapse (S+X seed sd 0.0015 → 0.0097 — the judge *adds* variance), and it has a 5.2% verdict flip rate at temperature 0. TreeSim's determinism is a real advantage; soft-TreeSim can only ever be a complement.

⚠ **J1-vs-J2 conflict, treat J2 as authoritative.** J1 reports neither metric predicts QoI error (|Spearman| < 0.04, **n = 20**) while J2 finds ρ = 0.402 (**n = 108**). J1's QoI inputs came from A2's CSVs, which **J2 proved stale**, and n = 20 is badly underpowered. Use J2's numbers.

### ⚠⚠⚠ The single most quotable finding of the sprint — and it lands on our own flagship number

**`ExampleProppantTest` `F0_s3`: TreeSim 0.000 — the lowest structural score in the study — and its simulation matches the reference exactly, SOF = 1.0000.**

This is the same run that our scorer calls unparseable, that single-handedly produces Vanilla's held-out σ = 0.081, and on which the "≈40× variance reduction" claim rests. It **loads in GEOS with exit 0**, **runs to completion**, and is **physically indistinguishable from the reference**. Its only defect is a prose double hyphen inside an XML comment.

So the paper's headline catastrophic failure is **a metric artifact end to end**. This strengthens the "**portability defect, not execution failure**" reframe already in `gep1.md` — we can now say the deck not only loads but reproduces the reference physics — and it is the clearest single illustration of the structural/physical gap we have.

⚠ **H23:** it surfaced only because J2 found **A2's published CSVs are stale by 2 of 38 records** (`F0_s3` and `SE_s2` are published as QoI failures but succeeded, both corrections running *against* A2's failure counts). **A2's artifacts must be corrected before anything is quoted from them.**

⚠ **H24:** `ExampleIsothermalHystInjection`'s **ground truth cannot run** — its top deck includes a file that does not exist anywhere in the GT tree. A broken reference in our own benchmark; decide whether to disclose.

### ⚠⚠ J3 FINAL — the validator swap works, but it **trades away the efficiency claim**. These two cannot be asserted from the same configuration.

| | control (xmllint) | treatment (`geosx -v`) |
|---|---|---|
| rung 3 | 20/30 | **24/30** (100% of the 24/30 ceiling; **only +2 of 4 attributable** — two flips were on never-blocked runs) |
| TreeSim | 0.7814 (σ 0.0018) | 0.7861 (σ **0.0240** — 13× worse) |
| **tools/task** | 74.7 (**−17.5%** vs Vanilla) | **115.7 (+27.8% vs Vanilla)** |
| wall-clock | 345.1 s | 330.7 s (−4.2%, n.s.) |

**The conflict, stated plainly.** §2.2 recommends emphasising efficiency (X+M and S+X at −17% tools, −17 to −18% wall-clock on held-out). §2.4 recommends proposing the `geosx -v` swap. **The swap costs +54.9% tool calls and destroys S+X's near-zero seed variance.** Both claims are true, but they describe *different configurations*, and asserting them together implies a system that does not exist.

**Recommended framing** — it is honest and still favourable:
> The configuration we evaluated is both more reliable and more efficient than the baseline. The improvement we propose — grounding end-of-turn verification in the simulator's own loader rather than a schema linter — buys loading validity at a measurable cost in tool calls, and we report that trade rather than presenting a free lunch.

That is a stronger position than an unqualified recommendation: it shows we implemented the fix, measured it, and know what it costs.

### ✅ The single cleanest execution result of the sprint — recommended for the AC and gep1

**`TutorialHydraulicFractureWithAdvancedXML` went 1/3 → 3/3 loading, via three genuine hook interventions, while TreeSim stayed pinned at 0.013.**

**Loadability and structural similarity are orthogonal — demonstrated, not argued.** No LLM, no QoI machinery, no statistics. It pairs naturally with the other zero-LLM item (10 decks, 0/10 load, TreeSim 0.840 — above the held-out mean) to make the case that an input-side structural metric cannot answer the execution objection.

Supporting evidence the mechanism is real: the agent's own repair in the smoketest was *"`rockThermalCond` needed to be included in the `CellElementRegion`'s `materialList`"* — a cross-reference fix `xmllint` structurally cannot see.

**Retry budget is NOT binding** (0/30 exhausted on genuine blocks) — an earlier interim claim to the contrary was withdrawn; it rested on a spurious block.

### ⚠ J3's confirmed finding changes a score-moving section — already applied to `gep1.md`

**On held-out F6 the xmllint stop hook fired zero times in 30 runs, because every deck was already schema-valid — while the simulator refuses 10 of those same 30 decks.** On this split S contributes nothing through its intended mechanism: *the defects were not absent, they were invisible to the validator we chose.*

Verified three ways: J3's ladder reproduces A1's F6 numbers row-for-row (r1 = 30, r2 = 30, r3 = 20); rung 2 = 30/30 makes zero blocks a **logical necessity** for an `xmllint` hook; and J3 read the original campaign's files rather than re-running, so a misconfigured control is ruled out by construction.

This **falsified** the claim in `gep1.md` Q2b that the hook "fired 32 times in 123 invocations" on the hard tail — those blocks come from a different campaign (`se_icl_2026-04-30`), and Thread F's cell mapping was inferred rather than confirmed. Q2b now states plainly that the hook never intervenes on either split when X is present, and that this does **not** establish stop-hook dominance on the hard tail. **Part of a claimed win became a concession** — but it makes the validator swap the constructive answer, and it sharpens §2.4 considerably.

**Open decision H20:** how to present that concession to gep1, whose stated bar was "my confidence would increase if the stop-hook effect remains dominant after removing this confound." We can no longer claim dominance on the hard tail. The strongest honest reply pairs the concession with the diagnosis — the mechanism was inactive because the chosen validator could not see the defects GEOS catches — plus the proposed fix.

---

## 6. Standing constraints

- **Nothing has been posted to OpenReview.** A human posts.
- 10,000 characters per response, plain text + markdown, **no uploads, no links, no images**.
- Anonymity: nothing identifying, and no verbatim arXiv sentences.
- Every number must trace to a file on disk — gep1 recomputes things.
- Deadline: **Jul 27 AOE (05:00 PT Jul 28)** for the initial response; Aug 3 is the last day anything can be posted.
