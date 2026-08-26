# hand_v8 markup pass

Line numbers refer to `siga_neurips26_rebuttal.md` as of this pass.
Mark each item: accept / reject / revise.

Structure assumed: 4 independently posted sections (AC, gep1, kEdh, nBNe).
Deliberate repetition across sections is treated as correct, not as a defect.

---

# PART A. Global fixes (once, everywhere)

**A1. Backslash escapes throughout. Highest priority.**
`1\.`, `rho \= 0.418`, `\+0.048`, `\[1\]`, `(77 of 77\)`, `2005\.`,
`xmllint \--schema`, `buckleyLeverett\_base.xml`, `verify\_outputs`.
These are Google Docs export artifacts. OpenReview renders markdown, so they post as
literal backslashes. This is the most visible sloppiness signal in the file.
Fix: global strip of `\.` `\=` `\+` `\-` `\[` `\]` `\)` `\_`, then eyeball code spans.

**A2. Heading depth differs between sections.**
The AC section uses `#` for its own subsections (L7, L20), the same level as the
section separator. The other three use `##` title then `###` items.
Fix: one scheme. Suggest `##` for the section title, `###` for every item inside it.

**A3. Section separators are internal filenames.**
L1 `# ac\_response\_latest`, L75 `# gep1\_latest`, L155 `# kEdh\_latest`,
L205 `# nBNe\_latest`. Fine as your own dividers, but if any of this is pasted as a
combined document they read as leftovers. Either strip them at paste time, or retitle
to `# Response to the Area Chair` etc. and drop the now duplicate `## Response to
Reviewer gep1` at L77.

**A4. Mixed straight and curly quotes.**
Same paragraph at L167: `component’s` then `component's`. L173: `**"Deck"**` then
`“input deck”`. Also L226. Fix: normalize to straight quotes.

**A5. Mixed en-GB and en-US spelling.**
`judgements` (L41, L102), `instalment` (L147) against `normalized` elsewhere.
Fix: en-US throughout.

**A6. Three different names for the same commitment.**
L43 "the camera-ready", L104 and L143 "manuscript revisions", L187 "the revised
version". Fix: use "the revision" everywhere. Note the no-revised-PDF constraint once,
in the kEdh section only.

**A7. Reference formatting differs between sections.**
AC section (L69 to L73) uses full-author APA; gep1 and nBNe use "Zhang et al." short
form, same five references. Fix: short form everywhere.

**A8. Reference [5] author names are mangled.**
L73: `Zhehao, D. O. N. G., Zhen, L. U., & Yue, Y. A. N. G.` A Scholar export bug.
Fix: `Dong, Z., Lu, Z., & Yang, Y.` The short form at L153 is already correct.

**A9. `rho` is never defined** (L40, L97, L101, L218). Presumably Spearman.
Fix: "Spearman rho" at first use in each section. Also standardize precision:
currently 2 dp (`0.36`) and 3 dp (`0.418`, `0.456`) are mixed.

**A10. "interval" where you mean a confidence interval.**
L87 "clustered interval +2.9 to +16.5", L97 "interval 0.20 to 0.51",
L104 "interval -0.003 to +0.072". A bare "interval" reads as evasive.
Fix: say "95% CI" (and "cluster-bootstrap 95% CI" at L87 if that is what it is).

**A11. `[6] [7]`** at L228 should be `[6, 7]`.

**A12. Trailing whitespace** on L70, L149 to L153, L228, L255 to L256. Harmless except
at L192, which produces a visible artifact (see B32).

---

# PART B. Line by line

## AC section

**B1. L11** "higher level, higher leverage tasks" needs hyphens:
`higher-level, higher-leverage tasks`.

**B2. L13** Wrong comma, missing period, missing hyphen. Proposed:
> Our primary work focuses on geophysics (GEOS), but we validate the method in two further domains: fluid dynamics (OpenFOAM) and molecular dynamics (LAMMPS, added post-submission).

**B3. L16 to L18** Capitalization after the colons is inconsistent ("Minutes instead
of hours" vs "Variance reduction"), and "wall clock" is used as a noun. Proposed:
> - vs. human: minutes instead of hours
> - vs. baseline coding agent: reduced variance (fewer catastrophic failures); up to 22% fewer tool calls and 18% less wall-clock time per task on the harder split

"(best adapter cells)" is opaque without the table. Name the cell or drop it.

**B4. L22** `## 1. Evaluation Metrics.` has a trailing period and is Title Case where
L45, L49 and L55 are sentence case. Fix: `## 1. Evaluation metrics`.

**B5. L24** "the physics **are** fixed" but L83 and L242 both say "the physics **is**
fixed". Pick "is".

**B6. L24** "our similarity to ground truth metrics captures this" is ungrammatical.
Fix: `our similarity-to-ground-truth metric captures this on the output side.`

**B7. L28** `New Metrics` is an orphan line, neither heading nor lead-in. The parallel
spot at L89 reads "New metrics beyond the artifact:". Fix: make it
`**New metrics** (all on the held-out split):` and delete the now redundant sentence
at L26.

**B8. L32** Grammar: "Does the simulation run to completion and the solver
converges?" The gep1 version at L92 is correct. Use it:
> (binary) does GEOS accept the deck, and does the run complete with a converged solver?

**B9. L35** Gerund fragment where L96 uses imperatives, plus a missing hyphen.
Proposed:
> (continuous) inject an identical ground-truth output block into both decks, run both, and compare mesh-independent reductions of each physical quantity, each normalized by the reference's own scale

**B10. L36, also L97 and L217** "reproducing the reference almost exactly" is
undefined, while L177 to L179 goes to trouble defining "almost exactly" as above 0.999
for the structural metric. Two different meanings in one document. Fix: give the
fidelity threshold inline.

**B11. L51, L108, L246** The repeated GEOS-scale paragraph contains a garbled clause
in all three copies:
> run counts balloon with various ablations, repeated runs for error bars, and other experiments on backbone models, and harnesses

Proposed:
> run counts multiply across ablations, repeated runs for error bars, and further experiments across backbone models and harnesses

Also "the achievable set is of this order" is vague. Suggest "the achievable pool is
bounded at roughly this size."

**B12. L53** Run-on, repeated "expanded", spurious capitals, a slash. Proposed:
> We have since expanded the fluid-dynamics (OpenFOAM) transfer study to 30 tasks and added two simulator-native baselines (see Reviewer gep1's thread). We have also added a third domain, molecular dynamics (LAMMPS), with 9 initial tasks and a 20-task scale-up underway.

**B13. L57** Missing commas around "however" and before "especially". Proposed:
> We agree the human baseline is better described as a preliminary calibration, and we are happy to relabel it in the revision. We do maintain, however, that it is a useful calibration: it establishes a human pace on a relatively easy 1D problem. Scale is constrained by time and resources, since recruiting PhD-level geophysics knowledge workers is difficult, especially for long, involved tasks such as simulation configuration.

**B14. L59** `## On the concern raised by Reviewer kEdh` is unnumbered where the other
four AC subsections are numbered. Fix: `## 5. Venue fit (raised by Reviewer kEdh)`.

**B15. L63** "this criteria" should be "these criteria". Hyphenate
"contribution-type guidance". Consider dropping the bold, which reads defensive.

**B16. L65 to L67** "find some decoupling between feedback and score" is vague and
pointed at the same time. Proposed:
> The review recommends rejection but does not identify a technical, evaluation, reproducibility, or ethical concern. We are glad to address the writing concerns raised, and we would welcome the reviewer's view on whether those concerns alone motivate the score.

## gep1 section

**B17. L87** Telegraphic, and one denominator is unexplained (X+M has 100 runs where
the others have 170). Proposed:
> **Artifact validity.** We re-ran this at 17 runs per cell rather than 3, because these are counts of rare events. Vanilla produces a well-formed, schema-valid deck on 155 of 170 runs; S+X on 170 of 170 and X+M on 100 of 100 (X+M was run on a smaller task subset, hence the smaller denominator: CONFIRM). The 8.8-point gap has a cluster-bootstrap 95% CI of +2.9 to +16.5, p = 0.0006, across 270 adapter runs with no failures.

**B18. L87 vs L93, consistency.** Artifact validity for Vanilla is 155/170 = 91.2%,
but two bullets later "decks accepted" for Vanilla is 78.2%. Different metrics, but
the juxtaposition invites confusion. Add half a sentence: "GEOS's own input check is
stricter than schema validity, hence the lower rate."

**B19. L93, arithmetic that does not close.** "decks accepted rises from 78.2% to
90.0% ... of accepted decks, 100% ran to completion (77 of 77)." If 90.0% acceptance
yields 77 accepted decks, n = 85.6, not an integer. No n is given for 78.2% either.
Please check the denominators before posting. If the numbers come from different
pools, say so.

**B20. L98** Long, and the ending is awkward. Proposed:
> the gap between structure and physics sits in decks that fail to run, not in decks that run and are wrong, which is consistent with the reliability framing the review credits.

("distance between structure and physics" is better as "gap".)

**B21. L102** Run-on. Proposed:
> it does not beat plain structural scoring at this task, and two of four judges ordered the conditions differently. It therefore needs calibration against domain-expert judgments before we would offer it as a metric, which we reserve for follow-up work.

**B22. L110 to L115** Superseded. See Part C.

**B23. L113** "Judge scores move from 4.56 to 7.78" gives no scale. Out of 10?
Add it.

**B24. L115** "Both remain single-run" is no longer true for OpenFOAM. See Part C.

**B25. L119** `SE` appears nowhere else in the document. The factors are R, S, X, M.
Typo for S+X? For "S alone"? Must be resolved. An undefined condition name in a
rebuttal is a gift to a skeptical reviewer.

**B26. L119** The delta is presented in the opposite order to how it is computed
("0.913 with the prefix against 0.917 without, a difference of +0.004"). Proposed:
> A targeted ablation gives 0.917 without the prefix against 0.913 with it, a difference of +0.004 across 3 runs on 17 tasks, with no single task moving by more than 0.10.

**B27. L119** "introduced a distractor text" should be "introduced distractor text".

**B28. L123** "The direction reinforces our conclusions." A +0.004 null result does
not reinforce anything. Suggest "The direction favors our conclusions."

**B29. L127 to L131** The "vs Vanilla" cell on the Vanilla row is empty. Put an em
placeholder or "n/a".

**B30. L137 to L139** `### Q3. Strengthening the OpenFOAM study` answered in one line
("Strengthened as described in W2") reads dismissive of a direct request. Replacement
drafted in C4.

**B31. L145 to L147** "Limitations wording" is the only item in this section without
a W or Q label, so it reads as an afterthought. Retitle
`### Additional point: limitations wording`, or fold into W1/Q1.
L147 "the first instalment" is en-GB and florid. Suggest "a first step".

**B32. gep1 item numbering.** The section covers W1/Q1, W2, Q2a, Q2b, Q3, Q4. There is
no W3. If the review has a W3, its absence is conspicuous. Please confirm against the
actual review.

## kEdh section

**B33. L161** "manuscript revisions" twice and "clarifications" twice in two
consecutive sentences. Proposed:
> Each concept the review highlights is defined in the submitted paper, and we locate each below. What the review identifies, usefully, is that several are defined later than their first use, an ordering problem with a definite fix. NeurIPS does not permit a revised PDF during this period, so we give the proposed replacement text inline below.

**B34. L165** "explained **at** line 182" should be "**on** line 182".
"a 2 factor interaction" should be "a two-factor interaction".
"(e.g. M only helps when X is present, etc.)" has redundant `e.g.` and `etc.`; drop
the `etc.`
"the abstract/early sections" should be "the abstract and early sections".

**B35. L167, formatting.** This is proposed replacement text but it is not
blockquoted, whereas every other proposed replacement in this section (L175, L179,
L183) is. Most visible slip in the kEdh section. Fix: wrap in `>`.

**B36. L167** "a carefully chosen half of the sixteen, eight combinations, selected so
that" is comma-stacked. Suggest "a carefully chosen half, eight of the sixteen,
selected so that".

**B37. L169** Garbled: "In line 290, we describe its relevant attributes of it being
1D and therefore a relatively simple task." Proposed:
> Line 290 gives the attributes that matter here: it is 1D, and therefore a relatively simple task.

**B38. L169** "Its details are largely unimportant for discussion purposes" brushes the
reviewer off, and then the next sentence supplies the details anyway. Proposed:
> It is the identifier of one benchmark task; its specifics matter less here than its role as an example.

**B39. L169** "is defined in its second mention" should be "at its second mention",
and it appears to conflict with the line 290 pointer above. Clarify which is the
defining mention.

**B40. L173** Comma splice. Proposed:
> **"Deck"** is defined in Section 3. We had assumed "input deck" to be standard terminology, but the reviewer is right that a reader meets the word earlier.

**B41. L177** "We will say it inline instead" should be "We will state it inline
instead".

**B42. L181** The three W2 sub-items are not parallel: two are quoted sentences, the
third is a description ("The failures-as-zero sentence"). Quote the actual sentence,
as with the other two. Also "To clarify, the point we mean to convey is that" can be
"The point is that".

**B43. L183** `e.g.` and `etc.` again. Drop the `etc.`

**B44. L189 to L195, rendering artifact.** L192 is a blockquote line containing only
`> `, splitting one quotation into two blockquotes with a gap. This renders as a stray
empty quote box. Fix as one blockquote with an explicit elision:
> I need to set up a simulation to model a 1D Buckley-Leverett CO2 core flood experiment. [...] **Physical Problem and Domain Geometry** [...] create a hexahedral mesh of length 0.1 m [...] Permeability is 9.0e-13 m2 in all directions. The reference porosity is 0.2 at a reference pressure of 10 MPa. [...] XML files to create: buckleyLeverett_base.xml, buckleyLeverett_benchmark.xml

**B45. L189 and L191** The task is `buckleyLeverettProblem` at L163 and L169 but "the
Buckley-Leverett task" at L189. Since W1 is specifically about that identifier being
confusing, use it consistently and gloss it once.

**B46. L197** Missing terminal colon.

**B47. L203** "we would welcome being told so during the discussion period" is stilted
passive. Suggest "we would welcome hearing so during the discussion period, and will
act on it."

## nBNe section

**B48. L209** "point **at** things we agree with" should be "point **to**".

**B49. L213** Missing comma before "and".

**B50. L215 to L218, broken bullet hierarchy.** The other two sections present three
parallel top-level metrics (Execution, Output, Plausibility). Here "Simulation
Execution" is top-level but "Simulation Output" and "Simulation Input" are nested
under an invented parent "Physics Plausibility". Same three results, different shape.
Fix: flatten to the same three parallel bullets used elsewhere.

**B51. L217** "(91 runs across various tasks and experimental settings)" is the only
place this n appears; the same 0.958 is quoted at L36 and L97 without it. Give the n
in all three or none. "various" is vague either way.

**B52. L217** Missing comma, weak ending. Proposed:
> Because our tasks are sourced from documentation examples, which correspond to representative workflows, the ground-truth outputs are physically meaningful, which is what makes the fidelity measure interpretable.

**B53. L220, factual error.** "Please see our response to **Reviewer 1**." There is no
Reviewer 1. The reviewers are gep1, kEdh, nBNe. Fix to "Reviewer gep1". Also do not
bold the whole sentence. This one matters: a wrong cross-reference is noticed
immediately.

**B54. L224, broken sentence** (no predicate):
> Scaling it is challenging: recruiting PhD-level geophysics knowledge workers for long, involved tasks such as simulation configuration.

Proposed:
> Scaling it is difficult: recruiting PhD-level geophysics knowledge workers is hard, especially for long, involved tasks such as simulation configuration.

**B55. L226** Broken parallelism ("motivated our discussion ... and including") and a
singular/plural mismatch. Proposed:
> Indeed, this motivated both our discussions with a GEOS developer and our inclusion of a geophysics domain expert, one who is not a GEOS expert, in the hands-on experiment.

**B56. L228, cross-reference consistency.** This points at "Section 6.4"; L26 says
"Appendix J"; L85 says "Appendix J, with results in Section 4.6". Three pointers,
possibly to the same thing. Please verify against the submitted PDF.

**B57. L238** "A result there is informative" has a vague referent. Proposed:
> A positive result under that constraint is informative precisely because the intervention is cheap: a real effect argues against rebuilding the agent loop for every new scientific target.

**B58. L244** `### W4` follows `### W2`, so W3 is missing. Same question as B32.
Please confirm against the review.

**B59. L113 vs L248, inconsistent mechanism claim.** L113 says the LAMMPS gain comes
from "knowledge injection rather than completion enforcement"; L248 says the binding
component shifts "from completion enforcement to memory and retrieval". Same result,
two mechanisms named. Pick one and use it in both.

---

# PART C. OpenFOAM numbers

Per your note, the arXiv-version OpenFOAM results are discarded and the new run stands
alone. So this is a clean replacement, not a reconciliation. The current L112 numbers
(0.870 SIGA, 0.516 Foam-Agent, 0.379 MetaOpenFOAM) all go.

## C1. New numbers

Text-similarity metric (`0.7 x similarity + 0.3 x coverage`), 30-task pool:

| System | Score | Tasks | Executability |
|---|---|---|---|
| SIGA best cell (R+S+X+M) | **0.668** (3 seeds: 0.668, 0.685, 0.665) | 30 | **26/29 (89.7%)** |
| Foam-Agent 2.0.0 | 0.565 | 10 | 1/10 (10.0%) |
| MetaOpenFOAM | 0.276 | 10 | 2/9 (22.2%) |

Two things to notice:

**The text-similarity margin is thin.** 0.668 vs 0.565 against Foam-Agent is not a
headline. Do not lead with it.

**Executability is the result.** A 4x to 9x gap, and it is a fair comparison in a way
worth stating explicitly: all three systems got the same 1500s per-task budget, the
same 30s bounded real-execution mechanism in the loop, and the same post-hoc
`test_executability.py` check applied uniformly. That fairness setup is the strongest
thing in the new data and the current draft has no equivalent of it.

## C2. One blocking issue: mismatched task sets

SIGA ran on 30 tasks; both baselines ran on a 10-task subset of the same pool. The
current draft implies 30 for all three.

Best fix: recompute SIGA's score and executability restricted to those same 10 tasks
and report the head-to-head on the matched 10. The per-task SIGA data already exists,
so this is a filter, not a re-run. This is the single highest-value action before
posting.

If that is not possible, state both task counts in the same sentence. C3 below is
written for that safe case, with a note on what to swap if you get the matched number.

## C3. Replacement for L110 to L115 (gep1, W2)

> **Beyond GEOS.** Since submission we have expanded the OpenFOAM transfer study and added a third domain, molecular dynamics, with the LAMMPS simulator.
>
> - **OpenFOAM: 30 tasks, a real-execution validator, and two simulator-native baselines.** The adapter's validator now runs the actual OpenFOAM solver in a container rather than a static linter. Across the full 9-cell factorial on 30 tasks, the best cell (R+S+X+M) scores 0.668 on the text-similarity metric and produces a structurally executable case on 26 of 29 tasks (89.7%). Repeating that cell over three seeds gives 0.668, 0.685 and 0.665, so it is not a single-seed artifact. We also ran two simulator-native systems on a 10-task subset of the same pool, under the same per-task budget, the same bounded real-execution mechanism in the loop, and the same post-hoc executability check: Foam-Agent scores 0.565 with 1 of 10 executable, MetaOpenFOAM 0.276 with 2 of 9. The text-similarity margins are modest; the executability margin is not, and executability is the measure that corresponds to the reliability effect the review singles out. As with GEOS, it measures structural acceptance rather than physical correctness.
> - **LAMMPS: a third simulator.** 9 molecular-dynamics tasks on two backbone models, with a 20-task scale-up underway. LAMMPS input is a command script with no formal schema, which tests whether the recipe is tied to XML. It is not, but the binding component shifts: scripts are structurally complete almost everywhere, so the gain comes from knowledge injection rather than completion enforcement. Judge scores move from 4.56 to 7.78 on one backbone and from 6.33 to 6.89 on the other (0 to 10 scale: CONFIRM).
>
> The LAMMPS study remains single-run and we present it as qualitative transfer evidence; the OpenFOAM best cell is now three-seed. The reliability effect the review singles out as our strongest result replicates on all three interfaces.

If you get the matched-10 number, swap the baseline sentence for:
> On the same 10 tasks, SIGA scores X with Y of 10 executable, against Foam-Agent 0.565 (1 of 10) and MetaOpenFOAM 0.276 (2 of 9).

## C4. Replacement for L137 to L139 (gep1, Q3), fixing B30

> ### Q3. Strengthening the OpenFOAM study
>
> Done, as described under W2. In brief: 30 tasks, a full 9-cell factorial, a validator that runs the real solver rather than a static linter, three seeds on the best cell, and head-to-head comparison against Foam-Agent and MetaOpenFOAM under matched budgets and a common executability check. The clearest separation is on executability: 89.7% for the best SIGA cell against 22.2% and 10.0% for the two baselines.

## C5. Knock-on edits

- **L53 (AC)**: handled in B12; confirm it carries no stale 0.870.
- **L248 (nBNe, W4)**: still true as written, but nBNe explicitly credited "the
  reduction in complete failures", so the executability contrast belongs here.
  Add: "and on that larger set the best cell produces an executable case on 89.7% of
  tasks, against 10% and 22% for the two simulator-native baselines."
- **L115**: "Both remain single-run" is now false. Covered in C3.

---

# PART D. Decisions for you, not copyedits

**D1. Do not put the vanilla OpenFOAM collapse in the rebuttal.**
Vanilla scores 0.089 on seed 1 and exactly 0.000 on seeds 2 and 3. It looks like your
strongest possible result and is your most attackable one, because your collaborator's
own doc attributes it to an unrelated fix in the same commit: a stale path
(`/data/brianliu` to `/data/brian`) made a large OpenFOAM C++ source tree browsable
for the first time, so unconstrained agents burn their budget reading solver source
(31 of 105 Bash calls on one task). The doc scopes it explicitly as "not a universal
claim about unassisted agents on OpenFOAM tasks in general." C3 omits it deliberately.
The SIGA-vs-nothing contrast is better carried by the two baselines, which are clean.

**D2. Foam-Agent's failures are a JSON-parsing fragility, not a reasoning failure.**
5 of 10 Foam-Agent tasks failed on malformed structured output from
deepseek-v4-flash, with no retry path. A retry patch was drafted, tested, then
reverted at your direction to report out-of-box behavior. Keeping the unpatched number
is defensible, but say so in one clause, e.g. "reported as shipped; several Foam-Agent
failures trace to its lack of retry on malformed structured output rather than to its
agent design." If a reviewer or the Foam-Agent authors find this unstated, it reads as
stacking the deck. One sentence buys real credibility here.

**D3. Executability is structural, not physical.** The doc is explicit that the check
measures dictionary-level acceptance only, and that the 30s bound is a timeout
approximation with a known false-pass risk for slow-initializing cases. The entire
gep1 thread is about the structural-vs-physical gap, so claiming an executability win
without this caveat walks into exactly the trap the reviewer is watching for. C3
includes the caveat.

**D4. Different backbone from the main results.** The OpenFOAM work uses
`deepseek/deepseek-v4-flash` via OpenRouter. If the GEOS results use a different
backbone, the transfer claim spans a simulator change and a model change at once.
Worth one clause, or the omission looks convenient.

**D5. Plugin manifest bug, now mostly moot.** `prepare_plugin_dir()` never wrote
`.claude-plugin/plugin.json`, so R's and X's MCP servers never registered in any
historical OpenFOAM run. Since you are discarding the prior OpenFOAM results, this no
longer affects anything you are claiming. Two residual questions: does it touch the
GEOS harness at all, and does any OpenFOAM statement surviving in the submitted PDF
attribute an effect to R or X? If yes to the second, correct it yourself in the
rebuttal rather than leaving it to be found.

---

# Suggested order

1. A1, strip escapes. Mechanical, biggest visual payoff.
2. B53 (Reviewer 1 to gep1), B25 (undefined SE), B54 (broken sentence), B19
   (arithmetic check). These are errors, not style.
3. C2, recompute SIGA on the matched 10 tasks. Highest-value substantive action.
4. Part C text replacement.
5. D1, D2, D3 decisions.
6. The rest of Part B.
