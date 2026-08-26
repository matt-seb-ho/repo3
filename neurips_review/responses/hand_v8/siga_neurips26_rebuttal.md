# ac\_response\_latest

**AC Response**

We thank the AC for a meta-review that cleanly summarizes the main concerns raised by reviewers.

# Contribution Summary

We study the application of coding agent techniques to the **novel domain of geophysics simulation**, proposing a lightweight adaptation method.

- **Problem Significance**: Automating the busy work of configuring simulations for experiments recovers valuable researcher hours for higher level, higher leverage tasks.  
- **Method**: Rather than building a new agent architecture around a new domain/simulator/workflow, or optimizing the entire harness, we propose searching a small set of lightweight modules implementing proven components.  
- **Cross-domain validation**: Our primary work focuses on geophysics (GEOS simulator) but we validate our method in two other domains: fluid dynamics (OpenFOAM), and molecular dynamics (LAMMPS; added post submission)  
- **Results**:  
  - Compared to human: Minutes instead of hours  
  - Compared to baseline coding agent:  
    - Variance reduction (preventing catastrophic failures)  
    - Up to 22% fewer tool calls and 18% less wall clock per task on the harder split (best adapter cells)

# Addressing Reviewer Concerns

## 1\. Evaluation Metrics.

**TreeSim fits the scope we currently study.** Our task scope assumes a complete user specification. As a result the agent's task is translation into simulator DSL and thus structural evaluation is appropriate. Since our tasks are mined from documentation examples, the physics are fixed on the input side and our similarity to ground truth metrics captures this on the output side.

The broader aim of this line of work is to expand the scope of agent responsibility (see initial exploration in Appendix J), so we explore expanding the evaluation with new metrics and protocols. Results below are on the held-out split.

New Metrics

- Simulation Execution:  
  - Metric: (Binary) Does GEOS accept the deck? Does the simulation run to completion and the solver converges?  
  - Result: Decks accepted rises from **78.2%** (Vanilla) to **90.0%** once the simulator's own input check replaces the schema linter inside the adapter loop; of accepted decks, **100%** ran to completion with a converged solver (77 of 77\)  
  - Insight: Execution is not the bottleneck, deck construction is  
- Simulation Output:  
  - Metric: (Continuous) Injecting an identical ground truth output block into both decks, running both, and comparing mesh-independent reductions of each physical quantity, normalized by the reference's own scale  
  - Result: Mean fidelity **0.958** (conditioned on the deck running), with 46% of running decks reproducing the reference almost exactly  
  - Insight: Further confirms that the reliability bottleneck exists at the deck construction level  
- Input Deck Evaluation for Physics Plausibility:  
  - Metric: LLM judge rates each deck section for physics considerations  
  - Result: Judge score predicts measured output fidelity at **rho \= 0.418** (p \= 0.0006)  
  - Comment: This requires further calibration against domain expert judgements (we reserve this for follow-up work)

We are happy to give the full protocol for any of these during discussion, and will document it in the camera-ready.

## 2\. Clarity and jargon

We discuss this in detail in our response to Reviewer kEdh (locating definitions/explanations; adding more context; etc.). In short, we are happy to add further clarifications for the revision.

## 3\. Limited experimental scale

**GEOS scale.** The evaluation covers 27 tasks (17 validation, 10 held-out), each run in every cell. Two things set this scale: the tasks are mined from GEOS documentation examples, which yield 46 candidates in total, so the achievable set is of this order; and within a fixed compute budget, run counts balloon with various ablations, repeated runs for error bars, and other experiments on backbone models, and harnesses. We judged breadth across those conditions more valuable than more documentation examples within GEOS: generalization is better tested by a second and third simulator than by a 28th GEOS task. This is in line with contemporary work in the area, which evaluates on 2–12 cases \[1–5\]. We are working with our domain expert collaborators to author tasks beyond the documentation corpus.

**Beyond GEOS.** We have since expanded the Fluid Dynamics/OpenFOAM transfer study to include 30 tasks (see results in Reviewer gep1's thread) and expanded to the Molecular Dynamics domain/LAMMPS as well with 9 initial tasks and a scaled up study with 20 tasks currently underway.

## 4\. Human comparison scale

We agree that the human baseline is better described as a preliminary calibration, and are happy to relabel in the revision. We do maintain that this is a useful calibration however as it establishes a human pace on a relatively easy 1D problem. Time and resource constraints factor in here as recruiting PhD-level geophysics knowledge workers is difficult especially for long, involved tasks such as simulation configuration.

## On the concern raised by Reviewer kEdh

Reviewer kEdh suggests a topic misfit for the NeurIPS venue.

- We refer to the NeurIPS 2026 contribution type guidance defining the Use-Inspired type as work whose main contribution is in framing or designing approaches to meet the needs of a specific real-world application, often involving engaging with domain experts. **We think our paper matches this criteria.**

They also recommended rejection despite not highlighting any technical, evaluation, reproducibility, or ethical issues.

- Again, we are happy to add clarifications to address their writing concerns but find some decoupling between feedback and score.

\[1\] Zhang, D., Wang, R., Liu, C., & Zhao, Y. (2026). Agentic AI for Particle-Based Simulation: Automating SPH Workflows for Debris Flow Modeling. arXiv preprint arXiv:2605.09265.  
\[2\] Wang, Z., Ma, Y., Schmidt, C. R., Ma, T., Sun, W., Li, Z., ... & Ye, Y. (2026). MDForge: Agentic Molecular Dynamics Pipeline Design under Sparse Simulator Feedback. arXiv preprint arXiv:2606.12916.   
\[3\] Zhao, A., Chandrasekhar, A., & Farimani, A. B. (2026). Polyjarvis: Llm agent for autonomous polymer md simulations. arXiv preprint arXiv:2604.02537.  
\[4\] Guilbert, S., Masschelein, C., Goumaz, J., Naida, B., & Schwaller, P. (2025). DynaMate: An Autonomous Agent for Protein-Ligand Molecular Dynamics Simulations. arXiv preprint arXiv:2512.10034.  
\[5\] Zhehao, D. O. N. G., Zhen, L. U., & Yue, Y. A. N. G. (2026). CFD-copilot: Leveraging domain-adapted large language model and model context protocol to enhance simulation automation. Chinese Journal of Aeronautics, 104321\.

# gep1\_latest

## Response to Reviewer gep1

We thank the reviewer for an actionable review. We do our best to address the feedback here.

### W1 / Q1. Evaluation beyond structure

**TreeSim fits the scope we currently study.** Our task scope assumes a complete user specification, so the agent's task is translation into the simulator DSL and structural evaluation is appropriate. Moreover, because our tasks are mined from GEOS documentation examples, the physics is fixed on the input side and hand-validated on the reference side, so similarity to ground truth captures it on the output side.

The broader aim of this line of work is to expand the scope of agent responsibility (see the initial exploration in Appendix J, with results in Section 4.6), so we are expanding the evaluation with new metrics and protocols. Results below are on the held-out split.

**Artifact validity**, re-run at 17 runs per cell rather than 3 because these are counts of rare events: Vanilla is well-formed and schema-valid on **155 / 170**, S+X on **170 / 170**, X+M on **100 / 100**. Gap 8.8 points, clustered interval \+2.9 to \+16.5, p \= 0.0006, with 270 adapter runs and no failures.

New metrics beyond the artifact:

- **Simulation Execution**  
  - Metric: (binary) does GEOS accept the deck, and does the run complete with a converged solver?  
  - Result: decks accepted rises from **78.2%** (Vanilla) to **90.0%** once the simulator's own input check replaces the schema linter inside the adapter loop; of accepted decks, **100%** ran to completion and converged (77 of 77\)  
  - Insight: execution is not the bottleneck, deck construction is  
- **Simulation Output**  
  - Metric: (continuous) inject an identical ground-truth output block into both decks, run both, and compare mesh-independent reductions (min, max, mean, root-mean-square) of every physical quantity, each normalized by the reference's own scale, with no interpolation  
  - Result: mean fidelity **0.958** conditioned on the deck running, 46% of running decks reproduce the reference almost exactly, and structural similarity predicts fidelity at **rho \= 0.36** (interval 0.20 to 0.51, p \= 0.0001)  
  - Insight: the distance between structure and physics sits in decks that fail to run, not in decks that run and are wrong, which is consistent with the reliability framing the review credits  
- **Input Deck Evaluation for Physics Plausibility**  
  - Metric: an LLM judge rates each deck section against the reference for physical materiality, using four judges from four model families, none of them the agent's backbone, blind to condition and order-swapped  
  - Result: the judge's score on the physics-bearing sections predicts measured output fidelity at **rho \= 0.418** (p \= 0.0006); the `Solvers` subtree alone reaches rho \= 0.456  
  - Comment: it does not beat plain structural scoring at that task and two of four judges ordered conditions differently, so it needs calibration against domain expert judgements before we would offer it as a metric; we reserve this for follow-up work

We also tested re-weighting the structural metric toward physics-bearing sections, which yields at most a small improvement (+0.033, interval \-0.003 to \+0.072), so uniform weighting now rests on a test rather than an assumption. We are happy to give the full protocol for any of these during discussion, and will document it in manuscript revisions.

### W2. Experimental scale

**GEOS scale.** The evaluation covers 27 tasks (17 validation, 10 held-out), each run in every cell. Two things set this scale: the tasks are mined from GEOS documentation examples, which yield 46 candidates in total, so the achievable set is of this order; and within a fixed compute budget, run counts balloon with various ablations, repeated runs for error bars, and other experiments on backbone models, and harnesses. We judged breadth across those conditions more valuable than more documentation examples within GEOS: generalization is better tested by a second and third simulator than by a 28th GEOS task. This is in line with contemporary work in the area, which evaluates on 2–12 cases \[1–5\]. We are working with our domain expert collaborators to author tasks beyond the documentation corpus.

**Beyond GEOS.** Since submission we have expanded the OpenFOAM transfer study and added a third domain in Molecular Dynamics with the LAMMPS simulator.

- **OpenFOAM, 5 tasks to 30, plus a second simulator-native baseline.** Best SIGA cell 0.870, with every SIGA cell producing all required files on all 30 tasks and no zero-score outputs. Foam-Agent reaches 0.516 (19 of 30 full coverage, 8 zero-score) and MetaOpenFOAM 0.379 (10 of 30, 12 zero-score).  
- **LAMMPS, a third simulator.** 9 molecular-dynamics tasks on two backbone models, with a 20-task scale-up underway. LAMMPS input is a command script with no formal schema, which tests whether the recipe is tied to XML. It is not, but the binding component shifts: scripts are structurally complete almost everywhere, so the gain comes from knowledge injection rather than completion enforcement. Judge scores move from 4.56 to 7.78 on one backbone and 6.33 to 6.89 on the other.

Both remain single-run and we present them as qualitative transfer evidence. The reliability effect the review singles out as our strongest result replicates on all three interfaces.

### Q2a. The native-plugin-prefix bug

We can bound the effect directly, finding it to be minimal in magnitude. A targeted ablation gives 0.913 with the prefix against 0.917 without, a difference of **\+0.004** across 3 runs on 17 tasks, with no single task moving by more than 0.10. The direction reinforces our conclusions: the prefix bug introduced a distractor text that slightly hurt the performance of SIGA runs, so reported SIGA performance is slightly understated. Vanilla and SE are unaffected by this prefix.

### Q2b. Separating S from X

The Resolution-IV design does separate the S and X main effects.

On the reviewer's underlying question, whether the termination hook still contributes once the agent-callable validator is available, the held-out column of Table 1 contains direct evidence, because it builds the two up in sequence:

| Cell (held-out) | TreeSim | vs Vanilla |
| :---- | :---- | :---- |
| Vanilla | 0.720 ± 0.081 |  |
| X+M (validator plus memory) | 0.768 ± 0.005 | \+0.048 |
| S+X+M (termination hook added on top) | **0.783 ± 0.022** | **\+0.063** |

M is the procedural-memory cheatsheet and is unrelated to validation, so the step from X+M to S+X+M isolates the addition of the termination hook, and it is positive. S+X reaches 0.781 on the same split, so the ordering holds with and without memory. These are three runs per cell, so we would not over-read the margins between adapter cells, and we would be glad to run a dedicated build-up experiment isolating the interaction.

We include both components by design: X gives the agent the tooling to check its own work mid-turn; S is the process guarantee that validation is run before submitting the configuration.

### Q3. Strengthening the OpenFOAM study

Strengthened as described in W2.

### Q4. The human comparison

We agree it is better described as a preliminary calibration and will relabel it in manuscript revisions. We do maintain it is a useful calibration, since it establishes a human pace on a relatively easy 1D problem. Recruiting PhD-level geophysics knowledge workers is difficult, especially for long, involved tasks such as simulation configuration.

### Limitations wording

We are glad to sharpen this in the main body. For the scope this paper studies a structural metric is the right primary measure, because the specification and its provenance are what establish that the target simulation is physically meaningful, and what the headline numbers measure is how reliably the agent reaches it. As the agent's responsibility widens, plausibility becomes a first-order question rather than one settled by the specification, which is why the evaluation protocol is expanding alongside the task scope, with the results above as the first instalment.

\[1\] Zhang et al. Agentic AI for Particle-Based Simulation: Automating SPH Workflows for Debris Flow Modeling. arXiv:2605.09265, 2026\.   
\[2\] Wang et al. MDForge: Agentic Molecular Dynamics Pipeline Design under Sparse Simulator Feedback. arXiv:2606.12916, 2026\.   
\[3\] Zhao, Chandrasekhar & Farimani. PolyJarvis: LLM Agent for Autonomous Polymer MD Simulations. arXiv:2604.02537, 2026\.   
\[4\] Guilbert et al. DynaMate: An Autonomous Agent for Protein-Ligand Molecular Dynamics Simulations. arXiv:2512.10034, 2025\.   
\[5\] Dong, Lu & Yang. CFD-Copilot: Leveraging domain-adapted large language model and model context protocol to enhance simulation automation. Chinese Journal of Aeronautics, 2026\.

# kEdh\_latest

## Response to Reviewer kEdh

We thank the reviewer for a close and specific reading, and for stating the practical takeaway accurately: adding verification checkpoints to a coding agent substantially reduces failures on difficult scientific tasks without retraining the model.

Each concept the review highlights is defined in the submitted paper, and we locate each below. What the review identifies, usefully, is that several are defined later than their first use. That is an ordering problem with a definite fix. NeurIPS does not allow a revised PDF during this period, but we are happy to add further clarifications for manuscript revisions. Below we provide some clarifications and propose text to include in manuscript revisions.

### Response to W1: Resolution-IV and buckleyLeverettProblem

**Resolution-IV.** The design is explained at line 182, which states that instead of exhaustively testing every combination of factors, we select a subset of configurations that allow us to discern the main effects without being confounded by a 2 factor interaction (e.g. M only helps when X is present, etc.). We propose to remove this language from the abstract/early sections of the paper and reserve this elaboration for the experiments/results sections. We plan to motivate this in plain prose:

Our aim is to quantify each component’s contribution. Testing them one at a time is cheap but cannot detect a component that only helps in combination. Testing all sixteen on/off combinations answers that, but doubles the experiment. We therefore run a carefully chosen half of the sixteen, eight combinations, selected so that each component's individual effect stays separable from the others. The price is that certain pairwise interactions become indistinguishable from each other, and we say explicitly which. In the design-of-experiments literature this choice is called a Resolution-IV fractional factorial (Box, Hunter and Hunter, Statistics for Experimenters, 2nd ed., Wiley 2005), and the name records exactly which effects remain separable.

**buckleyLeverettProblem.** This is the identifier of one benchmark task. Its details are largely unimportant for discussion purposes. In line 290, we describe its relevant attributes of it being 1D and therefore a relatively simple task. The identifier appears in the context of benchmark tasks and is defined in its second mention.

### Response to W2: "deck", and the two sentences quoted

**"Deck"** is defined in Section 3, we assumed the terminology of “input deck” to be standard and widely understood but the reviewer is right that a reader meets it earlier. We will move the definition to first use, in the abstract:

> An **input deck** is the configuration a simulator reads to define a run. For GEOS it is one or more XML files specifying the mesh, the physics modules to couple, the material models, the solver settings and the requested outputs.

**"The number of strictly perfect decks does not increase under any adapter."** The paper specifies "strictly perfect" as structural similarity above 0.999, later in the same section. We will say it inline instead:

> No configuration increased the number of decks that matched the reference almost exactly (structural similarity above 0.999). The adapters change how often the agent produces something badly wrong, not how often it produces something flawless.

**The failures-as-zero sentence.** To clarify, the point we mean to convey is that we score unscorable output as 0 rather than dropping it from the average, so a system is not rewarded for emitting nothing. Replacement:

> When a run produces no usable deck at all (e.g. no XML file, an empty file, a file that will not parse, timeout, etc.), we score it zero rather than dropping it from the average.

### Response to W3: examples of "briefs" and "structured repair feedback"

Agreed, and both will appear as figures in the revised version.

Here is an example from the Buckley-Leverett task, opening and closing:

> I need to set up a simulation to model a 1D Buckley-Leverett CO2 core flood experiment. The goal is to verify the immiscible displacement of brine by supercritical CO2 in a porous medium against analytical solutions. **Physical Problem and Domain Geometry** \[...\] create a hexahedral mesh of length 0.1 m \[...\]  
> 

> - Permeability is 9.0e-13 m2 in all directions.  
> - The reference porosity is 0.2 at a reference pressure of 10 MPa. \[...\] XML files to create: buckleyLeverett\_base.xml, buckleyLeverett\_benchmark.xml

Here is a real, lightly elided instance of structured repair feedback

> Stop blocked by verify\_outputs hook: \[...\] fail GEOS schema validation. \[...\] wellborePoromechanics.xml:49: element SinglePhasePoromechanics: Schemas validity error : Element 'SinglePhasePoromechanics', attribute 'porousMaterialNames': The attribute 'porousMaterialNames' is not allowed. \[...\] Fix the offending element/attribute names against the schema. Re-validate locally with xmllint \--schema \[...\] \--noout .xml before ending your turn.

### Closing

We would rather show the fixes than argue about them, which is why the replacement text is above rather than described. If any of it is still not clear enough, we would welcome being told so during the discussion period and will act on it.

# nBNe\_latest

## Response to Reviewer nBNe

We thank the reviewer for the careful reading and the positive assessment. All three questions point at things we agree with.

### Q1. Convergence checks and output validation

This was the most common thread across the reviews and we made it our first priority. We now evaluate along three new axes beyond structural similarity, on the held-out split:

- **Simulation Execution**: decks accepted by GEOS rise from 78.2% (Vanilla) to 90.0% once the simulator's own input check replaces the schema linter inside the adapter loop, and **100%** of accepted decks ran to completion with a converged solver (77 of 77). Execution is not the bottleneck, deck construction is.  
- **Physics Plausibility**  
  - **Simulation Output**: injecting an identical ground-truth output block into both decks and comparing mesh-independent reductions of each physical quantity gives **mean fidelity 0.958** (91 runs across various tasks and experimental settings) conditioned on the deck running. Since our tasks are sourced from the documentation examples which correspond to representative workflows, the ground truth outputs are physically meaningful, making fidelity useful.  
  - **Simulation Input**: an LLM judge rates each deck section for physical materiality; its score on the physics-bearing sections predicts measured output fidelity at **rho \= 0.418**. This needs calibration against domain expert judgements before we would offer it as a metric, and we reserve that for follow-up work.

**Please see our response to Reviewer 1 for more discussion on TreeSim and newer evaluation protocols**, which gives the protocol and all numbers.

### Q2. Levels of human expertise and a collaborative setting

We agree the human comparison is better described as a preliminary calibration and will relabel it. We maintain it remains a useful calibration, since it establishes a human pace on a relatively easy 1D problem. Scaling it is challenging: recruiting PhD-level geophysics knowledge workers for long, involved tasks such as simulation configuration.

The reviewer’s suggestion of examining different expertise levels is useful and might allow for more participants to be added to the human baseline. Indeed, this motivated our discussion with a GEOS expert (developer) and including a geophysics domain expert (but not GEOS simulator experts) for the hands-on experiment. We aim to improve scale and interactivity in future work.

One observation from our own data supports the reviewer's instinct about interactivity, and shows why it needs a different task design. In a companion study (see Section 6.4) we gave the agent an explicit channel for consulting a human expert and progressively removed information from the task brief. The agent used the channel in only 2 of 64 trials, because the on-disk example library acted as a cheaper substitute for asking. Eliciting genuine collaboration therefore requires tasks whose missing information cannot be recovered from accessible examples, which is itself an open benchmark-design problem. This finding also mirrors the broader result that LLMs optimized for autonomous work are not immediately equipped for interactive problem solving \[6\] \[7\]. 

Overall, bridging this gap between benchmark tasks and real practitioner usage is a key direction for our future work.

### Q3. The exact Claude Code version

The version used for experiments is **2.1.119**.

### W1. No fundamentally new agent architecture

We agree, and it is deliberate. Rather than building a new agent architecture around a new domain, simulator and workflow, or optimizing the entire harness, we search a small set of lightweight modules implementing proven components. A result there is informative precisely because the intervention is cheap: a real effect argues against rebuilding an agent loop for every new scientific target.

### W2. TreeSim is structural

Our task scope assumes a complete user specification, so the agent's task is translation into the simulator DSL and structural evaluation is appropriate. Moreover, because the tasks are mined from GEOS documentation examples the physics is fixed on the input side and hand-validated on the reference side. As we widen the agent's responsibility to demand less of the user, plausibility becomes a first-order question, which is why the evaluation is expanding alongside the task scope (see Q1).

### W4. Task set size and diversity

**GEOS scale.** The evaluation covers 27 tasks (17 validation, 10 held-out), each run in every cell. Two things set this scale: the tasks are mined from GEOS documentation examples, which yield 46 candidates in total, so the achievable set is of this order; and within a fixed compute budget, run counts balloon with various ablations, repeated runs for error bars, and other experiments on backbone models, and harnesses. We judged breadth across those conditions more valuable than more documentation examples within GEOS: generalization is better tested by a second and third simulator than by a 28th GEOS task. This is in line with contemporary work in the area, which evaluates on 2–12 cases \[1–5\]. We are working with our domain expert collaborators to author tasks beyond the documentation corpus.

**Task-type diversity.** Since submission we have grown OpenFOAM from 5 tasks to 30 with a second simulator-native baseline, and added **LAMMPS as a third simulator** (9 molecular-dynamics tasks, two backbone models, with a 20-task scale-up underway). This speaks to diversity as well as scale: LAMMPS input is a command script with no formal schema, so it tests whether the recipe is tied to XML. It is not, but the binding component shifts from completion enforcement to memory and retrieval, because LAMMPS scripts are already structurally complete almost everywhere. The reviewer cited cross-simulator transfer and the reduction in complete failures as the paper's major strengths, and both now hold at larger scale.

\[1\] Zhang et al. Agentic AI for Particle-Based Simulation: Automating SPH Workflows for Debris Flow Modeling. arXiv:2605.09265, 2026\.  
\[2\] Wang et al. MDForge: Agentic Molecular Dynamics Pipeline Design under Sparse Simulator Feedback. arXiv:2606.12916, 2026\.  
\[3\] Zhao, Chandrasekhar & Farimani. PolyJarvis: LLM Agent for Autonomous Polymer MD Simulations. arXiv:2604.02537, 2026\.  
\[4\] Guilbert et al. DynaMate: An Autonomous Agent for Protein-Ligand Molecular Dynamics Simulations. arXiv:2512.10034, 2025\.  
\[5\] Dong, Lu & Yang. CFD-Copilot: Leveraging domain-adapted large language model and model context protocol to enhance simulation automation. Chinese Journal of Aeronautics, 2026\.  
\[6\] Wu, Shirley, et al. "Collabllm: From passive responders to active collaborators." arXiv preprint arXiv:2502.00640 (2025).   
\[7\] Zhou, Xuhui, et al. "Tom-swe: User mental modeling for software engineering agents." arXiv preprint arXiv:2510.21903 (2025). 
