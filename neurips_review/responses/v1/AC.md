<!-- DRAFT v0.1 — 2026-07-26. Budget ~5,000 chars. Posted as an Official Comment to the AC.
     Structure: the AC's four meta-review bullets, in the AC's own order. The handbook says the
     meta-review is the guide — this text matters more than the union of reviewer asks.
     HIGHEST-RISK SECTION IN THE WHOLE SET is bullet 1: it must not read as "we answered the
     execution ask." Schema validity is rung 2 of 5 and the AC made execution the criterion. -->

We thank the AC for a meta-review that states the decision criteria plainly. We respond to the four points in the order given.

## 1. Structural-only evaluation

We accept the criticism and want to be precise about what our evidence does and does not cover, rather than let a partial result stand in for the whole ask.

The paper reports two claims that it does not separate clearly enough. The first is a **reliability** claim: on held-out-eval, across-seed sigma falls from 0.081 for Vanilla to 0.002 for S+X, because the adapter eliminates outputs our scorer cannot evaluate at all. That claim concerns how often the pipeline emits something unevaluable and does not depend on TreeSim's *scoring* semantics. The second is a **mean-lift** claim, +0.069 TreeSim from Vanilla to SE, which depends on them directly. The AC's objection lands on the second, and we should have distinguished them.

We describe the evaluation as a five-rung validity ladder: (1) well-formed XML, (2) schema-valid against the GEOS XSD, (3) the simulator accepts the input, (4) it runs to completion and the solver converges, (5) quantities of interest match a reference run. **The submitted paper reports rungs 1 and 2. That is not the execution evaluation requested, and we do not want to present it as such.**

**We have gone further up the ladder during the response period, and we want to report the result including where it does not help us.**

Rungs 1–2, recomputed across all six held-out cells (30 runs each; a run passes only if every XML file it emitted passes): Vanilla is schema-valid on **24 of 30**, all five adapter cells on **30 of 30**.

Rung 3 — asking the simulator itself to load the deck, across all 180 held-out decks — matters more, and **it does not support a claim.** Vanilla reaches **21 of 30**, X+M **21 of 30**, S+X 23, S+X+M 24, SE-prose 23, SE 24. The baseline ties X+M exactly; no per-cell difference approaches significance (Fisher p 0.55–1.00, pooled 0.49); and a per-task sign test is flat — the baseline is worse on 4 of 10 tasks, **better on 3**, tied on 3.

**So the rung-2 separation does not survive to rung 3 at this scale, and we are not going to claim that it does.** We would rather tell the AC that plainly than let a schema-validity number stand in for execution. (These are post-fix numbers: an earlier version of the sweep was confounded by our own harvester failing to stage non-XML assets into some run directories. All 10 tasks, nothing excluded.)

Four caveats, all of which we would rather state than have found:

- **Rung 2 is partly circular.** Cells containing S or X invoke `xmllint` against the same schema, so their perfect rate is partly true by construction. X+M, where the agent calls the validator voluntarily, is the least circular comparison.
- **GEOS is more permissive than our own evaluation pipeline.** Its XML parser accepts constructs that `xmllint` and our scorer reject, and we verified decks that fail our well-formedness check yet load in GEOS with exit code 0. So rungs 1–2 and rung 3 are **overlapping checks on different parsers, not a nested ladder**, and part of our reported unparseable-deck count reflects our pipeline being stricter than the simulator. That is a limitation of our metric rather than a property of the systems compared, and it is part of why the rung-2 gap exceeds the rung-3 gap.
- **We found a fairness bug in our own harness.** The largest single loading-failure category is a missing *non-XML* asset — property tables and mesh files a deck references but our harvester never copied into the run directory. It is an evaluation artifact rather than an authoring error, and it penalises the adapter cells more than the baseline. We report both denominators rather than the flattering one.
- **Effective n is well below 30.** The rung-2 failures span only four distinct tasks and cluster by seed.

The failure modes at rung 3 are worth more than the rates, because they are precisely the class a structural metric cannot see: cross-reference and arity errors such as a PVT model named but never defined, a constitutive model absent on the subregion that references it, or a component-count mismatch in a fluid definition. A tree match at 1e-6 tolerance scores all of these as near-perfect.

**One further check we ran on ourselves, and it costs us.** The single zero-score run on the entire held-out split is the one producing the baseline's sigma of 0.081, and therefore the variance-reduction figure we quote. We put that deck through GEOS: **it loads, exit code 0.** Its only defect is a prose double hyphen inside an XML comment. So the run is genuinely unevaluable by our metric but is not a deck the simulator refuses, and the natural reading of our reliability claim — that the baseline sometimes emits something unusable — is not supported by that instance. The honest characterisation is a **portability defect rather than an execution failure**: the decks are invalid XML per the specification and would break a spec-compliant consumer, but GEOS tolerates them. That is a real difference between conditions, but a smaller and different one than the paper implies, and we would rather narrow the claim ourselves.

On why deck-level evaluation is a well-posed target even so: the deck is a **sufficient statistic** for the simulation. There is no hidden state and no stochasticity, so everything about the result is determined by the input file. The open question is therefore the *metric on decks*, not the *choice to evaluate decks* — and we agree the metric is where our evaluation is weakest. On the worry that a different deck could yield the same physics, the effect is common-mode: every cell is scored against the same reference with the same metric, so the penalty depresses the absolute level for all cells equally and leaves the contrast intact.

A separate comment follows this one, reporting two corrections we would rather volunteer than have found, and an audit of TreeSim itself that qualifies our own reported margin.

## 2. Clarity and jargon

We accept this fully; both this reviewer and kEdh are right, and we do not contest it. Because the response period does not allow a revised PDF, we have put the actual replacement text inline in our response to kEdh rather than promising a rewrite: a definition of "input deck" at first use; the fractional design motivated in plain prose, with its aliasing stated explicitly; a gloss on Buckley–Leverett; rewrites of both sentences that reviewer quoted; and one worked example each of a task "brief" and of the stop hook's structured repair feedback.

[[BLOCKED: human decision H2 — how strongly to commit to the camera-ready rewrite.]]

We would offer one argument for how to weigh this against the evidence gap. **Clarity is the only weakness on the table that is certain to be fixed.** It requires no new experiment and no result to come out a particular way; it is entirely within camera-ready scope and we can commit to it. The evidence gaps depend on experiments that may not land in this window, or may land and come out negative. A certain fix and a hoped-for one should not carry the same weight in a borderline decision.

## 3. Limited experimental scale

We take the trade the AC offers explicitly: uncertainty estimates on the existing data, an argument about representativeness, and narrowed claims where the evidence does not support the general statement.

On representativeness, we would rather describe the held-out set than defend it as a random sample. The +0.069 gain decomposes into two catastrophic-failure rescues plus one task that fails universally at 0.013 in every cell; the remaining seven held-out tasks have a Vanilla mean of 0.898, statistically indistinguishable from the validation set's 0.910. The held-out set is therefore "in-distribution tasks plus a hard tail," and what we can support is a **hard-tail reliability effect** — narrower than the paper's current phrasing.

On uncertainty, we have computed intervals on the existing data and we would rather report the conservative version. Bootstrapping over tasks (10 tasks, all three seeds retained, paired, 20,000 resamples), the Vanilla-to-SE mean-lift contrast is +0.069 with a 95% interval of **[−0.009, +0.166]**. Treating (task, seed) pairs as independent gives [+0.001, +0.155], but that understates the interval because seeds within a task are correlated.

**We therefore do not claim the mean lift is statistically significant at ten tasks, and we will not phrase the paper as though it is.** We would rather tell the AC that than present the narrower interval.

This is also the quantitative reason we lead with reliability. That contrast does not rest on the interval at all: 1 of 30 Vanilla runs produced an unscorable deck against 0 of 30 for every adapter cell, and per-cell across-seed sigma is Vanilla 0.081, X+M 0.005, S+X 0.002, SE 0.012. Supporting the same reading, SE is higher on 7 of 10 tasks, tied on 1 and lower on 2, with a median delta of +0.022 against a mean of +0.069 — the two rescues carry the mean, which is what the paper already says the mechanism is.

[[BLOCKED: human decision H1 — whether to report the OpenFOAM n=30 campaign, which reverses one component's sign at larger n.]]

We will moderate the robustness and generalization claims accordingly, including in the abstract.

*(Corrections and the TreeSim audit move to the companion comment — see `AC_post2.md`.)*

## 4. Human comparison too small

We concede without reservation and adopt the AC's own framing: two participants on one tutorial-level task is **preliminary calibration**, not a human baseline. We will relabel it throughout, remove comparative time-savings language from the abstract and introduction, and state that it establishes the existence of an effect on one easy task rather than any ranking.

## On venue

We understand this is the committee's call and will not argue it. We would only note that the paper's contribution — a component-wise causal analysis of what grounding actually buys a general coding agent, including the negative results — is aimed at the agent-design literature rather than at a simulation audience.
