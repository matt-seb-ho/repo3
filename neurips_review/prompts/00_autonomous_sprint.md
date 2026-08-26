# Session prompt — Autonomous sprint to the Jul 27 initial response

*Paste into a fresh session started in `/home/matt/sci/repo3`. This session is expected to run for many hours, dispatch subagents in parallel, and loop until the done-conditions below are met.*

---

## Mission

Produce the four NeurIPS 2026 author responses for submission 31642 (SIGA), **plus as much new evidence as fits**, by **Jul 27 AOE (05:00 PT on Jul 28)**.

Scores: gep1 **4** (borderline accept) · kEdh **2** (reject) · nBNe **5** (accept) · AC **borderline**. gep1 is the winnable score; the AC's meta-review is the spec.

You have roughly **36 hours**. Work continuously, parallelize aggressively, and checkpoint often.

## Read first

1. `neurips_review/neurips_timeline_instructions.md` — the rules, read literally
2. `neurips_review/siga_neurips_reviews_clean.md` — reviews + meta-review
3. `neurips_review/MASTER_TODO.md` — owners, priorities, what's blocking
4. `neurips_review/SIGA_rebuttal_execution_plan.md` — our positions with evidence
5. `neurips_review/prompts/03_rebuttal_drafting.md` — drafting spec, budgets, hard rules

## Verified facts — do not re-derive these, but do re-verify any number before it reaches a reviewer

**The GEOS binary works, and it is fast.** Measured today:

```bash
export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH
GEOSX=/data/jixuan/geophysics/GEOS/install-your-platform-release/bin/geosx
```
- `geosx -v -i deck.xml` (validate-input): **~2.5 s/deck**
- Full run of a `_smoke.xml` variant: **~8.9 s**, and it emits `pressureHistory_*.hdf5`, `temperatureHistory_*.hdf5`, `stressHistory_*.hdf5`, `displacementHistory.hdf5` (TimeHistory series → QoI) plus `vtkOutput/` (field visualization)
- **Run from the deck's own directory** — `<Included>` paths resolve relative to cwd
- GEOS version 1.1.0 (sha1 58178e427). Its schema has 263 elements vs 269 in `data/GEOS/src/coreComponents/schema/schema.xsd`; the 6 it lacks are used by only 3 of 746 reference decks. Pre-screen, and apply any exclusion **identically across cells**
- **Validated example:** reference `ThermoPoroElasticWellbore_benchmark.xml` → exit 0. Generated F6/s1 version of the same task → exit 1, `Group … elementRegionsGroup has no child named rock` — a real dangling-reference error, exactly the class TreeSim cannot see. This is the finding to scale up.

**Data locations:**
- Held-out (ICL-10) generated decks: `/data/shared/geophysics_agent_data/data/eval/autocamp_followup_2026-05-02/icl/<cell>/<cell>_icl_s<N>/<task>/inputs/*.xml`
  Cells: `autocamp_F0` (Vanilla), `autocamp_F4`, `autocamp_F6`, `autocamp_F8`, `autocamp_F11`, `autocamp_SE`. **30 task-runs per cell** (10 tasks × 3 seeds).
- Held-out scores: `…/autocamp_followup_2026-05-02/_results_icl/<CELL>_icl_s<N>/…/*_eval.json`
- Val (17-task) results: `/data/shared/geophysics_agent_data/data/eval/autocamp_2026-05-01/dsv4/<cell>/`
- Reference decks: `data/GEOS/inputFiles/`
- TreeSim implementation: `src/eval/judge_geos.py`
- Cost accounting: read `/home/matt/.claude/projects/-home-matt-sci-repo3-research-copilot/memory/reference_deepseek_cost_accounting.md` before quoting any dollar figure — two known traps
- Figure style: `/home/matt/.claude/projects/-home-matt-sci-repo3-research-copilot/memory/user_figure_style_prefs.md`

## Plan

### Phase 0 — Verification gate (do first, serially, ~1–2 h). Blocks everything quotable.

1. **Resolve F3 (R+S).** `scripts/analyze_autocamp.py` used 0.874; Table 1 says 0.857. That single difference fully explains the main-effects discrepancy with the arXiv version. Recompute from `/data/shared/…/autocamp_2026-05-01/dsv4/autocamp_F3/` and determine **which is correct and why it moved**. Until this is settled, the main-effects correction cannot be volunteered.
2. **Verify the schema-validity ladder** — the claim is Vanilla 24/30 vs 30/30 for SIGA cells on held-out. Re-run `xmllint --schema` yourself against `data/GEOS/src/coreComponents/schema/schema.xsd`. This is the centrepiece of the AC response; it currently comes from a plan doc, not a re-run.
3. **Regenerate all derived tables** and diff against the submitted `writing/neurips/neurips_2026.tex`. If one derived table went stale, others may have.
4. **Confirm the Claude Code version** from an autocamp `events.jsonl` (expect `2.1.119`).

**If (1) cannot be resolved, drop the main-effects correction from the response entirely and say nothing about it.** A wrong correction is worse than no correction.

### Phase 1 — Parallel evidence tracks (dispatch concurrently, ~4–6 h each)

Run these as independent subagents. **None may block Phase 2.**

**Track A — Execution ladder (highest value; this is the AC's primary objection).**
- Rung 3: `geosx -v` across **F0, F6, SE × 10 held-out tasks × 3 seeds** = 90 runs ≈ 4 min compute. Report pass rate per cell, and **classify the failures** (dangling reference, missing region, bad attribute) — the classification is worth as much as the rate.
- Rung 4: full runs, preferring `_smoke.xml` variants where present on both sides. 90 runs ≈ 15 min compute. Cap wall-clock per run; record timeouts as failures.
- Rung 5: QoI from the TimeHistory HDF5 files — relative error vs the reference run on 1–2 task-appropriate scalars.
- **Run reference decks first as a gate.** If a reference does not itself validate/converge, that task is unusable for rungs 4–5 and that is a disclosable finding.
- Deliverable: ladder table (plain markdown — the rebuttal allows no images), plus the scatter `x = TreeSim, y = relative QoI error (log)`, marker = rung reached.
- Full spec: `prompts/02_execution_case_studies.md`

**Track B — LMaaJ secondary metric.**
- 3 cells × 10 tasks × 3 seeds = 90 decks; judge each **against the reference deck**, feeding it the TreeSim diff.
- Multiple judge models + A/B position swap; report inter-judge agreement.
- **No judge from the same family as the scored backbone** (`deepseek-v4-flash`).
- Calibrate against Track A's outcomes as they land.
- Full spec: `prompts/01_lmaaj_metric.md`

**Track C — Writeups from data already in hand (fast, ~1 h).**
- S/X separation: `C2→C6` = **+0.008**, `C6→C7` = **−0.007** (`docs/2026-04-30_dsv4-ablation-final-v2.md`). Verify both numbers at source.
- Prefix-bug probe: C2 0.9134 vs C9 0.9170, **Δ = +0.0036**, zero big-swing tasks (`docs/ablation_C2_vs_C9.md`). Verify.
- Fix the **"+0.24" mis-citation** in `src/runner/agents.py:425` and three docs. The correct value is **+0.004**.

### Phase 2 — Draft the four responses (start by hour ~12, don't wait for Phase 1)

Per `prompts/03_rebuttal_drafting.md`. Budgets: gep1 ~9,500 · kEdh ~7,000 · nBNe ~3,500 · AC ~5,000 characters.

**Write the first complete draft using only Phase 0 + Track C evidence.** Then fold in Tracks A and B as they land. This guarantees a postable response regardless of what finishes.

## Done conditions

Stop and report when **all** of these hold:

- [ ] Four response texts exist, each under its character budget, in `neurips_review/responses/`
- [ ] **Every number in them traces to a file on disk** — maintain a provenance table mapping each figure to its source path
- [ ] Phase 0 items 1–4 resolved, or explicitly excluded from the responses with a note
- [ ] Track A rung-3 results included, or a stated reason why not
- [ ] A short summary listing what landed, what didn't, and what a human must decide before posting

## Hard rules

1. **Do not post anything to OpenReview.** Produce text files; a human posts them.
2. **Every number traces to a file.** No number from a summary doc, a memory, or another agent's report without opening the source. gep1 recomputes things.
3. **Never quote "+0.24"** for the prefix effect — the measured value is **+0.004**.
4. **Do not claim Table 1 is post-prefix-fix.** The fix landed 2026-05-03; the factorial ran 2026-05-01/02.
5. **Do not say the bug fix produced the arXiv main-effects numbers.** One cell's mean was revised; the appendix table was never regenerated.
6. **Never pair a mean from one cell with a σ from another.** Print the per-cell σ table instead (Vanilla 0.081 · X+M 0.005 · S+X 0.002 · SE 0.012).
7. **Do not oversell schema validity as answering the execution ask** — it is rung 2 of 5.
8. **Paraphrase arXiv text; never paste verbatim** (the preprint may be public — anonymity risk).
9. **Report negative results.** If execution shows SIGA decks fail as often as Vanilla's, say so immediately and loudly — we need to know while we still control the disclosure.
10. **Apply every exclusion, timeout, and `maxTime` reduction identically across cells.** Asymmetric handling is a fairness bug.
11. **Do not promise reviewers a delivery date** for pending experiments.

## Escalate to the human — do not decide these alone

- Whether to include the OpenFOAM n=30 reversal or LAMMPS (advisor input pending)
- The R2 / clarity posture and how hard to commit to the camera-ready rewrite (advisor input pending)
- Whether to volunteer the main-effects correction (advisor input pending)
- Any result that would **weaken** a claim in the submitted paper — surface it immediately, don't bury it in a summary
- Anything requiring spend above trivial API cost

## Working discipline

- Set up checkpointing at the start: `/loop 15m Update checkpoint.md with current task, in-progress files, key numbers, blockers, next steps.`
- Update `status.md` phase as you move (TEST while running, THINK while analyzing).
- **Smoketest before every batch.** One task, one cell, one seed, inspect the raw output, *then* scale.
- Log every launched batch with its command so results are reproducible.
- When a track finishes, immediately fold its numbers into the draft and update the provenance table — don't leave integration to the end.
- If a track stalls for more than ~2 hours with no progress, cut it and reallocate. The response is the deliverable; the experiments are upside.

## First actions

1. Read the five documents listed above.
2. Verify the GEOS environment reproduces the two measurements quoted here (2.5 s validate, 8.9 s smoke run).
3. Start Phase 0 item 1 (F3) yourself — it is blocking and needs judgment.
4. Dispatch Tracks A, B, C as parallel subagents.
5. Report back with: F3's resolution, the rung-3 pass rates, and a draft outline with character budgets — before writing any response prose.
