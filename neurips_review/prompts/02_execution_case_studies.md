# Session prompt — GEOS execution case studies (rungs 3–5)

*Paste this into a fresh session started in `/home/matt/sci/repo3`.*

---

## Context

NeurIPS 2026 author-response window, submission 31642 (SIGA). The AC's **primary** objection, echoed by two of three reviewers:

> "The evaluation primarily measures structural similarity using TreeSim, rather than whether the generated configurations execute successfully, converge, or produce physically meaningful simulations. A small execution-based evaluation would substantially strengthen the central claim."

Reviewer gep1 was explicit: *"My score would increase if the reliability gains persist under execution or physical-validity checks,"* and asked for as little as "5 tasks across Vanilla and the best SIGA cell."

**This session's job:** run generated decks through the real GEOS binary and show empirically what a TreeSim gap means physically.

**Hard deadline Aug 3**; useful by ~Jul 31. Nothing here blocks the Jul 27 initial response — treat any result as upside.

Background: `neurips_review/SIGA_rebuttal_execution_plan.md` §4–5.

## The binary works — setup

```bash
export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH
$GEOSX_EXECUTABLE --help          # path is GEOSX_EXECUTABLE in .env
$GEOSX_EXECUTABLE -v -i deck.xml  # -v == --validate-input, "loading phase only"
```

Without the `LD_LIBRARY_PATH` prefix it fails on `GLIBCXX_3.4.30` because it picks up `/home/jixuan/anaconda3/lib/libstdc++.so.6`.

**Known compatibility gap, already checked:** the binary's generated schema has 263 elements vs 269 in `data/GEOS/src/coreComponents/schema/schema.xsd` — it is a slightly older build (Jan 15 2026). Missing: `CompositeFunction`, `SymbolicFunction`, and four `…ConformingFracturesALM` variants. Only **3 of 746** reference decks use any of them. **Pre-screen every deck anyway, and apply any exclusion identically across all cells** — an exclusion that hits one condition harder than another is a fairness bug.

The binary is owned by another user (`jixuan`). Do not depend on write access to that tree; copy what you need.

## Data

- Generated decks: `/data/shared/geophysics_agent_data/data/eval/autocamp_2026-05-01/dsv4/<cell>/<cell>_s<N>/<task>/`
- Reference decks: `data/GEOS/inputFiles/`
- Cells: Vanilla (`autocamp_F0`), best combo (`autocamp_F6` S+X or `autocamp_F4` X+M — check held-out), SE (`autocamp_SE`)

## Task selection — use this rule, don't hand-pick

Apply it and report which tasks it returned, so the selection is reproducible and defensible:

1. For each **held-out-eval** task, compute TreeSim spread = `max(cell mean) − min(cell mean)` across the three cells.
2. **Exclude** `TutorialHydraulicFractureWithAdvancedXML` — it scores ~0.013 across *every* cell (a universal model-level failure). Keep it aside as an optional negative control; it is not a case study.
3. **Take the top 2 by spread** — these are the two case studies. They should come out as `AdvancedExampleThermoPoroElasticWellbore` (≈0.355 → 0.761) and `ExampleProppantTest` (≈0.541 → 0.825). If they don't, trust the rule over this note and tell me.
4. **Add one ceiling control** — the *smallest*-spread task where all cells score high. This matters: it tests whether execution outcomes are identical when TreeSim says the decks are equivalent. Without it you cannot distinguish "TreeSim predicts execution" from "everything runs regardless."

Rationale for the top-2 rule: those two tasks are where the paper's entire held-out claim lives — the +0.069 Vanilla→SE gain is concentrated in exactly these catastrophic-failure rescues. If execution confirms the rescue, the paper's central claim is validated at the physics level. If it doesn't, we need to know before a reviewer does.

## Outcome ladder — how to establish "the simulation went OK"

Report every deck at the highest level it reaches. Levels 1–2 are the headline (they are gep1's literal ask); 3–4 are the physics.

| Level | Criterion | How |
|---|---|---|
| **L0** | Deck exists and is well-formed XML | already have |
| **L1** | Schema-valid | `xmllint --schema` vs the repo XSD |
| **L2** | **GEOS accepts the input** | `geosx -v -i deck` exits 0 |
| **L3** | **Runs to completion** | full run exits 0 **and** the log shows the final time reached (not just a clean exit — check the time-stepping actually finished) |
| **L4** | **Converged cleanly** | scrape the log for non-converged Newton / linear-solve warnings and timestep cuts; define a threshold up front and apply it identically to reference and generated |
| **L5** | **Physically comparable** | QoI within tolerance of the reference run (below) |

A deck that fails at L2 or L3 is **a result, not a hole.** Report the failure rate per cell — it directly supports the reliability claim.

## QoI comparison — preference order

Generated and reference decks often have **different meshes**, so do not compare fields point-wise; interpolation is fragile and a reviewer will attack the interpolation instead of the result. Use the first option that works and **report which one you used**:

1. **Preferred — identical injected observable.** Append the *same* standardized `Outputs`/`Tasks`/`TimeHistory` block to reference and generated decks alike, so every run emits the same scalar series. Document it as a normalization step. If it can't attach because region or field names differ, that itself is a recorded failure mode.
2. **Fallback — VTK final-state summary statistics.** Most GEOS example decks already write VTK. Compare mesh-independent scalars of the primary field at final time: min, max, mean, L2 norm. No interpolation needed.
3. **Fallback — log-scraped globals.** Total injected volume, mass balance, energy, iteration counts, plus a qualitative field plot.

Then compute **relative error vs the reference run** for 1–2 task-appropriate scalars (peak pressure, fracture half-length at final time, breakthrough time, total injected volume — pick per task and justify).

## Protocol

1. **Environment gate.** Verify `geosx --help` runs. Log the binary's build date and schema element count in the run record.
2. **Pre-screen** all decks for the 6 unsupported elements. Log exclusions.
3. **Run the reference decks FIRST — this is a gate, not a formality.** If a reference deck does not itself validate and converge under this binary, that task is unusable for L4–L5, and that is a disclosable finding. Do this before spending anything on generated decks.
4. **Smoketest one task end to end before estimating runtime for anything else.** Hydraulic-fracturing and thermoporoelastic-wellbore cases can be expensive. Do not estimate runtimes without a smoketest.
5. If the full time horizon is too expensive, **reduce `maxTime` identically in reference and generated decks.** Legitimate and disclosable; keeps the comparison fair. Never reduce it for one condition only.
6. **GEOS is deterministic — one run per deck.** No seed averaging, no repeats. (The three seeds here are *agent* seeds, i.e. different decks, not simulator repeats.)
7. Cap wall-clock per run and record timeouts as L3 failures.

## Deliverables

1. **The ladder table** — % of runs reaching each level, by cell. Plain markdown; this is what goes into the rebuttal, which allows no uploads or images.
2. **The key figure** — scatter: **x = TreeSim, y = relative QoI error (log scale)**, one point per (task, cell, seed), marker shape encoding L2/L3/L4/L5 outcome. This single plot answers "does structural similarity predict simulation similarity," which is the AC's question.
3. **Visual case study** — side-by-side final-state field renderings: reference vs Vanilla's deck vs SE's deck, for both case-study tasks. This is the figure that makes the point to a non-specialist.
4. Figure style: read `/home/matt/.claude/projects/-home-matt-sci-repo3-research-copilot/memory/user_figure_style_prefs.md` — rose-pine theme, Space Grotesk labels, Inconsolata numerals, setup at `writing/poster/scripts/posterstyle.py`. Advisor prefers charts over tables and wants chart-type variety.
5. An `XN-NNN` experiment note.

## Cautions

- **Do not oversell.** Even complete, this is 2–3 tasks. It is a **calibration study** answering "do TreeSim gains correspond to execution outcomes" — not a physics benchmark. Say so before gep1 does.
- **A low-TreeSim deck failing to run gives no QoI.** That is not missing data, it is the result. Report it as an L2/L3 failure rate.
- **Report negative results.** If the rescue tasks do *not* show better execution outcomes for SIGA, we need to know now, while we still control the disclosure. Do not quietly drop tasks.
- Never let an exclusion, timeout, or `maxTime` reduction apply asymmetrically across cells.

## First step

Set the environment, verify the binary, then run **one reference deck** for one case-study task end to end. Report the wall-clock, the log's convergence behaviour, and what output artifacts it produced — before touching any generated deck. That single run determines whether L3–L5 is feasible in the window at all.
