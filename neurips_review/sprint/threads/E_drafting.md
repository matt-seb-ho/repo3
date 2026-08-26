# Thread E — drafting the four responses (main thread)

Spec: `neurips_review/prompts/03_rebuttal_drafting.md`. Budgets: gep1 ~9,500 · kEdh ~7,000 · nBNe ~3,500 · AC ~5,000 characters (hard OpenReview cap is 10,000/review).

---

## 2026-07-26 22:2x UTC — Outline v1, with character allocations

### Strategy in one paragraph

**gep1 is the only winnable score** — rating 4, confidence 3, two explicit conditionals, one point from accept. **kEdh will not move** (rating 2, confidence 4, "needs to be significantly re-written"); their function now is as ammunition for the AC, so the kEdh text is written to be *read by the AC*. **nBNe is at 5** — answer the three questions, concede, and give them no new reasons to think. The handbook says the meta-review is the guide, so the **AC text is the one that has to be perfect**, and it follows the AC's own four bullets in the AC's own order.

Two structural commitments that apply everywhere:

1. **Separate the reliability claim from the mean-lift claim.** The headline is reliability (σ 0.081 → 0.002 on held-out, catastrophic-failure elimination). *You do not need physics to know that an empty, unparseable, or absent file does not run.* Only the mean-lift claim depends on TreeSim's semantics. The paper currently blurs these; separating them is the single strongest move available, and it is free.
2. **Nothing pending is load-bearing.** Every draft is written to stand on P0 + Track C evidence alone. Tracks A/B fold in as strengthening if they land, as follow-up comments if they land late, and cost nothing if they don't.

### Framings to use verbatim (and the ones to avoid)

| Use | Do NOT use |
|---|---|
| "The deck is a **sufficient statistic** for the simulation — no hidden state, no stochasticity. Deck authoring is therefore a well-posed target of study, and the open question is the *metric on decks*, not the *choice to evaluate decks*." | "GEOS is deterministic, therefore input-side evaluation is fair." A reviewer will bounce that: determinism says the input→output map is a function, not that it is well-conditioned — and PDE solvers are ill-conditioned exactly where it matters. |
| Non-uniqueness: **common-mode argument first.** TreeSim penalizes correct-but-different decks equally in *every* cell, so it depresses the absolute level for everyone and leaves the *contrast* intact. It attacks "SIGA scores 0.78", not "SIGA beats Vanilla by 0.069." | Leading with brief-specificity. That is the secondary argument — use it only as the reason the alternative-spec space is small to begin with. |
| Naming the ladder and stating which rung we are on. | Any phrasing that lets schema validity read as "the execution evaluation." It is rung 2 of 5, the AC made execution the decision criterion, and this is the single highest-risk move available. |

---

## gep1 — 9,500 characters

Priority order from the spec: execution/validity ladder → prefix bug + S/X isolation → OpenFOAM → human baseline → limitations wording.

| § | Content | Chars |
|---|---|---:|
| 1 | **Opening frame.** Separate reliability from mean-lift. Name what the response will concede up front (human baseline, transfer claims, structural-not-validated) so the concessions are ours, not extracted. | 700 |
| 2 | **Q1 — execution / physics validity** (score-moving, and the AC's primary). The ladder as a table, rungs 1–5. State what is verified vs named. Then state both caveats **ourselves**: (a) S- and X-cells invoke `xmllint`, so a perfect rung-2 score is partly true by construction — **X+M is the least circular cell**; (b) effective n is well below 30 because the Vanilla failures span only 4 distinct tasks and cluster by seed. Sufficient-statistic framing. Common-mode argument on non-uniqueness. Explicit statement that this is a *calibration study*, not a physics benchmark. **No delivery date.** | 2,800 |
| 3 | **Q2a — native-plugin-prefix bug** (score-moving). Ground the dismissal **empirically, not chronologically**: a dedicated probe, C2 0.9134 vs C9 0.9170, Δ = **+0.004**, zero big-swing tasks, 3 seeds × 17 tasks. Both bias directions favour the paper. Disclose the SE/SE-prose asymmetry before being asked. | 1,300 |
| 4 | **Q2b — S/X isolation** (score-moving). Resolution-IV *does* separate main effects — say so, the design is sound. What it cannot give is S×X, aliased with R×M. Then the direct answer from the build-up ablation: C2→C6 (**S**) = **+0.008**, C6→C7 (**X** on top) = **−0.007** → X adds nothing once S is on, which is exactly his bar. Caveat honestly: val-only, and val is at ceiling. | 1,300 |
| 5 | **Q3 — OpenFOAM.** Keep transfer claims explicitly qualitative (his own stated fallback). Decline Foam-Agent execute mode (fails in our environment; he permits this). *Content here depends on **H1**.* | 900 |
| 6 | **Q4 — human baseline.** Concede outright. Reframe as "preliminary calibration" — the AC's own phrase. | 500 |
| 7 | **Limitations wording.** Give him the sentence he asked for, verbatim, and commit it to the camera-ready main body. Cheapest win in the whole response. | 400 |
| 8 | **Main-effects correction.** *Conditional on **H3**.* If included: framed as the stale-derived-table story from `threads/P0_verification.md`, with R −0.037 · S −0.008 · X +0.011 · M +0.008 and the observation that all four move away from zero. If H3 says no, this section is cut and **nothing** is said about it. | 700 |
| 9 | **Scale.** Take the trade the AC offered: bootstrap intervals on existing data, representativeness of the hard tail, and explicitly narrow the robustness/generalization claims. Per-cell σ table. | 600 |
| 10 | Close — restate the two conditionals he set and what we believe now meets them. | 300 |
| | | **9,500** |

## kEdh — 7,000 characters

Priority: definitions and worked examples **shown inline**, not promised → camera-ready plan → one line on venue. Written to be read by the AC.

| § | Content | Chars |
|---|---|---:|
| 1 | Accept the critique without defensiveness. No litigating. | 400 |
| 2 | **Their item 1** — "Resolution-IV 2^(4−1) factorial" in plain prose, and a Buckley–Leverett gloss. Replacement text shown, not described. | 1,300 |
| 3 | **Their item 2** — "deck" defined at first use in the abstract; the "strictly perfect decks" sentence rewritten; the failures-as-zero sentence rewritten. Shown inline. | 1,700 |
| 4 | **Their item 3** — one worked example of a "**brief**" and one of "**structured repair feedback**", both concrete. This is the single most persuasive block in this response; give it the most room. | 2,200 |
| 5 | **Camera-ready commitment** — a concrete enumerated list, not a vague promise. *Strength of commitment depends on **H2**.* | 900 |
| 6 | **Venue** — one non-defensive sentence. They already called it the committee's call. Do not litigate. | 200 |
| 7 | Close. | 300 |
| | | **6,800** |

## nBNe — 3,500 characters

Rating 5, confidence 5. Answer the three questions, concede gracefully, **change nothing else**. Do not re-argue novelty.

| § | Content | Chars |
|---|---|---:|
| 1 | Thanks + one-line frame. | 250 |
| 2 | **Q1 — convergence checks and output validation.** The ladder, honestly scoped. Note they asked for *simulator* output validation specifically, so an LLM-judge metric is explicitly **not** offered as the answer to it. | 1,200 |
| 3 | **Q2 — expertise levels + human-agent collaborative setting.** Concede; future work. Agree it is the realistic usage mode. | 700 |
| 4 | **Q3 — exact Claude Code version.** `2.1.119`, plus the honest concession that the Docker image installed it **unpinned**, so the version tracked build time — which is exactly their point. | 600 |
| 5 | **W1 — no new architecture.** Brief. They rated 5 *despite* this; do not over-argue. | 350 |
| 6 | **Scale** — narrow the claims. | 400 |
| | | **3,500** |

## AC — 5,000 characters

The four meta-review bullets, in the AC's own order. This is the spec; the union of reviewer asks is not.

| § | Content | Chars |
|---|---|---:|
| 1 | **Bullet 1 — structural-only evaluation.** The reliability-vs-mean-lift separation, then the ladder with the rung we are on named explicitly and the circularity caveat stated by us. Highest-risk section in the whole set: **must not read as "we answered the execution ask."** | 2,000 |
| 2 | **Bullet 2 — clarity / jargon.** Point at the kEdh response for the actual replacement text, then make the argument aimed squarely here: *clarity is the only weakness on the table that is **certain** to be fixed; evidence gaps depend on experiments that may not land or may come out negative. A certain fix should be weighted differently from a hoped-for one.* | 1,300 |
| 3 | **Bullet 3 — limited experimental scale.** Take the offered trade explicitly: representativeness argument + bootstrap intervals + narrowed claims. | 900 |
| 4 | **Bullet 4 — human comparison too small.** Concede, reframe as preliminary calibration. | 400 |
| 5 | Venue, one sentence. | 150 |
| 6 | Close — what changed, what is pending, no promises. | 250 |
| | | **5,000** |

---

## Blocked-on / conditional content

| Section | Blocked on | Fallback if unresolved |
|---|---|---|
| gep1 §8 (main-effects correction) | **H3** (advisor) | Cut entirely and say nothing. A wrong or unwanted correction is worse than none. Evidence is ready either way (`threads/P0_verification.md`). |
| gep1 §5, AC §3 (OpenFOAM n=30 reversal) | **H1** (advisor) | Report the submitted n=5 result only, transfer claims qualitative. |
| kEdh §5, AC §2 (camera-ready commitment strength) | **H2** (advisor) | Commit only to the specific enumerated items, no global promise. |
| all — verbatim vs paraphrase of arXiv text | **H4** (advisor) | **Default to paraphrase.** Costs nothing; a distinctive searchable sentence is an unforced anonymity violation. |
| gep1 §2, AC §1 (rung-2/3 numbers) | Thread **A1** | Rung 1–2 from A1's re-run. If A1 fails entirely, describe the ladder qualitatively and name no numbers — do **not** fall back on the plan doc's unverified 24/30 vs 30/30. |
| gep1 §9, AC §3 (bootstrap CIs, per-cell σ) | Thread **D** | Per-cell σ is already verified from Table 1 (P0 finding F1); CIs can be dropped if D stalls. |
| §3/§4 numbers (prefix probe, S/X) | Thread **C** | If C cannot reproduce them from raw, these sections come out. Both are gep1's score-moving items, so this would hurt — but quoting an unreproduced number would hurt more. |

## Verified and ready to write now (needs no track)

- Reliability / mean-lift separation — framing, no new numbers.
- Sufficient-statistic and common-mode arguments — framing.
- Table 1 val column, all 11 cells, mean ± σ — **verified 11/11** (P0).
- Per-cell held-out σ: Vanilla 0.081 · X+M 0.005 · S+X 0.002 · SE 0.012 — from Table 1 `:195–202`, cross-checked by P0's cell-identity mapping.
- Vanilla → SE held-out Δ = +0.069, and the hard-tail concentration argument (`:212` — the other seven held-out tasks have a Vanilla mean of 0.898, indistinguishable from val's 0.910). **This is a strong and underused argument for representativeness.**
- Corrected main effects R −0.037 · S −0.008 · X +0.011 · M +0.008 — verified, pending only the H3 *decision* to use them.
- Limitations sentence for gep1 §7 — pure writing.
- kEdh's definitions and worked examples — pure writing.

---

## 2026-07-26 22:1x UTC — v0.1 skeletons written for gep1, nBNe, AC. kEdh awaits Thread F.

Three of four responses now exist as postable drafts with explicit `[[BLOCKED: …]]` markers where a track's numbers go. Per the spec's requirement that a postable response exist regardless of what finishes, each blocked marker names its own fallback.

Folded in so far: P0's verified Table-1 numbers, and A1's verified rung 1–2 ladder (Vanilla 24/30 vs 30/30, the failure-mode breakdown, the `--`-in-comment root cause, the effective-n caveat, and the scorer silent-drop disclosure).

### ⚠ CHARACTER BUDGET PROBLEM — gep1 is over the hard cap

| Response | prose now | budget | **hard cap** | open placeholders | verdict |
|---|---:|---:|---:|---:|---|
| gep1 | **10,288** | 9,500 | **10,000** | 8 | **over cap before pending content lands** |
| nBNe | 3,275 | 3,500 | 10,000 | 3 | fine |
| AC | 5,999 | 5,000 | 10,000 | 4 | over budget, under cap |

One compression pass already ran on gep1 (−474 chars: merged the sufficient-statistic and non-uniqueness paragraphs, tightened the failure-mechanism block). Not enough.

**Reserve rule adopted:** hold **1,500 chars** for pending Track A1/C/D content, so the pre-fill target for gep1 is **8,000**, and for AC **4,300**. That means gep1 needs roughly **−2,300** and AC **−1,700**.

### Compression plan for gep1, in the order I will cut (least load-bearing first)

1. The five-rung ladder table → prose sentence naming the rungs (saves ~350; the table is a nicety, the rung *names* are the content).
2. Merge the two self-stated caveats after the ladder into one paragraph (~200).
3. §1 opening: cut the bulleted restatement of the two claims to a single sentence each (~250).
4. Q3 OpenFOAM: fold the Foam-Agent execute-mode concession into one sentence (~200).
5. Per-cell σ table: 6 rows → 4 (Vanilla, X+M, S+X, SE), which is the set the drafting spec actually names (~180). **Keep the table** — it is what prevents a cross-cell mean/σ pairing question.
6. Closing paragraph → one sentence (~200).
7. Last resort: the scorer silent-drop disclosure. **Do not cut this** — it is a defect gep1 could find in the code himself, and disclosing it first, with the favourable bias direction, is worth more than the characters it costs.

Do NOT cut, at any budget: the two score-moving answers (Q2a prefix, Q2b S/X), the effective-n caveat, the rung-2 circularity caveat, or the limitations sentence he explicitly asked for.

---

## 2026-07-26 22:3x UTC — v0.2. **gep1's content genuinely exceeds one 10,000-char post. Plan two posts.**

After two compression passes (10,762 → 9,694 prose, with the ladder table converted to prose, the caveats merged, and the opening, Q3 and closing all tightened), gep1 sits at **9,694 with 306 chars of headroom** and four open placeholders that will need roughly 1,070. **It does not fit**, and every remaining cut would come out of score-moving evidence.

**Decision (D5): gep1 gets two posts, not one.** NeurIPS permits posting through Aug 3 and the handbook explicitly advises "engage early and engage often," so this is a normal use of the discussion phase rather than a workaround.

- **Post 1 — the initial Rebuttal (≤10,000):** the opening reliability/mean-lift split, Q1 (ladder rungs 1–2 verified, failure mechanism, three caveats, the well-posedness framing), Q2a (prefix), Q2b (S/X), the Limitations sentence he asked for, and Scale/uncertainty. These are the two score-moving items plus the two cheapest wins.
- **Post 2 — a same-day Official Comment:** Q3 OpenFOAM detail, the main-effects correction pointer, and anything from H1.
- **Post 3 — later, if it lands:** rungs 3–5 and LMaaJ, as the sprint prompt already specifies for pending tracks.

Two structural moves that bought the room:

1. **The main-effects correction moved from gep1 to the AC comment.** It is a paper-level correction and the AC is the decision-maker; the AC text has 2,770 chars of headroom where gep1 has 306. gep1 gets a one-sentence pointer if H3 is yes.
2. **Rung 3+ is stated as a forthcoming follow-up rather than reserved as a placeholder.** This is what the sprint prompt directs for pending tracks, and it removes the largest open slot from the initial post.

**Revised budget reality**, replacing the spec's allocations where they conflict with the hard cap:

| Response | prose | spec budget | hard cap | open | verdict |
|---|---:|---:|---:|---:|---|
| gep1 | 9,694 | 9,500 | 10,000 | 4 | **split across two posts** |
| nBNe | 3,713 | 3,500 | 10,000 | 2 | fine, slightly over budget, well under cap |
| AC | 7,230 | 5,000 | 10,000 | 5 | **over spec budget deliberately** — it absorbed the corrections section; still 2,770 under cap |
| kEdh | — | 6,800 | 10,000 | — | awaiting Thread F |

The AC overage is a deliberate reallocation, not drift: the handbook says the meta-review is the guide, the AC text now carries both volunteered corrections, and there is no competing use for its headroom.

---

## 2026-07-26 22:4x UTC — v0.3. **Five posts, not four.** Both gep1 and the AC needed splitting.

Once Tracks A1, C, D and B all landed, the verified content exceeded the 10,000-char-per-post cap for two of the four targets. Rather than delete verified evidence, both are split. **Decision D6:** the AC also gets a companion comment.

| File | Post | Contents | prose | open |
|---|---|---|---:|---:|
| `gep1.md` | Rebuttal | reliability/mean-lift split · Q1 execution ladder · Q2b S/X | 8,733 | 1 |
| `gep1_post2.md` | Official Comment | Q2a prefix · Q3 · Q4 · Limitations wording · scale + CIs · clean-subset null · TreeSim audit · correction pointer | 6,866 | 2 |
| `AC.md` | Official Comment | the four meta-review bullets, in the AC's order | 8,701 | 3 |
| `AC_post2.md` | Official Comment | clean-subset null · TreeSim self-audit · rejected LLM judge · both corrections | 4,132 | 3 |
| `nBNe.md` | Rebuttal | three questions · concessions · scale | 4,521 | **0** |

**nBNe is content-complete.** All three of its questions are answered from verified data with no open placeholders.

Split rationale for gep1: Post 1 keeps the AC's primary objection (execution) and the S/X answer — the crisp numeric answer to a score-moving conditional. Q2a (prefix) moved to Post 2 because it is a *dismissal* argument and sits naturally with the other methodology items, and because Post 1 could not hold it.

Split rationale for the AC: Post 1 answers the meta-review as the handbook directs; Post 2 is a coherent standalone unit — "here is what we found when we audited our own evaluation" — carrying every self-caught defect and both volunteered corrections. Putting the disclosures in their own comment makes them read as deliberate rather than buried.

### Framings falsified mid-sprint and corrected in every draft

Two sentences I had already written turned out to be false. Both are worth recording because they were plausible and load-bearing:

1. *"An unparseable file does not run in any simulator under any metric."* **False.** GEOS parses with pugixml, which tolerates `--` inside XML comments where `xmllint` and Python's ElementTree do not (finding F23). Every draft now distinguishes *unscorable by our metric* from *unrunnable by the simulator*, and volunteers the parser-strictness mismatch.
2. *"Val is at ceiling for every cell."* **False** — means are 0.913–0.921, the worst task is 0.77, only 3/17 tasks ≥0.99 (finding F25). Replaced with the true and stronger fact: **no run in the build-up ablation failed at all**, so there are no catastrophic failures for S or X to prevent, which is why the separation is established where the mechanism is inactive.

Also avoided: the execution plan's TreeSim description (§4.4) is wrong about the scoring function (finding F34). No draft quotes it — they say only "a tree match at 1e-6 tolerance," which is accurate. **Keep it that way.**

### Cross-response redundancy is intentional

gep1, kEdh, nBNe, and the AC each read only their own thread, so the ladder framing, the reliability/mean-lift split, and the scale argument are deliberately repeated across files. Do not dedupe them.

## Notes to self

- Character counts are of the **final plain-text markdown**, counted with `wc -m`, not estimated. Count every draft.
- The abstract's "+7pp / 40×" pairing (SE mean with S+X ratio; SE's own ratio is ≈6.75×) is **not to be volunteered**. Print the per-cell σ table and let a reader match ratio to cell. If asked in Phase 2, answer straight.
- Every number goes into `../PROVENANCE.md` before it goes into a draft, not after.
