# v11 decisions — 2026-07-29

Resolutions for the five open questions raised against the condensed draft, plus two
follow-on calls. All are applied in `draft.md`; no placeholders remain.

| # | Question | Decision | Applied as |
|---|---|---|---|
| 1 | Restore the AC strengths / contribution summaries? | **No.** Keep the existing one-sentence strengths paragraph. | Added six words: "including the reviewer recommending rejection". Contribution summary stays out (its 22% / 18% efficiency figures come from two different adapter cells and have no reviewer backing). |
| 2 | Where does venue fit live, and how sharp? | **Pointed sentence to the AC; substantive argument stays in kEdh.** | New "Venue fit" paragraph in the AC noting the rejecting review raises presentation issues only, and that replacement text is supplied for each. kEdh keeps the Use-Inspired argument. |
| 3 | OpenFOAM baseline comparison (blocking) | **Option (c).** Drop the matched-subset line; correct the task-set description; state both scales. | "a 10-task subset of the same pool" replaced with "a 10-task set drawn from the same benchmark family", presented as indicative rather than matched. The `[insert count]/10` blank is gone. |
| 4 | Add the LLM judge to gep1? | **Yes**, compressed. | Two-sentence "Physics plausibility" paragraph in gep1 W1/Q1, keeping the negative verdict, dropping the four-judge methodology detail. |
| 5 | Restore kEdh in-paper locations? | **Yes.** | "explained on line 182", "Line 290 gives the attributes that matter", "'Deck' is defined in Section 3" restored, each paired with the concession that it comes later than first use. |

## Follow-on calls

**Reliability counts as proportions.** Raw fractions had mismatched denominators across arms
(170 vs 30 vs 10 vs 29) which would distract reviewers. All acceptance, schema-validity and
executability figures are now percentages, with task-set sizes stated once per study so scale
stays visible. Full denominators go in the manuscript revision if accepted. This also retires
the two arithmetic tells flagged in `FACT_CHECK.md` F2 and F4.

**Section 6.4 confirmed** as the correct pointer for the agent-autonomy-under-
specification-relaxation study with the user simulator. The stray "Appendix J" and
"Section 4.6" pointers from v10 are dropped.

## Still open, by prior direction (not blocking)

- **Acceptance parity.** Under the originally shipped configuration Vanilla and S+X were tied
  on acceptance (Fisher p = 1.0000); the 90.0% figure arises only after the validator swap.
  Omitted since v5 by explicit direction. gep1 is the thread where it could plausibly be asked;
  one clause would cover it in discussion.
- **77/77.** Whether the convergence population matches the earlier 31/31 was never resolved.
  The text now reads "every accepted deck we tested for execution completed successfully",
  which is true under either reading. Restore the count only if the populations are confirmed.
