<!-- v4r2 DRAFT 2026-07-28. Companion Official Comment to the AC, posted alongside AC.md.
     AC.md carries the contribution recap and meta-review bullets 1 (structural evaluation) and
     2 (clarity). THIS post carries the construction and full numbers behind the extended
     evaluation, then bullets 3 (scale) and 4 (human comparison) and the kEdh point.
     Split because the two together exceed the 10,000 char cap.
     NUMBERS RE-VERIFIED this session from sprint_artifacts.tar.xz (K3_per_run.csv,
     K3_correlations.csv, L1_report.txt, L2_report.txt).
     Style: no em dashes, no links, no arXiv mention, VERIFIED numbers only.
     Prose ~8,000 chars. HARD CAP 10,000. -->

A companion to our main response, giving the construction and the full numbers behind the extended evaluation, then the two remaining points of the meta-review.

## The extended evaluation protocol, in detail

**Level 3, and a finding that changed our tooling.** GEOS's own documentation recommends validating input with `xmllint --schema`, and that is what we built into the adapter. The two are not equivalent: of 180 held-out decks, 49 pass `xmllint --schema` but are refused by `geosx`, on exactly the cross-reference and arity errors our bottleneck analysis reports as unfixed by any adapter. The defects were present; the validator we chose could not see them. Swapping in the simulator's own check, `geosx --validate-input` at about 2.5 s per deck, with everything else held constant, the agent repairs the newly surfaced defects: acceptance rises from **76.7% to 90.0%** for S+X and from **80.0% to 83.3%** for S+X+M. The general lesson, useful beyond this paper, is that a simulator's documented validation advice is not necessarily a sufficient acceptance test for that simulator.

**Level 4, convergence.** On the tasks whose reference deck itself converges cleanly, **every held-out deck GEOS accepted also ran to completion and converged, 77 of 77**. Loading is the binding constraint rather than solving, which means the cheap 2.5 second acceptance check captures nearly all of the execution signal.

**Level 5, output reproduction.** We built an output-side metric that injects an identical output block into the reference and the candidate deck, runs both, and compares mesh-independent reductions of each physical quantity normalised by the reference's own scale, with no interpolation anywhere. The reference alone fixes which quantities count, so the metric cannot be gamed, and a missing quantity scores zero. We ran it over 489 runs on 18 tasks. On the held-out split, **mean output fidelity conditional on the deck running is 0.958**, 46% of running decks reproduce the reference almost exactly, and structural similarity predicts output fidelity at rho = 0.36 (interval 0.20 to 0.51, p = 0.0001). The distance between structure and physics therefore sits in decks that fail to run rather than in decks that run and are wrong, which is what our reliability framing predicts.

**The semantic axis, which is the plausibility metric proper.** We built a section-level LLM judge: for each canonical GEOS section it sees the reference, the candidate and the task brief, and returns an ordinal materiality verdict rather than a number. Four judges from four model families, none of them the agent's backbone, blind to condition, with presentation order swapped. Validated against the level-5 simulation outputs above, **the judge's score on the physics-bearing sections predicts actual output fidelity at rho = 0.418 (p = 0.0006)**, and the `Solvers` subtree alone reaches rho = 0.456 (p = 0.0007), which identifies where structural error actually propagates into physical divergence. Two results keep us from offering it as a finished instrument: it does not beat plain TreeSim at predicting fidelity (paired difference -0.040, interval -0.257 to +0.166), and two of the four judges ordered the conditions differently. We also tested the obvious deterministic alternative, re-weighting TreeSim toward physics-bearing sections, which gives at most a small improvement (+0.033, interval -0.003 to +0.072), while restricting to physics sections alone does no better than a random subset of the same size. Uniform weighting therefore now rests on a test rather than an assumption.

One result from the judge runs in the paper's favour: roughly two-thirds of the attribute mismatches TreeSim penalises as total mismatches are judged physically immaterial. Together with 0.958 output fidelity among running decks, this indicates our reported structural numbers are conservative rather than generous.

**What remains for follow-up.** A validated plausibility metric needs a purpose-built benchmark with expert-labelled ground truth, and the choice of which quantities matter for a given physics problem is a domain judgement we are working through with simulator developers rather than asserting. That is a scope statement about the next study, not a hedge about this one.

## 3. Limited experimental scale

**The GEOS benchmark is larger than the paper makes it look.** It is 27 evaluated tasks, 17 validation plus 10 held-out, all evaluated across all cells. The split exists to give the self-evolution setup a clean train and test separation, not because the validation tasks go unevaluated, and we will present both splits together.

**On representativeness**, we would rather describe the held-out set than defend it as a random sample. Its gain decomposes into two catastrophic-failure rescues plus one task that fails universally in every cell; the remaining seven held-out tasks have a Vanilla mean of 0.898, close to the validation set's 0.910. So the held-out set is in-distribution tasks plus a hard tail, and what the evidence supports is a hard-tail reliability effect: fewer failed decks rather than better decks. We will adopt that narrower phrasing.
<!-- [[BLOCKED: H19 - how far to walk back the reliability claim. Task-clustered interval on the +0.069 mean lift is [-0.009, +0.166] if you want it given to the AC, who did ask for uncertainty estimates. Currently not printed.]] -->

**On scale beyond GEOS**, both transfer studies are now larger, with numbers in full on gep1's thread. OpenFOAM runs 30 tasks with a second simulator-native baseline: every SIGA cell returns a complete case on all 30 with no zero-score outputs (best cell 0.870), against Foam-Agent at 0.516 (19 of 30 complete) and MetaOpenFOAM at 0.379 (10 of 30). LAMMPS is added as a third simulator, whose input is a command script with no formal schema, testing whether the recipe is tied to XML. The reliability effect, which is the paper's actual claim, replicates on all three interfaces.

## 4. Human comparison too small

We agree that the human baseline is small and is primarily a preliminary calibration, and we will label it that way throughout, removing comparative time-savings language from the abstract and introduction. The reason for its size is worth stating: the task requires PhD-level geophysics knowledge and is extremely time consuming for human scientists, taking about three hours on an easier and smaller task, which makes this baseline far harder to scale than a typical human evaluation.

## On the concern raised by Reviewer kEdh

We answer this in full on that thread and note two points here. The review flags no technical flaw, no evaluation weakness, no reproducibility gap and no novelty concern, and its strengths section credits the contribution; the NeurIPS rating-2 description is "a paper with technical flaws, weak evaluation, inadequate reproducibility and incompletely addressed ethical considerations." And on venue, NeurIPS 2026's own contribution-type guidance defines the Use-Inspired type as work whose main contribution is in framing or designing approaches to meet the needs of a specific real-world application, often involving engaging with domain experts. That is this paper, and all three reviewers independently classified it Use-Inspired.

We thank the AC again for the clear criteria, and we are glad to answer anything further during the discussion period.
