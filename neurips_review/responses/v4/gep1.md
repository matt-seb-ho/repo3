<!-- v4 DRAFT 2026-07-28. Reviewer gep1 (Reviewer 1): rating 4 (borderline accept), confidence 3.
     Carries the FULL evaluation discussion (decision A1). gep1 CANNOT see our AC comment,
     so never point there. nBNe is pointed here.
     This is the primary "Rebuttal": W1/Q1, the evaluation question. Everything else (Q2a prefix bug,
     Q2b S/X separation, W2 scale, Q3 OpenFOAM, Q4 human comparison, limitations wording) is in the
     companion gep1_post2.md because the two together exceed the 10,000 char cap.
     Style: no em dashes, no links, no arXiv mention, VERIFIED numbers only, no "ladder/rung".
     Prose length ~7,700 chars. HARD CAP 10,000. -->

## Response to Reviewer gep1

We thank the reviewer for an unusually actionable review. Both score-moving items were specific enough to act on directly, and we did: we ran the execution evaluation asked for in Q1, and we bounded and separated the confounds raised in Q2. This comment answers W1 and Q1, which is the longest of the three. A companion comment posted alongside it answers Q2 (the prefix bug and the S/X separation), W2 (scale and seeds), Q3 (OpenFOAM), Q4 (the human comparison) and the limitations wording.

### Response to W1 and Q1, evaluation beyond structure [score-moving]

Two parts: why a structural metric fits the task this benchmark poses, and what we found when we went past it.

**Part 1: the scope of the task.** Each task brief states the domain geometry, material parameters, boundary conditions and requested outputs in domain language: a permeability of 9.0e-13 m2 in all directions, a reference porosity of 0.2 at 10 MPa, and so on. What the brief never does is name a single GEOS XML element. The agent has no property database, literature access or online source, and is not asked to decide what the physics should be. Its job is translation: expressing a well-specified modeling intent in the simulator's DSL, scored against a hand-validated reference deck. Under that scope, whether the agent produced the right deck is substantially a structural question, and TreeSim answers it deterministically and cheaply enough to run on every cell of a factorial design, which neither an execution-based nor a judge-based metric is at our budget.

**Part 2: what we ran since submission.** We now evaluate along two axes: the deck as an artifact (well-formed, schema-valid), and what the simulator does with it (loads, converges, reproduces the reference outputs).

| Held-out check | Vanilla | S+X | X+M |
|---|---|---|---|
| Well-formed and schema-valid (17 runs per cell) | 155 / 170 | **170 / 170** | **100 / 100** |
| GEOS accepts and loads the deck (`geosx -v -i`) | 133 / 170 | 132 / 170 | |
| Runs to completion and converges, given it loads | **77 / 77** (all cells pooled) | | |

We re-ran the artifact check at 17 runs per cell rather than 3, because these are counts of rare events and three runs estimate them poorly. The artifact-level gap is 8.8 points, with a run-and-task clustered interval of +2.9 to +16.5 points (p = 0.0006), and 270 adapter runs with no failures at all. One point of precision on the name: 10 of the 15 baseline failures are well-formedness errors, chiefly nested XML comments, rather than schema errors.

**The acceptance check does not inherit that gap, and we would rather say so than let the artifact numbers stand in for execution.** GEOS accepts 133 Vanilla decks and 132 S+X decks out of 170. **We claim no execution-level advantage between conditions**, and the reliability claim does not need one. What the third row does establish is worth having for anyone building this kind of benchmark: of the held-out decks GEOS accepted on tasks whose reference deck itself converges, **every one ran to completion and converged, 77 of 77**. Loading is the binding constraint, not solving, so a 2.5 second acceptance check captures nearly all of the execution signal.

**Why rows one and two disagree is the most useful thing we learned in this period.** GEOS's own documentation recommends validating input with `xmllint --schema`, and that is what we built into the adapter. The two checks are not equivalent: across the 180 held-out decks, **49 pass `xmllint --schema` but are refused by `geosx`**. What `xmllint` cannot see are cross-reference and arity errors: a PVT model named in one file but absent from the deck, a constitutive model missing on a named subregion, a component-count mismatch between two blocks. That class is exactly the residual failure mode our bottleneck analysis reports as unfixed by any adapter, and the diagnosis is now concrete: the defects were present, and the validator we chose could not see them. It also explains the second row directly. The stop hook was certifying decks the simulator would refuse, so there was nothing in the acceptance rate for it to improve.

**We have implemented the swap and run it.** Replacing `xmllint --schema` with `geosx --validate-input` inside the verification loop, at about 2.5 seconds per deck, holding everything else constant:

| Cell (3 runs, 10 held-out tasks) | Accepted, `xmllint` in the loop | Accepted, `geosx` in the loop |
|---|---|---|
| S+X | 23 / 30 | **27 / 30** |
| S+X+M | 24 / 30 | **25 / 30** |

The blocks the new validator raises are the errors described above, and the agent repairs them: in one case it added a missing thermal conductivity model to the region that referenced it, a cross-reference defect no schema check can express. The general lesson, useful beyond this paper: a simulator's documented validation advice is not necessarily a sufficient acceptance test for that simulator, and a benchmark that trusts it will certify decks the simulator refuses.

**Output fidelity.** We also built an output-side metric and ran it across 489 runs on 18 tasks, reporting the held-out split here. It injects an identical output block into the reference and the candidate deck, runs both, and compares mesh-independent summaries of each physical quantity (min, max, mean, root-mean-square over all cells at final time), normalised by the reference's own scale, with no interpolation at any point. The reference alone fixes which quantities count and what the scale is, so the metric cannot be gamed by emitting more or fewer outputs, and a missing quantity scores zero.

On the held-out split, structural similarity predicts output fidelity at a rank correlation of 0.36 (interval 0.20 to 0.51, p = 0.0001). The more informative result is conditional: **among held-out decks that run, mean output fidelity is 0.958, and 46% reproduce the reference almost exactly.** The distance between structure and physics is concentrated in decks that fail to run rather than in decks that run and are wrong, which is consistent with the reliability framing the reviewer credits in the strengths section.
<!-- [[BLOCKED: H22 — whether to volunteer rho = 0.31 at all. Kept here because gep1 asked the sharpest version of this question and the conditional 0.958 is the persuasive number either way. Cut the sentence containing 0.31 if the answer is no.]] -->

**What we are not offering, and why.** We agree with the reviewer that physical plausibility is the right direction, and we tested candidates rather than only promising them. We re-weighted the structural metric toward physics-bearing sections (`Solvers`, `Constitutive`, `FieldSpecifications`), which yields at most a small improvement (+0.033, interval -0.003 to +0.072), while restricting to those sections alone predicts output fidelity **no better than a random subset of the same size** (51st percentile of the random null). We also built a section-level semantic judge that compares candidate against reference one canonical GEOS section at a time, returning an ordinal materiality verdict rather than a number, with four judges from model families other than the agent backbone, blind to condition and order-swapped. Validated against the simulation outputs above, its score on the physics-bearing sections predicts actual output fidelity at rho = 0.418 (p = 0.0006), and the `Solvers` subtree alone reaches rho = 0.456 (p = 0.0007), which locates where structural error propagates into physical divergence. Two results keep us from offering it as a finished metric: it does not beat plain TreeSim at predicting fidelity (paired difference -0.040, interval -0.257 to +0.166), and two of the four judges ordered the conditions differently.

We report both as tests rather than as results, because they change the standing of the metric the reviewer is asking about: **uniform section weighting now rests on a test rather than on an assumption**, and the most plausible alternative was tried and did not beat it. A validated plausibility metric needs a purpose-built benchmark with expert-labelled ground truth, and that collaboration with simulator developers is under way. That is a statement about the scope of the next study rather than a hedge about this one.

One result from that work runs in our favour: independently of condition, roughly two-thirds of the attribute differences TreeSim scores as total mismatches are judged physically immaterial. Combined with 0.958 fidelity among running decks, this suggests the paper's absolute structural numbers are conservative rather than generous.

We are grateful for a review that told us precisely what evidence would move the score, and we hope the results above meet it. Our companion comment answers the remaining points.
