# Thread K2 — deterministic TreeSim matching fix, re-score everything

## STATE OF PLAY (updated 2026-07-27T11:05Z) — **COMPLETE**

**Mission.** Implement the deterministic `_bipartite_match` fix, re-score both splits, report old vs
new side by side, and answer H28: does the Vanilla→SE contrast survive?

**No API spend. Deterministic. Nothing in `src/` was modified.**

| Step | Status |
|---|---|
| Read scorer + threads B / J1 / OVERNIGHT_DECISIONS | done |
| Patched scorer `artifacts/K2_scorer.py`, 4 modes behind a flag | done |
| **Bit-exact reproduction, strict mode** | **held-out 179/179, worst 0.00e+00; val 557/559** |
| Cross-check against J1's independent `J1_treesim.py`, both modes | **179/179, worst 0.00e+00** |
| Re-score val (561 runs) + held-out (180 runs), 4 modes each | done |
| Old-vs-new table, bootstrap, rung-3 AUC | done |

**HEADLINE ANSWERS**

1. **The contrast survives and widens.** Vanilla→SE **+0.0695 → +0.0780**; paired bootstrap on the
   change **+0.0086, 95 % [−0.0037, +0.0217]**, n_boot = 20 000, seed 31642 — right direction,
   interval includes 0.
2. **Reported loudly, against us:** only the SE contrast widens. **S+X (+0.0618→+0.0601) and S+X+M
   (+0.0631→+0.0581) narrow and cross from P(Δ≤0) ≈ 0.04 to ≈ 0.09.** And the “≈40× lower
   variance” claim **changes cell**: S+X’s σ ratio falls 44.5× → 12.1× while X+M’s rises
   15.1× → 49.0×. Vanilla’s own σ gets *worse* (0.0809 → 0.0898).
3. **J1 confirmed independently.** rung-3 AUC **0.8036 → 0.8298**, annihilation subgroup
   **0.6636 → 0.7268**, r_pb **0.3944 → 0.3697** — that last one is a *degradation* whose 90 % CI
   **excludes 0**.
4. **A SIXTH harness bug found, unrelated to this thread:** the published **val** scoring pass raced
   the val campaign. 3 of the 4 published val “failures” are decks written after the scorer read
   them. R+S is really **0.887 ± 0.011**, not 0.857 ± 0.045, and this inflates each published
   Resolution-IV main effect by ±0.0075: **S −0.008→−0.000, X +0.011→+0.004, M +0.009→+0.001**.
   R stays largest and negative, so the paper’s val claim survives. See §3.1.
5. **Strictly perfect decks: unmoved by the fix in every cell, both splits.** (`tex:216`’s SE 6/51
   is really 7/51 — pre-existing, confirms thread D.)

**Artifacts.** `artifacts/K2_scorer.py` · `K2_analyse.py` · `K2_make_table.py` ·
`K2_rescored_val.jsonl` (561) · `K2_rescored_heldout.jsonl` (180) · `K2_comparison.json` ·
`K2_cell_means.csv` · **`K2_comparison_table.md`** (the single sorted old-vs-new table).

---

## 1. Orientation — what I inherited and verified before writing code

Read end to end: `src/eval/judge_geos.py` (933 lines), `threads/B_lmaaj.md`,
`threads/J1_judge_v2.md`, `sprint/OVERNIGHT_DECISIONS.md`, `sprint/PROVENANCE.md`,
`artifacts/D_recompute.py`, `artifacts/P0_f3_recompute.py`, `scripts/J1_treesim.py`,
`artifacts/B_treesim_annihilation.json`.

**The scorer description I am working from** (B §1 corrections, re-confirmed by J1 §1, and
re-confirmed independently here against source):

| Fact | Line in `src/eval/judge_geos.py` |
|---|---|
| `compute_element_similarity` (tag gate · 0.4 `name` bonus · `matched/│union\{name}│ × 0.6`) is the **matcher only** | `:219-253`, called at `:282` |
| The **scorer** is `attr_similarity` = `│matching attrs│ / │union of attr keys│`, no bonus, no 0.6, `name` **in** the union | `:396-413` |
| Matching is **greedy**, local to same-tag siblings under an already-matched parent | `:287-296` |
| Root's own attributes never enter the score | `own_attr` at `:525`, unused in `node_score` at `:522` |
| Each reference child contributes 1/N regardless of subtree size | `:515` |
| Nested lists fall back to string compare (whitespace-sensitive) | `_parse_list` `:169-177` |
| α = 0.3, β = 0.1, `NUMERIC_RTOL = 1e-6`, `IGNORE_TAGS = {Problem, Included, File}` | `:41, :52-53, :39` |
| Reference-side branch only (`if gt_grandchildren:`) — a reference **leaf** is scored with plain `attr_similarity` even when its candidate counterpart has children | `:483-491` (J1 §1) |

**The defect (B §6).** `_bipartite_match` appends a candidate pair only when
`compute_element_similarity` is **strictly > 0** (`:283`). For an unnamed container the similarity
collapses to `matched_non_name_attrs / │union \ {name}│ × 0.6`, so a reference `<Solvers>` with no
attributes against a candidate `<Solvers gravityVector="{0,0,-9.81}">` scores exactly 0, is never
paired, and the element **plus its whole subtree** scores 0. 31/90 held-out decks affected, worst
for SE (12/30) — i.e. the defect **understates** the reported SIGA advantage.

## 2. Conventions I am holding fixed (each with the line that justifies it)

| Convention | Justification |
|---|---|
| Scores read from `_summary.json` → `results[]`, never by globbing `*_eval.json` | sprint rule; `F0_s3_ExampleProppantTest` is exactly the run globbing drops (B §2 anomaly 1) |
| **failures-as-zero**: divide by `n_total`, not `n_scored` | paper's declared convention, `writing/neurips/neurips_2026.tex:169`; produced in `judge_geos.py:821/856/869` returning `score 0.0` |
| Cell mean = **mean of per-seed means**; σ = **sample** std (ddof=1) | reproduces all 11 Table-1 val cells exactly (`P0_f3_recompute.py`, verified ×2 by P0 and D) |
| A run scores 0 iff `load_and_resolve_dir` raises **now** — plus a `frozen_failures` variant in which any run whose *published* treesim is null is forced to 0 in every mode | I originally planned to freeze the published failure set so the comparison could not smuggle in a parse/staging fix. §3.1 showed that would have **hidden** a real harness bug: 3 of the 4 published val failures are decks the scorer read before the agent finished writing them. So I report both conventions and split every val delta into a *race* component and a *fix* component. Held-out is unaffected either way. |
| Reference and candidate directories taken from the **`gt_dir` / `gen_dir` recorded in each result row** | byte-identical input to what the published scorer saw; no path reconstruction |
| Cell identity map `F8 = S+X+M`, `F11 = SE-prose` | PROVENANCE #1d, verified by matching recomputed mean+σ to Table 1 |

## 3. Bit-exact reproduction — PASSES on held-out, and it caught a SIXTH harness bug on val

`K2_scorer.py --verify --mode strict` re-scores every run from the reference and candidate
directories recorded in `_summary.json` → `results[]` (`gt_dir` / `gen_dir`) and compares to the
published `treesim` at 1e-9.

```
verify[heldout,strict]: n=180 ok=179 mismatch=0 null_published=1 worst_abs_diff=0.00e+00
verify[val,strict]:     n=561 ok=557 mismatch=2 null_published=2 worst_abs_diff=4.81e-01
```

**Held-out: 179/179 scorable runs bit-exact, worst absolute difference 0.00e+00.** This is a
strictly stronger reproduction than J1's (`ok=89`, 3 cells) — 6 cells, all 180 runs. The one
`null_published` is `F0_s3_ExampleProppantTest`, whose deck genuinely does not parse
(`ValueError: Failed to parse XMLs … not well-formed (invalid token): line 4, column 21`); my
loader raises the same error, so it stays 0 exactly as published.

**Cross-implementation check.** Against J1's independently written `J1_treesim.py`, on all 179
held-out decks, in *both* modes:

```
K2 admit_zero vs J1 soft_match: ok=179 diff=0 worst=0.00e+00
K2 strict     vs J1 hard_match: ok=179 diff=0 worst=0.00e+00
```

Two independent re-implementations of `tree_sim` and of the fix agree to the last digit.

### 3.1 The two val mismatches are NOT a scorer defect — they are a scoring/campaign race

| run | published | strict re-score | published `gen_sections` | current `gen_sections` |
|---|---:|---:|---:|---:|
| `F3_s1_ExampleIsothermalLeakyWell` | 0.7032 | **0.8610** | 9 sections | 11 |
| `F3_s1_TutorialPoroelasticity` | 0.2371 | **0.7185** | 6 sections | 25 |

The reference decks are unchanged (I re-resolved both and reproduced the published `gt_sections`
exactly, including `TutorialPoroelasticity`'s duplicated sections from two entry files). The
*candidate* decks changed. `scripts/eval/batch_evaluate.py:203` writes `_summary.json`'s
`timestamp` with `datetime.now()` **after** the loop, so it is when scoring FINISHED, and tasks are
scored in sorted order (`:172`). Timeline:

```
F3_s1 _summary.json timestamp        14:25:28.976
ExampleIsothermalLeakyWell  base     14:25:22.364   <- scored
                            benchmark 14:25:51.507  <- WRITTEN 23 s AFTER SCORING FINISHED
TutorialPoroelasticity      base     14:25:18.377
                            smoke     14:25:41.863  <- after
                            benchmark 14:25:51.147  <- after
TutorialSneddon             all 7 files 14:30:01 - 14:32:37  <- 4.5 min after
```

`F3_s1_TutorialSneddon` is published as a **hard failure** (`FileNotFoundError: No XML files
found`) and therefore scores 0 under failures-as-zero — but the deck exists, has 7 XML files, and
scores **0.8993**. It was simply not written yet when the scorer looked.

A systematic mtime audit over all 73 run-cells (`max(mtime of *.xml) > summary timestamp`) found
exactly one more, in a different cell:

| run | published | strict re-score |
|---|---|---:|
| `F11_s2_pknViscosityDominated` | **failure** (`n_failed=1`, treesim null) | **0.9795** |

Its two XMLs are dated 11:40:33 and 11:40:53 against a summary timestamp of 11:40:10.

**So three of the four published val "failures" are a harness race, not model failures.** That is
harness bug #6 of this sprint and, like the previous five, it biases toward a conclusion we like —
it manufactures catastrophic zeros in two low-scoring cells (R+S and SE-prose). It is a *different*
bug from K1's external-asset staging bug (that one is about GEOS execution on held-out; this one is
about the val scoring pass racing the val campaign).

**Consequence for this thread.** I now report **three** columns, not two, so the two effects never
get folded together:

| column | what it is |
|---|---|
| `published` | `_summary.json` — exactly what Table 1 prints |
| `strict` | K2 scorer, published matcher, current disk — differs from `published` on 3 val runs only |
| `admit_zero` / `structural` | K2 scorer with the fix, current disk |

**race effect = strict − published** · **FIX effect = admit_zero − strict.** Held-out is unaffected
(`published == strict` on all 180 runs), so every held-out number in this thread is a pure
fix effect.

I also report a **frozen-failure-set** variant in `K2_comparison.json`
(`*_cells_frozen_failures`) in which any run whose *published* treesim is null is forced to 0 in
every mode. That variant isolates the matching fix from the race correction completely.

I did **not** stop, because the mission's stop condition is an unvalidated *re-scorer*, and the
re-scorer is validated: 179/179 held-out and 557/559 val bit-exact, with the two exceptions
explained by file mtimes and content diffs rather than by arithmetic.

## 4. The fix — precise diff

`_bipartite_match` (`judge_geos.py:278-296`) is unchanged up to and including the greedy
positive-similarity pass. The fix appends one block before the `unmatched_*` lists are formed:

```python
# judge_geos.py:283 --  if sim > 0:  -- is THE DEFECT: same-tag pairs whose
# compute_element_similarity is exactly 0 never enter `scores`, so the reference element
# and its whole subtree are scored 0.

# --- K2 fix, mode="admit_zero" (3 lines) -----------------------------------
left_gt  = [i for i in range(n_gt)  if i not in used_gt]
left_gen = [j for j in range(n_gen) if j not in used_gen]
for i, j in zip(left_gt, left_gen):          # document order
    matched.append((i, j, 0.0)); used_gt.add(i); used_gen.add(j)
```

Properties, all verified rather than asserted:

1. **It is a strict superset of the published matching.** The positive-similarity pass runs first,
   unmodified; only its leftovers are considered. No pair the published matcher forms is removed.
   Empirically: the score **never decreases** — 0 of 741 runs went down, 187 went up.
2. **A newly paired element gets no credit for its own attributes.** `compute_element_similarity`
   returns 0 only when the non-name key union is non-empty, no non-name attribute matches, and the
   two `name`s are not both present and equal. `attr_similarity`'s numerator counts exactly the
   keys that are in both with equivalent values, `name` included — so it is 0 for every leftover
   pair. The gain is therefore **entirely** (a) `(1−α)·subtree_score = 0.7 × subtree` recovered on
   interior elements and (b) the removed `extra_penalty`. A newly paired reference **leaf** still
   scores exactly 0. This is what bounds the fix: it cannot hand out arbitrary attribute credit.
3. It is **deterministic**, needs no model, and costs 12 s for 180 decks / 21 s for 561.

### 4.1 The second candidate fix — and it makes no difference

Mission asked whether the right fix is to admit zero-similarity pairs on tag+position, or to fall
back to *structural* matching when attribute similarity is 0. I implemented both:

| mode | leftover pairing rule |
|---|---|
| `admit_zero` | document order (J1's rung R2a) |
| `structural` | greedy by child-tag-multiset Jaccard, ties → lowest index |

**They are bit-identical on all 741 runs** (`admit_zero_equals_structural: true` for both splits).
Reason, measured: 41 % of leftover opportunities are 1×1 (a single unnamed container such as
`<Solvers>`), where ordering is vacuous; in the multi-element cases the leftovers are *leaves*
(e.g. three `TableFunction`s), whose child-tag bags are all empty, so structural similarity is 1.0
for every pair and the index tie-break reproduces document order. **The choice of primary is
therefore not a judgment call.** I report `admit_zero` as primary because it is the smaller change
and the one J1 already evaluated.

I also evaluated the aggressive reading, `structural_global`, in which a structural term enters the
**main** greedy pass and can re-order pairs the published matcher already formed. It is **worse**:
mean held-out delta +0.0258 vs +0.0265, and on `F6_s1_ExampleIsothermalLeakyWell` it destroys the
fix's benefit entirely (0.6314 → 0.6314 instead of → 0.6397) by mis-pairing a container that the
published matcher had matched correctly. **Rejected**: it perturbs matches that are not defective.

### 4.2 Worked case — thread B's canonical trigger, before and after

`ExampleProppantTest`, reference `<Solvers>` (no attributes) vs candidate
`<Solvers gravityVector="{ 0.0, 0.0, -9.81 }">`:

| deck | `Solvers` section | deck TreeSim | ref elements rescued |
|---|---|---:|---:|
| `F0_s1_ExampleProppantTest` | 0.0 → **0.6737** | 0.8065 → **0.8914** | 10 |
| `SE_s1_ExampleProppantTest` | 0.0 → **0.6796** | 0.8193 → **0.9048** | 10 |
| `F0_s1_ExampleIsothermalHystInjection` | 0.0 → 0.6132 | 0.7478 → 0.8312 | 19 |
| `SE_s1_ExampleIsothermalHystInjection` | 0.0 → 0.6122 | 0.7279 → 0.8081 | 19 |

Note the section does **not** go to 1.0 — the container's own attribute score is still 0 (property
2 above) and the subtree still has real errors. The fix removes a cliff; it does not hand out marks.

## 5. Results — old vs new

Full sorted table: **`artifacts/K2_comparison_table.md`** (52 rows + a σ-ratio block, generated by
`K2_make_table.py` from `K2_comparison.json`, so no number is hand-transcribed).
Per-run dumps: `K2_rescored_val.jsonl` (561 rows), `K2_rescored_heldout.jsonl` (180 rows), each
carrying all four modes, per-section scores, and the fix's own diagnostics.

### 5.1 Held-out — everything rises, and SE rises most

| cell | published | **fixed** | Δ | Δ vs Vanilla (published → fixed) |
|---|---:|---:|---:|---|
| Vanilla | 0.7196 ± 0.0809 | **0.7447 ± 0.0898** | +0.0251 | — |
| X+M | 0.7683 ± 0.0054 | **0.7960 ± 0.0018** | +0.0277 | +0.0487 → +0.0513 |
| S+X | 0.7814 ± 0.0018 | **0.8048 ± 0.0074** | +0.0234 | +0.0618 → +0.0601 |
| S+X+M | 0.7827 ± 0.0215 | **0.8028 ± 0.0161** | +0.0201 | +0.0631 → +0.0581 |
| SE-prose | 0.7749 ± 0.0242 | **0.8030 ± 0.0221** | +0.0281 | +0.0552 → +0.0583 |
| **SE** | 0.7891 ± 0.0123 | **0.8227 ± 0.0105** | **+0.0336** | **+0.0695 → +0.0780** |

The fix is monotone: **0 of 741 runs went down**, 187 went up (116 val, 71 held-out). That is not
luck, it is §4 property 1 plus property 2 — a strict superset of the published matching, where new
pairs earn only subtree credit and a removed hallucination penalty.

### 5.2 H28 — does the cell contrast survive? YES, and it widens, but not significantly

Percentile bootstrap, **n_boot = 20 000**, `random.Random(31642)`, resampling **tasks** (10) with
all 3 seeds retained, per-seed means then mean of seed means — the same resample used for both
modes so the change is paired.

| | Vanilla → SE | 95 % CI | 90 % CI | P(Δ ≤ 0) |
|---|---:|---|---|---:|
| published | +0.0695 | [−0.0078, +0.1672] | [+0.0005, +0.1513] | 0.0476 |
| **fixed** | **+0.0780** | [−0.0043, +0.1866] | [+0.0018, +0.1677] | **0.0426** |
| **change (paired)** | **+0.0086** | **[−0.0037, +0.0217]** | [−0.0015, +0.0193] | 0.0904 |

**The contrast survives and widens by +0.0086, exactly the predicted direction — but the change's
own 95 % interval includes zero.** So "fixing it widens the gap" is a point estimate, not a
demonstrated effect. The contrast's own significance barely moves (P 0.048 → 0.043).

### 5.3 Reported loudly, because it cuts against us: three things get WORSE

**(a) Only the SE contrast widens. Two SIGA contrasts narrow, and two lose nominal significance.**

| contrast | published Δ (P≤0) | fixed Δ (P≤0) | change |
|---|---|---|---:|
| Vanilla → SE | +0.0695 (**0.048**) | +0.0780 (**0.043**) | +0.0086 |
| Vanilla → SE-prose | +0.0552 (0.111) | +0.0583 (0.119) | +0.0031 |
| Vanilla → X+M | +0.0487 (0.107) | +0.0513 (0.108) | +0.0027 |
| Vanilla → S+X | +0.0618 (**0.042**) | +0.0601 (0.090) | **−0.0017** |
| Vanilla → S+X+M | +0.0631 (**0.045**) | +0.0581 (0.090) | **−0.0049** |

Thread B's inference — *the defect is worst for SE, so fixing it should raise SIGA more than
Vanilla* — holds for SE and **fails for S+X and S+X+M**. The mechanism is that Vanilla gains
+0.0251 from the fix, which is more than S+X (+0.0234) or S+X+M (+0.0201) gain. **S+X and S+X+M
both cross from P ≈ 0.04 to P ≈ 0.09**, i.e. from nominally-significant-at-5 %-one-sided to not.

**(b) The σ-collapse claim moves to a different cell.** This is the most consequential change in
the whole thread and it is not in the mission brief.

| cell | published σ (ratio vs Vanilla) | **fixed σ (ratio)** |
|---|---|---|
| Vanilla | 0.0809 (1×) | **0.0898 (1×)** — *worse* |
| X+M | 0.0054 (15.1× σ, 227× var) | **0.0018 (49.0× σ, 2400× var)** |
| **S+X** | **0.0018 (44.5× σ, 1984× var)** | **0.0074 (12.1× σ, 147× var)** |
| S+X+M | 0.0215 (3.8×) | **0.0161 (5.6×)** |
| SE-prose | 0.0242 (3.3×) | **0.0221 (4.1×)** |
| SE | 0.0123 (6.6× σ, 43× var) | **0.0105 (8.5× σ, 73× var)** |

The abstract's "roughly $40\times$ lower across-seed variance" is the **S+X σ ratio of 44.5×**
(PROVENANCE #7 / forbidden-pairing note). Under the corrected scorer **S+X's σ ratio falls to
12.1×** and the largest ratio becomes **X+M at 49.0×**. Vanilla's own σ *rises* (0.0809 → 0.0898)
because the fix lifts seeds 1 and 2 (0.7406 → 0.7670, 0.7880 → 0.8212) far more than seed 3
(0.6303 → 0.6458), whose score is dominated by the genuinely unparseable `ExampleProppantTest`
deck that the fix cannot touch. **So "≈40×" survives only by silently switching which cell carries
it.** If the corrected numbers are ever used, that sentence must be rewritten, not re-cited.

**(c) rung-3 `r_pb` gets significantly worse.** AUC improves as J1 reported, but the
point-biserial correlation *degrades* and its interval **excludes** zero:

| metric (90 decks, `rung3_lenient`, 62 pass / 28 fail) | published | **fixed** | Δ (90 % CI) |
|---|---:|---:|---|
| ROC AUC | 0.8036 | **0.8298** | +0.0262 [−0.0062, +0.0622] — crosses 0 |
| r_pb | 0.3944 | **0.3697** | **−0.0247 [−0.0479, −0.0020] — excludes 0** |
| mean(pass) | 0.8427 | 0.8660 | |
| mean(fail) | 0.5877 | 0.6241 | |

The reason is visible in the last two rows: the fix raises failing decks (+0.0364) slightly more
than passing decks (+0.0233), compressing the gap in absolute terms while improving the *ordering*.
On all 6 cells (180 decks, 127 pass) AUC goes 0.7347 → 0.7582.

### 5.4 Independent confirmation of J1's two headline deterministic numbers

| J1 claim | J1 value | K2 value | agreement |
|---|---|---|---|
| annihilation subgroup mean, R2a | 0.661 → 0.727 | **0.6636 → 0.7268** (n = 75 of 179, 6 cells) | ✓ |
| rung-3 AUC, R2a | 0.803 → 0.830 | **0.8036 → 0.8298** | ✓ |
| rung-3 r_pb, R2a | 0.3944 → 0.3697 | **0.3944 → 0.3697** | ✓ exact |

Reproduced with a separately written scorer and a separately written aggregator, and additionally
bit-exact against `J1_treesim.py` itself (§3). J1's numbers stand.

Held-out annihilation subgroup by cell (decks losing ≥1 container plus subtree, out of 30 each):
**Vanilla 10 · X+M 13 · S+X 12 · S+X+M 12 · SE-prose 14 · SE 14** — consistent with thread B's
10/9/12 for F0/F6/SE at the stricter "annihilation event" definition, and again worst for the SE
cells. Val: 106 of 561 runs, and there the *worst-hit* cells are the RAG ones (R+S 15, R+S+X+M 13,
R+M 11, R+X 10) — the defect is not SIGA-specific.

### 5.5 Val cells and the Resolution-IV main effects — the race dominates, not the fix

| cell | printed | published | strict (race-fixed) | **fixed** | of which FIX |
|---|---|---:|---:|---:|---:|
| Vanilla | 0.910 ± 0.024 | 0.9096 ± 0.0236 | 0.9096 ± 0.0236 | **0.9134 ± 0.0239** | +0.0038 |
| R+M | 0.885 ± 0.014 | 0.8848 ± 0.0136 | 0.8848 ± 0.0136 | **0.8876 ± 0.0136** | +0.0028 |
| S+M | 0.919 ± 0.004 | 0.9191 ± 0.0037 | 0.9191 ± 0.0037 | **0.9239 ± 0.0034** | +0.0048 |
| **R+S** | 0.857 ± 0.045 | 0.8567 ± 0.0449 | **0.8869 ± 0.0110** | **0.8899 ± 0.0106** | +0.0030 |
| X+M | 0.921 ± 0.007 | 0.9214 ± 0.0071 | 0.9214 ± 0.0071 | **0.9291 ± 0.0075** | +0.0077 |
| R+X | 0.893 ± 0.033 | 0.8928 ± 0.0329 | 0.8928 ± 0.0329 | **0.8958 ± 0.0334** | +0.0030 |
| S+X | 0.917 ± 0.004 | 0.9166 ± 0.0038 | 0.9166 ± 0.0038 | **0.9218 ± 0.0019** | +0.0052 |
| R+S+X+M | 0.885 ± 0.008 | 0.8853 ± 0.0083 | 0.8853 ± 0.0083 | **0.8896 ± 0.0074** | +0.0044 |
| S+X+M | 0.911 ± 0.018 | 0.9110 ± 0.0180 | 0.9110 ± 0.0180 | **0.9175 ± 0.0162** | +0.0065 |
| **SE-prose** | 0.897 ± 0.032 | 0.8965 ± 0.0316 | **0.9158 ± 0.0168** | **0.9209 ± 0.0146** | +0.0051 |
| SE | 0.919 ± 0.020 | 0.9191 ± 0.0201 | 0.9191 ± 0.0201 | **0.9238 ± 0.0197** | +0.0047 |

All 11 published values reproduce Table 1 to 3 dp. The fix moves every val cell by +0.003 to
+0.008 — small and almost common-mode, so **the val ordering and the "cells cluster within seed
noise" story are unchanged**. The two large val moves are the **race**, not the fix: R+S
+0.0302 (σ 0.045 → 0.011) and SE-prose +0.0192 (σ 0.032 → 0.017).

**Resolution-IV main effects (val, F0–F7):**

| source | R | S | X | M |
|---|---:|---:|---:|---:|
| printed appendix (stale, drop-nulls) `tex:412` | −0.032 | −0.003 | +0.007 | +0.004 |
| corrected convention (PROVENANCE #1b) | −0.037 | −0.008 | +0.011 | +0.008 |
| **published, recomputed here** | **−0.0368** | **−0.0077** | **+0.0115** | **+0.0087** |
| **strict, race-corrected** | −0.0292 | **−0.0002** | **+0.0039** | **+0.0012** |
| **fixed (race + matching)** | **−0.0313** | **−0.0002** | **+0.0054** | **+0.0023** |

My recomputation of the *published* effects matches PROVENANCE #1b to 4 dp, confirming that chain.
But **the R+S race artifact accounts for ±0.0075 of every one of the four published main effects**
(F3 is R=1,S=1,X=0,M=0, so a +0.0302 shift on one of four cells per group moves each effect by
exactly 0.0302/4). Correcting it:

* **S goes from −0.008 to −0.0002** — the S main effect essentially vanishes;
* **X goes from +0.011 to +0.004** and **M from +0.009 to +0.001** — both well inside seed noise;
* **R stays the largest and stays negative** (−0.031), so the paper's actual claim — *"the only main
  effect that clearly exceeds run-to-run variability is R, and it is negative"* (`tex:86`,
  `tex:~180`) — **survives and is if anything cleaner.**

The matching fix on its own moves the effects by ≤ 0.002. **The appendix main-effects table is
contaminated by the harness race, not by the metric.**

### 5.6 Strictly perfect decks — completely unmoved

| split | published | fixed |
|---|---|---|
| val /51 | Vanilla 7 · R+M 1 · S+M 4 · R+S 3 · X+M 6 · R+X 3 · S+X 6 · R+S+X+M 5 · S+X+M 7 · SE-prose 4 · **SE 7** | **identical, every cell** |
| held-out /30 | Vanilla 2 · X+M 1 · S+X 0 · S+X+M 0 · SE-prose 2 · SE 2 | **identical, every cell** |

The paper prints Vanilla 7/51, X+M 6/51, SE 6/51 (`tex:216`). **SE is 7/51, confirming thread D**
— that is a pre-existing transcription error, not something the fix causes. The fix creates
**zero** new perfect decks, in either split, in any cell: property 2 of §4 guarantees a newly
paired element cannot reach 1.0 (its own attribute score is 0 by construction). So the paper's
claim (4) *"strictly perfect tasks do not increase under any adapter"* and the discussion's *"the
count of strictly perfect decks is unmoved by any configuration we tried"* are **robust to the
re-score**, and gain a second reading: they are unmoved by fixing the metric either.

## 6. Dead ends and things I checked that went nowhere

* **`structural` matching as a distinct fix.** Bit-identical to `admit_zero` on all 741 runs (§4.1).
  Two hours of design, zero measurable difference. Worth it only because it removes a judgment call.
* **`structural_global`** (structural term in the main greedy pass). Strictly worse and it perturbs
  correct matches. Rejected; kept in the scorer behind a flag and in the dumps for auditability.
* **Freezing the published failure set** as the only convention. Would have concealed harness bug #6.
  Kept as a secondary variant (`*_cells_frozen_failures` in `K2_comparison.json`).
* **Recursing into reference leaves whose candidate has children.** J1 documented this trap; I read
  `judge_geos.py:483-491` first and branched on the reference side only, so my first `--verify` pass
  was clean on the `TutorialHydraulicFractureWithAdvancedXML` decks that cost J1 a debugging cycle.
* **mtime audit over all 73 run-cells.** Two of the five hits were benign (files in a
  `triaxialDriver/` subdirectory that `rglob` finds and my audit's `glob` did not; one late write
  that did not change the score). The other three are harness bug #6.

## 7. Open items for a human

1. **H28 verdict: fixing the metric does not endanger the headline contrast, but it is not a free
   win either.** Vanilla→SE widens +0.0695 → +0.0780; S+X and S+X+M *narrow* and lose nominal
   significance; the "≈40×" σ claim changes cell. Recommendation unchanged from thread B —
   **disclose, do not re-score for the response** — but now with the corrected numbers in hand.
2. **Harness bug #6 (val scoring/campaign race) is independent of this thread and needs a decision.**
   It inflates the published S, X and M main effects by 0.0075 each and manufactures 3 of the 4
   published val failures. R+S is really 0.887 ± 0.011, not 0.857 ± 0.045. Nothing in a draft
   currently depends on R+S or SE-prose val numbers, but the appendix main-effects table does.
3. **`tex:216` prints SE 6/51 strictly perfect; it is 7/51.** Independently confirmed here and by
   thread D. Pre-existing, unrelated to the fix.
4. **Which σ number the abstract quotes.** Under the corrected scorer the max σ ratio is X+M's 49×,
   not S+X's 44.5×. Any camera-ready re-score must re-pick the cell explicitly and say so.

## 8. Cross-thread checks and dependencies

**Against thread D** (`artifacts/D_recomputed.json`, independent script, independent author): my
`published` column reproduces D's `mean_fz` for all 11 val cells and all 6 held-out cells to 4 dp
(e.g. held-out F0 0.7196333 / F4 0.7682933 / F6 0.78142 / F8 0.7826867 / F11 0.7748733 / SE 0.7891;
val F0 0.9095863, F3 0.8567196). So the "old" side of every comparison in this thread is the same
"old" that D and P0 both verified against Table 1.

**Against thread J1**: bit-exact in both modes on all 179 held-out decks (§3), plus the three
headline R2a numbers reproduced (§5.4).

**Dependency on K1 (running concurrently).** The rung-3 ground truth here is
`artifacts/A1_rung3_corrected_by_taskrun.csv`, column `rung3_lenient` (62 pass / 28 fail on
F0/F6/SE — the exact labels J1 used, so the AUC comparison is like-for-like). K1 is re-deriving
rung 1–3 with the external-asset staging fix. **If K1's labels move, the AUC numbers in §5.3 must be
recomputed** — `K2_analyse.py`'s `rung3()` takes `csv_name` and `label_col` arguments precisely so
that is a one-line change. The TreeSim re-score itself does not depend on K1 at all.

**No API spend. No writes outside `neurips_review/sprint/{threads,artifacts}`. `src/eval/judge_geos.py`
verified unmodified (`git diff --stat` empty, md5 `ced8b1153fc95450f53e1c804dc1a8ae`).**
