# REBUTTAL_MERGE_RECOMMENDATION

Companion documents: `VERSION_DIFF_REPORT.md` (what changed), `ARXIV_VS_REVIEWS.md` (what it buys against the reviews).

---

## Recommendation

**Selective port. Do not submit the arXiv PDF as the revised NeurIPS PDF.**

Take the arXiv version's *writing* almost wholesale, take its OpenFOAM experiment, take every numeric correction, **restore** the things it deleted, keep LAMMPS out of the main body, and **revert the title**.

Concretely: build the revised PDF from `siga_arxiv_2.tex` as the base — it is the better-written document and it is the same `neurips_2026.sty` with one option flipped — then apply a defined set of reverts and additions. Do not build from `neurips/neurips_2026.tex`; you would be re-doing a rewrite that already exists.

### Why not wholesale

Five reasons, in descending order of how hard they bite.

1. **It does not fit.** The NeurIPS main-body limit is 9 pages. A's main body ends on p9 (References start p10). B's main body ends on p12 (References start p13). **B is three pages over.** This is not negotiable and it is not a formatting nit — a revised PDF that blows the page limit is a desk-level problem, and "we needed 12 pages" reads as scope creep. Three pages must come out regardless of every other consideration.

2. **The title change is a real bait-and-switch risk, and it is gratuitous.** All three reviewers refer to the system as SIGA; two of them spell out "Simulator-Interface Grounding Adapter" in their summaries. B's title — *Auto-Configuring Scientific Simulators with Lightweight Coding-Agent Adapters* — drops "SIGA" entirely. A reviewer opening the revised PDF and not finding the paper they reviewed is the fastest possible way to trigger "this is a different submission."

3. **B is de-anonymized.** `\usepackage[preprint]{neurips_2026}` plus five named UCSD authors on p1. The revised PDF must be anonymous. This is trivially fixable (one option, one author block) but it must not be missed, and it is a reminder that B was built for a different venue with different rules.

4. **B deletes disclosures that a reviewer asked about by name.** The native-plugin-prefix bug is gone from B. gep1 raised it as a score-moving question. Submitting a revision in which the thing you were asked about has silently vanished is the worst available response — it converts a fixable methodological question into a credibility question.

5. **B adds a whole third simulator whose evidence quality is the weakest in the paper.** LAMMPS is n=1, has no native baseline, and is judged by an LLM that is one of the two backbones being scored. Putting it in the abstract and contributions of a rebuttal PDF invites exactly the "this is a new paper" reaction — *and* the new material is the material least able to survive scrutiny. Nine tasks of single-run LLM-judged text similarity is not what buys you a reject-to-accept flip; it is what buys you a fourth reviewer complaint.

### Why not stay with the NeurIPS version either

Because the AC and kEdh both asked for a clarity overhaul and that overhaul **already exists, finished, compiled, and public**. Refusing to use it would be spending rebuttal days rewriting text that is written. And because A contains at least five verifiably wrong numbers (see `VERSION_DIFF_REPORT.md` §4, rows 2–8) that B already fixes; leaving them in a revised PDF is indefensible now that you know.

---

## Port list

Ranked by (score impact) ÷ (effort). Effort is wall-clock for one person, assuming they can edit LaTeX and have the repo.

### Tier 1 — mandatory, do these first

| # | Change | Verdict | Rationale | Effort |
|---|---|---|---|---|
| 1 | **Re-anonymize**: `\usepackage[preprint]{neurips_2026}` → `\usepackage{neurips_2026}`; restore `\author{Anonymous Authors}` | **PORT (revert)** | Anonymity requirement. Also restores line numbers. B already anonymizes the named GEOS developer, so no other de-anon pass is needed. | 5 min |
| 2 | **Revert the title** to A's: *Simulator-Interface Grounding Adapters for Scientific Simulation Setup* | **PORT (revert)** | See "Should the title revert?" below. | 5 min |
| 3 | **All numeric corrections**: Res-IV main effects (R −0.037, S −0.008, X +0.011, M +0.008), harness-less +0.488, 46→45 split, browser-history table sums, `yue2025foamagent` year | **PORT** | These are corrections of *errors in the submitted paper*. I re-derived the main effects and the +0.488 independently from tables that are identical in both versions — A is wrong, B is right. Not porting these means knowingly resubmitting wrong arithmetic. | 20 min (already in B) |
| 4 | **40× → 16×** reliability claim, everywhere | **PORT** | A's 40× uses the tightest cell (S+X σ=0.002); 16× uses X+M (σ=0.005). Both are real table entries; 40× is a cherry-pick. Moderating it is also literally what the AC asked for ("moderate the robustness and generalization claims"). **Fix B's residual sloppiness while you are here**: B's abstract pairs "0.720 → 0.789" (the SE cell, σ=0.012 → 6.75×) with "about 16×" (the X+M cell). Quote one cell or say "up to 16× depending on cell". | 15 min |
| 5 | **Drop the "16% fewer tool calls" claim**, replace with B's corrected two-sided statement | **PORT** | A's abstract claim is contradicted by A's own efficiency table (SE uses *more* tool calls on held-out: 97.4 vs 90.5). B already corrects it. | in B |
| 6 | **Restore Limitations to the main body** as a titled subsection of Discussion | **DO NOT PORT B's move to appendix — revert** | gep1 explicitly asked for a stronger limitations statement; burying it answers the opposite of the question. NeurIPS also expects main-body limitations. Use B's *content* (which is better — it adds the two-task concentration, human n=2, and the LLM-simulator-supervisor admissions) in A's *location*. | 30 min |
| 7 | **Add gep1's requested sentence verbatim in spirit**: "the current evidence supports structural authoring reliability, not validated simulator correctness" | **NEW (not in either version)** | gep1 named this. It is one sentence and it is free. Put it as the lead sentence of Limitations. | 10 min |
| 8 | **Restore the native-plugin-prefix bug disclosure**, and add one sentence saying the affected estimates were recomputed and the ranking is unchanged | **DO NOT PORT B's deletion — revert and strengthen** | gep1, score-moving. You have the *good* version of this answer available: the corrected main effects. Frame it as "we recomputed; R is −0.037 not −0.032; X+M-vs-Vanilla is unaffected since both are R⁻". Turning a deleted disclosure into a demonstrated fix is the single best effort:impact trade on this list. | 45 min |
| 9 | **Report the exact Claude Code version** (and the `claude-code` CLI build used for each campaign) | **NEW** | nBNe asked directly. One sentence in Evaluation setup + one line in the implementation appendix. Zero risk. If different campaigns used different builds, say so — that is a limitation, not a disqualifier. | 20 min (assuming the version is recoverable from logs) |

### Tier 2 — high value, port with edits

| # | Change | Verdict | Rationale | Effort |
|---|---|---|---|---|
| 10 | **The entire clarity rewrite**: new abstract, new intro, restructured Method (three-interface formalism), Experiments section with five RQs, `rqanswer` boxes, in-line TreeSim equation, TreeSim appendix | **PORT** | This is the substance of the response to kEdh and to the AC's second bullet. ~70% of kEdh's burden. It is already written and compiled. | already done; ~2h to reconcile with the reverts |
| 11 | **OpenFOAM 30-task study + MetaOpenFOAM baseline** | **PORT, with an explicit note** | Directly answers gep1 Q3 and the AC's scale bullet, 6× scale-up. **But** you must state plainly in the rebuttal text and in the paper that the 30-task run supersedes the 5-task run and that the within-SIGA coverage contrast does not survive at scale. Do not quietly swap the table. Reviewers who diff will find it; owning it reads as rigor, hiding it reads as the opposite. | in B; +1h for the superseding note |
| 12 | **Cost accounting table columns** (SIGA $23.20 vs Foam-Agent $0.30 / MetaOpenFOAM $0.17) | **PORT** | Unflattering but pre-empts an obvious question and demonstrates instrumentation discipline. Pair it with the honest reading: SIGA buys coverage with context length. | in B |
| 13 | **Method figure (Fig. 2) redraw** — port B's new figure but **regenerate the asset** to remove the "simulation outputs / post-process artifacts" elements | **PORT-WITH-EDITS** | B's caption and abstraction are much better. But the image depicts execution outputs for decks that are never executed. With the AC's primary objection being exactly "you never execute", shipping a figure that implies you do is a self-inflicted wound. This is logged as a known unfixed issue in the project's own changelist. | 2–3h (needs the figure source) |
| 14 | **Fig. 1**: keep **A's** caption structure (labelled manual-vs-SIGA panels), with B's image if it is clearer | **PORT-WITH-EDITS (revert caption)** | B's caption is a descriptive gloss and is *less* helpful than A's for a reviewer who complained about comprehensibility. | 30 min |
| 15 | **Human-baseline reframing** (Expert 1/2, protocol detail about the 10-min setup, caveats promoted, expertise honestly described) | **PORT** | Answers gep1 Q4 ("reframe more conservatively"). | in B |
| 16 | **Explain Expert 1's 0.812 → 0.689 file-level regression** | **NEW** | Present in both versions, unexplained in both, rated blocking by the project's own internal review. A human getting *worse* after 3× the time is exactly what a careful reviewer will notice. Even "the extended session restructured the deck across two files, so the base.xml comparison changed" is enough — but say something. | 30 min |
| 17 | **Restore the Future-work appendix**, in particular the execution-correctness ladder item | **DO NOT PORT B's `\iffalse` — revert** | It was in the submitted PDF. Removing it makes the paper look *less* aware of its central gap. Restoring it, and better still converting it from "future work" to "done, see App. X" (item 20 below), is the honest path. | 15 min |
| 18 | **Two new limitation admissions from B** (held-out lift concentrated in two tasks; the autonomy "supervisor" was an LLM simulator, not a human) | **PORT** | Genuinely more honest than A. Cheap credibility. | in B |
| 19 | **Related-work upgrade** (harness-as-code / meta-harness positioning, `lewis2021rag`, MetaOpenFOAM, `kim2024mdagents` removal) | **PORT** | Helps the venue-fit argument against kEdh. The `kim2024mdagents` removal is a factual correction (MDAgents is medical). Also reconcile the two coexisting LAMMPS bib keys (`holbrook2026lammps` and `LAMMPS`) if LAMMPS is cited at all. | in B; 15 min for the bib key |

### Tier 3 — the thing that actually moves the score, and it is in neither version

| # | Change | Verdict | Rationale | Effort |
|---|---|---|---|---|
| 20 | **Run the execution ladder.** A's own future-work sized it: *"5 tasks × 2 cells × 1 run"* through actual GEOS execution. | **NEW — highest priority of anything on this page** | This is gep1's stated score-moving condition, nBNe's question 1, and the AC's primary bullet and stated decision criterion. Nothing else on this list changes the AC's arithmetic. Even a small, honest ladder — *parses / schema-validates / GEOS accepts the deck and initializes / GEOS completes N timesteps* — converts "structural only" into "structural plus a runnability floor". Report it as a ladder with counts, not as a new headline metric. | 1–3 days incl. GEOS environment setup; the ladder itself was self-estimated as small |

### Tier 4 — do not port into the main body

| # | Change | Verdict | Rationale |
|---|---|---|---|
| 21 | **LAMMPS in the abstract, intro, contributions, and Results** | **DO NOT PORT to main body — appendix only, flagged preliminary** | Three problems compound: (a) it is the "new paper" trigger; (b) it is the weakest evidence in the document — 9 tasks, n=1, no native baseline, and the LLM judge (Claude Sonnet 4.6) is *one of the two backbones it scores*, which is a self-preference confound the paper notes as a fact but never treats as a threat; (c) the "M dominates (+2.13)" claim is not separable from "any adapter beats vanilla", because M appears in 5 of the 6 cells and is absent only from Vanilla — I checked the arithmetic and the M "main effect" is numerically identical to the adapter-vs-vanilla contrast. **Also: no LAMMPS artifacts exist anywhere in this repo** — no task specs, ground truths, results, runner, or validator, and no `repo3_lammps` sibling. You cannot currently audit or reproduce it in a rebuttal timeframe. Put it in an appendix as preliminary transfer evidence, mention it in one Discussion sentence, and keep it out of the claims. |
| 22 | **The title change** | **DO NOT PORT** | See below. |
| 23 | **De-anonymization** | **DO NOT PORT** | Obvious. |
| 24 | **Deletion of the ChatGPT-navigation disclosure** from the human-baseline appendix | **DO NOT PORT — restore A's paragraph** | A disclosed it and argued it was immaterial. Removing a disclosure while keeping the score it qualifies is the wrong direction, especially in a revision. Restoring it costs one paragraph and buys the "these authors disclose things" impression that materially helps everywhere else. |
| 25 | **Deletion of the 0.898 seven-task control** ("the remaining seven held-out-eval tasks have a Vanilla mean of 0.898, indistinguishable from val's 0.910") | **DO NOT PORT — restore** | It is the strongest evidence that the authors understand their own effect is tail-localized. gep1 praised exactly this kind of self-limiting framing. B replaced it with vaguer prose. |
| 26 | **Removal of "harm-reduction regime, not a correctness regime"** and similar blunt framings | **DO NOT PORT — restore at least one** | gep1's review singles out this honesty as a strength: *"The paper is careful in explaining that the adapter mainly prevents catastrophic failures rather than improving the ceiling. This distinction is important and makes the contribution more credible."* B's tone pass sanded it off. For a NeurIPS rebuttal, put it back. |
| 27 | **Deletion of the `Cell definitions` appendix (`tab:cells`)** | **NEUTRAL — do not port back** | B's component-indicator columns in Table 1 genuinely subsume it and save space, which you need. |
| 28 | **Renaming "seeds" → "runs"** | **PORT, but explain it once** | The rationale is correct (no RNG seed is set; these are temperature-sampling repeats) and it is more honest. But changing the word for the exact quantity three reviewers criticized, without comment, looks evasive. Add a half-sentence in Evaluation setup: "we write *runs* rather than *seeds* because no RNG seed is fixed; each run is an independent sample at the harness's default sampling settings." |

---

## Should the title revert to the NeurIPS one, or adopt the arXiv one?

**Revert to the NeurIPS title.** Not a close call.

- All three reviewers and the AC discuss the paper as **SIGA**. gep1 and nBNe both expand the acronym in their summaries. Removing the acronym from the title of the revised PDF is a gratuitous discontinuity at exactly the moment you need the reviewer to recognise the paper.
- The arXiv title (*Auto-Configuring Scientific Simulators with Lightweight Coding-Agent Adapters*) is arguably a *better* title in the abstract — it is plainer, which serves kEdh's complaint — but it is also a *systems/application* title, which cuts against the venue-fit argument you need to win with kEdh. The NeurIPS title at least contains "Grounding Adapters", which is the method-shaped framing.
- The change history is itself a liability: the title moved twice in seven weeks (A → *SIGA: Self-Evolving Coding-Agent Adapters for Scientific Simulation* → B). Locking to the reviewed title removes the question.
- If you want a clarity gain in the title, make a *minimal* edit rather than a replacement, e.g. drop the colon-subtitle: **"Simulator-Interface Grounding Adapters for Scientific Simulation Setup"**. Keep the acronym. Do not drop "SIGA".

One caveat to flag to the authors: **the arXiv preprint is public, de-anonymized, and carries a different title.** Whatever the merge decision, check the venue's preprint policy and whether the arXiv posting date creates any dual-submission or anonymity-period issue independent of the revised PDF. That is a policy question for the authors, not something the diff can settle — but it should be checked before anything else, because if the preprint is already a problem, the merge plan changes.

---

## Risks and mitigations

| Risk | Severity | Mitigation |
|---|---|---|
| **"This is effectively a new paper."** Only ~12% of A's main-body sentences survive into B verbatim. Even a selective port is a heavy rewrite. | High | (a) Keep the title, the section skeleton, and Table 1 identical to the reviewed version — those are the recognition anchors. (b) Open the rebuttal with a short "what changed and why" table mapping each change to the reviewer who asked for it. Changes traceable to a review read as responsiveness; untraceable changes read as a new submission. (c) Do **not** add LAMMPS to the claims. |
| **Reviewers diff the OpenFOAM tables and find the result reversed.** Vanilla 3/5 → 30/30; S effect halved; M flips sign. | High | State it first, in your own words: "at n=5 the coverage contrast appeared within SIGA; at n=30 it does not — every SIGA cell holds full coverage and the contrast is against the native agents. We report the 30-task run as superseding." This is a rigor win if you say it and a credibility loss if they find it. |
| **The prefix-bug disclosure looks deleted.** | High | Restore it *and* show the recomputation. Say explicitly: R's val main effect is −0.037 (not the −0.032/−0.033 reported in the submission, which did not reconcile with our own Table 1); the X+M-vs-Vanilla ranking is unchanged because both cells are R⁻. |
| **Five wrong numbers in the submitted PDF become visible once you correct them.** | Medium | Corrections in a revision are normal and expected. Group them in one "Corrections" paragraph in the rebuttal rather than scattering them. Do not draw a distinction between "typo" and "arithmetic error" — just list them. |
| **nBNe (the accept) drifts down.** They praised cross-simulator transfer and the human baseline; the OpenFOAM reversal weakens the first, and the "grad-level geoscientists" downgrade weakens the second. | Medium | Address nBNe's three questions directly (Claude Code version is free; convergence/validation is item 20; expertise levels should be conceded explicitly as a limitation with a concrete plan). Frame the OpenFOAM scale-up as *strengthening* the transfer claim — 30 tasks and two native baselines is more transfer evidence, not less, even though the mechanism story changed. |
| **Page limit.** B is 3 pp over 9. | High | Cut from B, in this order: (a) LAMMPS → appendix (~0.9 pp); (b) compress the Method formalism — keep Eq. `adapter`, move the derivation of Eq. `selfevolve` to an appendix (~0.7 pp); (c) trim the `rqanswer` boxes to two lines each (~0.4 pp); (d) move the in-line TreeSim equation's surrounding prose to the TreeSim appendix, keeping only the equation (~0.5 pp); (e) compress the OpenFOAM main-text table to the top 5 SIGA cells + 2 natives with the full table in the appendix (~0.5 pp). That is ~3 pp without touching the intro or the results narrative. |
| **Adding a whole new simulator mid-rebuttal.** | Medium | Handled by keeping LAMMPS in the appendix and out of the abstract/contributions. If asked, describe it as "a preliminary port we ran after submission; we include it because it *complicates* rather than confirms our transfer story — the dominant component shifts". That framing is defensible and interesting; "we added a third simulator to show generality" is not, at n=1. |
| **The execution ladder fails** — decks that score 0.8 on TreeSim don't run. | Medium | This is the correct outcome to report if it happens, and it is *still* better than silence. A ladder showing "9/10 parse, 7/10 schema-validate, 4/10 initialize, 2/10 complete 10 timesteps, and SIGA beats Vanilla at every rung" is a strong result. A ladder showing SIGA and Vanilla are equal at every rung is a real finding that should change the paper's claims — and finding it yourself in the rebuttal is far better than a reviewer inferring it. Budget for either outcome and pre-write both framings. |
| **Fig. 2 depicts execution.** | Medium | Regenerate before submitting. Under an AC bullet that says "you never execute", this is the one figure a reviewer will stare at. |

---

## Updated Triage (grounded on latest arXiv version)

**Note on `REBUTTAL_TRIAGE_v1.md`:** that file did not exist at the time of writing (checked twice; only `siga_neurips_review.md`, `siga_neurips_reviews_clean.md`, and my two companion docs are present in `/home/matt/sci/repo3/`). The differences I would expect against a NeurIPS-grounded triage are called out inline as **[already solved in arXiv]** — those are the items a submission-grounded plan would list as work and which the arXiv version has already discharged. If that file lands later, the items flagged below are the ones to strike from it.

Baseline assumption: the starting point is `siga_arxiv_2.tex`, with the Tier-1 reverts from the port list applied.

### (0) Already done — strike these from any submission-grounded plan

| Item a NeurIPS-grounded triage would list | Status |
|---|---|
| Rewrite the paper for a general NeurIPS audience | **[already solved in arXiv]** — main body is ~88% new text |
| Define TreeSim formally | **[already solved]** — Eq. in main text + full appendix |
| Explain the Resolution-IV design in plain language | **[already solved]** — motivated before it is named |
| Justify failures-as-zero | **[already solved]** — one added sentence |
| Introduce "deck" early | **[already solved]** — first sentence of the abstract |
| Scale OpenFOAM beyond 5 tasks | **[already solved]** — 30 tasks |
| Add a second OpenFOAM-native baseline | **[already solved]** — MetaOpenFOAM |
| Moderate the 40× variance claim | **[already solved]** — 16× (needs one internal-consistency fix) |
| Fix the SE "16% fewer tool calls" overclaim | **[already solved]** |
| Fix the Resolution-IV main effects / harness-less delta / split arithmetic | **[already solved]** |
| Reframe the human baseline conservatively | **[already solved]** |
| Add the "supervisor was an LLM, not a human" limitation | **[already solved]** |
| Position against harness-optimization literature (venue fit) | **[already solved]** |

That is a substantial fraction of any submission-grounded plan, and it is free.

### (a) Low-hanging fruit — hours

Ranked by score impact per unit effort.

| Rank | Item | Effort | Who it answers | Why it ranks here |
|---|---|---|---|---|
| 1 | **Report the exact Claude Code version** (per campaign if they differ) | 20 min | nBNe Q3 | Literally one sentence for a named reviewer request. Nothing on this list has a better ratio. |
| 2 | **Restore the native-plugin-prefix disclosure + state the recomputation** | 45 min | gep1 Q2 (score-moving) | Converts a deleted disclosure into a demonstrated fix. Half of a score-moving question answered for under an hour. |
| 3 | **Move Limitations back to the main body + add gep1's exact sentence** ("structural authoring reliability, not validated simulator correctness") | 40 min | gep1 limitations, AC | Named request, trivially satisfiable, and NeurIPS expects main-body limitations. |
| 4 | **Re-anonymize + revert title** | 10 min | all | Prerequisite. |
| 5 | **Fix the abstract's 16× / 0.789 cell mismatch** | 15 min | gep1, AC | B's abstract pairs the SE mean with the X+M σ ratio. A reviewer recomputing from Table 1 will get 6.75× for SE. Quote one cell. |
| 6 | **Explain Expert 1's 0.812 → 0.689 file-level drop** | 30 min | gep1/nBNe human baseline | Unexplained in both versions and rated blocking by the project's own review. Someone will ask. |
| 7 | **Restore the Future-work appendix incl. the execution ladder** | 15 min | AC | Makes the paper look aware of its own central gap rather than silent on it. |
| 8 | **Restore the 0.898 seven-task control and one "harm-reduction, not correctness" framing sentence** | 20 min | gep1 | gep1 explicitly praised this honesty; B sanded it off. |
| 9 | **Restore the ChatGPT-navigation disclosure** | 15 min | integrity | Cheap, and it is the kind of thing that, if noticed as removed, is very expensive. |
| 10 | **Add the "runs not seeds" explanatory half-sentence** | 10 min | gep1/nBNe/AC | Prevents the rename from reading as evasion. |
| 11 | **Reconcile the two LAMMPS bib keys; fix `tab:bottleneck` n=29–30 vs n=30 caption** | 15 min | hygiene | Free. |
| 12 | **Page-limit surgery to 9 pp** (per the mitigation plan above) | 3–4 h | mandatory | Not optional; scheduled here because it is mechanical. |

Total tier (a): **roughly one working day.** It discharges every cheap named request and repairs every regression B introduced.

### (b) Real new experiments — days

| Rank | Item | Effort | Who it answers | Notes |
|---|---|---|---|---|
| 1 | **GEOS execution / runnability ladder.** 5 held-out tasks × {Vanilla, best SIGA cell} × existing decks, scored as a ladder: parses → schema-validates → GEOS initializes → GEOS completes N timesteps. Report counts, not a new headline metric. | **1–3 days** (dominated by getting a GEOS build running; the scoring itself is small — the project's own future-work sized it at "5 tasks × 2 cells × 1 run") | gep1 Q1 **(score-moving)**, nBNe Q1, **AC primary** | **This is the single highest-value item in the entire triage and it is the only one that addresses the AC's stated decision criterion.** It can reuse decks already generated — no re-running of the agent is required, which is why it is days and not weeks. Pre-write both the positive and the null framing. |
| 2 | **S/X isolation cell.** Add one cell that separates hook-time validation from agent-callable validation at matched validation strength (e.g. S-with-parse-check-only vs S-with-xmllint), n=3 on held-out-eval. | **~1 day** (low API spend on `deepseek-v4-flash`; the factorial infrastructure exists) | gep1 Q2 **(score-moving)** | Completes the other half of gep1's second score-moving question. gep1's bar is explicit: "my confidence would increase if the stop-hook effect remains dominant after removing this confound." |
| 3 | **Clean multi-run rerun of the affected factorial cells** with the prefix-gate fix in place | **~2 h wall-clock** (self-estimated in A's future-work as ~1.5 h, low spend) | gep1 Q2 | Cheap. Pair with item (a)2. Do it if the ladder is not consuming all available machine time. |
| 4 | **Human baseline: one additional participant at a different expertise level**, ideally one experienced GEOS user, on the same task | **1–2 days** incl. recruiting | nBNe Q2, gep1 Q4, AC | Realistically hard inside a rebuttal window. nBNe asked for "different levels of GEOS user experience"; even n=3 with one experienced user changes the claim from anecdote to a two-point curve. Attempt only if the ladder is done. |
| 5 | **OpenFOAM multi-run** (n=3 on the 30-task benchmark) | **~1 day** compute | gep1 Q3 | gep1 asked for "more tasks, multiple seeds, **or** a fuller Foam-Agent execute-mode comparison" — the first is delivered, so this is a bonus rather than a requirement. Low priority. |
| 6 | **Regenerate Figure 2** without the execution imagery | **2–3 h** | AC | Listed here rather than in (a) because it needs the figure source, not just LaTeX. |

**If only one thing can be done: item (b)1.** Nothing else changes the AC's arithmetic. The AC's decision sentence is a conjunction — executable/valid simulations **and** clarity — and the arXiv rewrite has already delivered the clarity conjunct for free.

### (c) Must-concede

State these plainly rather than defending them. Conceded limitations that are named and scoped cost far less than limitations a reviewer discovers.

| Item | How to concede |
|---|---|
| **GEOS core scale: 10 held-out tasks, 3 runs, one backbone.** No realistic rebuttal-window fix. | Concede as scope. Report per-task variance, be explicit that the held-out lift is concentrated in two of ten tasks (B already says this), and restate the claim as "reliability on a hard tail of compound multiphysics tasks", not "improves GEOS deck authoring". |
| **Human baseline n=2 on one task** (unless (b)4 lands). | Concede as calibration, never as a comparison. B's framing is already right; keep it and say "anecdotal calibration" in the reviewers' own words. |
| **LAMMPS is n=1, LLM-judged, judge-is-backbone, and has no native baseline.** | Concede fully, put it in an appendix, and be the one to name the self-preference confound before a reviewer does. Do not let it appear in the abstract or contributions. |
| **OpenFOAM native baselines remain lint-only**; execute mode does not run in the environment. | Both versions already concede this. Keep the concession verbatim and add that the comparison is therefore a lower bound on the native agents. |
| **S/X remain partially confounded** if (b)2 does not land. | Concede and scope the claim to "validator-driven self-refinement (S and X jointly)" rather than attributing the effect to the stop hook specifically. |
| **The self-evolution pipeline is underspecified.** An appendix documenting it was written and then reverted; the reproducibility gap is real and was flagged internally as one of the two biggest. | Either restore the appendix (it exists in the Jun-8 source) or drop SE from the contributions. Do not keep a headline SE claim with no reproducible pipeline. |
| **Venue fit (kEdh).** | Not conceded — argued, once, briefly, using the harness-adaptation framing and the interface-dependence finding. Do not spend more than a paragraph; it is the AC's call, not the reviewer's. |

### Where this triage differs most from a submission-grounded one

Three structural differences, in case a `REBUTTAL_TRIAGE_v1.md` appears later:

1. **The entire "rewrite the paper" workstream is gone.** A submission-grounded plan would put "significant efforts towards improving clarity" (the AC's words) at or near the top, sized in days. It is done. That freed capacity should go to (b)1.
2. **The OpenFOAM workstream is gone, and partially inverted.** A submission-grounded plan would list "scale OpenFOAM" as a multi-day item. It is done — but it produced a *result change* that a submission-grounded plan would not anticipate, and handling that change honestly is now itself a work item (port-list #11).
3. **Three new repair items exist that a submission-grounded plan would never contain**, because they are regressions introduced *by* the arXiv version: restore the prefix-bug disclosure, restore Limitations to the main body, restore the future-work/execution-ladder item. Anyone working from the NeurIPS submission would not know these were at risk.
