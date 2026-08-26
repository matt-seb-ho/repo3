# How the 0.958 output-fidelity number is computed

**Question you asked:** "is it RMSE somehow, and how is that mapped to 0.958?"

**Short answer:** it is **not** RMSE, and it is not a normalised error either. It is a
bounded [0,1] **agreement score** called **SOF (Simulation Output Fidelity)**. RMS appears
only as *one of four summary statistics* used to reduce each physical field to a scalar
before comparison. The 0.958 is a **mean SOF over the 91 held-out runs that produced
output** (i.e. conditional on the deck running).

Primary source: `neurips_review/sprint/threads/J2_output_metric.md` §1 (definition, frozen
before any number was computed), §9 (definitive 6-task result).
Scale-up that produced the actual 0.958: `neurips_review/sprint/threads/K3_sof_scaleup.md`,
summarised in `SPRINT_LOG.md` finding F54 and `REBUTTAL_REVISION_BRIEF.md` §5.
Implementation: `neurips_review/sprint/artifacts/J2_metric.py`, `J2_validate.py`.

---

## The pipeline, step by step

### 1. Make the two decks emit the same observables
Generated and reference decks request different output variables, so they are not directly
comparable. An **identical** `<VTK plotLevel=3>` block plus a final-time `PeriodicEvent` is
appended to the reference deck *and* every generated deck. The generated deck's physical
configuration is untouched. Both are then run under GEOS (deterministic on this build —
16/16 statistics identical across repeat runs, so one execution per deck suffices).

### 2. Reduce each run to mesh-independent "bags"
For each output array `A` (cell data / point data), collect its values over all mesh cells
as an unordered multiset. Multi-component arrays are collapsed to per-cell Euclidean
magnitude first. For the one task whose solver writes a fixed scalar table
(`TriaxialDriver`), each column is an ordered bag instead.

### 3. Four reductions per bag
```
ρ ∈ { min, max, mean, rms }        rms(x) = sqrt(mean(x²))
(+ `last` for ordered time-series bags only)
```
**This is where RMS enters.** It is deliberately RMS and not the raw ℓ² norm, because ℓ²
scales like √n and would make a "mesh-independent" metric silently mesh-dependent (one run
uses a 16-cell mesh against a 40-cell reference). No interpolation is performed anywhere.

### 4. Reference-defined comparison basis
- **Live quantity set** `Q_t` = quantities that actually *vary* in the reference
  (`max − min > 0`, with a `CONST_RTOL = 1e-9` cut so round-off does not count as variation).
  Determined **from the reference alone**, so it is byte-identical for every cell and seed.
- **Per-quantity scale** `S_q = max(|min(R_q)|, |max(R_q)|)` — one scale per quantity, shared
  across its four reductions, so a near-zero mean cannot blow up the ratio. This is what makes
  the score dimensionless and comparable across quantities and tasks.
- Bookkeeping arrays (`ghostRank`, `*dofIndex`, `elementCenter`, …), solver diagnostics
  (`newton_iter`, `residual_norm`), and the independent variable `time` are excluded — all
  by rules evaluated on the reference only.
- Constitutive-model array names are canonicalised `<modelName>_<field>` → `<ModelType>_<field>`
  so the metric does not secretly score the deck's *naming* choices (see §3.3 of J2 — this was
  a real bug: a machine-precision-exact run scored 0.776 purely for calling the fluid `water`
  instead of `fluid`).

### 5. Deviation → fidelity → mean
```
δ(q,ρ) = |ρ(G_q) − ρ(R_q)| / S_q      (+∞ if the quantity is missing from the generated run)
ψ(q,ρ) = clip(1 − δ(q,ρ), 0, 1)
Ψ(q)   = mean over the four reductions ρ
SOF    = mean over q ∈ Q_t of Ψ(q)                     ← the reported scalar
```

So: **ψ = 1 − (relative deviation, measured against the reference quantity's own magnitude),
clipped to [0,1].** `ψ = 1` is exact reproduction; `ψ = 0` means that reduction is off by at
least 100% of the reference's own scale. Missing quantities score 0, so coverage is inside
the metric rather than a separate caveat.

### 6. Two reported conventions
| convention | non-executing runs | this is the number |
|---|---|---|
| `SOF_all` | scored **0** (the paper's failures-as-zero rule) | held-out mean **0.692**, 33.3% ≥ 0.999 |
| `SOF_ran` | **excluded** (conditional on producing output) | held-out mean **0.958**, **46.2%** ≥ 0.999 |

**`0.958` = held-out `SOF_ran` mean, n = 91 running runs out of 126 held-out runs
(27.8% produced no output).** The val split gives 0.913 / 65.5%, but val is contested on
both axes (asset-staging confound + a scoring race) and should not be quoted.

---

## Things you should know before this number goes on OpenReview

1. **0.958 is pooled across all six cells, not a SIGA number.** Cell separation on SOF is
   **not detectable on any split**, and the held-out point estimate slightly favours Vanilla
   (Δ = −0.0073, Mann–Whitney p = 0.409; ~56,000 runs per arm would be needed for 80% power).
   Four independent threads (B, D, J2, K3) reached this. The claim 0.958 supports is
   *"decks that run are usually physically right, so the gap is in runnability"* — it is
   **not** evidence that SIGA improves physics. The current top-half AC text overstates this
   (see `FACT_CHECK.md` F1).
2. **46% ≥ 0.999 is not "46% match exactly"** — it is 46% of *running* decks, at the ≥0.999
   threshold on this bounded agreement score.
3. **The companion ρ = 0.362 is aggregator-dependent.** Under the worst-reduction aggregator
   (`min` over the four reductions instead of `mean`) the held-out correlation drops to
   **ρ = 0.121, p = 0.176 — not significant**. The sprint's own standing instruction
   (finding H31) is *"any use of ρ must report both aggregators."* Neither draft half does.
   0.958 itself is *not* affected by this — it is a mean, not a correlation.
4. **ρ = 0.362 supersedes J2's ρ = 0.402.** Do not cite 0.402; it was the n = 108 estimate and
   came down with power (n = 489 pooled → 0.310; held-out n = 126 → 0.362).

## Suggested one-line protocol gloss for the rebuttal
> We append an identical output block to the generated and reference decks, run both, and for
> every physical quantity that varies in the reference we compare four mesh-independent
> summaries (min, max, mean, RMS), each normalised by that quantity's own reference scale.
> Fidelity is one minus that normalised deviation, clipped to [0,1] and averaged over
> quantities; no interpolation is used anywhere.
