# Reviewer raw notes — things I considered but didn't promote

These are the section-by-section observations I made while reading, including things I cut from the formal review either because they were nits, redundant with stronger criticisms, or speculative.

## Abstract
- "Simulator-Interface Grounding Adapter" — branded name for what is, mechanically, "four wrapper components." Considered making this a top-line concern but the discussion of W5 (novelty / framing) is the right place.
- "$40\times$ lower across-seed variance" — went straight to W2 calculation: $0.081 / 0.002 = 40.5$. So the number is arithmetically real, but the arithmetic is between two std estimates each computed from $n=3$ samples. The std of $0.081$ is driven by a single zero-score seed on `ExampleProppantTest`. So really we are reporting "1 vs 0 zero-score events" with extra decimal places.
- "$\sim 16\%$ fewer tool calls" — verified: SE val tools/task 68.9 vs Vanilla 81.5 = 15.5% drop. But on held-out-eval, SE 97.4 vs Vanilla 90.5 = 7.6% *increase*. Headline cherry-picks val.
- "$8$ to $36$ times as long as the agent" — combines a one-hour-budget cap (humans timed out) with an uncapped 3-hour result. Two different comparisons stapled together.

## Introduction
- Strong opening. Frames the bottleneck honestly. Citation density looks appropriate for an Applications-track intro.
- L86 "the only main effect that clearly exceeds run-to-run variability is generic retrieval; however, it decreases performance" — but App. F admits this estimate is contaminated by the native_plugin_prefix bug. The discussion's limitations paragraph waves it off because "X+M-vs-Vanilla is unaffected since both are R$^-$", but the *finding about R* is the contaminated one. Promoted to W7.
- Contributions list (i)-(iv) reads as a methods paper but the content is an empirical study. The structural mismatch is what made me push on framing / W5.

## Related work
- Coverage is broad. Most adjacent papers I would expect to see *are* cited: ChemCrow, Coscientist, CellVoyager, AI Scientist, OpenHands, SWE-agent, Foam-Agent, MOOSEAgent, MD-Agent2, MetaOpenFOAM, OpenFOAMGPT, JutulGPT. Some year-stamps look suspicious (2026 on several) — could be real arxiv preprints from earlier in the year, but bibtex audit would be worthwhile.
- Buffer of Thoughts / G-Memory citation for procedural memory is appropriate.

## Background
- §3 (GEOS as DSL) is well-pitched for a NeurIPS audience. The four-difficulties enumeration (large vocabulary, version drift, cross-section constraints, under-specification) sets up the bottleneck analysis cleanly.

## Method
- §4.1 component list is clear. The S vs X distinction (mandatory hook vs agent-callable tool, both via xmllint) is the right diagnostic structure for the factorial.
- SE-prose definition is muddy on first read: "takes only the rewritten v3 primer and cheatsheet from SE and inserts them into an otherwise standard S+X+M cell" — fine, but the *purpose* (does the SE lift come from prose or from the full SE package?) should be stated up front, not buried.
- Resolution-IV $2^{4-1}$ with generator D=ABC: design is standard and the main-effects justification is sound. The "S+X+M" 16th cell added back is the predicted-best corner from main effects; that is fine.
- Confound noted: S and X both invoke xmllint when both on. Authors flag this in §3.2 and again in limitations. Honest.

## Evaluation setup
- "deepseek-v4-flash" as backbone, 1500s timeout, $n=3$ seeds, failures-as-zero. Standard.
- Splits: 10 held-out-eval, 18 distillation, 17 val. Hygiene gate disclosed (caught a prior 13/17 leak). Good.
- TreeSim defined but not validated against a human-graded baseline. A reviewer could push on "is TreeSim a reasonable quality metric?" but the bottleneck analysis grounds it adequately for an Applications submission. Didn't promote.

## Results
- Table 1 is the headline. Verified arithmetic:
  - Vanilla val 0.910 ± 0.024; held-out-eval 0.720 ± 0.081. The 0.081 is the big number that produces the 40× ratio.
  - SE val 0.919 ± 0.020; held-out-eval 0.789 ± 0.012. Mean delta 0.069. Std ratio 0.081/0.012 ≈ 6.75×. Authors use S+X's 0.002 for the 40× number — pick of the lowest std cell.
- §5.1 main-effects paragraph: "The best val cell (X+M) beats Vanilla by $+0.011$, well within seed std" — honest.
- Table 4 (per-task): verified that 7 non-rescue tasks have within-noise differences across cells. Means of the 7 non-rescue, non-universal-failure Vanilla scores: (0.755+0.847+0.891+0.909+0.935+0.963+0.986)/7 = 0.898. Matches paper's claim.
- §5.2 bottleneck: Table 3 numbers seem internally consistent. Some "-" cells in Table 3 are ambiguous; assumed they mean zero counts.
- §5.2 "Strictly perfect tasks (TreeSim ≥ 0.999) do not increase under any adapter (Vanilla 7/51, X+M 6/51, SE 6/51)" — this is a strong qualitative point and supports the "harm-reduction not correctness" framing. The X+M and SE counts are actually *lower* than Vanilla here. Authors don't lean on this but they could.
- §5.3 OpenFOAM: R+X cell at 0.145 with 4/5 zeros, single seed. Brittle. Foam-Agent execute-mode failure is the key concern (W6).
- §5.4 autonomy: $2 / 64$ consultation rate is striking. The on-disk findability diagnostic (15/26 dropped values findable via grep) is the credible mechanism. This is the strongest individual finding in the paper.
- §5.5 human baseline: $n=2$, $1$ task. The ChatGPT disclosure (App. K) is the right move but it does undermine the headline 36× claim. Both participants ran out of time on a *single* file — the "minutes to author a deck" claim has a very specific scope.

## Appendix dives
- App. A (benchmark): v1/v2 spec contamination disclosed; hygiene gate added after prior leak. Discipline is visible.
- App. C bottleneck: classifier output looks reasonable. Some categories have low counts at the per-cell level — careful about over-interpretation.
- App. D per-task: confirms the 2-task concentration cleanly.
- App. E main effects: R = −0.032 is the only one clearly outside noise; this is the contaminated estimate.
- App. F cross-model: native_plugin_prefix bug write-up is excellent in form. Single-seed cross-model results are limitation, acknowledged.
- App. G OpenFOAM: scoring metric (0.7·sim + 0.3·coverage) is reasonable but bespoke. The "Foam-Agent in lint-only mode" issue is real (W6).
- App. K human baseline: Liam / Sahchit named in main text (App. K). Confirmed via tex source — these are real names that survived anonymization. Reviewer-form concern: report to PCs.
- App. M efficiency: SE has higher tool count on held-out-eval than Vanilla. Contradicts the "16% fewer tool calls" framing for the harder split.
- App. O cheatsheet: 775-token primer with explicit anti-patterns. Reasonable design artifact.

## Things I considered but did not raise
- TreeSim metric not validated against human grading — too aggressive a request for an Applications submission; bottleneck analysis covers this.
- Choice of deepseek-v4-flash as backbone — adequately justified, cross-model panel exists.
- Single-seed cross-model — acknowledged limitation, follow-ups appendix lists multi-seed as planned.
- "ICL pool" terminology in App. A is inconsistent with "held-out-eval" in §4.2 — they appear to be the same 10 tasks. Minor.
- App. K mentions "Sahchit" — possibly a typo of "Sachit" or "Sahchit"; either way, anonymization issue.
- App. L OpenFOAM per-task table: helmholtzResonance scores at zero for Vanilla and R+X but reasonable for others — single-seed dependence on initialization, not necessarily a method effect.
- The "memory-as-retrieval" negative finding is interesting but has a model-specific scope (deepseek-v4-flash + Claude Code harness). Authors don't overclaim its generality, which is appropriate.

## Net read
This is a careful, honest paper that has been polished in a way that hides its narrowness. The empirical contribution is "we ran a factorial of four wrapper interventions on one simulator and found that the headline effect is concentrated in 2 of 10 held-out tasks, and the underlying mechanism is preventing unparseable outputs." The two negative findings (procedural-memory-as-retrieval, consultation-vs-substitutes) are the freshest material. If those were promoted to the abstract and the +7pp/40× framing were demoted to a specific hard-tail statement, the paper would be a clear-accept on its negative-results contribution alone. As written, the marketing of the empirical numbers exceeds what the design supports.
