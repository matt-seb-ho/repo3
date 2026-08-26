# Thread K3 — scaling the simulation-output-fidelity (SOF) study for power

## STATE OF PLAY  (keep current; this is the resume point)

**Status: staged val + held-out grids running. Reproduction of J2's ρ = 0.402 PASSED (exact).
Design revised at 10:22Z after K1/K2 found val contaminated on BOTH axes — see §6.**

> **Read §6 before quoting any val number.** Val's SOF axis was confounded by unstaged
> external assets that **track cell identity** (F11 0/51, SE 0/51 vs F3 16/51) and val's
> TreeSim axis was produced by a scoring pass that **raced the campaign**. Both are fixed in
> the arm K3 reports (K1's staging + K2's strict re-score), but **held-out is the primary**
> because it is clean on both axes. **§5.3 of this log is WITHDRAWN and corrected in §6.3.**

| | |
|---|---|
| Metric | **SOF**, J2's, unchanged. `artifacts/J2_metric.py` imported, not forked. |
| Reproduction gate | **PASSED exactly** — see §1. ρ = 0.4020, meta 0.4111, I² = 42 %, conditional 0.4500, worst-reduction 0.1478, cells Δ = −0.0086 p = 0.292. All match J2 §9 to 4 dp. |
| Pre-registration | §2, timestamped **2026-07-27T09:55Z**, written before any new run |
| Amendments | §3 R2–R5 (closure maxTime, table backend, output purge, no asset staging) — all decided from GT + reference behaviour only |
| Cross-thread checks | §4 — TreeSim 180/180 vs A2, **11/11 vs D's verified Table-1 val column**, top-deck 5/5 vs J2 |
| Power target | n ≥ 206 (J2's own n for ρ = 0.2 at 80 % power); report min detectable \|ρ\| at final n |
| Artifacts prefix | `neurips_review/sprint/artifacts/K3_*` |

| Design after correction | **held-out = PRIMARY** (clean on both axes) · **val = staged + K2-rescored SECONDARY** · val unstaged = confound measurement only |
| Val fixes applied | K1's staging (fairness invariant re-proved, 34 envs/task) + K2's `treesim_strict` (4 val runs differ from published) |

**Done:** reproduction (§1); pre-registration (§2); amendments R2–R8 (§3, §6.6–6.8);
cross-thread checks (§4); unstaged reference gates, both splits (§5); course correction and
val re-design (§6); §5.3 withdrawn and corrected (§6.3, §6.9).
**Running:** staged reference gates + staged/unstaged grids (`K3_pipeline2.sh`).
**Next:** `K3_score.py` (both arms) → `K3_integrity.py` → `K3_validate.py` → `K3_confound.py`,
then §7 results.

---

**Owner:** Thread K3 (autonomous overnight round 2, NeurIPS 2026 sub 31642 SIGA)
**Started:** 2026-07-27 09:55Z
**Mandate:** `OVERNIGHT_DECISIONS.md` D3 — scale J2's SOF study to n ≈ 206+, adding held-out
tasks and opening the val split, so the study can answer the AC's execution/physical-validity
question with power rather than at its own detection floor.
**Builds on:** Thread J2 (`J2_output_metric.md`, **§9 authoritative**). The metric, the
extraction backends, the admissibility rules, the reference gate and the runner are inherited
**unchanged**. K3 adds tasks and splits; it does not redesign the metric.

---

## 1. REPRODUCTION GATE — J2's ρ = 0.402, recomputed independently

Rule imposed by `OVERNIGHT_DECISIONS.md`: *"K3 must reproduce J2's ρ = 0.402 before
extending."* Done first, and deliberately **not** by re-running `J2_validate.py` (which would
only prove the script is deterministic). Instead the statistic was re-implemented from J2's
written convention (§9.1: *within-task percentile ranks*, pooled Spearman) and applied to
`J2_per_run.csv` as a flat data file, importing none of J2's code.

Script: `artifacts/K3_repro.py` · output: `artifacts/K3_repro.txt`

```
n rows: 108   tasks: 6   cells: F0 F11 F4 F6 F8 SE   with output (ran=1): 91
SOF_all: n=108  POOLED raw rho=+0.3027 (p=0.0015)   POOLED within-task rho=+0.4020 (p=1.6e-05)
SOF_ran: n= 91  POOLED raw rho=+0.2801 (p=0.0072)   POOLED within-task rho=+0.4500 (p=7.7e-06)

per-task (SOF_all):
  AdvancedExampleCasedThermoElasticWellbore     n=18 rho=+0.735 p=0.001
  AdvancedExamplePureThermalDiffusionWellbore   n=18 rho=+0.503 p=0.033
  AdvancedExampleThermoPoroElasticWellbore      n=18 rho=+0.110 p=0.664
  AdvancedExampleViscoExtendedDruckerPrager     n=18 rho=+0.109 p=0.668
  ExampleProppantTest                           n=18 rho=+0.609 p=0.007
  ExamplesingleFracCompression                  n=18 rho=+0.200 p=0.427
  META Fisher-z rho=+0.4111 CI[+0.221,+0.571] Q=8.60 (df 5) p=0.126 I2=42%  range +0.11..+0.73
  META (ran)    rho=+0.5038 CI[+0.308,+0.659] I2=39%              range +0.13..+0.83

TreeSim vs ran(0/1):        n=108 rho=+0.1501 p=0.121
WORST-REDUCTION SOF_wc_all: n=108 rho=+0.1478 p=0.127
SIGA n=90 mean=0.8054 vs Vanilla n=18 mean=0.8140 delta=-0.0086 MW p=0.292
```

**Every J2 §9 headline reproduces to the digit** (J2: pooled 0.402, meta 0.411, conditional
0.450, meta-conditional 0.504, per-task 0.11–0.83, I² 42 %, ran-indicator 0.150 p = 0.119,
worst-reduction 0.148 p = 0.127, Δ = −0.0086 p = 0.292). The p-values differ in the 3rd
decimal only because K3's reproduction uses the asymptotic Spearman p and J2 uses a
20 000-draw permutation p (0.121 vs 0.119, 0.127 vs 0.127) — the statistic itself is
identical. **Gate PASSED; extension authorised.**

---

## 2. PRE-REGISTRATION — fixed 2026-07-27T09:55Z, before any new deck was executed

Everything below was written before the first new GEOS run of this thread. Nothing here may
be changed after seeing a result; deviations get their own numbered subsection with a reason.

### 2.1 Power target
- **Primary target: total n ≥ 206.** This is J2 §9.7's own Bonett–Wright figure for detecting
  Spearman ρ = 0.2 at 80 % power, α = 0.05.
- **Secondary target: k ≥ 12 tasks**, J2's figure for beginning to model the per-task
  heterogeneity (I² = 42 % at k = 6 is under-identified).
- Report the **minimum detectable |ρ| at the achieved n**, by the same
  `n_for_spearman` inversion J2 used, and state explicitly whether the ρ = 0.2 target cleared.

### 2.2 Primary analysis convention (J2's, unchanged)
- **Primary statistic:** pooled Spearman ρ(TreeSim, SOF) on **within-task percentile ranks**
  (`rankdata(v)/(n+1)` within each task), which is what J2 §9.1 headlines. Pooled-on-raw-values
  is reported alongside as a secondary.
- p-values: **permutation, 20 000 draws**; CIs: **percentile bootstrap, 10 000 draws**;
  RNG seed **20260727**, re-seeded per call (J2's convention, so numbers are call-order
  independent).
- **Meta-analysis:** fixed-effect Fisher-z over per-task ρ with Bonett–Wright weights
  (n−3)/1.06, plus Q and I². **The per-task range and I² are quoted every single time the
  pooled number is quoted.** This is J2's binding instruction and K3 inherits it.
- Both conventions always: `SOF_all` (non-executing runs = 0) and `SOF_ran` (conditional on
  producing output). Plus TreeSim vs the binary `ran` indicator, to keep a runnability effect
  from masquerading as a fidelity effect.

### 2.3 Aggregator — both, always
- **Primary: mean over reductions** (`agg_rho="mean"`), mean over quantities, `scale="peak"`,
  `squash="linear"`. J2's declared primary.
- **Mandatory secondary: worst reduction** (`agg_rho="min"` → `SOF_wc`). J2 found this drops
  ρ from 0.402 to 0.148 (p = 0.127) at n = 108 — **the largest analytic sensitivity in the
  study.** Every K3 headline is reported under **both** aggregators, side by side, including
  the val/held-out split and the cell contrast. If the two disagree in sign or significance at
  the larger n, that disagreement is the headline, not a footnote.

### 2.4 Reference gate (a gate, not a formality)
For every new task, **before any generated deck is executed**:
1. Run the **GT reference deck** under the identical J2 protocol — whole-tree copy with the
   `copy_complete` assertion, GT gap-fill of non-XML assets only, identical injected
   `<VTK plotLevel=3>` final-time event, identical **600 s wall-clock cap**, SIGKILL retry.
2. The task is **usable** iff the reference (a) reaches final time, (b) yields a non-empty
   bundle, and (c) has **≥ 1 live quantity** (`max − min > CONST_RTOL·scale` after the
   admissibility filter).
3. A task failing any of these is `task_unusable` and is **dropped for all cells and seeds**,
   recorded with its stage and wall-clock in `K3_ref_gate.csv`. An exclusion decided on
   reference behaviour alone can never be a result about a cell.
4. Top-deck rule: **J2_discover.py unchanged** — a root is a GT deck no other GT deck
   `<Included>`s; among roots carrying `<Events maxTime>`, prefer `smoke` > `benchmark` >
   lexicographically first. The chosen **filename** is then used unchanged for every
   generated deck. A generated set missing that filename is a recorded failure, never a
   licence to pick a different deck for that cell.

### 2.5 Task-inclusion rule for val — declared now so selection cannot be outcome-driven
- Run the reference gate on **all 17 val tasks**.
- Then include val tasks **in ascending order of reference wall-clock time**, taking whole
  tasks (**all 11 cells × 3 seeds**, no cell or seed subsetting), until either all gate-passing
  tasks are done or the wall-clock budget is exhausted.
- Cheapness is measured on the **reference** only — i.e. on data that carries no information
  about any cell's SOF — so the ordering is orthogonal to the outcome.
- If the budget forces a stop mid-list, the stopping point and the tasks not reached are
  recorded. **Partially-run tasks are excluded from the primary analysis** (a task with only
  some cells done would be a biased sample of cells) and reported separately.

### 2.6 Exclusion / normalisation rules — J2's, applied identically
- Live quantity set `Q_t` and per-quantity scale `S_q` come from the **reference alone**, so
  they are byte-identical across cells and seeds.
- Admissibility (J2 §1.3 / §3.2, `J2_metric.admissible`): drop bookkeeping/index arrays,
  solver diagnostics, the scalar table's independent variable, subnormal (uninitialised)
  arrays, and quantities numerically constant in the reference (`CONST_RTOL = 1e-9`).
- Absent quantity in a generated bundle → **δ = +∞ → ψ = 0**: coverage penalty stays inside
  the metric.
- Non-executing run → **SOF_all = 0**, excluded from `SOF_ran`. Status taxonomy is J2's.
- Constitutive-array names canonicalised to solver-defined types, with bag merging for
  repeated types (J2 §7.5), so the metric cannot secretly measure naming.
- **The 600 s cap, the copy rule, the gap-fill rule and the injection are identical for
  reference and generated decks and identical across every cell.**
- **No run is dropped post hoc.** Any exclusion must follow a rule stated above and is logged.

### 2.7 Val-vs-held-out analysis, declared in advance
- Report ρ separately for **val** and **held-out**, and pooled, each with per-task range and I².
- Test the split difference by comparing the two Fisher-z pooled estimates
  (z-test on z₁ − z₂ with SE = √(1/w₁ + 1/w₂)).
- **Both outcomes are pre-declared as results:**
  - if SOF varies substantially on val while TreeSim is at ceiling (val cell means 0.913–0.921),
    that is a sharp demonstration that structural agreement does not imply simulation agreement;
  - if SOF is *also* at ceiling on val, that is equally informative — it localises all the
    signal in the held-out hard tail.
  Whichever occurs is reported as the headline. Ceiling is quantified by the fraction of val
  runs with SOF ≥ 0.999 and by the IQR, not by eyeball.

### 2.8 Cell separation — phrased as detectability, never as "no difference"
- SIGA = every non-`F0` cell; Vanilla = `F0`. Mann–Whitney two-sided, plus Kruskal–Wallis
  across all cells, per task and pooled.
- Any null is reported as **"not detectable at this n"** together with the n per arm that
  *would* be needed at the observed effect size. J2's held-out figure is n ≈ 26 000 per arm.
- No threshold τ is reported as a single number; the whole curve or nothing.

### 2.9 Falsifiable predictions (so the result can disappoint)
1. Pooled ρ at the final n stays inside J2's CI [0.23, 0.55]. **If ρ falls below 0.23 or
   loses significance at higher n, that is the finding and it goes at the top of the report.**
2. The worst-reduction aggregator stays non-significant. If it *becomes* significant at higher
   n, J2's largest sensitivity has been resolved by power, and that is reported as such.
3. Val SOF is nearer ceiling than held-out SOF (val tasks are the harness development set).
4. The cell contrast remains undetectable. A *detectable* cell contrast at n > 400 would be a
   genuinely new positive result and would need its own adversarial check before being quoted.

### 2.10 Reproducibility discipline
- Every per-run result is appended to `K3_*` CSV/JSONL **as it completes**, never held only in
  context.
- The 108 held-out rows are **re-scored with the identical code path** and must reproduce
  J2's `SOF_all` bit-exact; a mismatch is a blocker, not a footnote.
- Parallelism capped at **8 workers**; machine load checked before each launch (K1 and K4 are
  also active). Load at 09:55Z: `load average 69.65` on 128 cores, 261 GB free — 8 GEOS
  workers is a ~6 % addition to the core count.

---

## 3. AMENDMENTS to the pre-registration — declared before any generated deck was executed

All four were forced by inspecting the **ground-truth tree and the reference runs only**, and
all were fixed before a single generated val deck was executed. Each is mechanical, decided
from GT alone, and applied identically to reference and generated decks and identically across
cells. They are recorded here rather than folded silently into §2.

### R1 — timestamp discipline
`K3_repro.py` / `K3_repro.txt` written 09:55Z; §2 written 09:55Z; the first new GEOS process
of this thread started 10:0xZ (`K3_scratch/SMOKE_ref.jsonl`). Nothing in §2 was written after
a new number existed.

### R2 — `<Events maxTime>` may live anywhere in the root deck's `<Included>` closure
**Problem.** J2's rule (§7.2) requires the *root file itself* to carry `<Events maxTime>`.
Applied to val, that rejects **8 of 17 tasks** — not because they lack a final time, but
because many GEOS example decks put `<Events>` in the `*_base.xml` that the root
`<Included>`s.

**Amendment.** A root qualifies if a final time is found anywhere in its transitive
`<Included>` closure. Preference order (`smoke` > `benchmark` > lexicographic) unchanged. The
chosen filename is still used unchanged for every generated deck.

**Why this is not tuning.** (a) It is computed from GT alone, with no generated deck read, so
it cannot be outcome-driven. (b) A2's injector already walks the closure to find `<Events>` —
the *runner* was always closure-aware; only the *discovery rule* was not, so R2 removes an
inconsistency inside the inherited code rather than adding a degree of freedom. (c) **Regression
check: on the 5 held-out tasks present in `J2_task_registry.json`, the amended rule picks the
identical top deck in 5/5 cases** (`K3_task_registry_heldout.json`), so it cannot change any J2
number. The un-amended answer is stored per task as `top_j2_strict_rule` for audit.

### R3 — TriaxialDriver tasks use the scalar-table backend, by rule rather than by hand
A GT closure containing `<TriaxialDriver>` has no `<Events>` at all: the driver runs from
`<Tasks>` and writes a fixed-schema scalar table. Such a task uses J2 §1.1's **scalar-table
backend with no injection**. This is not new behaviour — it is exactly how J2 treated
`AdvancedExampleViscoExtendedDruckerPrager`, which entered J2's study through A2's table path
rather than through `J2_discover.py`. R3 turns that hand-placed registry entry into a
mechanical rule. It adds **4 val tasks** (DruckerPrager, ExtendedDruckerPrager,
ModifiedCamClay, ViscoDruckerPrager) at ~5 s per run.

### R4 — output-shaped files are PURGED from the run directory before the run
**This one is a fairness bug I had to fix, and it is worth reading.**

GT `inputs/` for the four TriaxialDriver tasks ships `<Model>Results.txt` — *and that is also
the filename the run itself writes* (the deck's `TriaxialDriver output=` attribute). J2's copy
rule copies the **entire** source tree, so GT's shipped results table lands in the **reference**
run directory. It does *not* land in any generated run directory, because J2's gap-fill
explicitly refuses to copy anything whose name contains `Results`/`results`/`output`/`Output`
(A2's near-miss guard). The table backend then globs `*.txt` and reads the first parseable one.

So a reference run that *failed* could have been scored against **GT's own shipped answer**
while every generated deck was scored against its own output — a reference/generated asymmetry
of precisely the kind that was J2's bug 4. J2's runner *recorded* such files
(`stale_outputs_before_run`) but never removed them; J2 never hit it because its one
table-backend task came through A2's path, whose copy rule copied only `*.xml` + `tables/`.

**Amendment.** `K3_run_task.py` deletes every output-shaped file from the run directory after
the copy and gap-fill and **before** the run, records the deleted list (`purged_output_shaped`),
records the `.txt` inventory with mtimes before and after the run, and — on the table backend —
**refuses to score a table that this run did not write** (`table_written_by_run`, else
`qoi_fail_stage = extract`). Applied identically to reference and generated decks.

Verified on the first smoketest: `AdvancedExampleDruckerPrager` reference,
`purged_output_shaped = ['DruckerPragerResults.txt']`,
`txt_written_by_run = ['DruckerPragerResults.txt']`, `table_written_by_run = true`, 9 quantities.

### R5 — external-asset staging is NOT extended (deliberate, coordinated with K1)
`ExampleMandel`'s GT reference fails at parse time: `PoroElastic_Mandel_base.xml` references
`mandel_tables/xlin.geos`, which **is not in `experiments_gt/ExampleMandel/inputs/`** but *does*
exist upstream at `/data/jixuan/geophysics/GEOS/inputFiles/poromechanics/mandel_tables/`.
This is K1's `missing_external_asset` category (32/273 of A1's rung-3 failures).

**Decision: K3 does not stage assets from the upstream GEOS repository.** Reasons:
1. Changing where reference assets come from changes what "the ground truth" *is*, mid-study.
2. J2's held-out 6 were gated under the shipped-asset rule. Staging for val but not for
   held-out would make the two splits incomparable — and the val-vs-held-out contrast is the
   scientific point of this thread.
3. **K1 owns staging.** Two threads publishing different asset-resolution rules is worse than
   one thread having fewer tasks. K1's log was still at "orienting" at 10:0xZ, so there was no
   rule to adopt.

Consequence: such tasks are `task_unusable`, reason `missing_external_asset_in_GT`, recorded
per task and reported as a finding. If K1 lands a staging rule with time to spare, the val
grid is resumable per task (`K3_grid.py` skips completed work), so a staged arm can be added
as a clearly-separated secondary analysis rather than by rewriting the primary.

### R4a — the purge rule cannot manufacture a failure (audited, not assumed)
A purge rule can be dangerous: if a deck legitimately *reads* an input file whose name happens
to contain `output`/`Results`, deleting it would manufacture a deck failure. So the risk was
measured rather than argued.

```
scanned 2889 generated input files (all 180 held-out + all 561 val deck sets)
output-shaped files in GENERATED deck sets: 0
output-shaped files in GT inputs (purged from REFERENCE dirs only): 6
    AdvancedExampleViscoExtendedDruckerPrager  ViscoExtendedDruckerPragerResults.txt
    AdvancedExampleDruckerPrager               DruckerPragerResults.txt
    AdvancedExampleExtendedDruckerPrager       ExtendedDruckerPragerResults.txt
    AdvancedExampleModifiedCamClay             ModifiedCamClayResults.txt
    AdvancedExampleViscoDruckerPrager          ViscoDruckerPragerResults.txt
    pknViscosityDominated                      model-results.txt
```

**Not one of the 2889 agent-authored input files is output-shaped**, so R4's purge can only
ever touch a ground-truth reference directory, and there it touches exactly 6 files — every one
of them a GT-shipped *answer* file. The risk of the purge inventing a failure is therefore
empirically zero, and the 6 removals each close a path by which GT's own answer could have been
read back as a run's output. `purged_output_shaped` is recorded per run either way.

---

## 4. CROSS-THREAD CHECKS before trusting K3's own harness

`OVERNIGHT_DECISIONS.md`: *"Every thread must cross-check against an existing artifact before
trusting its own harness."* Three checks, all passed before any grid was launched.

### 4.1 TreeSim loader vs A2's held-out artifact — 180/180 exact
`K3_paths.treesim("heldout")` reads the raw `*_eval.json` files independently. Compared to
`A2_treesim_heldout_raw.csv` (A2's published 180 rows, value **and** `scored` flag):
**0 mismatches out of 180.** Including the one unscored run
(`ExampleProppantTest F0_s3`, treesim 0.0, scored 0) — so K3 inherits the paper's
failures-as-zero convention identically.

### 4.2 TreeSim loader vs Thread D's *verified* Table-1 val column — 11/11 exact
The val split had no equivalent published raw CSV, so the check went through D's verified
aggregate (failures-as-zero, sample sd over the 3 seed means — the convention D pinned as the
one Table 1 actually prints):

```
cell   K3 mean   D mean   K3 sd     D sd
F0     0.909586   0.9096  0.023563  0.0236
F1     0.884845   0.8848  0.013622  0.0136
F2     0.919084   0.9191  0.003664  0.0037
F3     0.856720   0.8567  0.044876  0.0449
F4     0.921363   0.9214  0.007051  0.0071
F5     0.892798   0.8928  0.032871  0.0329
F6     0.916645   0.9166  0.003810  0.0038
F7     0.885257   0.8853  0.008288  0.0083
F8     0.910998   0.9110  0.018032  0.0180
F11    0.896547   0.8965  0.031609  0.0316
SE     0.919124   0.9191  0.020056  0.0201
ALL 11 CELLS MATCH: True
```

**All 11 val cells reproduce to 4 dp in both mean and σ.** K3's val TreeSim vector is therefore
the same data Table 1 was computed from, not a re-derivation that happens to look similar.

### 4.3 Top-deck rule vs J2's registry — 5/5 exact
See R2: the amended discovery rule picks J2's top deck on all 5 held-out tasks that appear in
`J2_task_registry.json`.

### 4.4 Held-out SOF re-score vs `J2_per_run.csv` — asserted in code
`K3_score.py` produces the 108 held-out rows by calling **J2's own `run_metric()`** and then
asserts, row by row and column by column (`SOF_all`, `SOF_wc_all`, `status`, `ran`, `treesim`),
that they reproduce `J2_per_run.csv`. A mismatch calls `sys.exit(2)` — it is a blocker, not a
footnote.

### R6 — degenerate (zero-variance) tasks: declared BEFORE any val SOF value was computed
Declared 10:14Z, while the val reference gate was still running and before `K3_score.py` had
been run even once.

A task where every run scores the identical SOF (J2 already had one: `singleFracCompression`,
10 of 12 executing runs exactly 1.0000) carries **no rank information**, but under the
pre-registered within-task-percentile-rank estimator it still contributes its n to the pooled
correlation, diluting ρ toward 0. If val turns out to be near ceiling this could matter a lot,
and I do not want to be choosing how to handle it after seeing the number.

**Rule, fixed now:** the pre-registered primary stays exactly as declared in §2.2 — nothing is
dropped. In addition, two diagnostics are always reported next to it:
1. the count of tasks with zero variance in SOF (and in TreeSim), per split;
2. pooled ρ recomputed with zero-variance tasks excluded, labelled a **sensitivity, not the
   headline**.
The meta-analysis is unaffected by construction: a task with |ρ| undefined or ≥ 1 is already
skipped by the Fisher-z step, and `K3_validate.py` prints those tasks explicitly rather than
letting them vanish.

---

## 5. REFERENCE-GATE RESULTS — the gate did most of the work

`K3_scratch/val_ref_gate.jsonl`, `K3_scratch/heldout_ref_gate.jsonl`, rolled up into
`K3_ref_gate.csv`. Every outcome below was decided from the **ground-truth reference deck
alone**, before any generated deck of that task was executed.

### 5.1 val split — 9 of 17 tasks usable

| task | backend | ref wall | outcome | usable |
|---|---|---:|---|---|
| AdvancedExampleDruckerPrager | table | 5.4 s | L3 ✓ L4 ✓, 9 quantities, 4 live | **YES** |
| AdvancedExampleModifiedCamClay | table | 7.6 s | L3 ✓ L4 ✓, 9 q, 4 live | **YES** |
| AdvancedExampleViscoDruckerPrager | table | 8.7 s | L3 ✓ L4 ✓, 9 q, 4 live | **YES** |
| AdvancedExampleExtendedDruckerPrager | table | 9.1 s | L3 ✓ L4 ✓, 9 q, 4 live | **YES** |
| AdvancedExampleDeviatedElasticWellbore | mesh | 9.6 s | L3 ✓, 10 q, 7 live | **YES** |
| ExampleDPWellbore | mesh | 9.6 s | L3 ✓, 11 q, 8 live | **YES** |
| AdvancedExampleCasedContactThermoElasticWellbore | mesh | 10.2 s | L3 ✓, 61 q, 26 live | **YES** |
| TutorialPoroelasticity | mesh | 11.5 s | L3 ✓, 30 q, 9 live | **YES** |
| ExampleEDPWellbore | mesh | 246.5 s | L3 ✓, 11 q, 8 live | **YES** |
| ExampleMandel | mesh | 6.9 s | **GT asset missing**: `mandel_tables/xlin.geos` not in GT `inputs/` | no |
| ExampleIsothermalLeakyWell | mesh | 7.2 s | **GT asset missing**: `xlin.geos` | no |
| ExampleThermalLeakyWell | mesh | 8.1 s | **GT asset missing**: `phaseVolumeFraction_water.txt` | no |
| buckleyLeverettProblem | mesh | 174.8 s | **GT reference diverges**: floating-point error (signal handler) | no |
| kgdExperimentValidation | mesh | 600.5 s | **wall-clock cap** | no |
| TutorialSneddon | mesh | 601.4 s | **wall-clock cap** | no |
| pknViscosityDominated | mesh | 601.3 s | **wall-clock cap** | no |
| ExampleThermoporoelasticConsolidation | — | — | **GT `<Included>` reference missing** (below) | no |

**→ 9 usable val tasks × 11 cells × 3 seeds = 297 runs.**

### 5.2 held-out split — the two J2 exclusions re-checked cheaply, both confirmed

| task | ref wall | outcome | matches J2? |
|---|---:|---|---|
| `ExampleIsothermalHystInjection` | 3.3 s | fails at `run` — the `<Included>` file `class09_pb3_hystRelperm_direct_base.xml` still does not exist anywhere in the GT tree (re-verified by `find`) | **yes, J2 §7.4 G2** |
| `TutorialHydraulicFractureWithAdvancedXML` | 0.4 s | fails at `injection` — `<Events maxTime="$t_max$">` is a GEOS *parameter substitution*, so the injector cannot compute a final-time event. A2 had already excluded this task on TreeSim grounds (0.013 in every cell); this is an independent, reference-side reason | new, and it is a *reference-side* reason so it supersedes A2's outcome-side one |
| `ExampleMCCWellbore` | **600.09 s** | wall-clock cap, re-run by K3 rather than inherited | **yes, A2** |
| `ExampleVerticalPoroElastoPlasticWellbore` | **600.20 s** | wall-clock cap, re-run by K3 | **yes, J2 §7.4 G1** |

All four were **executed by K3**, not inherited on trust
(`K3_scratch/heldout_ref_gate.jsonl`). Every one reproduces the disposition A2/J2 recorded.

**No new held-out task became usable.** K1's asset-staging work (see R5) does not address either
blocker: one is a missing *XML include*, the other a *parameter-substituted maxTime*, neither of
which is an external data asset.

### 5.3 (WITHDRAWN — see §6.3) ~~NEW FINDING — a SECOND ground-truth task set that cannot run at all~~

> **WITHDRAWN 10:22Z.** The two "missing" base decks **do exist**, upstream in the GEOS
> repository; my `find` searched `experiments_gt/` only. The corrected — and stronger — finding
> is that the evaluation harness's asset harvest drops XML `<Included>` targets as well as data
> assets. See §6.3. Text kept verbatim below for audit.

J2 §7.4 G2 reported one held-out task (`ExampleIsothermalHystInjection`) whose GT deck set
`<Included>`s a file that does not exist. **The val split contains a second instance:**

```
ExampleThermoporoelasticConsolidation, GT inputs/ contains:
    ThermoPoroElastic_consolidation_base.xml
    ThermoPoroElastic_consolidation_benchmark_fim.xml   -> <Included> ..._benchmark_base.xml
    ThermoPoroElastic_consolidation_smoke_fim.xml       -> <Included> ..._smoke_base.xml

find over the ENTIRE experiments_gt/ tree:
    ThermoPoroElastic_consolidation_benchmark_base.xml  -> 0 hits
    ThermoPoroElastic_consolidation_smoke_base.xml      -> 0 hits
```

~~**Both** of its root decks reference a base file that exists nowhere in the ground truth. So
**2 of the 27 tasks in the two evaluation splits ship a ground-truth deck set that is
internally inconsistent and cannot be executed by anyone.**~~ **← WRONG; withdrawn, see §6.3.**
The `find` above covered `experiments_gt/` only. Both files exist in the GEOS upstream
repository, so both tasks are made unrunnable by *our harvest*, not by the benchmark.

### 5.4 Honest accounting of *why* 8 val tasks were dropped
Four distinct causes, and only one of them is about cost:

| cause | n tasks | what it means |
|---|---:|---|
| GT external asset not shipped in `inputs/` | 3 | harness staging gap (K1's category); the asset exists upstream in the GEOS repo but K3 deliberately does not stage it (R5) |
| GT `<Included>` file missing from the whole GT tree | 1 | the benchmark ships an unrunnable ground truth (§5.3) |
| GT reference itself diverges (floating-point error) | 1 | the reference has no final state to compare against |
| 600 s wall-clock cap | 3 | **a disclosed cost limit**, identical for reference and generated, identical across cells |

Only the last group could be recovered by spending more compute, and recovering it would
require re-running the whole study at a larger cap to keep the cap identical everywhere — so it
is recorded as a limitation rather than partially fixed.

---

## 6. COURSE CORRECTION 10:22Z — val is contaminated on BOTH axes; design revised

Threads K1 and K2 finished while K3's unstaged val grid was queued, and between them they
invalidated the val arm as I had built it. Recorded in full because the correction changes what
K3 can claim.

### 6.1 What K1 found (y-axis: the SOF side)
- **103 of 561 val task-runs reference external assets that were never staged into the run
  directory** — the evaluation harness's asset harvest dropped them.
- **On val this tracks cell identity, so it is a fairness confound, not noise:**
  `F11 0/51` and `SE 0/51` versus `F3 16/51`, `F5 15/51`. **The two cleanest cells are the two
  SE cells** — exactly the cells that would look best in a val comparison.
- **A1's licensing premise does not generalise to val.** On held-out all six cells referenced
  identical assets (which is what made the confound symmetric); on val only **34 of 51
  (task, seed) groups** have identical asset sets across the 11 cells.

**I reproduced all of this independently** with `K3_pools.py` (which imports K1's rule
functions and changes only the directory enumeration): per-cell staging-artifact counts
`F0 5, F1 14, F2 7, F3 16, F4 11, F5 15, F6 10, F7 14, F8 11, F11 0, SE 0` out of 51 —
**identical to K1's published numbers**, and the same 3 agent-invented references
(`F1/s1 DruckerPrager tables/zeroStrain.geos`, `F3/s1 ViscoDruckerPrager tables/zeroStrain.geos`,
`F6/s1 ThermalLeakyWell temp_bc.geos`).

### 6.2 What K2 found (x-axis: the TreeSim side)
**The val scoring pass raced the val campaign.** `autocamp_F3_s1`'s `_summary.json` finished
scoring at 14:25:28 while the decks it scored were written 14:25:41–14:32:37. So the published
val TreeSim values cannot all be reproduced from the decks now on disk (`published != strict`
on 4 val runs: F3_s1 ×3, F11_s2 ×1). Held-out is clean — K2 verified `published == strict` on
all 180 held-out runs, worst diff 0.00e+00.

**This retroactively reframes my own §4.2 cross-check.** Reproducing D's verified Table-1 val
column 11/11 exactly proved my loader reads the same data Table 1 was computed from — it did
**not** prove that data is correct, because Table 1 itself inherits the race. The check was
sound; my reading of what it licensed was too strong. Corrected here rather than quietly.

### 6.3 CORRECTION to my own §5.3 — I overclaimed, and K1's tooling caught it
§5.3 claimed `ExampleThermoporoelasticConsolidation` shows "a second ground-truth task set that
cannot run at all", generalising J2's finding G2. **That claim is wrong and is withdrawn.**

Its two missing `<Included>` base decks **do exist**, upstream in the GEOS repository:
```
ThermoPoroElastic_consolidation_benchmark_base.xml -> data/GEOS/inputFiles/thermoPoromechanics/...
ThermoPoroElastic_consolidation_smoke_base.xml     -> data/GEOS/inputFiles/thermoPoromechanics/...
```
and so does the file that made J2 declare `ExampleIsothermalHystInjection` unrunnable
(`class09_pb3_hystRelperm_direct_base.xml`, found by K1 in
`compositionalMultiphaseWell/benchmarks/Class09Pb3/`). My `find` searched `experiments_gt/`
only — the same mistake J2 made, and it produced the same wrong conclusion.

**The corrected finding is different, and stronger as evidence about the pipeline rather than
about the benchmark:** the evaluation harness's asset harvest **drops XML `<Included>` targets
as well as data assets**. Two of the 27 tasks in the two splits have a ground-truth deck set
with a dangling XML include, and in **both** cases the missing file exists upstream. So neither
task is intrinsically unrunnable; both were made unrunnable by our own harvest. J2's G2 needs
the same amendment — flagged for J2/the brief.

### 6.4 The design I chose, and why
> **Held-out is the primary. Val is a disclosed secondary with both contaminations fixed.**

| | x-axis (TreeSim) | y-axis (SOF) | role |
|---|---|---|---|
| **held-out, 6 J2 tasks, n = 108** | published == strict, verified by K2 on all 180 | **provably unaffected by staging** (see 6.5) | **PRIMARY** |
| **val, staged, K2-rescored** | K2 `treesim_strict`, re-scored from the decks on disk | K1 pool staged into every cell + GT, fairness invariant proved | **SECONDARY, disclosed** |
| val, unstaged | — | unstaged | **confound measurement only, never a headline** |

I did not take the "held-out only" option, because both fixes were already available as
finished artifacts (`K1_stage.py` split-agnostic; `K2_rescored_val.jsonl`, 561 runs) and
applying them is mechanical and auditable. Reporting val *as a secondary with both defects
fixed and both disclosed* strictly dominates dropping it — provided the primary does not depend
on it, which is why held-out is the primary. **If the staged val arm and the held-out arm
disagree, the disagreement is the result and held-out wins the headline.**

### 6.5 Held-out is provably unaffected by staging — checked, not assumed
`K3_pools.py --split heldout` finds a non-empty asset pool for exactly **two** held-out tasks:
`ExampleIsothermalHystInjection` (25 assets — not one of J2's 6) and
`ExamplesingleFracCompression` (**1** asset, `crackInPlane_benchmark.vtu`, resolved `gt_exact`).
J2's protocol already gap-fills GT assets, and on disk:

```
18/18 generated singleFrac run dirs + the reference all contain crackInPlane_benchmark.vtu
```

So for J2's 6 usable held-out tasks the staged and unstaged environments are **identical**, and
the 108 primary rows need no re-run. (Minor artifact-vs-prose correction: J2 §7.6 says the
`.vtu` was filled into 11 of 18 dirs; `J2_scratch/grid.jsonl` records **12** filled and 6
already present. Immaterial — every dir ends up with it — but the artifact is the authority.)

### 6.6 Staging rule adopted, with one amendment
**R7 — XML `<Included>` targets are pooled and staged.** K1 deliberately excluded XML because
its rung-3 sweep executes *every* root deck, so an extra XML could turn a fragment into a new
root. **K3 always executes exactly one declared top deck chosen from GT**, so an extra XML
cannot become a root here. K1's own isolating experiment (Entry 5, arm B) verified that staging
the XML is a no-op on the generated side and is precisely what makes Hyst's ground truth
runnable (GT 0/1 → 1/1). Everything else is K1's rule, imported from `K1_stage.py`:
per-task pool = union over all cells + GT, whole pool installed into every environment,
existing files never overwritten, agent-invented references never staged.

**Fairness invariant proved for val** (`K3_pools_val_out.txt`): for all 10 pooled tasks, all
**34 environments** (33 cell-seeds + GT) end up with identical asset-path sets.
```
OK  AdvancedExampleDruckerPrager          34 envs,  3 pool assets available in all
OK  AdvancedExampleExtendedDruckerPrager  34 envs,  3 pool assets available in all
OK  AdvancedExampleModifiedCamClay        34 envs,  3 pool assets available in all
OK  AdvancedExampleViscoDruckerPrager     34 envs,  3 pool assets available in all
OK  ExampleIsothermalLeakyWell            34 envs,  4 pool assets available in all
OK  ExampleMandel                         34 envs,  8 pool assets available in all
OK  ExampleThermalLeakyWell               34 envs, 13 pool assets available in all
OK  ExampleThermoporoelasticConsolidation 34 envs,  2 pool assets available in all
OK  TutorialPoroelasticity                34 envs,  1 pool asset  available in all
OK  buckleyLeverettProblem                34 envs,  2 pool assets available in all
FAIRNESS INVARIANT HOLDS
```

### 6.7 R8 — staged-arm discovery must run on the STAGED tree
Found while the staged gate was running: `ExampleThermoporoelasticConsolidation` still came back
`no_top_deck` in the staged arm, because the **registry** was built from the raw GT tree, where
the dropped `<Included>` base decks make *no* root carry a final time. Discovery and execution
have to see the same tree.

**Rule:** in the staged arm, top-deck discovery runs on `GT inputs/ + the task's staged pool`
(a temp copy — GT is read-only and never modified), producing
`K3_task_registry_<split>_staged.json`. Effect, measured:

```
val:      1 of 17 tasks changes  (ExampleThermoporoelasticConsolidation: None ->
                                  ThermoPoroElastic_consolidation_smoke_fim.xml, maxTime 100001)
          16 of 17 identical to the unstaged registry
held-out: 0 of 10 tasks change
```

So R8 is inert everywhere except the one task whose GT include was dropped — which is exactly
the case it exists for, and it is decided from GT+pool with no generated deck read.

### 6.8 Sanity checks on the staging implementation
- **The purge (R4) and staging (R7/D3) cannot conflict:** no pool member on either split has an
  output-shaped basename, checked exhaustively — so the purge can never delete a staged asset.
- **Staging order:** copy (+`copy_complete` assertion) → stage pool → purge output-shaped →
  inject → run. Recorded per run as `pool_size`, `staged`, `staged_kept_existing`,
  `staged_removed_dangling`.
- **`ExampleMandel`'s reference now passes** (6.6 s, 8 assets staged into the generated dirs,
  all 8 `kept_existing` in GT since they resolve `geos_canonical_exact` and GT lacks them —
  see the manifest), where unstaged it failed at parse on `mandel_tables/xlin.geos`.
- **`ExampleIsothermalLeakyWell` still fails the staged reference gate** at 25 s (not a
  timeout), so its exclusion is not an asset problem. Cause recorded in its `run.log`.

### 6.9 The corrected finding, confirmed by execution
`ExampleThermoporoelasticConsolidation`, staged reference run
(`K3_scratch/refruns/REF__val_staged__ExampleThermoporoelasticConsolidation`):

```
staged: ['ThermoPoroElastic_consolidation_benchmark_base.xml',
         'ThermoPoroElastic_consolidation_smoke_base.xml']
wall 10.63 s   L3 = True   L4 = True   reached_final_time = True   34 quantities
```

**Unstaged it could not even be assigned a top deck; staged its ground truth runs cleanly in
10.6 s.** Together with K1's `ExampleIsothermalHystInjection` result (GT 0/1 → 1/1 once the
dropped include is staged), that makes **2 for 2**: every task whose ground truth appeared
"internally inconsistent and unrunnable" was in fact made unrunnable by the evaluation
harness's own asset harvest, which drops XML `<Included>` targets as well as data assets.
**J2 §7.4 G2's finding, and my own §5.3, are both artifacts of searching `experiments_gt/`
instead of the GEOS source tree.** This should be corrected wherever G2 is quoted.

### 6.10 Messages back to the other threads (K3's obligations to them)
1. **To J2 / the revision brief:** §7.4 **finding G2 must be amended.**
   `ExampleIsothermalHystInjection`'s ground truth is **not** intrinsically broken — the missing
   include exists upstream in the GEOS repository and K1 showed GT passes 1/1 once it is staged.
   The `find` that established G2 covered `experiments_gt/` only. The correct statement is about
   our harvest, not the benchmark.
2. **To K1:** K3 independently reproduced K1's val staging-artifact counts exactly
   (`F0 5, F1 14, F2 7, F3 16, F4 11, F5 15, F6 10, F7 14, F8 11, F11 0, SE 0` of 51) and the
   same 3 agent-invented references, using `K1_stage.py`'s own rule functions. K3 adds one
   amendment K1 could not safely make (R7: XML includes pooled, valid because K3 executes a
   single declared top deck) and one new confirmation: with the two dropped base decks staged,
   **`ExampleThermoporoelasticConsolidation`'s ground truth runs cleanly in 10.6 s (L3 ✓ L4 ✓,
   34 quantities)** — a second instance of the XML-harvest bug, on the val split.
3. **To K2:** K3 independently confirmed `published == strict` on **all 180 held-out runs**
   (0 differ) and found exactly **4** val differences, the ones K2 flagged:
   `TutorialPoroelasticity F3_s1` 0.2371→0.7185, `TutorialSneddon F3_s1` 0.0→0.8993,
   `ExampleIsothermalLeakyWell F3_s1` 0.7032→0.8610, `pknViscosityDominated F11_s2` 0.0→0.9795.
   Two of those were failures-as-zero placeholders in the published data that the re-score
   rescues — so the race did not only perturb values, it manufactured two spurious zeros.
4. **To whoever writes the response:** the val split now carries **two disclosed pipeline
   defects**. If any val number is used anywhere in the response, it must be the staged +
   re-scored version, and the defects must be stated.

---

## 7. STAGED REFERENCE GATE — 11 of 17 val tasks usable (up from 9 unstaged)

`K3_scratch/val_staged_ref_gate.jsonl` (17 records, all executed).

| task | backend | ref wall | staged outcome | unstaged outcome | usable |
|---|---|---:|---|---|---|
| AdvancedExampleDruckerPrager | table | 7.7 s | L3 ✓ L4 ✓ | pass | **YES** |
| AdvancedExampleViscoDruckerPrager | table | 7.2 s | L3 ✓ L4 ✓ | pass | **YES** |
| AdvancedExampleModifiedCamClay | table | 7.7 s | L3 ✓ L4 ✓ | pass | **YES** |
| AdvancedExampleExtendedDruckerPrager | table | 7.9 s | L3 ✓ L4 ✓ | pass | **YES** |
| AdvancedExampleDeviatedElasticWellbore | mesh | 8.3 s | L3 ✓ | pass | **YES** |
| TutorialPoroelasticity | mesh | 8.5 s | L3 ✓ | pass | **YES** |
| ExampleDPWellbore | mesh | 8.5 s | L3 ✓ | pass | **YES** |
| AdvancedExampleCasedContactThermoElasticWellbore | mesh | 9.7 s | L3 ✓ | pass | **YES** |
| **ExampleMandel** | mesh | **6.3 s** | **L3 ✓ — 8 assets staged** | fail (missing `mandel_tables/xlin.geos`) | **YES (new)** |
| **ExampleThermoporoelasticConsolidation** | mesh | **10.6 s** | **L3 ✓ L4 ✓ — 2 XML includes staged** | fail (no top deck at all) | **YES (new)** |
| ExampleEDPWellbore | mesh | 254.2 s | L3 ✓ | pass | **YES** |
| ExampleIsothermalLeakyWell | mesh | 24.9 s | **GT diverges** — floating-point error | fail (missing asset) | no |
| buckleyLeverettProblem | mesh | 178.7 s | **GT diverges** — floating-point error | fail (same) | no |
| **ExampleThermalLeakyWell** | mesh | **600.3 s** | **wall-clock cap** | fail at 8 s (missing asset) | no |
| kgdExperimentValidation | mesh | 600.1 s | wall-clock cap | same | no |
| TutorialSneddon | mesh | 601.1 s | wall-clock cap | same | no |
| pknViscosityDominated | mesh | 601.2 s | wall-clock cap | same | no |

**→ 11 usable val tasks × 11 cells × 3 seeds = 363 runs**, plus the 108 held-out primary rows =
**471**, against a pre-registered target of 206. Task count **17** (6 held-out + 11 val),
clearing the k ≥ 12 secondary target.

Two things worth noting in the staged-vs-unstaged column:
- Staging **unblocked 2 tasks** (Mandel, ThermoporoelasticConsolidation), exactly the two whose
  failures were harvest artifacts.
- Staging **converted `ExampleThermalLeakyWell` from an asset failure at 8 s into a wall-clock
  failure at 600 s.** It is still excluded, but the reason changed from "our harness lost a
  file" to "this reference is expensive" — a more honest exclusion, and one that would have been
  mis-attributed without staging.
- The two floating-point divergences (`ExampleIsothermalLeakyWell`, `buckleyLeverettProblem`)
  survive staging, so those exclusions were never about assets.
