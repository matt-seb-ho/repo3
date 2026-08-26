<!-- DRAFT v0.1 — 2026-07-26. Budget ~3,500 chars. Rating 5, confidence 5.
     Rule for this response: answer the three questions, concede gracefully, change nothing else.
     Do NOT re-argue novelty. Do not give this reviewer new reasons to think. -->

We thank the reviewer for the careful reading. All three questions are ones we agree with, and we answer them directly.

## Q1 — Convergence checks and validation of simulator output

We agree this is the right next step, and it is the single most common thread across the reviews. We think of our evaluation as a five-rung ladder: (1) the deck exists and is well-formed XML, (2) it is schema-valid against the GEOS XSD, (3) the simulator accepts the input, (4) it runs to completion and the solver converges, (5) quantities of interest match a reference run. The paper reports rungs 1 and 2 only.

We have now run rungs 1–3. On schema validity, Vanilla passes **24 of 30** held-out runs and every adapter cell **30 of 30**. When we ask the simulator itself to load the deck, the separation is real but much smaller: **18 of 30** for Vanilla against **23 of 30** for the best cell. We would rather report that honestly than let the schema number stand in for execution — the reviewer's question is about rungs 3–5, and the gap narrows as we climb.

We also took a subset of decks all the way to convergence and to a comparison of simulation outputs against reference runs — which is precisely what the reviewer asked for. Two findings, both of which qualify our claims:

**At three seeds we cannot demonstrate an execution-level advantage.** On the hardest task the baseline converges cleanly on 2 of 3 seeds against 80% across the adapter cells, which is indistinguishable at this sample size.

**More importantly, high structural similarity does not imply matching physics — and we now know exactly why.** On a control task where every cell scores between 0.963 and 0.999, 11 of 17 runs differ from the reference by 40–99% on the primary quantity of interest. These simulations are driven by tabulated property data held in separate non-XML files that the agent also authors, and our structural metric compares XML only — **it never reads the files that set the physics.** The runs whose data tables match the reference exactly reproduce it exactly. One deck scoring 0.999 carried a 99% error; one run converged with all solver tolerances met and was still 99.97% wrong. This is a scope limitation of our metric, not only of this study, and we will state it as such.

One smaller finding, since it qualifies our reported failure counts: GEOS's XML parser is more permissive than the parsers in our pipeline and accepts some decks our scorer rejects as malformed. So rungs 1–2 and rung 3 are overlapping checks on different parsers rather than a nested ladder.

Two honest notes. First, one caveat on the schema-level results: cells containing S or X invoke `xmllint` against that schema, so their rung-2 rates are partly true by construction — X+M, where the agent calls the validator voluntarily, is the least circular comparison. Second, the reviewer asked specifically for validation of *simulator output*, so we want to be clear that an LLM-based semantic metric on input decks — which we are also exploring — is not an answer to this question. It sits at a different rung and we will not present it as substituting for convergence checks.

## Q2 — Expertise levels and a human-agent collaborative setting

We concede both. Our human comparison is two participants on one task at the easy end of the benchmark; it is preliminary calibration rather than a baseline, and we will label it that way. The reviewer's stronger design — multiple tasks spanning several levels of GEOS experience — is the right one, and we agree that a **collaborative** setting is the more realistic deployment mode than either the fully manual or fully autonomous condition we measured. Both go to future work explicitly rather than as a passing mention.

## Q3 — Exact Claude Code version

The version is **2.1.119**. We confirmed it from the harness's own initialisation records rather than from memory: all 903 initialisation events across the campaign report that version, with no exceptions.

We also owe a concession that reinforces the reviewer's point: our container installed the Claude Code package **unpinned**, so the version tracked image build time rather than being fixed by configuration. That is exactly the fragility the question is aimed at. We will pin it and report both the harness version and the container digest.

## On the remaining weaknesses

**No fundamentally new architecture.** We agree, and it is deliberate: the question we set out to answer is how much of the gap can be closed by wrapper-level grounding around an unmodified harness, without retraining. A negative or small result there is informative precisely because the intervention is cheap.

**Task-set size.** We accept this and will narrow the claims accordingly rather than defend the scale. Our held-out set is best described as "in-distribution tasks plus a hard tail" rather than a random sample: the mean gain is concentrated in two catastrophic-failure rescues, while the remaining seven held-out tasks have a Vanilla mean of 0.898, statistically indistinguishable from the validation set's 0.910. What we can support is a hard-tail reliability effect, and we will state it in those terms.

On uncertainty, bootstrapping over tasks (10 tasks, all three seeds retained, paired, 20,000 resamples) puts the Vanilla-to-SE contrast at +0.069 with a 95% interval of [−0.009, +0.166], so we do not claim the mean lift is significant at this scale and will not phrase it as though it is. The reliability contrast does not depend on that interval: 1 of 30 Vanilla runs produced an unscorable deck against 0 of 30 for every adapter cell.
