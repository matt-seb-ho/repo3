# NeurIPS 2026 — Reviews for Submission 31642 (SIGA)

**Paper:** Simulator-Interface Grounding Adapters (SIGA)
**Submission:** 31642
**Decision status:** Borderline (rebuttal phase)

## Score Summary

| Reviewer | Rating | Confidence | Quality | Clarity | Significance | Originality |
|---|---|---|---|---|---|---|
| gep1 | **4** — Borderline accept | 3 (fairly confident) | 3 good | 3 good | 3 good | 3 good |
| kEdh | **2** — Reject | 4 (confident) | 2 not good | 2 not good | 3 good | 3 good |
| nBNe | **5** — Accept | 5 (absolutely certain) | 3 good | 3 good | 4 excellent | 3 good |
| **AC GKRj** | — | — | — | — | — | — |

All three reviewers classified the contribution type as **Use-inspired**. No ethical concerns, no formatting concerns from any reviewer.

---

## Meta Review — Area Chair GKRj

*23 Jul 2026*

The paper proposes SIGA, a simulator-interface grounding adapter for improving the reliability of general-purpose coding agents when generating scientific simulator configurations. The reviewers agree that the problem is practically important and view the systematic component analysis, reduction in catastrophic failures, and preliminary transfer to OpenFOAM positively. However, the ratings are divergent, with accept, borderline accept, and reject scores. At this stage, the main obstacles to acceptance are:

- **Structural-only evaluation.** The evaluation primarily measures structural similarity using TreeSim, rather than whether the generated configurations execute successfully, converge, or produce physically meaningful simulations (gep1, nBNe). A small execution-based evaluation would substantially strengthen the central claim that SIGA improves simulator reliability rather than only configuration structure.
- **Clarity / jargon.** Reviewer kEdh also found several key concepts and evaluation choices difficult to follow and a bit jargony. I see the same issue with the writing of the paper, as in its current state, it would be hard for a NeurIPS reader to fully understand many things in the paper.
- **Limited experimental scale.** (gep1, nBNe) The main hard-task evaluation uses only ten tasks and three seeds, while the OpenFOAM transfer experiment uses five tasks and a single seed. The rebuttal should clarify the representativeness of these tasks, provide uncertainty estimates where possible, and moderate the robustness and generalization claims if additional evaluation is unavailable.
- **Human comparison too small.** (gep1, nBNe) Two participants on one task are useful as preliminary calibration, but the claims should either be narrowed or better contextualized.

> The decision will likely depend on whether the rebuttal can establish that the structural improvements translate to executable and scientifically valid simulations and whether the authors can put significant efforts towards improving the clarity of the paper towards general NeurIPS audience. At present, I view the paper as borderline.

---

## Reviewer gep1 — Rating 4 (Borderline accept), Confidence 3

*26 Jun 2026*

### Summary

Paper studies how to adapt a general-purpose LLM coding harness for scientific simulator setup, focusing on GEOS XML deck authoring. It proposes Simulator-Interface Grounding Adapters (SIGA): retrieval over documentation/schema/examples, stop-hook verification, an agent-callable XML validator, and an always-on memory cheatsheet. The paper contributes a GEOS deck-authoring benchmark, a TreeSim structural-similarity metric, a Resolution-IV factorial study over adapter components, a self-evolved adapter variant, a small human-baseline study, and a small OpenFOAM transfer study. The main finding is that SIGA does not uniformly improve already-good outputs, but reduces catastrophic failures on harder compound multiphysics tasks, especially through forced end-of-turn verification. The bottleneck analysis further shows that adapters help with missing whole blocks but do not solve attribute-level or semantic simulator errors.

### Strengths

- Useful and well-motivated paper; the problem setting is concrete and the case that simulator setup is an important bottleneck for scientific agents is convincing.
- Studies **wrapper-level grounding around an existing coding harness** rather than proposing an entirely new agent stack.
- The **factorial design is a strength**: gives more insight than a single "our system vs baseline" comparison.
- The **bottleneck analysis** makes the results more informative by showing which errors are actually being addressed.
- Strongest empirical result: the reliability improvement on the harder held-out GEOS tasks. The paper is careful in explaining that the adapter mainly prevents catastrophic failures (empty, missing, or unparseable decks) rather than improving the ceiling of already-good outputs. This distinction is important and makes the contribution more credible.
- The **negative findings are valuable**: retrieval can hurt, memory exposed as a retrievable tool may not be used, and human-consultation tools may be bypassed when an example library is available.

### Weaknesses

1. **Evaluation is mostly structural.** TreeSim is appropriate as a scalable first metric, but it does not establish that generated decks run successfully in GEOS or produce physically meaningful simulations. This limits the strength of the practical claims. The authors acknowledge this, but the central usefulness of the system would be much stronger with even a small runnability/physics-validity ladder.
2. **Statistical and experimental scale.** Main GEOS results use n=3 seeds and only 10 harder held-out tasks. The OpenFOAM transfer study is only 5 tasks, single-seed, and uses a constrained lint-only Foam-Agent baseline. The human baseline is only n=2 on one relatively easy task, so it should be interpreted as anecdotal calibration rather than strong evidence about human-vs-agent performance.
3. **Methodological confounds.** The S and X components both involve validation, so the individual role of stop-hook enforcement versus validator availability is not fully isolated. The paper also reports a **native-plugin-prefix bug** that contaminated some estimates involving retrieval.

**Originality:** good but not in the form of a new model or algorithm — novelty is in the benchmark, the adapter framing, the component-wise evaluation, and the detailed failure-mode analysis. **Significance:** good, especially for scientific-agent work, but impact depends on whether structural reliability gains translate to executable and scientifically valid simulations.

### Questions

1. **[Score-moving]** Can the authors add a small GEOS execution-based evaluation? Even 5 tasks across Vanilla and the best SIGA cell would help establish whether TreeSim gains correspond to runnable decks. *"My score would increase if the reliability gains persist under execution or physical-validity checks."*
2. **[Score-moving]** Can the authors rerun the cells affected by the native-plugin-prefix bug and more cleanly separate S from X? *"My confidence would increase if the stop-hook effect remains dominant after removing this confound."*
3. Can the authors strengthen the OpenFOAM transfer study with more tasks, multiple seeds, or a fuller Foam-Agent execute-mode comparison? If not feasible, the claims about transfer should remain explicitly qualitative.
4. Can the human baseline be reframed more conservatively or expanded? n=2 on one task does not support broad claims about expert-human time savings.

### Limitations assessment

Mostly yes. The authors are transparent about several limitations: structural rather than physical scoring, small OpenFOAM scale, single-seed cross-model runs, the constrained Foam-Agent comparison, and the S/X confound. **Would still like the limitations section to more directly state that the current evidence supports structural authoring reliability, not validated simulator correctness.**

---

## Reviewer kEdh — Rating 2 (Reject), Confidence 4

*23 Jun 2026*

### Summary

This paper introduces Simulator-Interface Grounding Adapters (SIGA), a set of add-on tools wrapped around the AI coding assistant Claude Code to help it automatically generate configuration files for complex scientific simulators. The researchers tested SIGA on GEOS, a simulator used for underground CO₂ storage and earthquake research, adding four components: a documentation search tool (R), a verification checkpoint (S), an on-demand file validator (X), and a memory cheat sheet (M). On simple tasks the AI already performed well without any add-ons, but on harder multi-physics tasks the best SIGA combinations improved output quality by about 7% and made results roughly 40 times more consistent by preventing the AI from producing broken or empty files. The AI completed tasks in about 5–7 minutes compared to 30 minutes to 3 hours for human experts. The same approach also worked on a different simulator (OpenFOAM), suggesting it generalizes beyond a single tool.

Limitations are that it still struggled with fine-grained detail errors that none of the add-ons could fix.

### Strengths

- Useful real-world application, given the promise of agentic interfaces to make legacy applications and repositories accessible to a wider range of scientists.
- Worth noting that the authors tested the same approach on a different simulator (OpenFOAM) and got similar results, suggesting the method isn't limited to just one tool.
- Presents a practical system. Key takeaway: adding simple verification checkpoints to an AI coding agent significantly reduces failures on difficult scientific tasks, without retraining the AI itself.

### Weaknesses

> "While the contributions of this paper are useful, this paper is not written well and practitioners will struggle to understand it and apply its findings in practice."

Concrete suggestions:

1. The driving example is "a Resolution-IV 2^(4−1) factorial". Another application appears to be "buckleyLeverettProblem". **A brief explanation of what these are is needed**, else none of the narrative that follows will be understood.
2. Wording such as *"The number of strictly perfect decks does not increase under any adapter"* must be clarified. Section 3 does explain what a "deck" is, but **this comes too late in the narrative**. Sentences such as *"Headline numbers average TreeSim under failures-as-zero: parse errors, timeouts, failed_no_outputs, and missing XML outputs all score 0, so systems are not rewarded for unscorable files"* will not make sense to most readers.
3. **Provide simple examples** of concepts like "briefs", "structured repair feedback".
4. *[Program committee's call]* Not sure NeurIPS is the right target for this work. A venue such as eScience may be better.

### Questions

> "This paper needs to be significantly re-written. Also, it may be better directed to a scientific conference such as eScience rather than to NeurIPS."

### Limitations assessment

Limitations are discussed.

---

## Reviewer nBNe — Rating 5 (Accept), Confidence 5

*21 Jun 2026*

### Summary

The authors ask whether a general coding agent, such as Claude Code, can become more useful in a scientific simulation setup by introducing a simulator-specific grounding layer. The framework is SIGA: Simulator Interface Grounding Adapter, mainly evaluated on GEOS, an open-source multiphysics simulator. SIGA has four components: Retrieval plugin, Stop hook self-verification, Agent-callable XML validator, and Memory cheatsheet. SIGA reduces across-seed variance roughly 40× and improves quality, raising mean structural similarity by around 7%. The human-baseline comparison shows it reaches comparable quality to a domain expert new to GEOS in minutes rather than hours. Transfer studies on OpenFOAM show the method generalises, although the most useful component depends on the simulator itself.

### Strengths

1. Realistic and useful target for the coding agent — setting up an interface rather than generic reasoning. Very useful in the context of how AI for science is evolving.
2. Well constructed and technically sound: clear motivation, method, experiments and analysis.
3. The framework reduces complete failures.
4. The **cross-simulator transfer seems like a major strength** — SIGA reads as a generalized interface-grounding framework rather than just GEOS-specific.
5. The human baseline is a good calibration point — it shows that even domain experts new to a simulator can spend substantial time learning the interface.

### Weaknesses

1. The paper does not introduce a fundamentally new agent architecture; it is based on existing ideas and the method depends on existing simulator structure.
2. TreeSim is good for structural similarity, but **scientific simulations need numerical stability and physically meaningful output**.
3. The human baseline, although a strength, seems a bit weak. A stronger baseline would include multiple tasks as well as **different levels of GEOS user experience, from beginners to experts**.
4. The task set is relatively small. The paper would be much stronger with a **larger benchmark with more diverse task types**; this would also strengthen the statistical conclusions.

### Questions

1. Adding **convergence checks and output validation from the simulator** may strengthen the claim of the paper.
2. Adding **different levels of human expertise** and also a **human-agent collaborative setting** in the baseline would make the paper better, as practitioners are likely to use such systems interactively.
3. The authors should report the **exact Claude Code version**, since results may depend on both the underlying model and the coding agent environment.

### Limitations assessment

Yes.

---

## Cross-Reviewer Issue Map

| Issue | gep1 | kEdh | nBNe | AC |
|---|:--:|:--:|:--:|:--:|
| Execution / physics validity beyond TreeSim | ✅ (score-moving) | — | ✅ | ✅ (primary) |
| Writing clarity / jargon for general NeurIPS audience | — | ✅ (primary) | — | ✅ |
| Small task set / few seeds | ✅ | — | ✅ | ✅ |
| Human baseline too small (n=2, 1 task) | ✅ | — | ✅ | ✅ |
| OpenFOAM transfer under-powered | ✅ | (cited as strength) | (cited as strength) | ✅ |
| S/X confound not isolated | ✅ (score-moving) | — | — | — |
| Native-plugin-prefix bug contamination | ✅ (score-moving) | — | — | — |
| Limitations should say "structural, not validated correctness" | ✅ | — | — | — |
| Report exact Claude Code version | — | — | ✅ | — |
| Venue fit (eScience vs NeurIPS) | — | ✅ | — | — |
| No new architecture / incremental | — | — | ✅ (minor) | — |
