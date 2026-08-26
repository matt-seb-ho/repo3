# v8 to v9 changelog

`hand_v8/` is preserved untouched. `hand_v9/siga_neurips26_rebuttal.md` is the new draft.
Structure is unchanged: 4 independently posted sections (AC, gep1, kEdh, nBNe).

Section lengths against the 10,000 character OpenReview cap:

| Section | Chars |
|---|---|
| Area Chair | 6,451 |
| gep1 | 9,919 |
| kEdh | 5,167 |
| nBNe | 7,054 |

gep1 was 10,394 after applying the edits, i.e. over the cap. See MAJOR-7 for what was cut.

Verified clean: zero em dashes, zero en dashes, zero curly quotes, zero backslash
escapes, zero trailing whitespace.

---

# MAJOR CHANGES (please review these specifically)

## MAJOR-1. Run counts are now disclosed in the Simulation Execution bullet

This is the fix for the arithmetic you asked about. See the "Arithmetic" section below
for the full provenance. v9 now reads:

> decks accepted rises from **78.2%** (Vanilla, 133 of 170 runs at 17 runs per cell) to **90.0%** (S+X, 27 of 30 runs at 3 runs per cell)

Previously neither denominator was stated. Your earlier session flagged this as an open
call and deferred it to you ("Say the word if you want them added on the reviewer
thread"); it was never resolved, so it carried into v8 unstated. I added them because a
reader who tries to reconcile 90.0% with "77 of 77" cannot, and the mismatch reads as
concealment when the actual explanation is benign.

The AC and nBNe sections get the denominators too but not the "runs per cell" detail,
to keep those posts lighter.

**If you would rather not surface the 3-vs-17 run asymmetry, this is the edit to revert.**

## MAJOR-2. Added a sentence reconciling artifact validity with acceptance

New in gep1:

> GEOS's own input check is stricter than schema validity, which is why acceptance rates sit below the artifact-validity rates above.

Without it, Vanilla appears as 155/170 (91.2%) in one paragraph and 78.2% two paragraphs
later, with no explanation.

## MAJOR-3. `SE` is now glossed, not removed

My first pass flagged `SE` as a probable typo. **It is not.** The session logs show SE is
the self-evolved adapter variant, one of the paper's listed contributions, and it is the
headline cell for the +0.069 gain. It was simply never defined in this document. v9:

> Vanilla and SE, the self-evolved adapter variant, are unaffected by this prefix.

**Related, and the item on this page I most want you to look at:** the efficiency bullet.

I first rewrote v8's vague "(best adapter cells)" as "for the hand-designed adapter
cells", on the strength of a v7 note saying the claim holds for hand-designed cells and
reverses for SE (+7.6% tool calls). Chasing the 22% figure showed that rewrite would have
been **wrong**. From the logs:

> **22%** is SE-prose at -21.7% tool calls, **18%** is X+M at -18.5% wall clock.

SE-prose is a self-evolved cell, not a hand-designed one, and the hand-designed cells top
out around 17.5%. So "hand-designed" plus "22%" is a contradiction, and it is checkable
against the appendix. v9 now reads:

> up to 22% fewer tool calls and 18% less wall-clock time per task on the harder split, taking the best adapter cell for each measure

That is precisely true and discloses that the two figures come from different cells.
Both are held-out, so no split cherry-picking. Note also that there appear to be two
distinct SE variants in the tables, `SE` (+7.6% tool calls) and `SE-prose` (-21.7%);
worth confirming they are what you think they are before posting a number that rests on
the difference.

## MAJOR-4. OpenFOAM section fully replaced with the new results

Old numbers (0.870 SIGA, 0.516 Foam-Agent, 0.379 MetaOpenFOAM) are gone, per your
instruction that the arXiv-version OpenFOAM results are supplanted.

The framing changed, not just the numbers. On text-similarity the gap is now thin
(0.668 vs 0.565), so v9 does not lead with it. It leads with executability
(89.7% vs 10.0% and 22.2%) and states the fairness setup explicitly: same per-task
budget, same bounded real-execution mechanism in the loop, same post-hoc executability
check across all three systems. That matched-conditions statement is new and is the
strongest thing in the data.

Two caveats are stated in the text: the 10-task baseline subset (see INPUT-1), and that
executability measures structural acceptance rather than physical correctness.

**Deliberately omitted: the vanilla collapse** (0.089 seed 1, exactly 0.000 on seeds 2
and 3). Your collaborator's doc attributes it to an unrelated stale-path fix in the same
commit that made a large OpenFOAM source tree browsable, and explicitly scopes it as not
a general claim. It looks like the strongest number available and is the most attackable
one. Tell me if you want it in.

## MAJOR-5. rho = 0.36 corrected to 0.362 with its CI, and Spearman named

v8 gave `rho = 0.36 (interval 0.20 to 0.51)`. The logs show the verified value is
**0.362, 95% CI [0.197, 0.505], p = 0.0001, n = 126**, held-out only. v9 uses 0.362 and
0.197 to 0.505, and labels all three correlations "Spearman rho". Every bare "interval"
is now "95% CI".

## MAJOR-6. "almost exactly" now given a threshold

v8 used "reproduce the reference almost exactly" undefined, while the kEdh section
separately defined "strictly perfect" as above 0.999 for the structural metric. v9 states
the fidelity threshold inline: "46% of running decks reproduce the reference at fidelity
above 0.999."

Sourced from the logs ("Near-exact share is 46% at >= 0.999"). Confirm that threshold is
right before posting.

## MAJOR-10. New "Strengths Identified by Reviewers" subsection in the AC post

Contribution Summary is restored to your clean bullets, verbatim as you supplied them
(including "higher-leverage tasks" and the new "The search process also allows for light
adaptation across domains"). Only a terminal period was added to the cross-domain bullet.

Reviewer attribution now lives in its own subsection directly beneath, sourced from
`neurips_review/siga_neurips_reviews_clean.md` and quoted verbatim:

| Strength | Cited |
|---|---|
| The problem setting | gep1, kEdh, nBNe, plus the meta-review's "reviewers agree that the problem is practically important" |
| Adapters rather than a new agent stack | gep1 |
| The experimental design (factorial + bottleneck analysis) | gep1, nBNe |
| The reliability result | gep1 ("strongest empirical result"), nBNe, kEdh |
| Cross-simulator transfer | nBNe ("a major strength"), kEdh |
| The negative findings | gep1 |
| The human calibration | nBNe |

The subsection is 1,218 characters, six bullets. Each is a claim label followed by short
quoted fragments with the reviewer ID in parens, so the AC can scan the IDs down the
right of each line without reading prose. Written to be skimmed, not read.

Four notes on the framing:

**kEdh appears on three of the six despite recommending reject.** Deliberate, and the
strongest move available: the reject reviewer's own summary supplies the problem
significance, the transfer result and the reliability number. It also sets up section 5,
where we note the review identifies no technical or evaluation concern.

**The human-calibration bullet was cut** in the concision pass. nBNe credits it ("a good
calibration point"), but both gep1 and nBNe criticize its scale, so listing it as a
strength needs a concession attached, and the concession costs more space than the
strength earns. Section 4 addresses it properly. Say the word if you want it restored.

**nBNe is not cited on the adapters bullet**, though it would look natural. nBNe's W1 is
that the paper introduces no fundamentally new architecture, framed as a weakness.
Citing it as support would misrepresent the review. It is answered on its own terms in
the nBNe thread.

**The efficiency figure (22% / 18%) has no reviewer backing** and correctly appears
nowhere in this subsection.

The AC section is 7,734 characters, comfortably under the cap.

## MAJOR-9. Artifact validity stated as proportions, avoiding the X+M denominator

The unexplained "100 of 100" for X+M sat under a sentence claiming 17 runs per cell,
which does not divide. Rather than dig for the true runs-per-cell, v9 reports what is
verified and drops what is not:

> Vanilla produces a well-formed, schema-valid deck on **91.2%** of runs (155 of 170), while S+X and X+M each reach **100%**, across 270 adapter runs with no failures. The 8.8-point gap has a run-and-task clustered 95% CI of +2.9 to +16.5 points, p = 0.0006.

Everything here is confirmed: Vanilla's exact count and its 17-runs-per-cell basis, both
adapter cells at 100%, the 270-run adapter aggregate, the gap, the CI and the p-value.
The only thing removed is the per-cell split of those 270 runs.

The rare-event rigor argument survives, since "270 adapter runs with no failures" carries
it. The repeat-count sentence is now "a much higher repeat count than the 3 runs per cell
used elsewhere" rather than asserting 17 for all three cells, which was only verified for
two of them.

The Simulation Execution denominators (133 of 170, 27 of 30) are independently verified
in the logs and stay as counts.

## MAJOR-7. gep1 trimmed to fit the 10,000 cap

Applying the edits pushed gep1 to 10,394. Cut back to 9,919 by:

- Q3 reduced from a full restatement to two sentences. It sits directly under W2, which
  now carries the detail, so nothing is lost. It is still substantially longer than v8's
  one-line "Strengthened as described in W2", which read dismissively.
- Tightened the OpenFOAM bullet, the limitations paragraph, the Q2b lead-in, and the
  closing line of Beyond GEOS.

No numbers or claims were dropped. If you want any of the fuller wording back, something
else in gep1 has to give.

## MAJOR-8. Tone change in the AC venue-fit answer

v8: "They also recommended rejection despite not highlighting any technical, evaluation,
reproducibility, or ethical issues" plus "we find some decoupling between feedback and
score."

v9:

> The review recommends rejection but does not identify a technical, evaluation, reproducibility, or ethical concern. We are glad to address the writing concerns raised, and we would welcome the reviewer's view on whether those concerns alone motivate the score.

Same point, stated once, and it ends with a question the AC can act on rather than a
complaint. Also removed the bold from "We think our paper matches these criteria", which
read defensive.

---

# The arithmetic, resolved

You were right to push back: none of the numbers are wrong. The bullet quotes three
different pools without labelling them. From session `7d8dc954` (2026-07-28):

| Figure | Actual basis |
|---|---|
| 78.2% Vanilla | **133 of 170**, held-out, 17 runs per cell |
| 90.0% S+X | **27 of 30**, held-out, 3 runs per cell (83.3% S+X+M is 25 of 30) |
| 77 of 77 | `K3_per_run.csv` gated on `ref_clean_converged`, held-out. A different gate: accepted decks on tasks whose reference deck itself converges cleanly |

So 90.0% and 77 were never meant to divide into each other. Same split and same tasks
throughout, so the comparison is fair; only the precision differs. That is now stated in
the text (MAJOR-1).

Two loose ends the logs surfaced, both previously flagged to you and never closed:

**The 77 vs 31 population question.** An earlier pass (`EVAL_WORK_EXPLAINED.md`) reported
31 of 31 from the A2 pass; `K3_per_run.csv` gives 77 of 77 on held-out (and 271 of 271 on
val, not cited because val is contested). The session switched to 77/77 and asked you
whether those are the same population. **That question was never answered.** It is
INPUT-3 below.

**X+M's 100/100 denominator.** Reported at "17 runs per cell" alongside 170/170, but 100
is not 17 x 10. Most likely X+M ran at 10 runs per cell. Not confirmed anywhere in the
logs. INPUT-4.

---

# I did not change these, and you should decide (INPUT NEEDED)

## INPUT-1. SIGA on the matched 10 tasks

SIGA ran 30 tasks; both baselines ran a 10-task subset of the same pool. v9 states both
counts explicitly, which is honest but weaker than a matched comparison.

The per-task SIGA data already exists, so recomputing SIGA's score and executability
restricted to those 10 tasks is a filter, not a re-run. **This is the highest-value
action left.** Drop-in replacement once you have it:

> On the same 10 tasks, SIGA scores X with Y of 10 executable, against Foam-Agent 0.565 (1 of 10) and MetaOpenFOAM 0.276 (2 of 9).

## INPUT-2. The acceptance parity, still omitted

Flagging because it is the one substantive disclosure gap I found, not to re-litigate it.

Under the originally shipped configuration, Vanilla and S+X were statistically tied on
deck acceptance: 133 vs 132 of 170. The 90.0% arises only after swapping
`xmllint --schema` for `geosx --validate-input` inside the adapter loop. The session's
own analysis note read: "The schema gap does NOT carry through to loading. Report this
plainly, do not let schema validity stand in for execution."

You directed that this be dropped, and it has been absent since v5. It is still absent in
v9. Worth knowing that gep1 asked the score-moving version of this question, so gep1 is
the one thread where a reviewer might expect it. One clause would cover it. Your call,
and I have not added it.

## INPUT-3. Is 77 of 77 the same population as 31 of 31?

See above. If they are different populations, 77/77 should revert to 31/31.

## INPUT-4. X+M's denominator. RESOLVED by switching to proportions, no lookup needed

Superseded. Rather than chase the runs-per-cell for X+M through the logs or the Spring
artifacts, artifact validity is now stated as proportions plus the verified aggregate.
See MAJOR-9. Nothing further is needed from you here.

## INPUT-5. The LAMMPS judge scale

v9 carries an inline marker: `[CONFIRM: state the judge scale, e.g. 0 to 10]`.
"Judge scores move from 4.56 to 7.78" is uninterpretable without it. **This is the only
placeholder left in the file and must be resolved before posting.**

## INPUT-6. Is there a W3?

Both gep1 and nBNe jump W2 to W4 or Q2 with no W3 addressed. If the reviews have a W3,
the silent gap is conspicuous. I could not verify against the actual reviews.

## INPUT-7. Cross-reference consistency

Three different pointers to what may be the same companion study: "Appendix J" (AC),
"Appendix J, with results in Section 4.6" (gep1), "Section 6.4" (nBNe). Needs checking
against the submitted PDF. Left as-is.

## INPUT-8. Foam-Agent's failure mode

5 of 10 Foam-Agent tasks failed on malformed structured output from deepseek-v4-flash,
with no retry path. A retry patch was drafted, tested, then reverted at your direction to
report out-of-box behavior. That is defensible, but I would say it in one clause:

> reported as shipped; several Foam-Agent failures trace to its lack of retry on malformed structured output rather than to its agent design

If the Foam-Agent authors or a reviewer find this unstated, it reads as stacking the
deck. Not added.

## INPUT-9. Backbone model difference

The OpenFOAM work uses `deepseek/deepseek-v4-flash` via OpenRouter. If GEOS uses a
different backbone, the transfer claim spans a simulator change and a model change at
once. One clause would neutralize it. Not added.

---

# Minor changes applied (no review needed unless something looks wrong)

**Global.** Stripped all backslash escapes. Normalized curly quotes to straight.
en-GB to en-US ("judgements" to "judgments", "instalment" gone). Removed all em dashes
and en dashes. "camera-ready" / "manuscript revisions" / "revised version" all unified to
"the revision". Section separators retitled from internal filenames
(`ac_response_latest`) to readable headings, with the now-duplicate
`## Response to Reviewer gep1` lines removed. Heading depth normalized: `#` section,
`##` items. References unified to short form in all four sections. Reference [5] author
names de-mangled (`Zhehao, D. O. N. G.` to `Dong, Z.`). `[6] [7]` to `[6, 7]`.
All trailing whitespace stripped.

**Grammar and factual fixes.** "Reviewer 1" corrected to "Reviewer gep1" (nBNe). The
predicate-less sentence at nBNe Q2 rewritten. "Does the simulation run to completion and
the solver converges?" fixed. "the physics are fixed" to "is fixed". "this criteria" to
"these criteria". "point at" to "point to". The Q2a delta reordered so it is presented in
the direction it is computed (0.917 without vs 0.913 with). Comma splices at kEdh W2 and
the garbled line-290 sentence rewritten. The broken parallelism at nBNe Q2 ("motivated
our discussion and including") fixed.

**Formatting.** The empty `> ` blockquote line that split the Buckley-Leverett example
into two boxes is fixed into one quotation. The Resolution-IV replacement text is now
blockquoted, matching the other three proposed replacements in that section. The nBNe
metrics bullets flattened to the same three parallel items used in the other sections.
The Table 1 empty cell filled with "n/a". The orphan "New Metrics" line in the AC section
made a proper lead-in. AC section headings unified to sentence case and the venue-fit
section numbered as 5.

**Wording.** The garbled "run counts balloon with various ablations ... and other
experiments on backbone models, and harnesses" rewritten in all three copies. "The
direction reinforces our conclusions" to "favors". "Its details are largely unimportant
for discussion purposes" softened. "e.g. ... etc." redundancy removed in both places.
`buckleyLeverettProblem` used consistently where v8 alternated with "the Buckley-Leverett
task". The LAMMPS mechanism described identically in gep1 and nBNe (v8 said "knowledge
injection" in one and "memory and retrieval" in the other).
