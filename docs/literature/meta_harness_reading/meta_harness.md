**Meta-harness: End to End Optimization of Model harnesses**
#paper #harness #self_evolving
https://arxiv.org/pdf/2603.28052
Authors: Yoonho Lee, Roshen Nair, Qizheng Zhang, Kangwook Lee, Omar Khattab, Chelsea Finn
Groups: Stanford, KRAFTON, MIT
30 Mar 2026

---

@@@ Personal Notes

### Abstract
Background
- LLM performance depends on model weights but also their harness
- harness definition: code determining: information to store, retrieve and present to the model

Limitations/Gap
- harnesses are still designed largely by hand
- existing text optimizers are poorly matched because they compress feedback too aggressively
	- memoryless
	- condition only on scalar scores
	- restrict feedback to short templates or summaries

Method
- meta-harness: outer loop system that searches over harness code for LLM applications
- agentic proposer accessing source code, scores, and execution traces of all prior candidates through a filesystem

Results
- online text classification: improves over SOTA context management by 7.7pt, 4x fewer context tokens
- RA-math: improves IMO problems by 4.7pp on 5 held-out models
- agentic coding: exceed top hand engineered

External Comparisons
- TTT-Discover
- OpenEvolve
- ACE

### Intro
Changing the harness around fixed LM can produce 6x performance gap
- harness engineering: practice of redefining code around an LLM to improve overall system performance

Comparison of text optimization methods and settings
- OPPRO: relies on past (solution, score) pairs
- TextGrad: textual feedback on current artifact
- AlphaEvolve: program database + eval scores
- GEPA: reflective feedback from rollout traces
- Feedback Descent: comparison + textual feedback
- TTT-Discover: prev solution fragment
MH paper compares MTok/iter: best estimate of full context generated from one evaluation of a text artifact in original paper; MH authors claim MH considers settings yielding OOM more context per artifact evaluation

Text Optimization as starting point
- shares DNA of iterative improvement of text and code artifacts

Problems with previous methods for Harness Engineering
- previous limits
	- short horizon, heavily compressed feedback
	- some condition only on the current candidate
	- other rely primarily on scalar scores
	- other restrict feedback to short templates or LLM generated summaries
		- for scalability; not that more context is not useful
- harness act over long horizons
	- single choices about storage, retrieval, presentation affects behaviour
	- compressed feedback removes information needed to trace downstream failures
	- available context at optimization step ranges from 100 to 30k tokens
- Meta-Harness: agentic harness for optimizing harnesses via E2E search
	- proposer: coding agent: LM based system invoking developer tools and modify code
	- using a coding agent matters because amount of experience quickly exceeds context limits so proposer must decide what to inspect and validate
	- key design choice: expose full history via file system
		- lazy/lossless alternative to compressing as in prior approaches
	- for each previous candidate harness, FS stores source, evaluation, execution traces
		- proposer retrieves using grep/cat rather than single prompt
	- practical observation: proposer reads ~82 files per iteration, referencing over 20 prior candidates per step

### Related Work

- brings idea from broader literature on
	- credit assignment
	- meta-learning
- to new regime enabled by coding agents
- assign credit at harness level
- most related to adaptive access to external context, code search, text optimization

External Memory/Access:
- RAG: Lewis
- interleaved retrieval and reasoning: Interleaved Retrieval with CoT (Trivedi 2023)
- memory based agents: MemGPT (Packer 2023)
- RLM: Zhang 2025
- more demanding setting: harness engineering where you need to optimize the context management procedure itself

Code Search
- code search for functions, workflows, or agent designs
- evolve functions from fixed program scaffolds:
	- Romera-Paredes 2024: math discoveries from PS
- meta agents to program agents
	- Hu 2025: ADAS 
- search workflow graphs for agentic systems
	- Zhang 2025: Aflow: 
- search memory designs for continual-learning:
	- 57: Zhang 2025: MemEvolve
	- 50: Xiong 2026: learning to continually learn via meta-learning agentic memory designs
- Contrast: MH searches over domain specific harnesses
	- prompt, retrieval, state update between tasks
	- outer loop is minimal, fixed scaffold (no archive of prior discoveries or prior persistent memory)
		- proposer gets unrestricted filesystem access to prior experience
		- agent decides what information to inspect
		- enables search over full harness implementation rather than a predefined space of context management

Text Optimization
- ProTeGi, TextGrad, OPRO, GEPA, AlphaEvolve/OpenEvolve, Feedback Descent
	- iterative prompt/text improvmenet from prior attempt feedback
	- optimization targets complete executable procedure and relevant environmental feedback is distributed across code, scores, and execution traces (hard to summarize up front)

### Method
- core idea:
	- harness optimization benefits from full access
		- NOT: lossy summaries, hand-designed search structure
	- is itself a harness: determines what information the proposer model sees
- objective:
	- stateful program wrapping LM determining context visible at each step
	- find the harness that maximizes the expected final reward
- harness constructs prompts for M; harness updates state after each interaction
- multi-objective: candidates evaluated under pareto dominance; report frontier
- MH search loop:
	- single CA proposer with FS D as feedback channel
	- CA: dev tools and edit code
	- instead of hand-designed search loop: delegate diagnosis and proposal to CA
		- which artifacts to inspect, which failure modes to address, whether to make a local edit or substantial rewrite
	- each evaluated harness candidate contributes a directory:
		- contains source code, scores, and execution traces (prompts, tool calls, model outputs, and state updates)
	- FS size >> context window
	- proposer inspects code, scores, traces, then reasons about likely failure modes
- MH maintains population of harnesses and pareto frontier
	- no parent selection rule
	- no hard-coded search heuristics, can improve automatically as coding agents become more capable
- Visibility control:
	- never sees test-set results
	- only feedback from search set: subset of tasks for candidate harness improvement

Algorithm
- initialize file system by evaluating initial population of harnesses
- for each iteration
	- query file system
	- propose k new harnesses
	- validate new candidate interface validity
	- if H passes interface validation, evaluate and add eval artifact to file system

Proposer can often infer why a harness failed and which design choices contributed
- proposer can modify harness at algo level:
	- individual component logic vs. full program rewrites
	- rather than templates/applying predefined mutation operators
- practically: start from a strong prior harness (emergent strategy)
- harness as programs helps regularize: coding models tend to propose algorithms instead of hard coded solutions; bias towards reusable procedures

In Practice:
- harness: single python program
	- prompting, retrieval, memory, orchestration logic
- proposer P: Claude Code with Opus-4.6
- proposer guided by minimal domain specific skill describing 
	- where to write new harnesses
	- how to inspect previous harnesses
	- file modification rules (access policy)

- Practical Tips 
	- new regime of LM-assisted coding
		- proposer conditions on long-horizon histories of prior runs and writes programs with non-obvious/far out consequences 
	- to be reliable, practical choices (engineering lessons):
		- write a good skill:
			- primary interface for steering search
			- quality is strongest lever on whether the loop works
			- proposer receives a NL skill defining its role, directory layout, CLI commands, and output format
			- constrain outputs, safety-relevant behaviour
			- not diagnosis procedure
			- what is forbidden, what artifacts to produce, what objectives to optimize, leave model free to inspect scores, traces, and prior code
			- intuition: accumulated traces often shape proposer behavior more than the skill itself
			- iterating on skill text had larger effect on search quality than changing iteration count or population size
			- 3-5 iteration evolution runs to debug/refine the skill
		- start with baseline harness and hard search set:
			- write a simple baseline (FS), construct the search set by either filtering for hard/diverse subset
			- saturating evaluation already leaves little optimization room
			- size: small enough for ~50 full evals per run (50-100 examples cls,): fast discrim eval is more valuable than large one
		- log everything in navigable formats
			- eval code should write code, scores, and traces in form that's easy to query
			- machine readable formats: JSON
			- hierarchical artifact organization
		- logs queryable with small CLI
			- raw FS access becomes cumbersome
			- short CLI listing pareto frontier, showing top-k harnesses, diffs code/results between pairs of runs can make the experience store easier to use
			- relevant offline experience exists?
				- kinds
					- rollouts from other models
					- solved problem corpora
					- relevant papers
				- convert into same directory format to warm-start exploration
		- lightweight validation
			- small validation test that imports module, instantiates the class, calls both methods on a tiny set of examples
		- automate evaluation outside the proposer
			- simple enough to not make the proposer do it
			- separate harness to score candidates and write results to file system

### Experiments
- domains:
	- online text classification: receives labeled examples one at a time, evaluated on held-out test set
		- Law: LawBench
		- Medicine: Symptom2Disease
		- Chemistry: USPTO: precursor reactant from product molecules
	- math reasoning
	- agentic coding
- baselines:
	- human designed strategies: hand-crafted harnesses
	- program search methods: search over candidate harnesses using feedback and reward signals
		- Best of N: independent samples with no search structure
		- OpenEvolve: evolutionary search over programs with LLM mutation
		- TTT-Discover: text optimization component (proposal selection via PUCT reuse rule)

- text classification results:
	- matches best prior optimizers in 0.1x evaluations
	- final accuracy wins
	- attributed speedup to: full experience access instad of more structured/limited proposer inputs
	- wins against MCE and ACE
		- find that MCE only wins against ACE for S2D dataset, loses on chem, law
		- ACE does have 50k extra tokens, MCE: 29, MH: 11.4
	- discovered harness wins on most OOD datasets
		- only loses to ACE on FiNER, FPB and FS on Bank, SCiT; better on average

- ablation:
	- ablate information available to proposer
	- full -> no trace but summary -> no trace, no summary
	- 50 -> 34.9 -> 34.6
	- raw execution traces is the key ingredient


- RA math results 
	- slightly non-standard
	- retrieval is non-standard in math setting, suggesting that naive retrieval rarely surfaces the right traces and success depends on discovering the right retrieval policy
	- retrieval corpus, 500K solved problems
	- results: 
		- comparisons: dense retriever, random FS, BM25
		- random FS is inconsistent and negative on average
		- BM25 always helps
		- Dense has inconsistent improvement (better average)
		- MH wins
	- MH discovered system:
		- BM 25 lexical retrieval stack

- TerminalBench 2
	- evaluate LLM agents on 89 tasks
	- public writeups describe repeated benchmark specific harness iteration
	- small and expensive enough that introducing a separate split would materially weaken the search signal
	- check for overfitting with manual inspection, task string leakage
	- result:
		- 2nd with Opus 4.6, best with Haiku 4.5
	- qualitative:
		- early iteration: combine plausible structural fixes and prompt template edits
		- observed both candidates regressed
		- hypothesized that regression are confounded by prompt intervention, isolated structural change and pivoted to safer additive modification
		- **evidence proposer can inspect prior experiences to form causal hypotheses and revise accordingly**

Discussion
- practical advantages:
	- discovered harnesses generalize to OOD datasets, unseen base models
	- search run completes in few hours
	- interpretable outputs/artifacts
		- overfitting is visible in code (not in weights)
- main advantage of MH:
	- not code search, but search with access to prior diagnostic experience
- reflective of the bitter lesson
- next:
	- co-evolve harness and model weights


@@@ GPT-5
## **Summary**

_Meta-Harness_ proposes an automated framework for “harness engineering”: optimizing the code around an LLM rather than the model weights themselves. The paper argues that LLM performance depends heavily on the surrounding harness — memory management, retrieval logic, prompt construction, orchestration, and context handling — yet these systems are still mostly engineered manually.

The central idea is to search directly over executable harness code using an agentic coding system that has access to the full history of prior attempts, including:

- source code,
- execution traces,
- evaluation scores,
- prompts and outputs.

Instead of compressing experience into scalar rewards or short summaries, Meta-Harness exposes all prior artifacts through a filesystem interface that the coding agent can inspect selectively.  

The paper evaluates this idea on:

1. online text classification,
2. retrieval-augmented mathematical reasoning,
3. agentic coding on TerminalBench-2.

Across all three domains, Meta-Harness discovers harnesses that outperform prior hand-engineered systems and prior text-optimization approaches.  

## **Main Contributions**

The paper’s primary contributions are:

### **1. A new formulation: harness optimization as code-space search**

The paper frames “harness engineering” as a search problem over executable programs that determine:

- what context is stored,
- how retrieval happens,
- what is shown to the model,
- how state evolves over time.  

Unlike prompt optimization, the optimization target is a full stateful program.

### **2. Meta-Harness: an agentic outer-loop optimizer**

The proposed system:

- repeatedly proposes harnesses,
- evaluates them,
- stores all artifacts in a filesystem,
- lets the proposer inspect arbitrary prior runs.  

A key design choice is that the proposer is a coding agent rather than a plain LLM prompt-completion system.

### **3. Full-history diagnostic access**

The paper argues existing text optimizers compress feedback too aggressively:

- scalar rewards,
- summaries,
- fixed templates,
- short windows.  

Meta-Harness instead gives unrestricted access to:

- raw traces,
- failed examples,
- prior code,
- execution logs.

The authors claim this enables causal diagnosis of failures.

### **4. Strong empirical results across diverse domains**

The system improves over:

- hand-designed context engineering systems,
- prior text optimization methods,
- strong coding-agent harnesses.  

### **5. Evidence that execution traces matter**

Ablation studies show that:

- scores-only optimization,
- scores + summaries,

perform substantially worse than access to full traces.  

This is one of the paper’s strongest empirical findings.

## **Methodology**

## **Problem Setup**

A harness H is defined as a stateful program wrapped around a frozen LLM M. The harness controls:

- prompting,
- retrieval,
- memory,
- orchestration,
- state updates.  

The optimization objective is:

H^* = \arg\max_H \mathbb{E}_{x,\tau}[r(\tau, x)]

where:

- x is a task,
- \tau is the rollout trajectory,
- r is a task-specific reward.  

## **Search Loop**

The Meta-Harness loop is:

1. Start with an initial population of harnesses.
2. Evaluate them.
3. Store:
    
    - code,
    - traces,
    - scores  
        into a filesystem.
4. A coding agent proposes new harnesses by reading the filesystem.
5. Evaluate the new harnesses.
6. Repeat.  

The proposer:

- uses terminal tools (`grep`, `cat`, etc.),
- selectively retrieves information,
- edits harness code directly.  

In experiments:

- proposer = Claude Code with Opus-4.6,
- harnesses = single-file Python programs.  

## **Key Design Philosophy**

The outer loop is intentionally minimal.

The authors explicitly avoid:

- hard-coded mutation operators,
- parent selection heuristics,
- predefined workflow graphs,
- compressed memory summaries.  

Instead, the coding agent itself decides:

- what failures matter,
- which prior harnesses to inspect,
- what edits to make.

The paper positions this as “search with selective access to diagnostic experience.”  

## **Tasks and Experimental Results**

## **1. Online Text Classification**

### **Setup**

Tasks:

- LawBench,
- Symptom2Disease,
- USPTO-50k.  

Base classifier:

- GPT-OSS-120B.  

Baselines:

- zero-shot,
- few-shot,
- ACE,
- MCE,
- OpenEvolve,
- TTT-Discover,
- GEPA,
- Best-of-N.  

### **Main Results**

Meta-Harness achieves:

- 48.6% average accuracy,
- compared to:
    - ACE: 40.9%,
    - MCE: 40.0%.  

Importantly, it uses much less context:

- Meta-Harness: 11.4K tokens,
- ACE: 50.8K,
- MCE: 28.5K.  

The paper emphasizes that gains are not due to larger prompts.

### **Comparison to Prior Text Optimizers**

Meta-Harness:

- reaches OpenEvolve/TTT-Discover performance after only ~4 evaluations,
- ultimately exceeds them by >10 points.  

Search-set accuracies:

- GEPA: best 40.2,
- OpenEvolve: best 43.3,
- TTT-Discover: best 45.6,
- Meta-Harness: best 56.7.  

### **OOD Generalization**

On 9 unseen classification datasets:

- Meta-Harness: 73.1%,
- ACE: 70.2%,
- Few-shot(32): 69.6%.  

The discovered harness generalizes reasonably well beyond the search datasets.

## **2. Retrieval-Augmented Math Reasoning**

### **Setup**

Goal:  
optimize retrieval policies for Olympiad-level math solving.  

Corpus:

- 500k solved problems,
- deduplicated against evaluation tasks.  

Search:

- 250 hard Olympiad problems,
- 109 candidate retrieval harnesses.  

Evaluation:  
200 held-out IMO-level problems using:

- GPT-OSS-20B,
- GPT-5.4-nano,
- GPT-5.4-mini,
- Gemini-3.1-Flash-Lite,
- Gemini-3-Flash.  

### **Results**

Average accuracies:

- No retrieval: 34.1,
- Dense retrieval (k=5): 38.1,
- BM25: 37.5,
- Meta-Harness: 38.8.  

Average improvement over no retrieval:

- +4.7 points.  

Notably:

- the same discovered retrieval harness transfers across unseen models,
- without retraining.  

## **3. Agentic Coding on TerminalBench-2**

### **Setup**

Benchmark:

- TerminalBench-2,
- 89 difficult long-horizon coding tasks.  

Initial harnesses:

- Terminus-2,
- Terminus-KIRA.  

Models:

- Claude Opus 4.6,
- Claude Haiku 4.5.  

### **Results**

For Opus 4.6:

- Meta-Harness: 76.4%,
- Terminus-KIRA: 74.7%.  

For Haiku 4.5:

- Meta-Harness: 37.6%,
- Goose: 35.5%,
- Terminus-KIRA: 33.7%.  

The paper claims:

- #2 Opus-4.6 agent,
- #1 Haiku-4.5 agent on the leaderboard.  

## **Main Takeaways from Analysis and Discussion**

## **1. Full execution traces are the crucial ingredient**

The strongest ablation result is:

|**Method**|**Median**|**Best**|
|---|---|---|
|Scores only|34.6|41.3|
|Scores + summaries|34.9|38.7|
|Full Meta-Harness|50.0|56.7|

This strongly supports the paper’s central claim:  
compressed summaries lose critical diagnostic information.

The authors argue:

- failures are long-horizon,
- causal structure is distributed across traces,
- summaries destroy attribution information.  

## **2. The proposer performs causal reasoning over failures**

One particularly interesting qualitative analysis shows the proposer:

- observes regressions,
- notices confounded edits,
- isolates shared causes,
- re-tests hypotheses.  

The paper presents this as evidence that:

- filesystem access enables deeper diagnosis,
- rather than shallow mutation search.

This is arguably the most novel conceptual contribution.

## **3. Search trajectories are highly non-Markovian**

The proposer:

- reads a median of 82 files/iteration,
- references many prior candidates,
- inspects both code and traces extensively.  

The authors use this to argue that:

- local-history optimization is insufficient,
- useful optimization requires broad historical access.

## **4. Harness engineering may become increasingly automated**

The discussion explicitly invokes Sutton’s “Bitter Lesson”:  
once search becomes feasible, general-purpose search may outperform hand-engineering.  

The paper suggests:

- stronger coding agents may naturally improve harness search,
- without redesigning the outer loop.

## **5. The discovered harnesses appear transferable**

The paper emphasizes transfer across:

- unseen datasets,
- unseen base models,
- different operating points.  

This is important because it suggests the system is not merely overfitting benchmark artifacts.

## **Limitations / Critical Perspective**

The paper does acknowledge several caveats implicitly:

### **Heavy reliance on a very strong proposer**

The system depends heavily on:

- Claude Code,
- Opus-4.6-level coding ability.  

It is unclear how well weaker agents would perform.

### **Computational cost**

Although framed as practical, the approach can generate:

- millions of tokens of traces,
- many harness evaluations,
- substantial infrastructure overhead.  

### **Benchmark specialization risk**

TerminalBench search/evaluation are performed on the same benchmark split.  

The authors justify this as standard practice, but it still raises concerns about benchmark-specific optimization.

### **Limited theoretical grounding**

The paper is largely empirical/system-oriented:

- little theory,
- no formal credit assignment analysis,
- no guarantees about scalability or convergence.

## **Overall Interpretation**

The paper’s central insight is not merely “search over prompts,” but:

give a coding agent unrestricted access to rich historical diagnostic information and let it reason over failures in code space.

That is the conceptual leap beyond prior text optimization methods.

The empirical evidence suggests:

- harness quality matters enormously,
- execution traces are much more informative than compressed feedback,
- coding-agent-driven outer loops can outperform carefully hand-designed harnesses.

This paper is likely to matter because it reframes:

- prompt engineering,
- context engineering,
- retrieval design,
- agent orchestration

as a unified search problem over executable systems rather than static prompts.
