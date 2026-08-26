# Thread L1 — validating the semantic plausibility judge against a *physical* ground truth

**Submission:** NeurIPS 2026 #31642 (SIGA), author response.
**Owner:** L1. **Started:** 2026-07-27, after J1 and K3 completed.
**Artifacts:** `neurips_review/sprint/artifacts/L1_*`
**API spend: $0. New GEOS runs: 0.** Everything below is a re-analysis of data already on disk.

---

## STATE OF PLAY

### *** VERDICT: the judge does NOT beat plain TreeSim at predicting physical fidelity. It ties it. ***
### *** But the judge's PER-SECTION scores do carry physics information TreeSim lacks — and its own deck-level aggregation throws that information away. ***

**Answer to the headline question, primary convention (within-task percentile ranks, K3's), n = 63:**

| SOF variant | n | ρ(soft-TreeSim) | ρ(TreeSim) | **Δ (soft − TreeSim)** | **95 % CI** | boot p |
|---|---:|---:|---:|---:|:---:|---:|
| **SOF mean-over-reductions, ALL runs** | 63 | 0.338 | 0.379 | **−0.040** | **[−0.257, +0.166]** | 0.719 |
| SOF mean-over-reductions, conditional on running | 47 | 0.411 | 0.421 | −0.010 | [−0.293, +0.258] | 0.944 |
| SOF **worst-reduction**, ALL runs | 63 | 0.170 | 0.206 | −0.036 | [−0.263, +0.181] | 0.744 |
| SOF **worst-reduction**, conditional on running | 47 | 0.148 | 0.175 | −0.027 | [−0.322, +0.260] | 0.852 |

Under the pre-registered convention the point estimate is **negative in all four cells** — plain
TreeSim is nominally the better predictor of physics — and every CI contains 0. Under the secondary
raw-value convention the sign flips (Δ = +0.065 [−0.032, +0.171] on SOF_all) and still contains 0.
**The honest reading is a tie whose sign is not even stable across conventions.**

**This is the middle outcome of the three the brief anticipated: the judge adds nothing over a free
deterministic metric at the deck level, and that must be said plainly.** It is *not* the third
outcome — soft-TreeSim is genuinely correlated with SOF (ρ = 0.338, permutation p = 0.006;
conditional ρ = 0.411, p = 0.005). It tracks physics. It just does not track it any better than the
metric we already have for free.

**Power. The study is underpowered for the headline and this is not a null to lean on.**
Minimum detectable |ρ| at n = 63 is **0.356** (80 % power, α = .05); at n = 47 it is **0.409**.
For the *paired difference* the bootstrap SE is 0.107 (n = 63) / 0.140 (n = 47), so the minimum
detectable |Δρ| is **0.299 / 0.393**. An advantage of Δρ = +0.2 would have been invisible here.
**We can rule out a large advantage for the judge. We cannot rule out a moderate one.**

**The interesting finding, and it survived the controls (but is not pre-registered).**
Splitting the judge's score by section:

| x | ρ with SOF_all (n = 63) | perm p |
|---|---:|---:|
| judge credit on **physics** sections (`Solvers`, `Constitutive`, `FieldSpecifications`, `Functions`) | **+0.418** | 0.0006 |
| judge credit on **bookkeeping** sections (`Outputs`, `Events`) | **−0.224** | 0.081 |
| soft-TreeSim, deck aggregate | +0.338 | 0.006 |

Separation D_judge = **+0.642, 95 % CI [+0.313, +0.941]**. TreeSim's own sections separate too, but
much less: D_TreeSim = +0.264 [+0.003, +0.519]. Difference-in-differences **+0.377 [+0.046, +0.703],
p = 0.027**; conditional on running, **+0.545 [+0.128, +0.945], p = 0.011**. And controlling for
plain TreeSim, `judge_physics` retains a partial ρ of **+0.283 [+0.093, +0.461]** with SOF while the
deck aggregate `soft_TreeSim` retains only +0.172 [−0.034, +0.363].

**So the judge does read physics — and then TreeSim's uniform 1/N section weighting averages that
signal against bookkeeping sections where the judge's score is *negatively* related to SOF, and the
two cancel.** That is a concrete, actionable diagnosis of why the deck-level metric ties.
**Under the worst-reduction aggregator the DiD is not significant** (+0.157 [−0.146, +0.461]) — the
aggregator choice flips it, exactly as K3 warned it would. **And no S1/S2 test survives Bonferroni
over its own family.** Suggestive, not established.

**Join integrity: 63 / 63 rows matched, 0 mismatches.** J1's TreeSim and K3's `treesim_published`
agree to 1e−4 on all 62 rows where both exist; the 63rd is a deck with no J1 TreeSim, and both
sources independently score it 0.0. soft-TreeSim rebuilt from the 5440 raw judge verdicts reproduces
`J1_section_deck_scores.csv` to its own 6-dp rounding on all 90 J1 decks. Details in §2.

**What a human must decide: §7.**

---

## 1. Why this thread exists

Thread J1 built a section-level LLM judge ("soft-TreeSim") and pre-registered its utility criterion
U1 as *"beats TreeSim at predicting whether the deck loads."* It passed (ΔAUC = +0.045, 90 % CI
[+0.007, +0.087]). But **loading is a syntactic/structural property, which is TreeSim's own
territory** — so the one criterion the judge passed answered the wrong question. J1 itself flagged
the gap (`J1_judge_v2.md` §11.8.5: neither metric predicts QoI error, |ρ| < 0.04 at n = 20), but had
no physical ground truth at adequate n.

Thread K3 then produced one: **simulation output fidelity (SOF)**, 489 runs across 18 tasks. SOF is
computed from the actual GEOS output bundle — if a generated deck produces different physics from
the reference, SOF says so. **Correlating the judge against SOF is the correct validation of a
"physical plausibility" metric, and it had not been run.** This thread runs it.

Nothing here is a new measurement. Both axes existed; L1 is a join and a set of paired statistics.

---

## 2. THE JOIN, and how it was checked before anything was believed

Script `artifacts/L1_join.py` → `L1_joined.csv` (63 rows × 52 cols), `L1_join_report.txt`,
`L1_sections_long.csv` (per-deck-per-section long form, joined decks only).

### 2.1 What each side covers, and what the intersection is

| | coverage | n |
|---|---|---:|
| J1 (judge) | held-out split, cells **F0 / F6 / SE**, 10 tasks, seeds 1–3 | 90 decks |
| K3 (SOF) | **held-out** 6 cells × 7 tasks × 3 seeds = 126, plus **val** 11 cells × 11 tasks × 3 seeds = 363 | 489 runs |
| **Intersection** | **held-out, F0 / F6 / SE, 7 tasks, seeds 1–3** | **63 runs** |

**Held-out only, deliberately.** J1 never judged a val deck, so no val row could enter regardless —
and this is the split K3 §6 declares clean on *both* axes. Val's SOF axis was confounded by unstaged
external assets that track cell identity, and its TreeSim axis came from a scoring pass that raced
the campaign; both were fixed by K3/K1/K2, but held-out needs no caveat at all. **No number in this
thread carries a val caveat.**

### 2.2 Rows dropped, and why (G3)

| dropped | n | reason |
|---|---:|---|
| J1 decks with no SOF | 27 | 3 tasks failed **K3's reference gate**: `ExampleMCCWellbore` (reference timed out at 600.1 s), `ExampleVerticalPoroElastoPlasticWellbore` (reference timed out at 600.3 s), `TutorialHydraulicFractureWithAdvancedXML` (reference failed at the injection stage). |
| K3 held-out runs with no judge score | 63 | cells **F4, F8, F11** — J1's panel only judged F0 / F6 / SE. |

Both exclusion sets are **decided upstream of any generated deck's outcome**: the reference-gate
failures are properties of the *reference* deck's own behaviour, and the cell restriction is J1's
pre-existing panel budget. Neither can be outcome-driven on the y axis.

### 2.3 Integrity gates — asserted in code, not assumed

Seven harness bugs have been found in this sprint, every one biasing toward our own conclusion. So
the join asserts rather than trusts:

| gate | check | result |
|---|---|---|
| **G1** | soft-TreeSim **rebuilt from the 5440 raw order-A judge verdicts** (median credit over the 4 judges → J1's frozen `aggregate()`) vs `J1_section_deck_scores.csv`, all 90 J1 decks | worst \|diff\| = **5.0e−7** — exactly the CSV's own 6-dp rounding |
| **G1b** | same for the instructed-pair score `soft_pair` | **5.0e−7** |
| **G2** | plain TreeSim rebuilt from J1's section decomposition vs the same CSV | **5.0e−7** |
| **G2b** | J1's `treesim_of_record` vs **K3's** `treesim_published`, on the 63 joined rows | **62 / 62 exact to 1e−4, 0 mismatches** (63rd row has no J1 value — see §2.4) |
| **G2c** | K3's K2-strict re-score vs published TreeSim, joined rows | **0 rows differ** — K2's 4 corrections were all in val |
| **G3** | every J1 deck and every K3 held-out row matched or dropped with a named reason | 90 = 63 + 27; 126 = 63 + 63 |
| **G4** | the headline Δρ re-derived **from the convention in words**, pure Python, no numpy/scipy, importing nothing from J1/J2/K3/L1 (`L1_recheck.py`) | **matches `L1_report.txt` §1 to 3 dp in all four cells** |

G2b is the load-bearing one: it is an **independent** confirmation that the two threads' `(cell,
seed, task)` keys point at the same deck, because the two pipelines computed TreeSim from different
code paths (J1 from `_summary.json` via `J1_sections.py`; K3 from `K3_paths.py`) and agree to 4 dp on
all 62 comparable rows.

### 2.4 The one row where the two sides disagree — and it is a real finding, not a bug

`F0_s3_ExampleProppantTest`. J1 has **no** TreeSim for it: `load_and_resolve_dir` raises
`ValueError: not well-formed (invalid token): line 4, column 21`, so J1 marks it `rung1_fail` and
scores both TreeSim and soft-TreeSim **0.0**. K3 also records `treesim = 0.0`. So the two agree.

**But K3 ran the deck and it scored SOF = 1.000 — a perfect reproduction of the reference physics.**

Cause, verified by hand: the generated deck's header comment reads
`<!-- Proppant Slot Test -- Base Case ... -->`. A `--` inside an XML comment is illegal XML, so
Python's `ElementTree` rejects the file; GEOS's own parser (pugixml) accepts it. I confirmed the
executed deck is the *generated* one and not the reference — the run directory's deck differs from
the generated deck by exactly one injected `a2vtk` output block, and differs from the reference by
three element names.

**Consequence: a deck that GEOS runs to bit-level physical agreement is scored 0.0 by TreeSim, and
soft-TreeSim inherits the 0.0 unchanged.** This is a TreeSim failure mode that the judge, as
designed, cannot fix — J1's rubric v4 hands rung-1 failures straight through. It is one row in 63,
and §4(a) shows the headline is insensitive to it, but it belongs in the paper's metric-limitations
discussion alongside J1 §11.6's blind spots.

### 2.5 Composition of the joined set (and two degeneracies, declared up front)

| task | n | ran | sd(SOF_all) | sd(soft-TreeSim) | sd(TreeSim) |
|---|---:|---:|---:|---:|---:|
| AdvancedExampleCasedThermoElasticWellbore | 9 | 8 | 0.3106 | 0.0600 | 0.0545 |
| AdvancedExamplePureThermalDiffusionWellbore | 9 | 8 | 0.3299 | 0.0883 | 0.0570 |
| AdvancedExampleThermoPoroElasticWellbore | 9 | 6 | 0.4574 | 0.2798 | 0.2499 |
| AdvancedExampleViscoExtendedDruckerPrager | 9 | 9 | 0.1024 | **0.0000** | 0.0283 |
| ExampleIsothermalHystInjection | 9 | **0** | **0.0000** | 0.0587 | 0.0320 |
| ExampleProppantTest | 9 | 7 | 0.4154 | 0.2715 | 0.2566 |
| ExamplesingleFracCompression | 9 | 9 | 0.0257 | 0.0747 | 0.0361 |
| **TOTAL** | **63** | **47** | | | |

Two tasks carry no rank information on one axis, and both were identified before any correlation was
read:

- **`ExampleIsothermalHystInjection`** — 0 / 9 generated decks produced output, so SOF is constant at
  0. (K3 reports this task's per-task ρ as `n/a` for the same reason. Note it is also the one
  held-out task that needed K1's asset staging; since it contributes zero SOF variance, the staging
  question is moot for L1.) Dropped in §4(b).
- **`AdvancedExampleViscoExtendedDruckerPrager`** — soft-TreeSim is **constant at 1.000** across all
  9 decks: the panel calls every deviation `equivalent`, while TreeSim ranges 0.911–1.000 and SOF
  ranges 0.765–1.000. The judge has *no* discrimination on this task. That is a small, concrete
  instance of the ceiling effect that limits it.

### 2.6 The ceiling on the y axis — the real reason the conditional test is weak

Of the 47 runs that produced output, **24 reproduce the reference EXACTLY (SOF = 1.000)** and 35 are
at or above 0.99. Median SOF_ran = 1.0000, IQR [0.9724, 1.0000]. **Only about a dozen runs carry any
graded fidelity signal.** The brief anticipated this ("roughly half reproduce the reference almost
exactly") and it is confirmed. Any comparison of two highly-correlated predictors on ~12 informative
points is going to be inconclusive, and that is what happened.

---

## 3. HEADLINE — the paired comparison

Script `artifacts/L1_analyse.py` → `L1_report.txt`, `L1_results.csv`.

**Method.** K3's / J2's statistics, *imported* from `J2_validate` rather than re-implemented so they
cannot drift: `spearman_fast` (20 000-draw permutation p, 10 000-draw percentile bootstrap CI, RNG
re-seeded to 20260727 per call) and `n_for_spearman` (Bonett–Wright). Primary convention is K3's:
pooled Spearman on **within-task percentile ranks** (`rankdata(v)/(n+1)` within task); pooled-on-raw
is the declared secondary. Both aggregators always. All runs and conditional-on-running always.

The paired difference resamples **(soft, TreeSim, SOF) triples together**, so both correlations are
computed on the identical bootstrap sample and the difference is properly paired. The rank transform
is applied once on the full sample, matching how K3's `pooled_within → spearman_fast` pipeline
treats within-task ranks.

### 3.1 Primary convention — within-task ranks

| SOF variant | n | ρ soft | ρ TreeSim | Δ | 95 % CI | boot p |
|---|---:|---:|---:|---:|:---:|---:|
| SOF, all runs | 63 | 0.338 | 0.379 | −0.040 | [−0.257, +0.166] | 0.719 |
| SOF, ran only | 47 | 0.411 | 0.421 | −0.010 | [−0.293, +0.258] | 0.944 |
| SOF_wc, all runs | 63 | 0.170 | 0.206 | −0.036 | [−0.263, +0.181] | 0.744 |
| SOF_wc, ran only | 47 | 0.148 | 0.175 | −0.027 | [−0.322, +0.260] | 0.852 |

### 3.2 Secondary convention — raw values

| SOF variant | n | ρ soft | ρ TreeSim | Δ | 95 % CI | boot p |
|---|---:|---:|---:|---:|:---:|---:|
| SOF, all runs | 63 | 0.590 | 0.525 | +0.065 | [−0.032, +0.171] | 0.200 |
| SOF, ran only | 47 | 0.255 | 0.197 | +0.058 | [−0.107, +0.204] | 0.430 |
| SOF_wc, all runs | 63 | 0.579 | 0.517 | +0.062 | [−0.036, +0.170] | 0.224 |
| SOF_wc, ran only | 47 | 0.232 | 0.179 | +0.053 | [−0.113, +0.203] | 0.469 |

**Δ changes sign between the two conventions.** Under ranks the judge is nominally worse; under raw
values nominally better. Neither is significant. **Report the primary and disclose the flip** — the
same discipline K3 imposed on its own aggregator sensitivity.

### 3.3 Aggregator sensitivity — K3's largest analytic knob, reproduced here

Switching mean-over-reductions → worst-reduction **roughly halves both correlations** (soft
0.338 → 0.170; TreeSim 0.379 → 0.206) and moves both out of significance (perm p 0.19 / 0.11). This
is the same direction and roughly the same magnitude as J2/K3 found (0.402 → 0.148 at n = 108).
**The paired difference is stable across the aggregator; the absolute correlations are not.**

### 3.4 Individual judges

| x | ρ with SOF_all (n = 63) | ρ with SOF_ran (n = 47) |
|---|---:|---:|
| plain TreeSim | 0.379 | 0.421 |
| soft-TreeSim, 4-judge ensemble | 0.338 | 0.411 |
| soft-TreeSim, instructed pair (`hy3` + `qwen3235b`) | **0.387** | **0.436** |
| `hy3` alone | 0.396 | 0.440 |
| `qwen3235b` alone | 0.273 | 0.360 |
| `gemini3flash` alone | 0.419 | 0.445 |
| `gpt54mini` alone | **0.420** | **0.506** |

**The 4-judge ensemble is worse than three of its four members.** And `gpt-5.4-mini` — the judge J1
identified as the systematic outlier (18.1 % `material_deviation` against 1.0–4.7 % for the others,
the judge that inverted v1's central contrast) — is the **best single predictor of physics** in both
columns. This does not rescue the metric: a panel whose worst-agreeing member is its best physics
predictor is a panel whose aggregation rule is unjustified. It does suggest that the harshness J1
treated as a reliability defect is partly signal.

### 3.5 Sanity check — J1's U1 replicates on this same 63-row subset

Recomputing J1's utility criterion on exactly the rows used above, with K3's `ran` indicator as the
executable proxy: ρ_soft = +0.577 vs ρ_TreeSim = +0.521 (Δ = +0.056, 95 % CI [−0.069, +0.188]);
AUC 0.882 vs 0.846. **Same direction and same magnitude as J1's ΔAUC = +0.045 at n = 90.** The join
is sound, and the contrast is sharp: the judge's advantage over TreeSim is **specific to predicting
execution, and disappears when the target is physical fidelity.**

---

## 4. POWER — say it before quoting the null

| target | n | min detectable \|ρ\| (80 %, α = .05) |
|---|---:|---:|
| SOF, all runs | 63 | **0.356** |
| SOF, conditional on running | 47 | **0.409** |

| paired difference | n | SE(Δ) | min detectable \|Δρ\| |
|---|---:|---:|---:|
| SOF, all runs | 63 | 0.107 | **0.299** |
| SOF, conditional | 47 | 0.140 | **0.393** |
| SOF_wc, all runs | 63 | 0.112 | 0.314 |
| SOF_wc, conditional | 47 | 0.149 | 0.416 |

n needed: ρ = 0.40 → 50; ρ = 0.30 → 90; ρ = 0.25 → 131; ρ = 0.20 → 206.

**This is emphatically not evidence of absence for a moderate effect.** A Δρ of +0.2 in the judge's
favour would have been undetectable at this n. What the data *can* support: an advantage of the size
that would justify a paid LLM panel over a free deterministic metric (Δρ ≳ 0.30) is ruled out.

**Why n cannot be raised without new spend.** The 63 is the hard intersection of J1's judged cells
(F0/F6/SE only — the other three held-out cells were never judged) and K3's usable held-out tasks.
Extending it means either judging F4/F8/F11 (90 more decks ≈ 5400 judge calls ≈ $6.6 at J1's
measured order-A rate) or judging the 363 val decks (several times that, and val carries K1/K2's
disclosed caveats on both axes). **Both are API spend and are out of scope for this thread.**

---

## 5. PER-SECTION — the interesting result, with its controls

### 5.1 Groups (declared in the brief, not fitted here)

- **physics** = `Solvers`, `Constitutive`, `FieldSpecifications`, `Functions`
- **bookkeeping** = `Outputs`, `Events`

Deck-level group score = mean judge credit over that deck's reference sections in the group; the
same construction with TreeSim's own section score is the control.

### 5.2 Main table

| x | ρ, SOF_all (n = 63) | p | ρ, SOF_ran (n = 47) | p |
|---|---:|---:|---:|---:|
| **judge_physics** | **+0.418** | 0.0006 | **+0.434** | 0.0023 |
| **judge_bookkeeping** | **−0.224** | 0.081 | −0.136 | 0.363 |
| ts_physics | +0.368 | 0.0028 | +0.424 | 0.0037 |
| ts_bookkeeping | +0.103 | 0.421 | +0.399 | 0.0073 |
| soft-TreeSim (deck) | +0.338 | 0.0064 | +0.411 | 0.0046 |
| TreeSim (deck) | +0.379 | 0.0024 | +0.421 | 0.0041 |

**Yes — the judge's physics sections predict SOF and its bookkeeping sections do not.** The paired
separation D_judge = ρ(physics) − ρ(bookkeeping):

| y | D_judge | 95 % CI | p |
|---|---:|:---:|---:|
| SOF_all | **+0.642** | [+0.313, +0.941] | <0.001 |
| SOF_ran | +0.570 | [+0.166, +0.945] | 0.007 |
| SOF_wc_all | +0.402 | [+0.048, +0.722] | 0.028 |
| SOF_wc_ran | +0.231 | [−0.229, +0.668] | 0.332 |

### 5.3 The control that matters — is the separation *the judge's*?

`judge_physics − ts_physics` = **+0.050, 95 % CI [−0.137, +0.238]**, p = 0.60 (SOF_all); +0.010
[−0.234, +0.257] conditional. **TreeSim's own physics-section score predicts SOF just as well as the
judge's.** So "physics sections predict physics" is largely a statement about *which sections
matter*, not about the judge.

What *is* the judge's is the **contrast**. Difference-in-differences
`(judge_phys − judge_book) − (ts_phys − ts_book)`:

| y | D_judge | D_TreeSim | **DiD** | 95 % CI | p |
|---|---:|---:|---:|:---:|---:|
| SOF_all | +0.642 | +0.264 | **+0.377** | [+0.046, +0.703] | 0.027 |
| SOF_ran | +0.570 | +0.025 | **+0.545** | [+0.128, +0.945] | 0.011 |
| SOF_wc_all | +0.402 | +0.245 | +0.157 | [−0.146, +0.461] | 0.305 |
| SOF_wc_ran | +0.231 | +0.037 | +0.195 | [−0.226, +0.629] | 0.381 |

**Under the primary aggregator the judge localises physics information into the physics sections
significantly more sharply than TreeSim does. Under the worst-reduction aggregator it does not.**
Both must be reported.

### 5.4 Incremental value over the free metric — partial correlations (control = plain TreeSim)

| x | ρ marginal | **ρ \| TreeSim** | 95 % CI | perm p |
|---|---:|---:|:---:|---:|
| soft-TreeSim (deck aggregate), SOF_all | 0.338 | **+0.172** | [−0.034, +0.363] | 0.176 |
| soft-TreeSim (deck aggregate), SOF_ran | 0.411 | +0.258 | [−0.020, +0.517] | 0.080 |
| soft_pair (instructed pair), SOF_all | 0.387 | +0.257 | [+0.047, +0.460] | 0.046 |
| **judge_physics, SOF_all** | 0.418 | **+0.283** | [+0.093, +0.461] | 0.025 |
| **judge_physics, SOF_ran** | 0.434 | **+0.308** | [+0.037, +0.534] | 0.035 |
| judge_bookkeeping, SOF_all | −0.224 | **−0.307** | [−0.514, −0.074] | 0.015 |

**This is the diagnosis.** The judge's *per-section* physics scores carry information about physical
fidelity that plain TreeSim does not have (partial ρ ≈ +0.28 to +0.31). Its bookkeeping scores carry
information of the **opposite sign** (−0.31). J1's aggregation is TreeSim's own uniform 1/N over all
top-level sections, so the two are averaged together and **cancel** — leaving a deck aggregate whose
partial correlation is +0.172 with a CI containing 0.

**The deck-level tie is an aggregation artifact, not an absence of signal.**

### 5.5 Every individual section

| section | n decks | ρ(judge credit, SOF_all) | p | ρ(TreeSim section, SOF_all) | p |
|---|---:|---:|---:|---:|---:|
| **Solvers** | 54 | **+0.456** | 0.0007 | **+0.448** | 0.0006 |
| Constitutive | 63 | +0.248 | 0.052 | +0.211 | 0.098 |
| FieldSpecifications | 54 | +0.234 | 0.093 | +0.258 | 0.059 |
| Tasks | 46 | +0.136 | 0.367 | +0.141 | 0.349 |
| Mesh | 63 | +0.089 | 0.488 | +0.197 | 0.119 |
| Outputs | 54 | +0.089 | 0.530 | +0.089 | 0.524 |
| NumericalMethods | 54 | +0.060 | 0.667 | +0.089 | 0.527 |
| Functions | 19 | +0.030 | 0.910 | +0.026 | 0.917 |
| ElementRegions | 63 | −0.034 | 0.794 | +0.213 | 0.095 |
| Geometry | 18 | −0.038 | 0.867 | −0.038 | 0.867 |
| **Events** | 63 | **−0.225** | 0.081 | +0.024 | 0.853 |

`Solvers` is the single strongest predictor of physical fidelity in the whole study — for **both**
the judge and TreeSim — and it beats every deck-level aggregate. `Events` is where the judge and
TreeSim diverge most sharply in sign. `Functions` (one of the brief's physics sections) is present
in only 19 of 63 decks and carries nothing; the physics-group result is driven by `Solvers` and
`Constitutive`.

**Caution on the conditional column** (`L1_report.txt` §3): among the 47 runs that ran, TreeSim's
*bookkeeping* sections also predict SOF (`Mesh` +0.402, `Outputs` +0.396, `Events` +0.325,
`Tasks` +0.375). That pattern is consistent with a deck-level "general quality" factor rather than a
clean physics/bookkeeping dissociation, and it is why D_TreeSim collapses to +0.025 there while
D_judge stays at +0.570. Do not oversell the dissociation.

---

## 6. ROBUSTNESS, and the multiplicity disclosure

| check | effect on the headline Δ (SOF_all, ranks) |
|---|---|
| (a) drop `F0_s3_ExampleProppantTest` (§2.4, TreeSim = soft = 0.0, SOF = 1.000) | n = 62, Δ = −0.038 [−0.254, +0.170]. Both ρ rise (0.381 / 0.419). **No change in conclusion.** |
| (b) drop `ExampleIsothermalHystInjection` (SOF constant at 0) | n = 54, Δ = −0.048 [−0.274, +0.177]. **No change.** |
| (c) task-clustered bootstrap (resample the 7 tasks, not the 63 rows) | Δ = −0.040, cluster CI [−0.283, +0.106]. Rows within a task are not independent, so this is the right dependence structure; it is wider on the lower side and narrower on the upper side than the row-level CI, and still contains 0. k = 7 makes it a coarse check. |
| (d) per-task ρ (n = 9 each, descriptive only) | soft better on 2 tasks (Cased +0.12, PureThermal +0.11), worse on 2 (ThermoPoro −0.43, Proppant −0.09), tied on 1, undefined on 2. **No consistent direction.** |

The §5 findings under the same sensitivities (`L1_report_supp.txt` §S4): dropping the §2.4 row
*strengthens* them — `judge_physics | TreeSim` goes +0.283 → +0.332 [+0.155, +0.491] and the DiD
goes +0.377 → +0.432 [+0.092, +0.763], p = 0.013.

**Multiplicity, stated plainly.** §5.4 runs 16 partial correlations; Bonferroni puts the threshold at
α = 0.0031 and **none of them clears it** (best = 0.0106). §5.3 runs 4 DiD tests; the threshold is
0.0125 and only SOF_ran (p = 0.011) clears it. **Neither the partial-correlation analysis nor the
DiD was pre-registered** — the physics/bookkeeping grouping came from the brief, but both analyses
were chosen after seeing the headline null. **§5 is a hypothesis worth a confirmatory test, not a
result.** §3 (the headline) is the pre-specified question and it is a tie.

---

## 7. WHAT A HUMAN MUST DECIDE

1. **Does the judge go in the paper at all?** L1's answer to the question it was asked is *no
   improvement over a free deterministic metric at the deck level*. Combined with J1's
   `VALID = false` (four of four pre-registered validity criteria failed), the defensible position
   is **do not present soft-TreeSim as a validated secondary metric**, which is also J1 §11.8.1's
   own recommendation. L1 supplies the physical-validity leg J1 could not.
2. **Is §5 worth a confirmatory run?** The section-weighting result (physics sections carry
   incremental physics information, bookkeeping sections carry the opposite, uniform 1/N cancels
   them) is the most interesting thing in this thread and it is **cheap to test deterministically**:
   re-weight TreeSim's sections toward `Solvers` / `Constitutive` and see whether SOF prediction
   improves, **with no LLM at all**. That is a free experiment on data already on disk. It would
   also let the paper say something constructive rather than only reporting a null. **Recommended.**
3. **Is it worth ≈ $7 of judge calls to raise n from 63 to 126?** Judging F4/F8/F11 held-out decks
   would double the sample and take the paired MDE from |Δρ| = 0.30 to roughly 0.21. Given that the
   deck-level point estimate is *negative*, my read is that this buys a sharper null, not a
   different answer. **Not recommended** unless §5 is being pursued, where the extra n would matter.
4. **Does §2.4 go in the metric-limitations text?** A generated deck that GEOS runs to a perfect
   reproduction of the reference is scored **0.0** by TreeSim because of a `--` inside an XML
   comment. That is a concrete, one-line demonstration that an input-side structural metric is not a
   proxy for physical correctness, and it pairs naturally with J1 §11.6 blind spot 1 (10 decks,
   0/10 load, TreeSim mean 0.840 — *above* the held-out average). **Recommended.**
5. **`gpt-5.4-mini` being the best single physics predictor (§3.4) while being J1's reliability
   outlier** is either a genuine signal that harshness is warranted, or a coincidence at n = 63.
   Someone should decide whether to say anything about it. Default: say nothing, it is one number.

---

## 8. ARTIFACTS

| file | what |
|---|---|
| `artifacts/L1_join.py` | the join, with integrity gates G1–G3 asserted in code |
| `artifacts/L1_joined.csv` | **the dataset** — 63 rows × 52 cols: both TreeSim axes, all judge scores (ensemble, pair, per-judge), per-section and per-group judge/TreeSim scores, all four SOF variants, status |
| `artifacts/L1_sections_long.csv` | per-deck-per-section long form (joined decks only): judge credit, TreeSim section score, whether judged |
| `artifacts/L1_join_report.txt` | join integrity console output |
| `artifacts/L1_analyse.py` | headline paired comparison, power, per-section, robustness |
| `artifacts/L1_report.txt` | full console report for the above |
| `artifacts/L1_results.csv` | every statistic in machine-readable form |
| `artifacts/L1_supp.py` | partial correlations (S1), difference-in-differences (S2), ceiling (S3), sensitivity (S4), multiplicity (S5) |
| `artifacts/L1_report_supp.txt`, `artifacts/L1_results_supp.csv` | supplement output |
| `artifacts/L1_recheck.py` | gate G4 — the headline re-derived in pure Python from the convention in words, importing nothing from any other thread |

**Reproducing** (no API, no GEOS, ~15 min of CPU):

```bash
cd neurips_review/sprint/artifacts
python3 L1_join.py       # asserts G1-G3; refuses to write if the reconstruction fails
python3 L1_analyse.py    # ~12 min (20 000-draw permutation p, 10 000-draw bootstraps)
python3 L1_supp.py       # ~3 min
python3 L1_recheck.py    # ~20 s — independent re-derivation of the headline (gate G4)
```

Statistics are imported from `J2_validate` (`spearman_fast`, `n_for_spearman`) and the judge
aggregation from `J1_sections` (`aggregate`) — **nothing is forked, so nothing can drift.**
