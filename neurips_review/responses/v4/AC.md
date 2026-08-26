<!-- v4r2 DRAFT 2026-07-28. Official Comment to Area Chair GKRj.
     REVISION per researcher comments:
       - thank you + contribution recap split out under their own headings, ahead of the responses
       - contribution recap expanded, framed off the arxiv abstract
       - TreeSim defense rewritten to the researcher's wording (well-specified task + gold reference
         IS the physical-meaning check at this scope; scope expansion is the motivation, App. J is
         the early exploration already in the paper)
       - tiered evaluation protocol presented explicitly
       - 133/170 vs 132/170 REMOVED; validator swap reported as percentages instead
       - convergence numbers added
       - LLM-as-judge plausibility numbers and output-side numbers both reported
       - clarity answers now cite submitted-PDF line numbers and push back on the quoted sentence
       - human baseline reframed as "hard to scale because it needs PhD-level geophysics expertise"
     NUMBERS RE-VERIFIED this session against sprint_artifacts.tar.xz (K3_per_run.csv,
     K3_correlations.csv, L1_report.txt, L2_report.txt). See _DECISIONS_NEEDED.md for two
     corrections to numbers that were mis-scoped in v4r1 and in EVAL_WORK_EXPLAINED.md.
     Style: no em dashes, no links, no arXiv mention, VERIFIED numbers only.
     Prose ~9,400 chars. HARD CAP 10,000. -->

We thank the AC for a meta-review that states the decision criteria plainly. It made this period easy to prioritise, and we spent it building and running the evaluation the meta-review asks for. We answer the first two points of the meta-review here and the remaining two, together with the detail behind the evaluation, in a companion comment.

## What the paper contributes

Configuring an advanced scientific simulator, meaning the translation of a modeling goal into a valid and runnable input deck, is a persistent bottleneck that costs domain scientists hours to days. Input decks are executable interfaces: simulator-specific vocabulary, cross-file references, schema constraints and validation rules must all align before a simulation runs. Our claim is that this bottleneck can be substantially reduced with a lightweight adapter around an off-the-shelf coding agent rather than a bespoke simulator agent. Coding agents already navigate files, edit code, run commands and repair outputs; what they lack is the simulator's executable contract, and rebuilding the agent loop risks discarding harness-calibrated tool use and self-correction. SIGA supplies that contract through retrieval, procedural memory, agent-callable validation and validation-gated termination, while leaving the model and loop frozen. Because the contract is small and external, it also supports adapter self-evolution: prior trajectories rewrite the adapter's contents without touching the underlying agent.

On GEOS the main gain is reliability rather than ceiling: on the harder held-out tasks structural quality rises from 0.720 to 0.789 while per-cell across-run standard deviation falls from 0.081 for the bare harness to between 0.002 and 0.012 for the adapter cells, by preventing empty and invalid decks. In a human calibration the adapter reaches in about five minutes the deck quality a domain expert reached in about three hours. Transfers to OpenFOAM and LAMMPS show the recipe is portable but interface-dependent: completion gates help when structural completeness is the bottleneck, memory and retrieval when value correctness is.

All three reviewers classify the contribution as Use-Inspired and judge the problem important: gep1 credits the factorial design and the bottleneck analysis, nBNe rates significance excellent and highlights the cross-simulator transfer and the reduction in complete failures, and kEdh credits the practical system and the transfer result.

# Responses to the concerns raised

## 1. Structural-only evaluation

**Why TreeSim fits the scope we currently study.** The initial task scope assumes a solid specification from the user, which makes the agent's primary task translation into the simulator's DSL. Every brief states the geometry, material parameters, boundary conditions and requested outputs in domain language and never names a GEOS XML element. In that setting the well-specification of the task, together with scoring against a hand-validated gold configuration, is itself the check on physical meaning and usefulness: the physics is fixed by the specification and certified by the reference deck, so agreement with the reference is agreement with a simulation a domain expert has already validated.

We are, however, planning to widen the agent's responsibility so that it handles ambiguity and requires less of the user to specify. An early exploration of exactly this is already in the paper (Appendix J, with results in Section 4.6): we tier-rewrite briefs to drop software defaults, then standard numerics, then domain-inferable physical values, and measure what the agent recovers. For that wider scope we agree with the AC that a structural score does not capture physical plausibility or execution behaviour, and that is why we are extending the evaluation protocol in step with the task scope rather than after it.

**The extended protocol.** We now evaluate a deck at five levels of strictness, plus a semantic axis:

| Level | Check | Result |
|---|---|---|
| 1-2 | Well-formed XML, schema-valid against the GEOS XSD | Vanilla **155 / 170**, S+X **170 / 170**, X+M **100 / 100** (17 runs per cell) |
| 3 | GEOS accepts and loads the input | With the simulator's own validator in the adapter loop, acceptance rises to **90.0%** (S+X) and **83.3%** (S+X+M) |
| 4 | Runs to completion and the solver converges | **77 of 77** accepted held-out decks converged |
| 5 | Quantities of interest reproduce a reference run | Mean fidelity **0.958** conditional on running; 46% reproduce the reference almost exactly |
| Semantic | LLM judge rates each deck section for physical materiality against the reference | Judge's physics-section score predicts actual output fidelity at **rho = 0.418** (p = 0.0006) |

The submitted paper reports levels 1 and 2. We have now run all five and the semantic axis; a companion comment gives the construction, the full numbers and the caveats. Two points matter most here.

**At level 3 we found and fixed a defect in our own tooling.** GEOS's documentation recommends validating input with `xmllint --schema`, and that is what we built into the adapter, but the two are not equivalent: of 180 held-out decks, 49 pass `xmllint --schema` and are still refused by `geosx`, on exactly the cross-reference and arity errors our bottleneck analysis reports as unfixed by any adapter. The defects were present; the validator we chose could not see them. Swapping in the simulator's own check, at about 2.5 s per deck with everything else held constant, the agent repairs the newly surfaced defects and acceptance reaches the figures above.

**Levels 4 and 5 and the semantic axis all support the reliability framing.** Loading is the binding constraint rather than solving, so a cheap acceptance check captures nearly all of the execution signal. The gap between structure and physics sits in decks that fail to run rather than in decks that run and are wrong. And roughly two-thirds of the attribute mismatches TreeSim penalises are judged physically immaterial, so our reported structural numbers are conservative rather than generous. We are not yet offering the judge as a finished instrument, for reasons given in the companion, and a validated plausibility metric will need a purpose-built benchmark with expert-labelled ground truth. That is a scope statement about the next study, not a hedge about this one.

## 2. Clarity and jargon

The concepts kEdh names are explained in the submitted paper, and we can point to where. Line 182 states that instead of the full design we run a Resolution-IV fraction, giving eight cells whose main effects are not confounded with two-factor interactions, which is what the term means. `buckleyLeverettProblem` is the identifier of one benchmark task rather than a concept the argument depends on, and line 290 describes it as 1D immiscible CO2 and brine displacement, which is the only property the surrounding discussion uses. On the failures-as-zero sentence the reviewer quotes, we would gently disagree that it is hard to parse: it says that our reported numbers count a failure to produce scorable output as a score of zero rather than dropping it, so a system is not rewarded for emitting nothing.

We are nonetheless happy to make all of these clearer. NeurIPS does not permit editing the manuscript during this period, so rather than promise a rewrite we have put the actual replacement text inline in our response to kEdh: an "input deck" definition at first use, the fractional design motivated in plain prose with its aliasing stated explicitly, an earlier Buckley-Leverett gloss, plainer rewrites of both quoted sentences, and a worked example each of a task brief and of the stop hook's structured repair feedback.

We would offer one argument on weighing this. **Clarity is the only item on the table that is certain to be fixed.** It needs no new experiment and no result to come out a particular way, and it sits entirely within camera-ready scope. A certain fix and a hoped-for one should not carry equal weight in a borderline decision.
<!-- [[BLOCKED: H2 - how hard to commit, in writing, to the camera-ready clarity rewrite.]] -->
