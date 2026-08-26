# Decisions needed from you before v5 goes out

## The acceptance parity, now removed everywhere

You asked to drop the "defect in our own tooling" framing from the AC comment. It is now gone from
all four posts, including `gep1.md`, which in the previous draft kept one sentence of it. Every post
now presents level 3 as Vanilla 78.2% against 90.0% for S+X with the simulator's own validator in
the loop, without stating that the originally shipped configuration showed no separation on
acceptance.

Flagging it once more only because gep1 tied a score increase to whether the gains persist under
execution, and is the one reviewer who might reasonably expect the disclosure. If you want it back, the sentence is:

> With the schema linter we originally shipped, the adapter cells did not separate from Vanilla on
> acceptance, which is what prompted us to put the simulator's own input check in the loop instead.

It would go immediately before the sentence about acceptance moving from 23 to 27 of 30. Your call,
and I will not raise it again.

## One new thing to confirm

**We now offer a dedicated S-by-X interaction experiment "for the camera-ready" rather than during
the response period.** That is deliberate: the keys are invalidated and nothing can run before
Aug 3, and a promise we miss would land right before Phase 3. If you would rather not commit even
to the camera-ready version, the sentence to cut is the last one of the Q2b answer in `gep1.md`.

## Two presentation choices worth a look

**Level 3 mixes run counts.** Vanilla's 78.2% is 133 of 170 (17 runs per cell). The adapter figures
are 27 of 30 and 25 of 30 (3 runs per cell), because the validator swap was run at 3 seeds. Both
are held-out and the same tasks, so the comparison is fair, but the precision differs and the table
says so inline. If you would rather not mix them, the alternative is to give all three at 30 runs
per cell, which puts Vanilla at 78.2% against 90.0% and 83.3% on a matched basis only if we re-run
Vanilla, which we cannot do now.

**The LLM-judge numbers.** `PROVENANCE.md` forbids quoting the per-cell judge score table because
one judge reverses our central contrast, so v5 reports the judge's validation against physics
(physics-section score predicts measured output fidelity at rho = 0.418, p = 0.0006; `Solvers`
subtree rho = 0.456, p = 0.0007) and states the two-of-four-judges caveat, but does not print
Vanilla 0.725 / S+X 0.804 / SE 0.804. Your call if you want the per-cell table in.

## Still open from v4

**H2 - the camera-ready clarity commitment.** The "clarity is the only item certain to be fixed"
argument is removed from `AC.md` per your note. That was the strongest borderline-decision argument
in the set, so if you want it back as a closing line in section 2, say so. Otherwise v5 commits
only to the specific replacements shown in `kEdh.md`.

**H7 - the Table 5 bottleneck-table error.** Not volunteered. The printed held-out bottleneck table
shows zero attribute-value errors for the two self-evolved cells where the underlying classifier
records four and three, so read literally it claims those cells fix the failure mode the paper says
nothing fixes. The correction runs in our favour.

**H10 - the harness fairness bug (missing non-XML assets).** Not presented. It is an evaluation
artifact that penalises the adapter cells more than the baseline, so disclosing runs in our favour,
but it is entangled with a PROVENANCE row still marked PROVISIONAL.

**H19 - how far to walk back the reliability claim.** No bootstrap interval is printed anywhere.
The AC did ask for uncertainty estimates, so there is a case for giving the AC the task-clustered
interval on the +0.069 mean lift, which is [-0.009, +0.166]. I would not add it to reviewer threads.

**H22 - the structure-versus-fidelity correlation.** rho = 0.36 now appears only in `AC_post2.md`,
the evaluation addendum. It is absent from every reviewer post and from `AC.md`. One sentence to
delete if you want it out entirely.

## Carried over from the v4 verification pass (already applied everywhere)

- 0.958 output fidelity is a **held-out** figure (n = 91 running rows), not a 489-run figure. The
  pooled conditional mean over all 413 running rows is 0.923.
- The structure-versus-fidelity correlation is **0.36 on held-out**, not the pooled 0.31.
- Convergence is **77 of 77** (from `K3_per_run.csv` gated on `ref_clean_converged`), not the
  31 of 31 reported in `EVAL_WORK_EXPLAINED.md` from the earlier A2 pass.
- The "51st percentile of the random null" belongs to `physics_only`. The `physics_weighted`
  variant is +0.033 [-0.003, +0.072], a marginal positive rather than a null.

## Before you post

1. **Strip the HTML comments.** They carry the internal notes and the BLOCKED markers.
2. **Eyeball PDF lines 182 and 290.** My own extraction landed the Resolution-IV sentence near 190
   and the Buckley-Leverett description at 289, close enough that it is probably my parser, but the
   line numbers are quoted to a reviewer so they should be right.
3. **Character counts.** `kEdh.md` (9,798) and `AC.md` (9,360) have the least margin; everything
   else sits between 5,700 and 7,500. If OpenReview counts differently, cut the aliasing sentence
   in kEdh's W1 first, and in `AC.md` the level-5 construction text in the table.
