# v4 responses (drafted 2026-07-28)

Drafted from `V4_DRAFTING_PRIMER.md`, `V4_OUTLINES.md`, `ac_response_outline.md` and
`siga_write_v4_response.md`, in the `ladir_rebuttal_iclr.md` style. No new experiments were run
or needed; this is a drafting and framing pass over already-VERIFIED numbers.

## Files and posting plan

| File | OpenReview post | Prose chars (cap 10,000) |
|---|---|---|
| `AC.md` | Official Comment to AC GKRj. Contribution recap + meta-review bullets 1 and 2. | 8,069 |
| `AC_post2.md` | Companion Official Comment to the AC. Evaluation detail + bullets 3 and 4 + the kEdh point. | 7,177 |
| `gep1.md` | Rebuttal on Reviewer 1's (gep1) thread. Carries W1/Q1, the evaluation question. | 8,539 |
| `gep1_post2.md` | Companion on gep1's thread. Q2a, Q2b, W2, Q3, Q4, limitations wording. | 8,424 |
| `kEdh.md` | Rebuttal on Reviewer 2's (kEdh) thread. | 9,798 |
| `nBNe.md` | Rebuttal on Reviewer 3's (nBNe) thread. | 8,015 |

Post `AC.md` + `AC_post2.md` first, then `gep1.md` + `gep1_post2.md`, then `nBNe.md` (it points at
gep1's thread, so gep1's must exist first), then `kEdh.md`.

## v4r2 revision (2026-07-28, per researcher comments on AC.md)

- Thank-you and contribution recap split under their own headings, ahead of a
  "Responses to the concerns raised" heading. Recap expanded to state the actual contribution
  (bottleneck, adapter-not-bespoke-agent claim, four grounding components, self-evolution,
  reliability result, human calibration, transfer), not only the strengths reviewers listed.
- TreeSim defense rewritten to the researcher's logic: the current scope assumes a solid user
  specification, so the task is translation, and the well-specified brief plus the hand-validated
  gold configuration *is* the physical-meaning check at that scope. Scope expansion is then framed
  as the motivation, pointing at Appendix J / Section 4.6, which is early exploration already in
  the submitted paper.
- Extended evaluation presented as an explicit five-level protocol plus a semantic axis, in a table.
- The 133/170 vs 132/170 acceptance parity is **removed from the AC comment**; level 3 is now
  reported as the validator swap in percentage terms (76.7 to 90.0 for S+X, 80.0 to 83.3 for
  S+X+M) with a one-paragraph note on why. It is **retained on gep1's thread**, where the reviewer
  asked the question directly. See `_DECISIONS_NEEDED.md`.
- Convergence and both plausibility-oriented metrics now reported with numbers: level 4 (77 of 77),
  level 5 output fidelity (0.958 conditional on running, 46% near-exact, rho = 0.36), and the LLM
  judge (physics-section score predicts real output fidelity at rho = 0.418, p = 0.0006; Solvers
  subtree rho = 0.456).
- Clarity answers now cite submitted-PDF line numbers (182 for Resolution-IV, 290 for
  buckleyLeverettProblem) and push back on the failures-as-zero sentence rather than accepting it
  is hard to parse.
- Human comparison reframed around why it cannot scale: PhD-level geophysics expertise, about
  three hours on an easier and smaller task.

Counts exclude HTML comments, which are internal notes and must be stripped before posting.
Strip them with: `python3 -c "import re,sys;print(re.sub(r'<!--.*?-->','',open(sys.argv[1]).read(),flags=re.S).strip())" <file>`

## What changed from v3

- **AC response now exists** and is built on the advisor's outline rather than an internal TODO.
  It answers the four meta-review bullets in the AC's own order, then the kEdh venue/criteria point.
- **Stale numbers propagated everywhere** (the mandatory mechanical task from primer §9). The v3
  reviewer files still carried pre-overnight numbers; all are replaced:
  - "24/30 vs 30/30" (3 seeds) becomes **155/170 vs 170/170 vs 100/100** at 17 runs per cell,
    gap 8.8 pts, CI [+2.9, +16.5], p = 0.0006.
  - "GEOS accepts 19/30 vs 23/30" becomes **133/170 vs 132/170**, reported plainly as a measured
    negative. No execution-level advantage is claimed anywhere in the set.
  - All "experiments are running now" language is deleted. The validator swap is reported as run:
    S+X 23 to **27/30**, S+X+M 24 to **25/30**.
- **kEdh posture reversed.** v3 opened "We accept this criticism." v4 does not concede a writing
  weakness at all: it shows where each flagged concept is already explained (Section 3.2, Section 4,
  Section 3, and the 0.999 operationalisation), offers the replacement text as an addition, reframes
  against the NeurIPS rating-2 rubric, and argues the venue affirmatively from the Use-Inspired
  contribution-type definition (quoted by name, not linked).
- **Two-axis framing** (deck-as-artifact / what-the-simulator-does) replaces "ladder and rungs".
- **Metric nulls reported as tests**, not failures: physics-weighted TreeSim is a tight null against
  a random-subset control, and the semantic judge ties plain TreeSim, so uniform weighting now rests
  on a test rather than an assumption.
- **Main-effects correction omitted** (decision H3: contested val inputs, camera-ready only).
- **OpenFOAM n=30 and LAMMPS cited** as qualitative transfer evidence (decision H1).
- **"Vanilla + geosx hook" excluded** from every table.

## Constraints checked mechanically

No em dashes in posted prose (the four that remain are inside HTML comments). No URLs. No mention of
the arXiv version. Every number traces to a VERIFIED row in `sprint/PROVENANCE.md` or to
`sprint/EVAL_WORK_EXPLAINED.md`. No forbidden number appears (`+0.24`, the main-effects correction,
cross-model panel figures, absolute May-campaign numbers, any claimed execution-level advantage).

Open researcher decisions are marked inline as `[[BLOCKED: H#]]` inside HTML comments. See
`_DECISIONS_NEEDED.md`.
