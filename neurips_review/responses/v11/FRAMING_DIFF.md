# Framing differences — condensed (top) vs. settled (bottom) half

What the advisor's condensed version **adds**, **removes**, and **reframes**. Ordered by how
much it changes what a reviewer takes away.

Approximate length: bottom half ≈ 6,900 words; top half ≈ 2,400 words (roughly a 65% cut).

---

## 1. The largest structural change: the AC response loses its argumentative spine

The bottom half's AC response is built as a **case**. The top half turns it into a **status
report**.

Removed entirely from the top-half AC:

| Section removed | What it was doing |
|---|---|
| **Contribution Summary** (with the "vs. human: minutes instead of hours" and "up to 22% fewer tool calls / 18% less wall-clock" bullets) | Stated the paper's value proposition in the AC's own terms before defending anything |
| **Summary of Reviewer-Identified Strengths** (7 bullets, quoted verbatim from the reviews) | Established that the reviewers agree on significance, method, design, reliability, generalization, and the human baseline — including that **all three rated significance and originality good or better, including the reviewer recommending rejection** |
| **The scale defense by comparison to the field** — "in line with contemporary work in the area, which evaluates on 2 to 12 cases [1–5]" | The single strongest answer to the scale objection: it reframes 27 tasks as generous, not thin |
| **The explicit reasoning about where to spend the budget** — "generalization is better tested by a second and third simulator than by a 28th GEOS task" | Converts a resource limitation into a design decision |
| **Section 5, Venue fit**, including the NeurIPS 2026 Use-Inspired contribution-type guidance and the closing challenge: *"The review recommends rejection but does not identify a technical, evaluation, reproducibility, or ethical concern."* | The only place the rejection recommendation is directly contested at the AC level |
| **References [1]–[5]** | The evidence behind the scale defense |

The top half retains a compressed strengths sentence (L7) and moves venue fit down into the
kEdh thread in softened form. Net effect: **the AC reads a summary of new experiments rather
than a case for the paper.** If you keep the condensed version, the strengths paragraph and
the [1–5] scale citation are the two highest-value restorations.

---

## 2. Tone: from "here is the evidence, and here is what it does and does not show" to "we will fix it"

The bottom half is written in a **concede-precisely-then-defend** register. The top half is
written in a **concede-and-promise** register. Concretely:

| Bottom half | Top half |
|---|---|
| "Each concept the review highlights **is defined in the submitted paper**, and we locate each below. What the review identifies, usefully, is that several are defined **later than their first use**, an ordering problem with a definite fix." | "The review identifies several places where key concepts appear before they are explained. We will address this by moving definitions to first use…" |
| Cites the exact locations — "explained on line 182", "defined in Section 3", "Line 290 gives the attributes that matter" | No locations at all |
| "We would rather show the fixes than argue about them, which is why the replacement text is above rather than described." | (Closing removed) |
| "NeurIPS does not permit a revised PDF during this period, so we give the proposed replacement text inline below." | (Removed — so the inline replacement text has no stated reason for being inline) |
| "We do maintain, however, that it is a useful calibration: it establishes a human pace on a relatively easy 1D problem." | "We will present the two-participant experiment explicitly as a preliminary calibration … rather than as a broad human-efficiency comparison." (concession only, defense dropped) |

**This is the most consequential framing difference.** kEdh recommends rejection primarily on
clarity. The bottom half's answer is "the material is all there, in the wrong order, and here
is the reordered text." The top half's answer is "you are right, we will fix it." The first
version is a much better response to a clarity-based reject.

---

## 3. Content dropped from the reviewer threads

### gep1
- **The LLM-judge physics-plausibility metric** — the whole third bullet, including the
  methodological rigour that makes it credible (four judges from four model families, none of
  them the agent's backbone, blind to condition, order-swapped) *and* the honest verdict that
  it does not beat plain structural scoring and needs expert calibration. Dropped.
- **The physics-weighted TreeSim test** (+0.033, CI [−0.003, +0.072]) — the sentence
  "uniform weighting now rests on a test rather than an assumption." Dropped.
- **"Insight" lines under each metric.** The bottom half attaches an interpretation to every
  result ("execution is not the bottleneck, deck construction is"; "a 2.5 second acceptance
  check captures nearly all of the execution signal"). Mostly dropped.
- **The entire "Beyond GEOS" block** — LAMMPS never appears in the top half's gep1 thread,
  even though the top-half AC promotes it. So the reviewer who asked about scale is the one
  reviewer not told about the third simulator.
- **The external baselines' text-similarity scores** (0.565, 0.276) — the top half keeps only
  the executability counts. Since the bottom half's own point is "the text-similarity margins
  are modest; the executability margin is not", dropping the modest number and keeping the
  favourable one changes the character of the comparison.
- **The "Additional point: limitations wording"** closing section. Dropped.

### kEdh
- All **line-number locations** (182, 290, Section 3) — see §2 above.
- The **Box–Hunter–Hunter citation** for Resolution-IV.
- The **verbatim brief excerpt** is replaced by a paraphrase (see §5).
- The **"NeurIPS does not permit a revised PDF"** framing note and the **Closing**.
- The bottom half's version of the "strictly perfect" replacement, which keeps the 0.999
  definition (see `FACT_CHECK.md` F5).

### nBNe
- The **[6, 7] citations** (CollabLLM, ToM-SWE) backing the claim that autonomy-optimised LLMs
  are not ready for interactive modes. Top half asserts it uncited.
- The **"20-task scale-up underway"** for LAMMPS, and the OpenFOAM 89.7% vs 10%/22% comparison.
- The justification that makes fidelity interpretable: *"Because our tasks are sourced from
  documentation examples, which correspond to representative workflows, the ground-truth
  outputs are physically meaningful."* Dropped.

---

## 4. What the top half **adds** (genuine improvements — keep these)

1. **W-numbered headings that match the reviews.** Top half uses `W1./Q1.`, `W3./Q2.`, `W2.`,
   `Q4.` etc. The bottom half labels some sections `Q2a`/`Q2b`/`Additional point`, and both
   gep1 and nBNe jump W2 → W4 with no W3 in the bottom half. The top half's numbering makes it
   obvious that every raised point is answered. **Adopt the top half's headings.**
2. **A real explanation of the 17/10 split** (top L66): *"the split mostly for improving
   iteration speed on the factorial eval and providing a held out set for the self-evolution
   setting."* The bottom half never explains *why* the split exists. This is new and good.
3. **A sharper takeaway for the human-collaboration finding** (top L158): the two numbered
   implications — benchmarks need clear informational boundaries between agent and human; and
   autonomy-optimised models are not ready for collaborative modes — are crisper than the
   bottom half's prose.
4. **Reviewer-facing brevity.** At ~2,400 words the top half is comfortably postable. The
   bottom half's gep1 thread alone is long enough that a reviewer may not finish it.
5. **The kEdh replacement text for failures-as-zero** is more readable in the top half's
   version, once the grammar is fixed.

---

## 5. One framing change that is a downgrade, not a compression

The bottom half's kEdh examples are **real artifacts**, and their provenance was verified
byte-for-byte: the brief is 3,672 B / 569 words, md5 `7c34ddc9…`, with every quoted fragment
re-verified via `grep -F`; the repair feedback is a real held-out instance on the paper's own
backbone (`PROVENANCE.md` #15, #16). The bottom half labels it as such: *"Here is a real,
lightly elided instance of structured repair feedback."*

The top half replaces both with clean paraphrases and presents them in blockquotes as
"Example task brief" / "Example repair feedback". They read better, but they are **no longer
artifacts** — and kEdh asked to *see* the artifacts. Restoring the verbatim versions is
strictly stronger, and it is what the reviewer requested.

---

## 6. Emphasis shift on the new evaluation results

| | Bottom half | Top half |
|---|---|---|
| Number of new metric axes presented | 3 (execution, output, LLM judge) | 2 in gep1/nBNe, 3 in the AC |
| Framing of the fidelity result | "the gap between structure and physics sits in decks that fail to run" — a **reliability** argument | "SIGA's reliability extends beyond structural correctness" — a **physics-improvement** argument (unsupported; see `FACT_CHECK.md` F1) |
| Self-criticism volunteered | substantial (judge doesn't beat structural scoring; two of four judges reverse the ordering; three-runs-per-cell hedge) | mostly removed |
| Uncertainty reported | CIs and p-values on most numbers | CIs kept on the schema-validity gap and ρ; dropped on the S/X build-up |

The bottom half's volunteered self-criticism is doing real work with gep1, who explicitly
credited the paper's *negative findings* as adding credibility ("the bottleneck analysis and
negative findings add credibility"). Removing it removes the thing that reviewer said they
liked.
