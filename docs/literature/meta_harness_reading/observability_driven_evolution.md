**Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses**
#paper #agent #coding_agent #self_evolving #harness
Authors: Jiahang Lin, Sichun Liu, Chengjun Pan, ..., Tao Gui
Groups: Fudan Uni, Peking Uni, Shanghai Qiji Zhifeng Co
30 April 2026
https://arxiv.org/pdf/2604.25850
https://github.com/china-qijizhifeng/agentic-harness-engineering

---

@@@ GPT Notes

## **Overview**

This paper introduces **Agentic Harness Engineering (AHE)**, a framework for automatically evolving the _harness_ of coding agents rather than training or fine-tuning the underlying language model. The authors argue that modern coding-agent performance depends heavily on the surrounding infrastructure — prompts, tools, middleware, memory systems, execution policies, and sub-agents — collectively called the _harness_.  

Their core claim is that harness evolution is primarily bottlenecked by **observability**, not by model capability. Existing approaches either:

- optimize only prompts or skills,
- lack structured debugging signals,
- or cannot reliably attribute whether edits improved performance.

AHE addresses this using three forms of observability:

1. **Component observability** — editable harness pieces are exposed as modular files.
2. **Experience observability** — trajectories are distilled into structured evidence.
3. **Decision observability** — every edit carries explicit predictions that are later verified.  

The system autonomously evolves a coding-agent harness over multiple iterations and achieves strong improvements on coding-agent benchmarks.

Source paper:  

## **Main Contributions**

The paper explicitly lists three contributions:

### **1. Formalizing agent-driven harness evolution**

The authors define harness evolution as a first-class optimization problem and propose AHE as a framework for solving it. The key conceptual contribution is framing the problem around _observability_.  

They introduce:

- a decoupled file-level harness substrate,
- a layered trajectory-analysis system,
- and a prediction-verification loop for edits.

### **2. Strong empirical performance**

AHE improves:

- Terminal-Bench 2 pass@1 from **69.7% → 77.0%**
- outperforming:
    - Codex CLI (71.9%)
    - ACE (68.9%)
    - TF-GRPO (72.3%)  

The evolved harness also transfers:

- to SWE-bench-verified,
- and across multiple model families without re-evolution.  

### **3. Analysis of limitations of self-evolution**

The paper studies:

- component interaction effects,
- attribution reliability,
- regression prediction failures,
- and limits of additive improvements.  

A key finding is that the evolution loop can accurately predict fixes, but is poor at predicting regressions.

## **What Is a “Harness”?**

The paper uses _harness_ to mean all model-external infrastructure that shapes agent behavior:

- system prompts,
- tools,
- middleware,
- memory,
- sub-agent orchestration,
- execution policies,
- runtime management.  

The authors argue that harness engineering is becoming increasingly important because:

- coding-agent tasks are long horizon,
- models change rapidly,
- and harnesses are highly model-specific.  

## **Methodology**

## **High-Level Architecture**

AHE is a closed-loop optimization system:

1. Run coding agent on benchmark tasks.
2. Collect trajectories.
3. Distill trajectories into structured evidence.
4. Use an “Evolve Agent” to modify harness components.
5. Evaluate modifications.
6. Attribute improvements/regressions.
7. Repeat.  

The loop is fully autonomous after initialization.

## **Three Observability Pillars**

### **1. Component Observability**

The harness is implemented using the NexAU framework, where every editable component exists as an explicit file:

- system prompts,
- tool descriptions,
- tool implementations,
- middleware,
- skills,
- memory,
- sub-agent configs.  

This gives:

- explicit action space,
- localized edits,
- rollback support,
- git-style diffs,
- better attribution.

The seed harness is intentionally minimal:

- only a bash tool,
- no middleware,
- no memory,
- no skills.  

This is important because the authors want every improvement to emerge from the evolution loop itself.

### **2. Experience Observability**

Raw agent traces are extremely long (millions of tokens), so AHE introduces an “Agent Debugger” that:

- analyzes trajectories,
- groups failures,
- extracts root causes,
- generates per-task reports,
- creates benchmark-level summaries.  

Importantly:

- raw traces are still available,
- but the system primarily consumes distilled evidence.

This is conceptually similar to:

- hierarchical debugging,
- layered retrieval,
- progressive disclosure for agent memory systems.

### **3. Decision Observability**

Every edit made by the Evolve Agent includes:

- target failure pattern,
- root-cause explanation,
- predicted fixes,
- predicted regressions.  

Later iterations compare:

- predicted outcomes,
- versus actual benchmark deltas.

Thus every edit becomes a falsifiable hypothesis.

This is one of the more novel aspects of the paper.

## **Algorithm**

The outer loop contains:

1. rollout generation,
2. trace cleaning,
3. attribution,
4. rollback,
5. debugging/distillation,
6. evolution,
7. git commit/tagging.  

The framework also:

- automatically reverts ineffective edits,
- keeps infrastructure immutable,
- and restricts edits to harness workspace files.

## **Benchmarks and Tasks**

## **Primary Benchmark: Terminal-Bench 2**

Main optimization target:

- 89 tasks
- split into:
    - 4 easy
    - 55 medium
    - 30 hard.  

These are realistic terminal-based coding tasks with long horizons.

## **Transfer Benchmark: SWE-bench-verified**

Secondary evaluation:

- 500 repository-level bug-fixing tasks
- across multiple repositories:
    - django
    - sympy
    - sphinx-doc
    - matplotlib
    - scikit-learn
    - pydata
    - astropy.  

## **Models Used**

Main experiments use:

- GPT-5.4 high reasoning  
    for:
- Code Agent,
- Debugger Agent,
- Evolve Agent.  

Transfer tests evaluate:

- GPT-5.4 medium/xhigh,
- qwen-3.6-plus,
- gemini-3.1-flash-lite,
- deepseek-v4-flash.  

## **Performance Compared to Baselines**

## **Terminal-Bench 2 Results**

|**Method**|**Overall pass@1**|
|---|---|
|opencode|47.2%|
|terminus-2|62.9%|
|Codex CLI|71.9%|
|NexAU0 seed|69.7%|
|ACE|68.9%|
|TF-GRPO|72.3%|
|AHE|**77.0%**|

Important observations:

- AHE beats both human-designed and automated baselines.
- Improvement accumulates across iterations.
- Hard tasks remain challenging.

## **SWE-bench Transfer Results**

AHE transfers surprisingly well:

- highest aggregate success rate,
- lowest token usage,
- no additional evolution required.  

Key result:

- AHE uses ~12% fewer tokens than the seed harness while slightly improving success rate.

This suggests the evolved harness encodes reusable coordination structure rather than benchmark-specific hacks.

## **Cross-Model Transfer**

AHE improves all tested model families:

- GPT-5.4 medium: +2.3 pp
- GPT-5.4 high: +7.3 pp
- GPT-5.4 xhigh: +2.3 pp
- Gemini Flash Lite: +5.1 pp
- DeepSeek V4 Flash: +10.1 pp
- Qwen 3.6+: +6.3 pp.  

The authors interpret this as evidence that:

- weaker models benefit more from harness structure,
- stronger models can internally reconstruct some coordination behaviors.

## **Key Analysis Findings**

## **1. Gains come from tools/middleware/memory — not prompts**

Ablations show:

|**Component Only**|**Pass@1**|
|---|---|
|memory only|75.3%|
|tool only|73.0%|
|middleware only|71.9%|
|system prompt only|67.4%|
|full AHE|77.0%|

This is one of the strongest findings in the paper.

The evolved prompt alone actually _hurts_ performance.

The authors argue:

- factual executable infrastructure transfers,
- prose strategies do not.

This directly challenges the common “prompt engineering” framing.

## **2. Component interactions are non-additive**

The gains from components do not stack linearly:

- memory, middleware, and prompts all encourage re-verification,
- causing redundant work,
- especially on long-horizon tasks.  

Thus:

- local improvements can conflict globally,
- evolution optimizes the aggregate objective,
- and medium-difficulty tasks dominate optimization pressure.

This resembles:

- interference in modular systems,
- non-additive policy composition,
- or optimizer over-specialization.

## **3. The system predicts fixes well but regressions poorly**

The self-attribution mechanism works asymmetrically:

### **Fix prediction**

- precision: 33.7%
- recall: 51.4%

versus random baselines:

- 6.5%
- 10.6%.  

### **Regression prediction**

- precision: 11.8%
- recall: 11.1%

close to random baselines:

- 5.6%
- 5.4%.  

Interpretation:

- the evolution agent can explain improvements,
- but cannot foresee collateral damage.

The authors identify this as a major future research direction.

## **Conceptual Takeaways**

## **1. Harness engineering may become a major scaling axis**

The paper strongly argues that:

- performance improvements need not come from model weights,
- but can come from externalized agent infrastructure.  

This parallels:

- systems engineering,
- compiler optimization,
- OS/runtime evolution,
- or agent architecture search.

## **2. Observability is the key bottleneck**

The authors repeatedly emphasize:

- agents are already capable enough to improve harnesses,
- but lack structured representations of failures and editable surfaces.  

This is the central thesis of the paper.

## **3. Prompt optimization alone is insufficient**

AHE outperforms prompt-centric methods because:

- prompts are not the main load-bearing component,
- executable infrastructure matters more.  

The strongest transferable improvements come from:

- middleware,
- tools,
- long-term memory.

## **4. Self-improvement loops still struggle with regressions**

AHE shows:

- autonomous improvement is possible,
- but stability remains difficult.  

The system can:

- identify local fixes,
- but not reliably reason about downstream side effects.

This resembles challenges in:

- program synthesis,
- automated software repair,
- RL reward hacking,
- continual learning interference.

## **Limitations**

The authors acknowledge several limitations:

### **Benchmark scope**

Only evaluated on:

- Terminal-Bench 2,
- SWE-bench-verified.  

### **Operating-point coupling**

Harnesses evolved under one reasoning budget/time limit may not generalize optimally to others.  

### **Safety/governance**

AHE is still a constrained research prototype:

- workspace-only edits,
- immutable infrastructure,
- rollback support,
- but incomplete safeguards for autonomous self-modification.  

## **Overall Interpretation**

This paper is notable because it shifts focus from:

- “improving the model”  
    to:
- “improving the surrounding agent runtime.”

The strongest ideas are probably:

- treating harnesses as modular editable substrates,
- trajectory distillation for agent debugging,
- and falsifiable edit manifests.

The empirical gains are meaningful, but the conceptual contribution is arguably larger:

- coding-agent capability may increasingly depend on evolving external infrastructure rather than solely model weights.

The paper also implicitly suggests a broader research direction:

- autonomous systems engineering loops,
- where agents iteratively redesign their own execution environment under structured observability constraints.