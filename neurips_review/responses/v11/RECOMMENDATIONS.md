# Final change recommendations

Ordered: blocking first, then high-value, then polish. "Applied" = already done in
`v11/draft.md`. "Decide" = needs your call.

---

## Blocking — do not post until resolved

**R1. Fix the "10-task subset of the same pool" claim.** *(Decide — 5 min)*
It is not a subset: 6 of the 10 baseline tasks are in the 30-task ablation pool, 4 are not.
Both v10 halves state it wrongly. `FACT_CHECK.md` F8.

**R2. The `SIGA: __/10` blank cannot be filled by filtering.** *(Decide)*
Consequence of R1 — SIGA has per-task data for at most 6 of those 10. Pick one:
- **(a)** Run SIGA on the 4 missing tasks (`boundaryWallFunctionsProfile`, `Grossetete`,
  `helmholtzResonance`, `damBreakWithObstacle`) → a genuinely matched 10-task comparison.
  Highest value, only viable if there is time.
- **(b)** Report the matched **6**: *"On the six tasks shared with the ablation pool, SIGA
  produces X of 6 executable cases against Foam-Agent's Y and MetaOpenFOAM's Z."* Cheap
  (a filter over existing data), honest, and still matched.
- **(c) (recommended if time is short)** Drop the matched line and keep the current framing
  with both task counts stated: SIGA on 30 tasks, baselines on a 10-task set drawn from the
  same benchmark family. This is what v9 shipped and it is defensible.

**R3. Resolve the 77/77 population question, or stop using 77.** *(Decide)*
"27 of 30 accepted … 77 of 77 completed" invites "which 77?" The question was raised at v8→v9
and never answered (`CHANGES_v8_to_v9.md` INPUT-3: *if they are different populations, 77/77
should revert to 31/31*). `v11/draft.md` currently hedges to "every accepted deck we tested for
execution completed successfully", which is true under either reading — **either confirm the
number and put it back, or leave the hedge.** `FACT_CHECK.md` F2.

**R4. Delete every `[OPEN]` block and the preamble from `draft.md` before posting.**

---

## High value

**R5. Restore the "in line with contemporary work … 2 to 12 cases [1–5]" defense.** *(Applied)*
It was the strongest single answer to the scale objection and the condensed AC dropped it.
Now in the AC, gep1 W2, and nBNe W4. References appended.

**R6. Do not claim the fidelity result shows SIGA improves physics.** *(Applied)*
0.958 is pooled across cells; cell separation on that axis is not detectable and the point
estimate slightly favours Vanilla. Rewritten to the reliability framing.
`FACT_CHECK.md` F1, `SOF_METRIC_EXPLAINED.md`.

**R7. Restore the three-runs-per-cell hedge on the S-vs-X build-up.** *(Applied)*
The verified paired build-up puts S at +0.008, CI [−0.007, +0.023] — not significant.
Asserting the ordering unhedged is what gep1 is probing. `FACT_CHECK.md` F3.

**R8. Restore "structural similarity above 0.999" in the "strictly perfect" replacement.**
*(Applied)* Without the number the replacement does not answer kEdh's actual complaint.
`FACT_CHECK.md` F5.

**R9. Volunteer the ρ aggregator sensitivity in one clause.** *(Applied)*
Under a worst-reduction aggregator held-out ρ falls to 0.121, not significant. The sprint's own
standing rule is to report both. ~15 words removes the discovery risk. `FACT_CHECK.md` F9.

**R10. Restore the verbatim brief and repair-feedback excerpts.** *(Applied)*
kEdh asked to see the artifacts. The condensed version paraphrased them into blockquotes; the
originals are byte-verified (`PROVENANCE.md` #15, #16). The real ones are strictly stronger.

**R11. Fix the "17 runs per task" arithmetic tell.** *(Applied)*
100 ≠ 17 × 10. Now stated as raw counts plus percentages. `FACT_CHECK.md` F4.

**R12. Restore the AC strengths / contribution summary.** *(Decide)*
The condensed AC reads as a status report rather than a case. The strengths paragraph — seven
verbatim reviewer quotes, ending with "all three rated significance and originality good or
better, including the reviewer recommending rejection" — is the cheapest way to get the case
back. `FRAMING_DIFF.md` §1. **Recommend restoring the strengths summary, skipping the
contribution summary** (its "22% / 18%" efficiency bullet has no reviewer backing and invites
a follow-up about which cell each figure comes from).

**R13. Decide where venue fit lives.** *(Decide)*
Bottom half rebuts it at AC level with the pointed observation that the review recommends
rejection without naming a technical, evaluation, reproducibility, or ethical concern. The
condensed version softens it and buries it in kEdh. **Recommend: keep the substantive
Use-Inspired argument in the kEdh thread (where the objection was raised) and add one sentence
to the AC noting it is addressed there.**

**R14. Restore the in-paper locations in kEdh.** *(Decide — recommend yes)*
"Explained on line 182", "defined in Section 3", "Line 290 gives the attributes that matter".
Turns a concession into a demonstration that the material exists and is merely mis-ordered.
Against a clarity-based reject this is the difference-maker. `FRAMING_DIFF.md` §2.

---

## Resolved from source (no further action)

**R15. LAMMPS judge scale = 0 to 10.** *(Applied)* Resolves the `[CONFIRM]` marker that
`CHANGES_v8_to_v9.md` INPUT-5 called "the only placeholder left in the file". Source:
`VERSION_DIFF_REPORT.md` L130–131; `responses/old_v2/gep1.md` L30.

**R16. Why one OpenFOAM task is not evaluable.** *(Applied)* Its solver is not present in the
evaluation Docker image, so executability cannot be assessed in any condition; the exclusion is
applied identically across cells. Source:
`hand_v9/2026-07-28_siga-3seed-real-validator-results.md`.
*Minor caveat worth knowing:* the source note says the exclusion applies "except vanilla/r+x
where none were excluded", hence 4/30 rather than 4/29 for Vanilla. If a reviewer notices the
mismatched denominators, the answer is that those two cells produced no artifact for the task
in question, so there was nothing to exclude.

**R17. Output-fidelity metric provenance.** *(Documented)* Not RMSE — see
`SOF_METRIC_EXPLAINED.md`. 0.958 = mean SOF conditional on running, n = 91 of 126 held-out
runs. A one-line protocol gloss is provided there if you want it in the rebuttal text.

---

## Consistency and polish

**R18. Use "46 candidate examples" in every scale answer.** *(Applied)* The condensed version
had it in nBNe but not gep1.

**R19. Decide on the LLM judge in gep1.** *(Decide)* Currently in the AC and nBNe but not in
gep1 — backwards, since gep1 asked the evaluation question. Restore text is in the
`[OPEN — gep1 W1/Q1]` block. **Recommend restoring**, including the honest verdict that it does
not beat structural scoring — gep1 explicitly credited the paper's negative findings.

**R20. Verify the companion-study cross-reference.** *(Decide)* v10 cites it three ways:
"Appendix J", "Appendix J with results in Section 4.6", and "Section 6.4". v11 uses
"Section 6.4" only. Check against the submitted PDF. (`CHANGES_v8_to_v9.md` INPUT-7.)

**R21. Acceptance-parity disclosure.** *(Decide, unchanged)* Still omitted per your v5
direction. Flagged only so the omission stays deliberate. `FACT_CHECK.md`, disclosure gaps.

---

## Markdown fixes applied for OpenReview

| Issue in v10 top half | Fix |
|---|---|
| Backslash escapes from the Google Docs export: `\+2.9`, `\=`, `\[`, `\]`, `failed\_no\_outputs`, `\\pm`, `\\rho`, `\\times`, `\\mathrm` | Removed; LaTeX fragments rewritten as plain text (`0.768 ± 0.005`, `9.0e-13 m2`, `Spearman rho`) |
| Inconsistent reviewer headings — `## **Response to the AC**`, plain-text `Response to Reviewer gep1`, bold-only `**Response to Reviewer kEdh**`, `## **Response to Reviewer nBNe**` | All four normalised to `## Response to …` |
| Bold inside headings (`### **W1./Q1. …**`) | Removed — redundant, and some renderers show the asterisks |
| `W1./Q1.` punctuation | `W1 / Q1` |
| Stray empty blockquote marker (v10 L114) | Removed |
| Revised text presented after "Revised:" but not inside a blockquote (v10 L112) | Put inside the blockquote to match the pattern |
| Trailing double-spaces (Google Docs hard line breaks) in bullet lists | Removed |
| `\=========================================` separator | Replaced with `---` |
| Markdown table missing an alignment row | Added |
| `(\rho=0.362)` inside prose | `Spearman rho = 0.362` |
| Grammar: "to ensure this reliability faults are accounted for" | Rewritten |
| No references section in the condensed version despite `[1–5]`-style claims | References [1]–[7] appended |

**Note on OpenReview:** it renders a Markdown subset and supports `$…$` MathJax, but plain
text is safer for symbols like `±` and `ρ`. `v11/draft.md` uses `±` (renders reliably) and
spells out `rho` in prose. Post each `## Response to …` section as its own comment.
