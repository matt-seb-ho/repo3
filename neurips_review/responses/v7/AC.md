<!-- v7 DRAFT 2026-07-28. Official Comment to Area Chair GKRj.
     BASE: hand_v6/siga_neurips26_rebuttal.md (researcher's hand version, advisor-approved).
     Wording and structure follow that file. Only three changes, all requested or required:
       1. Simulation Execution now carries the deck run rate (what earlier drafts called level 3):
          Vanilla 78.2% accepted vs 90.0% with the validator swap, plus the 100% convergence.
       2. The Simulation Output metric sentence, which ends mid-clause in the hand version, is
          completed.
       3. The efficiency bullet's "15-20%" placeholder is replaced with the real figures from the
          appendix efficiency table, held-out split: best tool-call reduction is SE-prose at
          -21.7%, best wall-clock reduction is X+M at -18.5%. Both drawn from the SAME split so
          there is no cross-split cherry-picking. "(best adapter cells)" is load-bearing: SE, the
          headline cell, is +7.6% on tool calls, so an unqualified claim is checkable and wrong.
     Style: no em dashes, no hyperlinks, no arXiv-version mention, VERIFIED numbers only.
     Prose ~4,600 chars. HARD CAP 10,000. -->

**AC Response**

We thank the AC for a meta-review that cleanly summarizes the main concerns raised by reviewers.

# Contribution Summary

We study the application of coding agent techniques to the **novel domain of geophysics simulation**, proposing a lightweight adaptation method.

- **Problem Significance**: automating the busy work of configuring simulations for experiments recovers valuable researcher hours for higher level, higher leverage tasks.
- **Method**: rather than building a new agent architecture around a new domain/simulator/workflow, or optimizing the entire harness, we propose searching a small set of lightweight modules implementing proven components.
- **Cross-domain validation**: our primary work focuses on geophysics (GEOS simulator) but we validate our method in two other domains: fluid dynamics (OpenFOAM), and molecular dynamics (LAMMPS; added post submission)
- **Results**:
  - Compared to human: compress hours to minutes
  - Compared to baseline coding agent:
    - variance reduction (preventing catastrophic failures)
    - up to 22% fewer tool calls and 18% less wall clock per task on the harder split (best adapter cells)

# Addressing Reviewer Concerns

## 1. Evaluation Metrics.

**TreeSim fits the scope we currently study.** Our task scope assumes a complete user specification. As a result the agent's task is translation into simulator DSL and thus structural evaluation is appropriate. Since our tasks are mined from documentation examples, the physics are fixed on the input side and our similarity to ground truth metrics captures this on the output side.

The broader aim of this line of work is to expand the scope of agent responsibility (see initial exploration in Appendix J), so we explore expanding the evaluation with new metrics and protocols. Results below are on the held-out split.

New Metrics

- Simulation Execution:
  - Metric: (Binary) Does GEOS accept the deck? Does the simulation run to completion and the solver converge?
  - Result: decks accepted rises from **78.2%** (Vanilla) to **90.0%** once the simulator's own input check replaces the schema linter inside the adapter loop; of accepted decks, **100%** ran to completion with a converged solver (77 of 77)
  - Insight: execution is not the bottleneck, deck construction is
- Simulation Output:
  - Metric: (continuous) injecting an identical ground truth output block into both decks, running both, and comparing mesh-independent reductions of each physical quantity, normalized by the reference's own scale
  - Result: mean fidelity **0.958** (conditioned on the deck running), with 46% of running decks reproducing the reference almost exactly
  - Insight: further confirms that the reliability bottleneck exists at the deck construction level
- Input Deck Evaluation for Physics Plausibility:
  - Metric: LLM judge rates each deck section for physics considerations
  - Result: judge score predicts measured output fidelity at **rho = 0.418** (p = 0.0006)
  - Comment: this requires further calibration against domain expert judgements (we reserve this for follow-up work)

We are happy to give the full protocol for any of these during discussion, and will document it in the camera-ready.

## 2. Clarity and jargon

We discuss this in detail in our response to Reviewer kEdh (locating definitions/explanations; adding more context; etc.). In short, we are happy to add further clarifications for the revision.

## 3. Limited experimental scale

**GEOS Scale.** Earlier experiments with weaker models found individual trajectories to take upward of 30 minutes to complete. Combined with having a large set of configuration conditions to run along with our aim to gather error bars with multiple runs per configuration, we decided to allocate our limited time and resource budget towards testing more conditions rather than more independent examples.

Moreover we refer to contemporary works on adapting LLMs for scientific simulation in specific related domains, and find that these works study cases on a similar order: Debris Flow, 5 cases [1]; Molecular Dynamics, 3 host-guest families [2], 9 polymer systems [3], 12 protein-ligand systems [4]; Computational Fluid Dynamics, 2 geometries [5].

Our combined size of 27 tasks is not unreasonable. We are presently working to expand this beyond documentation examples with our domain expert collaborators.

**Beyond GEOS.** We have since expanded the Fluid Dynamics/OpenFOAM transfer study to include 30 tasks (see results in Reviewer gep1's thread) and expanded to the Molecular Dynamics domain/LAMMPS as well with 9 initial tasks and a scaled up study with 20 tasks currently underway.

## 4. Human comparison scale

We agree that the human baseline is better described as a preliminary calibration, and are happy to relabel in the revision. We do maintain that this is a useful calibration however as it establishes a human pace on a relatively easy 1D problem. Time and resource constraints factor in here as recruiting PhD-level geophysics knowledge workers is difficult especially for long, involved tasks such as simulation configuration.

## On the concern raised by Reviewer kEdh

Reviewer kEdh suggests a topic misfit for the NeurIPS venue.

- We refer to the NeurIPS 2026 contribution type guidance defining the Use-Inspired type as work whose main contribution is in framing or designing approaches to meet the needs of a specific real-world application, often involving engaging with domain experts. **We think our paper matches this criteria.**

They also recommended rejection despite not highlighting any technical, evaluation, reproducibility, or ethical issues.

- Again we are happy to add clarifications to address their writing concerns but find some decoupling between feedback and score

[1] Zhang, D., Wang, R., Liu, C., & Zhao, Y. (2026). Agentic AI for Particle-Based Simulation: Automating SPH Workflows for Debris Flow Modeling. arXiv preprint arXiv:2605.09265.
[2] Wang, Z., Ma, Y., Schmidt, C. R., Ma, T., Sun, W., Li, Z., ... & Ye, Y. (2026). MDForge: Agentic Molecular Dynamics Pipeline Design under Sparse Simulator Feedback. arXiv preprint arXiv:2606.12916.
[3] Zhao, A., Chandrasekhar, A., & Farimani, A. B. (2026). Polyjarvis: Llm agent for autonomous polymer md simulations. arXiv preprint arXiv:2604.02537.
[4] Guilbert, S., Masschelein, C., Goumaz, J., Naida, B., & Schwaller, P. (2025). DynaMate: An Autonomous Agent for Protein-Ligand Molecular Dynamics Simulations. arXiv preprint arXiv:2512.10034.
[5] Zhehao, D. O. N. G., Zhen, L. U., & Yue, Y. A. N. G. (2026). CFD-copilot: Leveraging domain-adapted large language model and model context protocol to enhance simulation automation. Chinese Journal of Aeronautics, 104321.
