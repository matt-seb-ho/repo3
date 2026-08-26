## Response to Reviewer gep1

We thank the reviewer for the thoughtful and actionable review. We appreciate the recognition of the practical importance of simulator setup, the value of wrapper-level grounding, the factorial design, and the reduction in catastrophic failures. We address each question below.

### W1 / Q1. Evaluation metrics

TreeSim primarily checks structural and value equivalence, which suits our task scope of converting well-specified briefs into simulator input decks: because the tasks are derived from validated GEOS examples, similarity to the reference is a proxy for physical meaningfulness here. To make the evaluation more complete for a future expanded scope, we added checks for schema validity, execution, convergence, and physical output on the held-out tasks.

**Schema validity.** We re-ran this at a much higher repeat count than the 3 runs per cell used elsewhere, because these are counts of rare events. Vanilla produced a well-formed, schema-valid deck on 91.2% of runs; S+X and X+M each reached 100%, across 270 adapter runs with no failures. The improvement over Vanilla is 8.8 percentage points, with a run- and task-clustered 95% confidence interval of +2.9 to +16.5 points (p = 0.0006).

**Execution and convergence.** We replaced the schema linter inside the adapter loop with GEOS's native input checker. Acceptance on the held-out evaluation rises from 78.2% for Vanilla to 90.0% for S+X, and every accepted deck we tested for execution completed successfully and reached solver convergence.

**Physical-output fidelity.** Because generated and reference decks may request different output variables, we apply the same output specification to both while leaving the generated physical configuration unchanged, then compare mesh-independent summaries of every physical quantity, each normalized by the reference's own scale. Among decks that execute, mean output fidelity is 0.958 and 46% achieve fidelity above 0.999. Structural similarity predicts fidelity at Spearman rho = 0.362 (95% CI 0.197 to 0.505, p = 0.0001).

**Physics plausibility.** We also built a semantic check, in which a panel of LLM judges rates each deck section against the reference for physical materiality. Its score on the physics-bearing sections predicts measured output fidelity at rho = 0.418 (p = 0.0006), but it does not beat plain structural scoring here and the judges did not agree on the ordering of conditions, so we report it as built and tested rather than as a metric we would offer.

These results help flesh out a more complete evaluation and locate the bottleneck at the schema-correctness layer: once GEOS accepts a deck, it reliably executes and generally reproduces the reference outputs. We are happy to give the full protocol during discussion, and will document it in the revision.

### W3 / Q2. Prefix bug and the roles of S and X

**Native-plugin-prefix bug.** A targeted ablation over 17 tasks with three runs each puts the effect at +0.004 (TreeSim 0.913 to 0.917), with no task changing by more than 0.10. The prefix acted as minor distractor text and slightly reduced SIGA performance; Vanilla and the self-evolved adapter were unaffected. The magnitude is therefore minor and its direction leaves SIGA scores slightly understated.

**Separating S from X.** S and X are varied independently in the Resolution-IV design, so their main effects are separable. On the reviewer's underlying question, whether the termination hook still contributes once the agent-callable validator is available, the held-out column builds the two up in sequence:

| Cell (held-out) | TreeSim | vs. Vanilla |
| :---- | :---- | :---- |
| Vanilla | 0.720 ± 0.081 | n/a |
| X+M (validator plus memory) | 0.768 ± 0.005 | +0.048 |
| S+X+M (termination hook added on top) | **0.783 ± 0.022** | **+0.063** |

M is the procedural-memory cheatsheet and is unrelated to validation, so the step from X+M to S+X+M isolates the addition of the termination hook, and it is positive. S+X reaches 0.781 on the same split, so the ordering holds with and without memory.

We include both components by design: X gives the agent a validator it can call during generation, while S is the process guarantee that validation is run before submission.

### Q3. OpenFOAM transfer

We expanded the OpenFOAM study from 5 to 30 tasks and replaced the static linter with a validator that runs the OpenFOAM solver in a container.

Across the full factorial study on the 30 tasks, the best SIGA configuration (R+S+X+M) scores 0.668 on the text-similarity metric and produces executable cases on 89.7% of tasks, against 13.3% for Vanilla Claude Code, and is stable across three seeds (0.668, 0.685, 0.665). Executability is assessed only for tasks whose solver is present in the evaluation container, and that exclusion is applied identically across conditions.

We additionally ran two simulator-native systems on a 10-task set drawn from the same benchmark family, under matched budgets and the same bounded real-execution and post-hoc executability checks: Foam-Agent scores 0.565 with 10% executable, MetaOpenFOAM 0.276 with 22%. Because they ran on a smaller task set than SIGA's 30, we present this as indicative rather than matched.

The strongest transfer result is the improvement in execution reliability. In the revision we will limit this claim to the OpenFOAM tasks evaluated here and make clear that the experiment tests executable structure rather than physical correctness.

### W2. Experimental scale

The GEOS benchmark contains 27 distinct documentation-derived tasks: 17 for development and 10 held out. The split exists mainly to improve iteration speed on the factorial evaluation and to provide a held-out set for the self-evolution setting. Two things bound this scale. The tasks are mined from GEOS documentation examples, which yield 46 candidates in total, and within a fixed compute budget run counts multiply across component combinations, repeated runs for error bars, and further experiments across backbone models, harnesses, and domains. We judged breadth across those conditions more valuable than more documentation examples within GEOS: generalization is better tested by a second and third simulator than by a 28th GEOS task. The resulting scale is in line with contemporary work in the area, which evaluates on 2 to 12 cases [1-5]. We are working with domain-expert collaborators to author tasks beyond the documentation corpus.

Beyond GEOS, we have expanded the OpenFOAM study as described above and added a third simulator, LAMMPS, whose command-script interface has no formal schema and therefore tests whether the recipe is tied to XML (see our response to Reviewer nBNe). In the revision we will describe the coverage of the held-out tasks more clearly and report task-level uncertainty for the main results.

### Q4. Human comparison

The human study is intended as a preliminary calibration of the time required to learn GEOS conventions and configure one representative task. We will label it accordingly and avoid using it to support a broad human-efficiency claim. We do maintain it is a useful calibration, since it establishes a human pace on a relatively easy 1D problem; recruiting PhD-level geophysics knowledge workers is difficult, especially for long, involved tasks such as simulation configuration.

**References**

[1] Zhang et al. Agentic AI for Particle-Based Simulation: Automating SPH Workflows for Debris Flow Modeling. arXiv:2605.09265, 2026. [2] Wang et al. MDForge: Agentic Molecular Dynamics Pipeline Design under Sparse Simulator Feedback. arXiv:2606.12916, 2026. [3] Zhao, Chandrasekhar and Farimani. PolyJarvis: LLM Agent for Autonomous Polymer MD Simulations. arXiv:2604.02537, 2026. [4] Guilbert et al. DynaMate: An Autonomous Agent for Protein-Ligand Molecular Dynamics Simulations. arXiv:2512.10034, 2025. [5] Dong, Lu and Yang. CFD-Copilot: Leveraging domain-adapted large language model and model context protocol to enhance simulation automation. *Chinese Journal of Aeronautics*, 2026.
