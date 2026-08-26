<!-- One-page narrative progress report. Format target: Calibri 11pt, single-spaced. -->

# Year 1 Progress Report — Geophysics AI Agent for GEOS Multiphysics Simulation

**Project component:** UC AI team. Autonomous LLM agent for operating GEOS, LLNL's open-source multiphysics simulator for CO₂ storage and induced seismicity.

### 1. Progress toward project aims
The Year 1 aim was a working geophysics agent that lowers the expert-only barrier of running coupled multiphysics subsurface simulations in GEOS. We delivered it end-to-end: a Simulator-Interface Grounding Adapter (SIGA) wrapped around a frontier coding harness, combining GEOS-specific retrieval over documentation and schema, an XML validation hook, an agent-callable validator, and a procedural-memory primer distilled from training trajectories. We also built the first held-out benchmark, to our knowledge, for coupled multiphysics subsurface simulation setup, scored by a tree-aware structural-similarity metric, and a self-evolving variant in which the harness rewrites its own primer and skill library from execution traces.

### 2. Key results and major accomplishments
A Resolution-IV factorial over the four SIGA components, against a vanilla coding-harness baseline, yields three headline findings. **Reliability:** on a hard held-out set of compound multiphysics tasks, the best SIGA configuration cuts across-seed score variance by roughly **40×**, eliminating the empty, unparseable, and missing-deck failures the vanilla harness produces on a non-trivial tail. **Quality:** mean structural similarity on the same set rises by **~7 percentage points**, with two catastrophic-failure tasks recovered from sub-0.55 to above 0.76. **Efficiency:** the self-evolved variant matches the best hand-designed configuration with ~16% fewer tool calls. A human baseline with two graduate-level geoscientists new to GEOS finds the agent reaches the structural similarity of an unbounded-budget human submission (~3 hours) in roughly 5 minutes, an **8–36× wall-clock speedup** depending on task complexity. A cross-simulator transfer study to OpenFOAM reproduces the same pattern, and a failure-mode decomposition pinpoints the remaining frontier as attribute-level semantic errors that schema validation alone cannot catch.

### 3. Obstacles, delays, or challenges
The dominant obstacle was data scarcity: the public corpus of validated coupled-multiphysics simulation runs is too small for conventional supervised fine-tuning or RL. We pivoted to weight-free adaptation, an offline-distilled memory primer, a self-evolving harness that learns from execution traces, and structured validation feedback in place of gradient signal, placing the contribution at the harness rather than the model layer. No remaining blockers.

### 4. Plans for next year
Two complementary tracks. **(a) Scaling data and scope with LLNL.** Deeper collaboration with the GEOS development team to assemble a substantially larger corpus of validated simulations, supporting more robust evaluation and a first weight-update training attempt, and to expand the agent's responsibilities further into the geoscientist workflow with evaluation focused on autonomy and reliability in extended, multi-step tasks. **(b) Automating the recipe.** Converting the manually engineered SIGA recipe into an automated meta-procedure: given a scientific tool and its documentation, the meta-harness performs a structured pre-task study over the docs, distilling them into a persistent artifact and a component-to-section grounding graph from which it constructs and iteratively refines a tool-specialized harness. We will evaluate on GEOS plus a cross-tool transfer (FEniCS or MOOSE), with a post-training-cutoff tool version to control for in-distribution model exposure.

### 5. Publications
Submitted to NeurIPS 2026: *Simulator-Interface Grounding Adapters for Scientific Simulation Setup: A Geophysics Case Study*; refined preprint in preparation for arXiv.
