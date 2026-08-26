<!-- DRAFT v0.1 — 2026-07-26. THIS IS POST 2 of 2 for reviewer gep1 — a same-day Official Comment.
     Post 1 = gep1.md (the initial "Rebuttal"): opening, Q1 execution ladder, Q2b S/X.
     Post 2 carries: Q2a prefix, Q3 OpenFOAM, Q4 human baseline, the Limitations wording,
     scale/uncertainty, the clean-subset null, the TreeSim self-audit, and the correction pointer.
     Rationale for the split: threads/E_drafting.md decisions D5/D6.
     Current: 6,866 prose chars + 2 open placeholders. HARD CAP 10,000.
     Provenance: neurips_review/sprint/PROVENANCE.md -->

Continuing our response, covering the reviewer's remaining two questions, the Limitations wording, and statistical scale.

## Q2a — Native-plugin-prefix bug (score-moving)

We can now ground this in the run logs rather than in chronology, which we agree would not be persuasive alone.

The prefix's footprint is directly measurable. Cells with retrieval disabled that nonetheless carried the plugin attempt roughly 0.5 to 2.6 retrieval-tool calls per task-run, **every one of which errors** with "no such tool available" — so no retrieval content leaked in, and R was genuinely off. Retrieval-enabled cells make 12–13.5 successful calls with essentially no errors. Crucially, **Vanilla attempts 0 such calls and SE attempts 0**, so the headline Vanilla-to-SE contrast is unaffected on both sides. The handicapped cells are X+M, S+X, S+X+M and SE-prose — their reported lifts are *understated*.

For magnitude we have a dedicated probe built before submission: with the prefix 0.913, without it 0.917, a difference of **+0.004** over 3 seeds x 17 tasks, with **no single task moving by more than 0.10**. So both bias directions favour our conclusions rather than our claims: the baseline was not handicapped and the adapter cells were.

One asymmetry we should disclose rather than wait to be asked: SE opted out of the prefix while SE-prose carried it, so that one pairwise comparison is not matched. We should also be straight that the SE-versus-SE-prose difference is small and sensitive to the scoring convention, and we do not rest any claim on it.

## What the loading failures actually are

**The failure modes are exactly the class a structural metric cannot see.** Loading failures are dominated by cross-reference and arity errors — "PVT model PhillipsBrineDensity not found in input files"; "coupled solid constitutive model not found on subregion cb1"; "the number of default density values is not the same as the component number"; a trajectory given as a flat list where nested brace-triples are required. A bipartite tree match at 1e-6 tolerance scores all of these as near-perfect. This is the concrete version of the gap the paper describes only abstractly.

## A defect in our own harness, which we exclude rather than exploit

The largest single loading-failure category in our rung-3 sweep is a missing *non-XML* asset — property tables and mesh files a deck references but our harvester never staged into the run directory. We checked whether this reflects a real difference between conditions, and it does not: **all six cells reference identical assets** on the affected tasks, down to the same counts per cell and seed. What varies is only whether the file happened to get staged. It is measurement noise on 2 of 10 tasks, orthogonal to authoring quality, and we exclude those tasks identically across all cells rather than report a number it inflates.

## Q3 — OpenFOAM transfer

We accept the reviewer's own fallback and will keep the transfer claims explicitly qualitative. Foam-Agent's execute mode did not run in our environment, which is why we restricted it to its linting tool; that is a weaker comparison than it appears and we will say so in the text rather than a footnote.

[[BLOCKED: human decision H1 — whether to report the n=30 campaign and its reversal (Vanilla coverage 3/5 to 30/30; S effect +0.328 to +0.168; M effect +0.192 to −0.007). If yes, the honest framing is that the submitted n=5 result was noise-dominated and the larger run changes one component's sign — which is itself an argument for the reviewer's point about scale. Fallback: report the submitted n=5 only. ~600 chars.]]

## Q4 — Human baseline

We concede this without reservation. Two participants on one task at the easy end of the benchmark is preliminary calibration, not evidence about expert-human time savings. Concretely we will (i) relabel it "preliminary calibration" throughout, (ii) remove comparative time-savings language from the abstract and introduction, and (iii) state that it establishes the existence of an effect on one tutorial-level task rather than any ranking of humans against the agent.

## Limitations wording

The reviewer asked for this directly and we agree it is the honest summary. We will put it in the main body, not only in Limitations:

> The evidence in this paper supports improved **structural authoring reliability** — fewer catastrophic, unevaluable outputs and lower across-seed variance on compound multiphysics tasks. It does not establish **validated simulator correctness**. TreeSim is a structural metric: a deck scoring 0.8 is not thereby shown to load, converge, or produce physically meaningful output.

Our execution work during this period sharpens rather than softens that sentence, and we would rather adopt the reviewer's wording than argue at the margin. Two results in particular.

The separation narrows as we climb the ladder and then disappears. At 17 seeds the baseline is well-formed and schema-valid on 155/170 against 170/170 for the adapter cells — a real 8.8-point gap, cluster-bootstrap CI [+2.9, +16.5]. But at the rung where the simulator itself decides, the baseline reaches **133/170 against S+X's 132/170**, Fisher p = 1.0000, CI [−5.3, +2.9] — a firm negative, not missing evidence. And on convergence and quantities of interest we cannot demonstrate an execution-level advantage either. We are not claiming an execution-level rescue from this study, and we want to say so before it is inferred from the schema numbers.

The second result is more useful, and it is a limitation of our own instrument. We ran a control task on which **every cell scores between 0.963 and 0.999** — structurally near-identical decks. On that task **11 of 17 runs differ from the reference by 40–99%** on the primary quantity of interest. The mechanism is specific: the simulation is driven by tabulated property data in separate non-XML files that the agent also authors, and TreeSim compares XML only — it never reads them. The two runs whose data tables are byte-identical to the reference reproduce it exactly, at 0% error. One deck scoring 0.999 carried a 99% error in peak pressure. Relatedly, one run converged cleanly, with every solver tolerance met, and was 99.97% wrong: **convergence is not correctness.**

So the reviewer's central point is right in a stronger sense than the review states. It is not only that structural similarity may not imply physical validity — our metric does not even read the files that set the physics. We will state that as a scope limitation of TreeSim in the camera-ready, and it is the clearest argument we can make for the wording above.

## Scale and uncertainty

We can give intervals on the existing data, and we would rather report the conservative version. Bootstrapping over tasks (10 tasks, all three seeds retained, paired, 20,000 resamples), the Vanilla-to-SE mean-lift contrast is +0.069 with a 95% interval of **[−0.009, +0.166]**. Treating (task, seed) pairs as independent gives [+0.001, +0.155], but that understates the interval because seeds within a task are correlated. **So we do not claim the mean lift is statistically significant at ten tasks**, and we will not phrase the paper as though we do.

The reliability contrast does not rest on that interval: 1 of 30 Vanilla runs produced a deck our scorer could not read at all against 0 of 30 for every adapter cell, and per-cell across-seed sigma is Vanilla 0.081, X+M 0.005, S+X 0.002, SE 0.012. We give per-cell sigma rather than a single ratio so that any variance claim can be matched to the cell it came from.

One further result belongs here because it bears directly on the reviewer's reading of our contribution. Restricting to the held-out runs where **every** cell produced a schema-valid deck, no metric separates the cells at all — all pairwise differences within ±0.014, no comparison close to significance. The entire held-out separation is carried by catastrophic failures rather than graded quality. This is what the paper already argues qualitatively, and the reviewer singled that care out as a strength; it is now measured. But it does mean our abstract's "mean structural similarity" framing overstates the mechanism, and we will reframe it: decks did not get better, fewer of them failed.

We also audited TreeSim itself and found a defect running **against** our reported advantage: when an unnamed container element carries one unexpected attribute, our matching step can zero it and discard its whole subtree. The clearest case is a `Solvers` element carrying an explicit — and physically correct — gravity vector, which zeroes ten otherwise-matching children. It affects about a third of held-out decks and is worst for the self-evolved cell, so our margin is understated. We will not re-score mid-response, since that changes every number in the submission; we will disclose it and fix it for camera-ready.

On representativeness we would rather describe the held-out set than defend it as a random sample. The +0.069 decomposes into two catastrophic-failure rescues (0.355 to 0.761; 0.541 to 0.825) plus one task failing universally at 0.013 in every cell; the remaining seven tasks have a Vanilla mean of 0.898, indistinguishable from val's 0.910. SE is higher on 7 of 10 tasks, tied on 1 and lower on 2, with median delta +0.022 against mean +0.069 — the two rescues carry the mean, which is what the paper already says the mechanism is. Held-out-eval is therefore best described as "val plus a hard tail," and what we can support is a **hard-tail reliability effect**. That is narrower than the paper's current phrasing and we will state it in those terms, including in the abstract.

[[BLOCKED: human decision H3 — whether to volunteer the main-effects correction. If yes, one sentence here pointing at the full correction in our comment to the AC: "We have also volunteered a correction to the appendix main-effects table in our comment to the AC; the corrected effects are R −0.037, S −0.008, X +0.011, M +0.008." If no, cut entirely and say nothing. ~220 chars.]]

## Closing

On the S/X confound, we believe the build-up ablation meets the reviewer's stated bar on val, with the hard tail still open. On execution, we have moved from a structural-only evaluation to a measured loading result and an initial convergence and quantity-of-interest comparison — and we have reported where that helps us and where it does not. We will post further rungs as they land rather than promise a date.
