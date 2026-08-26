# Lessons from SGVEF-LOOP — concrete moves for our paper

Distilled from `sgvef_notes.md`. Each lesson includes a proposed action for
our paper.

## Lesson 1 — Hoist research questions to a §5.1 box

**SGVEF move**: §5.1 explicitly enumerates RQ1, RQ2, RQ3 before any results.
Each subsequent results subsection title carries the RQ tag.

**Our analogue**: our current §5 (Experiments) has Ablation design / Benchmark /
Metric / Baselines but no statement of *what we are asking the experiments to
answer*. We can add a short opening enumeration:

> Our experiments are designed to answer:
> **RQ1** (mechanism): Which grounding components contribute to reliability gains, and which to absolute-quality gains?
> **RQ2** (transfer): Does the recipe transfer beyond GEOS to a different simulator family?
> **RQ3** (autonomy): How does the agent behave when the brief specifies less, and does it consult a human when uncertain?
> **RQ4** (human anchor): How does the agent compare with domain experts on a representative task?

This gives §6 (Results) subsections a contract to fulfill.

## Lesson 2 — Add "**Takeaway.**" boxes to each results subsection

**SGVEF move**: gray-shaded "Ans. to RQx" box at end of each results
subsection.

**Our analogue**: same idea but using a bold lead-in instead of a custom box
(less LaTeX scaffolding):

> **Takeaway (RQ1).** The four grounding components separate cleanly on the
> reliability axis: end-of-turn schema verification carries roughly all the
> hard-tail reliability lift on its own. Mid-trajectory validation and the
> memory cheatsheet are small-positive; retrieval is a small-negative drag on
> the in-distribution split.

One box per subsection. Skimmable. Fulfills advisor's "easy to identify
takeaways" criterion without needing a separate Discussion section.

## Lesson 3 — Name findings as diagnostic phenomena

**SGVEF move**: *parametric hallucination*, *reasoning instability*,
*Incomplete Planning*, etc. — findings are nameable, reusable concepts.

**Our analogue**: we have several findings that could carry names:

- The val ceiling vs held-out hard-tail rescue dichotomy → "**hard-tail
  rescue**" as our coined phrase.
- Adapter cells trading `missing_block` for `extra_block`/
  `hallucinated_extras` → "**absence-to-imprecision trade-off**".
- Agent never invokes consultation tool because example library substitutes →
  "**oracle substitution**".
- Memory-as-MCP-tool never invoked, only system-prompt primer produces lift →
  "**interface-dominates-content** lesson" (already gestured at in Discussion;
  could be named).

Once named, these phenomena should be referenced by name everywhere they
recur in the body. The named-phenomenon discipline is what makes findings
*portable* (citeable downstream).

## Lesson 4 — Bold mini-headings inside subsections

**SGVEF move**: inside each result subsection, bold mini-headings (e.g.,
**Capability Stratification.**) name the sub-finding; one paragraph per
mini-heading.

**Our analogue**: we already do this in §6.2 (Bottleneck analysis) and the
advisor liked it. Apply the same pattern to:

- §6.1 reliability — currently flowing prose; could carry mini-headings
  like **Hard-tail rescue.** / **Variance reduction.** / **Val ceiling.**
- §6.4 autonomy — already has **Motivation. / Protocol. / Results. /
  Takeaway.** which is good; the *Takeaway* can be the boxed answer.
- §6.5 OpenFOAM — could mark the headline number with a bold lead-in
  rather than burying it in prose.

## Lesson 5 — Subsection titles should name the finding, not the topic

**SGVEF move**: §5.4 "Benchmarking MCP-based Agents (RQ2)" — the title
attaches a question. The four bold mini-headings inside name phenomena.

**Our analogue**: advisor flagged "Reliability is the key gain" as too
generic. Sharper alternatives:

- "**Reliability, not absolute quality, is where adapters help (RQ1)**"
- "**Schema-aware adapters fix block-level omissions; attribute errors persist (RQ1)**" (for §6.2)
- "**The on-disk example library substitutes for human consultation (RQ3)**" (for §6.4)
- "**Stop-hook reliability transfers to OpenFOAM (RQ2)**" (for §6.5)

Each title should make a claim the subsection then defends.

## Lesson 6 — Self-contained tables (already on the TODO)

**SGVEF move**: Table 1 uses short interpretable column headers, not letter
codes.

**Our analogue**: covered by Task #17. Add short-name columns to Table 1
(cell definitions) and remove the ± tick syntax in favor of explicit
component names.

## What we should NOT borrow

- Their tone is very dense and packed; our prose is lighter and that's OK.
- "Ans. to RQx" box typography — we don't need a custom environment, bold
  "**Takeaway.**" leads do the same job with less LaTeX overhead.
- Excessive first/second/third enumerations — advisor dislikes listy
  prose; we'll prefer flowing narrative with bold mini-heads as the
  scannability backbone.
