# SIGA (NeurIPS 2026, Submission 31642) — Consolidated Reviewer Weaknesses

**Deduplicated across all three reviews and the initial meta-review.**

| Tag | Reviewer | Rating | Confidence |
|---|---|---|---|
| **R1** | gep1 | 4 — Borderline accept | 3 |
| **R2** | kEdh | 2 — Reject | 4 |
| **R3** | nBNe | 5 — Accept | 5 |
| **AC** | GKRj | — (borderline) | — |

*"Score-moving" = the reviewer stated explicitly that resolving it would raise their score or confidence.*

---

## At a glance

| # | Weakness | R1 | R2 | R3 | AC |
|---|---|:--:|:--:|:--:|:--:|
| 1 | Evaluation is structural only (TreeSim), not execution / physics validity | ●* | | ● | **●** |
| 2 | Writing is jargon-heavy; not readable for a general NeurIPS audience | | **●** | | ● |
| 3 | Small experimental scale (10 held-out tasks × 3 runs; OpenFOAM 5 × 1) | ● | | ● | ● |
| 4 | Human baseline too small (n=2, one task, one experience level) | ● | | ● | ● |
| 5 | OpenFOAM transfer under-powered; native baseline constrained to lint-only | ● | ○ | ○ | ● |
| 6 | S and X components confounded — both invoke validation | ●* | | | |
| 7 | Native-plugin-prefix bug contaminated retrieval estimates | ●* | | | |
| 8 | Limitations should say "structural reliability, not validated correctness" | ● | | | |
| 9 | Exact Claude Code version not reported | | | ● | |
| 10 | Venue fit — eScience may be a better target than NeurIPS | | ● | | |
| 11 | No fundamentally new agent architecture; depends on simulator structure | | | ● | |

● raised as a weakness  ●* score-moving  **●** stated as that reviewer's primary objection  ○ cited as a *strength* by that reviewer

---

## 1. Structural-only evaluation — R1 (score-moving), R3, AC (primary)

TreeSim measures structural similarity, not whether decks **execute**, **converge**, or produce **physically meaningful** output.

- **R1:** "TreeSim is appropriate as a scalable first metric, but it does not establish that generated decks run successfully in GEOS." Asks for even 5 tasks × Vanilla + best SIGA cell. *"My score would increase if the reliability gains persist under execution or physical-validity checks."*
- **R3:** "scientific simulations need numerical stability and physically meaningful output"; asks for convergence checks and simulator output validation.
- **AC:** names this first and makes it the decision criterion — "A small execution-based evaluation would substantially strengthen the central claim that SIGA improves simulator reliability rather than only configuration structure."

## 2. Writing clarity / jargon — R2 (primary), AC

R2: *"this paper is not written well and practitioners will struggle to understand it and apply its findings in practice."* Four concrete items:

1. "Resolution-IV 2^(4−1) factorial" is used as the driving example with no explanation.
2. "Deck" is defined in §3, too late; the *"strictly perfect decks"* and *"failures-as-zero"* sentences are unparseable for a general reader.
3. No simple examples of "briefs" or "structured repair feedback."
4. (Separate item — see #10.)

AC independently endorses: *"in its current state, it would be hard for a NeurIPS reader to fully understand many things in the paper."*

## 3. Limited experimental scale — R1, R3, AC

- Main hard-task GEOS result: **10 tasks × 3 runs**. OpenFOAM transfer: **5 tasks × 1 run**.
- **R3:** asks for a larger benchmark with more diverse task types, which would also strengthen the statistical conclusions.
- **AC:** clarify representativeness of the task set, provide uncertainty estimates, "and moderate the robustness and generalization claims if additional evaluation is unavailable."

## 4. Human baseline too small — R1, R3, AC

- n=2 participants, one relatively easy task.
- **R1:** should be read as "anecdotal calibration," not evidence about human-vs-agent performance.
- **R3:** wants multiple tasks **and different levels of GEOS experience (beginner → expert)**, plus a **human–agent collaborative setting**.
- **AC:** "useful as preliminary calibration, but the claims should either be narrowed or better contextualized."

## 5. OpenFOAM transfer under-powered — R1, AC

5 tasks, single run, and the Foam-Agent baseline was constrained to `execution_mode=lint_only`. R1 asks for more tasks, multiple seeds, or a fuller execute-mode comparison — *"If not feasible, the claims about transfer should remain explicitly qualitative."*
**Note:** R2 and R3 both cite cross-simulator transfer as a **strength**, so this one cuts both ways.

## 6. S / X confound — R1 (score-moving)

S (stop-hook enforcement) and X (agent-callable validator) both involve validation, so their individual roles are not isolated. *"My confidence would increase if the stop-hook effect remains dominant after removing this confound."*

## 7. Native-plugin-prefix bug — R1 (score-moving)

The paper discloses a bug that contaminated some retrieval-related estimates. R1 asks for the affected cells to be rerun cleanly.

## 8. Limitations wording — R1

Limitations should *"more directly state that the current evidence supports structural authoring reliability, not validated simulator correctness."*

## 9. Exact Claude Code version — R3

Results may depend on both the model and the harness environment; the harness version is never reported.

## 10. Venue fit — R2

*"it may be better directed to a scientific conference such as eScience rather than to NeurIPS."* R2 explicitly flags this as the program committee's call, not their own.

## 11. Incremental / no new architecture — R3 (minor)

"Does not introduce a fundamentally new agent architecture; it is based on existing ideas and the method depends on existing simulator structure." Listed as a weakness but R3 still rated the paper 5.

---

## What the AC says the decision turns on

> "The decision will likely depend on whether the rebuttal can establish that the **structural improvements translate to executable and scientifically valid simulations** *and* whether the authors can put **significant efforts towards improving the clarity** of the paper towards a general NeurIPS audience."

That is a **conjunction** — items #1 and #2 above. Everything else is secondary.
