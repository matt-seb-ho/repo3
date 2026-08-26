# Thread L2 — does weighting TreeSim toward physics-bearing sections predict simulation fidelity better?

**Submission:** NeurIPS 2026 #31642 (SIGA), author response.
**Owner:** L2. **Started:** 2026-07-27, after L1.
**Artifacts:** `neurips_review/sprint/artifacts/L2_*`
**API spend: $0. New GEOS runs: 0. `src/eval/judge_geos.py` untouched (imported, never modified).**

---

## STATE OF PLAY

### *** VERDICT: NULL. Physics weighting does NOT beat uniform TreeSim. ***
### *** And a physics-selected subset of sections predicts physical fidelity no better than a RANDOM subset of the same size — it sits at the 51st percentile of its own null. ***

L1 recommended this experiment (its §7.2, "recommended") on the diagnosis that TreeSim's
uniform 1/N section weighting averages physics signal against bookkeeping anti-signal and
they cancel. **The diagnosis does not transfer from the judge to TreeSim, and the
constructive result L1 hoped for is not there.**

**Primary cell — held-out (K3's primary split), n = 126, SOF mean-over-reductions, all runs,
within-task percentile ranks:**

| variant | n | ρ vs SOF | **Δ vs uniform** | **95 % CI** | boot p | **random-subset null: pctile** | **one-sided p** |
|---|---:|---:|---:|:---:|---:|---:|---:|
| **`uniform`** (= published TreeSim) | 126 | **0.362** | — control — | | | | |
| `physics_only` (Solvers/Constitutive/FieldSpec/Functions) | 126 | 0.311 | **−0.051** | [−0.153, +0.044] | 0.317 | **51.5 %** | 0.485 |
| `physics_weighted` (2 / 1 / 0.5) | 126 | 0.395 | **+0.033** | [−0.003, +0.072] | 0.075 | 93.6 % | 0.065 |
| `solvers_only` | 108 | 0.309 | **−0.102** | [−0.267, +0.063] | 0.228 | **45.4 %** | 0.546 |

**Neither pre-registered criterion is met** (§0.8: paired CI excluding 0 **and** null
p < 0.05). Not in the primary cell, and not in any of the 12 headline cells.

**The three findings, in order of how loudly they should be said:**

1. **Dropping to the physics sections is no better than dropping to a random set of the
   same size, and both are worse than keeping everything.** `physics_only` Δ = −0.051; the
   null distribution of random 4-tag subsets has mean Δ = −0.060, sd 0.096, and the real
   physics subset sits at the **51.5th percentile** of it (n = 489: 52.0th percentile).
   `solvers_only` is at the **45.4th percentile** of a random-single-tag null. **The
   section grouping carries no information beyond "you discarded sections", and discarding
   sections costs you.** This is the brief's third anticipated outcome and it is the
   cleanest result in the thread.

2. **Graded re-weighting gives a consistent but tiny positive that never clears its bar.**
   Δ is positive in **12 / 12** headline cells (3 datasets × 4 SOF variants), range +0.001
   to +0.043, but the primary CI is [−0.003, +0.072], the permutation null p is 0.065, and
   the two datasets **disagree about which knob produces it** (§2: on held-out it is the
   bookkeeping down-weight, Δ = +0.022; on the full 489 it is the physics up-weight,
   Δ = +0.017, while the bookkeeping down-weight gives +0.005). A real mechanism would not
   swap knobs between splits. The 12 cells are nested and share the y axis, so they are not
   12 independent confirmations.

3. **The mechanism L1 proposed is not present in TreeSim.** L1's cancellation story needs a
   *negative* bookkeeping term. At n = 489 TreeSim's bookkeeping sections are weakly
   **positive**: marginal ρ = +0.177, partial ρ over uniform TreeSim = **+0.036
   [−0.058, +0.129]**, and `Events` alone is ρ = **+0.211** (p < 1e−4). L1's −0.224 /
   −0.307 was the **judge's** bookkeeping credit, not TreeSim's — L1 §5.3 already showed
   `ts_bookkeeping` at +0.103 and flagged a "general quality factor" in its conditional
   column. **There is no anti-signal in TreeSim's own sections for a re-weighting to
   un-cancel.** This is why the constructive experiment fails: the diagnosis was about the
   judge and was mis-transferred to the deterministic metric.

**The one thing that DOES replicate, and it is not a metric change.** L1's strongest
per-section claim survives an 8× increase in n: `Solvers` is the top single structural
predictor of physical fidelity at n = 489, **ρ = +0.343, 95 % CI [+0.245, +0.436]**, and it
retains **partial ρ = +0.223, 95 % CI [+0.123, +0.317]** controlling for the deck aggregate.
**That CI excludes zero — it is the only interval in L1 or L2 that does at large n.** But it
cannot be turned into a better metric: 5 of 18 tasks are constitutive-driver decks with **no
`<Solvers>` section at all**, so `solvers_only` is undefined there, and where it is defined
it loses to `uniform` (Δ = −0.102 held-out).

**Power. This is a TIGHT null, unlike L1's.** The variants are near-collinear with uniform
(Spearman 0.985 for `physics_weighted`), so the paired SE is small:

| set | n | MDE, `physics_weighted` | MDE, `physics_only` | MDE, `solvers_only` |
|---|---:|---:|---:|---:|
| held-out (**primary**) | 126 | **0.054** | 0.141 | 0.233 |
| full | 489 | **0.034** | 0.083 | 0.145 |
| L1's subset | 63 | 0.099 | 0.218 | 0.357 |

L1 could not detect |Δρ| below 0.30. L2 can detect **0.034** on the full set. **An
improvement worth shipping would have been visible many times over.** We can rule out any
physics-weighting gain larger than ≈ 0.05 ρ points on the primary set.

**Aggregator sensitivity, the one place to be careful.** Under **worst-reduction** on
held-out, `physics_weighted` reaches Δ = **+0.043 [+0.005, +0.084], p = 0.023** (task-
clustered CI [+0.010, +0.087]) — nominally significant, and it does *not* shrink the way
K3/L1 warned aggregator switches do. It does not survive on the full 489 (+0.019
[−0.006, +0.043], p = 0.137), and it is one nominal cell out of 12 with no multiplicity
correction. Reported, not leaned on. In the same cell `solvers_only` is significantly
**worse** than uniform (conditional: −0.259 [−0.459, −0.055], p = 0.011).

**Integrity: 4 gates, all asserted in code.** G0 reproduces L1's baseline exactly; G1
rebuilds TreeSim from the section decomposition on all 488 scored runs with worst
|diff| = **0.00e+00**; G2 matches K3's own published pooled correlations to 5 dp on held-out;
S1 reproduces L1's per-section ρ to **0.00e+00** on all 11 sections. Details in §1.

**What a human must decide: §7.**

---

## 0. PRE-REGISTRATION (written before any variant was computed)

Written after gate G0 passed and before `L2_sections.py` or `L2_analyse.py` had produced a
single variant correlation. Preserved verbatim below.

### 0.1 Gate G0 — reproduce L1's baseline

Required before anything else: plain TreeSim vs SOF on `L1_joined.csv`, primary convention
(pooled Spearman on within-task percentile ranks).

| target | L1 reports | L2 recomputes | verdict |
|---|---:|---:|---|
| SOF mean-over-reductions, all runs, n = 63 | 0.379 | **0.3786** | PASS |
| SOF mean-over-reductions, ran only, n = 47 | 0.421 | **0.4213** | PASS |
| SOF worst-reduction, all runs, n = 63 | 0.206 | **0.2059** | PASS |
| SOF worst-reduction, ran only, n = 47 | 0.175 | **0.1752** | PASS |

**G0 PASSED.** Proceeding.

### 0.2 The hypothesis under test

L1 §5.4: the judge's *physics-section* scores carry incremental information about physical
fidelity (partial ρ = +0.283 controlling for plain TreeSim) while its *bookkeeping* scores
carry information of the opposite sign (−0.307). TreeSim's own aggregation is a uniform
1/N over all reference top-level sections, so the two are averaged and cancel.

**H1 (confirmatory test of an exploratory finding):** a structural metric that up-weights
the physics-bearing sections and down-weights the bookkeeping sections predicts SOF better
than the uniform metric — *with no LLM in the loop*.

**H0-alt (the objection that must be ruled out):** any metric built on a *subset* of
sections looks better simply because it drops noisy sections. Tested against a
random-subset null of the same size.

### 0.3 Section groups — inherited from L1's brief, not fitted here

- **physics** = `Solvers`, `Constitutive`, `FieldSpecifications`, `Functions`
- **bookkeeping** = `Outputs`, `Events`
- **plumbing** (everything else) = `ElementRegions`, `Geometry`, `Mesh`, `NumericalMethods`,
  `Tasks`

### 0.4 The metric family

TreeSim's root frame is, exactly (J1's identity, re-verified here as G1):

```
TreeSim(deck) = clip01( sum_i s_i / n_ref  -  beta * n_extra / (n_ref + n_extra) )
```

where `i` runs over the deck's **reference top-level section units** (duplicated tags are
separate units), `s_i` is that unit's TreeSim section score, and `beta = 0.1`.

The weighted family changes **only the section weighting**, holding the hallucination
penalty fixed so nothing else can move:

```
TreeSim_w(deck) = clip01( sum_i w(tag_i)*s_i / sum_i w(tag_i)  -  beta * n_extra / (n_ref + n_extra) )
```

| variant | weights |
|---|---|
| `uniform` | w = 1 everywhere — **the control; identical to published TreeSim** |
| `physics_only` | w = 1 on the 4 physics tags, 0 elsewhere |
| `physics_weighted` | **w = 2 physics, 1 plumbing, 0.5 bookkeeping** |
| `solvers_only` | w = 1 on `Solvers`, 0 elsewhere |

**Why those weights.** Chosen a priori, not fitted: a factor-2 up-weight and a factor-2
down-weight around the uniform 1 is the smallest non-trivial monotone ordering consistent
with L1's sign pattern, and it keeps every section in the metric — so it is not a "drop
sections" variant. A full sensitivity sweep over (physics weight × bookkeeping weight) is
reported (§4), so the choice can be audited.

**Failures-as-zero** is inherited unchanged: a deck whose XML cannot be parsed scores 0.0 on
*every* variant, exactly as TreeSim does. Applied identically, so it cannot favour a variant.

### 0.5 Data sets, and which is primary — declared before seeing any result

| set | n | what |
|---|---:|---|
| **`heldout`** | **126** | K3's held-out split — **PRIMARY**. K3 §6 declares it clean on both axes; it is K3's own primary. |
| `full` | 489 | held-out + K3's staged/K2-rescored val. Powered secondary; val carries K3 §6's disclosed caveats. |
| `L1_63` | 63 | L1's exact subset. Reported for comparability only. |

Both SOF aggregators and both populations (all runs / conditional on output) always.

### 0.6 Statistics

Imported, not re-implemented: `spearman_fast`, `n_for_spearman` from `J2_validate`
(K3's/J2's); `within_task_rank`, `paired_delta`, `min_detectable` from `L1_analyse` — so
nothing can drift from L1. Primary convention is K3's pooled Spearman on within-task
percentile ranks. Paired differences resample (variant, uniform, SOF) triples together over
decks, 10 000 draws, seed 20260727.

### 0.7 The random-subset null (H0-alt)

For each subset-style variant, draw 2 000 random subsets of **distinct reference tags** of
the same cardinality as the variant (4 for `physics_only`, 1 for `solvers_only`), rebuild
the metric, and report where the real variant's paired Δ sits in that distribution. For
`physics_weighted`, randomly permute which tags receive the up- and down-weights, preserving
group sizes (4 up / 2 down). The statistic is the **paired Δ vs uniform on the rows where
that draw's metric is defined**, so n-differences cancel inside the pair.

**If the physics variant does not clear its random-subset null, H1 is dead and this thread
reports a null.**

### 0.8 Pre-declared decision rule

- H1 supported only if, on the **primary set (`heldout`, n = 126, SOF mean-over-reductions,
  all runs)**, the paired Δρ against `uniform` is positive with a 95 % CI excluding 0
  **and** the random-subset one-sided p < 0.05.
- Aggregator sensitivity (`worst-reduction`) is reported alongside; it does not veto, but a
  sign flip there must be disclosed.

---

## 1. INTEGRITY — four gates, asserted in code, not assumed

Seven harness bugs have been found in this sprint, every one biasing toward our own
conclusion. So nothing here is trusted without a check against another thread's artifact.

| gate | check | result |
|---|---|---|
| **G0** | L1's four headline TreeSim ρ, recomputed from `L1_joined.csv` | **all four match to 3 dp** (§0.1) |
| **G1** | TreeSim rebuilt from L2's section decomposition (`J1_sections.deck_sections`, imported verbatim) vs K3's TreeSim of record, all 488 scored SOF runs | worst \|diff\| = **0.00e+00** |
| **G2** | the `uniform` variant vs **K3's own published pooled correlations** (`K3_correlations.csv`) | held-out **exact to 5 dp in all 4 cells** (0.36219 / 0.44995 / 0.12093 / 0.14316); full-489 differs by ≤ **0.0006** |
| **S1** | L2's per-section scores vs L1's `ts_sec_*` columns, all 11 sections, L1's 63 rows | worst \|diff\| = **0.00e+00** |

**G2's 0.0006 on the full set is explained, not waved past.** `K3_per_run.csv` stores
`treesim` rounded to 4 dp; L2 reconstructs at full precision. Rounding creates rank ties in
the val rows that full precision breaks. Recomputing L2's `uniform` correlation *from K3's
rounded column* reproduces K3's number to 5 dp in all four full-set cells
(0.30971 / 0.29980 / 0.26118 / 0.24708). Held-out has no such ties and matches exactly. The
discrepancy is 0.0006 ρ points and touches no conclusion.

**Why the section decomposition is recomputed rather than read from
`treesim_section_scores`.** The scorer's `treesim_section_scores` dict is keyed by tag and
**silently collapses duplicated top-level sections** — the median deck has **12 reference
top-level units over 9 distinct tags** (max 30 units), so the dict cannot reproduce the deck
score. L2 uses `J1_sections.deck_sections`, imported verbatim, which keeps duplicates as
separate units. G1 is the proof this is the right object: it reproduces published TreeSim
exactly on all 488 runs. **`src/eval/judge_geos.py` is imported and never modified.**

### 1.1 Coverage, declared before any correlation was read

489 runs, 18 tasks, 11 cells, 11 distinct reference top-level tags. **5 of the 18 tasks are
constitutive-model driver decks with no `<Solvers>` section at all**
(`AdvancedExampleDruckerPrager`, `AdvancedExampleExtendedDruckerPrager`,
`AdvancedExampleModifiedCamClay`, `AdvancedExampleViscoDruckerPrager`,
`AdvancedExampleViscoExtendedDruckerPrager`). `solvers_only` is **undefined** on those 150
runs. Every `solvers_only` comparison is therefore run on the subset where it is defined,
with `uniform` recomputed on the **same rows**, so the pairing is honest. **This is not a
nuisance — it is a first-order objection to any Solvers-weighted metric** (§5).

One deck in 489 is a rung-1 XML parse failure and scores 0.0 on every variant by the
published failures-as-zero convention.

---

## 2. HEADLINE — every variant against SOF, paired against uniform TreeSim

Script `artifacts/L2_analyse.py` → `L2_report.txt`, `L2_results.csv`.

### 2.1 Primary set — held-out, n = 126

| y | variant | n | ρ | perm p | Δ vs uniform | 95 % CI | boot p |
|---|---|---:|---:|---:|---:|:---:|---:|
| **SOF, all runs** | uniform | 126 | **0.362** | 0.0001 | — | | |
| | physics_only | 126 | 0.311 | 0.0005 | **−0.051** | [−0.153, +0.044] | 0.317 |
| | physics_weighted | 126 | 0.395 | <0.0001 | **+0.033** | [−0.003, +0.072] | 0.075 |
| | solvers_only | 108 | 0.309 | 0.0011 | **−0.102** | [−0.267, +0.063] | 0.228 |
| SOF, ran only | uniform | 91 | 0.450 | <0.0001 | — | | |
| | physics_only | 91 | 0.383 | 0.0001 | −0.067 | [−0.202, +0.058] | 0.315 |
| | physics_weighted | 91 | 0.451 | <0.0001 | +0.001 | [−0.043, +0.046] | 0.989 |
| | solvers_only | 74 | 0.397 | 0.0005 | −0.154 | [−0.334, +0.025] | 0.092 |
| **SOF_wc, all runs** | uniform | 126 | 0.121 | 0.177 | — | | |
| | physics_only | 126 | 0.097 | 0.277 | −0.024 | [−0.131, +0.081] | 0.673 |
| | physics_weighted | 126 | 0.164 | 0.066 | **+0.043** | **[+0.005, +0.084]** | **0.023** |
| | solvers_only | 108 | −0.054 | 0.576 | −0.173 | [−0.347, +0.001] | 0.051 |
| SOF_wc, ran only | uniform | 91 | 0.143 | 0.177 | — | | |
| | physics_only | 91 | 0.113 | 0.290 | −0.030 | [−0.175, +0.102] | 0.702 |
| | physics_weighted | 91 | 0.162 | 0.127 | +0.019 | [−0.030, +0.070] | 0.462 |
| | solvers_only | 74 | −0.090 | 0.440 | **−0.259** | **[−0.459, −0.055]** | **0.011** |

### 2.2 Powered secondary — full 489

| y | variant | n | ρ | Δ vs uniform | 95 % CI | boot p |
|---|---|---:|---:|---:|:---:|---:|
| **SOF, all runs** | uniform | 489 | **0.310** | — | | |
| | physics_only | 489 | 0.267 | −0.043 | [−0.101, +0.014] | 0.143 |
| | physics_weighted | 489 | 0.332 | +0.021 | [−0.003, +0.045] | 0.083 |
| | solvers_only | 339 | 0.343 | −0.032 | [−0.135, +0.068] | 0.531 |
| SOF, ran only | uniform | 413 | 0.300 | — | | |
| | physics_only | 413 | 0.276 | −0.025 | [−0.091, +0.043] | 0.457 |
| | physics_weighted | 413 | 0.327 | **+0.027** | **[+0.001, +0.054]** | **0.043** |
| | solvers_only | 273 | 0.360 | −0.036 | [−0.155, +0.086] | 0.574 |
| SOF_wc, all runs | uniform | 489 | 0.262 | — | | |
| | physics_only | 489 | 0.217 | −0.044 | [−0.103, +0.014] | 0.136 |
| | physics_weighted | 489 | 0.280 | +0.019 | [−0.006, +0.043] | 0.137 |
| | solvers_only | 339 | 0.248 | −0.058 | [−0.164, +0.046] | 0.277 |
| SOF_wc, ran only | uniform | 413 | 0.248 | — | | |
| | physics_only | 413 | 0.210 | −0.038 | [−0.105, +0.031] | 0.259 |
| | physics_weighted | 413 | 0.268 | +0.021 | [−0.005, +0.048] | 0.122 |
| | solvers_only | 273 | 0.246 | −0.076 | [−0.199, +0.047] | 0.233 |

### 2.3 L1-comparable — n = 63

| y | uniform | physics_only | physics_weighted | solvers_only |
|---|---:|---:|---:|---:|
| SOF, all runs (n=63) | 0.379 | 0.369 (Δ −0.010) | 0.400 (Δ **+0.021** [−0.049, +0.090]) | 0.383 (Δ −0.075) |
| SOF, ran (n=47) | 0.421 | 0.425 (Δ +0.004) | 0.430 (Δ +0.009) | 0.483 (Δ −0.054) |
| SOF_wc, all (n=63) | 0.206 | 0.223 (Δ +0.017) | 0.239 (Δ +0.034) | 0.088 (Δ −0.146) |
| SOF_wc, ran (n=47) | 0.175 | 0.199 (Δ +0.023) | 0.205 (Δ +0.030) | 0.057 (Δ −0.151) |

**Every CI in the L1_63 block contains 0 and is 2–3× wider than the primary set's.** L1's n
simply cannot answer this question; that is why the primary is n = 126 and the powered
secondary is n = 489.

### 2.4 Which half of the re-weighting does the work? (`L2_report.txt` §2)

| dataset | drop bookkeeping entirely | up-weight physics only (×2) | down-weight bookkeeping only (×0.5) |
|---|---:|---:|---:|
| held-out (n=126) | Δ = **+0.042** [−0.007, +0.094], p = 0.099 | Δ = +0.014 [−0.009, +0.040], p = 0.274 | Δ = **+0.022** [−0.002, +0.050], p = 0.082 |
| full (n=489) | Δ = **−0.005** [−0.050, +0.040], p = 0.827 | Δ = **+0.017** [+0.001, +0.033], p = 0.037 | Δ = +0.005 [−0.012, +0.022], p = 0.574 |

**The two datasets attribute the effect to different knobs, and they disagree in sign on
one of them.** On held-out the whole effect is the bookkeeping down-weight and dropping
bookkeeping outright is best; on the full 489 dropping bookkeeping is *negative* and the
effect is the physics up-weight. A real mechanism would not behave this way. This is the
single strongest internal reason not to believe the +0.02 to +0.04.

---

## 3. THE OBJECTION, TESTED — physics, or just fewer sections?

2 000 draws per cell, seed 20260727. Statistic = the paired Δ vs uniform on the rows where
that draw's metric is defined.

| dataset | y | variant | real Δ | null mean Δ | null sd | **pctile** | one-sided p |
|---|---|---|---:|---:|---:|---:|---:|
| held-out | SOF all | **physics_only** | −0.051 | −0.060 | 0.096 | **51.5 %** | 0.485 |
| held-out | SOF all | **solvers_only** | −0.102 | −0.142 | 0.130 | **45.4 %** | 0.546 |
| held-out | SOF all | physics_weighted | +0.033 | +0.005 | 0.017 | 93.6 % | 0.065 |
| held-out | SOF_wc all | physics_only | −0.024 | −0.033 | 0.098 | 51.9 % | 0.481 |
| held-out | SOF_wc all | solvers_only | −0.173 | −0.149 | 0.120 | 45.4 % | 0.546 |
| held-out | SOF_wc all | physics_weighted | +0.043 | +0.009 | 0.020 | 93.7 % | 0.064 |
| full | SOF all | **physics_only** | −0.043 | −0.048 | 0.046 | **52.0 %** | 0.480 |
| full | SOF all | solvers_only | −0.032 | −0.143 | 0.075 | 91.8 % | 0.082 |
| full | SOF all | physics_weighted | +0.021 | +0.005 | 0.012 | 89.9 % | 0.101 |
| full | SOF_wc all | physics_only | −0.044 | −0.051 | 0.049 | 52.8 % | 0.472 |
| full | SOF_wc all | solvers_only | −0.058 | −0.161 | 0.081 | 83.5 % | 0.166 |
| full | SOF_wc all | physics_weighted | +0.019 | +0.004 | 0.013 | 86.7 % | 0.133 |

**Read this table plainly.**

- **`physics_only` is a coin flip against a random 4-tag subset — 51.5 % and 52.0 %.** The
  brief asked for this to be said plainly if it happened: *physics weighting by subsetting
  is no better than a random subset of the same size, and the hypothesis is dead in that
  form.* Note also that the **null mean is negative** (−0.048 to −0.060): the honest reading
  is not "subsets are neutral" but "dropping any 7 of 11 section types costs you about 0.05
  ρ points, and dropping the physics ones costs exactly the average amount."
- **`solvers_only` is *below* the median of its null on held-out (45.4 %)** — worse than
  picking one section at random. It is above the null on the full set (91.8 %) only because
  the average random single tag is very bad there (null mean −0.143), not because it is
  good in absolute terms (Δ = −0.032, still negative).
- **`physics_weighted` clears the 86th–94th percentile everywhere but never p < 0.05.** Its
  null is narrow (sd 0.012–0.020) precisely because graded re-weighting barely moves the
  metric. Being at the 93rd percentile of a distribution whose entire spread is ±0.04 ρ
  points is not a result worth shipping.

---

## 4. SENSITIVITY TO THE WEIGHTS (`L2_report.txt` §4)

Δ vs uniform, ρ points, y = SOF all runs. Plumbing fixed at 1. Pre-registered choice
(physics 2, bookkeeping 0.5) is marked **★**.

**held-out, n = 126**

| w_phys \ w_book | 1.00 | 0.75 | 0.50 | 0.25 | 0.00 |
|---|---:|---:|---:|---:|---:|
| 1.0 | +0.000 | +0.011 | +0.022 | +0.032 | **+0.042** |
| 1.5 | +0.003 | +0.009 | +0.021 | +0.035 | +0.037 |
| 2.0 | +0.014 | +0.020 | **★+0.033** | **+0.043** | +0.039 |
| 3.0 | +0.001 | +0.007 | +0.015 | +0.027 | +0.023 |
| 5.0 | −0.004 | +0.008 | +0.007 | +0.013 | +0.017 |
| 10.0 | −0.008 | −0.007 | −0.003 | −0.003 | −0.001 |

**full, n = 489**

| w_phys \ w_book | 1.00 | 0.75 | 0.50 | 0.25 | 0.00 |
|---|---:|---:|---:|---:|---:|
| 1.0 | +0.000 | +0.003 | +0.005 | +0.014 | −0.005 |
| 1.5 | +0.002 | +0.010 | +0.012 | +0.021 | −0.009 |
| 2.0 | +0.017 | +0.018 | **★+0.021** | +0.021 | −0.010 |
| 3.0 | +0.016 | +0.013 | +0.015 | +0.010 | −0.017 |
| 5.0 | +0.012 | +0.014 | +0.010 | +0.009 | −0.017 |
| 10.0 | +0.008 | +0.006 | +0.007 | +0.003 | −0.023 |

**How sensitive is the result to the weights? Not very — and that is the problem.** The
entire 6 × 5 grid spans **−0.008 to +0.043** (held-out) and **−0.023 to +0.021** (full).
There is no weight setting anywhere in the grid that produces an improvement worth having.
The pre-registered (2, 0.5) is mid-table on both sets, so the choice was neither lucky nor
unlucky.

**The argmax is not stable.** Held-out's best cell is `w_book = 0` (Δ +0.042 at w_phys = 1);
on the full set the **entire `w_book = 0` column is negative**. Anyone tuning these weights
on held-out and reporting the tuned value would be reporting noise. Extreme up-weighting
(w_phys = 10) degrades on held-out (−0.008), consistent with §3: concentrating weight on a
few sections is a cost, not a gain.

**Penalty sensitivity** (`L2_report_supp.txt` §S2): re-running every variant *without*
TreeSim's extra-element penalty moves nothing material — held-out `physics_weighted`
Δ = +0.033 → +0.036, `physics_only` −0.051 → −0.035, full `physics_weighted`
+0.021 → +0.024. The design choice to keep the penalty (so each variant is a complete
drop-in metric) is not what produces the null.

---

## 5. WHY IT FAILS — the mechanism, tested directly

### 5.1 L1's per-section table extended to all 489 runs (`L2_report_supp.txt` §S3)

L1's construction exactly (plain mean of a section's unit scores, no penalty), so the two
threads' numbers are directly comparable — S1 proves they agree to 0.00e+00 on L1's rows.

| section | n decks (full) | ρ vs SOF_all | perm p | 95 % CI | L1's ρ at n = 63 |
|---|---:|---:|---:|:---:|---:|
| **`Solvers`** | 339 | **+0.343** | <0.0001 | **[+0.245, +0.436]** | +0.448 |
| `Constitutive` | 489 | +0.227 | <0.0001 | [+0.138, +0.312] | +0.211 |
| **`Events`** | 456 | **+0.211** | <0.0001 | [+0.114, +0.303] | +0.024 |
| `FieldSpecifications` | 339 | +0.209 | 0.0001 | [+0.100, +0.315] | +0.258 |
| `Mesh` | 456 | +0.205 | 0.0001 | [+0.112, +0.296] | +0.197 |
| `ElementRegions` | 489 | +0.156 | 0.0009 | [+0.068, +0.244] | +0.213 |
| `Functions` | 367 | +0.087 | 0.094 | [−0.024, +0.194] | +0.026 |
| `Tasks` | 421 | +0.077 | 0.119 | [−0.023, +0.179] | +0.141 |
| `NumericalMethods` | 339 | +0.047 | 0.394 | [−0.063, +0.158] | +0.089 |
| `Geometry` | 69 | +0.025 | 0.843 | [−0.216, +0.280] | −0.038 |
| `Outputs` | 339 | +0.023 | 0.677 | [−0.089, +0.135] | +0.089 |
| *[uniform TreeSim]* | 489 | *+0.310* | | | *+0.379* |

**At n = 489 every one of the eleven sections has a non-negative point estimate.** There is
no anti-signal anywhere in TreeSim's section decomposition. `Events` — one of the two
bookkeeping sections the hypothesis needed to be negative — is the **third strongest
predictor** at n = 489 with a CI excluding zero. (On held-out alone, two sections are
nominally negative: `Functions` −0.160 on the 37 decks that have one, and `Outputs` −0.019;
both CIs are wide and contain 0, and both go positive on the full set. Neither is the sign
pattern the hypothesis needs — `Functions` is a *physics* section.)

`Solvers` is confirmed as the top single section (+0.343, and +0.348 on held-out alone),
replicating L1's headline per-section claim at 5× the n. But note it does **not** beat the
deck aggregate on the full set (0.343 vs 0.310 marginally, but the aggregate is defined on
489 rows and `Solvers` on 339) — L1's "beats every deck-level aggregate" was an n = 63
statement.

### 5.2 Partial correlations, controlling for uniform TreeSim (`L2_report_supp.txt` §S4)

| dataset | x | ρ marginal | **ρ \| TreeSim** | 95 % CI |
|---|---|---:|---:|:---:|
| **full (489)** | ts_physics | +0.262 | **+0.043** | [−0.051, +0.134] |
| **full (489)** | ts_bookkeeping | +0.177 | **+0.036** | [−0.058, +0.129] |
| **full (489)** | **ts_solvers** | +0.343 | **+0.223** | **[+0.123, +0.317]** |
| held-out (126) | ts_physics | +0.333 | +0.061 | [−0.122, +0.248] |
| held-out (126) | ts_bookkeeping | +0.083 | −0.125 | [−0.303, +0.063] |
| held-out (126) | ts_solvers | +0.348 | +0.078 | [−0.112, +0.263] |
| L1's 63 | ts_physics | +0.368 | +0.124 | [−0.116, +0.353] |
| L1's 63 | ts_bookkeeping | +0.103 | −0.224 | [−0.454, +0.017] |
| L1's 63 | ts_solvers | +0.448 | +0.263 | [+0.021, +0.475] |

**Two things follow.**

1. **The physics *group* carries essentially nothing over the deck aggregate** (+0.043
   [−0.051, +0.134] at n = 489). Grouping four sections together dilutes `Solvers` with
   `Functions` (+0.087), `FieldSpecifications` (+0.209) and `Constitutive` (+0.227). **This
   is why `physics_weighted` cannot work: the group it up-weights is barely better than the
   deck.**
2. **The bookkeeping anti-signal is an n = 63 artifact.** L1's −0.224 becomes **+0.036
   [−0.058, +0.129]** at n = 489. The negative partial that motivated the whole hypothesis
   does not survive. (L1 was careful about this: its §5.3 already reported `ts_bookkeeping`
   at +0.103 marginal and warned in §5.5 that the conditional column looked like a "general
   quality factor". L1's −0.307 was the **judge's** bookkeeping credit — a property of the
   LLM's scoring, not of TreeSim's.)

**So the cancellation mechanism is absent from the object we tried to fix.** L1's diagnosis
may still be true *of the judge*; it is not true of TreeSim, and TreeSim is what a
deterministic re-weighting acts on.

### 5.3 And `Solvers` still cannot be turned into a metric

`ts_solvers` retains +0.223 [+0.123, +0.317] over the aggregate at n = 489 — real,
replicated, CI excluding zero. Yet `solvers_only` **loses** to uniform (Δ = −0.102
held-out, −0.032 full). Three reasons, all structural:

1. **Undefined on 5 of 18 tasks** (150 of 489 runs) — constitutive-driver decks have no
   `<Solvers>`. A metric that cannot score a third of the benchmark is not a metric.
2. **It throws away `Constitutive` (+0.227) and `Mesh` (+0.205)**, which are independently
   predictive.
3. **Up-weighting is not free**: the weight sweep shows monotone degradation past
   w_phys ≈ 2–3, and `physics_only`/`solvers_only` both land at the ~50th percentile of a
   random-subset null whose mean is negative.

**The right statement is "the `Solvers` subtree is where structural error predicts physical
error", not "weight `Solvers` more".**

---

## 6. ROBUSTNESS AND MULTIPLICITY

| check | effect |
|---|---|
| task-clustered bootstrap (resample tasks, not rows) — `L2_report_supp.txt` §S5 | held-out `physics_weighted` SOF_all: Δ = +0.033, cluster CI **[−0.002, +0.084]** (still contains 0); SOF_wc: +0.043 [+0.010, +0.087]. full: +0.021 [−0.019, +0.066]. `physics_only` negative with 0 inside everywhere. **No change in conclusion.** |
| drop TreeSim's extra-element penalty (§S2) | Δ moves by ≤ 0.017 anywhere. **No change.** |
| K3's 4-dp rounding of `treesim` (G2) | ≤ 0.0006 ρ points on the full set, 0 on held-out. **No change.** |
| aggregator switch (mean-over-reductions → worst-reduction) | absolute ρ falls as K3/L1 warned (0.362 → 0.121 held-out); **the paired Δ does not** — `physics_weighted` goes +0.033 → +0.043 and `solvers_only` goes −0.102 → −0.173. Disclosed in the state of play. |

**Multiplicity, stated plainly.** The headline runs 3 variants × 3 datasets × 4 SOF
variants = 36 paired tests. **Two are nominally p < 0.05 in the favourable direction**
(held-out SOF_wc `physics_weighted` p = 0.023; full SOF_ran `physics_weighted` p = 0.043)
and **two are nominally p < 0.05 in the *unfavourable* direction** (held-out SOF_wc_ran
`solvers_only` p = 0.011; held-out SOF_wc `solvers_only` p = 0.051). Bonferroni over the 3
variants in the pre-declared primary cell puts the threshold at α = 0.0167 and **nothing
clears it — the primary-cell `physics_weighted` p is 0.075, which does not clear even an
uncorrected 0.05.** The pre-declared rule (§0.8) is not met.

**This thread was a confirmatory test of an exploratory, non-pre-registered L1 finding, and
it is reported as such.** L1 §6 disclosed that no §5 test survived Bonferroni over its own
family. L2 pre-registered the primary cell and the decision rule before computing a single
variant (§0), and the rule returned "not supported."

---

## 7. WHAT A HUMAN MUST DECIDE

1. **Do we ship a physics-weighted TreeSim? No.** The best honest number is +0.033 ρ points
   on the primary set with a CI touching zero, a permutation-null p of 0.065, and an
   attribution that swaps between knobs across splits. **L1 §7.2's "recommended" experiment
   is now run and answered negatively — mark it resolved-negative rather than open.** The
   cost of being wrong here is high: changing the headline metric on a +0.03 ρ point,
   post-hoc, tuned-adjacent basis is exactly what a reviewer would call metric shopping.
2. **Report the null, and report the random-subset test with it.** "A physics-selected
   subset of the deck predicts simulation fidelity no better than a random subset of the
   same size (51.5th percentile of 2 000 draws)" is a strong, cheap, honest sentence, and it
   forecloses an obvious reviewer question about whether our structural metric could be
   trivially improved. It also **strengthens the defence of uniform 1/N**: we tested the
   most plausible alternative weighting, with power to detect Δρ = 0.034, and found nothing.
3. **Does the `Solvers` finding go in the paper, and as what?** It replicates at 5× n with a
   CI excluding zero (partial ρ = +0.223 [+0.123, +0.317] over the deck aggregate). My read:
   it belongs in **analysis/limitations as a diagnostic** — "structural error in the
   `Solvers` subtree is what predicts physical divergence; error elsewhere largely does
   not" — and **not** as a metric change, for the three structural reasons in §5.3. Someone
   should decide whether the rebuttal has room.
4. **Should L1's §5 diagnosis be restated?** L1's cancellation story is about the **judge's**
   per-section credit. L2 shows it does **not** hold for TreeSim's own sections at n = 489
   (bookkeeping partial +0.036 [−0.058, +0.129]; `Events` marginal +0.211). If anything from
   L1 §5.4 is quoted in the response, it must be scoped to the judge, and L2's n = 489
   refutation of the TreeSim analogue should be acknowledged in the same breath.
5. **Is more n worth buying? No, and this is the one place L2 is decisively better than L1.**
   MDE for the paired Δ is 0.034 on the full set. There is no experiment to buy: the
   question is answered.
6. **Val inclusion.** The full-489 set mixes K3's held-out with its staged/K2-rescored val,
   which carries K3 §6's disclosed caveats. Held-out alone (n = 126) is the pre-declared
   primary and it agrees with the full set on every qualitative conclusion, so nothing turns
   on this. If the response quotes only one number, quote the held-out one.

---

## 8. ARTIFACTS

| file | what |
|---|---|
| `artifacts/L2_sections.py` | builds TreeSim's top-level section decomposition for all 489 SOF runs; asserts **G1** |
| `artifacts/L2_sections.jsonl` | **the dataset** — per run: section units (tag, score), n_ref, n_extra, TreeSim of record, all four SOF variants, status |
| `artifacts/L2_sections_report.txt` | G1 console output + tag/unit census |
| `artifacts/L2_analyse.py` | headline paired comparison, decomposition of the re-weighting, random-subset null, weight sweep, power |
| `artifacts/L2_report.txt`, `artifacts/L2_results.csv` | full console report + every statistic machine-readable |
| `artifacts/L2_supp.py` | S1 reconciliation with L1 · S2 penalty sensitivity · S3 L1 §5.5 at n = 489 · S4 partial correlations · S5 task-clustered bootstrap |
| `artifacts/L2_report_supp.txt`, `artifacts/L2_results_supp.csv` | supplement output |

**Reproducing** (no API, no GEOS, ~35 min of CPU):

```bash
cd neurips_review/sprint/artifacts
python3 L2_sections.py   # ~20 s — asserts G1, refuses to write if the decomposition fails
python3 L2_analyse.py    # ~25 min (20 000-draw permutation p, 10 000-draw paired bootstraps,
                         #          2 000-draw random-subset nulls)
python3 L2_supp.py       # ~8 min
```

Statistics are imported from `J2_validate` (`spearman_fast`, `n_for_spearman`), from
`L1_analyse` (`within_task_rank`, `paired_delta`, `min_detectable`) and from `L1_supp`
(`pcorr`, `boot_stat`); the section decomposition is imported from `J1_sections`
(`deck_sections`, `aggregate`), which itself imports `src/eval/judge_geos` unmodified.
**Nothing is forked, so nothing can drift.**
