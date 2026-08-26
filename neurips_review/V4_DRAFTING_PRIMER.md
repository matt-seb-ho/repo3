# V4 Rebuttal Drafting — Session Primer

**You are a fresh Claude Code session whose only job is to draft the v4 SIGA NeurIPS rebuttal responses.**
This primer gives you everything you need. The lab server that ran the experiment sprint lost its
connection, so this work is being done on a second machine that has the rebuttal docs but **not** the
raw experiment data. Read this whole file first, then the "Read these first" list, then draft.

The task instructions from the researcher are in `siga_write_v4_response.md` (in this folder). This
primer is the context that makes those instructions actionable. Where this primer and the task file
overlap, the task file is the authority on *what to write*; this primer is the authority on *what is
true, what is safe to cite, and what you must not do.*

---

## 0. TL;DR — what you are doing

Draft **v4** of the rebuttal: one response to the **AC** (drafted first), and updated responses to the
three reviewers. The sprint that generated all the evidence is **finished**. **No new experiments are
needed or possible from this machine** — v4 is a *drafting and framing* task built entirely from
already-verified numbers. Your job is persuasion and clarity, not new analysis.

The core message across all four responses is the same and it is already worked out (see §5):
1. TreeSim's structural score **fits the scope of the current task** (translation, not physics discovery).
2. We did **substantial post-submission evaluation work** (execution, convergence, output-fidelity) and
   report it honestly, including the nulls.
3. Fuller physical-plausibility scoring is **future follow-up work** that needs domain-expert calibration
   and its own benchmark — a scope statement, not a hedge.

---

## 1. Read these first (in this order)

| Order | File | Why |
|---|---|---|
| 1 | `siga_write_v4_response.md` | The researcher's actual instructions for v4. |
| 2 | `ac_response_outline.md` | The AC-response outline made *with the advisor*. Fill this out (§4). |
| 3 | `ladir_rebuttal_iclr.md` | A colleague's ICLR rebuttal the **advisor approved of and that succeeded**. Use it as the style/structure template (see §7). |
| 4 | `siga_neurips_reviews_clean.md` | The four reviews (AC + 3 reviewers), with a cross-reviewer issue map at the bottom. |
| 5 | `sprint/EVAL_WORK_EXPLAINED.md` | Plain-language explanation of every piece of post-submission eval work + suggested framing. **This is your main evidence source.** |
| 6 | `sprint/PROVENANCE.md` | The number-safety authority. Every number you cite must have a VERIFIED row here. Read §8 of this primer before trusting any number. |
| 7 | `V4_OUTLINES.md` (this folder) | **Per-reviewer outlines** (gep1 / kEdh / nBNe) prepared for you in the ladir style, plus AC notes. Draft from these. |
| 8 | `responses/v3/01_evaluation.md` | The one v3 file with the **corrected overnight numbers**. Best source for the eval content (written in full in both the AC comment and gep1 — see §6). |
| 9 | `responses/v2/*.md` | The researcher's preferred base for tone/structure ("I liked the v2, build off that"). |
| 10 | `sprint/WHAT_WE_RAN.md`, `sprint/REBUTTAL_REVISION_BRIEF.md` | Narrative of the three campaigns + the drafting brief, if you want more depth. |

**Do NOT base anything on the base-level `responses/*.md` files** (`AC.md`, `AC_post2.md`, `gep1_post2.md`,
`kEdh.md`, `nBNe.md` sitting directly in `responses/`). Those are **v1**, which the researcher dislikes,
and the AC ones were built on a wrong structure (invented from an internal TODO, not the handbook). Use
`responses/v2/` and `responses/v3/` only, and see §8 before trusting any v3 reviewer-file number.

Everything you need to draft is in the files above. `sprint/threads/*.md` are the raw working logs behind
each result, and `sprint/SPRINT_LOG.md` is a 58-finding working artifact the researcher called "asinine" —
consult threads only if a specific number in PROVENANCE.md is unclear, and do not use SPRINT_LOG as a
summary.

---

## 2. Where things stand (situation report)

- The paper is **SIGA** (Simulator-Interface Grounding Adapters), NeurIPS 2026 submission 31642,
  currently **borderline** (scores 4 / 2 / 5). All three reviewers class it **Use-inspired**.
- An overnight/multi-day **evidence sprint** ran (Jul 26–28) to answer the reviews. It is done. It
  produced: an execution "validity ladder" (rungs 1–5), an output-fidelity metric, an LLM-judge metric
  (rejected), a physics-weighted TreeSim variant (null), and a set of self-audits of TreeSim. All
  results are digested in `sprint/EVAL_WORK_EXPLAINED.md` and `sprint/PROVENANCE.md`.
- **v1→v3 responses already exist** (`responses/`, `responses/v2/`, `responses/v3/`). v3 is the latest
  full pass. There are also Phase-2 follow-up drafts (`AC_post2.md`, `gep1_post2.md`).
- **You are drafting v4.** Per the task file, v4 restructures around: (a) an AC response filled from the
  advisor's outline, (b) a sharpened reviewer-2 (kEdh) rebuttal, (c) eval work concentrated in
  reviewer-1's (gep1) response with reviewer-3 (nBNe) pointed to it.

### Timeline / deadline (from `neurips_timeline_instructions.md`)
- **We are in Phase 2** (Jul 27 – Aug 3): reviewers and ACs can now see responses and message each
  other. Today is **2026-07-28**.
- **Hard deadline Aug 3.** Phase 3 (Aug 3–10) is reviewer/AC-only; authors cannot post or even see it.
  Anything posted after Aug 3 is worthless for the decision. So v4 should be finalized within days.
- Because we are in Phase 2, reviewers can see each other's per-review threads — so a **cross-reference
  between reviewer responses** (e.g. nBNe → "see our response to Reviewer 1") is viable. But the AC
  Official Comment is **not** reviewer-visible, so never point a reviewer to it. This is exactly why the
  eval discussion is written in full in both the AC comment and gep1 (see §6).

---

## 3. CRITICAL CONSTRAINTS — read before writing a single line

These are NeurIPS 2026 handbook rules and project-specific hazards. Violating any of them can sink the
response.

1. **10,000 character limit per review.** Each response is a separate OpenReview "Rebuttal." Budget:
   gep1 ~9,500, kEdh ~7,000, nBNe ~3,500–6,000, AC comment ~5,000. If a response overflows, split into a
   primary "Rebuttal" plus a companion "Official Comment" (that is why `AC_post2.md` / `gep1_post2.md`
   exist).

2. **NO LINKS are allowed.** The only exception is an anonymized *code* link to the AC. This has a direct
   consequence for the task: the researcher wants to point reviewer 2 to the NeurIPS 2026 "choice of
   contribution types" blog post. **You cannot paste that URL.** Instead, **quote/paraphrase the
   "Use-Inspired" contribution-type definition and refer to it by name** ("NeurIPS 2026's own
   contribution-type guidance defines a Use-Inspired track as ...") without a hyperlink. Note that all
   three reviewers *already classified the paper as Use-inspired* — lean on that.

3. **No paper revisions during the response period.** You cannot submit a revised PDF. The established
   (and effective) strategy is to **paste the actual replacement text inline** in the response — this is
   already done well in `responses/v3/kEdh.md`. Continue that.

4. **Anonymity — do NOT mention the arXiv rewrite, but you MAY read it for numbers.** A deanonymized arXiv
   version exists at `writing/arxiv/siga_arxiv_2.tex` (and `.pdf`). It is a legitimate **source of the
   authors' own verified numbers** (e.g. the OpenFOAM/LAMMPS transfer results, §8), and you may open it to
   pull them. But it is *deanonymizing*: **never mention it, cite it, link it, or paste its prose verbatim
   in a response** — reviewers see only the submission, and the rewrite improvements cannot be referenced.
   The motivation (get accepted so those improvements land in camera-ready) is context for *you*, not text
   for the response. Never write anything that reveals author identity or an external posting.

5. **Minimal em dashes.** Explicit researcher style rule. The v3 drafts already avoid them; keep it up.
   (This primer uses them; your output should not.)

6. **Only cite VERIFIED numbers.** See §8. Held-out numbers are safe; validation-set numbers are
   contested. Do not invent or "remember" a number — if it is not in `PROVENANCE.md` as VERIFIED, do not
   put it in a response.

---

## 4. Reviewer map (who is who)

| Tag | = "Reviewer #" in task file | Rating | Core asks |
|---|---|---|---|
| **AC GKRj** | the Area Chair | meta | Structural-only eval (primary), clarity/jargon, limited scale, human baseline too small. **The meta-review is the decision guide.** |
| **gep1** | **Reviewer 1** | 4 (borderline accept), conf 3 | Structural eval (**score-moving**), scale/seeds, S/X confound (**score-moving**), native-plugin-prefix bug (**score-moving**), human baseline. Unusually actionable. |
| **kEdh** | **Reviewer 2** | 2 (reject), conf 4 | **Sole complaint is writing clarity/jargon.** Names Buckley-Leverett and Resolution-IV as unexplained. Suggests eScience venue. **Flags no technical flaw, no novelty problem.** |
| **nBNe** | **Reviewer 3** | 5 (accept), conf 5 | Convergence/output validation, human expertise levels + collaborative setting, larger task set, report exact Claude Code version. Positive overall. |

Task-file routing: put the full **evaluation work in gep1's (Reviewer 1) response**, and **direct nBNe
(Reviewer 3) to that same content**; answer nBNe's other asks directly. Address the AC first.

---

## 5. The argument playbook (already worked out — reuse, don't reinvent)

### 5a. The TreeSim "structural-only" objection (AC + gep1 W1 + nBNe W2) — the centerpiece
Two-part defense, both parts already drafted in `responses/v3/01_evaluation.md` and `EVAL_WORK_EXPLAINED.md`:

**Part 1 — scope.** The task is **translation**: the task brief supplies all the physics (geometry,
permeability, porosity, BCs) in domain language and never names a GEOS XML element. The agent's job is to
express a well-specified intent in the simulator's DSL, scored against a **hand-validated reference deck**.
Under that scope, "did the agent produce the right deck" is largely a *structural* question, and TreeSim
answers it — fast, deterministic, cheap enough to run on every cell of a factorial design.

**Part 2 — the post-submission work, reported honestly.** We built and ran a five-rung validity ladder
and an output-fidelity metric. Safe headline numbers (all VERIFIED, held-out unless noted):
- **Rung 1–2 (well-formed + schema-valid), 17 runs/cell:** Vanilla **155/170**, S+X **170/170**,
  X+M **100/100**. Gap 8.8 pts, cluster-bootstrap CI [+2.9, +16.5].
- **Rung 3 (GEOS loads it):** Vanilla and S+X are **statistically tied** (133 vs 132 / 170; per-cell 3-run
  figures ~19–24/30). **The schema gap does NOT carry through to loading.** Report this plainly — do not
  let schema validity stand in for execution.
- **Rung 4 (converges):** of decks GEOS accepted on tasks whose reference converges, **31/31 converged.**
  Loading is the binding constraint, not solving.
- **Rung 5 (output fidelity), 489 runs / 18 tasks:** structure predicts fidelity moderately (ρ = 0.31);
  **conditional on running, mean fidelity is 0.958**; roughly half of runs reproduce the reference almost
  exactly. Most of the structure-vs-physics gap is in decks that *fail to run*, not decks that run wrong —
  consistent with the reliability framing.
- **Key honest finding:** `xmllint --schema` (which GEOS docs recommend, and which we built in) is **not**
  equivalent to `geosx --validate-input`; 49 of 180 decks pass xmllint but GEOS refuses them. The gap is
  exactly the cross-reference/arity errors the bottleneck analysis calls unfixed. We swapped in
  `geosx --validate-input` (~2.5 s/deck) and the agent repairs the newly-surfaced defects.

**Part 3 — the future-work framing (researcher-CONFIRMED — use this exact logic).** The message is
positive and forward-leaning, not defensive:
1. **TreeSim's structural comparison is appropriate for the current scope** (translation against a
   hand-validated reference).
2. **We agree** that testing physical plausibility is **crucial for expanding the scope** and is central
   to our future work.
3. So we are **actively looking into, and already have results for, several additional evaluation
   approaches** — physics-weighted TreeSim, an LM-as-a-judge metric, output-side (quantity-of-interest)
   evaluation, and convergence checks — which we can report.
4. **Some of these (notably the LM-as-a-judge) require further domain-expert collaboration, which is
   ongoing.** Frame this as work in progress needing expert-labeled ground truth, not as a failed metric.

Keep it honest within that positive frame: **do NOT claim an execution-level or output-fidelity advantage
between conditions** (neither is detectable, and the reliability claim does not need it), and do not claim
the LM-judge is validated or that it beats TreeSim. "Ongoing domain collaboration" is the honest and
accurate status.

Two tested nulls that *defend* the metric (report as tests, not failures):
- A **section-level semantic LLM judge** (4 judges, other model families, blind, order-swapped) tracks
  fidelity but **no better than plain TreeSim**, and two of four judges ordered conditions differently —
  so we do not offer it as a validated metric.
- **Physics-weighted TreeSim** (physics sections ×2, plumbing ×1, bookkeeping ×0.5) is a **tight null**:
  a physics-selected subset predicts fidelity no better than a random subset (51st percentile), with power
  to detect a 0.034 improvement. So uniform weighting is now a *tested* choice, not an assumed one.

Positive result to carry: independent of condition, the judge indicates **TreeSim understates deck
quality** — ~2/3 of the attribute mismatches it penalizes are judged physically immaterial. Combined with
0.958 output fidelity among running decks, the paper's numbers are conservative, not generous.

### 5b. Reviewer 2 (kEdh) — the reject over writing clarity (researcher-CONFIRMED posture)
**Do NOT concede the writing is bad. Do NOT frame clarity as a weakness at all.** The posture is
confident, not apologetic:
1. **Show where we already explain each flagged item.** For every concept kEdh names (Buckley-Leverett,
   the Resolution-IV factorial design, "deck," the failures-as-zero convention), point to **where in the
   paper it is explained**, and **offer/promise to add further clarification in the revision.** The frame
   is "we do in fact explain X, and we are happy to expand that explanation," never "we accept this is
   badly written." Pasting improved replacement text is fine — as an *offer to add*, not a *confession of
   a defect*. (`responses/v3/kEdh.md` has the replacement text but opens with "We accept this criticism" —
   **drop that concession**; rewrite the framing.)
2. **Reframe against the NeurIPS reject criteria.** The rating-2 rubric is "technical flaws, weak
   evaluation, inadequate reproducibility, novelty." kEdh flags **none** of these — the entire critique is
   presentation. Make this point clearly: the concerns raised do not match the stated grounds for
   rejection, and the strengths section credits the contribution.
3. **Push back firmly on the venue.** The researcher's position: the reviewer is **out of line** on this;
   NeurIPS is a perfectly reasonable venue. Rebut confidently (while staying professional) using NeurIPS
   2026's own **Use-Inspired** contribution-type definition ("The main contribution is in framing or
   designing approaches to meet the needs of a specific real-world application ... often involves engaging
   with domain experts"). Our AI-for-scientific-simulation (geophysics) work fits it squarely, **all three
   reviewers already tagged the paper Use-inspired**, and the AC and other reviewers judged the
   contribution significant. Remember §3.2: **quote the definition, do not link it.** Never mention the
   arXiv rewrite.

### 5c. Other threads (already answered in v3 — carry forward)
- **Scale/seeds:** clarify the benchmark is **27 evaluated GEOS tasks** (17 val + 10 held-out), not 10;
  give uncertainty on existing data; narrow claims to a **hard-tail reliability effect**. OpenFOAM grown
  5→30 with a second native baseline; LAMMPS added as a third simulator. Reliability replicates across all
  three. (OpenFOAM/LAMMPS numbers are the paper's own — see §8; cite as qualitative transfer evidence.)
- **S/X confound (gep1 Q2b):** Resolution-IV separates the main effects; the S×X interaction aliases and
  is answered by a build-up ablation + hook telemetry (the two are substitutes). Numbers in PROVENANCE #5.
- **Prefix bug (gep1 Q2a):** effect bounded at +0.004; Vanilla and SE both attempt zero retrieval calls,
  so the headline contrast is untouched; bias runs *against* us. PROVENANCE #6.
- **Human baseline (all):** concede — relabel "preliminary calibration," drop time-savings language.
- **Claude Code version (nBNe Q3):** **2.1.119** (VERIFIED across 903 init events); concede unpinned
  install, will pin + report container digest.

---

## 6. Response structure — DECIDED (task-file item 1)

The researcher has resolved this. **Reviewers cannot see our Official Comment to the AC**, so we do not
rely on cross-referencing into the AC comment. The layout:

- **AC comment:** carries the **full evaluation discussion.**
- **gep1 (Reviewer 1):** carries the **full evaluation discussion, repeated** (do not tell gep1 to "see
  our comment to the AC" — gep1 cannot see it).
- **nBNe (Reviewer 3):** a **very brief** eval summary (2–4 sentences) plus **"please see our response to
  Reviewer 1"** for the full treatment. (Reviewers *can* see each other's per-review responses in Phase 2,
  so a cross-reference to Reviewer 1's thread is fine; a cross-reference to the AC comment is not.)
- **kEdh (Reviewer 2):** no eval content needed.

So the eval discussion is written twice in full (AC + gep1) and once briefly (nBNe → refer to gep1).
Draft the **AC response first** (`ac_response_outline.md` is the spine; the meta-review is the decision
guide), then reuse/adapt that eval content in gep1.

---

## 7. Style template — the ladir rebuttal

`ladir_rebuttal_iclr.md` is the advisor-approved, successful reference. Structural lessons to copy:
- Opens with **grouped "General Response to Common Weaknesses"** for issues multiple reviewers share,
  then per-reviewer sections that say "Please see the General Response" for shared points and answer the
  rest inline. (Maps directly onto our shared-eval + per-reviewer structure.)
- **Point-by-point**: quote each W#/Q#, then "**Response to W#:**". Do this.
- Cordial, confident, concrete; leads with the strongest evidence; states planned revisions explicitly.
- Note: ladir also has a pointed section challenging two low-quality reviews. Our reviewer-2 handling is
  gentler (cordial reframing against the reject rubric), per the advisor's "acknowledge concern, do not
  concede weakness" guidance — do not copy ladir's confrontational tone wholesale.

**Advisor's writing guidance (from the task file), verbatim intent:**
- Thank the reviewers/AC, be cordial.
- **Do not concede weakness** — acknowledge the concern and provide a clear defense.
- We have clean answers to essentially every concern; the goal is to move scores up and get the AC to
  accept.
- Be concise and easy to read — readability is part of persuasion.
- Minimal em dashes.

---

## 8. Number safety (do not skip)

`sprint/PROVENANCE.md` is the authority. Rules:
- **Held-out numbers are VERIFIED and safe** (`published == strict` on all 180 held-out runs,
  cross-checked by two independent scorers).
- **Validation-set numbers are CONTESTED** — the val scoring pass raced the val campaign (finding F52),
  so published val numbers cannot be reproduced from the decks now on disk. The *convention* analysis
  stands; the *inputs* do not. **Prefer held-out numbers; use val numbers only where PROVENANCE marks the
  specific row VERIFIED** (e.g. the build-up ablation rows #5, prefix probe #6 are VERIFIED).
- **The raw data is NOT on this machine.** `$VAL` / `$HO` (`/data/shared/geophysics_agent_data/...`) and
  the large `sprint/artifacts/` run directories live on the (compromised) lab server only. You **cannot
  re-run or re-derive** anything. Cite only numbers already present as VERIFIED rows in `PROVENANCE.md` /
  `EVAL_WORK_EXPLAINED.md`. If a number you want is not there, flag it for the researcher rather than
  guessing.

### Safe to cite (VERIFIED, each independently derived twice; held-out split verified clean)
- Schema-valid 17-seed: **Vanilla 155/170, S+X 170/170, X+M 100/100**; gap **8.8 pts**, cluster CI
  **[+2.9, +16.5], p=0.0006** (NOT the paper's "20-point / 24-of-30" framing — the paper's 3 seeds were
  the two lowest draws of 17; the honest number is 8.8).
- Loads (`geosx -v -i`, roots): **133/170 vs 132/170, p=1.0, CI [−5.3, +2.9]** — a FIRM measured negative.
- Converges: **31/31**. Validator swap in the loop: **S+X 23→27/30, S+X+M 24→25/30**.
- Output fidelity: **ρ=0.31, n=489, 18 tasks**; **0.958 conditional on running**; not sig. better than
  Vanilla. xmllint ≠ geosx: **49/180** pass xmllint but geosx refuses. Both metric nulls (semantic judge
  ties TreeSim Δρ=−0.040; physics-weighted TreeSim tight null at 51st percentile, min-detectable Δρ=0.034).
- Claude Code version **2.1.119** (903 init events, zero exceptions); unpinned install.
- S/X build-up ablation (val, VERIFIED rows): S **+0.008**, X-on-top **−0.007**, together **+0.000**.
  Prefix-bug bound **+0.004**, Vanilla and SE attempt **0** retrieval calls.

### DO NOT cite / handle with extreme care
- **The "main-effects correction" (R −0.037, S −0.008, X +0.011, M +0.008) — DO NOT volunteer.** The val
  scoring pass raced the val campaign (finding F52), so both the published and the "corrected" main
  effects rest on bad inputs. This flips the earlier plan in the v3/AC_post2 drafts. Held-out is clean, so
  headline claims survive, but the main-effects correction is off the table unless the researcher revives
  it. (Human decision H3 — DECIDED: do not include in v4; camera-ready only.)
- **Cross-model panel figures — do not quote any.** No scored output on disk; traces only to a summary doc.
- **OpenFOAM / LAMMPS numbers ARE citable** — they are the paper's own transfer study, present in
  `writing/arxiv/siga_arxiv_2.tex`: OpenFOAM SIGA best **0.870** (all SIGA cells 30/30 full coverage, 0
  zero-score), Foam-Agent **0.516** (19/30 full, 8 zero-score), MetaOpenFOAM **0.379** (10/30 full, 12
  zero-score), n=30, S effect **+0.168**; LAMMPS judge scores **4.56→7.78** (deepseek backbone) and
  **6.33→6.89** (Claude Sonnet backbone). Present them as **new post-submission transfer evidence** and
  keep the framing **qualitative** (single-run, transfer not a second benchmark). This resolves the old
  "unverified" flag and H1 — the arxiv already adopts the n=30 OpenFOAM numbers, so the n=5→n=30 change is
  settled, not an open reversal. **Anonymity: you may READ `siga_arxiv_2.tex` to source these numbers, but
  never mention, cite, quote verbatim, or link the arxiv version in the rebuttal — it is deanonymized.**
- **Absolute May-campaign numbers** — not reproducible now (86-day model drift, H33). Keep every new
  comparison within-campaign / same-day.
- **Do not claim any execution-level or output-fidelity advantage between conditions** — genuinely negative.

### Two framing notes from the sprint
- The team **dropped the "ladder / rungs" vocabulary** (the ordering is false — GEOS's pugixml accepts
  `--` inside XML comments where xmllint and our scorer reject them, so "well-formed" and "loads" can
  disagree). v3 reframes as **two axes**: (A) the deck as an artifact [structural=TreeSim / semantic=judge];
  (B) what the simulator does [loads / converges / outputs reproduce]. Use the two-axis framing.
- **Exclude the "Vanilla + geosx hook" condition from tables** (researcher instruction): rhetorically it
  strengthens Vanilla's case when the credit belongs to the S setting.

---

## 9. Open human decisions — do NOT resolve these yourself

The v3 drafts contain `[[BLOCKED: human decision H#]]` placeholders. These are calls for the researcher
and advisor (see `MASTER_TODO.md` "Awaiting Lianhui"), not for you. Leave them as clearly-marked
placeholders in v4 and surface them to the researcher:
- **H1** — RESOLVED: the OpenFOAM n=30 numbers are the paper's own (in `siga_arxiv_2.tex`); cite them as
  qualitative transfer evidence, no open reversal to adjudicate. See §8.
- **H2** — how hard to commit, in writing, to the camera-ready clarity rewrite.
- **H3 / H9** — DECIDED (researcher): **do NOT volunteer** the main-effects correction; camera-ready only
  (contested val inputs). Do not include it in v4.
- **H7** — whether to volunteer the Table 5 bottleneck-table error.
- **H10** — how to present the harness fairness bug (missing non-XML assets).

Additional unresolved calls surfaced in the last session's catch-up (treat the same way):
- **H19** — how far to walk back the reliability claim (the headline effect was ~2.3× overstated once
  scored at 17 seeds; the honest story is "fewer failures, not better decks").
- **H22** — whether to volunteer the ρ ≈ 0.31 structure-vs-fidelity correlation.
- **H23** — the stale A2 output-fidelity CSVs need correcting before those numbers are final ("not
  optional," but a data task for the researcher, not you).
- **H30 / H33** — rebuilding the loads-check story cleanly, and the 86-day model-drift confound.

Draft the surrounding text both ways or with the placeholder intact; do not silently pick a side.

### A mandatory mechanical task for v4 (not a judgment call)
**Propagate the corrected overnight numbers into every reviewer response.** Only `responses/v3/01_evaluation.md`
was updated during the sprint. `v3/gep1.md`, `v3/nBNe.md`, and `v3/kEdh.md` **still carry v2 pre-overnight
numbers** ("19/30", "23/30", "experiments ... running now"). The sprint flagged this three times and never
did it. In v4, replace those with the VERIFIED numbers in §8 (155/170 17-seed, loads 133/170 vs 132/170,
validator swap 23→27, etc.), and delete "running now" language — the runs are done.

---

## 10. Suggested workflow for your session

1. Read the files in §1 order. The outlines in `V4_OUTLINES.md` are your section-by-section plan; follow
   them.
2. **Draft the AC response first** from `ac_response_outline.md` (see the AC notes in `V4_OUTLINES.md`),
   brief and readable, hitting the four meta-review bullets in the AC's order (structural eval → clarity →
   scale → human baseline) plus the reviewer-2 venue/criteria point. Keep the highest-risk bullet
   (structural eval) honest: schema validity is the artifact axis, not the simulator axis; do not let it
   read as "we did the execution study and won." Report the loads negative plainly.
3. Draft **gep1 (Reviewer 1)** carrying the full eval work; **nBNe (Reviewer 3)** pointing to it +
   answering its specific asks; **kEdh (Reviewer 2)** on the clarity + reject-criteria + venue reframe.
   Use the per-reviewer outlines in `V4_OUTLINES.md`.
4. Enforce the constraints in §3 on every draft (10k char cap, no links, no arXiv mention, no em dashes,
   VERIFIED numbers only) and do the mandatory stale-number propagation (§9).
5. Keep the `[[BLOCKED: H#]]` placeholders only for the still-open decisions; write a short "Decisions
   needed from you" summary at the end for the researcher (H2, H7, H10, H19, H22, H23). Already decided —
   bake in, no placeholder: A1 structure, A2 clarity posture, A3 venue, H1 OpenFOAM (cite), H3 main-effects
   (omit).
6. Write v4 into a new `responses/v4/` folder (mirror the v3 filenames: `AC.md`, `gep1.md`, `kEdh.md`,
   `nBNe.md`, plus a companion `*_post2.md` if a response overflows 10k chars).

---

## 11. Do we need more experiments? (the question the researcher flagged)

**No. This was settled explicitly, and no experiment is possible anyway.** The most recent sprint session
(log `c60e6d98`, Jul 28) ends with exactly this exchange: the researcher reported the server was
compromised, said he had **invalidated the API keys so no more experiments can run**, and asked directly
"do we have all the results we need for the rebuttal? Are we good on results and can focus on just writing
now?" The answer was **"Yes, you're set on results. Nothing left that an experiment would fix,"** noting
that the two metric nulls that came back overnight (semantic judge ties TreeSim; physics-weighted TreeSim
null) **defend TreeSim better than shipping them would have.** The session then moved to v4 and was
interrupted at a `/login` before drafting anything, which is why **no `v4/` folder exists yet.**

So: v4 is a **writing-and-framing pass over already-verified results.** Do not wait on, plan, or promise
any experiment. `MASTER_TODO.md` frames any further evidence (more OpenFOAM seeds, LAMMPS scale-up, extra
QoI comparisons) as **"pure upside, post it if it lands, never promise a delivery date"** — and with the
keys dead and the server down, none of it is landing before the Aug 3 deadline anyway. If new numbers ever
do arrive, they go out as **follow-up Official Comments**, never folded into v4 as load-bearing claims.
