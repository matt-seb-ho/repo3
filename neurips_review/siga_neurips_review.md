#### Meta Review of Submission31642 by Area Chair GKRj

Meta Reviewby Area Chair GKRj23 Jul 2026, 01:07 (modified: 23 Jul 2026, 11:32)Senior Area Chairs, Area Chairs, Authors, Reviewers Submitted, Program Chairs, Area Chair GKRj[Revisions](https://openreview.net/revisions?id=gdKoS2wwyx)

**Metareview:**

The paper proposes SIGA, a simulator-interface grounding adapter for improving the reliability of general-purpose coding agents when generating scientific simulator configurations. The reviewers agree that the problem is practically important and view the systematic component analysis, reduction in catastrophic failures, and preliminary transfer to OpenFOAM positively. However, the ratings are divergent, with accept, borderline accept, and reject scores. At this stage, the main obstacles to acceptance are:

- The evaluation primarily measures structural similarity using TreeSim, rather than whether the generated configurations execute successfully, converge, or produce physically meaningful simulations (gep1, nBNe). A small execution-based evaluation would substantially strengthen the central claim that SIGA improves simulator reliability rather than only configuration structure.
- Reviewer kEdh, also found several key concepts and evaluation choices difficult to follow and a bit jargony. I see the same issue with the writing of the paper, as in its current state, it would be hard for a NeurIPS reader to fully understand many things in the paper.
- The experimental scale is limited (gep1, nBNe). The main hard-task evaluation uses only ten tasks and three seeds, while the OpenFOAM transfer experiment uses five tasks and a single seed. The rebuttal should clarify the representativeness of these tasks, provide uncertainty estimates where possible, and moderate the robustness and generalization claims if additional evaluation is unavailable.
- The human comparison is too small to support broad efficiency claims (gep1, nBNe). Two participants on one task are useful as preliminary calibration, but the claims should either be narrowed or better contextualized.

The decision will likely depend on whether the rebuttal can establish that the structural improvements translate to executable and scientifically valid simulations and whether the authors can put significant efforts towards improving the clarity of the paper towards general NeurIPS audience. At present, I view the paper as borderline.

Add:

#### Official Review of Submission31642 by Reviewer gep1

Official Reviewby Reviewer gep126 Jun 2026, 00:55 (modified: 23 Jul 2026, 09:52)Program Chairs, Senior Area Chairs, Area Chairs, Reviewers Submitted, Authors, Reviewer gep1[Revisions](https://openreview.net/revisions?id=89MxR8MK1m)

**Summary:**

Paper studies how to adapt a general-purpose LLM coding harness for scientific simulator setup, focusing on GEOS XML deck authoring. It proposes Simulator-Interface Grounding Adapters (SIGA): retrieval over documentation/schema/examples, stop-hook verification, an agent-callable XML validator, and an always-on memory cheatsheet. The paper contributes a GEOS deck-authoring benchmark, a TreeSim structural-similarity metric, a Resolution-IV factorial study over adapter components, a self-evolved adapter variant, a small human-baseline study, and a small OpenFOAM transfer study. The main finding is that SIGA does not uniformly improve already-good outputs, but reduces catastrophic failures on harder compound multiphysics tasks, especially through forced end-of-turn verification. The bottleneck analysis further shows that adapters help with missing whole blocks but do not solve attribute-level or semantic simulator errors.

**Contribution Type:** Use-inspired: The main contribution is in framing or designing approaches to meet the needs of a specific real-world application. (This often involves, e.g., engaging with domain experts.)

**Strengths And Weaknesses:**

This is a useful and well-motivated paper. The problem setting is concrete, and the authors make a convincing case that simulator setup is an important bottleneck for scientific agents. I especially appreciate that the work studies wrapper-level grounding around an existing coding harness rather than proposing an entirely new agent stack. The factorial design is a strength: it gives more insight than a single “our system vs baseline” comparison, and the bottleneck analysis makes the results more informative by showing which errors are actually being addressed.

The strongest empirical result is the reliability improvement on the harder held-out GEOS tasks. The paper is careful in explaining that the adapter mainly prevents catastrophic failures such as empty, missing, or unparseable decks, rather than improving the ceiling of already-good outputs. This is an important distinction and makes the contribution more credible. The negative findings are also valuable: retrieval can hurt, memory exposed as a retrievable tool may not be used, and human-consultation tools may be bypassed when an example library is available.

The main weakness is that the evaluation is still mostly structural. TreeSim is appropriate as a scalable first metric, but it does not establish that generated decks run successfully in GEOS or produce physically meaningful simulations. This limits the strength of the practical claims. The authors acknowledge this, but the central usefulness of the system would be much stronger with even a small runnability/physics-validity ladder.

The second weakness is statistical and experimental scale. The main GEOS results use n=3 seeds and only 10 harder held-out tasks. The OpenFOAM transfer study is useful as a sanity check, but it is only 5 tasks, single-seed, and uses a constrained lint-only Foam-Agent baseline. The human baseline is also only n=2 on one relatively easy task, so it should be interpreted as anecdotal calibration rather than strong evidence about human-vs-agent performance.

There are also some methodological confounds. The S and X components both involve validation, so the individual role of stop-hook enforcement versus validator availability is not fully isolated. The paper also reports a native-plugin-prefix bug that contaminated some estimates involving retrieval.

Originality is good but not in the form of a new model or algorithm. The novelty is in the benchmark, the adapter framing, the component-wise evaluation, and the detailed analysis of failure modes in scientific simulator authoring. Significance is also good, especially for scientific-agent work, but the impact depends on whether the structural reliability gains translate to executable and scientifically valid simulations.

**Quality:** 3: good

**Clarity:** 3: good

**Significance:** 3: good

**Originality:** 3: good

**Questions:**

Can the authors add a small GEOS execution-based evaluation? Even 5 tasks across Vanilla and the best SIGA cell would help establish whether TreeSim gains correspond to runnable decks. My score would increase if the reliability gains persist under execution or physical-validity checks.

Can the authors rerun the cells affected by the native-plugin-prefix bug and more cleanly separate S from X? My confidence would increase if the stop-hook effect remains dominant after removing this confound.

Can the authors strengthen the OpenFOAM transfer study with more tasks, multiple seeds, or a fuller Foam-Agent execute-mode comparison? If this is not feasible, the claims about transfer should remain explicitly qualitative.

Can the human baseline be reframed more conservatively or expanded? The current study is informative, but n=2 on one task does not support broad claims about expert-human time savings.

**Limitations:**

Mostly yes. The authors are transparent about several limitations: structural rather than physical scoring, small OpenFOAM scale, single-seed cross-model runs, the constrained Foam-Agent comparison, and the S/X confound. I would still like the limitations section to more directly state that the current evidence supports structural authoring reliability, not validated simulator correctness.

**Rating:** 4: Borderline accept: Technically solid paper where reasons to accept outweigh reasons to reject, e.g., limited evaluation. Please use sparingly.

**Confidence:** 3: You are fairly confident in your assessment. It is possible that you did not understand some parts of the submission or that you are unfamiliar with some pieces of related work. Math/other details were not carefully checked.

**Ethical Concerns:** NO or VERY MINOR ethics concerns only

**Paper Formatting Concerns:**

No comments on the visible formatting of the main manuscript

**Code Of Conduct Acknowledgement:** Yes

**Responsible Reviewing Acknowledgement:** Yes

Add:

#### Official Review of Submission31642 by Reviewer kEdh

Official Reviewby Reviewer kEdh23 Jun 2026, 13:04 (modified: 23 Jul 2026, 09:52)Program Chairs, Senior Area Chairs, Area Chairs, Reviewers Submitted, Authors, Reviewer kEdh[Revisions](https://openreview.net/revisions?id=N17AUwgl9b)

**Summary:**

This paper introduces Simulator-Interface Grounding Adapters (SIGA), a set of add-on tools wrapped around the AI coding assistant Claude Code to help it automatically generate configuration files for complex scientific simulators. The researchers tested SIGA on GEOS, a simulator used for underground CO₂ storage and earthquake research, adding four components: a documentation search tool (R), a verification checkpoint (S), an on-demand file validator (X), and a memory cheat sheet (M). On simple tasks the AI already performed well without any add-ons, but on harder multi-physics tasks the best SIGA combinations improved output quality by about 7% and made results roughly 40 times more consistent by preventing the AI from producing broken or empty files. The AI completed tasks in about 5–7 minutes compared to 30 minutes to 3 hours for human experts. The same approach also worked on a different simulator (OpenFOAM), suggesting it generalizes beyond a single tool.

Limitations are that it still struggled with fine-grained detail errors that none of the add-ons could fix.

**Contribution Type:** Use-inspired: The main contribution is in framing or designing approaches to meet the needs of a specific real-world application. (This often involves, e.g., engaging with domain experts.)

**Strengths And Weaknesses:**

Strengths: This is work that has useful real-world application, given the promise of agentic interfaces to make legacy applications and repositories accessible to a wider range of scientists. It was worth noting that the authors tested the same approach on a different simulator called OpenFOAM and got similar results, suggesting the method isn’t limited to just one tool. This submission presents a practical system. The key takeaway is that adding simple verification checkpoints to an AI coding agent significantly reduces failures on difficult scientific tasks, without needing to retrain the AI itself.

Weaknesses: However, while the contributions of this paper are useful, this paper is not written well and practitioners will struggle to understand it and apply its findings in practice. Below are concrete suggestions for improvement:

1. The driving example is "a Resolution-IV 24−1 factorial". Another application appears to be "buckleyLeverettProblem". A brief explanation of what these are is needed, else none of the narrative that follows will be understood.
    
2. Wording such as "The number of strictly perfect decks does not increase under any adapter." must be clarified. Section 3 does explain what a "deck" is, but this comes too late in the narrative. Sentenses such as "Headline numbers average TreeSim under failures-as-zero: parse errors, timeouts, failed_no_outputs, and missing XML outputs all score 0, so systems are not rewarded for unscorable files" will not make sense to most readers.
    
3. Provide simple examples of concepts like "briefs", "structured repair feedback"
    
4. This is the program committee's call, but not sure that Neurips is the right target for this work. A venue such as eScience may be better.
    

**Quality:** 2: not good

**Clarity:** 2: not good

**Significance:** 3: good

**Originality:** 3: good

**Questions:**

This paper needs to be significantly re-written. Also, it may be better directed to a scientific conference such as eScience rather than to Neurips.

**Limitations:**

Limitations are discussed.

**Rating:** 2: Reject: For instance, a paper with technical flaws, weak evaluation, inadequate reproducibility and incompletely addressed ethical considerations.

**Confidence:** 4: You are confident in your assessment, but not absolutely certain. It is unlikely, but not impossible, that you did not understand some parts of the submission or that you are unfamiliar with some pieces of related work.

**Ethical Concerns:** NO or VERY MINOR ethics concerns only

**Paper Formatting Concerns:**

N/A

**Code Of Conduct Acknowledgement:** Yes

**Responsible Reviewing Acknowledgement:** Yes

Add:

#### Official Review of Submission31642 by Reviewer nBNe

Official Reviewby Reviewer nBNe21 Jun 2026, 20:21 (modified: 23 Jul 2026, 09:52)Program Chairs, Senior Area Chairs, Area Chairs, Reviewers Submitted, Authors, Reviewer nBNe[Revisions](https://openreview.net/revisions?id=4GYHpsWQiF)

**Summary:**

In this work, the authors have tried to answer the question if a general coding agent, such as Claude code, can become more useful in a scientific simulation setup by introducing a simulator-specific grounding layer. The authors call their framework SIGA: Simulator Interface Grounding Adapter. The authors have mainly evaluated their method on GEOS, an open-source multiphysics simulator. The SIGA has four components: Retrieval plugin, Stop hook self-verification, Agent callable XML validator and Memory cheatsheet. The authors have shown that SIGA reduces across seed variance roughly by 40 times and improves the quality, raising mean structural similarity by around 7 per cent. They also compare their framework with a human baseline, where they show it reaches comparable quality to a domain expert new to GEOS in minutes rather than hours. Moreover, the author has shown transfer studies on OpenFoam to show that the proposed method generalises, although the most useful component depends on the simulator itself.

**Contribution Type:** Use-inspired: The main contribution is in framing or designing approaches to meet the needs of a specific real-world application. (This often involves, e.g., engaging with domain experts.)

**Strengths And Weaknesses:**

Strength i) The authors have shown a realistic and useful target for the coding agent to set up as an interface rather than generic reasoning. This is very useful in the context of how AI for science is evolving. ii) The paper is well constructed and technically sound. It presents a clear motivation, method, experiments and analysis. iii) Also one of the good points about the paper is the fact that framework is that it reduces complete failures. iv) The cross-simulator transfer shown in the paper seems like a major strength. So the framework presented by the authors seems more like an interface grounding generalized framework rather than just GEOS-specific. v) The human baseline presented in the paper is a good calibration point. It shows the fact that even domain experts who are new to a simulator can spend a substantial amount of time learning the interface.

Weakness: i) The paper does not introduce a fundamentally new agent architecture and are based on existing ideas and the method depends on existing simulator structure ii) The authors have used TreeSim for scores to evaluate. TreeSim is good for structural similarity, but scientific simulations need numerical stability and physically meaningful output. iii) The human baseline, although a strength, seems a bit weak. A stronger baseline may include multiple tasks as well as different levels of experience GEOS users from beginners to experts. This might even improve the generalizability of use case. iv)The task set seems relatively small. The paper would be much stronger with a larger benchmark with more diverse task types. Also, this would make the statistical conclusions stronger.

**Quality:** 3: good

**Clarity:** 3: good

**Significance:** 4: excellent

**Originality:** 3: good

**Questions:**

i) Adding convergence checks and output validation from the simulator may strengthen the claim of the paper.

ii) Adding different levels of human expertise and also a human-agent collaborative setting in the baseline would make the paper better, as practitioners are likely to use such systems interactively.

iii) The authors should also report the exact Claude code verison, since the result may depend on both the underlying model and the coding agent environment.

**Limitations:**

Yes.

**Rating:** 5: Accept: Technically solid paper, with high potential value on at least one sub-area of AI or moderate-to-high impact on more than one area of AI, with good-to-excellent evaluation, resources, reproducibility, and no unaddressed ethical considerations.

**Confidence:** 5: You are absolutely certain about your assessment. You are very familiar with the related work and checked the math/other details carefully.

**Ethical Concerns:** NO or VERY MINOR ethics concerns only

**Paper Formatting Concerns:**

N.A.

**Code Of Conduct Acknowledgement:** Yes

**Responsible Reviewing Acknowledgement:** Yes