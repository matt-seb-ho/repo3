---
name: GEOS thermoelastic XML — Biot=0 trick and HistoryCollection dt forcing
description: Two non-obvious GEOS schema gotchas surfaced while writing CasedThermoElasticWellbore_{base,benchmark,smoke}.xml — forcing Biot coefficient to zero via grain bulk modulus, and forcing event dt for history packs.
type: feedback
---

While authoring `CasedThermoElasticWellbore_base.xml` + `_benchmark.xml` + `_smoke.xml` for a fully-implicit single-phase poromechanics + thermal run on a quarter cased-wellbore, two GEOS-schema details bit me that are worth remembering for any future thermo-poromechanics XML.

## 1. Forcing Biot coefficient = 0 in `BiotPorosity`

The `BiotPorosity` element does **not** expose a direct `biotCoefficient` attribute. The Biot coefficient is computed internally as

    b = 1 - K_drained / K_grain

So to force `b ≡ 0` (which is what you want when you are deliberately decoupling fluid pressure from the solid mechanics — e.g. an "artificially blocked flow" thermoelastic study where you also set permeability to ~1e-100 m²), you must set

    grainBulkModulus = drainedBulkModulus

on every `ElasticIsotropic` solid + its companion `BiotPorosity`. For this case that means using **identical** numbers for casing (1.594202899e11), cement (2.298850575e9), and rock (5.535714286e9) in both the elastic-modulus block and the porosity block. Setting only one side leaves a residual Biot coefficient that quietly contaminates the stress field — and because we initialize stresses to 0 and drive the system purely with a thermal BC, the contamination shows up as a spurious pressure-coupled stress at t>0 that is hard to attribute.

**Why:** GEOS's poromechanics constitutive update is `σ_eff = σ_total - b·p·I`; with `p=0` initial + `p=0` Dirichlet on inner/outer + permeability → 0, you'd think `b` is irrelevant. It isn't, because the effective-stress update is still evaluated on every Newton iterate and any residual `b·∂p` from the linearization couples back into the solid block.

**How to apply:** whenever the user wants a "pure thermoelastic" or "decoupled" run with the poromechanics solver still wired up, always mirror `drainedBulkModulus` into `grainBulkModulus` (or equivalent for the chosen porous-solid model) on every region. Don't try to do it via a `biotCoefficient` attribute — it does not exist on `BiotPorosity`.

## 2. `PeriodicEvent` does not honor the solver's `maxDt` for history packs

For the benchmark case the user asked for 1e4 s history cadence while letting the solver take steps up to 1e3 s. The natural thing is to write

    <PeriodicEvent name="historyCollectionEvent"
                   timeFrequency="1e4"
                   target="/Tasks/temperatureHistoryCollection_casing" />

…and assume the event will fire at exactly t = 1e4, 2e4, …. It does **not** in general — the solver's adaptive dt can land on, say, t = 9750 s, then 10750 s, and the periodic event fires on the *next* step boundary ≥ 10000 s, so your history samples drift off the requested 1e4 grid.

The fix is to add `forceDt="1e4"` (or `targetExactTimestep="1"` depending on GEOS version) on the history `PeriodicEvent` so the event manager actively trims the next solver step to land exactly on the requested cadence. The smoke case doesn't need this because it has no `HistoryCollection` tasks at all and only cares about VTK output every 1e4 s — there a small drift is harmless.

**Why:** `PeriodicEvent` is a *cadence*, not a *deadline*, unless you tell it to be one. The history-collection machinery samples whatever the simulator state is at the firing instant; if firings drift, your CSV's time column is no longer uniformly spaced and post-processing FFTs / convergence tables become annoying.

**How to apply:** any time we collect time histories at a coarser cadence than the solver step, put `forceDt` on the collection event. For VTK / restart events, only force dt if the user explicitly wants exact times — otherwise let the solver pick its natural step and let the event fire on the next boundary.

---

These two together are the "boring but load-bearing" parts of getting the cased-wellbore thermoelastic benchmark to produce a clean, comparable result against the analytical solution. Worth remembering before the next thermoelastic / poro-decoupled XML.
