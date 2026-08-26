# Sprint handoff — read this before posting anything

**Sprint:** 2026-07-26 21:57 → 23:00 UTC. **Target:** Jul 27 AOE (05:00 PT Jul 28) — roughly 37 h remaining at time of writing.
**Nothing has been posted to OpenReview.** Six text files are ready; a human posts them.

Detail: `SPRINT_LOG.md` (42 findings, 19 open decisions) · `PROVENANCE.md` (every number → source path) · `threads/` (per-thread logs, reproducible from the commands recorded there).

---

## What landed

| Thread | Status | Outcome |
|---|---|---|
| **P0** F3 resolution | ✅ done | **0.857 is correct.** Convention mismatch, not a revised score. Table 1's val column verified 11/11, means and σ. |
| **A1** rungs 1–3 | ⏳ re-deriving | Rung 2 verified (24/30 vs 30/30). **Rung 3 provisional** — root-detection bug found late (see below). |
| **A2** rungs 4–5 | ✅ done | Execution rescue **does not survive**; but found the study's best result — TreeSim never reads the files that set the physics. |
| **B** LMaaJ | ✅ done | **Null — do not ship the metric.** Produced four deterministic findings worth more than the metric. |
| **C** writeups | ✅ done | All target numbers reproduced. Two framing claims falsified. "+0.24" fixed at 6 of 7 sites. |
| **D** derived tables | ✅ done | ~120 paper numbers verified identical. 12 stale numbers found, one serious. |
| **F** clarity material | ✅ done | All kEdh material verified verbatim; plus a mechanistic answer to gep1's S/X question. |
| **E** drafting | ✅ done | Six texts, all under the 10,000-char cap. |

## The four deliverables

| File | Post as | chars | open slots | headroom |
|---|---|---:|---:|---:|
| `responses/gep1.md` | Rebuttal to gep1 | 9,400 | **0 — complete** | 600 |
| `responses/gep1_post2.md` | Official Comment (same day) | 9,698 | 2 | 302 |
| `responses/kEdh.md` | Rebuttal to kEdh | 8,528 | 1 | 1,472 |
| `responses/nBNe.md` | Rebuttal to nBNe | 5,609 | **0 — complete** | 4,391 |
| `responses/AC.md` | Official Comment to AC | 9,987 | 2 | **13 — trim before adding** |
| `responses/AC_post2.md` | Official Comment to AC | 6,507 | 3 | 3,493 |

Counts exclude HTML comments and `[[BLOCKED]]` markers; both are stripped before posting.

**All eight remaining open slots are human decisions. None is missing data.** Each names its own fallback, so every text is postable as-is if you decline all of them.

⚠ **`AC.md` has 13 characters of headroom** — anything added under H2 must be paid for by trimming. `gep1_post2.md` has 302. The other four have room.

---

## Resolved since this handoff was first written

**Rung 3 is final.** A1 re-derived it with GEOS-tolerant include recovery. **Exactly one run of 180 flipped** (Vanilla 18→19) — the bug was real but small. All three texts now carry the corrected figures, the primary denominator (n=24), and the fact that **none of the rung-3 differences is statistically significant**: per-cell Fisher p 0.27–0.79, against p = 0.024 at rung 2.

**One thing I had drafted was refuted and is now corrected.** I wrote that the `missing_external_asset` failures were "a fairness bug penalising the adapter cells." A1 checked: **all six cells reference identical assets** on the affected tasks, down to the same counts per cell and seed. Only whether the file got *staged* varies. It is measurement noise on 2 of 10 tasks, orthogonal to authoring — still worth excluding and disclosing, but for a different reason than I first wrote. Fixed in both texts.

**A clean new result worth keeping:** well-formedness and schema violations behave completely differently under execution. All 3 schema-invalid runs also fail in GEOS with the same root cause `xmllint` found. But of the 3 unparseable runs, 2 load with exit 0 and the third fails for an unrelated reason — **not one fails GEOS because of the defect our metric flagged.**

Also verified and now in gep1: **the pre-screen excluded nothing** — no deck in any cell uses the schema elements this GEOS build lacks. Pre-empts the obvious "what did you exclude?" question.

---

## What the evidence actually says — read this before deciding anything

Four independent threads converged on one conclusion, and it is not what the abstract implies:

| thread | evidence |
|---|---|
| B | On runs where every cell is schema-valid, **no metric separates the cells** (all Δ within ±0.014, all p ≥ 0.85) |
| D | Bootstrap on the mean lift: **[−0.009, +0.166]**, P(Δ≤0) = 0.052 |
| C | **`n_failed = 0`** in all 21 val build-up run-cells |
| F | **0 hook interventions in 410 val invocations** vs 32/123 on held-out |

**The entire held-out separation is a failure-rate effect, not a quality effect.** This *confirms the paper's own stated interpretation* — gep1 explicitly praised that care — but it kills any "mean quality improved" reading, including the abstract's framing.

And the execution work does not rescue the mean-lift claim:
- **No execution-level advantage at n=3** (Vanilla 2/3 vs SIGA 12/15 on the hardest task).
- **At TreeSim 0.963–0.999, 11 of 17 runs differ from the reference by 40–99%** on the primary QoI — because the decks are driven by non-XML data tables **TreeSim never reads**. One deck scoring 0.999 carried a 99% error. One L4-clean run was 99.97% wrong. One schema-valid TreeSim-0.99 deck GEOS refuses to load.
- **The flagship catastrophic failure loads fine in GEOS.** The single zero-score held-out run — sole cause of Vanilla's σ = 0.081 and the numerator of the "≈40×" claim — validates with exit 0. Its only defect is a prose `--` inside an XML comment.

All six texts are written to this reading: lead with reliability, narrow the claims, and volunteer every defect we found ourselves.

---

## Decisions only a human can make

Ranked by how much they change what gets posted. Full rationale in `SPRINT_LOG.md`.

| # | Decision | My recommendation |
|---|---|---|
| **H19** | The flagship σ=0.081 failure is a metric artifact. How far to walk back the reliability framing? | Reframe as **portability defects, not execution failures** — real, but smaller and different from what the paper implies. Drafted that way. |
| **H11** | How hard to state the rung-5 negative? | **Plainly and early.** The AC made execution the criterion; burying this is the one move that could lose the paper outright. |
| **H17** | Volunteer the clean-subset null? | **Yes.** It converts the paper's qualitative claim into a measured one. Requires dropping the abstract's "+7pp mean" framing. |
| **H3 / H9** | Volunteer the main-effects correction (R −0.037, S −0.008, X +0.011, M +0.008)? | Evidence is ready either way. If yes, §5.1's "within ±0.007" sentence is **false** under the correction and must be fixed in the same breath. |
| **H7** | Disclose the Table 5 error (prints 0 for SE/SE-prose where artifacts say 4 and 3)? | **Yes.** It is an internal contradiction visible from the table alone. |
| **H15** | Ship the LMaaJ table? | **No.** Report as built-tested-rejected. One judge reverses our central contrast. |
| **H16** | Disclose the TreeSim annihilation defect? | **Disclose, do not fix.** Re-scoring mid-response changes every number in the paper. |
| **H1** | OpenFOAM n=30 reversal? | Advisor's call. Drafted with a fallback to the submitted n=5. |
| **H2** | Camera-ready commitment strength? | Drafts assume a firm itemised commitment; soften if preferred. |
| **H4** | Is the arXiv preprint public? | **Defaulted to paraphrase.** All kEdh replacement prose is written fresh — costs nothing, removes the anonymity risk. |
| **H5** | Pre-empt the human-baseline anomaly? | Not addressed in drafts. Note: P1's file-level score *drops* 0.812→0.689 while deck-level *rises* 0.540→0.931 — explicable as restructuring into two files, so we have an answer ready if asked. |
| **H6** | Include LAMMPS? | Not in drafts. Its judge is one of the two backbones it scores. |
| **H8** | Volunteer the bootstrap CIs? | **Yes**, and lead with reliability. Refusing the AC's explicit request is worse than an honest wide interval. |
| **H10** | Disclose the harness fairness bug? | **Yes** — self-caught bugs that hurt our own numbers buy credibility cheaply. |
| **H12–H14, H18** | SE-vs-SE-prose footnote wording · correct RN-006 · the primer-confound claim · re-run Proppant rung-5 | Lower stakes; see log. |

---

## Methodological note worth keeping

**Every harness bug found this sprint biased toward our own conclusion** — three in A2, one in A1 — and in each case a *different thread's independent measurement* caught it, never the owning agent's self-checking. A2 flagged this itself, unprompted.

Two of my own framing sentences were also falsified mid-sprint (*"an unparseable file does not run in any simulator"*; *"val is at ceiling for every cell"*), both corrected in every draft.

If a larger execution campaign is funded before Aug 3, keep the redundancy. Treat any single-thread execution number as provisional until cross-checked.

## Not done / not verified

- **Cross-model panel has no scored output on disk** — traces only to a summary doc. No cross-model number may be quoted (MASTER_TODO P0 #4, still open).
- **OpenFOAM tables are the largest unverified block in the paper** (2 tables, 60+ cells).
- Also unverified: the OpenHands row, the harness-less 0.333, the autonomy study, the human baseline.
- Rungs 4–5 cover 3 tasks, not 10. Rungs 3–5 are cheap; a 10–17 task run is feasible before Aug 3 and would resolve the n=3 ambiguity.
