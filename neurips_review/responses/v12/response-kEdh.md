## Response to Reviewer kEdh

We thank the reviewer for the careful reading and concrete suggestions. We also appreciate the clear summary of the paper's main practical finding: lightweight verification around an existing coding agent can substantially reduce failures on difficult scientific-simulation tasks without retraining the model.

Each concept the review highlights is defined in the submitted paper; what the review identifies, usefully, is that several are defined **later than their first use (e.g. in Abstract)**, an ordering problem with a definite fix. NeurIPS does not permit a revised PDF during this period, so we give the proposed replacement text inline below.

### W1. Terminology and experimental design

**Resolution-IV.** The design is explained on **line 182**, which states that instead of exhaustively testing every combination of factors we select a subset of configurations that lets us discern the main effects without confounding by a two-factor interaction. The term nonetheless first appears in the abstract, which is too early. We will remove it from the abstract and early narrative and first explain the design directly:

> We study four adapter components. Testing them one at a time would miss interactions, while testing all 16 combinations would double the experiment. We therefore evaluate eight carefully selected combinations that let us estimate each component's main effect without confounding it with a two-component interaction. Some interaction effects remain indistinguishable, which we state explicitly in the experimental section.

The formal design-of-experiments term will appear only after this motivation, with a citation (Box, Hunter and Hunter, *Statistics for Experimenters*, 2nd ed., Wiley, 2005).

**buckleyLeverettProblem.** **Line 290** gives the attributes that matter, namely that it is 1D and therefore a relatively simple task, but that is its second mention, which we agree is too late. We will move the gloss to first use: it is a relatively simple one-dimensional benchmark in which CO₂ displaces brine through porous rock.

### W2. "Input deck" and evaluation wording

"Deck" is defined in Section 3. We had assumed "input deck" to be standard terminology, but the reviewer is right that a reader meets the word earlier. We will move the definition to first use, in the abstract:

> An **input deck** is the configuration a simulator reads to define a run. In GEOS it is one or more XML files specifying the mesh, the physics modules to couple, the material models, the solver settings, and the requested outputs.

We will also replace the two sentences highlighted by the reviewer.

Current, with "strictly perfect" specified as structural similarity above 0.999 later in the same section:

> The number of strictly perfect decks does not increase under any adapter.

Revised, stating it inline:

> No configuration increased the number of decks that matched the reference almost exactly (structural similarity above 0.999). The adapters change how often the agent produces something badly wrong, not how often it produces something flawless.

Current:

> Headline numbers average TreeSim under failures-as-zero: parse errors, timeouts, failed_no_outputs, and missing XML outputs all score 0, so systems are not rewarded for unscorable files.

Revised:

> When a run produces no usable input deck at all (for example no XML file, an empty file, a file that will not parse, or a timeout), we score it zero rather than dropping it from the average, so that reliability faults are counted rather than removed.

### W3. Concrete examples

We will add a running example that shows both the task given to the agent and the feedback returned by SIGA. Both will appear as figures in the revision.

Example task brief (from the `buckleyLeverettProblem` task, opening and closing, lightly elided):

> I need to set up a simulation to model a 1D Buckley-Leverett CO2 core flood experiment. The goal is to verify the immiscible displacement of brine by supercritical CO2 in a porous medium against analytical solutions. **Physical Problem and Domain Geometry** [...] create a hexahedral mesh of length 0.1 m [...] Permeability is 9.0e-13 m2 in all directions. The reference porosity is 0.2 at a reference pressure of 10 MPa. [...] XML files to create: buckleyLeverett_base.xml, buckleyLeverett_benchmark.xml

A real instance of structured repair feedback, lightly elided:

> Stop blocked by verify_outputs hook: [...] fail GEOS schema validation. [...] wellborePoromechanics.xml:49: element SinglePhasePoromechanics: Schemas validity error : Element 'SinglePhasePoromechanics', attribute 'porousMaterialNames': The attribute 'porousMaterialNames' is not allowed. [...] Fix the offending element/attribute names against the schema. Re-validate locally with xmllint --schema [...] --noout .xml before ending your turn.

### NeurIPS relevance

We believe the paper is strongly aligned with the NeurIPS Use-Inspired contribution type. Its central question extends beyond one GEOS workflow: how can a general-purpose coding agent be grounded in a complex scientific tool without retraining?

SIGA addresses this through modular retrieval, procedural guidance, validation, and enforced checking. The factorial study shows which components improve reliability and which failure modes remain, offering broader evidence for the design of reliable tool-using agents. The expanded 30-task OpenFOAM study, now with execution-based validation, further shows that the approach transfers beyond GEOS.

We will make this broader agent-design contribution more explicit in the introduction.

We would rather show the fixes than argue about them, which is why the replacement text above is given rather than described. If any of it is still not clear enough, we would welcome hearing so during the discussion period, and will act on it.
