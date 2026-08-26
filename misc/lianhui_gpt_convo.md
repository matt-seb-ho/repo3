The cleanest move is to reframe the method as a reusable simulator-interface grounding recipe, with GEOS/geophysics as the first instantiation and stress test.

Yes. To make the method feel generalizable, you should **stop presenting it as a GEOS customization** and instead present it as a **general adapter recipe for turning coding agents into scientific simulation agents**.

The paper’s method should be:

> **A simulator-interface grounding adapter for scientific simulation setup.**

Then GEOS/geophysics becomes:

> **The first demanding case study where we instantiate and evaluate this adapter.**

That gives you a much stronger technical story.

---

# 1. Rename the method around a general principle

Avoid names like:

> GEOS-RAG plugin  
> GEOS Claude Code customization  
> GEOS XML agent

Those sound engineering-specific.

Use something like:

> **Simulator-Interface Grounding Adapter**  
> **Scientific Simulator Adapter**  
> **Interface-Grounded Simulation Agent**  
> **SimAdapter**  
> **SimAgent Adapter**

My favorite is:

> **Simulator-Interface Grounding Adapter**

Then define it generally:

> Given a scientific simulator SS, its documentation, schema, examples, parser, and execution interface, our method constructs an adapter that grounds a general-purpose coding agent in the simulator’s executable interface. The adapter consists of: simulator-interface retrieval, offline-distilled interface memory, and bounded output verification.

This makes the method domain-agnostic.

---

# 2. Separate domain-independent method from domain-specific instantiation

Right now, the draft’s method reads as: Claude Code + GEOS plugin + GEOS stop-hook + GEOS primer. That is useful but sounds narrow. The draft already contains the reusable ingredients: retrieval over schema/source/docs, a stop-hook verifier, and a distilled primer; the full system improves from 0.497 for vanilla Claude Code to 0.796 ± 0.057, with the largest gain coming from the domain-specific primer.

Rewrite the method as two layers:

## General layer: Simulator-Interface Grounding Adapter

For any simulator SS, construct:

1. **Interface index**  
    Index simulator documentation, schema, examples, source snippets, and tutorials.
    
2. **Interface retrieval tools**  
    Provide retrieval routes for conceptual guidance, formal schema/attributes, and concrete reference examples.
    
3. **Distilled interface primer**  
    Compress successful training trajectories, schema names, solver families, model names, and configuration patterns into an always-on primer.
    
4. **Output verifier**  
    Check whether the agent produced files in the correct location, whether they parse, and ideally whether they execute.
    
5. **Repair loop**  
    Feed verifier errors back to the agent for bounded self-correction.
    

## Domain instantiation: Geophysics

For this paper:

- simulator SS: GEOS-based geophysics simulation setup;
    
- interface language: XML input decks;
    
- retrieved assets: GEOS schema, examples, docs;
    
- verifier: XML presence and parseability;
    
- metric: TreeSim-fa0 over generated simulator decks.
    

This way, the reader sees that **GEOS is an instantiation of a general recipe**, not the recipe itself.

---

# 3. Present the method as an adapter function

A nice formal framing:

SimAgent(S)=A∘G(S)SimAgent(S)=A∘G(S)

where:

- AA is a general-purpose coding agent;
    
- SS is a scientific simulator;
    
- G(S)G(S) is the simulator-interface grounding adapter.
    

Then define:

G(S)={RS,PS,VS,HS}G(S)={RS​,PS​,VS​,HS​}

where:

- RSRS​: simulator-specific retrieval over schema, docs, examples;
    
- PSPS​: distilled simulator-interface primer;
    
- VSVS​: output verifier/parser/execution checker;
    
- HSHS​: repair hints generated from verifier failures.
    

This gives the method a clean ML-paper structure.

You can write:

> Our method does not train a new model and does not assume access to simulator internals beyond assets that most scientific simulators already expose: documentation, examples, schemas or parsers, and command-line execution. This makes the adapter portable in principle across simulator families. In this paper, we instantiate the adapter for geophysics simulation setup and evaluate it on GEOS-based input-deck generation.

That sounds much more general.

---

# 4. Claim “designed for generalization,” not “proven across all domains”

Since the current experiments are mainly GEOS/geophysics, be careful. You should not claim:

> Our method generalizes to all scientific simulators.

Instead claim:

> Our method is **designed as a reusable adapter pattern** for scientific simulators, and geophysics provides the first high-stakes case study.

Or:

> While our empirical evaluation is in geophysics, the method is constructed from simulator-agnostic components: interface retrieval, distilled interface memory, and bounded output verification. These components depend only on assets common to many simulators.

This is honest and defensible.

---

# 5. Add a “generalization axes” paragraph

This would strengthen the paper a lot.

You can say:

> Generalization in this setting has four axes. **Task generalization** asks whether the agent handles unseen simulation setups within the same simulator. **Model generalization** asks whether the adapter improves different LLM backbones. **Harness generalization** asks whether the adapter transfers across coding-agent harnesses. **Simulator generalization** asks whether the same adapter-construction recipe can be instantiated for other scientific simulators.

Then map your current evidence:

- Task generalization: 17 held-out geophysics tasks.
    
- Model generalization: partial, plugin tested on another model.
    
- Harness generalization: not yet tested.
    
- Simulator generalization: future work.
    

This makes the scope clear.

Suggested wording:

> In this paper we provide evidence for task generalization within a demanding geophysics benchmark and partial evidence for model generalization through cross-model retrieval experiments. We do not yet claim full harness or simulator generalization; instead, we define the adapter so that these become measurable future transfer experiments.

That is reviewer-friendly.

---

# 6. Make the reusable method depend on common simulator assets

To make the method convincingly general, emphasize that it only requires things many scientific simulators already have.

Most simulators have:

- documentation;
    
- example input files;
    
- source code or API references;
    
- parser errors;
    
- execution commands;
    
- output files;
    
- benchmark/tutorial cases.
    

Your method should say:

> We assume a simulator provides documentation, example configurations, and a parser or execution command. These are weak assumptions satisfied by many scientific software systems.

Then:

> The adapter is constructed automatically or semi-automatically from these assets.

That makes it portable.

---

# 7. Replace GEOS-specific component names with generic names

Current-style wording:

> We build a GEOS-RAG plugin over GEOS schema, source, and navigator docs.

More general wording:

> We build a simulator-interface retrieval module with three retrieval channels: conceptual navigation, authoritative schema lookup, and reference-example lookup.

Current-style wording:

> The stop hook checks `/workspace/inputs/` for XML.

More general wording:

> The verifier checks whether the generated simulator artifact exists, is placed correctly, and satisfies the simulator’s parseability constraints.

Current-style wording:

> The primer contains GEOS solver families and constitutive-model class names.

More general wording:

> The primer contains the simulator’s executable vocabulary: solver families, model classes, required fields, allowed attributes, and canonical configuration patterns.

Then you can add:

> In our geophysics instantiation, these become GEOS XML sections, solver classes, constitutive models, and field specifications.

That is the right hierarchy.

---

# 8. Add a general algorithm box

This would make the paper feel less like engineering and more like a method paper.

## Algorithm: Simulator-Interface Grounding Adapter

**Input:** simulator SS, documentation DD, example configurations EE, parser or validator VV, training tasks TtrainTtrain​, coding agent AA

**Offline construction:**

1. Build retrieval indices from DD, EE, schemas, and source snippets.
    
2. Run AA on training tasks with retrieval enabled.
    
3. Collect successful trajectories and common failures.
    
4. Distill an interface primer containing valid vocabulary and canonical patterns.
    
5. Construct verifier VSVS​ for artifact presence, parseability, and optionally execution.
    

**Inference:**

1. User provides natural-language simulation goal.
    
2. Agent retrieves relevant schema/examples.
    
3. Agent writes simulator input files.
    
4. Verifier checks output artifacts.
    
5. If verification fails, agent receives repair hints.
    
6. Final simulator configuration is returned for expert review or execution.
    

This gives you a clean, reusable method.

---

# 9. Add one small cross-domain pilot if possible

The best way to make the method generalizable is to test it on **one small second simulator**.

It does not need to be a full benchmark. Even a small proof-of-transfer helps.

For example:

- OpenFOAM case setup;
    
- LAMMPS molecular dynamics input generation;
    
- FEniCS/PDE solver setup;
    
- MODFLOW groundwater flow configuration;
    
- MOOSE input files;
    
- PyBaMM battery simulation setup.
    

A small transfer experiment could be:

> We instantiate the same adapter recipe on 5 OpenFOAM or LAMMPS tasks using only simulator docs, examples, a distilled primer, and a parser/execution check. The goal is not to outperform specialized systems, but to show that the adapter construction process is not GEOS-specific.

Even a small result table would help:

|Domain|Simulator artifact|Adapter changes|Tasks|Result|
|---|---|---|---|---|
|Geophysics|XML decks|Full|17|Main result|
|CFD / MD / groundwater|case/input files|Retrieval + primer + verifier|5|Pilot transfer|

If you cannot run this before submission, include it as a future-work protocol, but actual numbers would make the paper much stronger.

---

# 10. Add an “adapter construction cost” metric

This is a great way to sell generalizability.

Report:

- number of documents indexed;
    
- number of examples indexed;
    
- number of training trajectories used for primer distillation;
    
- number of domain-specific lines of code;
    
- number of simulator-specific verifier rules;
    
- human hours needed to build the adapter.
    

Then you can claim:

> The adapter requires simulator assets rather than model retraining.

This is a strong generalizable message.

For example:

> For the geophysics instantiation, the adapter is built from existing simulator documentation, example decks, and 18 training trajectories. No model training is required. The only simulator-specific implementation is the asset indexer, the XML verifier, and the domain primer.

That makes the method look portable.

---

# 11. Reframe the central result as a reusable lesson

Current result:

> The monolithic GEOS primer works best.

Generalizable lesson:

> In scientific simulation setup, always-on interface memory can outperform optional retrieval because simulator vocabulary is needed continuously throughout generation.

This is much broader.

Suggested wording:

> Our ablations suggest that the dominant adaptation is not geophysics-specific reasoning, but exposure to the simulator’s executable vocabulary. This observation should transfer to other simulators whose interfaces are similarly brittle: OpenFOAM dictionaries, LAMMPS scripts, finite-element input decks, reservoir-simulation schedules, or climate-model namelists. In all such cases, the agent must produce exact interface tokens rather than approximate natural-language answers.

This turns a GEOS result into a general design principle.

---

# 12. Proposed revised method section opening

You can use this directly:

> We propose a **Simulator-Interface Grounding Adapter**, a lightweight method for adapting general-purpose coding agents to scientific simulation setup. The method is motivated by a common structure across scientific simulators: users specify scientific intent in natural language, but simulators require executable artifacts written in specialized interface languages such as XML decks, input scripts, case dictionaries, namelists, or configuration files. General coding agents can edit files and invoke tools, but they are not reliably grounded in the exact vocabulary, schema, version conventions, and cross-file constraints of these simulator interfaces.
> 
> Our adapter supplies this missing grounding through three simulator-agnostic mechanisms. First, it builds retrieval indices over simulator documentation, schemas, source-adjacent references, and example configurations. Second, it distills successful training trajectories into an always-on interface primer containing valid solver names, model classes, attributes, and canonical configuration patterns. Third, it verifies generated artifacts using simulator-specific parseability or execution checks and provides bounded repair feedback. The adapter does not require training a new model; it requires only simulator assets that are commonly available in scientific software.
> 
> We instantiate this method in geophysics simulation setup, where the generated artifacts are GEOS-compatible XML input decks. GEOS is therefore the experimental substrate, not the methodological assumption: the same adapter recipe can be applied to other simulators by replacing the indexed assets, primer vocabulary, and verifier.

This is exactly the framing you want.

---

# 13. Revised contribution list with generalizability

Use this instead of a GEOS-heavy list:

> **Our contributions are:**
> 
> 1. We identify scientific simulation setup as a general bottleneck for AI-assisted science: converting scientific intent into executable simulator configurations remains expert-intensive and difficult to scale.
>     
> 2. We propose a **Simulator-Interface Grounding Adapter** for adapting general-purpose coding agents to simulator setup tasks. The adapter combines simulator-interface retrieval, offline-distilled interface memory, and bounded output verification.
>     
> 3. We instantiate the adapter in geophysics, a representative simulation-heavy scientific domain, where the task is to generate structured simulator input decks from natural-language descriptions.
>     
> 4. We introduce a 17-task geophysics simulation setup benchmark and show that the adapted agent substantially improves over harness-less prompting and vanilla coding-agent baselines.
>     
> 5. Through ablations, we show that the primary mechanism is simulator-interface grounding: content-specific executable vocabulary improves performance, while optional memory retrieval and generic self-refinement do not drive the result.
>     
> 6. We discuss how the adapter can be instantiated for other scientific simulators by replacing the indexed assets, distilled primer, and verifier, providing a roadmap for cross-domain scientific simulation agents.
>     

---

# 14. What not to overclaim

Do **not** say:

> Our method generalizes to all scientific domains.

Say:

> Our method is designed to generalize across scientific simulators because it depends on common simulator assets rather than GEOS-specific assumptions.

Do **not** say:

> We solve scientific simulation.

Say:

> We reduce the setup bottleneck by generating expert-reviewable first drafts.

Do **not** say:

> The agent understands geophysics.

Say:

> The agent is grounded in the simulator interface well enough to produce high-quality configuration drafts.

---

# 15. Best final framing

I would frame the method like this:

> **General problem:** scientific simulation setup is a bottleneck.  
> **General method:** simulator-interface grounding adapter.  
> **Case-study domain:** geophysics.  
> **Concrete instantiation:** GEOS-compatible input-deck generation.  
> **Empirical lesson:** always-on executable-interface vocabulary matters more than generic agentic machinery.  
> **Future generalization:** replace the schema/docs/examples/verifier to instantiate the same adapter for other simulators.

That gives you a method that feels general, timely, and technically meaningful without pretending you have already solved every simulator domain.

  

# Selling AgentFactory for Geophysics

You’re viewing user-generated content that may be unverified or unsafe.

[Report](https://openai.com/form/report-content/)

The cleanest move is to reframe the method as a reusable simulator-interface grounding recipe, with GEOS/geophysics as the first instantiation and stress test.

Yes. To make the method feel generalizable, you should **stop presenting it as a GEOS customization** and instead present it as a **general adapter recipe for turning coding agents into scientific simulation agents**.

The paper’s method should be:

> **A simulator-interface grounding adapter for scientific simulation setup.**

Then GEOS/geophysics becomes:

> **The first demanding case study where we instantiate and evaluate this adapter.**

That gives you a much stronger technical story.

---

# 1. Rename the method around a general principle

Avoid names like:

> GEOS-RAG plugin  
> GEOS Claude Code customization  
> GEOS XML agent

Those sound engineering-specific.

Use something like:

> **Simulator-Interface Grounding Adapter**  
> **Scientific Simulator Adapter**  
> **Interface-Grounded Simulation Agent**  
> **SimAdapter**  
> **SimAgent Adapter**

My favorite is:

> **Simulator-Interface Grounding Adapter**

Then define it generally:

> Given a scientific simulator SS, its documentation, schema, examples, parser, and execution interface, our method constructs an adapter that grounds a general-purpose coding agent in the simulator’s executable interface. The adapter consists of: simulator-interface retrieval, offline-distilled interface memory, and bounded output verification.

This makes the method domain-agnostic.

---

# 2. Separate domain-independent method from domain-specific instantiation

Right now, the draft’s method reads as: Claude Code + GEOS plugin + GEOS stop-hook + GEOS primer. That is useful but sounds narrow. The draft already contains the reusable ingredients: retrieval over schema/source/docs, a stop-hook verifier, and a distilled primer; the full system improves from 0.497 for vanilla Claude Code to 0.796 ± 0.057, with the largest gain coming from the domain-specific primer.

Rewrite the method as two layers:

## General layer: Simulator-Interface Grounding Adapter

For any simulator SS, construct:

1. **Interface index**  
    Index simulator documentation, schema, examples, source snippets, and tutorials.
    
2. **Interface retrieval tools**  
    Provide retrieval routes for conceptual guidance, formal schema/attributes, and concrete reference examples.
    
3. **Distilled interface primer**  
    Compress successful training trajectories, schema names, solver families, model names, and configuration patterns into an always-on primer.
    
4. **Output verifier**  
    Check whether the agent produced files in the correct location, whether they parse, and ideally whether they execute.
    
5. **Repair loop**  
    Feed verifier errors back to the agent for bounded self-correction.
    

## Domain instantiation: Geophysics

For this paper:

- simulator SS: GEOS-based geophysics simulation setup;
    
- interface language: XML input decks;
    
- retrieved assets: GEOS schema, examples, docs;
    
- verifier: XML presence and parseability;
    
- metric: TreeSim-fa0 over generated simulator decks.
    

This way, the reader sees that **GEOS is an instantiation of a general recipe**, not the recipe itself.

---

# 3. Present the method as an adapter function

A nice formal framing:

SimAgent(S)=A∘G(S)SimAgent(S)=A∘G(S)

where:

- AA is a general-purpose coding agent;
    
- SS is a scientific simulator;
    
- G(S)G(S) is the simulator-interface grounding adapter.
    

Then define:

G(S)={RS,PS,VS,HS}G(S)={RS​,PS​,VS​,HS​}

where:

- RSRS​: simulator-specific retrieval over schema, docs, examples;
    
- PSPS​: distilled simulator-interface primer;
    
- VSVS​: output verifier/parser/execution checker;
    
- HSHS​: repair hints generated from verifier failures.
    

This gives the method a clean ML-paper structure.

You can write:

> Our method does not train a new model and does not assume access to simulator internals beyond assets that most scientific simulators already expose: documentation, examples, schemas or parsers, and command-line execution. This makes the adapter portable in principle across simulator families. In this paper, we instantiate the adapter for geophysics simulation setup and evaluate it on GEOS-based input-deck generation.

That sounds much more general.

---

# 4. Claim “designed for generalization,” not “proven across all domains”

Since the current experiments are mainly GEOS/geophysics, be careful. You should not claim:

> Our method generalizes to all scientific simulators.

Instead claim:

> Our method is **designed as a reusable adapter pattern** for scientific simulators, and geophysics provides the first high-stakes case study.

Or:

> While our empirical evaluation is in geophysics, the method is constructed from simulator-agnostic components: interface retrieval, distilled interface memory, and bounded output verification. These components depend only on assets common to many simulators.

This is honest and defensible.

---

# 5. Add a “generalization axes” paragraph

This would strengthen the paper a lot.

You can say:

> Generalization in this setting has four axes. **Task generalization** asks whether the agent handles unseen simulation setups within the same simulator. **Model generalization** asks whether the adapter improves different LLM backbones. **Harness generalization** asks whether the adapter transfers across coding-agent harnesses. **Simulator generalization** asks whether the same adapter-construction recipe can be instantiated for other scientific simulators.

Then map your current evidence:

- Task generalization: 17 held-out geophysics tasks.
    
- Model generalization: partial, plugin tested on another model.
    
- Harness generalization: not yet tested.
    
- Simulator generalization: future work.
    

This makes the scope clear.

Suggested wording:

> In this paper we provide evidence for task generalization within a demanding geophysics benchmark and partial evidence for model generalization through cross-model retrieval experiments. We do not yet claim full harness or simulator generalization; instead, we define the adapter so that these become measurable future transfer experiments.

That is reviewer-friendly.

---

# 6. Make the reusable method depend on common simulator assets

To make the method convincingly general, emphasize that it only requires things many scientific simulators already have.

Most simulators have:

- documentation;
    
- example input files;
    
- source code or API references;
    
- parser errors;
    
- execution commands;
    
- output files;
    
- benchmark/tutorial cases.
    

Your method should say:

> We assume a simulator provides documentation, example configurations, and a parser or execution command. These are weak assumptions satisfied by many scientific software systems.

Then:

> The adapter is constructed automatically or semi-automatically from these assets.

That makes it portable.

---

# 7. Replace GEOS-specific component names with generic names

Current-style wording:

> We build a GEOS-RAG plugin over GEOS schema, source, and navigator docs.

More general wording:

> We build a simulator-interface retrieval module with three retrieval channels: conceptual navigation, authoritative schema lookup, and reference-example lookup.

Current-style wording:

> The stop hook checks `/workspace/inputs/` for XML.

More general wording:

> The verifier checks whether the generated simulator artifact exists, is placed correctly, and satisfies the simulator’s parseability constraints.

Current-style wording:

> The primer contains GEOS solver families and constitutive-model class names.

More general wording:

> The primer contains the simulator’s executable vocabulary: solver families, model classes, required fields, allowed attributes, and canonical configuration patterns.

Then you can add:

> In our geophysics instantiation, these become GEOS XML sections, solver classes, constitutive models, and field specifications.

That is the right hierarchy.

---

# 8. Add a general algorithm box

This would make the paper feel less like engineering and more like a method paper.

## Algorithm: Simulator-Interface Grounding Adapter

**Input:** simulator SS, documentation DD, example configurations EE, parser or validator VV, training tasks TtrainTtrain​, coding agent AA

**Offline construction:**

1. Build retrieval indices from DD, EE, schemas, and source snippets.
    
2. Run AA on training tasks with retrieval enabled.
    
3. Collect successful trajectories and common failures.
    
4. Distill an interface primer containing valid vocabulary and canonical patterns.
    
5. Construct verifier VSVS​ for artifact presence, parseability, and optionally execution.
    

**Inference:**

1. User provides natural-language simulation goal.
    
2. Agent retrieves relevant schema/examples.
    
3. Agent writes simulator input files.
    
4. Verifier checks output artifacts.
    
5. If verification fails, agent receives repair hints.
    
6. Final simulator configuration is returned for expert review or execution.
    

This gives you a clean, reusable method.

---

# 9. Add one small cross-domain pilot if possible

The best way to make the method generalizable is to test it on **one small second simulator**.

It does not need to be a full benchmark. Even a small proof-of-transfer helps.

For example:

- OpenFOAM case setup;
    
- LAMMPS molecular dynamics input generation;
    
- FEniCS/PDE solver setup;
    
- MODFLOW groundwater flow configuration;
    
- MOOSE input files;
    
- PyBaMM battery simulation setup.
    

A small transfer experiment could be:

> We instantiate the same adapter recipe on 5 OpenFOAM or LAMMPS tasks using only simulator docs, examples, a distilled primer, and a parser/execution check. The goal is not to outperform specialized systems, but to show that the adapter construction process is not GEOS-specific.

Even a small result table would help:

|Domain|Simulator artifact|Adapter changes|Tasks|Result|
|---|---|---|---|---|
|Geophysics|XML decks|Full|17|Main result|
|CFD / MD / groundwater|case/input files|Retrieval + primer + verifier|5|Pilot transfer|

If you cannot run this before submission, include it as a future-work protocol, but actual numbers would make the paper much stronger.

---

# 10. Add an “adapter construction cost” metric

This is a great way to sell generalizability.

Report:

- number of documents indexed;
    
- number of examples indexed;
    
- number of training trajectories used for primer distillation;
    
- number of domain-specific lines of code;
    
- number of simulator-specific verifier rules;
    
- human hours needed to build the adapter.
    

Then you can claim:

> The adapter requires simulator assets rather than model retraining.

This is a strong generalizable message.

For example:

> For the geophysics instantiation, the adapter is built from existing simulator documentation, example decks, and 18 training trajectories. No model training is required. The only simulator-specific implementation is the asset indexer, the XML verifier, and the domain primer.

That makes the method look portable.

---

# 11. Reframe the central result as a reusable lesson

Current result:

> The monolithic GEOS primer works best.

Generalizable lesson:

> In scientific simulation setup, always-on interface memory can outperform optional retrieval because simulator vocabulary is needed continuously throughout generation.

This is much broader.

Suggested wording:

> Our ablations suggest that the dominant adaptation is not geophysics-specific reasoning, but exposure to the simulator’s executable vocabulary. This observation should transfer to other simulators whose interfaces are similarly brittle: OpenFOAM dictionaries, LAMMPS scripts, finite-element input decks, reservoir-simulation schedules, or climate-model namelists. In all such cases, the agent must produce exact interface tokens rather than approximate natural-language answers.

This turns a GEOS result into a general design principle.

---

# 12. Proposed revised method section opening

You can use this directly:

> We propose a **Simulator-Interface Grounding Adapter**, a lightweight method for adapting general-purpose coding agents to scientific simulation setup. The method is motivated by a common structure across scientific simulators: users specify scientific intent in natural language, but simulators require executable artifacts written in specialized interface languages such as XML decks, input scripts, case dictionaries, namelists, or configuration files. General coding agents can edit files and invoke tools, but they are not reliably grounded in the exact vocabulary, schema, version conventions, and cross-file constraints of these simulator interfaces.
> 
> Our adapter supplies this missing grounding through three simulator-agnostic mechanisms. First, it builds retrieval indices over simulator documentation, schemas, source-adjacent references, and example configurations. Second, it distills successful training trajectories into an always-on interface primer containing valid solver names, model classes, attributes, and canonical configuration patterns. Third, it verifies generated artifacts using simulator-specific parseability or execution checks and provides bounded repair feedback. The adapter does not require training a new model; it requires only simulator assets that are commonly available in scientific software.
> 
> We instantiate this method in geophysics simulation setup, where the generated artifacts are GEOS-compatible XML input decks. GEOS is therefore the experimental substrate, not the methodological assumption: the same adapter recipe can be applied to other simulators by replacing the indexed assets, primer vocabulary, and verifier.

This is exactly the framing you want.

---

# 13. Revised contribution list with generalizability

Use this instead of a GEOS-heavy list:

> **Our contributions are:**
> 
> 1. We identify scientific simulation setup as a general bottleneck for AI-assisted science: converting scientific intent into executable simulator configurations remains expert-intensive and difficult to scale.
>     
> 2. We propose a **Simulator-Interface Grounding Adapter** for adapting general-purpose coding agents to simulator setup tasks. The adapter combines simulator-interface retrieval, offline-distilled interface memory, and bounded output verification.
>     
> 3. We instantiate the adapter in geophysics, a representative simulation-heavy scientific domain, where the task is to generate structured simulator input decks from natural-language descriptions.
>     
> 4. We introduce a 17-task geophysics simulation setup benchmark and show that the adapted agent substantially improves over harness-less prompting and vanilla coding-agent baselines.
>     
> 5. Through ablations, we show that the primary mechanism is simulator-interface grounding: content-specific executable vocabulary improves performance, while optional memory retrieval and generic self-refinement do not drive the result.
>     
> 6. We discuss how the adapter can be instantiated for other scientific simulators by replacing the indexed assets, distilled primer, and verifier, providing a roadmap for cross-domain scientific simulation agents.
>     

---

# 14. What not to overclaim

Do **not** say:

> Our method generalizes to all scientific domains.

Say:

> Our method is designed to generalize across scientific simulators because it depends on common simulator assets rather than GEOS-specific assumptions.

Do **not** say:

> We solve scientific simulation.

Say:

> We reduce the setup bottleneck by generating expert-reviewable first drafts.

Do **not** say:

> The agent understands geophysics.

Say:

> The agent is grounded in the simulator interface well enough to produce high-quality configuration drafts.

---

# 15. Best final framing

I would frame the method like this:

> **General problem:** scientific simulation setup is a bottleneck.  
> **General method:** simulator-interface grounding adapter.  
> **Case-study domain:** geophysics.  
> **Concrete instantiation:** GEOS-compatible input-deck generation.  
> **Empirical lesson:** always-on executable-interface vocabulary matters more than generic agentic machinery.  
> **Future generalization:** replace the schema/docs/examples/verifier to instantiate the same adapter for other simulators.

That gives you a method that feels general, timely, and technically meaningful without pretending you have already solved every simulator domain.