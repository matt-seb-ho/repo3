# v11 — rebuttal consolidation pass

**Created:** 2026-07-29 02:02 PDT
**Input:** `neurips_review/responses/v10/draft.md`
**Author:** research-copilot session (analysis + cleanup); source material by M. Ho, collaborator, and advisor

---

## What v10 was

A single file containing two versions of the same rebuttal separated by a bar of `=` signs:

- **Below the bar** — the settled version by Matt + main collaborator (~6,900 words). Framing
  and most numbers agreed.
- **Above the bar** — the advisor's condensed/LLM-assisted version (~2,400 words), partly
  hand-edited, with two `[TODO]` placeholders.

## What v11 contains

| File | Purpose |
|---|---|
| `draft.md` | **Postable.** The condensed version, cleaned for OpenReview: markdown normalised, all TODOs and open questions resolved, fact-check corrections applied inline, reliability counts as proportions, no em dashes |
| `DECISIONS.md` | The five open questions and how each was resolved (2026-07-29) |
| `FACT_CHECK.md` | Task 1 — every top-half claim checked against the bottom half and the sprint artifacts |
| `FRAMING_DIFF.md` | Task 2 — what the condensed version adds, removes, and reframes |
| `RECOMMENDATIONS.md` | Task 4 — ordered change list (blocking / high-value / polish) + the markdown fixes applied |
| `SOF_METRIC_EXPLAINED.md` | Answers the standing question: how the 0.958 output-fidelity score is computed (it is **not** RMSE) |

`v10/` is untouched.

---

## Headline findings

**On the numbers.** No figure in the condensed version is numerically wrong. Three claims are
**overstated** because a qualifier was lost in compression, and two problems are **inherited
from the settled version** and need fixing either way.

**Biggest single issue.** The condensed AC says the new results "confirm SIGA's reliability
extends beyond structural correctness." They do not. The 0.958 is pooled across all cells;
cell separation on output fidelity is **not detectable on any split**, and the held-out point
estimate slightly favours Vanilla (Δ = −0.0073, p = 0.409), corroborated independently by four
sprint threads. The supportable claim — the one the settled version makes — is that the
physics gap sits in decks that *fail to run*, not in decks that run wrong. Rewritten in
`draft.md`.

**Blocking issue.** Both versions describe the external-baseline task set as "a 10-task subset
of the same pool." It is not: 5 of the 10 came from an earlier 5-task baseline set, 5 were
drawn from the 30-task pool, 1 is shared — **6 of 10 overlap**. This also means the advisor's
`SIGA: __/10` blank **cannot be filled by filtering existing data**, contrary to the v8→v9
note that assumed it could.

**The 0.958 question, answered.** It is not RMSE. It is a bounded [0,1] agreement score (SOF):
an identical output block is injected into the generated and reference decks, both are run,
and for every quantity that varies in the reference, four mesh-independent reductions (min,
max, mean, **RMS**) are compared and normalised by the reference's own scale; fidelity is
1 − that deviation, clipped and averaged. **0.958 = the mean over the 91 held-out runs that
produced output** (of 126 total). RMS is one of four summary statistics, not the metric.
Full derivation in `SOF_METRIC_EXPLAINED.md`.

**TODOs resolved from source.**
- *Why one OpenFOAM task is not evaluable:* its solver is absent from the evaluation Docker
  image, so executability cannot be assessed in any condition.
- *LAMMPS judge scale:* **0 to 10**. (This was the last remaining placeholder flagged at v9.)
- *SIGA on the matched 10:* not resolvable — see the blocking issue above.

**Framing.** The condensed version cuts ~65% of the length, and most of what it cuts is
argument rather than detail: the AC's strengths summary, the "contemporary work evaluates on
2 to 12 cases [1–5]" scale defense, the venue-fit rebuttal, and — in the kEdh thread — the
in-paper line locations that turn "you are right, we will fix it" into "the material is there,
in the wrong order, and here is the reordering." Against a clarity-based reject
recommendation, that last one matters most.

---

## Status

All five open questions resolved on 2026-07-29 (see `DECISIONS.md`). The blocking one was the
OpenFOAM baseline paragraph, which carried both a false "subset of the same pool" claim and a
literal `[insert count]/10` blank; it now describes the task sets accurately and is presented
as indicative rather than matched.

`draft.md` is postable. Remaining steps: delete the preamble, then post each
`## Response to …` section as a separate OpenReview comment.

**Length.** 3,845 words including 117 words of references, against 2,655 for the advisor's v10
condensed version and 4,575 for the settled version. The residual gap over v10 is content v10
did not have rather than verbosity: the aggregator disclosure on rho, the three-runs-per-cell
hedge, the scale defense with citations, and the LAMMPS material. Each was added for accuracy
and I would not trade any of them back for length.
