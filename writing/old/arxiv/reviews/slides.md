---
marp: true
theme: default
paginate: true
---

# SIGA paper: review, storytelling, revision pass

Paper: `writing/arxiv/neurips_2026.tex` (NeurIPS 2026, Applications track)

Three threads to walk through:

1. Fresh-context NeurIPS-style review
2. Storytelling diagnosis and suggestions
3. What the revision pass actually adopted

---

## Context

- Application paper on adapting Claude Code for **GEOS** multiphysics deck authoring.
- Four-component grounding adapter: **R** retrieval, **S** stop-hook, **X** xmllint, **M** memory cheatsheet, plus a self-evolved variant (SE).
- Experiments: factorial dissection, bottleneck analysis, human baseline ($n=2$), autonomy sub-study, OpenFOAM transfer.
- Advisor's note: enough empirics; weak story; methodological novelty is not the contribution.

---

# Part 1: the review

Fresh-context adversarial subagent in NeurIPS-Application-track reviewer mode. Full file: `neurips_review.md`.

---

## Headline judgment

| Axis | Score |
|---|---|
| Soundness | 2 / 4 |
| Presentation | 3 / 4 |
| Contribution | 2 / 4 |
| Confidence | 4 / 4 |
| **Recommendation** | **Borderline Reject** |

Honest paper; the marketing of the empirical numbers exceeds what the design supports.

---

## Strengths

- Genuine Resolution-IV factorial with main-effects disambiguation; rare for an application paper.
- Bottleneck analysis is the strongest section: "fixes `missing_block` but not `bad_attribute_value`."
- Negative findings are unusually clean: memory-as-retrieval ignored zero times; consultation rate 3.1%.
- Cross-simulator OpenFOAM transfer attempted at all.
- Human baseline exists; browser histories collected.
- Paper documents its own bugs in the open (native-plugin-prefix bug).

---

## Weaknesses (priority order)

1. Headline numbers oversold versus underlying evidence.
2. "Method" section reads like an apology for not being novel.
3. The cautionary findings (memory, consultation) are buried below the main quality table.
4. Self-evolved variant treated as an afterthought.
5. Title + acronym signal "method paper."
6. OpenFOAM transfer is single-seed, 5 tasks, Foam-Agent crippled to lint-only.

---

## Specific numbers the reviewer pushed on

- **$40\times$ variance reduction**: arithmetic correct ($0.081 / 0.002$); mechanism is **one zero-score seed vs zero** on `ExampleProppantTest`.
- **$+7$pp held-out-eval lift**: concentrated in two specific tasks; the other seven match val within noise.
- **$16\%$ fewer tool calls (SE)**: val-only; on held-out-eval SE makes more tool calls than Vanilla ($+7.6\%$).
- **$8$ to $36\times$ human speedup**: budget-matched humans timed out; $36\times$ is one no-cap participant on one task.
- **R as "only main effect that clears noise"**: on data the paper admits was contaminated by the native-plugin-prefix bug.
- **Anonymization breach**: real names in App. K (`Liam`, `Sahchit`).

---

# Part 2: storytelling suggestions

Full file: `storytelling_suggestions.md`.

Two storytelling problems:

1. Method-section local framing (§4 catalog-of-features).
2. Whole-paper global identity (what the paper is *about*).

---

## §4 reads like a feature catalog

Current open: "Our agent is a customization of Claude Code... We add four binary SIGA components..."

Reframe moves:

- Open §4 with the **question**, not the answer.
- Motivate each component by the **failure mode it addresses**, not by what it is.
- Redefine **SIGA as a class of adapters**, not as the specific system you built.
- Promote SE to a separate subsection: "Can the adapter be discovered automatically?"

---

## Three candidate spines for the whole paper

| Spine | Identity | Risk |
|---|---|---|
| **1. Application paper** | Working GEOS assistant + evaluation | NeurIPS says "belongs at geo venue" |
| **2. Empirical study** | Mechanism findings for scientific agents | "methodology isn't novel" |
| **3. Position paper** | Adapt-not-rebuild argument | Needs much sharper claims |

**Recommended**: Spine-1 framing + Spine-2 substance.

---

## Headline numbers: pick three, drop the rest

Keep:

- $+0.07$ mean TreeSim on held-out-eval (cite table).
- $\sim 3\%$ consultation rate (genuinely surprising).
- Wall-clock anchor: $\sim 7$ min agent vs $\sim 3$h human, no cap.

Drop or qualify:

- $40\times$ variance ratio: state mechanism (prevents zero-score outputs).
- $16\%$ fewer tool calls: qualify ("on val only") or drop.
- $8\times$ speedup: humans timed out; $36\times$ no-cap is the honest one.

---

## Foreground the negative findings

The genuinely reusable contributions are buried:

- **Memory-as-retrieval**: a procedural-memory store exposed as a retrievable tool was invoked **zero** times.
- **Consultation rate**: $3.1\%$ across 64 trials; the example library substitutes as a cheaper oracle.

Both are claims about *agents in general*, not just GEOS. Both currently appear after the main quality table.

---

## Minimum-effort 5-item checklist

1. **Fix the anonymization breach.** Non-negotiable.
2. **Rewrite the abstract** to lead with reliability; demote the rest.
3. **Reorder §1 contributions**: cautionary findings up.
4. **Rewrite §4.1 opening**: "we built X" becomes "we investigate a design space."
5. **Re-run F0/F4/F6/SE with the prefix-gate fix** so §5.1 does not rest on contaminated data.

Half a day of writing + ~1.5h compute. The difference between Borderline Reject and Borderline Accept.

---

## Recommended one-liner

> We adapt an off-the-shelf coding agent (Claude Code) to author multiphysics simulation decks for the GEOS geophysics simulator, and empirically identify which standard grounding components, retrieval, schema-validation hooks, and procedural memory, actually make it reliable on this real-world scientific-software task.

Drop from the advisor pitch: "agents need specialized harnesses," "self-validation/self-improvement," the four-sub-studies list.

---

# Part 3: what was adopted

Backup: `old/neurips_2026_pre_storytelling_2026-05-21.tex`. Change log: `changes.md`. Live: `neurips_2026.tex` (compiles, 32 pages).

---

## Adopted: structural

1. **Title** switched: "Adapting Off-the-Shelf Coding Agents for Scientific Simulator Setup: A GEOS Case Study."
2. **Abstract rewritten** to lead with reliability framed as zero-score-failure prevention; trimmed from ~430 to ~250 words.
3. **§1 restructured**: application bottleneck, adapt-vs-build position, design space as object of study, findings, anchors, then contributions in new order.
4. **§4 reframed** as design-space investigation; each R/S/X/M motivated by failure mode addressed.
5. **§4.2 promoted**: SE/SE-prose given their own subsection "Can the adapter be discovered automatically?"

---

## Adopted: results section reordering

6. **§5.1 reordered**: reliability paragraph first; explicit "concentrated in two tasks" caveat in body; R-effect contamination flagged at first mention, not just limitations.
7. **§5.2 memory-as-retrieval** rewritten with stronger reusable-claim framing.
8. **§5.4 autonomy** opens with the $3.1\%$ finding and substitution mechanism.
9. **§6 recommendations** expanded from 4 to 6 bullets (added always-on memory delivery + autonomy-benchmark substitute removal).
10. **§7 conclusion** updated; dropped "factor of forty" framing.

---

## Adopted: integrity + mechanical

11. **Anonymization fix** in App. K.
12. **Unused `\sys` macro** removed.
13. **"16% fewer tool calls"** qualified in both abstract and §5.2 efficiency paragraph (val: $-15.5\%$; held-out-eval: $+7.6\%$).
14. **Em-dash scrub paper-wide**: zero unicode `—`, zero LaTeX `---` remain.

---

## Before vs after

| | Before | After |
|---|---|---|
| Title | Method-paper signal | Application-paper signal |
| Abstract first claim | Six headline numbers | Reliability mechanism |
| §1 contribution order | Benchmark first | Empirical dissection first |
| §4 opening | "We add four components" | "What does the agent need?" |
| §5.1 first paragraph | Numbers | Reliability mechanism |
| Memory finding | Inline aside | Labeled negative result |
| R-contamination | Only in limitations | Flagged at first mention |
| Anonymization | Real names | P1 / P2 |
| Em dashes | 17 + 2 | 0 |

---

## Still to do (not in this pass)

**High priority before arXiv push:**

- Fix `references.bib`: literal `&` in `q&a`; duplicate / malformed entries.
- Re-run F0/F4/F6/SE with prefix-gate fix (~1.5h compute) so §5.1 R-effect statement drops the hedge.

**Medium priority:**

- Refit Fig. 1 and Fig. 2 captions to the "adapter is a class" framing.
- Larger OpenFOAM benchmark + Foam-Agent execute mode.
- Multi-seed cross-model panel.

---

## Files in the pass

- `writing/arxiv/neurips_2026.tex` (live, revised; 32 pages)
- `writing/arxiv/old/neurips_2026_pre_storytelling_2026-05-21.tex` (backup)
- `writing/arxiv/reviews/neurips_review.md` (fresh-context review)
- `writing/arxiv/reviews/reviewer_raw_notes.md` (subagent scratch)
- `writing/arxiv/reviews/storytelling_suggestions.md` (suggestions)
- `writing/arxiv/reviews/one_liner.md` (pitch candidates)
- `writing/arxiv/reviews/paper_notes.md` (Claude reading notes)
- `writing/arxiv/reviews/changes.md` (revision change log)
- `writing/arxiv/reviews/slides.md` (this deck)
