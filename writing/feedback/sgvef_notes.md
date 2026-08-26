# Notes on SGVEF-LOOP paper (advisor's reference)

Quick read of the SGVEF-LOOP paper to identify organizational patterns the
advisor likes. Below: what they do, why it works.

## 1. Research questions made explicit and load-bearing

**Section 5 opens with §5.1 "Research Questions (RQs)" listing three numbered RQs:**

> **RQ1**: How efficiently does SGVEF navigate the sparse and constrained topology of the tool transition space?
> **RQ2**: Can the constructed benchmark effectively differentiate the capabilities of diverse MCP Agents across multiple dimensions?
> **RQ3**: What critical vulnerabilities and behavioral inconsistencies in agents are revealed by the metamorphic testing paradigm?

Each subsequent results subsection is named **"Effectiveness of SGVEF LOOP (RQ1)"**, **"Benchmarking MCP-based Agents (RQ2)"**, **"Insights from Metamorphic Testing (RQ3)"**. The RQ tag in every subsection title.

**Why it works**: the reader can jump to any subsection and immediately know what question is on the table. The RQ is the contract; the results section is the answer.

## 2. Boxed "Ans. to RQx" summaries

At the end of each results subsection, a gray-shaded box:

> **Ans. to RQ1**: SGVEF enables efficient navigation via synergistic mechanisms. Sampling accelerates initial discovery by 2.1×, while feedback breaks exploration plateaus. Consequently, SGVEF saturates C_node (100%) by round 15 and exhausts 80.54% of the theoretical transition space by round 60.

> **Ans. to RQ2**: The benchmark reveals marked capability stratification and discerns distinct behavioral profiles. It effectively isolates critical phenomena: *reasoning instability*, *parametric hallucination*, and *interaction friction*.

**Why it works**: skimmable. A reviewer reading only the boxes gets the headline answer to each RQ. The named phenomena (italicized) anchor the contributions.

## 3. Findings as named phenomena (the collaborator's point)

Findings are not bullet-listed observations; they are **named diagnostic phenomena**:
- *reasoning instability*
- *parametric hallucination*
- *interaction friction*
- *Incomplete Planning*
- *Poor Noise Robustness*
- *Unstable Tool Selection*

Each name gets one bold mini-section in the body where it is defined, evidenced, and connected to what causes it.

**Why it works**: nameable concepts travel. A reader can cite "we observed *parametric hallucination*" downstream; an unnamed observation cannot. The reusability is part of the contribution.

## 4. Bold mini-headings inside subsections (instead of \paragraph dumps)

Inside §5.4, subsection covers RQ2. Body uses bold lead-in mini-headings:

- **Capability Stratification.** [one paragraph]
- **Reasoning Stability.** [one paragraph]
- **Execution-Response Alignment.** [one paragraph]
- **Interaction Friction.** [one paragraph]

Each mini-heading **is itself a finding name**. Reading just the bold leads gives the reader the structure of the answer.

**Why it works**: this is the move that lets the section read as narrative (no bullet lists) while still being heavily scannable. Advisor objects to bullets but likes bold; this hits both constraints.

## 5. Comparison table that is genuinely self-contained

Table 1 (related work): a feature matrix with column headers like "MCP-Focused", "Auto. Gen.", "Verif.", "Tool Logic", "Traj.", "Fuzzing", "Meta." — all columns are short, interpretable names, not letter codes. The caption defines each abbreviation explicitly.

**Why it works**: a reader can land on the table without reading the caption and still get the message because the column names speak for themselves. We could not say that of our current Table 1.

## 6. Section 4 (Methodology) uses titled subsections that mirror Section 5

§4.1 S: Adaptive Sampling Strategy
§4.2 G: Fact-Grounded Metamorphic Generation
§4.3 V: Dual-Constraint Validation
§4.4 E & F: Execution and Feedback Loop
§4.5 Self-Constructed Evolution

The letter prefixes (S, G, V, E&F) are introduced in the methodology subsection
titles themselves, not buried in body prose. Reader sees the letter, the name,
and the role in the table-of-contents-style outline.

**Why it works**: maximum redundancy across paper structure / figures /
methodology / results — the reader has multiple low-effort ways to pin down what
a letter means.

## 7. Conclusion is one tight paragraph

Their conclusion is ~120 words, three sentences. Names the contribution, the
headline empirical finding, the broader implication. Same scale as our
post-revision conclusion.

## What I'm not borrowing

- Their tone is very dense; sentences are heavy. Our prose is lighter.
- Their tables are crammed; we have more room.
- They use "first/second/third" enumerations heavily, which can feel listy.
