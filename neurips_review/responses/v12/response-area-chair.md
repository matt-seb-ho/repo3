## Response to the Area Chair

We thank the Area Chair for the thoughtful meta-review and clear summary of the discussion.

SIGA introduces a lightweight way to ground general-purpose coding agents in scientific simulators without retraining the model or building a new agent architecture. It adds modular support for simulator-specific retrieval, procedural guidance, validation, and termination, and uses a factorial study to identify which components improve reliability and efficiency.

The reviewers consistently recognized the importance of the problem (gep1, kEdh, nBNe), the practical and technically sound design (kEdh, nBNe), the systematic component analysis (gep1), and the reduction in catastrophic failures (gep1, kEdh, nBNe). They also viewed the OpenFOAM transfer results as evidence that the approach is not limited to GEOS (kEdh, nBNe). All three reviewers rated the paper's significance and originality as good or better, including the reviewer recommending rejection.

Since the reviews, we have addressed each of the main concerns with new experiments and targeted revisions.

**Evaluation metrics.** We added direct evaluation of simulator acceptance, execution, convergence, and physical-output fidelity on the held-out GEOS split. With GEOS's native input checker integrated into SIGA, acceptance rises from 78.2% for the Vanilla baseline to 90.0% for S+X, and every accepted deck we tested for execution completed successfully with the solver converging.

We also compare generated and reference simulations using normalized output specifications while leaving the generated physical configuration unchanged. Among decks that execute, the mean output fidelity is 0.958, and 46% achieve fidelity above 0.999. The gap between structural and physical correctness therefore sits in decks that **fail to run**, not in decks that run and are wrong, which is directly the axis our reliability claim occupies.

**Experimental scope.** The main GEOS study contains 27 tasks, including 10 held-out tasks, evaluated across component combinations and repeated runs. The task pool is bounded by (a) the GEOS documentation corpus, which yields 46 candidate examples in total; (b) a fixed compute budget allocated across various experiment settings/runs, and the resulting scale is comparable to contemporary work in this area (see our response to gep1). We have also expanded the OpenFOAM study from 5 to 30 tasks, added two simulator-native baselines, and completed an initial evaluation on 9 LAMMPS tasks. These experiments provide evidence of transfer across domains + simulators.

**Clarity.** To make the paper easier to follow for readers outside scientific simulation, we will add an end-to-end overview figure, introduce each component in plain language, provide execution artifact examples (briefs, feedback), and clarify the relationship among the tasks, metrics, and factorial analysis. We will also state the central contribution more directly from the outset: SIGA is a lightweight adapter that improves an existing coding agent's ability to work reliably with scientific simulators.

**Human comparison.** We will present the two-participant experiment explicitly as a preliminary calibration of simulator onboarding and configuration time for one representative task, rather than as a broad human-efficiency comparison. We do maintain that it is a useful calibration: it establishes a human pace on a relatively easy 1D problem, and recruiting PhD-level geophysics knowledge workers for long, involved configuration tasks is difficult.

**Venue fit.** We address this in our response to Reviewer kEdh, and believe the paper matches the NeurIPS Use-Inspired contribution type. **We note that the review recommending rejection does so on presentation grounds and does not identify a technical, evaluation, reproducibility, or ethical concern**; we have given the proposed replacement text for every clarity issue it raises.

Together, the new results strengthen the paper's main conclusion: lightweight simulator-interface grounding reduces catastrophic failures and improves coding-agent reliability, and this translates into simulator-accepted, executable, and physically consistent simulations across domains.
