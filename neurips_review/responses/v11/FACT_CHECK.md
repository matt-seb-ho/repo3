# Fact check — condensed (top) half vs. settled (bottom) half of `v10/draft.md`

Scope: every number and claim in the top half checked against (a) the bottom half and
(b) the underlying sprint artifacts. Line numbers are from `v10/draft.md`.

Verdict key: ✅ consistent · ⚠️ consistent but a caveat was dropped · ❌ wrong or unsupported

---

## Summary

- **No number in the top half is numerically wrong.** Every figure I could trace matches the
  bottom half and the sprint artifacts.
- **Three claims are unsupported or overstated** because a qualifier was dropped in
  compression (F1, F4, F5).
- **Two problems are inherited from the bottom half**, i.e. they are wrong in *both* versions
  and need fixing regardless of which you post (F8, F9).
- **Two internal inconsistencies** exist between sections of the top half itself (F6, F7).

---

## ❌ Unsupported / overstated in the top half

### F1 — "SIGA's reliability extends beyond structural correctness" (L13, AC)
> "These results confirm SIGA's reliability extends beyond structural correctness as measured
> by TreeSim: the generated configurations execute reliably and closely reproduce the intended
> physical behavior."

**This does not follow from 0.958.** The 0.958 is a mean over *all cells* conditional on
running. On the output-fidelity axis, cell separation is **not detectable on any split**, and
the held-out point estimate slightly favours **Vanilla** (Δ = −0.0073, MW p = 0.409;
`SPRINT_LOG.md` F54, corroborated independently by threads B, D and J2). The correct claim —
the one the bottom half makes — is that *the physics gap sits in decks that fail to run, not
in decks that run wrong*, which supports the **reliability-first** framing without asserting
a physics improvement.

The bottom half says exactly this and no more:
> "the gap between structure and physics sits in decks that fail to run, not in decks that run
> and are wrong" (L280).

**Fix:** replace the sentence. Suggested wording is in `draft.md`.

### F2 — "27 of 30 accepted … all 77 of 77 completed" reads as a contradiction (L11, AC)
77 > 30. These are two different populations: 27/30 is the S+X held-out arm with GEOS's native
input check in the adapter loop (3 seeds × 10 tasks); 77/77 is the convergence count from the
execution grid (`K3_per_run.csv`). Putting them in consecutive sentences with no denominators
invites the reviewer to ask which 77.

Note: **this population question was raised during v8→v9 and never answered**
(`hand_v9/CHANGES_v8_to_v9.md`, INPUT-3: *"Is 77 of 77 the same population as 31 of 31? … If
they are different populations, 77/77 should revert to 31/31."*). This is the one number in
the rebuttal whose provenance is still formally open. Resolve or hedge before posting.

The bottom half survives this only because it separates the two into different bullets with
explicit run counts ("at 17 runs per cell" / "at 3 runs per cell").

### F3 — the S-vs-X isolation loses its hedge (L43–48, gep1)
Top half presents X+M 0.768 ± 0.005 → S+X+M 0.783 ± 0.022 and concludes "adding S improves the
result", full stop. The bottom half adds the sentence that makes this defensible:
> "These are three runs per cell, so we would not over-read the margins between adapter cells,
> and we would be glad to run a dedicated build-up experiment isolating the interaction." (L315)

Independently, the verified paired build-up (`PROVENANCE.md` #5) puts the S effect at
**+0.0077, t(16) = 1.09, CI [−0.007, +0.023] — not significant.** Asserting the improvement
without the hedge is the exact thing gep1 is probing. **Restore the hedge.**

### F4 — "17 runs per task" is applied to a cell that did not run 17 (L31, gep1 / L146, nBNe)
> "We increased the evaluation from 3 to 17 runs per task. Vanilla produced … 155/170 … 170/170
> for S+X and 100/100 for X+M."

170 = 17 × 10 tasks. **100 is not 17 × 10.** X+M evidently ran ~10 runs per cell. This was
flagged as INPUT-4 in v8→v9 and resolved there *by switching to proportions* — the bottom half
consequently says "17 runs per cell" only where it is true and gives raw counts elsewhere. The
top half re-introduces the arithmetic tell. **Fix:** state "91.2% (155 of 170)", "100% (170 of
170)", "100% (100 of 100)" and drop the blanket "17 runs per task", or say "17 runs per cell
for Vanilla and S+X".

### F5 — the "strictly perfect" replacement drops the operational definition (L104, kEdh)
kEdh's complaint (item 3) is precisely that "strictly perfect" is used at line 86 of the paper
and only operationalised at line 216 as **structural similarity ≥ 0.999**. The top half's
replacement — "outputs that nearly match the reference" — replaces one vague phrase with
another and **does not answer the review**. The bottom half's replacement keeps the number:
> "No configuration increased the number of decks that matched the reference almost exactly
> (structural similarity above 0.999)." (L355)

**Restore the 0.999.**

---

## ⚠️ Internal inconsistencies within the top half

### F6 — the LLM-judge metric appears in the AC section but nowhere else
Top-half AC (L228–229) reports the physics-plausibility judge (Spearman ρ = 0.418, p = 0.0006).
Top-half gep1 and nBNe do not mention it at all. In the bottom half it appears in all three.
gep1 and nBNe are the two reviewers who asked for evaluation beyond structure, so dropping it
from their threads and keeping it in the AC's is backwards. Either add it to gep1 (with the
bottom half's "needs calibration against domain experts before we would offer it as a metric"
caveat) or drop it from the AC.

### F7 — the "46 candidate examples" bound is in nBNe but not gep1
Top gep1 W2 (L68) says only "bounded by the available GEOS documentation examples"; top nBNe
W4 (L174) gives the concrete "46 candidate examples in total". Same objection, two different
levels of specificity, in the same posting. Use 46 in both — it is the stronger answer and
it is verified.

---

## ❌ Wrong in **both** halves — fix regardless of which you post

### F8 — "a 10-task subset of the same pool" is not accurate
Both halves describe the external-baseline task set as "a 10-task subset of the same pool"
(top L56, bottom L294). The baseline methodology doc says otherwise:

> "`foamgpt_subset_seed42_n10_combined/` — a 10-task set built for this baseline comparison:
> the 5 original tasks used in earlier baseline runs (`boundaryWallFunctionsProfile`,
> `Grossetete`, `helmholtzResonance`, `externalCoupledCavity`, `damBreakWithObstacle`) plus 5
> more drawn at random (seed 42) from the remaining 29 cases in the 30-task ablation pool
> (`periodicCubeWater`, `cavityClipped`, `aachenBomb`, `simpleShapes`, `damBreak`).
> `externalCoupledCavity` is the one case shared between the two source sets."
> — `hand_v9/2026-07-28_metaopenfoam-baseline-results.md`

So **6 of the 10 tasks are in the 30-task ablation pool; 4 are not**
(`boundaryWallFunctionsProfile`, `Grossetete`, `helmholtzResonance`, `damBreakWithObstacle` —
verified absent from the n30 per-task tables in `docs/openfoam_n30/`). Accurate phrasing:
*"a 10-task set drawn from the same benchmark family, six of whose tasks are in the 30-task
ablation pool."*

**Knock-on:** this is why the top half's `[insert executable count]/10` TODO **cannot be
filled by filtering existing data.** The v8→v9 note (INPUT-1) assumed it could — that
assumption is wrong. SIGA has per-task data for at most 6 of the 10. Either run SIGA on the
missing 4, report the matched **6**, or keep the current unmatched-but-disclosed framing.
See `RECOMMENDATIONS.md` R3.

### F9 — the ρ = 0.362 aggregator sensitivity is suppressed in both halves
Both halves quote ρ = 0.362 (95% CI 0.197–0.505, p = 0.0001) with no aggregator caveat. Under
the worst-reduction aggregator the same held-out split gives **ρ = 0.121, p = 0.176 — not
significant** (`SPRINT_LOG.md` F54; `J2_output_metric.md` §9.6 calls this "the single largest
analytic sensitivity in the study and it must not be buried"; the sprint's standing rule H31
is *"any use of ρ must report both aggregators"*).

gep1 is the reviewer most likely to ask how the metric was built. Volunteering it in one
clause costs ~15 words and removes the discovery risk. Suggested:
> "…ρ = 0.362 (95% CI 0.197–0.505) under our declared mean-over-reductions aggregator; under a
> worst-reduction aggregator the same association is ρ = 0.121 and not significant, which we
> will report alongside it."

---

## ✅ Verified consistent (top half ↔ bottom half ↔ artifacts)

| Claim (top half) | Source | Status |
|---|---|---|
| Vanilla 155/170 schema-valid; S+X 170/170; X+M 100/100; gap 8.8 pp, CI [+2.9, +16.5], p = 0.0006 | `K5_seed_stability.md`; `EVAL_WORK_EXPLAINED.md` | ✅ |
| GEOS accepted 27/30 S+X; 133/170 Vanilla | `K5`, `SPRINT_LOG` F53/F54 | ✅ |
| mean output fidelity 0.958; 46% ≥ 0.999 | `SPRINT_LOG` F54 (held-out `SOF_ran`, n = 91) | ✅ |
| TreeSim–fidelity ρ = 0.362, CI [0.197, 0.505], p = 0.0001 | `SPRINT_LOG` L432; `L2_physics_weighted_treesim.md` | ✅ (but see F9) |
| Judge–fidelity ρ = 0.418, p = 0.0006 | `L1_judge_vs_physics.md` L46 | ✅ |
| Prefix bug: 0.913 → 0.917, Δ +0.004, no task moves > 0.10 | `PROVENANCE.md` #6 (0.913398/0.916965, per-task Δ ∈ [−0.036, +0.074]) | ✅ |
| X+M 0.768 ± 0.005, S+X+M 0.783 ± 0.022, S+X 0.781 | `PROVENANCE.md` #7 (per-cell σ) | ✅ |
| OpenFOAM best cell 26/29 executable (89.7%), Vanilla 4/30, seeds 0.668 / 0.685 / 0.665 | `hand_v9/2026-07-28_siga-3seed-real-validator-results.md` | ✅ |
| Foam-Agent 1/10 executable; MetaOpenFOAM 2/9 | the two baseline docs | ✅ |
| 27 GEOS tasks (17 dev / 10 held out); 46 candidates in the corpus | `PROVENANCE.md`, `SPRINT_LOG` | ✅ |
| Claude Code 2.1.119 | `PROVENANCE.md` #4 (903 `system/init` events, zero exceptions) | ✅ |
| Human-consult channel used in 2 of 64 trials | bottom half; paper §6.4 | ✅ |
| 8 of 16 combinations = 2× saving, not 4× | `PROVENANCE.md` #17a | ✅ (top half correctly says "double", not "quadruple") |
| LAMMPS 9 tasks, two backbones, 4.56 → 7.78 and 6.33 → 6.89 | `VERSION_DIFF_REPORT.md` L130–131 | ✅ — **judge scale is 0 to 10** (resolves the `[CONFIRM]` marker) |

---

## Disclosure gaps carried forward (unchanged, listed so the decision is explicit)

- **Acceptance parity under the shipped configuration.** Vanilla 133/170 vs S+X 132/170,
  Fisher p = 1.0000, cluster bootstrap CI [−5.3, +2.9] pp. The 90.0% figure exists *only*
  after swapping `xmllint --schema` for `geosx --validate-input` inside the adapter loop. You
  directed this be dropped at v5 and it has stayed out. It is still out in both halves. gep1
  is the thread where a reviewer could plausibly ask. (`hand_v9/CHANGES_v8_to_v9.md` INPUT-2.)
- **Cross-reference inconsistency** for the human-consult companion study: the bottom half says
  "Appendix J" (AC), "Appendix J, with results in Section 4.6" (gep1) and "Section 6.4" (nBNe).
  The top half keeps only "Section 6.4". Unverified against the submitted PDF. (INPUT-7.)
- **Claude Code install is unpinned** (`run/Dockerfile:32`, `npm install -g` with no version).
  2.1.119 is what actually ran, verified across 903 events; the pin is absent. Neither half
  mentions it. Low risk, but nBNe asked the version question specifically.
