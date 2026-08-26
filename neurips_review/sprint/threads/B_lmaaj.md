# Thread B — LMaaJ secondary metric (input side)

Submission 31642 (SIGA), NeurIPS 2026 author response. Started 2026-07-26T22:02:09+00:00.

Spec: `neurips_review/prompts/01_lmaaj_metric.md`. Frame: `SIGA_rebuttal_execution_plan.md` §4, §6.

**Mission in one line:** TreeSim's `rtol = 1e-6` is effectively exact equality, so it has no
notion of *how wrong* a wrong value is. The judge supplies the magnitude-and-plausibility
dimension. Everything below serves that.

---

## 1. Verification of `src/eval/judge_geos.py` (read end to end, 933 lines)

The description in the execution plan §4.4 and in the session prompt is **mostly accurate but
conflates two different functions**. Corrections below; the rebuttal should not quote §4.4 as
written.

### Confirmed as stated

| Claim | Verdict | Evidence |
|---|---|---|
| Resolves XML includes | **Correct** | `_resolve_included` (l.62), `load_and_resolve_dir` (l.112). Also cycle-safe via `_ancestors`, and skips non-existent include targets silently. |
| Penalizes hallucinated elements, β = 0.1 | **Correct** | `TREESIM_BETA = 0.1` (l.53); `extra_penalty = beta * (total_extra / (n_gt + total_extra))` (l.520). Max penalty is 0.1, applied per node. |
| α = 0.3 weights own-attributes vs subtree for interior nodes | **Correct** | `TREESIM_ALPHA = 0.3` (l.52); `child_score = alpha * a_score + (1 - alpha) * subtree_score` (l.486), taken when the GT child has non-ignored children. |
| `values_equivalent` parses scalars and float lists, numeric compare at `NUMERIC_RTOL = 1e-6`, case-insensitive string fallback | **Correct** | l.180–199. Exact-string fast path first, then scalar, then equal-length float list (recursive), then `left.lower() == right.lower()`. |
| `1e6`, `1000000`, `1.0e+06` all match | **Correct** | `_SCALAR_RE` (l.55) accepts all three; `float()` then relative compare. |
| rtol = 1e-6 ⇒ effectively exact equality, no notion of how wrong | **Correct, and this is the real gap** | `abs(n1-n2)/max(|n1|,|n2|) <= 1e-6`. A 2× error and an 18-orders-of-magnitude error both score 0 on that attribute. |

### CORRECTION 1 — "tag match + name bonus (0.4) + attribute-value overlap" is the *matcher*, not the *scorer*

Two distinct functions exist and the plan's sentence merges them:

- `compute_element_similarity` (l.219) — has the tag gate, the **0.4 `name` bonus**, and
  `attr_score = matched / |union \ {name}| * 0.6`. This is used **only** inside
  `_bipartite_match` to decide *which* generated element pairs with *which* reference element.
  It never enters the headline number.
- `attr_similarity` (l.396) — what actually contributes to TreeSim:
  `|matching attrs| / |union of attrs|`, **no name bonus, no 0.6 scaling, and `name` IS
  included in the union**. Returns 1.0 vacuously when neither element has attributes.

So the accurate sentence is: *"TreeSim pairs elements with a similarity heuristic that gates on
tag equality and gives a 0.4 bonus for an exact `name` match; the score it then reports for each
paired element is the plain Jaccard-style ratio of exactly-matching attributes over the union of
attribute keys."* Quoting the 0.4/0.6 constants as if they were scoring weights is wrong and a
reviewer reading the source would catch it.

### CORRECTION 2 — bipartite matching is **greedy**, not optimal

`_bipartite_match` (l.256) sorts all positive-similarity pairs descending and takes them
greedily. The docstring concedes this ("exact Hungarian is overkill"). Matching is also
**local**: only among same-tag siblings under an already-matched parent, so a correct element
placed under the wrong parent cannot be recovered. Say "greedy bipartite matching over same-tag
siblings," not "bipartite-matches elements."

### CORRECTION 3 — the root element's own attributes never enter the score

At the top-level `tree_sim(gt_root, gen_root)` call, `own_attr` is computed (l.525) and stored in
the detail record, but `node_score` is `matched_score - extra_penalty` only (l.522). `<Problem>`
attributes are therefore ignored. Harmless here (`Problem` carries only xmlns noise) but the
`alpha` blend genuinely does not apply at the root.

### CORRECTION 4 — each reference child contributes 1/N regardless of subtree size

`matched_score = sum(child_scores) / n_gt` (l.515). A one-line leaf sibling and an entire
`<Solvers>` subtree at the same level carry equal weight. This is a design choice, not a bug,
but it means TreeSim is **not** an element-count-weighted similarity, and per-section scores are
not size-weighted either. Worth knowing before anyone claims TreeSim "measures the fraction of
the deck that is correct."

### Discrepancies worth logging as latent defects (not load-bearing for the rebuttal)

- **Nested lists fall back to string comparison.** `_parse_list` (l.169) does
  `.strip().strip("{").strip("}")` then splits on `,`. For a GEOS nested list like
  `{ {0,0,0}, {1,1,1} }` the inner braces survive as tokens (`"0}"`, `"{1"`), `_parse_scalar`
  returns `None`, so the list path fails and it falls through to `left.lower() == right.lower()`.
  **Consequence: for nested-list attributes (`xCoords`, `nodeSets`, `Box` bounds), TreeSim is
  whitespace-sensitive** — `{{0,0,0}}` and `{ {0, 0, 0} }` are scored as a mismatch. This is a
  real source of spurious mismatches and is exactly the "cosmetic vs material" call the judge is
  being asked to make.
- **A reference leaf whose generated counterpart has spurious children loses attribute scoring
  entirely.** The leaf branch at l.449 requires `n_gt == 0 AND len(gen_children) == 0`. If the
  generated element has children, control falls to the grouping branch with `n_gt == 0`, so
  `matched_score = 1.0`, `extra_penalty = 0.1`, and the node scores a flat **0.9 no matter how
  wrong its attributes are**.
- **`n_matched` in `TreeSimDetail` is unreliable** (l.531): `len(child_scores) - count(s == 0.0)`
  conflates "unmatched" with "matched but scored exactly zero." Diagnostic only.
- `_parse_scalar` rejects `.5` (no leading digit), `inf`, `nan`. Such values fall to string
  comparison.

**Net effect on the rebuttal argument: unchanged and slightly strengthened.** Every correction
above makes TreeSim *more* structural and *more* brittle to cosmetic variation than §4.4 claims,
which is the premise the LMaaJ metric is built on. But §4.4's specific sentence must be rewritten
before it is quoted, because two of its three scoring constants belong to the matcher.

---

## 2. Data reconnaissance

Held-out ICL results, per `_results_icl/*/*/*_eval.json` (`treesim` is a top-level key, not under
`metrics` — the `metrics.*` schema in `evaluate_geos()` is the *runner* wrapper; these files are
raw `evaluate_directories()` output).

Reference decks: the eval JSONs record `gt_dir = /data/shared/geophysics_agent_data/data/eval/experiments_gt/<task>/inputs`,
**not** `/home/matt/sci/repo3/data/GEOS/inputFiles/` as the brief stated. Using the recorded
`gt_dir` so the judge sees byte-identical reference input to what TreeSim scored.

Generated decks: `icl/autocamp_<CELL>/<CELL>_icl_s<N>/<task>/inputs/*.xml` (brief said
`<cell>/<cell>_icl_s<N>` — the outer dir is `autocamp_F6`, the inner is `F6_icl_s1`).

### Held-out TreeSim, recomputed from raw (10 tasks × 3 seeds)

| Cell | s1 | s2 | s3 | mean | sd(seeds) |
|---|---:|---:|---:|---:|---:|
| F0 Vanilla | 0.7406 | 0.7880 | 0.6303 | **0.7196** | 0.0809 |
| F4 X+M | 0.7624 | 0.7730 | 0.7695 | 0.7683 | 0.0054 |
| **F6 S+X** | 0.7799 | 0.7809 | 0.7834 | **0.7814** | 0.0018 |
| F8 | 0.8022 | 0.7862 | 0.7597 | 0.7827 | 0.0215 |
| F11 | 0.7472 | 0.7924 | 0.7850 | 0.7749 | 0.0242 |
| SE | 0.7972 | 0.7952 | 0.7749 | **0.7891** | 0.0123 |

Reproduces the plan's headline σ 0.081 → 0.002 (F0 → F6) and both rescue tasks
(`AdvancedExampleThermoPoroElasticWellbore` 0.355 → 0.761, `ExampleProppantTest` 0.541 → 0.825).

**DECISION — best combo = `autocamp_F6` (S+X).** F6 mean 0.7814 > F4 mean 0.7683 on held-out
(Δ = +0.013), and F6's seed sd is 0.0018 vs F4's 0.0054. F6 is stronger on *both* level and
stability, so it is the honest choice of "best combo" and it is also the cell that carries the
σ-collapse claim. Recorded before any judge call, so this is not a post-hoc pick.

### Data anomalies found

1. **`F0_icl_s3/ExampleProppantTest` has no `_eval.json`** (179 eval files, not 180). The deck
   *does* exist on disk (`inputs/ProppantSlotTest_base.xml`, `ProppantSlotTest_benchmark.xml`),
   so this is a missing *scoring*, not a missing run. Treating it as 0.0 is what produces
   F0_s3 = 0.6303 and hence F0's sd = 0.0809. **This needs checking before the σ 0.081 → 0.002
   number is quoted** — see §3 below. Flagged to the sprint.
2. **`TutorialHydraulicFractureWithAdvancedXML` scores 0.013 for every cell and every seed.**
   A hard floor, identical across conditions. Almost certainly an Advanced-XML
   (`<Parameters>`/`<Included>`) resolution issue rather than an agent failure. It contributes
   ~0.099 of depression to every cell's mean equally, so it does not affect contrasts, but it is
   a per-task outlier the judge will see.

---
## 3. Rubric frozen

`neurips_review/sprint/artifacts/B_rubric_v1.md`
- **Frozen 2026-07-26T22:14:00+00:00**, written and hashed before any judge API call and before
  any judge had seen any deck.
- `sha256 = 6b0e216eb5ff71111eafc1055c752b089b44f4330b012ea2e25070918a4dac8b`
- Verify with: `sha256sum neurips_review/sprint/artifacts/B_rubric_v1.md`

Contains: score dimensions, the four-way severity ladder with **fixed credit weights**
(cosmetic 1.0 / minor 0.7 / material 0.3 / severe 0.0), the blinding rules, the position-swap
design, the aggregation rule (median across judges, then mean over tasks, then mean±sd over
seeds), the rung-1 floor convention, the judge-model list, and **four pre-registered
null/unfavourable conditions**. Not edited after the freeze.

Design note on the credit weights: they turn the judge's per-mismatch labels into a
**magnitude-aware re-score of exactly the attributes TreeSim scored as zero**. TreeSim implicitly
assigns credit 0.0 to every entry in the difference report; `mismatch_credit` is the same
quantity with graded credit. That makes the metric interpretable as "TreeSim plus magnitude
awareness" rather than as a free-floating LLM opinion, which was design requirement 2's whole
point.

## 4. Judge models and the family constraint

Verified from `eval_metadata.json` of every held-out run:
`"claude_model": "deepseek-v4-flash"`, `"anthropic_base_url": "https://api.deepseek.com/anthropic"`,
`"claude_code_version": "2.1.119"` (also confirms plan item 4). So the **scored backbone is
DeepSeek**; Claude Code is only the harness.

| Judge | Family | Why it is clean |
|---|---|---|
| `openai/gpt-5.4-mini` | OpenAI | not DeepSeek, not MiniMax, not the harness vendor |
| `google/gemini-3-flash-preview` | Google | same |
| `moonshotai/kimi-k2.6` | Moonshot AI | same |

Three families. **No DeepSeek judge** (would be disqualifying — it is the scored backbone, and it
is the known flaw in our own LAMMPS study). **No MiniMax judge** (the paper's second scored
backbone). **No Anthropic judge** either: although no Anthropic model is a scored backbone,
Anthropic is the vendor of the Claude Code harness, and excluding it removes the only remaining
same-vendor objection at zero cost. Temperature 0, via OpenRouter (`OPENROUTER_API_KEY` in
`.env`).

## 5. Prompt construction

Script: `neurips_review/sprint/scripts/B_build_prompts.py`

```
python3 neurips_review/sprint/scripts/B_build_prompts.py --out <jsonl> [--cells ...] [--seeds ...] [--tasks ...]
```

- Brief: `/data/shared/geophysics_agent_data/data/eval/experiments_from_mined_specs/<task>/instructions.txt`
  (real natural-language simulation requests, 3.7-6.7 kB each — verified present for all 10 tasks).
- Reference deck: raw XML of `experiments_gt/<task>/inputs/*.xml`.
- Candidate deck: raw XML of `icl/autocamp_<CELL>/<CELL>_icl_s<N>/<task>/inputs/*.xml`.
- Difference report: recomputed with `judge_geos.match_trees` on the **resolved** trees, so the
  judge sees TreeSim's own view. GT/GEN relabelled to REFERENCE/CANDIDATE.
- Blinding: regex strips every filesystem path and every `autocamp_F*`/`*_icl_s*` token; asserted
  over all 90 prompts before any call.
- Decks capped at 26 000 chars each, difference report at 90 entries.

Measured prompt size, smoketest deck: **31 416 chars ≈ 7.9 k tokens**, no truncation.

## 6. FINDING (no LLM required) — TreeSim subtree annihilation

Found while validating the difference report on the smoketest deck. **This is the sharpest result
in this thread and it is fully deterministic.**

`_bipartite_match` (`judge_geos.py:292`) only records pairs whose `compute_element_similarity`
is **strictly greater than zero**. For a container element with **no `name` attribute**,
`compute_element_similarity` reduces to `matched_attrs / |union \ {name}| * 0.6` with no name
bonus. So if the reference container has zero attributes and the candidate container has even
**one** attribute, the ratio is 0/1 → similarity exactly 0.0 → **the two elements are never
paired**, and the reference element plus its entire subtree is scored 0.

Instantiated on `ExampleProppantTest`:

```
REF  <Solvers>                                            attrib {}
CAND <Solvers gravityVector="{ 0.0, 0.0, -9.81 }">        attrib {'gravityVector': ...}
compute_element_similarity(ref, cand) = 0.0
```

The two `<Solvers>` blocks contain **the same four solvers with the same `name` attributes**
(`ProppantTransport`, `FlowProppantTransport`, `SinglePhaseProppantFVM`/`SinglePhaseFVM`,
`SurfaceGenerator`/`SurfaceGen`) and the same nested solver-parameter blocks. TreeSim reports
`treesim_section_scores.Solvers = 0.0` and lists all 10 reference elements as unmatched.

And `gravityVector="{0,0,-9.81}"` is **GEOS's own default**, stated explicitly — and gravity is
the physical mechanism the proppant-settling task is *about*. So the candidate was penalised the
entire `Solvers` section for writing down the correct default value of the most physically
relevant parameter in the problem.

### Prevalence across the held-out set (all 90 decks, deterministic)

| Cell | decks affected | annihilation events | reference elements zeroed |
|---|---:|---:|---:|
| F0 Vanilla | 10 / 30 | 23 | 167 |
| F6 S+X | 9 / 30 | 19 | 137 |
| SE | 12 / 30 | 27 | 186 |

**31 of 90 held-out decks (34 %) lose at least one whole subtree this way.** The dominant trigger
is `cand_only=['gravityVector']` on `<Solvers>`; it fires for every cell and every seed on
`ExampleProppantTest` and `ExampleIsothermalHystInjection`.

Interpretation, stated carefully:
- It is close to **common-mode** (10/9/12 of 30), so it supports §4.3's argument that TreeSim
  depresses the absolute level for every cell roughly equally and leaves the *contrast* intact.
- But it is *not exactly* common-mode, and it is slightly **against** SIGA: SE, the best cell,
  is hit most often (12/30, 186 elements), because SE decks more often add correct-but-absent
  attributes. So the measured SIGA advantage is, if anything, understated by this defect.
- It is a **cliff, not a gradient** — one extra attribute on a name-less container costs an entire
  subtree. This is a stronger and more concrete criticism of TreeSim than magnitude-blindness,
  and unlike the LMaaJ result it requires no LLM and no trust.

Artifact: `neurips_review/sprint/artifacts/B_treesim_annihilation.json` (per-event records).

**Recommendation to the sprint:** this belongs in the response *regardless of how LMaaJ turns
out*. It is a self-reported metric limitation with a measured, bounded, direction-known effect —
exactly the kind of disclosure that buys credibility. It also gives the LMaaJ metric a concrete
job: the judge should label `gravityVector` as `cosmetic`, and if it does, the two metrics
disagree for a reason we can name.

## 7. FINDING — `TutorialHydraulicFractureWithAdvancedXML` is a TreeSim artifact, not an agent failure

The reference deck's raw text is 11 687 chars, but `load_and_resolve_dir` expands it to
**351 085 chars / 3333 elements** — two orders of magnitude more than any other reference deck in
the set (next largest: `TutorialDeadOilEgg`, 407 elements). Advanced-XML `<Included>` expansion
is multiplying the tree. Every generated deck has ~50 elements, so TreeSim ≈ 0.013 for **every
cell and every seed** — an exactly identical floor, which is the signature of a metric artifact
rather than a modelling failure.

It contributes ≈ 0.099 of depression to every cell's held-out mean, identically. Contrasts are
unaffected; absolute levels are understated for all cells alike. Should be disclosed.

Consequence for this thread: the judge sees the **raw** (unresolved) reference text for this task,
which is what a human would read. Disclosed in the rubric.

---

## 8. Smoketest (mandated) — one task, one cell, one seed, raw output inspected

`F6_s1_ExampleProppantTest`, order A, all three judges. Prompt 31 416 chars ≈ 7.9 k tokens.

```
python3 neurips_review/sprint/scripts/B_build_prompts.py --out $SC/smoke.jsonl \
    --cells F6 --seeds 1 --tasks ExampleProppantTest
python3 neurips_review/sprint/scripts/B_run_judges.py --prompts $SC/smoke.jsonl \
    --out $SC/smoke_out.jsonl --orders A
```

### Round 1 result — two defects, both mine

```
gemini3flash  lmaaj=0.907 credit=0.920 pl=9 pf=9   labels: 21 cosmetic, 2 minor, 2 material
gpt54mini     lmaaj=0.500 credit=0.200 pl=7 pf=6   labels: 20 severe, 5 cosmetic
kimik26       FAILED - no JSON object found (finish_reason=length, 6000 output tokens burned)
```

**Defect 1 — my difference report was feeding the judge a false premise.** Because of the
annihilation defect in §6, `match_trees` reports the *same* element on both the `gt_unmatched` and
`gen_unmatched` lists. My report rendered those as two separate entries: one saying "present in
REFERENCE, no counterpart in CANDIDATE" and one saying "present in CANDIDATE, no counterpart in
REFERENCE". Both statements are false — the element exists on both sides.

Per-entry comparison showed the entire gemini/gpt disagreement traced to this:

```
M007  gemini=cosmetic  "Element moved between files, parameters remain identical."
      gpt   =severe    "Newton and timestep-cut controls for the proppant solver are missing..."
M017  gemini=cosmetic  "Duplicate of M007 logic; element moved to base file."
      gpt   =severe    "Requested proppant solver nonlinear controls are absent from the ..."
```

gemini distrusted the report and inspected the decks; gpt believed the report. gemini also
correctly identified that M017-M024 were **duplicates** of M005-M014 (the mirror side of the same
annihilation). 25 reported entries contained ~10 duplicated pairs.

**Fix (a prompt-input bug fix, NOT a rubric change).** `build_mismatch_report` now reconciles the
two unmatched lists: an unmatched reference element and an unmatched candidate element sharing a
tag (and a `name`, when both have one) are emitted as **one** entry of kind `unpaired_same_tag`
that states plainly that the metric failed to pair them, shows **both** attribute dicts, and adds
"the metric's own failure to pair is not itself a defect of the candidate deck." A legend for the
four entry kinds and a note that relocated elements are not functional differences were added.

I want to be explicit about rule 7 here. The frozen rubric — dimensions, the four severity
definitions, the credit weights, the 0-10 scales, the aggregation rule, the null conditions — is
**byte-identical to v1**. What changed is that the prompt no longer asserts something false. This
was found on a single cell (F6) during the smoketest the spec mandates; **no cross-cell comparison
had been computed at that point**, so it cannot have been tuned toward a result. Entry count for
the smoketest deck went 25 → 15.

**Defect 2 — `moonshotai/kimi-k2.6` is not usable as a judge here.** It spent all 6000 permitted
output tokens on prose and emitted no JSON object (`finish_reason=length`), at $0.0221/call — the
most expensive of the three *and* the only failure. Substituted
**`qwen/qwen3-235b-a22b-2507` (Alibaba family)**: still a third distinct family, still not
DeepSeek / MiniMax / Anthropic, and $0.0012/call. Substitution reason is a **technical failure to
emit the required schema**, not its scores — its scores were never obtained.

### Round 2 result — corrected report, three judges, both orders

```
gpt54mini     A lmaaj=0.776 cred=0.827 pl=8  pf=7   |  B lmaaj=0.753 cred=0.760 pl=8  pf=7
gemini3flash  A lmaaj=0.973 cred=0.920 pl=10 pf=10  |  B lmaaj=0.987 cred=0.960 pl=10 pf=10
qwen3235b     A lmaaj=0.964 cred=0.893 pl=10 pf=10  |  B lmaaj=0.987 cred=0.960 pl=10 pf=10
```

Coverage 1.00 for all six (every mismatch id received a valid severity label). Position shift
|A−B| = 0.023 / 0.014 / 0.023. All three judges labelled `gravityVector` on `<Solvers>` as
`cosmetic` or `minor` — i.e. **the judge does the job it was built for**: TreeSim scores that
element and its 10-element subtree at 0.0; all three judges say it is not a real defect.

Compare with the deck's TreeSim of record: **0.8143**.

### Cost calibration from the smoketest

| Judge | input tok | output tok | $/call |
|---|---:|---:|---:|
| `openai/gpt-5.4-mini` | 9 331 | 604 | 0.00972 |
| `google/gemini-3-flash-preview` | 9 994 | 636 | 0.00690 |
| `qwen/qwen3-235b-a22b-2507` | 9 628 | 645 | 0.00122 |

$0.0178 per deck for all three judges, one order. **Projected total: 90 order-A + 30 order-B
deck-passes = $2.14.** Under the "a few dollars" constraint, so proceeding. Costs are recorded
per call in `B_judge_raw.jsonl` (`cost_usd`, computed from OpenRouter list price captured
2026-07-26, not from any provider-reported cost field — cf. the `total_cost_usd` trap in the
DeepSeek cost-accounting memory).

## 9. Blinding audit over all 90 prompts

```
python3 neurips_review/sprint/scripts/B_build_prompts.py --out neurips_review/sprint/artifacts/B_prompts.jsonl
```

90 records, 0 truncated. A crude substring audit flagged 36 apparent `SE_` hits; all were the
**same** false positive — the string `<!-- SPHINX_FIELD_CASE_Co2_SOLVER -->` inside the
*reference* deck for `ExampleIsothermalHystInjection` and
`TutorialHydraulicFractureWithAdvancedXML`, where `CASE_` contains `SE_`. It appears identically
in the F0, F6 and SE prompts for those tasks, so it carries zero condition information. No path,
no `autocamp_*`, no `*_icl_s*` token reaches any prompt.

## 10. FINDING — TreeSim silently tolerates partially unparseable decks

`load_and_resolve_dir` (`judge_geos.py:125`) raises only `if parse_errors and not parsed`. So a
deck in which **some** files fail to parse is scored on the surviving subset, with no penalty and
no flag.

Instantiated, cross-checked against Thread A1's per-file rung-1 results:

```
F0_icl_s1 / AdvancedExampleThermoPoroElasticWellbore
  ThermoPoroElasticWellbore_base.xml       parses
  ThermoPoroElasticWellbore_benchmark.xml  parses
  ThermoPoroElasticWellbore_smoke.xml      NOT well-formed (line 71: double hyphen in comment)
  -> load_and_resolve_dir() succeeds; eval json says status "success", treesim 0.235
```

So this deck contains a file that `xmllint` rejects, and the pipeline recorded it as a successful
scoring run. It only becomes a hard `xml_parse_error` (score 0.0) when **every** file fails, as in
`F0_s3/ExampleProppantTest`.

Direction of the bias: all such cases are in **F0 (Vanilla)**, so TreeSim **under-counts
Vanilla's failures** and the reliability contrast is, if anything, understated. Disclose it; it
does not need fixing for the rebuttal, but nobody should claim TreeSim detects malformed output.

## 11. Execution calibration data pulled from Thread A1 (rungs 1-2)

Source: `neurips_review/sprint/artifacts/A1_rungs12_perfile.csv` (486 per-file rows; A1's
rung-3 sweep was still failing on `shutil.copytree` over broken symlink dirs at the time of
writing — polled, not rebuilt).

Aggregated to deck level (a deck passes a rung only if **every** file in it passes):

| Cell | rung 1 (well-formed) | rung 2 (schema-valid vs GEOS XSD) |
|---|---|---|
| F0 Vanilla | 24 / 30 | 24 / 30 |
| F6 S+X | **30 / 30** | **30 / 30** |
| SE | **30 / 30** | **30 / 30** |

**Every one of the six failures is in F0.** Three are `unparseable` (double hyphen inside an XML
comment — the same failure mode three times, and in one case the agent's final message claimed
the files were "complete and verified against the GEOS XSD schema"), three are `schema_invalid`.

This is a clean binary ground-truth label on 90 decks, and it is the calibration target for
§13.

## 12. Full run — commands, and one operational error

```bash
cd /home/matt/sci/repo3 && source .venv/bin/activate
python3 neurips_review/sprint/scripts/B_build_prompts.py \
    --out neurips_review/sprint/artifacts/B_prompts.jsonl
python3 -u neurips_review/sprint/scripts/B_run_judges.py \
    --prompts neurips_review/sprint/artifacts/B_prompts.jsonl \
    --out    neurips_review/sprint/artifacts/B_judge_raw.jsonl \
    --orders A B --order-b-seeds 1 --workers 8
python3 neurips_review/sprint/scripts/B_analyse.py
python3 neurips_review/sprint/scripts/B_figure.py
```

Expected call count: 89 decks × 3 judges × order A = 267, plus the seed-1 position-bias subsample
30 decks × 3 judges = 90. **357 calls.** (90 decks minus the one rung-1 failure,
`F0_s3_ExampleProppantTest`, which is floored without an API call.)

**Operational error, disclosed.** My first launch used a relative log path from the wrong cwd, so
`tail` on the log failed and I concluded the process had died. It had not. I launched a second
process against the same output file, and the two ran concurrently for several minutes, each
duplicating the other's work. Detected by counting unique `(deck_id, judge, order)` triples:
**377 rows, 205 unique, 172 duplicates.** Both processes ran at temperature 0 against identical
prompts, so no scoring contamination — the duplicates were redundant, not divergent. Killed both,
deduped keeping the first row per triple, relaunched a single process; the runner's resume logic
picked up the remaining 152 calls.

**Wasted spend: ~$1.7 on the 172 duplicate calls.** Reported in the cost section rather than
quietly absorbed.

Realised per-call cost is ~$0.0097, higher than the $0.0059 the smoketest deck projected, because
`ExampleProppantTest` is one of the smaller decks; `AdvancedExampleCasedThermoElasticWellbore` and
`ExampleVerticalPoroElastoPlasticWellbore` are 3-5× larger and produce far longer verdict lists
(up to 106 mismatch entries).

### Analysis script

`neurips_review/sprint/scripts/B_analyse.py` implements the frozen aggregation and computes:
nominal Krippendorff's α and Fleiss' κ over the 4-way severity labels (and over a collapsed
low/high dichotomy), per-judge and judge-pair Pearson/Spearman on per-deck LMaaJ, the order-A vs
order-B position shift per judge, Pearson/Spearman against TreeSim with and without the
`TutorialHydraulicFractureWithAdvancedXML` artifact task, the ranked divergence list, and
point-biserial correlation plus Mann-Whitney U of each metric against A1's rung-1/2 outcomes.
All statistics are implemented in-file (no scipy dependency) so the numbers are auditable.

## 13. Coordinator's `*_eval.json` warning — checked, does not apply here

Thread D warned that globbing `*_eval.json` silently drops catastrophic-failure runs (no eval file
is written for them), reintroducing a scored-only bias. **My pipeline does not glob.**
`B_build_prompts.py` enumerates the 10 held-out tasks explicitly and constructs the eval path per
`(cell, seed, task)`; a missing file is recorded as `treesim_source = "missing_eval_json"` and, when
the deck also fails to parse, floored to `treesim = 0.0` under the frozen rung-1 convention.

Verified by re-deriving from `_summary.json` → `results[]` (the source D recommends):

```
F0 : seeds [0.7406, 0.7880, 0.6303] mean 0.7196 sd 0.0809   nulls: 1 (s3, status "error")
F4 : seeds [0.7624, 0.7730, 0.7695] mean 0.7683 sd 0.0054
F6 : seeds [0.7799, 0.7809, 0.7834] mean 0.7814 sd 0.0018
F8 : seeds [0.8022, 0.7862, 0.7597] mean 0.7827 sd 0.0215
F11: seeds [0.7472, 0.7924, 0.7850] mean 0.7749 sd 0.0242
SE : seeds [0.7972, 0.7952, 0.7749] mean 0.7891 sd 0.0123
```

Identical to my §2 table and to D's verified reference points, to 4 dp. Provenance audit of
`B_prompts.jsonl`: 89 records `eval_json`, 1 record `rung1_fail_floor`
(`F0_s3_ExampleProppantTest`, treesim 0.0). Exactly one zero-score held-out run, as D found. No
correction needed.

### Best-combo criterion, stated explicitly

I chose **F6 (S+X)** on **held-out mean (0.7814 vs F4's 0.7683) and seed stability (sd 0.0018 vs
0.0054)** — decided in §2 before any judge call. The coordinator's point is well taken and worth
recording: **F4 (X+M) is the less circular cell for a validity-flavoured argument**, because in F4
the agent calls the validator voluntarily rather than being gated on it by a stop hook, so an
argument of the form "our decks are more valid" is less self-fulfilling for F4 than for F6. I did
not switch, because switching after seeing which cell scores higher is exactly the kind of choice
the freeze is meant to prevent, and because F6 is the cell that carries the σ-collapse claim. **If
the rebuttal leads with a validity argument rather than a reliability argument, F4 is the better
cell and this run should be repeated for F4** — the pipeline takes one flag (`--cells F4`) and
about $1.

## 14. Coordinator's sharpening — the decisive subset

Accepted and implemented as a first-class deliverable. A1's rungs 1-2 discriminate the cells almost
entirely on **lexical and schema** errors (double hyphen in a comment; schema violations), all in
F0. If LMaaJ merely reproduces that signal it adds nothing. The test that matters is whether it
separates the cells on the **(task, seed) pairs where all six cells cleared rung 2**.

`B_analyse.py` now computes that subset: **24 of 30 (task, seed) pairs are clean for all six
cells.** Results reported in §15.

---

# 15. RESULTS — the metric is UNFAVOURABLE for its primary purpose

**357/357 calls completed. 351 scored (98.3 %). Mean mismatch coverage 0.995.**
Six calls failed, all "no JSON object found" (5 × qwen3235b, 1 × gemini3flash), all on large
decks; the frozen median-across-judges rule absorbs them.

Verdict against the four **pre-registered** null conditions from `B_rubric_v1.md`:

| # | Pre-registered condition | Measured | Tripped? |
|---|---|---|:--:|
| 1 | Krippendorff α ≤ 0.2 or Fleiss κ ≤ 0.2 on the 4-way severity label | α = **0.2137**, κ = **0.2238** | **marginal pass** (clears 0.2 by 0.014; both sit in Landis-Koch "slight agreement") |
| 2 | mean \|order A − order B\| ≥ 0.013 (the F6−F4 held-out gap) | pooled mean\|B−A\| = **0.0552** | **TRIPPED (4.2× the threshold)** |
| 3 | LMaaJ fails to separate the cells while TreeSim does | separates on the full set; **flat on the clean subset, where TreeSim is also flat** | not tripped as written; see §15.4 |
| 4 | LMaaJ and TreeSim rank the cells in opposite order | not opposite overall, but **the top two swap**, and one judge inverts the SIGA advantage | partial |

Plus one finding not anticipated by the pre-registration, and it is the most important:

> **The three judges produce three different cell rankings, and GPT-5.4-mini ranks Vanilla
> *above* the best SIGA combo.** Judge choice moves the score 4.8× as much as the condition does.

## 15.1 Score table (Deliverable 1) — plain text, rebuttal-ready

Held-out, 10 tasks × 3 seeds, `mean ± sd across seeds`. `F0_s3/ExampleProppantTest` floored to 0
in both metrics (unparseable deck, no API call made). Aggregation exactly as frozen.

| Cell | TreeSim | LMaaJ | mismatch credit | plausibility /10 | physics fidelity /10 |
|---|---:|---:|---:|---:|---:|
| Vanilla (F0) | 0.7196 ± 0.0809 | 0.8264 ± 0.0483 | 0.8075 ± 0.0484 | 9.30 | 7.78 |
| S+X (F6) | 0.7814 ± 0.0018 | 0.8809 ± 0.0200 | 0.8671 ± 0.0082 | 9.27 | 8.58 |
| SE | 0.7891 ± 0.0123 | 0.8666 ± 0.0087 | 0.8470 ± 0.0121 | 9.50 | 8.27 |

Excluding `TutorialHydraulicFractureWithAdvancedXML` (the TreeSim artifact of §7):

| Cell | TreeSim | LMaaJ |
|---|---:|---:|
| Vanilla (F0) | 0.7982 ± 0.0898 | 0.8364 ± 0.0773 |
| S+X (F6) | 0.8668 ± 0.0020 | 0.9087 ± 0.0207 |
| SE | 0.8753 ± 0.0137 | 0.9060 ± 0.0081 |

Read superficially this looks encouraging: LMaaJ is higher than TreeSim for every cell (+0.08 to
+0.11), it preserves Vanilla-last, and it reproduces the σ-collapse (F0 sd 0.048 → F6 sd 0.020).
**Do not use it that way.** §15.2 and §15.3 are why.

## 15.2 Agreement statistics (Deliverable 2)

**Severity labels — 4137 (deck × mismatch) units, 3 judges each:**

| Statistic | Value | Reading |
|---|---:|---|
| Krippendorff α (nominal, 4-way) | **0.2137** | "slight" — far below the 0.667 usually demanded of a coding scheme |
| Fleiss κ (4-way) | **0.2238** | same band |
| Exact 3-judge label agreement | **41.5 %** | chance ≈ 25 % for 4 classes |
| Krippendorff α, collapsed {cosmetic,minor} vs {material,severe} | **0.2566** | still "slight" |
| Exact agreement, collapsed | **59.7 %** | chance ≈ 50 % |

Collapsing the ladder to a binary barely helps, so this is not a boundary-definition problem — the
judges genuinely disagree about whether a given difference matters physically.

**Per-deck LMaaJ, judge vs judge:**

| Pair | n | Pearson | Spearman |
|---|---:|---:|---:|
| gemini3flash vs gpt54mini | 88 | +0.556 | +0.539 |
| gemini3flash vs qwen3235b | 83 | +0.629 | +0.663 |
| gpt54mini vs qwen3235b | 84 | +0.741 | +0.611 |

Correlated but not interchangeable, and the **levels** are wildly different:

| Judge | mean LMaaJ | cosmetic | minor | material | severe |
|---|---:|---:|---:|---:|---:|
| `google/gemini-3-flash-preview` | 0.9573 | 85.3 % | 7.6 % | 5.5 % | **1.6 %** |
| `openai/gpt-5.4-mini` | 0.6978 | 40.3 % | 14.5 % | 18.6 % | **26.6 %** |
| `qwen/qwen3-235b-a22b-2507` | 0.8658 | 70.6 % | 8.5 % | 3.9 % | **17.0 %** |

gpt-5.4-mini calls 26.6 % of flagged differences physically severe; gemini-3-flash calls 1.6 % —
a **17× spread** on the single quantity the metric exists to measure.

**Position-bias check (order A vs order B, seed-1 subsample, 30 decks × 3 judges):**

| Judge | n | mean signed (B−A) | mean \|B−A\| | max \|B−A\| |
|---|---:|---:|---:|---:|
| gemini3flash | 30 | +0.0178 | 0.0214 | 0.1681 |
| gpt54mini | 30 | −0.0007 | 0.0737 | 0.1922 |
| qwen3235b | 29 | +0.0269 | 0.0710 | 0.2770 |
| **pooled** | **89** | **+0.0145** | **0.0552** | 0.2770 |

Two readings, both worth stating:
- **Systematic bias is small.** Pooled signed shift +0.0145; gpt54mini's is −0.0007. Simply
  swapping which deck is printed first does not systematically favour either.
- **Instability is large.** Pooled mean\|B−A\| = **0.0552**, i.e. **1.01× the entire
  between-cell effect (0.0545)**, with individual decks moving up to 0.277. Re-ordering two
  blocks of an otherwise byte-identical prompt at temperature 0 moves a single deck's score as
  much as the effect we are trying to measure.

**Nuisance vs signal — the summary number:**

| Quantity | Value | × the LMaaJ cell effect |
|---|---:|---:|
| LMaaJ cell-effect range (F0→F6) | 0.0545 | 1.00 |
| TreeSim cell-effect range | 0.0695 | 1.28 |
| **Judge-choice range** | **0.2595** | **4.76** |
| **Position instability (mean \|B−A\|)** | **0.0552** | **1.01** |

## 15.3 Ranking stability — the disqualifying result

Per-judge cell means (order A, floors included):

| Judge | Vanilla | S+X | SE | ranking |
|---|---:|---:|---:|---|
| gemini3flash | 0.9342 | 0.9479 | 0.9585 | SE > S+X > Vanilla |
| gpt54mini | 0.6799 | **0.6674** | 0.7230 | SE > **Vanilla > S+X** |
| qwen3235b | 0.8243 | 0.8783 | 0.8678 | S+X > SE > Vanilla |
| *(TreeSim)* | *0.7196* | *0.7814* | *0.7891* | *SE > S+X > Vanilla* |

**Three judges, three different orderings. Only 2 of 3 put Vanilla last.** `gpt-5.4-mini` scores
Vanilla **above** S+X — it reverses the sign of the paper's central contrast. A reviewer who ran
this metric with one plausible judge choice would conclude SIGA does not help.

Any claim of the form "a second, semantic metric confirms the SIGA advantage" is **not supported**.
The only claim that survives is the much weaker "under two of three judge choices the ordering is
preserved," which is not worth making.

## 15.4 TreeSim correlation and divergence (Deliverable 3)

| Set | n | Pearson | Spearman |
|---|---:|---:|---:|
| all held-out decks | 90 | **+0.718** | **+0.566** |
| excluding `TutorialHydraulicFractureWithAdvancedXML` | 81 | +0.758 | +0.483 |

Moderate agreement — enough that the two metrics are measuring overlapping things, loose enough
that LMaaJ is not a relabelling of TreeSim.

**The divergences, which are the interesting part.** Largest LMaaJ − TreeSim:

| Δ | cell | seed | task | TreeSim | LMaaJ | credit | n flagged |
|---:|---|---|---|---:|---:|---:|---:|
| +0.978 | F0 | 3 | TutorialHydraulicFractureWithAdvancedXML | 0.012 | 0.990 | 0.969 | 3363 |
| +0.679 | F6 | 1 | TutorialHydraulicFractureWithAdvancedXML | 0.013 | 0.692 | 0.594 | 3321 |
| +0.640 | F6 | 3 | TutorialHydraulicFractureWithAdvancedXML | 0.013 | 0.653 | 0.358 | 3318 |
| +0.558 | SE | 3 | TutorialHydraulicFractureWithAdvancedXML | 0.013 | 0.571 | 0.413 | 3319 |
| +0.357 | F6 | 2 | AdvancedExampleThermoPoroElasticWellbore | 0.643 | 1.000 | 1.000 | 197 |
| +0.331 | F6 | 3 | AdvancedExampleThermoPoroElasticWellbore | 0.669 | 1.000 | 1.000 | 173 |
| +0.344 | F0 | 3 | AdvancedExampleThermoPoroElasticWellbore | 0.058 | 0.402 | 0.114 | 200 |

And the other direction (LMaaJ harsher than TreeSim):

| Δ | cell | seed | task | TreeSim | LMaaJ |
|---:|---|---|---|---:|---:|
| −0.361 | F6 | 1 | ExamplesingleFracCompression | 0.862 | 0.501 |
| −0.324 | F6 | 2 | AdvancedExamplePureThermalDiffusionWellbore | 0.944 | 0.620 |
| −0.144 | F0 | 2 | ExampleIsothermalHystInjection | 0.762 | 0.619 |

Two things to note honestly:
- The nine largest divergences are **all the same task** — `TutorialHydraulicFractureWithAdvancedXML`,
  the deck whose reference expands to 3333 elements (§7). The judges are right that a
  ~50-element deck answering the brief is not 0.013-quality, so **the divergence confirms the
  TreeSim artifact** rather than revealing magnitude-blindness. That is a real result but it is
  the §7 result, not a new one.
- The judges' *own* spread on that one task is 0.46 → 0.99 across cells and seeds for
  near-identical content, which is more evidence of judge instability than of TreeSim error.
- The negative-direction divergences are where the metric earns its keep in principle:
  `F6_s1_ExamplesingleFracCompression` scores 0.862 structurally but 0.501 on physics. Whether
  that is right cannot be settled without execution, and this task is not in A2's run set.

### The decisive subset (the coordinator's sharpening)

24 of 30 (task, seed) pairs are schema-valid for **all six** cells; 72 decks across my three cells.

| Cell | n | TreeSim | LMaaJ | credit |
|---|---:|---:|---:|---:|
| Vanilla (F0) | 24 | 0.8504 ± 0.1949 | 0.8851 ± 0.1352 | 0.8883 |
| S+X (F6) | 24 | 0.8444 ± 0.1999 | 0.8823 ± 0.1511 | 0.8851 |
| SE | 24 | 0.8462 ± 0.2011 | 0.8962 ± 0.1300 | 0.8868 |

Contrasts (Mann-Whitney U, two-sided):

| Contrast | metric | Δ | p |
|---|---|---:|---:|
| F0 → F6 | TreeSim | −0.0060 | 1.000 |
| F0 → F6 | LMaaJ | −0.0028 | 0.901 |
| F0 → SE | TreeSim | −0.0042 | 0.942 |
| F0 → SE | LMaaJ | +0.0112 | 0.926 |
| F6 → SE | TreeSim | +0.0018 | 0.853 |
| F6 → SE | LMaaJ | +0.0139 | 1.000 |

**On the runs where every cell produced schema-valid XML, neither metric separates the cells at
all** — every Δ is within ±0.014 against sds of 0.13-0.20, every p ≥ 0.85, and LMaaJ actually
puts Vanilla *above* S+X here too. So:

- The coordinator's test is answered, and the answer is **no**: LMaaJ does **not** find a
  magnitude-dimension signal that survives removal of the lexical/schema signal. It adds nothing
  over TreeSim on the clean subset.
- This is also an important **substantive** result about the paper, independent of LMaaJ:
  **on held-out, the entire measured cell separation is carried by catastrophic failures**
  (unparseable / schema-invalid decks, all Vanilla), not by graded quality differences on the
  runs that work. That is *exactly* the reliability framing of execution-plan §4.1 — and it says
  the reliability claim is the honest headline while the mean-lift claim on held-out is thin. It
  should be checked by Threads C/D against the val-split numbers.

## 15.5 Execution calibration (Deliverable 4)

Ground truth from Thread A1 (rungs 1-3, all 90 decks) and Thread A2 (rungs 3-4 via the real GEOS
binary, 27 decks on the two rescue tasks). Point-biserial r and two-sided Mann-Whitney U.

| Rung | Check | n pass / fail | LMaaJ pass / fail | LMaaJ r_pb (p) | TreeSim r_pb (p) |
|---|---|---|---|---|---|
| 1 | well-formed XML | 87 / 3 | 0.877 / 0.310 | **+0.562** (0.004) | +0.413 (0.011) |
| 2 | schema-valid vs GEOS XSD | 84 / 6 | 0.877 / 0.592 | +0.393 (0.063) | **+0.506** (0.002) |
| 3 | `geosx --validate-input`, per file (A1) | 61 / 29 | 0.923 / 0.722 | **+0.520** (<0.001) | +0.451 (<0.001) |
| 3 | `geosx --validate-input`, full deck (A2) | 20 / 7 | 0.947 / 0.633 | +0.608 (0.005) | **+0.653** (0.002) |
| 4 | runs to completion (A2) | 16 / 11 | 0.963 / 0.724 | **+0.518** (0.001) | +0.519 (0.018) |

**This is the genuinely positive result.** LMaaJ is not noise: it correlates with real simulator
outcomes at r ≈ 0.5-0.6, significantly, including rung 4 (the deck actually runs). It is a valid
instrument.

**But it is not a *better* instrument.** TreeSim achieves the same thing, with equal or better r
on three of the five rungs, at zero marginal cost and with perfect reproducibility. On rung 4 the
two are indistinguishable (+0.518 vs +0.519). The one place LMaaJ is clearly better is rung 1
(+0.562 vs +0.413) — and rung 1 is well-formedness, which `xmllint` decides for free.

Rung-4 failures span all three cells (5 × F0, 2 × F6, 4 × SE), so this is a task-difficulty
signal more than a cell signal — consistent with §15.4.

## 15.6 The severity spectrum — the one output worth shipping

| Cell | cosmetic | minor | material | severe | n flagged differences |
|---|---:|---:|---:|---:|---:|
| Vanilla (F0) | 62.7 % | 11.0 % | 9.3 % | 17.0 % | 4169 |
| S+X (F6) | 67.0 % | 9.8 % | 9.1 % | 14.1 % | 4041 |
| SE | 65.7 % | 9.9 % | 10.1 % | 14.2 % | 3882 |

**Every one of these ~12 000 differences scores exactly zero under TreeSim.** All three judges,
from three different families, agree that `cosmetic` is the **modal** class (85 % / 40 % / 71 %),
so the *direction* is robust even though the magnitude is not.

The defensible claim, stated at the strength the data supports:

> Under an LLM-judge audit with three judges from three model families, the **majority** of the
> attribute-level differences TreeSim scores as total failures are judged physically immaterial
> (point estimate 63-67 % per cell; individual judges range 40-85 %). TreeSim therefore
> understates the absolute quality of every cell's decks. The effect is close to common-mode
> across cells (the cosmetic share differs by only 4 pp between Vanilla and S+X), so it depresses
> levels rather than distorting contrasts.

That supports execution-plan §4.3's Gap-B / common-mode argument — a *self-criticism* of TreeSim's
absolute level — which is exactly the kind of claim that does not require the judge to be a
reliable discriminator. It is a within-deck audit, not a between-cell measurement, and it is
robust in the only respect it needs to be.

## 15.7 Cost (honest, including waste)

Computed from raw token counts × OpenRouter list price captured 2026-07-26 from
`/api/v1/models`, stored per call in `B_judge_raw.jsonl.cost_usd`. **Not** taken from any
provider-reported cost field — per the DeepSeek cost-accounting memory, logged `total_cost_usd`
fields in this repo are computed at Anthropic rates and are wrong by ~60× for non-Anthropic runs.

| Item | Cost |
|---|---:|
| `openai/gpt-5.4-mini` (119 calls) | $1.827 |
| `google/gemini-3-flash-preview` (118 calls) | $1.330 |
| `qwen/qwen3-235b-a22b-2507` (114 calls) | $0.238 |
| **Final 357-call run, total** | **$3.395** |
| Smoketest (9 calls incl. the discarded kimi round) | ~$0.077 |
| **Wasted on my duplicate-launch error (172 redundant calls)** | **~$1.70** |
| **Total API spend for this thread** | **≈ $5.17** |

Above the "trivial" target, and ~$1.70 of that was avoidable operator error. Reported rather than
absorbed. A repeat run for cell F4 would cost ≈ $1.1.

## 15.8 What this thread recommends

**Do not put the LMaaJ score table in the response as a confirming second metric.** It fails on
inter-judge agreement (α = 0.21), it is unstable to prompt ordering at the scale of the effect
(1.01×), it is dominated by judge choice (4.76×), one of three judges inverts the central
contrast, and on the clean subset it separates nothing. A reviewer who checks any of these — and
the AC made evaluation the decision criterion, so they will — turns it into a fifth weakness.
Overselling this is worse than not running it, as the spec warned.

**Do ship, in descending order of strength:**

1. **§6 — TreeSim subtree annihilation.** Deterministic, no LLM, no trust required. 31/90 held-out
   decks lose ≥1 whole subtree because one extra attribute on a name-less container forces
   `compute_element_similarity` to exactly 0. The `gravityVector` example is vivid and the
   direction (SE hit hardest, 12/30) is against us, which makes disclosing it credible.
2. **§7 — the `TutorialHydraulicFractureWithAdvancedXML` 0.013 floor.** Identical for all cells and
   seeds; a metric artifact worth ≈0.099 of depression on every held-out mean.
3. **§10 — TreeSim silently scores partially unparseable decks.** All instances are Vanilla, so it
   under-counts Vanilla's failures.
4. **§15.6 — the severity spectrum**, framed strictly as a within-deck audit of TreeSim's absolute
   level with the 40-85 % judge range stated in the same sentence. One short paragraph, no table
   of cell scores.
5. **§15.5 — LMaaJ tracks execution** (rung 4 r_pb = +0.52, p = 0.001), reported as evidence that
   the *input side* is measurable, alongside the concession that TreeSim does it equally well.
6. **§15.4 — the clean-subset null.** This is a genuine and useful finding about the paper: on
   held-out, the cell separation is carried by catastrophic failures, not graded quality. It
   argues for leading with the reliability claim, which is §4.1's recommendation anyway.

**Caveats to state before any reviewer does:** this is an LLM judging LLM output; nBNe asked
specifically for *simulator*-output validation and this is not that; it is an intermediate rung
between structure and execution; and its own reliability statistics are poor. Threads A1/A2's
execution ladder is the real answer to the execution ask, and this thread's honest contribution is
a set of measured TreeSim defects plus a negative result about LLM judging.

---

## 16. Reproduction and provenance

```bash
cd /home/matt/sci/repo3 && source .venv/bin/activate
# matplotlib was missing from the venv; note that bare `pip` here resolves to conda's pip and
# installs OUTSIDE the venv. Correct incantation:
#   source .venv/bin/activate && VIRTUAL_ENV=$PWD/.venv uv pip install matplotlib
# (appended matplotlib==3.11.1 to requirements.txt)

python3 neurips_review/sprint/scripts/B_build_prompts.py \
    --out neurips_review/sprint/artifacts/B_prompts.jsonl
python3 -u neurips_review/sprint/scripts/B_run_judges.py \
    --prompts neurips_review/sprint/artifacts/B_prompts.jsonl \
    --out    neurips_review/sprint/artifacts/B_judge_raw.jsonl \
    --orders A B --order-b-seeds 1 --workers 8      # resumable; 357 calls
python3 neurips_review/sprint/scripts/B_analyse.py
python3 neurips_review/sprint/scripts/B_figure.py
```

Rubric integrity check (must still match the freeze):
```
$ sha256sum neurips_review/sprint/artifacts/B_rubric_v1.md
6b0e216eb5ff71111eafc1055c752b089b44f4330b012ea2e25070918a4dac8b   # verified post-run, unchanged
```

### Deliverables checklist

| # | Deliverable | Where |
|---|---|---|
| 1 | Score table, per cell, mean ± sd across seeds, held-out, TreeSim-shaped | §15.1; `B_analysis.json:score_table` |
| 2 | Agreement statistics + position-bias check | §15.2; `B_analysis.json:agreement`, `position_bias` |
| 3 | Correlation with TreeSim and the divergent cases | §15.4; `B_analysis.json:treesim_corr`, `divergences` |
| 4 | Calibration against execution (rungs 1-4) | §15.5; `B_analysis.json:execution_calibration` |
| 5 | Chart (rose-pine dawn+moon, 4 chart types, Space Grotesk + Inconsolata) | `artifacts/figs/B_lmaaj_{dawn,moon}.{png,pdf}` |
| 6 | XN experiment note | `docs/XN-024_lmaaj-semantic-metric-heldout.md` (`.copilot/config.yml` next_number 24 → 25) |
| 7 | Raw per-deck judge outputs as JSONL | `artifacts/B_judge_raw.jsonl` (357 calls, response text + tokens + cost + parsed verdicts), `artifacts/B_prompts.jsonl` |

Every number in §15 and in XN-024 was cross-checked programmatically against `B_analysis.json`
(20 spot-checks, 0 mismatches) rather than transcribed by hand.

### Boundaries respected

Wrote only to `neurips_review/sprint/{threads,artifacts,scripts}/`, `docs/XN-024_*.md`,
`.copilot/config.yml` (next_number bump), `requirements.txt` (matplotlib pin), and the project
`.venv`. **No `_`-prefixed directory was written.** `/data/shared/` was read-only throughout.
`writing/` was **read** only (`writing/poster/scripts/posterstyle.py`); the figure `outdir` was
redirected to `neurips_review/sprint/artifacts/figs/` so `writing/poster/figs/` is untouched
(mtimes still Jun 3). Any `writing/` entries in `git status` are not from this thread.

### Open items for a human

1. **Decide whether to ship the LMaaJ score table at all.** This thread's recommendation is **no**
   — see §15.8. The three deterministic TreeSim defects (§6, §7, §10) and the clean-subset null
   (§15.4) are the shippable output and none of them requires trusting a judge.
2. **§15.4 needs a decision that is bigger than this thread.** On held-out, the cell separation is
   carried entirely by catastrophic failures; on schema-valid runs neither metric separates the
   cells (all p ≥ 0.85). If that also holds on val, the mean-lift claim needs re-framing and the
   reliability claim should lead. Threads C/D own the val numbers.
3. **Rewrite execution-plan §4.4** before quoting it — two of its three scoring constants belong to
   the matcher, not the scorer (§1, CORRECTION 1).
4. **Whether to re-run for F4 (X+M)** instead of / in addition to F6. F4 is the less circular cell
   for a validity argument (voluntary validator call rather than hook-gated). ≈ $1.1 and one flag.
5. **Whether to fix the §6.1 annihilation defect in `judge_geos.py`.** Recommendation: **do not fix
   it for the rebuttal** — re-scoring changes every number in the paper. Disclose it, with the
   measured prevalence (31/90) and the direction (worst for SE, so it understates our advantage).
   Fix it for camera-ready and report both.
6. **~$1.70 of avoidable API spend** from my duplicate-launch error (§12). Total thread spend
   ≈ $5.17.
