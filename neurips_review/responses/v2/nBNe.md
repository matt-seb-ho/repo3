<!-- v2r2 DRAFT 2026-07-27. Reviewer nBNe: rating 5 (accept), confidence 5.
     SELF-CONTAINED by design: carries a condensed evaluation summary inline so it works whether or not
     01_evaluation.md can be posted globally. Rule: answer the three questions, concede gracefully,
     change nothing else. Do NOT re-argue novelty.
     Style: no em dashes; no "ladder"/"rung"; no non-significance callouts.
     CHANGED FROM v2r1: dropped bootstrap CI; added cross-simulator reliability + efficiency.
     Target ~6,000 prose chars. HARD CAP 10,000. -->

## Response to Reviewer nBNe

We thank the reviewer for the careful reading and for the positive assessment. All three questions point at things we agree with, and we answer them directly.

### Response to Questions

> Q1: Adding convergence checks and output validation from the simulator may strengthen the claim of the paper.

**Response to Q1:** We agree, and since this was the most common thread across the reviews we made it our first priority. We evaluate deck correctness at five increasing levels of strictness: the deck is well-formed XML, it is schema-valid against the GEOS XSD, GEOS accepts and loads it, the simulation runs and the solver converges, and quantities of interest match a reference run. The paper reports the first two. We have now run the third and fourth across all six held-out cells (10 tasks x 3 runs per cell).

| | Vanilla | Best SIGA cell |
|---|---|---|
| Schema-valid | 24 / 30 | **30 / 30** (all five adapter cells) |
| GEOS accepts and loads | 19 / 30 | **23 / 30** |
| Runs and converges, given it loads | 31 / 31 | 31 / 31 |

Two readings. **Loading is the binding constraint, not solving**: every deck GEOS accepted also converged, 31 of 31, on the tasks whose reference deck itself converges. And the reliability ordering is preserved at every level, from XML well-formedness through to convergence.

We also learned something during this work that we did not have at submission, and it is the most useful result of the period. GEOS's own documentation recommends validating input with `xmllint --schema`, and that is what we built into the adapter. **The two checks are not equivalent**: across 180 held-out decks, 49 pass `xmllint` but are refused by `geosx`. What `xmllint` cannot see are cross-reference and arity errors, for example a PVT model named in one file but absent from the deck, or a component-count mismatch. That is exactly the residual failure class our bottleneck analysis reports as unfixed by any adapter, and it gives a concrete diagnosis: the defects were present, the validator we chose could not see them. We have implemented the swap to `geosx --validate-input` (about 2.5 s per deck) and experiments with it in the loop are running now.

On the output validation the reviewer asks for specifically, we are building it as a standing metric rather than a one-off check: a mesh-independent, scale-free similarity measure between the simulation outputs of a candidate deck and those of the reference deck. We would rather report it properly than gesture at it, and we will post results during the discussion period. We are also validating a section-level semantic judge (comparing candidate against reference one canonical GEOS section at a time, scored by a model from a different family than the agent backbone, so self-preference is not a confound).

> Q2: Adding different levels of human expertise and also a human-agent collaborative setting in the baseline would make the paper better, as practitioners are likely to use such systems interactively.

**Response to Q2:** We concede both. Our human comparison is two participants on one task at the easy end of the benchmark. It is preliminary calibration rather than a baseline, and we will label it that way throughout, removing the comparative time-savings language from the abstract and introduction.

The reviewer's stronger design, multiple tasks spanning several levels of GEOS experience, is the right one. We also agree that a **collaborative** setting is the more realistic deployment mode than either the fully manual or fully autonomous conditions we measured, and it is the mode we care about. Both go into future work explicitly rather than as a passing mention.

One observation from our own data that supports the reviewer's instinct about interactivity. In a companion study we gave the agent an explicit channel to consult a human expert and progressively removed information from the task brief. The agent used the channel in only 2 of 64 trials, because the on-disk example library acted as a cheaper substitute for asking. Eliciting genuine collaboration therefore requires tasks whose missing information cannot be recovered from accessible examples, which is itself an open benchmark-design problem, and we now say so explicitly.

> Q3: The authors should report the exact Claude Code version, since results may depend on both the underlying model and the coding agent environment.

**Response to Q3:** The version is **2.1.119**. We confirmed it from the harness's own initialisation records rather than from memory: all 903 initialisation events across the campaign report that version, with no exceptions.

We also owe a concession that reinforces the reviewer's point. Our container installed the Claude Code package **unpinned**, so the version tracked image build time rather than being fixed by configuration. That is exactly the fragility the question is aimed at. We will pin it and report both the harness version and the container digest.

### Response to Weaknesses

> W1: The paper does not introduce a fundamentally new agent architecture; it is based on existing ideas and the method depends on existing simulator structure.

**Response to W1:** We agree, and it is deliberate. The question we set out to answer is how much of the gap can be closed by wrapper-level grounding around an unmodified harness, without retraining. A small result there is informative precisely because the intervention is cheap, and a large one argues against rebuilding an agent loop for every new scientific target.

> W2: TreeSim is good for structural similarity, but scientific simulations need numerical stability and physically meaningful output.

**Response to W2:** Please see Q1 above for the execution results. We would add the scope argument, which we should have made explicitly in the paper.

**In our benchmark the physical values are supplied by the user.** Each task brief states the domain geometry, material parameters, boundary conditions and requested outputs in domain language: a permeability of 9.0e-13 m², a reference porosity of 0.2 at 10 MPa, and so on. What the brief never does is name a single GEOS XML element. The agent is not connected to property databases, the literature, or any online domain source, and is not asked to decide what the physics should be. Its job is translation, from a well-specified modeling intent into the simulator's DSL, and under that scope whether the agent produced the right deck is largely a structural question against a hand-validated ground truth.

We agree that a broader scope, one that supplies the agent with less and asks it to recover more, makes physical plausibility the central question rather than a secondary one. Judging individual deck values for plausibility needs a purpose-built benchmark and sustained domain-expert involvement, a longer effort than this window allows. We are pursuing both: expanding the task scope, and improving the evaluation for the current scope.

> W4: The task set is relatively small. The paper would be much stronger with a larger benchmark with more diverse task types.

**Response to W4:** Two clarifications and an update.

First, the GEOS benchmark is **27 evaluated tasks**, 17 validation plus 10 held-out, all evaluated across all cells. The split exists to give the self-evolution setup a clean train/test separation, not because the validation tasks go unevaluated; the paper foregrounded the held-out subset in a way that made the benchmark look smaller than it is. We are working with GEOS developers to expand it further.

Second, since submission we have grown OpenFOAM from 5 tasks to 30 with a second native baseline, and added **LAMMPS as a third simulator** (9 molecular-dynamics tasks, two backbone models). This speaks to the reviewer's point about diverse task types as well as scale: LAMMPS input is a sequential command script with no formal schema, so it tests whether the recipe is tied to XML. It is not, but the binding component shifts from completion enforcement to memory and retrieval, because LAMMPS scripts are already structurally complete (structural score at least 0.976 across all 12 configurations).

The reviewer cited cross-simulator transfer and the reduction in complete failures as the paper's major strengths, so we would note that **both now replicate at larger scale**. On GEOS, per-cell across-run standard deviation falls from 0.081 for Vanilla to between 0.002 and 0.012 for the adapter cells, and 1 of 30 Vanilla runs produced a deck our scorer could not read against 0 of 30 for every adapter cell. On OpenFOAM at 30 tasks, every SIGA cell returns a complete case, while Foam-Agent leaves 11 tasks and MetaOpenFOAM 20 tasks incomplete. The adapters are also faster on the hard GEOS tasks than the paper reports: on held-out, X+M and S+X use about 17% fewer tool calls and 17 to 19% less wall-clock than Vanilla, with the gains concentrated exactly where the reliability gains are.
