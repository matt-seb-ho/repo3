# Thread K1 — External-asset staging fix + clean validity ladder (rungs 1–3), HELD-OUT split

**Submission:** NeurIPS 2026 #31642 (SIGA)
**Mission:** remove the `missing_external_asset` confound from the rung-3 measurement, then re-measure rungs 1–3 cleanly on all 180 held-out deck-runs.
**Split:** `/data/shared/geophysics_agent_data/data/eval/autocamp_followup_2026-05-02/icl/`
**Cells:** F0 (Vanilla), F4 (X+M), F6 (S+X), F8 (S+X+M), F11 (SE-prose), SE
**Artifacts:** `/home/matt/sci/repo3/neurips_review/sprint/artifacts/K1_*`

---

## STATE OF PLAY

**Status: COMPLETE.** All deliverables produced. Nothing running. No API spend.

- [x] Arithmetic reproduction of A1's aggregates from A1's own CSVs — matches exactly
- [x] Empirical (element, attribute) survey → principled input-asset whitelist
- [x] Asset enumeration + source resolution (`K1_asset_refs.csv`, `K1_pools.json`)
- [x] **Fairness invariant PROVEN** — 10 tasks × 19 environments, identical asset sets
- [x] **Independent re-run reproduction, unstaged: 180/180 task-runs agree with A1, ZERO disagreements**
- [x] Staged sweep, 273 deck-runs, 0 harness errors
- [x] Clean ladder + significance (Fisher, stratified permutation, sign test) + decomposition
- [x] GT ceiling control, both arms; `ExampleIsothermalHystInjection` isolating experiment
- [x] Agent-invented reference vs fabricated-content taxonomy
- [x] Val split staging audit

### THE ANSWER IN FIVE LINES

1. **Reproduction exact** — 0/180 disagreements vs A1 before changing anything.
2. **Clean rung 3 (n=30, no exclusions):** F0 **21**, F4 **21**, F6 **23**, F8 **24**, F11 **23**, SE **24**.
3. **New ceiling 30/30** (was an effective 24/30). No task needs excluding any more.
4. **The direction does NOT survive intact.** Vanilla is no longer strictly lowest — it **ties F4 (X+M) at 21/30**. Gap 8.7 pp → 6.7 pp; pooled Fisher p 0.38 → **0.49**; stratified permutation p 0.17 → **0.31**; per-task sign test **4 worse / 3 better / 3 tied, p = 1.00**.
5. **Val has the same bug, worse and asymmetric:** 103/561 task-runs affected, **F11 0/51 and SE 0/51 vs F3 16/51, F5 15/51**. Do not ship a val execution number unstaged.

**Two survivors worth keeping:** rung 2 is untouched (F0 24/30 vs 30/30, p = 0.0237) and
`bad_attribute_value` failures are **6 for Vanilla vs 0–1 per adapter cell** — a narrow,
mechanism-matched claim that does hold.

---

## Entry 0 — reproduction check, step 1 of 2: arithmetic from A1's artifacts

Before running anything I re-aggregated A1's own CSVs to confirm the numbers in the brief are
the numbers on disk (catches "the log says X but the CSV says Y").

```
RUNG1/2 framing F (all files must pass):
  autocamp_F0    n=30 files=81 rung1=27/30 rung2=24/30
  autocamp_F4    n=30 files=81 rung1=30/30 rung2=30/30
  autocamp_F6    n=30 files=81 rung1=30/30 rung2=30/30
  autocamp_F8    n=30 files=81 rung1=30/30 rung2=30/30
  autocamp_F11   n=30 files=81 rung1=30/30 rung2=30/30
  autocamp_SE    n=30 files=81 rung1=30/30 rung2=30/30

RUNG3 (rung3_lenient, authoritative), 180 rows:
  autocamp_F0    A=19/30  B=19/27  C=18/24   (strict roots: 18)
  autocamp_F4    A=21/30  B=21/27  C=21/24
  autocamp_F6    A=20/30  B=20/27  C=20/24
  autocamp_F8    A=21/30  B=21/27  C=21/24
  autocamp_F11   A=23/30  B=23/27  C=22/24
  autocamp_SE    A=23/30  B=23/27  C=21/24

A1_rung3_classified.csv, 273 deck-runs:
   pass 193 | missing_external_asset 32 | dangling_reference 23 | missing_region 14
   bad_attribute_value 8 | unknown_element_or_attribute 1 | missing_required_attribute 1
   unsupported_by_binary 1
```

**Every number in the brief reproduces from A1's artifacts.** Rung 2: Vanilla 24/30, five adapter
cells 30/30. Rung 3: 19 / 21 / 20 / 21 / 23 / 23. `missing_external_asset` = 32/273, the largest
single failure category. Proceeding to an independent re-run.

---

## Entry 1 — REPRODUCTION CHECK PASSED (independent re-run, unstaged)

I did not trust A1's numbers on A1's own harness alone, so I rebuilt the sweep
(`K1_rung3.py`) and re-ran all 273 deck-runs from scratch. `K1_rung3.py` imports
`classify`, `root_decks`, `MISSING_RE`, `GEOSX`, `TIMEOUT` **directly from `A1_rung3.py`**,
and imports `reclassify` from `A1_rung3_classify.py`, so the failure taxonomy cannot drift.

```bash
export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH
python3 K1_rung3.py --out K1_rung3_unstaged.jsonl --scratch ./K1_scratch/unstaged \
        --stage none --workers 8
python3 K1_report.py
```

```
REPRODUCTION CHECK — K1 unstaged vs A1 rung3_lenient, per task-run
  task-runs compared : 180
  disagreements      : 0

RUNG 3 — K1 UNSTAGED
cell               A: all 10 (n=30)   B: -GTfail (n=27)   C: -GTfail-asset (n=24)
F0 Vanilla                    19/30               19/27                     18/24
F4 X+M                        21/30               21/27                     21/24
F6 S+X                        20/30               20/27                     20/24
F8 S+X+M                      21/30               21/27                     21/24
F11 SE-prose                  23/30               23/27                     22/24
SE                            23/30               23/27                     21/24

RUNGS 1-2 (framing F): rung2 = F0 24/30, all five adapter cells 30/30
```

**Exact match on every cell at every denominator, and 0/180 task-run disagreements.**
Also: **0 harness errors and 0 copy-integrity failures across 273 deck-runs**, so the
`relset(src) == relset(dst)` assertion (added because A2 lost two runs to a silently
dropped `tables/zeroStrain.geos`) never fired. And no sign of the J3 RPATH trap — 132/273
decks exit 0, not a uniform failure.

Smoketest beforehand reproduced A1's Entry-4 sanity pair verbatim:
`F6/s1 ThermoPoroElasticWellbore_benchmark.xml → rc=1 dangling_reference`
(`elementRegionsGroup has no child named rock`).

**Harness trusted. Proceeding to staging.**

---

## Entry 2 — asset enumeration: three false-positive classes found before staging

Building the enumerator surfaced three ways a naive path scan gets this wrong. All three
would have inflated the "missing asset" count and two would have polluted the manifest.

**(a) `TriaxialDriver/output` is an OUTPUT path.** I built the input-attribute whitelist
*empirically* (`K1_attr_survey.py`: every `(element, attribute)` pair in all 180 generated
+ 46 GT deck dirs whose value carries an asset extension) rather than guessing. Result —
the complete path-valued attribute set in this corpus:

| kind | (element, attribute) |
|---|---|
| input | `TableFunction/coordinateFiles`, `TableFunction/voxelFile` |
| input | `CO2Brine{Phillips,Ezrokhi}[Thermal]Fluid/phasePVTParaFiles`, `/flashModelParaFile` |
| input | `VTKMesh/file`, `VTKWell/file`, `DeadOilFluid/tableFiles` |
| input | `Included/File/name` (include graph) |
| **output** | **`TriaxialDriver/output`** — the only one |

`TriaxialDriver/output="ViscoExtendedDruckerPragerResults.txt"` appears in **all 18
cell-seeds** of `AdvancedExampleViscoExtendedDruckerPrager` and the file is absent from
every one. A naive scan calls that 18 missing assets; GEOS *writes* it. Excluded.

**(b) `$table_root$` is a GEOS `<Parameter>` substitution, not a directory.** My first pass
reported 22 missing `$table_root$/*.csv` assets for `TutorialHydraulicFractureWithAdvancedXML`.
The enumerator now resolves each file's own `<Parameters>` block before testing the path.
(These were GT-side only — the generated decks for that task reference no assets at all.)

**(c) Dangling symlinks hide behind their parent directory.** `inputs/tables/x.geos` is
"missing" when `inputs/tables` is itself a dangling symlink, but `Path.is_symlink()` on the
leaf returns False. `exists_as_file()` + an ancestor walk handles both.

### *** CORRECTION TO A1 ENTRY 5: the symlink inventory is materially incomplete ***

A1 Entry 5 states: *"**Exactly 2 symlinks in the whole dataset**, both in F0/s2 … Every
other cell's `tables`/`fc_tables` are real copied directories."* That is wrong.

```
F0/s2 ExampleIsothermalHystInjection: tables -> /geos_lib/.../tables          (dir symlink, dangling)
                                      fc_tables -> /geos_lib/.../fc_tables    (dir symlink, dangling)
F6/s2 ExampleIsothermalHystInjection: tables/ and fc_tables/ are REAL DIRS containing
                                      21 dangling per-FILE symlinks to /geos_lib/...
                                      plus a literal `*` symlink (an unexpanded shell glob)
F8/s2 ExampleIsothermalHystInjection: same, 21 dangling per-file symlinks + literal `*`
```

So three cell-seeds ship dangling `/geos_lib/...` links, not one, and F6/s2 + F8/s2 do it
at file granularity inside real directories — which is why a directory-level walk missed
them. The literal `*` symlink is a nice artefact: the agent ran
`ln -s .../tables/* tables/` in a shell where the glob did not expand.

This does not change any A1 number (all three fail rung 3 either way), but "exactly 2
symlinks, all other cells are real directories" should not go into a rebuttal.

### The asset landscape, generated side (742 ref rows, `K1_asset_refs.csv`)

| class | refs | meaning |
|---|---|---|
| `present` | 454 | asset resolves to a real file in `inputs/` |
| `staging_artifact` | 198 | missing, but resolvable from GT or the GEOS repo → **our harvester's fault** |
| `absolute_container_path` | 21 | `/geos_lib/...` baked into the XML → **genuine authoring defect, unfixable by staging** |
| `agent_invented_reference` | **0** | missing *and* unresolvable anywhere |
| `missing_xml_include` | **0** | dangling `<Included><File>` edge |

Only **two of ten tasks** have any missing assets at all:
`ExampleIsothermalHystInjection` (24-asset pool) and `ExamplesingleFracCompression`
(1 asset, `crackInPlane_benchmark.vtu`).

**The 21 `absolute_container_path` refs are all F0/s1 `ExampleIsothermalHystInjection`.**
Vanilla wrote `coordinateFiles="/geos_lib/inputFiles/.../tables/..."` — a path that exists
only inside the generation sandbox. Staging into the run directory cannot fix an absolute
path, and fabricating `/geos_lib` on the host would be inventing evidence. So this stays a
failure and is reported as a **portability defect**, symmetrically available to any cell.

---

## Entry 3 — the staging design, and the fairness invariant PROOF

**Pool-based, not demand-based.** The pool for task *T* is the union of every input-asset
reference made by any of the 18 (cell, seed) dirs for *T* **and** by the GT deck, resolved
to a concrete source. The **whole pool** is installed into **all 19 environments**. Demand-
driven staging would be subtly asymmetric — a cell that happened not to name an asset would
silently get a different environment.

**Resolution priority** (task-scoped before repo-wide, so a same-named table from an
unrelated physics example cannot be silently substituted):
`GT exact relpath` → `GT basename` → `canonical GEOS example dir, exact relpath` →
`canonical GEOS dir, basename` → `anywhere in data/GEOS/inputFiles, basename`.
The canonical GEOS dir per task is derived by matching GT XML basenames — e.g.
`ExampleIsothermalHystInjection → compositionalMultiphaseWell/benchmarks/Class09Pb3`.
This mattered: a repo-wide basename search had resolved `tables/capPres_water.txt` from
`compositionalMultiphaseFlow/dbc/grav_seg_1d/`, a different physics setup, when the correct
`Class09Pb3/tables/capPres_water.txt` exists.

**Existing files are NEVER overwritten.** An agent-authored `tables/x.geos` stays as the
agent wrote it — overwriting it with the GT copy would mask an authoring defect. So the
invariant is "the same asset *paths* are available", which is exactly the staging property;
content differences stay visible as authoring properties (Entry 5).

**Not staged, deliberately:** (i) `*.xml` includes — dropping an XML into the run dir would
change the root-deck set and hence the measured object; (ii) absolute container paths;
(iii) output attributes.

### Proof, not assertion (`K1_build_pools.py`)

Dry-run staged all 10 tasks × 19 environments and compared the resulting available-asset
sets:

```
  OK   ExampleIsothermalHystInjection    19 envs, 24 pool assets available in all
  OK   ExamplesingleFracCompression      19 envs,  1 pool asset  available in all
  OK   (the other 8 tasks)               19 envs,  0 pool assets (nothing missing)
*** FAIRNESS INVARIANT HOLDS for all 10 tasks x 19 environments ***
```

Staged-file counts differ across cells (`F0/s1=24 … F11/s1=3 … F6/s1=19`) precisely because
cells started with different numbers of assets already present — the *end state* is
identical, which is the requirement. Full per-file record: `K1_staging_manifest.csv`
(519 rows: `staged` / `kept_existing` / `removed_dangling_symlink`).

---

## Entry 4 — *** THE CLEAN RUNG-3 TABLE. READ THE NEGATIVE FIRST. ***

### *** NEGATIVE, STATED FIRST: the direction does NOT survive intact ***

A1's rung-3 headline was *"Vanilla is the **lowest** cell at every denominator"* (directional
but non-significant, per-cell Fisher p 0.27–0.79). **After the confound is removed, Vanilla is
no longer strictly lowest — it ties with F4 (X+M) at 21/30 — and every significance measure
gets worse.**

| cell | A1 confounded | K1 unstaged (repro) | **K1 STAGED (clean)** | Δ |
|---|---|---|---|---|
| F0 Vanilla | 19/30 | 19/30 | **21/30** | +2 |
| F4 X+M | 21/30 | 21/30 | **21/30** | +0 |
| F6 S+X | 20/30 | 20/30 | **23/30** | +3 |
| F8 S+X+M | 21/30 | 21/30 | **24/30** | +3 |
| F11 SE-prose | 23/30 | 23/30 | **23/30** | +0 |
| SE | 23/30 | 23/30 | **24/30** | +1 |

```
ranking unstaged: F0 < F6 < F4 = F8 < F11 = SE      (Vanilla strictly lowest)
ranking staged  : F0 = F4 < F6 = F11 < F8 = SE      (Vanilla JOINT-lowest with an adapter cell)
```

- Vanilla rate 0.633 → **0.700**; pooled SIGA 0.720 → **0.767**.
- Gap **narrows from +8.7 pp to +6.7 pp**.
- Fisher pooled p **0.3822 → 0.4865**. Per-cell Fisher p **0.55–1.00** (F0 vs F4 is now
  p = 1.0000 exactly — an identical 21/30).
- Task-stratified exact permutation (permutes the cell label within each (task, seed) block,
  which is the randomisation the design licenses and which respects the clustering A1 Entry 3
  flagged): **p = 0.1734 → 0.3109**.

95% Wilson intervals on the clean measurement overlap almost completely:
`F0 [0.521, 0.833]` vs `SE [0.627, 0.905]`.

### *** AND THE STATISTIC NOBODY COMPUTED: the per-task sign test ***

The pooled rate hides that the cell ordering rests on a minority of tasks. Vanilla vs the SIGA
mean, per task:

| task | Vanilla /3 | SIGA mean /3 | |
|---|---|---|---|
| AdvancedExampleCasedThermoElasticWellbore | 2 | 3.00 | worse |
| AdvancedExamplePureThermalDiffusionWellbore | 3 | 2.80 | **better** |
| AdvancedExampleThermoPoroElasticWellbore | 2 | 2.40 | worse |
| AdvancedExampleViscoExtendedDruckerPrager | 3 | 2.80 | **better** |
| ExampleIsothermalHystInjection | 0 | 0.00 | tie |
| ExampleMCCWellbore | 3 | 3.00 | tie |
| ExampleProppantTest | 2 | 2.80 | worse |
| ExampleVerticalPoroElastoPlasticWellbore | 3 | 3.00 | tie |
| ExamplesingleFracCompression | 3 | 2.00 | **better** |
| TutorialHydraulicFractureWithAdvancedXML | 0 | 1.20 | worse |

**Vanilla is worse in 4/10 tasks, BETTER in 3/10, tied in 3/10. Two-sided sign test p = 1.0000.**
Identical counts unstaged, so this is *not* caused by staging — but A1 never computed it, and it
is a far more honest summary of a 6.7 pp pooled gap on 10 clustered tasks than the pooled rate
is. **A reviewer will compute this by eye from the per-task table. We should present it
ourselves.**

### *** THE NEW CEILING: 30/30, not 24/30 ***

A1 recommended denominator **C (n=24)**, excluding `ExampleIsothermalHystInjection` (GT-unpassable)
and `ExamplesingleFracCompression` (asset-confounded), giving an effective ceiling of 24/30.
Both exclusions are now unnecessary:

- `ExamplesingleFracCompression` — the entire failure was the single missing
  `crackInPlane_benchmark.vtu`. Staged, it is passable, and **9 of the 9 flipped task-runs in the
  whole sweep are this task.** It no longer needs excluding.
- `ExampleIsothermalHystInjection` — see Entry 5. The GT deck **does** pass once the
  ground-truth harvest gap is repaired, so it is a legitimately discriminating task, not a
  hard-zero.

**Ceiling: assets staged → 27/30 (GT passes 9/10). Assets + the GT xml-include gap staged →
30/30 (GT passes 10/10).** Reported both ways; `K1_rung3_gt.jsonl` + `K1_hyst_sensitivity.json`.

**Recommended denominator is now A: all 10 tasks, n = 30, no exclusions.** That is a strictly
better position than A1's — the exclusions were the weakest part of the rung-3 story and they
are no longer needed.

### Failure decomposition, per cell (deck-runs), staged vs unstaged

**`missing_external_asset` goes 32 → 0. The category is completely eliminated.**

| cell | bad_attr_value | dangling_ref | missing_region | missing_req_attr | unknown_elem | unsupported | **missing_external_asset** |
|---|---|---|---|---|---|---|---|
| **STAGED** | | | | | | | |
| F0 Vanilla | 6 | 4 | 4 | 0 | 1 | 0 | **0** |
| F4 X+M | 1 | 4 | 6 | 1 | 0 | 0 | **0** |
| F6 S+X | 1 | 6 | 5 | 0 | 0 | 0 | **0** |
| F8 S+X+M | 1 | 3 | 4 | 0 | 0 | 1 | **0** |
| F11 SE-prose | 0 | 6 | 5 | 0 | 0 | 0 | **0** |
| SE | 1 | 6 | 4 | 0 | 0 | 0 | **0** |
| **UNSTAGED** | | | | | | | |
| F0 Vanilla | 6 | 3 | 3 | 0 | 1 | 0 | 4 |
| F4 X+M | 1 | 2 | 1 | 1 | 0 | 0 | 7 |
| F6 S+X | 0 | 5 | 1 | 0 | 0 | 0 | 9 |
| F8 S+X+M | 0 | 2 | 0 | 0 | 0 | 1 | 9 |
| F11 SE-prose | 0 | 5 | 4 | 0 | 0 | 0 | 2 |
| SE | 1 | 6 | 4 | 0 | 0 | 0 | 1 |

So the *remaining* rung-3 failures are all genuine authoring defects, in three dominant classes:
**dangling reference** (29), **missing/bad region** (28), **bad attribute value** (10). One
useful asymmetry survives: `bad_attribute_value` is **6 for Vanilla vs 0–1 for every adapter
cell** — that is the one failure class where the validator-in-the-loop mechanism shows a clean
signal, and it is the same class as the rung-2 story (invented attributes, R1Tensor format
errors). That is a narrower but much more defensible claim than the aggregate rate.

### Robustness: the fragment framing changes nothing

Re-aggregating with `*_base.xml` fragments dropped from the root set ("runnable roots") gives
**21 / 21 / 23 / 24 / 23 / 24 — identical to the headline in every cell.** Column
`rung3_staged_runnable` in `K1_ladder_by_taskrun.csv`.

### Rungs 1–2 unchanged, as designed

Staging installs no XML, so rungs 1–2 are staging-invariant by construction:
**rung 1** F0 27/30, others 30/30; **rung 2** F0 24/30, others 30/30. The rung-2 result
(p = 0.0237 per cell) remains by far the strongest execution-validity evidence we have, and
**the clean rung-3 measurement makes the rung-2/rung-3 contrast sharper, not weaker**: our
adapters demonstrably fix machine-readability, and demonstrably do *not* fix simulator
loadability to any significant degree.

---

## Entry 5 — TWO MORE HARVEST BUGS on `ExampleIsothermalHystInjection`, both found by staging

After staging all 24 assets the task was still **0/30 for every cell and 0/1 for GT**, which
did not smell like an authoring result. Two stacked artifacts, both ours:

**Bug A — a fragment is run standalone.** The harvest ships THREE xmls: `class09_pb3_smoke_3d.xml`
plus TWO `*_base.xml` fragments, but `smoke_3d.xml` `<Included>`s only ONE of them. The other
is unreferenced, so the root rule calls it a root and runs it standalone, where it dies on
`numberOfMeshBodies == 0` — a fragment has no `<Mesh>`. This is exactly the artifact class A1
Entry 12 corrected for `ProppantSlotTest_base.xml`, and **A1's regex fix cannot catch it**,
because here the include edge does not *exist* rather than being invisible to ElementTree.
It hits **all 20 `*_base.xml` roots in the sweep, every one of them on this task**, identically
across cells. A1's own decisive control applies verbatim: GT's
`class09_pb3_drainageOnly_iterative_base.xml` **also fails standalone**, so the fragment
carries zero information.

**Bug B — the GROUND TRUTH has a dangling xml include.** GT's `smoke_3d.xml` contains
`<File name="./class09_pb3_hystRelperm_direct_base.xml"/>`, and **the GT harvest never copied
that file.** Verbatim:

```
***** Rank 0: Could not resolve absolute path for: <cwd>/./class09_pb3_hystRelperm_direct_base.xml.
Frame 0: geos::xmlWrapper::xmlDocument::addIncludedXML(pugi::xml_node&, int)
```

The file exists at
`data/GEOS/inputFiles/compositionalMultiphaseWell/benchmarks/Class09Pb3/class09_pb3_hystRelperm_direct_base.xml`.
So the same harvest bug the whole thread is about also affects an **xml** reference, one level up,
and it is what made the reference deck unloadable. Note the generated decks *repaired* this
themselves — they include `hystRelperm_iterative_base.xml`, which is present.

### The isolating experiment (`K1_hyst_sensitivity.py`)

Top deck only (so no fragment is ever run standalone, and adding an xml cannot create a new
root), all 19 environments, two arms:

```
env        A: assets staged   B: + xml include staged
F0                     0/3                    0/3
F4                     0/3                    0/3
F6                     0/3                    0/3
F8                     0/3                    0/3
F11                    0/3                    0/3
SE                     0/3                    0/3
GT                     0/1                  *** 1/1 ***
```

**GT passes in arm B.** So `ExampleIsothermalHystInjection` is NOT a hard-zero task — A1's
statement that it *"has a hard rung-3 ceiling of 0 for every cell, including ground truth"* is
an artifact of two stacked harvest bugs. Arm B is a no-op for the generated cells
(`missing_xml_include = 0` on the generated side), so it is symmetric.

**And the cells still fail 0/18 in arm B, on genuine defects** — verbatim:

```
CO2BrinePhillipsFluid fluid (class09_pb3_hystRelperm_iterative_base.xml, l.70):
  PVT model PhillipsBrineDensity not found in input files          [x11 across cells]
Mismatch in phase names between constitutive models .../elementRegionsGroup/...   [x2]
WellControls wellControls (l.41): The interpolation method for the time-dependent
  total rate table ...                                             [x3]
```

That is a **real and unanimous** authoring failure: every cell, every seed, on the hardest task
in the set. Worth stating plainly — it is the clearest evidence in the thread that neither
Vanilla nor any SIGA adapter can author a multiphase CO2 injection deck that loads.

---

## Entry 6 — agent-invented references vs agent-FABRICATED data (the brief conflates them)

**Agent-invented *references* (deck names an asset that exists nowhere): ZERO on the held-out
split.** Every one of the 198 missing-asset references resolves to a real file in the GT tree or
the GEOS repo. There is no dangling `<Included>` edge either. So on held-out, **100 % of the
`missing_external_asset` failures were our harness, none were the agent naming something
imaginary.**

**Correction to Thread J3.** J3 reported `tables/elevation.txt` as *"an agent-invented
`tables/elevation.txt` that is in neither the GT tree nor the GEOS repo."* Two errors:
1. `elevation.txt` **does** exist in the GEOS repo —
   `data/GEOS/inputFiles/compositionalMultiphaseFlow/elevation.txt` and
   `.../poromechanicsFractures/elevation.txt`. Same for `initTemp.txt`. They are real GEOS table
   names, just not part of the `Class09Pb3` example.
2. It is not a dangling *reference* at all — **F6/s1 wrote the file**, so the deck loads. The
   defect is fabricated *content*, not a missing file.

The right taxonomy, over all 240 assets the agents actually provided (`K1_fabricated_assets.csv`,
content-hashed against every same-named file in the GT tree and the GEOS repo):

| class | n | meaning |
|---|---|---|
| `authentic_copy` | 178 | byte-identical to a real upstream file |
| `authentic_name_modified_content` | **58** | real table name, **numbers found in no upstream copy** |
| `fabricated_name_and_content` | **4** | name exists nowhere upstream |

**62 of 240 provided assets (26 %) contain fabricated numerical data**, and it is spread across
**all six cells**: F0 9, F4 9, F6 15, F8 6, F11 13, SE 6. Examples:

```
F6/s1  tables/elevation.txt   (17 B)  -3238.2 / -2506.13          <- a 2-point "table"
F6/s1  tables/initTemp.txt    (16 B)  380.296 / 358.334
F6/s1  fc_tables/xlin.geos     (5 B)  5000                        <- a 1-point coordinate axis
F4/s2  tables/zeroStrain.geos (24 B)  0.0 / 0.0 / 0.0 / 0.0 / 0.0 / 0.0
F0/s1  tables/time.geos       (24 B)  0.0 / 0.2 / 0.4 / 0.6 / 0.8 / 1.0
```

**This is a failure class rung 3 CANNOT SEE** — a 2-row table loads perfectly. It is invisible to
rungs 1–3 and to TreeSim, and staging deliberately does not mask it (existing files are never
overwritten). **SIGA does not reduce it**: the two most-affected cells are F6 (15) and F11 (13),
both adapter cells. If a reviewer asks "does your validator catch fabricated physical data?",
the answer on our own data is **no**, and it is better to concede that than to have it found.

`tables/zeroStrain.geos` (F4/s2 and F8/s1) also settles the A1/A2 dispute from A1 Entry 9: the
file is real and A2's copy dropped it, but its *contents* are six zeros the agent invented, and
it exists nowhere upstream.

---

## Entry 7 — DOES THE VAL SPLIT HAVE THE SAME BUG? YES, AND WORSE

Static audit, no GEOS runs (`K1_val_audit.py`, path convention imported from `K3_paths.py` so
K1 and K3 agree on what "val" means): val = **17 tasks x 11 cells x 3 seeds = 561 task-runs**,
`autocamp_2026-05-01/dsv4/autocamp_<cell>/autocamp_<cell>_s<seed>/<task>/inputs`.

```
VAL reference classification (1921 refs)
  present                    1274
  staging_artifact            618      <- missing but resolvable = OUR harness
  absolute_container_path       26
  agent_invented_reference       3

VAL task-runs affected
  staging_artifact             103 / 561   (18.4 %)
  absolute_container_path        2
  agent_invented_reference       3
```

### *** The val confound is SEVERELY asymmetric across cells — far worse than held-out ***

```
staging_artifact task-runs, per cell (out of 51 = 17 tasks x 3 seeds)
  F0   5/51     F1  14/51     F2   7/51     F3  16/51
  F4  11/51     F5  15/51     F6  10/51     F7  14/51
  F8  11/51     F11  0/51     SE   0/51
```

**F11 and SE are at 0/51 while F3 is at 16/51 and F5 at 15/51.** On held-out the spread was
1–9 deck-runs and A1 could call it harvest noise; on val it is a 0-to-16 spread that lines up
with cell identity, and **the two cleanest cells are the two SE cells**. Any val-based execution
claim that puts F11/SE ahead of F1–F8 is confounded with asset-harvest completeness in exactly
the direction that flatters us.

Concentrated in 8 of 17 tasks: `ExampleMandel` 26/33, `ExampleThermalLeakyWell` 21/33,
`AdvancedExampleDruckerPrager` 13/33, `AdvancedExampleModifiedCamClay` 13/33,
`buckleyLeverettProblem` 12/33, `AdvancedExampleViscoDruckerPrager` 10/33,
`AdvancedExampleExtendedDruckerPrager` 7/33, `ExampleIsothermalLeakyWell` 1/33.

### And A1's key premise does NOT generalise to val

A1 Entry 10's load-bearing finding — *"All six cells reference the same assets"* — is what
licensed treating the confound as harvest noise. On val:

```
34/51 (task, seed) groups where all 11 cells reference exactly the same asset set
```

**17 of 51 groups have cells referencing genuinely different asset sets.** So on val the
"identical references, only staging differs" argument is unavailable for a third of the groups,
and the confound cannot be dismissed the same way.

**Val also has 3 genuine agent-invented references** (unresolvable anywhere), which held-out has
zero of: `F1/s1 AdvancedExampleDruckerPrager tables/zeroStrain.geos`,
`F3/s1 AdvancedExampleViscoDruckerPrager tables/zeroStrain.geos`,
`F6/s1 ExampleThermalLeakyWell temp_bc.geos`.

**Recommendation: do not ship a val-based execution-validity number without staging val first.**
The fix is mechanical — `K1_stage.py` is split-agnostic and `K1_val_asset_refs.csv` already lists
every source path. Flagged to K3, which is opening val for SOF.

---

## Entry 8 — artifact manifest and reproduction

All under `/home/matt/sci/repo3/neurips_review/sprint/artifacts/`.

**Data**
| file | rows | what |
|---|---|---|
| `K1_ladder_by_taskrun.csv` | 180 | **the per-task/cell/seed deliverable** — rung1, rung2, rung3 unstaged, rung3 staged, A1's value, categories both arms, n staged assets, root sets, runnable-root framing |
| `K1_rung3_unstaged.jsonl` | 273 | reproduction arm, one row per deck-run (exit code, category, message, stdout tail, copy_ok) |
| `K1_rung3_staged.jsonl` | 273 | clean arm, same schema + `n_staged` and the staged path list |
| `K1_staging_manifest.csv` | 519 | **the staging manifest** — every file staged / kept / dangling-symlink-removed, per task x cell x seed, with source path and resolution method |
| `K1_asset_refs.csv` | 742 | every asset reference on held-out, generated + reference, with presence, class and resolution |
| `K1_pools.json` | 2 tasks | the per-task asset pool: relpath -> (source, resolution) |
| `K1_fabricated_assets.csv` | 240 | content provenance of every asset the agents provided |
| `K1_val_asset_refs.csv` | 1921 | the val-split audit |
| `K1_rung3_gt.jsonl` | 30 | GT ceiling control, both arms |
| `K1_hyst_sensitivity.json` | 38 | the `ExampleIsothermalHystInjection` isolating experiment |

**Code** — `K1_stage.py` (enumeration + staging + fairness invariant), `K1_build_pools.py`,
`K1_rung3.py`, `K1_rung3_gt.py`, `K1_hyst_sensitivity.py`, `K1_report.py`, `K1_stats.py`,
`K1_val_audit.py`, `K1_attr_survey.py`.
**Printed reports** — `K1_report_out.txt`, `K1_stats_out.txt`, `K1_rung3_gt_out.txt`,
`K1_val_audit_out.txt`, `K1_fabricated_out.txt`.

Superseded and deleted so nobody reads them: a first-pass `K1_assets.py` / `K1_asset_resolution.csv`
that had the `TriaxialDriver/output` and `$table_root$` false positives (Entry 2).

**Reproduce from scratch (~55 min, no API spend)**
```bash
export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH
cd /home/matt/sci/repo3/neurips_review/sprint/artifacts
python3 K1_attr_survey.py                     # the input-attribute whitelist, empirically
python3 K1_build_pools.py                     # pools + FAIRNESS INVARIANT PROOF (exits 1 on violation)
python3 K1_rung3.py --out K1_rung3_unstaged.jsonl --scratch ./K1_scratch/unstaged --stage none --workers 8
python3 K1_rung3.py --out K1_rung3_staged.jsonl   --scratch ./K1_scratch/staged   --stage pool --workers 8
python3 K1_rung3_gt.py --scratch ./K1_scratch/gt --workers 6
python3 K1_hyst_sensitivity.py
python3 K1_report.py ; python3 K1_stats.py ; python3 K1_fabricated.py ; python3 K1_val_audit.py
```

**Discipline.** No API spend. Nothing under `/data/shared/` or `/data/jixuan/` written —
verified with `find -newermt` after the fact. No `_`-prefixed directory touched. `writing/` not
touched. No git commits. Every geosx run executed in a private scratch copy under
`artifacts/K1_scratch/`, deleted after each deck-run and the tree removed at the end.
546 deck-runs + 30 GT + 38 sensitivity, **0 harness errors, 0 copy-integrity failures,
0 timeouts**. Max 8 workers throughout; machine load stayed ~75/128 (K4 concurrent).
