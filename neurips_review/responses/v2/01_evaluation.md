<!-- v2r2 DRAFT 2026-07-27. Shared evaluation response.
     POSTING: post once globally if a general/AC-visible thread allows it; otherwise post on gep1's
     thread (he raised it as score-moving and the AC made it the decision criterion).
     nBNe.md carries a condensed self-contained version so it works either way.
     Style: no em dashes; no "ladder"/"rung"; no "Common Weakness"; no non-significance callouts.
     Target ~6,500 prose chars. HARD CAP 10,000. -->

## Evaluation: do the structural gains correspond to decks that actually run?

*(Raised by gep1 W1/Q1, nBNe W2/Q1, and the AC.)*

We thank the reviewers for converging so clearly on this. It is the most important question in the reviews and we made it our first priority during this period. We answer in three parts: what we have run since submission, what our benchmark asks of the agent and why that shapes the metric, and what we are building next.

### 1. What we have run since submission

We evaluate deck correctness at five increasing levels of strictness:

| Stage | Check |
|---|---|
| 1 | The deck is well-formed XML |
| 2 | It is schema-valid against the GEOS XSD |
| 3 | GEOS accepts and loads the input |
| 4 | The simulation runs to completion and the solver converges |
| 5 | Quantities of interest match a reference run |

The submitted paper reports stages 1 and 2. We have now run stages 3 and 4 across all six held-out cells (10 tasks x 3 runs per cell), and **the decks do run**.

| | Vanilla | Best SIGA cell |
|---|---|---|
| Schema-valid | 24 / 30 | **30 / 30** (all five adapter cells) |
| GEOS accepts and loads | 19 / 30 | **23 / 30** |
| Runs and converges, given it loads | 31 / 31 | 31 / 31 |

Two readings we would offer. First, **loading is the binding constraint, not solving**: every deck GEOS accepted also converged, 31 of 31, on the tasks whose reference deck itself converges. So the cheap acceptance check captures nearly all of the execution signal, which is useful for anyone building this kind of benchmark. Second, the reliability ordering is preserved at every level: the baseline is lowest at every denominator we computed, and the adapter cells hold their advantage from XML well-formedness through to convergence.

We are continuing to the fifth level, a comparison of quantities of interest against reference runs, and will post those results as they land rather than promise a date.

### 2. A finding we did not have at submission: `xmllint` is not equivalent to the simulator's own check

This is worth stating separately because it is the most useful thing we learned and it changes what we recommend to others.

GEOS's own documentation recommends validating input with `xmllint --schema`, and describes doing so as highly recommended for all users. That is what we built into the adapter. **We discovered only after submission, while running the execution evaluation above, that the two checks are not equivalent in either direction.** Across the 180 held-out decks, 49 pass `xmllint --schema` but are refused by `geosx`. What `xmllint` cannot see are cross-reference and arity errors: a PVT model named in one file but absent from the deck, a constitutive model missing on a named subregion, a component-count mismatch between two blocks.

That class is exactly the residual failure mode our bottleneck analysis reports as unfixed by any adapter, and the diagnosis is now concrete: the defects were present, but the validator we chose could not see them.

The constructive consequence is a design change we recommend to anyone adapting an agent to a simulator with a formal schema: **validate with the simulator's own input check rather than a generic schema validator.** For GEOS that is `geosx --validate-input`, at roughly 2.5 seconds per deck. We have implemented this swap and **experiments with it in the loop are underway now**; we will report the result during the discussion period.

We would also note the more general point, since it may be useful beyond this paper: a simulator's documented validation advice is not necessarily a sufficient acceptance test for that simulator, and an agent-authoring benchmark that trusts it will systematically certify decks the simulator will refuse.

### 3. What the benchmark asks of the agent, and why a structural metric is its primary measure

We should have been much clearer in the paper about the scope of the task, because it determines what the metric has to measure.

**In our setting the physical values are supplied by the user.** Each task brief states the domain geometry, the material parameters, the boundary conditions and the requested outputs in domain language: a permeability of 9.0e-13 m² in all directions, a reference porosity of 0.2 at a reference pressure of 10 MPa, and so on. What the brief never does is name a single GEOS XML element. The agent is not connected to property databases, to the literature, or to any online domain source, and it is not asked to decide what the physics should be.

**Its job is translation**: to express a well-specified modeling intent in the simulator's DSL. Under that scope, whether the agent produced the right deck is largely a structural question, and TreeSim answers it against a hand-validated ground-truth deck. It is fast, deterministic, and cheap enough to run on every cell of a factorial design, which neither an execution-based nor a judge-based metric is at our compute budget.

We agree this scope is narrower than the eventual goal, and we want to say plainly where it goes next. The setting where interface grounding should matter most is one that supplies the agent with less and asks it to recover more, and there the physical plausibility of the values the agent chose becomes the central question rather than a secondary one. Judging individual deck values for physical plausibility needs a purpose-built benchmark and sustained domain-expert involvement, which is a longer effort than this response window allows. We are pursuing both directions: expanding the task scope, and improving the evaluation for the current scope.

### 4. What we are building next

Three things are in progress, and we would rather describe them accurately than over-promise:

- **A section-level semantic judge.** An LLM judge that compares candidate against reference one canonical GEOS section at a time (`Mesh`, `Solvers`, `Constitutive`, and so on), which is the granularity TreeSim already reports, so the two are directly comparable per section. We are using a judge from a different model family than the agent backbone so that self-preference is not a confound.
- **An output-side metric.** A mesh-independent, scale-free similarity measure between the simulation outputs of a candidate deck and those of the reference deck. This is the direct answer to nBNe's Q1 and we would rather report it as a standing metric than as a one-off check.
- **A tolerance-aware TreeSim.** Our current scorer treats any difference as a total mismatch at the leaf. A large fraction of the differences it penalises are physically immaterial, so a variant that does not treat those as failures is a fairer structural measure and we are validating it now.

### 5. Two results on what the evidence does support

Since the reviews turn on what our evidence establishes, we want to put two results in front of the reviewers positively rather than only defending the metric.

**The reliability finding now replicates across all three simulators.** gep1 and nBNe both singled this out as the paper's strongest result, and we think replication across interfaces is a stronger form of the claim than more runs on GEOS alone would be. On GEOS, per-cell across-run standard deviation falls from 0.081 for Vanilla to 0.002 (S+X), 0.005 (X+M) and 0.012 (SE), and 1 of 30 Vanilla runs produced a deck our scorer could not read against 0 of 30 for every adapter cell. On OpenFOAM at 30 tasks, every SIGA cell returns a complete case, while Foam-Agent leaves 11 tasks and MetaOpenFOAM 20 tasks incomplete. On LAMMPS there is almost nothing to prevent (structural score at least 0.976 everywhere), and consistent with that the completion gate contributes little while memory and retrieval carry the gain. The same mechanism, applied to three different interfaces, produces the pattern the mechanism predicts.

**The adapters are also faster on the hard tasks**, which the paper understates: the submitted version claims only that they impose no runtime overhead. On the held-out split the hand-designed cells are meaningfully more efficient than the bare harness.

| Cell | Tool calls / task | vs Vanilla | Wall seconds / task | vs Vanilla |
|---|---:|---:|---:|---:|
| Vanilla | 90.5 | | 416.5 | |
| X+M | 75.0 | **-17.1%** | 339.5 | **-18.5%** |
| S+X | 74.7 | **-17.5%** | 345.1 | **-17.2%** |

These gains are largest exactly where the reliability gains are, which we read as one effect rather than two: on hard tasks the bare harness thrashes, and grounding stops the thrashing. We will re-anchor the efficiency claim on these cells for the camera-ready, and note for completeness that the self-evolved cell does not share this property and uses more tool calls than Vanilla on held-out.

### 6. What we will state in the paper

We adopt the wording gep1 asked for, in the main body rather than the appendix:

> The evidence in this paper supports improved **structural authoring reliability**, meaning fewer unevaluable outputs and lower across-run variance on compound multiphysics tasks. It does not establish **validated simulator correctness**. TreeSim is a structural metric: a deck scoring 0.8 is not thereby shown to load, converge, or produce physically meaningful output.

The execution work above sharpens that sentence rather than softening it, and we would rather adopt the reviewer's wording than argue at the margin.
