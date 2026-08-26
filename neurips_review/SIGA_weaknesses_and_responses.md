# SIGA (NeurIPS 2026) — Weaknesses and How We Plan to Respond

**R1** = gep1 (4, borderline accept) · **R2** = kEdh (2, reject) · **R3** = nBNe (5, accept) · **AC** = borderline.

The AC says the decision turns on two things: **(a)** does structural improvement translate to *executable, scientifically valid* simulations, and **(b)** can we substantially improve clarity. Everything else is secondary.

---

## The main question for you

**We are not allowed to revise the paper.** NeurIPS 2026 rules: no revised PDF, no supplementary changes, no uploads, no links — responses are plain text in OpenReview only (10k characters per review), and the original submission stays the basis for the decision.

That's a problem for **R2**, whose whole review is "this paper is not written well." We spent two months rewriting it for arXiv, and that rewrite fixes roughly 70% of what R2 complains about — a defined "input deck" in the abstract's first sentence, Resolution-IV motivated in plain prose, TreeSim formally defined. **None of it can be shown to them.** We can't submit it, upload it, or link it (and a link would break anonymity).

**What we propose:** paste the actual rewritten sentences *inline* in the response — show the text rather than promise it — and then aim the argument at the AC, not at R2:

> Clarity is the only weakness on the table that is *certain* to be fixed. The evidence gaps depend on experiments that may not land or may come out negative. A definition or a worked example is a certainty within camera-ready scope. A certain fix should be weighted differently from a hoped-for one.

R2 is at 2 with confidence 4 and realistically will not move; their function now is as ammunition for the AC, who independently endorsed the complaint. **Does that posture seem right to you, and how strongly can we commit to the camera-ready rewrite in writing?**

---

## The weaknesses and our plans

| # | Weakness | Raised by | Our plan | Need your call? |
|---|---|---|---|---|
| 1 | **Evaluation is structural (TreeSim) only** — doesn't show decks run, converge, or are physically meaningful | R1\*, R3, **AC (primary)** | **We have a working GEOS binary**, so we can now actually run the decks. Plan: (a) report schema validity — Vanilla **24/30** vs **30/30** for every SIGA cell; (b) run the decks through GEOS and report how many validate, run, and converge; (c) a small case study plotting simulation outputs against TreeSim, to show what a TreeSim gap means physically; (d) add an LLM-judge metric for semantic plausibility, which TreeSim cannot capture. | Yes — Q3 |
| 2 | **Jargon / unreadable for a general audience** | **R2 (primary)**, AC | Paste replacement text inline for each of their items: "deck", Resolution-IV, Buckley–Leverett, the failures-as-zero sentence, plus one verbatim example each of a "brief" and "structured repair feedback." Commit the full rewrite to camera-ready. | Yes — main question above |
| 3 | **Small scale** (10 held-out tasks × 3 runs) | R1, R3, AC | Take the trade the AC explicitly offered: argue the held-out tasks are the hard tail where the effect lives, add bootstrap intervals on existing data, and **narrow the robustness/generalization claims**. No new runs. | — |
| 4 | **Human baseline too small** (n=2, one task) | R1, R3, AC | Concede. Reframe as **"preliminary calibration"** (the AC's own words) on a tutorial-level task. R3's ask for multiple expertise levels + a collaborative setting goes to future work. | Q6 |
| 5 | **OpenFOAM transfer under-powered** (5 tasks, 1 run, lint-only baseline) | R1, AC *(R2 and R3 call transfer a strength)* | Report our **30-task** campaign with a second baseline, plus the LAMMPS study as extra task diversity for R3. Keep transfer claims **explicitly qualitative**, which is R1's own stated fallback. Decline Foam-Agent execute mode (fails in our env; R1 permits this). | Yes — Q2 |
| 6 | **S and X confounded** — both involve validation | R1\* | **We can already answer this.** Our build-up ablation isolates them one at a time: adding the hook-enforced validator (S) gives **+0.008**; adding the agent-callable validator (X) on top gives **−0.007**. So X adds nothing once S is on — which is exactly R1's question. Caveat: this is on the easy split only. | — |
| 7 | **Native-plugin-prefix bug** contaminated retrieval estimates | R1\* | **No rerun needed.** We built a dedicated probe for this before submission: removing the prefix moves scores by **+0.004** (3 seeds × 17 tasks, no task affected by more than 0.1). Disclose it as a process note, show the measurement. Separately, volunteer a correction to the main-effects table — the corrected numbers make our own findings *stronger*. | Yes — Q4 |
| 8 | Limitations should say "structural reliability, not validated correctness" | R1 | Write exactly that sentence in the response and commit it to the camera-ready main body. Free. | — |
| 9 | Exact Claude Code version not reported | R3 | Report it: **2.1.119**. Also concede honestly that our Docker image installed it unpinned, so the version tracked build time — which is exactly R3's point. | — |
| 10 | Venue fit (eScience vs NeurIPS) | R2 | One non-defensive sentence to the AC, then stop. R2 already called it the committee's call. | — |
| 11 | No new agent architecture | R3 (minor) | Answer briefly. R3 rated us **5 despite** this — don't over-argue and give them new reasons to think. | — |

\* = reviewer said explicitly this would move their score or confidence.

---

## Questions for you

1. **R2 / clarity** — the posture above, and how hard we can commit to the rewrite. *(the big one)*
2. **LAMMPS** — we have a third simulator study that is **not in the submitted paper** (9 tasks, 1 run, no native baseline). We plan to include it, but only as evidence of task diversity for R3, clearly labelled preliminary — never as an answer to the execution question, since the agent never actually runs LAMMPS. Comfortable with that line?
3. **OpenFOAM n=30** — scaling it up **changed the answer** (Vanilla coverage went 3/5 → 30/30, the memory effect went +0.19 → −0.01). Reporting it means telling reviewers the submitted n=5 result was noise-dominated, and R2/R3 both cited transfer as a *strength*. Our lean: **report it anyway** — a reviewer finding the reversal on arXiv later is much worse. Agree?
4. **Volunteering our own numerical corrections** (#7) — the corrected numbers are already public in the arXiv version, so being second to our own correction would look bad. Comfortable?
5. **Human-baseline anomaly** — one expert's score *drops* between their 1-hour and 3-hour session, unexplained in both versions. Pre-empt it, or wait to be asked? Our lean: wait.
6. **Is the arXiv version publicly posted?** If it is, we should paraphrase rather than quote it verbatim in the rebuttal — a distinctive sentence is searchable and would lead a reviewer to a non-anonymous preprint.

---

## Three practical notes

**We can run the simulator.** We found a working GEOS binary on the workstation, so the execution evaluation the AC asked for is no longer blocked. It still has to be scoped carefully — a handful of tasks, framed as a calibration study, not a physics benchmark — and the initial response will not depend on it landing.

**The deadline is Aug 3, not Aug 7.** Phase 3 (Aug 3–10) is reviewer/AC discussion only — we can't post or even see it. Anything landing after Aug 3 is worthless for the decision. Initial responses go up **Jul 27**, built entirely from data we already have.

**One number to confirm before anything is posted.** The main-effects table in the appendix was generated before one cell's score was revised, and never regenerated — that, rather than a calculation error, is the source of the discrepancy with the arXiv version. We need to confirm which value is correct before describing the correction to reviewers.
