# My Notes on the Paper

Reading notes captured while going through `writing/arxiv/neurips_2026.tex` (745 lines). Separate from the fresh-context NeurIPS review (`neurips_review.md`) and the storytelling document (`storytelling_suggestions.md`). These are my own observations from reading top-to-bottom.

## What I think the paper is, in plain English

You took an existing coding agent (Claude Code), wrapped it with four ordinary engineering pieces — a retrieval plugin, a stop-hook validator, an in-loop validator tool, and a memory cheatsheet — and tested whether each piece helps the agent write GEOS multiphysics simulation deck files. You did this carefully, with a fractional factorial design, on two benchmark splits, with bottleneck failure-mode analysis, against a $n=2$ human baseline, with a small autonomy sub-study, and a small cross-simulator transfer to OpenFOAM. You also explored a self-evolution loop that rewrites the wrapper offline against held-out training scores.

The findings, honestly stated, are:

1. On easy tasks, the wrapper components don't measurably help — the bare agent already does fine.
2. On hard compound-physics tasks, the wrapper prevents catastrophic failures (zero-score outputs), gaining ~7pp mean and ~40× lower variance — but mostly via reliability on 2 specific tasks.
3. None of the components fix attribute-value errors. Only block-presence errors.
4. The dominant transferable component is the stop-hook (forced end-of-turn validation).
5. Two negative findings: (a) agents ignore retrievable procedural memory (use always-on system-prompt memory instead); (b) agents rarely consult humans when an example library is reachable.

## Where the paper is strong

- **The factorial design is real.** Resolution-IV $2^{4-1}$ with the corner cell filled in. Disambiguating main effects is a serious effort for an application paper.
- **The bottleneck analysis (§5.2) is the best part.** "Adapters fix missing_block but not bad_attribute_value" is a genuinely useful finding, with table-backed counts. This is what I'd lead the paper with if I had to pick one section.
- **The negative results are unusually clean.** The memory-as-retrieval result (zero tool calls over many trials) and the supervisor-consultation rate (3.1%) are exactly the kind of mechanism-revealing observations the agent-research community will cite.
- **Cross-simulator transfer is attempted.** Most application papers wouldn't bother. Even with the lint-only Foam-Agent caveat, having an OpenFOAM result puts you ahead of the typical "one domain only" application paper.
- **The human baseline exists.** $n=2$ is small but you collected browser histories and made the comparison qualitative. This is hard work that most papers skip.
- **The paper acknowledges its own bugs in the open.** The native-plugin-prefix bug appendix (App.~F) is unusually honest. Reviewers will read this as careful work.

## Where the paper is weak

- **The headline numbers are oversold relative to the underlying evidence.** $40\times$ variance reduction = 1 zero-score failure vs 0. $+7$pp mean = 2 task rescues on a 10-task held-out set. The arithmetic is correct but the framing reads stronger than the data supports.
- **The "method" section reads like an apology.** §4 introduces R/S/X/M as if the paper has to justify why these four — instead of stating they are *the obvious off-the-shelf choices* and letting the empirical study do the work.
- **The cautionary findings are buried.** §5.2.3 ("Memory-as-retrieval") and §5.4 (autonomy/consultation) are arguably the most novel parts of the paper, and they appear after the main quality table.
- **The self-evolved variant is treated as an afterthought.** SE is the most methodologically novel piece — an automatically discovered adapter that matches the best hand-designed one — but it gets one bullet in §4.1 and is mentioned almost casually.
- **Title and acronym signal "method paper."** "Simulator-Interface Grounding Adapters" sounds like a method contribution. Application-track reviewers will check whether the method is actually novel enough; you'd rather they not check at all.
- **The OpenFOAM section is honest but weak.** $n=1$, 5 tasks, lint-only Foam-Agent. Useful as transfer evidence but the table makes it look more like a benchmark than the prose claims. Either commit to "this is qualitative" by removing some of the precision, or run more.

## Specific things I noticed while reading

- **Line 67 (abstract).** "Reducing across-seed variance by roughly $40\times$" — this is the most aggressive framing in the abstract. See storytelling doc.
- **Line 144 (cheatsheet origin).** The cheatsheet is distilled with `gemini-3-flash-preview` from 18 training trajectories. Worth noting in §4 that this is *itself* a small offline pipeline — useful prelude to introducing SE.
- **Line 157 ("S and X both use xmllint").** This is an acknowledged confound but only mentioned once. If a reviewer is going to gripe about something in the factorial design, this is the spot.
- **Line 161 (hygiene gate).** "Added after an earlier cheatsheet leaked 13/17 validation-task basenames." This is the kind of thing that *helps* you in review — it shows real care. Don't tuck it in parentheses; make it a half-paragraph.
- **Line 207 ("only R clears noise, with negative sign").** The R-effect estimate is on contaminated data (admitted in App. F). This is a real problem; see storytelling doc.
- **Line 218 (efficiency).** "SE matches Vanilla on val tools per task (68.9 vs 81.5) and runs about 16% faster." Cross-check against Table 9: on held-out-eval, SE makes *more* tool calls than Vanilla (97.4 vs 90.5). Either qualify the abstract claim or report both splits in the body.
- **Line 220 (memory-as-retrieval).** "Across every test-set run in which the tool was available, the agent called it zero times." Promote this. It is your most reusable contribution.
- **Line 232 (autonomy).** "$3.1\%$ … 31/32 silent runs were not silent for lack of questions" — this sentence is the paper's most interesting observation about agent behavior. Foreground it.
- **Line 270 ("adapter-design recommendations").** These four bullets are the *output* of the paper as a guide for future scientific-agent builders. Worth promoting to a numbered list with explicit "we recommend X" framing in the discussion.
- **Line 611 (App. K, participants).** Real names ("Liam", "Sahchit") in the .tex source. Anonymization breach. Fix before anything else.
- **Line 47 (`\sys` macro = `GeoAgent`).** Defined but unused. Decide on a name and stick with it; remove the unused macro.
- **Line 50–51 (commented-out title).** The commented-out title ("Coding Agent Adaptation for Advanced Scientific Tooling: An Application Study in Automating Geophysics Simulations") matches your Application-track framing better than the current title. Consider switching back.

## The bigger picture: what I think you should believe

Your advisor and collaborator are right that you have enough empirical work. The paper does not need more experiments; it needs to commit to its identity. The most damaging current state is that it reads as a method paper hedging about its method's novelty. The same data, reframed as an empirical investigation into "what grounding components actually matter when you take an off-the-shelf coding agent into a real scientific software stack," with honest, qualified numbers and the negative findings foregrounded, would be a substantially stronger Application-track paper.

The single biggest gain available to you is not in the data — it is in the abstract and §1. A reviewer who reads the abstract you currently have starts skeptical. A reviewer who reads an abstract that says "we test the cheapest off-the-shelf recipe on a hard application, find that one component carries almost all the weight, surface several reusable mechanism findings, and show the recipe ports to a second simulator" starts curious. Same paper, different starting point.

## Files written in this pass

- `neurips_review.md` — the formal NeurIPS-style review from the fresh-context subagent
- `reviewer_raw_notes.md` — the subagent's section-by-section scratch notes
- `storytelling_suggestions.md` — concrete suggestions for §4 and overall paper reframing
- `one_liner.md` — advisor-ready 1–2 sentence summaries
- `paper_notes.md` — this file
