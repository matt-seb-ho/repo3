# Thread K4 — validator ablations: corrected root rule, second cell, and the hook as a standalone intervention

**Submission:** NeurIPS 2026 #31642 (SIGA)
**Owner:** K4. **Started:** 2026-07-27 ~09:52Z (overnight, researcher asleep).
**Budget:** $10 hard cap for this thread.
**Results root:** `/data/matt/k4_validator_ablations/` (NEVER J3's `/data/matt/j3_geosx_validate/`)
**Artifacts:** `/home/matt/sci/repo3/neurips_review/sprint/artifacts/K4_*`

---

## STATE OF PLAY

**Status: ALL THREE ARMS COMPLETE. Thread finished 2026-07-27 ~12:40Z.**

| arm | what | status | est. $ | actual $ |
|---|---|---|---|---|
| A | F6 (S+X) held-out, geosx hook + **corrected root rule** | **COMPLETE** | 0.60 | **0.5889** |
| B | F8 (S+X+M) held-out, same corrected rule | **COMPLETE** | 0.60 | **0.5475** |
| C | **Vanilla + geosx stop hook only** (`autocamp_K4C`) | **COMPLETE** | 0.62 | **0.5791** |
| — | Arm A smoketest | done | 0.02 | 0.0215 |

**TOTAL SPEND: $1.7370 / $10.00 (17.4% of cap).** Estimate was $1.82 — actual came in **4.6% under**.
90 campaign runs + 1 smoketest, 91/91 `process_status: success`, zero null TreeSim, zero unpaired runs.

### THE FOUR ANSWERS

**1. Arm A — did the corrected rule eliminate the fabrication? YES.**
1 -> **0** validator-induced fabrication task-runs; spurious blocks 3 -> **0**; orphan rule fired 9x.
Arms B and C also 0. The remaining token hits are the *legitimate* TriaxialDriver dummy mesh, present
in the ground truth and the control. **"Unreferenced is not the same as root" is a correct and
sufficient fix** — in-loop simulator validation does **not** induce fabrication more generally.

**2. Arm B — does the validator result hold on a second cell? YES for what matters, NO for sigma.**
Fabrication 0, spurious blocks 0, rung 3 up, orthogonality reproduced. But J3's **13x sigma inflation
does not generalise** — on F8 sigma *fell* 3.5x and on Vanilla 4.5x. And on K1's clean ladder Arm B's
raw +3 **collapses to +1**.

**3. Arm C — how much does the hook alone deliver? MEASURED: all of S+X's benefit, at +8% tools.
CAUSALLY: +1 of 30, same as every other arm.**
Vanilla + one hook: TreeSim **0.7839** (S+X 0.7814, Vanilla 0.7196), rung1/rung2 **30/30** (= every
adapter cell), rung 3 **26/30 staged — above every published cell**. Tools **+8.0%** vs Vanilla
(S+X: -17.5%); wall-clock **-24.4%**. But the hook blocked only **3 times in 30**, and the +6 rung-2
gain has **no mechanism** (zero schema/parse blocks fired) — it is seed variance.

**4. *** THE NEGATIVE THAT OUTRANKS ALL THREE *** — the effect is ~1 task-run in 30, everywhere.**

| arm | control | treatment | RAW | **ATTRIBUTABLE** |
|---|---|---|---|---|
| A F6 | 23/30 | 27/30 | +4 (57%) | **+1 (14%)** |
| B F8 | 24/30 | 25/30 | +1 (17%) | **+1 (17%)** |
| C S-only | 21/30 | 26/30 | +5 (56%) | **+1 (11%)** |

Three cells, three campaigns, **all +1**, and in every case the *same task*
(`TutorialHydraulicFractureWithAdvancedXML`). J3's "+4 = 100% of the ceiling" does not survive K1's
clean ladder plus attribution. **At n=3 seeds, neither the swap nor the original S+X result is
separable from replicate variance.**

**What a human must decide:** see Entry 16.

---

## Entry 0 — orientation, and the three things I am NOT going to rebuild

Read in full before touching anything: J3's thread log (1089 lines), `K1_asset_staging_ladder.md`,
`J3_launch.sh`, `J3_score.sh`, `J3_ladder.py`, `J3_cost.py`, `plugin/hooks/verify_outputs.py`,
`src/runner/{agents,cli,docker_cmd,claude_settings,orchestrator}.py`,
`src/runner/prompts/__init__.py`, `scripts/launch_autocamp_scaleup.sh`.

**Reused as-is, not reimplemented:** `J3_ladder.py` (rungs 1-3, reproduces A1 row-for-row),
`J3_cost.py` (raw tokens x DeepSeek off-peak list price), `J3_score.sh` pattern (`batch_evaluate.py`
+ `experiments_gt`), `J3_launch.sh` pattern.

**J3 status: COMPLETE** (Entry 13 written, `J3_analyze_out.txt` mtime 09:49Z). I will still not write
anything under `/data/matt/j3_geosx_validate/`. My `J3_RESULTS_ROOT` is
`/data/matt/k4_validator_ablations/`.

**K1 status: ORIENTING** — no clean ceiling available yet. Its Entry 0 confirms A1's numbers
reproduce exactly and that `missing_external_asset` = 32/273 deck-runs. I will re-check K1 before
writing final ceilings; if still unavailable I use J3's control-derived ceiling (F6: 24/30) and say so.

**Machine load at start:** load average 57.54 (128 cores), 205 GB free of 1007 GB. Room for
`--workers 8`. K1/K2/K3 concurrent — I will re-check before each launch.

### A measurement/intervention separation I am committing to up front

The corrected root rule goes in the **hook** (the intervention). It does **NOT** go in
`J3_ladder.py` (the measurement). The ladder keeps "root = unreferenced", exactly as A1 and J3 ran
it, so rung 3 stays comparable to A1's published 19/21/20/21/23/23 and to J3's 20/30 -> 24/30.
Changing the scorer at the same time as the treatment would make the A/B uninterpretable.

Consequence, stated so it is not mistaken for a bug later: the ladder will still validate
`class09_pb3_drainageOnly_iterative_base.xml` standalone and still fail it. That is intended.

---

## Entry 1 — coordinator directive (received mid-implementation), and the analysis plan LOCKED BEFORE ANY NUMBERS LAND

Locking this before launching anything, so no reporting choice can be made after seeing the result.

### 1. ATTRIBUTION IS THE HEADLINE, raw delta is the upper bound

J3's lesson: only **+2 of its +4** rung-3 flips were attributable to the hook. Two flips landed on
runs the hook **never blocked** — unpaired replicate variance between two independent 3-seed samples.
The single largest TreeSim move in J3 (-0.071) was on a **zero-block** task.

**Committed rule, for every arm:** every rung-3 flip and every TreeSim delta is decomposed into
- **(a) hook-intervened runs** — the run has >=1 *genuine* block in `.verify_hook_events.jsonl`
- **(b) never-blocked runs** — replicate variance, attributable to nothing

The **attributable delta** (a-only) is reported as the headline; the raw delta is reported as an
**upper bound**. **If an arm's entire delta sits on never-blocked runs, that arm shows nothing and I
will say exactly that.**

### 2. Across-seed sigma, per arm
The swap raised F6's sigma **13x** (0.0018 -> 0.0240). Near-zero seed variance is one of the paper's
headline reliability claims for S+X, so sigma inflation is a real cost of the swap and is reported
beside the tool-call cost, not buried.

### 3. Tool calls against **Vanilla's 90.5**, not only against each arm's own control
J3's swap lands at 115.7 = **+27.8% above Vanilla**, converting a claimed -17.5% efficiency win into
a loss. For **Arm C** this is arguably the single most important number: it says whether a
simulator-grounded hook alone is affordable, or whether the cost is intrinsic to the approach.
Every efficiency table gets a `vs Vanilla 90.5 / 416.5 s` column.

### 4. Check whether the orthogonality result replicates
J3's clean finding is n=1 task: `TutorialHydraulicFractureWithAdvancedXML` went 1/3 -> 3/3 loading
through 3 genuine blocks **while TreeSim stayed pinned at 0.013**. If Arm B or C reproduces
"rung 3 up, TreeSim flat, blocks > 0" on a *different* task, loadability/similarity orthogonality
stops being an anecdote. Explicitly tested per arm.

### 5. Infra gotchas inherited from J3, not to be rediscovered
- Runtime bundle **excludes all OpenMPI** — image ships 4.1.6, bundling host 4.1.2 breaks `MPI_Init`.
  I reuse `/home/matt/geos_runtime_J3` unmodified rather than building my own.
- GEOS writes diagnostics to **stdout**, not stderr. Parse both.
- Stop-hook registration timeout must be **240 s**, not the shipped 30 s. At 30 s a slow deck's
  `decision: block` is silently dropped and the arm would read as "the hook never fired."
  Already handled in `claude_settings.py`, gated on `GEOS_HOOK_GEOSX_VALIDATE`.

### 6. Failures-as-zero, and never glob
TreeSim read from `_summary.json -> results[]` only. **Never** `glob("*_eval.json")` — failed runs
write no eval json, so globbing silently drops exactly the catastrophic-failure runs.

---

## Entry 2 — Arm A implementation: the corrected root rule, and a 3-case unit test against the real binary

### The change — `plugin/hooks/verify_outputs.py`, still purely additive

`git diff --numstat` vs HEAD: **402 insertions, 0 deletions** (J3 left it at 286/0; my +116 are all
new lines). Leaving `GEOS_HOOK_GEOSX_ORPHAN_SKIP` unset reproduces J3's treatment arm exactly.

Three pieces:

1. **`_include_referenced(paths, inputs_dir) -> set[Path]`** — split out of `_root_decks` so the
   correction can ask "did anybody `<Included>` this deck?" without recomputing the graph.
   `_root_decks` now takes an optional `referenced=` and is otherwise unchanged.
2. **`GEOSX_ORPHAN_RE = re.compile(r"numberOfMeshBodies\s*==\s*0")`** plus
   **`_is_orphan_fragment(err_lines)`**, which enforces the *only* in "only hard failure":
   ```python
   causes = [ln for ln in err_lines if ln.startswith("(cause) ")]
   if not causes: return False
   return all(GEOSX_ORPHAN_RE.search(c) for c in causes)
   ```
   Tested against the `Error cause:` lines — where GEOS states the assertion that actually aborted
   the load. GEOS aborts on first fatal error so there is normally exactly one cause; requiring
   *every* cause to be the orphan signal means a deck failing for any additional reason still
   blocks. The `Rank N:` lines ("Error while parsing region reservoir") are context for the same
   abort, not independent failures, so they are deliberately excluded from the test.
3. In `_geosx_validate`, before the hard-fail accounting: if skip is enabled **and** the deck is not
   in `referenced` **and** `_is_orphan_fragment(errs)`, then count `n_orphan_fragment`, append to
   `orphan_details`, and `continue`. New stats keys `n_orphan_fragment`, `orphan_skip_enabled`,
   `orphan_details` land in `.verify_hook_events.jsonl` so the decision is auditable per run.

**Why `referenced` is checked explicitly rather than inferring "it is in `roots`, therefore
unreferenced":** `_root_decks` has a mutual-include-cycle fallback (`return roots or list(paths)`)
that returns *every* deck as a root, referenced ones included. Trusting the roots list would let the
orphan rule fire on a referenced deck in that degenerate case.

`src/runner/docker_cmd.py`: +1 line, `-e GEOS_HOOK_GEOSX_ORPHAN_SKIP`.

### Unit test — 1 positive, 2 negatives, against the REAL geosx binary

Test fixture for the positive case: I could not use J3's affected run directly (the control's copy
is masked by `missing_external_asset`, and the treatment's copy already carries the fabricated
mesh). So I built a *realistic* orphan — a real passing deck with its `<Mesh>` block stripped:

```
ModifiedCamClayWellbore_benchmark.xml  minus  <Mesh>...</Mesh>  ->  orphan_nomesh_base.xml
```
It reproduces J3 Entry 10's signature **exactly**:
```
***** LOCATION: .../mesh/ElementRegionBase.cpp:57
***** Error cause: numberOfMeshBodies == 0
***** Rank 0: Error while parsing region Omega (ModifiedCamClayWellbore_base.xml, l.26):
```

Harness: `scratchpad/k4_hooktest.py` imports the hook module and calls `_geosx_validate` directly.

| test | case | SKIP=OFF | SKIP=ON | verdict |
|---|---|---|---|---|
| 1 (positive) | synthetic orphan, unreferenced, no `<Mesh>` | `hard_fail=1`, **BLOCKS** | `orphan_fragment=1`, **NO BLOCK** | **PASS** |
| 2 (negative) | `triaxialDriver_ViscoExtendedDruckerPrager.xml` — no `<Mesh>`, legitimately passes | `n_pass=1`, no block | `n_pass=1`, no block, `orphan=0` | **PASS** — J3's recorded non-discriminator respected |
| 3 (negative) | `ThermoPoroElasticWellbore` s1 — genuine `has no child named rock` | `hard_fail=2`, **BLOCKS** | `hard_fail=2`, **BLOCKS**, identical feedback | **PASS** — genuine defects still block |

Test 2 is the one that matters: it confirms the rule keys on GEOS's own
`numberOfMeshBodies == 0`, not on "has no `<Mesh>` block", so the deck J3 warned about is untouched.

### Known, accepted false-negative of the corrected rule — stated, not discovered later

If a deck genuinely IS the root and the agent simply **forgot** to write a `<Mesh>` block, the
corrected rule lets that real defect through unblocked. There is no signal distinguishing it from an
orphan fragment: both are unreferenced and both abort with `numberOfMeshBodies == 0`. J3 established
no reliable discriminator exists. I take the trade deliberately — a false-allow costs one unblocked
defect, whereas the false-block it replaces demonstrably **induced the agent to fabricate physics**,
which corrupts the deck *and* contaminates TreeSim. Recorded as a limitation of the recommended fix.

---

## Entry 3 — Arm C cell definition, and the exact diff (as required by the brief)

### The diff — one line removed from F6, nothing added

```diff
  "autocamp_K4C": {                     # == "autocamp_F6" minus one line
      "runner": "claude_native",
      "results_dir": DATA_DIR / "eval" / "autocamp_2026-05-01" / "dsv4" / "autocamp_K4C",
      "api_key_env": "ANTHROPIC_AUTH_TOKEN",
      "model": DEFAULT_CLAUDE_MODEL,
      "requires_rag": False,
      "plugin_enabled": True,
      "rag_enabled": False,
-     "xmllint_mcp_enabled": True,
  },
```
Launched with `GEOS_HOOK_XMLLINT=0`, `GEOS_HOOK_GEOSX_VALIDATE=1`, `GEOS_HOOK_GEOSX_ORPHAN_SKIP=1`.

So the cell is simultaneously **F6 minus X** and **F0 plus S** — which is what makes it the right
probe. It is not a new configuration invented for this arm; it is the S-only corner.

### Proof it is prompt-identical to Vanilla — measured, not asserted

```
autocamp_F0     sha256=02c19db35ac7181c len=2442 primer_inlined=True rag_on=False native_prefix=False
autocamp_K4C    sha256=02c19db35ac7181c len=2442 primer_inlined=True rag_on=False native_prefix=False
autocamp_F6     sha256=02c19db35ac7181c len=2442 primer_inlined=True rag_on=False native_prefix=False
autocamp_F8     sha256=8ac8ed8e639afe2b len=6017 ...  (M = +3575 chars of cheatsheet)

F0 == K4C system prompt : True
```
**All three of F0 / K4C / F6 share a byte-identical system prompt.** The four mechanisms that could
have broken this were each checked in the runner source rather than assumed:
- `--plugin-dir` is **never** passed to `claude` (`docker_cmd.py`) — the plugin is only bind-mounted
  and the hook arrives via `--settings`, so no plugin skill enters the tool list (RN-002 / XN-010).
- `rag_enabled=False` => `_RAG_INSTRUCTIONS_VANILLA`, the same branch F0 takes.
- `_add_prefix = agent.get("add_native_plugin_prefix", _rag_on)` => `False`, so the native plugin
  prompt prefix is not prepended.
- no `cheatsheet_path` => no memory block.

And from the dry run (`--dry-run`, all three cells, task `ExampleMCCWellbore`):
```
K4C claude_mcp_config.json : {"mcpServers": {}}          <- ZERO agent-callable tools
F6  claude_mcp_config.json : {"mcpServers": {"xmllint": ...}}
K4C claude_settings.json   : Stop hook, "timeout": 240   <- identical to F6's, diff = empty
F0                          : no settings/mcp files at all (plugin_enabled=False)
```
Timeout is **240**, not the shipped 30 — J3's silent-block-drop trap avoided.

### The caveat I will report rather than bury

Registering the Stop hook also activates its **unconditional floor**: the `no_xml` check and the XML
`parse_error` check run whenever the hook is registered at all, before either validator. So Arm C
measures **"Vanilla + Stop hook whose validator is geosx"**, not geosx validation in perfect
isolation. Separating the parse-check floor from geosx validation would need a fourth arm. I will
report the floor's contribution from the event log (`reason_category` counts) so the reader can see
how much of any Arm C effect is parse-check versus simulator-grounding.

Incidental gain: the Phase-2 resolution-IV factorial has **no S-only cell** (F0=none, F1=R+M, F2=S+M,
F3=R+S, F4=X+M, F5=R+X, F6=S+X, F7=all). Arm C fills that hole, with geosx as the validator.

---

## Entry 4 — COST ESTIMATES, recorded BEFORE any launch (hard rule 1)

Control per-run cost measured from the held-out control tree with `J3_cost.py`
(raw tokens x DeepSeek V4-flash off-peak list price 0.14 / 0.0028 / 0.28 per 1M;
**never** `total_cost_usd`, which Claude Code computes at Anthropic rates and over-states ~60x):

```
autocamp_F0 (Vanilla)  runs=30  TOTAL=$0.4128  mean/run=$0.0138
autocamp_F6 (S+X)      runs=30  TOTAL=$0.4003  mean/run=$0.0133
autocamp_F8 (S+X+M)    runs=30  TOTAL=$0.3975  mean/run=$0.0133
```

J3's measured geosx-hook overhead: **1.29x** on 20 completed treatment runs (its smoketest-derived
1.45x over-stated it; its full-30 figure came out 1.51x). I use **1.45x** for estimating — the
conservative end of J3's observed range — so I am unlikely to under-estimate.

| arm | cell | base $/run | x overhead | 30 runs | + smoketest | **estimate** |
|---|---|---|---|---|---|---|
| A | F6 | 0.0133 | 1.45 | $0.579 | $0.02 | **$0.60** |
| B | F8 | 0.0133 | 1.45 | $0.579 | $0.02 | **$0.60** |
| C | K4C | 0.0138 | 1.45 | $0.600 | $0.02 | **$0.62** |
| | | | | | **total** | **$1.82** |

Against the **$10.00** thread cap that is **18%**, leaving 5.5x headroom. Even at a 3x cost
blow-out on every arm I stay inside the cap. No arm will be launched without re-checking cumulative
actual spend first.

**Launcher:** `artifacts/K4_launch.sh`, `K4_ARM=A|B|C`. Identical to `J3_launch.sh` in every
respect (primer, tasks, seeds, model, timeouts, workers 8, experiments-dir, ground-truth-dir) except
the cell and `GEOS_HOOK_GEOSX_ORPHAN_SKIP=1`. Reuses J3's runtime bundle
`/home/matt/geos_runtime_J3` **unmodified** — no second bundle built, so the OpenMPI trap cannot
recur.

---

## Entry 5 — Arm A SMOKETEST: the corrected rule fires in-container, and the fabrication is already gone

Deliberately smoketested on **`ExampleIsothermalHystInjection` seed 1** — the exact task-run where
J3's uncorrected rule induced the fabrication. That makes the smoketest a real test of the delta
rather than a plumbing check.

```
K4_ARM=A K4_SEEDS=1 K4_TASKS=ExampleIsothermalHystInjection \
  K4_PREFIX=K4Asmoke K4_WORKERS=1 bash neurips_review/sprint/artifacts/K4_launch.sh
# 10:02:50Z -> 10:08:26Z (5m36s), process_status success
```

### VERBATIM hook event from the smoketest (`.verify_hook_events.jsonl`, `geosx_validate_stats`)

```json
{"binary_available": true, "n_roots": 2, "n_pass": 0, "n_hard_fail": 0, "n_soft_fail": 2,
 "n_timeout": 0, "n_skipped_budget": 0, "n_orphan_fragment": 0, "orphan_skip_enabled": true,
 "roots": ["class09_pb3_drainageOnly_iterative_base.xml", "class09_pb3_smoke_3d.xml"], ...}
```

Plumbing confirmed: `orphan_skip_enabled: true` reached the container (the new `-e` forward works),
`binary_available: true`, the hook ran and completed inside the 240 s registration window.

**No block fired in this run**, and the reason is the masking mechanism J3 documented in Entry 10:
both roots failed **soft** (`missing_external_asset`), so the structural
`numberOfMeshBodies == 0` error never surfaced and the orphan rule had nothing to act on
(`n_orphan_fragment: 0`). That is the *control*-side behaviour reappearing — this run authored
external table references it could not resolve, so the masking error was present.
Consequence: the smoketest does not exercise the orphan branch in-container. The branch is proven by
Entry 2's 3-case unit test against the real binary, and the 30-run campaign gives it 3 more chances.

### The result that matters, on the same task+seed J3 fabricated on

```
                                              GT  CONTROL  J3 (uncorrected)  K4 ARM A (corrected)
class09_pb3_drainageOnly_iterative_base.xml    0     0            6                   0
class09_pb3_hystRelperm_iterative_base.xml     0     0            5                   0
class09_pb3_smoke_3d.xml                       0     0            0                   0
   (case-insensitive count of dummy|placeholder|standalone|fake|stub)
```

**Zero fabrication tokens, matching the control and the ground truth exactly.** n=1 run, and via the
soft-mask path rather than the orphan path, so this is an encouraging signal and not yet the answer.
The 30-run campaign decides it.

**Smoketest actual cost: $0.0215** (1 run). Cumulative K4 spend: **$0.0215 / $10.00**.

---

## Entry 6 — measurement harness: what is reused verbatim, what is new

### Reused from J3 with zero modification
- **`J3_ladder.py`** — rungs 1/2/3. Invoked directly. Its `lenient_roots()` keeps
  "root = unreferenced", which is the *A1-comparable* rule. Per Entry 0 this is deliberate: the
  corrected rule is the intervention, not the measurement.
- **`J3_cost.py`** — cost from raw tokens.
- **`J3_ladder_control.jsonl`** — copied to `K4_A_ladder_control.jsonl`. Verified before reuse:
  30 rows, runs `F6_icl_s{1,2,3}`, `rung1=30 rung2=30 rung3=20` — matches A1's published F6 row
  exactly, so Arm A's control needs no re-run.
- J3's loader semantics inside `K4_analyze.py` (`treesim` / `ladder` / `hooks` / `effcost`), copied
  so no methodological difference can leak into a delta.
- **`/home/matt/geos_runtime_J3`** — used unmodified. No second bundle built, so the OpenMPI
  MPI_Init trap cannot recur.

### New for K4
| artifact | purpose |
|---|---|
| `K4_launch.sh` | all three arms, `K4_ARM=A|B|C`; adds `GEOS_HOOK_GEOSX_ORPHAN_SKIP=1` |
| `K4_score.sh` | same `batch_evaluate.py` + `experiments_gt` as the controls |
| `K4_analyze.py` | one analysis path per arm, with the attribution decomposition |
| `K4_fabrication.py` | J3's differential test, generalised; Arm A additionally scans J3's own uncorrected arm for the direct A/B |
| `K4_{A,B,C}_ladder_{control,treatment}.jsonl` | ladders |

Control ladders for **F8** (Arm B) and **F0** (Arm C) had to be built — J3 only ever laddered F6.
Launched as a pure-CPU background job (`OMP_NUM_THREADS=1`, one geosx at a time), no API cost.

### What `K4_analyze.py` adds beyond J3's analysis
1. **Attribution split** — `genuine_blocks > 0` partitions every run into intervened vs
   never-blocked. Prints RAW delta (labelled upper bound) and ATTRIBUTABLE delta (the headline), and
   prints an explicit *"ENTIRE DELTA SITS ON NEVER-BLOCKED RUNS — THIS ARM SHOWS NOTHING"* banner
   when that is what the data says.
2. **Across-seed sigma** for TreeSim and per-seed rung 3, plus the treatment/control sigma ratio with
   an `*** INFLATED ***` flag above 2x.
3. **Efficiency vs Vanilla** (90.5 tools / 416.5 s) as a dedicated column, plus an explicit warning
   when treatment tools/task exceeds Vanilla's.
4. **Orphan-rule verification** — asserts `orphan_skip_enabled` is true in the event log and counts
   surviving spurious (`numberOfMeshBodies == 0`) blocks, which must be **0** if the rule works.
5. **Orthogonality replication counter** — tasks with rung 3 up, TreeSim flat, and genuine blocks > 0.
   J3 has exactly 1; anything more makes the finding more than an anecdote.
6. **Leading-with-the-negative guard** — if mean TreeSim falls while rung 3 rises, it prints that
   fact as a banner rather than letting the rung-3 gain lead.

---

## Entry 7 — Arm C: the ONE residual difference vs Vanilla that is not the hook, found by inspection

Chasing every non-hook difference between `autocamp_K4C` and `autocamp_F0` turned up exactly one,
and it is not in the prompt or the tool list. `preflight_claude_native_mcp()` is gated on
`enable_plugin`, **not** on `rag_enabled`, so it runs for every plugin-enabled cell. It warms the uv
env and proves the RAG MCP server can open its DB, in a *separate* container invocation before the
agent starts. Consequence, verified on disk:

```
F0 (Vanilla) task workspace : acpx_output.json eval_metadata.json events.jsonl exit_code.txt
                              inputs outputs status.json stderr.txt stdout.txt tool_calls.json
F6 (and K4C) task workspace : ... + claude_mcp_config.json + claude_settings.json
                                  + mcp_preflight.json
```

So a K4C workspace contains **3 harness files that a Vanilla workspace does not**. They are inside
`/workspace`, hence technically readable by the agent's Read tool, though nothing in the system
prompt or task prompt mentions them and the agent has no reason to look.

**Why I am not treating this as a confound to fix:**
1. It is *identical* to the difference between the published `autocamp_F6` and `autocamp_F0` — i.e.
   every plugin-enabled cell in the Phase-2 factorial already carries it. The paper's **S main
   effect already includes this exact difference**, so Arm C inherits the same footing as the
   factorial rather than introducing a new asymmetry.
2. Removing it would require changing the runner for K4C only, which would make Arm C *less*
   comparable to F6 and F8 (Arms A and B), the two cells it is most useful to sit beside.

Recorded so it is disclosed rather than discovered. **Arm C's claim is therefore: "Vanilla + the
Stop hook, on the same harness footing as every plugin-enabled cell in the factorial."**

---

## Entry 8 — control ladders for F8 and F0 built, both reproduce A1 — plus a ceiling problem I found doing it

J3 only ever laddered F6, so Arms B and C needed control ladders. Built with **J3's unmodified
`J3_ladder.py`** (pure CPU, `OMP_NUM_THREADS=1`, no API cost):

```
autocamp_F8: n=30 rung1=30/30 rung2=30/30 rung3=21/30   A1 expects 30/30/21  -> MATCH
autocamp_F0: n=30 rung1=27/30 rung2=24/30 rung3=19/30   A1 expects 27/24/19  -> MATCH
```
Both reproduce A1's published rows exactly, so my measurement path is sound on two more cells (J3
had established it on F6, which I reuse as `K4_A_ladder_control.jsonl`, verified 30/30/20).

### The problem: J3's ceiling method is cell-dependent, and I nearly inherited it silently

J3's ceiling rule is "a task is exempt if **all 3 control seeds** fail rung 3 on
`missing_external_asset`". Applied to F6 it gives 2 exempt tasks and the published **24/30**. Applied
to F0 it gives **zero** exempt tasks and a ceiling of 30/30. Same tasks, same held-out split,
different ceiling — because the rule reads the *cell's* control rather than the task.

Looking at why:

```
ExampleIsothermalHystInjection   (F0 control)
   s1 rung3=0 cats=['missing_region', 'dangling_reference']        <- genuine authoring defect
   s2 rung3=0 cats=['missing_external_asset', 'missing_external_asset']
   s3 rung3=0 cats=['missing_region', 'missing_region', 'dangling_reference']

ExamplesingleFracCompression    (F0 control)
   s1 rung3=1 cats=['pass']                                        <- *** IT PASSES ***
   s2 rung3=0 cats=['missing_external_asset']
   s3 rung3=0 cats=['missing_external_asset']
```

**`ExamplesingleFracCompression` PASSES rung 3 in F0 seed 1.** So it is not intrinsically
unpassable: whether its external asset is staged **varies run to run**. The exemption is a per-run
staging accident, not a property of the task. That is precisely the bug **K1** is fixing, and it
means J3's 24/30 ceiling for F6 rests on all three F6 seeds happening to lose the same coin flip.

### What I do about it

`K4_analyze.py` now reports the ceiling **three ways** rather than picking one:
- **(a) cell-derived** — J3's rule, for continuity with its published 24/30.
- **(b) uniform CONFOUNDED set** `{ExampleIsothermalHystInjection, ExamplesingleFracCompression}`
  applied identically to all three arms, so the arms are comparable to each other.
- **(c) an over-exemption warning** naming any task that some control seed of that cell actually
  passed — direct evidence that (b) is too generous.

Both (a) and (b) print RAW and ATTRIBUTABLE headroom capture. **K1's staged ladder remains the
authoritative ceiling**; I will substitute it if K1 finishes in time and flag which number I used.

**Cross-thread note for K1:** `ExamplesingleFracCompression` F0 s1 passing rung 3 while s2/s3 fail on
`missing_external_asset` is a clean single-cell demonstration that staging varies per run. Useful as
a test case for the staging fix.

---

## Entry 9 — MISTAKE I MADE, and the fix (logging it because it would have silently corrupted Arm A)

Trying to save serial time, I ran `K4_score.sh` for Arm A while **seed 3 was still running**.
`batch_evaluate.py` found empty `inputs/` dirs for all 8 in-flight s3 tasks and wrote a
`_summary.json` recording **0/8 scored, 8 failed**:

```
[  6/8] ExampleMCCWellbore  FAILED: FileNotFoundError: No XML files found in
        .../K4A_icl_s3/ExampleMCCWellbore/inputs
  Batch evaluation: 0/8 succeeded
  Wrote /data/matt/k4_validator_ablations/_results_icl/K4A_icl_s3/autocamp_F6/_summary.json
```

Under **failures-as-zero** those 8 would have entered the mean as TreeSim = 0.0, dragging Arm A's
seed-3 TreeSim to near zero and manufacturing a catastrophic-looking regression out of nothing. And
`K4_score.sh` skips any run that already has a `_summary.json`, so the bogus file would have been
**silently reused** by the real scoring pass afterwards.

**Fix:** `rm -rf /data/matt/k4_validator_ablations/_results_icl/K4A_icl_s3`. Re-scored only after the
campaign log printed `ARM A COMPLETE`.

Seeds 1 and 2, which *were* complete, scored cleanly and are unaffected:
```
s1: n_total=10 n_scored=10 n_failed=0 failed=[] treesim(failures-as-zero)=0.79488  null treesim: []
s2: n_total=10 n_scored=10 n_failed=0 failed=[] treesim(failures-as-zero)=0.77953  null treesim: []
```

**Rule for the rest of this thread: never score an arm before its launcher prints `ARM x COMPLETE`.**
This is the concrete form of "partial data lies" — and note the failure mode is *invisible* rather
than loud, because the scorer treats a missing deck as a legitimate zero.

---

## Entry 10 — ARM A RESULTS (F6, S+X, corrected root rule). Campaign 10:09:22Z -> 10:48:02Z.

Integrity: 30/30 `process_status: success`, exit codes `{0: 30}`, 3 summaries with
`n_total=10 n_scored=10 n_failed=0 failed_names=[]`, **zero null TreeSim**, 0 unpaired runs.
Per-seed TreeSim (failures-as-zero): s1 0.79488, s2 0.77953, s3 0.76537.

### *** THE NEGATIVE, FIRST: mean TreeSim FELL while rung 3 ROSE ***

```
TreeSim mean   0.7814 -> 0.7799   (-0.0015)
rung 3          20/30 -> 24/30    (+4 raw)
```
This is objective mismatch **at the mean**, and it is sharper than J3's (which had TreeSim +0.0047).
It gets worse when split by whether the hook acted:

```
TreeSim on INTERVENED    runs (n= 6): 0.5413 -> 0.5055   (-0.0357)
TreeSim on NEVER-BLOCKED runs (n=24): 0.8415 -> 0.8485   (+0.0071)
```
**Where the hook actually intervened, TreeSim went DOWN by 0.036; where it did nothing, TreeSim
drifted up.** The sign of the effect is the opposite of what a "the hook improves decks" story needs.
n=6 and those are the low-baseline hard tasks (0.54 vs 0.84), so this is suggestive rather than
conclusive — but it is the second arm in a row where the TreeSim gain lives on runs the hook never
touched.

### *** ARM A's HEADLINE QUESTION: DID THE CORRECTED RULE ELIMINATE THE FABRICATION? YES. ***

```
J3, UNCORRECTED root rule : 1 fabrication task-run  [('J3gx_icl_s1','ExampleIsothermalHystInjection')]
K4 ARM A, CORRECTED rule  : 0 fabrication task-runs []
```
Differential test (token absent from BOTH ground truth AND control for that task). Arm A's only
remaining token hits are all on `AdvancedExampleViscoExtendedDruckerPrager` /
`triaxialDriver_base.xml`, classified **LEGITIMATE** in all 3 seeds because the token is present in
the ground truth *and* the control — J3's TriaxialDriver caveat, reproduced independently.

Raw totals, which are *not* the finding: GT 3 | control 16 | **Arm A 10** | J3 uncorrected 32.

And the mechanism behaved exactly as designed:
```
orphan_skip_enabled in events : True
orphan_fragment SKIPS recorded: 9
    class09_pb3_drainageOnly_iterative_base.xml  x6
    class09_pb3_hystRelperm_iterative_base.xml   x3
SPURIOUS blocks (numberOfMeshBodies==0) : 0     <- J3 had 3
GENUINE blocks                          : 6     <- J3 had 3
```
The rule fired 9 times, converted all 3 of J3's spurious blocks into recorded skips, and the
validator's attention moved to the **real** root (`class09_pb3_smoke_3d.xml`) instead of the orphan
fragment.

### VERBATIM — every genuine block Arm A issued. All 6 are real cross-reference defects.

```
K4A_icl_s1 / ExampleIsothermalHystInjection            [geosx_error] retries=1
  class09_pb3_smoke_3d.xml
    (cause) phase1InputParams[PHASE1::InputParamOrder::DENSITY].empty()
    CO2BrinePhillipsFluid fluid (class09_pb3_hystRelperm_iterative_base.xml, l.75):
      PVT model PhillipsBrineDensity not found in input files

K4A_icl_s1 / TutorialHydraulicFractureWithAdvancedXML  [geosx_error] retries=1
  walshQuarterNoChombo_smoke.xml
    (cause) constitutiveName.empty()
    hydrofracture (walshQuarterNoChombo_base.xml, l.43):
      coupled solid constitutive model not found on subregion cb1

K4A_icl_s2 / ExampleIsothermalHystInjection            [geosx_error] retries=1
  class09_pb3_smoke_3d.xml
    Mismatch in phase names between constitutive models
      .../elementRegionsGroup/reservoir(class09_pb3_hystRelperm_iterative_base.xml,l.62)
      /elementSubRegions/1_hexahedra/ConstitutiveModels/relperm
      and fluid (class09_pb3_hystRelperm_iterative_base.xml, l.72)

K4A_icl_s2 / TutorialHydraulicFractureWithAdvancedXML  [geosx_error] retries=1
  walshQuarterNoChombo_smoke.xml
    (cause) constitutiveName.empty()
    hydrofracture (walshQuarterNoChombo_smoke.xml, l.23):
      coupled solid constitutive model not found on subregion cb1

K4A_icl_s3 / AdvancedExamplePureThermalDiffusionWellbore [geosx_error] retries=1
  thermalCompressible_2d_benchmark.xml
    wellborePressure (thermalCompressible_2d_base.xml, l.114):
      this FieldSpecification targets (an) empty set(s).
  thermalCompressible_2d_smoke.xml
    wellborePressure (thermalCompressible_2d_base.xml, l.114):
      this FieldSpecification targets (an) empty set(s).

K4A_icl_s3 / ExampleIsothermalHystInjection            [geosx_error] retries=1
  class09_pb3_smoke_3d.xml
    (cause) phase1InputParams[PHASE1::InputParamOrder::ENTHALPY].empty() && (...)
    CO2BrineEzrokhiThermalFluid fluid (class09_pb3_smoke_3d.xml, l.142):
      PVT model BrineEnthalpy not found in input files
```
Missing PVT models, a missing coupled solid constitutive model, mismatched phase names, a
FieldSpecification targeting an empty set. **Every one is a cross-reference/arity defect that
`xmllint --schema` structurally cannot see, and the control's xmllint hook blocked 0 times on these
same 30 decks.** This is the qualitative core of the "the validator we chose was blind" claim, and
it is now clean of harness artefacts.

### ATTRIBUTION — and it is WEAKER than J3's, not stronger

```
rung-3 GAINS on runs the hook BLOCKED (attributable) : 1
    + TutorialHydraulicFractureWithAdvancedXML  s2  genuine_blocks=1
rung-3 GAINS on runs the hook NEVER blocked (variance): 3
    ? AdvancedExampleThermoPoroElasticWellbore     s1
    ? AdvancedExamplePureThermalDiffusionWellbore  s2
    ? TutorialHydraulicFractureWithAdvancedXML     s3
rung-3 LOSSES: 0 hook-blocked, 0 never-blocked

RAW rung-3 delta          = +4   (UPPER BOUND ONLY)
ATTRIBUTABLE rung-3 delta = +1   <-- THE HEADLINE
```
**Only 1 of the 4 rung-3 gains sits on a run the hook actually blocked.** J3 got +2 of 4; I get
+1 of 4 on the same cell with a *better* rule. Taken together the two arms say the honest
attributable effect of the swap on F6 is **+1 to +2 of 30**, not +4, and that the raw +4 is roughly
half to three-quarters replicate variance.

Note the awkward detail that makes this concrete: `TutorialHydraulicFractureWithAdvancedXML` improved
1/3 -> 3/3, but only **s2** had a genuine block; s1 also blocked and repaired, while **s3 reached
rung-3 pass with no block at all**. The same task improves both with and without the mechanism.

### CEILING (both definitions agree for this arm)
```
exempt = [ExampleIsothermalHystInjection, ExamplesingleFracCompression];  ceiling 24/30
control 20/30 -> treatment 24/30
RAW          +4 of a possible +4 = 100% of headroom
ATTRIBUTABLE +1 of a possible +4 =  25% of headroom
```
"100% of the ceiling" is true and is the number J3 published — but **25% is the attributable
figure**, and that is the one that should go anywhere near the paper.

### FOUR QUADRANTS — per task, by name
```
Q1 r3 UP / TreeSim UP     — 1 task
   AdvancedExampleThermoPoroElasticWellbore     r3 2/3->3/3  0.681->0.705 (+0.024)  blocks=0
Q2 r3 UP / TreeSim DOWN   — 0 tasks
Q3 r3 UP / TreeSim FLAT   — 2 tasks
   AdvancedExamplePureThermalDiffusionWellbore  r3 2/3->3/3  0.956->0.957 (+0.001)  blocks=1
   TutorialHydraulicFractureWithAdvancedXML     r3 1/3->3/3  0.013->0.013 (+0.000)  blocks=2
Q4 r3 FLAT                — 7 tasks
   AdvancedExampleCasedThermoElasticWellbore    r3 3/3->3/3  0.923->0.828 (-0.096)  blocks=0  <- largest move, ZERO blocks
   AdvancedExampleViscoExtendedDruckerPrager    r3 3/3->3/3  0.963->1.000 (+0.037)  blocks=0
   ExampleIsothermalHystInjection               r3 0/3->0/3  0.751->0.689 (-0.062)  blocks=3
   ExampleMCCWellbore                           r3 3/3->3/3  0.908->0.933 (+0.025)  blocks=0
   ExampleProppantTest                          r3 3/3->3/3  0.809->0.818 (+0.009)  blocks=0
   ExampleVerticalPoroElastoPlasticWellbore     r3 3/3->3/3  0.906->0.914 (+0.008)  blocks=0
   ExamplesingleFracCompression                 r3 0/3->0/3  0.904->0.943 (+0.039)  blocks=0
Q5 r3 DOWN                — 0 tasks
```
As in J3, **the largest single TreeSim move is on a zero-block task**
(`AdvancedExampleCasedThermoElasticWellbore`, **-0.096**, bigger than J3's -0.071). That is the
cleanest available yardstick for how much of any TreeSim delta here is signal: not much.

### ORTHOGONALITY REPLICATED — 2 tasks, up from J3's 1
`TutorialHydraulicFractureWithAdvancedXML` (r3 1/3->3/3, TreeSim pinned at 0.013, 2 genuine blocks)
**and** `AdvancedExamplePureThermalDiffusionWellbore` (r3 2/3->3/3, TreeSim 0.956->0.957, 1 genuine
block). Loadability and structural similarity move independently on two different tasks now, at
opposite ends of the TreeSim range (0.013 and 0.956). This is the one place where Arm A makes an
existing finding **stronger**.

### RETRY BUCKETS — budget still not binding, and a new bucket appears
```
clean_first_try                          24/30
blocked_then_repaired                     3/30   (PureThermalDiffusion s3, THFWAX s1, THFWAX s2)
blocked_allowed_but_ladder_still_fails    3/30   (ExampleIsothermalHystInjection s1,s2,s3)
BLOCKED_EXHAUSTED_terminated_with_defect  0/30
SPURIOUS_BLOCK_ONLY_harness_defect        0/30   <- J3 had 2
runs exhausting the retry budget on GENUINE blocks = 0/30  => budget is NOT binding
```
The new `blocked_allowed_but_ladder_still_fails` bucket is all three `ExampleIsothermalHystInjection`
seeds: the hook raised a genuine PVT/phase-name defect, the agent was allowed to stop after its
retries, and the ladder still fails the task — because the ladder additionally trips on
`missing_external_asset`, which the hook deliberately exempts. Not a contradiction; the two
instruments have different soft-failure policies, and this bucket is where that shows up.

### EFFICIENCY — the tool-call cost is confirmed, but wall-clock is now clearly BETTER than Vanilla
```
                 control   treatment   delta%    vs Vanilla(90.5 / 416.5s)
tools/task          74.7       111.5   +49.3%              +23.2%
sec/task           345.1       317.6    -8.0%              -23.7%
per-seed tools control  : 75.3 / 71.8 / 76.9
per-seed tools treatment: 106.5 / 111.7 / 116.2
```
**The tool-call regression replicates** (J3: 115.7, +27.8% vs Vanilla; me: 111.5, +23.2%). Robust,
not noise — the lowest treatment seed (106.5) is far above the highest control seed (76.9). The
rebuttal's "-17.5% tool calls vs Vanilla" claim for F6 does **not** survive the validator swap.

But wall-clock is a genuinely favourable and *new* result: **317.6 s/task, -23.7% vs Vanilla's
416.5 s**, where J3 measured 330.7 s with sigma 85.6 and called it n.s. Two arms now agree the swap
costs tool calls while *saving* wall-clock. Worth stating positively: it buys more, cheaper turns.

### ACROSS-SEED SIGMA — inflated, replicating J3
```
control   per-seed TreeSim: 0.7799 / 0.7809 / 0.7834   sigma = 0.0018
treatment per-seed TreeSim: 0.7949 / 0.7795 / 0.7654   sigma = 0.0148   -> 8.12x  *** INFLATED ***
control   per-seed rung3  : 7 / 6 / 7
treatment per-seed rung3  : 8 / 8 / 8       <- rung 3 is MORE stable, TreeSim LESS
```
J3 saw 13x; I see **8.12x**. Both large. F6's near-zero across-seed sigma is one of the paper's
headline reliability claims and **the swap destroys it** — confirmed independently on a second run of
the same cell. Note the split personality: rung 3 becomes perfectly stable (8/8/8) while TreeSim
becomes 8x less stable. The swap makes *loadability* reliable and *structural similarity* noisier.

### COST — estimate vs actual
```
estimate (pre-launch, Entry 4) : $0.60
ACTUAL, 30 runs                : $0.5889   ($0.0196/run)   error -1.9%
control, same 30 runs          : $0.4003   ($0.0133/run)
ratio                          : 1.47x
```
Cumulative K4 spend: **$0.6104 / $10.00** (smoketest $0.0215 + Arm A $0.5889).

---

## Entry 11 — K1 FINISHED. Re-measuring Arm A on its clean ladder collapses the "100% of ceiling" claim.

K1 completed while Arm B was running. Its result changes the denominator for every arm:

> **New ceiling 30/30** (was an effective 24/30). No task needs excluding any more.
> Clean staged rung 3: **F0 21, F4 21, F6 23, F8 24, F11 23, SE 24.**

Critically, K1's `rung3_unstaged` column reproduces my ladder numbers **exactly** (F6 20, F8 21,
F0 19), so the two harnesses agree and the only difference is staging.

### I could not just swap the ceiling in — that would have been a real error

K1's control numbers are **staged**. My treatment ladders were **unstaged**. Comparing a staged
control (F6 23/30) against an unstaged treatment (24/30) would manufacture a difference out of the
staging alone. So the treatment has to be re-laddered with the same staging.

`K4_staged_ladder.py` does that as a thin wrapper: it imports **K1's own `K1_rung3` module** and
repoints `ICL` at K4's results tree. K4's tree has the identical shape
(`<root>/<cell>/<run>_icl_s<N>/<task>/inputs`), so K1's seed extraction works unchanged. None of
K1's logic, taxonomy, staging, root rule, timeout or classifier is touched, and nothing K1 wrote is
modified.

### ARM A ON THE CLEAN LADDER — the headline number gets much smaller

```
                                unstaged (J3-comparable)     STAGED (K1 clean)
control  (F6)                            20/30                      23/30
treatment (Arm A)                        24/30                      27/30
ceiling                                  24/30                      30/30
headroom                                    +4                         +7
RAW delta                        +4 = 100% of headroom       +4 =  57% of headroom
ATTRIBUTABLE delta               +1 =  25% of headroom       +1 =  14% of headroom
```

Attribution on the clean ladder, per task-run:
```
  ? gain (variance)         AdvancedExampleThermoPoroElasticWellbore      s1
  ? gain (variance)         AdvancedExamplePureThermalDiffusionWellbore   s2
  + GAIN (hook, blocks=1)   TutorialHydraulicFractureWithAdvancedXML      s2
  ? gain (variance)         TutorialHydraulicFractureWithAdvancedXML      s3
  gains: hook=1 variance=3   losses: hook=0 variance=0
```

**J3's headline "+4 = 100% of the 24/30 achievable ceiling" does not survive contact with K1's
clean ladder.** Two independent corrections push the same way:
1. **K1's staging** raises both arms and lifts the ceiling to 30/30, so the same +4 is **57%** of
   headroom, not 100%.
2. **Attribution** shows 3 of the 4 gains are on runs the hook never blocked, leaving **+1 = 14%**.

Both corrections are necessary and they compound. The defensible statement for the paper is
**"+1 of 30 attributable, 14% of the clean headroom"**, with +4/57% as the raw upper bound.
Neither is 100%.

---

## Entry 12 — ARM B RESULTS (F8, S+X+M, corrected root rule). Campaign 10:48:46Z -> 11:31:31Z.

Integrity: 30/30 success, exit `{0: 30}`, 3 summaries `n_scored=10 n_failed=0 failed_names=[]`,
**zero null TreeSim**, 0 unpaired. Per-seed TreeSim: 0.80468 / 0.81228 / 0.79993.

### DOES THE VALIDATOR RESULT HOLD ON A SECOND CELL? YES for rung 3 and fabrication; NO for sigma.

```
                            unstaged (A1/J3-comparable)      STAGED (K1 clean, ceiling 30/30)
control  (F8)                        21/30                            24/30
treatment (Arm B)                    24/30                            25/30
RAW delta                    +3 = 100% of 24/30 headroom       +1 =  17% of headroom
ATTRIBUTABLE delta           +1 =  33% of headroom             +1 =  17% of headroom
TreeSim                    0.7827 -> 0.8056  (+0.0229)
rung 1 / rung 2                    30/30 -> 30/30 (no change, as on F6)
```

**Fabrication: 0 task-runs, same as Arm A.** Only token hits are the legitimate
`AdvancedExampleViscoExtendedDruckerPrager` / `triaxialDriver_base.xml` dummy mesh, present in the
ground truth *and* the control in all 3 seeds. Orphan rule fired **6x**
(`class09_pb3_drainageOnly` x4, `class09_pb3_hystRelperm` x2), **spurious blocks = 0**, genuine
blocks = 4.

### *** THE STRIKING CROSS-ARM RESULT: both arms land on ATTRIBUTABLE +1, on the SAME TASK ***

```
                       clean staged ladder, ceiling 30/30
ARM A (F6)    23/30 -> 27/30   RAW +4 (57%)   ATTRIBUTABLE +1 (14%)
ARM B (F8)    24/30 -> 25/30   RAW +1 (17%)   ATTRIBUTABLE +1 (17%)
```
And in **both** arms the single attributable gain is `TutorialHydraulicFractureWithAdvancedXML`
(Arm A s2, Arm B s1) — the same task J3 identified as its only hook-driven improvement. Across
three independent campaigns on two different cells, **the entire attributable benefit of the
validator swap concentrates on one task out of ten.**

Note the raw numbers move in opposite directions once the ladder is clean: Arm A's +4 survives as
+4 (57% of a bigger headroom), while Arm B's +3 **collapses to +1**, because staging lifts F8's
control from 21 to 24 and simultaneously exposes 2 *losses* on `ExamplesingleFracCompression`
(s1, s3, both on zero-block runs). That is a concrete demonstration that the unstaged ladder was
inflating the apparent effect.

### *** SIGMA INFLATION DOES NOT REPLICATE — J3's claim is cell-specific, not a property of the swap ***

```
              control sigma   treatment sigma   ratio
ARM A (F6)       0.0018           0.0148        8.12x   *** INFLATED ***
ARM B (F8)       0.0215           0.0062        0.29x   *** REDUCED ***
J3    (F6)       0.0018           0.0240       13.0x    *** INFLATED ***
```
On F8 the swap **reduced** across-seed sigma by 3.5x. F6's control sigma is anomalously tiny
(0.0018) and F8's is 12x larger (0.0215) before any intervention, so the two cells were never
comparable on this axis. **The honest statement is: the swap moves TreeSim seed-variance toward
~0.006-0.015 regardless of where the cell started** — which inflates F6's exceptionally low sigma
and deflates F8's high one. J3's "the swap destroys the low-sigma selling point" is real for F6 but
must **not** be generalised to the swap. I would have reported it as a general cost had I only run
one cell; this is Arm B's main methodological payoff.

Both arms agree that **rung 3 becomes more stable**: per-seed rung3 goes 7/7/7 -> 8/8/8 (Arm B) and
7/6/7 -> 8/8/8 (Arm A).

### TreeSim attribution — opposite sign to Arm A, so no reliable effect either way
```
ARM B  TreeSim on INTERVENED    runs (n= 4): 0.5657 -> 0.6198  (+0.0540)
ARM B  TreeSim on NEVER-BLOCKED runs (n=26): 0.8161 -> 0.8342  (+0.0182)
ARM A  TreeSim on INTERVENED    runs (n= 6): 0.5413 -> 0.5055  (-0.0357)
ARM A  TreeSim on NEVER-BLOCKED runs (n=24): 0.8415 -> 0.8485  (+0.0071)
```
Arm A's intervened runs got **worse** by 0.036; Arm B's got **better** by 0.054. With n=4-6
intervened runs per arm and opposite signs, **there is no measurable TreeSim effect of the hook in
either direction.** This settles the objective-mismatch question the honest way: underpowered, not
demonstrated. Arm B's Q2 (rung 3 up / TreeSim down) is empty, as was Arm A's.

### QUADRANTS — Arm B
```
Q1 r3 UP / TreeSim UP     — 0 tasks
Q2 r3 UP / TreeSim DOWN   — 0 tasks
Q3 r3 UP / TreeSim FLAT   — 1 task
   TutorialHydraulicFractureWithAdvancedXML  r3 0/3->3/3  TreeSim 0.013->0.013  blocks=1
Q4 r3 FLAT                — 9 tasks  (largest moves: ExampleIsothermalHystInjection +0.072 blocks=3,
                                      ExampleVerticalPoroElastoPlasticWellbore +0.069 blocks=0,
                                      ExampleMCCWellbore +0.047 blocks=0)
Q5 r3 DOWN                — 0 tasks
```
`TutorialHydraulicFractureWithAdvancedXML` goes **0/3 -> 3/3** while TreeSim stays pinned at 0.013 —
an even cleaner version of J3's orthogonality result (J3 and Arm A saw 1/3 -> 3/3). The deck now
loads in every seed while remaining structurally nothing like the reference. **Loadability and
structural similarity are orthogonal: now demonstrated on the same task in three independent
campaigns, and in Arm A on a second task at the opposite end of the TreeSim range (0.956).**

### RETRY BUCKETS — budget not binding, third arm running
```
clean_first_try                          26/30
blocked_allowed_but_ladder_still_fails    3/30  (ExampleIsothermalHystInjection s1,s2,s3)
blocked_then_repaired                     1/30  (TutorialHydraulicFractureWithAdvancedXML s1)
BLOCKED_EXHAUSTED_terminated_with_defect  0/30
SPURIOUS_BLOCK_ONLY_harness_defect        0/30
runs exhausting the retry budget on GENUINE blocks = 0/30  => NOT binding
```

### EFFICIENCY — tool-call regression replicates; wall-clock advantage replicates and grows
```
                 control   treatment   delta%    vs Vanilla (90.5 / 416.5 s)
tools/task          82.9       108.2   +30.5%              +19.5%
sec/task           358.1       290.8   -18.8%              -30.2%
per-seed tools control  : 98.2 / 81.3 / 69.2
per-seed tools treatment: 107.0 / 108.5 / 109.0
```
Three campaigns now agree the swap costs tool calls and lands **above Vanilla**: J3 115.7 (+27.8%),
Arm A 111.5 (+23.2%), Arm B 108.2 (+19.5%). And three campaigns agree wall-clock **improves**:
330.7, 317.6, 290.8 s vs Vanilla's 416.5 (-20.6%, -23.7%, -30.2%). Note the treatment's per-seed
tool counts are far *tighter* than the control's (107.0/108.5/109.0 vs 98.2/81.3/69.2) — the hook
makes effort predictable as well as larger.

### COST
```
estimate $0.60  |  ACTUAL $0.5475  ($0.0183/run)  error -8.8%  |  control $0.3975  |  ratio 1.38x
```
Cumulative K4 spend: **$1.1579 / $10.00** (11.6% of cap).

---

## Entry 13 — Arm C launch verification (new cell, never run before)

`autocamp_K4C` had never been executed, so I verified its runtime behaviour on the first completed
tasks rather than waiting for the campaign:

```
claude_mcp_config.json  : {"mcpServers": {}}      <- ZERO agent-callable tools, as designed
hook event files        : present per completed run (30/30 on Arms A and B; C accrues as it goes)
orphan_skip_enabled     : true
process_status          : success on every completed task
```
Confirms the cell delivers what Arm C claims: Vanilla's prompt, no MCP tools, hook active.

One false alarm worth recording so nobody re-investigates it: several K4C task dirs briefly showed
an **empty `inputs/` and no `.verify_hook_events.jsonl`**. That is simply an in-flight run
(`process_status: running`) — the hook writes its event log at the Stop event, so the file does not
exist until the agent finishes. Both completed arms have exactly **30/30** hook-event files.

---

## Entry 14 — ARM C RESULTS: Vanilla + nothing but a `geosx -v` stop hook. Campaign 11:31:49Z -> 12:17:31Z.

Integrity: 30/30 success, exit `{0: 30}`, 3 summaries `n_scored=10 n_failed=0 failed_names=[]`,
**zero null TreeSim**, 0 unpaired. Fabrication: **0** task-runs (only the legitimate TriaxialDriver
dummy mesh). Orphan rule fired 4x, **spurious blocks 0**, genuine blocks 3.

### THE COMPARISON THE BRIEF ASKED FOR

```
                        Vanilla(F0)   F6 = S+X    ARM C = Vanilla + geosx hook ONLY
TreeSim (faz)              0.7196       0.7814              0.7839
rung 1                     27/30        30/30               30/30
rung 2 (xmllint schema)    24/30        30/30               30/30
rung 3 unstaged            19/30        20/30               24/30
rung 3 STAGED (K1 clean)   21/30        23/30               26/30      ceiling 30/30
tools/task                  90.5         74.7                97.7   (+8.0% vs Vanilla)
sec/task                   416.5        345.1               315.0   (-24.4% vs Vanilla)
```

**As measured, one hook on plain Vanilla matches or beats the S+X cell on every quality axis** —
TreeSim 0.7839 vs 0.7814, rung 1 and rung 2 both 30/30, rung 3 **26/30 staged vs 23/30**. It also
beats **every** published staged cell (K1: F0 21, F4 21, F6 23, F8 24, F11 23, SE 24). The tool cost
is **+8.0% over Vanilla**, versus +23.2% (Arm A) and +19.5% (Arm B) for the swap on top of the full
stack, and wall-clock is **-24.4%**.

### *** BUT: THE ATTRIBUTION SAYS THE HOOK DID ALMOST NONE OF IT ***

The hook fired **3 times in 30 runs. All 3 were `geosx_error`. Zero `parse_error`, zero `no_xml`.**
Every one of the 30 runs terminated `allow: xml_clean`.

```
BLOCKS: {'geosx_error': 3}      ALLOWS: {'xml_clean': 30}
```

On K1's clean staged ladder:
```
K1 staged Vanilla 21/30 -> Arm C 26/30    headroom +9
  ? gain (variance)      AdvancedExampleThermoPoroElasticWellbore    s1
  ? gain (variance)      ExampleProppantTest                         s1
  ? gain (variance)      TutorialHydraulicFractureWithAdvancedXML    s1
  ? gain (variance)      TutorialHydraulicFractureWithAdvancedXML    s2
  ? gain (variance)      AdvancedExampleCasedThermoElasticWellbore   s3
  - loss (variance)      ExamplesingleFracCompression                s3
  + GAIN (hook, 1 block) TutorialHydraulicFractureWithAdvancedXML    s3
RAW          +5 = 56% of headroom
ATTRIBUTABLE +1 = 11% of headroom
```

### *** THE RUNG-2 GAIN CANNOT BE THE HOOK, AND THAT MATTERS FOR A PAPER HEADLINE ***

Arm C improves rung 2 by **+6** (24/30 -> 30/30) — exactly the gap the paper attributes to the
adapter cells. **But `GEOS_HOOK_XMLLINT=0` in this arm and the hook issued zero parse/schema blocks.
There is no mechanism by which it could have caused this.** The hook is invisible to the agent unless
it blocks; it never blocked on a schema or well-formedness issue.

The reason is visible per seed:
```
Vanilla F0 control :  s1 rung2 8/10 | s2 rung2 10/10 | s3 rung2 6/10
Arm C              :  s1 rung2 10/10 | s2 rung2 10/10 | s3 rung2 10/10
```
**Vanilla's own seed 2 already scores a perfect 10/10 on rung 2.** Its 24/30 is driven entirely by
seeds 1 and 3, and its per-seed rung-1 spread is 9/10, 10/10, 8/10. The `<<TagTag>` malformed-XML
failure mode is stochastic and clustered by seed.

**Cross-thread flag for K1 and for whoever writes this up:** K1 reports rung 2 as its *surviving*
significant result ("F0 24/30 vs 30/30, p = 0.0237"). Arm C is the closest thing anyone has run to a
**fresh replicate of Vanilla** on rung 2 — behaviourally identical for rungs 1-2, since the hook
never fired on them — and it scored **30/30**. That does not refute the effect, but it does say the
Vanilla 24/30 figure is **seed-unstable at n=3**, and a 4th, 5th and 6th Vanilla seed could plausibly
move it a long way. This deserves checking before the rung-2 result is leaned on in the rebuttal.

### QUADRANTS — Arm C is the only arm with a rung-3 REGRESSION
```
Q1 r3 UP / TreeSim UP   — 3 tasks   (all zero-block)
   AdvancedExampleThermoPoroElasticWellbore   r3 2/3->3/3  0.355->0.680 (+0.325)  blocks=0
   ExampleProppantTest                        r3 2/3->3/3  0.541->0.819 (+0.278)  blocks=0
   AdvancedExampleCasedThermoElasticWellbore  r3 2/3->3/3  0.847->0.919 (+0.072)  blocks=0
Q2 r3 UP / TreeSim DOWN — 0 tasks
Q3 r3 UP / TreeSim FLAT — 1 task
   TutorialHydraulicFractureWithAdvancedXML   r3 0/3->3/3  0.013->0.013 (+0.000)  blocks=1
Q4 r3 FLAT              — 5 tasks
Q5 r3 DOWN              — 1 task
   ExamplesingleFracCompression               r3 1/3->0/3  0.891->0.902 (+0.011)  blocks=0
```
The three Q1 tasks carry TreeSim gains of +0.325, +0.278 and +0.072 — the largest moves anywhere in
this thread — and **all three had zero hook blocks.** Against that, Arm C's 3 intervened runs moved
TreeSim **-0.018**. The mean TreeSim gain of +0.0643 over Vanilla is therefore almost entirely
carried by runs the hook never touched.

`TutorialHydraulicFractureWithAdvancedXML` again: **0/3 -> 3/3 with TreeSim pinned at 0.013**, one
genuine block. Fourth independent reproduction of the orthogonality result.

### SIGMA — the swap *stabilises* a noisy cell, third data point
```
                     control sigma   treatment sigma   ratio
ARM A (F6)              0.0018          0.0148         8.12x   INFLATED
ARM B (F8)              0.0215          0.0062         0.29x   reduced
ARM C (Vanilla)         0.0809          0.0178         0.22x   reduced
J3    (F6)              0.0018          0.0240        13.0x    INFLATED
```
Three cells now agree with the reading I proposed in Entry 12: **the hook pulls across-seed TreeSim
sigma toward ~0.006-0.018 regardless of where the cell started.** It inflates F6's anomalous 0.0018
and it *collapses* Vanilla's 0.0809 by 4.5x. Per-seed rung 3 goes 6/7/6 -> **8/8/8**. So the honest
framing is **"the hook makes outcomes more uniform"**, not "the hook destroys reliability" — J3's
conclusion was an artefact of picking the one cell with a freakishly low baseline sigma.

### RETRY BUCKETS
```
clean_first_try                          27/30
blocked_allowed_but_ladder_still_fails    2/30  (ExampleIsothermalHystInjection s1, s2)
blocked_then_repaired                     1/30  (TutorialHydraulicFractureWithAdvancedXML s3)
BLOCKED_EXHAUSTED_terminated_with_defect  0/30
SPURIOUS_BLOCK_ONLY_harness_defect        0/30
runs exhausting the retry budget on GENUINE blocks = 0/30  => NOT binding
```

### COST
```
estimate $0.62  |  ACTUAL $0.5791 ($0.0193/run)  error -6.6%  |  Vanilla control $0.4128  |  1.40x
```

---

## Entry 15 — CROSS-ARM SYNTHESIS

### The three arms on ONE ladder (K1's clean staged, ceiling 30/30)

| arm | cell | control | treatment | RAW | **ATTRIBUTABLE** | attributable task |
|---|---|---|---|---|---|---|
| A | F6 (S+X) | 23/30 | 27/30 | +4 (57%) | **+1 (14%)** | `TutorialHydraulicFractureWithAdvancedXML` s2 |
| B | F8 (S+X+M) | 24/30 | 25/30 | +1 (17%) | **+1 (17%)** | `TutorialHydraulicFractureWithAdvancedXML` s1 |
| C | K4C (S only) | 21/30 | 26/30 | +5 (56%) | **+1 (11%)** | `TutorialHydraulicFractureWithAdvancedXML` s3 |

**Three independent campaigns, three different cells, and every one lands on attributable +1 of 30 —
always on the same task.** Add J3 (+2 of 4 raw on F6, also `TutorialHydraulicFractureWithAdvancedXML`)
and the picture is unambiguous: **the causal, mechanism-verified benefit of swapping `xmllint` for
`geosx -v` is roughly one task-run in thirty, concentrated on a single task in the ICL-10 set.**
Everything above that is unpaired replicate variance between two independent 3-seed samples.

### Blocks are rare, and that is the real story

```
arm   genuine blocks / 30 runs    orphan skips   spurious blocks
A            6                         9               0
B            4                         6               0
C            3                         4               0
J3           3                         0               3   (uncorrected rule)
```
The validator swap changes the outcome of **3-6 runs in 30**. With effects that sparse, a 3-seed
design cannot separate the intervention from replicate noise — which is exactly what the attribution
column shows. **Any future version of this experiment needs more seeds, not more cells.**

### What replicated, what did not

| J3 claim | status after 3 more campaigns |
|---|---|
| Corrected root rule stops the fabrication | **CONFIRMED.** 1 -> 0 on Arm A; 0 on B and C. Spurious blocks 3 -> 0 in all arms. |
| `xmllint` is blind to cross-reference defects | **CONFIRMED, strongly.** All 13 genuine blocks across A/B/C are missing PVT models, missing constitutive models, phase-name mismatches, empty FieldSpecification target sets. The control's xmllint hook blocked **0 times in 30**. |
| Loadability ⟂ structural similarity | **CONFIRMED and strengthened.** 4 independent reproductions; Arm A adds a 2nd task at the opposite end of the TreeSim range (0.956). |
| rung 3 "+4 = 100% of the ceiling" | **DOES NOT SURVIVE.** K1's clean ladder + attribution reduce it to **+1, 11-17% of headroom**, on all three cells. |
| The swap inflates across-seed sigma 13x | **DOES NOT GENERALISE.** True only for F6 (anomalous 0.0018 baseline). On F8 sigma fell 3.5x, on Vanilla 4.5x. Correct statement: the hook pulls sigma toward ~0.006-0.018 either way, i.e. it makes outcomes **more uniform**. |
| The swap erases the efficiency story | **CONFIRMED for tool calls, REVERSED for wall-clock.** Tools vs Vanilla: +27.8 / +23.2 / +19.5 / +8.0 % (J3/A/B/C). Wall-clock vs Vanilla: -20.6 / -23.7 / -30.2 / -24.4 %. Four campaigns agree on both signs. |
| Retry budget binding | **NOT binding.** 0/30 exhausted on genuine blocks in every arm. |

### Arm C's answer to the question the paper cannot currently answer

> *How much of SIGA's benefit is obtainable from simulator-grounded end-of-turn verification alone?*

**As measured: essentially all of it, and more, at a fraction of the tool cost.**
Vanilla + one hook reaches TreeSim 0.7839 (vs S+X 0.7814, Vanilla 0.7196), rung 1 and rung 2 30/30
(equal to every adapter cell), and rung 3 **26/30 staged — above every published cell** (best: F8/SE
24/30). It costs **+8.0% tool calls** over Vanilla against S+X's **-17.5%**, and **saves 24.4%
wall-clock**.

**Causally: almost none of it is demonstrated.** +1 of 30 is attributable; the hook blocked 3 times;
and the +6 rung-2 gain has **no possible mechanism** because the hook issued zero schema/parse blocks.

Both halves are true and they must be reported together. The actionable version is:

> A single simulator-grounded stop hook, with no retrieval, no memory and no agent-callable
> validator, reproduces the entire measured benefit of the S+X configuration on held-out tasks at
> +8% tool overhead. But at n=3 seeds neither that result **nor the original factorial's S+X result**
> is separable from replicate variance — only 1 task-run in 30 changes through the verified
> mechanism. The cheap configuration is at least as well supported as the expensive one.

That last clause is the finding with teeth: **Arm C does not just make a case for the hook, it
undermines the case for the rest of the stack**, because the same attribution test applied to S+X
and S+X+M returns the same +1.

---

## Entry 16 — ARTIFACTS, DISCIPLINE, AND WHAT A HUMAN MUST DECIDE

### Artifacts (all under `neurips_review/sprint/artifacts/`)

| path | what |
|---|---|
| `K4_launch.sh` | all three arms (`K4_ARM=A|B|C`); the only deltas vs `J3_launch.sh` are the cell and `GEOS_HOOK_GEOSX_ORPHAN_SKIP=1` |
| `K4_score.sh` | scorer invocation, identical `batch_evaluate.py` + `experiments_gt` as the controls |
| `K4_analyze.py` / `K4_{A,B,C}_analyze_out.txt` / `K4_{A,B,C}_comparison.json` | one analysis path per arm, incl. the attribution decomposition |
| `K4_fabrication.py` / `K4_{A,B,C}_fabrication.csv` / `_affected.json` | J3's differential test, generalised; Arm A also scans J3's uncorrected arm |
| `K4_{A,B,C}_ladder_{control,treatment}.jsonl` + `.log` | unstaged ladders (J3/A1-comparable) |
| `K4_staged_ladder.py` / `K4_{A,B,C}_rung3_staged.jsonl` / `_bytaskrun.json` | K1's staged ladder repointed at K4's trees |
| `/data/matt/k4_validator_ablations/` | 90 runs + `_results_icl/*/\*/_summary.json` + `_logs/` |
| `plugin/hooks/verify_outputs.py` | **+402 insertions, 0 deletions** vs HEAD (J3 left it at +286) |
| `src/runner/docker_cmd.py` | +12 lines (J3's 11 + `-e GEOS_HOOK_GEOSX_ORPHAN_SKIP`) |
| `src/runner/agents.py` | +`autocamp_K4C` cell (F6 minus one line) |
| `scratchpad/k4_hooktest.py` | the 3-case unit test of the corrected rule against the real binary |

Everything is env-gated: with `GEOS_HOOK_GEOSX_ORPHAN_SKIP` unset the hook reproduces J3's arm
byte-for-byte, and with `GEOS_HOOK_GEOSX_VALIDATE` unset it reproduces the original xmllint campaign.

### Discipline
No writes to `/data/shared/`, `/data/jixuan/`, `writing/`, any `_`-prefixed directory, or **J3's
output tree**. No git commits. Reused `/home/matt/geos_runtime_J3` unmodified. Max 8 workers
throughout; arms run strictly sequentially (Arm C chained to start when B finished). Every dollar
figure computed from raw tokens x DeepSeek off-peak list price, never `total_cost_usd`.

### WHAT A HUMAN MUST DECIDE

1. **How to report the validator swap.** The defensible claim is **"+1 of 30 task-runs attributable,
   11-17% of clean headroom, replicated on three cells"** — not J3's "+4 = 100% of the ceiling".
   Decide whether a +1/30 effect is worth a rebuttal paragraph at all. My view: the **qualitative**
   finding (49/180 held-out decks pass `xmllint` but are rejected by GEOS; the control's xmllint hook
   blocked 0 times in 30 while GEOS refuses 10 of those 30) is strong and stands on its own. The
   quantitative improvement from acting on it is currently ~1 in 30 and should not be oversold.

2. **Whether to run more seeds.** This is the single highest-value follow-up and it is cheap. The
   hook changes 3-6 runs in 30, so n=3 seeds cannot separate it from noise — that limitation applies
   equally to **the paper's own S+X result**. At ~$0.02/run, 7 more seeds on Vanilla, S-only and S+X
   is ~**$4** and would settle both questions. I did not launch it: it is outside my brief and it
   materially affects a published table, so it needs a human decision.

3. **Whether Arm C changes the paper's recommendation.** Vanilla + one hook matches or beats S+X on
   every measured quality axis at +8% tool overhead and -24% wall-clock, and beats every published
   staged cell on rung 3. If that holds with more seeds it is a **simpler and more actionable
   recommendation than the factorial**, and it partly undercuts the case for retrieval + memory +
   agent-callable validator. That is a narrative decision, not a measurement one.

4. **The rung-2 stability question — flag to K1.** K1's surviving significant result is rung 2
   (F0 24/30 vs 30/30, p = 0.0237). Arm C is effectively a fresh Vanilla replicate for rungs 1-2
   (the hook never fired on them) and scored **30/30**; Vanilla's own per-seed rung 2 is
   **8/10, 10/10, 6/10**. The effect may be seed-unstable. Worth checking before leaning on it.

5. **Whether to ship the corrected root rule.** Recommend **yes** — it is env-gated, purely additive,
   provably eliminates the fabrication, and cost nothing in blocks (all 13 genuine blocks across the
   three arms are real cross-reference defects). Its one accepted false-negative is documented in
   Entry 2: a deck that genuinely *is* the root but omits `<Mesh>` will now pass unblocked, and no
   discriminator exists that separates it from an orphan fragment.

### Loose ends I did not close
- Arm C bundles the Stop hook's unconditional parse-check floor with geosx validation (Entry 3). It
  did not matter empirically here — **zero** parse blocks fired in Arm C — but a clean decomposition
  would need a 4th arm (Vanilla + parse-check-only hook).
- The `blocked_allowed_but_ladder_still_fails` bucket (3/30 in A and B, 2/30 in C, all
  `ExampleIsothermalHystInjection`) reflects the hook exempting `missing_external_asset` while the
  ladder does not. K1's staging removes the disagreement at the ladder end; the hook's soft-failure
  policy could be revisited now that assets can be staged.

### Discipline verification (run at close)
```
git diff --numstat  (my three files)
  402  0  plugin/hooks/verify_outputs.py      <- purely additive
   49  4  src/runner/agents.py
   12  0  src/runner/docker_cmd.py            <- purely additive
```
The **4 deletions in `agents.py` are not mine**: they are comment-only lines in an unrelated
`abl_*` cell ("phantom RAG instruction" note), part of the pre-existing uncommitted edit J3 recorded
in its Entry 2 and present in `git status` before this thread started. My own change to that file
(`autocamp_K4C`) is purely additive.

```
find <control tree>          -newermt "2026-07-27 09:50"   -> empty (untouched)
find /data/matt/j3_geosx_validate -newermt "2026-07-27 09:52" -> empty (J3's tree untouched)
git log -1  -> f13d033 (unchanged; no commits made)
```
