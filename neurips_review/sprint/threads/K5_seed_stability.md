# Thread K5 — seed stability of the rung-2 schema-validity result

**Submission:** NeurIPS 2026 #31642 (SIGA)
**Owner:** K5. **Started:** 2026-07-27 12:32Z (overnight, researcher asleep).
**Budget:** $8.00 hard cap (remaining from $10 authorisation; K4 used $1.74).
**Results root:** `/data/matt/k5_seed_stability/` — NEVER J3's `/data/matt/j3_geosx_validate/`,
NEVER K4's `/data/matt/k4_validator_ablations/`, NEVER `/data/shared/`.
**Artifacts:** `/home/matt/sci/repo3/neurips_review/sprint/artifacts/K5_*`

---

## STATE OF PLAY

### *** VERDICT: the DIRECTION survives; the PUBLISHED NUMBER does not. ***
### *** Do NOT post "24/30 vs 30/30, p = 0.0237". The rate is 0.912, not 0.800, and the gap is 8.8 pp, not 20 pp. ***

Final: **17 seeds per cell, 170 held-out task-runs per cell**, of which **14 seeds / 140 runs per
cell are fresh, out-of-sample, and were run today back-to-back on the same endpoint.**

```
RUNG 2 (xmllint --schema)      F0 Vanilla        F6 S+X       gap    Fisher    task-perm   task-cluster bootstrap
published  s1-3    (n= 30)   24/ 30 = 0.800   30/ 30 = 1.000  20.0pp   0.0237     0.0308    +20.0pp [ +3.3, +36.7]
OUT-OF-SAMPLE s4-17 (n=140)  131/140 = 0.936  140/140 = 1.000   6.4pp   0.0034     0.0039     +6.4pp [ +1.4, +12.9]
POOLED     s1-17   (n=170)  155/170 = 0.912  170/170 = 1.000   8.8pp  <0.0001    <0.0001     +8.8pp [ +2.9, +16.5]
```

**What is wrong with the current response.** Vanilla's true schema-validity rate is **0.912**
(Clopper–Pearson 95% [0.859, 0.950]), not 0.800. The published 24/30 drew **seed 3 at 6/10 and seed
1 at 8/10 — the two lowest of seventeen draws.** The claimed effect is overstated by **2.3×**.

```
Vanilla rung 2, all seventeen seeds, out of 10:
  s1  s2  s3 | s4  s5  s6  s7  s8  s9 s10 | s11 s12 s13 s14 s15 s16 s17
   8  10   6 |  9  10  10  10  10   9   9 |   8  10   9   9  10   9   9
   ^^^^^^^^^ the published sample
```

**What is right about it, and is now far better supported than before.** Both adapter cells are
**perfect**: `autocamp_F6` **170/170** and `autocamp_F4` **100/100**, zero rung-1 and zero rung-2
failures in 270 held-out runs. Out-of-sample the gap is significant on all three pre-registered
tests, including the task-clustered ones the original never ran. The defensible claim is:

> On 10 held-out tasks × 17 seeds, SIGA's adapter configurations emit well-formed, schema-valid GEOS
> XML in **170/170** runs; the Vanilla baseline in **155/170 (91.2%)**. Difference **8.8 pp**,
> task-clustered bootstrap 95% CI **[+2.9 pp, +16.5 pp]**, task-stratified permutation p < 0.0001.

That is a *smaller* number than the one we were going to post and a *much* stronger result.

**Two-thirds of the deficit is not schema at all.** Of Vanilla's 15 pooled rung-2 failures, **10 are
rung-1 well-formedness failures** — nested XML comments (`<!--  <!--  -->`). Rung 1 alone: 160/170 vs
170/170, p = 0.0017, bootstrap CI [+0.6, +12.9]. The metric should be described as "well-formed and
schema-valid", not "schema validity".

**Rung 3 is dead and stays dead.** On K1's clean staged ladder at 10 seeds: F0 **78/100**, F6
**78/100** (Fisher p = 1.0000, bootstrap CI [−6.0, +5.0]), F4 75/100. No execution-validity advantage
exists at any sample size we have.

### How the pre-registered criteria actually resolved — reported in full, including where I was wrong at n = 7

| criterion | evaluated at | result |
|---|---|---|
| **F1** rate ≥ 0.93 (Entry 2) | s4–10, n=70 | **FIRED** (0.9571) — and stands: pooled rate 0.912 ≫ 0.800 |
| **F2** Fisher p > 0.05 (Entry 2) | s4–10, n=70 | fired (p = 0.2446) — **but this was an UNDERPOWERED null** |
| **F3** clustering (Entry 2) | s4–10, n=70 | fired (perm 0.2501; CI ∋ 0) — same, underpowered |
| **F4** overdispersion ≤ 0.05 (Entry 2) | s1–10, n=100 | fired (p = 0.0330, ICC 0.114) — **does NOT persist at n=17** (p = 0.1406, ICC 0.042) |
| **extension: all three (Entry 12)** | s4–17, n=140 | **ALL MET** → the residual claim **survives** |

Entry 12 was written at 15:42Z, *before* seeds 11–17 existed, precisely because "n.s. at n = 7" could
not distinguish "no effect" from "no power". It could not: at n = 14 the same test gives p = 0.0034.
**I am recording that my own n = 7 interim reading was too pessimistic**, and that F4 — which I
reported as a firing criterion at n = 10 — was itself a small-sample artifact driven by seed 3.
The one criterion that survived every enlargement is **F1: the published rate is simply wrong.**

| phase | what | status | est. $ | actual $ |
|---|---|---|---|---|
| 0 | Pre-registration + falsification criteria (Entry 2) | **DONE 12:32Z** | — | — |
| — | Smoketest, 1 Vanilla run | DONE 12:37Z | 0.02 | **0.0130** |
| — | Reproduction cross-check, 4 instruments | DONE 12:45Z, **all PASS** | 0 | 0 |
| 1 | `autocamp_F0` seeds 4–10 | COMPLETE 13:45Z | 0.97 | — |
| 2 | `autocamp_F6` seeds 4–10 | COMPLETE 15:05Z | 0.93 | — |
| 3 | `autocamp_F4` seeds 4–10 | COMPLETE 16:12Z | 0.96 | **1.1040** |
| 4 | Extension (pre-registered Entry 12): F0 + F6 seeds 11–17 | COMPLETE 18:56Z | 2.22 | — |
| — | Finalize pipeline (integrity, 4 instruments, analysis) | **COMPLETE 19:45Z** | 0 | 0 |

```
TOTAL API SPEND, from raw tokens x DeepSeek V4-flash off-peak list price (0.14 / 0.0028 / 0.28 per 1M):
   autocamp_F0  140 runs   $2.1873   ($0.0156/run)
   autocamp_F6  140 runs   $2.2980   ($0.0164/run)
   autocamp_F4   70 runs   $1.1040   ($0.0158/run)
   smoketest      1 run    $0.0130
   --------------------------------------------------
   351 runs                $5.6023   of $8.00  (70%)
```
Every run: `process_status: success`, exit 0. **351/351, zero failures, zero harness errors.**
Estimate for the same scope was $5.09; actual came in **+10%** (per-run cost is $0.0158 today against
the $0.0136 measured on the May control tree). `total_cost_usd` was never used — it computes at
Anthropic rates and overstates ~60x.

---

## Entry 0 — orientation, and what I am NOT rebuilding

Read in full before touching anything: `threads/K4_validator_ablations.md` (1218 lines),
`threads/K1_asset_staging_ladder.md`, `artifacts/{J3,K4}_launch.sh`, `artifacts/K1_rung3.py`,
`artifacts/K1_stage.py`, `artifacts/K4_staged_ladder.py`, `artifacts/A1_rungs12_perfile.py`,
`artifacts/K1_stats.py`, `scripts/launch_autocamp_scaleup.sh`,
`src/runner/{agents,docker_cmd,claude_settings}.py`.

**Reused as-is, not reimplemented:**
- `A1_rungs12_perfile.py` — rungs 1 & 2 (`xmllint --noout`, then `xmllint --schema`), per-file,
  framing F. This is the *exact instrument that produced the 24/30*.
- `K1_rung3.py` (which imports `A1_rung3.classify`, `root_decks`, `MISSING_RE`, `GEOSX`, `TIMEOUT`
  directly, so the taxonomy cannot drift) + `K1_stage.py` pools — rung 3, staged and unstaged.
- `K1_stats.py`'s `fisher()`, `wilson()`, `strat_perm()` — imported, not retyped.
- `J3_cost.py` — cost from raw tokens × DeepSeek V4-flash off-peak list price
  (0.14 / 0.0028 / 0.28 per 1M). **Never** `total_cost_usd`.
- K4's launcher pattern, with the hook env vars **removed** (see Entry 1).

### The critical fact about "seeds" in this codebase, verified in source not assumed

`grep -rn "seed" scripts/run_experiment.py src/runner/*.py` returns **exactly one hit**, and it is
a comment in an unrelated cell's docstring. **No RNG seed is passed to the model, the sampler, or
the container anywhere.** The `s1/s2/s3` suffix is a *replicate label* baked into the run name; the
run name reaches only `agent["results_dir"] / run_name / task_name` (`orchestrator.py:93`) and
metadata dicts. It never enters a prompt.

Consequence, and it is the whole basis of this thread: **"adding seeds" = drawing more independent
replicates from the same sampling distribution.** Seeds 4–10 are exchangeable with seeds 1–3 by
construction, provided the launch configuration is identical. That makes hard-rule 1 checkable
rather than aspirational, and it is checked in Entry 1.

---

## Entry 1 — the launch configuration, and the proof it is Vanilla and not something Vanilla-like

K4's Arm C is the cautionary tale: it *looked* prompt-identical to Vanilla (verified sha256) and
still carried three extra harness files into the workspace. I am not repeating that. My replicates
must be byte-identical in configuration to `scripts/launch_autocamp_scaleup.sh` Phase A, which is
the script that produced the published 24/30.

The original per-cell invocation, from `launch_autocamp_scaleup.sh`:

```
"autocamp_F0|plugin/GEOS_PRIMER_contract.md|0|"     # GEOS_HOOK_XMLLINT=0
"autocamp_F6|plugin/GEOS_PRIMER_contract.md|1|"     # GEOS_HOOK_XMLLINT=1
"autocamp_F4|plugin/GEOS_PRIMER_contract.md|0|"     # GEOS_HOOK_XMLLINT=0
RUN="${AGENT##autocamp_}_${SET}_s${SEED}"           # -> F0_icl_s4
--workers 8 --timeout 1500 --strip-baked-primer
--geos-primer-path plugin/GEOS_PRIMER_contract.md
--tmp-geos-parent /data/matt/geos_eval_tmp
--experiments-dir     /data/shared/.../experiments_from_mined_specs
--ground-truth-dir    /data/shared/.../experiments_gt
--results-root-dir    $RESULTS_ROOT/icl
--claude-model deepseek-v4-flash
```

**The ONLY thing `K5_launch.sh` changes is `--results-root-dir` and the seed number.** Everything
else — cell, primer, xmllint env, workers, timeout, model, experiments dir, ground-truth dir, run
naming — is copied verbatim. In particular:

- `GEOS_RUNTIME_HOST_DIR`, `GEOS_HOOK_GEOSX_VALIDATE`, `GEOS_HOOK_GEOSX_BIN`,
  `GEOS_HOOK_GEOSX_LDPATH`, `GEOS_HOOK_GEOSX_TIMEOUT`, `GEOS_HOOK_GEOSX_ORPHAN_SKIP` are all
  **explicitly `unset`** at the top of my launcher. J3's and K4's launchers *export* them; if any
  leaked into my environment I would be running K4's treatment and calling it Vanilla.
- `GEOS_HOOK_XMLLINT` is set per cell to the value the original campaign used (F0→0, F6→1, F4→0).

### The uncommitted-working-tree risk, and why it does not bite

`git status` shows J3/K4 left three runner files modified. I checked each diff rather than assuming
they are inert:

| file | diff | effect on my runs |
|---|---|---|
| `plugin/hooks/verify_outputs.py` | **+402 / −0**, purely additive | The geosx branch is gated on `GEOS_HOOK_GEOSX_VALIDATE`, which I unset. F0 has `plugin_enabled: False` so the hook is not even registered. |
| `src/runner/docker_cmd.py` | **+12 / −0**, purely additive | 1 conditional `-v` mount gated on `GEOS_RUNTIME_HOST_DIR` (unset) + 5 `-e` forwards of unset vars. Docker `-e VAR` with VAR unset in the parent forwards nothing. |
| `src/runner/claude_settings.py` | +7 / −1 | `stop_hook_timeout = 240 if _envflag("GEOS_HOOK_GEOSX_VALIDATE") else 30`. Unset ⇒ **30**, the shipped value, i.e. the original campaign's. |
| `src/runner/agents.py` | +49 / −4 | Adds the `autocamp_K4C` cell and comments. `autocamp_F0`, `autocamp_F6`, `autocamp_F4` definitions are **untouched** (verified by reading the diff hunks — neither hunk overlaps their line ranges). |

So with the geosx env vars unset the working tree reproduces the original campaign. This is
asserted, not assumed, and it is re-verified empirically in Entry 3 by the reproduction check.

---

## Entry 2 — *** PRE-REGISTRATION. Written 2026-07-27 12:32Z, BEFORE ANY RUN WAS LAUNCHED. ***

Nothing below may be changed once the first result lands. If I later want a different analysis I
will add it as clearly-labelled exploratory, and the pre-registered result stands as the answer.

### The claim under test

> Schema validity at rung 2, held-out ICL-10: **Vanilla (`autocamp_F0`) 24/30, every adapter cell
> 30/30, Fisher exact p = 0.0237.** (K1 thread, "two survivors worth keeping".)

This is the last surviving significant result in the response and is currently the centrepiece of
the reply to the Area Chair on execution validity.

### Why it is in doubt

1. Vanilla's per-seed rung-2 counts at n=3 are **8/10, 10/10, 6/10** — a spread of 4 on a
   10-run denominator. Seed 2 alone is a perfect 10/10.
2. K4 Arm C is prompt-identical to Vanilla (sha256-verified), issued **zero** schema and **zero**
   parse blocks — so for rungs 1–2 it is behaviourally Vanilla — and scored **30/30**.

A fourth Vanilla-like draw at 30/30 against an original 24/30, with no mechanism available to
explain the difference, is what seed noise looks like.

### Design

+7 independent replicates (seeds 4–10) of `autocamp_F0` and `autocamp_F6`, held-out ICL-10,
everything constant except the replicate index (Entry 1). Pooled with the published seeds 1–3 this
gives **n = 10 seeds = 100 task-runs per cell**. `autocamp_F4` added if budget allows.

### Primary and secondary estimands, fixed now

- **PRIMARY (the decisive test): seeds 4–10 ONLY, n = 70 per cell.** Seeds 1–3 are the sample that
  *generated* the hypothesis — 24/30 was selected for reporting *because* it was significant, so a
  pooled estimate inherits that selection. The unbiased test of "is the rung-2 gap real" is the
  out-of-sample replication. This is stated up front precisely because the pooled number will be
  more favourable to us and I do not want the freedom to prefer it after the fact.
- **SECONDARY (best overall estimate): pooled seeds 1–10, n = 100 per cell.**
- Both are reported, always together, with the new-only figure first.

### Statistics, fixed now

1. **Per-seed rung-2 counts** for all 10 Vanilla seeds, listed individually.
2. **Pooled rate** with **Clopper–Pearson exact 95% CI** (and Wilson, from `K1_stats.wilson`, for
   continuity with K1's tables).
3. **Seed-level variance**: observed variance of the 10 per-seed counts vs the binomial variance
   expected at the pooled rate. Formal test = **dispersion / overdispersion test**
   (χ² = Σ(kᵢ − n p̂)² / (n p̂(1−p̂)) on 9 df, two-sided) plus the **intra-seed ICC** implied by a
   beta-binomial fit.
4. **Fisher exact**, F0 vs F6, on the enlarged 2×2 (`K1_stats.fisher`, unchanged).
5. **Task-clustered test** — Fisher is optimistic here because runs cluster by task (A1 flagged
   this; the 6 original Vanilla rung-2 failures span only **4 distinct tasks**). Two clustered
   procedures, both pre-specified:
   - **(a) task-stratified exact permutation** — `K1_stats.strat_perm`, permuting the cell label
     within each (task, seed) block. This is the randomisation the design licenses.
   - **(b) cluster bootstrap over tasks** — resample the 10 tasks with replacement, 20 000 draws,
     percentile CI on the rate difference; p = 2 × min(P(Δ≤0), P(Δ≥0)).
6. **Rungs 1 and 3 get the same treatment** at the same n, rung 3 via K1's staged ladder (and
   unstaged, for A1/J3 comparability).

### *** FALSIFICATION CRITERIA — stated before any result exists ***

The claim **does not survive** if ANY of the following holds.

- **F1 — point estimate.** Vanilla's rung-2 pass rate on the new seeds (4–10) is **≥ 0.93**
  (≥ 65/70). 0.93 is the upper 95% Clopper–Pearson bound of the original 24/30 (exact CI
  [0.6143, 0.9160]); landing above it means the published 24/30 was not a representative draw.
- **F2 — significance.** Fisher exact p on the **new-seeds-only** F0-vs-F6 2×2 rises **above 0.05**.
- **F3 — clustering.** The task-stratified permutation p (5a) **exceeds 0.05**, or the task cluster
  bootstrap 95% CI for the rate difference **includes 0**. Either means the nominal Fisher result is
  an artifact of treating clustered runs as independent.
- **F4 — instability.** The overdispersion test on the 10 per-seed counts is significant
  (p ≤ 0.05), i.e. seed is a real variance component beyond binomial. In that case the honest
  finding is that **n = 3 cannot measure this quantity at all** — which is a substantive criticism
  of the paper's own design, and one we should make ourselves rather than have a reviewer make.

The claim **survives, strengthened**, only if: new-seeds Vanilla rate is in the neighbourhood of
0.80 (95% CI excluding 1.0), F2 and F3 both give p < 0.05, and F4 is not triggered.

An **intermediate** outcome — rate materially above 0.80 but below 0.93, or significance surviving
Fisher but not clustering — is reported as *"directionally present, not robustly significant"*, and
in that case my recommendation will be **not to lead the AC response with it**.

### Pre-committed reporting rule

Whatever lands, the negative reading is reported **first and in the state-of-play block**. If
Vanilla's rate rises and the gap closes, that goes at the top of the thread log and at the top of
the final answer, above every other finding, because it is the thing that changes what we post.

### Cross-check obligation (hard rule 4 — six harness bugs this sprint, every one flattering us)

Before any new number is trusted, my rungs-1/2 instrument and my rung-3 instrument are re-run on
the **published seeds 1–3** in the shared tree and must reproduce `K1_ladder_by_taskrun.csv`
**exactly, per task-run**. Any disagreement halts the thread. Recorded in Entry 3.

---

## Entry 3 — COST ESTIMATES (recorded 12:33Z, before any campaign launch) and the smoketest

### Cost, computed from raw tokens × DeepSeek V4-flash off-peak list price

`J3_cost.py` re-run by me on the published control tree (not copied from K4's log — re-measured,
and it reproduces K4's Entry 4 exactly):

```
autocamp_F0 (Vanilla)  runs=30  TOTAL=$0.4128  mean/run=$0.0138
autocamp_F6 (S+X)      runs=30  TOTAL=$0.4003  mean/run=$0.0133
autocamp_F4 (X+M)      runs=30  TOTAL=$0.4111  mean/run=$0.0137
```

**No hook-overhead multiplier applies to this thread.** K4 needed 1.45× because its arms ran
`geosx --validate-input` in-loop; my runs are the *original* configuration with the geosx validator
off, so the per-run cost should land on the control figure. I therefore quote the point estimate and
a 1.3× buffered ceiling.

| phase | cell | runs | $/run | **point est.** | 1.3× ceiling |
|---|---|---|---|---|---|
| smoketest | F0 | 1 | 0.0138 | $0.02 | $0.02 |
| 1 | autocamp_F0 | 70 | 0.0138 | **$0.966** | $1.256 |
| 2 | autocamp_F6 | 70 | 0.0133 | **$0.931** | $1.210 |
| 3 | autocamp_F4 | 70 | 0.0137 | **$0.959** | $1.247 |
| | | | **total** | **$2.876** | **$3.73** |

**$3.73 worst case against an $8.00 cap = 47%.** Headroom is deliberate: if the primary result is
ambiguous, the highest-value marginal dollar is *more Vanilla seeds*, and I want to be able to buy
them without a second authorisation.

### Smoketest — 1 run, `F0_icl_s99`, `ExampleMCCWellbore`, 12:34:02Z → 12:37:28Z

Purpose was not plumbing but the **leaked-env-var disaster**: if any of J3's/K4's `GEOS_HOOK_GEOSX_*`
exports survived into my shell I would be running K4's treatment arm and reporting it as Vanilla.

```
=== geosx env purged: VALIDATE='<unset>' RUNTIME='<unset>' ===
exit_code 0, status.json process_status success, elapsed 203.4 s, cost $0.0130
```

And the decisive check — the workspace **file set**, diffed against a published Vanilla workspace:

```
diff <(ls -a .../K5/.../F0_icl_s99/ExampleMCCWellbore) \
     <(ls -a .../published/autocamp_F0/F0_icl_s1/ExampleMCCWellbore)
  -> WORKSPACE FILE SET IDENTICAL TO PUBLISHED VANILLA
grep -Ei "settings|mcp|verify_hook"  -> NONE
```

This is the exact test that exposed K4 Arm C's three extra harness files (`claude_settings.json`,
`claude_mcp_config.json`, `mcp_preflight.json`). My replicates carry **none** of them. They are
Vanilla, not Vanilla-like.

The smoketest run was then **moved out of the analysis tree** to `_smoketest/` so no ladder or
aggregation can pick up an `s99` that is not part of the design.

---

## Entry 4 — REPRODUCTION CROSS-CHECK (hard rule 4), and a real aggregation bug it caught

Six harness bugs this sprint, every one flattering us, every one caught by another thread
re-measuring. So before trusting any new number, both instruments were run over the **published**
seeds 1–3 and required to reproduce `K1_ladder_by_taskrun.csv` per task-run.

### Rungs 1 & 2 — PASS, exactly

`K5_rungs12.py` is a wrapper that imports `A1_rungs12_perfile.py` and repoints three module-level
constants. Same xmllint, same `schema.xsd`, same root/referenced computation, same framing F.

```
task-runs compared : 90        DISAGREEMENTS : 0
autocamp_F0: rung1=27/30 rung2=24/30   (K1: 27/30, 24/30)
autocamp_F4: rung1=30/30 rung2=30/30   (K1: 30/30, 30/30)
autocamp_F6: rung1=30/30 rung2=30/30   (K1: 30/30, 30/30)
  F0 s1: rung1= 9/10 rung2= 8/10
  F0 s2: rung1=10/10 rung2=10/10
  F0 s3: rung1= 8/10 rung2= 6/10
```

Vanilla's per-seed rung-2 counts **8 / 10 / 6** reproduce independently. The instrument is trusted.

### Rung 3 — FAILED on the first attempt. The measurement was right; my aggregation was wrong.

First run gave **F0 staged 20/30** against K1's published **21/30** (F6 23/30 matched). Rather than
accept a 1-run discrepancy as noise I diffed per task-run:

```
DISAGREE ('autocamp_F0','s3','ExampleProppantTest')   K1=1  K5=0
```

Cause: I had copied the aggregation from `K4_staged_ladder.py`, which ANDs `rung3_pass` over **every
strict-root deck row** in the jsonl. K1's *authoritative* rule (`K1_report.load_taskruns`, documented
in its module docstring) is AND over **lenient roots** only. On `autocamp_F0/s3/ExampleProppantTest`
the file `ProppantSlotTest_base.xml` is a strict root — no other deck `<Included>`s it under
ElementTree parsing — but is **not** a lenient root, and it fails standalone. The naive rule counted
that standalone failure against the task-run.

Fixed by importing `K1_report.load_taskruns` instead of reimplementing it. Re-aggregation:

```
compared 60   DISAGREEMENTS 0
autocamp_F0: 21/30      autocamp_F6: 23/30      (K1 published: 21 and 23)
harness_error deck-runs: 0
```

**Reproduction check now passes on both instruments, 0/90 and 0/60 disagreements.**

### Cross-thread note for K4 (checked, not merely suspected): no K4 number is affected

`K4_staged_ladder.py` carries the same naive rule, so I re-aggregated all three K4 arms from K4's own
`K4_{A,B,C}_rung3_staged.jsonl` + `_meta.json` using K1's correct rule:

```
ARM A : naive 27/30   correct 27/30   (K4 log says 27)
ARM B : naive 25/30   correct 25/30   (K4 log says 25)
ARM C : naive 26/30   correct 26/30   (K4 log says 26)
```

**Identical.** The bug is latent in K4's script — its treatment trees happen to contain no failing
strict-root-but-not-lenient-root deck — so K4's conclusions stand unchanged. Recording it because
the next thread to copy that file will not be so lucky.

### Rung 3 UNSTAGED — also PASS

```
K5 rung3 (none) autocamp_F0: 19/30      A1/K1 published: 19/30
K5 rung3 (none) autocamp_F6: 20/30      A1/K1 published: 20/30
harness_error deck-runs: 0
```

So all four instruments (rung 1, rung 2, rung 3 staged, rung 3 unstaged) reproduce the published
numbers on the published seeds before any new number is generated.

**Artifacts:** `K5_rungs12.py`, `K5_ladder.py`, `K5_repro_autocamp_{F0,F4,F6}.csv`,
`K5_repro_rung3_{staged,unstaged}.jsonl` + `_meta.json` + `_bytaskrun.json`.

---

## Entry 5 — campaign launched, and the analysis code written before the results exist

- **12:38:04Z** — `K5_CELL=autocamp_F0 K5_SEEDS="4 5 6 7 8 9 10" bash K5_launch.sh`, `--workers 8`,
  seeds run strictly sequentially inside the launcher.
- Phase 2 (`autocamp_F6`, seeds 4–10) is **chained** to start the moment Phase 1's process exits
  (`_logs/chain_f6.sh`), so the two campaigns never overlap — hard rule 7 caps parallelism at 8
  workers and each campaign uses all 8.

`K5_analyze.py` and `K5_power.py` were both written and committed to disk **before** the first new
seed finished. `K5_analyze.py` imports `fisher`, `wilson` and `strat_perm` from `K1_stats.py`, so
the significance machinery is literally the code that produced K1's published tables.

---

## Entry 6 — what the 6 published Vanilla rung-2 failures actually ARE (recorded before new results land)

Worth knowing before interpreting anything, because it determines whether a "schema validity" claim
is even about schema validity:

```
s1 AdvancedExampleThermoPoroElasticWellbore  ThermoPoroElasticWellbore_smoke.xml       rung1=0 unparseable
      parser error : Double hyphen within comment:  <!--      <!-- ---- Solve...
s1 TutorialHydraulicFractureWithAdvancedXML  walshQuarterNoChombo_smoke.xml            rung1=1 schema_invalid
      Element 'Hydrofracture', attribute 'initialTimeStep' ...
s3 AdvancedExampleCasedThermoElasticWellbore CasedThermoElasticWellbore_base.xml       rung1=1 schema_invalid
      Element 'Solvers', attribute 'gravityVector' ...
s3 AdvancedExampleThermoPoroElasticWellbore  ThermoPoroElasticWellbore_{base,benchmark}.xml  rung1=0 unparseable
      parser error : Comment must not contain '--' (double-hyphen)
s3 ExampleProppantTest                       ProppantSlotTest_{base,benchmark}.xml     rung1=0 unparseable
      parser error : Double hyphen within comment
s3 TutorialHydraulicFractureWithAdvancedXML  walshQuarterNoChombo_base.xml             rung1=1 schema_invalid
      Element 'Box', attribute 'xMin': [facet 'pattern'] ...
```

Three observations that matter for the AC response:

1. **Half of the "schema validity" gap is not schema at all — it is well-formedness.** 3 of the 6
   failing task-runs fail *rung 1*, and every one of those is the same lexical bug: a **nested XML
   comment** (`<!--   <!-- ... -->`), which is a hard XML parse error. Only 3 of 6 are genuine
   schema violations (`initialTimeStep`, `gravityVector`, `Box/xMin` pattern). Rung 2 is defined as
   AND-with-rung-1, so rung-1 failures propagate into it.
2. **The failures cluster hard on seed 3**, which contributes 4 of the 6 — consistent with Vanilla's
   per-seed counts 8/10, 10/10, 6/10 and the reason a 3-seed estimate is fragile.
3. **They cluster on tasks too: 6 failures over only 4 distinct tasks** (ThermoPoroElasticWellbore
   ×2, THFWAX ×2, CasedThermoElastic, ProppantTest). This is precisely why the nominal Fisher test is
   optimistic and why the pre-registration requires a task-clustered test.

---

## Entry 7 — INCREMENTAL RESULTS AS THEY LAND (monitoring only until the cell completes)

Written to disk as each seed finishes, per hard rule 5 (three agents killed by API 529s tonight).
**These are partial. No conclusion is drawn from them and no table is updated until the cell prints
`COMPLETE` and the integrity gate passes** — K4 Entry 9's lesson: scoring a cell mid-flight silently
manufactures failures, because a task dir with no XML scores rung1=rung2=0 rather than erroring.

Guard against exactly that: `K5_view.sh` builds a symlink view containing only seed dirs with
10/10 task dirs *and* `process_status: success` on every one. The instruments are pointed at the
view, never at the live tree.

### `autocamp_F0` (Vanilla), new seeds — rungs 1 & 2

| seed | rung 1 | rung 2 | landed |
|---|---|---|---|
| s4 | 10/10 | **9/10** | 12:48Z |
| s5 | 10/10 | **10/10** | 12:57Z |
| s6 | 10/10 | **10/10** | 13:07Z |

(published for comparison: s1 8/10, s2 10/10, s3 6/10)

---

## Entry 8 — *** THE PRIMARY RESULT. `autocamp_F0` seeds 4–10 complete, 13:45:16Z. ***

Reporting the negative first, per the pre-committed reporting rule in Entry 2.

### Integrity gate — PASS before anything was scored

```
expected runs 70   inspected 70   process_status {'success': 70}   exit codes {0: 70}   PROBLEMS 0
INTEGRITY GATE: PASS
```

### Vanilla rung 2, per seed, all ten seeds

| | s1 | s2 | s3 | s4 | s5 | s6 | s7 | s8 | s9 | s10 |
|---|---|---|---|---|---|---|---|---|---|---|
| rung 1 | 9 | 10 | 8 | 10 | 10 | 10 | 10 | 10 | 9 | 9 |
| **rung 2** | **8** | **10** | **6** | **9** | **10** | **10** | **10** | **10** | **9** | **9** |

```
PUBLISHED seeds 1-3 :  24/ 30 = 0.8000   Clopper-Pearson 95% [0.6143, 0.9229]
NEW seeds 4-10      :  67/ 70 = 0.9571   Clopper-Pearson 95% [0.8798, 0.9911]   *** PRIMARY ***
POOLED seeds 1-10   :  91/100 = 0.9100
```

**Falsification criterion F1 fires.** F1 was "new-seeds rate ≥ 0.93". Observed **0.9571**. The
out-of-sample point estimate lands *above* the upper 95% confidence bound of the published figure —
0.957 vs an upper bound of 0.923. On the pre-registered reading, the published 24/30 is not a
representative estimate of Vanilla's schema-validity rate.

### Why the published number was low: one seed, and it is the minimum of ten

Seed 3 scored **6/10**, the lowest of all ten draws; seed 1 scored 8/10, the second lowest. The two
lowest draws in ten happened to be two of the three that were run. Seed 2 — the third published seed
— already scored a perfect 10/10, which is why K4's Arm C hitting 30/30 was a warning sign rather
than a puzzle.

### The four new-seed failures, and what they are

```
s4  TutorialHydraulicFractureWithAdvancedXML    walshQuarterNoChombo_base.xml       schema_invalid
       Element 'LinearSolverParameters', attribute ...
s9  AdvancedExamplePureThermalDiffusionWellbore thermalCompressible_2d_base.xml     unparseable (rung 1)
       parser error : Double hyphen within comment
s10 AdvancedExampleThermoPoroElasticWellbore    ThermoPoroElasticWellbore_base.xml      unparseable (rung 1)
s10 AdvancedExampleThermoPoroElasticWellbore    ThermoPoroElasticWellbore_benchmark.xml unparseable (rung 1)
```

Same two failure modes as the published seeds, in the same proportion: **3 of the 4 new failures are
nested-XML-comment parse errors (rung 1), not schema violations.** Across all ten seeds, Vanilla's
rung-2 deficit is 9 task-runs, of which **6 are `<!-- <!-- -->` well-formedness bugs**. That matters
for how the AC response is worded even in the pooled framing — the headline metric is not measuring
what its name says it measures.

### Fisher, computed the moment the cell closed (F6 pending; 70/70 assumed for the preview)

```
published : F0 24/ 30 vs F6 30/ 30    p = 0.0237   <- the number in the response
NEW ONLY  : F0 67/ 70 vs F6 70/ 70    p = 0.2446   <- PRIMARY, *** n.s.  F2 FIRES ***
POOLED    : F0 91/100 vs F6 100/100   p = 0.0032
```

The pooled p is *smaller* than the published p, and that is not a rescue — it is the arithmetic of a
larger n applied to an estimate that still contains the sample which generated the hypothesis. The
pre-registration (Entry 2) fixed the **new seeds as the primary estimand** precisely so this choice
could not be made after seeing the numbers. On the primary estimand the result is **not significant**.

The honest effect size moved from **20.0 pp to 4.3 pp**.

---

## Entry 9 — Vanilla's rung 3 ALSO rose, which forces a confound check: has the model drifted?

```
Vanilla, K1 clean STAGED ladder     published s1-3  21/30 = 0.700   CP95 [0.506, 0.853]
                                    NEW      s4-10  57/70 = 0.814   CP95 [0.703, 0.897]
                                    POOLED          78/100= 0.780
Vanilla, UNSTAGED (A1-comparable)   published       19/30 = 0.633
                                    NEW             53/70 = 0.757
per-seed staged, new: 8, 8, 8, 9, 7, 8, 9   (K1 published per-seed: 7, 7, 7)
harness_error deck-runs: 0
```

**All three rungs moved up for Vanilla on the new seeds.** Two explanations are available and they
are not equally comfortable:

**(a) the published 3 seeds were a low draw across the board** — supported by the rung-3 shift being
comfortably *inside* the published 95% CI ([0.506, 0.853] contains 0.814);

**(b) `deepseek-v4-flash` has changed behind the alias.** The published campaign is dated
**2026-05-02**; mine is **2026-07-27**, 86 days later. There is no version string to check — both
old and new `events.jsonl` report only `model=deepseek-v4-flash` — so I tested it behaviourally:

```
metric                  PUBLISHED n=30            NEW n=70        Mann-Whitney p
tool_calls              90.5  +- 35.6           109.7  +- 43.6         0.0382
elapsed_s              416.5  +-110.6           261.3  +- 70.4         0.0000
output_tokens        21150.9  +-8735.8        19827.8  +-6278.5        0.8420
total_input_tokens  973713.7  +-608244.8     868451.3  +-403319.8      0.3338
```

Token production is statistically indistinguishable (p = 0.84 / 0.33). Wall-clock is 37% faster,
which is serving-side latency on a different day rather than a behavioural change. Tool calls are up
21% at p = 0.038 — a weak signal that is not decisive either way, and is within the seed-to-seed
spread K4 measured on this cell.

**I cannot rule out model drift, and I am not going to pretend otherwise.** So state the limitation
plainly: *any* comparison between a number measured in May and a number measured in July is
confounded by time, and that includes the published 24/30 itself.

### Why the verdict survives the confound anyway

The decisive comparison does not span the two campaigns. **Seeds 4–10 of `autocamp_F0` and seeds
4–10 of `autocamp_F6` were run back to back on the same day, on the same endpoint, with the same
harness.** The new-seeds F0-vs-F6 contrast is therefore internally valid whatever the model did
between May and July, and it is the pre-registered PRIMARY estimand. Drift can move both arms; it
cannot manufacture or destroy the *gap between them* measured contemporaneously.

If anything the confound makes the situation worse for the response, not better: it means the
published 24/30 vs 30/30 is a snapshot whose absolute level is not reproducible 86 days later, which
is exactly the kind of fragility an Area Chair asking about execution validity is probing for.

---

## Entry 10 — THE POWER CALCULATION (the brief's second question), and a result that outranks it

K4 asked: the hook blocks only 3–6 times per 30 runs; **how many seeds would be needed to detect
that?** — noting the same limitation applies to the paper's own S+X result.

### The generative model, calibrated to K4's own numbers rather than invented

The mechanism fires independently on each run with probability `f`, and when it fires on a run that
would otherwise fail it converts it to a pass:  `p_treat(task) = p_ctrl(task) + f·(1 − p_ctrl(task))`.
K4 measured `f = 3/30 … 6/30`. At the observed clean-ladder Vanilla base rate `p0 = 0.780` (now
estimated from **100** task-runs, not 30) this yields a per-run effect of **0.022–0.044**, i.e.
**0.7–1.3 task-runs in 30** — which is exactly K4's measured attributable **+1/30**. The model is
calibrated to the thing it is being asked about, and it is the maximally *generous* version: every
single block is assumed to convert a failure into a pass.

Control per-task rates used (pooled Vanilla, 10 seeds, K1 staged ladder):

```
CasedThermoElastic 0.900 | PureThermalDiffusion 1.000 | ThermoPoroElastic 0.900
ViscoExtendedDruckerPrager 1.000 | IsothermalHystInjection 0.000 | MCCWellbore 1.000
ProppantTest 0.900 | VerticalPoroElastoPlastic 1.000 | singleFracCompression 0.700
THFWAX 0.400                                                       pooled p0 = 0.780
```

### Seeds required for 80% power (3000 simulations per cell)

| effect | per-run δ | Fisher (nominal) | task-clustered paired t |
|---|---|---|---|
| f = 1/30 (K4's attributable flip) | 0.0073 | **> 500 seeds** | **> 500 seeds** |
| f = 3/30 (Arm C block rate) | 0.0220 | **500 seeds** (5 000 runs/arm) | **> 500 seeds** |
| f = 6/30 (Arm A block rate) | 0.0440 | **150 seeds** (1 500 runs/arm) | **> 500 seeds** |

**Power at the paper's n = 3 seeds is 0.000 – 0.005 on the nominal test and 0.012 – 0.028 on the
clustered one.** The original design had roughly a **half of one percent** chance of detecting the
effect it reports having detected. K4's suspicion is confirmed with a number: n = 3 is not
"underpowered", it is *three orders of magnitude* from adequate.

### *** THE RESULT THAT OUTRANKS THE POWER CURVE: more seeds cannot fix this at all ***

Pushing the simulation to the infinite-seed limit, the per-task rate difference converges to
`δ_t = f·(1 − p_t)` and the task-clustered t-statistic converges to a **fixed** value:

```
      f   mean delta   sd across tasks   limiting t (df=9)   limiting p
   1/30       0.0073            0.0111               2.091       0.0660
   3/30       0.0220            0.0333               2.091       0.0660
   6/30       0.0440            0.0665               2.091       0.0660
  10/30       0.0733            0.1109               2.091       0.0660
```

**The limiting p is 0.0660 for every effect size.** That invariance is not an artifact: `f` is a
pure scale factor in `δ_t = f·(1 − p_t)`, so it cancels out of
`t = mean(δ)/(sd(δ)/√T)`. The limiting cluster-level p depends **only** on the heterogeneity of the
10 task base rates, not on how big the effect is.

So, plainly: **for a mechanism of this shape on this benchmark, no number of seeds will ever produce
a task-clustered p below 0.05.** A stronger hook would not help. A longer campaign would not help.
The binding constraint is that there are **10 tasks**, four of them pinned at 1.000, one pinned at
0.000 and one at 0.400.

K4 concluded "any future version of this experiment needs more seeds, not more cells." That is right
for the nominal test and **insufficient** for the clustered one. **A cluster-valid claim needs more
TASKS.** This is a limitation of the benchmark, not of any particular campaign, and we are far
better off stating it ourselves than having a reviewer derive it.

---

## Entry 11 — `autocamp_F6` (S+X) seeds 4–10 complete, 15:05:08Z. Integrity 70/70. THE FULL ANALYSIS.

```
expected 70   inspected 70   process_status {'success': 70}   exit codes {0: 70}   PROBLEMS 0
INTEGRITY GATE: PASS
F6 per seed, rungs 1 and 2:  s4..s10 all 10/10 and 10/10.   rung-2 failures: NONE
```

**F6 is 100/100 at rung 1 and rung 2 across ten seeds.** The adapter side of the claim is solid; it
is the Vanilla side that moved.

### RUNG 2 — the claim under test, all three pre-registered estimands

| estimand | F0 Vanilla | F6 S+X | gap | Fisher | task-strat perm | task cluster bootstrap |
|---|---|---|---|---|---|---|
| published s1–3 | 24/30 = 0.800 | 30/30 = 1.000 | 20.0 pp | **0.0237** | **0.0308** | **0.0114**, CI [+0.033, +0.367] |
| **NEW s4–10 (PRIMARY)** | **67/70 = 0.957** | 70/70 = 1.000 | **4.3 pp** | **0.2446 n.s.** | **0.2501 n.s.** | **0.0582**, CI [+0.000, +0.086] **∋ 0** |
| pooled s1–10 | 91/100 = 0.910 | 100/100 = 1.000 | 9.0 pp | 0.0032 | 0.0037 | 0.0023, CI [+0.030, +0.160] |

Clopper–Pearson 95% CIs: published F0 [0.614, 0.923]; **new F0 [0.880, 0.991]**; pooled F0
[0.836, 0.958]. The new point estimate 0.957 is **above** the published upper bound 0.923.

### Seed IS a real variance component — F4 fires, and this is the substantive methodological finding

```
F0 counts = [8,10,6,9,10,10,10,10,9,9]   p_hat=0.9100
    var_obs 1.656  vs  binomial 0.819    ratio 2.02x
    overdispersion chi2 = 18.193, df 9, p = 0.0330   *** OVERDISPERSED ***   implied ICC = 0.1135
F6 counts = [10]*10                       zero variance, ICC = 0
```

Vanilla's between-seed variance is **twice** what independent binomial sampling predicts, with an
intra-seed correlation of 0.11. Runs within a seed are *not* independent. That is the formal version
of "n = 3 cannot measure this": with an ICC of 0.11 and 10 runs per seed the design effect is
1 + 9×0.1135 = **2.02**, so 30 runs at n = 3 seeds carry the information of about **15** independent
runs, and the published Fisher p = 0.0237 is optimistic by that factor.

### Rung 1 — the well-formedness half was never significant

| estimand | F0 | F6 | Fisher | perm | bootstrap |
|---|---|---|---|---|---|
| published | 27/30 = 0.900 | 30/30 | 0.2373 n.s. | 0.2490 n.s. | 0.2135, CI ∋ 0 |
| new | 68/70 = 0.971 | 70/70 | 0.4964 n.s. | 0.5039 n.s. | 0.2097, CI ∋ 0 |
| pooled | 95/100 = 0.950 | 100/100 | **0.0594 n.s.** | 0.0639 n.s. | 0.0545, CI ∋ 0 |

This matters because **6 of Vanilla's 9 pooled rung-2 failures are rung-1 failures** — nested XML
comments (`<!--  <!--  -->`), a lexical bug, not a schema violation. Rung 2 is defined as
AND-with-rung-1, so the headline "schema validity" number is majority-composed of a failure mode
that has nothing to do with schema knowledge, and whose own test is **not significant** even pooled.

### Where Vanilla's remaining deficit lives — 2 tasks of 10

```
                                              F0      F6
AdvancedExampleThermoPoroElasticWellbore     7/10   10/10     <- 3 of the 9 failures
TutorialHydraulicFractureWithAdvancedXML     7/10   10/10     <- 3 of the 9 failures
CasedThermoElastic / PureThermalDiffusion / ProppantTest   9/10 each
the other 5 tasks                           10/10   10/10
```

Six of nine pooled failures sit on **two** of ten tasks — the same clustering that makes the nominal
Fisher optimistic and that the cluster bootstrap partially absorbs.

### RUNG 3 — the tie

```
K1 clean STAGED ladder            F0            F6         Fisher
published  s1-3                21/30 =0.700   23/30 =0.767   0.7710
NEW        s4-10               57/70 =0.814   55/70 =0.786   0.8330    <- Vanilla AHEAD
POOLED     s1-10               78/100=0.780   78/100=0.780   1.0000    <- EXACT TIE
```

At n = 10 seeds on the clean staged ladder, **Vanilla and S+X are indistinguishable at rung 3 —
78/100 each, p = 1.0000.** K1's finding that the rung-3 direction does not survive is confirmed at
3.3× the sample size, and on the new seeds the sign is actually reversed.

### RUNG 3 in full, both ladders, n = 10 seeds

```
K1 clean STAGED                s1  s2  s3 |  s4  s5  s6  s7  s8  s9 s10    pooled
F0 Vanilla                      6   8   7 |   8   8   8   9   7   8   9    78/100 = 0.780
F6 S+X                          8   7   8 |   9   8   7   8   9   7   7    78/100 = 0.780
UNSTAGED (A1/J3-comparable)
F0 Vanilla                      6   7   6 |   7   8   8   8   7   7   8    72/100 = 0.720
F6 S+X                          7   6   7 |   8   7   7   7   8   7   6    70/100 = 0.700
```

| ladder | estimand | F0 | F6 | Fisher | perm | bootstrap |
|---|---|---|---|---|---|---|
| staged | published | 21/30 | 23/30 | 0.7710 | 0.6269 | 0.4213, CI ∋ 0 |
| staged | **new (primary)** | **57/70** | 55/70 | 0.8330 | 0.7526 | 0.5467, CI ∋ 0 |
| staged | pooled | **78/100** | **78/100** | **1.0000** | 1.0000 | 1.0000, CI [−0.060, +0.050] |
| unstaged | pooled | **72/100** | 70/100 | 0.8763 | 0.7766 | 0.5956, CI ∋ 0 |

**On both ladders, at ten seeds, Vanilla is level with or ahead of S+X.** The staged pooled result is
an exact tie at 78/100 with p = 1.0000, and the cluster bootstrap CI [−6.0 pp, +5.0 pp] is tight
enough to rule out anything larger than a ±6 pp effect. K1's conclusion that the rung-3 direction
does not survive is confirmed at 3.3× the sample size — and on the *new* seeds the sign reverses.

Note also `TutorialHydraulicFractureWithAdvancedXML`, the single task on which J3 and all three K4
arms located their entire attributable benefit: at ten seeds it is **F0 4/10 vs F6 3/10**, i.e.
Vanilla ahead.

### The seed instability is specific to the XML-lexical rungs, not to loadability

```
                     overdispersion chi2 (df 9)      p        implied ICC
rung 2, F0                    18.193             0.0330      0.1135   *** OVERDISPERSED ***
rung 1, F0                     9.474             0.3947      0.0058
rung 3 staged,   F0            4.429             0.8810      0.0000
rung 3 unstaged, F0            2.778             0.9725      0.0000
rung 3 staged,   F6            3.263             0.9529      0.0000
```

Rung 3 is *under*-dispersed relative to binomial (variance ratio 0.21–0.49) — remarkably stable
across seeds. **Only rung 2 shows a genuine seed effect.** So the fragility is not a general property
of the benchmark; it is specific to the stochastic XML-authoring failure modes (nested comments,
occasional bad attribute values) that rung 2 aggregates — which is exactly the metric the response
currently leads with.

---

## Entry 12 — *** SECOND PRE-REGISTRATION, written 15:42Z BEFORE launching the extension ***

### Why extend at all

The primary question is answered: the published 24/30 / p = 0.0237 result does not survive. But the
answer leaves one thing genuinely undecided, and it is the thing the humans actually need:

> Is the **residual** gap real? Out-of-sample it is **4.3 pp** (F0 67/70 vs F6 70/70) and **not
> significant** — but n = 7 seeds has little power against a 4 pp difference when one arm is pinned
> at 100%. "Not significant" here does not distinguish "no effect" from "underpowered".

That distinction changes the recommendation. If the residual gap is real, the response can make a
**much weaker but honest** claim ("adapter cells emit schema-valid XML in 100/100 runs; Vanilla
fails ~5–9% of the time"). If it is not, the response should claim **nothing** at rung 2.

### The extension

**+7 more seeds (s11–s17) on `autocamp_F0` and `autocamp_F6`**, identical configuration
(`K5_launch.sh`, unchanged). This is the contingency for which Entry 3 deliberately reserved
headroom: *"if the primary result is ambiguous, the highest-value marginal dollar is more Vanilla
seeds, and I want to be able to buy them without a second authorisation."*

Final n = **17 seeds** per cell = 170 task-runs; **out-of-sample n = 14 seeds = 140 task-runs**.

### Cost, estimated before launch, from MEASURED per-run cost of this thread's own runs

```
F0 measured this thread: $1.0957 / 70 = $0.01565 /run   ->  70 runs = $1.096
F6 measured this thread: $1.1202 / 70 = $0.01600 /run   ->  70 runs = $1.120
                                                extension estimate = $2.216
```

Cumulative projection: $2.2289 (done) + ~$1.10 (F4, in flight) + $2.216 = **~$5.55 of $8.00 (69%)**,
leaving ~$2.45. If F4 overruns, the extension is cut to F0-only ($1.10) rather than breaching the cap.

### Falsification criteria for the extension — fixed now, before any of it runs

Primary estimand stays **out-of-sample**, now seeds 4–17 (n = 140/arm).

- **The residual claim SURVIVES** only if all three hold on seeds 4–17:
  Fisher p < 0.05 **and** task-stratified permutation p < 0.05 **and** task cluster bootstrap 95% CI
  excludes 0.
- **The residual claim DIES** if the out-of-sample Fisher p is still > 0.05 at n = 140/arm. At that
  sample size, with F6 pinned at 100%, a true 4.3 pp gap would produce ~6 Vanilla failures against 0
  and Fisher p ≈ 0.03 — so a null at n = 140 is an informative null, not an underpowered one.
- Either way, **the verdict on the published claim (Entry 11) is unchanged and stands.** This
  extension can only decide the size of the *replacement* claim, never resurrect the original.

I am writing down in advance the recommendation that follows from each branch, so it cannot be
chosen after the fact:
- survives → recommend the response state the **pooled 17-seed rate with the cluster bootstrap CI**,
  and explicitly retract the 24/30 framing.
- dies → recommend the response make **no rung-2 claim**, and use the qualitative finding instead.

---

## Entry 13 — `autocamp_F4` (X+M) seeds 4–10 complete, 16:12Z. The second adapter cell is also perfect.

```
INTEGRITY GATE: PASS   (70 runs, process_status {'success': 70}, exit {0: 70}, 0 problems)
F4 per seed s4..s10:   rung1 = 10/10 every seed,  rung2 = 10/10 every seed
F4 TOTAL new seeds  :  rung1 70/70,  rung2 70/70   ->  pooled with published: 100/100 and 100/100
cost: $1.1040 (70 runs, $0.0158/run) against a $0.959 estimate
```

So at ten seeds:

```
                 rung 1        rung 2
F0 Vanilla       95/100        91/100
F4 X+M          100/100       100/100
F6 S+X          100/100       100/100
```

**Two independent adapter cells, 200 task-runs between them, zero rung-1 and zero rung-2 failures.**
That half of the original claim ("30/30 for every adapter cell") is not merely intact — it is much
more strongly supported at n = 10 than at n = 3. The result that broke is the *Vanilla baseline*,
whose true rate is 0.91, not 0.80.

This also rules out the most obvious alternative explanation for the whole thread. If my harness or
the July endpoint were systematically easier than the May campaign, the adapter cells would have had
nowhere to go — they were already at 30/30 — but the *pattern* would show up as Vanilla converging
toward the adapters from below, which is what happened, **and** as a change in the adapters' own
failure profile, which did not happen (0 failures then, 0 failures now, on 70 more runs each).

### F4 at rung 3 — Vanilla is joint-best at ten seeds

```
K1 clean STAGED ladder, pooled n=10 seeds
  F0 Vanilla   78/100 = 0.780
  F4 X+M       75/100 = 0.750     (published 21/30; new seeds 54/70)
  F6 S+X       78/100 = 0.780
```

Vanilla ties the best adapter cell and beats the other. Combined with the exact 78/100–78/100 tie
against F6 (p = 1.0000), **there is no rung-3 execution-validity advantage to report at any sample
size we have.** K1 reached this at n = 3; it is now confirmed at n = 10 with 300 task-runs.

---

## Entry 14 — extension, `autocamp_F0` seeds 11–17 complete 17:31Z. The residual gap looks REAL.

```
F0 EXTENSION seeds 11-17:   s11 8/10  s12 10/10  s13 9/10  s14 9/10  s15 10/10  s16 9/10  s17 9/10
                            rung 2 TOTAL 64/70 = 0.914   (rung 1: 65/70)
```

Note this tranche is *lower* than the first: 0.914 vs 0.957. Seeds 4–10 were themselves a somewhat
high draw, just as seeds 1–3 were a low one. The two tranches bracket the pooled estimate, which is
the cleanest possible demonstration of the point this thread exists to make.

```
Vanilla rung 2, per seed, ALL SEVENTEEN:
  s1  s2  s3 | s4  s5  s6  s7  s8  s9 s10 | s11 s12 s13 s14 s15 s16 s17
   8  10   6 |  9  10  10  10  10   9   9 |   8  10   9   9  10   9   9
```

```
out-of-sample s4-17 :  131/140 = 0.9357     vs F6 (140/140 pending): Fisher p = 0.0034
pooled       s1-17  :  155/170 = 0.9118
```

**So the residual gap is looking real once there is enough power to see it** — which is exactly the
question Entry 12 was pre-registered to answer, and the opposite of the n = 7 result (p = 0.2446).
That contrast is itself the finding: **at 7 out-of-sample seeds the residual effect was invisible;
at 14 it is p ≈ 0.003.** Awaiting F6 seeds 11–17 before anything is concluded — the p above assumes
F6 stays perfect and is therefore provisional.

The verdict on the **published** claim is untouched by this and stands: Vanilla's rate is **0.912**,
not 0.800, and the gap is **~8.8 pp**, not 20 pp.

---

## Entry 15 — FINAL RESULTS AT n = 17 SEEDS. Extension complete 18:56Z, finalize 19:45Z.

Integrity: `autocamp_F0` **140/140** and `autocamp_F6` **140/140** on the extension seeds,
`process_status {'success': ...}`, exit `{0: ...}`, **0 problems**. Both gates PASS.

### RUNG 2 — the claim under test, final

```
cell            s1  s2  s3 | s4  s5  s6  s7  s8  s9 s10 |s11 s12 s13 s14 s15 s16 s17    pooled
F0 Vanilla       8  10   6 |  9  10  10  10  10   9   9 |  8  10   9   9  10   9   9   155/170 = 0.9118
F6 S+X          10  10  10 | 10  10  10  10  10  10  10 | 10  10  10  10  10  10  10   170/170 = 1.0000
```

| estimand | F0 | F6 | gap | Fisher | task-strat perm | task cluster bootstrap |
|---|---|---|---|---|---|---|
| published s1–3 | 24/30 = 0.800 | 30/30 | 20.0 pp | 0.0237 | 0.0308 | 0.0114, CI [+0.033, +0.367] |
| **out-of-sample s4–17** | **131/140 = 0.9357** | 140/140 | **6.4 pp** | **0.0034** | **0.0039** | **0.0125, CI [+0.014, +0.129]** |
| pooled s1–17 | **155/170 = 0.9118** | 170/170 | **8.8 pp** | **< 0.0001** | **< 0.0001** | **0.0006, CI [+0.029, +0.165]** |

Clopper–Pearson 95%: published F0 [0.6143, 0.9229]; out-of-sample F0 **[0.8815, 0.9702]**; pooled F0
**[0.8586, 0.9498]**. F6 pooled [0.9785, 1.0000].

**All three Entry-12 extension criteria are met** (Fisher < 0.05, permutation < 0.05, bootstrap CI
excludes 0), so the *residual* claim survives. **F1 also stands**: the published *rate* is wrong.

### RUNG 1 — significant at n = 17, and it carries two-thirds of the deficit

```
F0 160/170 = 0.9412   F6 170/170 = 1.0000
pooled: Fisher p = 0.0017 | perm p = 0.0018 | bootstrap +5.9pp CI [+0.6, +12.9]  EXCLUDES 0
```

**10 of Vanilla's 15 pooled rung-2 failures are rung-1 failures** — nested XML comments
(`<!--  <!--  -->`), a lexical bug. The metric must be described as *"well-formed and schema-valid"*.
Describing it as "schema validity" attributes to schema knowledge a deficit that is mostly a
comment-nesting bug.

### RUNG 3 — dead at both ladders, with a tight CI around zero

```
STAGED (K1 clean)    F0 133/170 = 0.7824   F6 132/170 = 0.7765   Fisher p = 1.0000
                     bootstrap delta = -0.0059, 95% CI [-0.0529, +0.0294]
UNSTAGED (A1/J3)     F0 121/170 = 0.7118   F6 120/170 = 0.7059   Fisher p = 1.0000
                     bootstrap delta = -0.0059, 95% CI [-0.0529, +0.0294]
F4 X+M (10 seeds)     75/100 = 0.750
```

Vanilla is marginally **ahead** on both ladders. This is no longer "we failed to find an effect" —
the cluster bootstrap CI **[−5.3 pp, +2.9 pp]** is tight enough to *exclude* any execution-validity
advantage larger than about 3 pp. That is a much stronger negative than K1 could state at n = 3.

### Seed-level variance, final — and a correction to my own Entry 11

```
                     overdispersion chi2   df    p        ICC
rung 2, F0  n=10 seeds        18.193        9   0.0330   0.1135   *** I reported this as F4 FIRING ***
rung 2, F0  n=17 seeds        22.082       16   0.1406   0.0422   consistent with binomial
rung 1, F0  n=17 seeds        14.662       16   0.5495   0.0000
rung 3 staged, F0  n=17        4.975       16   0.9959   0.0000
rung 3 staged, F6  n=17        4.067       16   0.9988   0.0000
```

**The overdispersion I reported at n = 10 does not survive to n = 17.** It was driven by seed 3's
6/10, the extreme draw of seventeen. The honest final statement is *not* "seed is a large variance
component"; it is **"n = 3 is far too small to estimate a rate near 0.9, because a single unlucky
seed moves it 11 points"** — a sampling-precision problem, not a hidden seed effect. I am recording
this because it is a place where more data corrected an intermediate conclusion of my own.

---

## Entry 16 — ARTIFACTS, DISCIPLINE, AND WHAT A HUMAN MUST DECIDE

### Artifacts (all under `neurips_review/sprint/artifacts/`)

| path | what |
|---|---|
| `K5_launch.sh` | replication launcher; only deltas vs `launch_autocamp_scaleup.sh` Phase A are `--results-root-dir` and the seed number, plus an explicit `unset` of every `GEOS_HOOK_GEOSX_*` var J3/K4 export |
| `K5_view.sh` | symlink view of COMPLETE seed dirs only — the guard against K4 Entry 9's silent mid-flight scoring |
| `K5_integrity.py` | run-integrity gate; refuses to certify a cell until every (seed, task) exists with `process_status: success` |
| `K5_rungs12.py` | thin wrapper importing **A1's** `A1_rungs12_perfile.py` unmodified (rungs 1 & 2) |
| `K5_ladder.py` | thin wrapper importing **K1's** `K1_rung3.py` unmodified (rung 3), aggregating via `K1_report.load_taskruns` |
| `K5_analyze.py` | the pre-registered analysis; imports `fisher`, `wilson`, `strat_perm` from `K1_stats.py` |
| `K5_power.py` | power simulation + asymptotic cluster limit |
| `K5_finalize.sh` | detached end-to-end pipeline so results land on disk even if the session dies |
| `K5_repro_*` | reproduction check against published seeds (rungs 1/2 CSVs, rung-3 jsonl + meta + bytaskrun) |
| `K5_all_autocamp_{F0,F6}.csv`, `K5_new_autocamp_F4.csv` | rungs 1 & 2, all new seeds |
| `K5_all_autocamp_{F0,F6}_rung3_{staged,unstaged}.jsonl` + `_meta.json` + `_bytaskrun.json` | rung-3 ladders |
| `K5_analyze_n17_out.txt`, `K5_analyze_n17_rungs12_out.txt`, `K5_analyze_out.txt` | full analysis output |
| `K5_power_out.txt`, `K5_vanilla_pertask.json` | power calculation |
| `/data/matt/k5_seed_stability/` | 351 runs + `_logs/` + `_view/` + quarantined `_smoketest/` |

### Discipline verification, run at close

```
git log -1  ->  f13d033 (UNCHANGED; no commits made)
git diff --numstat, src/ and plugin/:
   402  0  plugin/hooks/verify_outputs.py     |  all four are J3's and K4's pre-existing
    49  4  src/runner/agents.py               |  uncommitted edits. K5 added ZERO lines
     7  1  src/runner/claude_settings.py      |  to src/ or plugin/ -- this thread is a
    12  0  src/runner/docker_cmd.py           |  pure replication, it changed no code.
mtime /data/shared/.../autocamp_followup_2026-05-02/icl  ->  2026-05-02  (untouched)
mtime /data/matt/j3_geosx_validate                       ->  09:46Z, before K5 started (untouched)
mtime /data/matt/k4_validator_ablations                  ->  10:38Z, before K5 started (untouched)
files under the published control tree newer than 12:30Z ->  0
files under writing/ newer than 12:30Z                   ->  0
```

No writes to `/data/shared/`, `/data/jixuan/`, `writing/`, any `_`-prefixed directory, or J3's/K4's
result trees. No git commits. Max 8 workers throughout; the four campaigns ran strictly sequentially,
each chained to its predecessor's exit. Every dollar figure from raw tokens × DeepSeek off-peak list
price; `total_cost_usd` never read.

### WHAT A HUMAN MUST DECIDE

1. **Rewrite the rung-2 paragraph — do not delete it.** The current text ("24/30 vs 30/30,
   p = 0.0237") must go: the rate is **0.912**, not 0.800, and the gap is **8.8 pp**, not 20 pp. But
   the replacement is *stronger*, not weaker: **170/170 vs 155/170 across 17 seeds and 340 held-out
   runs, task-clustered bootstrap 95% CI [+2.9 pp, +16.5 pp], permutation p < 0.0001**, plus a second
   adapter cell (`F4`) at **100/100**. My recommendation is to lead with the 17-seed number and say
   explicitly that it supersedes the 3-seed one.

2. **Rename the metric.** Call it *"well-formed and schema-valid"*. **10 of the 15 Vanilla failures
   are XML well-formedness failures** (nested comments), not schema violations. A reviewer who opens
   the decks will see this immediately.

3. **Decide whether to disclose the seed-count issue ourselves.** I recommend yes. The honest
   sentence is: *"our original 3-seed measurement placed Vanilla at 24/30; at 17 seeds the rate is
   155/170, and we report the larger sample."* Volunteering that we re-ran and corrected our own
   number is worth more with an AC asking about execution validity than any single p-value.

4. **Do not revive any rung-3 claim.** At 17 seeds Vanilla is level with or ahead of S+X on both
   ladders (133/170 vs 132/170 staged, p = 1.0000) and the cluster bootstrap CI [−5.3 pp, +2.9 pp]
   now *excludes* any advantage above ~3 pp. This is a firm negative, not an absence of evidence.

5. **Decide how to state the benchmark's power limitation.** The power calculation (Entry 10) says a
   3–6-per-30 mechanism needs **150–500 seeds** for 80% power on the nominal test, and that the
   task-clustered test **can never reach p < 0.05 at any seed count** on this 10-task benchmark
   (limiting p = 0.0660, invariant to effect size). If we make any claim about the validator swap, it
   must carry that caveat; better, we state it as a design limitation ourselves.

6. **Model drift is an open confound and I could not close it** (Entry 9). The published campaign is
   86 days older than mine and `deepseek-v4-flash` carries no version string. It does **not** affect
   the headline, because every comparison I report is between arms run within the same campaign on
   the same day. It does mean the *absolute* May numbers are not reproducible in July, which someone
   should decide whether to disclose.

