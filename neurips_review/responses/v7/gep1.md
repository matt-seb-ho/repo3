<!-- v7 DRAFT 2026-07-28. Reviewer gep1 (Reviewer 1): rating 4 (borderline accept), confidence 3.
     Rebuilt in the hand_v6 house style: bullets, short declaratives, defend rather than concede.
     Messaging aligned with hand_v6/siga_neurips26_rebuttal.md on the two shared threads:
       - evaluation is framed as "New Metrics" with the same three instruments and same numbers
       - scale is defended on cost grounds plus contemporary works at comparable scale
     Reviewers get slightly more depth than the AC: the artifact-validity counts, the correlation
     interval, the two metric tests, and the transfer numbers in full.
     v5's gep1_post2.md is FOLDED IN. One post now, no companion.
     Style: no em dashes, no hyperlinks, no arXiv-version mention, VERIFIED numbers only.
     Prose ~8,700 chars. HARD CAP 10,000. -->

## Response to Reviewer gep1

We thank the reviewer for an unusually actionable review. Every point was specific enough to act on directly, and we did.

### W1 / Q1. Evaluation beyond structure

**TreeSim fits the scope we currently study.** Our task scope assumes a complete user specification, so the agent's task is translation into the simulator DSL and structural evaluation is appropriate. The briefs state geometry, material parameters, boundary conditions and requested outputs in domain language and never name a GEOS XML element. Because our tasks are mined from GEOS documentation examples, the physics is fixed on the input side and hand-validated on the reference side, so similarity to ground truth captures it on the output side.

The broader aim of this line of work is to expand the scope of agent responsibility (see the initial exploration in Appendix J, with results in Section 4.6), so we are expanding the evaluation with new metrics and protocols. Results below are on the held-out split.

**Artifact validity**, re-run at 17 runs per cell rather than 3 because these are counts of rare events: Vanilla is well-formed and schema-valid on **155 / 170**, S+X on **170 / 170**, X+M on **100 / 100**. Gap 8.8 points, clustered interval +2.9 to +16.5, p = 0.0006, with 270 adapter runs and no failures.

New metrics beyond the artifact:

- **Simulation Execution**
  - Metric: (binary) does GEOS accept the deck, and does the run complete with a converged solver?
  - Result: decks accepted rises from **78.2%** (Vanilla) to **90.0%** once the simulator's own input check replaces the schema linter inside the adapter loop; of accepted decks, **100%** ran to completion and converged (77 of 77)
  - Insight: execution is not the bottleneck, deck construction is
- **Simulation Output**
  - Metric: (continuous) inject an identical ground-truth output block into both decks, run both, and compare mesh-independent reductions (min, max, mean, root-mean-square) of every physical quantity, each normalized by the reference's own scale, with no interpolation
  - Result: mean fidelity **0.958** conditioned on the deck running, 46% of running decks reproduce the reference almost exactly, and structural similarity predicts fidelity at **rho = 0.36** (interval 0.20 to 0.51, p = 0.0001)
  - Insight: the distance between structure and physics sits in decks that fail to run, not in decks that run and are wrong, which is consistent with the reliability framing the review credits
- **Input Deck Evaluation for Physics Plausibility**
  - Metric: an LLM judge rates each deck section against the reference for physical materiality, using four judges from four model families, none of them the agent's backbone, blind to condition and order-swapped
  - Result: the judge's score on the physics-bearing sections predicts measured output fidelity at **rho = 0.418** (p = 0.0006); the `Solvers` subtree alone reaches rho = 0.456
  - Comment: it does not beat plain structural scoring at that task and two of four judges ordered conditions differently, so it needs calibration against domain expert judgements before we would offer it as a metric; we reserve this for follow-up work

We also tested re-weighting the structural metric toward physics-bearing sections, which yields at most a small improvement (+0.033, interval -0.003 to +0.072), so uniform weighting now rests on a test rather than an assumption. We are happy to give the full protocol for any of these during discussion, and will document it in the camera-ready.

### W2. Experimental scale

**GEOS scale.** One clarification we owe the reviewer first: the benchmark is **27 evaluated tasks**, 17 validation plus 10 held-out, all evaluated across all cells. The split exists to give the self-evolution setup a clean train and test separation, not because the validation tasks go unevaluated. On why it is not larger, earlier experiments with weaker models found individual trajectories to take upward of 30 minutes, and combined with a large set of configuration conditions and our aim of gathering error bars with multiple runs per configuration, we allocated a limited budget toward testing more conditions rather than more independent examples.

Contemporary works adapting LLMs for scientific simulation in related domains study cases on a similar order: Debris Flow, 5 cases [1]; Molecular Dynamics, 3 host-guest families [2], 9 polymer systems [3], 12 protein-ligand systems [4]; Computational Fluid Dynamics, 2 geometries [5]. We are presently working with our domain expert collaborators to expand beyond documentation examples.

**Beyond GEOS.** Both transfer studies are larger than the submitted version.

- **OpenFOAM, 5 tasks to 30, plus a second simulator-native baseline.** Best SIGA cell 0.870, with every SIGA cell producing all required files on all 30 tasks and no zero-score outputs. Foam-Agent reaches 0.516 (19 of 30 full coverage, 8 zero-score) and MetaOpenFOAM 0.379 (10 of 30, 12 zero-score).
- **LAMMPS, a third simulator.** 9 molecular-dynamics tasks on two backbone models, with a 20-task scale-up underway. LAMMPS input is a command script with no formal schema, which tests whether the recipe is tied to XML. It is not, but the binding component shifts: scripts are structurally complete almost everywhere, so the gain comes from knowledge injection rather than completion enforcement. Judge scores move from 4.56 to 7.78 on one backbone and 6.33 to 6.89 on the other.

Both remain single-run and we present them as qualitative transfer evidence. The reliability effect the review singles out as our strongest result replicates on all three interfaces.

### Q2a. The native-plugin-prefix bug

We can bound the effect directly rather than argue from chronology, and it is very small. A targeted ablation gives 0.913 with the prefix against 0.917 without, a difference of **+0.004** across 3 runs on 17 tasks, with no single task moving by more than 0.10. The direction is the reassuring part: the bias runs against the adapter cells, so their reported lifts are understated rather than inflated. The headline comparison is untouched in any case, since Vanilla and SE both attempt zero retrieval calls, leaving that contrast prefix-free on both sides.

### Q2b. Separating S from X

The Resolution-IV design does separate the S and X **main effects**: with defining relation I = RSXM, main effects alias only with three-factor interactions, so S and X are clean of each other and of every two-factor interaction. What the fraction cannot estimate is the S by X **interaction**, and we should have said so.

On the underlying question, whether the termination hook still contributes once the agent-callable validator is available, the held-out column of Table 1 builds the two up in sequence:

| Cell (held-out) | TreeSim | vs Vanilla |
|---|---|---|
| Vanilla | 0.720 ± 0.081 | |
| X+M (validator plus memory) | 0.768 ± 0.005 | +0.048 |
| S+X+M (termination hook added on top) | **0.783 ± 0.022** | **+0.063** |

M is the procedural-memory cheatsheet and is unrelated to validation, so the step from X+M to S+X+M isolates adding the termination hook, and it is positive. S+X reaches 0.781 on the same split, so the ordering holds without memory as well. At three runs per cell we would not over-read the margins between adapter cells, and we are happy to run the build-up experiment the reviewer describes.

We include both by design: X gives the agent tooling to check its own work mid-turn, and S is the process guarantee that validation has happened before the turn ends, which does not depend on the agent choosing to invoke it.

### Q3. Strengthening the OpenFOAM study

Strengthened as described in W2, and we accept the reviewer's fallback. Foam-Agent's execute mode did not run in our environment, so that comparison remains lint-only and we will state this in the main text rather than a footnote, and we keep the transfer claims explicitly qualitative.

### Q4. The human comparison

We agree it is better described as a preliminary calibration and will relabel it, removing comparative time-savings language from the abstract and introduction. We do maintain it is a useful calibration, since it establishes a human pace on a relatively easy 1D problem. Recruiting PhD-level geophysics knowledge workers is difficult, especially for long, involved tasks such as simulation configuration.

### Limitations wording

We are glad to sharpen this in the main body. For the scope this paper studies a structural metric is the right primary measure, because the specification and its provenance are what establish that the target simulation is physically meaningful, and what the headline numbers measure is how reliably the agent reaches it. As the agent's responsibility widens, plausibility becomes a first-order question rather than one settled by the specification, which is why the evaluation protocol is expanding alongside the task scope, with the results above as the first instalment.

[1] Zhang et al. Agentic AI for Particle-Based Simulation: Automating SPH Workflows for Debris Flow Modeling. arXiv:2605.09265, 2026.
[2] Wang et al. MDForge: Agentic Molecular Dynamics Pipeline Design under Sparse Simulator Feedback. arXiv:2606.12916, 2026.
[3] Zhao, Chandrasekhar & Farimani. PolyJarvis: LLM Agent for Autonomous Polymer MD Simulations. arXiv:2604.02537, 2026.
[4] Guilbert et al. DynaMate: An Autonomous Agent for Protein-Ligand Molecular Dynamics Simulations. arXiv:2512.10034, 2025.
[5] Dong, Lu & Yang. CFD-Copilot: Leveraging domain-adapted large language model and model context protocol to enhance simulation automation. Chinese Journal of Aeronautics, 2026.
