## **Response to the Area Chair**

We thank the Area Chair for the thoughtful meta-review and clear summary of the discussion.

SIGA introduces a lightweight way to ground general-purpose coding agents in scientific simulators without retraining the model or building a new agent architecture. It adds modular support for simulator-specific retrieval, procedural guidance, validation, and termination, and uses a factorial study to identify which components improve reliability and efficiency.

The reviewers consistently recognized the importance of the problem (gep1, kEdh, nBNe), the practical and technically sound design (kEdh, nBNe), the systematic component analysis (gep1), and the reduction in catastrophic failures (gep1, kEdh, nBNe). They also viewed the OpenFOAM transfer results as evidence that the approach is not limited to GEOS (kEdh, nBNe). All three reviewers rated the paper’s significance and originality as good or better.

Since the reviews, we have addressed each of the main concerns with new experiments and targeted revisions.

**Evaluation Metrics.** We added direct evaluation of simulator acceptance, execution, convergence, and physical-output fidelity on the held-out GEOS split. With GEOS’s native input checker integrated into SIGA, 27 of 30 generated decks were accepted. Across the accepted decks in our execution study, all 77 of 77 simulations completed successfully with the solver converging.

We also compare generated and reference simulations using normalized output specifications while leaving the generated physical configuration unchanged. Among executable decks, the mean output fidelity is 0.958, and 46% achieve fidelity above 0.999. These results confirm SIGA’s reliability extends beyond structural correctness as measured by TreeSim: the generated configurations execute reliably and closely reproduce the intended physical behavior.

**Experimental scope.** The main GEOS study contains 27 tasks, including 10 held-out tasks, evaluated across component combinations and repeated runs. We will describe their coverage more clearly and report task-level uncertainty for the main results. We have also expanded the OpenFOAM study from 5 to 30 tasks, added two simulator-native baselines, and completed an initial evaluation on 9 LAMMPS tasks. These experiments provide evidence of transfer across the evaluated geophysics, fluid-dynamics, and molecular-dynamics simulators.

**Clarity.** To make the paper easier to follow for readers outside scientific simulation, we will add an end-to-end overview figure, introduce each component in plain language, provide execution artifact examples (briefs, feedback), and clarify the relationship among the tasks, metrics, and factorial analysis. We will also state the central contribution more directly from the outset: SIGA is a lightweight adapter that improves an existing coding agent’s ability to work reliably with scientific simulators.

**Human comparison.** We will present the two-participant experiment explicitly as a preliminary calibration of simulator onboarding and configuration time for one representative task, rather than as a broad human-efficiency comparison.

Together, the new results strengthen the paper’s main conclusion: lightweight simulator-interface grounding reduces catastrophic failures and improves coding-agent reliability, and this translates into simulator-accepted, executable, and physically consistent simulations across domains.

Response to Reviewer gep1

We thank the reviewer for the thoughtful and actionable review. We appreciate the recognition of the practical importance of simulator setup, the value of wrapper-level grounding, the factorial design, and the reduction in catastrophic failures. We address each question below.

### **W1./Q1. Evaluation Metrics**

TreeSim primarily checks for structural and value equivalence. For our task scope of converting well specified briefs into simulator input decks, this is appropriate. Because our tasks are derived from validated GEOS examples, similarity to the reference is a proxy for physical meaningfulness in this setting. To make the evaluation more complete for future expanded scope, we further check for schema-validity, execution, convergence, and physical-output tests on the held-out tasks.

**Schema validity.** We increased the evaluation from 3 to 17 runs per task. Vanilla produced a well-formed, schema-valid deck in 155/170 runs, compared with 170/170 for S+X and 100/100 for X+M. The improvement over Vanilla is 8.8 percentage points, with a run- and task-clustered 95% confidence interval of \+2.9 to \+16.5 points (p=0.0006).

**Execution and convergence.** We replaced the schema linter inside the adapter loop with GEOS’s native input checker. GEOS accepted 27/30 S+X decks on the held-out evaluation. Across all accepted decks tested for execution, 77/77 completed successfully and reached solver convergence. For context, GEOS accepted 133/170 Vanilla decks in the larger repeated-run evaluation.

**Physical-output fidelity.** Generated and reference decks may request different output variables. We therefore apply the same output specification to both while leaving the generated physical configuration unchanged. We then compare normalized, mesh-independent summaries of the resulting physical quantities. Among executable decks, mean output fidelity is 0.958, and 46% achieve fidelity above 0.999. TreeSim also correlates with output fidelity ((\\rho=0.362), 95% CI 0.197–0.505, (p=0.0001)).

These results help flesh out a more complete evaluation and confirm the bottleneck at the schema correctness layer. Once GEOS accepts a deck, it reliably executes and generally reproduces the reference outputs.

### **W3./Q2. Prefix bug and the roles of S and X**

**Native-plugin-prefix bug.** We ran a targeted ablation over 17 tasks with three runs each. Removing the prefix changes TreeSim from 0.913 to 0.917, a difference of \+0.004, and no task changes by more than 0.10. The prefix acted as minor distractor text and slightly reduced SIGA performance. Vanilla and the self-evolved adapter were unaffected. In short, the impact magnitude of this issue is minor and its direction causes SIGA scores to be slightly understated.

**Separating S from X.** S and X are varied independently in the Resolution-IV design. The held-out results also help isolate the effect of S:

* X+M: (0.768 \\pm 0.005)  
* S+X+M: (0.783 \\pm 0.022)

Holding X and M fixed, adding S improves the result. The same ordering appears without memory, where S+X reaches 0.781. The results support the distinct roles of the two components: X gives the agent a validator it can call during generation, while S ensures that validation occurs before submission.

### **Q3. OpenFOAM transfer**

We expanded the OpenFOAM study from 5 to 30 tasks and replaced the static linter with a validator that runs the OpenFOAM solver in a container.

Across the full factorial study, the best SIGA configuration produces executable cases on 26/29 evaluable tasks (89.7%); **\[briefly explain why one task was not evaluable\]**. Vanilla Claude Code produces 4/30 executable cases. The best SIGA configuration is also stable across three seeds, with text-similarity scores of 0.668, 0.685, and 0.665.

On the matched subset used for the external baselines:

* SIGA: **\[insert executable count\]/10**  
* Foam-Agent: 1/10  
* MetaOpenFOAM: 2/9

The strongest transfer result is the improvement in execution reliability. In the revision, we will limit this claim to the OpenFOAM tasks evaluated here and make clear that the experiment tests executable structure rather than physical correctness.

### **W2. Experimental scale**

The GEOS benchmark contains 27 distinct documentation-derived tasks: 17 for development and 10 held with the split mostly for improving iteration speed on the factorial eval and providing a held out set for the self-evolution setting. This task set dimension is bounded by our resource budget allocated across factorial component combinations, repeated runs, and other experiments involving different models, harnesses, and domains. In the revision, we will describe the physical and configuration coverage of the held-out tasks more clearly and report task-level uncertainty for the main results.

The task pool itself is currently bounded by the available GEOS documentation examples. We are also working with domain collaborators to author additional tasks beyond this corpus.

### **Q4. Human comparison**

The human study is intended as a preliminary calibration of the time required to learn GEOS conventions and configure one representative task. We will label it accordingly, and avoid using it to support a broad human-efficiency claim.

**Response to Reviewer kEdh**

We thank the reviewer for the careful reading and concrete suggestions. We also appreciate the clear summary of the paper’s main practical finding: lightweight verification around an existing coding agent can substantially reduce failures on difficult scientific-simulation tasks without retraining the model.

The review identifies several places where key concepts appear before they are explained. We will address this by moving definitions to first use, replacing compressed terminology with plain language, and adding a running example that connects the task, adapter, validation process, and results.

### **Terminology and experimental design**

We will remove “Resolution-IV fractional factorial” from the early narrative and first explain the design directly:

> We study four adapter components. Testing them one at a time would miss interactions, while testing all 16 combinations would double the experiment. We therefore evaluate eight carefully selected combinations that let us estimate each component’s main effect without confounding it with a two-component interaction. Some interaction effects remain indistinguishable, which we state explicitly in the experimental section.

The formal design-of-experiments term will appear only after this motivation.

We will also explain `buckleyLeverettProblem` at first mention: it is a relatively simple one-dimensional benchmark in which CO₂ displaces brine through porous rock.

### **“Input deck” and evaluation wording**

We will define “input deck” when it first appears:

> An input deck is the configuration that defines a simulator run. In GEOS, it consists of XML files specifying the geometry, physical models, materials, solver settings, and requested outputs.

We will also replace the two sentences highlighted by the reviewer.

Current:

> The number of strictly perfect decks does not increase under any adapter.

Revised:

> The adapters do not increase the number of outputs that nearly match the reference. Their main benefit is reducing severely incomplete or invalid outputs.

Current:

> Headline numbers average TreeSim under failures-as-zero: parse errors, timeouts, failed\_no\_outputs, and missing XML outputs all score 0, so systems are not rewarded for unscorable files.

Revised:

In some runs the agent does not produce a usable input deck for various reasons (e.g. missing files, empty files, invalid schema, or agent timeout). We score these runs as zero instead of removing them from the average to ensure this reliability faults are accounted for.

> 

### **Concrete examples**

We will add a running example that shows both the task given to the agent and the feedback returned by SIGA.

Example task brief:

> Set up a one-dimensional Buckley–Leverett simulation of supercritical CO₂ displacing brine through porous rock. Use a 0.1 m domain, permeability of (9.0\\times10^{-13},\\mathrm{m}^2), porosity of 0.2, and a reference pressure of 10 MPa. Produce the required GEOS XML files.

Example repair feedback:

> Validation failed: `SinglePhasePoromechanics` contains an unsupported attribute, `porousMaterialNames`. Correct the attribute and validate the XML again before submitting.

### **NeurIPS relevance**

We believe the paper is strongly aligned with the NeurIPS Use-Inspired contribution type. The central question is broader than automating one GEOS workflow: how can a general-purpose coding agent be grounded in a complex scientific tool without retraining the underlying model?

SIGA addresses this question through a modular adapter built from retrieval, procedural guidance, validation, and enforced checking. The factorial study shows which components improve reliability, which do not, and which failure modes remain. This provides evidence about the design of reliable tool-using agents, not only a system for one simulator.

The OpenFOAM study applies the same approach to a second simulator with a different interface. We expanded this evaluation from 5 to 30 tasks and added execution-based validation, providing stronger evidence that the method transfers beyond GEOS.

We will make this broader agent-design contribution more explicit in the introduction while keeping the scientific application and practical motivation central.

## **Response to Reviewer nBNe**

We thank the reviewer for the careful reading and positive assessment. We appreciate the recognition of SIGA’s practical value, technical soundness, reduction in complete failures, and transfer across simulators. We address each question and concern below.

### **W2./Q1. Additional Evaluation: Convergence checks and output validation**

TreeSim checks for structural and value equivalence. For our task scope of converting well specified briefs into simulator input decks (a DSL translation task), this is appropriate. Because our tasks are derived from validated GEOS examples, similarity to the reference is a proxy for physical meaningfulness in this setting. To make the evaluation more complete for future expanded scope, we further check for schema-validity, execution, convergence, and physical-output tests on the held-out tasks.

**Schema validity.** We increased the evaluation from 3 to 17 runs per task. Vanilla produced a well-formed, schema-valid deck in 155/170 runs, compared with 170/170 for S+X and 100/100 for X+M. The improvement over Vanilla is 8.8 percentage points, with a run- and task-clustered 95% confidence interval of \+2.9 to \+16.5 points (p=0.0006).

**Execution and convergence.** We replaced the schema linter inside the adapter loop with GEOS’s native input checker. GEOS accepted 27/30 S+X decks on the held-out evaluation. Across all accepted decks tested for execution, 77/77 completed successfully and reached solver convergence. For context, GEOS accepted 133/170 Vanilla decks in the larger repeated-run evaluation.

**Physical-output fidelity.** Generated and reference decks may request different output variables. We therefore apply the same output specification to both while leaving the generated physical configuration unchanged. We then compare normalized, mesh-independent summaries of the resulting physical quantities. Among executable decks, mean output fidelity is 0.958, and 46% achieve fidelity above 0.999. TreeSim also correlates with output fidelity (Spearman rho=0.362).

These results help flesh out a more complete evaluation and confirm the bottleneck at the schema correctness layer. Once GEOS accepts a deck, it reliably executes and generally reproduces the reference outputs.

### **W3./Q2. Human expertise and human-agent collaboration**

The human experiment is designed as a preliminary calibration of the time needed for geophysics domain experts to learn GEOS conventions and configure a simple 1D task, rather than as a population-level comparison. We will make this intent explicit, describe the participants’ backgrounds more clearly, and avoid drawing broad human-efficiency conclusions from the study.

We also explored human-agent interaction in a companion experiment (Section 6.4) where the agent could consult a human as information was progressively removed from the task specification. The agent used this channel in only 2 of 64 trials, largely because the local example library provided an easier source of information. This suggests that (1) a more robust collaboration benchmark should design for clear informational/capability boundaries between agents and (2) that models optimized for autonomous task completion are not fully immediately prepared for collaborative modes.

### **Q3. Exact Claude Code version**

All experiments used Claude Code version **2.1.119**. We will add this information to the reproducibility details.

### **W1. Contribution beyond a new agent architecture**

SIGA is deliberately not a new agent architecture. Its contribution is a lightweight grounding layer that makes an existing coding agent more reliable in a specialized scientific interface without retraining the model or rebuilding the agent loop.

The paper contributes the modular adapter design, the GEOS input deck authoring benchmark, a controlled factorial study of the adapter components, and an analysis of which simulator-authoring failures these components do and do not address. The cross-simulator studies further test whether the same grounding approach transfers when both the simulator and interface format change.

This design is practically important because it shows that meaningful reliability gains can come from adapting the interface around an existing agent rather than developing a separate agent stack for every simulator.

### **W4. Task scale and diversity**

The GEOS benchmark contains 27 distinct documentation-derived tasks: 17 for development and 10 held out for final evaluation. The held-out tasks are evaluated across all factorial cells and repeated runs. The documentation corpus yielded 46 candidate examples in total, and we are working with domain collaborators to add expert-authored tasks beyond this source. We will also describe the task coverage more clearly and report task-level uncertainty for the main results.

We expanded the OpenFOAM study from 5 to 30 tasks, replaced the static linter with a validator that runs the OpenFOAM solver in a container, and added two external baselines. We also added an initial LAMMPS study with 9 molecular-dynamics tasks and two backbone models. Because LAMMPS uses command scripts rather than XML or a formal schema, it provides a distinct test of whether SIGA depends on the GEOS interface format.

Together, these additions broaden both the scale of the evaluation and the diversity of simulator interfaces, and support transfer across the three evaluated simulators.

\=========================================

Response to the Area Chair  
We sincerely thank the AC for a meta-review that cleanly summarizes the main concerns raised by reviewers.

## Contribution Summary

We study the application of coding agent techniques to the **novel domain of geophysics simulation**, proposing a lightweight adaptation method.

- **Problem significance**: Automating the busy work of configuring simulations for experiments recovers valuable researcher hours for higher-leverage tasks.  
- **Method**: Rather than building a new agent architecture around a new domain, simulator and workflow, or optimizing the entire harness, we search a small set of lightweight modules implementing proven components. The search process also allows for light adaptation across domains.  
- **Cross-domain validation**: Our primary work focuses on geophysics (GEOS), but we validate the method in two further domains: fluid dynamics (OpenFOAM) and molecular dynamics (LAMMPS, added post-submission)   
- **Results**:  
  - **vs. human**: Minutes instead of hours  
  - **vs. baseline coding agent**: Reduced variance, preventing catastrophic failures; and up to 22% fewer tool calls and 18% less wall-clock time per task on the harder split, taking the best adapter cell for each measure

## Summary of Reviewer-Identified Strengths

- **Problem significance**: All reviewers credit the problem: the simulator-setup bottleneck is "convincing" (gep1), a "useful real-world application" (kEdh), and a "realistic and useful target" for AI-for-science (nBNe).  
- **Method**: Wrapper-level grounding around an existing harness rather than a new agent stack (gep1); a practical recipe to reduce failures without retraining (kEdh); "well constructed and technically sound" (nBNe).  
- **Experimental design**: The factorial study gives "more insight than a single 'our system vs baseline' comparison," and the bottleneck analysis and negative findings add credibility (gep1).  
- **Reliability**: The "strongest empirical result" (gep1): preventing catastrophic failures (kEdh, nBNe).  
- **Generalization**: OpenFOAM transfer shows the method "isn't limited to just one tool" (kEdh) and is "a major strength" (nBNe).  
- **Human baseline**: "A good calibration point" for expert time-to-learn (nBNe).  
- **Significance and originality**: Rated good or better by all three reviewers, including the one recommending rejection (gep1, kEdh, nBNe).

## Addressing Reviewer Concerns

### 1\. Evaluation metrics

**TreeSim fits the scope we currently study.** Our task scope assumes a complete user specification. As a result the agent's task is translation into the simulator DSL, and structural evaluation is appropriate. Since our tasks are mined from documentation examples, the physics is fixed on the input side, and our similarity-to-ground-truth metric captures this on the output side.

The broader aim of this line of work is to expand the scope of agent responsibility (see the initial exploration in Appendix J), so we are expanding the evaluation with new metrics and protocols.

**New metrics** (all on the held-out split):

**Simulation Execution:**

- **Metric**: (binary) does GEOS accept the deck, and does the run complete with a converged solver?  
- **Result**: decks accepted rises from **78.2%** (Vanilla, 133 of 170 runs) to **90.0%** (S+X, 27 of 30 runs) once the simulator's own input check replaces the schema linter inside the adapter loop. Of accepted decks, **100%** ran to completion with a converged solver (77 of 77).

**Simulation Output:**

- **Metric**: (continuous) inject an identical ground-truth output block into both decks, run both, and compare mesh-independent reductions of each physical quantity, each normalized by the reference's own scale  
- **Result**: mean fidelity **0.958**, conditioned on the deck running, with 46% of running decks reproducing the reference at fidelity above 0.999

**Input Deck Evaluation for Physics Plausibility:**

- **Metric**: an LLM judge rates each deck section for physics considerations  
- **Result**: the judge's score predicts measured output fidelity at Spearman rho \= **0.418** (p \= 0.0006)

We are happy to give the full protocol for any of these during discussion, and will document it in the revision.

### 2\. Clarity and jargon

We discuss this in detail in our response to Reviewer kEdh: locating definitions and explanations, adding more context, and so on. In short, we are happy to add further clarifications for the revision.

### 3\. Limited experimental scale

**GEOS scale.** The evaluation covers 27 tasks (17 validation, 10 held-out), each run in every cell. Two things set this scale. The tasks are mined from GEOS documentation examples, which yield 46 candidates in total, so the achievable pool is bounded at roughly this size. And within a fixed compute budget, run counts multiply across ablations, repeated runs for error bars, and further experiments across backbone models and harnesses. We judged breadth across those conditions more valuable than more documentation examples within GEOS: generalization is better tested by a second and third simulator than by a 28th GEOS task. This is in line with contemporary work in the area, which evaluates on 2 to 12 cases \[1-5\]. We are working with our domain expert collaborators to author tasks beyond the documentation corpus.

**Beyond GEOS.** We have since expanded the fluid-dynamics (OpenFOAM) transfer study to 30 tasks and added two simulator-native baselines (see Reviewer gep1's thread). We have also added a third domain, molecular dynamics (LAMMPS), with 9 initial tasks and a 20-task scale-up underway.

### 4\. Human comparison scale

We agree the human baseline is better described as a preliminary calibration, and we are happy to relabel it in the revision. We do maintain, however, that it is a useful calibration: it establishes a human pace on a relatively easy 1D problem. Scale is constrained by time and resources, since recruiting PhD-level geophysics knowledge workers is difficult, especially for long, involved tasks such as simulation configuration.

### 5\. Venue fit (raised by Reviewer kEdh)

Reviewer kEdh suggests a topic misfit for the NeurIPS venue.

- We refer to the NeurIPS 2026 contribution-type guidance defining the Use-Inspired type as work whose main contribution is in framing or designing approaches to meet the needs of a specific real-world application, often involving engaging with domain experts. We think our paper matches these criteria.

The review recommends rejection but does not identify a technical, evaluation, reproducibility, or ethical concern. We are glad to address the writing concerns raised, and we would welcome the reviewer's view on whether those concerns alone motivate the score.

\[1\] Zhang et al. Agentic AI for Particle-Based Simulation: Automating SPH Workflows for Debris Flow Modeling. arXiv:2605.09265, 2026\. \[2\] Wang et al. MDForge: Agentic Molecular Dynamics Pipeline Design under Sparse Simulator Feedback. arXiv:2606.12916, 2026\. \[3\] Zhao, Chandrasekhar & Farimani. PolyJarvis: LLM Agent for Autonomous Polymer MD Simulations. arXiv:2604.02537, 2026\. \[4\] Guilbert et al. DynaMate: An Autonomous Agent for Protein-Ligand Molecular Dynamics Simulations. arXiv:2512.10034, 2025\. \[5\] Dong, Lu & Yang. CFD-Copilot: Leveraging domain-adapted large language model and model context protocol to enhance simulation automation. Chinese Journal of Aeronautics, 2026\.

---

# Response to Reviewer gep1

We thank the reviewer for an actionable review. We do our best to address the feedback here.

## W1 / Q1. Evaluation beyond structure

**TreeSim fits the scope we currently study.** Our task scope assumes a complete user specification, so the agent's task is translation into the simulator DSL and structural evaluation is appropriate. Moreover, because our tasks are mined from GEOS documentation examples, the physics is fixed on the input side and hand-validated on the reference side, so similarity to ground truth captures it on the output side.

The broader aim of this line of work is to expand the scope of agent responsibility (see the initial exploration in Appendix J, with results in Section 4.6), so we are expanding the evaluation with new metrics and protocols. Results below are on the held-out split.

**Artifact validity.** We re-ran this at 17 runs per cell rather than 3, because these are counts of rare events. Vanilla produces a well-formed, schema-valid deck on **155 of 170** runs, S+X on **170 of 170**, and X+M on **100 of 100**. The 8.8-point gap has a run-and-task clustered 95% CI of \+2.9 to \+16.5 points, p \= 0.0006, across 270 adapter runs with no failures.

New metrics beyond the artifact:

- **Simulation Execution**  
  - **Metric**: (binary) does GEOS accept the deck, and does the run complete with a converged solver?  
  - **Result**: decks accepted rises from **78.2%** (Vanilla, 133 of 170 runs at 17 runs per cell) to **90.0%** (S+X, 27 of 30 runs at 3 runs per cell) once the simulator's own input check replaces the schema linter inside the adapter loop. Of accepted decks, **100%** ran to completion and converged (77 of 77). GEOS's own input check is stricter than schema validity, which is why acceptance rates sit below the artifact-validity rates above.  
  - **Insight**: execution is not the bottleneck, deck construction is, so a 2.5 second acceptance check captures nearly all of the execution signal  
- **Simulation Output**  
  - **Metric**: (continuous) inject an identical ground-truth output block into both decks, run both, and compare mesh-independent reductions (min, max, mean, root-mean-square) of every physical quantity, each normalized by the reference's own scale, with no interpolation  
  - **Result**: mean fidelity **0.958** conditioned on the deck running, 46% of running decks reproduce the reference at fidelity above 0.999, and structural similarity predicts fidelity at Spearman rho \= **0.362** (95% CI 0.197 to 0.505, p \= 0.0001)  
  - **Insight**: the gap between structure and physics sits in decks that fail to run, not in decks that run and are wrong, which is consistent with the reliability framing the review credits  
- **Input Deck Evaluation for Physics Plausibility**  
  - **Metric**: an LLM judge rates each deck section against the reference for physical materiality, using four judges from four model families, none of them the agent's backbone, blind to condition and order-swapped  
  - **Result**: the judge's score on the physics-bearing sections predicts measured output fidelity at rho \= **0.418** (p \= 0.0006); the Solvers subtree alone reaches rho \= 0.456  
  - **Comment**: it does not beat plain structural scoring at this task, and two of four judges ordered the conditions differently. It therefore needs calibration against domain expert judgments before we would offer it as a metric, which we reserve for follow-up work

We also tested re-weighting the structural metric toward physics-bearing sections, which yields at most a small improvement (+0.033, 95% CI \-0.003 to \+0.072), so uniform weighting now rests on a test rather than an assumption. We are happy to give the full protocol for any of these during discussion, and will document it in the revision.

## W2. Experimental scale

**GEOS scale.** The evaluation covers 27 tasks (17 validation, 10 held-out), each run in every cell. Two things set this scale. The tasks are mined from GEOS documentation examples, which yield 46 candidates in total, so the achievable pool is bounded at roughly this size. And within a fixed compute budget, run counts multiply across ablations, repeated runs for error bars, and further experiments across backbone models and harnesses. We judged breadth across those conditions more valuable than more documentation examples within GEOS: generalization is better tested by a second and third simulator than by a 28th GEOS task. This is in line with contemporary work in the area, which evaluates on 2 to 12 cases \[1-5\]. We are working with our domain expert collaborators to author tasks beyond the documentation corpus.

**Beyond GEOS.** Since submission we have expanded the OpenFOAM transfer study and added a third domain, molecular dynamics, with the LAMMPS simulator.

- **OpenFOAM: 30 tasks (up from 5), a real-execution validator, and two external baselines.** The adapter's validator now runs the actual OpenFOAM solver in a container rather than a static linter. Across the full 9-cell factorial on 30 tasks, the best cell (R+S+X+M) scores 0.668 on the text-similarity metric and produces a structurally executable case on 26 of 29 tasks (89.7%), stable across three seeds (0.668, 0.685, 0.665). This far outstrips the Vanilla Claude Code baseline with 4/30 executable outputs. External baselines, run on a 10-task subset of the same pool under matched budgets, the same bounded real-execution mechanism, and the same post-hoc executability check, score 0.565 (Foam-Agent, 1 of 10 executable) and 0.276 (MetaOpenFOAM, 2 of 9). The text-similarity margins are modest; the executability margin is not, and executability is the measure that corresponds to the reliability effect the review singles out. As with GEOS, it measures structural acceptance rather than physical correctness.  
- **LAMMPS: a third simulator.** 9 molecular-dynamics tasks on two backbone models, with a 20-task scale-up underway. LAMMPS input is a command script with no formal schema, which tests whether the recipe is tied to XML. It is not, but the binding component shifts: scripts are structurally complete almost everywhere, so the gain comes from knowledge injection rather than completion enforcement. Judge scores move from 4.56 to 7.78 on one backbone and from 6.33 to 6.89 on the other \[CONFIRM: state the judge scale, e.g. 0 to 10\].

The LAMMPS study remains single-run and we present it as qualitative transfer evidence. The reliability effect the review singles out as our strongest result replicates on all three interfaces.

## Q2a. The native-plugin-prefix bug

We can bound the effect directly, and find it to be minimal in magnitude. A targeted ablation gives 0.917 without the prefix against 0.913 with it, a difference of **\+0.004** across 3 runs on 17 tasks, with no single task moving by more than 0.10. The direction favors our conclusions: the prefix bug introduced distractor text that slightly hurt the performance of SIGA runs, so reported SIGA performance is slightly understated. Vanilla and SE, the self-evolved adapter variant, are unaffected by this prefix.

## Q2b. Separating S from X

The Resolution-IV design does separate the S and X main effects.

On the reviewer's underlying question, whether the termination hook still contributes once the agent-callable validator is available, the held-out column of Table 1 builds the two up in sequence:

| Cell (held-out) | TreeSim | vs Vanilla |
| :---- | :---- | :---- |
| Vanilla | 0.720 ± 0.081 | n/a |
| X+M (validator plus memory) | 0.768 ± 0.005 | \+0.048 |
| S+X+M (termination hook added on top) | **0.783 ± 0.022** | **\+0.063** |

M is the procedural-memory cheatsheet and is unrelated to validation, so the step from X+M to S+X+M isolates the addition of the termination hook, and it is positive. S+X reaches 0.781 on the same split, so the ordering holds with and without memory. These are three runs per cell, so we would not over-read the margins between adapter cells, and we would be glad to run a dedicated build-up experiment isolating the interaction.

We include both components by design: X gives the agent the tooling to check its own work mid-turn, and S is the process guarantee that validation is run before submitting the configuration.

## Q3. Strengthening the OpenFOAM study

Done, as described under W2. The clearest separation is on executability, 89.7% for the best SIGA cell against 22.2% and 10.0% for the two simulator-native baselines.

## Q4. The human comparison

We agree it is better described as a preliminary calibration and will relabel it in the revision. We do maintain it is a useful calibration, since it establishes a human pace on a relatively easy 1D problem. Recruiting PhD-level geophysics knowledge workers is difficult, especially for long, involved tasks such as simulation configuration.

## Additional point: limitations wording

We are glad to sharpen this in the main body. For the scope this paper studies, a structural metric is the right primary measure: the specification and its provenance establish that the target simulation is physically meaningful, and the headline numbers measure how reliably the agent reaches it. As the agent's responsibility widens, plausibility becomes a first-order question rather than one settled by the specification, which is why the evaluation protocol is expanding alongside the task scope.

\[1\] Zhang et al. Agentic AI for Particle-Based Simulation: Automating SPH Workflows for Debris Flow Modeling. arXiv:2605.09265, 2026\. \[2\] Wang et al. MDForge: Agentic Molecular Dynamics Pipeline Design under Sparse Simulator Feedback. arXiv:2606.12916, 2026\. \[3\] Zhao, Chandrasekhar & Farimani. PolyJarvis: LLM Agent for Autonomous Polymer MD Simulations. arXiv:2604.02537, 2026\. \[4\] Guilbert et al. DynaMate: An Autonomous Agent for Protein-Ligand Molecular Dynamics Simulations. arXiv:2512.10034, 2025\. \[5\] Dong, Lu & Yang. CFD-Copilot: Leveraging domain-adapted large language model and model context protocol to enhance simulation automation. Chinese Journal of Aeronautics, 2026\.

# Response to Reviewer kEdh

We thank the reviewer for a close and specific reading, and for stating the practical takeaway accurately: adding verification checkpoints to a coding agent substantially reduces failures on difficult scientific tasks without retraining the model.

Each concept the review highlights is defined in the submitted paper, and we locate each below. What the review identifies, usefully, is that several are defined later than their first use, an ordering problem with a definite fix. NeurIPS does not permit a revised PDF during this period, so we give the proposed replacement text inline below.

## Response to W1: Resolution-IV and buckleyLeverettProblem

**Resolution-IV.** The design is explained on line 182, which states that instead of exhaustively testing every combination of factors, we select a subset of configurations that allow us to discern the main effects without being confounded by a two-factor interaction (for example, M only helps when X is present). We propose to remove this language from the abstract and early sections of the paper and reserve this elaboration for the experiments and results sections. We plan to motivate it in plain prose:

> Our aim is to quantify each component's contribution. Testing them one at a time is cheap but cannot detect a component that only helps in combination. Testing all sixteen on/off combinations answers that, but doubles the experiment. We therefore run a carefully chosen half, eight of the sixteen, selected so that each component's individual effect stays separable from the others. The price is that certain pairwise interactions become indistinguishable from each other, and we say explicitly which. In the design-of-experiments literature this choice is called a Resolution-IV fractional factorial (Box, Hunter and Hunter, Statistics for Experimenters, 2nd ed., Wiley 2005), and the name records exactly which effects remain separable.

**buckleyLeverettProblem.** This is the identifier of one benchmark task; its specifics matter less here than its role as an example. Line 290 gives the attributes that matter: it is 1D, and therefore a relatively simple task. The identifier appears in the context of benchmark tasks and is defined at its second mention, which we agree is too late, and we will move the gloss to first use.

## Response to W2: "deck", and the two sentences quoted

**"Deck"** is defined in Section 3\. We had assumed "input deck" to be standard terminology, but the reviewer is right that a reader meets the word earlier. We will move the definition to first use, in the abstract:

> An **input deck** is the configuration a simulator reads to define a run. For GEOS it is one or more XML files specifying the mesh, the physics modules to couple, the material models, the solver settings and the requested outputs.

**"The number of strictly perfect decks does not increase under any adapter."** The paper specifies "strictly perfect" as structural similarity above 0.999, later in the same section. We will state it inline instead:

> No configuration increased the number of decks that matched the reference almost exactly (structural similarity above 0.999). The adapters change how often the agent produces something badly wrong, not how often it produces something flawless.

**"Failures are scored as zero."** The point is that we score unscorable output as 0 rather than dropping it from the average, so a system is not rewarded for emitting nothing. Replacement:

> When a run produces no usable deck at all (for example no XML file, an empty file, a file that will not parse, or a timeout), we score it zero rather than dropping it from the average.

## Response to W3: examples of "briefs" and "structured repair feedback"

Agreed, and both will appear as figures in the revision.

Here is an example from the buckleyLeverettProblem task, opening and closing:

> I need to set up a simulation to model a 1D Buckley-Leverett CO2 core flood experiment. The goal is to verify the immiscible displacement of brine by supercritical CO2 in a porous medium against analytical solutions. **Physical Problem and Domain Geometry** \[...\] create a hexahedral mesh of length 0.1 m \[...\] Permeability is 9.0e-13 m2 in all directions. The reference porosity is 0.2 at a reference pressure of 10 MPa. \[...\] XML files to create: buckleyLeverett\_base.xml, buckleyLeverett\_benchmark.xml

Here is a real, lightly elided instance of structured repair feedback:

> Stop blocked by verify\_outputs hook: \[...\] fail GEOS schema validation. \[...\] wellborePoromechanics.xml:49: element SinglePhasePoromechanics: Schemas validity error : Element 'SinglePhasePoromechanics', attribute 'porousMaterialNames': The attribute 'porousMaterialNames' is not allowed. \[...\] Fix the offending element/attribute names against the schema. Re-validate locally with xmllint \--schema \[...\] \--noout .xml before ending your turn.

## Closing

We would rather show the fixes than argue about them, which is why the replacement text is above rather than described. If any of it is still not clear enough, we would welcome hearing so during the discussion period, and will act on it.

# Response to Reviewer nBNe

We thank the reviewer for the careful reading and the positive assessment. All three questions point to things we agree with.

## Q1. Convergence checks and output validation

This was the most common thread across the reviews, and we made it our first priority. We now evaluate along three new axes beyond structural similarity, on the held-out split:

- **Simulation Execution**: decks accepted by GEOS rise from 78.2% (Vanilla, 133 of 170 runs) to 90.0% (S+X, 27 of 30 runs) once the simulator's own input check replaces the schema linter inside the adapter loop, and **100%** of accepted decks ran to completion with a converged solver (77 of 77). Execution is not the bottleneck, deck construction is.  
- **Simulation Output**: injecting an identical ground-truth output block into both decks and comparing mesh-independent reductions of each physical quantity gives **mean fidelity 0.958**, conditioned on the deck running. Because our tasks are sourced from documentation examples, which correspond to representative workflows, the ground-truth outputs are physically meaningful, which is what makes the fidelity measure interpretable.  
- **Simulation Input**: an LLM judge rates each deck section for physical materiality; its score on the physics-bearing sections predicts measured output fidelity at Spearman rho \= **0.418**. This needs calibration against domain expert judgments before we would offer it as a metric, and we reserve that for follow-up work.

Please see our response to Reviewer gep1 for more discussion on TreeSim and the newer evaluation protocols, which gives the protocol and all numbers.

## Q2. Levels of human expertise and a collaborative setting

We agree the human comparison is better described as a preliminary calibration and will relabel it. We maintain it remains a useful calibration, since it establishes a human pace on a relatively easy 1D problem. Scaling it is difficult: recruiting PhD-level geophysics knowledge workers is hard, especially for long, involved tasks such as simulation configuration.

The reviewer's suggestion of examining different expertise levels is useful and might allow for more participants to be added to the human baseline. Indeed, this motivated both our discussions with a GEOS developer and our inclusion of a geophysics domain expert, one who is not a GEOS expert, in the hands-on experiment. We aim to improve scale and interactivity in future work.

One observation from our own data supports the reviewer's instinct about interactivity, and shows why it needs a different task design. In a companion study (see Section 6.4) we gave the agent an explicit channel for consulting a human expert and progressively removed information from the task brief. The agent used the channel in only 2 of 64 trials, because the on-disk example library acted as a cheaper substitute for asking. Eliciting genuine collaboration therefore requires tasks whose missing information cannot be recovered from accessible examples, which is itself an open benchmark-design problem. This finding also mirrors the broader result that LLMs optimized for autonomous work are not immediately equipped for interactive problem solving \[6, 7\].

Overall, bridging this gap between benchmark tasks and real practitioner usage is a key direction for our future work.

## Q3. The exact Claude Code version

The version used for experiments is **2.1.119**.

## W1. No fundamentally new agent architecture

We agree, and it is deliberate. Rather than building a new agent architecture around a new domain, simulator and workflow, or optimizing the entire harness, we search a small set of lightweight modules implementing proven components. A positive result under that constraint is informative precisely because the intervention is cheap: a real effect argues against rebuilding the agent loop for every new scientific target.

## W2. TreeSim is structural

Our task scope assumes a complete user specification, so the agent's task is translation into the simulator DSL and structural evaluation is appropriate. Moreover, because the tasks are mined from GEOS documentation examples, the physics is fixed on the input side and hand-validated on the reference side. As we widen the agent's responsibility to demand less of the user, plausibility becomes a first-order question, which is why the evaluation is expanding alongside the task scope (see Q1).

## W4. Task set size and diversity

**GEOS scale.** The evaluation covers 27 tasks (17 validation, 10 held-out), each run in every cell. Two things set this scale. The tasks are mined from GEOS documentation examples, which yield 46 candidates in total, so the achievable pool is bounded at roughly this size. And within a fixed compute budget, run counts multiply across ablations, repeated runs for error bars, and further experiments across backbone models and harnesses. We judged breadth across those conditions more valuable than more documentation examples within GEOS: generalization is better tested by a second and third simulator than by a 28th GEOS task. This is in line with contemporary work in the area, which evaluates on 2 to 12 cases \[1-5\]. We are working with our domain expert collaborators to author tasks beyond the documentation corpus.

**Task-type diversity.** Since submission we have expanded the OpenFOAM study to 30 tasks with two external baselines, and added **LAMMPS as a third simulator** (9 molecular-dynamics tasks, two backbone models, with a 20-task scale-up underway). This speaks to diversity as well as scale: LAMMPS input is a command script with no formal schema, so it tests whether the recipe is tied to XML. It is not, but the binding component shifts: LAMMPS scripts are already structurally complete almost everywhere, so the gain comes from knowledge injection rather than completion enforcement. The reviewer cited cross-simulator transfer and the reduction in complete failures as the paper's major strengths, and both now hold at larger scale. On the expanded OpenFOAM set, the best cell produces an executable case on 89.7% of tasks, against 10% and 22% for the two simulator-native baselines. Please see the reviewer gep1 thread for further details on the transfer studies.

\[1\] Zhang et al. Agentic AI for Particle-Based Simulation: Automating SPH Workflows for Debris Flow Modeling. arXiv:2605.09265, 2026\. \[2\] Wang et al. MDForge: Agentic Molecular Dynamics Pipeline Design under Sparse Simulator Feedback. arXiv:2606.12916, 2026\. \[3\] Zhao, Chandrasekhar & Farimani. PolyJarvis: LLM Agent for Autonomous Polymer MD Simulations. arXiv:2604.02537, 2026\. \[4\] Guilbert et al. DynaMate: An Autonomous Agent for Protein-Ligand Molecular Dynamics Simulations. arXiv:2512.10034, 2025\. \[5\] Dong, Lu & Yang. CFD-Copilot: Leveraging domain-adapted large language model and model context protocol to enhance simulation automation. Chinese Journal of Aeronautics, 2026\. \[6\] Wu et al. CollabLLM: From Passive Responders to Active Collaborators. arXiv:2502.00640, 2025\. \[7\] Zhou et al. ToM-SWE: User Mental Modeling for Software Engineering Agents. arXiv:2510.21903, 2025\.  
