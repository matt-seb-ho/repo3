<!-- v2r2 DRAFT 2026-07-27. Shared evaluation response.
     POSTING: post once globally if a general/AC-visible thread allows it; otherwise post on gep1's
     thread (he raised it as score-moving and the AC made it the decision criterion).
     nBNe.md carries a condensed self-contained version so it works either way.
     Style: no em dashes; no "ladder"/"rung"; no "Common Weakness"; no non-significance callouts.
     Target ~6,500 prose chars. HARD CAP 10,000. -->

## Evaluation: do the structural gains correspond to decks that actually run?

*(Raised by gep1 W1/Q1, nBNe W2/Q1, and the AC.)*

We thank the reviewers for converging so clearly on this. It is the most important question in the reviews and we made it our first priority.

### 1. What we have run since submission

We evaluate deck correctness at five increasing levels of strictness:

| Stage | Check |
|---|---|
| 1 | The deck is well-formed XML |
| 2 | It is schema-valid against the GEOS XSD |
| 3 | GEOS accepts and loads the input |
| 4 | The simulation runs to completion and the solver converges |
| 5 | Quantities of interest match a reference run |

The submitted paper reports stages 1 and 2. We have now run all five.

**Stages 1 and 2, re-run at 17 runs per cell rather than 3**, because these are counts of rare events:

| | Vanilla | S+X | X+M |
|---|---|---|---|
| Well-formed and schema-valid | 155 / 170 | **170 / 170** | **100 / 100** |

A gap of 8.8 points, with a run-and-task clustered interval of +2.9 to +16.5 points, and 270 adapter runs with no failures at all. One point of precision on the name: 10 of the 15 baseline failures are well-formedness errors, chiefly nested XML comments, rather than schema errors.

**Stage 3, GEOS accepts the input.** Across the same 170 runs per cell, the simulator accepts 133 for Vanilla and 132 for S+X. **The structural advantage does not by itself carry through to the acceptance check**, and the reason is more interesting than the number. It is the subject of section 2.

**Stage 4, convergence.** On the tasks whose reference deck itself converges, **every deck GEOS accepted also ran to completion and converged, 31 of 31**. Loading is the binding constraint, not solving, so the cheap acceptance check captures nearly all of the execution signal. That is useful for anyone building this kind of benchmark.

**Stage 5, quantities of interest.** We built an output-side metric and ran it across 489 runs on 18 tasks. It injects an identical output block into reference and candidate decks, runs both, and compares mesh-independent summaries of each physical quantity, normalised by the reference's own scale, with no interpolation at any point.

Structural similarity predicts output fidelity with a rank correlation of 0.31 (interval 0.23 to 0.39), varying from 0.11 to 0.74 across tasks. The most informative result is conditional: **among decks that run, mean output fidelity is 0.958, and roughly half reproduce the reference almost exactly.** The distance between structure and physics is concentrated in decks that fail to run rather than in decks that run and are wrong, which is consistent with the paper's reliability framing.

### 2. A finding we did not have at submission: `xmllint` is not equivalent to the simulator's own check

This is the most useful thing we learned during this period, and it changes what we recommend to others.

GEOS's own documentation recommends validating input with `xmllint --schema`, and describes doing so as highly recommended for all users. That is what we built into the adapter. **We discovered only after submission, while running the evaluation above, that the two checks are not equivalent in either direction.** Across the 180 held-out decks, 49 pass `xmllint --schema` but are refused by `geosx`. What `xmllint` cannot see are cross-reference and arity errors: a PVT model named in one file but absent from the deck, a constitutive model missing on a named subregion, a component-count mismatch between two blocks.

That class is exactly the residual failure mode our bottleneck analysis reports as unfixed by any adapter, and the diagnosis is now concrete: **the defects were present, but the validator we chose could not see them.** It also explains stage 3: the stop hook was certifying decks the simulator would refuse, so there was nothing in the acceptance rate for it to improve.

**We have now implemented the swap and run it.** Replacing `xmllint --schema` with `geosx --validate-input` inside the verification loop, at roughly 2.5 seconds per deck, and holding everything else constant:

| Cell (3 runs, 10 held-out tasks) | Accepted, `xmllint` in the loop | Accepted, `geosx` in the loop |
|---|---|---|
| S+X | 23 / 30 | **27 / 30** |
| S+X+M | 24 / 30 | **25 / 30** |

The blocks the new validator raises are the errors described above, and the agent repairs them: in one case it added a missing thermal conductivity model to the region that referenced it, a cross-reference defect no schema check can express.

The general point, useful beyond this paper: **a simulator's documented validation advice is not necessarily a sufficient acceptance test for that simulator**, and a benchmark that trusts it will certify decks the simulator refuses. Validate with the simulator's own input check wherever one exists.

### 3. What the benchmark asks of the agent, and why a structural metric is its primary measure

We should have been clearer in the paper about the scope of the task, because it determines what the metric has to measure.

**In our setting the physical values are supplied by the user.** Each task brief states the domain geometry, material parameters, boundary conditions and requested outputs in domain language: a permeability of 9.0e-13 m² in all directions, a reference porosity of 0.2 at 10 MPa, and so on. What it never does is name a single GEOS XML element. The agent has no property database, literature or online source, and is not asked to decide what the physics should be.

**Its job is translation**: to express a well-specified modeling intent in the simulator's DSL. Under that scope, whether the agent produced the right deck is largely a structural question, and TreeSim answers it against a hand-validated ground-truth deck. It is fast, deterministic, and cheap enough to run on every cell of a factorial design, which neither an execution-based nor a judge-based metric is at our budget.

We agree this scope is narrower than the eventual goal. The setting where interface grounding should matter most is one that supplies the agent with less and asks it to recover more, and there the physical plausibility of the chosen values becomes the central question rather than a secondary one. Judging individual deck values that way needs a purpose-built benchmark and sustained domain-expert involvement, a longer effort than this window allows. We are pursuing both: expanding the task scope, and improving the evaluation for the current one.

### 4. What we are building next

Two further instruments, and we would rather report what they show than what we hoped.

**A section-level semantic judge.** An LLM judge that compares candidate against reference one canonical GEOS section at a time (`Mesh`, `Solvers`, `Constitutive` and so on), which is the granularity TreeSim already reports, so the two are directly comparable per section. We use a judge from a different model family than the agent backbone so that self-preference is not a confound.

We validated it against the stage-5 measurements above and report the result rather than the intention: **the judge tracks output fidelity, but no better than the structural metric already does**, so we are not offering it as a validated secondary metric.

We then tested the obvious improvement it suggested, that the metric should weight the physics-bearing sections (`Solvers`, `Constitutive`, `FieldSpecifications`) above bookkeeping ones. **It does not help.** Re-weighting moves the correlation with output fidelity by at most +0.03, inside its own interval, and a physics-selected subset of sections predicts simulation fidelity **no better than a random subset of the same size** (51st percentile of the random null). The comparison had power to detect an improvement of 0.034, so this is a tight negative rather than an underpowered one. We report it because the uniform section weighting now stands on a test rather than on assumption: the most plausible alternative was tried and did not beat it.

We are also validating a tolerance-aware variant, since the current scorer treats any leaf difference as a total mismatch and many are physically immaterial.

### 5. Two results on what the evidence does support

Since the reviews turn on what our evidence establishes, we want to put two results forward positively rather than only defending the metric.

**The reliability finding now replicates across all three simulators**, which we think is a stronger form of the claim than more GEOS runs alone would give. On GEOS, per-cell across-run standard deviation falls from 0.081 for Vanilla to 0.002 (S+X), 0.005 (X+M) and 0.012 (SE), and 1 of 30 Vanilla runs produced a deck our scorer could not read against 0 of 30 for every adapter cell. On OpenFOAM at 30 tasks, every SIGA cell returns a complete case, while Foam-Agent leaves 11 tasks and MetaOpenFOAM 20 incomplete. On LAMMPS there is almost nothing to prevent (structural score at least 0.976 everywhere), and consistent with that the completion gate contributes little while memory and retrieval carry the gain. The same mechanism, applied to three interfaces, produces the pattern it predicts.

**The adapters are also faster on the hard tasks**, which the paper understates by claiming only that they impose no runtime overhead. On the held-out split the hand-designed cells are meaningfully more efficient than the bare harness.

| Cell | Tool calls / task | vs Vanilla | Wall seconds / task | vs Vanilla |
|---|---:|---:|---:|---:|
| Vanilla | 90.5 | | 416.5 | |
| X+M | 75.0 | **-17.1%** | 339.5 | **-18.5%** |
| S+X | 74.7 | **-17.5%** | 345.1 | **-17.2%** |

These gains are largest exactly where the reliability gains are, which we read as one effect rather than two: on hard tasks the bare harness thrashes, and grounding stops the thrashing. We will re-anchor the efficiency claim on these cells for the camera-ready, noting that the self-evolved cell does not share it.
