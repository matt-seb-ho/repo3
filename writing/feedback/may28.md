# abstract

- applying agents to scientific disciplines is important topic, blah blah blah
	- but even before we can consider tackling agents taking on end to end scientific positions we need to consider if agents can reliably use powerful scientific tools
	- interfacing with tools is its own bottleneck for human workflows that should be resolved before setting agents loose
- "we call any wrapper" -> we call this lightweight adaptive approach SIGA
- don't mention resolution 4 factorial in abstract, too hard to understand, just explain we have detailed ablations on these components
- I don' think we need to mention the stop-hook as the dominant factor in the abstract. I think we definitely explain that our method yields in whatever result improvements
- I think we don't explicitly list n=2 for the human baseline. We should mention that they are geoscience domain experts
- "embedding retrievable memory tool" fact is extremely random to include in abstract, let's remove this
- I think the "consult human" tool should have slightly more elaboration in the abstract: we should explain that we explore agent autonomy by varying the task specification level of detail and allow the agent to consult a human supervisor/expert.
- finally have the self-evolved thing explaining that we also show effectiveness of open-ended self-evolution on top of the constrained design space we explore in the main recipe

## intro

paragraph 1: this should introduce the problem
- "the part of simulation campaign that benefits least from general reasoning ability" -> I don't get this line and I'm the one most familiar with this work

paragraph 2: this should explain where the gap lies (where does our work stand in comparison)
- I think from an application perspective the gap is that there just isn't an agent designed for GEOS in particular
- from an AI/method perspective, these prior scientific agent work focus primarily on building a framework from scratch compared to building on top of the engineering efforts of either (a) industry leading engineering teams: e.g. Claude Code or (b) open source community (OpenCode, etc.)
- I think the gap is correct:
	- building on top of existing SOTA harness should still be principled: what are the actual shortcomings of these general coding agents and what specific interventions can resolve them for our class of tasks.

paragraph 3: our work/our method/etc.
- GEOS introduction here is good
- I wonder if we emphasize Claude Code here or later in experiments
- I think we also position the grounding components as ideas that AI literature have proven individually as excellent ideas:
	- semantic (embedding) based retrieval provides an alternative to coding agents' typical agentic search (e.g. find, grep, combing through file tree)
	- self-refinement: this is typically implemented through control loops about getting the LM to self reflect on an answer and prompting it to improve its answer as needed. In the "adapting an existing harness" this mean implementing this control through hooks
	- agentic validation/self-refinement at agent's discretion:
		- while self-refinement is known to work, why only embed validation logic at the workflow's endpoint?  Why not give the agent the ability to actively, intermediately check its work instead of only hearing feedback at the end
	- memory: persistent memory scratch pad is a sample efficient way to save lessons and crucial knowledge from experience.

- we don't need to go into this level of depth in the introduction and maybe this can be saved for the method section
- I think resolution-iv is not standard terminology in AI parlance, let's at least preface it with explaining its an elaborate battery of ablations, etc.

paragraph 4: findings:
- again I don't think love the embedding procedural memory tool thing being brought up here. I just don't view it as a core finding

- let's merge paragraph 5 (intro wrap up) here too 
	- let's mention that the surprising finding is that even in the well-constrained, well-defined version of the task that doesn't demand a lot of scientific reasoning (since we somewhat view this as a busy work task of configuring a simulation according to provided specs) we find that SOTA agents on their own aren't quite sufficient
	- This motivates our work/study and further work/study in improving agentic systems for these workflows.
	- my advisor likes including a surprising finding and some concrete takeaway

# Related Work
- again, seemingly large emphasis on the memory embedding-retrievable items
- I think this worth mentioning in discussion/results/appendix sections (one of these) but this seems to be overrepresented in the writing so far

# Method

- I think starting with "we do not" in the method section is too negative right out the gate.
	- The meaning is still correct, this is a style complaint
	- I think maybe something like "Rather build another ReAct framework, [we do this instead]" could be more positive?
	- I think we can treat this as a boon-- this procedure of adapting an existing harness is a more repeatable action for different domains/target softwares, etc. Doesn't demand maintaining a large code base.
	- The ultimate goal is a fully automatic construction/optimization of this harness and exposing a massive optimization space via a large code base is potentially worse compared to optimizing an adapter instead
- Components:
	- I already expressed some of my per component thoughts above
	- R:
		- let's be clear that we're also providing the same documentation available to the agent's normal filesystem exploring patterns
		- this is an extra avenue to search against the knowledge base
	- S:
		- the details are good but we should frame this as an instantiation of self-refinement
	- X:
		- again, the more active version of validation that is available at anytime to the agent instead of just baked into the broader control loop
	- M: 

- Self Evolve Subsection:
	- need to frame this as a rapidly emerging research topic in the AI community:
		- meta harness
		- harness as code
		- agentic harness engineering
		- skill optimization
	- these are typically explored in the context of core AI benchmarks like coding, terminal navigation, math, etc.
	- how does this fare for something that is driven by domain knowledge?
	- frame ours as an initial study of this direction
	- we are fundamentally similar to these AI self-improvement methods (esp meta harness) because we are having the agent reflect and write its own plugin (which is the adapter)

- 4.3: resolution-IV factorial
	- I think this needs to be moved to section 5 which we should rename to "experiments"
	- we should again first frame it as elaborate/detailed ablations instead of "resolution-iv" as the headline
	- we should motivate why do resolution-iv instead of just stacking each component/stripping each component one by one

# Results

- I am not sure explaining that "eval lift is concentrated in two specific tasks" is something we should bring special attention to.
- do we really need \paragraph headers in 6.1?
- I think this can flow more nicely in prose without these loud paragraph headers.
- I think this is honest result reporting that is useful, but is framed as overly negative right now
	- "reliability is the largest effect" should framed more like the key gain is an improvement in reliability
	- "concentrated on two tasks" makes it sound like the adapter is useless on other tasks. Instead should frame it as that the adapter changes can rescue catastrophic failures
	- "adapter wins fall within seed noise": while true and something we absolutely can mention, should not be in bold. That looks like "we barely win", just explain that the absolute score improvements are subtle-- it's less absolute quality improvement than reliability/efficiency improvement

- Efficiency analysis: should explain why the similar efficiency result is good: harness optimization through LLM reflection driven optimization often leads to over-specification (more and more little features are tacked on over time) which can derail or slow down workflows. Our adapters don't have this overcomplicating effect.
- Negative result of retrieval memory is a good thing to include:
	- just because you provide new tools, does not mean the agent will choose to use them
	- maybe this belongs in the discussion section instead?

- 6.3 human baseline
	- "His note that an agent would...", let's not include this

- 6.4 agent autonomy
	- I don't like this subsection's title
	- let's cut it to something more concise like "exploring agent autonomy"
	- I also really dislike the flow in this subsection
		- we should NOT start with just the results since we have not introduced what this thing is exploring really
		- let's first explain that ok the eval setup provides all the simulation information upfront in a single turn 
		- this is to facilitate standardized evaluation (removes potential ambiguity/confounders)
		- so here we're choosing to limit the scope of the agent's responsibility, we're narrowing the scope of the agent's task-- we give it all the info about what simulation to run and the agent just figures out how to express this
		- eventually we're interested in expanding the agent's responsibility/scope of task so it can take on more and more of the workflow and be more useful
		- This introduces ambiguity that should be resolved with the human scientist collaborator/user
		- We explore this direction by producing alternative specs that specify less and less, requiring the agent to figure out more on its own and seeing when/how it decides to consult the human expert user to resolve ambiguities
	- so the flow should  be about motivating what this subset of the study is about, then explaining the experiment, and then the results and takeaways

- 6.5: cross domain transfer
	- let's be more charitable and just explain how the initial 5 task setting comprises "a pilot study" just to sanity check that this methodology is not only useful on the GEOS domain/task/eval


# overall framing

I think we should consider this work in 2 respects:
1. an application paper: we're trying to help geoscientists expedite a time consuming aspect of their work by building an AI agent for them
2. an (initial) AI for science contribution:
	1. there are maybe 2-ish interesting ideas here:
		1. AI4Science subarea seems really gung-ho about trying to automate end to end. This requires really competent scientific reasoning to identify what directions are worth exploring, how to innovate useful, principled, and novel methods, and interpreting results in scientifically plausible/useful ways that can further improve the methods, findings, etc. Hard scientific reasoning is required for all that, **but even an "easier" bottleneck/challenge of running experiments/operating scientific tools** can be unreliable with current systems and we should invest in improving the reliability here to provide immediate value to our domain partners (instead of trying to threaten their job security). So the idea about "interface" itself being something that requires some amount of domain-know-how and scientific reasoning and needs its own deliberate effort
		2. The thing about doing lightweight adaptation over top existing harnesses instead of rebuilding from scratch.

These are overall framing ideas so it's kinda throughout the paper.
