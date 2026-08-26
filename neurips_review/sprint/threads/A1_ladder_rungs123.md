# Thread A1 — Validity ladder, rungs 1–3, HELD-OUT split

**Submission:** NeurIPS 2026 #31642 (SIGA)
**Scope:** rung 1 (well-formed XML), rung 2 (XSD schema-valid), rung 3 (`geosx --validate-input`)
**Split:** held-out ICL eval — `/data/shared/geophysics_agent_data/data/eval/autocamp_followup_2026-05-02/icl/`
**Cells:** autocamp_F0 (Vanilla), F4 (X+M), F6 (S+X), F8, F11, SE
**Artifacts dir:** `/home/matt/sci/repo3/neurips_review/sprint/artifacts/`

---

## 2026-07-26 — Entry 1: orientation

### Commands run

```bash
ls /data/shared/geophysics_agent_data/data/eval/autocamp_followup_2026-05-02/icl/
# -> autocamp_F0 autocamp_F11 autocamp_F4 autocamp_F6 autocamp_F8 autocamp_SE

cd /data/shared/geophysics_agent_data/data/eval/autocamp_followup_2026-05-02/icl
for c in autocamp_F0 autocamp_F4 autocamp_F6 autocamp_F8 autocamp_F11 autocamp_SE; do
  for s in $c/*/; do n=$(ls -d $s*/ | wc -l); echo "$s -> $n tasks"; done; done
# -> every cell: 3 seed dirs (s1,s2,s3), each with 10 task dirs => 30 task-runs/cell, 180 total
```

Note on directory naming: the seed dirs are `<CELLSHORT>_icl_s<N>` (e.g. `autocamp_F0/F0_icl_s1`),
not `<cell>_icl_s<N>` as the task brief stated. No impact.

Tool availability confirmed:
- `xmllint` = `/data/matt/miniconda3/bin/xmllint`
- XSD = `/home/matt/sci/repo3/data/GEOS/src/coreComponents/schema/schema.xsd` (632 761 bytes)
- `geosx` = `/data/jixuan/geophysics/GEOS/install-your-platform-release/bin/geosx`
  (also `GEOSX_EXECUTABLE` in `/home/matt/sci/repo3/.env`)

### DECISION: deck-selection rule (scorer-faithful)

Read `/home/matt/sci/repo3/src/eval/judge_geos.py`. The official scorer's entry point for a
generated task-run is `evaluate_directories` -> `load_and_resolve_dir(generated_dir)`
(judge_geos.py:112–147). The rule it implements:

```python
112  def load_and_resolve_dir(directory: Path) -> ET.Element:
113      xml_files = sorted(directory.rglob("*.xml"))
114      if not xml_files:
115          raise FileNotFoundError(f"No XML files found in {directory}")   # -> error type "missing_xml"
...
119      for xml_file in xml_files:
121          parsed[xml_file.resolve()] = ET.parse(xml_file).getroot()
123          parse_errors.append(...)                                        # unparseable files collected
125      if parse_errors and not parsed:
126          raise ValueError(...)                                           # -> error type "xml_parse_error"
128      referenced: set[Path] = set()
129      for file_path, root in parsed.items():
130          for file_tag in root.iter("File"):                              # <Included><File name="..."/>
131              rel = file_tag.get("name") or file_tag.get("Name", "")
134              candidate = (file_path.parent / rel).resolve()
135              if candidate.exists():
136                  referenced.add(candidate)
138      entries = [fp for fp in parsed if fp not in referenced]
139      if len(entries) == 1:
140          return _resolve_included(parsed[entries[0]], entries[0].parent, {entries[0]})   # <-- PRIMARY DECK
142      merged = ET.Element("Problem")                                      # >1 root: ALL roots merged
143      for file_path, root in parsed.items():
144          resolved = _resolve_included(root, file_path.parent, {file_path})
145          for child in list(resolved):
146              merged.append(child)
147      return merged
```

**Rule adopted (identical to the scorer):** the *root decks* of a task-run are the XML files
under `<task>/inputs/` (recursive) that are **not** referenced by any other XML's
`<File name="...">` tag. Load-bearing line: **judge_geos.py:138** (`entries = [fp for fp in parsed
if fp not in referenced]`), with the single-root special case at **judge_geos.py:139–140**.

Consequences I will honour, so the ladder measures the same object the scorer scores:
- When a task-run has exactly 1 root deck, that file *is* the deck under evaluation.
- When it has >1 root deck (the common case here — GT tasks ship `*_base.xml` +
  `*_benchmark.xml` + `*_smoke.xml`, where `base` is `<Included>`-ed by the other two, leaving
  2 roots), the scorer merges **all** roots. The faithful ladder verdict for the task-run is
  therefore the **AND over its root decks** — every root deck must pass the rung.
- Per-deck results are stored in the raw artifacts so any other aggregation (e.g. "benchmark deck
  only", "any-root-passes") can be re-derived without re-running.
- Files that are `<Included>` fragments (e.g. `*_base.xml`) are **not** independently valid GEOS
  problems, so they are not validated standalone at rung 2/3; they are exercised transitively
  because `<Included>` resolution pulls them in.

### Rung-1 failure taxonomy (matches the scorer's own error classes)
- `missing` — no `*.xml` under `<task>/inputs/` at all (scorer: FileNotFoundError -> `missing_xml`)
- `empty` — a root deck file exists but is 0 bytes / whitespace only
- `unparseable` — `xmllint --noout` fails (not well-formed) (scorer: `xml_parse_error`)
- `schema_invalid` — well-formed but fails `xmllint --schema schema.xsd`
- `valid` — passes rung 2

---

## 2026-07-26 — Entry 2: SMOKETEST — and it already broke an assumption

### Command
```bash
cd /home/matt/sci/repo3/neurips_review/sprint/artifacts
python3 A1_rungs12.py --out /tmp/.../smoke.jsonl \
  --cells autocamp_F0 --seeds s1 --tasks AdvancedExampleThermoPoroElasticWellbore
```
Harness: `/home/matt/sci/repo3/neurips_review/sprint/artifacts/A1_rungs12.py`

### Raw result (F0 / s1 / AdvancedExampleThermoPoroElasticWellbore)
`inputs/` holds 3 XMLs:
- `ThermoPoroElasticWellbore_base.xml` — referenced (`<Included><File name=...>`) => not a root
- `ThermoPoroElasticWellbore_benchmark.xml` — root, **rung1 PASS, rung2 PASS**
- `ThermoPoroElasticWellbore_smoke.xml` — root, **rung1 FAIL (not well-formed)**

```
ThermoPoroElasticWellbore_smoke.xml:71: parser error : Double hyphen within comment: <!--
    <!-- ---- Solver time stepping ---- -->
```
(the model emitted `<!-- ---- ... ---- -->`; `--` inside a comment is illegal XML)

### *** SURPRISE / SCORER BUG: silent drop of unparseable decks ***

Because `smoke.xml` raises `ET.ParseError`, it never enters `parsed` (judge_geos.py:119-123),
so it cannot appear in `entries` (line 138, which iterates `parsed`). `entries` therefore
has length **1** (`benchmark.xml`) and the scorer takes the single-entry fast path
(line 139-140) and scores **only the benchmark deck**. The malformed smoke deck is
silently discarded and the run receives an ordinary non-zero TreeSim score.

The same silent-skip behaviour exists in `_resolve_included`: unparseable includes
(judge_geos.py:93-94) and non-existent includes (87-88) are skipped with `continue`.

**Consequence for this thread:** "schema-valid" is ambiguous and I must report *both*
framings, because they give different numbers:

- **Framing P (scorer-faithful / "primary deck")** — the deck(s) the scorer actually
  compared, i.e. `entries` from judge_geos.py:138 (unparseable files already dropped).
  This is what the reported TreeSim numbers were computed on.
- **Framing A (all-roots, strict)** — AND over every non-referenced XML the agent emitted,
  *including* ones that fail to parse. This is the reliability-relevant measure and the one
  the paper's "catastrophic failure" claim is actually about.

Both are derivable from the raw JSONL (`scorer_entries` + per-deck `decks[]` are recorded),
so no re-run is needed to switch framing.

### Decision
Scale to all 6 cells x 3 seeds x 10 tasks = 180 task-runs.
```bash
python3 A1_rungs12.py --out /home/matt/sci/repo3/neurips_review/sprint/artifacts/A1_rungs12_raw.jsonl
```

---

## 2026-07-26 — Entry 3: **DELIVERABLE 1 COMPLETE — rungs 1–2. The 24/30 claim REPRODUCES EXACTLY.**

### Headline
**No negative result at rungs 1–2.** `Vanilla (F0) 24/30 vs 30/30 for all five SIGA cells` is
**confirmed by re-run**, and every subsidiary number in `REBUTTAL_TRIAGE_v1.md:19-28` reproduces
to the digit (30 runs / 81 XML files / 76 well-formed / 73 schema-valid for F0).

### How I found which framing the plan doc used
My first sweep validated only *root* decks and got **26/30**, not 24/30. Tracked the discrepancy to
`neurips_review/REBUTTAL_TRIAGE_v1.md:21`, which counts **every `*.xml` in `inputs/`** (81 files for
F0), including `<Included>` fragments (`*_base.xml`). Re-ran at per-file granularity so all
framings are derivable from one artifact. Framing F reproduces the doc exactly.

```bash
cd /home/matt/sci/repo3/neurips_review/sprint/artifacts
python3 A1_rungs12_perfile.py     # 486 file rows -> A1_rungs12_perfile.csv
```

### Rung 1–2 table, framing F ("ALL files in inputs/ must pass") — the plan doc's framing
| Cell | runs (denominator) | XML files | well-formed | schema-valid | runs fully well-formed (rung 1) | **runs fully schema-valid (rung 2)** |
|---|---|---|---|---|---|---|
| autocamp_F0 (Vanilla) | **30** | 81 | 76 | 73 | 27 | **24 / 30** |
| autocamp_F4 (X+M)     | **30** | 81 | 81 | 81 | 30 | **30 / 30** |
| autocamp_F6 (S+X)     | **30** | 81 | 81 | 81 | 30 | **30 / 30** |
| autocamp_F8           | **30** | 81 | 81 | 81 | 30 | **30 / 30** |
| autocamp_F11          | **30** | 81 | 81 | 81 | 30 | **30 / 30** |
| autocamp_SE           | **30** | 81 | 81 | 81 | 30 | **30 / 30** |

Denominators are **exactly 30** for every cell (3 seed dirs x 10 task dirs, verified; the 10 task
names are byte-identical across all 18 seed dirs — md5 of the sorted basename list matches).
Every cell emits **exactly 81** XML files. Nothing was normalised away.

### Two alternative framings (same raw data, for robustness — the direction never flips)
| Cell | F: all files | A: root decks only | P: scorer's `entries` (judge_geos.py:138) |
|---|---|---|---|
| F0 | **24/30** (81 files) | 26/30 (47 roots) | 28/30 (43 entries) |
| F4/F6/F8/F11 | 30/30 | 30/30 | 30/30 |
| SE | 30/30 | 30/30 | 30/30 |

Framing F is the one to report: (a) it is what the plan doc used, (b) it is the strictest, and
(c) GEOS itself consumes *every* file in the deck directory, so an `<Included>` fragment that is
malformed breaks the run just as surely as a root deck does. Framing P is the *weakest* precisely
because of the scorer's silent-drop path (Entry 2) — do not use it.

### Failure-mode breakdown (framing F, per run — worst category over the run's files)
| Cell | missing | empty | unparseable | parses-but-schema-invalid | schema-valid |
|---|---|---|---|---|---|
| F0 | 0 | 0 | **3** | **3** | 24 |
| F4 | 0 | 0 | 0 | 0 | 30 |
| F6 | 0 | 0 | 0 | 0 | 30 |
| F8 | 0 | 0 | 0 | 0 | 30 |
| F11 | 0 | 0 | 0 | 0 | 30 |
| SE | 0 | 0 | 0 | 0 | 30 |

**No `missing` and no `empty` cases anywhere** — every one of the 180 task-runs produced at least
one non-empty XML. So the rung-1 "catastrophic failure" class here is *malformed*, not *absent*.
That is a weaker (but still real) form of catastrophic failure than the paper's framing implies —
worth stating precisely rather than letting a reviewer discover it.

### The 6 failing F0 runs, individually (file paths behind every one)
Root: `/data/shared/geophysics_agent_data/data/eval/autocamp_followup_2026-05-02/icl/autocamp_F0/F0_icl_s<N>/<task>/inputs/`

| seed | task | failing file(s) | class |
|---|---|---|---|
| s1 | AdvancedExampleThermoPoroElasticWellbore | `ThermoPoroElasticWellbore_smoke.xml` | unparseable |
| s1 | TutorialHydraulicFractureWithAdvancedXML | `walshQuarterNoChombo_smoke.xml` | schema_invalid |
| s3 | AdvancedExampleCasedThermoElasticWellbore | `CasedThermoElasticWellbore_base.xml` | schema_invalid |
| s3 | AdvancedExampleThermoPoroElasticWellbore | `ThermoPoroElasticWellbore_base.xml`, `ThermoPoroElasticWellbore_benchmark.xml` | unparseable |
| s3 | ExampleProppantTest | `ProppantSlotTest_base.xml`, `ProppantSlotTest_benchmark.xml` | unparseable |
| s3 | TutorialHydraulicFractureWithAdvancedXML | `walshQuarterNoChombo_base.xml` | schema_invalid |

### *** CAVEAT THE REBUTTAL MUST STATE ITSELF: effective n is far below 30 ***
The 6 failures span only **4 distinct tasks** and cluster hard by seed: **4 of 6 are seed s3**,
2 are s1, **0 are s2**. Two tasks (ThermoPoroElasticWellbore, TutorialHydraulicFracture) account
for 4 of the 6. Runs are clustered by task *and* by seed, so the nominal Fisher p = 0.024 is
optimistic — report it descriptively, as `REBUTTAL_TRIAGE_v1.md:28` already says.

### *** ROOT CAUSE: all 5 unparseable files are ONE bug — `--` inside an XML comment ***
100% (5/5) of the rung-1 failures are the double-hyphen-in-comment error. Vanilla Claude Code
writes decorative banner comments and prose em-dashes inside comments, both illegal in XML:
```
ThermoPoroElasticWellbore_smoke.xml:71: parser error : Double hyphen within comment: <!--
    <!-- ---- Solver time stepping ---- -->
ProppantSlotTest_base.xml:4: parser error : Double hyphen within comment: <!--
    Proppant Slot Test -- Base Case
ThermoPoroElasticWellbore_benchmark.xml:11: parser error : Comment must not contain '--' (double-hyphen)
       theta:     40 elements  (0 -- 90 deg quarter)
```
This is a genuinely useful, concrete story: the vanilla agent's rung-1 failures are not
"hallucinated physics", they are a lexical XML rule it does not know. An `xmllint` gate in the
loop catches 100% of them, which is exactly the S/X adapter mechanism — so the "true by
construction" caveat is *precisely* right for rung 1 and should be conceded up front.

### The 3 schema_invalid files, verbatim
```
walshQuarterNoChombo_smoke.xml:30: Schemas validity error : Element 'Hydrofracture',
  attribute 'initialTimeStep': The attribute 'initialTimeStep' is not allowed.

CasedThermoElasticWellbore_base.xml:4: Schemas validity error : Element 'Solvers',
  attribute 'gravityVector': [facet 'pattern'] The value '0.0, 0.0, 0.0' is not accepted
  by the pattern '...\{...\}...'      # missing the required { } braces

walshQuarterNoChombo_base.xml:8: Schemas validity error : Element 'Box', attribute 'xMin':
  [facet 'pattern'] The value '-1.0' is not accepted by the pattern '...'
  # R1Tensor attribute given a scalar instead of a 3-vector
```
Two distinct classes: **invented attribute** (`initialTimeStep` on `Hydrofracture`) and
**wrong value type for an R1Tensor attribute** (scalar or unbraced list where `{a, b, c}` required).

### Minor note recorded for completeness
`autocamp_SE` has 46 root decks vs 45 for the other SIGA cells (F0 has 47 because unparseable
files break `<File>` reference detection). SE's `ExampleIsothermalHystInjection` emits a second
`*_base.xml` that nothing includes, and `ExampleVerticalPoroElastoPlasticWellbore` emits two
`*_benchmark.xml` roots. All are schema-valid, so 30/30 is unaffected. Recorded so no one
"discovers" the asymmetry later.

### Artifacts
- `/home/matt/sci/repo3/neurips_review/sprint/artifacts/A1_rungs12_perfile.csv` — **486 rows, one per XML file**, the canonical rung-1/2 artifact
- `/home/matt/sci/repo3/neurips_review/sprint/artifacts/A1_rungs12_raw.jsonl` — 180 rows, one per task-run (root-deck framing + scorer-entry bookkeeping)
- `/home/matt/sci/repo3/neurips_review/sprint/artifacts/A1_rungs12_perfile.py`, `A1_rungs12.py` — harnesses

---

## 2026-07-26 — Entry 4: rung-3 setup, pre-screen, and sanity-check reproduction

### Binary / env
```bash
export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH
G=/data/jixuan/geophysics/GEOS/install-your-platform-release/bin/geosx
$G --help    # confirms: -v, --validate-input,  "Only do the loading phase, and not actual simulation"
```

### PRE-SCREEN — dumped the binary's own schema and diffed it
```bash
$G -s bin_schema.xsd            # exit 0, 619320 bytes
# then counted <xsd:element name="..."> in each
```
- binary schema: **263** elements
- repo XSD (`data/GEOS/src/coreComponents/schema/schema.xsd`): **269** elements
- in repo, NOT in binary — **exactly the 6 named in the brief**, nothing else:
  `CompositeFunction`, `SymbolicFunction`,
  `MultiphasePoromechanicsConformingFracturesALM`(+`Initialization`),
  `CompositionalMultiphaseReservoirPoromechanicsConformingFracturesALM`(+`Initialization`)
- in binary, NOT in repo: **none**.

Binary schema saved as `artifacts/A1_binary_schema.xsd` so the diff is re-derivable.

**Pre-screen result: ZERO task-runs use any of the 6 elements, in ANY of the 6 cells.**
```
autocamp_F0 0   autocamp_F4 0   autocamp_F6 0   autocamp_F8 0   autocamp_F11 0   autocamp_SE 0
```
=> **no exclusions are applied at all**, so the fairness hazard the brief warned about cannot
arise. This is the best possible outcome for that concern and should be stated in the rebuttal:
*"no deck was excluded for binary/schema-version reasons."* The pre-screen code stays in the
harness anyway (`A1_rung3.py`, `BINARY_MISSING`/`MISSING_RE`) so the check is auditable.

### Deck unit for rung 3 — and why it differs from rung 2
`geosx -i` takes exactly one file, and an `<Included>` fragment is not a standalone GEOS problem,
so rung 3 must be run on **root decks** (non-referenced `*.xml`, judge_geos.py:138) — 273 deck-runs
total. This is not a weakening: GEOS resolves `<Included>` itself, so a malformed or invalid
fragment is caught **transitively** when its parent root deck is run. Verdict per task-run =
AND over root decks.

### READ-ONLY DISCIPLINE (important)
`geosx` writes output files into its cwd, and `/data/shared` must not be modified. The harness
therefore `shutil.copytree`s each `inputs/` dir into a private scratch dir per deck-run, runs
there, and deletes it. **Nothing under `/data/shared/` or `/data/jixuan/` is ever written.**

### SANITY CHECK — both halves of the known pair reproduce exactly
Reference deck (found at `/home/matt/sci/repo3/data/GEOS/inputFiles/wellbore/`):
```bash
cd <scratch>/ref_thermo   # copy of data/GEOS/inputFiles/wellbore/ThermoPoroElasticWellbore_*.xml
$G -v -i ThermoPoroElasticWellbore_benchmark.xml
# EXIT=0 ; "initialization time 00h00m00s (0.25 s)" ; total 5.2 s
```
Generated F6/seed-1 version of the same task:
```bash
cd <scratch>/f6s1_thermo  # copy of icl/autocamp_F6/F6_icl_s1/AdvancedExampleThermoPoroElasticWellbore/inputs
$G -v -i ThermoPoroElasticWellbore_benchmark.xml
# EXIT=1
# ***** Rank 0: Group /domain/MeshBodies/wellboreMesh/meshLevels/Level0/ElementRegions/elementRegionsGroup has no child named rock
# The children of elementRegionsGroup are: { rockRegion }
```
**Reproduced verbatim.** Harness trusted.

**Gotcha worth recording:** GEOS writes its error message to **stdout**, not stderr. stderr only
carries the Open MPI `MPI_ABORT` boilerplate. A harness that classified on stderr alone would
score every failure as `other`. `classify()` therefore parses `stdout + stderr` combined and
extracts the `***** Rank N: <message>` line.

### Launch
```bash
python3 A1_rung3.py --out artifacts/A1_rung3_raw.jsonl --scratch <scratch>/r3full --workers 4
# 273 deck-runs, 0 excluded, 120 s cap each (timeout recorded as failure)
```

## 2026-07-26 — Entry 5: rung-3 sweep attempt 1 CRASHED — three harness defects, all fixed

The first launch stalled at 27/273 and died. Three separate defects, all worth recording because
they are the kind that silently corrupt a sweep:

**Defect 1 — `shutil.copytree` crashed on a dangling symlink, killing the whole sweep.**
```
shutil.Error: [('.../autocamp_F0/F0_icl_s2/ExampleIsothermalHystInjection/inputs/tables',
  ..., "[Errno 2] No such file or directory")]
```
The exception propagated out of `ThreadPoolExecutor.map` and terminated `main` before any record
was written. Fixes: `copytree(..., symlinks=True, ignore_dangling_symlinks=True)` (reproduces the
on-disk state faithfully — a dangling link stays dangling), **and** `run_deck` now wraps
`_run_deck` in try/except returning a `harness_error` record, **and** records are written+flushed
incrementally so a crash can never lose completed work.

Full symlink inventory (walked `inputs/` without following links, all 6 cells):
```
autocamp_F0 s2 ExampleIsothermalHystInjection fc_tables -> /geos_lib/inputFiles/compositionalMultiphaseWell/benchmarks/Class09Pb3/fc_tables  exists=False
autocamp_F0 s2 ExampleIsothermalHystInjection tables    -> /geos_lib/inputFiles/compositionalMultiphaseWell/benchmarks/Class09Pb3/tables     exists=False
```
**Exactly 2 symlinks in the whole dataset, both in F0/s2, both dangling.** They point at
`/geos_lib/...`, the *container* path — the vanilla agent symlinked to a path that only exists
inside the sandbox, so the tables are unreachable on the host. Every other cell's
`tables`/`fc_tables` are real copied directories. This is a **real F0 failure mode, not something
my harness imposed**, and it will legitimately show up as a rung-3 failure. Flagging it explicitly
so nobody mistakes it for a fairness bug. Related asymmetry, recorded for transparency: the
`tables`/`fc_tables` payload is absent entirely for F0/s1, F4/s2, F4/s3, F6/s3 — so
`ExampleIsothermalHystInjection` is confounded by data availability in *both* directions and its
rung-3 result should be read per-task, not folded silently into the cell total.

**Defect 2 — `subprocess.run(timeout=)` did not actually enforce the cap; processes leaked.**
`ps` showed `geosx -i ModifiedCamClayWellbore_benchmark.xml` still running at **5 min 15 s**
elapsed, well past the 120 s cap, and orphaned after the parent died. Cause: `run(timeout=)` kills
only the direct child, but GEOS/OpenMPI leaves grandchildren holding the stdout pipe, so
`communicate()` blocks forever. Fix: `Popen(..., start_new_session=True)` +
`os.killpg(os.getpgid(p.pid), SIGKILL)` on timeout, then a bounded second `communicate(timeout=30)`.
Leaked processes were killed by PID before relaunching.

**Defect 3 — the real cause of the slowness was CPU oversubscription, not slow decks.**
Timed the two suspects standalone:
```bash
cd <scratch> && /usr/bin/time -f "wall=%e" $G -v -i ModifiedCamClayWellbore_benchmark.xml
#  EXIT=0  wall=8.38
cd <scratch> && /usr/bin/time -f "wall=%e" $G -v -i ProppantSlotTest_benchmark.xml
#  EXIT=0  wall=8.63
```
Both **exit 0 in ~8.5 s**. Each geosx is internally multithreaded, so 4 unpinned concurrent
instances thrashed the machine. Fix: `OMP_NUM_THREADS=OPENBLAS_NUM_THREADS=MKL_NUM_THREADS=1`,
`OMP_PROC_BIND=false`, and `--workers 2`. **Applied identically to every deck in every cell**, so
it cannot bias the comparison. 8.5 s vs a 120 s cap leaves ~14x headroom.

Note the brief's "~2.5 s/deck" estimate is low for this binary — the real figure is ~8.5 s, so the
sweep is ~25-40 min, not 8.

### Relaunch
```bash
python3 A1_rung3.py --out artifacts/A1_rung3_raw.jsonl --scratch <scratch>/r3v2 --workers 2
# 273 deck-runs, 0 excluded by pre-screen
```

## 2026-07-26 — Entry 6: *** DATA-INTEGRITY FINDING while building the TreeSim cross-tab ***

Extracted TreeSim from `_results_icl/<SHORT>_icl_s<N>/<cell>/<task>_eval.json` -> `A1_treesim.csv`.
**Found 179 eval records, not 180.**

```
MISSING EVAL: autocamp_F0 s3 ['ExampleProppantTest']
```
This is exactly the task-run where **both** XML files were unparseable (double-hyphen comments), so
`load_and_resolve_dir` raised `ValueError` -> `evaluate_geos` returned `xml_parse_error` and **no
`_eval.json` was ever written**. The per-seed summary does record it correctly:

```
F0_icl_s3/autocamp_F0/_summary.json:
  "n_total": 10, "n_scored": 9, "n_failed": 1, "failed_names": ["ExampleProppantTest"],
  "treesim": { "scored_mean": 0.7003222222222222,   <-- mean over 9, failure DROPPED
               "with_failures_as_zero_mean": 0.63029,  <-- mean over 10, failure counted as 0
               "scored_n": 9, "total_n": 10 }
```

**A human must check which of these two the paper reported.** The gap is large: 0.700 vs 0.630 for
F0/s3, i.e. **0.070 TreeSim** on one of three Vanilla seeds. If the paper used `scored_mean`, it
silently dropped Vanilla's single worst (catastrophic) run — which *understates* Vanilla's
weakness, so the direction is conservative for our claim, but the σ figure in the headline
reliability claim (σ 0.081 -> 0.002) would be computed on the wrong denominator. Every other
cell-seed has `n_scored: 10, n_failed: 0`, so **F0 is the only cell affected** — which is precisely
the cell whose variance the headline claim is about. This needs verifying before the σ number ships.

For my own cross-tab I treat F0/s3/ExampleProppantTest as **treesim = 0.0** (the
`with_failures_as_zero` convention), and record it as such.

## 2026-07-26 — Entry 7: correction to Entry 5, and the resume mechanism

**Correction to Entry 5, Defect 3.** I mis-attributed the slowness. `ps` shows processes
`geosx -i <deck>` **without `-v`** — i.e. full simulations, not validate-input runs. My harness
*always* passes `-v`, so those are **not mine**; something else on this box (another sprint thread,
or another user) is running full GEOS simulations. `uptime` confirms: **128 cores, load average
147.9**. So the 5-minute `ModifiedCamClayWellbore` process was external, and the real constraint is
machine contention, not my concurrency. The thread-pinning fix (`OMP_NUM_THREADS=1` etc.) is still
correct and harmless, and is applied identically to every cell — but it was not the cause.
Recording the correction rather than quietly leaving the wrong diagnosis in the log.

**Resume mechanism added** so no completed work is ever lost:
```bash
python3 A1_rung3.py --out artifacts/A1_rung3_raw.jsonl --scratch <scratch>/r3v2 \
        --workers 8 --resume
# resume: 26 deck-runs already recorded
# 247 deck-runs, 0 task-runs excluded by pre-screen
```
`--resume` reads the existing JSONL, skips any `(cell, seed, task, deck)` already recorded
(excluding `harness_error` rows, which are retried), and appends. Raised to 8 workers since each
geosx is now pinned to 1 thread. **0 timeouts** at 52/273.

**Classification is done offline**, by `A1_rung3_classify.py`, operating only on the saved
`A1_rung3_raw.jsonl` (which stores `stdout_tail` and the extracted `***** Rank N:` message for
every deck-run). This means the failure taxonomy can be revised and re-derived without re-running
geosx, and every category assignment traces to text on disk.

## 2026-07-26 — Entry 8: added a GROUND-TRUTH rung-3 CONTROL (not in the brief, but required)

### Why
Without it the generated pass rate is uninterpretable. If a task's GT deck cannot itself pass
`geosx -v -i` — because the reference `inputs/` does not ship the external table/mesh files the deck
references — then *no* cell can pass that task, and a "SIGA fails rung 3 too" reading would be an
artifact of the dataset, not a property of the agent. Harness: `A1_rung3_gt.py`, importing
`GEOSX`, `TIMEOUT`, `classify`, `root_decks`, `MISSING_RE` **directly from `A1_rung3.py`** so the
control cannot drift from the treatment.

```bash
python3 A1_rung3_gt.py <scratch>/gt2     # -> artifacts/A1_rung3_gt.jsonl
# GT at /data/shared/geophysics_agent_data/data/eval/experiments_gt/<task>/inputs/
```

### *** HARNESS BUG found by the control (and fixed) ***
First GT run reported `TutorialHydraulicFractureWithAdvancedXML` 0/22 with
`Could not resolve absolute path for: heterogeneousInSitu_benchmark.xml.` — a deck failing to
resolve *its own filename*. Cause: `root_decks()` uses `inputs.rglob("*.xml")`, so it can return
decks in **subdirectories**, but the runner did `cwd=work` and `-i <basename>`. GT
`TutorialHydraulicFractureWithAdvancedXML/inputs/` has **61 XMLs** including a `hydraulicFracturing/`
subdir, so the basename was unresolvable from the top-level cwd.

**Blast radius check — the generated sweep is NOT affected:**
```
generated XMLs in SUBDIRS of inputs/: 0
```
Verified from `A1_rungs12_perfile.csv`: **every one of the 486 generated XML files sits directly in
`inputs/`**, zero nested. So `A1_rung3_raw.jsonl` is valid as collected. I fixed both harnesses
anyway (`cwd = work / relpath.parent`, `-i relpath.name`, deck id now the relative path) and
re-ran the GT control. Recording this because "the control found a bug in the treatment harness"
is exactly why the control was worth adding.

### GT control result, first (buggy) run — still informative for the flat tasks
```
AdvancedExampleCasedThermoElasticWellbore       2/2 pass
AdvancedExamplePureThermalDiffusionWellbore     2/2 pass
AdvancedExampleThermoPoroElasticWellbore        2/2 pass
AdvancedExampleViscoExtendedDruckerPrager       1/1 pass
ExampleMCCWellbore                              1/1 pass
ExampleProppantTest                             1/1 pass
ExampleVerticalPoroElastoPlasticWellbore        2/2 pass
ExamplesingleFracCompression                    1/1 pass
ExampleIsothermalHystInjection                  0/3 pass   <-- REAL GT FAILURE
TutorialHydraulicFractureWithAdvancedXML        0/22 pass  <-- was the harness bug
```

### *** RUNG-3 CEILING: `ExampleIsothermalHystInjection` is unpassable by ANY cell ***
```
Could not resolve absolute path for: <cwd>/tables/phaseVolumeFraction_...
```
The GT `inputs/` for this task ships only the 3 XMLs — the `tables/` and `fc_tables/` payload the
deck references is **not** in the dataset. So the deck cannot load regardless of who wrote it. This
task therefore has a **hard rung-3 ceiling of 0 for every cell, including ground truth**, and it
must be reported separately rather than folded into a cell total. It also explains the F0/s2
dangling `/geos_lib/...` symlinks from Entry 5 — the agent was reaching for tables that were never
there.

Combined with the `tables`/`fc_tables` presence asymmetry already logged (absent for F0/s1, F4/s2,
F4/s3, F6/s3; dangling for F0/s2; real dirs elsewhere), the honest treatment is: **report
`ExampleIsothermalHystInjection` as a separate excluded row for all six cells identically**, and
give the rung-3 rate both with and without it. Any other choice either flatters or penalises
whichever cell happened to copy the tables.

---

## 2026-07-26 — Entry 9: *** RECONCILIATION WITH THREAD A2 — and the ladder is NOT MONOTONE ***

Coordinator flagged that A2's `L2` and my `rung 3` disagree. I diffed **all 54** overlapping
(task, cell, seed) runs from `A2_ladder_per_run.csv` against `A1_ladder_by_taskrun.csv`.

**Result: 51/54 agree. All 3 disagreements diagnosed. Two are an A2 harness bug.**

### Disagreements 1 & 2 — A2's deck copy DROPS an asset file (A1 is correct)
`F4/s2` and `F8/s1` of `AdvancedExampleViscoExtendedDruckerPrager`: A2 `validate_rc=1`, mine rc=0.
From A2's own `validate.log:28` (both runs):
```
***** Rank 0: Could not resolve absolute path for:
  .../A2_scratch/runs/F4_s2__AdvancedExampleViscoExtendedDruckerPrager/tables/zeroStrain.geos.
```
```bash
SRC=/data/shared/.../icl/autocamp_F4/F4_icl_s2/AdvancedExampleViscoExtendedDruckerPrager/inputs
ls $SRC/tables   # axialStrain.geos radialStress.geos time.geos zeroStrain.geos   (4 files)
ls A2_scratch/runs/F4_s2__AdvancedExampleViscoExtendedDruckerPrager/tables
                 # axialStrain.geos radialStress.geos time.geos                   (3 files)
for f in $SRC/*.xml; do diff $f <A2 rundir>/$(basename $f); done   # NO DIFF
```
The XML is byte-identical; A2 is specifically dropping a **non-XML asset**. My
`copytree(..., symlinks=True, ignore_dangling_symlinks=True)` gets all 4 and geosx exits 0.
Reported to A2 via the coordinator with a request to re-run those two and assert
`set(copied) == set(source)` per run.

### Disagreement 3 — cascade vs independence, AND a finding that changes the whole framing
`F0/s3/AdvancedExampleThermoPoroElasticWellbore`: A2 `L0=0, L1=1, L2=0`, `validate_rc` **empty** —
A2 never invoked geosx; its L2 cascaded from the L0 failure. My rung3=1.

### *** THE VALIDITY LADDER IS NOT MONOTONE — rung 3 is NOT a subset of rung 1 ***
Verified directly, on the exact deck:
```bash
cd <copy of icl/autocamp_F0/F0_icl_s3/AdvancedExampleThermoPoroElasticWellbore/inputs>
xmllint --noout ThermoPoroElasticWellbore_benchmark.xml
#  ThermoPoroElasticWellbore_benchmark.xml:11: parser error :
#    Comment must not contain '--' (double-hyphen)
python3 -c "import xml.etree.ElementTree as ET; ET.parse('ThermoPoroElasticWellbore_benchmark.xml')"
#  xml.etree.ElementTree.ParseError: not well-formed (invalid token): line 11, column 38
geosx -v -i ThermoPoroElasticWellbore_benchmark.xml
#  exit 0     <-- GEOS ACCEPTS IT
```
**GEOS parses with pugixml, which does not enforce the XML double-hyphen-in-comment rule**;
`xmllint` (libxml2) and Python's `ElementTree` both do. So a deck that is **not well-formed XML by
the W3C spec still loads fine in the simulator.**

Consequences, all of which must be disclosed:
- Rungs 1–2 (xmllint/libxml2) and rung 3 (GEOS/pugixml) are **overlapping, not nested.** The
  rebuttal must NOT present rungs 1→2→3 as a monotone ladder. A reviewer who runs `geosx` on the
  decks we call "does not even parse" will find them loading, and that would look like a
  misrepresentation.
- **All 5 of Vanilla's rung-1 failures are double-hyphen comments** — precisely the class GEOS
  tolerates. So "3 runs emit XML that does not even parse" is true of `xmllint` and of the
  project's own scorer, but **not** of GEOS.
- It is still a real failure: the project's scorer uses `ElementTree`, which rejects them, and that
  is exactly why `F0/s3/ExampleProppantTest` has no `_eval.json` at all (Entry 6). The correct
  framing is "**breaks the evaluation toolchain and every standards-compliant XML tool**", not
  "the simulator cannot run it".
- A **cascading** ladder (A2's) therefore *understates* rung-3 capability.

### AGREED NAMING (to stop shipping two numbers for one quantity)
- **A1 = "rung 3 — GEOS accepts the deck, measured INDEPENDENTLY"** (every root deck run through
  `geosx -v -i` regardless of rung-1/2 outcome).
- **A2 = "L2 — GEOS validate, CONDITIONAL on L0/L1"** (cascaded).
These are different quantities and are now named differently. After A2 fixes the copy bug I expect
53/54 agreement, the remaining difference being the cascade case by construction.

### Task-run verdict rule (mine, stated explicitly)
**AND over all root decks**, where root deck = a `*.xml` under `<task>/inputs/` not referenced by
any other file's `<Included><File name=...>` — the official scorer's own rule,
`src/eval/judge_geos.py:138`. In the 54-run overlap this rule changes nothing: every disagreement is
explained by the copy bug or the cascade, not by AND-vs-single-deck.

---

## 2026-07-26 — Entry 10: `missing_external_asset` — coordinator's hypothesis TESTED and REFUTED

Coordinator hypothesised: *adapter cells write more complete decks that reference more external
assets, so the harness penalises them for being more faithful.* **This is false.** I tested it by
counting, per (cell, seed), how many external assets the decks *reference* vs how many are
*present* in `inputs/`:

```
=== does the DECK reference the asset at all? (grep for *.vtu|*.txt|*.geos|*.vtk in the XML) ===
-- ExampleIsothermalHystInjection      every cell, every seed: 20-25 refs (essentially identical)
-- ExamplesingleFracCompression        every cell, every seed: EXACTLY 1 ref
=== is the referenced asset PRESENT in inputs/? ===
-- ExamplesingleFracCompression   F0: s1 yes, s2 no, s3 no
                                  F4: no no no      F6: no no no      F8: no no no
                                  F11: yes yes yes  SE: yes yes no
-- ExampleIsothermalHystInjection F0: no, dangling, yes   F4: yes no no    F6: yes no no
                                  F8: no no no            F11: yes yes yes  SE: yes yes yes
```
**All six cells reference the same assets.** The decks are equally "complete" in what they cite.
The only thing that varies is whether the referenced *file* was staged next to the deck and
harvested into `inputs/`. So `missing_external_asset` measures **data-asset staging / harvest
completeness**, which is orthogonal to deck authoring and is not what TreeSim or schema validity
measures. The per-cell counts (F6 9, F8 9, F4 7 vs F0 4, F11 2, SE 1) are noise in harvest
completeness across **only 2 of 10 tasks**, not a signal about faithfulness.

**It is nonetheless a fairness bug in our evaluation and must be reported**, just for a different
reason than hypothesised: it is the single largest failure category (**32/273 deck-runs**), it hits
cells unequally, and it is not an authoring failure. Hence it is excluded from the headline
denominator, identically for all six cells.

(Partial nuance worth one sentence in the rebuttal: staging the asset *is* an agent action — F0/s2
even tried, creating dangling `/geos_lib/...` container-path symlinks. So it reflects a real if
minor workspace-hygiene capability. But with n=2 tasks and no consistent ordering it cannot support
a claim in either direction.)

---

## 2026-07-26 — Entry 11: labelling bug fixed; recommended primary denominator

**Bug fixed (coordinator item 2).** `A1_report_out.txt` previously headed a column
`8 GT-passable (n=21)`; n=21 was 7 tasks x 3 seeds. Cause: the GT control used "do ALL GT root
decks pass", which wrongly failed `TutorialHydraulicFractureWithAdvancedXML` — its GT `inputs/`
holds the whole reference example tree (**39 root decks**, incl. a `hydraulicFracturing/` subdir)
while the agent writes **1**. Fixed by making the control **matched-deck**: does the GT deck with
the *same filename* as a generated deck pass? Under that rule only
`ExampleIsothermalHystInjection` is GT-unpassable, so the columns are now
**B: 9 tasks, n=27** and **C: 8 tasks, n=24**. Headers and counts now agree.

**Recommended primary denominator: C (8 tasks, n=24) — the GT-passable AND asset-clean subset.**
Justification:
- A task whose own reference deck cannot load (`ExampleIsothermalHystInjection`) has a rung-3
  ceiling of 0 for every cell and can only dilute, never discriminate. Verified by the GT control.
- `ExamplesingleFracCompression` fails only via `missing_external_asset`, which Entry 10 shows is
  harvest luck, not authoring, and which is unequally distributed across cells. Leaving it in
  imports a known confound directly into the headline.
- Both exclusions are applied **identically to all six cells**, are decided by a **control run on
  ground truth** rather than by looking at which choice helps us, and both are pre-registered in
  this log before the number was chosen.
I agree with the coordinator's ordering: **C as headline, D (authoring-only, n=30) as sensitivity
check, A (all 10, n=30) as the conservative bound.** Report all three — they are cheap and their
disagreement is itself informative.

---

## 2026-07-27 — Entry 12: *** Q1 ANSWERED — THE FLAGSHIP CATASTROPHIC FAILURE LOADS FINE IN GEOS ***

Coordinator's Q1 and my own verification agree. **`F0/s3/ExampleProppantTest` — the single
zero-score run on the held-out split, the sole cause of Vanilla's σ = 0.081, the numerator of the
"≈40x variance reduction" claim — is a deck GEOS accepts.**

```bash
cd <copy of icl/autocamp_F0/F0_icl_s3/ExampleProppantTest/inputs>
xmllint --noout ProppantSlotTest_benchmark.xml
#  :4: parser error : Double hyphen within comment:   "Proppant Slot Test -- Benchmark Case"
python3 -c "import xml.etree.ElementTree as ET; ET.parse('ProppantSlotTest_benchmark.xml')"
#  ParseError: not well-formed (invalid token): line 4, column 21
geosx -v -i ProppantSlotTest_benchmark.xml
#  EXIT 0     total time 00h00m02s (2.04 s)
```
The offending text is a prose double hyphen in a title comment. The deck is invalid XML per the
W3C spec, unscorable by our pipeline (Python `ElementTree`), and **fully acceptable to the
simulator**.

### Root-detection bug — CONFIRMED, and it could only ever hurt Vanilla
Confirmed the coordinator's diagnosis; I had reached the same conclusion independently in the same
turn. `judge_geos.load_and_resolve_dir` builds `referenced` by iterating **ET-parsed files only**
(judge_geos.py:129-136). When `benchmark.xml` is not well-formed, its
`<Included><File name="./ProppantSlotTest_base.xml"/>` edge is never seen, so `base.xml` is
misclassified as a **root** and my AND-over-roots rule failed the task-run on a **fragment that was
never meant to load standalone.**

**Decisive control — a fragment failing standalone carries zero information:**
```bash
cd <copy of experiments_gt/ExampleProppantTest/inputs>     # GROUND TRUTH
geosx -v -i ProppantSlotTest_base.xml       # exit 1  "Error while parsing region region (l.49)"
geosx -v -i ProppantSlotTest_benchmark.xml  # exit 0
```
**The ground-truth `base.xml` fails standalone too, identically.** So the old verdict was measuring
an artifact. Because only F0 has unparseable files, the bug **could only depress Vanilla** — i.e.
it *inflated* our own reported advantage. Correcting it was mandatory.

### THE FIX — GEOS-tolerant root detection
`A1_rung3_corrected.py`: recover the `<Included><File name=...>` graph by **regex over the raw text
of every XML file, parsed or not** — mirroring what pugixml sees. `roots_lenient` is always a
subset of `roots_strict`, so the corrected verdict re-derives from the existing sweep with **no
re-running of geosx**. Applied identically to all six cells.

**Exactly one task-run changes, in the whole 180:**
```
F0 Vanilla/s3/ExampleProppantTest
  strict roots : [ProppantSlotTest_base.xml, ProppantSlotTest_benchmark.xml] -> rung3=0
  lenient roots: [ProppantSlotTest_benchmark.xml]                            -> rung3=1  *** FLIPS ***
```

### CORRECTED RUNG 3 (old -> corrected)
| cell | A: all 10 (n=30) | B: −GTfail (n=27) | C: −GTfail−asset (n=24) |
|---|---|---|---|
| F0 Vanilla | 18 → **19**/30 | 18 → **19**/27 | 17 → **18**/24 |
| F4 X+M | 21/30 | 21/27 | 21/24 |
| F6 S+X | 20/30 | 20/27 | 20/24 |
| F8 | 21/30 | 21/27 | 21/24 |
| F11 | 23/30 | 23/27 | 22/24 |
| SE | 23/30 | 23/27 | 21/24 |

### Q3 — does the direction change? **NO. Magnitude only.**
Vanilla remains the **lowest** cell at every denominator. But it was never significant and is less
so now: Fisher F0 vs each SIGA cell at rung 3 gives **p = 0.27–0.79** (all 10 tasks) and
**p = 0.14–0.49** (n=24); pooled F0 vs all SIGA p ≈ 0.06–0.20 depending on denominator. **Compare
rung 2: p = 0.0237 per cell, p = 1.4e-05 pooled.** The rung-3 separation is directionally
consistent, uniformly non-significant, and **much smaller than the rung-2 separation.**

---

## 2026-07-27 — Entry 13: Q2 — every Vanilla rung-1/2 failure vs its rung-3 outcome

| seed | task | rung-1/2 failing file(s) | class | rung 3 | GEOS error, and is it the SAME defect? |
|---|---|---|---|---|---|
| s1 | AdvancedExampleThermoPoroElasticWellbore | `..._smoke.xml` | unparseable | **FAIL** | `mesh1/trajectory ... should be specified in the form of { { xbottom, ... } }` on **benchmark.xml, a well-formed file** — a **DIFFERENT** defect |
| s1 | TutorialHydraulicFractureWithAdvancedXML | `walshQuarterNoChombo_smoke.xml` | schema_invalid | **FAIL** | `XML Node at '/Problem/Solvers/Hydrofracture' contains unused attribute 'initialTimeStep'` — **SAME** defect |
| s3 | AdvancedExampleCasedThermoElasticWellbore | `..._base.xml` | schema_invalid | **FAIL** | `Input string validation failed at:` (gravityVector `0.0, 0.0, 0.0` missing braces) — **SAME** defect |
| s3 | AdvancedExampleThermoPoroElasticWellbore | `..._base.xml`, `..._benchmark.xml` | unparseable | **PASS** | — GEOS loads it |
| s3 | ExampleProppantTest | `..._base.xml`, `..._benchmark.xml` | unparseable | **PASS** | — GEOS loads it |
| s3 | TutorialHydraulicFractureWithAdvancedXML | `walshQuarterNoChombo_base.xml` | schema_invalid | **FAIL** | `Input string validation failed at:` (Box `xMin="-1.0"` scalar for an R1Tensor) — **SAME** defect |

**The split is perfectly clean along the failure class:**
- **All 3 `schema_invalid` runs also fail rung 3, each with the SAME root cause `xmllint` found.**
  On genuine schema violations, our validator and GEOS agree completely. This part of the rung-2
  story is solid.
- **All 3 `unparseable` (double-hyphen) runs: 2 pass rung 3 outright, and the third fails for an
  unrelated reason.** Proven by a comment-stripping control:
```bash
# F0/s1 ThermoPoro smoke.xml, all comments removed -> now well-formed
xmllint --noout nocomment.xml        # clean
geosx -v -i nocomment.xml            # STILL exit 1, same mesh1/trajectory error
```
So **0 of 3 double-hyphen runs fail GEOS because of the double hyphen.**

### All 5 double-hyphen FILES vs GEOS (coordinator asked for all five)
| # | file | role | GEOS |
|---|---|---|---|
| 1 | F0/s1 `ThermoPoroElasticWellbore_smoke.xml` | root | parses; exit 1 on an **unrelated** `trajectory` R1Tensor error (control above) |
| 2 | F0/s3 `ThermoPoroElasticWellbore_base.xml` | `<Included>` fragment | loads via parent — parent **exit 0** |
| 3 | F0/s3 `ThermoPoroElasticWellbore_benchmark.xml` | root | **exit 0** |
| 4 | F0/s3 `ProppantSlotTest_base.xml` | `<Included>` fragment | loads via parent — parent **exit 0** |
| 5 | F0/s3 `ProppantSlotTest_benchmark.xml` | root | **exit 0** |

**GEOS's pugixml parses all 5 without complaint. 4 of 5 yield exit 0; the 5th fails on an
unrelated attribute error.** Not one is rejected for the double hyphen.

---

## 2026-07-27 — Entry 14: recommended wording (coordinator asked me to sanity-check the framing)

**The coordinator's rewrite is correct and, if anything, slightly understates the problem.** The
falsified sentence — *"an unparseable file does not run in any simulator under any metric"* — is
false for the double-hyphen class in the strongest possible way: not merely "might run", but
**verified exit 0 on the exact deck the paper's headline variance claim rests on.**

One correction to the framing: it is not only that our parsers are "stricter than GEOS's". `--`
inside a comment is **illegal XML per the W3C spec** — libxml2 and ElementTree are *correct* and
pugixml is *permissive*. We are not using an over-strict validator; GEOS is using a lenient one.
That distinction is worth keeping because it is the difference between "our metric is wrong" and
"our metric measures something real that this particular simulator happens to tolerate."

**One clean sentence describing the relationship (offered for quoting):**

> Rungs 1–2 and rung 3 are **overlapping checks performed by different parsers, not nested stages
> of a single ladder**: rungs 1–2 use the W3C-conformant `libxml2`/`ElementTree` stack that our
> evaluation pipeline itself depends on, while GEOS parses with `pugixml`, which accepts some
> spec-invalid constructs — so a deck can fail rung 1 and still load in the simulator, and a deck
> that loads in the simulator can still be unusable by every standards-compliant XML tool,
> including our own scorer.

**And on the `--` class specifically** — I endorse the coordinator's "portability defect" framing:

> The `--`-in-comment failures are a **portability defect rather than an execution failure**: the
> decks violate the XML specification and break every spec-compliant consumer — including the
> evaluation harness, which cannot score them at all — but GEOS's own parser tolerates them.

**What this costs us, stated plainly so nobody is surprised:** the σ = 0.081 → 0.002 reliability
claim rests on ONE run (`F0/s3/ExampleProppantTest`), that run's zero score is a **scorer** artifact
rather than a simulator failure, and the "≈40x variance reduction" headline therefore needs
rewording — it is reliability of *machine-readable authoring*, not of *runnability*. **This is the
most damaging finding of my thread and it should be disclosed by us, not discovered by a reviewer**
who runs `geosx` on the deck in 2 seconds.

---

## 2026-07-27 — Entry 15: artifact manifest (every number in my report traces to one of these)

All under `/home/matt/sci/repo3/neurips_review/sprint/artifacts/`:

**Data**
| file | rows | what |
|---|---|---|
| `A1_rungs12_perfile.csv` | 486 | **canonical rung-1/2 artifact** — one row per XML file: cell, seed, task, filename, size, `is_root`, `is_referenced`, `in_scorer_entries`, rung1, rung2, category, verbatim xmllint error |
| `A1_rungs12_raw.jsonl` | 180 | one row per task-run: root-deck sets, scorer-entry bookkeeping, per-deck verdicts |
| `A1_rung3_raw.jsonl` | 273 | one row per deck-run: exit code, timeout flag, category, extracted GEOS message, `stdout_tail`, `stderr_tail` |
| `A1_rung3_classified.csv` | 273 | same, with the final failure category |
| `A1_rung3_corrected_by_taskrun.csv` | 180 | **authoritative rung-3 artifact** — strict vs GEOS-tolerant roots and both verdicts, per task-run |
| `A1_rung3_gt.jsonl` | 54 | ground-truth control deck-runs |
| `A1_ladder_by_taskrun.csv` | 180 | rung1 / rung2 / rung3 / TreeSim joined per task-run |
| `A1_treesim.csv` | 179 | TreeSim from `_eval.json` (179 not 180 — see Entry 6) |
| `A1_binary_schema.xsd` | — | `geosx -s` dump; diff vs repo XSD gives the 263-vs-269 element gap |

**Code** — `A1_rungs12.py`, `A1_rungs12_perfile.py`, `A1_rung3.py`, `A1_rung3_gt.py`,
`A1_rung3_classify.py`, `A1_report.py`, `A1_rung3_corrected.py`

**Printed reports** — `A1_report_out.txt`, `A1_rung3_corrected_out.txt`, `A1_classify_out.txt`

**Reproduce from scratch**
```bash
export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH
cd /home/matt/sci/repo3/neurips_review/sprint/artifacts
python3 A1_rungs12_perfile.py                                   # rungs 1-2  (~2 min)
python3 A1_rung3.py --out A1_rung3_raw.jsonl --scratch <tmp> --workers 8   # rung 3 (~25 min)
python3 A1_rung3_gt.py <tmp>/gt                                 # GT control (~3 min)
python3 A1_rung3_classify.py && python3 A1_report.py && python3 A1_rung3_corrected.py
```

**Nothing under `/data/shared/` or `/data/jixuan/` was modified.** Every geosx run executed in a
private scratch copy; scratch dirs are deleted after each run. No `_`-prefixed directory was
written. The paper and `writing/` were not touched.
