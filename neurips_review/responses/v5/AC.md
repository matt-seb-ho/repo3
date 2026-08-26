<!-- v5 DRAFT 2026-07-28. Official Comment to Area Chair GKRj. POST 1 OF 2.
     REVISION from v4 per researcher comments:
       - contribution recap cut from three paragraphs to two (one short + the reviewer agreement)
       - "Responses to the concerns raised" -> "Addressing Reviewer Concerns"
       - "Structural-only evaluation" -> "Evaluation Metrics"
       - extended protocol framed as "currently exploring", not as finished
       - table: level 3 now shows the Vanilla acceptance rate; level 4 states the 100% conclusion;
         level 5 explains the construction
       - the level-3 "defect in our own tooling" paragraph is DELETED (negative framing; hold it
         in reserve if a reviewer raises it)
       - levels 4/5 discussion reduced to one short forward-looking note on judge calibration
       - clarity section's last paragraph ("clarity is the one certain fix") DELETED
       - bullets 3 and 4 folded BACK into this post, so post 1 answers every criticism;
         AC_post2.md is now a pure evaluation addendum
       - representativeness reduced to a one-sentence counter-argument
     Style: no em dashes, no links, no arXiv mention, VERIFIED numbers only.
     Prose ~7,400 chars. HARD CAP 10,000. -->

We thank the AC for a meta-review that states the decision criteria plainly. It made this period easy to prioritise, and we spent it building and running the evaluation the meta-review asks for. We answer all four points below; a short addendum follows this comment with the construction and full numbers behind the new evaluation.

## What the paper contributes

Translating a modeling goal into a valid, runnable simulator input deck is a persistent bottleneck that costs domain scientists hours to days, because a deck is an executable interface whose vocabulary, cross-file references, schema constraints and validation rules must all align before anything runs. We show that this bottleneck can be substantially reduced with a lightweight adapter around an off-the-shelf coding agent rather than a bespoke simulator agent: SIGA supplies the simulator's executable contract through retrieval, procedural memory, agent-callable validation and validation-gated termination, leaving the model and the agent loop frozen, and because that contract is small and external it also supports adapter self-evolution. On GEOS the main gain is reliability rather than ceiling: structural quality on the harder held-out tasks rises from 0.720 to 0.789 while per-cell across-run standard deviation falls from 0.081 for the bare harness to between 0.002 and 0.012 for the adapter cells, by preventing empty and invalid decks. In a human calibration the adapter reaches in about five minutes the deck quality a domain expert reached in about three hours, and transfers to OpenFOAM and LAMMPS show the recipe is portable but interface-dependent.

All three reviewers classify the contribution as Use-Inspired and judge the problem important: gep1 credits the factorial design and the bottleneck analysis, nBNe rates significance excellent and highlights the cross-simulator transfer and the reduction in complete failures, and kEdh credits the practical system and the transfer result.

# Addressing Reviewer Concerns

## 1. Evaluation Metrics

**Why TreeSim fits the scope we currently study.** The initial task scope assumes a solid specification from the user, which makes the agent's primary task translation into the simulator's DSL. Every brief states the geometry, material parameters, boundary conditions and requested outputs in domain language and never names a GEOS XML element. In that setting the well-specification of the task, together with scoring against a hand-validated gold configuration, is itself the check on physical meaning and usefulness: the physics is fixed by the specification and certified by the reference deck, so agreement with the reference is agreement with a simulation a domain expert has already validated.

We are, however, planning to widen the agent's responsibility so that it handles ambiguity and requires less of the user to specify. An early exploration of exactly this is already in the paper (Appendix J, with results in Section 4.6): we tier-rewrite briefs to drop software defaults, then standard numerics, then domain-inferable physical values, and measure what the agent recovers. For that wider scope we agree with the AC that a structural score does not capture physical plausibility or execution behaviour, which is why we are extending the evaluation protocol in step with the task scope rather than after it.

**We are therefore currently exploring an extended protocol**, evaluating a deck at five levels of strictness plus a semantic axis. Results below are on the held-out split.

| Level | Check | Result |
|---|---|---|
| 1-2 | Well-formed XML, then schema-valid against the GEOS XSD | Vanilla **155 / 170**, S+X **170 / 170**, X+M **100 / 100** (17 runs per cell) |
| 3 | GEOS itself accepts and loads the deck (`geosx --validate-input`) | Vanilla **78.2%** (133 / 170); with the simulator's own validator in the adapter loop, S+X **90.0%** and S+X+M **83.3%** (30 runs per cell) |
| 4 | The simulation runs to completion and the solver converges | **100%**: every deck GEOS accepted also ran to convergence (77 of 77), so acceptance is the binding constraint, not solving |
| 5 | Outputs reproduce a reference run. We inject an identical output block into both decks, run both, and compare mesh-independent reductions (min, max, mean, root-mean-square) of every physical quantity, each normalised by the reference's own scale, with no interpolation | Mean fidelity **0.958** conditional on the deck running; 46% of running decks reproduce the reference almost exactly |
| Semantic | An LLM judge rates each deck section against the reference for physical materiality, using four judges from four model families, blind to condition | The judge's score on the physics-bearing sections predicts measured output fidelity at **rho = 0.418** (p = 0.0006) |

The submitted paper reports levels 1 and 2; the addendum following this comment gives the construction, full numbers and caveats for the rest. The one dependency we would flag is the semantic axis: turning that judge into a validated plausibility metric requires calibrating it against expert-labelled ground truth, which needs sustained domain-expert input and a purpose-built benchmark of its own. That is the follow-up work, and a statement about the scope of the next study rather than a hedge about this one.

## 2. Clarity and jargon

The concepts kEdh names are explained in the submitted paper, and we can point to where. Line 182 states that instead of the full design we run a Resolution-IV fraction, giving eight cells whose main effects are not confounded with two-factor interactions, which is what the term means. `buckleyLeverettProblem` is the identifier of one benchmark task rather than a concept the argument depends on, and line 290 describes it as 1D immiscible CO2 and brine displacement, which is the only property the surrounding discussion uses. On the failures-as-zero sentence the reviewer quotes, we would gently disagree that it is hard to parse: it says that our reported numbers count a failure to produce scorable output as a score of zero rather than dropping it, so a system is not rewarded for emitting nothing.

We are nonetheless happy to make all of these clearer. NeurIPS does not permit editing the manuscript during this period, so rather than promise a rewrite we have put the actual replacement text inline in our response to kEdh: an "input deck" definition at first use, the fractional design motivated in plain prose, an earlier Buckley-Leverett gloss, plainer rewrites of both quoted sentences, and a worked example each of a task brief and of the stop hook's structured repair feedback.
<!-- [[BLOCKED: H2 - how hard to commit, in writing, to the camera-ready clarity rewrite. The "clarity is the one weakness certain to be fixed" argument was cut from v5 per your note; say the word if you want it back as a closing line here. -->

## 3. Limited experimental scale

**The GEOS benchmark is larger than the paper makes it look.** It is 27 evaluated tasks, 17 validation plus 10 held-out, all evaluated across all cells. The split exists to give the self-evolution setup a clean train and test separation, not because the validation tasks go unevaluated, and we will present both splits together.

On representativeness, the task pool is mined from GEOS's own advanced examples and tutorial decks, which the simulator's developers curate to span the problem classes users actually set up, including poromechanics, hydraulic fracture, thermal coupling and wellbore modeling, so coverage follows the simulator's documentation rather than a selection of our own.

**On scale beyond GEOS**, both transfer studies are now larger, with numbers in full on gep1's thread. OpenFOAM runs 30 tasks with a second simulator-native baseline: every SIGA cell returns a complete case on all 30 with no zero-score outputs (best cell 0.870), against Foam-Agent at 0.516 (19 of 30 complete) and MetaOpenFOAM at 0.379 (10 of 30). LAMMPS is added as a third simulator, whose input is a command script with no formal schema, testing whether the recipe is tied to XML. The reliability effect, which is the paper's claim, replicates on all three interfaces.
<!-- [[BLOCKED: H19 - how far to walk back the reliability claim. No bootstrap interval is printed. The task-clustered interval on the +0.069 mean lift is [-0.009, +0.166] if you want it given to the AC, who did ask for uncertainty estimates.]] -->

## 4. Human comparison too small

We agree that the human baseline is small and is primarily a preliminary calibration, and we will label it that way throughout, removing comparative time-savings language from the abstract and introduction. The reason for its size is worth stating: the task requires PhD-level geophysics knowledge and is extremely time consuming for human scientists, taking about three hours on an easier and smaller task, which makes this baseline far harder to scale than a typical human evaluation.

## On the concern raised by Reviewer kEdh

We answer this in full on that thread and note two points here. The review flags no technical flaw, no evaluation weakness, no reproducibility gap and no novelty concern, and its strengths section credits the contribution; the NeurIPS rating-2 description is "a paper with technical flaws, weak evaluation, inadequate reproducibility and incompletely addressed ethical considerations." And on venue, NeurIPS 2026's own contribution-type guidance defines the Use-Inspired type as work whose main contribution is in framing or designing approaches to meet the needs of a specific real-world application, often involving engaging with domain experts. That is this paper, and all three reviewers independently classified it Use-Inspired.

We thank the AC again for the clear criteria, and we are glad to answer anything further during the discussion period.
