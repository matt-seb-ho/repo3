# Jun 8 changelist — `jun8_v1.tex` (and arXiv copy `arxiv_v1.tex`)

Changes from `jun7_v0.tex` → `jun8_v1.tex`, plus creation of the arXiv preprint build `arxiv_v1.tex`.

`jun8_v1.tex` compiles clean (`pdflatex` + `bibtex`, exit 0, 0 undefined refs).

---

## Edits to `jun8_v1.tex`

### 1. Author block — de-anonymized
- **Before:** `Anonymous Authors`.
- **After:** Matthew Ho, Brian Liu, Jixuan Chen, Audrey Wang, Lianhui Qin (all UC San Diego), laid out with `\And`.
- Note: the NeurIPS template is still loaded without `[preprint]`, so in the submission build these names remain hidden behind the anonymous block; they render in the arXiv build (see §arXiv below).

### 2. Abstract (active/second paragraph) — concrete numbers + tighter claims
Rewritten to lead with headline numbers instead of qualitative phrasing.
- "We primarily **study** GEOS…" → "We primarily **evaluate SIGA on** GEOS…".
- Human-baseline sentence now states the numbers inline: "SIGA produces a complete GEOS deck in about five minutes with TreeSim above 0.90, matching the quality of an extended-budget human expert who required about three hours, a roughly ~36× wall-clock speedup."
- Held-out sentence now gives the TreeSim deltas: "grounding raises TreeSim from 0.720 to 0.789, a roughly 10% relative gain over the bare agent, and can reduce the [across-seed] standard deviation by 16×."
- Self-evolution sentence: "We further show that a self-evolution mechanism (in which the agent edits its own harness)…" → "Self-evolution further improves SIGA by rewriting adapter contents from prior trajectories, yielding the best held-out GEOS performance and outperforming the strongest hand-designed configuration."
- Transfer sentence: "Finally, we additionally explore generalization on two more simulators…" → "Transfers to OpenFOAM and LAMMPS show that the dominant mechanism shifts by interface: validation matters most when structural completeness is the bottleneck, while memory and retrieval matter most when domain correctness is the bottleneck."
- Closing sentence tightened to "lightweight, self-improvable grounding layers can turn general coding agents into practical operators of scientific software."

### 3. Related work — self-evolving-agents paragraph reworded
- Old sentence ("Our self-evolved variant … is fundamentally similar to these methods…") commented out and replaced with a tighter pair: "adopts this reflect-and-rewrite paradigm: the agent revises its own plugin, the adapter, based on prior trajectories. Our focus is different: we study whether such self-revision helps on a task whose bottleneck is domain knowledge and procedural guidance rather than general programming competence."
- Now explicitly connects to Buffer of Thoughts (`yang2024bot`) and forward-references the discussion (`\S\ref{sec:discussion}`).

### 4. NeurIPS checklist input — disabled
- `\newpage \input{checklist.tex}` → commented out (`% \input{checklist.tex}`).

---

## arXiv preprint build — `arxiv_v1.tex`

New file: a copy of `jun8_v1.tex` set up for arXiv. Full recipe in `ARXIV_INSTRUCTIONS.md`. Summary of what differs from `jun8_v1.tex`:

### A. Preprint style option
- `\usepackage{neurips_2026}` → `\usepackage[preprint]{neurips_2026}`.
- This single option reveals the author block, removes submission line numbers, un-hides `\ack`, and changes the page-1 notice from "Submitted to … NeurIPS … Do not distribute." to **"Preprint."** No manual hunting for "neurips" strings is needed.

### B. Authors
- Real author block (same five UCSD authors as `jun8_v1.tex`) placed in the now-visible `\author{}`.

### C. Acknowledgments
- Added a commented-out `\begin{ack} … \end{ack}` template (allowed in preprint mode) for later fill-in.

### D. Content fixes also applied here (SHOULD be back-ported to Overleaf / `jun8_v1.tex`)
These are genuine source bugs, not arXiv-specific:
1. **Broken cross-reference.** The "Hard-tail rescue" paragraph cited `App.~\ref{app:per-task}`, but that label is commented out, so it rendered as `App.~??`. Repointed to `Table~\ref{tab:per-task-icl10}`.
2. **Abstract typo.** `10\% \ relative` had a stray `\ ` (double space) — removed.
3. **Abstract wording.** `roughly $\sim 36\times$` (redundant "roughly"+"~") → `roughly $36\times$`; "reduce the standard deviation across the seed" → "reduce the across-seed standard deviation."

Build verified: 31 pages, 0 undefined references, "Preprint." notice present, authors render.

### Still TODO before posting
- Fill in / restore acknowledgments if desired.
- Back-port fixes D.1–D.3 into the Overleaf source so they don't reappear on the next re-copy.

---
---

# Polishing pass 2 (2026-06-08) — GPT + Claude feedback

Source: `gpt_feedback.md` and `claude_feedback.md`. **All edits below were applied to BOTH `jun8_v1.tex` (Overleaf master) and `arxiv_v1.tex`.** Bibliography fixes are in the shared `references.bib`. Both files recompile clean (32 pp, 0 undefined refs/citations, no LaTeX errors).

> **Guardrail honored:** the advisor approved the previous pass and is protective of the **abstract and intro**. I left the abstract **completely untouched** and made exactly **one** intro edit — a factual variance→SD correction (item E1 below). Everything the feedback wanted done to the abstract is in the "**Flagged, NOT changed**" list at the bottom for your/her decision.

## A. Clear factual errors fixed

| # | Where | Before → After | Source |
|---|-------|----------------|--------|
| A1 | §5.2 split arithmetic | "46 tasks are split into 10 + 18 + 17" (=45) → "From the 46-task pool we reserve 10 / 18 / 17 …, **dropping one task**." | GPT 2, Claude 4 |
| A2 | App G.3 harness-less | vanilla CC on minimax "recovers **+0.164**" → "**+0.488**" (Table 7 gives 0.821 vs the 0.333 floor; +0.164 was stale). | Claude 1 |
| A3 | §6.1 Resolution-IV main effects | "R Δ=**−0.032**; X, M, S within **±0.007**" → recomputed over the 8 fractional cells: "**R −0.037**; X +0.011, M +0.008, S −0.008, all within **±0.011**." (Old numbers didn't reconcile with Table 1.) | Claude 6 |
| A4 | Table 10 (App I) extended row | "GEOS docs **89**, GitHub 21, Search 6, Other **7**" (sum 123 ≠ 106) → "docs **73**, GitHub 21, Search 6, Other **6**" (sum = 106). Derived from the verified aggregates in the data/text: total 106, GEOS-internal 94 (= 73 docs + 21 GitHub), search 6, other 6 (the round's 69 GEOS-internal + 8 non-GEOS on top of the original 29). | Claude 2 |
| A5 | Table 3 (OpenFOAM) caption | "The first **nine** rows are the SIGA 2^{4-1} cells" → "**Eight** rows form the Resolution-IV 2^{4-1} fraction and S+X+M is an additional hand-selected cell (nine SIGA cells total)." | GPT 3 |
| A6 | Table 4 (LAMMPS headline) caption | Noted that for Claude, **M+R and M+R+S+X tie at 6.89** (we list M+R). | GPT smaller |

## B. Related work / citations

| # | Where | Change | Source |
|---|-------|--------|--------|
| B1 | §2 MD-agents list | Removed **`kim2024mdagents`** (MDAgents is medical decision-making, not molecular dynamics). | GPT 4 |
| B2 | `references.bib` `cursor2026composer2` | `author={Cursor Research …}` → `author={{Cursor Research} …}` so the corporate author renders as "**Cursor Research et al.**" not "Research et al." | GPT 4 |
| B3 | `references.bib` `yue2025foamagent` | `year={2026}` → `year={2025}` (Foam-Agent, arXiv:2505.04997, is 2025). | GPT 4 |

## C. New content — the two biggest reproducibility gaps

| # | Where | Added | Source |
|---|-------|-------|--------|
| C1 | §5.3 + new App "TreeSim: full definition" (`app:treesim`) | Formal TreeSim definition with an equation (Eq. `treesim`): node = `tag[name]`; Jaccard attribute similarity (string/numeric-tolerance value match); **unordered** bipartite child matching; node score `s = αa + (1−α)·s̄_child − β·extra/(gt+extra)`, α=0.3, β=0.1; `<Included>` resolution + file-merge → file-/deck-level; per-section = top-level children. Points to scorer `src/eval/judge_geos.py`. Grounded in the actual scorer code. | GPT 1 |
| C2 | §4.3 ref + new App "Self-evolution pipeline details" (`app:selfevolve`) | Proposer = **deepseek-v4-flash**; **3 sequential greedy rounds** (v0→v3) over the 17-task validation-selection split partitioned into cohorts of **6/6/5**, single run per task; selection = mean TreeSim per cohort; held-out-eval never seen. New **Table `se-configs`** enumerating exactly what differs among S+X+M / SE-prose / SE (primer, cheatsheet, auxiliary skills, evolution rounds). Grounded in `scripts/self_evolving/{run_full_evolution.sh,reflect.py}` + design doc. | GPT 6 |

## D. Wording softened to match what the system actually does (results sections only — NOT the abstract)

| # | Where | Change | Source |
|---|-------|--------|--------|
| D1 | §6.2 | "counts drop … **since schema validation requires these blocks** and the cheatsheet enumerates them" → "…; the cheatsheet enumerates these canonical blocks and the validator's structural pressure discourages finishing without them" (xmllint checks XSD validity, not task-required-block presence). | GPT 5 |
| D2 | §5.3 | dropped "executable" from "returned workspace is **executable** or at least structurally inspectable" → "…is at least structurally inspectable." | GPT 5 |
| D3 | RQ5 (OpenFOAM) answer box | native agents "leave 8–12 tasks…" → "**in our lint-only reproduction**, leave 8–12 tasks…" (don't claim the native agents fail in general). | GPT 5 |

## E. Smaller corrections & layout

| # | Where | Change | Source |
|---|-------|--------|--------|
| E1 | **Intro** finding (2) | "cuts score **variance** by about 16×" → "cuts across-run **standard deviation** by about 16×" (16× is the σ ratio). *The one intro edit; purely factual.* | Claude 5 |
| E2 | App A terminology | "**ICL pool**" → "**held-out-evaluation pool**" (+ noted it's the same ten as held-out-eval, never used as demos); "17-task **test set**" → "17-task **validation-selection set**." | GPT 2, Claude 11 |
| E3 | §5.2 | "the full factorial … at the cost of **4× the runs**" → "**substantially more** runs" (the 4× was contestable). | GPT smaller |
| E4 | §6.1 | "(Table 6, **§6.1**)" self-reference → just "(Table `per-task-icl10`)". | GPT smaller |
| E5 | Table 3 (OpenFOAM) caption | clarified Est. cost is the **per-row total over all 30 tasks**. | GPT smaller |
| E6 | §6.6 | "on Claude all effects are within **±0.5**" → "small (**at most 0.52** in magnitude)" (R=+0.52 exceeded the stated bound). | Claude 7 |
| E7 | Table 5 (bottleneck) caption | noted all-zero/unreported categories (`no_failure`, `wrong_constitutive`) are omitted; made per-cell n explicit. | GPT smaller |
| E8 | §6.3 | "graduate level" → "graduate-level". | GPT smaller |
| E9 | preamble | added `\hypersetup{hidelinks}` — removes the colored boxes around links/citations/URLs. | GPT PDF/layout |

## Flagged, NOT changed — your / advisor's call (all touch the ABSTRACT, or a figure)

1. **Abstract "outperforming the strongest hand-designed configuration"** (GPT 6, Claude 8). SE 0.789±0.012 vs S+X+M 0.783±0.022 at n=3 is within noise; the intro already says "matches." Recommended: change "outperforming" → "matching"/"the highest observed mean." *Left for the advisor since it's the abstract.*
2. **Abstract "executable configurations" / "complete GEOS deck" / "practical operators"** (GPT 5). Reviewer may read these as runnability claims, which TreeSim doesn't establish. Recommended softening (e.g. "schema-valid / structurally complete decks"). *Abstract — left alone.*
3. **Abstract "a harder held set" → "a harder held-out set"** (GPT smaller). Trivial, but it's in the abstract.
4. **Figure 2** shows "simulation outputs" / "post-process artifacts" though decks aren't executed (GPT 5). Can't fix in TeX — needs the figure source (`assets/siga_f2.png`) regenerated or those boxes marked out-of-scope.

## Deliberately skipped (minor, per your "mostly ignore")
- Claude 3 (Expert 1 file-level 0.812→0.689 in the longer session) — you said no explanation needed; left as-is.
- Claude 9, 10, 12; GPT's "ten canonical sections includes Functions, omits Tasks" — left as-is.

---

## Pass 2 follow-up (2026-06-08, per your questions)

- **Self-evolution appendix REMOVED.** Deleted the new `app:selfevolve` section and `tab:se-configs` table (C2 above) and the one-sentence pointer to it in §4.3. Self-evolution is back to the previous (vague) treatment while you keep working on it. The self-evolution *equation* (Eq. 2, `eq:selfevolve`) and the SE/SE-prose method paragraphs are unchanged.
- **SE verb harmonized to "matches or outperforms"** in BOTH abstract and intro:
  - Abstract: "yielding the best held-out GEOS performance and **outperforming**…" → "yielding the **highest held-out GEOS mean** and **matching or outperforming** the strongest hand-designed configuration."
  - Intro finding (3): "**matches** the best hand-designed configuration" → "**matches or outperforms** the best hand-designed configuration."
- **Abstract "a harder held set" → "a harder held-out set"** (flagged item #3, now done).
- **Synced jun8 abstract to arxiv:** fixed the stray `10\% \ relative` and "standard deviation across the seed" and the redundant `$\sim 36\times$` in `jun8_v1.tex` (these were previously fixed only in `arxiv_v1.tex`). Abstracts now identical across the two files.
- **Still open / flagged:** abstract "executable configurations / complete deck / practical operators" (#2) and Figure 2 "simulation outputs / post-process artifacts" (#4) — untouched, awaiting your call.

Both files recompile clean (31 pp, 0 undefined refs).

