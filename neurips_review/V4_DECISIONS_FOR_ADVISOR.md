# V4 Rebuttal — Decisions to Resolve (advisor discussion)

Open calls the drafting session cannot make for us. Each has a recommended default so the session can
proceed even if a decision is not yet made. Items marked **✔ DECIDED (researcher)** are already resolved
(A1, A2, A3, B1, and C1) — listed here for the advisor's awareness; the still-open ones for the advisor
are **A4** and **B2–B6, C2, C3**. Grouped by type. Sources in brackets are on disk under `neurips_review/`.

Context you already know: we are in Phase 2 (Jul 27–Aug 3), 10k chars per review, no links, no paper
revision, no arXiv mention (anonymity). Held-out numbers are verified clean; validation-set numbers are
contested (the val scoring pass raced the val campaign). The server is down and API keys are invalidated,
so no new experiments — this is a writing pass.

---

## A. Posture / strategy

**A1. Response structure. ✔ DECIDED (researcher).** *(task-file item 1)*
**Reviewers cannot see our comment to the AC**, so we repeat the eval discussion in full in **both the AC
comment and Reviewer 1 (gep1)**. Reviewer 3 (nBNe) gets a **super-brief** summary and is **referred back to
our response to Reviewer 1** (reviewers can see each other's per-review threads). Reviewer 2 (kEdh) needs
no eval content.

**A2. Clarity posture toward Reviewer 2. ✔ DECIDED (researcher).** *(H2 / MASTER_TODO #24)*
**Do not concede the writing is bad; do not even call it a weakness.** For each item Reviewer 2 flagged,
**explain where the paper already explains it**, and **offer/promise to add further clarification in the
revision.** Frame as an offer to expand, not a confession of a defect. (Still open for the advisor: exactly
how strong a camera-ready commitment to make in writing.)

**A3. Venue rebuttal to Reviewer 2. ✔ DECIDED (researcher).**
**Push back firmly** — the reviewer is out of line and NeurIPS is a perfectly reasonable venue. Rebut via
NeurIPS 2026's own **Use-Inspired** contribution-type definition (quoted, not linked — links are barred),
noting all three reviewers already tagged the paper Use-inspired and the contribution was judged
significant. Confident but professional.

**A4. Anonymity — is the arXiv version publicly posted, and may we quote our own paper verbatim?**
*(MASTER_TODO #25)*
- *Why it matters:* governs whether the replacement text we paste for Reviewer 2 must be freshly written
  (to avoid matching a deanonymized arXiv posting) or can reuse existing prose. **Default is paraphrase /
  write fresh.** Need a yes/no on whether arXiv is live.

---

## B. Self-corrections — what do we volunteer vs stay silent on?

The paper has a few internal errors we found ourselves. Volunteering builds credibility but adds attack
surface; each is a judgment call.

**B1. Main-effects correction — ✔ DECIDED (researcher): DO NOT volunteer.** *(H3/H9 / MASTER_TODO #26)*
Not useful for the rebuttal; save any correction for camera-ready. (It was also unsafe to volunteer: the
val scoring pass raced the val campaign, so both the published AND the "corrected" effects rest on bad
inputs. Held-out is clean, so no headline claim depends on this.) [source: `sprint/PROVENANCE.md` F52]

**B2. Reliability claim — how far do we walk it back?** *(H19)*
Scored at 17 seeds the headline effect is ~2.3× smaller than the paper's 3-seed number (the paper's seeds
were the two lowest draws of 17). The honest story is "fewer catastrophic failures, not better decks."
- **Recommend:** adopt the narrower framing proactively — it is much harder to attack and the AC is
  borderline. State the corrected schema numbers (155/170 vs 170/170, gap 8.8) rather than the "24/30."
- *Decision needed:* agree to lead with the smaller, firmer claim.

**B3. Do we volunteer the structure-vs-fidelity correlation ρ ≈ 0.31?** *(H22)*
It is honest and shows the metric only moderately predicts physics.
- **Recommend:** yes — it supports "future work needs a real plausibility benchmark" and pre-empts the
  objection. It does not concede an inter-condition advantage.

**B4. Table 5 bottleneck-table error — volunteer?** *(H7)*
The printed held-out table shows 0 attribute-value errors for the two self-evolved cells, where the
underlying classifier recorded 4 and 3. Read literally, the table claims those cells eliminate a failure
mode the paper elsewhere says is untouched. The artifacts support the paper's thesis; the printed cell
contradicts it.
- **Recommend:** volunteer briefly (the table cell is the error, not the thesis) — low cost, and it is the
  kind of thing a careful reviewer could catch.

**B5. Harness fairness bug (missing non-XML assets) — how to present?** *(H10)*
The largest single loading-failure category is our harvester failing to stage property/mesh files, not an
authoring error. All cells reference identical assets, so it is measurement noise on ~2 of 10 tasks.
- **Recommend:** disclose and exclude those tasks identically across cells; report both denominators.

**B6. Pre-empt the human-baseline anomaly?** *(MASTER_TODO #27)*
One expert's score drops 0.812 → 0.689 between sessions.
- **Recommend:** since we are relabeling the human comparison "preliminary calibration" and dropping
  comparative claims anyway, do **not** proactively raise this; answer only if asked.

---

## C. Numbers we currently cannot verify

**C1. OpenFOAM / LAMMPS transfer numbers — RESOLVED (they are in the paper).** *(was H1)*
These numbers are the paper's own transfer study and appear in `writing/arxiv/siga_arxiv_2.tex`: OpenFOAM
SIGA 0.870 (all SIGA cells 30/30 full coverage), Foam-Agent 0.516 (19/30), MetaOpenFOAM 0.379 (10/30),
n=30, S effect +0.168; LAMMPS 4.56→7.78 and 6.33→6.89. The arxiv already adopts the n=30 OpenFOAM numbers,
so the earlier "n=5 → n=30 sign reversal" is settled, not an open reversal. **We may cite them as new
post-submission transfer evidence; we may NOT reference the arxiv version itself (anonymity).**
- **Recommend:** cite as **qualitative** transfer evidence (single-run, transfer not a second benchmark).
  No need to extract the 7 GB sprint tarball for this. Only decision left: are we comfortable presenting
  the n=30 OpenFOAM result as-is (recommend yes — it matches the paper).

**C2. A2 output-fidelity CSVs need a correction pass.** *(H23)*
ρ=0.31 and the 0.958-conditional figure are independently cross-derived and safe to cite, but the stored
A2 CSVs are stale and should be regenerated before these are "final." Data task, not a writing call.
- *Decision needed:* who owns regenerating them, and whether it must happen before we cite (recommend: cite
  now, regenerate for camera-ready).

**C3. Keep all new comparisons within-campaign / same-day** because of an 86-day model-drift confound.
*(H33)* Not a decision so much as a constraint to confirm we accept: no cross-campaign absolute-number
comparisons.

---

## D. Quick reference — recommended defaults if undecided at draft time

| # | Decision | Recommended default |
|---|---|---|
| A1 ✔ | Response structure | Full eval in AC AND gep1 (AC comment not reviewer-visible); nBNe brief + refer to gep1 |
| A2 ✔ | Clarity posture | Don't concede/call it a weakness; show where we explain; offer more clarification |
| A3 ✔ | Venue rebuttal | Push back firmly via Use-Inspired definition (quoted, not linked) |
| A4 | arXiv live? / quoting | Paraphrase / write fresh until confirmed otherwise |
| B1 ✔ | Main-effects correction | **Omit** (camera-ready only; contested inputs) |
| B2 | Reliability claim | Walk back to "fewer failures, not better decks" |
| B3 | Volunteer ρ≈0.31 | Yes |
| B4 | Table 5 error | Volunteer briefly |
| B5 | Harness fairness bug | Disclose, exclude affected tasks symmetrically |
| B6 | Human-baseline anomaly | Do not pre-empt; answer only if asked |
| C1 | OpenFOAM/LAMMPS numbers | Resolved — cite paper's numbers, qualitative (don't name arxiv) |
| C2 | A2 CSVs | Cite now, regenerate for camera-ready |
| C3 | Cross-campaign numbers | Never compare across campaigns |

The drafting session is instructed to leave `[[BLOCKED: H#]]` placeholders wherever these are unresolved,
so it can produce a complete draft on defaults and you can slot in decisions afterward.
