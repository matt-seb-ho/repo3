<!-- DRAFT v0.3 — 2026-07-26. THIS IS POST 1 of 2 (the initial "Rebuttal").
     Post 2 = gep1_post2.md, a same-day Official Comment carrying Q3, Q4, Scale, and the correction pointer.
     Rationale for the split: threads/E_drafting.md decision D5 — gep1's content exceeds one 10,000-char post
     and every remaining cut would come out of score-moving evidence.
     Post 1 carries: the reliability/mean-lift split, Q1 (execution ladder, the AC's primary objection and
     gep1's first score-moving item), and Q2b (S/X, his second score-moving item).
     Q2a (prefix) moved to Post 2 to fit the cap — it is a dismissal argument and sits naturally with the
     other methodology items there.
     Current: 8,733 prose chars + 1 open placeholder. HARD CAP 10,000.
     Provenance: neurips_review/sprint/PROVENANCE.md -->

We thank the reviewer for an unusually actionable review; the two conditionals are specific enough to answer directly, so we take them first.

**One distinction governs everything below.** The paper makes two claims and blurs them. The **reliability** claim: held-out across-seed sigma falls from 0.081 (Vanilla) to 0.012 (SE) and 0.002 (S+X), and 1 of 30 Vanilla runs emitted a deck our scorer could not read, against 0 of 30 for every adapter cell. The **mean-lift** claim: +0.069 mean TreeSim. The first concerns how often the pipeline emits something unevaluable and does not depend on TreeSim's *scoring* semantics; the second does, and the reviewer's objection lands there. We should have separated them, and will.

## Q1 — Execution-based evaluation (score-moving)

We accept the framing and have now run the check. We think of the evaluation as a five-rung ladder: (1) the deck is well-formed XML, (2) it is schema-valid against the GEOS XSD, (3) the simulator accepts and loads the input, (4) it runs to completion and the solver converges, (5) quantities of interest match a reference run. The submitted paper reports rungs 1 and 2 only.

**Rungs 1–2.** We should correct our own number here before anything else. The three-seed sample in the paper gave Vanilla 24/30, but two of those three seeds turned out to be the lowest of a much larger draw. **We re-ran to 17 seeds** (170 held-out runs per cell; a run passes only if *every* XML file it emitted passes, since GEOS consumes the whole deck directory):

- Vanilla: **155 / 170 = 91.2%** [95% CI 85.9–95.0]
- S+X and X+M: **170/170 and 100/100 — 270 adapter runs, zero failures**

So the real gap is **8.8 points, not the 20 points our three-seed sample implied.** It is also far better supported: Fisher p < 0.0001, and a task-clustered bootstrap — which the original never ran — gives **[+2.9, +16.5] points, p = 0.0006**. We would rather hand the reviewer the corrected, smaller, better-evidenced number than the flattering one.

One further correction to the metric's name: **10 of Vanilla's 15 failures are not schema errors at all** but well-formedness errors, chiefly nested XML comments. This rung is "well-formed *and* schema-valid," and we will label it that way.

**Rung 3 is the important new number, and it is much weaker than rung 2.** Running the simulator's own input-validation phase on all 180 held-out decks. Two tasks have reference decks that do not themselves load, and two more depend on data assets our harvester failed to stage; we exclude those identically across all cells and give both denominators:

At 17 seeds, **Vanilla reaches 133/170 and S+X 132/170 — Fisher p = 1.0000, bootstrap CI [−5.3, +2.9] points.** The baseline is marginally *ahead*.

**This is a firm negative, not an absence of evidence.** The interval excludes any adapter advantage above about 3 points. Whatever separation exists at the well-formedness and schema rung does **not** survive to the point where the simulator itself decides, and we would rather state that plainly than let a schema result stand in for execution.

(Two disclosures on the measurement itself: an earlier version of this sweep was confounded by our own harvester failing to stage non-XML assets into some run directories, which we have now fixed — the numbers above are post-fix, all 10 tasks, nothing excluded. And our pre-screen excluded nothing: no deck in any cell uses the handful of schema elements this GEOS build lacks.)

Two things we found that matter more than the rates (a third, the failure-mode taxonomy, is in our second comment):

**Well-formedness and schema violations behave completely differently under execution.** Every schema-invalid run also fails in GEOS, with the same root cause `xmllint` identified — validator and simulator agree on genuine violations. But of the unparseable runs, two load in GEOS with exit 0 and the third fails for an unrelated reason: **not one fails GEOS because of the defect our metric flagged.**

One caveat we would rather state than have extracted. **Rung 2 is partly circular:** cells containing S or X invoke `xmllint` against this same schema, so a perfect rate is in part true by construction. **X+M is the least circular comparison** — the agent calls the validator voluntarily rather than being gated on it — and it is 100/100.

**On rung 1 we owe the reviewer two concessions, one of which we found only by running the simulator.**

All of Vanilla's well-formedness failures share a single cause: a `--` sequence inside an XML comment, which the XML specification forbids. So at rung 1 the adapter is catching a lexical rule, not a physics error, and an `xmllint` gate catches that class by construction.

More importantly: **GEOS itself does not enforce that rule.** It parses with pugixml, which accepts double hyphens in comments, whereas both `xmllint` and the Python parser inside our scorer reject them. So rungs 1–2 and rung 3 are **overlapping checks on different parsers, not a nested ladder**, and part of our reported catastrophic-failure count reflects our pipeline being stricter than the simulator. That is a limitation of our metric rather than a property of the systems compared, and it is part of why the rung-2 separation exceeds the rung-3 separation. (A second, smaller point in the same family: our scorer discards a file that fails to parse *before* selecting which deck to compare, so it catches total failure but not partial malformation — again biased against our own contrast, since the discarded files are almost all the baseline's.)

**We checked this against our own headline number, and it costs us.** The single zero-score run on the held-out split is the one producing Vanilla's sigma of 0.081, and hence the variance-reduction figure we quote. We ran it through GEOS: **the deck loads, exit code 0.** Its only defect is a prose double hyphen inside a comment in a title line. So the run is genuinely unscorable by our metric, but it is not a deck the simulator refuses — and the natural reading of our reliability claim, that the baseline sometimes emits something unusable, is not supported by that instance.

The honest characterisation is **portability defects rather than execution failures**: the decks are invalid XML per the specification and would break a spec-compliant consumer, but GEOS tolerates them. That is a real defect and a real difference between conditions, but smaller and different from what the paper implies, and we would rather narrow the claim ourselves.

Finally, why deck-level evaluation is well-posed at all: **the deck is a sufficient statistic for the simulation** — no hidden state, no stochasticity, so the result is fully determined by the input file. The open question is the *metric on decks*, not the *choice to evaluate decks*. And on non-uniqueness, the effect is common-mode: all cells are scored against the same reference with the same metric, so the penalty depresses the absolute level equally and leaves the *contrast* intact. It attacks "SIGA scores 0.78", not "SIGA exceeds Vanilla by 0.069".

We are continuing up the ladder to convergence and quantity-of-interest comparison, and will post what lands rather than promise a date.

## Q2b — Separating S from X (score-moving)

A clarification we owe the reviewer: **the Resolution-IV design does separate the S and X main effects.** With defining relation I = RSXM, main effects alias only with three-factor interactions, so S and X are clean of each other and of all two-factor interactions. What the fraction cannot estimate is the **S x X interaction**, aliased with R x M — and that is precisely "is X redundant once S is on?" The design is sound but silent on exactly the point raised.

We can answer it two ways. **From a build-up ablation** run one factor at a time (3 seeds x 17 tasks) that never made it into our framing: adding the hook-enforced validator (**S**) gives **+0.008**, adding the agent-callable validator (**X**) on top gives **−0.007**, the two together **+0.000**. Both single-step deltas sit well inside their own variability — per-task standard deviation about 0.029, roughly four times the effect — so the defensible claim is not that X hurts but that **X buys nothing once S is on**.

**From the hook's own telemetry**, which is more direct. We instrumented every stop-hook invocation. In cells where both components are enabled the hook **never intervened once** — 0 interventions in 410 invocations on validation, and 0 in 30 on held-out — because the agent had already validated its own output mid-turn via the agent-callable validator, roughly three calls per task, leaving the hook nothing to catch. So the two components are **substitutes**: either one suffices, which is precisely why neither shows a main effect.

We should be straight about what that does and does not establish. It does **not** show that the stop-hook effect is dominant on the hard tail — with the validator present, the hook's mechanism is inactive on both splits. And the reason is not that those decks were sound: the simulator refuses to load **10 of those same 30** held-out decks. The defects were there; the validator we chose could not see them.

Two disclosures in the same breath. The construct overlap is worse than the paper says: the hook's schema check is itself **gated on the agent-callable validator being enabled**, so "S" alone means parse-checking only while "S with X" means parse plus schema — the S treatment is not constant across cells. And the ablation is on validation data where **no run failed at all**, so it separates the components precisely where the mechanism is inactive.

Our second comment covers Q3, Q4, statistical scale, an audit of TreeSim itself, and the Limitations wording the reviewer asked for — which we adopt verbatim.
