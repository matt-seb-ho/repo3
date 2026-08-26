# The evaluation work, explained

What each measurement actually is, how it was computed, what it returned, and how to frame it in the rebuttal.

---

## Part 1 — The four checks on "does this deck work"

These are objective and need no model. All are on the held-out split (10 tasks), and all apply the same check identically to the reference deck and the generated one.

### 1. Well-formed and schema-valid — yes, this is `xmllint`

Two checks, both libxml2, run on every XML file a task-run emitted:

```
xmllint --noout <deck>                              # well-formed XML
xmllint --schema data/GEOS/.../schema.xsd --noout <deck>   # matches the GEOS XSD
```

A task-run passes only if **every** file it emitted passes, because GEOS consumes the whole deck directory and one malformed include breaks the run.

**Result, at 17 runs per cell (170 runs each):** Vanilla **155/170 (91.2%)**, S+X **170/170**, X+M **100/100**. Gap 8.8 points, task-clustered bootstrap [+2.9, +16.5], p = 0.0006.

Two things worth knowing. **10 of Vanilla's 15 failures are well-formedness, not schema** — chiefly nested XML comments (`<!-- <!-- -->`), which is a lexical bug rather than missing schema knowledge. And the paper's 24/30 came from three runs that happened to include the two lowest draws of seventeen; the number is 91.2%, not 80%.

### 2. Loads — yes, this is `geosx --validate-input`

GEOS's own loading phase, without running the simulation:

```
geosx -v -i <root_deck>     # from the deck's own directory, ~2.5 s
```

Only *root* decks are checked. An `<Included>` fragment is not a standalone problem and fails spuriously if you validate it alone.

**Result:** Vanilla **133/170**, S+X **132/170**, bootstrap CI [−5.3, +2.9]. **No adapter advantage, and the interval excludes one above about three points.**

**Important: this check and check 1 overlap, they do not nest.** GEOS parses with **pugixml**, which accepts `--` inside an XML comment; `xmllint` and our Python scorer reject it. So a deck can fail check 1 and load and run perfectly. We verified this on the single run that produces our largest variance figure: it loads with exit 0 and reproduces the reference physics exactly.

### 3. Converges

Full run with a wall-clock cap, checking exit code, whether time-stepping reached the final time, and solver convergence from the log.

**Result:** on the tasks whose *reference* deck converges cleanly, **every deck GEOS accepted also ran to completion and converged, 31 of 31.** Loading is the binding constraint, not solving, so the cheap 2.5-second check captures nearly all of the execution signal.

### 4. Output reproduction — how it actually works

This is the one worth explaining in detail, because the design choices are what make it defensible.

**The problem.** Generated and reference decks routinely have different meshes. You cannot compare fields cell-by-cell without interpolating, and interpolation is exactly what a reviewer would attack instead of the result.

**The construction.** For each task:

1. **Inject identical instrumentation into both decks.** We add the same `<VTK plotLevel=3>` output block and final-time event to the reference and the candidate. Neither deck's own choice of outputs affects the comparison.
2. **Run both.** GEOS is bitwise deterministic (verified: 16/16 statistics identical across repeat runs), so one run per deck suffices.
3. **Treat each physical quantity as a bag of values.** For quantity *q* (pressure, stress, temperature, and so on), collect its values over all cells at final time, merged across ranks and regions.
4. **Compare only mesh-independent reductions.** Four per quantity: `min`, `max`, `mean`, `rms`. Note `rms = sqrt(mean(x²))`, **not** the raw ℓ² norm, which scales like √n and would make the metric mesh-*dependent*.
5. **Normalise by the reference's own scale.** With `S = max(|min(R)|, |max(R)|)`:

   ```
   δ(q,ρ) = |ρ(G) − ρ(R)| / S
   ψ(q,ρ) = clip(1 − δ, 0, 1)
   Ψ(q)   = mean over the four reductions
   SOF    = mean over quantities, in [0,1]
   ```

6. **The reference alone defines the comparison basis** — which quantities count and what the scale is. The candidate cannot influence either, so the metric cannot be gamed by emitting more or fewer outputs.
7. **A missing quantity scores zero**, so coverage is inside the metric rather than a separate footnote.
8. **Constitutive array names are canonicalised** from deck-chosen names to solver-defined types, so the metric does not secretly measure whether the agent picked the same *names*.

**Sanity checks it passes:** the two runs whose data tables are byte-identical to the reference score exactly **1.0000**; a run that is 99.97% wrong on peak pressure scores **0.0003** under the strict variant.

**Results, 489 runs across 18 tasks:**

- Structural similarity predicts output fidelity **moderately: ρ = 0.31 [0.23, 0.39]**, ranging **0.11 to 0.74** across tasks.
- **Cells do not separate** (Δ = −0.007 held-out, p = 0.41).
- **The useful one: conditional on the deck running, mean fidelity is 0.958, and roughly half of all runs reproduce the reference almost exactly.**

**One honest sensitivity.** Averaging the four reductions dilutes catastrophic failures. Using the *worst* reduction instead, the correlation drops to 0.12 and is not significant on the clean split. Both must be reported.

---

## Part 2 — The two experiments on the metric itself

Here is the distinction that matters, because I have been blurring it.

| | **Semantic judge** | **Physics-weighted TreeSim** |
|---|---|---|
| What changes | the **measurement** of each section | the **aggregation** of existing measurements |
| Model involved | yes, an LLM scores each section | **none at all** |
| Input | reference section, candidate section, task brief | TreeSim's per-section scores, already computed |
| Question it asks | "are these differences physically material?" | "should `Solvers` count more than `Outputs`?" |
| Deterministic | no (5.2% verdict flip rate at temperature 0) | yes |
| Cost | $12.70 for one sweep | free |

They are two different interventions that happened to be connected by one hypothesis, which turned out to be wrong (below).

### The semantic judge

**Unit of judgment:** one (deck, top-level GEOS section) pair. **Not** whole decks, and **not** individual values.

For each section the judge sees the reference version, the candidate version, and the relevant part of the task brief, and returns an **ordinal level** (equivalent / minor / material / severe). Code maps levels to credit (1.0 / 0.7 / 0.3 / 0.0) and aggregates with TreeSim's own section weighting, so the two are directly comparable. **The model never emits a number** — that was the design lesson from an earlier attempt where it did, and judges disagreed wildly about the scale.

Four judges from four model families, none of them the agent's backbone, blind to which condition produced the deck, with presentation order swapped.

**What it returned:**

- **It does track physics**: correlation with output fidelity ρ = 0.338 (p = 0.006), rising to 0.411 conditional on running.
- **But it does not beat plain TreeSim at that**: paired Δ = −0.040 [−0.257, +0.166], negative in all four analysis cells and not sign-stable across conventions.
- Reliability: raw agreement 70% (up from 41% in the earlier design), Gwet's AC1 = 0.81 — but **two of four judges ordered the conditions differently**, which was the criterion that mattered.
- Cell scores: Vanilla 0.725, S+X 0.804, SE 0.804 — it does rank the adapters above Vanilla and slightly *widens* the gap relative to TreeSim.

**Its advantage is specific to predicting whether a deck loads**, not whether the physics is right (AUC 0.882 vs TreeSim's 0.846 on the same rows). That was a mis-set validation target on my part, which is why the physics validation was run afterwards.

### Physics-weighted TreeSim

No model. Take TreeSim's per-section scores and re-weight: physics-bearing sections (`Solvers`, `Constitutive`, `FieldSpecifications`, `Functions`) ×2, plumbing ×1, bookkeeping (`Outputs`, `Events`) ×0.5. Weights fixed in advance.

**Result: null, and tightly so.** Best variant is +0.033 [−0.003, +0.072], and **a physics-selected subset of sections predicts fidelity no better than a random subset of the same size** (51st percentile of the random null). Minimum detectable improvement was 0.034, so an improvement worth shipping would have been visible.

**Why the connecting hypothesis failed.** The judge's bookkeeping-section scores *anti*-correlate with fidelity (−0.31), which suggested TreeSim's uniform weighting was cancelling signal against anti-signal. But that negative term is **the judge's, not TreeSim's**: in TreeSim at n = 489, bookkeeping's partial correlation is **+0.036**, and `Events` alone is **+0.211**. The diagnosis did not transfer from the model-based metric to the deterministic one.

**One finding that does replicate:** structural error in the **`Solvers`** subtree is what predicts physical divergence (ρ = 0.343, partial 0.223 over the deck aggregate — the only interval across both experiments excluding zero at large n). It cannot become a metric, because **5 of 18 tasks have no `<Solvers>` section at all**. It belongs in analysis as a diagnostic.

---

## Part 3 — What this says about deck quality, which is the positive result

Independent of any condition comparison: **the judge indicates TreeSim understates how good the decks are.** Roughly two-thirds of the attribute differences TreeSim scores as total mismatches are judged **physically immaterial**, with all judges agreeing that "cosmetic" is the modal category.

Combined with output reproduction being **0.958 among decks that run**, the picture is: decks that run mostly produce the right physics, and much of TreeSim's absolute penalty is cosmetic. That supports the paper's numbers being conservative rather than generous, and it is orthogonal to Vanilla-versus-SIGA — which is the right place to make it, given the paper's claim is about preventing bad runs.

---

## Part 4 — Suggested framing for the rebuttal

The trap to avoid is presenting any of these as a finished instrument. The framing that holds up:

**1. Lead with why the current metric fits the current scope.** The task is translation: the brief supplies the physics, the agent supplies the interface expression, and every deck is scored against a hand-validated reference. Structural fidelity to a known-correct reference substantially *is* the quantity of interest there.

**2. Present the new work as a protocol under construction, with the objective parts already usable.** Suggested wording:

> We treat these as a protocol under construction rather than as finished instruments. The execution checks are objective and we report them as measured. The output-side comparison is also objective, but the choice of which quantities matter for a given physics problem is a domain judgement, and we are working through those definitions with GEOS developers rather than asserting them. The semantic judge is the least settled of the three: judging whether a parameter choice is physically reasonable is exactly the kind of question that needs a purpose-built benchmark with expert-labelled ground truth, and we would rather build that than report a number from an instrument we have not validated against expert judgement.

**3. Report the nulls as tests, because they defend the metric.** We tried re-weighting the structural metric toward physics-bearing sections and it did not beat uniform weighting, against a random-subset control, with power to detect a small improvement. **That makes uniform weighting a tested choice rather than an assumed one** — a stronger position than not having looked.

**4. State the one dependency plainly.** The remaining work needs domain-expert involvement and a separate benchmark for the judging process itself. That is a scope statement, not a hedge, and it is more credible than promising a validated plausibility metric inside a response window.

**5. Do not claim** an execution-level or output-fidelity advantage between conditions. Neither is detectable, and the reliability claim does not need either.

### What genuinely needs the domain experts

- **Which quantities of interest matter per task.** We chose defensible defaults (peak pressure, final-state field summaries), but a domain scientist should decide what "the same simulation" means for each problem class.
- **Tolerances.** Our output metric normalises by the reference's own scale; what counts as an acceptable relative error is physics, not statistics.
- **Ground truth for plausibility.** The judge cannot be validated without expert-labelled examples of physically reasonable versus unreasonable parameter choices. This is the separate benchmark.
- **Whether `Solvers` deserves special status.** The one replicating signal we found. A domain expert would know whether that is expected.
