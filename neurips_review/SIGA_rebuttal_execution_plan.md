# SIGA Rebuttal — Detailed Execution Plan

**Working document (not for the advisor).** The advisor-facing summary is `SIGA_weaknesses_and_responses.md`.
Written 2026-07-26. Supersedes the tactics in `REBUTTAL_PLAN_v2_TIMELINE_GROUNDED.md`; that document's facts still stand except where corrected below.

---

## 0. What changed today — four findings that reshape the plan

**(1) The GEOS binary works.** `GEOSX_EXECUTABLE` in `.env` points at
`/data/jixuan/geophysics/GEOS/install-your-platform-release/bin/geosx`. It fails on first invocation because it picks up `/home/jixuan/anaconda3/lib/libstdc++.so.6`, which lacks `GLIBCXX_3.4.30`. Prepending the system library path fixes it:

```bash
export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH
$GEOSX_EXECUTABLE --help          # works
$GEOSX_EXECUTABLE -v -i deck.xml  # --validate-input == rung 3
```

`-v, --validate-input` ("only do the loading phase, and not actual simulation") is exactly what gep1 asked for. **The single blocking assumption of the previous plan — "no GEOS binary" — is false.** Rungs 3–5 are all reachable.

*Compatibility check, done:* the binary's generated schema has 263 elements vs 269 in the repo XSD (`data/GEOS/src/coreComponents/schema/schema.xsd`) — the binary is a strict subset, slightly older (built Jan 15 2026 vs schema Feb 8). The 6 missing elements are `CompositeFunction`, `SymbolicFunction`, and four `…ConformingFracturesALM` variants. Only **3 of 746** reference decks in `data/GEOS/inputFiles/` use any of them, so the risk is negligible — but pre-screen anyway and apply any exclusion identically across all cells.

**(2) The autocamp results are on disk after all**, at
`/data/shared/geophysics_agent_data/data/eval/autocamp_2026-05-01/dsv4/` — not under the repo. All 11 cells (F0–F8, F11, SE) × 3 seeds are present. Every number in Table 1 is locally verifiable.

**(3) The main-effects discrepancy is not an arithmetic error.** See §1 — it's a stale-input error, which is a much better story.

**(4) Claude Code version confirmed: `2.1.119`**, read from `system/init` events in run artifacts. On-disk history: 2.1.114 through 2026-04-27, then 2.1.119 from 2026-04-27 onward including the 2026-05-03 campaign. Autocamp (2026-05-01/02) is bracketed on both sides. Confirm directly against one autocamp `events.jsonl` now that the results are located. Note honestly that `run/Dockerfile` installs `@anthropic-ai/claude-code` **unpinned**, so the version tracked image build time — that concession costs nothing and is exactly nBNe's point.

---

## 1. The main-effects discrepancy — resolved

**It was never bad arithmetic.** `scripts/analyze_autocamp.py:409` `compute_main_effects()` is correct: it computes `mean(cells with factor=1) − mean(cells with factor=0)` over F0–F7, and `F_FACTORS` matches Table 1's cell labelling exactly (F0 Vanilla, F1 R+M, F2 S+M, F3 R+S, F4 X+M, F5 R+X, F6 S+X, F7 R+S+X+M — generator M = R⊕S⊕X, defining relation I = RSXM, a correct Resolution-IV design).

The script's own output (`docs/2026-05-02_autocamp_metrics.md`) lists the cell means it used:

| Cell | Script's mean | Table 1 val | Same? |
|---|---:|---:|:--:|
| F0 Vanilla | 0.910 | 0.910 | ✓ |
| F1 R+M | 0.885 | 0.885 | ✓ |
| F2 S+M | 0.919 | 0.919 | ✓ |
| **F3 R+S** | **0.874** | **0.857** | **✗** |
| F4 X+M | 0.921 | 0.921 | ✓ |
| F5 R+X | 0.893 | 0.893 | ✓ |
| F6 S+X | 0.917 | 0.917 | ✓ |
| F7 R+S+X+M | 0.885 | 0.885 | ✓ |

**One cell differs.** Recomputing the main effects with F3 = 0.874 reproduces the *published* values exactly — R −0.0325, S −0.0035, X +0.0070, M +0.0040 → the printed −0.032 / −0.003 / +0.007 / +0.004. Recomputing with F3 = 0.857 gives the arXiv values — R −0.0368, S −0.0078, X +0.0113, M +0.0083.

So: **F3's mean was revised from 0.874 to 0.857 at some point, Table 1 picked up the revision, and the appendix main-effects table was never regenerated.** (Corroborating signal: Table 1 reports R+S σ = 0.045 while the metrics doc reports 0.018 — consistent with one seed changing substantially, not with a rounding difference.)

**Is that concerning?** It's a normal and common failure mode — a derived table not regenerated after an upstream number moved — and it's far less alarming than a formula bug, which would have corrupted every downstream analysis. But two things should be nailed down before it's described to reviewers:

- [ ] **Why did F3 move 0.874 → 0.857?** Re-score, re-run, replaced seed, or a failures-as-zero convention applied later? The raw data is now locatable, so recompute F3 from `/data/shared/.../autocamp_F3/` and confirm 0.857 is the correct value. *Do not describe the correction publicly until you can say which value is right and why.*
- [ ] **Check for other stale derived numbers.** If the appendix table went stale, anything else generated from that snapshot may have too. Regenerate every derived figure from the current results and diff against the paper.

**How to present it:** "One factorial cell's mean was revised after the appendix main-effects table was generated, and the table was not regenerated. The corrected effects are R −0.037, S −0.008, X +0.011, M +0.008. All four move away from zero; in particular the negative retrieval effect is larger than reported, strengthening the paper's finding." Then note the internal inconsistency already visible in the submission (§5 and the appendix say −0.032, Limitations says −0.033).

**Do NOT say the bug fix produced the arXiv numbers.** It didn't — no re-run occurred, and the main effects are fully determined by the eight cell means, so any reviewer can check.

---

## 2. Native-plugin-prefix bug — settled

Full trace in the previous turn's analysis. Summary of what goes in the response:

- **Chronology:** fix `000b4ba` landed 2026-05-03; the autocamp factorial ran 2026-05-01/02. Table 1 is **pre-fix**. Only minimax × X+M was re-run post-fix (`4c668d9`, 0.392 → 0.867) — which is the number the paper already discloses. Do not claim Table 1 is post-fix.
- **Affected Table 1 rows:** all cells with `plugin_enabled=True` — R+M, S+M, R+S, X+M, R+X, S+X, R+S+X+M, S+X+M, SE-prose. **Vanilla did not** (`plugin_enabled=False`); **SE opted out** via `add_native_plugin_prefix=False`.
- **Magnitude, measured before the paper:** `abl_c9_no_prefix` was built for exactly this. `docs/ablation_C2_vs_C9.md`, 3 seeds × 17 tasks: C2 (prefix) 0.9134 vs C9 (no prefix) 0.9170, **Δ = +0.0036**, big-swing tasks (|Δ| ≥ 0.10) = **0**.
- **The "+0.24" is a mis-citation.** C1→C0 was +0.194 and C0→C2 +0.049 (≈ +0.243) — that was the lift being *explained*. The hypothesis "the prefix drives it" is explicitly refuted in `docs/2026-04-30_dsv4-ablation-final-v2.md`: *"C2→C9 (remove prefix) = +0.004 (null)."* Three later docs restate it as a "+0.24 anomaly attributable to the prefix." **Correct the internal docs so nobody quotes +0.24 in a rebuttal.**
- **Bias direction — both favourable.** R− cells were told to call an absent server → depressed → measured R is *less* negative than truth. Vanilla had no prefix while SIGA cells did → SIGA was handicapped → true advantage is *larger*. Both bounded at ~0.004.
- **Honest footnote:** SE-prose carried the prefix, SE did not, so that pairwise comparison has a small asymmetry (0.004 against a 0.022 gap — doesn't explain it, but say it first).

**Recommendation:** decline the re-run, disclose in the appendix as a process item, and ground the dismissal empirically ("we measured it with a dedicated 3-seed probe; +0.004, zero big-swing tasks") rather than chronologically.

---

## 3. S/X confound — answerable from existing data

**Resolution-IV is not the problem, and say so.** With I = RSXM, main effects alias only with three-factor interactions, so the S and X main effects are cleanly separated from each other and from all two-factor interactions.

Two things the design genuinely cannot do:
1. **S×X is aliased with R×M** — not estimable. That interaction is precisely "is X redundant once S is on?"
2. **Construct overlap** — both invoke `xmllint`, so even a clean X main effect means "agent-callable validator, averaged over configurations where a hook-enforced validator may also be present."

**The build-up ablation already answers gep1's question** (`docs/2026-04-30_dsv4-ablation-final-v2.md`, 3 seeds × 17 tasks, one factor at a time):

| Contrast | Isolates | Δ |
|---|---|---:|
| C2 → C6 | add hook-enforced `xmllint` (**S**) | **+0.008** |
| C6 → C7 | add voluntary agent-callable `xmllint` on top (**X**) | **−0.007** |

**X adds nothing once S is on.** gep1's bar — *"my confidence would increase if the stop-hook effect remains dominant after removing this confound"* — is cleared on val.

Caveat to state: the build-up ablation is val-only, and val is at ceiling for every cell. You do not have this separation on the hard tail, where the effect actually lives. Still, "not addressed" is wrong — this is a real answer that never made it into the paper's framing.

---

## 4. The evaluation argument — how to frame it

### 4.1 Lead with the claim that is immune to the whole objection

The headline is a **reliability** claim: catastrophic-failure reduction, σ 0.081 → 0.002. You do not need physics to know that an empty file, an unparseable file, or a timeout does not run. **Only the mean-lift claim depends on TreeSim's semantics.** The paper currently blurs these; separating them explicitly is the single strongest move available.

### 4.2 The determinism argument — reframed

Do **not** say "GEOS is deterministic, therefore input-side evaluation is fair." Determinism says the input→output map is a function; it gives you *identical deck ⇒ identical simulation*. Your decks score ~0.78, not 1.0, and determinism says nothing about what a 0.78-similar deck produces. It is a statement that the map exists, not that it is well-conditioned — and PDE solvers are ill-conditioned exactly where it matters.

Claim this instead:

> **The deck is a sufficient statistic for the simulation.** No hidden state, no stochasticity, no run-to-run variation — everything about the result is determined by the input file. Deck authoring is therefore a well-posed target of study, and the open question is the *metric on decks*, not the *choice to evaluate decks*.

Bonus that follows: determinism means **one execution per deck suffices**, no averaging over simulator seeds — so the execution study is cheaper than it looks.

### 4.3 The two acknowledged gaps

**Gap A — sensitivity.** How much simulation difference does a TreeSim gap correspond to? Unknown. Addressed by the execution study in §5.

**Gap B — non-uniqueness.** An alternative deck could produce the same physics. The brief-specificity argument is fine but secondary. **Lead with the common-mode argument:** TreeSim penalizes correct-but-different decks for *every* cell equally, since all cells are scored against the same reference with the same metric. It depresses the absolute level for everyone and leaves the *contrast* intact. Non-uniqueness attacks "SIGA scores 0.78," not "SIGA beats Vanilla by 0.069." Use brief-specificity as the reason the alternative-spec space is small to begin with.

### 4.4 What TreeSim actually measures — state it precisely

From `src/eval/judge_geos.py`, TreeSim is **not** a string match: it resolves XML includes, bipartite-matches elements, scores tag match + `name`-attribute bonus (0.4) + attribute-value overlap, penalizes hallucinated elements (β = 0.1), and weights own-attributes vs subtree at α = 0.3 for interior nodes. Attribute values go through `values_equivalent`, which parses scalars and float lists and compares numerically at `NUMERIC_RTOL = 1e-6`, falling back to case-insensitive string equality.

So `1e6`, `1000000`, and `1.0e+06` all match. **But rtol = 1e-6 is effectively exact equality, so TreeSim has no notion of how wrong a wrong value is** — a permeability off by 2× and one off by 18 orders of magnitude score identically. It also has no notion of physical equivalence (unit changes, renamed regions, equivalent formulations, different-but-valid discretizations all read as mismatches).

That framing sets up the LMaaJ metric precisely: **its job is to supply the magnitude-and-plausibility dimension a 1e-6 tolerance cannot express.**

### 4.5 The ladder, defined

| Rung | Check | Needs binary | Status |
|---|---|:--:|---|
| 1 | Well-formed XML | No | Have it |
| 2 | Schema-valid (`xmllint --schema` vs GEOS XSD) | No | Have it |
| 3 | GEOS accepts input (`geosx -v`) | Yes | **Now reachable** |
| 4 | Runs to completion / solver converges | Yes | **Now reachable** |
| 5 | Physically meaningful (QoI vs reference) | Yes | **Now reachable** |

---

## 5. New experiment A — execution study (rungs 3–5)

**Purpose:** establish the empirical mapping from TreeSim distance to simulation-output difference — the missing modulus of continuity — and answer the AC's primary objection directly.

### Scope

Three cells (**Vanilla**, **best combo** — S+X or X+M, **SE**) × **held-out-eval** tasks × 3 seeds. Held-out is the right split: val is at ceiling and has no spread to explain, while held-out spans a wide per-task range (`AdvancedExampleThermoPoroElasticWellbore` 0.355 → 0.761; `ExampleProppantTest` 0.541 → 0.825). Those two rescue tasks are the ideal case studies — they are where the paper's whole claim lives.

Start with those 2 tasks × 3 cells × 3 seeds = 18 runs + 2 reference runs. Expand if cheap.

### Procedure

1. **Environment gate.** `export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH`. Verify `geosx --help` runs. Record the binary's build date and schema element count in the run log.
2. **Pre-screen** every deck (reference *and* generated) for the 6 elements the binary lacks. Exclude affected tasks identically across all cells; log any exclusion.
3. **Run the reference decks first.** This is a gate, not a formality: if a reference deck does not itself validate/converge, the task is unusable for rungs 4–5 — and that is a disclosable finding in its own right. Do this before spending anything on generated decks.
4. **Rung 3** — `geosx -v -i <deck>` for every deck. Binary pass/fail. Cheap, fast, and on its own it answers gep1's literal ask.
5. **Rung 4** — full run with a wall-clock cap. Record exit code, whether time-stepping completed, and Newton/linear-solver convergence from the log. If the horizon is too expensive, reduce `maxTime` **identically in reference and generated decks** — a legitimate, disclosable modification that keeps the comparison fair.
6. **Rung 5 — QoI extraction.** **Compare scalar time-history outputs, not fields.** Generated and reference decks frequently have different meshes, and field comparison would require interpolation — fragile, and a reviewer would attack the interpolation rather than the result. GEOS `TimeHistory` collection writes HDF5 series; extract 1–2 task-appropriate scalars (peak pressure, fracture half-length at final time, breakthrough time, total injected volume) and compute relative error vs the reference run. This is also what a domain scientist would actually compare.
7. **Determinism means one run per deck.** No repeats.

### Outputs

- **The figure the AC is asking for:** scatter, x = TreeSim, y = relative QoI error (log scale), one point per (task, cell, seed), marker shape encoding rung-3/4 outcome (validates / runs / converges / diverges). This single plot answers "does structural similarity predict simulation similarity."
- **The ladder table:** % of runs passing each rung, by cell. Plain text, survives the no-uploads constraint.
- **Visual case study:** side-by-side output plots for the two rescue tasks — Vanilla's failing deck vs SE's succeeding deck vs reference.

### Honest risks to plan for

- **Runtime is unknown.** Smoketest one task end-to-end before estimating anything — hydraulic-fracturing and thermoporoelastic-wellbore cases can be expensive.
- **A low-TreeSim deck may fail to run at all**, giving no QoI. That is not a hole; it is a result — report it as a rung-4 failure rate and it strengthens the reliability story.
- **The binary is one build on one machine** (owned by another user, `jixuan`). Do not let the study depend on write access to that tree; copy what you need.
- **Do not oversell.** Even complete, this is 2–3 tasks. It is a *calibration study* answering "do TreeSim gains correspond to execution outcomes," not a full physics benchmark. Say that before gep1 does.

---

## 6. New experiment B — LMaaJ semantic metric

**Purpose:** cover the semantic gap TreeSim's `rtol = 1e-6` cannot express, as a second metric on a subset. Needs no binary, so it is the highest-feasibility item and can run in parallel with §5.

**Scope:** Vanilla, best combo, SE × held-out-10 × 3 seeds = 90 decks.

Design decisions to settle in a dedicated session, but the load-bearing ones:

- **Comparative, not absolute** — judge the generated deck *against the reference deck*, which is the same information TreeSim uses.
- **Feed it the TreeSim diff, not just the two files.** The gap being targeted is magnitude-blindness on flagged attribute mismatches; showing the judge exactly which attributes differ points its budget at the right question.
- **Score dimensions:** (a) physical plausibility of parameter values, (b) whether each difference is physically material or cosmetic, (c) whether the deck specifies the requested physics at all.
- **Multiple queries:** several judge models plus A/B position swapping to control order bias; report inter-judge agreement, not just the mean.
- **Blind the judge** to which cell produced which deck.
- **Do not use a judge from the same family as any scored backbone** — that is the flaw in the LAMMPS study and reviewers will apply it here too.
- **Calibrate against §5.** On the subset where you have execution outcomes, correlate LMaaJ score with rung 3/4/5 results. A judge validated against execution is a far stronger instrument than a free-floating one — and it converts "we added an LLM metric" into "we added a metric and showed it tracks ground truth."

---

## 7. Scale — OpenFOAM 30 + LAMMPS

Report the 30-task OpenFOAM campaign (with MetaOpenFOAM as second baseline) and handle the reversal openly: Vanilla coverage 3/5 → 30/30, S effect +0.328 → +0.168, M effect +0.192 → −0.007. Offering it means saying the submitted n=5 result was noise-dominated; do it anyway, since a reviewer finding the reversal later is worse. Keep transfer claims explicitly qualitative, which is gep1's own stated fallback.

**LAMMPS:** include, but for **nBNe and the AC's scale bullet only**, explicitly labelled preliminary and qualitative. It answers "more diverse task types," which OpenFOAM alone does not. Do not lead with it for gep1 and never let it drift toward the execution ask — the agent never runs LAMMPS, making it the *least* execution-grounded study in the paper. Its LLM judge is also one of the two backbones it scores; expect that to be noticed.

---

## 8. Clarity

Mine the arXiv rewrite for definitions, framing, and worked examples. That is your own text and reusing it is not a paper revision.

**But rewrite the wording rather than pasting verbatim.** If the arXiv version is publicly posted, a distinctive sentence is searchable and lands a reviewer on a non-anonymous preprint — an unforced anonymity violation. Same content, different sentences.

Items still needing new writing either way (the arXiv version didn't fix them): a worked example of a "brief" and of "structured repair feedback," and the Buckley–Leverett gloss.

**Open question:** is the arXiv version actually posted? That determines how careful to be.

---

## 9. Sequencing

Everything below is gated on the 2026-08-03 hard stop (Phase 3 is reviewer/AC only — nothing posted after that is visible to you).

| Priority | Item | Blocking? |
|---|---|:--:|
| 1 | Confirm F3 = 0.857 from raw data; regenerate all derived tables | **Yes** — blocks quoting any corrected number |
| 2 | Verify the schema-validity ladder (24/30 vs 30/30) against `/data/shared/...` | **Yes** — centrepiece of the response |
| 3 | Smoketest one GEOS execution end-to-end; get a real runtime estimate | **Yes** — sizes everything in §5 |
| 4 | Confirm Claude Code version from an autocamp `events.jsonl` | No |
| 5 | Correct the "+0.24" mis-citation in the internal docs | No |
| 6 | Rung 3 (`--validate-input`) across all three cells | No — cheap, high value |
| 7 | LMaaJ design session, then run | No |
| 8 | Rungs 4–5 on the two rescue tasks | No — highest value, highest risk |
| 9 | Draft the four responses from existing data | **Yes** — must not wait on 6–8 |

**The initial response must be written so that nothing in §5 or §6 is load-bearing.** Anything that lands by Aug 3 goes in as a follow-up comment — pure upside. Do not promise a delivery date for the execution study: a missed promise lands immediately before Phase 3, when you can no longer respond to it.

---

## 10. Open items

- [ ] Why did F3 move 0.874 → 0.857? Which value is correct?
- [ ] Any other derived numbers stale from the same snapshot?
- [ ] Is the arXiv version publicly posted (anonymity constraint on quoted text)?
- [ ] Does the reference deck for each rescue task actually converge under this binary?
- [ ] Confirm the `/data/shared/` results are complete for all 11 cells × 3 seeds, and that held-out decks are present.
