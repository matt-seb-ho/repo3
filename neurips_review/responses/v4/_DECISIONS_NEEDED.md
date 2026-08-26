# Decisions needed from you before v4 goes out

## FIRST: two number corrections I made after re-checking the sprint artifacts

I re-derived the output-fidelity numbers directly from `artifacts/K3_per_run.csv` and
`K3_correlations.csv` in the tarball, and two figures that v4r1 carried (inherited from
`sprint/EVAL_WORK_EXPLAINED.md` and the primer's "safe to cite" list) were mis-scoped. Both are
now fixed in every file, but you should know they changed.

**1. The 0.958 conditional output fidelity is a HELD-OUT number, not a 489-run number.**
v4r1 said "across 489 runs on 18 tasks, mean fidelity conditional on running is 0.958". That glues
two different scopes together. Recomputed: conditional mean over all 413 running rows of the
489-run campaign is **0.9228**. The **0.958** figure is the held-out split only (n = 91 running
rows of 126). Held-out is also the split the sprint declares clean on both axes, so it is the one
to cite. Every file now says "on the held-out split ... 0.958". The near-exact share is **46%** of
running held-out decks at fidelity >= 0.999 (73% within 1%), which does support "roughly half".

**2. The structure-versus-fidelity correlation is 0.36 on held-out, not 0.31.**
rho = 0.310 [0.227, 0.391] is the pooled val-plus-held-out figure, and val is the contested split.
Held-out alone is **rho = 0.362 [0.197, 0.505], p = 0.0001, n = 126**. Files now cite 0.36 on
held-out, which is both cleaner and slightly stronger.

**3. Convergence is 77 of 77, not 31 of 31.** `EVAL_WORK_EXPLAINED.md` reports 31/31 from the
earlier A2 pass. K3_per_run.csv, gated on `ref_clean_converged`, gives **77 of 77** on held-out
(and 271 of 271 on val, which I did not cite because val is contested). I used 77/77. If the two
studies are not the same population, tell me and I will revert to 31/31.

**4. One precision note on the physics-weighting result.** The primer's "51st percentile of the
random null" belongs to `physics_only` (restricting to physics sections), which is a genuine null.
The `physics_weighted` variant is **+0.033 [-0.003, +0.072], 93.6th percentile, one-sided
p = 0.065**, which is a marginal positive rather than a null. The drafts now state both separately
rather than calling the whole thing a null.

## Open calls

**The acceptance parity (133/170 vs 132/170).** You asked to drop it from the AC comment and report
the validator swap instead, which I did. I **kept** it on gep1's thread, because gep1 asked
"can you add an execution-based evaluation" as an explicitly score-moving question and said the
score would rise "if the reliability gains persist under execution". Reporting the swap while
silently omitting the pre-swap parity to the one reviewer who asked seems more likely to cost us
credibility than the parity number itself, especially since the AC can read that thread. Say the
word and I will pull it from gep1 too.

**H2 - how hard to commit, in writing, to the camera-ready clarity rewrite.**
Default: commit to the specific replacements shown, no more, plus the AC argument that clarity is
the one weakness certain to be fixed. Stronger commitments read closer to conceding kEdh's premise.

**H7 - whether to volunteer the Table 5 bottleneck-table error.** Currently not volunteered. The
printed held-out bottleneck table shows zero attribute-value errors for the two self-evolved cells
where the underlying classifier records four and three, so read literally it claims those cells fix
the failure mode the paper says nothing fixes. The correction runs in our favour.

**H10 - how to present the harness fairness bug (missing non-XML assets).** Currently not
presented. It is an evaluation artifact that penalises the adapter cells more than the baseline, so
disclosing runs in our favour, but it is entangled with a PROVENANCE row still marked PROVISIONAL.

**H19 - how far to walk back the reliability claim.** Default: "hard-tail reliability effect, fewer
failed decks rather than better decks", with per-cell standard deviations and failure counts, and
**no bootstrap interval printed** (your v3 direction). The AC did ask for uncertainty estimates, so
there is a case for giving the AC the task-clustered interval on the +0.069 mean lift, which is
[-0.009, +0.166]. Tell me whether to add it to `AC_post2.md`. I would not add it to reviewer threads.

**H22 - the structure-versus-fidelity correlation.** rho = 0.36 now appears in `gep1.md` and
`AC_post2.md`, and is absent from `kEdh.md` and `nBNe.md`. The persuasive number everywhere is the
conditional 0.958. One sentence to delete in each file if you want it out.

**H23 - the A2 output-fidelity CSVs.** I recomputed everything from `K3_per_run.csv` this session,
which supersedes the stale A2 pass for the fidelity numbers. The A2 QoI table (the 11-of-17 runs
at 40 to 99% error) is not cited anywhere in v4, so I believe H23 is no longer load-bearing. Please
confirm.

## Two things I should flag as judgment calls I made

**PDF line numbers.** You gave 182 (Resolution-IV) and 290 (buckleyLeverett) and I used those. My
own text extraction from `siga_neurips_init_sub.pdf` landed the Resolution-IV sentence near line
190 and the Buckley-Leverett description at line 289, which is close enough that the difference is
probably my extraction rather than yours, but please eyeball both in the PDF before posting. The
sentence at 182 does say what we claim: "instead of the full 2^4 design, we run a Resolution-IV
2^(4-1) fraction with generator D=ABC, giving eight cells whose main effects are not confounded
with two-factor interactions."

**The LLM-judge numbers.** `PROVENANCE.md` forbids quoting "the LMaaJ score table" because one
judge reverses our central contrast. I have therefore reported the judge's **validation against
physics** (physics-section score predicts real output fidelity at rho = 0.418, p = 0.0006; Solvers
subtree rho = 0.456, p = 0.0007), which is what you asked for and which is a positive result, but
I have **not** printed the per-cell judge scores (Vanilla 0.725 / S+X 0.804 / SE 0.804). The
two-of-four-judges caveat is stated in each file that reports the judge. If you want the per-cell
table in, that is your call to make, not mine.

## Already decided, baked in (no placeholder left)

- **A1 structure.** Full evaluation discussion written twice: to the AC and on gep1's thread.
  nBNe gets a short summary plus a pointer to Reviewer 1's thread. kEdh gets no eval content.
  No reviewer is ever pointed at the AC comment.
- **A2 clarity posture.** kEdh's response concedes no writing weakness, shows where each concept is
  already explained with line numbers, and pushes back on the failures-as-zero sentence.
- **A3 venue.** Rebutted affirmatively from the NeurIPS 2026 Use-Inspired definition, quoted by
  name with no link.
- **H1 OpenFOAM / LAMMPS.** Cited as qualitative transfer evidence at n=30 and single-run.
- **H3 / H9 main-effects correction.** Omitted entirely (contested val inputs, camera-ready only).

## Before you post

1. **Strip the HTML comments.** They carry the internal notes and the BLOCKED markers.
2. **Character counts.** All six files are under 10,000, but `kEdh.md` (9,798) has the least margin.
   If OpenReview counts differently, cut the aliasing sentence in kEdh's W1 first.
