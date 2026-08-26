## Response to Reviewer nBNe

We thank the reviewer for the careful reading and positive assessment. We appreciate the recognition of SIGA's practical value, technical soundness, reduction in complete failures, and transfer across simulators. We address each question and concern below.

### W2 / Q1. Additional evaluation: convergence checks and output validation

This was a common thread across the reviews, and we made it our first priority. Please see our response to Reviewer gep1 for the full protocol and all numbers; in brief, on the held-out split:

- **Simulation execution.** Decks accepted by GEOS rise from 78.2% for Vanilla to 90.0% for S+X once the simulator's own input check replaces the schema linter inside the adapter loop, and every accepted deck we tested ran to completion with a converged solver. Execution is not the bottleneck; deck construction is.
- **Simulation output.** Injecting an identical ground-truth output block into both decks and comparing mesh-independent reductions of each physical quantity gives mean fidelity 0.958 conditional on the deck running, with 46% above 0.999. Because our tasks are sourced from documentation examples corresponding to representative workflows, the ground-truth outputs are physically meaningful, which is what makes the fidelity measure interpretable.
- **Simulation input.** An LLM judge rates each deck section for physical materiality; its score on the physics-bearing sections predicts measured output fidelity at Spearman rho = 0.418 (p = 0.0006). This needs calibration against domain-expert judgments before we would offer it as a metric, and we reserve that for follow-up work.

### W3 / Q2. Human expertise and human-agent collaboration

The human experiment is designed as a preliminary calibration of the time needed for geophysics domain experts to learn GEOS conventions and configure a simple 1D task, rather than as a population-level comparison. We will make this intent explicit, describe the participants' backgrounds more clearly, and avoid drawing broad human-efficiency conclusions.

We also explored human-agent interaction in a companion experiment (Section 6.4) where the agent could consult a human as information was progressively removed from the task specification. The agent used this channel in only 2 of 64 trials, largely because the local example library provided an easier source of information. This suggests that (1) a more robust collaboration benchmark must design for clear informational and capability boundaries between agent and human, and (2) models optimized for autonomous task completion are not immediately prepared for collaborative modes, mirroring broader findings in the literature [1, 2]. Bridging the gap between benchmark tasks and real practitioner usage is a key direction for our future work.

### Q3. Exact Claude Code version

All experiments used Claude Code (harness) version **2.1.119**. We will add this to the reproducibility details.

### W1. Contribution beyond a new agent architecture

SIGA is deliberately not a new agent architecture. Rather than building a new agent stack around each new domain, simulator, and workflow, or optimizing the entire harness, we search a small set of lightweight modules implementing proven components. A positive result under that constraint is informative precisely because the intervention is cheap: a real effect argues against rebuilding the agent loop for every new scientific target.

**The paper contributes the modular adapter design**, the GEOS input-deck authoring benchmark, a controlled factorial study of the adapter components, and an analysis of which simulator-authoring failures these components do and do not address. The cross-simulator studies further test whether the same grounding approach transfers when both the simulator and interface format change.

### W4. Task scale and diversity

The GEOS benchmark contains 27 distinct documentation-derived tasks: 17 for development and 10 held out for final evaluation, each evaluated across all factorial cells and repeated runs. The documentation corpus yielded 46 candidate examples in total, and we are working with domain collaborators to add expert-authored tasks beyond this source. The resulting scale is comparable to contemporary work in this area (see our response to Reviewer gep1). We will also describe the task coverage more clearly and report task-level uncertainty for the main results.

We expanded the OpenFOAM study from 5 to 30 tasks and replaced the static linter with a validator that runs the OpenFOAM solver in a container: on the expanded set the best cell produces an executable case on 89.7% of tasks, against 10% for the Foam-Agent baseline and 22% for MetaOpenFOAM on a smaller task set. We also added an initial LAMMPS study with 9 molecular-dynamics tasks and two backbone models, with a 20-task scale-up underway. Because LAMMPS uses command scripts rather than XML or a formal schema, it provides a distinct test of whether SIGA depends on the GEOS interface format. It does not, but the binding component shifts: LAMMPS scripts are structurally complete almost everywhere, so the gain comes from knowledge injection rather than completion enforcement. On a 0-to-10 judge scale, scores move from 4.56 to 7.78 on one backbone and from 6.33 to 6.89 on the other. This study remains single-run and we present it as qualitative transfer evidence.

Together, these additions broaden both the scale of the evaluation and the diversity of simulator interfaces, and support transfer across the three evaluated simulators.

**References**

[1] Wu et al. CollabLLM: From Passive Responders to Active Collaborators. arXiv:2502.00640, 2025. [2] Zhou et al. ToM-SWE: User Mental Modeling for Software Engineering Agents. arXiv:2510.21903, 2025.
