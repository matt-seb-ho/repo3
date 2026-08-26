<!-- v7 DRAFT 2026-07-28. Reviewer kEdh (Reviewer 2): rating 2 (reject), confidence 4.
     This is the ONE thread that keeps full depth: the AC comment now defers every clarification
     item here rather than itemising them, so the replacement text has to live somewhere.
     Tightened in the hand_v6 style and the rating/venue framing aligned with the hand version
     ("decoupling between feedback and score").
     Sole complaint is writing clarity. POSTURE (researcher-confirmed): do NOT concede the writing
     is poor and do NOT frame clarity as a weakness. Show where the paper already explains each item,
     offer to expand. Reframe against the NeurIPS reject criteria. Push back firmly on venue using
     the Use-Inspired contribution-type definition, quoted by name, NO LINK.
     Replacement prose written fresh. Never mention the arXiv rewrite.
     Style: no em dashes, no links, VERIFIED numbers only.
     Prose length ~8,000 chars. HARD CAP 10,000. -->

## Response to Reviewer kEdh

We thank the reviewer for a close and specific reading, and for stating the practical takeaway accurately: adding verification checkpoints to a coding agent substantially reduces failures on difficult scientific tasks without retraining the model.

Each concept the review names is defined in the submitted paper, and we locate each below. What the review identifies, usefully, is that several are defined later than their first use. That is an ordering problem with a definite fix. NeurIPS does not allow a revised PDF during this period, so rather than promise a rewrite we give the actual replacement text, and we are happy to add all of it.

### On the grounds for the rating

We raise this respectfully, and only because the review is clear about its basis. The NeurIPS rating-2 description is "a paper with technical flaws, weak evaluation, inadequate reproducibility and incompletely addressed ethical considerations." This review highlights none of these: no technical error, no disputed result, no reproducibility or novelty concern, no ethical concern, and a strengths section that credits the contribution and scores significance and originality as good. We are glad to add clarifications to address the writing concerns, but find some decoupling between the feedback given and the score assigned.

### Response to W1: Resolution-IV and buckleyLeverettProblem

**Resolution-IV.** The design is explained at line 182, which states that instead of the full design we run a Resolution-IV fraction giving eight cells whose main effects are not confounded with two-factor interactions. That is what the term means, and it is the property the rest of the analysis relies on. The reviewer is right that the term first appears in the abstract, ahead of that explanation, so we will motivate it in plain prose at first use:

> We want to know what each of the four components contributes. Testing them one at a time is cheap but cannot detect a component that only helps in combination. Testing all sixteen on/off combinations answers that, but doubles the experiment. We therefore run a carefully chosen half of the sixteen, eight combinations, selected so that each component's individual effect stays separable from the others. The price is that certain pairwise interactions become indistinguishable from each other, and we say explicitly which. In the design-of-experiments literature this choice is called a Resolution-IV fractional factorial (Box, Hunter and Hunter, Statistics for Experimenters, 2nd ed., Wiley 2005), and the name records exactly which effects remain separable.

We will add that citation, which the submitted version omits, and spell out the aliasing rather than leaving a reader to derive it: the six pairwise interactions collapse into three indistinguishable pairs, which is why the stop-hook and validator interaction cannot be read off this design, a point Reviewer gep1 also raises and which we answer separately with a one-component-at-a-time ablation. We will also give the concrete cost, which we did not state: eight combinations at three runs is 24 runs against 48 for the full sixteen, exactly half the compute.

**buckleyLeverettProblem.** This is the identifier of one benchmark task rather than a concept the argument depends on, and line 290 describes it as 1D immiscible CO2 and brine displacement, which is the only property the surrounding discussion uses. The identifier does appear earlier than that description, so we will move a one-sentence gloss to first use:

> `buckleyLeverettProblem` asks the agent to configure a one-dimensional simulation of CO2 displacing brine through porous rock. Because the physics reduces to a single conservation law with a known analytical solution, the deck needs only a handful of GEOS blocks, which is why we treat it as the easy end of our benchmark and use it as our running example.

### Response to W2: "deck", and the two sentences quoted

**"Deck"** is defined in Section 3, and the reviewer is right that a reader meets it earlier. We will move the definition to first use, in the abstract:

> An **input deck** is the configuration a simulator reads to define a run. For GEOS it is one or more XML files specifying the mesh, the physics modules to couple, the material models, the solver settings and the requested outputs. Writing one correctly is the task we study, and it is closer to programming against an unfamiliar API than to filling in a configuration file.

**"The number of strictly perfect decks does not increase under any adapter."** The paper operationalises "strictly perfect" as structural similarity above 0.999, later in the same section. We will say it inline instead:

> No configuration increased the number of decks that matched the reference almost exactly (structural similarity above 0.999). The adapters change how often the agent produces something badly wrong, not how often it produces something flawless.

**The failures-as-zero sentence.** Here we would gently disagree on the substance: the sentence says that our reported numbers count a failure to produce scorable output as a score of zero rather than dropping it from the average, so a system is not rewarded for emitting nothing. We do accept that it carries an internal status string from our own runner (`failed_no_outputs`) that appears nowhere else in the paper and should not be in the text. Replacement:

> When a run produces no usable deck at all, meaning no XML file, an empty file, a file that will not parse, or a timeout, we score it zero rather than dropping it from the average. This matters: a system that fails outright on a hard task should not be rewarded with a missing entry instead of a bad one.

### Response to W3: examples of "briefs" and "structured repair feedback"

Agreed, and both will appear as a figure in the main text.

**A brief** is the natural-language task specification the agent receives. From the Buckley-Leverett task, opening and closing:

> I need to set up a simulation to model a 1D Buckley-Leverett CO2 core flood experiment. The goal is to verify the immiscible displacement of brine by supercritical CO2 in a porous medium against analytical solutions.
> **Physical Problem and Domain Geometry** [...] create a hexahedral mesh of length 0.1 m [...]
> - Permeability is 9.0e-13 m2 in all directions.
> - The reference porosity is 0.2 at a reference pressure of 10 MPa. [...]
> XML files to create: buckleyLeverett_base.xml, buckleyLeverett_benchmark.xml

The point worth making explicit alongside it: the brief is written entirely in domain language and never names a single GEOS XML element. That is what makes this a translation problem rather than form-filling, and why interface grounding helps at all. Briefs run 2.2k to 6.7k characters, median about 4.2k.

**Structured repair feedback** is the stop hook's output when it refuses to let the agent finish. A real instance, lightly elided:

> Stop blocked by verify_outputs hook: [...] fail GEOS schema validation. [...]
> wellborePoromechanics.xml:49: element SinglePhasePoromechanics: Schemas validity error : Element 'SinglePhasePoromechanics', attribute 'porousMaterialNames': The attribute 'porousMaterialNames' is not allowed.
> [...] Fix the offending element/attribute names against the schema. Re-validate locally with
>   xmllint --schema [...] --noout <file>.xml
> before ending your turn.

Two things this shows better than description. "Structured" means the feedback names the file, the line, the element, the attribute and how to re-check, rather than saying the deck is invalid. And in this run it worked: the agent was blocked once for a parse error, fixed it, was blocked again for this schema error, fixed that, and finished with a clean deck in about 45 seconds. The example also shows why the task is hard: `porousMaterialNames` is a GEOS attribute renamed in a later version, learned by the model from older examples, which is exactly the failure mode Section 3 describes and the reason schema grounding matters.

### On venue

We refer to the NeurIPS 2026 contribution type guidance, which defines the Use-Inspired type as work whose "main contribution is in framing or designing approaches to meet the needs of a specific real-world application," adding that this "often involves, e.g., engaging with domain experts." We think our paper matches this criteria, and all three reviewers, including this one, independently classified the contribution as Use-Inspired.

The contribution is also aimed at the agent-design audience rather than a simulation audience: a component-wise analysis of what wrapper-level grounding buys a general-purpose coding agent, including several negative results (retrieval can hurt; memory exposed as a retrievable tool goes unused; a human-consultation channel is bypassed when an example library is available). A simulation venue would be the right home for a paper about GEOS; this is a paper about grounding general agents in unfamiliar tool interfaces, with a simulator as the testbed.

### Closing

We would rather show the fixes than argue about them, which is why the replacement text is above rather than described. If any of it is still not clear enough, we would welcome being told so during the discussion period and will act on it. Given that the review raises no concern about the method, the results or their reproducibility, we hope the reviewer will reconsider the rating.
