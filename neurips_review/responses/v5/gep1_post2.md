<!-- v5 DRAFT 2026-07-28. Unchanged from v4. Companion Official Comment on gep1's thread, posted alongside gep1.md.
     gep1.md carries W1/Q1 (evaluation) and both parts of Q2 (prefix bug, S/X separation).
     THIS post carries W2 (scale and seeds), Q3 (OpenFOAM), Q4 (human comparison) and the
     limitations wording. Split because the two exceed the 10,000 char cap.
     The limitations section is KEPT but rewritten: the reviewer asked for that wording explicitly,
     so granting it is cheap goodwill, but v5r2 states it forward-looking rather than as a
     concession, and updates it for the execution and output-side results we now have.
     Style: no em dashes, no links, no arXiv mention, VERIFIED numbers only.
     Prose length ~8,500 chars. HARD CAP 10,000. -->

## Response to Reviewer gep1, part 2

This companion comment answers W2, Q3, Q4 and the limitations request. Our main response on this thread answers W1 and Q1 on evaluation, and Q2 on the two confounds.

### Response to W2, statistical and experimental scale

Three things: a clarification we owe the reviewer, what the existing data supports, and what is larger since submission.

**The GEOS benchmark is 27 evaluated tasks, not 10.** It is 17 validation plus 10 held-out, all evaluated across all cells. The split exists to give the self-evolution setup a clean train and test separation, not because the validation tasks go unevaluated. The paper foregrounded the held-out subset in a way that made the benchmark look smaller than it is, and we will present both splits together. We are also working with GEOS developers to expand it.

**What the held-out data supports.** We would rather characterise that set than defend it as a random sample. The held-out gain decomposes into two catastrophic-failure rescues plus one task that fails universally in every cell at 0.013; the remaining seven held-out tasks have a Vanilla mean of 0.898, close to the validation set's 0.910. So the held-out set is in-distribution tasks plus a hard tail, and what the evidence supports is a **hard-tail reliability effect: fewer failed decks rather than better decks.** That is narrower than the paper's current phrasing and we will adopt it, in the abstract as well as the results section.

The supporting contrast is not a mean. Per-cell across-run standard deviation is 0.081 for Vanilla against 0.002 (S+X), 0.005 (X+M) and 0.012 (SE). At 17 runs per cell, 15 of 170 Vanilla runs emit a deck that is not well-formed or not schema-valid, against 0 of 270 adapter runs. And the per-task pattern matches the mechanism the paper describes: SE is higher on 7 of 10 tasks, tied on 1 and lower on 2, with a median difference of +0.022 against a mean of +0.069, so the two rescues carry the mean.
<!-- [[BLOCKED: H19 — how far to walk back the reliability claim. Current text: "fewer failures, not better decks", hard tail, no bootstrap interval printed. The task-clustered interval on the +0.069 mean lift is [-0.009, +0.166]; (task, seed) i.i.d. gives [+0.001, +0.155]. Add if you want the interval stated to gep1. ]] -->

**Scale beyond GEOS.** Both transfer studies are larger than the submitted version.

*OpenFOAM, 5 tasks to 30, with a second simulator-native baseline.* The best SIGA cell reaches 0.870, and every SIGA cell produces all required files on all 30 tasks with no zero-score outputs. Two purpose-built native agents fail exactly there: Foam-Agent reaches 0.516 (19 of 30 with full coverage, 8 zero-score) and MetaOpenFOAM 0.379 (10 of 30, 12 zero-score). At this scale the informative contrast is a general harness with interface grounding against agents built for that simulator.

*LAMMPS, a third simulator.* 9 molecular-dynamics tasks on two backbone models. LAMMPS input is a sequential command script with no formal schema, which tests whether the recipe is tied to XML. It is not, but the binding component shifts: scripts are structurally complete almost everywhere (structural score at least 0.976 across all 12 configurations), so the gain comes from knowledge injection rather than completion enforcement. Judge scores move from 4.56 to 7.78 on one backbone and from 6.33 to 6.89 on the other.

Both remain single-run, and we present them as qualitative transfer evidence rather than as second and third benchmarks. The point we would emphasise is that the effect the reviewer singled out as our strongest result, the reduction in catastrophic failures, replicates on all three interfaces, and that the component analysis correctly predicts where it should not help.

### Response to Q3, strengthening the OpenFOAM study

We have strengthened it as described above, and we accept the reviewer's fallback in full. Foam-Agent's execute mode did not run in our environment, so that comparison remains lint-only, and we will state this in the main text rather than in a footnote. Both transfer studies remain single-run and we will keep the transfer claims explicitly qualitative.

### Response to Q4, the human comparison

We agree, and we will (i) relabel it "preliminary calibration" throughout, (ii) remove comparative time-savings language from the abstract and introduction, and (iii) state that it establishes the existence of an effect on one task rather than any ranking of humans against the agent. The reason it is small is worth stating: the task requires PhD-level geophysics knowledge and is extremely time consuming for human scientists, which makes this baseline far harder to scale than a typical human evaluation.

One observation we offer without leaning on it. The task used, `buckleyLeverettProblem`, is a 1D two-phase verification case with a known analytical solution and sits at the easy end of our benchmark, and it still took a domain expert new to GEOS about three hours. An easy task should if anything understate the value of automation, since the same developers' written estimate rises to a couple of days for compound multiphysics decks, which is where our held-out result lives.

### Limitations wording

We are glad to sharpen this in the main body, and we would frame it around scope rather than around what the metric lacks.

For the task scope this paper studies, a structural metric is the right primary measure. The brief supplies the physics in domain language, the reference decks are hand-validated, and the task pool is mined from GEOS's own advanced examples and tutorials, so the specification and its provenance are what establish that a target simulation is physically meaningful and useful. Agreement with that reference is therefore agreement with a simulation the simulator's own developers stand behind, and what our headline numbers measure is how reliably the agent reaches it: fewer unevaluable outputs and lower across-run variance on compound multiphysics tasks.

What we will add is the scope statement in the other direction. As we widen the agent's responsibility to handle ambiguity and demand less of the user, physical plausibility becomes a first-order question rather than one settled by the specification, and that is why we are extending the evaluation protocol alongside the task scope. The preliminary results in our main response are the first instalment: every held-out deck GEOS accepted ran to completion and converged, decks that run reproduce the reference at 0.958 mean fidelity, and a section-level plausibility judge tracks measured output fidelity. Saying both halves plainly is a more accurate limitations paragraph than either alone.

We are grateful for a review that told us precisely what evidence would help, and we hope the results above meet it.
