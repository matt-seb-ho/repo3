# Session prompt — Draft the four rebuttal responses

*Paste this into a fresh session started in `/home/matt/sci/repo3`.*

---

## Context

NeurIPS 2026 author response, submission 31642 (SIGA). Scores: **gep1 4** (borderline accept, conf 3) · **kEdh 2** (reject, conf 4) · **nBNe 5** (accept, conf 5) · **AC: borderline**.

Read first, in this order:
1. `neurips_review/neurips_timeline_instructions.md` — the rules. Read them literally.
2. `neurips_review/siga_neurips_reviews_clean.md` — the reviews and meta-review
3. `neurips_review/SIGA_weaknesses.md` — deduped weakness list
4. `neurips_review/SIGA_rebuttal_execution_plan.md` — our positions, with evidence
5. `neurips_review/MASTER_TODO.md` — what has cleared and what hasn't

## Hard constraints

- **No revisions to the paper or supplementary material.** The original submission is the basis for the decision. There is no revised PDF this year.
- **10,000 characters per review.** Plain text with markdown. No file uploads, no images, no links.
- **Anonymity.** Nothing that could identify the authors.
- **Deadline Jul 27** for the initial response. Authors can keep posting through **Aug 3**; Phase 3 (Aug 3–10) is reviewer/AC only.

## Deliverables — four texts, not three

| Target | Budget | Priority order |
|---|---|---|
| **gep1** | ~9,500 chars | execution/validity ladder → prefix bug + S/X isolation → OpenFOAM → human baseline → limitations wording |
| **kEdh** | ~7,000 | definitions and worked examples inline → camera-ready plan → one line on venue |
| **nBNe** | ~3,500 | answer their three questions, concede gracefully, **change nothing else** |
| **AC** | ~5,000 | the four meta-review bullets, in the AC's own order |

**gep1 is the winnable score** — he wrote two explicit conditionals and is one point from accept. **kEdh will probably not move**; their function now is as ammunition for the AC. **nBNe is at 5** — do not re-argue novelty, do not give them new reasons to think.

The handbook says *"use the initial meta-review as your guide."* The AC's four bullets are the spec, not the union of all reviewer asks.

## Content — what to say where

**Execution / physics validity (gep1 score-moving, nBNe, AC primary).** Lead with the distinction the paper currently blurs: the headline is a **reliability** claim (σ 0.081 → 0.002, catastrophic-failure reduction), and you do not need physics to know an empty or unparseable file doesn't run. Only the mean-lift claim depends on TreeSim's semantics. Then present the validity ladder: rungs 1–2 done (schema validity: Vanilla 24/30 vs 30/30 for SIGA cells), rungs 3–5 named. State both caveats yourself — (a) S and X cells invoke `xmllint` so 30/30 is partly true by construction, with X+M the least circular cell; (b) effective n is well below 30, since the 6 Vanilla failures span only 4 distinct tasks and cluster by seed.

On determinism, use this framing and **not** "deterministic ⇒ input-side eval is fair" (a reviewer will bounce that):

> The deck is a sufficient statistic for the simulation — no hidden state, no stochasticity. Deck authoring is therefore a well-posed target of study, and the open question is the metric on decks, not the choice to evaluate decks.

On non-uniqueness ("another deck could produce the same physics"), lead with the common-mode argument: TreeSim penalizes correct-but-different decks for *every* cell equally, so it depresses the absolute level and leaves the *contrast* intact. It attacks "SIGA scores 0.78," not "SIGA beats Vanilla by 0.069."

**S/X confound (gep1 score-moving).** Say Resolution-IV *does* separate main effects — the design is sound. What it cannot give is the S×X interaction, aliased with R×M. Then give the direct answer from the existing build-up ablation: `C2→C6` (hook-enforced validator) = **+0.008**, `C6→C7` (agent-callable validator on top) = **−0.007**. X adds nothing once S is on. Caveat honestly: val-only, and val is at ceiling.

**Prefix bug (gep1 score-moving).** Ground the dismissal empirically, not chronologically. We built a dedicated probe: C2 (prefix) 0.9134 vs C9 (no prefix) 0.9170, **Δ = +0.0036**, zero big-swing tasks, 3 seeds × 17 tasks. Note both bias directions favour the paper. Disclose the SE/SE-prose asymmetry before being asked.

**Scale (all three + AC).** Take the trade the AC explicitly offered: bootstrap intervals on existing data, argue representativeness of the hard tail, and **explicitly narrow** the robustness/generalization claims. Report OpenFOAM at 30 tasks and handle the reversal openly. LAMMPS only for nBNe and the AC's scale bullet, labelled preliminary.

**Human baseline.** Concede. Reframe as "preliminary calibration" — the AC's own phrase.

**Clarity (kEdh primary, AC).** Show the rewritten text inline rather than promising it — definitions of "deck," Resolution-IV, Buckley–Leverett, the failures-as-zero sentence, plus one worked example each of a "brief" and of "structured repair feedback." Then aim this argument at the AC: *clarity is the only weakness on the table that is certain to be fixed; evidence gaps depend on experiments that may not land or may come out negative. A certain fix should be weighted differently from a hoped-for one.*

**Claude Code version (nBNe).** `2.1.119`. Add the honest concession that the Docker image installed it unpinned, so the version tracked build time — which is exactly nBNe's point.

**Venue (kEdh).** One non-defensive sentence to the AC. Do not litigate.

## Rules that must not be broken

1. **Every number traces to a file on disk.** No number from a summary doc, a memory, or another agent's report. gep1 recomputes things. A wrong number in a rebuttal is unrecoverable.
2. **Never pair a mean from one cell with a σ from another.** The submitted abstract pairs "+7pp" (SE) with "40×" (S+X); SE's own ratio is ≈6.75×. Nobody has raised it and it is defensible in the paper as "best cells" plural, so **do not volunteer it** — but print the per-cell σ table (Vanilla 0.081 · X+M 0.005 · S+X 0.002 · SE 0.012) and let the reader match ratio to cell. If asked in Phase 2, answer straight.
3. **Do not oversell schema validity as answering the execution ask.** It is rung 2 of 5. The AC made execution the decision criterion and gep1 checks things. This is the single highest-risk move available.
4. **Do not claim Table 1 is post-prefix-fix.** It isn't — the fix landed 2026-05-03, the factorial ran 2026-05-01/02. Only minimax × X+M was re-run.
5. **Do not say the bug fix produced the arXiv main-effects numbers.** It didn't. One cell's mean was revised and the appendix table was never regenerated. The main effects are fully determined by the eight cell means, so any reviewer can check.
6. **Never quote "+0.24"** for the prefix effect. The measured value is **+0.004**; +0.24 was the C1→C2 lift being *explained*. Several internal docs still carry the error.
7. **Paraphrase the arXiv text; do not paste it verbatim** unless Lianhui confirms the preprint is not publicly posted. A distinctive sentence is searchable and would lead a reviewer to a non-anonymous version.
8. **Nothing pending may be load-bearing.** The Jul 27 response must stand entirely on evidence already verified. Anything from the execution or LMaaJ sessions goes in later as a follow-up comment.
9. **Do not promise a delivery date** for the execution study. A missed promise lands right before Phase 3, when we can no longer respond.

## Before drafting — check these have cleared

From `MASTER_TODO.md` P0. If any is open, either resolve it or leave that claim out:

- [ ] F3 (R+S) resolved: 0.874 or 0.857, and why it moved
- [ ] All derived tables regenerated and diffed against the paper
- [ ] Schema-validity ladder verified against `/data/shared/...`
- [ ] Claude Code version confirmed from an autocamp `events.jsonl`
- [ ] Lianhui's answers on: R2 posture, arXiv posting status, volunteering the main-effects correction, pre-empting the human-baseline anomaly

## First step

Read the four documents listed at the top, then produce **an outline of each of the four responses with character budgets per section** — before writing any prose. Show me the outlines. Getting the allocation right matters more than the wording; gep1's response is the one worth 9,500 characters of care.
