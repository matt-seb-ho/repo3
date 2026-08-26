# Thread J1 — physical-plausibility judge metric, v2

## STATE OF PLAY  (updated 2026-07-27T08:40Z)

**Deliverable: SECTION-level soft-TreeSim.** Unit of judgment = one (deck, top-level GEOS section).
The judge returns one of four ordinal levels; **code** maps level → credit and aggregates with
TreeSim's own section weighting. Value-level judging is explicitly **out of scope** (rubric v4 §10).

| Rubric | sha256 | Frozen (mtime) | Status |
|---|---|---|---|
| `J1_rubric_v2.md` (value level) | `cb00c83822f250077c6ac1020eb37766c09650e9046c335995a3fffff69b7e46` | 2026-07-27T07:56:45Z | superseded |
| `J1_rubric_v3.md` (judge panel amendment) | `21f4a3c95831cce90f48b0920cd410c35d8d1368a31087c1a0395b86a063ad70` | 2026-07-27T08:06:35Z | superseded |
| **`J1_rubric_v4.md` (SECTION level — shipped)** | **`5ee738e008d94c31e884cbeca1d1d7b1213642f82732ad8b0428373a06a9bb4d`** | **2026-07-27T08:23:41Z** | **active** |

All three frozen **before any cell-level result of their own design was computed**. v4 §0 discloses
exactly what I had seen (partial *value-level* cell means) before v4 was written, and records that
the pre-registered criterion below was fixed at 07:56Z — before any judge call of any kind.

**Pre-registered success criterion — SHIPPABLE = VALID ∧ USEFUL** (full text `J1_rubric_v4.md` §11):

| | Criterion | Threshold | v1 result |
|---|---|---|---|
| C1 | inter-judge reliability | Krippendorff α ≥ **0.667** on the binary gate, **and** ≥ **0.40** on the 4-level ordinal | 0.2137 / 0.2566 |
| C2 | position stability | pooled mean \|B−A\| ≤ **0.0232** (⅓ of TreeSim's 0.0695 cell range) | 0.0552 |
| C3 | **ranking stability** | **every** judge's ordering identical, Vanilla (F0) last | 3 judges → 3 orderings |
| C4 | nuisance < signal | judge-choice range ≤ **1.0×** cell-effect range | 4.76× |
| U1 | utility | beats TreeSim on rung-3 prediction, **both** r_pb and AUC, bootstrap 90 % CI excluding 0 | v1 ≈ TreeSim |

**Judges (section level):** `tencent/hy3` (Tencent, **primary**), `qwen/qwen3-235b-a22b-2507`
(Alibaba), plus `google/gemini-3-flash-preview` and `openai/gpt-5.4-mini` — the two judges whose
17× severe-share spread killed v1, included to make C3/C4 the hardest available test. No DeepSeek.

**Run state**

| Pass | Status | Output (append+flush per call, resumable) |
|---|---|---|
| Section decomposition, 90 decks | **done**, reproduces published TreeSim `ok=89 mismatch=0 worst=0.00e+00` | `artifacts/J1_sections.jsonl` |
| Section order A, 1360 units × 4 judges = 5440 calls | **done** 5440/5440 | `artifacts/J1_sections_raw.jsonl` |
| Section order B, seed 1 (position control) | **done** 1808/1808 | `artifacts/J1_sections_raw_B.jsonl` |
| Section determinism re-run, seed 1 | **done** 1787/1808 | `artifacts/J1_sections_raw_rep1.jsonl` |
| *(secondary)* value-level order A, 526 calls | **done**, 0 failures | `artifacts/J1_judge_raw.jsonl` |

**FINAL RESULT: VALID = false, USEFUL = true, SHIPPABLE = false.** C1-C4 all fail; U1 passes
(soft-TreeSim beats TreeSim at predicting rung-3 loading failure, bootstrap CIs excluding 0).
Full verdict table and reasoning in §11. **Total spend $12.7** against the $40 gate.

**Resumability.** Every runner appends one JSONL row per call and `flush()`es immediately, and skips
`(deck_id, unit_id, judge, order, rep)` triples already on disk. A killed sweep resumes with no
lost calls and no duplicates. Single-writer is asserted before every launch (thread B lost ~$1.70
to two concurrent writers).

---


Submission 31642 (SIGA), NeurIPS 2026 author response. Started 2026-07-27T05:10Z.

**Baseline:** Thread B (`threads/B_lmaaj.md`), rubric `B_rubric_v1.md`. v1 FAILED. This thread does
not start from scratch: v1's five measured failure modes are the binding design constraints.

**Thesis in one line.** v1 asked a judge to make a physical judgment while *simultaneously*
performing arithmetic on magnitudes, exhaustive cross-deck search for renamed or relocated
counterparts, and identifier-consistency checking — in a 30 kB prompt with ~24 output tokens of
budget per verdict. v2 does all three of those in **code**, deterministically, and asks the model
only the residual physical question, one item at a time, in a bounded forced choice with no
severity vocabulary. Then it aggregates in code.

---

## 1. Verification of `src/eval/judge_geos.py` — v1's corrections confirmed

Read independently. Every correction in `B_lmaaj.md` §1 is **accurate**; the widely-circulated
description is wrong. Confirmed against source:

| v1 correction | Confirmed | Evidence |
|---|---|---|
| `compute_element_similarity` (tag gate, 0.4 `name` bonus, `matched/|union\{name}| * 0.6`) is the **matcher**, used only inside `_bipartite_match` | yes | `judge_geos.py:219-254`, called at `:288` |
| The **scorer** is `attr_similarity` = `|matching attrs| / |union of attr keys|` — no name bonus, no 0.6, `name` IS in the union | yes | `:394-411` |
| Matching is **greedy**, not Hungarian; local to same-tag siblings under an already-matched parent | yes | `:256-300`, `scores.sort(reverse=True)` |
| Root's own attributes never enter the score | yes | `own_attr` computed at `:525` but `node_score = matched_score - extra_penalty` |
| Each reference child contributes 1/N regardless of subtree size | yes | `matched_score = sum(child_scores)/n_gt` at `:515` |
| Nested lists fall back to string comparison (`{ {0,0,0} }` tokens keep braces, `_parse_scalar` → None) | yes | `_parse_list` `:169-177` |
| `IGNORE_TAGS = {Problem, Included, File}` | yes | `:39` |

I found one **additional** branch detail that v1 did not state and that matters for any
re-implementation: judge_geos branches on the **reference** side only (`if gt_grandchildren:`).
When a reference *leaf* has a candidate counterpart that *does* have children, the score is still
plain `attr_similarity` — the "flat 0.9" path v1 described applies to the top-level entry, not to
children. Getting this wrong cost me one debugging cycle (§3).

**Treating v1's corrected description as the reference description**, as instructed.

## 2. Diagnosis of v1 from its own raw output — what actually has to be fixed

Recomputed from `B_judge_raw.jsonl` + `B_prompts.jsonl` (4137 deck×item units, order A):

**2.1 Every score component is judge-dominated, so dropping the 0-10 scales is not sufficient.**

| Component | judge-mean range (max−min over 3 judges) |
|---|---:|
| `physics_fidelity`/10 | 0.294 |
| `mismatch_credit` | **0.287** |
| `plausibility`/10 | 0.197 |
| `lmaaj` (headline) | 0.260 |

The item-level `mismatch_credit` — the part v1 said "held up" — has a judge range of 0.287, i.e.
5.3× the 0.0545 cell effect *on its own*. So "decompose into item verdicts" alone does not fix
v1. Something has to shrink the judge's leverage over the number, not just relocate it.

**2.2 Three-judge exact agreement, split by item kind — the real story:**

| Item kind | n | 3-judge exact agreement | label distribution |
|---|---:|---:|---|
| `attribute` | 2716 | 48.6 % | cosmetic 73 / minor 10 / material 9 / severe 8 |
| `unpaired_same_tag` | 395 | 45.8 % | cosmetic 63 / minor 16 / material 10 / severe 11 |
| `extra_element` | 219 | 26.5 % | cosmetic 68 / minor 14 / material 7 / severe 11 |
| **`missing_element`** | **459** | **2.6 %** | cosmetic 24 / minor 5 / material 8 / **severe 63** |

Pairwise item agreement (4-way / collapsed cosmetic-vs-rest):
gpt×gemini 43.5 % / 53.2 %; gpt×qwen 58.4 % / 66.1 %; gemini×qwen 74.5 % / 82.0 %.

`missing_element` items agree at **2.6 %** — essentially zero, on 12 % of the items and the
highest-severity ones. That is not a rubric-boundary problem. Asking "is this missing reference
element important?" requires **searching the candidate deck for an equivalent under a different
name or a different parent**, over 26 000 characters. LLMs are poor at exhaustive long-context
search, and TreeSim's matcher is *local* (same-tag siblings under an already-matched parent), so
the elements it reports as missing are exactly the ones most likely to be present-but-relocated.
v1 handed the judge a search problem and recorded the resulting noise as a physics disagreement.

**This is the single largest actionable finding, and it drives the v2 design.**

## 3. Instrumented, credit-substitutable TreeSim — `scripts/J1_treesim.py`

Rather than scoring on a free-floating scale, v2's headline metric is **TreeSim recomputed with
the judge's credit substituted for the zeros**. To do that safely I re-implemented `tree_sim` with
per-event instrumentation and proved the re-implementation is exact.

```
$ python3 neurips_review/sprint/scripts/J1_treesim.py --verify
verify: ok=89 mismatch=0 skipped=1 worst_abs_diff=0.00e+00
```

**All 89 scorable held-out decks reproduce their published TreeSim score bit-exactly with
credit = 0.** (The 1 skip is `F0_s3_ExampleProppantTest`, `treesim: null` in `_summary.json` — the
known unparseable deck, floored to 0 with no API call, exactly as v1 did.)

Scores were read from `_summary.json` → `results[]`, never by globbing `*_eval.json`, per the
sprint rule. `F0_s3_ExampleProppantTest` is precisely the run globbing would have dropped.

Substitution semantics, frozen with the rubric:

| TreeSim scoring event | TreeSim | v2 with credit c |
|---|---|---|
| attribute in the key union that is not exactly equivalent | contributes 0 to `matched/|union|` | contributes `c` |
| unmatched reference child | `child_score = 0.0` | `child_score = c` |
| extra candidate child | `extra_penalty = β·n_extra/(n_gt+n_extra)` | `β·Σ(1−c_j)/(n_gt+n_extra)` |

Why this shape addresses v1: it inherits TreeSim's size weighting (so a deck with 200 flagged
differences cannot score 1.000 the way `F6_s2_AdvancedExampleThermoPoroElasticWellbore` did under
v1's flat mean), it sits on TreeSim's scale by construction, and — decisively — it caps the
judge's leverage. Only the ~20-25 % of the score that TreeSim currently zeroes is exposed to the
model. A judge-mean spread of 0.287 in item credit becomes ≈0.06 in the headline score.

*(Debugging note, disclosed: the first `--verify` pass failed on all 9
`TutorialHydraulicFractureWithAdvancedXML` decks by ~2e-4 because I recursed into reference leaves
whose candidate counterpart had children, taking the n_gt==0 grouping branch (flat 0.9) that
judge_geos does not take for children. Fixed by scoring reference leaves with `attr_similarity`
directly. Caught by the verification test, not by inspection — which is why the test exists.)*

---

## 4. Design change adopted mid-thread — "soft TreeSim" (coordinator, message 1)

The researcher's redesign arrived after §3 was built and **is a better idea than my brief's**, so
I adopted it. It also happens to be what `J1_treesim.py` already implemented: a
credit-substitutable TreeSim *is* soft-TreeSim. What changed in my plan:

| Coordinator requirement | What I did | v1 failure it addresses |
|---|---|---|
| Soften **scoring** only, keep matching hard | only `attr_*` events are judged; `missing_element` / `extra_element` keep TreeSim's verdict at every rung | v1's `missing_element` items had **2.6 %** three-judge agreement (§2.2). Removing them from the model's remit removes the single noisiest input. |
| Then a second rung that softens **pairing** | rung R2a: `_bipartite_match` admits same-tag pairs at similarity 0. **Deterministic — no model.** | subtree annihilation (thread B §6, 31/90 decks) |
| Ordinal rubric mapped to credits **in code** | the model answers a 3-question forced-choice tree; **code** maps the 4 terminals to v1's credits (1.0 / 0.7 / 0.3 / 0.0), byte-identical | free-form scales; judge-choice range 0.26 |
| Never call the model when the hard check passes | events exist only where `values_equivalent` returned False | cost |
| Cache on the substitution | cache key = SHA-256 of the rendered card, scoped to task | consistency + cost |
| Batch | 8 items per call, one shared task brief | v1 gave ~24 output tokens per verdict; v2 gives ~300 |
| Cap per deck, identical across cells | K = 60, **top-weight** selection, disclosed | one deck expands to 3333 reference elements |

**Deviation I made, and why.** The coordinator said to reuse v1's four severity *words*. I kept
v1's four **levels and credits** exactly, but elicit them through the bounded decision tree rather
than by asking for a severity word. Justification is in the v1 data, not in preference: v1's
4-way α was 0.2137 and its *collapsed binary* α was 0.2566 — collapsing barely helped, so the
disagreement was **not** a boundary-definition problem and re-using the words would have re-imported
it. The tree also yields, for free, the derived 4-level label that is directly comparable to v1's
α. Both are reported.

**A second deviation, in the strict direction.** The design direction in my brief wanted the judge
to read external data files. The researcher has ruled external assets out of scope and requires
soft-TreeSim to inherit TreeSim's information set so the ablation stays attributable. So EV5 (file
existence and shape) is **computed and stored on every item but never rendered into the judge's
card**, and is instead reported as a **zero-LLM deterministic diagnostic**. This matters: A1's
rung-3 failure categories show `missing_external_asset` is the **largest single failure class
(22 of 53 failures)**.

## 5. What the judge is actually asked — the deterministic evidence layer

The v2 thesis, restated concretely: v1 asked the model to do physics *and* arithmetic *and*
cross-deck search *and* consistency checking. v2 does the last three in code.

Live example from the smoketest, verbatim from the prompt:

```
ITEM I0002   kind=attr_diff   section=<ElementRegions>
  enclosing element : <CellElementRegion name="region">
  enclosing element attributes : {"name": "region", "cellBlocks": "{ * }", "materialList": "{ water, sand }"}
  attribute         : name
  REFERENCE value   : 'region'
  CANDIDATE value   : 'Region2'
  --- ESTABLISHED FACTS (computed from the files, not inferred) ---
  * GEOS schema declares name on <CellElementRegion> with NO default and marks it REQUIRED.
  * REFERENCE value token 'region': defined as an element name 1x in the reference / 0x in the
    candidate; referenced 1x in the reference / 0x in the candidate.
  * CANDIDATE value token 'Region2': defined as an element name 0x in the reference / 1x in the
    candidate; referenced 0x in the reference / 1x in the candidate.
```

"Is this rename used consistently?" is now a **stated fact**, not a search the model has to perform
over 26 kB. The GEOS binary's own XSD supplies 1699 attribute defaults, so
`gravityVector="{0,0,-9.81}"` — thread B's canonical annihilation trigger — is now *provably* the
schema default rather than a judgment call.

## 6. Rubric frozen

| File | sha256 | Frozen (mtime) |
|---|---|---|
| `artifacts/J1_rubric_v2.md` | `cb00c83822f250077c6ac1020eb37766c09650e9046c335995a3fffff69b7e46` | 2026-07-27T07:56:45Z |
| `artifacts/J1_rubric_v3.md` (judge-panel amendment) | `21f4a3c95831cce90f48b0920cd410c35d8d1368a31087c1a0395b86a063ad70` | 2026-07-27T08:06:35Z |

Verify: `sha256sum neurips_review/sprint/artifacts/J1_rubric_v*.md`

v2 was written **before any judge API call and before the judged-item population was even
counted**. v3 amends **only §8, the judge panel**, on the researcher's directive received after the
v2 freeze; at that moment **no cell-level quantity of any kind had been computed by this thread**,
so the panel change cannot have been made to obtain a result. The pre-registered success criterion
(v2 §11) is untouched by v3.

### Pre-registered success criterion (verbatim summary; full text in v2 §11)

**SHIPPABLE = VALID ∧ USEFUL.**

| | Criterion | Threshold | v1 |
|---|---|---|---|
| C1 | inter-judge reliability | Krippendorff α ≥ **0.667** on the Q1 gate **and** ≥ **0.40** on the 4-level label | 0.2137 / 0.2566 |
| C2 | position stability | pooled mean \|B−A\| ≤ **0.0232** (⅓ of TreeSim's 0.0695 cell range) | 0.0552 |
| C3 | ranking stability | **every** judge's single-judge ordering identical, Vanilla last | 3 judges → 3 orderings |
| C4 | nuisance < signal | judge-choice range ≤ **1.0×** cell-effect range | 4.76× |
| U1 | utility | beats TreeSim on rung-3 prediction, both r_pb and AUC, bootstrap 90 % CI excluding 0 | LMaaJ ≈ TreeSim |

## 7. Judge panel — one substitution and one addition, both disclosed

Per rubric v3: **`deepseek-v4-flash` is the primary judge** (researcher directive), with a
**mandatory same-family bias control** — the scored backbone is itself `deepseek-v4-flash`.

The coordinator asked for one independent judge on a stratified subsample. **I ran all four
independent judges over the full sweep instead**, because the full independent pass priced at
**$1.70** and because C1/C3/C4 were *already pre-registered* and need a multi-judge α, every
judge's ordering, and the per-judge cell-mean range. Weakening pre-registered criteria after the
fact is the thing pre-registration exists to prevent. Running more than asked, at negligible cost,
cannot bias the result toward us.

`moonshotai/kimi-k2.6` **dropped**: `finish_reason=length` on 4 of 5 smoketest calls, returning an
**empty body** after burning the whole 3000-token completion budget — 12 517 output tokens billed
for one usable call ($0.047, the most expensive judge and the only failing one). `response_format`
did not help; its hidden reasoning consumes the budget before content is emitted. **Excluded for
technical failure to emit the schema, not for its scores — its scores were never obtained.** Same
model, same failure, same disposition as thread B §8.

### Three technical fixes found by the smoketest (parsing only, no rubric content changed)

1. `qwen3235b` returns `"id": "ITEM X01"` where the schema asks for `"X01"` → ids normalised to the
   `X\d+` token. Recovered qwen from 60 % to **100 %** coverage.
2. `deepseek-v4-flash` ignores `response_format: json_schema` and emits either a dict keyed by item
   id or a bare array → a shape normaliser accepts all three shapes. Verdict content untouched.
3. DeepSeek's `json_object` mode **400s unless the prompt contains the word "json"** → an explicit
   output-format block was added to the question text (and it improves shape conformance for every
   judge).

## 8. Smoketest (mandated) — one task, raw output inspected before scaling

`ExampleProppantTest`, 37 unique item-units, 5 chunks × 5 judges = **25 calls, 25 ok, coverage
1.00, $0.0658**.

| Judge | cosmetic | minor | material | severe | uncertain |
|---|---:|---:|---:|---:|---:|
| `dsv4flash` | 83.8 % | 8.1 % | 2.7 % | 0.0 % | 5.4 % |
| `gpt54mini` | 89.2 % | 8.1 % | 2.7 % | 0.0 % | 0.0 % |
| `gemini3flash` | 81.1 % | 13.5 % | 5.4 % | 0.0 % | 0.0 % |
| `qwen3235b` | 86.5 % | 5.4 % | 2.7 % | 5.4 % | 0.0 % |
| `mistralmed31` | 81.1 % | 13.5 % | 2.7 % | 2.7 % | 0.0 % |

**Five-judge exact 4-way agreement 83.8 %; Q1-gate agreement 89.2 %.** v1's comparable numbers were
41.5 % and 59.7 % on three judges. The severe share spans 0–5.4 % across judges where v1's spanned
**1.6–26.6 %**. `dsv4flash` agrees with the independent judges at 83.8–89.2 % (4-way) and
89.2–97.3 % (gate); its abstention rate is 5.4 %, well under the 25 % escalation trigger, so
**no escalation to `deepseek-v4-pro`** — the 4 partial `dsv4pro` calls made by an aborted launch are
parked unanalysed in `J1_judge_raw_dsv4pro_partial.jsonl`.

Raw verdicts on the deck v1 smoketested (`F6_s1_ExampleProppantTest`) are in the session record; the
one instructive disagreement is `maxProppantConcentration` absent in the candidate, which therefore
takes the schema default 0.6 against the reference's 0.62: `dsv4flash` said `cosmetic`, the other
four said `minor`, and the frozen median-across-judges rule returns `minor`. That is the ensemble
rule doing exactly the job it was frozen for.

*Caveat, stated before the full sweep: `ExampleProppantTest` is dominated by identifier renames,
which the evidence layer makes easy. Full-sweep agreement will be lower.*

## 9. Cost estimate before launching (gate: stop and report above $40)

Computed from **raw token counts × list price**, never from a provider cost field
(`total_cost_usd` in this repo is computed at Anthropic rates — trap 2 of the cost memory).
DeepSeek off-peak list, from `scripts/oh_dsv4_compare.py:56`: input $0.14/M (billed at the
cache-**miss** rate throughout, which over-states), output $0.28/M.

| Pass | Est. |
|---|---:|
| Order A, full sweep, 115 chunks × 5 judges = 575 calls | $1.78 |
| Order B, seed-1 subsample, 5 judges | ~$1.30 |
| Determinism re-run, seed-1, order A, 5 judges | ~$1.30 |
| Smoketests already spent (incl. the discarded kimi/dsv4pro rounds) | $0.31 |
| **Projected total** | **≈ $4.7** |

Under the gate by ~8×. Proceeding.

### Operational discipline

Thread B lost ~$1.70 to two concurrent processes writing one output file. Before every launch this
thread asserts a single writer:
`ps -eo pid,comm,args --no-headers | awk '$2=="python3" && /J1_run_judges/ {print $1}' | wc -l` → 1.
One aborted launch did occur (the default judge list included the escalation-only `dsv4pro` and the
dropped `kimik26`); it was killed, the output file was verified to have 0 corrupt lines, deduped on
`(chunk_id, judge, rep)`, and filtered to the frozen panel before relaunch. Wasted spend: **$0.14**.

---

# 10. SECONDARY ARM — value-level soft-TreeSim (rubric v2/v3, superseded design)

Completed before the researcher redirected to section level. **526/526 calls, 0 failures, $1.54.**
Reported because it is a complete, independent test of the same hypothesis at a different
granularity, and because its failure modes explain why the section unit is the better one.
It is **not** the deliverable — value-level judging is out of scope (rubric v4 §10).

Artifacts: `J1_items.jsonl`, `J1_judge_raw.jsonl`, `J1_analysis.json`, `J1_deck_scores.csv`.
Judges: `deepseek-v4-flash` (primary, per rubric v3) + `gpt-5.4-mini`, `gemini-3-flash-preview`,
`qwen3-235b-a22b-2507`, `mistral-medium-3.1`. 889 unique item-units, **83.3 % cache hit rate**
(5312 judged item-slots → 889 calls per judge).

## 10.1 Agreement — large improvement over v1, still short of the pre-registered bar

| Statistic | v2 value-level (5 judges, 889 units) | v1 (3 judges, 4137 units) |
|---|---:|---:|
| Krippendorff α, binary gate | **0.5265** | 0.2566 |
| Krippendorff α, 4-level nominal | **0.4561** | 0.2137 |
| Krippendorff α, 4-level ordinal | 0.5218 | — |
| Fleiss κ, 4-level | 0.4695 | 0.2238 |
| Exact all-judge agreement, 4-level | 50.1 % | 41.5 % |

**α more than doubled** (0.2137 → 0.4561 on the like-for-like 4-level nominal statistic), with
*more* judges, which makes α harder, not easier. The deterministic evidence layer is doing real
work. But **C1 fails**: 0.5265 < 0.667 on the gate. The 4-level sub-threshold (≥ 0.40) passes.

Severity shares are far tighter than v1's 17× spread but still not close:

| Judge | cosmetic | minor | material | severe | abstain |
|---|---:|---:|---:|---:|---:|
| `dsv4flash` | 71.6 % | 4.6 % | 2.9 % | 16.3 % | 4.5 % |
| `gpt54mini` | 57.5 % | 6.5 % | 10.9 % | 25.0 % | 0.1 % |
| `gemini3flash` | 73.2 % | 6.9 % | 2.9 % | 16.8 % | 0.2 % |
| `qwen3235b` | 59.7 % | 4.1 % | 0.8 % | **34.7 %** | 0.7 % |
| `mistralmed31` | 62.3 % | 6.1 % | 4.6 % | 26.9 % | 0.1 % |

severe-share range **16.3–34.7 % (2.1×)** against v1's **1.6–26.6 % (17×)**.

## 10.2 C3 — ranking stability: PASSES, and this is the headline of the secondary arm

| Judge | R1 ranking |
|---|---|
| `dsv4flash` | F6 > SE > F0 |
| `gpt54mini` | F6 > SE > F0 |
| `gemini3flash` | F6 > SE > F0 |
| `qwen3235b` | F6 > SE > F0 |
| `mistralmed31` | F6 > SE > F0 |
| *(ensemble)* | F6 > SE > F0 |

**All five judges, from five families, produce the identical ordering, and all put Vanilla last.**
v1 had three judges producing three orderings, one of which inverted the paper's central contrast.
That specific failure — the one the coordinator called disqualifying — **is fixed.**

Note the ensemble swaps the top two relative to TreeSim (TreeSim: SE > F6 > F0; soft: F6 > SE > F0).
The F6/SE gap is 0.0019 against seed sds of 0.010, so that swap is not resolvable and should not be
reported as a finding either way.

## 10.3 C4 — nuisance vs signal: marginal fail, but 4× better than v1

| Quantity | v2 value-level | v1 |
|---|---:|---:|
| cell-effect range (F0 → best) | 0.0775 | 0.0545 |
| judge-choice range | 0.0878 | 0.2595 |
| **ratio** | **1.13×** | **4.76×** |

Fails the ≤ 1.0 threshold by 13 %. The mechanism is the one the design predicted: because only the
~20 % of the score TreeSim zeroes is exposed to the model, a 0.29 spread in mean item credit
becomes a 0.088 spread in the deck score.

## 10.4 Ladder — where the movement actually comes from

| Rung | Values | Matching | F0 Vanilla | F6 S+X | SE | ranking |
|---|---|---|---:|---:|---:|---|
| **R0** TreeSim | hard | hard | 0.7196 ± 0.0661 | 0.7814 ± 0.0015 | 0.7891 ± 0.0101 | SE > F6 > F0 |
| **R1** soft values | **soft** | hard | 0.7476 ± 0.0731 | 0.8251 ± 0.0103 | 0.8232 ± 0.0095 | F6 > SE > F0 |
| **R2a** soft matching | hard | **soft** | 0.7447 ± 0.0733 | 0.8048 ± 0.0060 | 0.8227 ± 0.0086 | SE > F6 > F0 |
| **R2** both | **soft** | **soft** | 0.7839 ± 0.0819 | 0.8590 ± 0.0063 | 0.8696 ± 0.0075 | SE > F6 > F0 |

**R2a requires no model at all.** Admitting same-tag pairs at similarity 0 — a three-line
deterministic change — moves the mean as much as the entire five-judge LLM panel does (+0.025 for
F0, +0.023 for F6, +0.034 for SE). Anyone considering paying for an LLM judge should be shown this
row first.

**Credit-mapping sensitivity is negligible**, which is reassuring: frozen (1.0/0.7/0.3/0.0) gives
F0 0.7717 / F6 0.8251 / SE 0.8232; a pure binary mapping (1/1/0/0) gives 0.7726 / 0.8255 / 0.8236.
The headline is not an artifact of the chosen weights.

## 10.5 U1/U2 — calibration against execution: does NOT beat TreeSim

Ground truth: A1 rung-3 `rung3_lenient`, all 90 held-out decks (62 pass / 28 fail).

| Metric | r_pb | ROC AUC |
|---|---:|---:|
| TreeSim (R0) | 0.3944 | 0.8033 |
| R1 soft values | 0.3958 | 0.8177 |
| R2a soft matching *(no model)* | 0.3697 | 0.8298 |
| R2 both | 0.3494 | **0.8494** |

Paired bootstrap, 2000 resamples: R1 − R0 in AUC = **+0.0144, 90 % CI [−0.0097, +0.0409]** —
**crosses zero. U1 FAILS.** R2a − R0 = +0.0265 [−0.0039, +0.0613], also crossing zero, and R2a is
free. On r_pb the softened rungs are *worse* than TreeSim.

Rung 4 (runs to completion, n = 27): AUC 0.71 for **every** metric including TreeSim — no separation.
Rung 5 (QoI relative error, n = 20): Spearman −0.02 (TreeSim), −0.04 (R1). **No input-side metric
in this study predicts quantity-of-interest error at all.** That is worth stating plainly: it is the
strongest available argument that the execution ladder, not any input-side metric, is the answer to
the reviewers' ask.

## 10.6 Self-preference control (rubric v3) — measured, and it is a level effect

`deepseek-v4-flash` judging `deepseek-v4-flash`'s own decks:

- mean item credit, primary = **0.757**; independent-4 median = **0.695**; **difference +0.062**.
- It agrees with the independent judges at 83.8–89.2 % (4-way) on the smoketest and produces the
  **same cell ordering** as every independent judge on the full sweep.
- Its abstention rate is 4.5 %, the highest of the five but far under the 25 % escalation trigger.

So the primary judge is measurably more generous to its own family's output, but **uniformly** —
it is a level shift, not a contrast distortion, and it does not move any ranking. That is the
distinction that has to be stated if this is ever reported: self-preference of this size is
harmless to a *comparison* and fatal to an *absolute* claim.

## 10.7 U4 — the two blind spots, quantified

**Blind spot 1 — external data files. This is the sharpest number in the secondary arm.**

10 held-out decks have rung-3 failure category `missing_external_asset`.

| | value |
|---|---:|
| rung-3 pass rate of these decks | **0 / 10** |
| mean TreeSim | **0.8396** |
| mean soft-TreeSim (R1) | **0.8751** |

Every one of these decks **fails to load in the real GEOS binary**, and both metrics score them
*above* the overall held-out mean — soft-TreeSim scores them *higher* than TreeSim does. Neither
metric reads the files, so neither can see it, and `missing_external_asset` is the **largest single
rung-3 failure class (22 of 53 failures)**. A deterministic zero-LLM file-existence check reaches
AUC 0.661 / r_pb 0.378 on rung-3 prediction on its own — worse than TreeSim overall, but on a
failure class TreeSim cannot see at all.

**Blind spot 2 — unmatched subtrees.** 37 of 89 decks (F0 10, F6 13, SE 14) lose at least one whole
reference subtree to the `similarity > 0` pairing gate. Their mean TreeSim is **0.661** against
0.760 overall; soft matching alone lifts them to **0.727** and the full R2 to **0.796**. Consistent
with thread B §6, and again slightly *against* SIGA (SE hit most often), which is what makes
disclosing it credible.

---

# 11. PRIMARY ARM — SECTION-level soft-TreeSim (rubric v4). RESULT: **FAIL**

**9056 calls, 21 failures (0.23 %), $10.71.** Unit coverage **1360/1360 for all four judges after
retry** (mean per-deck judge coverage 0.9889 — the shortfall is the one rung-1-failed deck).

Artifacts: `J1_sections.jsonl`, `J1_sections_raw{,_B,_rep1}.jsonl`,
`J1_sections_failed_quarantine.jsonl`, `J1_section_analysis.json`, `J1_section_deck_scores.csv`.

## 11.1 Verdict against the pre-registered criterion

| # | Criterion | Threshold | Measured | | v1 |
|---|---|---|---|:--:|---|
| **C1** | Krippendorff α, binary gate | ≥ 0.667 | **0.391** | **FAIL** | 0.2566 |
| | Krippendorff α, 4-level nominal | ≥ 0.40 | **0.288** | **FAIL** | 0.2137 |
| **C2** | pooled mean \|order B − order A\| | ≤ 0.0232 | **0.0264** | **FAIL** | 0.0552 |
| **C3** | all judges same cell ordering, Vanilla last | both | **2 orderings**; Vanilla last **4/4** | **FAIL** | 3 orderings; Vanilla not last |
| **C4** | judge-choice range ÷ cell-effect range | ≤ 1.0 | **1.81** (centered 1.16) | **FAIL** | 4.76 |
| **U1** | beats TreeSim on rung-3, both r_pb and AUC, bootstrap CI excluding 0 | — | **r_pb 0.476 vs 0.394; AUC 0.848 vs 0.803; both CIs exclude 0** | **PASS** | ≈ TreeSim |

**VALID = false. USEFUL = true. SHIPPABLE = false.**

**Do not ship this metric as a validated secondary evaluation metric.** It fails four of four
validity criteria that were fixed before any judge call. That is the answer to the question I was
asked, and it is the same answer v1 got, from an independently designed instrument at a different
granularity.

## 11.2 But the failure is a different, more informative failure than v1's

| Quantity | v1 | v2 value-level | **v4 section-level** |
|---|---:|---:|---:|
| α, 4-level nominal | 0.2137 | 0.4561 | 0.2878 |
| α, 4-level ordinal | — | 0.5218 | 0.4735 |
| **Gwet's AC1, 4-level** *(diagnostic)* | — | — | **0.8107** |
| raw all-judge exact agreement, 4-level | 41.5 % | 50.1 % | **70.3 %** |
| raw all-judge exact agreement, gate | 59.7 % | 55.9 % | **73.3 %** |
| judge-choice ÷ cell-effect range | 4.76× | 1.13× | 1.81× |
| judges putting Vanilla last | **2 / 3** | **5 / 5** | **4 / 4** |
| beats TreeSim on rung-3 (CI excludes 0) | no | no | **yes** |

**C1's failure is a prevalence artifact and must be reported as ambiguous, not as low agreement.**
74–94 % of section verdicts are `equivalent`. When one category dominates, α and κ estimate chance
agreement from the observed marginals and collapse toward zero even when raters almost always agree
— the well-known kappa paradox. Here the two bracket the truth: **α = 0.29–0.47 (pessimistic),
Gwet's AC1 = 0.81 (optimistic), raw exact agreement 70.3 %.** I pre-registered α, so **C1 fails as
pre-registered** and I am not moving the goalposts. But the honest summary is *"chance-corrected
inter-judge reliability cannot be established on this label distribution"*, not *"the judges
disagree"*.

Pairwise exact agreement makes the structure plain:

| Pair | exact 4-level | gate |
|---|---:|---:|
| `hy3` × `gemini3flash` | **91.5 %** | 93.5 % |
| `qwen3235b` × `gemini3flash` | 89.3 % | 91.0 % |
| **`hy3` × `qwen3235b`** *(the instructed pair)* | **86.5 %** | **89.6 %** |
| `qwen3235b` × `gpt54mini` | 77.6 % | 82.6 % |
| `gemini3flash` × `gpt54mini` | 76.7 % | 80.1 % |
| `hy3` × `gpt54mini` | 74.1 % | 77.9 % |

Three of four judges agree with each other at 86–92 %. **`gpt-5.4-mini` is a systematic outlier**:
grand mean 0.707 against 0.771 / 0.774 / 0.788, and `material_deviation` on **18.1 %** of sections
against 1.0–4.7 % for the others. It is the same judge that inverted v1's central contrast. On the
instructed pair alone (`hy3` + `qwen3235b`) α_gate rises to 0.480 and exact agreement to 89.6 % —
still short of 0.667.

**C3 is a near-miss with the important half fixed.** All four judges put **Vanilla last**; the
disagreement is entirely in the F6/SE ordering (`hy3`, `gpt54mini`: SE > F6; `qwen3235b`,
`gemini3flash`: F6 > SE). The F6−SE gap in the ensemble is **0.0001** against seed sds of ~0.009,
so it is unresolvable by any metric — TreeSim's own F6−SE gap is 0.0077 against sd 0.010. C3 as
written demands an ordering the data cannot support at any n we have. **The specific v1 failure —
a judge ranking Vanilla above the best SIGA cell — did not recur in either v2 arm.**

**C2 is a 14 % overshoot**, pooled mean \|B−A\| 0.0264 vs the 0.0232 bar, with a 10.0 % unit-level
verdict flip rate between orders. `hy3` (0.0125) and `gemini3flash` (0.0125) are well inside the
bar; `qwen3235b` (0.0367) and `gpt54mini` (0.0440) blow it. Determinism re-run at temperature 0:
**5.2 % unit-level flip rate** — soft-TreeSim is not reproducible, and TreeSim is.

## 11.3 Score table by cell (held-out, 10 tasks × 3 seeds, mean ± sd over seeds)

| Cell | TreeSim | soft-TreeSim (4 judges) | instructed pair only |
|---|---:|---:|---:|
| Vanilla (F0) | 0.7196 ± 0.0661 | 0.7246 ± 0.0629 | 0.7178 ± 0.0625 |
| S+X (F6) | 0.7814 ± 0.0015 | **0.8043 ± 0.0097** | 0.8008 ± 0.0104 |
| SE | 0.7891 ± 0.0101 | **0.8042 ± 0.0086** | 0.7984 ± 0.0048 |

Per judge:

| Judge | F0 | F6 | SE | ranking |
|---|---:|---:|---:|---|
| `hy3` | 0.7193 | 0.7928 | 0.8007 | SE > F6 > F0 |
| `qwen3235b` | 0.7163 | 0.8087 | 0.7960 | F6 > SE > F0 |
| `gemini3flash` | 0.7363 | 0.8168 | 0.8108 | F6 > SE > F0 |
| `gpt54mini` | 0.6726 | 0.7100 | 0.7383 | SE > F6 > F0 |

Note soft-TreeSim **inflates F6/SE by ~+0.02 but barely moves F0 (+0.005)**, so the measured cell
separation *grows* from 0.0695 to 0.0797. It also does **not** reproduce TreeSim's σ-collapse: F6's
seed sd goes 0.0015 → 0.0097, i.e. the judge *adds* seed variance. That matters — the σ-collapse
claim is a TreeSim property, and this metric does not independently corroborate it.

**Credit-mapping sensitivity is negligible**: frozen (1/0.7/0.3/0) gives 0.7246 / 0.8043 / 0.8042;
binary (1/1/0/0) gives 0.7215 / 0.8029 / 0.7999. The headline is not an artifact of the weights.

## 11.4 The named deliverable — per-section LLM credit vs per-section TreeSim

**This is the most useful output of the thread.**

| Section | n | mean TreeSim | mean LLM credit | gap | Pearson | LLM `equivalent` share |
|---|---:|---:|---:|---:|---:|---:|
| `Outputs` | 156 | 0.899 | 0.999 | **+0.100** | 0.098 | 98.7 % |
| `Events` | 123 | 0.827 | 0.928 | **+0.101** | 0.468 | — |
| `ElementRegions` | 165 | 0.866 | 0.935 | +0.069 | 0.521 | — |
| `Tasks` | 76 | 0.944 | 1.000 | +0.056 | n/a | — |
| `Mesh` | 123 | 0.955 | 0.978 | +0.023 | 0.455 | — |
| `Geometry` | 26 | 0.975 | 0.988 | +0.014 | −0.027 | — |
| `NumericalMethods` | 174 | 0.994 | 1.000 | +0.006 | n/a | — |
| `Functions` | 81 | 0.849 | 0.840 | −0.010 | 0.621 | — |
| `FieldSpecifications` | 165 | 0.912 | 0.896 | −0.016 | 0.513 | — |
| `Constitutive` | 174 | 0.953 | 0.923 | **−0.031** | 0.751 | 79.9 % |
| `Solvers` | 97 | 0.900 | 0.849 | **−0.050** | 0.568 | **69.8 %** |

**The sign of the gap sorts the sections into bookkeeping and physics, and it sorts them correctly.**
The judge is *more lenient* than TreeSim on `Outputs`, `Events`, `Tasks`, `ElementRegions` — naming,
scheduling and plumbing, where TreeSim's exact-equality penalties are mostly renames. It is
*harsher* than TreeSim on `Solvers`, `Constitutive`, `FieldSpecifications`, `Functions` — the
sections that carry the physics. On `Solvers` it calls only 69.8 % of sections equivalent and
17.3 % `material_deviation`, where TreeSim scores 0.900.

That is exactly the behaviour a physical-plausibility instrument should show, it was not tuned for,
and it is the one claim in this thread that does not depend on the judge being a reliable
discriminator between *cells*. `Outputs` also has near-zero correlation with TreeSim (r = 0.098)
while `Constitutive` has r = 0.751 — the two metrics agree where physics lives and disagree where it
does not.

## 11.5 U1/U2 — calibration against execution. Beats TreeSim on rung 3, nothing else.

Rung 3 (`geosx -v` lenient, all 90 held-out decks, 62 pass / 28 fail):

| Metric | r_pb | ROC AUC | mean(pass) | mean(fail) |
|---|---:|---:|---:|---:|
| TreeSim | 0.3944 | 0.8033 | 0.8427 | 0.5877 |
| **soft-TreeSim (4 judges)** | **0.4761** | **0.8479** | 0.8773 | 0.5571 |
| soft-TreeSim (instructed pair) | 0.4640 | 0.8335 | 0.8683 | 0.5598 |

Paired bootstrap over decks, 2000 resamples:
- Δ AUC = **+0.0446, 90 % CI [+0.0068, +0.0867]** — excludes 0.
- Δ r_pb = **+0.0817, 90 % CI [+0.0412, +0.1318]** — excludes 0.

**U1 PASSES.** This is the one thing v1 could not do: v1's LMaaJ matched TreeSim at zero marginal
cost and therefore earned nothing. The section-level judge is a **significantly better predictor of
whether a deck loads in the real GEOS binary** than the structural metric is.

Everything else fails to separate:

| Ladder rung | n | TreeSim | soft-TreeSim |
|---|---:|---:|---:|
| rung 4, runs to completion (AUC) | 27 | 0.712 | 0.697 (Δ CI [−0.106, +0.074]) |
| rung 5, QoI relative error (Spearman) | 20 | −0.017 | +0.033 |

**No input-side metric in this study predicts quantity-of-interest error.** Both are ~0. State that
plainly: it is the strongest available argument that the execution ladder, not any input-side
metric, answers the reviewers' ask.

## 11.6 U4 — the two blind-spot subgroups

**Blind spot 1 — external data files. The sharpest number in the thread.**

10 held-out decks fail rung 3 with category `missing_external_asset`
(`missing_external_asset` is the largest single rung-3 failure class overall, **22 of 53**).

| | value |
|---|---:|
| rung-3 pass rate | **0 / 10** |
| mean TreeSim | **0.8396** |
| mean soft-TreeSim | **0.7874** |
| overall held-out mean (TreeSim) | 0.7634 |

**Every one of these decks fails to load, and TreeSim scores them above the held-out average.**
soft-TreeSim marks them down by 0.052 — directionally right, still far above a failing score.
Neither metric reads the files, by deliberate design (rubric v4 §10), so neither can see it. This
is the cleanest demonstration available that an input-side metric cannot substitute for execution.

**Blind spot 2 — unmatched reference sections (subtree annihilation / `<Included>` duplication).**
49 of 89 decks (F0 18, F6 15, SE 16) have ≥1 reference section with no candidate counterpart and
more than one element. Their mean TreeSim is **0.627** vs 0.763 overall; soft-TreeSim gives
**0.633** — essentially no change, because rubric v4 keeps matching hard by instruction, so those
sections retain credit 0 and are never judged. Thread B's separate finding stands: 5237 of 6597
section units (79.4 %) have no candidate counterpart, dominated by `<Included>` expansion
duplicating top-level section tags in the reference.

**The value-level arm shows what fixing this is worth, deterministically**: admitting same-tag pairs
at similarity 0 (rung R2a, a three-line change, **no model**) lifts the annihilation subgroup from
0.661 to 0.727 and improves rung-3 AUC from 0.803 to 0.830. That is a larger gain than the entire
LLM panel delivers, at zero marginal cost. **Anyone weighing whether to pay for an LLM judge should
be shown that row first.**

## 11.7 Operational record

| Item | Value |
|---|---:|
| Section order A | 5440 calls, 5440 ok after retry, $6.55 |
| Section order B (seed 1, position control) | 1808 calls, 1808 ok after retry, $2.18 |
| Section determinism re-run (seed 1, rep 1) | 1808 calls, 1787 ok, $2.13 |
| Value-level arm (secondary) | 526 calls, 0 failures, $1.54 |
| Smoketests + aborted `dsv4pro` launch | $0.31 |
| **Total API spend** | **≈ $12.7** |

Against the $40 stop-and-report gate. All figures computed from **raw token counts × list price**,
never from a provider-reported cost field.

**`tencent/hy3` is a reasoning model and that is a real cost.** It emitted **2 677 054** completion
tokens against ~100–127 k for each of the other three judges — 21× more — which is why it cost
$2.12 despite the cheapest input rate on the panel. 61 of its calls (1.1 %) initially returned an
**empty body** after exhausting a 3600-token budget; all 61 succeeded on retry at 8000 tokens.
Failures were evenly distributed across cells (F0 20 / F6 20 / SE 21), so no cell bias, and the
quarantined rows are kept at `J1_sections_failed_quarantine.jsonl`. 21 residual failures in the
determinism re-run are `hy3` truncations and affect only that statistic.

**Single-writer discipline held.** Order A, order B, and the re-run each wrote their own file; the
analysis dedups on `(deck_id, unit_id, judge, order, rep)`. One launch was aborted (default judge
list included the escalation-only `dsv4pro` and the dropped `kimik26`): killed, file verified 0
corrupt lines, deduped, filtered to the frozen panel, relaunched. Wasted spend **$0.14** against
thread B's $1.70.

**No escalation to `deepseek-v4-pro` or `deepseek-v4-flash`.** `hy3`'s invalid-level rate was 1.1 %
before retry and 0 % after, far under the 25 % trigger, and it is one of the three mutually
consistent judges (86–92 % pairwise). The capability bar was met; the reliability bar was not, and
that is not a capability problem — `gpt-5.4-mini`, the strongest and most expensive judge on the
panel, is the outlier.

## 11.8 What this thread recommends

1. **Do not present soft-TreeSim as a validated second metric.** It fails four of four
   pre-registered validity criteria. Two independently designed judge metrics — v1's deck-level
   scalar and v4's section-level ordinal — have now failed their own pre-registered reliability
   tests on this task. That consistency is itself the finding.
2. **Do ship §11.4, the per-section divergence table.** It is a within-deck audit of *TreeSim*, not
   a between-cell measurement, so it does not need the judge to be a reliable cell discriminator.
   The gap's sign separates bookkeeping sections (judge more lenient) from physics sections (judge
   harsher), which is evidence that TreeSim's absolute level is depressed by naming and plumbing
   penalties and that its physics sections are, if anything, scored too generously.
3. **Do ship §11.6 blind spot 1.** 10 decks, 0/10 load in GEOS, TreeSim mean 0.840 — above the
   held-out average. One table, no LLM trust required, and it is the most honest possible statement
   of why the execution ladder is the answer to the reviewers' objection.
4. **Do ship the R2a deterministic result** (value-level §10.4, §11.6): a three-line fix to
   `_bipartite_match` moves the numbers more than a four-judge LLM panel does. Free, reproducible,
   and it makes the metric-limitation disclosure concrete.
5. **Report the QoI null.** Neither TreeSim nor soft-TreeSim predicts QoI error (|Spearman| < 0.04,
   n = 20). Input-side metrics do not reach the quantity reviewers care about.
6. **State the value-level gap as named work in progress** (rubric v4 §10): per-value physical
   plausibility needs a purpose-built benchmark and domain-expert coordination, and the section
   judge does not cover it.
