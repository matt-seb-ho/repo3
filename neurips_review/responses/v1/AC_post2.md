<!-- DRAFT v0.1 — 2026-07-26. Companion Official Comment to the AC, posted alongside AC.md.
     AC.md answers the four meta-review bullets. THIS post carries: the clean-subset null,
     the TreeSim self-audit, the rejected LLM-judge metric, and both volunteered corrections.
     Rationale for the split: AC.md exceeded the 10,000-char cap once the metric audit was folded in,
     and "corrections and metric audit" is a coherent standalone unit. See threads/E_drafting.md D6.
     HARD CAP 10,000. Provenance: neurips_review/sprint/PROVENANCE.md -->

A companion to our main response, reporting what we found when we audited our own evaluation during this period. All of it qualifies our claims rather than strengthening them, and we would rather put it on the record ourselves.

## 1. The separation is entirely a failure-rate effect, not a quality effect

This is the most informative result we obtained. Restricting to the held-out runs where **every** cell produced a schema-valid deck, no metric separates the cells at all: all pairwise differences fall within ±0.014, and no comparison approaches significance.

**The entire held-out separation is carried by catastrophic failures rather than by graded quality.**

We think this is the right reading of our own results, and it sharpens what the paper already argues — that SIGA prevents unusable outputs rather than improving good ones, and that the number of strictly perfect decks is unmoved by any configuration we tried. One reviewer specifically credited the paper for drawing that distinction. What was qualitative there is now measured.

It also means our abstract's "mean structural similarity" framing overstates the mechanism. Decks did not get better; fewer of them failed. We will reframe the abstract and §5 in those terms.

## 2. We ran the decks through the simulator. The result cuts toward the AC's position.

We obtained a working GEOS build during the response period and took a subset of decks through convergence and a quantity-of-interest comparison against reference runs, injecting an identical observable into reference and generated decks alike so that no interpolation is involved.

**We cannot demonstrate an execution-level advantage at this sample size.** On the hardest rescue task the baseline reaches clean convergence on 2 of 3 seeds against 80% across the adapter cells — indistinguishable at three seeds per cell. We report that plainly rather than let the schema-validity numbers imply otherwise.

**The informative result is a limitation of our own metric.** On a control task where every cell scores between 0.963 and 0.999 — structurally near-identical decks — **11 of 17 runs differ from the reference by 40–99%** on the primary quantity of interest. The mechanism is specific and verified: these simulations are driven by tabulated property data in separate non-XML files that the agent also authors, and TreeSim compares XML only. **It never reads the files that set the physics.** The two runs whose data tables are byte-identical to the reference reproduce it exactly, at 0% error; one deck scoring 0.999 carried a 99% error in peak pressure.

Two further observations in the same direction. One run converged cleanly, with every solver tolerance satisfied, and was 99.97% wrong — **convergence is not correctness**. And one deck that is schema-valid and scores 0.99 declares an elastic material with no elastic constants at all: GEOS refuses to load it, while our metric sees a near-perfect deck.

So the AC's objection is right in a stronger sense than the meta-review states. It is not only that structural similarity may fail to imply physical validity; our instrument does not inspect part of the deck that determines the physics. We will state this as a scope limitation of TreeSim, and it is the clearest justification we can offer for narrowing our claims to structural authoring reliability.

We are being candid that this study weakens our execution-level claim more than it supports it. We think offering it anyway is the right call, and we would rather the committee weigh a negative result we found ourselves than a gap we left for someone else to find.

## 3. A defect in TreeSim that understates our own margin

When an unnamed container element carries one unexpected attribute, our element-matching step can score that element zero and discard its entire subtree along with it. The clearest instance is a `Solvers` element carrying an explicit gravity vector — which is GEOS's own default value, and physically correct — and which zeroes ten otherwise-matching child elements.

It affects roughly a third of held-out decks, and it is **worst for the self-evolved cell**, so our reported margin is understated rather than inflated.

We are deliberately **not** re-scoring during the response period: that would change every number in the submission while reviewers are reading it. We will disclose it as a metric limitation, fix it for camera-ready, and report both the original and corrected numbers.

One consequence worth flagging: a failure mode our bottleneck analysis labels a hallucinated attribute is better described as a metric artifact, since the attribute in question is a correct default rather than an authoring error.

Two smaller metric facts from the same audit, both common-mode and so harmless to the contrast: one held-out task scores 0.013 in every cell because its reference deck expands to roughly 3,300 elements against the ~50 a generated deck contains, costing every cell about 0.099 identically; and our scorer silently scores partially unparseable decks, with every instance being the baseline's — which under-counts baseline failures.

## 3. An LLM-judge metric we built, tested, and are not reporting

Because the reviews asked for evaluation beyond structural similarity, we built a comparative LLM-judge metric on the held-out set — judging each generated deck against the reference, blind to condition, with multiple judge models and position swapping.

**It failed its own reliability checks and we are not offering it as a result.** Inter-judge agreement was poor, position effects were as large as the entire between-condition effect, judge identity moved scores several times more than the experimental condition did, and one of the three judges reversed the ranking of the baseline and the best adapter cell. It does correlate with actual loading and convergence outcomes — but no better than TreeSim already does, at zero cost.

We report this because the negative result is itself informative for the question the reviews raise: LLM judging did not substitute for execution here. One narrower output does survive, as a within-deck audit rather than a comparison — roughly two-thirds of the attribute differences TreeSim treats as total mismatches are judged physically immaterial. That is consistent with the argument in our main response: TreeSim's absolute level is depressed for every cell alike, which is why we rely on the contrast rather than the level.

## 4. Corrections to the submitted paper

[[BLOCKED: human decision H3 + H9 — the main-effects correction. If yes, this subsection says:
  - The appendix main-effects table was produced by an analysis script that averages over *scored* runs, whereas the paper's headline convention — stated in §3 and repeated in Table 1's caption — scores unevaluable runs as zero. Exactly one factorial cell contains an unevaluable run, so exactly one cell mean differs, and the derived table inherited it.
  - **Table 1 itself is correct.** We reverified all eleven of its validation cells and all six held-out cells, means and standard deviations, against the raw results.
  - Corrected effects: **R −0.037, S −0.008, X +0.011, M +0.008**, computed from the eight cell means printed in Table 1 so they can be checked directly. All four move away from zero; the negative retrieval effect is larger than reported, which strengthens the paper's own finding.
  - Per H9, §5.1's "X, M and S all fall within ±0.007" is FALSE under the correction and must be corrected in the same breath — it is the sentence licensing "don't add RAG; the rest doesn't matter."
  - Do NOT say the prefix-bug fix produced these numbers (no re-run occurred). Do NOT claim Table 1 is post-fix.
If no: omit this subsection entirely and say nothing.]]

[[BLOCKED: human decision H7 — the Table 5 error. If yes: the held-out bottleneck table prints zero attribute-value errors for the two self-evolved cells, where the underlying classifier output records four and three. Read literally the printed table claims those cells eliminate the failure mode the paper elsewhere describes as untouched by every configuration — the artifacts support the paper's thesis and the printed table contradicts it. Worth stating that the table cell is the error, not the thesis.]]

[[BLOCKED: human decision H10 — the harness fairness bug, if not already covered in the main response's §1.]]
