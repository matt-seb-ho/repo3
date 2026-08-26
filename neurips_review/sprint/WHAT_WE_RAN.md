# What we ran, and what it told us

A plain-language guide to the overnight work. No cross-references, no severity markers.

---

## First, the vocabulary you need

Everything below refers to a **validity ladder** — five increasingly demanding checks on a generated deck:

| Rung | Check | How |
|---|---|---|
| 1 | It's well-formed XML | `xmllint --noout` |
| 2 | It matches the GEOS schema | `xmllint --schema` |
| 3 | **GEOS will actually load it** | `geosx -v` |
| 4 | It runs to completion and converges | full run |
| 5 | Its physics matches the reference | compare outputs |

The paper reports rungs 1–2. The AC's objection is that rungs 3–5 are what matter.

Two other terms: **held-out** is the 10 hard tasks (3 seeds each = 30 runs per cell); **val** is the 17 easier tasks (17 × 3 = 51 runs per cell). **Cells** are experimental conditions — Vanilla (no adapters), S+X, X+M, SE, etc.

---

# Part 1 — The three campaigns you asked for

## Campaign 1: LLM as a judge

**The question.** TreeSim compares values at `rtol = 1e-6`, which is effectively exact equality — so it can't tell a permeability that's 2× off from one that's 18 orders of magnitude off. Can an LLM judge supply that missing sense of *how wrong* a wrong value is, and of whether a deck is physically sensible?

**What ran, in two attempts:**

**Attempt 1 (before you woke).** A comparative judge: show a model the generated deck, the reference deck, and the list of differences TreeSim flagged, and ask it to score physical plausibility. 90 decks, 3 judge models, each deck judged in both presentation orders to control for position bias.

*Result: it failed.* The three judges produced three different rankings of the conditions, and one of them ranked Vanilla **above** the best SIGA cell — reversing the paper's central result. Judge identity moved scores 4.8× more than the experimental condition did.

**Attempt 2 (your soft-TreeSim idea).** Keep TreeSim's whole algorithm — its tree matching, its section decomposition, its weighting — and replace only the innermost comparison with an LLM judgment, then aggregate in code rather than asking the model for a number. Per your steer, this judged at the **section** level (Constitutive, Mesh, Solvers, …) rather than per-value. Judge was `tencent/hy3` plus three others.

*Result: it failed its pre-registered bar too*, though far less badly — inter-judge agreement went from 41% to 70%, and the judges no longer disagreed about direction. But two of four still ordered the cells differently, which was the criterion that mattered.

**What we got anyway — three things worth keeping:**

1. **A per-section audit of TreeSim.** The judge is systematically more lenient than TreeSim on `Outputs` and `Events`, harsher on `Solvers` and `Constitutive`. That's a critique of our *metric*, and it doesn't require the judge to rank conditions reliably — which is the part that failed.
2. **A zero-LLM argument that's stronger than the judge.** Ten decks fail to load in GEOS, and TreeSim scores them **0.840** — above the held-out average. No LLM needed to make that point.
3. **A 3-line code fix beats the entire $12.70 LLM panel.** TreeSim throws away an element and its whole subtree when it can't pair it. Fixing that improves prediction of whether a deck loads more than four judge models did, for free.

**Bottom line:** two independently designed judges failed their own reliability tests. That's a reportable finding — it pre-empts "why didn't you just use an LLM judge?" — and the honest headline is that a deterministic fix outperformed the expensive semantic one.

---

## Campaign 2: Output-side evaluation

**The question.** Everything in the paper is measured on the *input* deck. Can we measure the *simulation output*, and does structural similarity actually predict simulation similarity? This is the AC's question, restated.

**What ran, in two stages:**

**Stage 1 — build the metric.** Generated and reference decks have different meshes, so you can't compare fields point-by-point without interpolation, which a reviewer would attack. Instead: inject an identical output block into both reference and generated decks, run both, and compare *mesh-independent summaries* (min, max, mean, RMS) of each physical quantity, normalised by the reference's own scale. Call it SOF. Validated on 6 tasks × 6 cells × 3 seeds = 108 runs.

**Stage 2 — scale it for statistical power.** The first pass was underpowered by its own analysis. Extended to 18 tasks and 489 runs, adding more held-out tasks and opening the val split.

**Results:**

- **Structure predicts simulation, moderately.** Spearman ρ = **0.31** pooled (n=489), CI [0.23, 0.39]. It explains roughly a tenth to a quarter of the variance. The first pass said 0.40 at n=108 — that came down with power, which is what scaling was for.
- **It varies enormously by task**: from 0.11 to 0.74. Never quote the pooled number alone.
- **It depends on an analysis choice.** Using the worst summary statistic instead of the average, the relationship is **not significant on the clean split** (ρ = 0.12, p = 0.18). Both have to be reported.
- **Conditions do not separate.** SIGA vs Vanilla on output fidelity: difference of 0.03, p = 0.90. You'd need roughly 2,000 runs per arm to detect it.
- **The most useful finding: conditional on a deck running, the physics is usually right.** Mean SOF among runs that produced output is **0.958**, with 46% matching the reference almost exactly. The gap is concentrated in decks that *fail to run*, not decks that run wrong.

**Bottom line:** structural similarity carries real but insufficient information about simulation fidelity, and our structural gains don't translate into measurably better simulations. But the fact that the physics gap lives in "did it run at all" supports leading with reliability.

---

## Campaign 3: Swapping the validator

**The question.** Our stop hook validates decks with `xmllint`. GEOS's own documentation recommends `xmllint`. But GEOS doesn't load decks with `xmllint` — it uses its own loader. Does that matter, and what happens if we use the real thing?

**Why we suspected it mattered.** 49 of 180 held-out decks (27%) pass `xmllint` but are **rejected by GEOS**. Every adapter cell scores a perfect 30/30 under `xmllint` while GEOS refuses 7–10 of the same decks. Our hook was certifying decks the simulator won't load. Meanwhile `xmllint` is *stricter* in one narrow way: it rejects `--` inside XML comments, which GEOS tolerates.

**What ran, in four pieces:**

1. **Build it and test one cell.** The hook runs inside a container that can't see the GEOS binary, so this needed a 388 MB self-contained runtime bundle. Then S+X re-run on held-out, 30 runs, everything held constant except the validator.
2. **Fix a bug it exposed and re-run.** The first version validated files that were never meant to stand alone — include fragments with no mesh. The agent's only way to satisfy that was to **invent a mesh**, which it did. Corrected rule, re-run.
3. **A second cell (S+X+M),** so the result didn't rest on one condition.
4. **A new condition: Vanilla plus nothing but the GEOS-validating hook** — no retrieval, no memory, no agent-callable validator. One line different from Vanilla, verified identical prompts.

**Results:**

- **The fabrication was our bug, not a property of the approach.** With the corrected rule: zero fabrications across all three arms. The lesson — "unreferenced is not the same as root" — is a real cautionary note about in-loop validation, but the approach is sound.
- **The hook alone does nearly everything the full adapter does.**

  | | Vanilla | S+X (full adapter) | **hook only** |
  |---|---:|---:|---:|
  | TreeSim | 0.720 | 0.781 | **0.784** |
  | rung 3 (loads) | 21/30 | 23/30 | **26/30** |
  | wall-clock | — | −17% | **−24%** |

- **But the attributable effect is tiny.** Across three arms the raw gains were +4, +1, +5 — yet once you exclude flips on runs the hook never touched, it's **+1 every time, always the same task**. The hook only fires 3–6 times per 30 runs.

**Bottom line:** the swap is a real, cheap improvement worth proposing — with the caveat that we measured its failure mode ourselves. But at this scale we cannot prove it does much.

---

# Part 2 — The five campaigns I added, and why

You said "run whatever takes a long time overnight, make reasonable decisions." I used that to verify the numbers we were about to hand a reviewer. That turned out to matter more than the new experiments.

## Campaign 4: Were we measuring our own bug?

**The question.** The single biggest category of "GEOS rejected this deck" was a missing data file — a property table or mesh file the deck referenced but that our harness never copied into the run directory. Is that the agent's failure or ours?

**What ran.** Reproduce the original sweep exactly (it matched, 0/180 disagreements), then stage every referenced file properly and re-measure all 180 decks.

**Result: ours.** That failure category went from 32 to zero. And with it, the execution claim collapsed: **Vanilla ties X+M exactly** at rung 3, and a per-task sign test is flat — Vanilla is worse on 4 tasks, **better on 3**, tied on 3.

**It also found a defect class nothing else can see.** Content-hashing the data files: **26% contain fabricated numbers.** The agent writes a file with the right name and invents the contents. No rung detects this, and SIGA doesn't reduce it. Worth knowing given we'd assumed those values were supplied.

## Campaign 5: Fixing TreeSim's matching, and what it uncovered

**The question.** TreeSim discards an element and everything under it when it can't pair it — so one unexpected attribute on a container zeroes ten correct children. Does fixing that change our conclusions?

**What ran.** Reproduce the published scorer exactly (bit-for-bit on all 180 held-out runs), apply the fix, re-score both splits — 741 runs.

**Result: it helps mildly and isn't free.** Only the SE contrast widens; S+X and S+X+M actually narrow, and the "40× variance reduction" claim would have to switch cells. Recommendation: disclose the defect, fix it for camera-ready, don't re-score mid-response.

**But it uncovered something much worse.** While verifying, it found the **val scoring pass ran before the val campaign finished**. `_summary.json` was written at 14:25:28; the decks it was supposed to score were written up to 14:32. One task is recorded as a failure when the scorer simply looked before the agent had written anything.

**This is why we must not publish the main-effects correction.** Both the published numbers and our "corrected" ones rest on that data. Held-out was verified clean, so every headline claim survives — but val is contaminated.

## Campaign 6: Is our last significant number real?

**The question.** After everything above, one significant result was left: schema validity, Vanilla 24/30 vs 30/30, p = 0.024. But Vanilla's three seeds were 8/10, 10/10, **6/10** — a big spread. And the new hook-only condition, which behaves like Vanilla at this rung, scored 30/30. Is 24/30 just an unlucky draw?

**What ran.** 14 more seeds on Vanilla and S+X — 17 total, 170 runs per cell — with the falsification criteria written down before any results existed.

**Result: the direction is real, the number was wrong.**

| | rate |
|---|---|
| published (3 seeds) | 24/30 = **80.0%** |
| **actual (17 seeds)** | 155/170 = **91.2%** |

Adapter cells: **270 runs, zero failures.** The real gap is **8.8 points, not 20** — we overstated our own effect by 2.3×. But it's now far better evidenced: a task-clustered bootstrap gives [+2.9, +16.5] points, p = 0.0006, a valid test the original never ran.

**Two more things from this:**
- **Two-thirds of the deficit isn't schema knowledge.** 10 of Vanilla's 15 failures are malformed XML — nested comments — not schema errors. The rung should be called "well-formed *and* schema-valid."
- **Rung 3 is now a firm negative.** 133/170 vs 132/170, and the interval **excludes any adapter advantage above 3 points.** Not underpowered — measured.

**And one structural limitation worth putting in the paper.** For a mechanism that only fires 3–6 times per 30 runs, we computed that **no number of seeds can ever make it statistically significant** on a 10-task benchmark, because the effect enters the clustered test as a scale factor that cancels. Only *more tasks* help. That applies to the paper's own S component.

---

# What this does to the rebuttal

**The shape of the response changes from "here is our win" to "here is what we checked, including what we got wrong."** With a borderline AC probing execution validity, that's the stronger position — but it is a different document from the one we started with.

**Claims that survive:**
- Adapters eliminate malformed and schema-invalid decks: **91.2% → 100%**, cluster-valid, now on 17 seeds.
- The effect is concentrated in preventing bad runs, not improving good ones — four independent lines of evidence.
- Conditional on running, the physics is usually right.

**Claims we should drop:**
- Any execution-level (rung 3) advantage. Measured negative.
- Any output-fidelity advantage. Not detectable at n = 489.
- The main-effects correction. Contaminated input.

**Things to volunteer, because we found them ourselves:**
- The 2.3× overstatement, corrected to 17 seeds.
- The flagship "catastrophic failure" deck loads fine in GEOS and reproduces the reference physics exactly.
- 26% of data files contain fabricated numbers.
- The benchmark cannot statistically resolve a mechanism this sparse at any seed count.

**Things to propose:**
- Swap the in-loop validator to GEOS's own loader, with its measured failure mode stated.
- A simulator-grounded hook alone recovers most of the benefit at lower cost.
