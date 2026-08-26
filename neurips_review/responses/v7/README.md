# v7 responses (2026-07-28)

Built on `hand_v6/siga_neurips26_rebuttal.md`, the researcher's hand-written AC response after the
advisor meeting. That file is the style and messaging authority; v7 follows its wording, structure
and level of concision, and extends the same messaging to the three reviewer threads.

## Files and posting plan

| File | OpenReview post | Prose chars (cap 10,000) |
|---|---|---|
| `AC.md` | Official Comment to AC GKRj. | 6,749 |
| `gep1.md` | Rebuttal on Reviewer 1's (gep1) thread. Every point in one post. | 9,686 |
| `kEdh.md` | Rebuttal on Reviewer 2's (kEdh) thread. | 9,455 |
| `nBNe.md` | Rebuttal on Reviewer 3's (nBNe) thread. | 6,750 |

Four posts, down from six in v5. Post `AC.md` first, then `gep1.md`, then `nBNe.md` (it points at
gep1's thread, so gep1's must exist first), then `kEdh.md`.

Counts exclude HTML comments, which are internal notes and must be stripped before posting.
Strip with: `python3 -c "import re,sys;print(re.sub(r'<!--.*?-->','',open(sys.argv[1]).read(),flags=re.S).strip())" <file>`

## AC.md: what changed from the hand version

Three edits only. Everything else is the hand text verbatim.

1. **Simulation Execution now carries the deck run rate**, as requested. It reports that decks
   accepted rises from **78.2%** (Vanilla) to **90.0%** once the simulator's own input check
   replaces the schema linter inside the adapter loop, alongside the existing 100% convergence
   figure (77 of 77). One closing line offers the full protocol during discussion and defers the
   details to the camera-ready, so the AC is not overburdened.
2. **The Simulation Output metric line is completed.** It ends mid-clause in the hand version
   ("injecting the ground truth output block into both decks and"). It now finishes: run both, then
   compare mesh-independent reductions of each physical quantity normalized by the reference's own
   scale. The 46% near-exact figure is added alongside the 0.958.
3. **The efficiency bullet's placeholder is replaced with real numbers**, see the note below.

## Reviewer threads: what was pulled into line

**Evaluation** is now the same three-instrument "New Metrics" structure everywhere, with the same
numbers: Simulation Execution, Simulation Output, Input Deck Evaluation for Physics Plausibility.
gep1 gets the extra depth it earned (artifact-validity counts at 17 runs per cell, the rho = 0.36
structure-versus-fidelity interval, the `Solvers` subtree, the physics-weighting test); nBNe gets
three bullets and a pointer to gep1's thread; kEdh gets none, as before.

**Scale** now uses the hand version's argument on every thread: the cost basis (30-minute
trajectories, many conditions, multiple runs per condition for error bars, so budget went to
conditions rather than examples), then the five contemporary works at comparable or smaller scale,
then 27 evaluated tasks and the expansion work underway. Citations are given in full on the AC
thread and in compact form on the reviewer threads, purely to buy character margin.

**Human baseline** uses the hand version's framing everywhere: better described as preliminary
calibration, still useful because it establishes a human pace on a relatively easy 1D problem, and
hard to scale because PhD-level geophysics knowledge workers are difficult to recruit for long
tasks.

**kEdh's clarification items** are no longer itemised in the AC comment. The AC comment says only
that we discuss them in detail on that thread and are happy to add clarifications. `kEdh.md`
therefore keeps its full depth, since the replacement text has to live somewhere, but its rating
and venue paragraphs now use the hand version's phrasing, including "we find some decoupling
between the feedback given and the score assigned".

**Structural consolidation.** v5's `gep1_post2.md` and `AC_post2.md` are gone. The concision pass
freed enough room that gep1 fits in a single post, and the AC comment no longer needs an addendum.

## One thing you should check

**The efficiency numbers.** The hand version's "15-20%" was a placeholder. v7 uses the real figures
from the appendix efficiency table, both on the harder held-out split: **up to 22% fewer tool calls**
(SE-prose, -21.7%) and **18% less wall clock** (X+M, -18.5%). Taking both from the same split avoids
cross-split cherry-picking. The "(best adapter cells)" qualifier is load-bearing, because SE, the
headline cell for the +0.069 gain, is **+7.6%** on tool calls for held-out; an unqualified claim is
checkable against the table and wrong.

See `_DECISIONS_NEEDED.md` for the remaining open calls.
