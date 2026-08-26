# Thread A2 — GEOS execution ladder rungs 4–5

**Owner:** Thread A2 (autonomous sprint, NeurIPS 2026 sub 31642 SIGA)
**Started:** 2026-07-26 22:00 local
**Scope:** rungs 4 (full run / converged) and 5 (QoI comparability). Thread A1 owns rungs 1–3.
**Scratch dir:** `/home/matt/sci/repo3/neurips_review/sprint/artifacts/A2_scratch`
**Artifacts prefix:** `neurips_review/sprint/artifacts/A2_*`

---

## 1. Environment gate — PASSED

```bash
export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH
/data/jixuan/geophysics/GEOS/install-your-platform-release/bin/geosx --help
```
Runs clean (prints usage + Umpire memory table, exits after "No XML input file nor schema specified").

**Binary provenance:**
- Path: `/data/jixuan/geophysics/GEOS/install-your-platform-release/bin/geosx`
- mtime of binaries in that dir: **Jan 14 2026**; install dir mtime Jan 15 2026.
- Owner `jixuan` — treated read-only throughout.

**Schema element count** (`geosx -s binary_schema.xml`, then count `<xsd:element name=...>`):
- binary-generated schema: **391 element decls / 263 unique names**
- repo XSD (`data/GEOS/src/coreComponents/schema/schema.xsd`): **401 decls / 269 unique**
- Confirms the documented 263 vs 269 gap (binary is a strict-subset older build).

```bash
cd $SCRATCH && geosx -s binary_schema.xml
python3 -c "import re; s=open('binary_schema.xml').read(); els=re.findall(r'<xsd:element name=\"([A-Za-z0-9_]+)\"',s); print(len(els), len(set(els)))"
```

---

## 2. Task selection by rule — and a convention discovery

**Data source:** `/data/shared/geophysics_agent_data/data/eval/autocamp_followup_2026-05-02/_results_icl/<CELL>_icl_s<N>/autocamp_<CELL>/*_eval.json`
Six held-out cells present: **F0 (Vanilla), F4 (X+M), F6 (S+X), F8, F11, SE**. 10 held-out tasks × 6 cells × 3 seeds = 180 (cell,seed,task) points.

### 2.1 First pass gave the WRONG answer — and that led to a real finding

Averaging only *scored* runs, `ExampleProppantTest` had spread **0.027** (F0 0.811 → SE 0.825), nowhere near the spec's expected 0.541 → 0.825. Investigating: only **179** eval JSONs exist, not 180. `F0_icl_s3` has `n_scored: 9, n_failed: 1, failed_names: ["ExampleProppantTest"]`.

The task summaries carry **two** means: `scored_mean` and `with_failures_as_zero_mean`. The paper's convention is **failures-as-zero** (consistent with its catastrophic-failure/σ reliability framing). Under that convention F0's ProppantTest mean = (0.8065 + 0.8165 + 0)/3 = **0.5410** — reproducing the spec's expected 0.541 exactly.

**Decision: use `with_failures_as_zero` — the paper's own convention.** Rationale: (a) it is what the eval harness itself reports as the headline mean, (b) it reproduces the documented Table-1-era numbers, (c) dropping failures would *hide* exactly the catastrophic failures the paper claims to fix. Both conventions are saved in the artifacts so either can be re-derived.

### 2.2 Why that one run failed — a quotable Vanilla failure mode

```bash
xmllint --noout /data/shared/.../icl/autocamp_F0/F0_icl_s3/ExampleProppantTest/inputs/ProppantSlotTest_base.xml
# ProppantSlotTest_base.xml:4: parser error : Double hyphen within comment
#   Proppant Slot Test -- Base Case
```
Vanilla (F0), seed 3, wrote `--` **inside an XML comment**, which is illegal XML. Both of its decks (`_base` and `_benchmark`) are affected. This deck is an **L0 failure — not well-formed XML** — the strongest possible version of the paper's reliability claim, and it requires no simulator at all to demonstrate. (Rung 1 is Thread A1's, but this is the reason my selection differs, so it is recorded here.)

### 2.3 Spread table (failures-as-zero cell means)

| task | F0 | F4 | F6 | F8 | F11 | SE | spread | min |
|---|---|---|---|---|---|---|---|---|
| AdvancedExampleThermoPoroElasticWellbore | 0.355 | 0.680 | 0.681 | 0.708 | 0.743 | 0.761 | **0.4060** | 0.355 |
| ExampleProppantTest | 0.541 | 0.810 | 0.809 | 0.799 | 0.817 | 0.825 | **0.2843** | 0.541 |
| AdvancedExampleCasedThermoElasticWellbore | 0.847 | 0.807 | 0.923 | 0.919 | 0.877 | 0.886 | 0.1165 | 0.807 |
| ExampleVerticalPoroElastoPlasticWellbore | 0.909 | 0.903 | 0.906 | 0.891 | 0.834 | 0.944 | 0.1100 | 0.834 |
| AdvancedExamplePureThermalDiffusionWellbore | 0.963 | 0.922 | 0.956 | 0.947 | 0.864 | 0.880 | 0.0984 | 0.864 |
| ExampleIsothermalHystInjection | 0.755 | 0.747 | 0.751 | 0.750 | 0.769 | 0.717 | 0.0524 | 0.717 |
| ExamplesingleFracCompression | 0.891 | 0.887 | 0.904 | 0.931 | 0.929 | 0.928 | 0.0444 | 0.887 |
| AdvancedExampleViscoExtendedDruckerPrager | 0.986 | 0.991 | 0.963 | 0.964 | 0.999 | 0.996 | 0.0368 | 0.963 |
| ExampleMCCWellbore | 0.935 | 0.924 | 0.908 | 0.905 | 0.905 | 0.941 | 0.0362 | 0.905 |
| TutorialHydraulicFractureWithAdvancedXML | 0.013 | 0.013 | 0.013 | 0.013 | 0.013 | 0.013 | 0.0004 | 0.013 |

**Rule output — matches the spec's expectation:**
- Case study 1: **AdvancedExampleThermoPoroElasticWellbore** (0.355 → 0.761, spread 0.406)
- Case study 2: **ExampleProppantTest** (0.541 → 0.825, spread 0.284)
- Excluded per rule: `TutorialHydraulicFractureWithAdvancedXML` (0.013 everywhere — universal model-level failure)
- Ceiling control: `min cell mean ≥ 0.90` threshold (declared before looking at run outcomes) leaves two near-tied candidates: **ExampleMCCWellbore** (spread 0.0362, floor 0.905) and **AdvancedExampleViscoExtendedDruckerPrager** (spread 0.0368, floor 0.963). Spreads differ by 0.0006 — a meaningless margin. Decision: **gate both**, run both if affordable; this removes an arbitrary tiebreak.

Scripts: `A2_scratch/select_tasks2.py`. Artifacts: `A2_treesim_heldout_raw.csv` (180 rows, per-seed, with `scored` flag + source path), `A2_treesim_task_cell_means.csv`.

---

## 3. Smoketest (reference ThermoPoro `_smoke.xml`) — PASSED

```bash
export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH
cd $S/runs/REF_ThermoPoro_smoke   # copy of experiments_gt/.../inputs/*.xml
/usr/bin/time -f "VALIDATE_WALL=%e" geosx -v -i ThermoPoroElasticWellbore_smoke.xml   # exit 0, 5.13 s
/usr/bin/time -f "RUN_WALL=%e" timeout 600 geosx -i ThermoPoroElasticWellbore_smoke.xml # exit 0, 7.93 s
```
- **7.93 s wall** — matches the reported ~8.9 s baseline.
- Artifacts emitted: `pressureHistory_rock.hdf5`, `temperatureHistory_rock.hdf5`, `stressHistory_rock.hdf5`, `displacementHistory.hdf5`, `vtkOutput/` + `.pvd`, 3 restart dirs.
- **Implication for scope:** at ~8 s/run, the full grid (4 tasks × 6 cells × 3 seeds + 4 refs = 76 runs) is affordable *if* the other tasks are comparably cheap at their native horizon. Benchmark horizons are much longer (ThermoPoro benchmark `maxTime=3700` vs smoke `maxTime=12`), so the smoke variant is the right unit where it exists on both sides.

### Deck-file symmetry survey (checked before any run)
For all 4 candidate tasks, generated deck **filenames match GT exactly in all 18 cell-seeds** — no missing or extra XML. Notably `ThermoPoroElasticWellbore_smoke.xml` exists on **both** sides in all 18, so using the smoke variant there is symmetric, not a favour to either condition.

`ExampleProppantTest`, `ExampleMCCWellbore`, `AdvancedExampleViscoExtendedDruckerPrager` have **no smoke variant** in GT → their `_benchmark` (resp. `triaxialDriver_*`) deck is the run unit.

---

## 4. Thresholds — DECLARED BEFORE LOOKING AT ANY GENERATED RESULT

**Wall-clock cap: 600 s (10 min) per run**, enforced with `timeout 600`, applied identically to reference and generated decks. A timeout is recorded as an **L3 failure**.

Log markers were derived from the reference smoke run and `data/GEOS/src/coreComponents/events/EventManager.cpp:235`:

| Level | Operational definition (identical for ref and generated) |
|---|---|
| L0 | top-level deck file exists and `xmllint --noout` passes (well-formed) |
| L1 | `xmllint --schema data/GEOS/src/coreComponents/schema/schema.xsd` passes |
| L2 | `geosx -v -i <deck>` exits 0 |
| L3 | full run exits 0 **AND** log contains `Cleaning up events` (EventManager's post-event-loop marker — proves time-stepping finished, not merely a clean exit) |
| L4 | L3 **AND** total `Time step cuts` across all SolverStatistics tables == 0 **AND** no `Convergence not achieved` **AND** no `Attempt:  [1-9]` (every step succeeded on attempt 0) **AND** no `Line search failed` **AND** no `Solution check failed` |
| L5 | L4 on both reference and generated **AND** the standardized scalar QoI extracts from both **AND** relative error on the primary scalar ≤ **0.10** |

The 0.10 L5 tolerance is arbitrary but declared up front; raw relative errors are reported so any other tolerance can be applied post hoc.

**`maxTime` policy:** no `maxTime` edits unless a deck exceeds the 600 s cap. If reduction becomes necessary it is applied to reference and generated identically and logged here. Using the GT-supplied `_smoke.xml` for ThermoPoro is *not* an asymmetric reduction — that file ships in GT and was reproduced by every cell.

---

## 5. Reference-deck gate — results

Run with `ladder.py --label REF`, decks copied from `experiments_gt/<task>/inputs/` into scratch (`/data/shared` is read-only).

| task | run unit | L0 | L1 | L2 | L3 | L4 | wall | timesteps | cuts | retries | native outputs |
|---|---|:--:|:--:|:--:|:--:|:--:|---:|---:|---:|---:|---|
| AdvancedExampleThermoPoroElasticWellbore | `_smoke.xml` | ✓ | ✓ | ✓ | ✓ | **✓** | 5.6 s | 2 | 0 | 0 | 4× TimeHistory hdf5 + vtkOutput |
| ExampleProppantTest | `_benchmark.xml` | ✓ | ✓ | ✓ | ✓ | **✗** | 86.0 s | 314 | 0 | **10** | Silo + Restart only (no hdf5, no VTK) |

### Finding R1 — the ProppantTest *reference* deck does not converge cleanly

`ExampleProppantTest`'s own GT deck runs to completion (L3 ✓) but takes **10 retried timesteps**:
```
New dt = 0.05
  Attempt:  1, ConfigurationIter:  0, NewtonIter:  0
  ... NewtonIter: 7  ( Rproppant ) = ( 1.31e-05 )   <- Newton stalls, no convergence
New dt = 0.025
  Attempt:  2, ConfigurationIter:  0, NewtonIter:  0
```
Note the per-solver `Time step cuts` counter reads **0** while the run demonstrably cut dt twice at that step — the counter belongs to the `ProppantTransport` sub-solver, and the cut happens at the coupled/parent level. My declared `Attempt: [1-9]` criterion caught what the counter missed; the counter alone would have produced a **false L4 pass**. Keeping both criteria.

**Consequence, stated per the spec's gate rule:** `ExampleProppantTest` is **not usable for an absolute L4 criterion** — the reference itself fails it, so "generated deck fails L4" carries no information there. It remains fully usable for **L0–L3** and for **L5 QoI** (it reaches final time and produces a comparable state), and for a *relative* convergence comparison (retry count vs the reference's 10). This is reported, not worked around.

### Finding R2 — ProppantTest's reference emits no scalar time series at all
Its `<Outputs>` block is `Silo` + `Restart` only. There is no `TimeHistory`/HDF5 and no VTK. So QoI preference (b) "use the VTK the decks already write" is **not available** for this task — which is exactly why preference (a), injecting an identical observable, is the right primary method rather than a fallback.

### Finding R3 — a shared non-deck data dependency
`AdvancedExampleViscoExtendedDruckerPrager`'s `triaxialDriver_base.xml` reads `tables/time.geos`, `tables/axialStrain.geos`, `tables/radialStress.geos` via `TableFunction`. These are **data files, not deck XML**, and were never part of the agent's authoring task (no cell produced them). The runner copies GT `tables/` into **every** run directory, reference and generated identically (`ladder.py: tables_injected`). Logged as a normalization step.

---

## 6. Rung-5 QoI method — preference (a), the injected standardized observable

**Method used: (a) identical injected observable.** `inject_qoi.py` appends to *every* deck set — reference and generated alike:
```xml
<Outputs>  <VTK name="a2vtk" plotLevel="3" plotFileRoot="a2qoi"/>  </Outputs>
<Events>   <PeriodicEvent name="a2vtkFinal" timeFrequency="<maxTime>"
                          targetExactTimestep="0" target="/Outputs/a2vtk"/>  </Events>
```
Design choices and why:
- **`<VTK>`, not `<TimeHistory>`.** A `TimeHistory`/`PackCollection` target needs deck-specific region and field names, so it would fail to attach whenever a generated deck renamed a region — turning a *metric* problem into a *coverage* problem. `<VTK>` needs no names, so injection is deck-agnostic and the observable is genuinely identical across conditions.
- **Injection follows the `<Included>` closure from the top deck**, so running `_smoke.xml` cannot accidentally pick up `_benchmark.xml`'s `Events` block. (First implementation had exactly that bug: it read `maxTime=3700` from the benchmark while running the smoke deck. Fixed and re-verified.)
- `outputDir` is **not** a valid `<VTK>` attribute in this binary — used `plotFileRoot`. (First attempt aborted in `Group::processInputFileRecursive`.)
- **Injection failure is a recorded QoI failure mode**, not missing data (`qoi_fail_stage: injection`). A deck with the illegal `--` comment cannot be parsed by the injector, which is the correct outcome.

**Then: mesh-independent reductions, never point-wise fields.** `vtu_stats.py` reads the final VTK snapshot and reduces each field to `min / max / mean / L2 / n_cells`. Meshes differ freely between decks; no interpolation is performed anywhere. VTU inline binary is zlib-block encoded, so the reader decodes it directly (no `vtk`/`meshio` on this box) and **cross-checks every min/max against VTK's independently written `RangeMin`/`RangeMax` attributes** — they agree exactly, which validates the decoder.

Verified on the reference ThermoPoro deck (wall 9.9 s with injection vs 5.6 s without):
`CellData:pressure` max = **3.048330e6**, mean = 3.084569e5; `CellData:temperature` max = **2.701474**, mean = 2.717057e-1; 40 cells, region `rock`.

---

## 7. CONTAMINATION INCIDENT — v1 results discarded, methodology fixed

**This is the most important methodological event in the thread. Read before trusting any A2 number.**

The first ladder pass and first QoI pass were run at 6-way concurrency on a box whose load average was already 150–185 (sibling sprint threads). An audit of return codes found:

| pass | signalled runs (`rc = -9`, SIGKILL) |
|---|---|
| ref gate v1 | `ExampleMCCWellbore` (run), `AdvancedExampleViscoExtendedDruckerPrager` (validate) |
| ladder grid v1 | `SE_s2`, `SE_s3` on `ExampleProppantTest` |
| QoI grid v1 | **all 19** `ExampleProppantTest` runs, plus `SE_s1`/`SE_s3` ThermoPoro |

`rc = -9` accompanied by `ORTE_ERROR_LOG: Broken pipe in orted_main.c` is an **external kill**, not a deck defect. Proof: `AdvancedExampleViscoExtendedDruckerPrager`'s reference deck was scored **L2 fail** in v1 and, re-run serially with no other change, reaches **L2 ✓ L3 ✓ in 5.15 s**.

Had this gone unnoticed it would have produced a fabricated "SE fails to run" result — the exact direction that would have damaged the paper, invented by my own scheduling.

### Fixes applied, then everything re-run from scratch
1. **`sh(..., retry_on_kill=True)`** in `ladder.py` / `qoi_pass.py`: a signalled run is retried up to 2× with backoff before being scored. Applied **identically** to reference and generated decks.
2. **Concurrency reduced** from 6 to 4; reference gate re-run **serially**.
3. v1 artifacts retained as `.v1_*_contaminated.jsonl` — not deleted, so the incident is auditable.

### Separate, genuine bug the audit exposed: the injected observable killed every Proppant run
All 19 Proppant QoI runs died at `Time: 0.00e+00 s, Cycle: 0`, wall ≈12 s, MAXRSS small — i.e. exactly at the **t = 0 VTK write**. Cause: `ExampleProppantTest` uses a `SurfaceGenerator`, so its `Fracture` region is still empty at t = 0 and the plot-level-3 write over it aborts. Not concurrency, and not deck-dependent (the reference did it too).

**Fix:** write the observable at the **final time only** — `beginTime="<maxTime>"` instead of `timeFrequency="<maxTime>"`, dropping the t = 0 write. Rung 5 only ever needed the final state. Verified on the Proppant reference: runs to completion, **75.9 s, MAXRSS 243 MB**, emits `a2qoi/000310`. Applied identically everywhere.

### Threshold amendment (decided from a REFERENCE run, not from generated results)
`AdvancedExampleViscoExtendedDruckerPrager` is a `TriaxialDriver` task: it has **no `Events` block and no time stepping**, so no `SolverStatistics` table is printed and `Time step cuts` is *undefined* rather than 0. The original L4 rule `cuts == 0` therefore failed it for having no timestepping to diverge in.

Amended: `cuts in (0, None)` — absence of a timestepping solver is not evidence of divergence. The amendment was decided from the **reference** deck's behaviour before any generated DP deck was scored, and applies identically to both sides. Recorded here rather than silently patched.

---

## 8. Reference-deck gate v2 (serial, with SIGKILL retries) — the authoritative gate

| task | run unit | L0 | L1 | L2 | L3 | L4 | wall | steps | retries | native outputs | **usable for rungs 4–5?** |
|---|---|:--:|:--:|:--:|:--:|:--:|---:|---:|---:|---|---|
| AdvancedExampleThermoPoroElasticWellbore | `_smoke.xml` | ✓ | ✓ | ✓ | ✓ | **✓** | 19.1 s | 2 | 0 | 4× TimeHistory hdf5 + vtkOutput | **yes — fully** |
| ExampleProppantTest | `_benchmark.xml` | ✓ | ✓ | ✓ | ✓ | **✗** | 78.7 s | 314 | **10** | Silo + Restart only | **L0–L3 and L5 yes; absolute L4 no** |
| AdvancedExampleViscoExtendedDruckerPrager | `triaxialDriver_Visco….xml` | ✓ | ✓ | ✓ | ✓ | **✓** | 10.1 s | n/a | 0 | `ViscoExtendedDruckerPragerResults.txt` | **yes — ceiling control** |
| ExampleMCCWellbore | `_benchmark.xml` | ✓ | ✓ | ✓ | *pending / expensive* | | ≥341 s | | | Silo | deprioritized (see below) |

ProppantTest's 10 retries **reproduced exactly** between v1 (concurrent) and v2 (serial) — so unlike the MCC/DP kills, that is a genuine property of the reference deck, not an artifact.

### Ceiling-control decision — made by the reference gate, not by convenience
§2.3 left two near-tied ceiling candidates (`ExampleMCCWellbore` spread 0.0362, `AdvancedExampleViscoExtendedDruckerPrager` spread 0.0368 — a 0.0006 margin). The reference gate breaks the tie on evidence:
- **DruckerPrager**: reference reaches **L4 clean in 10 s**. → adopted as the ceiling control.
- **MCCWellbore**: reference needs ≥341 s and had not demonstrated L3 at the time of selection; 200 forced timesteps × 3200-element mesh × Silo dump per step, ×19 runs, is the most expensive item in the study by a wide margin.

This is disclosable and, importantly, was decided **only from reference-deck behaviour** — no generated MCC deck was scored and then dropped.

---

## 9. Cross-check against Thread D and Thread A1 — both warnings verified

### Thread D's warning: "failed runs have no `*_eval.json`; glob-based selection is biased"
**Already handled, and independently verified.** My first pass (§2.1) did glob `*_eval.json`, produced the wrong ProppantTest spread (0.027), and I traced the discrepancy to the missing file before selecting any task. `select_tasks2.py` reads `_summary.json` → `summary.failed_names` and enters `treesim = 0.0, scored = 0` for failures. Confirmed at `select_tasks2.py:6-14`.

Verification against D's two reference points:

| cell | my mean (failures-as-zero) | Thread D | Δ | my σ (pstdev) | D σ | ratio |
|---|---:|---:|---:|---:|---:|---:|
| F0 Vanilla | 0.7196 | 0.7196 | 0.0000 | 0.0661 | 0.0809 | ×1.2247 |
| F4 X+M | 0.7683 | 0.7683 | 0.0000 | 0.0044 | 0.0054 | ×1.2247 |
| F6 S+X | 0.7814 | 0.7814 | 0.0000 | 0.0015 | 0.0018 | ×1.2247 |
| F8 S+X+M | 0.7827 | 0.7827 | 0.0000 | 0.0176 | 0.0215 | ×1.2247 |
| F11 SE-prose | 0.7749 | 0.7749 | 0.0000 | 0.0198 | 0.0242 | ×1.2247 |
| SE | 0.7891 | 0.7891 | 0.0000 | 0.0101 | 0.0123 | ×1.2247 |

Means agree to 4 dp. The σ discrepancy is entirely `pstdev` vs `stdev`: √(3/2) = 1.2247 exactly, in all six cells. **No correction needed; nothing to re-derive.** (Reporting D's sample-σ convention going forward.)

Cell identities adopted from D: **F8 = S+X+M**, **F11 = SE-prose**. Labels updated in `analyze.py` / `figures.py`.

I also independently reproduce D's "exactly one zero-score held-out run": F0/s3 `ExampleProppantTest`, malformed at line 4 of `ProppantSlotTest_base.xml` (D reports column 21 "invalid token"; `xmllint` reports it as `Double hyphen within comment` at the same line — same defect).

### Thread A1's warning: "the scorer silently drops unparseable decks; don't equate schema-valid with runnable"
**Verified, and A2 finds a sharper version of it.** My ladder works from files on disk and requires **every** XML in the deck set to be well-formed for L0, so it is not affected. Two results fall out:

**(a) A run that is schema-valid at the top level but cannot run at all.**
`F0_s3 AdvancedExampleThermoPoroElasticWellbore`: **L0 = FAIL, L1 = PASS, L2 = FAIL.** Its top deck `_smoke.xml` is well-formed *and* schema-valid — but both files it `<Included>`s are malformed:
```
ThermoPoroElasticWellbore_base.xml:76:      Double hyphen within comment
ThermoPoroElasticWellbore_benchmark.xml:11: Comment must not contain '--'
```
The scorer scored this run (TreeSim 0.0582) because it parsed what it could; GEOS rejects it outright. **Validating only the top-level deck over-reports runnability.** This is exactly A1's mechanism, observed at the binary.

**(b) Schema validity over-counts GEOS acceptance in every condition.**
6 of the case-study runs are `L1 PASS, L2 FAIL` — `F0_s3`, `F6_s1`, `F11_s2`, `SE_s3` (ThermoPoro) and `F0_s1`, `F4_s1` (Proppant). So the gap between "xmllint accepts" and "GEOS accepts" is real for SIGA cells too, not a Vanilla-only artifact. Worth stating in the rebuttal: rung 2 is a genuinely weaker bar than rung 3.

### Finding: Vanilla's characteristic failure mode is a single defect class
Malformed-XML runs among the case-study grid, by cell:

| cell | malformed / runs |
|---|---|
| **F0 Vanilla** | **3 / 6** |
| F4 X+M | 0 / 6 |
| F6 S+X | 0 / 6 |
| F8 S+X+M | 0 / 5 |
| F11 SE-prose | 0 / 3 |
| SE | 0 / 3 |

All three Vanilla failures are the **same defect: `--` inside an XML comment** (F0_s1 ThermoPoro `_smoke.xml:71`, F0_s3 ThermoPoro `_base.xml:76`, F0_s3 Proppant `_base.xml:4`). Zero occurrences in any SIGA cell. This is a concrete, mechanism-level account of the reliability claim that needs no simulator to verify — and it is the kind of defect a `xmllint` stop-hook catches by construction.

---

## 10. Determinism check — the "one run per deck" assumption, verified not assumed

The plan asserts GEOS determinism to justify no repeats. I measured it: two independent runs of the *identical* reference ThermoPoro deck, separate directories, separate processes, under different machine load.

```bash
python3 qoi_pass.py --label DETCHECK --task AdvancedExampleThermoPoroElasticWellbore \
  --src ref/AdvancedExampleThermoPoroElasticWellbore --rundir detcheck
```

**All 16 statistics across 4 fields are bitwise identical** (`min/max/mean/L2` × `pressure`, `temperature`, `averageStress`, `totalDisplacement`) — e.g. peak pressure `3048330.4338683877` in both runs, to the last digit.

So the input→output map really is a function on this build, and **one execution per deck is sufficient**; the 3 seeds here are *agent* seeds (different decks), never simulator repeats. This converts a rhetorical claim in §4.2 of the execution plan into a measured one. Artifact: `A2_scratch/detcheck.json`.

---

## 11. Ceiling control (DruckerPrager) — the control WORKS, and it nuances the story

This is the load-bearing control: all six cells score TreeSim **0.963–0.999** here, i.e. TreeSim says the decks are equivalent. If everything ran regardless, execution outcomes would be identical.

**They are not.** 3 of 18 runs fail L2, and — importantly — **Vanilla is 3/3 clean** while two SIGA cells are not:

| cell | L2 | note |
|---|---|---|
| F0 Vanilla | 3/3 | — |
| F4 X+M | 1/3 | `F4_s1`, `F4_s2` fail |
| F6 S+X | 3/3 | — |
| F8 S+X+M | 2/3 | `F8_s1` fails |

### The three failures are two different things — do not merge them

**(a) `F4_s1` — a genuine semantic defect that both TreeSim and `xmllint` miss.**
```
ElasticIsotropic.cpp:97  Error cause: numConstantsSpecified != 2
Rank 0: ElasticIsotropic dummy (triaxialDriver_base.xml, l.13): A specific pair of
elastic constants is required. Either (K,G), (K,E), (G,E), (K,nu), (G,nu) or (E,nu).
You have specified ( )
```
The deck declares an elastic material and specifies **no elastic constants at all**. Every attribute is optional in the XSD, so it is **schema-valid**; TreeSim's attribute matching sees missing attributes as a small score deduction. Only the solver knows the pair is mandatory. At TreeSim ≈ 0.99 this deck cannot even be loaded. **This is the single best concrete example in the whole study of what an execution check buys over a structural metric** — and it argues for the AC's point, not against it.

**(b) `F4_s2`, `F8_s1` — a normalization-boundary artifact, partly mine. Disclose it.**
```
XML parsing error at node named TableFunction, attribute voxelFile (triaxialDriver_base.xml, l.104)
Input value: 'tables/zeroStrain.geos'   ->  File does not exist.
```
Both reference a data table `tables/zeroStrain.geos`. GT's `tables/` contains only `time.geos`, `axialStrain.geos`, `radialStress.geos`. Per §5/R3 I inject **GT's** table set identically into every run — so a deck that (not unreasonably) invents a different table filename cannot run under my normalization, and the agent was **never asked to author `.geos` table files** in the first place.

I am not counting this as equivalent to (a). Report the ceiling control **both ways**:
- **strict:** 15/18 reach L2 (3 failures)
- **excluding the table-file artifact:** 17/18 reach L2 (1 genuine failure, `F4_s1`)

### What the ceiling control establishes
1. **"Everything runs regardless" is false** — so the control is informative rather than vacuous.
2. **High TreeSim does not guarantee runnability.** A 0.99-similar deck can fail to load.
3. **TreeSim ordering does not determine execution ordering at the ceiling.** Vanilla is perfect here and two SIGA cells are not. Any claim that TreeSim gains "translate into" execution gains must be restricted to the **low-TreeSim / catastrophic-failure regime**, which is exactly where the paper's held-out gain actually lives (§2.3). State that limit explicitly rather than letting a reviewer find it.

---

## 12. THREE HARNESS BUGS FOUND BY THREAD A1 — all mine, all biased toward our own claim

Thread A1 diffed all 54 overlapping runs: 51/54 agreed, 3 disagreed, and **A1 was right on all 3**. Every one of these bugs pushed results in the direction that flattered SIGA. Everything was re-run; results before the fixes are retained as `.v2_*_preA1fix.jsonl`.

### Bug 1 — my deck copy deleted agent-authored non-XML assets
`ladder.py` copied only `*.xml` from the source, then overlaid GT's `tables/`. But on
`AdvancedExampleViscoExtendedDruckerPrager` the agents author their **own** `tables/` — and `F4_s2` and `F8_s1` each authored a 4th file, `zeroStrain.geos`:

```
SRC tables: axialStrain.geos radialStress.geos time.geos zeroStrain.geos   (4)
A2  tables: axialStrain.geos radialStress.geos time.geos                   (3)   <- mine
```
My overlay **replaced their tables with GT's 3-file set**, deleting the file their deck referenced, and I then recorded the resulting `Could not resolve absolute path for: tables/zeroStrain.geos` as a **deck failure**. It was my failure.

Worse: I had already written this up in §11 as a finding ("normalization-boundary artifact"). **§11(b) is retracted** — see §13. Two of the three ceiling-control failures I was about to report never existed.

**Fix:** copy the entire source tree (`copytree(..., symlinks=True, ignore_dangling_symlinks=True)`); GT assets now fill **only genuine gaps** and never replace agent output; plus an assertion that the copied file set covers the source, which raises loudly (`copy_complete`, `copy_missing` in every record).

Verified: `F4_s2` and `F8_s1` now reach **L2 = L3 = L4 = 1**.

**Follow-on bug I introduced while fixing it, caught before it produced numbers:** the first gap-fill copied *every* non-XML GT file, which includes GT's reference **output** `ViscoExtendedDruckerPragerResults.txt`. My DP QoI reader globs `*.txt`, so a run that produced nothing would have had GT's own reference results read back as its output — fabricating a 0% error. Gap-fill is now restricted to `tables/` (genuine input data), and every record carries `stale_txt_before_run` (empty in all runs) as a standing guard.

### Bug 2 — I cascaded L2 from L0/L1 instead of measuring it
My runner only invoked `geosx -v` when L0 passed. **GEOS parses with pugixml, which does not enforce the XML rule that `--` may not appear inside a comment**, while libxml2 (`xmllint`) and Python's `ElementTree` both do. So a deck can fail well-formedness and still load in GEOS. A1 demonstrated it:

```
xmllint --noout ...benchmark.xml  -> parser error: Comment must not contain '--'
ET.parse(...)                     -> ParseError: not well-formed, line 11 col 38
geosx -v -i ...benchmark.xml      -> exit 0
```

I confirmed it independently with an unconditional probe over every **root** deck (`l2_rootdecks.tsv`):

| task | cell | ALL-root pass | ANY-root pass | my cascaded L2 |
|---|---|---|---|---|
| ThermoPoro | **F0 Vanilla** | **2/3** | 2/3 | **1/3** ← wrong |
| ThermoPoro | F4/F6/F8/F11/SE | 3/3, 2/3, 3/3, 2/3, 2/3 | same | agreed |
| DruckerPrager | F4 | 1/3 (pre-fix) | 1/3 | agreed (both wrong, bug 1) |

**Fix:** `geosx -v` and the full run are now invoked **unconditionally** whenever the top deck exists. No cascading. Verified: `F0_s3` ThermoPoro is `L0=0, L1=1, **L2=1, L3=1, L4=1**`.

**The ladder is therefore NOT monotone.** L0/L1 use libxml2 semantics; L2+ use pugixml semantics. A deck can fail L0 and pass L2–L4. This must be stated wherever the ladder appears, and it weakens my §9 "Vanilla writes illegal XML" finding: the decks *are* illegal XML by the W3C rule, but **GEOS runs them anyway**, so it is a portability/tooling defect, not an execution failure. §9 is corrected in §13.

### Bug 3 — my QoI injector was stricter than GEOS
`inject_qoi.py` used `ET.parse`, so it rejected exactly the `--`-comment decks GEOS runs happily, and recorded `qoi_fail_stage: injection` — inflating the rung-5 failure count for precisely the Vanilla runs at issue. **Fix:** `_parse_lenient()` retries with comments stripped (comments are meaningless to GEOS), matching pugixml's permissiveness.

### Naming agreed with A1
A1's independent measurement is **"rung 3 — GEOS accepts the deck, measured independently"**. With cascading removed my L2 measures the same thing on the top deck. To keep one number per quantity I adopt A1's definition and report my column as **L2 / rung 3 (GEOS accepts, measured unconditionally, top deck)**, noting that A1's AND-over-all-root-decks variant is the stricter task-level form. Where they can differ (a task with >1 root deck) I report both from `l2_rootdecks.tsv`.

---

## 13. CORRECTIONS after the A1 bug fixes — the headline weakens substantially

**Read this instead of §9 and §11.** All numbers below are from the re-run (`grid_v2.jsonl`, `qoi_v2.jsonl`); the pre-fix set is `.v2_*_preA1fix.jsonl`.

### 13.1 Ladder, corrected

| task | cell | L0 | L1 | L2/rung3 | L3 | L4 | changed by the fixes |
|---|---|---|---|---|---|---|---|
| ThermoPoro | **F0 Vanilla** | 1/3 | 2/3 | **2/3** | **2/3** | **2/3** | `F0_s3` L2 0→1 |
| ThermoPoro | F4 X+M | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | — |
| ThermoPoro | F6 S+X | 3/3 | 3/3 | 2/3 | 2/3 | 2/3 | — |
| ThermoPoro | F8 S+X+M | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | — |
| ThermoPoro | F11 SE-prose | 3/3 | 3/3 | 2/3 | 2/3 | 2/3 | — |
| ThermoPoro | SE | 3/3 | 3/3 | 2/3 | 2/3 | 2/3 | — |
| DruckerPrager | F0 Vanilla | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | — |
| DruckerPrager | F4 X+M | 3/3 | 3/3 | **2/3** | 2/3 | 2/3 | `F4_s2` L2 0→1 |
| DruckerPrager | F6 S+X | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | — |
| DruckerPrager | F8 S+X+M | 3/3 | 3/3 | **3/3** | 3/3 | 3/3 | `F8_s1` L2 0→1 |
| DruckerPrager | F11 SE-prose | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | — |
| DruckerPrager | SE | 3/3 | 3/3 | 3/3 | 3/3 | 3/3 | — |

`copy_complete` is true and `stale_txt_before_run` is empty for **every** run — the bug-1 and gap-fill guards are clean.

### 13.2 NEGATIVE RESULT — the execution-level rescue at rungs 2–4 does not survive the fixes

On `AdvancedExampleThermoPoroElasticWellbore`, Vanilla's L2/L3/L4 went **1/3 → 2/3**. Against SIGA's 12/15 (80%), Vanilla's 2/3 (67%) is **not distinguishable at n = 3 per cell**. The pre-fix contrast (1/3 vs 80%) that looked like clean execution-level confirmation of the reliability claim was substantially an artifact of my own L2 cascading.

**Do not claim an execution-level rescue at rungs 2–4 from this study.** Anything stronger than "directionally consistent, underpowered" would be overclaiming. With 3 seeds per cell the study cannot resolve a 13-point difference.

### 13.3 §9 corrected — the `--`-comment finding is a portability defect, not an execution failure

§9 reported "Vanilla writes illegal XML in 3/6 case-study runs, SIGA 0/23" and framed it as the mechanism behind the reliability claim. The **count stands** (it is a real, W3C-illegal construct that `xmllint` and ElementTree both reject, and it is Vanilla-only), but the **consequence does not**: GEOS parses with pugixml, which accepts `--` in comments, so those decks **run fine**. It is a defect against the XML standard and against standard tooling — not one that stops the simulation.

Correct framing: *Vanilla emits XML that standard validators reject, which breaks downstream tooling and any schema-based CI; GEOS itself is lenient enough to run it anyway.* That is still worth saying, and it is honest about what it costs.

### 13.4 §11(b) RETRACTED
The "normalization-boundary artifact" (`F4_s2`, `F8_s1` referencing `tables/zeroStrain.geos`) was **my deck-copy bug deleting agent-authored assets**. Both runs reach L2/L3/L4 cleanly. Retracted in full.

### 13.5 Ceiling control, corrected — cleaner, and it says something different
DruckerPrager is now **17/18 at L2–L4**; the single failure is `F4_s1`, the genuine `ElasticIsotropic`-with-no-elastic-constants defect. So at the ceiling:
- execution outcomes *are* near-uniform (unlike my pre-fix reading), which **licenses** reading a low-TreeSim contrast as signal rather than noise;
- but **one schema-valid, TreeSim≈0.99 deck still cannot be loaded** — the existence proof that a structural metric and `xmllint` together do not imply loadability.
- Vanilla is 3/3 here. High TreeSim does not order the cells by execution outcome.

### 13.6 The MCC reference deck — confirmed unusable
`ExampleMCCWellbore`'s reference deck **hits the 600 s wall-clock cap** at t = 0.75 of maxTime = 1.0 (`rc=None, run_timeout=True`), reproducibly. Per the gate rule the task is unusable for rungs 3–5 and was excluded — a decision made from reference-deck behaviour alone, before scoring any generated MCC deck. Disclosable as a cost limit, not a result about any cell.

---

## 14. THE HEADLINE FINDING — TreeSim ≈ 1 does NOT imply matching physics

Fixing bug 1 (the deck copy) did more than remove two false failures: it **unmasked the study's most important result**. Previously my harness overwrote every agent's `tables/*.geos` with GT's copies, which forced every DruckerPrager run down the reference's loading path and manufactured a uniform "0.000% error". With the agents' own assets restored:

### Ceiling control, corrected rung 5 — `final axial stress` vs the reference

| cell | TreeSim | s1 | s2 | s3 |
|---|---:|---:|---:|---:|
| F0 Vanilla | 0.987 | **64.2%** | 0.000% | 0.000% |
| F4 X+M | 0.991 | no QoI | 0.000% | **64.8%** |
| F6 S+X | 0.963 | 0.000% | **64.8%** | **71.0%** |
| F8 S+X+M | 0.964 | 0.000% | **99.3%** | **64.8%** |
| F11 SE-prose | 0.999 | **64.8%** | 0.000% | 0.000% |
| SE | 0.996 | **40.7%** | 0.000% | **64.8%** |

**11 of 17 runs differ from the reference by 40–99% on the primary QoI, at TreeSim 0.963–0.999.** Six reproduce it exactly. No cell is reliably better.

### Verified mechanism — TreeSim cannot see part of the deck
`triaxialDriver_base.xml` drives the test through `TableFunction` files (`tables/time.geos`, `axialStrain.geos`, `radialStress.geos`). **The agents author these files, and TreeSim never reads them** — it compares XML trees only. Diffed directly:

```
GT     : time = 0 1 2 3 4 5          axialStrain = 0.0 -0.004 -0.002 -0.005 -0.003 -0.006
F6_s3  : time = 0.0 0.1 ... 1.0      axialStrain = 0.0 -0.002 -0.001 -0.003 -0.0015 -0.004 ...   -> 71.0% error
F8_s2  : time = 0 0.25 0.5 0.75 1.0  axialStrain = 0.0 -0.003 -0.001 -0.004 -0.002              -> 99.3% error
SE_s1  : time = 0 0.2 0.4 0.6 0.8 1  axialStrain = 0.0 -0.005 -0.002 -0.008 -0.003 -0.006       -> 40.7% error
SE_s2  : IDENTICAL to GT on all three                                                            ->  0.000% error
```
Both runs whose tables are byte-identical to GT give exactly 0%. Agreement between "tables identical" and "zero error" is 11/17 — not 17/17, because two different strain programs can still terminate at the same final strain, which is physically expected. Data: `A2_dp_table_vs_qoi.txt`.

**This is the sharpest available answer to the AC's question.** Structural similarity of the XML does not predict simulation similarity, for a concrete and demonstrable reason: the deck's behaviour depends on artifacts the structural metric does not inspect at all. A metric scoring 0.999 sat on top of a 99% physics error.

### Corrected ThermoPoro rung 5 (complete, post-fix)
Only **three** distinct relative errors occur across 13 runs with QoI — 0.00%, 10.47%, 99.97%:

| cell | n with QoI | exact (0%) | ≤10% | ≤15% | values |
|---|---|---|---|---|---|
| F0 Vanilla | 2/3 | 1 | 1 | 2 | 0.00, 10.47 |
| F4 X+M | 3/3 | 0 | 0 | 3 | 10.47 ×3 |
| F6 S+X | 2/3 | 0 | 0 | 2 | 10.47 ×2 |
| F8 S+X+M | 3/3 | 0 | 0 | 2 | 10.47, 10.47, **99.97** |
| F11 SE-prose | 2/3 | 1 | 1 | 2 | 0.00, 10.47 |
| SE | 2/3 | **2** | **2** | 2 | 0.00, 0.00 |

The declared 10% tolerance falls *between* the 0% and 10.47% clusters, so L5 pass/fail is decided entirely by that gap — the tolerance is doing all the work. Robust statements: on **exact reproduction** SE leads (2/3 vs Vanilla 1/3); at **≤15%** every cell is ≥2/3 and indistinguishable. n = 3; neither is significant.

`F8_s1` is the key counter-example: **L4-clean** (converged, no cuts, no retries) yet 99.97% wrong, on a **16-cell** mesh instead of 40. Converged ≠ correct.

### Bottom line
This study does **not** demonstrate an execution-level or physics-level advantage for SIGA over Vanilla on these three tasks. The large TreeSim gap on ThermoPoro (0.355 → 0.761) does not translate into a corresponding gap at rungs 2–5. What it does establish is that **rungs 3–5 are reachable and cheap**, that **GEOS is bitwise deterministic** (so one run per deck suffices), and that there are **concrete, verified cases where TreeSim and `xmllint` both pass while the physics is badly wrong** — which supports the AC's request rather than rebutting it.

