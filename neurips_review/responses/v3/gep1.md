<!-- v2r2 DRAFT 2026-07-27. Reviewer gep1: rating 4 (borderline accept), confidence 3.
     Post AFTER 01_evaluation.md (which goes globally, or on this thread as the first comment).
     Style: no em dashes; no "ladder"/"rung"; no non-significance callouts; point by point.
     CHANGED FROM v2r1: dropped bootstrap CI and all "not significant" language per researcher direction;
     added the cross-simulator reliability replication and the held-out efficiency numbers.
     Target ~7,500 prose chars. HARD CAP 10,000. -->

## Response to Reviewer gep1

We thank the reviewer for an unusually actionable review. Both score-moving items were specific enough to act on directly, and we did. We respond to each point below.

### Response to Weaknesses

> W1: Evaluation is mostly structural. TreeSim does not establish that generated decks run successfully in GEOS or produce physically meaningful simulations.

**Response to W1:** Please see our separate response on evaluation, which covers this in full. In summary: we have now run the simulator's own acceptance check and convergence on all six held-out cells. GEOS accepts 19 of 30 Vanilla decks against 23 of 30 for the best adapter cell, and **every deck GEOS accepted also converged, 31 of 31**. Loading is the binding constraint, not solving.

That response also reports a finding we did not have at submission: `xmllint --schema`, which the GEOS documentation itself recommends, is not equivalent to the simulator's own input check, and the gap is exactly the cross-reference and arity errors our bottleneck analysis identifies as unfixed. Experiments with the corrected validator in the loop are running now.

> W2: Statistical and experimental scale. Main GEOS results use n=3 and 10 held-out tasks; OpenFOAM is 5 tasks, single-seed, with a lint-only Foam-Agent baseline.

**Response to W2:** We have strengthened this since submission on three fronts.

**GEOS: 27 evaluated tasks.** We should clarify a presentation choice that made the benchmark look smaller than it is. The paper foregrounds the 10 held-out tasks, but the benchmark is **17 validation plus 10 held-out, 27 tasks in total, all evaluated across all cells**. The split exists to give the self-evolution setup a clean train/test separation, not because the validation tasks go unevaluated. We are working with GEOS developers to expand it in both scope and scale.

**OpenFOAM: 5 tasks to 30, plus a second native baseline.** The best SIGA cell reaches mean 0.870, and every SIGA cell produces all required files on all 30 tasks with no zero-score outputs. Two simulator-native agents fail exactly there: Foam-Agent reaches 0.516 (19/30 full coverage, 8 zero-score), MetaOpenFOAM 0.379 (10/30, 12 zero-score). At this scale the informative reliability contrast is SIGA against purpose-built native agents.

**LAMMPS: a third simulator.** 9 molecular-dynamics tasks, two backbone models. LAMMPS input is a sequential command script with no formal schema, which tests whether the recipe is tied to XML. It is not, but the binding component shifts: scripts are structurally complete almost everywhere (structural score at least 0.976 across all 12 configurations), so the gain comes from knowledge injection rather than completion enforcement.

On the judge metric (0 to 10), deepseek-v4-flash goes from 4.56 unguided to **7.78** with the full adapter, and Claude Sonnet 4.6 from 6.33 to 6.89. Both transfer studies remain single-run, and we present them as transfer evidence rather than as second and third benchmarks. We are scaling both further.

Two further results bear on what the evidence supports at this scale, and we give them in full in our separate response. In short: **the reliability finding the reviewer singled out as our strongest result now replicates across all three simulators**, which we think is a stronger form of the claim than more GEOS runs alone would give. And **the adapters are also faster on the hard tasks**, by about 17% in both tool calls and wall-clock for the hand-designed cells, which the submitted paper understates by claiming only that they impose no overhead.

> W3: Methodological confounds. S and X both involve validation, so their individual roles are not fully isolated. A native-plugin-prefix bug contaminated some estimates involving retrieval.

**Response to W3:** Both are answered under Q2 below.

### Response to Questions

> Q1 [Score-moving]: Can the authors add a small GEOS execution-based evaluation? "My score would increase if the reliability gains persist under execution or physical-validity checks."

**Response to Q1:** Yes, and it is run; see the summary under W1 and our evaluation response for the full results. The gains do persist under execution: the ordering is preserved from XML well-formedness through schema validity, simulator acceptance and convergence, and every deck the simulator accepted converged.

> Q2 [Score-moving]: Can the authors rerun the cells affected by the native-plugin-prefix bug and more cleanly separate S from X? "My confidence would increase if the stop-hook effect remains dominant after removing this confound."

**Response to Q2, part (a), the prefix bug:** We can bound its effect directly rather than argue from chronology, and it is small.

A targeted ablation run before submission gives 0.913 with the prefix and 0.917 without, a difference of **+0.004** across 3 runs on 17 tasks, with no single task moving by more than 0.10. We also counted retrieval-tool calls per run: cells with retrieval disabled that nonetheless carried the prefix attempted roughly 0.5 to 2.6 calls per task-run, **every one of which errored** with "no such tool available", so no retrieval content entered those runs.

The point that matters for the headline comparison: **Vanilla attempts zero such calls and SE attempts zero**, so the Vanilla-to-SE contrast is untouched on both sides. The affected cells are X+M, S+X, S+X+M and SE-prose, and the bias runs against us, so their reported lifts are **understated**.

**Response to Q2, part (b), separating S from X:** One clarification we owe the reviewer, then the direct answer.

The Resolution-IV design does separate the S and X **main effects**. With defining relation I = RSXM, main effects alias only with three-factor interactions, so S and X are clean of each other and of every two-factor interaction. What the fraction cannot estimate is the S x X **interaction**, which aliases with R x M, and that is precisely the question of whether X is redundant once S is on. The design is sound but silent on exactly the point raised.

We can answer it two ways. From a **one-factor-at-a-time build-up ablation** (3 runs, 17 tasks): adding the hook-enforced validator (S) gives +0.008, adding the agent-callable validator (X) on top gives -0.007, the two together +0.000, against per-task variability of about 0.029. The defensible reading is not that X hurts but that **X buys nothing once S is on**. From the **hook's own telemetry**, which is more direct: in cells where both are enabled the hook never intervened, 0 times in 410 validation invocations and 0 in 30 held-out runs, because the agent had already validated its own output mid-turn. The two components are **substitutes**, which is why neither carries a large main effect.

We should be straight about what this does not establish. It does not show that the stop-hook effect is dominant on the hard tail, because with X present the hook's mechanism is inactive on both splits. And the reason is not that those decks were sound: GEOS refuses to load 10 of those same 30 held-out decks. The defects were there; the validator we chose could not see them. That diagnosis is what motivates the `geosx --validate-input` swap now running, and we think it is a more useful answer than a claim of dominance we cannot support.

> Q3: Can the authors strengthen the OpenFOAM transfer study? If not feasible, the transfer claims should remain explicitly qualitative.

**Response to Q3:** We have strengthened it (see W2) and we also accept the reviewer's fallback. Foam-Agent's execute mode still did not run in our environment, so that comparison remains lint-only and we will say so in the text rather than in a footnote. Both transfer studies remain single-run, and we will keep the transfer claims explicitly qualitative.

> Q4: Can the human baseline be reframed more conservatively or expanded? n=2 on one task does not support broad claims about expert-human time savings.

**Response to Q4:** We concede this without reservation. Two participants on one task is preliminary calibration, not evidence about expert-human time savings. Concretely we will (i) relabel it "preliminary calibration" throughout, (ii) remove comparative time-savings language from the abstract and introduction, and (iii) state that it establishes the existence of an effect on one task rather than any ranking of humans against the agent.

One observation we offer without leaning on it: the task used, `buckleyLeverettProblem`, is a 1D two-phase verification case with a known analytical solution and is the easy end of our benchmark. An easy task should if anything **understate** the value of automation, since a GEOS developer's own written estimate rises from under 30 minutes for this case to a couple of days for compound multiphysics decks, which is where our held-out result lives.

### Limitations wording

We adopt the reviewer's wording and will place it in the main body rather than the appendix; the exact sentence is in our evaluation response. We agree it is the honest summary of what this paper establishes.

### On the limitations wording

The reviewer asked us to state this directly, and we agree it is the honest summary. We will put it in the main body rather than the appendix:

> The evidence in this paper supports improved **structural authoring reliability**, meaning fewer unevaluable outputs and lower across-run variance on compound multiphysics tasks. It does not establish **validated simulator correctness**. TreeSim is a structural metric: a deck scoring 0.8 is not thereby shown to load, converge, or produce physically meaningful output.

The execution work above sharpens that sentence rather than softening it, and we would rather adopt the reviewer's wording than argue at the margin.
