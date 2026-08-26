<!-- v2 DRAFT 2026-07-27. Reviewer kEdh: rating 2 (reject), confidence 4. Sole complaint is writing quality.
     Strategy: SHOW the replacement text, do not promise it. Written to be read by the AC too.
     ANONYMITY: all replacement prose is written fresh. Do NOT paste arXiv sentences verbatim.
     Style: patterned on ladir_rebuttal_iclr.md. No em dashes.
     Target ~6,500 prose chars. HARD CAP 10,000. -->

## Response to Reviewer kEdh

We accept this criticism. The reviewer is right that a practitioner should be able to read this paper and apply it, and in the submitted version several central terms arrive before they are explained. Rather than promise a rewrite, we give the actual replacement text below for each item raised, and we describe the broader reframing we have already carried out.

### Response to Weaknesses

> W1: The driving example is "a Resolution-IV 2^(4-1) factorial". Another application appears to be "buckleyLeverettProblem". A brief explanation of what these are is needed, else none of the narrative that follows will be understood.

**Response to W1, part (a), Resolution-IV:** The term currently appears first in the abstract with no scaffolding, and the design is explained only in Section 3.2. We also never say what resolution IV means, only what follows from it. Replacement, to appear before the term is used:

> We want to know what each of the four components contributes. Testing them one at a time is cheap but cannot detect a component that only helps in combination. Testing all sixteen on/off combinations answers that, but doubles the experiment. We therefore run a carefully chosen **half** of the sixteen, eight combinations, selected so that each component's individual effect stays separable from the others. The price is that certain *pairwise* interactions become indistinguishable from each other, and we say explicitly which. In the design-of-experiments literature this choice is called a **Resolution-IV fractional factorial** (Box, Hunter and Hunter, *Statistics for Experimenters*, 2nd ed., Wiley 2005), and the name records exactly which effects remain separable.

We will also add the citation above, which the submitted paper omitted, so a reader who wants the underlying theory has somewhere to go. And we will state the aliasing explicitly rather than leave a reader to derive it, since it determines what the experiment can answer:

> Each single-component effect is separable from every pairwise interaction. The six pairwise interactions collapse into three indistinguishable pairs: retrieval x stop-hook with validator x memory, retrieval x validator with stop-hook x memory, and retrieval x memory with stop-hook x validator. The last of these is why we cannot read the stop-hook/validator interaction off this design, a limitation reviewer gep1 also raises and which we address separately with a one-component-at-a-time ablation.

We will also give the concrete cost, which we omitted entirely: eight combinations at three runs is 24 runs against 48 for the full sixteen, so **half the compute**, roughly forty hours saved.

**Response to W1, part (b), Buckley-Leverett:** It appears first as a bare identifier and is glossed only 70 lines later. Replacement, at first use:

> `buckleyLeverettProblem` asks the agent to configure a one-dimensional simulation of CO2 displacing brine through porous rock. Because the physics reduces to a single conservation law with a known analytical solution, the deck needs only a handful of GEOS blocks, which is why we treat it as the easy end of our benchmark and use it as our running example.

> W2: Wording such as "The number of strictly perfect decks does not increase under any adapter" must be clarified. Section 3 does explain what a "deck" is, but this comes too late. Sentences such as "Headline numbers average TreeSim under failures-as-zero..." will not make sense to most readers.

**Response to W2:** The reviewer is precisely right, and on "deck" it is worse than the review suggests: the word appears **eleven times** across the abstract, introduction and related work before Section 3 defines it. We have already moved the definition to first use in the abstract. Replacement:

> An **input deck** is the configuration a simulator reads to define a run. For GEOS it is one or more XML files specifying the mesh, the physics modules to couple, the material models, the solver settings and the requested outputs. Writing one correctly is the task we study, and it is closer to programming against an unfamiliar API than to filling in a configuration file.

For the two sentences quoted:

**"The number of strictly perfect decks does not increase under any adapter."** The problem is that "strictly perfect" is operationalised 130 lines later. Replacement:

> No configuration increased the number of decks that matched the reference almost exactly (structural similarity above 0.999). The adapters change how often the agent produces something badly wrong, not how often it produces something flawless.

**The failures-as-zero sentence.** It contains three undefined terms, one of which (`failed_no_outputs`) is a raw internal status string from our own runner that appears nowhere else in the paper. Replacement:

> When a run produces no usable deck at all, meaning no XML file, an empty file, a file that will not parse, or a timeout, we score it **zero** rather than dropping it from the average. This matters: a system that fails outright on a hard task should not be rewarded with a missing entry instead of a bad one.

> W3: Provide simple examples of concepts like "briefs", "structured repair feedback".

**Response to W3:** Agreed, and both will appear as a figure in the main text. Here are the two examples.

**A brief** is the natural-language task specification the agent receives. From the Buckley-Leverett task, opening and closing:

> I need to set up a simulation to model a 1D Buckley-Leverett CO2 core flood experiment. The goal is to verify the immiscible displacement of brine by supercritical CO2 in a porous medium against analytical solutions.
> **Physical Problem and Domain Geometry** [...] create a hexahedral mesh of length 0.1 m [...]
> - Permeability is 9.0e-13 m² in all directions.
> - The reference porosity is 0.2 at a reference pressure of 10 MPa. [...]
> XML files to create: buckleyLeverett_base.xml, buckleyLeverett_benchmark.xml

The point we should have made explicitly: **the brief is written entirely in domain language and never names a single GEOS XML element.** That is what makes this a translation problem rather than a form-filling one, and it is why interface grounding can help at all. Briefs run 2.2k to 6.7k characters (median about 4.2k); this one is 3.7k.

**Structured repair feedback** is the stop hook's output when it refuses to let the agent finish. A real instance, lightly elided:

> Stop blocked by verify_outputs hook: [...] fail GEOS schema validation. [...]
> wellborePoromechanics.xml:49: element SinglePhasePoromechanics: Schemas validity error : Element 'SinglePhasePoromechanics', attribute 'porousMaterialNames': The attribute 'porousMaterialNames' is not allowed.
> [...] Fix the offending element/attribute names against the schema. Re-validate locally with
>   xmllint --schema [...] --noout <file>.xml
> before ending your turn.

Two things we should have shown rather than described. First, "structured" means the feedback names the file, the line, the element, the attribute, and how to re-check, not "your deck is invalid." Second, in this run it worked: the agent was blocked once for a parse error, fixed it, was blocked again for this schema error, fixed that, and finished with a clean deck, the whole exchange taking about 45 seconds.

The example also illustrates why the task is hard. `porousMaterialNames` is a GEOS attribute renamed in a later version. The model learned it from older examples, which is exactly the failure mode our Section 3 describes and the reason schema grounding matters.

### Broader clarity revision

Beyond the six items above, we have rewritten the paper for a general audience rather than edited it. The abstract is de-jargoned and now opens on the practical problem, defining "input deck" in the first sentence. TreeSim, which the submitted version never formally defined, now has a main-text definition and a full appendix, which was also the paper's largest reproducibility gap. The method section is restructured into three single-pass subsections around a clean three-interface abstraction (context, tools, termination) instead of a formalism-then-repeat layout. We state five explicit research questions and place a short boxed answer after each results subsection, so a reader can follow the argument without reconstructing it. Related work now positions the contribution against a named subfield rather than listing papers.

We commit to all of this for the camera-ready, together with expanding every acronym at first use and removing the internal status strings that leaked into the text.

### On venue

We understand this is the committee's call and will not argue it. We would only note that the paper's intended contribution is a component-wise causal analysis of what interface grounding does and does not buy a general coding agent, including several negative results, aimed at readers who build agents rather than at a simulation audience. We are content to let the committee judge the fit.

We think the reviewer identified the most fixable weakness in the paper, and we would rather show the fix than argue about it. If any replacement above is still not clear enough, we would genuinely welcome being told so during the discussion period.
