# Paper Revision Pass: 2026-05-21

Backup of pre-revision draft: `old/neurips_2026_pre_storytelling_2026-05-21.tex`. Live edits are in `neurips_2026.tex`. This document tracks every change with rationale.

Storytelling recommendations are referenced as **[S#]** where the source is `reviews/storytelling_suggestions.md`.

## Status: complete

Compile sanity check: `pdflatex neurips_2026.tex` (single pass with existing .bbl) succeeds, EXIT=0, 32 pages output. A clean rebuild via `bibtex` triggers a pre-existing `Misplaced alignment tab` error in `references.bib` (literal `&` in a title that needs escaping as `\&`); this is not caused by this revision pass and should be fixed separately in `references.bib`.

Tasks executed in order of leverage:

1. [x] Anonymization breach in App. K (real names → P1/P2). Critical for blind review.
2. [x] Title switched to Application-track framing.
3. [x] Abstract rewritten to lead with reliability framed as zero-score-failure prevention; oversold numbers qualified or removed.
4. [x] §1 restructured: application size, position paragraph (adapt vs build), design space as object of study, headline finding, two cautionary findings, anchors, then contributions in new order.
5. [x] §4.1 reframed from "we built SIGA" to "design-space components"; each R/S/X/M component now motivated by the failure mode it addresses.
6. [x] §4.2 (SE/SE-prose) promoted to its own subsection titled "Can the adapter be discovered automatically?"
7. [x] §5.1 reordered: reliability paragraph promoted to first; "concentrated in two specific tasks" caveat made explicit; R-effect data contamination flagged in body, not just limitations.
8. [x] §5.2 (memory-as-retrieval negative result) rewritten with a stronger reusable-claim framing.
9. [x] §5.4 (autonomy) reframed to lead with the consultation-rate finding and the substitution mechanism.
10. [x] §6 (Discussion) recommendations expanded from 4 to 6 bullets, integrating the memory-interface and consultation-substitute findings; limitations paragraph expanded with the two-task concentration and human-baseline n=2 caveats.
11. [x] §7 (Conclusion) updated to match new framing and drop "factor of forty" framing.
12. [x] Unused `\sys` macro removed.
13. [x] All em dashes scrubbed paper-wide (advisor stylistic preference). Confirmed via `grep`: zero unicode em dashes and zero LaTeX `---` remain in `neurips_2026.tex` or `checklist.tex`. In-table `---` (null-cell markers) replaced with `--` (en-dash). Section headings with `—`/`---` replaced with colons. Prose em dashes replaced contextually with commas, semicolons, colons, or parentheses depending on the case.
14. [x] "16% fewer tool calls" claim qualified in both abstract and §5.2 efficiency paragraph; the abstract now states the val-only direction, and §5.2 reports both splits (`-15.5%` val, `+7.6%` held-out-eval).

## Change log

### C01 — App. K participant anonymization
**File**: `neurips_2026.tex` ~line 611 and ~625–626.
**Rationale**: Anonymization breach flagged in `neurips_review.md` and `storytelling_suggestions.md` Part 3 (1). Real names ("Liam", "Sahchit") were in the .tex source. This is a desk-reject-class issue under blind review.
**Edit**: Replace "Liam" → "P1", "Sahchit" → "P2" wherever they appear in App. K prose and table caption.

---

## Change log

### C01 — App. K participant anonymization
**File**: `neurips_2026.tex` ~line 611 and ~625–626.
**Rationale**: Anonymization breach flagged in `neurips_review.md` and `storytelling_suggestions.md` Part 3 (1). Real names ("Liam", "Sahchit") were in the .tex source. This is a desk-reject-class issue under blind review.
**Edit**: Replace "Liam" → "P1", "Sahchit" → "P2" wherever they appear in App. K prose and table caption.

### C02 — Title change
**File**: `neurips_2026.tex` line 52.
**Rationale**: `storytelling_suggestions.md` Part 3 (5) — current title reads as a method paper; the commented-out alternative on lines 50–51 is closer to the Application-track framing. Picked a moderate variant that drops SIGA from the title while keeping it in the body as a design-space term.
**Old**: "Simulator-Interface Grounding Adapters for Scientific Simulation Setup: A Geophysics Case Study"
**New**: "Adapting Off-the-Shelf Coding Agents for Scientific Simulator Setup: A GEOS Case Study"

### C03 — Drop unused `\sys` macro
**File**: `neurips_2026.tex` lines 46–48.
**Rationale**: `storytelling_suggestions.md` Part 3 (2). The `\sys` macro defined as `\textsc{GeoAgent}` is never used in the body. Removing dead code; if a system noun is needed later, define it then.

### C04 — Abstract rewrite
**File**: `neurips_2026.tex` lines 66–68.
**Rationale**: `storytelling_suggestions.md` Part 2 ("Lead with reliability, not quality"; "Headline numbers: pick three, drop the rest"; "Honesty moves"). Current abstract throws 6 headline numbers; the 40×/16%/8× framings are oversold relative to the underlying data. Reframe to lead with the reliability finding stated in terms of zero-score-failure prevention, qualify the 16% claim (val-only; reverses on held-out-eval), state the cautionary findings (memory-as-retrieval, consultation rate) as headline contributions, and lead the OpenFOAM transfer with the stop-hook mechanism rather than the absolute numbers.

### C05 — §1 (Introduction) restructure
**File**: `neurips_2026.tex` lines 71–95.
**Rationale**: `storytelling_suggestions.md` Part 2 ("Spine 1 + Spine 2 hybrid"). Open with the application size; add a position paragraph on adapting vs building from scratch; frame R/S/X/M as a design space rather than a system; reorder contributions so the empirical dissection and the two cautionary findings precede the OpenFOAM bullet; replace "definition + evaluation of SIGA" framing of contribution (ii) with "empirical dissection of which grounding components matter."

### C06 — §4 (Method) reframe
**File**: `neurips_2026.tex` lines 115–162.
**Rationale**: `storytelling_suggestions.md` Part 1. Replace §4.1 opening from "we built SIGA" to "we investigate a design space of grounding components"; motivate each R/S/X/M component by the failure mode it addresses, not by what it does; redefine "SIGA" as the class of grounding adapters, not as the specific system; promote SE/SE-prose to a separate paragraph framed as "can the adapter be discovered automatically?"

### C07 — §5.1 honesty moves
**File**: `neurips_2026.tex` lines 178–211.
**Rationale**: `storytelling_suggestions.md` Part 2 ("Honesty moves that strengthen the paper"). Add an explicit sentence in §5.1 that the held-out-eval gain is concentrated in two specific tasks. Flag the R-effect data contamination in body, not just in §6 limitations. Replace the "40× variance" framing with "prevents zero-score outputs on the same tasks" framing.

### C08 — §5.2.3 (Memory-as-retrieval) foregrounding
**File**: `neurips_2026.tex` lines 219–221.
**Rationale**: `storytelling_suggestions.md` Part 2 ("Foreground the negative findings"). Promote this paragraph to a labeled subsection-style heading and expand the reusable framing. Already a clean negative result; current framing buries it.

### C09 — §5.4 (Autonomy) foregrounding
**File**: `neurips_2026.tex` lines 227–232.
**Rationale**: Same as C08. The 3.1% consultation rate is one of the paper's most reusable contributions. Reframe the opening to commit to the finding before introducing protocol.

### C10 — Qualify "16% fewer tool calls" claim
**File**: `neurips_2026.tex` abstract (line 67) and §5.2 efficiency paragraph (line 218).
**Rationale**: `storytelling_suggestions.md` Part 1 + paper_notes.md observation. Currently the abstract says "matches the best hand-designed cell with roughly 16% fewer tool calls" without qualifiers. Cross-check against Table 9 (`app:results`): on held-out-eval, SE makes *more* tool calls than Vanilla (97.4 vs 90.5). Qualify or remove from abstract; add the both-splits statement to §5.2.

### C11 — §6 (Discussion) reorder + recommendations expansion
**File**: `neurips_2026.tex` lines 263–275.
**Rationale**: Discussion opens with "what transfers across simulators", fine, but the design-recommendations paragraph (which is the paper's prescriptive output) should sit closer to the mechanism statement. Reorder so that the cross-simulator finding leads naturally into the recommendations. Limitations paragraph expanded with the two-task-concentration caveat and the human-baseline `n=2` caveat (per storytelling Part 2 honesty moves).

### C13 — Round 2: advisor-style intro + abstract refresh + §5 reorder (same day)

**Rationale**: After the first revision pass, the advisor's stylistic and structural preferences were articulated more sharply:

- **Intro format**: pure prose, no `\paragraph` headers, no bullets or lists. Standard scientific intro flow: (¶1) problem/background, (¶2) gap/situating, (¶3) method/contribution, (¶4) results, (¶5) wrap up.
- **Intro content**: explicitly name simulation as common across many fields (physics, medicine, chemistry, biology, etc), drop extraneous GEOS detail (LLNL provenance, ten-section structure, deck syntax), motivate why GEOS specifically is worth automating. Domain → tooling, broad → narrow.
- **Framing change**: drop "deck authoring." Reframe as "operating any scientific software amounts to learning its domain-specific language (DSL); simple tools are basic function calls; powerful software demands a more expressive DSL."
- **Abstract**: less defensive, no apologetic qualifications. Don't hide negatives, just don't put them in the abstract. Drop "10-task hard tail" and "5-task OpenFOAM" specific qualifiers (call them "pilot" instead). Include the human baseline, currently missing.
- **§5 subsection order**: human baseline before autonomy before OpenFOAM (human anchors GEOS, autonomy is on GEOS, OpenFOAM is the cross-simulator generalization).

**Edits**:

- **§1 (Introduction) fully rewritten as five-paragraph prose.** Removed all six `\paragraph{...}` headers and the bulleted contributions list. New paragraph structure: (¶1) simulation across many scientific fields + DSL framing; (¶2) gap (existing agents reimplement orchestration from scratch); (¶3) method on GEOS, SIGA design space, SE variant; (¶4) results, including human baseline as a co-anchor; (¶5) wrap-up in prose.
- **Abstract rewritten** to lead with the simulation-is-everywhere framing and to surface human baseline. Pilot-scale language replaces specific small-n numbers (5 tasks → "pilot", 10-task tail dropped). Word count: 297 (vs ~250 prior, ~430 original).
- **§5 subsections reordered** to: human baseline → autonomy → cross-simulator transfer. The human baseline takes priority; autonomy and OpenFOAM swap because autonomy is on GEOS while OpenFOAM is generalization beyond GEOS.

**Compile check**: pdflatex single-pass exits 0, 32 pages, 0 em dashes anywhere in `neurips_2026.tex`, 0 `\paragraph` commands in §1.

### C12 — Em-dash scrub paper-wide
**Files**: `neurips_2026.tex` (multiple locations).
**Rationale**: Advisor stylistic preference, raised mid-pass.
**Edit**: All em dashes (both unicode `—` and LaTeX `---`) replaced. Section headings: colons. Prose: contextual commas/semicolons/colons/parens. In-table null-cell markers (`---`) replaced with `--` (en-dash, the standard scientific-table notation for null). Verified by `grep` to zero remaining instances in `neurips_2026.tex` and `checklist.tex`.

---

## What's left for future passes

These are not part of this revision (they require compute, design decisions, or a co-author conversation), but they were identified by the review and should be on the queue:

### High priority (do before arXiv submission)

- **Fix `references.bib` `&` escape.** BibTeX fails on `knowledge q&a` (literal `&`); should be `q\&a`. Other entries (line 146, 254, 354 of `references.bib`) have missing field names and repeated entries (foamagent2025, li2025seismologyagent, moyner2026jutulgpt). Estimated time: 30 min.
- **Re-run F0/F4/F6/SE on DSv4 × val at 3 seeds with the native-plugin-prefix-gate fix.** App. M (`app:future-work`) lists this as `~1.5h wall-clock, low API spend`. The §5.1 R-effect statement currently hedges with the contamination caveat; a clean estimate would let us state it without hedge or remove R from the headline entirely. Cheapest single experiment with the biggest reviewer-credibility return.

### Medium priority (do for the camera-ready / next submission)

- **Re-cut Fig. 1 caption.** Still says "Comparison of manual and Simulator-Interface Grounding Adapter (SIGA) workflows." Under the new framing SIGA is a class of adapters, not "the SIGA workflow." Suggested edit: "Comparison of manual deck authoring (a) and an adapter-augmented agent workflow (b)..." Minor.
- **Fig. 2 caption.** Currently "Execution trace of the SIGA agent loop." Same critique. Could read "Execution trace of an adapter-augmented agent (cell X+M)..."
- **Multi-seed cross-model panel.** App. M follow-up. Cost-limited by gemini-3-flash pricing. Strengthens the cross-model claim if budget allows.
- **Larger OpenFOAM benchmark.** Move from 5 tasks `n=1` to 20+ tasks multi-seed. Would convert the transfer claim from qualitative to quantitative.
- **Foam-Agent execute-mode comparison.** Currently the Foam-Agent baseline is constrained to `lint_only` because execute mode failed in our environment. This is the single biggest weak point a reviewer attacked in the fresh-context review.

### Low priority / cosmetic

- **Drop `xspace` package** if no command uses it (was loaded for `\sys`, which is now removed).
- **Skim the older title comments** at lines 50–53 of the .tex; if the team agrees on the new title, the commented-out alternatives can be removed.
- **Section title `\label{sec:discussion}\label{sec:analysis}\label{subsec:limitations}`** triple-labels the same section. The last label name is misleading because the section is more than its limitations. Pick one canonical label and update any cross-references.

## Summary of what reviewers should see now versus what they saw before

| | Before | After |
|---|---|---|
| **Title** | "Simulator-Interface Grounding Adapters for Scientific Simulation Setup: A Geophysics Case Study" (reads as method paper) | "Adapting Off-the-Shelf Coding Agents for Scientific Simulator Setup: A GEOS Case Study" (reads as application paper) |
| **Abstract first claim** | "$40\times$ reliability + $+7$pp quality + $16\%$ fewer tool calls" (six headline numbers) | "Reliability dominates; lift is concentrated in two specific hard tasks" |
| **§1 contribution order** | benchmark, SIGA evaluation, cautionary findings, OpenFOAM | empirical dissection, cautionary findings, benchmark, OpenFOAM, self-evolved variant |
| **§4 framing** | "We add four SIGA components..." | "What does a general-purpose coding agent need on top of itself? We investigate a four-component design space..." |
| **§5.1 first paragraph** | "Cells cluster narrowly on val..." (numerical) | "Reliability is the largest visible adapter effect" (mechanism-first) |
| **Memory-as-retrieval finding** | Inline note at end of §5.2 efficiency paragraph | Promoted to a labeled negative-result subsection with explicit "interface as load-bearing as substance" claim |
| **Consultation-rate finding** | Mentioned in §1, restated in §5.4 with protocol-first opening | §5.4 opens with the finding, the substitution mechanism is stated up front |
| **R-effect contamination** | Mentioned only in limitations | Flagged in body at §5.1 where the negative effect is first reported |
| **Anonymization** | Real names in App. K | Replaced with P1/P2 |
| **Em dashes** | 17 LaTeX em-dashes + 2 unicode in body | Zero (paper-wide scrub) |

## Files in this pass

- `writing/arxiv/neurips_2026.tex` — live, revised
- `writing/arxiv/old/neurips_2026_pre_storytelling_2026-05-21.tex` — pre-revision backup
- `writing/arxiv/reviews/changes.md` — this file
- `writing/arxiv/reviews/neurips_review.md` — fresh-context NeurIPS-style review (input to this pass)
- `writing/arxiv/reviews/storytelling_suggestions.md` — storytelling recommendations (input to this pass)
- `writing/arxiv/reviews/one_liner.md` — one- and two-line summary candidates (separate artifact)
- `writing/arxiv/reviews/paper_notes.md` — Claude Code reading notes (separate artifact)
- `writing/arxiv/reviews/reviewer_raw_notes.md` — fresh-context subagent's scratch notes (separate artifact)
