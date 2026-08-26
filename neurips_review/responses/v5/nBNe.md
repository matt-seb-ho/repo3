<!-- v5 DRAFT 2026-07-28. Reviewer nBNe (Reviewer 3): rating 5 (accept), confidence 5.
     Rule: answer the three questions, concede gracefully, change nothing else. Do NOT re-argue novelty.
     CHANGED FROM v4: the Q1 evaluation answer is cut back to a brief summary plus a pointer to our
     Reviewer 1 response, per researcher direction. Reviewers CAN see each other's per-review threads
     in Phase 2, so this cross-reference is safe. Never refer a reviewer to our AC comment.
     Style: no em dashes, no links, no arXiv mention, VERIFIED numbers only.
     Prose length ~6,000 chars. HARD CAP 10,000. -->

## Response to Reviewer nBNe

We thank the reviewer for the careful reading and the positive assessment. All three questions point at things we agree with, and we answer them directly.

### Response to Q1: convergence checks and output validation

We agree, and since this was the most common thread across the reviews we made it our first priority. We now evaluate a deck at five levels of strictness, from well-formed XML through schema validity, acceptance by GEOS itself, convergence, and reproduction of a reference run's outputs, plus a semantic axis in which an LLM judge rates each deck section against the reference for physical materiality. Two results are worth stating here. **Acceptance is the binding constraint rather than solving**: every held-out deck GEOS accepted also ran to completion and converged, 77 of 77. And **among held-out decks that run, mean output fidelity against the reference is 0.958**, with 46% reproducing the reference almost exactly, so the gap between structural and physical correctness sits in decks that fail to run rather than in decks that run and are wrong.

**Please see our response to Reviewer 1 for the full treatment**, which gives the protocol, the construction of the output metric, and all numbers including where they do not favour us. In short, we do not claim an execution-level advantage between conditions, and turning the semantic judge into a validated plausibility metric requires calibration against expert-labelled ground truth, which needs sustained domain-expert input and a purpose-built benchmark. That is the follow-up work this question points at, and we agree it is the right direction.

### Response to Q2: levels of human expertise and a collaborative setting

We agree the human comparison is small and primarily a preliminary calibration, and we will label it that way throughout, removing the comparative time-savings language from the abstract and introduction. The reason for its size is worth stating: the task requires PhD-level geophysics knowledge and is extremely time consuming for human scientists, taking about three hours on an easier and smaller task, which makes this baseline far harder to scale than a typical human evaluation.

The reviewer's stronger design, multiple tasks spanning several levels of GEOS experience, is the right one, and we agree that a **collaborative** setting is the more realistic deployment mode than either the fully manual or fully autonomous conditions we measured. Both go into future work explicitly rather than as a passing mention.

One observation from our own data supports the reviewer's instinct about interactivity, and also shows why it needs a different task design. In a companion study we gave the agent an explicit channel for consulting a human expert, and progressively removed information from the task brief. The agent used the channel in only 2 of 64 trials, because the on-disk example library acted as a cheaper substitute for asking. Eliciting genuine collaboration therefore requires tasks whose missing information cannot be recovered from accessible examples, which is itself an open benchmark-design problem. We now say so explicitly.

### Response to Q3: the exact Claude Code version

The version is **2.1.119**. We confirmed it from the harness's own initialisation records rather than from memory: all 903 initialisation events across the campaign report that version, with no exceptions.

We also owe a concession that reinforces the reviewer's point. Our container installed the Claude Code package **unpinned**, so the version tracked image build time rather than being fixed by configuration. That is exactly the fragility the question is aimed at. We will pin it and report both the harness version and the container digest.

### Response to W1: no fundamentally new agent architecture

We agree, and it is deliberate. The question we set out to answer is how much of the gap can be closed by wrapper-level grounding around an unmodified harness, without retraining. A result there is informative precisely because the intervention is cheap: a large effect argues against rebuilding an agent loop for every new scientific target, and a small one would have been worth knowing too.

### Response to W2: TreeSim is structural

Please see Q1 above for the execution results. We would add the scope argument, which we should have made explicitly in the paper. Each task brief states the geometry, material parameters, boundary conditions and requested outputs in domain language (a permeability of 9.0e-13 m2 in all directions, a reference porosity of 0.2 at 10 MPa) and never names a single GEOS XML element. The agent has no property database, literature access or online source, and is not asked to decide what the physics should be. Its job is translation, from a well-specified modeling intent into the simulator's DSL, scored against a hand-validated reference deck, and under that scope whether the agent produced the right deck is substantially a structural question. We agree that a broader scope, one that supplies the agent with less and asks it to recover more, makes physical plausibility the central question, and that is the direction of the follow-up work described in Q1.

### Response to W4: task set size and diversity

Two clarifications and an update.

First, the GEOS benchmark is **27 evaluated tasks**, 17 validation plus 10 held-out, all evaluated across all cells. The split exists to give the self-evolution setup a clean train and test separation, not because the validation tasks go unevaluated; the paper foregrounded the held-out subset in a way that made the benchmark look smaller than it is. We are working with GEOS developers to expand it further.

Second, since submission we have grown OpenFOAM from 5 tasks to 30 with a second simulator-native baseline, and added **LAMMPS as a third simulator** (9 molecular-dynamics tasks, two backbone models). This speaks to the reviewer's point about diverse task types as well as scale: LAMMPS input is a sequential command script with no formal schema, so it tests whether the recipe is tied to XML. It is not, but the binding component shifts, because LAMMPS scripts are already structurally complete almost everywhere (structural score at least 0.976 across all 12 configurations), so the gain comes from knowledge injection rather than completion enforcement. On OpenFOAM at 30 tasks, every SIGA cell returns a complete case with no zero-score outputs, while the simulator-native Foam-Agent leaves 11 tasks and MetaOpenFOAM 20 tasks incomplete. Both transfer studies remain single-run and we keep those claims explicitly qualitative.

The reviewer cited cross-simulator transfer and the reduction in complete failures as the paper's major strengths, so we would note that both now hold at larger scale, and that the component analysis correctly predicts where the effect should not appear.
