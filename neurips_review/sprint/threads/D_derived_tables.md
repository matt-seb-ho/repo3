# Thread D — Derived-number regeneration sweep

**Started** 2026-07-26. Mission: regenerate every derived number in `writing/neurips/neurips_2026.tex` from raw results on disk and diff.

Hard rules honoured: `writing/`, `/data/shared/`, `/data/jixuan/` treated read-only. No writes to `_`-prefixed dirs. No git commits.

---

## Log

### 0. Context read
- `neurips_review/SIGA_rebuttal_execution_plan.md` §0–§4
- `neurips_review/MASTER_TODO.md` P0 #1–#4
- `scripts/analyze_autocamp.py` (461 lines) — `compute_main_effects()` @ L409, `F_FACTORS` @ L395, `aggregate_cell()` @ L197
- `src/eval/judge_geos.py` (933 lines) — `evaluate_geos()` @ L804

### 1. Convention discovery — THE failures-as-zero rule

`src/eval/judge_geos.py:804 evaluate_geos()` returns `score: 0.0` + `status: "execution_error"` for three cases:
- `agent_output["status"] == "execution_error"` (L818–830) — agent produced no outputs / timed out
- `FileNotFoundError` from `evaluate_directories` (L852–864) — `error.type = "missing_xml"` — **no XML outputs on disk**
- `ET.ParseError` / `ValueError` (L865–878) — `error.type = "xml_parse_error"`

So the scorer itself scores an unscorable deck **0.0**. Downstream, each per-seed `_summary.json` records BOTH aggregations explicitly:

```
summary.treesim.scored_mean                  # mean over scored tasks only (failures DROPPED)
summary.treesim.with_failures_as_zero_mean   # mean over total_n, failures = 0
summary.treesim.scored_n / total_n
summary.n_failed / summary.failed_names
```

Evidence (real file, `_results/autocamp_F3_s1/autocamp_F3/_summary.json`):
```
n_total 17, n_scored 16, n_failed 1, failed_names ["TutorialSneddon"]
treesim.scored_mean                = 0.85598125
treesim.with_failures_as_zero_mean = 0.8056294117647059
```
and the corresponding `results[]` entry is `{"experiment":"TutorialSneddon","status":"error","treesim":null}`.

**`scripts/analyze_autocamp.py` does NOT apply failures-as-zero.** `collect_cell()` L74–82:
```python
ts = r.get("treesim")
if isinstance(ts, (int, float)):
    task_scores[task].append(float(ts))
```
A `null` treesim is silently **skipped**, i.e. the failed task is dropped. So `analyze_autocamp.py` implements *scored-only*, contradicting the scorer's own convention.

**Decision: the pipeline's rule is failures-as-zero** (`judge_geos.py:821/856/869` → `score: 0.0`; surfaced as `with_failures_as_zero_mean`). `analyze_autocamp.py` is the outlier. I compute both and report both.

### 2. Val factorial — both conventions, all 11 cells × 3 seeds

Command:
```bash
R=/data/shared/geophysics_agent_data/data/eval/autocamp_2026-05-01
python3 -c "... json.load(f'$R/_results/autocamp_{cell}_s{s}/autocamp_{cell}/_summary.json') ..."
```

| Cell | scored-only mean | σ(sample) | failures-as-0 mean | σ(sample) | n_failed by seed |
|---|---:|---:|---:|---:|---|
| F0 | 0.9096 | 0.0236 | 0.9096 | 0.0236 | 0,0,0 |
| F1 | 0.8848 | 0.0136 | 0.8848 | 0.0136 | 0,0,0 |
| F2 | 0.9191 | 0.0037 | 0.9191 | 0.0037 | 0,0,0 |
| **F3** | **0.8735** | 0.0169 | **0.8567** | **0.0449** | **1,0,0** (s1 TutorialSneddon) |
| F4 | 0.9214 | 0.0071 | 0.9214 | 0.0071 | 0,0,0 |
| F5 | 0.8928 | 0.0329 | 0.8928 | 0.0329 | 0,0,0 |
| F6 | 0.9166 | 0.0038 | 0.9166 | 0.0038 | 0,0,0 |
| F7 | 0.8853 | 0.0083 | 0.8853 | 0.0083 | 0,0,0 |
| **F8** | 0.9110 | 0.0180 | 0.9110 | 0.0180 | 0,0,0 |
| **F11** | **0.9146** | 0.0162 | **0.8965** | **0.0316** | **0,1,0** (s2 pknViscosityDominated) |
| SE | 0.9191 | 0.0201 | 0.9191 | 0.0201 | 0,0,0 |

**→ F3 RESOLVED.** 0.857 = failures-as-zero (`0.8567`), and its σ = **0.0449 → 0.045**, exactly Table 1's σ. 0.874 = scored-only (`0.8735`), and the metrics doc's σ 0.018 is what `analyze_autocamp.py`'s index-grouping produces (see §3). Table 1's F3 mean AND σ are both internally consistent under failures-as-zero. **0.857 is the correct value.** The appendix main-effects table was generated from `analyze_autocamp.py`, which drops failures.

**→ NEW: F11 (S+X+M) has the same problem.** Its two conventions differ by 0.018. Must check which value the paper prints.

Per-seed F3 detail (treesim):
- s1: scored_mean 0.85598125 (16/17), failures-as-0 0.8056294117647059, failed = TutorialSneddon
- s2: 0.8747705882352941 (17/17)
- s3: 0.8897588235294117 (17/17)


### 3. Why `analyze_autocamp.py` gives F3 = 0.874 AND σ = 0.018 — the index-grouping bug

`scripts/analyze_autocamp.py:203-212` builds per-seed means by grouping the per-task
score lists **by list index**, not by seed id:

```python
all_lists = list(task_scores.values())
n_seeds = max((len(v) for v in all_lists), default=0)
for s in range(n_seeds):
    seed_vals = [v[s] for v in all_lists if len(v) > s]
```

For F3, `task_scores["TutorialSneddon"]` has only 2 entries (`[s2, s3]`) because s1 failed
and was skipped at L74-82. So index 0 (nominally "seed 1") pulls s2's TutorialSneddon value.
The seed means are therefore *mixtures*. Reproduced exactly by running the module's own
functions:

```bash
python3 -c "... importlib load scripts/analyze_autocamp.py; collect_cell/aggregate_cell/compute_main_effects ..."
#   autocamp_F3: n_seeds=3 q=0.8742 σ=0.0184
#   MAIN EFFECTS: R -0.0324  S -0.0034  X +0.0071  M +0.0043
```

`{eff:+.3f}` (L309) → `-0.032 / -0.003 / +0.007 / +0.004` = **the appendix table verbatim**,
and σ `0.018` = **the metrics doc verbatim**. Both "stale" numbers are fully explained.

**THREE distinct R values, all from the same raw data:**

| Convention | F3 mean | R (full prec.) | R @3dp | Where it appears |
|---|---:|---:|---:|---|
| index-grouped scored-only (`analyze_autocamp.py`) | 0.8742 | −0.032431 | **−0.032** | §5.1 prose, App tab:main-effects, `docs/2026-05-02_autocamp_metrics.md` |
| clean scored-only (mean of true seed means) | 0.8735 | −0.032569 | **−0.033** | Limitations ¶, App future-work ¶ |
| **failures-as-zero (paper's declared convention, tex:169)** | **0.8567** | **−0.036765** | **−0.037** | **nowhere in the paper** |

So the §5-vs-Limitations "−0.032 vs −0.033" inconsistency is NOT two snapshots of one number —
it is two different aggregation conventions, both scored-only, differing by the index bug.

### 4. Table 1 val column — 11/11 exact under failures-as-zero + sample std (ddof=1)

Sample std, not population std. `analyze_autocamp.py:215` uses `statistics.pstdev`;
Table 1 needs `statistics.stdev`. Verified on every cell (F3 0.0449→0.045, F5 0.0329→0.033, …).

Cell→label mapping confirmed: **F8 = S+X+M, F11 = SE-prose**. Established by matching
Table 1 rows: F8 gives 0.911±0.018 (S+X+M row) and F11 gives 0.8965±0.0316 = 0.897±0.032
(SE-prose row) *only under failures-as-zero* — F11's scored-only value is 0.9146±0.0162,
which matches nothing in the paper. **F11's failure (s2, `pknViscosityDominated`) is the
second cell where the convention matters, and Table 1 got it right there too.**

### 5. Table 1 held-out column — 6/6 exact under failures-as-zero + ddof=1

| Cell | paper | recomputed |
|---|---|---|
| Vanilla F0 | 0.720 ± 0.081 | 0.71964 ± 0.08092 |
| X+M F4 | 0.768 ± 0.005 | 0.76829 ± 0.00537 |
| S+X F6 | 0.781 ± 0.002 | 0.78142 ± 0.00182 |
| S+X+M F8 | 0.783 ± 0.022 | 0.78269 ± 0.02150 |
| SE-prose F11 | 0.775 ± 0.024 | 0.77487 ± 0.02423 |
| SE | 0.789 ± 0.012 | 0.78910 ± 0.01233 |

Vanilla→SE = 0.78910 − 0.71964 = **+0.06946 → +0.069** ✓.
The σ=0.081 mechanism claim (§5.1) is confirmed verbatim from the error string in
`_results_icl/F0_icl_s3/autocamp_F0/_summary.json`:
`ValueError: Failed to parse XMLs in .../ExampleProppantTest/inputs: ProppantSlotTest_base.xml: not well-formed (invalid token): line 4, column 21; ProppantSlotTest_benchmark.xml: ...`
Note the failed task has **no `*_eval.json` file at all** — per-task eval files exist only for
scored tasks (9 files in F0_icl_s3, 10 elsewhere). Any per-task analysis that globs `*_eval.json`
silently drops failures. Must read `_summary.json`'s `results[]` instead.

### 6. σ ratios vs Vanilla on held-out (per cell, never mixed)

| Cell | σ (ddof=1) | σ ratio vs Vanilla | σ² ratio |
|---|---:|---:|---:|
| Vanilla | 0.080920 | 1.00× | 1× |
| X+M | 0.005366 | 15.08× | 227× |
| S+X | 0.001817 | **44.54×** | 1984× |
| S+X+M | 0.021498 | 3.76× | 14× |
| SE-prose | 0.024231 | 3.34× | 11× |
| **SE** | 0.012332 | **6.56×** | 43× |

Ratios are identical under pstdev (the ddof cancels). The "≈40×" is **S+X's** 44.5×.
SE's own ratio is **6.56×** (the brief's "≈6.75×" is close but not what the data gives).

### 7. Efficiency table (App tab:efficiency) — recomputed from `tool_calls.json` + `status.json`

Rule: tools/task = Σ`per_tool_counts` / n_task_runs; wall = Σ`status.elapsed_seconds` / n.
n = 51 (val) and 30 (held-out) for every cell — no missing run dirs.

| Cell | paper tools val | recomp | paper wall val | recomp | paper tools HO | recomp | paper wall HO | recomp |
|---|---|---|---|---|---|---|---|---|
| Vanilla | 81.5 | 81.55 ✓ | 359 | 358.67 ✓ | 90.5 | 90.50 ✓ | 417 | 416.55 ✓ |
| X+M | 79.6 | 79.61 ✓ | 337 | 336.98 ✓ | 75.0 | 75.00 ✓ | 340 | 339.49 ✓ |
| S+X | 83.3 | 83.29 ✓ | 348 | 347.61 ✓ | 74.7 | 74.70 ✓ | 345 | 344.61 ✓ |
| S+X+M | 71.0 | 70.98 ✓ | 326 | 325.60 ✓ | 82.9 | 82.90 ✓ | 358 | 358.11 ✓ |
| SE-prose | 62.7 | 62.75 ✓ | 326 | 326.31 ✓ | 70.9 | 70.90 ✓ | 362 | 361.66 ✓ |
| SE | 68.9 | 68.88 ✓ | 321 | 320.66 ✓ | 97.4 | 97.43 ✓ | 390 | 389.82 ✓ |

24/24 exact. But the §5.2 **prose** derived from it does not hold — see §9 below.

### 8. Factor-implementation fidelity check (positive result, rebuttal-usable)

`tool_calls.json.mcp_server_statuses` per (cell, seed, task), all 51/30 runs identical within cell:

| Cell | declared (R,S,X,M) | MCP servers registered | xmllint calls/task |
|---|---|---|---:|
| F0 Vanilla | 0,0,0,0 | *(none)* | 0.00 |
| F1 R+M | 1,0,0,1 | geos-rag | 0.00 |
| F2 S+M | 0,1,0,1 | *(none)* | 0.00 |
| F3 R+S | 1,1,0,0 | geos-rag | 0.00 |
| F4 X+M | 0,0,1,1 | xmllint | 2.84 |
| F5 R+X | 1,0,1,0 | geos-rag, xmllint | 2.84 |
| F6 S+X | 0,1,1,0 | xmllint | 2.75 |
| F7 R+S+X+M | 1,1,1,1 | geos-rag, xmllint | 2.75 |
| F8 S+X+M | 0,1,1,1 | xmllint | 2.69 |
| F11 SE-prose | 0,1,1,1 | xmllint | 2.75 |
| SE | 0,1,1,1 | xmllint | 2.71 |

**R and X are correctly gated at the MCP layer in all 11 cells, all 3 seeds, all tasks.**
This directly rebuts an implementation-fidelity objection. Also confirms §4's "~3 xmllint calls
per task" (2.69–2.84).

### 9. Native-plugin-prefix footprint, measured

`per_tool_counts` records `mcp__geos-rag__search_*` in cells where geos-rag is **not** registered.
Traced in `dsv4/autocamp_F4/autocamp_F4_s1/ExampleMandel/events.jsonl`:

```
CALL mcp__geos-rag__search_technical {"query": "Mandel poroelastic consolidation benchmark XML example"}
  RESULT {"type":"tool_result","content":"<tool_use_error>Error: No such tool available: mcp__geos-rag__search_technical</tool_use_error>","is_error":true}
```
(and the same for `search_schema`, `search_navigator`).

Per-cell footprint (attempts/task; task-runs affected):

| Split | Vanilla | S+M | X+M | S+X | S+X+M | SE-prose | SE |
|---|---|---|---|---|---|---|---|
| val (n=51) | 0.00 (0) | 0.45 (8) | 2.25 (39) | 1.96 (34) | 2.61 (46) | 2.02 (38) | **0.00 (0)** |
| held-out (n=30) | 0.00 (0) | — | 2.73 (28) | 1.90 (19) | 2.73 (29) | 2.10 (23) | **0.00 (0)** |

Three consequences:
1. **The calls all errored** — no retrieval leaked into R− cells. R was genuinely off. Fairness intact.
2. **Vanilla emitted zero and SE emitted zero.** The headline **Vanilla→SE +0.069 contrast is
   entirely prefix-free on both sides.** The prefix-handicapped cells are X+M / S+X / S+X+M /
   SE-prose, whose Δ vs Vanilla are therefore *understated*. This is stronger than the
   chronological argument in the execution plan §2 and it is measured, not inferred.
3. `pseudo_tool_calls == 0` in every DSv4 run (val and held-out) — the pseudo-tool-call pathology
   is minimax-specific, as the paper says.
4. ⚠ `rag_requirement_met: true` and `rag_mcp_unavailable: false` are set on 8–46 val runs and
   19–29 held-out runs where geos-rag was **not connected**. These diagnostic flags are unreliable;
   nobody should quote them.

### 10. "free-form Read calls" mechanism check

Reads bucketed by target path from `events.jsonl` (same extraction as `analyze_autocamp.py:160-176`):

| Cell | Reads/task into `/geos_lib` | into `/workspace` |
|---|---:|---:|
| Vanilla | 39.86 | 2.37 |
| R+M | 8.61 | 2.10 |
| S+M | 32.06 | 2.75 |
| R+S | 9.39 | 2.29 |
| X+M | 34.39 | 0.25 |
| R+X | 10.24 | 0.08 |
| S+X | 36.80 | 0.24 |
| R+S+X+M | 9.02 | 0.06 |
| S+X+M | 30.41 | 0.12 |
| SE-prose | 24.71 | 0.39 |
| SE | 30.61 | 0.18 |

Factorial main effects on `/geos_lib` reads/task: **R = −26.5 (−74%)**, **M = −3.05 (−12.7%)**.
Restricting to R− cells: M-on {32.1, 34.4, 30.4} vs M-off {39.9, 36.8} → ≈ −13%.
**The Read-call collapse is caused by R (retrieval), not M (cheatsheet).**

### 11. Bottleneck counts (Table 5) vs the on-disk classifier artifacts

Source artifacts (LLM classifier output, cannot be re-run cheaply — this is a doc-vs-paper diff,
not a raw recompute): `docs/XN-020_bottleneck-analysis-combined.md` (val, F0/F2/F4/F6/F8/F11/SE),
`docs/XN-021_bottleneck-analysis-icl10.md` (held-out, F0/F4/F6/F8/F11/SE).
The artifacts' own cell headers confirm the pipeline used **scored-only** (F11 val n=50,
F0 held-out n=29) — i.e. the zero-score catastrophic failures that drive the reliability
claim have **no row anywhere in Table 5**.

val panel diffs (paper ⇒ artifact):
- S+X `missing_block` **2 ⇒ 3**
- S+X `hallucinated_extras` **"−" ⇒ 4**
- SE `hallucinated_extras` **"−" ⇒ 3**
- SE `missing_block` **"−" ⇒ 3**
- SE `structural_mismatch` **"−" ⇒ 6**

held-out panel diffs:
- Vanilla `hallucinated_extras` **0 ⇒ 1**
- X+M `hallucinated_extras` **0 ⇒ 1**; X+M `partial_implementation` **0 ⇒ 2**
- S+X `hallucinated_extras` **0 ⇒ 3**
- S+X+M `hallucinated_extras` **0 ⇒ 1**
- **SE-prose `bad_attribute_value` 0 ⇒ 3**
- **SE `bad_attribute_value` 0 ⇒ 4**

Also: the classifier emitted **off-schema labels** despite App:bottleneck stage 2 declaring a
strict 8-category JSON schema — `wrong_solver_type`, `wrong_attribute_value`, `unknown` (7/51 in
val SE), `structure_mismatch`, `None`, `none`, `""`. And Table 5's caption attributes the n<30
shortfall to "LLM-judge parse-failures", when for held-out Vanilla it is the *deck* parse failure
(ExampleProppantTest s3) — the same failure the reliability claim rests on.

### 12. Strictly-perfect deck counts (§5.2 item 4)

Threshold sensitivity on val, failures-as-zero (no failures in these cells so convention is moot):

| threshold | Vanilla | X+M | SE | S+X | S+X+M |
|---|---|---|---|---|---|
| ≥ 0.999 (paper's stated threshold) | 7/51 | 6/51 | **7/51** | 6/51 | 7/51 |
| = 1.000 | 6/51 | 5/51 | 5/51 | 4/51 | 4/51 |

Paper prints "Vanilla 7/51, X+M 6/51, SE 6/51". SE = **7/51** at ≥0.999, 5/51 at =1.0.
No threshold reproduces (7, 6, 6). The *conclusion* ("does not increase under any adapter")
survives either way.

### 13. Bootstrap — design and results

Resampling units and n_boot stated explicitly:
- **n_boot = 20 000**, RNG `random.Random(31642)` (submission id), percentile method.
- **Primary (as specified in the brief): (task, seed) units, i.i.d.** — 30 units per held-out cell.
- **Robustness: task-clustered** — resample the 10 tasks with replacement, keep all 3 seeds of the
  drawn task. This is the more defensible frame: seeds within a task are strongly correlated
  (per-task σ across seeds is tiny for adapter cells), so the i.i.d. unit bootstrap treats 30
  correlated observations as 30 independent ones and **understates** the interval.
- Contrasts are **paired**: the same resampled tasks (or task-seed keys) are used for both cells,
  since all cells ran the identical task list and seed indices.

See §D of the final report for the tables. Headline: the Vanilla→SE +0.069 gain's 95% CI
**includes zero** under the task-clustered bootstrap ([−0.0085, +0.1663], P(Δ≤0)=0.0515) and only
just excludes it under the i.i.d. unit bootstrap ([+0.0008, +0.1550], P(Δ≤0)=0.0228).

### 14. Completeness

- **val:** 11 cells × 3 seeds = 33 runs, all present. 17 tasks in every run → **561 task-runs, 0 missing**.
  2 unscorable, both scored 0 under the pipeline rule: F3/s1 `TutorialSneddon`, F11/s2 `pknViscosityDominated`.
- **held-out:** 6 cells × 3 seeds = 18 runs, all present. 10 tasks in every run → **180 task-runs, 0 missing**.
  1 unscorable, scored 0: F0/s3 `ExampleProppantTest`.
- Deck inventory: all 180 held-out `<task>/inputs/` directories exist and every one contains ≥1 `.xml`
  (so the F0/s3 failure is a *malformed* deck, not an absent one — consistent with the
  `not well-formed (invalid token)` error, and consistent with §5.1's "unparseable" wording).
- Cross-check: for all 51 (cell, seed) summaries, the `_summary.json` aggregates equal my independent
  re-derivation from `results[]` to <1e-9. **0 mismatches.**
- Nothing was normalised away. Every missing score is an explicit zero.

### 15. Not recomputed by Thread D — sources located for a follow-up pass

| Claim block | Source located | Status |
|---|---|---|
| Cross-model panel (minimax 0.821/0.867/0.861; gemini 0.768/0.797/0.757) | `/data/shared/.../cross_model_2026-05-03/{minimax,gemini,minimax_minimax-m2.7,google_gemini-3-flash-preview}/` — **no `_summary.json` found anywhere under it**; values match `docs/2026-05-04_cross-cutting-paper-section.md:30-35` | ⚠ eval summaries not on disk at that path |
| OpenHands row (0.856±0.061, 0.881±0.023) | `docs/XN-019_openhands-dsv4-flash.md` | not recomputed |
| Harness-less floor 0.333 | `scripts/harnessless_eval.py` | not recomputed |
| OpenFOAM tables (2 tables, 60+ cells) | `~/sci/repo3_openfoam` | not recomputed |
| Autonomy study (64 runs, 3.1%, drop volumes, 15/26 findability) | `scripts/relax_specs.py`, App autonomy | not recomputed |
| Human baseline (0.812/0.781/0.689/0.931, browser counts) | `data/human_baseline/`, `scripts/score_human_baseline.py` | not recomputed |
| Bottleneck counts | docs XN-020 / XN-021 (diffed, see §11) | LLM output, not re-runnable |

⚠ The cross-model panel is the one gap that matters for a "traces to a file on disk" audit: I could
not find `_summary.json` under `cross_model_2026-05-03/`. Someone should locate the scored output
before any cross-model number is quoted.

---

## 16. MASTER DIFF TABLE — claim · submitted · recomputed · match? · Δ

Sorted by |Δ| descending within tiers. "Correct" = the paper's own declared convention
(failures-as-zero, tex:169) applied to the raw `_summary.json` files.

### Tier 1 — WRONG NUMBER (a reviewer recomputing gets something else)

| # | Claim | Where | Submitted | Recomputed | Match | Δ |
|---|---|---|---|---|:-:|---|
| 1 | held-out `bad_attribute_value`, SE | Tab.5 | **0** | **4** | ✗ | 4 counts |
| 2 | held-out `bad_attribute_value`, SE-prose | Tab.5 | **0** | **3** | ✗ | 3 counts |
| 3 | held-out `hallucinated_extras`, S+X | Tab.5 | 0 | 3 | ✗ | 3 |
| 4 | held-out `partial_implementation`, X+M | Tab.5 | 0 | 2 | ✗ | 2 |
| 5 | val `missing_block`, S+X | Tab.5 | 2 | 3 | ✗ | 1 |
| 6 | held-out `hallucinated_extras`, Vanilla / X+M / S+X+M | Tab.5 | 0 / 0 / 0 | 1 / 1 / 1 | ✗ | 1 each |
| 7 | strictly-perfect decks, SE val | §5.2(4) | 6/51 | 7/51 @≥0.999 | ✗ | 1 |
| 8 | main effect **R** | §5.1 + Tab.6 | −0.032 | **−0.0368** | ✗ | 0.0048 |
| 9 | main effect **S** | Tab.6 | −0.003 | **−0.0077** | ✗ | 0.0047 |
| 10 | main effect **M** | Tab.6 | +0.004 | **+0.0087** | ✗ | 0.0047 |
| 11 | main effect **X** | Tab.6 | +0.007 | **+0.0115** | ✗ | 0.0045 |
| 12 | main effect **R** | Limitations, future-work | −0.033 | **−0.0368** | ✗ | 0.0038 |
| 13 | "SE … runs about 16% faster" (val wall) | §5.2 | −16% | **−10.6%** (320.7 vs 358.7 s) | ✗ | 5.4 pp |
| 14 | val range, non-RAG cells | §5.1 | 0.910–0.921 | **0.897–0.921** (SE-prose is R−) | ✗ | 0.013 |

### Tier 2 — MIS-ATTRIBUTED MECHANISM / MISLEADING PAIRING (arithmetic fine, inference not)

| # | Claim | Where | Submitted | Recomputed | Match | Δ |
|---|---|---|---|---|:-:|---|
| 15 | "+7 pp" paired with "≈40× variance reduction" | Abstract, §1, Conclusion | one system | +0.069 is **SE** (σ ratio **6.56×**); 44.5× is **S+X** (Δ +0.061) | ✗ | 40× vs 6.6× |
| 16 | "X, M and S all fall within ±0.007" | §5.1 | ±0.007 | S −0.0077, X +0.0115, M +0.0087 — **all three outside** | ✗ | up to 0.0045 |
| 17 | "Cheatsheet cells make about half as many free-form Read calls" | §5.2 | ≈½, cause = M | M effect **−12.7%**; R effect **−74%** | ✗ | mechanism |
| 18 | SE "matches the best hand-designed cell with ~16% fewer tool calls" | Abstract | −16% | vs Vanilla −15.5%; vs X+M −13.5%; vs S+X+M −3.0%; **held-out +17.5% MORE** | ✗ | comparator |
| 19 | "S is essentially zero" | App main-effects | ≈0 | −0.0077, same order as X (+0.0115) | ✗ | — |
| 20 | Tab.5 caption: n<30 from "LLM-judge parse-failures" | Tab.5 caption | LLM-judge | **deck** parse failure (F0/s3 ExampleProppantTest) | ✗ | — |
| 21 | classifier returns one of 8 categories, strict JSON | App bottleneck st.2 | 8 cats | artifacts contain `wrong_solver_type`, `wrong_attribute_value`, `unknown` (7/51 SE val), `structure_mismatch`, `None`, `none`, `""` | ✗ | — |
| 22 | "RAG cells make 12 to 13 retrieval calls" | §5.2 | 12–13 | **12.10–13.53** (R+M = 13.53) | ~ | 0.53 |

### Tier 3 — EXACT MATCH (verified, quotable)

| Claim | Where | Submitted | Recomputed | Match |
|---|---|---|---|:-:|
| Table 1 val, all 11 cells (mean ± σ) | Tab.1 | see §4 | 11/11 identical | ✓ |
| Table 1 held-out, all 6 cells (mean ± σ) | Tab.1 | see §5 | 6/6 identical | ✓ |
| Table 1 Δ columns, val (10) + held-out (5) | Tab.1 | — | 15/15 identical | ✓ |
| Vanilla→SE held-out gain | §5.1, §5.1(per-task) | +0.069 | +0.06946 | ✓ |
| Vanilla held-out σ = 0.081, mechanism = unparseable XML on ExampleProppantTest, one seed | §5.1 | 0.081 | 0.08092, error string matches verbatim | ✓ |
| X+M σ = 0.005, S+X σ = 0.002 | §5.1 | 0.005 / 0.002 | 0.005366 / 0.001817 | ✓ |
| val range all cells 0.857–0.921 | §5.1 | 0.857–0.921 | 0.8567–0.9214 | ✓ |
| held-out range 0.720–0.789 | §5.1 | 0.720–0.789 | 0.7196–0.7891 | ✓ |
| per-task held-out table, **all 60 cells** | Tab.4 | — | 60/60 identical to 3 dp | ✓ |
| ThermoPoroElasticWellbore 0.355→0.761 | §5.1 | 0.355 / 0.761 | 0.3551 / 0.7614 | ✓ |
| ExampleProppantTest 0.541→0.825 | §5.1 | 0.541 / 0.825 | 0.5406 / 0.8248 | ✓ |
| TutorialHydraulicFracture 0.013 across every cell | §5.1 | 0.013 | 0.0119 all 6 cells | ✓ |
| remaining-seven Vanilla mean 0.898 | §5.1 | 0.898 | 0.8982 | ✓ |
| efficiency table, 24 cells | Tab.9 | — | 24/24 identical | ✓ |
| "~3 xmllint calls per task" in X cells | §4, §5.2 | ≈3 | 2.69–2.84 | ✓ |
| RAG cells run faster | §5.2 | — | 257–279 s vs 321–359 s | ✓ |
| val `missing_block` 6→3, Vanilla→X+M | §5.2(1) | 6→3 | 6→3 | ✓ |
| val `extra_block` 9→11, `hallucinated_extras` 4→7 | §5.2(3) | 9→11, 4→7 | 9→11, 4→7 | ✓ |
| val `bad_attribute_value` 12/11/15 (Van/X+M/S+X) | §5.2(2) | 12/11/15 | 12/11/15 | ✓ |
| perfect decks Vanilla 7/51, X+M 6/51 | §5.2(4) | 7 / 6 | 7 / 6 @≥0.999 | ✓ |
| §5/Limitations internal inconsistency −0.032 vs −0.033 | — | both present | **both confirmed present** (tex:207/412 vs tex:272/547) | ✓ |
| val cell factor settings (R, X gating) | Tab.2 | — | MCP registration matches declared levels in 11/11 cells × 3 seeds × all tasks | ✓ |
| n=3 seeds, 17 val / 10 held-out tasks | §4 | — | 561 + 180 task-runs, 0 missing | ✓ |

---

## 17. Rebuttal-ready block A — per-cell σ on held-out (10 tasks, n=3 seeds, failures-as-zero)

Every mean is paired with the σ from the **same** cell.

| Cell | mean TreeSim | σ across seeds | σ ratio vs Vanilla | Δ mean vs Vanilla | zero-score runs / 30 |
|---|---:|---:|---:|---:|---:|
| Vanilla | 0.7196 | 0.0809 | 1.00× | — | 1 |
| X+M | 0.7683 | 0.0054 | 15.1× | +0.049 | 0 |
| S+X | 0.7814 | 0.0018 | **44.5×** | +0.062 | 0 |
| S+X+M | 0.7827 | 0.0215 | 3.8× | +0.063 | 0 |
| SE-prose | 0.7749 | 0.0242 | 3.3× | +0.055 | 0 |
| SE | 0.7891 | 0.0123 | 6.6× | **+0.069** | 0 |

Per-seed means, so the σ can be checked by hand:
- Vanilla: 0.74061, 0.78800, 0.63029 (seed 3 = the ExampleProppantTest zero)
- X+M: 0.76244, 0.77298, 0.76946
- S+X: 0.77992, 0.78090, 0.78344
- S+X+M: 0.80223, 0.78617, 0.75966
- SE-prose: 0.74723, 0.79244, 0.78495
- SE: 0.79723, 0.79516, 0.77491

## 18. Rebuttal-ready block B — bootstrap 95% CIs

**Method.** Percentile bootstrap, n_boot = 20 000, `random.Random(31642)`.
Two resampling frames reported because they answer different questions and the honest one is
the wider:
- **(task, seed) units, i.i.d.** — 30 units per cell. Treats each of the 30 task×seed observations
  as exchangeable. Understates uncertainty (seeds within a task are highly correlated).
- **task-clustered** — resample the 10 tasks with replacement, keeping all 3 seeds of each drawn
  task. Correct frame if the task set is the sampling frame of interest. **This is the one to quote.**
Contrasts are **paired**: the same resampled tasks are used for both cells (all cells ran the
identical task list and seed indices).

Per-cell mean, 95% CI:

| Cell | point | (task,seed) 95% CI | task-clustered 95% CI |
|---|---:|---|---|
| Vanilla | 0.7196 | [0.5906, 0.8346] | [0.5156, 0.8879] |
| X+M | 0.7683 | [0.6653, 0.8549] | [0.5809, 0.8934] |
| S+X | 0.7814 | [0.6768, 0.8692] | [0.5911, 0.9083] |
| S+X+M | 0.7827 | [0.6756, 0.8683] | [0.5939, 0.9077] |
| SE-prose | 0.7749 | [0.6666, 0.8631] | [0.5920, 0.8946] |
| SE | 0.7891 | [0.6822, 0.8777] | [0.6013, 0.9147] |

Paired contrasts vs Vanilla:

| Contrast | Δ | (task,seed) 95% CI | P(Δ≤0) | task-clustered 95% CI | P(Δ≤0) |
|---|---:|---|---:|---|---:|
| Vanilla → X+M | +0.0487 | [−0.0152, +0.1321] | 0.083 | [−0.0173, +0.1362] | 0.113 |
| Vanilla → S+X | +0.0618 | [−0.0012, +0.1423] | 0.028 | [−0.0045, +0.1456] | 0.044 |
| Vanilla → S+X+M | +0.0631 | [−0.0013, +0.1439] | 0.028 | [−0.0059, +0.1479] | 0.048 |
| Vanilla → SE-prose | +0.0552 | [−0.0155, +0.1402] | 0.074 | [−0.0240, +0.1530] | 0.108 |
| **Vanilla → SE** | **+0.0695** | **[+0.0008, +0.1550]** | **0.023** | **[−0.0085, +0.1663]** | **0.052** |

**Reading.** The mean-lift claims are *directionally* consistent but individually fragile at
n=10 tasks — every CI is wide, and the headline +0.069 straddles zero under task clustering.
The **reliability** claim does not depend on any of this: it is a σ ratio and a
zero-score count (Vanilla 1/30 vs 0/30 in all five SIGA cells), not a mean contrast.
This is the quantitative case for leading with reliability, exactly as execution-plan §4.1 argues.

Supporting per-task paired view (SE − Vanilla, 10 tasks): SE higher on 7, tied on 1
(the universal 0.013 failure), lower on 2. **Mean Δ +0.0695 but median Δ only +0.0221** —
two rescues carry the mean, which is what the paper already says.

| Task | Vanilla | SE | Δ |
|---|---:|---:|---:|
| AdvancedExampleThermoPoroElasticWellbore | 0.355 | 0.761 | +0.406 |
| ExampleProppantTest | 0.541 | 0.825 | +0.284 |
| AdvancedExampleCasedThermoElasticWellbore | 0.847 | 0.886 | +0.039 |
| ExamplesingleFracCompression | 0.891 | 0.928 | +0.037 |
| ExampleVerticalPoroElastoPlasticWellbore | 0.909 | 0.944 | +0.035 |
| AdvancedExampleViscoExtendedDruckerPrager | 0.986 | 0.996 | +0.010 |
| ExampleMCCWellbore | 0.935 | 0.941 | +0.005 |
| TutorialHydraulicFractureWithAdvancedXML | 0.013 | 0.013 | 0.000 |
| ExampleIsothermalHystInjection | 0.755 | 0.717 | −0.039 |
| AdvancedExamplePureThermalDiffusionWellbore | 0.963 | 0.880 | −0.083 |

## 19. Stale derived numbers, ranked by damage if a reviewer finds it first

1. **Tab.5 held-out `bad_attribute_value` = 0 for SE-prose and SE** (artifacts: 3 and 4).
   Read literally the table says SIGA's two self-evolved cells **eliminate** the failure mode
   the abstract, §5.2(2), §6(iii) and the Conclusion all say is **untouched**. Either the table
   or the paper's central "harm-reduction not correctness" thesis is wrong. Highest damage:
   it is an internal contradiction in the paper's headline mechanism claim, and it is in a table.
2. **App main-effects table (all four values) is computed under a convention the paper explicitly
   disclaims.** tex:169 declares failures-as-zero; the table is scored-only *plus* an index-grouping
   bug. The four correct values are −0.037 / −0.008 / +0.011 / +0.009. Any reviewer can derive
   these from Table 1's own eight cells in two minutes.
3. **"X, M and S all fall within ±0.007" (§5.1) is false under the corrected numbers.** This is the
   sentence that licenses "don't add RAG; the rest doesn't matter." Under −0.008 / +0.011 / +0.009
   the S and X effects are comparable in magnitude and opposite in sign — a different conclusion.
4. **Abstract pairs "+7 pp" (SE, σ ratio 6.6×) with "≈40×" (S+X, Δ +0.061).** No single cell
   delivers both. A reviewer who asks "which cell?" gets no answer that satisfies both halves.
5. **Five more Tab.5 cells wrong or blank** (val S+X missing_block 2 vs 3; val S+X and SE
   `hallucinated_extras`/`missing_block`/`structural_mismatch` printed as "−" when the artifacts
   have 4 / 3 / 3 / 6; held-out `hallucinated_extras` 0 vs 1 in three cells; held-out X+M
   `partial_implementation` 0 vs 2).
6. **§5.2 "SE runs about 16% faster"** — the 16% is the tool-call reduction; wall-clock is 10.6%.
   And SE uses **17.5% MORE** tool calls than S+X+M on held-out, so the efficiency claim is val-only.
7. **§5.2 attributes the free-form-Read collapse to the cheatsheet.** The data attributes it to
   retrieval (R −74%, M −13%). The paper's own §5.2 says RAG cells score *lower*, so the
   efficiency story and the quality story point at different factors.
8. **SE perfect-deck count 6/51 should be 7/51** at the paper's stated ≥0.999 threshold.
9. **"non-RAG cells 0.910 to 0.921"** — SE-prose (R−) is 0.897.
10. **Tab.5 caption mis-attributes the n<30 shortfall** to LLM-judge parse failures; it is the deck
    parse failure that the reliability claim is built on. Also: the bottleneck panel is scored-only,
    so the catastrophic failures have no row in it at all.
11. **App bottleneck stage 2 claims a strict 8-category JSON schema**; the artifacts contain seven
    off-schema labels, including `unknown` on 7/51 val SE runs.
12. **`docs/2026-05-04_cross-cutting-paper-section.md:57`** explains SE's gemini regression with
    "SE's plugin includes both geos-rag and xmllint MCP servers". On DSv4 SE registers **only**
    xmllint (51/51 val, 30/30 held-out) and makes **zero** geos-rag calls. Internal doc is wrong —
    same class of hazard as the "+0.24" mis-citation. Do not let it into a rebuttal.

## 20. Artifacts

- `neurips_review/sprint/artifacts/D_recompute.py` — the script; re-derives everything above.
- `neurips_review/sprint/artifacts/D_recomputed.json` — machine-readable dump (all cells,
  all seeds, per-task scores under both conventions, main effects under 5 aggregation variants,
  bootstrap, completeness, per-tool counts, read audit, prefix footprint, deck inventory).
- This log.

Run: `python3 neurips_review/sprint/artifacts/D_recompute.py` (~10 min; the events.jsonl read
audit dominates).

---

## 21. Corrections to my own earlier entries in this log

Applying rule 6 (suspect my own convention first). Three fixes:

**(a) §16 Tier 3 "Table 1 Δ columns … 15/15 identical" — needs a qualifier.**
Table 1's Δ columns are computed as **(rounded mean − rounded mean)**, not from full precision.
Under that convention **15/15 are exact**. Under full precision, 5 of 15 differ by 0.001:

| Δ cell | printed | full-precision | round(full) |
|---|---:|---:|---:|
| val X+M | +0.011 | +0.011776 | +0.012 |
| val R+S+X+M | −0.025 | −0.024329 | −0.024 |
| val SE | +0.009 | +0.009537 | +0.010 |
| held-out X+M | +0.048 | +0.048660 | +0.049 |
| held-out S+X | +0.061 | +0.061787 | +0.062 |

This is **not** a stale number and it is arguably the better choice: a reviewer who subtracts the
printed mean columns reproduces the printed Δ exactly. But it means "recompute the deltas from
raw data" gives 0.001 differences in five cells, and we should say which convention we used if
asked. Same applies to §5.1's "X+M beats Vanilla by +0.011" (full precision +0.0118).
The headline **+0.069 is robust to the choice** (+0.069467 → +0.069 both ways).

**(b) §16 Tier 3 "TutorialHydraulicFracture 0.013 … 0.0119 all 6 cells" — the 0.0119 was wrong.**
That figure was `scored_min` from an unrelated summary. The actual per-task means are
F0 0.01277, X+M 0.01300, S+X 0.01300, S+X+M 0.01310, SE-prose 0.01277, SE 0.01310 — all round to
**0.013**, so the paper's table cell is correct in all six columns. Claim verified ✓; my number was not.

**(c) §16 Tier 3 per-task values — my 4-dp figures were off in the last digit.**
Correct: `AdvancedExampleThermoPoroElasticWellbore` Vanilla **0.35500** → SE **0.76100**;
`ExampleProppantTest` Vanilla **0.54100** → SE **0.82533**. Both round to the paper's
0.355 → 0.761 and 0.541 → 0.825 ✓.

**(d) §3 table: index-grouped R is −0.032396**, not −0.032431. Rounds to −0.032 either way, so the
appendix-table provenance conclusion is unchanged. Clean scored-only R = −0.032569 → −0.033 (the
Limitations value). Confirmed exact `F3_variants` from the JSON:
```
failures_as_zero_mean            0.856720   sd_ddof1 0.044876   sd_pop 0.036641
scored_only_mean                 0.873504   sd_ddof1 0.016924   sd_pop 0.013819
index_grouped_mean               0.874193   pstdev   0.018433
```
`0.874193 → 0.874` and `0.018433 → 0.018` are the metrics-doc pair, exactly.
`0.856720 → 0.857` and `0.044876 → 0.045` are the Table 1 pair, exactly.

**Dead ends recorded.**
- Looked for the cross-model panel's scored output under
  `/data/shared/.../cross_model_2026-05-03/`: `find … -name _summary.json` returns nothing
  (the run took >120 s; completed with 0 hits). Only raw run dirs
  (`minimax/`, `gemini/`, `minimax_minimax-m2.7/`, `google_gemini-3-flash-preview/`). Values in
  Tab.7 match `docs/2026-05-04_cross-cutting-paper-section.md:30-35` but I could not trace them to
  an eval summary on disk. **Left open — see §15.**
- Tried to reproduce Tab.5's `bad_attribute_value` zeros by re-running the classifier: not
  attempted (LLM cost, and it would not reproduce deterministically anyway). Diffed against the
  committed artifacts instead, which is what the table should have been transcribed from.
- Tried a `*_eval.json` glob for per-task scores first; abandoned it because failed tasks have no
  `_eval.json`, which would silently reintroduce the scored-only bias. Switched to
  `_summary.json → results[]`.
