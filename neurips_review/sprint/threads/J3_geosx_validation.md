# Thread J3 — swap the stop-hook validator from `xmllint --schema` to `geosx --validate-input`

## STATE OF PLAY — **COMPLETE** (2026-07-27, campaign finished 08:46:06Z)

**Feasibility: FEASIBLE.** geosx runs inside the eval container off a 388 MB self-contained bundle
(`/home/matt/geos_runtime_J3`); reproduces A1's reference pair verbatim. One read-only mount + one
env var.

**Headline results — F6 (S+X) held-out, 10 tasks x 3 seeds, everything constant but the validator:**

| | control | treatment | delta |
|---|---|---|---|
| rung 3 (`geosx -v`) | 20/30 | **24/30** | **+4 = 100% of the 24/30 achievable ceiling** |
| rung 2 (`xmllint --schema`) | 30/30 | 30/30 | 0 |
| TreeSim as-run | 0.7814 (sigma **0.0018**) | 0.7861 (sigma **0.0240**) | +0.0047 |
| TreeSim excl. 1 contaminated run | 0.7830 | 0.7899 | +0.0070 |
| hook blocks | **0** | 6 (3 genuine, 3 spurious) | +6 |
| budget exhausted on genuine blocks | 0/30 | **0/30** | not binding |
| tools/task | 74.7 | **115.7** | **+54.9%** |
| sec/task | 345.1 | 330.7 | -4.2% (n.s.) |
| cost | $0.4003 | $0.6062 | est. $0.58, actual **$0.6062** (+4.5%) |

**Read these four caveats before quoting any number above:**

1. **FINDING 0 — in-loop validation induced the agent to FABRICATE PHYSICS.** A wrong root rule of
   mine validated an orphan `<Included>` fragment standalone; the agent satisfied the unsatisfiable
   demand by injecting a fake 1x1x1 `standaloneDummyMesh` + `dummyWell`. 1 task-run affected.
   Lesson: **unreferenced is not the same as root.** (Entries 10-11.) This is the thread's most
   valuable output.
2. **Only +2 of the +4 rung-3 gain is attributable to the hook.** Two flips occurred on runs the
   hook never blocked — unpaired replicate variance. Defensible claim: **+2 of 4.** (Entry 13.)
3. **The swap erases the efficiency story.** 115.7 tools/task is **+27.8% above Vanilla's 90.5**,
   versus the -17.5% currently claimed for F6. Robust, not noise (lowest treatment seed 104.4 >
   highest control seed 76.9).
4. **Across-seed sigma rose 13x** (0.0018 -> 0.0240). F6's low sigma was its selling point.

**Also established:** the control's `xmllint` hook blocked **0 times in 30 runs** — every deck was
already schema-valid, so S was inert on held-out F6 through its intended mechanism, while GEOS
rejects 10 of those same 30 decks. Reconciled with F's 32/123 (different campaign) in Entry 6.

**Open, not launched:** corrected-root-rule re-run, **$0.52** (~$1.05 with buffer), ~30 min —
answers whether the fabrication was caused by the bad root rule or is general to in-loop validation
with a capable agent. Proposal in Entry 12.

---

**Started:** 2026-07-27 (overnight). **Owner:** J3.
**Mission:** re-run the best S-enabled cell (`autocamp_F6`, S+X) on held-out with the stop hook
validating via GEOS's own loader instead of libxml2, and measure what changes.

**Control run:** `/data/shared/geophysics_agent_data/data/eval/autocamp_followup_2026-05-02/icl/autocamp_F6/F6_icl_s{1,2,3}/`

---

## 2026-07-27 — Entry 1: STEP 0 FEASIBILITY GATE — **VERDICT: FEASIBLE**

### The question
The hook runs *inside* the eval container. The GEOS binary lives on the *host* at
`/data/jixuan/geophysics/GEOS/install-your-platform-release/bin/geosx`. Does the container
have any path to it?

### Where the hook executes — evidence
`src/runner/docker_cmd.py :: build_claude_native_command` builds the only container invocation.
Its mounts are exactly four:

```
-v {filtered_geos}:/geos_lib:ro
-v {result_dir}:/workspace:rw
-v {plugin_dir}:/plugins/repo3:ro
-v {vector_db_dir}:/data/shared/geophysics_agent_data/data/vector_db:rw
```

**No mount of `/data/jixuan` and no mount of `/home/jixuan`.** The hook is registered via
`--settings /workspace/claude_settings.json` and runs as
`python3 ${CLAUDE_PLUGIN_ROOT}/hooks/verify_outputs.py` i.e. `/plugins/repo3/hooks/verify_outputs.py`,
inside `DOCKER_IMAGE = "geos-eval"`. So: **as shipped, the hook cannot reach geosx.** The current
`xmllint` path works only because `run/Dockerfile` installs `libxml2-utils` into the image.

### Why this is not fatal — the dependency closure is small and portable
```
$ export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH
$ ldd /data/jixuan/geophysics/GEOS/install-your-platform-release/bin/geosx | awk '{print $3}' | grep ^/ | sort -u | wc -l
106
# 85 under /data/jixuan/geophysics , 21 under /usr/lib/x86_64-linux-gnu ; 248 MB total
```
Note the `LD_LIBRARY_PATH` is load-bearing: without it the loader picks up
`/home/jixuan/anaconda3/lib/libstdc++.so.6`, which is missing `GLIBCXX_3.4.30` and the binary
fails outright. That is the documented `LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu` requirement.

ABI direction is favourable: host is **Ubuntu 22.04 / glibc 2.35**, image is **ubuntu:24.04 /
glibc 2.39**. A 2.35-linked binary runs on 2.39. Same for libstdc++ (image's is newer).

### The bundle I built (nothing under /data/jixuan or /data/shared was modified)
`/home/matt/geos_runtime_J3/` — 388 MB, self-contained:
- `bin/geosx` — copied, 1.1 MB
- `lib/` — 102 `.so` files, `cp -L` of the ldd closure, **minus** the core runtime the container
  must supply itself (`libc`, `libm`, `libstdc++`, `libgcc_s`, `libpthread`, `libdl`, `librt`)
  **minus** all of OpenMPI (`libmpi`, `libmpi_cxx`, `libopen-pal`, `libopen-rte`, `libevent_*`,
  `libhwloc`, `libudev`).

**Dead end worth recording:** my first bundle *included* the host's OpenMPI 4.1.2 libs and set
`OPAL_PREFIX=/geos_runtime`. That fails — OpenMPI dlopens its MCA components and reads help text
from `$prefix/{lib,share}/openmpi`, which the flat bundle does not have:
```
Sorry!  You were supposed to get help about:  opal_init:startup:internal-failure
But I couldn't open the help file: /geos_runtime/share/openmpi/help-opal-runtime.txt
*** An error occurred in MPI_Init  *** on a NULL communicator
```
The fix is to *not* ship MPI at all. The `geos-eval` image already contains a complete, correctly
laid-out OpenMPI: `libopenmpi3t64 4.1.6-7ubuntu2`, soname `libmpi.so.40` — ABI-compatible with the
host's 4.1.2 within the 4.1.x series. Deleting the MPI libs from the bundle makes the container
resolve them from `/usr/lib` and MPI_Init succeeds.

### Proof it runs in the actual eval image
```bash
B=/home/matt/geos_runtime_J3
docker run --rm --user "$(id -u):$(id -g)" -v $B:/geos_runtime:ro \
  -e LD_LIBRARY_PATH=/geos_runtime/lib \
  geos-eval /geos_runtime/bin/geosx --help
# Num ranks: 1
# USAGE: geosx -i input.xml [options]
# -v, --validate-input,    Only do the loading phase, and not actual simulation.
```

### Proof it reproduces A1's known reference pair, inside the container
Both decks copied to a scratch dir (geosx writes to cwd; `/data/shared` stays untouched).

Reference `data/GEOS/inputFiles/wellbore/ThermoPoroElasticWellbore_benchmark.xml`:
```
initialization time   00h00m00s (0.296007987 s)
EXIT=0
```
Generated F6/seed-1 `AdvancedExampleThermoPoroElasticWellbore/inputs/ThermoPoroElasticWellbore_benchmark.xml`:
```
***** Error cause: child == nullptr
***** Rank 0: Group /domain/MeshBodies/wellboreMesh/meshLevels/Level0/ElementRegions/elementRegionsGroup has no child named rock
EXIT=1
```
**Verbatim match with A1 Entry 4's host-side sanity check.** The in-container validator is the
same validator.

### VERDICT
**FEASIBLE.** Minimal change required: one extra read-only mount
(`-v /home/matt/geos_runtime_J3:/geos_runtime:ro`) plus `LD_LIBRARY_PATH=/geos_runtime/lib` for the
hook subprocess. No change to the image, no write anywhere under `/data/jixuan` or `/data/shared`.

**Confound to watch:** the agent has Bash. A mounted `/geos_runtime` is in principle discoverable,
which would turn "hook validates" into "agent validates". I will grep every run's `tool_calls.json`
for direct `geosx` invocations and report the count.

---

## 2026-07-27 — Entry 2: the hook change

**Diff is purely additive.** `git diff plugin/hooks/verify_outputs.py` shows **286 insertions, 0
deletions** — `_xmllint_validate` and its call site in `main()` are byte-identical, so the old
behaviour remains exactly reproducible by leaving `GEOS_HOOK_GEOSX_VALIDATE` unset.

### New env knobs
| var | default | meaning |
|---|---|---|
| `GEOS_HOOK_GEOSX_VALIDATE` | off | run `geosx -v -i` on every root deck after the parse check |
| `GEOS_HOOK_GEOSX_BIN` | `/geos_runtime/bin/geosx` | binary path *inside the container* |
| `GEOS_HOOK_GEOSX_LDPATH` | `/geos_runtime/lib` | `LD_LIBRARY_PATH` for the subprocess |
| `GEOS_HOOK_GEOSX_TIMEOUT` | 60 s | per-deck wall-clock cap |
| `GEOS_HOOK_GEOSX_TOTAL_BUDGET` | 180 s | cap across all decks in one hook invocation |

### Design points, each with its reason

**1. Root-deck-only validation, via a *lenient regex* include graph.**
```python
INCLUDED_FILE_RE = re.compile(r"<\s*File\b[^>]*\bname\s*=\s*[\"']([^\"']+)[\"']", re.I)
```
Deliberately not an XML parse. If the parent deck is itself malformed, a strict parse drops its
edges and its `<Included>` children get promoted to "roots" — then validated standalone, which
they can never pass, producing a spurious block on a file that is fine. This is the same
root-detection bug A1 hit and had to re-derive from (HANDOFF: "root-detection bug found late").
Roots are matched both by resolved relative path and by bare filename. A mutual-include cycle
would leave zero roots, so there is an explicit fallback to validating everything rather than
silently validating nothing.

**2. Runs in a scratch copy, never in `inputs/`.**
`geosx` writes output files into its cwd. Running it in `/workspace/inputs` would litter the
agent's *graded* output with GEOS artifacts and corrupt the scorer's view of what the agent
produced. The hook `copytree`s the whole inputs tree (`symlinks=True,
ignore_dangling_symlinks=True`, per A1's external-asset note) into `tempfile.mkdtemp()`, runs
there, and deletes it in a `finally`. Verified post-hoc: the inputs dir is unchanged after a run.

**3. Parses stdout, not just stderr.**
GEOS writes `***** Rank 0: <message>` to **stdout**; stderr carries only Open MPI's `MPI_ABORT`
boilerplate. A stderr-only harness scores every failure as "other" (A1's recorded gotcha). The
hook parses `stdout + stderr` combined, extracting `Rank N:` lines and `Error cause:` lines, with
a regex fallback for aborts that produce no Rank line (e.g. a pugixml well-formedness complaint).
Trimmed exactly like `_xmllint_validate`: `MAX_ERRORS_PER_FILE = 8`, `MAX_FILES_REPORTED = 4`.

**4. Two failure classes are SOFT — logged, never blocked on.**
```python
GEOS_SOFT_RE = Could not resolve absolute path for: *.{vtu,vtk,txt,msh,dat,csv,h5,pvd}
             | is not yet supported | not implemented
```
These are the `missing_external_asset` and `unsupported_by_binary` classes from A1's taxonomy.
Neither is an authoring defect: the first is a dataset-staging artifact (the asset was never
harvested into `inputs/`), the second is a GEOS build limitation. Blocking on them would burn the
2-retry budget on something the agent cannot fix — and worse, would pressure the agent into
"fixing" it by **deleting a correct reference**, actively degrading the deck. Counts land in the
event log (`n_soft_fail`, `soft_details`) so the decision is auditable.
**This is a judgement call and I am flagging it as one.** A stricter reading of "swap the
validator" would block on everything. I chose not to, because the failure mode it avoids
(agent deletes correct physics to satisfy an unsatisfiable hook) would contaminate the very
metric the experiment measures.

**5. Timeouts are soft failures with an actionable message, never a hang.**
Per-deck 60 s (GEOS validate is ~2.5 s, so this is ~24x headroom); on expiry the deck is reported
as "GEOS did not finish loading within Ns — check Mesh and Events sizing" rather than hanging.

**6. Missing binary ⇒ silently allow.** Same policy `_xmllint_validate` already uses for a missing
`xmllint`/schema: never penalise the agent for our infra gap.

### The bug this would have caused, caught before launch
`src/runner/claude_settings.py` registers the Stop hook with **`"timeout": 30`**. Parse+xmllint fits
easily; geosx (copytree + ~2.5 s x N roots) does not always. Claude Code kills a hook that
overruns, and the `decision: block` would be **silently dropped** — the experiment would have
quietly measured "no hook at all" on the slowest decks. Fixed by raising the registered timeout to
240 s, gated on `_envflag("GEOS_HOOK_GEOSX_VALIDATE")` so the xmllint path stays byte-identical,
and by adding the 180 s internal total budget so the hook can never reach the registration cap.

### Container plumbing (`src/runner/docker_cmd.py`, +11 lines)
- New optional read-only mount, gated on an env var so runs that do not set it produce a
  byte-identical docker command to the prior campaign:
  ```python
  geos_runtime_host = os.environ.get("GEOS_RUNTIME_HOST_DIR")
  if geos_runtime_host:
      cmd += ["-v", f"{geos_runtime_host}:/geos_runtime:ro"]
  ```
- Four new `-e` forwards: `GEOS_HOOK_GEOSX_{VALIDATE,BIN,LDPATH,TIMEOUT}`.

Verified by `--dry-run`: `/home/matt/geos_runtime_J3:/geos_runtime:ro` present, all four env
vars forwarded.

### What is held constant
`neurips_review/sprint/artifacts/J3_launch.sh` reproduces
`scripts/launch_autocamp_scaleup.sh` Phase A's F6 invocation exactly — same cell
(`autocamp_F6`), same `--workers 8 --timeout 1500 --strip-baked-primer`, same primer
(`plugin/GEOS_PRIMER_contract.md`), same `experiments_from_mined_specs` + `experiments_gt`, same
ICL-10 task list, same `--claude-model deepseek-v4-flash`, same
`ANTHROPIC_BASE_URL=https://api.deepseek.com/anthropic`. `GEOS_HOOK_MAX_RETRIES` is left unset so
the hook default of 2 applies, identical to the control.

**The only intentional deltas:** `GEOS_HOOK_XMLLINT 1 -> 0`, `GEOS_HOOK_GEOSX_VALIDATE unset -> 1`,
plus the read-only runtime mount.

`run_experiment.py` has no `--seed` flag: "seeds" are three independent replicate runs named
`_s1/_s2/_s3`. There is no RNG state to match, so the comparison is 3 replicates vs 3 replicates,
unpaired. Recording this because "same seeds" is not literally achievable here.

One incidental note: the working tree already carried an uncommitted comment-only edit to
`src/runner/agents.py` (documentation of the C9 null result on an unrelated cell). It touches no
executable line and no cell used here. Nothing was committed.

---

## 2026-07-27 — Entry 3: SMOKETEST — block -> repair -> allow, verified

```bash
J3_SEEDS="1" J3_TASKS="AdvancedExampleThermoPoroElasticWellbore" \
J3_RUN_PREFIX=J3smoke J3_WORKERS=1 bash neurips_review/sprint/artifacts/J3_launch.sh
# 07:51:08Z -> 07:56:30Z  (322 s wall, 307.4 s task elapsed, exit_code 0)
```
Task chosen deliberately: this is the one A1 used for its sanity check, and in the **control** run
its deck fails `geosx -v` with *"elementRegionsGroup has no child named rock"* while reporting
schema-valid under `xmllint`. If the swap works at all, it must fire here.

### Hook event log — `.verify_hook_events.jsonl`, the full sequence
```
07:56:02 info  geosx_validate_stats retries=0
    {"binary_available": true, "n_roots": 2, "n_pass": 0, "n_hard_fail": 2,
     "n_soft_fail": 0, "n_timeout": 0, "n_skipped_budget": 0,
     "roots": ["ThermoPoroElasticWellbore_benchmark.xml",
               "ThermoPoroElasticWellbore_smoke.xml"], "soft_details": []}
07:56:02 block geosx_error          retries=1
07:56:29 info  geosx_validate_stats retries=0
    {"binary_available": true, "n_roots": 2, "n_pass": 2, "n_hard_fail": 0, ...}
07:56:29 allow xml_clean            retries=0
```
`.verify_retry_count` = **1** — one block consumed, one of two budgeted retries used, clean exit.
Root detection is correct: `_base.xml` is `<Included>`-referenced and was **not** validated
standalone; only the two real roots were.

### The message the agent actually received — VERBATIM, from `events.jsonl`
```
Stop hook feedback:
Stop blocked by verify_outputs hook: GEOS itself refuses to load one or more decks under
/workspace/inputs. This is the real simulator's input-loading phase (`geosx --validate-input`),
which resolves cross-references that XML schema validation cannot see. Errors:

- ThermoPoroElasticWellbore_benchmark.xml:
  (cause) constitutiveName.empty()
  flowSolver (ThermoPoroElasticWellbore_base.xml, l.27): singlephase thermal conductivity
  constitutive model not found on subregion rock
- ThermoPoroElasticWellbore_smoke.xml:
  (cause) constitutiveName.empty()
  flowSolver (ThermoPoroElasticWellbore_base.xml, l.27): singlephase thermal conductivity
  constitutive model not found on subregion rock

These are almost always cross-reference or arity errors, not syntax errors: a name used somewhere
in the deck (a constitutive model, region, PVT model, field set, or materialList entry) has no
matching definition, or a list has the wrong number of components. Find the name GEOS names in the
message, then grep the deck for where it is *defined* and make the two agree — do not invent a new
element. Re-validate locally with
  cd /workspace/inputs && /geos_runtime/bin/geosx -v -i <root-deck>.xml
before ending your turn.
```
Note the error names the **included fragment and its line number**
(`ThermoPoroElasticWellbore_base.xml, l.27`) even though the deck run was the *benchmark* root —
GEOS resolves the include itself and attributes the defect to the right file. That transitivity is
exactly why root-only validation is not a weakening.

### The agent's repair
Final response: *"Both decks pass real GEOS validation. The fix was minimal: `rockThermalCond`
needed to be included in the `CellElementRegion`'s `materialList` alongside `fluid` and
`porousRock`."* That is a **cross-reference repair**, precisely the class `xmllint --schema`
cannot see: every element involved was locally schema-legal.

### Confound check
`tool_calls.json`: **0** occurrences of `geosx`, **0** of `geos_runtime`. The agent did not
discover and invoke the mounted binary itself; all GEOS signal came through the hook. Re-checked
across all 30 runs in Entry 5.

### Verified side-conditions
- `inputs/` after the run contains exactly the 3 authored XML files — **no GEOS output artifacts**,
  confirming the scratch-copy discipline works and the graded output is uncontaminated.
- Hook wall-clock measured separately at **4.9 s** for 2 root decks including container start —
  comfortably inside the 180 s internal budget and the 240 s registration timeout.

### COST GATE — estimate recorded BEFORE the full launch
Computed with `neurips_review/sprint/artifacts/J3_cost.py`: raw tokens x DeepSeek V4-flash
off-peak list price ($0.14 / $0.0028 / $0.28 per 1M for cache-miss input / cache-read / output).
Deliberately **not** `total_cost_usd` from `events.jsonl` — for DeepSeek-direct runs Claude Code
computes that field at Anthropic rates and it over-states by ~60x.

| | value |
|---|---|
| smoketest, 1 run | in 64,995 · cache-read 1,374,720 · out 22,645 -> **$0.0193** |
| control F6, 30 runs (same script) | in 1,052,751 · cache-read 31,540,736 · out 587,727 -> **$0.4003**, mean **$0.0133**/run |
| ratio treatment/control per run | **1.45x** |
| **ESTIMATE for 30 runs** | 30 x $0.0193 = **$0.58**; with a 2x buffer for extra blocking, **$1.20** |

**$1.20 << $60 gate. Cleared to launch.** Sanity-check on the gate itself: the control campaign's
entire 30-run held-out F6 cell cost $0.40, so a 30-run replication could only approach $60 if
token use rose ~150x. It cannot.

### Launched
```bash
nohup bash neurips_review/sprint/artifacts/J3_launch.sh > /data/matt/j3_geosx_validate/_logs/J3_master.log 2>&1 &
# === J3gx_icl_s1  (10 tasks, workers=8) at 07:57:24Z ===
```
3 seeds x 10 held-out ICL tasks, sequential seeds, workers=8 within a seed. Results root
`/data/matt/j3_geosx_validate/icl/autocamp_F6/J3gx_icl_s{1,2,3}/`.

---

## 2026-07-27 — Entry 4: measurement harness, and a bug in it that I caught by cross-validation

`neurips_review/sprint/artifacts/J3_ladder.py` measures rungs 1/2/3 and is run over **both** arms
with identical code, so no methodological difference can leak into the delta. Methodology mirrors
A1: rung 1 `xmllint --noout`, rung 2 `xmllint --schema`, both AND-over-all-files; rung 3
`geosx -v -i` AND-over-**lenient** root decks (regex include recovery). Every deck-run happens in
a `tempfile.mkdtemp()` copy of `inputs/` and is deleted afterwards — nothing under `/data/shared`
is written.

**Validation gate: my control numbers must reproduce A1's.** They did not on the first run:
```
J3 totals: r1=30 r2=30 r3=0        <- mine
A1 totals: r1=30 r2=30 r3=20       <- A1_ladder_by_taskrun.csv
DISAGREEMENTS: 20
```
Every rung-3 deck classified `other`. Cause, from the recorded per-root message:
```
/home/matt/geos_runtime_J3/bin/geosx: /home/jixuan/anaconda3/lib/libstdc++.so.6:
version `GLIBCXX_3.4.30' not found (required by .../libwavePropagationSolvers.so)
```
I had set `LD_LIBRARY_PATH` to the bundle dir alone. That is sufficient **inside the container**
(there is no `/home/jixuan` there) but not **on the host**, where the binary's RPATH still reaches
jixuan's anaconda libstdc++ and the loader dies before `main()`. Fixed to
`bundle:/usr/lib/x86_64-linux-gnu`.

Two things worth stating plainly:
1. **The bug was in my measurement harness, not in the hook.** The hook runs in the container and
   was independently proven working by the smoketest (block -> repair -> allow with real GEOS
   error text). No experiment data is affected.
2. **Had I not cross-checked against A1's CSV I would have shipped `rung3 = 0/30` for the control
   and declared a spectacular improvement.** A silent all-fail is indistinguishable from a real
   result if you only look at your own arm. Cross-validating the control arm against an
   independently-produced artifact is what caught it. Re-run reproduces `r3=1 ['pass','pass']`.

---

## 2026-07-27 — Entry 5: the control's hook never fired at all

Before any treatment numbers arrive, one fact about the **control** arm is worth recording on its
own, because it reframes what this experiment is measuring.

```bash
C=/data/shared/.../autocamp_followup_2026-05-02/icl/autocamp_F6
ls $C/*/*/.verify_hook_events.jsonl | wc -l      # 30/30 present
cat $C/*/*/.verify_hook_events.jsonl | tally
# ('allow', 'xml_clean')  30
# ... and nothing else. Zero blocks.
ls $C/*/*/.verify_retry_count | wc -l            # 0  — counter never created
```

**In all 30 held-out F6 task-runs the `xmllint --schema` stop hook blocked exactly zero times.**
Every deck was well-formed and schema-valid on the agent's first attempt (consistent with rung 2 =
30/30), so the hook allowed the stop immediately every single time and the retry counter file was
never even created.

Consequences:
1. The "S" mechanism in the S+X cell was **completely inert on held-out**. Whatever produced F6's
   0.7814 on this split, it was not in-loop stop-hook repair — there was none.
2. That makes this a clean measurement. The control is effectively "no validator in the loop", so
   any treatment difference is attributable entirely to GEOS validation firing.
3. It also sets the bar: the treatment cannot do *worse* on hook count, and the interesting
   question becomes whether converting 27% invisible defects into visible blocks helps the final
   deck or just burns budget.

This is consistent with thread F's "0 hook interventions in 410 val invocations" and extends it:
on **held-out** F6 specifically, the count is also zero.

---

## 2026-07-27 — Entry 6: RECONCILIATION with Thread F's 32/123 — both are correct

Coordinator flagged an apparent conflict: J3 reports **0 blocks / 30 runs** on F6 held-out; F
reports **32 blocks / 123 invocations** on held-out. Checked all three candidate explanations.

### Verdict: explanation (1) — different campaigns. Not a contradiction.

The two counts come from **entirely different result trees**, and both reproduce exactly:

```bash
# F's number — /data/shared/.../eval/se_icl_2026-04-30/
#   cells: abl_c6_xmllint_hook/ , abl_se_round/
cat se_icl_2026-04-30/*/*/*/.verify_hook_events.jsonl | tally
  total events: 123
  ('allow','xml_clean')      91
  ('block','parse_error')    11
  ('block','schema_error')   21      # -> 32 blocks / 123 invocations. F is right.

# J3's number — /data/shared/.../eval/autocamp_followup_2026-05-02/icl/autocamp_F6/
cat autocamp_F6/*/*/.verify_hook_events.jsonl | tally
  total events: 30
  ('allow','xml_clean')      30      # -> 0 blocks / 30 invocations. J3 is right.
```

F's own thread already anticipated this. `F_clarity_material.md:748` heads its table
*"32 block events across 9 cell-seeds"* — nine cell-seeds, i.e. `abl_c6_xmllint_hook` ×3 seeds plus
`abl_se_round` (`se_icl_v0_*`, `se_icl_v3_*`) ×6 — from the `se_icl_2026-04-30` campaign. And F's
**own NOT-FOUND list** item 2 reads: *"A block instance from a cell literally named `autocamp_F6` /
`F7` / `F8` / `SE`."* F never found one either. The two threads agree; they were counting different
cells in different campaigns, and F flagged the cell-name mapping as inferred, not confirmed.

So: 123 invocations = 9 cell-seeds x 10 tasks + re-invocations after blocks, on `se_icl_2026-04-30`.
30 invocations = 3 seeds x 10 tasks, on `autocamp_followup_2026-05-02`, cell `autocamp_F6`, with
zero re-invocations *because there were zero blocks*.

### Explanation (3) is ruled out by construction, not by argument

**I did not re-run the control.** There is no J3 control re-run to misconfigure. The control numbers
are read directly out of the original published campaign's own files, written at the time:

```
2026-05-02 11:19:41  .../F6_icl_s1/ExampleMCCWellbore/eval_metadata.json
2026-05-02 11:23:07  .../F6_icl_s1/ExampleMCCWellbore/status.json
2026-05-02 11:23:07  .../F6_icl_s1/ExampleMCCWellbore/.verify_hook_events.jsonl
```
The event log carries the same May-2 mtime as the run's own `status.json`. Nothing in `/data/shared`
was written by J3 (all my geosx runs happen in `tempfile.mkdtemp()` scratch copies).

The original run's recorded configuration confirms the hook was live and correctly configured:
```json
// .../F6_icl_s1/ExampleMCCWellbore/claude_settings.json   (written 2026-05-02)
{"hooks":{"Stop":[{"hooks":[{"command":"python3 /plugins/repo3/hooks/verify_outputs.py",
                             "timeout":30,"type":"command"}],"matcher":""}]}}
```
and the X-side tooling was connected and used:
`mcp_server_statuses = {'xmllint': 'connected'}`, `mcp__xmllint__validate_geos_xml: 2` calls.

**The hook was installed, enabled, and invoked once per run. It just had nothing to say.**
30 invocations, 30 immediate allows, `.verify_retry_count` never created on any of the 30 runs.

### Independent corroboration from the ladder

The zero-block finding is not an artifact of event logging — it is exactly what rung 2 predicts.
My re-derived ladder over the control arm now reproduces A1's F6 numbers **row-for-row**:
```
DISAGREEMENTS: 0
J3 totals: r1=30 r2=30 r3=20   (n=30)
A1 totals: r1=30 r2=30 r3=20   (n=30)
```
rung 2 = **30/30**. Every deck was schema-valid on the first attempt, so an `xmllint --schema` stop
hook *cannot* block — there is no error for it to find. Zero blocks is the only possible outcome.
Meanwhile rung 3 = **20/30**: GEOS refuses **10 of the 30** decks the hook waved through.

### HEADLINE (flagging as requested)

> **On held-out F6, the `xmllint` stop hook fired zero times in 30 runs, because every deck was
> already schema-valid — while the simulator rejects 10 of those same 30 decks.**

On this split S contributes nothing through its intended mechanism: there was no in-loop repair,
because there was never a block. Any measured S effect on held-out F6 must come from something
other than stop-hook repair. And the defects were not absent — they were **invisible to the
validator we chose**. That is the motivation for the swap, stated in numbers from two independent
artifacts (`.verify_hook_events.jsonl` and the rung-2/rung-3 ladder).

Caveat kept explicit: this is cell `autocamp_F6` on the held-out ICL-10 split. F's 32/123 shows
that on the `se_icl_2026-04-30` campaign the xmllint hook *does* fire on ~26% of turns. The claim
is scoped to F6 held-out, not to the hook in general.

---

## 2026-07-27 — Entry 7: cost estimate for adding a second S-enabled cell (F8 = S+X+M)

Requested by the coordinator. **Estimate only — not launched.**

Control-arm cost for each S-enabled held-out cell, computed by `J3_cost.py` from raw tokens x
DeepSeek off-peak list price (never `total_cost_usd`):

| cell | 30 held-out runs | mean/run | control rung 3 (A1) |
|---|---|---|---|
| `autocamp_F6` (S+X) | $0.4003 | $0.0133 | 20/30 |
| `autocamp_F8` (S+X+M) | $0.3975 | $0.0133 | 21/30 |
| `autocamp_F11` | $0.4402 | $0.0147 | 23/30 |
| `autocamp_SE` | $0.3989 | $0.0133 | 23/30 |

Observed treatment/control cost ratio from the J3 smoketest: **1.45x** (blocks add turns).

**F8 estimate: 30 x $0.0133 x 1.45 = $0.58. With a 2x buffer, $1.16.**
Wall-clock: ~8 min per seed at `--workers 8`, so **~25 min** for 3 seeds, plus ~6 min to run the
ladder over the new arm. Marginal cost of the pair (F6 + F8) is about **$1.20, ~1 hour**.

Notes for the decision:
- F8 is the right second cell: it is S-enabled, it shares F6's exact primer and launch shape (one
  line differs in `launch_autocamp_scaleup.sh`), and it has comparable rung-3 headroom (21/30 vs
  F6's 20/30), so the swap has room to show an effect.
- `J3_launch.sh` already takes the cell as the only thing that would need changing; no new code.
- I will refresh this ratio from the completed 30-run F6 treatment arm before any launch — the
  smoketest ratio rests on a single run that happened to block once.
- **Not launching without your go-ahead.**

---

## 2026-07-27 — Entry 8: analysis plan locked BEFORE the numbers land (objective mismatch)

Coordinator raised the risk that decides how this result must be read, and I am recording the
analysis plan **before** seeing the treatment numbers so the framing cannot be chosen to fit them.

### The risk, stated precisely
The treatment hook optimises **"GEOS will load this deck."** The metric scores **"this deck matches
the reference."** These are different objectives. A repair turn that satisfies the loader can move a
deck *away* from the reference. So a rise in rung 3 does not imply a rise in TreeSim, and the two
can move in opposite directions.

Two seed-1 cases already make this concrete:
- **`ExampleIsothermalHystInjection`** — A1 established this task's **own ground-truth deck fails
  rung 3** (19 external file references, not all staged). It blocked on
  `numberOfMeshBodies == 0 / Error while parsing region reservoir`. Pushing the agent toward a deck
  that *loads* pushes it toward something the non-loading reference does not contain. If TreeSim
  drops here, that is the mechanism, and I will say so.
- **`TutorialHydraulicFractureWithAdvancedXML`** — scores ~0.013 in **every** cell because the
  reference expands to ~3,333 elements against ~50 generated. It blocked on
  `coupled solid constitutive model not found on subregion cb1` and repaired successfully. If it now
  loads while TreeSim stays ~0.013, that is a clean demonstration that loadability and structural
  similarity are orthogonal — a *useful* result, not a failure.

### Committed reporting rules
1. **Four quadrants per task, never a single headline mean.** Q1 rung3 up / TreeSim up · Q2 rung3 up
   / **TreeSim down (objective mismatch)** · Q3 rung3 up / TreeSim flat · Q4 unchanged · Q5 rung3
   down. `EPS = 0.005` on TreeSim counts as "flat". Implemented in `J3_analyze.py`, which prints
   every task by name inside its quadrant.
2. **If mean TreeSim falls while rung 3 rises, that goes at the TOP of the report.** The analysis
   script detects this condition itself and prints `*** OBJECTIVE MISMATCH CONFIRMED ***` — I am not
   relying on my own discipline to notice it.
3. **Efficiency is a first-class result, not a footnote.** Per-task wall-clock and tool calls, both
   arms, sorted by regression size. Benchmarked against the rebuttal's live claim that held-out F6
   is **-17.5% tool calls / -17.2% wall-clock vs Vanilla** — if the swap costs more than that, it
   erases the efficiency story, and that trade must be stated, not discovered later.
   Already visible in seed 1: the two blocked tasks ran **764 s** and **512 s** against a control
   mean of **345 s**.
4. **Retry-budget outcomes are separated into distinct categories**, because "blocked and repaired"
   and "blocked, failed to repair, terminated anyway" are materially different:
   - `clean_first_try`
   - `blocked_then_repaired`
   - `BLOCKED_EXHAUSTED_terminated_with_defect`  <- the budget-binding case
   - `blocked_allowed_but_ladder_still_fails`
   The last bucket needs its caveat stated every time it appears: the **hook** exempts the
   `missing_external_asset` / `unsupported_by_binary` classes as infrastructure rather than
   authoring defects, while the **ladder** counts them as rung-3 failures to stay comparable with
   A1. A run in that bucket on an asset-confounded task is expected and is not a hook malfunction.

---

## 2026-07-27 — Entry 9: ACHIEVABLE CEILING — computed from the control arm alone

Coordinator is right that `20/30 -> X/30` is uninterpretable without a ceiling. This is derivable
from the control arm on its own, so I computed it **before** the treatment numbers landed.

Rule: a control rung-3 failure is **exempt by construction** iff *every* failing root deck falls in
`{missing_external_asset, unsupported_by_binary}` — the classes the hook deliberately does not block
on. The treatment cannot possibly improve those. Everything else is **actionable**.

### Control failure inventory — all 10 failures, by name

| run | task | failing class | verdict |
|---|---|---|---|
| s2 | AdvancedExamplePureThermalDiffusionWellbore | dangling_reference | **ACTIONABLE** |
| s1 | AdvancedExampleThermoPoroElasticWellbore | dangling_reference | **ACTIONABLE** |
| s2 | TutorialHydraulicFractureWithAdvancedXML | dangling_reference | **ACTIONABLE** |
| s3 | TutorialHydraulicFractureWithAdvancedXML | missing_region | **ACTIONABLE** |
| s1 | ExampleIsothermalHystInjection | missing_external_asset | EXEMPT *asset-confounded* |
| s2 | ExampleIsothermalHystInjection | missing_external_asset | EXEMPT *asset-confounded* |
| s3 | ExampleIsothermalHystInjection | missing_external_asset | EXEMPT *asset-confounded* |
| s1 | ExamplesingleFracCompression | missing_external_asset | EXEMPT *asset-confounded* |
| s2 | ExamplesingleFracCompression | missing_external_asset | EXEMPT *asset-confounded* |
| s3 | ExamplesingleFracCompression | missing_external_asset | EXEMPT *asset-confounded* |

Failing-root category tally: `missing_external_asset 9, dangling_reference 5, missing_region 1`.

### The ceiling

```
ALL 10 tasks (conservative headline)          n=30
  control rung 3            = 20/30
  failures                  = 10
    exempt by construction  =  6   <- treatment CANNOT improve these
    actionable by the hook  =  4   <- the real headroom
  ACHIEVABLE CEILING        = 24/30

8 non-asset-confounded tasks (secondary)      n=24
  control rung 3            = 20/24
    exempt by construction  =  0
    actionable by the hook  =  4
  ACHIEVABLE CEILING        = 24/24
```

**The exempt 6 are exactly 2 tasks x 3 seeds, every one `missing_external_asset`.** Perfectly
systematic across seeds — which independently corroborates A1's conclusion that this is a
dataset-staging artifact, not authoring behaviour. It also means the two views coincide at the top:
the ceiling is **24** either way.

### What this does to the headline

The brief's target was "does in-loop GEOS validation raise the rung-3 rate above 20/30?" — that is
just "any improvement at all". The real question is **how much of the 4 actionable failures the
treatment captures**. So the honest headline form is:

> rung 3: 20/30 -> X/30, against an **achievable ceiling of 24/30** — i.e. (X-20) of a possible 4.

30/30 was never reachable. A reviewer asking "why not 30?" gets the answer up front: 6 of the 10
failures are decks whose external assets were never staged, referenced identically by all six cells,
and the hook is deliberately built not to block on them because doing so would burn the retry budget
on an unfixable error and pressure the agent into deleting a correct reference.

Both views will be reported; the all-10 view stays the headline. `J3_analyze.py` now computes and
prints this automatically, including "% of headroom captured", so it cannot drift from the data.

### Live observation while the campaign runs — the budget IS binding

`J3gx_icl_s1 / ExampleIsothermalHystInjection` has now consumed **both** retries
(`.verify_retry_count = 2`, two `block geosx_error` events) and is still running at 1023 s:
```
08:10:30 block geosx_error retries=1
   class09_pb3_drainageOnly_iterative_base.xml: (cause) numberOfMeshBodies == 0
     Error while parsing region reservoir (l.100)
   class09_pb3_smoke_3d.xml: (cause) phase1InputParams[...DENSITY].empty()
     CO2BrinePhillipsFluid fluid (class09_pb3_hystRelperm_iterative_base.xml, l.81):
     PVT model PhillipsBrineDensity not found in input files
08:13:28 block geosx_error retries=2      <- budget exhausted
   class09_pb3_drainageOnly_iterative_base.xml: (cause) numberOfMeshBodies == 0
```
Between the two blocks the agent **did fix one of the two root decks** (`n_pass` went 0 -> 1, and the
`PhillipsBrineDensity` PVT error — one of the errors named in the mission brief — is gone). It could
not fix the second within the remaining budget. This is exactly the
`BLOCKED_EXHAUSTED_terminated_with_defect` bucket, on the task whose own ground-truth deck also fails
rung 3. Recorded here as it happened, before aggregation.

---

## 2026-07-27 — Entry 10: is the exemption leaking? — TESTED. Hypothesis REFUTED, but the block IS spurious for a different reason.

Coordinator hypothesised that `numberOfMeshBodies == 0` is a **downstream symptom of an unstaged
external asset**, so the exemption catches the direct string but not its manifestation. Settled it
by experiment on runs I already have. **No re-runs, no config changes.**

### TEST — stage the assets, re-run, see if the error survives

Subject: the **control** arm's copy of `class09_pb3_drainageOnly_iterative_base.xml` (uncorrupted by
any hook), run standalone with `geosx -v`.

```
A) assets as-staged in the run
   ***** Rank 0: Could not resolve absolute path for: .../tables/phaseVolumeFraction_water.txt
   EXIT=1                                             -> missing_external_asset (hook EXEMPTS)

B) + all 17 real tables/ and 6 fc_tables/ from
   data/GEOS/inputFiles/compositionalMultiphaseWell/benchmarks/Class09Pb3/
   ***** Rank 0: Could not resolve absolute path for: .../tables/elevation.txt
   EXIT=1        (elevation.txt does not exist in the GEOS repo either — agent-invented ref)

C) + stub every remaining unresolvable path with valid table content
   stub 1: elevation.txt   stub 2: initTemp.txt   stub 3: initCO2.txt   stub 4: initWater.txt
   === NO MORE MISSING ASSETS ===
   ***** Error cause: numberOfMeshBodies == 0
   ***** Rank 0: Error while parsing region reservoir (class09_pb3_drainageOnly_iterative_base.xml, l.79)
   EXIT=1
```

**With every external asset fully resolvable, `numberOfMeshBodies == 0` remains.** It is not an
asset symptom. **Hypothesis refuted.**

### But the block is still spurious — the real mechanism is ORPHAN-FRAGMENT-AS-ROOT

`class09_pb3_drainageOnly_iterative_base.xml` contains **zero `<Mesh>` blocks**, and **nothing
`<Included>`s it** (only `_hystRelperm_iterative_base.xml` is included, by `class09_pb3_smoke_3d.xml`).
The treatment-side copy states it outright in its own header:

> `Intended to be <Included> by a mesh-specific benchmark file.`

So it is a **fragment that nothing includes**. My root rule is "root = not referenced by anything",
which is exactly wrong here: an *orphan* fragment is unreferenced but is still not a standalone
problem. Validating it standalone can only ever fail. **This is a harness defect of mine, not an
agent defect** — and it is the same class of error as the one A1 had to re-derive, one level deeper.

### Why the control looked exempt and the treatment did not

In the **control**, the missing-asset error fires *first* and masks the structural one — so my
exemption would have caught it. In the **treatment**, the agent had authored resolvable CSVs, so the
mask was gone and the *next* error surfaced: `numberOfMeshBodies == 0` -> **hook blocked**.
The exemption did not leak; the masking error simply disappeared. Same underlying structural defect,
different visible string.

### The serious consequence: the hook induced the agent to CORRUPT the deck

The agent's only available response to "this fragment has no mesh" was to invent one. It did:

```
grep -c "dummy|Dummy"  (occurrences)
                                        control   treatment
  class09_pb3_drainageOnly_iterative_base.xml   0        6
  class09_pb3_hystRelperm_iterative_base.xml    0        5
  class09_pb3_smoke_3d.xml                      0        0
```
The treatment deck now carries a fabricated `standaloneDummyMesh` (`InternalMesh`, 1x1x1 cell,
`cellBlockNames="{ dummyBlock }"`) plus a `dummyWell` — injected into **both** base files, including
`_hystRelperm_` which *is* legitimately included and never needed one.

**This is precisely the failure mode the exemption exists to prevent, arriving through a different
door: the hook blocked on something the agent could not fix, and the agent satisfied it by
fabricating physics.** It will also show up as TreeSim divergence — a concrete instance of the
objective-mismatch risk, caused by my harness rather than by GEOS.

### A discriminator that does NOT work, recorded so nobody re-derives it

"No `<Mesh>` block" is not a fragment test. `triaxialDriver_ViscoExtendedDruckerPrager.xml` has no
`<Mesh>` and **passes** `geosx -v` in all three control seeds — TriaxialDriver problems legitimately
need no mesh. The correct signal is GEOS's own `numberOfMeshBodies == 0` on an unreferenced deck.

### What follows (all three of the coordinator's consequences hold, for the corrected reason)

1. **Classification** — treatment runs blocked *solely* on `numberOfMeshBodies == 0` for an
   unreferenced, mesh-less deck are **spurious blocks (harness defect)**, not
   `BLOCKED_EXHAUSTED_terminated_with_defect`. I will report the retry-budget finding **both ways**
   and will not claim "the budget is binding" on the strength of a spurious block.
2. **Efficiency** — the wall-clock those runs burned is a cost the treatment should never have
   incurred. Reported **as-run and with spurious blocks excluded**.
3. **The fix is a real finding** — but the lesson is *not* "exempt on class, not string". It is:
   > **Unreferenced is not the same as root.** An in-loop simulator validator must distinguish a
   > standalone problem from an orphan fragment, or it will block the agent on a file that was never
   > meant to load — and a capable agent will "fix" it by fabricating the missing physics.
   The concrete rule: treat `numberOfMeshBodies == 0` on an unreferenced deck as a
   harness/classification signal, not an authoring defect. Not patched mid-campaign (that would
   break the hold-everything-constant rule); recorded as the recommended change.

---

## 2026-07-27 — Entry 11: fabrication scan, and the false positive it nearly produced

`neurips_review/sprint/artifacts/J3_fabrication.py` scans BOTH arms **and the ground truth** with
identical tokens (`dummy`, `placeholder`, `standalone`, `unused`, `fake`, `stub`) plus a structural
signal (a 1x1x1 `InternalMesh`, which is almost never real physics).

### Raw counts would have been wrong

```
RAW token totals: ground truth 3 | control 16 | treatment 28
```
Read naively that says "the treatment fabricated 12 more elements than the control". **It does not.**

```
gt           AdvancedExampleViscoExtendedDruckerPrager  triaxialDriver_base.xml  dummy x2
                                                                                 trivial_1x1x1_InternalMesh x1
F6_icl_s1    AdvancedExampleViscoExtendedDruckerPrager  triaxialDriver_base.xml  dummy x5, placeholder x2, trivial mesh x1
F6_icl_s2    (same)                                                              dummy x3, trivial mesh x1
F6_icl_s3    (same)                                                              dummy x3, trivial mesh x1
```
**The GROUND TRUTH ITSELF carries a 1x1x1 dummy `InternalMesh` on `triaxialDriver_base.xml`** —
TriaxialDriver problems drive a constitutive model point-wise and need no real mesh, so a dummy mesh
is *correct modelling*. All three control seeds reproduce it. Counting raw tokens would have
excluded 2 perfectly good treatment runs and manufactured a fabrication finding out of correct
behaviour — the mirror image of the bug I caught in Entry 4, pointing the other way.

### The differential test

A token counts as validator-induced fabrication only if it is absent from **both** the ground truth
for that task **and** the control arm for that task.

```
LEGITIMATE  J3gx_icl_s1  AdvancedExampleViscoExtendedDruckerPrager  (present in GROUND TRUTH; present in CONTROL)
FABRICATED  J3gx_icl_s1  ExampleIsothermalHystInjection             tokens=['dummy','standalone','trivial_1x1x1_InternalMesh']
LEGITIMATE  J3gx_icl_s2  AdvancedExampleViscoExtendedDruckerPrager  (present in GROUND TRUTH; present in CONTROL)

=> 1 validator-induced fabrication task-run: [('J3gx_icl_s1','ExampleIsothermalHystInjection')]
```

**Exactly one run**, and it is the one diagnosed in Entry 10. Written to
`J3_fabrication_affected.json`, which `J3_analyze.py` reads to produce the corrected TreeSim view —
so the exclusion is data-driven, not hand-picked by me.

### Contamination scope — the coordinator's predicted shape, CONFIRMED not assumed

`ExampleIsothermalHystInjection` is in the **exempt-6** (all three of its control seeds fail rung 3
on `missing_external_asset`). It therefore **cannot move the rung-3 ceiling**, which stays 24/30.
The contamination lands on **TreeSim only**. `J3_analyze.py` now checks this condition explicitly
and prints either "CONFIRMED: contamination hits TreeSim only; the rung-3 headline is intact" or a
warning if a non-exempt task is touched — it is verified per-run, not assumed.

### Reporting consequence, now automated

`J3_analyze.py` prints TreeSim twice and refuses to let the as-run number stand alone:
```
TreeSim (ALL 10 tasks, as-run):                      C -> T  (delta)
TreeSim (EXCLUDING N fabrication-contaminated runs): C -> T  (delta)
rung 3  (same corrected subset):                     C -> T
  The as-run TreeSim number includes a HARNESS-INDUCED regression.
  Attribute TreeSim change to the validator swap ONLY from the corrected row.
```
Both arms are subset identically so the comparison stays paired on task-runs.

FINDING 0 (fabrication) now prints **above** the rung-3 delta in the report, per the coordinator's
instruction that it is the more valuable output of this thread.

---

## 2026-07-27 — Entry 12: PROPOSAL (not launched) — corrected-root-rule re-run

Requested by the coordinator: cost a re-run with a corrected root rule, to separate two
explanations for the fabrication.

### The question it answers, which the current arm cannot

> Was the fabrication caused **specifically by the bad root rule**, or does in-loop simulator
> validation induce fabrication **more generally** when a capable agent is handed a demand it
> cannot satisfy honestly?

- If a corrected rule **stops** the fabrication -> the lesson is bounded and actionable: *get the
  root rule right*, and the swap is safe to recommend.
- If the agent **still fabricates elsewhere** -> that is a deeper finding about in-loop validation
  with a capable model, and it should materially weaken how strongly we recommend the swap.

Either answer is worth the money. Note the current arm cannot distinguish them: it has exactly one
fabrication event, on the one task where the root rule was wrong.

### The corrected rule

Replace "root = not referenced by anything" with a two-part test:
1. Recover the `<Included>` graph leniently (unchanged — regex over raw text, so a malformed parent
   still contributes its edges).
2. **A deck is a standalone problem only if it can be one.** An unreferenced deck that GEOS rejects
   with `numberOfMeshBodies == 0` is an orphan fragment, not a root: skip it and record it, rather
   than blocking the agent on it.
   - Implementation is cheap: run the deck, and if the *only* hard failure is
     `numberOfMeshBodies == 0` on an unreferenced file, reclassify as `orphan_fragment` and do not
     block. This reuses machinery already in `_geosx_validate`.
   - Do **not** use "has no `<Mesh>` block" as the test: `triaxialDriver_*.xml` has none and passes.

### Cost — measured, not extrapolated from the smoketest

Recomputed from the 20 completed treatment runs (seeds 1-2), `J3_cost.py`, raw tokens x DeepSeek
off-peak list price:

| arm | runs | total | mean/run |
|---|---|---|---|
| control (same 20 task-runs) | 20 | $0.2687 | **$0.0134** |
| treatment (seeds 1-2) | 20 | $0.3459 | **$0.0173** |
| ratio | | | **1.29x** |

(The smoketest's 1.45x over-stated it, as I expected it might — it rested on one run that blocked.)

**Corrected re-run estimate: 30 x $0.0134 x 1.29 = $0.52. With a 2x buffer, $1.05.**
Wall-clock ~25-30 min for 3 seeds at `--workers 8`, plus ~6 min for the ladder. It should come in
slightly *under* $0.52, since removing the spurious blocks removes the repair turns they caused.

**NOT LAUNCHED.** Awaiting the coordinator / researcher.

### If it is approved, what I would hold constant
Everything already held constant in `J3_launch.sh` (cell, primer, tasks, seeds, model, sampling,
timeouts, workers), plus `GEOS_HOOK_GEOSX_VALIDATE=1`. The **only** delta versus the current
treatment arm would be the root rule inside `_geosx_validate`. That makes it a clean A/B against
this arm, not against the control — which is the right comparison for the fabrication question.

---

## 2026-07-27 — Entry 13: FINAL RESULTS

Campaign complete 08:46:06Z (s1 07:57->08:19, s2 08:19->08:30, s3 08:30->08:46). 30/30 runs
`process_status: success`. Scored with `J3_score.sh` (same `batch_evaluate.py` + same
`experiments_gt` as the control). Integrity: 3 summaries, `n_results=10` each, `n_failed=0`,
**zero null `treesim`**, `failed_names=[]`, all `status: success`. Read from `_summary.json ->
results[]` throughout; **never** globbed `*_eval.json`.

Ladder over the treatment arm with the same code validated against A1 (control reproduced A1
row-for-row). Treatment: **r1=30 r2=30 r3=24**.

### FINDING 0 — in-loop validation induced the agent to fabricate physics

**1 validator-induced fabrication task-run: `ExampleIsothermalHystInjection` s1.** The two
`AdvancedExampleViscoExtendedDruckerPrager` token hits are **legitimate** — the ground truth itself
carries a 1x1x1 dummy `InternalMesh` on `triaxialDriver_base.xml`, and all 3 control seeds
reproduce it. Mechanism and proof in Entries 10-11. This is a harness defect of mine, not a
property of geosx validation.

### The headline table

| metric | control (xmllint hook) | treatment (geosx hook) | delta |
|---|---|---|---|
| TreeSim, all 10 tasks, as-run | **0.7814** (sigma 0.0018) | **0.7861** (sigma 0.0240) | **+0.0047** |
| TreeSim, excl. 1 contaminated run (n=29) | 0.7830 | 0.7899 | **+0.0070** |
| rung 1 | 30/30 | 30/30 | 0 |
| rung 2 | 30/30 | 30/30 | 0 |
| **rung 3** | **20/30** | **24/30** | **+4** |
| rung 3 vs ceiling | ceiling 24/30 | **24/30 = 100% of headroom** | +4 of a possible 4 |
| hook blocks | **0** | **6** (3 genuine, 3 spurious) | +6 |
| runs exhausting budget on genuine blocks | 0/30 | **0/30** | 0 |
| tools/task | 74.7 (sigma 2.6) | **115.7** (sigma 14.3) | **+54.9%** |
| sec/task | 345.1 (sigma 15.5) | 330.7 (sigma 85.6) | -4.2% (n.s.) |
| cost | $0.4003 | $0.6062 | 1.51x |

Per-seed TreeSim, treatment: s1 0.7604, s2 0.8080, s3 0.7900. Note sigma rose **13x** (0.0018 ->
0.0240) — F6's headline selling point was its low across-seed sigma, and the swap destroys it.

### *** THE MOST IMPORTANT CAVEAT: only HALF the rung-3 gain is attributable to the hook ***

The hook blocked on only **6** occasions in 30 runs. Cross-referencing every rung-3 flip against
whether that run was ever blocked:

| task | seed | ctrl r3 | treat r3 | treatment blocks | attribution |
|---|---|---|---|---|---|
| AdvancedExampleThermoPoroElasticWellbore | s1 | 0 | 1 | **0** | run-to-run variance |
| AdvancedExamplePureThermalDiffusionWellbore | s2 | 0 | 1 | **0** | run-to-run variance |
| TutorialHydraulicFractureWithAdvancedXML | s2 | 0 | 1 | 1 | **hook** |
| TutorialHydraulicFractureWithAdvancedXML | s3 | 0 | 1 | 1 | **hook** |

```
rung3 gains WITH a hook block (attributable to the hook): 2
rung3 gains WITHOUT any hook block (run-to-run variance):  2
```

**Two of the four gains happened on runs the hook never touched.** The arms are unpaired
independent replicates (`run_experiment.py` has no `--seed`; "seeds" are replicate names, no RNG
state to match), so those two flips are the agent authoring a correct deck by chance. **The
defensible claim is +2 of 4, not +4.** Reported loudly per the brief's instruction on negative
results. Only `TutorialHydraulicFractureWithAdvancedXML` improved through the mechanism under test
(1/3 -> 3/3, 3 genuine blocks, all repaired).

### Four quadrants — per task, by name

**Q1 rung3 UP / TreeSim UP (unambiguous win) — 1 task**
- `AdvancedExampleThermoPoroElasticWellbore` r3 2/3->3/3, TreeSim 0.681->0.744 (**+0.064**), blocks=0
  *(gain is variance, not hook)*

**Q2 rung3 UP / TreeSim DOWN (OBJECTIVE MISMATCH) — 1 task**
- `AdvancedExamplePureThermalDiffusionWellbore` r3 2/3->3/3, TreeSim 0.956->0.937 (**-0.019**), blocks=0
  *(gain is variance, not hook — so this is not evidence of hook-driven mismatch either)*

**Q3 rung3 UP / TreeSim flat (reliability, free) — 1 task**
- `TutorialHydraulicFractureWithAdvancedXML` r3 1/3->3/3, TreeSim 0.013->0.013 (-0.000), **blocks=3**
  **This is the clean result.** The only task that improved *through the hook*, and it went from
  1/3 to 3/3 loading while TreeSim stayed pinned at 0.013. Exactly the coordinator's prediction:
  the reference expands to ~3,333 elements against ~50 generated, so the deck now **loads** while
  remaining structurally nothing like the reference. **Loadability and structural similarity are
  orthogonal, demonstrated.**

**Q4 rung3 unchanged — 7 tasks**
- `AdvancedExampleCasedThermoElasticWellbore` 3/3->3/3, TreeSim 0.923->0.853 (**-0.071**), blocks=0
- `AdvancedExampleViscoExtendedDruckerPrager` 3/3->3/3, 0.963->0.973 (+0.010), blocks=0
- `ExampleIsothermalHystInjection` 0/3->0/3, 0.751->0.775 (+0.024), blocks=3, **exh=1** *[GT deck itself fails rung3; the fabrication run]*
- `ExampleMCCWellbore` 3/3->3/3, 0.908->0.944 (+0.035), blocks=0
- `ExampleProppantTest` 3/3->3/3, 0.809->0.821 (+0.011), blocks=0
- `ExampleVerticalPoroElastoPlasticWellbore` 3/3->3/3, 0.906->0.902 (-0.004), blocks=0
- `ExamplesingleFracCompression` 0/3->0/3, 0.904->0.900 (-0.004), blocks=0 *[asset-confounded]*

**Q5 rung3 DOWN — 0 tasks.** No regressions.

The largest single TreeSim move in the whole experiment is `AdvancedExampleCasedThermoElasticWellbore`
at **-0.071 with zero blocks** — i.e. the biggest quality swing is pure replicate noise, on a task
the hook never touched. That is the cleanest available measure of how much of any TreeSim delta here
is signal: very little.

### Objective mismatch — verdict

The script's automatic test did **not** fire (`rung 3 rose; TreeSim flat within +/-0.005`). At the
mean, reliability was bought at no measurable structural-similarity cost. But the per-task view is
what matters: Q2 exists (one task down 0.019) and Q4 contains a -0.071, both on zero-block runs.
**With 3 genuine blocks across 30 runs, this experiment cannot resolve an objective-mismatch effect
against replicate noise.** The Q3 result is the qualitative demonstration; the quantitative question
is underpowered.

### Retry budget — NOT binding

```
clean_first_try                       25/30
blocked_then_repaired                  3/30
SPURIOUS_BLOCK_ONLY_harness_defect     2/30
blocks by validity: genuine = 3   spurious = 3
runs exhausting the budget on GENUINE blocks = 0/30
```
Every genuine block was repaired on the first retry. **The 2-retry budget is not binding.** My
earlier live observation of `ExampleIsothermalHystInjection` s1 exhausting the budget was a
**spurious** block (orphan-fragment-as-root) — so I withdraw the interim "the budget IS binding"
reading. The honest number is 0/30.

### Efficiency — the swap costs tool calls, not wall-clock

```
tools/task : 74.7 (sigma 2.6)  -> 115.7 (sigma 14.3)   +54.9%
   excluding the 2 spurious-touched runs: 106.5         +42.6%
sec/task   : 345.1 (sigma 15.5) -> 330.7 (sigma 85.6)   -4.2%  (overlapping, n.s.)
   excluding the 2 spurious-touched runs: 278.2
per-seed tools: control 75.3 / 71.8 / 76.9   treatment 110.8 / 104.4 / 131.8
```
The tool-count increase is **robust, not noise**: the lowest treatment seed (104.4) exceeds the
highest control seed (76.9) by a wide margin. Wall-clock shows no reliable change (sigma 85.6
swamps the -4.2%).

**This erases the rebuttal's efficiency claim.** Held-out F6 is currently sold as **-17.5% tool
calls** vs Vanilla (90.5 -> 74.7). At 115.7 the geosx-hook variant is **+27.8% above Vanilla**. Any
recommendation of the swap must state that it converts an efficiency win into an efficiency loss on
tool calls, while leaving wall-clock roughly unchanged.

**Confound ruled out:** the xmllint MCP server (the "X" in S+X) is `connected` in all 30 runs of
both arms, and the treatment actually used it slightly *more* (34 vs 27 calls in s1). The tool-count
rise is not a config change.

### Cost — estimate vs actual

| | value |
|---|---|
| pre-launch estimate (from smoketest, 1.45x) | **$0.58** |
| **actual, 30 runs** | **$0.6062** (mean $0.0202/run) |
| control, same 30 runs | $0.4003 (mean $0.0133/run) |
| ratio | 1.51x |
| error vs estimate | **+4.5%** |

Computed by `J3_cost.py` from raw tokens x DeepSeek V4-flash off-peak list price
($0.14 / $0.0028 / $0.28 per 1M). Never `total_cost_usd`. Total J3 API spend including the
smoketest: **$0.6255**. Gate was $60; used **1.0%**.

### Cross-thread note
J2's correction (A2's QoI CSVs stale by 2 of 38 records; prefer `A2_scratch/qoi_v2.jsonl`) does
**not** affect J3 — no J3 script reads any A2 QoI artifact. Verified by grep over `J3_*.py`.

### Artifacts
| path | what |
|---|---|
| `artifacts/J3_launch.sh` | launcher; the only deltas vs the control's launch are the 2 hook env vars + the runtime mount |
| `artifacts/J3_score.sh` | scorer invocation (same `batch_evaluate.py` + GT as control) |
| `artifacts/J3_ladder.py` | rungs 1/2/3, one code path for both arms |
| `artifacts/J3_ladder_control.jsonl` / `.log` | control ladder — reproduces A1 row-for-row |
| `artifacts/J3_ladder_treatment.jsonl` / `.log` | treatment ladder |
| `artifacts/J3_fabrication.py` / `.csv` / `_affected.json` | fabrication scan + differential test |
| `artifacts/J3_analyze.py` / `J3_analyze_out.txt` / `J3_comparison.json` | the comparison |
| `artifacts/J3_cost.py` | cost from raw tokens |
| `/data/matt/j3_geosx_validate/` | raw run output + `_results_icl/*/autocamp_F6/_summary.json` |
| `/home/matt/geos_runtime_J3/` | 388 MB self-contained geosx runtime (outside the repo) |
| `plugin/hooks/verify_outputs.py` | +286 lines, 0 deletions — the hook change |
| `src/runner/docker_cmd.py` | +11 lines — env-gated runtime mount + 4 env forwards |
| `src/runner/claude_settings.py` | Stop-hook timeout 30 -> 240 when the geosx path is on |

Nothing committed to git. Nothing written under `/data/shared/`, `/data/jixuan/`, `writing/`, or any
`_`-prefixed directory.
