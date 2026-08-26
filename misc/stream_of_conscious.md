# More on paper framing.

Let me give you the full arc of this project. This is a grant project that I treated as a side project to my part time work with MSR. Initially the ask was just to develop an agent around state of the art tooling like GEOS.

The basic premise was that GEOS is SOTA tooling and somewhat hard to learn and not super ergonomic to use. It is, however, extremely powerful software and therefore useful to geoscientists and engineers. Thus, we're interested in building AI tooling around it to reduce this friction.

So as my side project I frankly put low effort into designing a basic coding agent harness with standard tools (read/write, bash, python) with the key feature being documentation search (because crucially the doc search tool implements main domain adaptation for generic coding -> GEOS specific) which we implemented in a semi-interesting way. We indexed the RST files into a dense vector database to do semantic search, and then noted the docs' RST files referenced external XML files as snippets and many tutorials provide paths to example XML files. So we created a separate index for the XML files. Finally GEOS experts gave us heads up that the data structure index and schema tables are really important (these list all valid attributes/tags/elements in GEOS XML) so we built a third search tool for these tables specifically.

After the successful initial demo, progress slowed to a crawl because we had less pressure to deliver. We pursued some weird directions in refining evaluation, doing multi-turn simulation/evaluation. And then we had external requests for features: integration with OpenClaw, new UI, etc.

From a process standpoint we weren't treating this as a proper research project, but an engineering one-- developing a useful tool for our geoscience domain collaborators.

Then when it came to having research output for the grant project we got kinda stuck. My collaborator and I were discussing science project directions of harness engineering automation which at the time was blossoming in the now very popular meta-harness learning research. We wanted This suggestion was rejected by advisors because they wanted to focus on being an application paper-- being maximally useful to geophysicists.


So then for the next month we tried to take a principled scientific approach to designing our GEOS agent specifically. We re-adapted our agent to use a collaborator's library that implements various memory/planning modules (designed for embodied agents first and foremost) so we could easily run ablations with different implementations.

We investigated the following components at first
- primer (system prompt)
- search tools (we haven't introduced an alternative search tool yet just ablated with/without our 3 index version)
- self-refinement loop (within a single task, refining the output)
- memory (across/between tasks, recording takeaways to reuse)

We compared our initial agent against Claude Code as a baseline and found that Claude Code was really quite good, so then we decided "why compete against a highly skilled engineering team's insanely popular product when we can just build on top of it" so we reimplemented our agent but this time as a plugin over Claude Code.

Next, worried about the limited contributions of current design we also expored:
- subagents and orchestration (if tightly controlling context for different stages helps) 
- self evolution: (extended version of memory: across/between tasks, can the agent propose new tools, skills, plugins, to improve performance)

We're now very close (a few days) to a neurips deadline (we don't necessarily need to meet it, but for the grant project we need the paper polished in a few weeks).

My personal conviction is that we don't have enough to write a neurips paper right now. The current extent of content we would have is:
- we built an agent for advance scientific automation
- our agent is CC plus customizations that we test with thorough ablations
- we test various configurations, some other harnesses, base LMs (without a harness)
- we also have a human baseline case study where we show that for a task our agent completes in 5 minutes, geoscience PhD students (who are fairly new to GEOS) take an hour to do

The current set of results is kinda dismal in that only the self refinement hook seems to be consistently good. Anyways the sad part is that the "domain adaptation" doesn't seem to be very grounded in reading and following tutorials because the default Claude Code agent is already so proficient at finding stuff on its own and copying from examples in the documentation from its native file system search (we provide the entire GEOS source code repo which includes documentation to the agent).

So this has kinda nuked my confidence in the neurips paper submission. It feels as though even if we iron our experiments out the best case is that we have a manually engineered or for paper rhetoric "designed" agent that are minor add ons to claude code. Maybe I'm underselling this.

When we were told to focus on being maximally helpful to the geoscientists, I argued ok then we are sacrificing methodological novelty. One of the advising profs said that novelty for the sake novelty is pointless, being useful for the intended user is more important. I agreed with him. He said that application papers are fine-- even if they don't introduce new methods they still study the application of existing methods (all our components are things that have already been explored: RAG, search, self refinement loops, memory systems, etc.) to a new problem (there is no agent for GEOS simulations). This advising prof only joined for that meeting. The main advising prof has instead insisted that reporting engineering effort is not good enough and that we at least need the scientific rigour of ablations so we did that. But she sent us this chatgpt conversation which establishes that I think she wants to claim some methodological novelty/generalization as well: please see `/home/matt/sci/repo3/misc/lianhui_gpt_convo.md`.

My advisor has final say so I would highly recommend understanding this chat log which is the biggest contributor to her expectations for our neurips submission because she has been extremely hands off this project otherwise.

So my conviction from a while ago was that the most interesting direction would be in the automation of this agent design. This is in line with meta-harness and papers in this direction. These other meta-harness mostly focus on standard benchmark tasks like coding, terminal bench, tau bench on so on. I think adapting to advanced scientific software has its own interesting niche. So that's how broadly came to the key ideas of (1) automatic harness adapter engineering (2) scientific software domain adaptation.

I already mentioned this in our previous discussion but the interesting piece of (2) is that there frequently exists documentation for these softwares but it might be long inefficient to just dump all in context or have the agent navigate through tutorials on its own every time. So the key challenge of domain adaptation is baking the documentation into the harness design somehow. I think this represents an interesting problem distinct from the majority of existing benchmarks that lack a documentation wiki to ground it. Because instead of just learning from task experience (rollouts), the difference for science software adaptation is you read documentation to build the agent harness to read documentation. i.e. on the meta-harness level you want documentation to guide you, on the harness level when the agent is actually executing the task you also want that agent to be guided/informed by documentation.

So I think this represents an interesting technical challenge that is potentially novel.

My immediate thought is that I feel unconfident in our current manual designed contribution, so I want to pursue this automatic documentation-driven harness adaptation as the methodological novelty.

Looking at other domain specific agents, where it's more of an application paper because their proposed workflow is not super novel (each of the components are individually not novel) but I think the interesting piece is that they apply combine this in a deliberate way for their task. My main example for this is the Cell Voyager paper: see `/home/matt/sci/repo3/misc/cellvoyager_summary.md`. So theoretically our current manual design is somewhat similar in that our individual components are not novel but we put together this custom workflow for this new task that no one has really evaluated/tackled before. But the problem is that our custom workflow is not that exciting even compared to Cell Voyager. Like we don't even control our own control loop except for the self refinement hook that forces Claude Code agent to keep going while the xml schema validation fails. Like the other pieces we have are a top level prompt, search tools that maybe don't help over native file system based search, and a memory system of also questionable efficacy. That's kinda where my insecurity in the current method lies and why I want to pursue the documentation driven automatic adaptation engineering if that makes any sense.

In some ways my effort in the subagent orchestration thread: `docs/2026-04-30_subagent-orchestrator-handoff.md` was a previous effort of this documentation driven engineering. But the key differences was that I was (1) forcing the subagents direction (2) semi automatically specifying the design-- subagents and use previous manual tooling. So I think even though this initial attempt produced not so good results, a second try could be good with
- not forcing subagents
- not forcing any initial manually designed components
- making the design experience driven (seeing how a baseline agent actually interacts with documentation during task execution)
- studying meta-harness' methods

---

So that has been my stream of consciousness. I want to hear all your feedback. Please write it up to a document. And then help me strengthen paper framing/project direction so I can decide what to pursue next with more thought put into planning.

Maybe we can commit to the current pipeline for the neurips paper (is that enough?) and then have the automatic harness engineering left for the follow up project? Maybe we should do automatic harness engineering with the special documentation focus but without the adapter thing? I'm not sure and would love any and all of your feedback.
