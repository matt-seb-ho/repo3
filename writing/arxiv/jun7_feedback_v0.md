# Changes/Feedback I want you to address 

## Advisor Feedback

Abstract
- replace small with lightweight in describing the adapter
	- last sentence: "these results suggest that a small..."

Introduction
- replace small with lightweight in describing the adapter
	- last paragraph: "these results suggest that a small..."

- 2nd sentence in last paragraph of Intro ("Taken together...")
	- problem: 
		- it's too confusing
		- too much to read
		- THING can reduce task completion, while adapting to the problem: MECH 1 for BOTTLENECK X, MECH 2/3 for BOTTLENECK Y.
	- make it straight forward, less wordy, and maybe put shortened version of MECH1/MECH2  stuff in parentheses or smth or omit them. Fine to just say it provides speedup and also can address different bottlenecks, idk.
	- My advisor puts a strong premium on clarity


## Collaborator Feedback

Table 1: 
- problem: hard to follow horizontally
	- add row lines between rows so the components markings are easier to follow horizontally?
	- for the existing lines make them doubled or bolded or thicker to maintain distinction (alternatively make the new lines slightly slight or something)
	- alternating background colours for rows is fine too

Introduction

Background
- "a deck is better understood as a small domain-specific language (DSL)"
	- let's check the correctness here. Is it right to call a file/set of files written in a DSL, a DSL?
	- maybe it's more correct to say, although GEOS directly uses XML for input files, its elaborate vocabulary/schema make its config language more akin to a DSL, etc.

Methods Section
- base harness and objective
	- "we never introduce treesim before this paragraph. viewers may also conflate this metric with eval for OpenFOAM and LAMMPS"
		- I'm not entirely sure what he's asking for here tbh
		- maybe clarify that TreeSim is our quality metric for GEOS specifically?
- component paragraphs
	- in the S+X paragraph, S and X are bolded; maybe bold R and M in their respective paragraphs?
	- in R paragraph maybe briefly mention/define RAG
		- the coding agent already does this through find/grep tools which we acknowledge but we never directly mention/define RAG
		- just add that the base coding agent does this already but because of the drawbacks we already have in the paragraph we want to consider the semantic search that prior RAG research has thoroughly investigated (cite `lewis2021rag`)
- "The SIGA design space..."
	- "We refer to any wrapper instantiating such a subset as a SIGA"
		- This is somewhat clunky. A nicer way is to describe SIGA as the add-on (plugin) constructed on top of an existing coding agent with this minimal design centered around these main ideas of cross session memory, additional connectors to knowledge bases, and validation/self-refinement. No need to copy my exact terminology but the subset thing is somewhat strange to read, would prefer describing SIGA adapters as something designed from this general recipe (which involves building and testing this small set of ideas)
 

# Feedback to discuss

There's a piece of feedback from junior collaborators I don't know if I totally agree with, so I want your thoughts.

In an intro paragraph "Concretely, SIGA factorizes this grounding into 4 reusable components..."
- they think we could have more structure here, maybe do a bullet point list instead of paragraph form
- maybe even add the abbreviated letters for each thing too here?

So my concerns for this feedback are
1. historically my advisor doesn't like having lists in the intro and prefers a more flowing, narrative approach. She also directly suggested putting numbers in parentheses for the following intro paragraph, so clearly this is not absolute
	1. we could do the same compromise of inline numbers in parentheses but I'm not totally sure about this. Is it nice parallel structure to the next paragraph, or repetitive?
2. I think I may have deliberately not used the abbreviations in the intro because I didn't feel it was needed/I felt that it's over-explaining. I think the intro should be able to stand alone in many ways so I think the letter abbreviations are a little bit of an implementation detail/detail about our experiments/notation that is not needed here and very clearly explained in the method section where it becomes relevant...

Your thoughts?

# Instructions

Please act on the first set of changes. Make a TODO list. Make a new jun 7 change log markdown file to record progress (record changes, before/after snippets if it's more substantial, etc.).

Then, talk to me about the last point of feedback that I want to discuss...
