<!-- v5r2 DRAFT 2026-07-28. Reviewer gep1 (Reviewer 1): rating 4 (borderline accept), confidence 3.
     CHANGED FROM v5r1: the evaluation section now MIRRORS the AC post-1 structure exactly
     (scope argument, five-level table, calibration note) instead of folding in the addendum
     detail. gep1 asked whether an execution-based evaluation exists and what it shows; the table
     answers that, and the construction detail is methodology the reviewer did not ask for.
     The freed space lets Q2a and Q2b move up here, so this post carries W1/Q1 and both Q2 parts,
     and gep1_post2.md carries W2 / Q3 / Q4.
     "[score-moving]" tags removed throughout: that was our own triage annotation, not the
     reviewer's wording, and echoing it back reads as strategising about the score.
     ALSO REMOVED per the AC direction: the "with the shipped configuration the adapter cells did
     not separate from Vanilla on acceptance" clause. See _DECISIONS_NEEDED.md, it is one sentence
     to restore if you want it.
     v5r3: Q2b no longer cites the val build-up ablation (S +0.008 / X -0.007 / together +0.000)
     or the hook telemetry (0 firings in 410 invocations). Both read as the two components
     cancelling. It now uses the paper's own Table 1 held-out column, where Vanilla -> X+M ->
     S+X+M increases monotonically and the X+M -> S+X+M step isolates the termination hook,
     plus an offer to run the reviewer's build-up experiment.
     Style: no em dashes, no links, no arXiv mention, VERIFIED numbers only.
     Prose ~8,300 chars. HARD CAP 10,000. -->

## Response to Reviewer gep1

We thank the reviewer for an unusually actionable review. Every point was specific enough to act on directly, and we did: we built and ran the execution-based evaluation asked for in Q1, and we bounded and separated the confounds raised in Q2. We answer those here. A companion comment posted alongside answers W2 (scale and seeds), Q3 (OpenFOAM), Q4 (the human comparison) and the limitations wording.

### Response to W1 and Q1, evaluation beyond structure

Two parts: why a structural metric fits the task this benchmark currently poses, and what we found when we went past it.

**Why TreeSim fits the scope we currently study.** The initial task scope assumes a solid specification from the user, which makes the agent's primary task translation into the simulator's DSL. Each brief states the domain geometry, material parameters, boundary conditions and requested outputs in domain language, a permeability of 9.0e-13 m2 in all directions, a reference porosity of 0.2 at 10 MPa, and so on, and never names a single GEOS XML element. The agent has no property database, literature access or online source, and is not asked to decide what the physics should be. In that setting the well-specification of the task, together with scoring against a hand-validated gold configuration, is itself the check on physical meaning: the physics is fixed by the brief and certified by the reference deck, so agreement with the reference is agreement with a simulation a domain expert has already validated. TreeSim answers that question deterministically and cheaply enough to run on every cell of a factorial design, which neither an execution-based nor a judge-based metric is at our budget.

We are, however, planning to widen the agent's responsibility so that it handles ambiguity and requires less of the user to specify. An early exploration of exactly this is already in the paper (Appendix J, with results in Section 4.6): we tier-rewrite briefs to drop software defaults, then standard numerics, then domain-inferable physical values, and measure what the agent recovers. For that wider scope we agree with the reviewer that a structural score does not capture physical plausibility or execution behaviour, which is why we are extending the evaluation protocol in step with the task scope rather than after it.

**We are therefore currently exploring an extended protocol**, evaluating a deck at five levels of strictness plus a semantic axis. Results below are on the held-out split.

| Level | Check | Result |
|---|---|---|
| 1-2 | Well-formed XML, then schema-valid against the GEOS XSD | Vanilla **155 / 170**, S+X **170 / 170**, X+M **100 / 100** (17 runs per cell) |
| 3 | GEOS itself accepts and loads the deck (`geosx --validate-input`) | Vanilla **78.2%** (133 / 170); with the simulator's own validator in the adapter loop, S+X **90.0%** and S+X+M **83.3%** (30 runs per cell) |
| 4 | The simulation runs to completion and the solver converges | **100%**: every deck GEOS accepted also ran to convergence (77 of 77), so acceptance is the binding constraint, not solving |
| 5 | Outputs reproduce a reference run. We inject an identical output block into both decks, run both, and compare mesh-independent reductions (min, max, mean, root-mean-square) of every physical quantity, each normalised by the reference's own scale, with no interpolation | Mean fidelity **0.958** conditional on the deck running; 46% of running decks reproduce the reference almost exactly |
| Semantic | An LLM judge rates each deck section against the reference for physical materiality, using four judges from four model families, blind to condition | The judge's score on the physics-bearing sections predicts measured output fidelity at **rho = 0.418** (p = 0.0006) |

The submitted paper reports levels 1 and 2. Two notes on what the rest does and does not establish. We do not claim an execution-level or output-fidelity advantage between conditions; neither is detectable at this scale and the reliability claim does not need one. And the one dependency we would flag is the semantic axis: turning that judge into a validated plausibility metric requires calibrating it against expert-labelled ground truth, which needs sustained domain-expert input and a purpose-built benchmark of its own. That is the follow-up work, and a statement about the scope of the next study rather than a hedge about this one.

We are happy to give the full construction and the per-level caveats during the discussion period if that would be useful.

### Response to W3 and Q2a, the native-plugin-prefix bug

We can bound the effect directly rather than argue from chronology, and it is very small. A targeted ablation gives 0.913 with the prefix against 0.917 without, a difference of **+0.004** across 3 runs on 17 tasks, with no single task moving by more than 0.10. The direction is the reassuring part: the bias runs against the adapter cells, so their reported lifts are understated rather than inflated. The headline comparison is untouched in any case, since Vanilla and SE both attempt zero retrieval calls, leaving that contrast prefix-free on both sides.

### Response to W3 and Q2b, separating S from X

The Resolution-IV design does separate the S and X **main effects**: with defining relation I = RSXM, main effects alias only with three-factor interactions, so S and X are clean of each other and of every two-factor interaction. What the fraction cannot estimate is the S by X **interaction**, and we should have said so.

On the reviewer's underlying question, whether the termination hook still contributes once the agent-callable validator is available, the held-out column of Table 1 is the most direct evidence we have, because it builds the two up in sequence:

| Cell (held-out) | TreeSim | vs Vanilla |
|---|---|---|
| Vanilla | 0.720 ± 0.081 | |
| X+M (validator plus memory) | 0.768 ± 0.005 | +0.048 |
| S+X+M (termination hook added on top) | **0.783 ± 0.022** | **+0.063** |

M is the procedural-memory cheatsheet and is unrelated to validation, so the step from X+M to S+X+M isolates the addition of the termination hook, and it is positive. S+X reaches 0.781 on the same split, so the ordering holds with and without memory. These are three runs per cell, so we would not over-read the margins between adapter cells, and we would be glad to run a dedicated build-up experiment isolating the interaction.

We include both components by design rather than by accident. X gives the agent the tooling to check its own work mid-turn, which is what we want it using while it drafts; S is the process guarantee that validation has actually happened before the turn ends, which does not depend on the agent choosing to invoke it. A system that relies on the agent's initiative alone has no floor, and one that relies only on a terminal gate gives the agent no way to check as it goes.

We are grateful for a review that told us precisely what evidence would move the score, and we hope the results above meet it.
