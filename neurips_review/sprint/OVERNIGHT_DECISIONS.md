# Overnight round 2 — autonomous decisions

**Authorisation.** Researcher, 2026-07-27 ~09:50Z: *"I'm going to sleep — please run whatever takes a long time overnight. Make reasonable decisions. Write them down. Do whatever to make our rebuttal stronger with new metrics/experiments/ablations. There's ~24h left."*

**Deadline.** Jul 27 AOE = **05:00 PT Jul 28 = 12:00Z Jul 28**. ~26 h from dispatch.

**Standing constraints kept:** nothing posted to OpenReview · `writing/`, `/data/shared/`, `/data/jixuan/` read-only · no `_`-prefixed writes · no git commits · every number traces to a file · negatives reported loudly.

---

## What I chose to run, and why

Selection rule: maximise (value to the AC's primary objection × feasibility) ÷ risk. The AC made **execution validity** the decision criterion, so anything that strengthens the execution evidence or removes a confound from it outranks everything else.

### Tier 1 — no API cost, removes confounds from evidence we already have

| # | Thread | What | Why it matters |
|---|---|---|---|
| D1 | **K1** | Fix the external-asset **staging** bug, then re-run rungs 1–3 on all 180 held-out decks | **6 of the 10 rung-3 failures are our own harness artifact.** Fixing staging converts a confounded measurement into a clean one. Currently the headline is 19/30 vs 23/30 with a ceiling of 24/30 — after staging, the ceiling should rise and the comparison becomes interpretable. Pure GEOS compute. |
| D2 | **K2** | Implement the 3-line `_bipartite_match` fix and **re-score everything** (val + held-out), reporting old vs new side by side | J1 showed this deterministic fix beats the $12.70 four-judge LLM panel at predicting whether a deck loads (rung-3 AUC 0.803 → 0.830). We need to know **whether the cell contrast survives re-scoring** before deciding H28. Free, deterministic, and it produces the camera-ready numbers either way. |
| D3 | **K3** | Scale J2's SOF output metric toward **n ≈ 206+**, adding held-out tasks and opening the **val split** | J2's own power analysis: n = 108 gives min detectable ρ ≈ 0.27; resolving ρ = 0.2 and the task heterogeneity (I² = 42%, per-task ρ 0.11–0.83) needs ~12 tasks. This is **the AC's question**, and more power is the single best thing we can do to it. Val is a bonus: TreeSim is at ceiling there, so if SOF still varies, that is a sharp result. |

### Tier 2 — trivial API cost, tests the improvement we intend to propose

| # | Thread | What | Why it matters |
|---|---|---|---|
| D4 | **K4** | (a) J3's **corrected root-rule** re-run (H21, ~$0.52); (b) extend the validator swap to **F8 = S+X+M** (~$0.58); (c) **new ablation — a simulator-grounded stop hook as a standalone intervention** | (a) separates "the bad root rule caused the fabrication" from "in-loop validation induces fabrication generally"; (b) stops the validator result resting on a single cell; (c) is the most novel experiment available — it tests the improvement we are proposing to reviewers *as an intervention*, rather than only measuring the old validator's blindness. |

**Total API budget I authorised: ≤ $10** across all threads (J1+J2+J3 spent ≈$13.9 combined; each of these arms is well under $1). Anything above $10 stops and reports. This is trivial spend and inside the researcher's "make reasonable decisions" grant.

### What I deliberately did NOT do

- **No re-running of published paper numbers as replacements.** K2 computes the re-scored values and reports both; it does not overwrite anything. Re-scoring mid-response would change every number while reviewers are reading.
- **No new LLM-judge design.** Two independent designs have now failed pre-registered reliability tests (Threads B and J1). A third would be motivated reasoning, and J1 showed the deterministic fix outperforms the panel anyway.
- **No value-level plausibility benchmark.** The researcher ruled it out of scope: it needs domain-expert coordination and a longer window.
- **No posting, and no edits to the four response texts.** Response revision is a separate session working from `REBUTTAL_REVISION_BRIEF.md`. If these threads produce something that changes a draft, I record it in the brief rather than editing prose.
- **No cross-model campaigns.** MASTER_TODO P0 #4 is still open (cross-model panel has no scored output on disk); adding cross-model work would compound an unverified block rather than strengthen a verified one.

### Coordination and risk controls I imposed

- **CPU/docker contention:** only K4 launches agent campaigns; K1/K2/K3 are GEOS-compute and scoring only. All threads capped at ≤8 workers and told to check for a running campaign before launching.
- **Every thread must cross-check against an existing artifact before trusting its own harness.** Five harness bugs this sprint, every one biasing toward our own conclusion, every one caught by a *different* thread's measurement. K1 checks against A1's CSV; K2 must reproduce current TreeSim bit-exact with the fix disabled; K3 must reproduce J2's ρ = 0.402 before extending.
- **Pre-registration where a result could be framed after the fact** — K3 must fix its power target and analysis plan before extending, as J2 and J3 both did.

---

## Running decision log

| Time (Z) | Decision | Rationale |
|---|---|---|
| 09:50 | Let J3 finish its current analysis rather than restarting it | Its runs are complete and scoring is in flight; interrupting would lose the pre-registered analysis. |
| 09:52 | Dispatched K1–K4 as above | Highest value per hour against the AC's primary objection. |
| 09:52 | Capped total new API spend at $10, each thread reporting its estimate before launching | Well inside "reasonable"; keeps a hard stop without needing the researcher awake. |
| 09:52 | Chose F8 (S+X+M) as the second validator-swap cell | Highest rung-3 headroom of the S-enabled cells (21/30 control) and it is the predicted main-effects-best corner, so it is the most informative second arm. |
| 09:52 | Chose to open the **val** split for SOF rather than only adding held-out tasks | Val is 17 tasks × 11 cells × 3 seeds. TreeSim is at ceiling there, so SOF variation on val is a sharp, near-free test of whether structural agreement implies simulation agreement. |
