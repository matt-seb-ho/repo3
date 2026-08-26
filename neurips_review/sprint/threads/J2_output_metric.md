# Thread J2 — a simulation-output-side fidelity metric for GEOS runs

## STATE OF PLAY  (keep current; this is the resume point)

**Status: 6-task validation COMPLETE. All artifacts on disk.**

| | |
|---|---|
| Metric | **SOF** (Simulation Output Fidelity), defined in §1, amended in §3 / §7.5 |
| Implementation | `artifacts/J2_metric.py` (metric), `J2_validate.py` (stats), `J2_interp_check.py`, `J2_run_task.py` + `J2_run_grid.py` + `J2_discover.py` (execution) |
| Executed set | **6 usable tasks × 6 cells × 3 seeds = 108 runs**; 3 inherited from A2 + 3 added by J2 |
| Reference gate | 5 candidates tried, **2 rejected on reference behaviour alone** (§7.4 G1 wall-clock cap, G2 GT deck set broken) |
| Headline | TreeSim is a **moderate but insufficient** predictor of output fidelity: pooled Spearman **rho = 0.41** (95% CI 0.22-0.57, n=108), rho^2 ~ 0.17-0.25; per-task rho 0.11-0.83. Cells do NOT separate (SIGA vs Vanilla delta = -0.009, p = 0.29). **See §9.** |
| Known issues found | **4 metric bugs** (§3.3 name canonicalisation, §7.5 order-dependent collision, §8.6 reference/generated asymmetry, plus the §3.1 mesh-dependent-L2 check) + **1 data-integrity finding** in A2's published artifacts (§4b) |

**Done:** metric definition (§1); admissibility rules (§3); 3-task validation (§4);
interpolation cross-check (§6); extension gate + grid (§7); bug-4 fix (§8.6);
**corrected 6-task validation (§9) — this is the result to quote.**
**Superseded:** §8 (computed before the bug-4 fix; kept verbatim for audit).
**Running:** nothing.
**Next if resumed:** nothing blocking. Optional: extend to the 2 remaining candidate tasks
only if the wall-clock cap is raised (they were rejected for cost / broken GT, not chance).

---

**Owner:** Thread J2 (autonomous sprint, NeurIPS 2026 sub 31642 SIGA)
**Started:** 2026-07-27 ~04:50 local
**Scope:** design an output-side evaluation metric (the complement to TreeSim, which is
input-side only), validate it on the decks Thread A2 already executed, and answer the AC's
actual question: *does structural similarity of the deck predict similarity of the simulation?*
**Artifacts prefix:** `neurips_review/sprint/artifacts/J2_*`
**Builds on:** Thread A2 (`A2_execution_rungs45.md`). A2's execution harness, reference gate,
determinism check, and raw per-field reductions are inherited, not redone.

---

## 0. What I inherit from A2, and what I am fixing

Inherited (not re-derived):
- The **injected-observable** method: an identical `<VTK plotLevel=3>` + final-time
  `PeriodicEvent` is appended to reference *and* generated decks alike; the run is then
  reduced to **mesh-independent bag statistics** (min/max/mean/RMS) of every field.
  No interpolation anywhere.
- **GEOS is bitwise deterministic** on this build (16/16 statistics identical across repeat
  runs, `A2_scratch/detcheck.json`) → one execution per deck is sufficient.
- The **reference-deck gate**: `ExampleMCCWellbore` excluded (reference hits the 600 s cap);
  `ExampleProppantTest`'s reference completes but with 10 retried timesteps.
- A2's per-run raw field statistics: `A2_scratch/qoi_v2.jsonl` (38 runs × 34–43 fields ×
  4 reductions) and the DruckerPrager `TriaxialDriver` result tables in
  `A2_scratch/runs/*__AdvancedExampleViscoExtendedDruckerPrager/*.txt`.

What I am fixing — A2's weakness, stated in its own §13.6/§14:
- A2 reduced each run to **one scalar** and applied a **hard 10 % tolerance**. The resulting
  errors clustered at exactly three values (0.00 %, 10.47 %, 99.97 %) and the threshold fell
  *between* clusters, so the pass/fail verdict was decided entirely by where the threshold sat.
- A2 also **discarded the other 33–42 fields it had already measured**. That is where the
  "what actually differs" information lives.

J2 therefore produces a **continuous, multi-quantity, reference-normalised** score.

---

## 1. THE METRIC — Simulation Output Fidelity (SOF)

*Declared in full before any J2 number was computed. Frozen at commit time of this section.*

### 1.1 Data model

A run's output is an **output bundle** `B`: a finite set of **quantities**. A quantity `q`
carries a **sample bag** `B_q` — a finite multiset of reals — plus a flag saying whether the
bag is **ordered** (a time series) or **unordered** (a spatial field).

Two backends produce bundles. Both are applied identically to reference and generated decks.

- **Mesh backend (VTK).** Read the *last* snapshot of the injected `a2qoi` VTK output. For each
  `CellData`/`PointData` array `A`, quantity name `CellData:A` / `PointData:A`; sample bag =
  the array's values over the mesh's cells, merged across all ranks/regions of that snapshot.
  Multi-component arrays are reduced to their per-cell Euclidean magnitude first.
  Bag is **unordered**. (Bookkeeping arrays `localToGlobalMap`, `ghostRank`, `domain`,
  `elementCenter` are dropped — identically everywhere.)
- **Scalar-table backend.** For a task whose solver natively writes a fixed-schema scalar table
  (GEOS `TriaxialDriver`), quantity name `<Table>:<column>`; sample bag = the column's values
  over the table's rows. Bag is **ordered** (rows are time-ordered).
  No injection is needed: the schema is fixed by the solver, so the observable is already
  identical across decks.

Only **bag reductions** are ever compared. Consequently the metric is invariant to the number
of mesh cells and to the number of time samples, and **no interpolation is performed anywhere**
in the primary metric. (§6 runs an interpolated *secondary* check purely to show it does not
change the answer.)

### 1.2 Reductions

For a bag `x` with `n = |x| > 0`:

```
ρ ∈ { min, max, mean, rms }          rms(x) = sqrt( mean( x² ) )
plus  ρ = last                        only for ordered (time-series) bags
```

`rms` is used rather than the unnormalised ℓ² norm precisely because the ℓ² norm scales like
√n and would therefore be **mesh-dependent**. (A2's `l2` field is already RMS —
`vtu_stats.py:75` — so this is the same quantity, renamed for accuracy.)

`last` exists only where "last" is defined. It is the reduction that reproduces A2's
"final axial stress" scalar, so the new metric contains the old one as a special case.

### 1.3 Reference-defined comparison basis (this is the fairness mechanism)

For task `t`, run the reference deck under **identical** treatment (same injection, same
wall-clock cap, same copy rules) and let `R` be its bundle.

**Live quantity set**

```
Q_t := { q ∈ R : max(R_q) − min(R_q) > 0 }
```

i.e. the quantities that actually *vary* in the reference solution. A quantity that is constant
in the reference carries no solution information — it is a material constant or a zero
derivative echoed straight back out — and including it inflates every run's score toward 1
without discriminating anything. `Q_t` is determined **from the reference alone**, so it is
byte-identical for every cell and every seed. Excluded quantities are written out
(`J2_excluded_quantities.csv`) and a sensitivity arm (§5) puts them back.

**Per-quantity scale**

```
S_q := max( |min(R_q)| , |max(R_q)| )        (> 0 for every q ∈ Q_t)
```

One scale per quantity, shared by all of its reductions — so a reduction that happens to sit
near zero (e.g. a mean of a signed field) cannot blow the ratio up. `S_q` depends on the
reference only. This makes the metric **scale-free**: `S_q` carries the quantity's units, so
every δ below is dimensionless and comparable across quantities and across tasks.

### 1.4 Deviation, fidelity, aggregation

For a generated bundle `G`:

```
                | ρ(G_q) − ρ(R_q) | / S_q      if q ∈ G
δ(q,ρ)  :=      {
                +∞                             if q ∉ G          (coverage penalty)

ψ(q,ρ)  :=  clip( 1 − δ(q,ρ) , 0 , 1 )   ∈ [0,1]

Ψ(q)    :=  mean over ρ of ψ(q,ρ)        ∈ [0,1]        ← per-quantity breakdown

SOF     :=  mean over q ∈ Q_t of Ψ(q)    ∈ [0,1]        ← the reported scalar
```

Reading: `ψ = 1 − relative-deviation-from-reference-scale`, clipped. `ψ = 1` means exact
reproduction; `ψ = 0` means the reduction is off by at least 100 % of the reference quantity's
own magnitude, i.e. "completely wrong". `SOF = 1` means the run's output is indistinguishable
from the reference's at the level of these reductions.

Three deliberate choices, each with a sensitivity arm in §5:

1. **Clipping at δ = 1 (saturation).** Being 1000× too large and being 100 % too small are
   both "completely wrong"; a bounded score should not rank the flavours of total failure.
   The raw unclipped δ is written to the per-quantity CSV so nothing is lost.
2. **The denominator of SOF is `|Q_t|`, fixed by the reference.** A run that emits fewer
   quantities does not get an easier test — every missing live quantity contributes Ψ = 0.
   Coverage is therefore *inside* the metric, not a separate caveat.
3. **Arithmetic mean over quantities.** The least clever aggregator, chosen because it is the
   hardest to accuse of tuning. Geometric mean, min, and a primary-field-only restriction are
   all reported in §5.

### 1.5 Behaviour on every known pathological case — declared explicitly, never NaN

| status | trigger | `SOF_all` | `SOF_ran` |
|---|---|---|---|
| `ok` | reached final time, bundle non-empty | SOF | SOF |
| `no_output_inject` | observable could not be attached (deck unparseable even under GEOS-lenient parsing) | **0** | excluded |
| `no_output_load` | GEOS rejected the deck before time-stepping | **0** | excluded |
| `no_output_run` | started, did not reach final time (divergence, or the 600 s wall-clock cap) | **0** | excluded |
| `no_overlap` | reached final time and wrote output, but shares **no** live quantity with the reference | **0** | **0** |
| `task_unusable` | the **reference** produced no comparable final state | task dropped for **all** cells | dropped |

Annotations that are recorded but are **not** exclusions:

- `ref_clean_converged` — did the reference reach A2's L4 (no cuts, no retries, no failed line
  searches)? `ExampleProppantTest` = **False** (10 retried timesteps). SOF measures *agreement
  with the reference*, not correctness. Because GEOS is bitwise deterministic, a reference that
  completes-with-retries is still a perfectly well-defined comparand: the input→output map is a
  function. So the task stays in, annotated, and every result is also reported split by this
  flag. Excluding it would have been a silent, unjustified drop.
- `ref_timeout` — the reference hit the wall-clock cap (`ExampleMCCWellbore`). There is no
  reference final state, so `SOF` is *undefined*, not zero. Zero would be arbitrary and would
  make the headline depend on which tasks we could afford. → `task_unusable`, dropped for every
  cell identically. This is a **cost limit disclosed as a limitation**, not a result about any cell.

**Two reported conventions, always both:**

- `SOF_all` — non-executing runs scored **0**. This is the paper's own failures-as-zero
  convention (`docs/XN-011`, A2 §2.1) and is the primary number.
- `SOF_ran` — conditional on the run producing output. Isolates *"does TreeSim predict
  fidelity given the deck runs"* from *"does TreeSim predict runnability"*. Reporting only
  `SOF_all` would let a runnability effect masquerade as a fidelity effect, and vice versa.

### 1.6 Pass/fail is strictly secondary

A pass/fail flag `SOF ≥ τ` is reported **only** as a curve over all τ ∈ [0,1]
(`J2_threshold_curve.csv`), never as a single number, so no threshold can do the work the way
A2's 10 % tolerance did. Where one number is needed the nominal value is τ = 0.95, declared here.

---

## 2. Implementation

`neurips_review/sprint/artifacts/J2_metric.py` — extraction + metric + per-run/per-quantity CSVs.
`neurips_review/sprint/artifacts/J2_validate.py` — correlations, per-cell, sanity, sensitivity.

Both are runnable end-to-end from the preserved A2 run directories; nothing is hard-coded from
memory. Log continues below as work proceeds.

---

## 3. Implementation findings that AMENDED the metric definition

All four amendments below were forced by inspecting the **reference** bundles and by two
designated calibration runs; each is a rule applied identically to every cell and seed.
They are recorded here rather than silently folded into §1.

### 3.1 `rms`, not the raw L2 norm — the mesh-independence check

A2's `vtu_stats.py:75` already computes `sqrt(sum(v**2)/v.size)`, i.e. RMS. Verified before
reuse: the *unnormalised* ℓ² norm scales like √n and would have made a "mesh-independent"
metric silently mesh-dependent, which matters here because `F8_s1` runs ThermoPoro on a
**16-cell** mesh against the reference's 40. Renamed to `rms` in J2 so the property is
visible in the name.

### 3.2 Admissibility rules — declared, task-agnostic, reference-only

A fully automatic "every field that varies in the reference" set turned out to include
material that is not simulation output at all. Five exclusion rules, all evaluated on the
**reference bundle only** (hence identical for all 18 runs of a task):

| rule | what it removes | why it is not physics |
|---|---|---|
| bookkeeping / index | `*dofIndex`, `childIndex`, `parentIndex`, `degreeFromCrack*`, `SIFNode`, `localToGlobalMap`, `ghostRank`, `domain`, `elementCenter` | integer labels for unknowns and mesh topology. Comparing them measures how a deck *numbered* its DOFs. |
| solver diagnostic | `newton_iter`, `residual_norm` | describe how the solve went, not what it produced |
| independent variable | `time` (scalar-table backend) | the schedule the deck was **given** — an input. Its physical consequence is fully visible in the state columns (for a rate-dependent material a different schedule moves the stress), so removing it deletes double-counting, not information. |
| subnormal in reference | `componentConcentration`, `componentConcentration_n`, `water_componentDensity` (ProppantTest) | entries are subnormal doubles (≈4.7e-310) — GEOS allocates these arrays for a single-component fluid and never fills them. Deterministic on this build, but meaningless. |
| numerically constant | `elementArea` (ProppantTest), plus 14/21/2 genuinely constant fields | range/scale = 1.0e-12, i.e. round-off. Strict `max>min` kept it and would then have normalised deviations by a scale 10¹² larger than the variation. Threshold `CONST_RTOL = 1e-9`; the smallest *genuine* variation in any reference here is 7.1e-4, so the cut sits far from both round-off and physics. |

Resulting live quantity counts: ThermoPoro **18 / 34**, ProppantTest **11 / 43**,
DruckerPrager **4 / 9**. Full list with reasons: `J2_excluded_quantities.csv`.

### 3.3 THE IMPORTANT ONE — canonicalising constitutive-model names

GEOS names a constitutive array `<constitutiveModelName>_<fieldName>`. **The model name is
chosen freely by the deck author; the field name is fixed by the solver.** Verified:

```
REF   ThermoPoro:  <ThermalCompressibleSinglePhaseFluid name="fluid">   -> CellData:fluid_density
F0_s2 ThermoPoro:  <ThermalCompressibleSinglePhaseFluid name="water">   -> CellData:water_density
SE_s2 ThermoPoro:  <PorousElasticIsotropic name="porousRock">  (ref: name="rock")
```

Same model **type**, same physics — F0_s2's pressure field agrees with the reference to
**4.1e-11** — but the array names do not match. Under the coverage rule (missing quantity →
Ψ = 0) the uncanonicalised metric scored F0_s2 **0.776** instead of 0.998, purely for
calling the fluid `water`.

That is a metric that partly measures **deck naming** — exactly the input-side conflation
this thread exists to avoid. Fix: rewrite `<modelName>_<field>` → `<ModelType>_<field>`
using the deck's own `<Constitutive>` block (name → XML tag), for reference and generated
decks alike. A deck that swaps in a genuinely *different* constitutive model still fails to
match, which is correct — that IS a physics difference. Zero name collisions occurred in any
of the 54 runs; a collision would fall back to the raw name and be recorded.

**This is kept as an explicit sensitivity arm** (`no name canonicalisation`) because it cuts
in a direction that matters — see §4.5.

### 3.4 Non-finite guard

A generated field that overflows to `inf`/`NaN` yields δ = +∞ → ψ = 0, never a NaN score.
Guarded at the point of computation so no downstream statistic can silently become NaN.

---

## 4. VALIDATION on the 3 executed tasks (54 runs, 45 with output)

Command: `python3 neurips_review/sprint/artifacts/J2_validate.py`
Report: `J2_validation_report.txt`. Data: `J2_per_run.csv`, `J2_per_quantity.csv`,
`J2_correlations.csv`, `J2_per_cell.csv`, `J2_sanity.csv`, `J2_sensitivity.csv`,
`J2_threshold_curve.csv`, `J2_bundles.jsonl`.

### 4.1 HEADLINE — TreeSim is a WEAK predictor of output fidelity

Spearman ρ, permutation p (20 000 perms), percentile bootstrap 95 % CI (10 000):

| scope | convention | n | ρ | p | 95 % CI |
|---|---|---:|---:|---:|---|
| ThermoPoro | SOF_all | 18 | 0.110 | 0.662 | [−0.41, 0.59] |
| DruckerPrager | SOF_all | 18 | 0.109 | 0.660 | [−0.46, 0.59] |
| **ProppantTest** | SOF_all | 18 | **0.609** | **0.008** | [0.18, 0.90] |
| **POOLED (within-task ranks)** | **SOF_all** | **54** | **0.292** | **0.034** | **[0.01, 0.53]** |
| POOLED (raw values) | SOF_all | 54 | 0.223 | 0.104 | [−0.06, 0.49] |
| **POOLED (within-task ranks)** | **SOF_ran** | **45** | **0.223** | **0.141** | **[−0.09, 0.49]** |
| POOLED: TreeSim vs `ran` (0/1) | — | 54 | 0.239 | 0.082 | [0.01, 0.45] |

Read this as: **TreeSim explains about 9 % of the rank variance in output fidelity
(ρ² ≈ 0.085), the association is barely distinguishable from zero, and what association
there is disappears once you condition on the deck actually running.** The pooled
`SOF_all` correlation is carried by (a) a single task, ProppantTest, and (b) the
runnability component — TreeSim vs the binary "produced output" is ρ = 0.24, essentially
the same size as the fidelity correlation.

Two of the three tasks show **no** association at all (ρ ≈ 0.11, p ≈ 0.66).

**This is the answer to the AC's question and it is a negative one.** A structural
similarity score on the input deck does not tell you whether the simulation agrees with the
reference. It is a weak proxy for *runnability* and close to uninformative about *fidelity*.

### 4.2 Per-cell distribution — no separation, corroborating Thread B

Mean ± sd of `SOF_all`, n = 9 per cell pooled:

| cell | ThermoPoro | DruckerPrager | ProppantTest | POOLED |
|---|---|---|---|---|
| F0 Vanilla | 0.646±0.560 | 0.922±0.136 | 0.667±0.577 | 0.745±0.429 |
| F4 X+M | 0.941±0.000 | 0.609±0.534 | 0.643±0.558 | 0.731±0.418 |
| F6 S+X | 0.628±0.543 | 0.868±0.117 | 0.665±0.576 | 0.720±0.416 |
| F8 S+X+M | 0.882±0.102 | 0.834±0.163 | 0.666±0.577 | 0.794±0.319 |
| F11 SE-prose | 0.646±0.560 | 0.942±0.101 | 0.999±0.002 | 0.862±0.328 |
| SE | 0.664±0.575 | 0.872±0.112 | 1.000±0.000 | 0.846±0.328 |

Kruskal–Wallis across the 6 cells: ThermoPoro p = 0.945, DruckerPrager p = 0.888,
ProppantTest p = 0.241, pooled p = 0.550. SIGA cells (n = 45, mean 0.791) vs Vanilla
(n = 9, mean 0.745): Δ = **+0.046**, Mann–Whitney **p = 0.653**.

Every cell's sd is comparable to or larger than every between-cell difference.
**No metric separates the cells** — the same conclusion Thread B reached on its 24 held-out
(task, seed) pairs by a completely different route. That is corroboration, not failure.

### 4.3 Known-good / known-bad — the metric separates them

| | task | run | TreeSim | SOF | SOF_wc |
|---|---|---|---:|---:|---:|
| KNOWN-GOOD | DruckerPrager | F8_s1 | 0.972 | **1.0000** | 1.0000 |
| KNOWN-GOOD | DruckerPrager | SE_s2 | 1.000 | **1.0000** | 1.0000 |
| KNOWN-GOOD | ThermoPoro | F0_s2 | 0.772 | **0.9978** | 0.9938 |
| KNOWN-GOOD | ThermoPoro | SE_s2 | 0.729 | **0.9978** | 0.9938 |
| KNOWN-BAD | ThermoPoro | F8_s1 | 0.800 | **0.7645** | 0.3882 |
| KNOWN-BAD | DruckerPrager | F8_s2 | 0.922 | **0.6752** | 0.3110 |
| KNOWN-BAD | DruckerPrager | F6_s3 | 0.911 | **0.7788** | 0.5611 |

Separated under the declared primary (gap **+0.219**) and much more sharply under the
worst-reduction arm (gap **+0.433**). The two byte-identical-tables DruckerPrager runs score
exactly **1.0000**, as required.

**Reported weakness of the declared primary, not hidden:** averaging ψ over the four
reductions *dilutes* a catastrophic failure. `F8_s1` ThermoPoro is 99.97 % wrong on peak
pressure, yet Ψ(pressure) = 0.646 — because the reference pressure field is a sharp
near-wellbore spike whose `mean` is only 10 % of its `max`, so a run that produces
essentially zero pressure is "only" 10 % of peak off on the mean. `SOF_wc`
(Ψ = min over reductions, i.e. worst summary statistic) gives Ψ(pressure) = 0.0003 and is
the crisper instrument. Both are reported for every run; §4.5 shows the headline does not
depend on the choice. **The declared primary was kept as primary** — swapping it after
seeing which separates better would be exactly the tuning this metric exists to avoid.

### 4.4 Threshold curve — why pass/fail must not be reported alone

Runs with `SOF_all ≥ τ`, out of 9 per cell:

| τ | F0 | F4 | F6 | F8 | F11 | SE |
|---|---|---|---|---|---|---|
| 0.50 | 7 | 7 | 7 | 8 | 8 | 8 |
| 0.80 | 6 | 7 | 6 | 6 | 8 | 7 |
| 0.90 | 6 | 6 | 5 | 5 | 7 | 6 |
| 0.95 | **5** | 2 | 3 | 3 | 6 | 6 |
| 0.999 | 4 | 2 | 1 | 1 | 4 | 4 |

The cell ordering **changes with τ** — Vanilla is mid-pack at τ = 0.80 and joint-second at
τ = 0.95. Any single declared tolerance would have picked a winner by fiat, which is exactly
A2's problem with its 10 % L5 cut. The full curve is in `J2_threshold_curve.csv`.

### 4.5 Sensitivity — the headline is invariant to every design choice

Pooled within-task Spearman across 13 arms:

| arm | ρ (SOF_all) | p | ρ (SOF_ran) | p | good_min | bad_max | separated |
|---|---:|---:|---:|---:|---:|---:|---|
| **PRIMARY (declared)** | **0.292** | 0.032 | 0.223 | 0.137 | 0.998 | 0.779 | yes |
| worst-reduction (agg_ρ=min) | 0.295 | 0.031 | 0.233 | 0.128 | 0.994 | 0.561 | yes |
| agg_q = geomean | 0.286 | 0.038 | 0.214 | 0.162 | 0.998 | 0.765 | yes |
| agg_q = min | 0.248 | 0.069 | 0.176 | 0.249 | 0.961 | 0.616 | yes |
| scale = range | 0.292 | 0.031 | 0.223 | 0.137 | 0.998 | 0.761 | yes |
| scale = peak_or_range | 0.292 | 0.032 | 0.223 | 0.139 | 0.998 | 0.779 | yes |
| squash = exp(−δ) | 0.292 | 0.033 | 0.223 | 0.138 | 0.998 | 0.826 | yes |
| squash = 1/(1+δ) | 0.292 | 0.034 | 0.223 | 0.137 | 0.998 | 0.853 | yes |
| A2's primary scalars only | 0.248 | 0.073 | 0.175 | 0.247 | 1.000 | 0.646 | yes |
| no quantity exclusions | 0.255 | 0.062 | 0.188 | 0.217 | 0.932 | 0.805 | yes |
| **no name canonicalisation** | 0.296 | 0.031 | **0.306** | **0.043** | **0.776** | 0.779 | **NO** |
| drop \|scale\| < 1e-12 | 0.294 | 0.032 | 0.249 | 0.101 | 1.000 | 0.779 | yes |
| worst-reduction + geomean_q | 0.263 | 0.054 | 0.194 | 0.202 | 0.994 | 0.513 | yes |

**ρ ranges over 0.248 – 0.296 across all 13 arms (median 0.292).** The headline — a weak,
marginal association that vanishes conditional on running — does not depend on the
normalisation, the squash, either aggregator, the quantity set, or the reduction set. That
is the strongest statement available about robustness, and it means no reviewer can move the
conclusion by objecting to one of these choices.

**The one arm that behaves differently is diagnostic, not a free parameter.** Dropping name
canonicalisation is the *only* arm that (a) breaks known-good/known-bad separation (a
machine-precision-exact run scores 0.776, below a 99 %-wrong run at 0.779) and (b) makes the
conditional correlation significant (ρ_ran = 0.306, p = 0.043). Both happen for the same
reason: without canonicalisation the "output" metric is partly re-reading the deck's naming
choices, which is input-side information TreeSim already sees. **An output metric that
correlates better with TreeSim because it secretly measures naming is a broken metric, and
this arm is the proof that canonicalisation was necessary rather than convenient.**

### 4.6 Status decomposition

| task | n | ok | no output |
|---|---:|---:|---:|
| ThermoPoro | 18 | 14 | 4 |
| DruckerPrager | 18 | 17 | 1 |
| ProppantTest | 18 | 14 | 4 |
| **POOLED** | **54** | **45** | **9** |

9 of the 54 zeros in `SOF_all` are non-execution, not wrong physics. This is why both
conventions are always reported.

### 4.7 Power — the executed set is too small for a stable answer

Detectable |ρ| at 80 % power, α = 0.05 (Bonett–Wright):

| target ρ | n needed | tasks needed (6 cells × 3 seeds) |
|---|---:|---:|
| 0.2 | 206 | 12 |
| 0.3 | **90** | **5** |
| 0.4 | 50 | 3 |
| 0.5 | 31 | 2 |

At n = 54 the smallest detectable |ρ| is **≈ 0.38**. The observed ρ = 0.29 sits **below** that,
so the study is underpowered for the effect it is actually measuring: its bootstrap CI
[0.03, 0.53] is consistent with anything from "no association" to "moderate".
**Stated conclusion: n ≈ 90 (≈ 5 usable tasks × 6 cells × 3 seeds) is needed to resolve
ρ = 0.3 at 80 % power; n ≈ 206 (≈ 12 tasks) to resolve ρ = 0.2.** Extension to more tasks is
therefore the single highest-value next step, and §7 pursues it.

### 4.8 Robustness of the headline (influence and jackknife)

- **Leave-one-out**: pooled ρ = +0.292, jackknife range **[+0.255, +0.332]**. No single run
  drives it; the most influential is ThermoPoro `SE_s1` (removing it gives ρ = +0.255).
- **Dropping the TreeSim = 0 points** (decks the eval harness could not parse, entered as 0
  by the failures-as-zero convention): n = 53, ρ = **+0.347**, p = 0.010, CI [0.07, 0.57].
  The weak association is therefore *not* an artifact of the zero-entry convention — it is
  slightly stronger without it, and still weak.
- **SIGA cells only** (F0 excluded): n = 45, ρ = +0.276, p = 0.066.
- **Task heterogeneity**: per-task ρ is 0.11, 0.11, 0.61. *Whether* TreeSim predicts output
  fidelity is itself task-dependent — a further reason not to quote the pooled number alone.

### 4.9 Continuity with A2 — SOF contains A2's scalar and ranks with it

Over the 43 runs where A2 reported a relative error,
`Spearman(SOF, 1 − A2's worst declared relative error) = **+0.974**, p < 1e-15`.

SOF is therefore not a different answer dressed up — it agrees with A2's single-scalar
verdict almost perfectly, while additionally (a) resolving the runs A2's three-value
clustering (0 %, 10.47 %, 99.97 %) could not separate, (b) saying *which* quantities differ,
and (c) removing the threshold that was doing all the work.

### 4.10 What actually differs — the per-quantity breakdown

`J2_quantity_rollup.csv`, mean Ψ over the 18 runs of each task, lowest first:

| task | most discrepant quantities | least discrepant |
|---|---|---|
| ThermoPoro | `mass` 0.678, `elementVolume` 0.678, `PointData:mass` 0.682, `averagePlasticStrain` 0.711, `totalDisplacement` 0.723 | fluid `density`/`dDensity` 0.778, `BiotPorosity_porosity` 0.778 |
| ProppantTest | `pressure` / `deltaPressure` 0.764, `proppantConcentration` 0.773, `proppantPackVolumeFraction` 0.774 | `elementVolume` 0.778, `ruptureTime` 0.778 |
| DruckerPrager | `axial_stress` 0.709 | `axial_strain` 0.910 |

Two readable statements come out of this:
- On **ThermoPoro** the largest discrepancies are `elementVolume` and `mass` — i.e. the
  **discretisation itself** — followed by kinematics (displacement), and only then the state
  variables (pressure, temperature). Decks diverge first in how they mesh the wellbore.
- On **DruckerPrager** the *strain* is reproduced far better than the *stress*
  (Ψ 0.910 vs 0.709). The decks impose nearly the right strain program and get the
  constitutive response wrong — precisely A2 §14's mechanism (rate-dependent material,
  different `tables/time.geos` schedule), now quantified rather than anecdotal.

This per-quantity layer is the part A2 discarded, and it is what lets us answer *what*
differs rather than only *whether*.

---

## 4b. A DATA-INTEGRITY FINDING ABOUT A2's PUBLISHED ARTIFACTS

While cross-checking, J2 found that **two of A2's 38 published rung-5 records are stale**.

```
A2_grid_qoi.jsonl      mtime 22:46      <- published artifact
A2_qoi_per_run.csv     mtime 22:52      <- published artifact (analyze.py mtime 22:30)
A2_scratch/qoi_v2.jsonl mtime 22:53     <- authoritative final pass
```

Diffing them run-by-run:

| task | run | published | authoritative (verified on disk) |
|---|---|---|---|
| ExampleProppantTest | `F0_s3` | `qoi_ok=false`, stage `injection` | `qoi_ok=true`, snapshot `000310` |
| ExampleProppantTest | `SE_s2` | `qoi_ok=false`, stage `run` | `qoi_ok=true`, snapshot `000310` |

Both were verified directly against the preserved run directories: each contains
`a2qoi/000310` **and** its `run.log` contains `Cleaning up events`, so both reached final
time and emitted the observable. The published files simply predate the final pass.

Both corrections go **against** A2's reported failure counts — i.e. A2 over-reports rung-5
failures for ProppantTest by 2 runs. J2 uses the authoritative `qoi_v2.jsonl` throughout.

**And one of the two is substantively important.** `ExampleProppantTest F0_s3` is the
Vanilla deck with the illegal `--` inside an XML comment — the deck the eval harness could
not parse, entered as **TreeSim = 0.000**, the lowest structural score in the entire study.
It runs to completion under GEOS and its output matches the reference at **SOF = 1.0000**.

> The single worst-scoring deck by the structural metric produces a simulation
> indistinguishable from the reference.

That is the sharpest single counterexample available to "structural similarity predicts
simulation similarity", and it exists only because the stale record was caught.

*Caveat, stated:* the injector strips XML comments when (and only when) a deck fails strict
parsing, matching GEOS' pugixml permissiveness (A2 §12 bug 3). Comments are inert to GEOS,
so this cannot change physics — but it is a **conditional** normalisation, triggered only by
malformed-comment decks, all of which here are Vanilla. It therefore acts in Vanilla's
favour, not SIGA's, so it cannot be flattering our own claim.

---

## 5. §1.5 amendment — one status was missing from the declared table

`no_output_extract`: the deck **reached final time** but the injected observable produced
nothing readable (no `a2qoi/` snapshot, or no decodable field). Declared behaviour:
`SOF_all = 0` **and** `SOF_ran = 0`. It is grouped with `no_overlap`, not with the
`no_output_load` / `no_output_run` family: the deck *did* run, so excluding it from
`SOF_ran` would let a deck that runs and emits nothing comparable escape the conditional
analysis entirely. Recorded here because it was implemented in `classify_status()` but
omitted from the §1.5 table as first written.

---

## 6. THE INTERPOLATION CROSS-CHECK — it does not drive the result

Requirement: the primary metric interpolates nowhere, but a reviewer will ask whether a
conventional interpolated relative-L2 over the time history would have said something
different. `AdvancedExampleViscoExtendedDruckerPrager` is the one task where this is
answerable, because its `TriaxialDriver` writes a genuine scalar **time series**
(201 rows × 9 columns) rather than a single final state.

Script: `J2_interp_check.py`. Data: `J2_interp_check.csv`.

Two abscissae, because there is no single obviously-right one:

- **(A) normalised time** `τ = t / t_max ∈ [0,1]`, 201-point grid. Both series are uniformly
  sampled on their own `[0, t_max]`, and the driver's strain program is a table defined over
  the deck's own duration, so `τ` is the natural common abscissa. Matching on **absolute**
  time is ill-posed here: the reference runs to `t = 5` while 9 of 17 generated decks stop at
  `t = 1`.
- **(B) absolute time restricted to the overlap** `[0, min(t_max^ref, t_max^gen)]` — the
  choice a sceptical reviewer would propose, answering the different question "do they agree
  while both are still running".

Then `relL2 = ‖σ_gen(·) − σ_ref(·)‖₂ / ‖σ_ref(·)‖₂` on the axial stress, and
`fidelity = clip(1 − relL2, 0, 1)`.

### Rank agreement with the no-interpolation metric (n = 17 runs with output)

| pair | Spearman ρ | p |
|---|---:|---:|
| SOF (no interpolation) vs 1 − relL2 on normalised time | **+0.910** | 3e-7 |
| SOF (no interpolation) vs 1 − relL2 on overlapping absolute time | +0.772 | 0.0003 |
| SOF_wc (no interpolation) vs 1 − relL2 on normalised time | **+0.949** | 4e-9 |

### And the check that actually matters — each metric vs TreeSim

| metric | scope | ρ | p |
|---|---|---:|---:|
| SOF (no interpolation) | all 18 | +0.109 | 0.668 |
| SOF (no interpolation) | ran only | +0.128 | 0.624 |
| SOF_wc (no interpolation) | all 18 | +0.140 | 0.579 |
| 1 − relL2, interpolated on normalised time | all 18 | +0.128 | 0.611 |
| 1 − relL2, interpolated on normalised time | ran only | +0.155 | 0.552 |
| 1 − relL2, interpolated on overlapping absolute time | all 18 | **−0.092** | 0.718 |

**Conclusion: interpolation changes nothing.** The interpolated relative-L2 ranks the runs
almost identically to the reduction-based SOF (ρ = 0.91–0.95), and every variant gives the
same answer about TreeSim — no association, ρ between −0.09 and +0.16, p ≥ 0.55. The
no-interpolation design is therefore a *robustness* choice, not a result-shaping one, and the
finding cannot be attacked through the interpolation scheme.

### Incidental confirmation of A2 §14's mechanism
Every generated deck whose `tables/time.geos` runs to `t = 5` (matching the reference's
schedule) scores `relL2 = 0.0000` **exactly**; every deck that stops at `t = 1` differs.
Because `ViscoExtendedDruckerPrager` is rate-dependent, running the same final strain over a
5× shorter duration changes the stress. This is the same "TreeSim never reads the data
tables" mechanism A2 found, now visible in the full response history rather than one endpoint.

---

## 7. EXTENSION to more tasks — reference gate first, as the rule requires

Scripts: `J2_discover.py` (root-deck rule), `J2_run_task.py` (one deck), `J2_run_grid.py`
(the 6×3 grid). Scratch: `J2_scratch/`. Records: `J2_scratch/ref_gate.jsonl`,
`J2_scratch/grid.jsonl`.

### 7.1 Candidate selection
Of the 10 held-out tasks, A2 already covers 3 and excluded 2 by rule
(`ExampleMCCWellbore` — reference hits the 600 s cap; `TutorialHydraulicFractureWithAdvancedXML`
— TreeSim 0.013 in every cell, a universal model-level failure). That leaves **5 candidates**.

### 7.2 Top-deck rule — declared before any run
A **root** deck is a GT deck file that no other GT deck file `<Included>`s. Among roots
carrying an `<Events maxTime>` attribute (required, because the injected observable is a
final-time event), prefer `smoke` > `benchmark` > lexicographically first. The chosen
*filename* is then used unchanged for every generated deck, so the run unit is identical
across cells; a generated set missing that filename is a recorded failure, never an excuse to
pick a different deck for that cell.

| task | root decks | chosen TOP | maxTime | present in generated |
|---|---|---|---|---|
| CasedThermoElasticWellbore | benchmark, smoke | `CasedThermoElasticWellbore_smoke.xml` | 1e5 | 18/18 |
| VerticalPoroElastoPlasticWellbore | PoroDruckerPrager_bm, PoroElastic_bm | `PoroDruckerPragerWellbore_benchmark.xml` | 497639.9 | 18/18 |
| PureThermalDiffusionWellbore | benchmark, smoke | `thermalCompressible_2d_smoke.xml` | 1e5 | 18/18 |
| IsothermalHystInjection | smoke_3d only | `class09_pb3_smoke_3d.xml` | 1e6 | 18/18 |
| ExamplesingleFracCompression | ContactMechanics_bm only | `ContactMechanics_SingleFracCompression_benchmark.xml` | 1.0 | 18/18 |

### 7.3 Copy rule extended — and why it had to be
A2's gap-fill only restored `tables/`. Two of the new tasks need more:

- `ExampleIsothermalHystInjection` — GT ships `co2flash.txt`, `pvtgas.txt`; **no** generated
  deck set contains them (several author their own `tables/` and `fc_tables/` instead).
- `ExamplesingleFracCompression` — GT ships `crackInPlane_benchmark.vtu`, a 1 MB **external
  mesh**; only 7 of 18 generated sets contain it.

Rule (declared, applied identically to reference and generated): copy the entire source tree
and assert the copy covers the source (A2's bug-1 guard, raises loudly); then fill from GT
`inputs/` **only files the run dir does not already have**, and only genuine input assets —
never `*.py` helpers, and never anything whose name contains `Results`/`output` (A2's
near-miss where GT's own reference results file could have been read back as a run's output).
Every record carries `gt_assets_filled`, `gt_assets_skipped`, `stale_outputs_before_run`.

### 7.4 REFERENCE GATE RESULTS — 2 of 5 candidates are unusable, both for disclosable reasons

| task | wall | outcome | usable? |
|---|---:|---|---|
| **AdvancedExampleCasedThermoElasticWellbore** | 7.9 s | L3 ✓ L4 ✓, 10 steps, 56 quantities, 3 regions | **YES** |
| **AdvancedExamplePureThermalDiffusionWellbore** | 3.7 s | L3 ✓ L4 ✓, 10 steps, 23 quantities | **YES** |
| ExampleVerticalPoroElastoPlasticWellbore | 600.1 s | **hits the wall-clock cap** at t = 1990 of maxTime = 497 640 (0.4 % complete), with persistent line-search backtracking and 6 000+ negative pressures per Newton iteration | no — `task_unusable` |
| ExampleIsothermalHystInjection | 2.1 s | **GT's own deck set is broken** (below) | no — `task_unusable` |
| ExamplesingleFracCompression | *(pending)* | | |

#### Finding G1 — `ExampleVerticalPoroElastoPlasticWellbore` is unaffordable, like MCC
The reference reaches only 0.4 % of its horizon in 600 s. Same disposition as A2's
`ExampleMCCWellbore`: `task_unusable`, decided from reference behaviour alone, before any
generated deck was scored. A **cost limit disclosed as a limitation**, not a result about
any cell.

#### Finding G2 — `ExampleIsothermalHystInjection`'s GROUND TRUTH cannot run

```
class09_pb3_smoke_3d.xml:
  <Included><File name="./class09_pb3_hystRelperm_direct_base.xml"/></Included>

GT inputs/ actually contains:
  class09_pb3_drainageOnly_iterative_base.xml
  class09_pb3_hystRelperm_iterative_base.xml     <- "iterative", not "direct"
  class09_pb3_smoke_3d.xml, co2flash.txt, pvtgas.txt
```

GEOS aborts in `xmlWrapper::xmlDocument::addIncludedXML` after 2.1 s. The referenced file
`class09_pb3_hystRelperm_direct_base.xml` **does not exist anywhere in the entire GT tree**
(`find` over `experiments_gt/` returns nothing).

So **one of the 10 held-out tasks ships a ground-truth deck set that is internally
inconsistent and cannot be executed.** This is worth stating in its own right: for that task,
"similarity to the ground truth" is similarity to a deck that does not run. It also means the
task can never contribute to any execution-side or output-side evaluation, by anyone.
Recorded as `task_unusable`; no generated Hyst deck was scored.

#### Gate outcome, complete

| task | ref wall | L3 | L4 | quantities | usable |
|---|---:|:--:|:--:|---:|---|
| AdvancedExampleCasedThermoElasticWellbore | 7.9 s | ✓ | ✓ | 56 (3 regions: casing/cement/rock) | **YES** |
| AdvancedExamplePureThermalDiffusionWellbore | 3.7 s | ✓ | ✓ | 23 | **YES** |
| ExamplesingleFracCompression | 117.6 s | ✓ | ✓ | 30 | **YES** |
| ExampleVerticalPoroElastoPlasticWellbore | 600.1 s | ✗ | — | 0 | no — wall-clock cap (G1) |
| ExampleIsothermalHystInjection | 2.1 s | ✗ | — | 0 | no — GT deck set broken (G2) |

**3 of 5 candidates pass → the study grows from 3 to 6 usable tasks, n = 54 → 108**, which
clears the n ≈ 90 needed to resolve ρ = 0.3 at 80 % power (§4.7).

### 7.5 A THIRD METRIC BUG, found by the extension — order-dependent canonicalisation

`AdvancedExampleCasedThermoElasticWellbore` instantiates the **same constitutive type three
times**, once per region: `casingInternalEnergy` / `cementInternalEnergy` /
`rockInternalEnergy` are all `SolidInternalEnergy`; likewise `BiotPorosity`,
`ConstantPermeability`, `SinglePhaseThermalConductivity`, `ElasticIsotropic`,
`PorousElasticIsotropic` — 6 types × 3 instances.

Canonicalising each to its type therefore **collides**, and my first implementation resolved
the collision by "whichever model appeared first in the XML wins, the rest keep their raw
names". That makes the canonical name depend on **XML element order**, which two decks can
legitimately differ in — a genuine order-dependence bug that would have silently mismatched
quantities between reference and generated runs.

**Fix:** when a type has several instances, canonicalise them all to the type and **merge
their sample bags** (`merge_stats`: min→min, max→max, mean and rms combined by bag size).
This is order-independent, deterministic, and additionally removes any dependence on the
deck's *region* naming, which is exactly as arbitrary as the model naming. Ordered
(time-series) bags are never merged.

Regression check: re-running the 3 original tasks after the fix changes **0 of 54** SOF
values — those tasks have no repeated constitutive type, so the fix is inert there and the
§4 results stand unchanged.

### 7.6 Extension grid — 54 runs, and every failure is a genuine deck defect

`J2_scratch/grid.jsonl` (54 records), 4-way concurrency, 600 s cap, SIGKILL retries.

| task | n | produced output | failure stages |
|---|---:|---:|---|
| AdvancedExampleCasedThermoElasticWellbore | 18 | 17 | 1 × run |
| AdvancedExamplePureThermalDiffusionWellbore | 18 | 17 | 1 × run |
| ExamplesingleFracCompression | 18 | 12 | 4 × run, 2 × injection |

Each failure was traced to its cause in `run.log` rather than left as a bare count:

| run | cause |
|---|---|
| CasedThermoElastic `F0_s3` (Vanilla) | `XML parsing error … attribute gravityVector`, input value `'0.0, 0.0, 0.0'` — GEOS requires brace syntax `{0.0,0.0,0.0}`; input-string validation fails |
| PureThermalDiffusion `F6_s2` | `innerPressure (…l.43): this FieldSpecification targets (an) empty set(s)` |
| singleFrac `F4_s1` | `initialStress/objectPath … is a wrong objectPath: ElementRegions/Region/elementSubRegion` (actual children: `0_hexahedra`, `1_hexahedra`) |
| singleFrac `F11_s1`, `F11_s2`, `F4_s3` | `tractionCollection … wrong objectPath: ElementRegions/Fracture/faceElementSubRegion` (actual child: `FractureSubRegion`) |
| singleFrac `F4_s2`, `F8_s1` | injector: **no `<Events>` block anywhere in the `<Included>` closure** |

#### Fairness check on the two `injection` failures — run uninjected, as the agent wrote them
A2's bug 3 was an injector *stricter than GEOS*, which inflated the failure count. So the two
`no_output_inject` decks were re-run **without any injection**, from a clean copy of the
agent's own inputs (plus the gap-filled GT mesh):

```
F4_s2: rc=1, 0 × "Cleaning up events"
       Error cause: child == nullptr — tractionCollection has a wrong objectPath
F8_s1: rc=1, 0 × "Cleaning up events"
       Error cause: wrapper == nullptr — tractionCollection/fieldName: Target not found!
```

**Both fail on their own merits.** Classifying them as `no_output` is therefore correct and
is *not* an artifact of the injector being stricter than the simulator. Recorded because it
is exactly the mistake A2 made and had to retract.

#### Gap-fill worked and is auditable
`crackInPlane_benchmark.vtu` (the 1 MB external mesh) was gap-filled into the 11 of 18
singleFrac run dirs that lacked it, and into none of the 7 that had it —
`gt_assets_filled` is recorded per run. `copy_complete` is true and
`stale_outputs_before_run` empty for **all 54** runs.

---

## 8. SIX-TASK VALIDATION (SUPERSEDED — see §9)

> **WITHDRAWN.** The numbers in this section were computed with a reference/generated
> ASYMMETRY on `AdvancedExampleCasedThermoElasticWellbore` — bug 4, §8.6. They are kept
> verbatim for auditability. **Use §9 for every 6-task number.**

### 8.0 (superseded) the extension CHANGES the headline

**Read this instead of §4.1 for the headline number.** §4 stands as the 3-task result; §8
supersedes it with n = 108. The change is in the direction the §4.7 power analysis predicted:
at n = 54 the study could only resolve |ρ| ≳ 0.38, the observed ρ was 0.29, and the honest
reading was "underpowered". With n = 108 the association resolves.

Executed set: **6 usable tasks × 6 cells × 3 seeds = 108 runs, 91 with output.**

| task | n | produced output |
|---|---:|---:|
| AdvancedExampleCasedThermoElasticWellbore | 18 | 17 |
| AdvancedExamplePureThermalDiffusionWellbore | 18 | 17 |
| AdvancedExampleThermoPoroElasticWellbore | 18 | 14 |
| AdvancedExampleViscoExtendedDruckerPrager | 18 | 17 |
| ExampleProppantTest | 18 | 14 |
| ExamplesingleFracCompression | 18 | 12 |
| **POOLED** | **108** | **91** |

### 8.1 THE HEADLINE

| scope | convention | n | ρ | p | 95 % CI |
|---|---|---:|---:|---:|---|
| CasedThermoElastic | SOF_all | 18 | **0.735** | 0.001 | [0.34, 0.90] |
| PureThermalDiffusion | SOF_all | 18 | **0.503** | 0.034 | [0.14, 0.74] |
| ThermoPoro | SOF_all | 18 | 0.110 | 0.662 | [−0.41, 0.59] |
| DruckerPrager | SOF_all | 18 | 0.109 | 0.666 | [−0.46, 0.60] |
| ProppantTest | SOF_all | 18 | **0.609** | 0.009 | [0.17, 0.90] |
| singleFracCompression | SOF_all | 18 | 0.200 | 0.420 | [−0.32, 0.66] |
| **POOLED (within-task ranks)** | **SOF_all** | **108** | **0.402** | **<0.0001** | **[0.23, 0.55]** |
| POOLED (raw values) | SOF_all | 108 | 0.201 | 0.035 | [0.02, 0.38] |
| **POOLED (within-task ranks)** | **SOF_ran** | **91** | **0.450** | **<0.0001** | **[0.26, 0.61]** |
| POOLED: TreeSim vs `ran` (0/1) | — | 108 | 0.150 | 0.119 | [−0.02, 0.32] |

**Meta-analysis (fixed-effect Fisher-z over the 6 per-task ρ, with heterogeneity test):**

| convention | k | per-task ρ | pooled ρ | 95 % CI | p | Q (df 5) | I² |
|---|---:|---|---:|---|---:|---|---:|
| SOF_all | 6 | +0.73, +0.50, +0.11, +0.11, +0.61, +0.20 | **+0.411** | [+0.22, +0.57] | <0.001 | 8.60, p = 0.126 | 42 % |
| SOF_ran | 6 | +0.83, +0.55, +0.30, +0.13, +0.46, +0.48 | **+0.504** | [+0.31, +0.66] | <0.001 | 8.26, p = 0.142 | 39 % |

**Statement of the result, unsoftened:**

> Across 6 held-out GEOS tasks and 108 generated decks, TreeSim is a **moderate but far from
> sufficient** predictor of simulation-output fidelity. Pooled Spearman **ρ = 0.41
> (95 % CI 0.22–0.57, n = 108, p < 0.001)**; conditional on the deck actually running,
> **ρ = 0.50 (95 % CI 0.31–0.66, n = 91)**. That is ρ² ≈ **0.17–0.25** — TreeSim accounts for
> roughly a sixth to a quarter of the rank variance in how closely the simulation reproduces
> the reference, and leaves three quarters unexplained.

Three things must be said alongside it:

1. **It is a fidelity signal, not a runnability signal.** TreeSim vs the binary "produced
   output" is ρ = 0.150, **p = 0.119 — not significant**. So the association is not the
   trivial one ("bad decks don't run"); it survives, and strengthens, once you condition on
   running.
2. **It is task-dependent.** Per-task ρ spans **0.11 to 0.83**. On 2 of 6 tasks
   (ThermoPoro, DruckerPrager) TreeSim carries essentially no information about output
   fidelity (ρ ≈ 0.11, p ≈ 0.66). The heterogeneity test does not reject consistency
   (Q = 8.60, df 5, p = 0.126) but I² = 42 % means a substantial share of the spread is real,
   not sampling noise. **Do not quote the pooled number without the range.**
3. **The 3-task version of this study said something different**, and it was underpowered
   rather than wrong: ρ = 0.29, CI [0.03, 0.53], p = 0.034, and the conditional analysis was
   non-significant (ρ = 0.22, p = 0.13). Doubling n moved the estimate from "marginal, and it
   disappears conditional on running" to "moderate, and it strengthens conditional on
   running". **This is a direct demonstration that 3 tasks is not enough to answer the AC's
   question, and 6 is close to the floor.**

### 8.2 Robustness of the 6-task headline

- **Leave-one-out jackknife**: ρ = +0.402, range **[+0.387, +0.427]** over all 108 deletions.
  No single run drives it (at 3 tasks the range was [0.255, 0.332]).
- **Dropping TreeSim = 0 points**: n = 107, ρ = **+0.433**, p < 0.001, CI [0.27, 0.58].
- **SIGA cells only** (F0 excluded): n = 90, ρ = **+0.425**, p < 0.001, CI [0.24, 0.59]. The
  association is not an artifact of Vanilla sitting at one end.
- **Continuity with A2** unchanged: ρ(SOF, 1 − A2's worst declared relative error) = **+0.974**.

*Caveat on one CI:* `singleFracCompression` `SOF_ran` reports ρ = 0.482 with a bootstrap CI
[0.483, 0.777] that excludes its own point estimate. That is a degenerate percentile
bootstrap — 10 of its 12 runs with output score exactly 1.0000, so most resamples have no
variance in y and are dropped. Its per-task CI should not be trusted; the permutation p
(0.159) and the meta-analysis (which weights by n − 3, not by the bootstrap) are unaffected.

### 8.3 Per-cell distribution at n = 108 — STILL no separation, and now slightly against SIGA

Mean ± sd of `SOF_all`, n = 3 per (task, cell), n = 18 per cell pooled:

| cell | CasedThE | PureThDiff | ThermoPoro | DruckerP | Proppant | singleFrac | **POOLED (n=18)** |
|---|---|---|---|---|---|---|---|
| F0 Vanilla | 0.534±0.463 | 1.000±0.000 | 0.646±0.560 | 0.922±0.136 | 0.667±0.577 | 1.000±0.000 | **0.795±0.374** |
| F4 X+M | 0.827±0.000 | 1.000±0.000 | 0.941±0.000 | 0.609±0.534 | 0.643±0.558 | 0.000±0.000 | **0.670±0.432** |
| F6 S+X | 0.828±0.000 | 0.667±0.577 | 0.628±0.543 | 0.868±0.117 | 0.665±0.576 | 0.973±0.047 | **0.771±0.363** |
| F8 S+X+M | 0.828±0.000 | 0.844±0.270 | 0.882±0.102 | 0.834±0.163 | 0.666±0.577 | 0.667±0.577 | **0.787±0.315** |
| F11 SE-prose | 0.828±0.000 | 1.000±0.000 | 0.646±0.560 | 0.942±0.101 | 0.999±0.002 | 0.333±0.577 | **0.791±0.371** |
| SE | 0.810±0.030 | 0.844±0.270 | 0.664±0.575 | 0.872±0.112 | 1.000±0.000 | 1.000±0.000 | **0.865±0.252** |

Kruskal–Wallis across the 6 cells: CasedThE p = 0.207, PureThDiff p = 0.778,
ThermoPoro p = 0.945, DruckerPrager p = 0.888, ProppantTest p = 0.241,
singleFrac p = 0.072, **POOLED p = 0.569**.

**SIGA cells (n = 90, mean 0.7769) vs Vanilla F0 (n = 18, mean 0.7948): Δ = −0.018,
Mann–Whitney p = 0.304.** The point estimate now *favours Vanilla*, by an amount far inside
noise.

**Report this loudly.** Doubling the task count did not produce cell separation; it made the
absence sharper. Every cell's within-cell sd (0.25–0.43) dwarfs every between-cell difference
(≤ 0.20 pooled, and 0.018 for the SIGA-vs-Vanilla contrast that matters). This independently
corroborates Thread B's result on its 24 held-out (task, seed) pairs — reached by a
completely different route, on an output-side rather than input-side measurement.

The one task that comes closest to separating (singleFrac, p = 0.072) does so **against**
SIGA: cell F4 (X+M) is 0/3 there, all three seeds failing to load on genuine `objectPath`
defects (§7.6).

**So: TreeSim rank-correlates with output fidelity (§8.1), but the factorial cells do not
differ in output fidelity.** Those are consistent — TreeSim varies far more within a cell
than between cells, so a real TreeSim→fidelity association can coexist with no detectable
cell effect. It does mean the AC's question splits in two, and the two halves have different
answers:
- *"Does structural similarity track simulation similarity?"* → **partly, ρ ≈ 0.41.**
- *"Do SIGA's structural gains translate into better simulations?"* → **not detectably, on
  6 tasks × 6 cells × 3 seeds.**

### 8.4 Known-good / known-bad at n = 108 — unchanged, still separated

The sanity set is unchanged by the extension (all 7 designated runs are on the original 3
tasks): `SOF` good-min 0.9978 vs bad-max 0.7788 (gap **+0.219**);
`SOF_wc` good-min 0.9938 vs bad-max 0.5611 (gap **+0.433**). Both byte-identical-tables
DruckerPrager runs score exactly **1.0000**.

### 8.5 Threshold curve at n = 108 — the ordering still moves with τ

Runs with `SOF_all ≥ τ`, out of 18 per cell:

| τ | F0 | F4 | F6 | F8 | F11 | SE |
|---|---|---|---|---|---|---|
| 0.50 | 15 | 13 | 15 | 16 | 15 | 17 |
| 0.80 | 13 | 13 | 14 | 13 | 15 | 14 |
| 0.90 | **12** | 9 | 10 | 9 | 11 | 11 |
| 0.95 | **11** | 5 | 7 | 7 | 10 | **11** |
| 0.999 | **10** | 5 | 5 | 5 | 8 | 9 |

Vanilla (F0) is *joint best or best* at every τ ≥ 0.90. At τ = 0.50 it is mid-pack. A single
declared tolerance would therefore have picked whichever winner it was set to pick — which is
precisely A2's problem with its 10 % L5 cut, now demonstrated at 6 tasks. Full curve in
`J2_threshold_curve.csv`.

### 8.6 BUG 4 — a reference/generated ASYMMETRY, caught by the per-quantity breakdown

`J2_quantity_rollup.csv` showed two CasedThermoElastic quantities at **mean Ψ = 0.0000 across
all 18 runs** — `cementInternalEnergy_internalEnergy` and `rockInternalEnergy_internalEnergy`
— with a third, `SolidInternalEnergy_internalEnergy`, at 0.0896. A quantity that no run ever
matches is a metric defect, not a physics result.

**Cause.** The extension reference bundles were extracted by `J2_run_task.py` and cached
inside `J2_scratch/ref_gate.jsonl` **before** the merge_stats fix of §7.5; the generated
bundles were written **after** it. `extension_rows()` trusted the cached `quantities`. So on
the one task with repeated constitutive types, the reference kept three separately-named
quantities while every generated run had them merged into one — **reference and generated
went through different canonicalisation code.** Every generated run was then missing 2 of the
reference's 17 live quantities by construction, and scored Ψ = 0 on both.

This is precisely the failure mode the whole design is supposed to exclude ("apply every
exclusion and normalisation identically to reference and generated"). It was caused by
caching, not by the metric definition.

**Fix.** `extension_rows()` now **always re-extracts both the reference and every generated
bundle from the preserved run directory with the current code**, and never trusts the
`quantities` stored in a record. Reference and generated are identical by construction, and
the pipeline is immune to any future change in extraction landing between two passes.

**Effect.** 17 of 108 runs change, all on CasedThermoElastic, all upward
(e.g. `F0_s2` 0.827 → 0.998, `F0_s1` 0.775 → 0.949). The other 5 tasks are bit-identical.
Merging across regions also correctly *promotes* three formerly per-region-constant fields to
live (`ElasticIsotropic_density`, `BiotPorosity_grainBulkModulus`,
`SinglePhaseThermalConductivity_effectiveConductivity`) — casing, cement and rock genuinely
have different densities, so the merged bag varies even though each region's does not.

The bug inflated apparent discrepancy on one task, i.e. it made SIGA and Vanilla alike look
*worse*, and it distorted that task's contribution to the headline. §8 is withdrawn; §9 is
the corrected result.

---

# 9. DEFINITIVE 6-TASK RESULT (post bug-4 fix) — QUOTE THIS SECTION

Data: `J2_per_run.csv` (108 rows), `J2_validation_report.txt`, `J2_correlations.csv`,
`J2_per_cell.csv`, `J2_sanity.csv`, `J2_sensitivity.csv`, `J2_threshold_curve.csv`,
`J2_headline_corrected.txt`, `J2_quantity_rollup.csv`, `J2_bundles.jsonl`.

**Executed set: 6 usable tasks × 6 cells × 3 seeds = 108 runs, 91 with output.**

## 9.1 HEADLINE — does TreeSim predict output similarity?

| scope | conv | n | ρ | p | 95 % CI |
|---|---|---:|---:|---:|---|
| CasedThermoElastic | SOF_all | 18 | **0.735** | 0.001 | [0.34, 0.90] |
| PureThermalDiffusion | SOF_all | 18 | **0.503** | 0.034 | [0.14, 0.74] |
| ThermoPoro | SOF_all | 18 | 0.110 | 0.662 | [−0.41, 0.59] |
| DruckerPrager | SOF_all | 18 | 0.109 | 0.666 | [−0.46, 0.60] |
| ProppantTest | SOF_all | 18 | **0.609** | 0.009 | [0.17, 0.90] |
| singleFracCompression | SOF_all | 18 | 0.200 | 0.420 | [−0.32, 0.66] |
| **POOLED (within-task ranks)** | **SOF_all** | **108** | **0.402** | **<0.0001** | **[0.23, 0.55]** |
| POOLED (raw values) | SOF_all | 108 | 0.303 | 0.001 | [0.12, 0.48] |
| **POOLED (within-task ranks)** | **SOF_ran** | **91** | **0.450** | **<0.0001** | **[0.26, 0.61]** |
| POOLED (raw values) | SOF_ran | 91 | 0.280 | 0.007 | [0.05, 0.51] |
| **POOLED: TreeSim vs `ran` (0/1)** | — | 108 | **0.150** | **0.119** | [−0.02, 0.32] |

**Meta-analysis (fixed-effect Fisher-z over the 6 per-task ρ, with heterogeneity test):**

| conv | k | per-task ρ | pooled ρ | 95 % CI | p | Q (df 5) | I² |
|---|---:|---|---:|---|---:|---|---:|
| SOF_all | 6 | +0.73, +0.50, +0.11, +0.11, +0.61, +0.20 | **+0.411** | [+0.22, +0.57] | 0.0001 | 8.60, p=0.126 | **42 %** |
| SOF_ran | 6 | +0.83, +0.55, +0.30, +0.13, +0.46, +0.48 | **+0.504** | [+0.31, +0.66] | <0.0001 | 8.26, p=0.142 | **39 %** |

### The statement, unsoftened

> Across **6 held-out GEOS tasks and 108 generated decks**, TreeSim is a **moderate but far
> from sufficient** predictor of simulation-output fidelity. Pooled Spearman
> **ρ = 0.41 (95 % CI 0.22 – 0.57, n = 108, p ≈ 1e-4)**; conditional on the deck actually
> running, **ρ = 0.50 (95 % CI 0.31 – 0.66, n = 91)**. That is **ρ² ≈ 0.17 – 0.25** —
> structural similarity of the input deck accounts for roughly **a sixth to a quarter** of
> the rank variance in how closely the simulation reproduces the reference, and leaves
> three quarters unexplained.

Four qualifications that must travel with that number:

1. **It is a fidelity signal, not a runnability signal.** TreeSim vs the binary "produced
   output" is ρ = 0.150, **p = 0.119 — not significant**. The association is therefore *not*
   the trivial "bad decks don't run"; it survives and strengthens once you condition on
   running.
2. **It is strongly task-dependent.** Per-task ρ spans **0.11 → 0.83**. On **2 of 6 tasks**
   (ThermoPoro, DruckerPrager) TreeSim carries essentially no information about output
   fidelity (ρ ≈ 0.11, p ≈ 0.66). Heterogeneity does not reach significance
   (Q = 8.60, df 5, p = 0.126) but **I² = 42 %** — a substantial share of the spread is real.
   **Never quote the pooled ρ without the 0.11–0.83 range.**
3. **The 3-task version of this study said something materially weaker**, and it was
   underpowered rather than wrong: ρ = 0.29, CI [0.03, 0.53], with the conditional analysis
   non-significant (ρ = 0.22, p = 0.13). Doubling n moved it to "moderate, and stronger
   conditional on running". At n = 54 the minimum detectable |ρ| was 0.38 and the estimate was
   0.29 — below its own detection floor. At n = 108 it is 0.27, and 0.40 clears it.
   **3 tasks cannot answer the AC's question; 6 is roughly the floor.**
4. **This is a rank correlation on a calibration study, not a physics benchmark.** 6 tasks,
   1 GEOS build, 1 deterministic run per deck.

## 9.2 Robustness

- **Leave-one-out jackknife**: ρ = +0.402, range **[+0.387, +0.427]** over 108 deletions.
- **Dropping TreeSim = 0 points**: n = 107, ρ = +0.433, p < 0.001.
- **SIGA cells only** (F0 excluded): n = 90, ρ = +0.425, p < 0.001 — not an artifact of
  Vanilla sitting at one end.
- **Continuity with A2**: ρ(SOF, 1 − A2's worst declared relative error) = **+0.974**.
- *Caveat:* `singleFracCompression`'s `SOF_ran` bootstrap CI is degenerate (10 of its 12 runs
  with output score exactly 1.0000, so most resamples have no variance in y). Use its
  permutation p (0.159), not its CI.

## 9.3 Per-cell distribution — NO separation, and the point estimate favours Vanilla

Mean ± sd of `SOF_all`:

| cell | CasedThE | PureThDiff | ThermoPoro | DruckerP | Proppant | singleFrac | **POOLED (n=18)** |
|---|---|---|---|---|---|---|---|
| F0 Vanilla | 0.649±0.563 | 1.000±0.000 | 0.646±0.560 | 0.922±0.136 | 0.667±0.577 | 1.000±0.000 | **0.814±0.379** |
| F4 X+M | 0.998±0.000 | 1.000±0.000 | 0.941±0.000 | 0.609±0.534 | 0.643±0.558 | 0.000±0.000 | **0.699±0.448** |
| F6 S+X | 0.998±0.000 | 0.667±0.577 | 0.628±0.543 | 0.868±0.117 | 0.665±0.576 | 0.973±0.047 | **0.800±0.373** |
| F8 S+X+M | 0.998±0.000 | 0.844±0.270 | 0.882±0.102 | 0.834±0.163 | 0.666±0.577 | 0.667±0.577 | **0.815±0.326** |
| F11 SE-prose | 0.998±0.000 | 1.000±0.000 | 0.646±0.560 | 0.942±0.101 | 0.999±0.002 | 0.333±0.577 | **0.820±0.380** |
| SE | 0.982±0.028 | 0.844±0.270 | 0.664±0.575 | 0.872±0.112 | 1.000±0.000 | 1.000±0.000 | **0.894±0.254** |

Kruskal–Wallis across the 6 cells: CasedThE p = 0.207, PureThDiff p = 0.778,
ThermoPoro p = 0.945, DruckerPrager p = 0.888, Proppant p = 0.241, singleFrac p = 0.072,
**POOLED p = 0.468**.

**SIGA cells (n = 90, mean 0.8054) vs Vanilla F0 (n = 18, mean 0.8140): Δ = −0.0086,
Mann–Whitney p = 0.292.** The point estimate *favours Vanilla*, by an amount far inside noise.

**Report this loudly.** Doubling the task count did not produce cell separation — it made the
absence sharper. Every within-cell sd (0.25–0.45) dwarfs every between-cell difference. This
independently corroborates Thread B, by a different route and on an output-side rather than
input-side measurement. The one task closest to separating (singleFrac, p = 0.072) does so
**against** SIGA: cell F4 (X+M) is 0/3 there, all three seeds failing to load on genuine
`objectPath` defects.

### The AC's question splits in two, and the halves have different answers

- *"Does structural similarity track simulation similarity?"* → **partly. ρ ≈ 0.41 (0.11–0.83
  by task), ρ² ≈ 0.17–0.25.**
- *"Do SIGA's structural gains translate into better simulations?"* → **not detectably.**
  Δ = −0.009, p = 0.29, on 6 tasks × 6 cells × 3 seeds.

These are consistent: TreeSim varies far more *within* a cell than *between* cells, so a real
TreeSim→fidelity association can coexist with no detectable cell effect.

## 9.4 Known-good / known-bad — separated (unchanged; all 7 are on the original 3 tasks)

`SOF` good-min 0.9978 vs bad-max 0.7788 (gap **+0.219**); `SOF_wc` good-min 0.9938 vs
bad-max 0.5611 (gap **+0.433**). Both byte-identical-tables DruckerPrager runs score exactly
**1.0000**; both machine-precision ThermoPoro runs score 0.9978; the L4-clean-but-99.97 %-wrong
`F8_s1` scores 0.7645 (0.3882 under `SOF_wc`).

## 9.5 Threshold curve — the ordering still moves with τ

Runs with `SOF_all ≥ τ`, out of 18 per cell:

| τ | F0 | F4 | F6 | F8 | F11 | SE |
|---|---|---|---|---|---|---|
| 0.50 | 15 | 13 | 15 | 16 | 15 | **17** |
| 0.80 | 14 | 13 | 14 | 13 | **15** | **15** |
| 0.90 | **14** | 12 | 13 | 12 | **14** | **14** |
| 0.95 | 12 | 8 | 10 | 10 | **13** | **13** |
| 0.999 | **10** | 5 | 5 | 5 | 8 | 9 |

Vanilla is joint-best at τ = 0.90 and best at τ = 0.999; SE/F11 lead at 0.95. **A single
declared tolerance picks whichever winner it is set to pick.** Full curve in
`J2_threshold_curve.csv`.

## 9.6 SENSITIVITY — robust to 11 of 13 arms, but NOT to the aggregator

| arm | ρ (SOF_all) | p | ρ (SOF_ran) | p | good_min | bad_max | separated |
|---|---:|---:|---:|---:|---:|---:|---|
| **PRIMARY (declared)** | **0.402** | <0.001 | **0.450** | <0.001 | 0.998 | 0.779 | yes |
| agg_q = geomean | 0.402 | <0.001 | 0.448 | <0.001 | 0.998 | 0.765 | yes |
| scale = range | 0.402 | <0.001 | 0.450 | <0.001 | 0.998 | 0.761 | yes |
| scale = peak_or_range | 0.402 | <0.001 | 0.450 | <0.001 | 0.998 | 0.779 | yes |
| squash = exp(−δ) | 0.402 | <0.001 | 0.450 | <0.001 | 0.998 | 0.826 | yes |
| squash = 1/(1+δ) | 0.402 | <0.001 | 0.450 | <0.001 | 0.998 | 0.853 | yes |
| **no name canonicalisation** | 0.399 | <0.001 | **0.464** | <0.001 | **0.776** | 0.779 | **NO** |
| agg_q = min | 0.380 | <0.001 | 0.422 | <0.001 | 0.961 | 0.616 | yes |
| no quantity exclusions | 0.381 | <0.001 | 0.421 | <0.001 | 0.932 | 0.805 | yes |
| A2 primary scalars only | 0.376 | <0.001 | 0.421 | <0.001 | 1.000 | 0.646 | yes |
| drop \|scale\| < 1e-12 | 0.277 | 0.004 | 0.277 | 0.008 | 1.000 | 0.779 | yes |
| **worst-reduction (agg_ρ = min)** | **0.148** | **0.127** | **0.143** | **0.177** | 0.994 | 0.561 | yes |
| **worst-reduction + geomean_q** | **0.125** | **0.197** | **0.120** | **0.259** | 0.994 | 0.513 | yes |

**ρ spans 0.125 – 0.402 across all 13 arms (median 0.399); 11 of 13 reach p < 0.05.**

Two honest statements, and they pull in opposite directions:

- **The headline is robust to everything about the *normalisation*.** Scale mode (peak /
  range / peak-or-range), squash function (linear / exponential / rational), quantity
  aggregator (mean / geomean / min), quantity set (all live / A2's two scalars / no
  exclusions) — every one of these leaves ρ in **0.28 – 0.40, all p ≤ 0.004**. A reviewer
  cannot move the conclusion by objecting to any of them.
- **It is NOT robust to replacing the mean over reductions with the worst reduction.**
  `agg_ρ = min` drops ρ to **0.148 (p = 0.127)** — the association becomes non-significant.
  Reason: min-over-reductions is dominated by whichever of {min, max, mean, rms} is noisiest,
  which injects variance uncorrelated with TreeSim. It is the *sharper* instrument for
  separating known-good from known-bad (gap +0.433 vs +0.219, §9.4) and the *blunter* one for
  detecting a population-level association. **These are different jobs and the same
  aggregator does not win both.** Declared primary is kept; both are reported for every run
  (`SOF_all` and `SOF_wc_all` columns of `J2_per_run.csv`).

  **This is the single largest analytic sensitivity in the study and it must not be buried.**
  If a reader prefers the worst-case aggregator, the honest reading of this study is
  "no significant association" (ρ = 0.15, p = 0.13).

- **The diagnostic arm is still diagnostic.** Dropping name canonicalisation is the only arm
  that (a) *breaks* known-good/known-bad separation — a machine-precision-exact run scores
  0.776, *below* a 99 %-wrong run at 0.779 — and (b) *raises* the conditional correlation
  (ρ_ran 0.450 → 0.464). Both for the same reason: without canonicalisation the "output"
  metric is partly re-reading the deck's naming choices, which is input-side information
  TreeSim already sees. An output metric that correlates better with TreeSim *because it
  secretly measures naming* is broken; this arm is the proof canonicalisation was necessary.

## 9.7 Power — now adequate for the effect measured, still thin for a smaller one

| target ρ | n needed (80 % power, α = 0.05) | tasks (6 cells × 3 seeds) |
|---|---:|---:|
| 0.2 | 206 | 12 |
| 0.3 | 90 | 5 |
| 0.4 | 50 | 3 |
| 0.5 | 31 | 2 |

At **n = 108 the minimum detectable |ρ| is ≈ 0.27**, and the observed 0.40 clears it — so
unlike the 3-task version, this study *is* adequately powered for the association it reports.
It is **not** powered to (a) resolve ρ ≈ 0.2 (would need ~12 tasks / n ≈ 206), (b) resolve the
per-task heterogeneity (I² = 42 % with k = 6 is under-identified; ~12–15 tasks would be needed
to model it), or (c) detect the SIGA-vs-Vanilla cell contrast, where the observed Δ = −0.009
with pooled sd ≈ 0.37 would need **n ≈ 26 000 per arm** for 80 % power — i.e. that contrast is
not merely unproven, it is unprovable at any realistic scale *if the true effect is this size*.
