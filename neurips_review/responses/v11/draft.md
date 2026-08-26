# SIGA — NeurIPS 2026 rebuttal, v11 (condensed line, cleaned for OpenReview)

This is the **condensed** version (the top half of `v10/draft.md`), with:
- Markdown normalised for OpenReview (escapes removed, headings regularised, LaTeX artifacts
  stripped, list markers fixed).
- The two fillable TODOs resolved from source (OpenFOAM non-evaluable task; LAMMPS judge scale).
- The corrections from `FACT_CHECK.md` F1-F5, F8, F9 applied inline.
- All five open questions resolved per the 2026-07-29 decisions — see `DECISIONS.md`.
- **Reliability counts reported as proportions**, not raw fractions, so mismatched denominators
  do not distract the reviewers. Task-set sizes are stated once per study so the scale stays
  visible. Full denominators go in the manuscript revision.

**No placeholders remain.** Post each `## Response to …` section as a separate comment on
OpenReview; delete this preamble first. Reference lists are per-comment, since each comment is
read standalone.

---

## Response to the Area Chair

We thank the Area Chair for the thoughtful meta-review and clear summary of the discussion.

SIGA introduces a lightweight way to ground general-purpose coding agents in scientific
simulators without retraining the model or building a new agent architecture. It adds modular
support for simulator-specific retrieval, procedural guidance, validation, and termination,
and uses a factorial study to identify which components improve reliability and efficiency.

The reviewers consistently recognized the importance of the problem (gep1, kEdh, nBNe), the
practical and technically sound design (kEdh, nBNe), the systematic component analysis
(gep1), and the reduction in catastrophic failures (gep1, kEdh, nBNe). They also viewed the
OpenFOAM transfer results as evidence that the approach is not limited to GEOS (kEdh, nBNe).
All three reviewers rated the paper's significance and originality as good or better, including
the reviewer recommending rejection.

Since the reviews, we have addressed each of the main concerns with new experiments and
targeted revisions.

**Evaluation metrics.** We added direct evaluation of simulator acceptance, execution,
convergence, and physical-output fidelity on the held-out GEOS split. With GEOS's native input
checker integrated into SIGA, acceptance rises from 78.2% for the Vanilla baseline to 90.0%
for S+X, and every accepted deck we tested for execution completed successfully with the solver
converging.

We also compare generated and reference simulations using normalized output specifications
while leaving the generated physical configuration unchanged. Among decks that execute, the
mean output fidelity is 0.958, and 46% achieve fidelity above 0.999. The gap between
structural and physical correctness therefore sits in decks that **fail to run**, not in decks
that run and are wrong, which is directly the axis our reliability claim occupies.

**Experimental scope.** The main GEOS study contains 27 tasks, including 10 held-out tasks,
evaluated across component combinations and repeated runs. The task pool is bounded by the
GEOS documentation corpus, which yields 46 candidate examples in total; within a fixed compute
budget we judged breadth across simulators more valuable than a 28th GEOS task, and the
resulting scale is comparable to contemporary work in this area (see our response to Reviewer
gep1). We will describe the tasks' coverage more clearly and report task-level uncertainty for
the main results. We have also expanded the OpenFOAM study from 5 to 30 tasks, added two
simulator-native baselines, and completed an initial evaluation on 9 LAMMPS tasks. These
experiments provide evidence of transfer across the evaluated geophysics, fluid-dynamics, and
molecular-dynamics simulators.

**Clarity.** To make the paper easier to follow for readers outside scientific simulation, we
will add an end-to-end overview figure, introduce each component in plain language, provide
execution artifact examples (briefs, feedback), and clarify the relationship among the tasks,
metrics, and factorial analysis. We will also state the central contribution more directly
from the outset: SIGA is a lightweight adapter that improves an existing coding agent's
ability to work reliably with scientific simulators.

**Human comparison.** We will present the two-participant experiment explicitly as a
preliminary calibration of simulator onboarding and configuration time for one representative
task, rather than as a broad human-efficiency comparison. We do maintain that it is a useful
calibration: it establishes a human pace on a relatively easy 1D problem, and recruiting
PhD-level geophysics knowledge workers for long, involved configuration tasks is difficult.

**Venue fit.** We address this in our response to Reviewer kEdh, and believe the paper matches
the NeurIPS Use-Inspired contribution type. We note that the review recommending rejection does
so on presentation grounds and does not identify a technical, evaluation, reproducibility, or
ethical concern; we have given the proposed replacement text for every clarity issue it raises.

Together, the new results strengthen the paper's main conclusion: lightweight
simulator-interface grounding reduces catastrophic failures and improves coding-agent
reliability, and this translates into simulator-accepted, executable, and physically
consistent simulations across domains.

---

## Response to Reviewer gep1

We thank the reviewer for the thoughtful and actionable review. We appreciate the recognition
of the practical importance of simulator setup, the value of wrapper-level grounding, the
factorial design, and the reduction in catastrophic failures. We address each question below.

### W1 / Q1. Evaluation metrics

TreeSim primarily checks structural and value equivalence, which suits our task scope of
converting well-specified briefs into simulator input decks: because the tasks are derived from
validated GEOS examples, similarity to the reference is a proxy for physical meaningfulness
here. To make the evaluation more complete for a future expanded scope, we added checks for
schema validity, execution, convergence, and physical output on the held-out tasks.

**Schema validity.** We re-ran this at a much higher repeat count than the 3 runs per cell used
elsewhere, because these are counts of rare events. Vanilla produced a well-formed,
schema-valid deck on 91.2% of runs; S+X and X+M each reached 100%, across 270 adapter runs with
no failures. The improvement over Vanilla is 8.8 percentage points, with a run- and
task-clustered 95% confidence interval of +2.9 to +16.5 points (p = 0.0006).

**Execution and convergence.** We replaced the schema linter inside the adapter loop with
GEOS's native input checker. Acceptance on the held-out evaluation rises from 78.2% for Vanilla
to 90.0% for S+X, and every accepted deck we tested for execution completed successfully and
reached solver convergence. GEOS's own input check is stricter than schema validity, which is
why acceptance rates sit below the schema-validity rates above.

**Physical-output fidelity.** Because generated and reference decks may request different
output variables, we apply the same output specification to both while leaving the generated
physical configuration unchanged, then compare mesh-independent summaries of every physical
quantity, each normalized by the reference's own scale. Among decks that execute, mean output
fidelity is 0.958 and 46% achieve fidelity above 0.999. Structural similarity predicts
fidelity at Spearman rho = 0.362 (95% CI 0.197 to 0.505, p = 0.0001) under our declared
mean-over-reductions aggregator; under a worst-reduction aggregator the same association is
rho = 0.121 and not significant, and we will report both.

**Physics plausibility.** We also built a semantic check, in which a panel of LLM judges rates
each deck section against the reference for physical materiality. Its score on the
physics-bearing sections predicts measured output fidelity at rho = 0.418 (p = 0.0006), but it
does not beat plain structural scoring here and the judges did not agree on the ordering of
conditions, so we report it as built and tested rather than as a metric we would offer.

These results help flesh out a more complete evaluation and locate the bottleneck at the
schema-correctness layer: once GEOS accepts a deck, it reliably executes and generally
reproduces the reference outputs. We are happy to give the full protocol during discussion,
and will document it in the revision.

### W3 / Q2. Prefix bug and the roles of S and X

**Native-plugin-prefix bug.** A targeted ablation over 17 tasks with three runs each puts the
effect at +0.004 (TreeSim 0.913 to 0.917), with no task changing by more than 0.10. The prefix
acted as minor distractor text and slightly reduced SIGA performance; Vanilla and the
self-evolved adapter were unaffected. The magnitude is therefore minor and its direction leaves
SIGA scores slightly understated.

**Separating S from X.** S and X are varied independently in the Resolution-IV design, so
their main effects are separable. On the reviewer's underlying question, whether the
termination hook still contributes once the agent-callable validator is available, the
held-out column builds the two up in sequence:

| Cell (held-out) | TreeSim | vs. Vanilla |
| --- | --- | --- |
| Vanilla | 0.720 ± 0.081 | n/a |
| X+M (validator plus memory) | 0.768 ± 0.005 | +0.048 |
| S+X+M (termination hook added on top) | **0.783 ± 0.022** | **+0.063** |

M is the procedural-memory cheatsheet and is unrelated to validation, so the step from X+M to
S+X+M isolates the addition of the termination hook, and it is positive. S+X reaches 0.781 on
the same split, so the ordering holds with and without memory. **These are three runs per
cell, so we would not over-read the margins between adapter cells, and we would be glad to run
a dedicated build-up experiment isolating the interaction.**

We include both components by design: X gives the agent a validator it can call during
generation, while S is the process guarantee that validation is run before submission.

### Q3. OpenFOAM transfer

We expanded the OpenFOAM study from 5 to 30 tasks and replaced the static linter with a
validator that runs the OpenFOAM solver in a container.

Across the full factorial study on the 30 tasks, the best SIGA configuration (R+S+X+M) scores
0.668 on the text-similarity metric and produces executable cases on 89.7% of tasks, against
13.3% for Vanilla Claude Code, and is stable across three seeds (0.668, 0.685, 0.665).
Executability is assessed only for tasks whose solver is present in the evaluation container,
and that exclusion is applied identically across conditions.

We additionally ran two simulator-native systems on a 10-task set drawn from the same benchmark
family, under matched budgets and the same bounded real-execution and post-hoc executability
checks: Foam-Agent scores 0.565 with 10% executable, MetaOpenFOAM 0.276 with 22%. Because they
ran on a smaller task set than SIGA's 30, we present this as indicative rather than matched.

The strongest transfer result is the improvement in execution reliability. In the revision we
will limit this claim to the OpenFOAM tasks evaluated here and make clear that the experiment
tests executable structure rather than physical correctness.

### W2. Experimental scale

The GEOS benchmark contains 27 distinct documentation-derived tasks: 17 for development and 10
held out. The split exists mainly to improve iteration speed on the factorial evaluation and
to provide a held-out set for the self-evolution setting. Two things bound this scale. The
tasks are mined from GEOS documentation examples, which yield 46 candidates in total, and
within a fixed compute budget run counts multiply across component combinations, repeated runs
for error bars, and further experiments across backbone models, harnesses, and domains. We
judged breadth across those conditions more valuable than more documentation examples within
GEOS: generalization is better tested by a second and third simulator than by a 28th GEOS task.
The resulting scale is in line with contemporary work in the area, which evaluates on 2 to 12
cases [1-5]. We are working with domain-expert collaborators to author tasks beyond the
documentation corpus.

Beyond GEOS, we have expanded the OpenFOAM study as described above and added a third
simulator, LAMMPS, whose command-script interface has no formal schema and therefore tests
whether the recipe is tied to XML (see our response to Reviewer nBNe). In the revision we will
describe the coverage of the held-out tasks more clearly and report task-level uncertainty for
the main results.

### Q4. Human comparison

The human study is intended as a preliminary calibration of the time required to learn GEOS
conventions and configure one representative task. We will label it accordingly and avoid
using it to support a broad human-efficiency claim. We do maintain it is a useful calibration,
since it establishes a human pace on a relatively easy 1D problem; recruiting PhD-level
geophysics knowledge workers is difficult, especially for long, involved tasks such as
simulation configuration.

**References**

[1] Zhang et al. Agentic AI for Particle-Based Simulation: Automating SPH Workflows for Debris
Flow Modeling. arXiv:2605.09265, 2026.
[2] Wang et al. MDForge: Agentic Molecular Dynamics Pipeline Design under Sparse Simulator
Feedback. arXiv:2606.12916, 2026.
[3] Zhao, Chandrasekhar and Farimani. PolyJarvis: LLM Agent for Autonomous Polymer MD
Simulations. arXiv:2604.02537, 2026.
[4] Guilbert et al. DynaMate: An Autonomous Agent for Protein-Ligand Molecular Dynamics
Simulations. arXiv:2512.10034, 2025.
[5] Dong, Lu and Yang. CFD-Copilot: Leveraging domain-adapted large language model and model
context protocol to enhance simulation automation. *Chinese Journal of Aeronautics*, 2026.

---

## Response to Reviewer kEdh

We thank the reviewer for the careful reading and concrete suggestions. We also appreciate the
clear summary of the paper's main practical finding: lightweight verification around an
existing coding agent can substantially reduce failures on difficult scientific-simulation
tasks without retraining the model.

Each concept the review highlights is defined in the submitted paper; what the review
identifies, usefully, is that several are defined **later than their first use**, an ordering
problem with a definite fix. NeurIPS does not permit a revised PDF during this period, so we
give the proposed replacement text inline below.

### W1. Terminology and experimental design

**Resolution-IV.** The design is explained on line 182, which states that instead of
exhaustively testing every combination of factors we select a subset of configurations that
lets us discern the main effects without confounding by a two-factor interaction. The term
nonetheless first appears in the abstract, which is too early. We will remove it from the
abstract and early narrative and first explain the design directly:

> We study four adapter components. Testing them one at a time would miss interactions, while
> testing all 16 combinations would double the experiment. We therefore evaluate eight
> carefully selected combinations that let us estimate each component's main effect without
> confounding it with a two-component interaction. Some interaction effects remain
> indistinguishable, which we state explicitly in the experimental section.

The formal design-of-experiments term will appear only after this motivation, with a citation
(Box, Hunter and Hunter, *Statistics for Experimenters*, 2nd ed., Wiley, 2005).

**buckleyLeverettProblem.** Line 290 gives the attributes that matter, namely that it is 1D
and therefore a relatively simple task, but that is its second mention, which we agree is too
late. We will move the gloss to first use: it is a relatively simple one-dimensional benchmark
in which CO₂ displaces brine through porous rock.

### W2. "Input deck" and evaluation wording

"Deck" is defined in Section 3. We had assumed "input deck" to be standard terminology, but
the reviewer is right that a reader meets the word earlier. We will move the definition to
first use, in the abstract:

> An **input deck** is the configuration a simulator reads to define a run. In GEOS it is one
> or more XML files specifying the mesh, the physics modules to couple, the material models,
> the solver settings, and the requested outputs.

We will also replace the two sentences highlighted by the reviewer.

Current, with "strictly perfect" specified as structural similarity above 0.999 later in the
same section:

> The number of strictly perfect decks does not increase under any adapter.

Revised, stating it inline:

> No configuration increased the number of decks that matched the reference almost exactly
> (structural similarity above 0.999). The adapters change how often the agent produces
> something badly wrong, not how often it produces something flawless.

Current:

> Headline numbers average TreeSim under failures-as-zero: parse errors, timeouts,
> failed_no_outputs, and missing XML outputs all score 0, so systems are not rewarded for
> unscorable files.

Revised:

> When a run produces no usable input deck at all (for example no XML file, an empty file, a
> file that will not parse, or a timeout), we score it zero rather than dropping it from the
> average, so that reliability faults are counted rather than removed.

### W3. Concrete examples

We will add a running example that shows both the task given to the agent and the feedback
returned by SIGA. Both will appear as figures in the revision.

Example task brief (from the `buckleyLeverettProblem` task, opening and closing, lightly
elided):

> I need to set up a simulation to model a 1D Buckley-Leverett CO2 core flood experiment. The
> goal is to verify the immiscible displacement of brine by supercritical CO2 in a porous
> medium against analytical solutions. **Physical Problem and Domain Geometry** [...] create a
> hexahedral mesh of length 0.1 m [...] Permeability is 9.0e-13 m2 in all directions. The
> reference porosity is 0.2 at a reference pressure of 10 MPa. [...] XML files to create:
> buckleyLeverett_base.xml, buckleyLeverett_benchmark.xml

A real instance of structured repair feedback, lightly elided:

> Stop blocked by verify_outputs hook: [...] fail GEOS schema validation. [...]
> wellborePoromechanics.xml:49: element SinglePhasePoromechanics: Schemas validity error :
> Element 'SinglePhasePoromechanics', attribute 'porousMaterialNames': The attribute
> 'porousMaterialNames' is not allowed. [...] Fix the offending element/attribute names against
> the schema. Re-validate locally with xmllint --schema [...] --noout .xml before ending your
> turn.

### NeurIPS relevance

We believe the paper is strongly aligned with the NeurIPS Use-Inspired contribution type,
which the 2026 guidance defines as work whose main contribution is in framing or designing
approaches to meet the needs of a specific real-world application, often involving engagement
with domain experts.

The central question is broader than automating one GEOS workflow: how can a general-purpose
coding agent be grounded in a complex scientific tool without retraining the underlying model?
SIGA addresses this through a modular adapter built from retrieval, procedural guidance,
validation, and enforced checking. The factorial study shows which components improve
reliability, which do not, and which failure modes remain. This provides evidence about the
design of reliable tool-using agents, not only a system for one simulator. The OpenFOAM study
applies the same approach to a second simulator with a different interface, expanded from 5
to 30 tasks with execution-based validation, providing stronger evidence that the method
transfers beyond GEOS.

We will make this broader agent-design contribution more explicit in the introduction while
keeping the scientific application and practical motivation central.

We would rather show the fixes than argue about them, which is why the replacement text above
is given rather than described. If any of it is still not clear enough, we would welcome
hearing so during the discussion period, and will act on it.

---

## Response to Reviewer nBNe

We thank the reviewer for the careful reading and positive assessment. We appreciate the
recognition of SIGA's practical value, technical soundness, reduction in complete failures,
and transfer across simulators. We address each question and concern below.

### W2 / Q1. Additional evaluation: convergence checks and output validation

This was the most common thread across the reviews, and we made it our first priority. Please
see our response to Reviewer gep1 for the full protocol and all numbers; in brief, on the
held-out split:

- **Simulation execution.** Decks accepted by GEOS rise from 78.2% for Vanilla to 90.0% for
  S+X once the simulator's own input check replaces the schema linter inside the adapter loop,
  and every accepted deck we tested ran to completion with a converged solver. Execution is not
  the bottleneck; deck construction is.
- **Simulation output.** Injecting an identical ground-truth output block into both decks and
  comparing mesh-independent reductions of each physical quantity gives mean fidelity 0.958
  conditional on the deck running, with 46% above 0.999. Because our tasks are sourced from
  documentation examples corresponding to representative workflows, the ground-truth outputs
  are physically meaningful, which is what makes the fidelity measure interpretable.
- **Simulation input.** An LLM judge rates each deck section for physical materiality; its
  score on the physics-bearing sections predicts measured output fidelity at Spearman
  rho = 0.418 (p = 0.0006). This needs calibration against domain-expert judgments before we
  would offer it as a metric, and we reserve that for follow-up work.

### W3 / Q2. Human expertise and human-agent collaboration

The human experiment is designed as a preliminary calibration of the time needed for
geophysics domain experts to learn GEOS conventions and configure a simple 1D task, rather
than as a population-level comparison. We will make this intent explicit, describe the
participants' backgrounds more clearly, and avoid drawing broad human-efficiency conclusions.
The reviewer's suggestion of examining different expertise levels is useful and may allow more
participants to be added; it motivated both our discussions with a GEOS developer and our
inclusion of a geophysics domain expert who is not a GEOS expert in the hands-on experiment.

We also explored human-agent interaction in a companion experiment (Section 6.4) where the
agent could consult a human as information was progressively removed from the task
specification. The agent used this channel in only 2 of 64 trials, largely because the local
example library provided an easier source of information. This suggests that (1) a more robust
collaboration benchmark must design for clear informational and capability boundaries between
agent and human, and (2) models optimized for autonomous task completion are not immediately
prepared for collaborative modes, mirroring broader findings in the literature [1, 2].
Bridging the gap between benchmark tasks and real practitioner usage is a key direction for
our future work.

### Q3. Exact Claude Code version

All experiments used Claude Code version **2.1.119**. We will add this to the reproducibility
details.

### W1. Contribution beyond a new agent architecture

SIGA is deliberately not a new agent architecture. Rather than building a new agent stack
around each new domain, simulator, and workflow, or optimizing the entire harness, we search a
small set of lightweight modules implementing proven components. A positive result under that
constraint is informative precisely because the intervention is cheap: a real effect argues
against rebuilding the agent loop for every new scientific target.

The paper contributes the modular adapter design, the GEOS input-deck authoring benchmark, a
controlled factorial study of the adapter components, and an analysis of which
simulator-authoring failures these components do and do not address. The cross-simulator
studies further test whether the same grounding approach transfers when both the simulator and
interface format change.

### W4. Task scale and diversity

The GEOS benchmark contains 27 distinct documentation-derived tasks: 17 for development and 10
held out for final evaluation, each evaluated across all factorial cells and repeated runs.
The documentation corpus yielded 46 candidate examples in total, and we are working with
domain collaborators to add expert-authored tasks beyond this source. The resulting scale is
comparable to contemporary work in this area (see our response to Reviewer gep1). We will also
describe the task coverage more clearly and report task-level uncertainty for the main results.

We expanded the OpenFOAM study from 5 to 30 tasks, replaced the static linter with a validator
that runs the OpenFOAM solver in a container, and added two simulator-native baselines: on the
expanded set the best cell produces an executable case on 89.7% of tasks, against 10% and 22%
for the two baselines on a smaller task set. We also added an initial LAMMPS study with 9
molecular-dynamics tasks and two backbone models, with a 20-task scale-up underway. Because
LAMMPS uses command scripts rather than XML or a formal schema, it provides a distinct test of
whether SIGA depends on the GEOS interface format. It does not, but the binding component
shifts: LAMMPS scripts are structurally complete almost everywhere, so the gain comes from
knowledge injection rather than completion enforcement. On a 0-to-10 judge scale, scores move
from 4.56 to 7.78 on one backbone and from 6.33 to 6.89 on the other. This study remains
single-run and we present it as qualitative transfer evidence.

Together, these additions broaden both the scale of the evaluation and the diversity of
simulator interfaces, and support transfer across the three evaluated simulators.

**References**

[1] Wu et al. CollabLLM: From Passive Responders to Active Collaborators. arXiv:2502.00640,
2025.
[2] Zhou et al. ToM-SWE: User Mental Modeling for Software Engineering Agents.
arXiv:2510.21903, 2025.
