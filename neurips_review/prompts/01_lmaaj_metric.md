# Session prompt — LMaaJ secondary metric (input side)

*Paste this into a fresh session started in `/home/matt/sci/repo3`.*

---

## Context

We are in the NeurIPS 2026 author-response window for submission 31642 (SIGA). Three reviewers and the AC all converge on one objection: our only evaluation metric, **TreeSim**, is structural. It does not establish that generated GEOS input decks are physically sensible. The AC made this the decision criterion.

**Hard deadline: Aug 3.** Useful results are wanted by ~Jul 31 so they can be posted as a follow-up comment. Nothing here blocks the Jul 27 initial response.

Background reading, in order:
- `neurips_review/SIGA_weaknesses.md` — what the reviewers actually said
- `neurips_review/SIGA_rebuttal_execution_plan.md` §4 — how we frame the evaluation argument
- `src/eval/judge_geos.py` — the TreeSim implementation

## Why this metric exists — the precise gap being filled

TreeSim is **not** a string match. It resolves XML includes, bipartite-matches elements between reference and generated trees, scores tag match + `name`-attribute bonus (0.4) + attribute-value overlap, penalizes hallucinated elements (β = 0.1), and weights own-attributes vs subtree at α = 0.3 for interior nodes. Attribute values pass through `values_equivalent`, which parses scalars and float lists and compares numerically at **`NUMERIC_RTOL = 1e-6`**, falling back to case-insensitive string equality.

So `1e6`, `1000000` and `1.0e+06` all match correctly.

**But `rtol = 1e-6` is effectively exact equality, so TreeSim has no notion of how wrong a wrong value is.** A permeability off by 2× and one off by 18 orders of magnitude score identically. It also has no notion of physical equivalence: unit changes, renamed regions, algebraically equivalent formulations, and different-but-valid discretizations all read as mismatches.

**The judge's job is to supply the magnitude-and-plausibility dimension that a 1e-6 tolerance cannot express.** That framing should drive every design decision below. This is not "add an LLM metric because LLM metrics are nice."

## Scope

- **Cells:** Vanilla (`autocamp_F0`), best combo (`autocamp_F6` = S+X, or `autocamp_F4` = X+M — check which is stronger on held-out), and SE (`autocamp_SE`)
- **Split:** held-out-eval (10 tasks). Not val — val is at ceiling for every cell and has no spread to explain.
- **Seeds:** all 3
- **Total:** ~90 decks

**Data locations:**
- Generated decks: `/data/shared/geophysics_agent_data/data/eval/autocamp_2026-05-01/dsv4/<cell>/<cell>_s<N>/<task>/`
- Reference decks: `/home/matt/sci/repo3/data/GEOS/inputFiles/`
- Cost accounting: read `/home/matt/.claude/projects/-home-matt-sci-repo3-research-copilot/memory/reference_deepseek_cost_accounting.md` before quoting any dollar figure — there are two known traps that produce wrong numbers.

## Design requirements — these are load-bearing, do not silently drop them

1. **Comparative, not absolute.** Judge the generated deck *against the reference deck*. Same information TreeSim uses, so the comparison to TreeSim is apples-to-apples.

2. **Feed the judge the TreeSim diff, not just the two files.** The gap we are targeting is magnitude-blindness on *flagged attribute mismatches*. Showing the judge exactly which attributes TreeSim marked as different points its budget at the right question and makes the metric interpretable as "TreeSim plus magnitude awareness."

3. **Score dimensions** (keep it small and defensible):
   - physical plausibility of parameter values
   - whether each flagged difference is physically **material** or **cosmetic**
   - whether the deck specifies the physics the task brief actually asked for

4. **Multiple queries.** Several judge models, plus A/B position swapping to control order bias. **Report inter-judge agreement, not just the mean** — a metric with no agreement statistic will be dismissed.

5. **Blind the judge** to which cell produced which deck. No cell names, no file paths that leak the condition.

6. **Do not use a judge from the same family as any scored backbone.** The backbone here is `deepseek-v4-flash`. A DeepSeek judge is disqualifying. This is exactly the flaw in our own LAMMPS study and reviewers will apply it here too.

7. **Calibrate against execution.** A parallel session is running decks through the real GEOS binary (`prompts/02_execution_case_studies.md`). On whatever subset has execution outcomes, **correlate LMaaJ score against validate/run/converge results**. This is the difference between "we added an LLM metric" and "we added a metric and showed it tracks ground truth." Coordinate — don't rebuild their pipeline.

## Deliverables

1. **Score table** — per cell, mean LMaaJ ± std across seeds, on held-out. Same shape as the TreeSim table so they can sit side by side.
2. **Agreement statistics** — inter-judge agreement, position-bias check.
3. **Correlation with TreeSim** — where do they agree, where do they diverge? The divergences are the interesting part: they are the cases TreeSim gets wrong, which is the whole argument.
4. **Calibration against execution**, if the parallel session has produced outcomes.
5. **A chart.** Figure style: read `/home/matt/.claude/projects/-home-matt-sci-repo3-research-copilot/memory/user_figure_style_prefs.md`. Short version: rose-pine theme, Space Grotesk for labels, Inconsolata for numbers, reusable setup at `writing/poster/scripts/posterstyle.py`. Advisor's standing rule is charts over tables, and vary the chart type.
6. **An `XN-NNN` experiment note** in the project's convention.

## Constraints and cautions

- **Everything must survive as plain text.** The rebuttal allows no file uploads, no links, and no images. The chart is for us and for camera-ready; the number that goes to reviewers must work as a markdown table.
- **State the caveats yourself.** It is an LLM judging LLM output, and nBNe asked for *simulator* output validation specifically. Present this as an intermediate rung, not as an answer to the execution ask. Overselling it is worse than not running it.
- **Do not tune the judge prompt against the results.** Fix the rubric before looking at cell-level scores, or the metric is worthless.
- If the metric comes out **null or unfavourable**, that is a real finding — report it. We are not obligated to use it, and discovering it doesn't work is much better discovered by us now than by a reviewer later.

## First step

Before writing any judging code, read `src/eval/judge_geos.py` end to end and confirm the description of `values_equivalent` above is accurate. Then smoketest the pipeline on **one task, one cell, one seed**, and show me the judge's raw output before scaling to 90 decks.
