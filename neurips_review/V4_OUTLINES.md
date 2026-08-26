# V4 Response Outlines

Section-by-section plans for the four v4 responses, in the `ladir_rebuttal_iclr.md` structure (grouped
shared content + point-by-point "Response to W#/Q#"). **These are outlines, not prose** — the next session
writes the prose. Read `V4_DRAFTING_PRIMER.md` first; it holds the constraints (10k chars, no links, no
em dashes, no arXiv mention, VERIFIED numbers only) and the number-safety lists. Reviewer map:
**gep1 = Reviewer 1** (4, borderline accept), **kEdh = Reviewer 2** (2, reject), **nBNe = Reviewer 3**
(5, accept).

Only numbers on the primer's "safe to cite" list appear below. Anything marked **[H#]** is a researcher
decision — leave a `[[BLOCKED: H#]]` placeholder, do not pick a side.

---

## AC (Area Chair GKRj) — draft this FIRST

Use `ac_response_outline.md` (advisor-made) as the spine. It already lays out: thank → contributions +
importance (cite reviewer IDs) → the four meta-review weaknesses → the reviewer-2 concern. Post as an
Official Comment to the AC. Keep it **brief and readable** per the advisor (the four bullets in the AC's
order), but it must carry the **eval discussion in substance** — reviewers cannot see this comment, so it
does not lean on any other thread, and the same eval discussion is **repeated in full in gep1** (A1
decision). Target ~5,000 chars, hard cap 10,000.

Notes / corrections to layer onto the advisor's outline:
- **Bullet 1 (structural eval) is the highest-risk paragraph in the whole set.** Follow the §5a playbook:
  (1) scope — the task is translation, physics is supplied in the brief, scored vs a hand-validated
  reference, so structure substantially *is* the quantity of interest; (2) the post-submission work,
  reported honestly, including that **the schema gap does not carry through to loading** (133/170 vs
  132/170) and that we claim **no** execution-level advantage; (3) future work = a plausibility benchmark
  needing domain-expert calibration. Do NOT let schema validity read as "we did the execution study."
- **Bullet 3 (scale):** the "add a new simulator / expand FOAM 5→30" lines in the advisor outline are the
  paper's own transfer numbers (primer §8, from `siga_arxiv_2.tex` — never named). Cite them as
  **qualitative** transfer evidence. The solid scale points are "27 evaluated GEOS tasks (17 val + 10
  held-out), not 10" and uncertainty on the held-out data narrowing the claim to a hard-tail effect.
- **Bullet 2 (clarity):** the strongest AC-level argument (from the v3 AC draft, worth keeping): clarity
  is **the one weakness certain to be fixed** — no experiment, entirely camera-ready scope — and a certain
  fix should weigh more than a hoped-for one in a borderline decision. **[H2]** governs how hard to commit.
- **Reviewer-2 concern:** briefly make the reject-criteria-mismatch + Use-Inspired-venue points here too
  (full version goes in kEdh). Quote the Use-Inspired definition, do not link it.
- Do **not** volunteer the main-effects correction here (decided: omit — contested val inputs; primer §8).

---

## gep1 (Reviewer 1) — carries the full evaluation content. Target ~9,500 chars (may split to `gep1_post2.md`)

**Opening:** thank the reviewer for an unusually actionable review; both score-moving items (structural
eval, S/X + prefix confounds) were specific enough to act on directly, and we did.

**Response to W1 / Q1 — structural eval [score-moving]:** the full eval treatment lives here, **repeated in
full** (scope + post-submission work + future-work framing per primer §5a). Do **not** write "see our
comment to the AC" — gep1 cannot see it. Use the researcher-confirmed framing (TreeSim fine for current
scope; we agree plausibility is crucial for scope expansion / future work; we have results for several
approaches to report; LM-as-a-judge needs ongoing domain collaboration). Use the two-axis framing, not
"ladder/rungs."
- Scope: translation task, physics in the brief, hand-validated reference → structure is the right primary
  measure at this scope.
- What we ran since submission (VERIFIED, held-out): schema-valid **155/170 vs 170/170** (17 seeds, gap
  8.8, CI [+2.9,+16.5], p=0.0006); **loads 133/170 vs 132/170** — say plainly the structural gap does not
  by itself carry to loading; **converges 31/31** (loading is the binding constraint); output fidelity
  **ρ=0.31**, **0.958 conditional on running**.
- The honest headline finding: `xmllint --schema` (GEOS-recommended, and what we built in) ≠
  `geosx --validate-input`; **49/180** decks pass xmllint but GEOS refuses them, exactly the
  cross-reference/arity errors the bottleneck analysis calls unfixed. Validator swap in the loop:
  **S+X 23→27/30, S+X+M 24→25/30.**
- Two nulls reported **as tests** that defend the metric: semantic judge ties plain TreeSim (Δρ=−0.040);
  physics-weighted TreeSim is a tight null (51st percentile of random subsets, min-detectable Δρ=0.034) →
  uniform weighting now stands on a test, not an assumption.
- Future work: a plausibility metric needs a purpose-built, expert-labeled benchmark. Scope, not caution.
- **Do NOT claim an execution or output-fidelity advantage between conditions.**
- **[H19/H22]** how far to walk back the reliability claim / whether to volunteer ρ≈0.31.

**Response to W2 — scale/seeds:** benchmark is **27 evaluated GEOS tasks** (17 val + 10 held-out), not 10;
give held-out uncertainty and narrow to a **hard-tail reliability effect**; reliability replicates across
simulators. Cite the transfer numbers from the paper's own study (in `siga_arxiv_2.tex`, never named):
OpenFOAM SIGA **0.870** at n=30, all SIGA cells 30/30 full coverage; Foam-Agent **0.516** (19/30),
MetaOpenFOAM **0.379** (10/30); LAMMPS **4.56→7.78** and **6.33→6.89**. Keep the framing **qualitative
transfer evidence** (single-run), not a second/third benchmark. H1 is resolved — the paper already uses the
n=30 OpenFOAM numbers.

**Response to W3 / Q2b — S/X confound [score-moving]:** Resolution-IV separates the main effects; the S×X
interaction aliases. Explain the two factors plainly (S = mandatory, terminal stop-hook; X = voluntary,
mid-turn validator) and point to the build-up ablation (val, VERIFIED): S **+0.008**, X-on-top **−0.007**,
together **+0.000** → "X buys nothing once S is on," not "X hurts." Add hook telemetry (they are
substitutes). Be straight it does not prove stop-hook dominance on the hard tail.

**Response to Q2a — native-plugin-prefix bug [score-moving]:** effect bounded at **+0.004** (3 seeds ×
17 tasks, no task moves >0.10); **Vanilla and SE both attempt 0** retrieval calls, so the headline
Vanilla→SE contrast is untouched; the bias runs against us, so adapter lifts are **understated**.

**Response to Q3 — OpenFOAM:** strengthened (see W2) and we accept the fallback: keep transfer claims
explicitly qualitative; Foam-Agent execute mode did not run in our env, so that comparison is lint-only —
say so in the text, not a footnote.

**Response to Q4 — human baseline:** concede — relabel "preliminary calibration," remove comparative
time-savings language from abstract/intro.

**Limitations wording:** adopt the reviewer's own sentence ("supports structural authoring reliability,
not validated simulator correctness") in the main body.

**Table hygiene:** exclude the "Vanilla + geosx hook" condition from any table (primer §8).
**[H3]** placeholder where relevant (main-effects correction — default: omit).

---

## kEdh (Reviewer 2) — the reject on writing clarity. Target ~7,000 chars

**Strategy (primer §5b, researcher-CONFIRMED — firm, not apologetic): do NOT concede the writing is poor,
and do NOT frame clarity as a weakness at all.** For each item kEdh named, show where the paper already
explains it, and offer/promise to add further clarification in the revision — an offer to expand, never a
confession of a defect. Reframe against the reject criteria. Push back firmly on the venue. Base the
replacement text on `responses/v3/kEdh.md` (the text is good) but drop its opening concession ("We accept
this criticism"); rewrite fresh, no verbatim arXiv sentences (anonymity), no em dashes.

**Opening:** thank the reviewer; note the strengths they credit; then, instead of accepting a clarity
weakness, state that the concepts they flag are in fact explained in the paper, point to where, and say we
are happy to add further clarification in a revision.

**Reframe against NeurIPS reject criteria (do this prominently):** the rating-2 rubric is about technical
flaws / weak evaluation / inadequate reproducibility / novelty. This review flags **none** of these; the
strengths section credits the contribution. The concerns raised are about presentation, not the stated
grounds for rejection, and all three reviewers class the contribution as significant and Use-inspired.

**Response to W1 — Buckley-Leverett & Resolution-IV unexplained:** show the paper does introduce them, and
paste **improved replacement text** for first-use (plain-prose gloss of the fractional-factorial design +
its aliasing cost; one-sentence Buckley-Leverett gloss). Add the missing Box-Hunter-Hunter citation. Frame
as "we explain these and are happy to make the explanation clearer," not "our writing is bad."

**Response to W2 — "deck" defined too late; jargon sentences:** note the concrete fix (define "input deck"
at first use) and paste clean rewrites of the two sentences the reviewer quoted ("strictly perfect decks";
the failures-as-zero sentence), removing the internal status strings.

**Response to W3 — examples of "briefs" / "structured repair feedback":** paste the two concrete examples
(a brief excerpt showing it is pure domain language naming no XML element; a real structured-repair-hook
message showing it names file/line/element/attribute and how to re-check).

**Response to venue (W1 item 4 / Questions) — push back firmly:** the researcher's position is that this
criticism is out of line and NeurIPS is a perfectly reasonable venue. Rebut confidently (but
professionally) by quoting NeurIPS 2026's **Use-Inspired** contribution-type definition ("the main
contribution is in framing or designing approaches to meet the needs of a specific real-world application,
often involving engaging with domain experts") **by name, no link** (primer §3.2). Argue that
AI-for-scientific-simulation in geophysics fits it squarely, that all three reviewers already tagged the
paper Use-inspired, and that the AC and reviewers judged the contribution significant. This is not a
concession that the venue is borderline; it is a rebuttal that the venue fit is clear.

**Close:** we would rather show the fixes than argue about them, and welcome being told if any replacement
is still unclear during discussion. **Never mention the arXiv rewrite.**

---

## nBNe (Reviewer 3) — positive review; refer to Reviewer 1. Target ~3,500 chars

**Rule: answer the three questions, concede gracefully, change nothing else. Do NOT re-argue novelty.**
Per the A1 decision, keep the eval content **super brief** here and **refer to our response to Reviewer 1**
for the full treatment (reviewers can see each other's per-review threads).

**Opening:** thank for the careful reading and positive assessment; all three questions point at things we
agree with.

**Response to Q1 — convergence / output validation:** the most-common thread across reviews, so it was our
first priority. Give a **2–4 sentence** summary only (we now check the deck loads, converges, and compare
outputs; loading is the binding constraint; plausibility scoring is ongoing future work with domain
experts), then **"please see our response to Reviewer 1 for the full evaluation."** Do not paste the full
number set here; do not claim an execution advantage.

**Response to Q2 — human expertise levels + collaborative setting:** concede; relabel preliminary
calibration; both go into future work explicitly. Offer the supporting observation from the
consultation-channel study (agent used the human channel in only 2 of 64 trials because the example
library was a cheaper substitute) — motivates why genuine collaboration needs a different task design.

**Response to Q3 — exact Claude Code version:** **2.1.119** (confirmed across 903 init events, zero
exceptions); concede the container installed it **unpinned** and we will pin + report the container digest.

**Response to W1 — no new architecture:** agree, and it is deliberate — the question is how much
wrapper-level grounding buys on an unmodified harness; a cheap intervention with a real effect is the
informative result.

**Response to W2 — TreeSim structural:** point to Q1 + the scope argument (translation task, physics in the
brief).

**Response to W4 — small/undiverse task set:** 27 evaluated GEOS tasks; OpenFOAM grown to n=30 and LAMMPS
added as a third simulator with a different input format (no formal schema), which addresses task-type
diversity as well as scale. Cite the paper's transfer numbers (see gep1 W2); keep qualitative.

---

## Cross-cutting reminders for all four

- No em dashes. No links. 10k char cap each. No arXiv mention. VERIFIED numbers only (primer §8).
- Two-axis framing, not "ladder/rungs." Exclude "Vanilla + geosx hook" from tables.
- Propagate corrected overnight numbers everywhere (primer §9 — the v3 reviewer files are stale).
- End the package with a short "Decisions needed from you" list for the researcher — the still-open ones:
  H2 (how strong a clarity commitment), H7 (Table 5), H10 (harness fairness bug), H19/H22/H23 (reliability
  walk-back, ρ disclosure, A2 CSV fix). Already decided (bake in, no placeholder): A1 structure, A2 clarity
  posture, A3 venue, H1 (cite paper's OpenFOAM/LAMMPS numbers, qualitative), H3 (omit main-effects
  correction).
