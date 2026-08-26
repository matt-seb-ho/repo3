<!-- One-page narrative progress report. Format target: Calibri 11pt, single-spaced. -->

# Year 1 Progress Report — Geophysics AI Agent for GEOS Multiphysics Simulation

**Project component:** UC AI team. Autonomous LLM agent for operating GEOS, LLNL's open-source multiphysics simulator for CO₂ storage and induced seismicity.

### 1. Progress toward project aims
The Year 1 aim was a working geophysics agent that lowers the expert-only barrier of running coupled multiphysics subsurface simulations in GEOS. We delivered it as a Simulator-Interface Grounding Adapter (SIGA) wrapped around a frontier coding harness, combining domain-specific retrieval, validation hooks, and a distilled procedural-memory primer, alongside the first held-out benchmark for coupled multiphysics subsurface simulation setup and a self-evolving variant in which the harness rewrites its own primer and skill library from execution traces.

### 2. Key results and major accomplishments
A Resolution-IV factorial over the four SIGA components, against a vanilla coding-harness baseline, yields three headline findings. **Reliability:** on a hard held-out set of compound multiphysics tasks, the best SIGA configuration cuts across-seed score variance by roughly **40×**, eliminating the empty, unparseable, and missing-deck failures the vanilla harness produces. **Quality:** mean structural similarity on the same set rises by **~7 percentage points**, with two catastrophic-failure tasks recovered from sub-0.55 to above 0.76. **Efficiency:** the self-evolved variant matches the best hand-designed configuration with **~16% fewer tool calls**. A human baseline with two graduate-level geoscientists new to GEOS finds the agent reaches the structural similarity of an unbounded-budget human submission (~3 hours) in roughly 5 minutes, an **8–36× wall-clock speedup** depending on task complexity. A cross-simulator transfer study to OpenFOAM reproduces the same pattern.

### 3. Obstacles, delays, or challenges
The dominant obstacle was data scarcity: the public corpus of validated coupled-multiphysics simulation runs is too small for conventional supervised fine-tuning or RL. We pivoted to weight-free adaptation, using an offline-distilled memory primer, a self-evolving harness that learns from execution traces, and structured validation feedback. No remaining blockers.

### 4. Plans for next year
Two complementary tracks. **(a) Scaling data and scope with LLNL.** Deeper collaboration with the GEOS development team to assemble a larger corpus of validated simulations, enabling more robust evaluation and a first reinforcement-learning fine-tuning attempt, and to expand the agent's responsibilities into broader portions of the geoscientist workflow, with evaluation focused on autonomy and reliability in extended multi-step tasks. **(b) Exploiting scientific-domain priors for meta-harness construction.** Current automated harness builders treat documentation, scientific literature, and codebases as flat substrates to grep. We will instead leverage their structure as priors: the meta-harness performs a structured pre-task study over each tool's docs and related artifacts, distilling them into a persistent typed substrate (section notes, hierarchical roll-ups, a component-to-section grounding graph) that both the meta-harness and the runtime harness it builds consume directly. Evaluation on GEOS plus a cross-tool transfer (FEniCS or MOOSE), with a post-training-cutoff condition to control for in-distribution model exposure.

### 5. Publications
Submitted to NeurIPS 2026: *Simulator-Interface Grounding Adapters for Scientific Simulation Setup: A Geophysics Case Study*; refined preprint in preparation for arXiv.
