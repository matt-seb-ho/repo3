<!-- DRAFT v0.1 — 2026-07-26. Budget ~6,800, HARD CAP 10,000.
     Reviewer kEdh: rating 2 (reject), confidence 4. Sole complaint is writing quality.
     Realistically will not move; this text is written to be read by the AC, who independently
     endorsed the complaint. Strategy: SHOW the replacement text, do not promise it.
     All line references verified by Thread F against writing/neurips/neurips_2026.tex.
     ANONYMITY: all replacement prose below is written fresh. Do NOT paste arXiv sentences (H4).
     Provenance: neurips_review/sprint/PROVENANCE.md -->

We accept this criticism. The reviewer is right that a practitioner should be able to read this paper and apply it, and in its submitted form several of our central terms arrive before they are explained. The response period does not allow a revised PDF, so rather than promise a rewrite we give the actual replacement text below, for each of the four items raised.

## 1. "deck" arrives 44 lines before it is defined

The reviewer is precisely right, and it is worse than the review suggests: the word appears **eleven times** — across the abstract, the introduction and the related-work section — before §3 defines it. Replacement, to appear at first use in the abstract:

> An **input deck** is the configuration a simulator reads to define a run: for GEOS, one or more XML files specifying the mesh, the physics modules to couple, the material models, the solver settings and the requested outputs. Writing one correctly is the task we study; it is closer to programming against an unfamiliar API than to writing a configuration file.

## 2. Resolution-IV: motivate the design before naming it

The term currently appears first in the **abstract**, with no scaffolding at all, and the design is explained only in §3.2. We also never actually say what resolution IV *means* — only what follows from it. Replacement, to appear before the term is used:

> We want to know what each of the four components contributes. Testing them one at a time is cheap but cannot detect components that only help in combination. Testing all sixteen on/off combinations answers that but doubles the experiment. We therefore run a carefully chosen **half** of the sixteen — eight combinations — selected so that each component's individual effect stays separable from the others. The price of the half-design is that certain *pairwise* interactions become indistinguishable from each other, and we say explicitly which. In the design-of-experiments literature this choice is called a **Resolution-IV fractional factorial**; the name records exactly which effects remain separable.

We should also state the aliasing explicitly rather than leave a reader to derive it, since it is what determines what the experiment can answer:

> Each single-component effect is separable from every pairwise interaction. The six pairwise interactions collapse into three indistinguishable pairs: retrieval×stop-hook with validator×memory, retrieval×validator with stop-hook×memory, and **retrieval×memory with stop-hook×validator**. The last of these is why we cannot read the stop-hook/validator interaction off this design — a limitation reviewer gep1 also raises, and which we address separately with a one-component-at-a-time ablation and with the hook's own telemetry.

And the concrete cost, which we omitted entirely: eight combinations at three seeds is 24 runs against 48 for the full sixteen — **half the compute**, roughly forty hours of the compute we would otherwise have spent. (We then added one further combination that the main effects predicted would be best but which the half-design omits.)

## 3. "buckleyLeverettProblem" needs one sentence

It appears first in §4 as a bare identifier among two others, and is glossed only 70 lines later, in a parenthetical inside the human-baseline subsection. Replacement, at first use:

> `buckleyLeverettProblem` asks the agent to configure a one-dimensional simulation of CO2 displacing brine through porous rock. Because the physics reduces to a single conservation law with a known analytical solution, the deck needs only a handful of GEOS blocks — which is why we treat it as the easy end of our benchmark and use it as our running example.

## 4. The two sentences the reviewer quotes

**"The number of strictly perfect decks does not increase under any adapter."** The problem is that "strictly perfect" is operationalised 130 lines later. Replacement:

> No configuration increased the number of decks that matched the reference almost exactly (structural similarity above 0.999). The adapters change how often the agent produces something badly wrong, not how often it produces something flawless.

**The failures-as-zero sentence.** It contains three undefined terms, one of which (`failed_no_outputs`) is a raw internal status string from our own runner that appears nowhere else in the paper. Replacement:

> When a run produces no usable deck at all — no XML file, an empty file, a file that will not parse, or a timeout — we score it **zero** rather than dropping it from the average. This matters: a system that fails outright on a hard task should not be rewarded with a missing entry instead of a bad one.

## 5. A worked example of a "brief"

A brief is the natural-language task specification the agent receives. Here is the opening and closing of a real one, for the Buckley–Leverett task:

> I need to set up a simulation to model a 1D Buckley-Leverett CO2 core flood experiment. The goal is to verify the immiscible displacement of brine by supercritical CO2 in a porous medium against analytical solutions.
> **Physical Problem and Domain Geometry** […] create a hexahedral mesh of length 0.1 m […]
> - Permeability is 9.0e-13 m² in all directions.
> - The reference porosity is 0.2 at a reference pressure of 10 MPa. […]
> XML files to create: buckleyLeverett_base.xml, buckleyLeverett_benchmark.xml

The point we should have made explicitly: **the brief is written entirely in domain language and never names a single GEOS XML element.** That is what makes this a translation problem rather than a form-filling one, and it is why interface grounding can help at all. Briefs run 2.2k–6.7k characters (median ≈4.2k); this one is 3.7k.

## 6. A worked example of "structured repair feedback"

This is the stop hook's output when it refuses to let the agent finish. A real instance, lightly elided for length:

> Stop blocked by verify_outputs hook: […] fail GEOS schema validation. […]
> wellborePoromechanics.xml:49: element SinglePhasePoromechanics: Schemas validity error : Element 'SinglePhasePoromechanics', attribute 'porousMaterialNames': The attribute 'porousMaterialNames' is not allowed.
> […] Fix the offending element/attribute names against the schema (do NOT guess again — `xmllint` lists expected alternatives for unexpected-element errors and required attribute names for missing-attribute errors). Re-validate locally with
>   xmllint --schema […] --noout <file>.xml
> before ending your turn.

Two things we should have shown rather than described. First, "structured" means the feedback names the file, the line, the element, the attribute, and how to re-check — not "your deck is invalid." Second, in this run it **worked**: the agent was blocked once for a parse error, fixed it, was blocked again for this schema error, fixed that, and terminated with a clean deck — the whole exchange taking about 45 seconds. That is the mechanism the paper's central claim rests on, and one concrete trace communicates it better than our prose does.

The example is also a good illustration of *why* the task is hard: `porousMaterialNames` is a GEOS attribute that was renamed in a later version. The model learned it from older examples, which is exactly the failure mode our §3 describes and the reason schema grounding matters.

## Camera-ready commitment

[[BLOCKED: human decision H2 — how strongly to commit in writing. Draft assumes a firm, itemised commitment; soften if the advisor prefers.]]

Every item above is a text change within camera-ready scope, and we commit to all six: define "input deck" in the abstract; motivate the fractional design before naming it and state the aliasing explicitly; gloss Buckley–Leverett at first use; rewrite both quoted sentences; and add both worked examples — a brief and a repair-feedback trace — as a figure. We will also expand every acronym at first use and replace the internal status strings that leaked into the text.

## On venue

We understand this is the committee's call and will not argue it. We would only note that the paper's intended contribution is a component-wise causal analysis of what interface grounding does and does not buy a general coding agent — including several negative results — which we aimed at readers who build agents rather than at a simulation audience. We are content to let the committee judge the fit.

## Closing

We think the reviewer has identified the most fixable weakness in the paper, and we would rather show the fix than argue about it. If any of the replacements above are still not clear enough, we would genuinely welcome being told so during the discussion period — that is more useful to us than agreement.
