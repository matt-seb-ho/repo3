# ARXIV_VS_REVIEWS — does swapping in the arXiv version discharge the reviewer burden?

Sources: reviews at `/home/matt/sci/repo3/siga_neurips_reviews_clean.md`; A = `writing/neurips/neurips_2026.tex` (submitted); B = `writing/arxiv/siga_arxiv_2.tex` (Jun 25 arXiv).

Verdict up front: **B discharges roughly 40–45% of the aggregate reviewer burden, almost all of it concentrated on kEdh's clarity complaint. It does essentially nothing for the AC's primary objection.** Two of gep1's three score-moving items are unaddressed, and one of them — the native-plugin-prefix bug — is in a *worse* state in B than in A.

---

## Issue-by-issue

### 1. Execution / physics validity beyond TreeSim — gep1 (score-moving), nBNe, AC (**primary**)

**Status: NOT ADDRESSED. Arguably made worse in presentation.**

There is **no execution-based or physics-validity evidence anywhere in B**, for any of the three simulators. I searched the full source for `execut|runnab|converg|physical valid|smoke ?test|solver run`; every hit is either the word "solver" as simulator vocabulary, "executable interface/contract" used rhetorically, or the harness "executing a rollout".

B concedes it, at `siga_arxiv_2.tex:749` (in the **appendix**):
> "TreeSim is structural, not physical: a $0.8$ deck is not guaranteed to run."

That is the same sentence as A's, at `neurips_2026.tex:272` — except in A it was in the **main body**.

The OpenFOAM native baselines are still lint-only, for the same reason, in both versions (`siga_arxiv_2.tex:665`):
> "the stable comparison available in our environment used `execution_mode=lint_only`, since **execute-mode runs failed to yield usable benchmark outputs**."

And LAMMPS is explicit (`siga_arxiv_2.tex:696`):
> "Each task provides a detailed natural-language specification; **the agent writes the input script without executing LAMMPS.**"

**The critical point the author must not blur:** *LAMMPS adds a third simulator, which answers "does this generalize?". It does not answer "do the decks run?".* These are different reviewer asks and B only touches the first. In fact LAMMPS is the *least* execution-grounded study in the paper — its structural stage is a regex pass-rate (≥0.976, near-ceiling, therefore non-discriminating) and its discriminating stage is a single-pass LLM judge that is itself one of the two backbones being scored. Presenting LAMMPS as a response to the AC's ask would be a misread that a competent reviewer will catch and punish.

**Made worse in two respects:**
- A's Future-work appendix contained a concrete plan — *"**Execution-correctness ladder.** Run a sample of agent-produced decks through actual GEOS execution… Even a small panel (5 tasks × 2 cells × 1 seed) would convert the structural-similarity metric into a ladder"* — and it is in the submitted PDF. In B it is wrapped in `\iffalse…\fi` at `siga_arxiv_2.tex:757-772` and **does not appear in the arXiv PDF** (verified: 1 hit in `siga_neurips_init_sub.pdf`, 0 in `siga_arxiv_2.pdf`). B therefore looks *less* aware of the gap than A did.
- The word "executable" was deliberately struck from the failures-as-zero justification: A's *"the returned workspace is **executable** or at least structurally inspectable"* → B's *"…is at least structurally inspectable"*.
- Figure 2 in B still depicts "simulation outputs" / "post-process artifacts" for decks that are never executed — a known, logged, unfixed issue.

### 2. Writing clarity / jargon for a general NeurIPS audience — kEdh (**primary**), AC

**Status: LARGELY FIXED. This is where B earns its keep.**

Evidence:
- **The main body is a rewrite, not an edit**: only 20 of A's 163 main-body sentences survive verbatim into B's 248 (~12%).
- **Abstract fully de-jargoned.** A's opened on "Frontier LLMs are increasingly capable of expert-level scientific reasoning" and named Resolution-IV, TreeSim, `consult_supervisor`. B opens (`:98`): *"Configuring an advanced scientific simulator, translating a modeling goal into a valid, runnable input deck, is a persistent bottleneck that costs domain scientists hours to days."* **"Input deck" is defined in the first sentence** — directly answering kEdh's complaint that "deck" arrives too late.
- **kEdh's item 1 (explain Resolution-IV):** B now motivates it in plain prose before naming it (`:289`): *"A standard one-factor-at-a-time ablation … cannot disambiguate main effects from two-factor interactions: if R and S help only when combined, neither single-factor ablation reveals this. The full $2^4 = 16$-cell factorial does, at the cost of substantially more runs. We instead use a Resolution-IV $2^{4-1}$ fraction…"* A gave the reader only the term.
- **kEdh's item 2 (the failures-as-zero sentence):** retained but now justified (`:339`): *"This convention is important because simulator setup is only useful when the returned workspace is at least structurally inspectable."*
- **kEdh's item 2 (the "strictly perfect decks" sentence):** the blunt A framing *"The harness operates in a harm-reduction regime, not a correctness regime"* was removed; the finding is now contextualised with two explanatory paragraphs (`:399`).
- **TreeSim is now formally defined** — main-text Eq. (`:325`) plus a full appendix (`:774`). A had no definition anywhere. This was also flagged internally as "the biggest reproducibility omission".
- **Five explicit RQs** (`:250-253`) plus a boxed `rqanswer` after each results subsection — a large readability win for a reviewer skimming.
- **Method restructured** from a formalism-then-repeat layout into three single-pass subsections with a clean three-interface abstraction ($c_0$, $\mathcal{T}_0$, $\mathrm{stop}_0$).
- **Related work** now positions the contribution against a named subfield (harness-as-code / meta-harness) instead of listing papers.

**Not fixed:**
- **kEdh's item 1, second half:** `buckleyLeverettProblem` is still only glossed parenthetically as "1D immiscible CO$_2$/brine displacement, the easy end of our bench" (`:410`) — the same gloss A had. No worked example.
- **kEdh's item 3 (simple examples of "briefs" and "structured repair feedback"):** **not done.** Neither term gets an illustrative example in the main text. The representative-trajectory appendix (`:960`) is the closest thing and it is appendix-buried.
- **Figure 1's caption got worse**, not better: A's caption walked the reader through a labelled (a)/(b)/(c) manual-vs-SIGA contrast; B's is a descriptive gloss ("Illustrative example of advanced tooling usage bottleneck for the geophysics domain…"). For a reviewer complaining about comprehensibility, this is a step back.

**Discharge: ~70%.**

### 3. Limited experimental scale (10 hard tasks × 3 seeds; OpenFOAM 5 × 1) — gep1, nBNe, AC

**Status: PARTIALLY FIXED — OpenFOAM only. The GEOS core is untouched.**

- **GEOS: unchanged.** Table 1 in B (`:365-384`) is cell-for-cell identical to A's (`:186-207`): same 17 val / 10 held-out tasks, same n=3. The *word* changed — "seeds" → "runs", 33 occurrences of "seed" in A vs 1 in B — with a defensible rationale (no RNG seed is set; the repeats are temperature-sampling repeats). That is more honest, but it does not add data, and a reviewer who reads it as an attempt to make n=3 sound bigger would be unimpressed.
- **OpenFOAM: 5 → 30 tasks**, still single-run, plus a second native baseline (MetaOpenFOAM). This is a real 6× scale-up and directly responsive.
- **LAMMPS: +9 tasks**, single-run.

Total distinct tasks evaluated: 27 GEOS + 5 OpenFOAM = 32 in A; 27 GEOS + 30 OpenFOAM + 9 LAMMPS = 66 in B.

**Caveat the author must handle:** scaling OpenFOAM did not merely tighten the estimate, it **changed the answer** (see issue 5). Offering the 30-task result is offering evidence that the submitted 5-task result was noise-dominated.

**Discharge: ~45%** (the AC's "ten tasks and three seeds" complaint about the *main* result is untouched; "uncertainty estimates where possible" and "moderate the claims if additional evaluation is unavailable" are partly met by the 40×→16× moderation and the new limitations admissions).

### 4. Human baseline too small (n=2, one task) — gep1, nBNe, AC

**Status: PARTIALLY ADDRESSED — reframed more conservatively, not expanded.**

- **No new participants, no new tasks.** `tab:human-baseline` is numerically identical in A and B.
- **What improved:** the n=2/one-task caveat is **promoted into the Limitations paragraph** (`:749`: "the human baseline is $n=2$ on a single task with the budget-matched comparison bounded below by the agent") — in A it lived only in an appendix caveat. New protocol detail is disclosed (`:412`): *"Each one-hour session opened with roughly ten minutes of task explanation and environment setup"*, which explains the single-file outcome better than A's "ran out of time at 47 to 48 min". The abstract's claim narrowed from "between 8 and 36 times as long" to a plain "about five minutes … about three hours".
- **What got weaker:** participants are now described as "grad-level geoscientists" rather than A's "multi-year subsurface-modelling experience" — an honest downgrade, but it *reduces* the authority of the anchor rather than strengthening it. The instruction "no LLM chatbots or web search" was softened to "working primarily from the GEOS documentation and source tree", and the ChatGPT-navigation disclosure from A's appendix was deleted.
- **nBNe's specific asks — "different levels of GEOS user experience, from beginners to experts" and "a human–agent collaborative setting" — are NOT addressed.**
- **Unfixed liability:** Expert 1's *file-level* score falls 0.812 → 0.689 between the 1-hour and the 3-hour session (`tab:human-baseline`, both versions). Neither version explains it. The project's own internal review rated this blocking and it was deliberately skipped.

**Discharge: ~30%.**

### 5. OpenFOAM transfer under-powered — gep1, AC

**Status: LARGELY FIXED (scale) — but the result partly reverses, which must be handled explicitly.**

| | A | B |
|---|---|---|
| Tasks | 5 | **30** (`foamgpt_subset_seed42_n30_hybrid`) |
| Runs | 1 | 1 (unchanged — gep1 also asked for multiple seeds) |
| Native baselines | Foam-Agent (lint-only) | Foam-Agent **+ MetaOpenFOAM**, both lint-only |
| Foam-Agent execute mode | failed in env | **still fails** — gep1's "fuller Foam-Agent execute-mode comparison" is not delivered |
| Best SIGA cell | R+S 0.871 | R+S 0.870 |
| Vanilla | 0.466, 3/5 coverage | **0.681, 30/30 coverage** |
| S factor effect | +0.328 | **+0.168** |
| M factor effect | +0.192 | **−0.007** |

**The reversal**, quoted:
- A (`neurips_2026.tex:224`): *"every $\mathrm{S}$-enabled cell achieves full required-file coverage with no zero-score failures; Vanilla covers 3/5 and R+X covers 1/5."*
- B (`siga_arxiv_2.tex:456`): *"**every** SIGA cell, **including Vanilla**, produces all required files on all 30 tasks with no zero-score outputs."*

At n=30, the within-SIGA reliability contrast disappears; the contrast is relocated to SIGA-vs-native-agents. B also adds cost accounting that is unflattering: SIGA $23.20 total vs Foam-Agent $0.30 and MetaOpenFOAM $0.17, with B conceding SIGA is *"roughly an order of magnitude more expensive per task"*.

gep1's fallback — *"If not feasible, the claims about transfer should remain explicitly qualitative"* — **is met**: B says (`:684`) *"we read it as transfer evidence rather than a second full benchmark."*

**Discharge: ~70%.**

### 6. S/X components confounded — gep1 (**score-moving**)

**Status: NOT ADDRESSED. Acknowledged more clearly, but not isolated.**

B restates the confound in two places (`:293` and `:749`): *"Because S and X both use `xmllint`, the X main effect partly conflates agent-callable validation with hook-time schema validation when S is also enabled."* This is the same admission A made.

What B *does* add is a conceptual separation — S and X are now framed as "the two faces of validator-driven self-refinement: externally enforced (S) and agent-managed (X)" at different control points (`:213`). That is a better *explanation* of the design, not a *disentanglement* of the estimate. No new cell (e.g. S-with-parse-check-only, or X-alone-vs-S-alone at matched validation strength) was run.

gep1's stated bar: *"My confidence would increase if the stop-hook effect remains dominant after removing this confound."* Not cleared.

**Discharge: ~15%.**

### 7. Native-plugin-prefix bug contamination — gep1 (**score-moving**)

**Status: MADE WORSE.**

A disclosed it thoroughly. `neurips_2026.tex:427` (table caption): *"The minimax × X+M result of $0.392$ in italic is the pre-fix number reported in the project log; the corrected number ($0.867$) replaces it after the prefix-gate bug fix described below."* And `:444`, a full paragraph naming `src/runner/prompts/native_plugin_prefix.txt`, `src/runner/orchestrator.py`, the adversarial review RN-006 that found it, and the clean re-run. A's Limitations named the contaminated estimate: *"A native-plugin-prefix bug … contaminated the $R=-0.033$ estimate."* A's Future-work listed a clean re-run at *"~1.5h wall-clock, low API spend."*

**B contains none of this.** `grep -in "native.plugin|plugin.prefix|pseudo-tool|RN-00|0.392"` over `siga_arxiv_2.tex` returns **zero hits**. The corrected 0.867 is retained with no provenance; the "[was 0.392]" annotation is stripped from the caption; the Limitations sentence is gone; the Future-work re-run item is gone with the whole appendix. The author's changelist records the rationale as *"overstated, solved by new results"*.

There is a genuine partial fix hiding underneath, which is worth extracting: **the Resolution-IV main effects were recomputed and corrected.** A reported R −0.032 / S −0.003 / X +0.007 / M +0.004 (and, inconsistently, R = −0.033 in its own Limitations). B reports R −0.037 / S −0.008 / X +0.011 / M +0.008. I recomputed all four from the eight factorial val cells — which are **identical in both versions** — and get R −0.0368, S −0.0077, X +0.0112, M +0.0083. **B is arithmetically correct; A was not.** So the contaminated-looking estimate gep1 asked about was, at least in part, an arithmetic error in A rather than a data contamination, and B fixes it.

But that fix is invisible in B, because B deleted the appendix table that would let anyone see the change and deleted the discussion that would explain it. **From gep1's seat, the paper responded to "please rerun the contaminated cells and tell us what happened" by removing the disclosure.** That is the single worst-looking delta in the whole diff.

**Discharge: −20%** (i.e. it costs you rather than helps, unless the disclosure is restored and the recomputation is made explicit — at which point this becomes a strong, cheap rebuttal win; see the merge doc).

### 8. Limitations should state "structural authoring reliability, not validated simulator correctness" — gep1

**Status: NOT ADDRESSED; presentation regressed.**

gep1 asked for the limitations section to *"more directly state that the current evidence supports structural authoring reliability, not validated simulator correctness."*

B's limitations paragraph still says only *"TreeSim is structural, not physical: a $0.8$ deck is not guaranteed to run"* — the identical sentence A had, no stronger — and it now sits in an appendix (`:749`) instead of the main body. The main body's §7 is "Broader impact" only, one paragraph, which merely points at the appendix.

B does add three new limitation items (held-out lift concentrated in two tasks; human baseline n=2 on one task; the autonomy "supervisor" was an LLM simulator, not a human — this last is a genuinely good new disclosure). But the specific sentence gep1 asked for was not written, and the section it belongs in was demoted.

**Discharge: 0%** on the wording; **negative** on placement. NeurIPS also expects limitations in the main body; the checklist justification in B now points to an appendix.

### 9. Report the exact Claude Code version — nBNe

**Status: NOT ADDRESSED.**

`grep -inE "claude code (v|version|[0-9])|v[0-9]+\.[0-9]+\.[0-9]+"` over the compiled `siga_arxiv_2.pdf` → **zero hits**. The Implementation-details appendix (`:787`) gives hook-wiring history and artefact paths but no harness version. The only version-ish strings anywhere are model names (`deepseek-v4-flash`, `minimax-m2.7`, `gemini-3-flash-preview`, `Claude Sonnet 4.6`).

This is the cheapest item on the entire review list — one sentence — and B does not do it.

**Discharge: 0%.**

### 10. Venue fit (eScience vs NeurIPS) — kEdh

**Status: PARTIALLY HELPED, indirectly.**

Nothing addresses this head-on, and nothing can. But two changes make the NeurIPS case easier to argue:
- The framing moved from "a GEOS case study" to a general **interface-grounding / harness-adaptation** problem with a formal three-interface abstraction and an explicit connection to the meta-harness / harness-as-code literature (`:150`, four new citations). That is a recognisably ML-methods framing.
- The multi-simulator result gives a *transferable design principle* — "match the component to the interface's binding constraint" — rather than a GEOS engineering report.

Against that: the title change **removes** the method's name and reads more like a systems/application title than the original.

**Discharge: ~25%**, and only as ammunition for the rebuttal text, not as something the reviewer will see and change their mind about.

### 11. No fundamentally new architecture / incremental — nBNe (minor, listed as a weakness not a request)

**Status: PARTIALLY ADDRESSED.**

B adds the formalism (Eqs. `adapter`, `selfevolve`) and an explicit "adaptation-over-reconstruction" thesis with three defended reasons (`:194`), plus a positioning against harness-optimization work. This converts "we added four tools" into "we identify the three harness interfaces where simulator grounding must enter, and show which one binds depends on the interface". That is a real conceptual upgrade.

nBNe rated the paper 5 despite this weakness, so it is low-stakes.

**Discharge: ~50%.**

---

## Scorecard

| Issue | Raised by | Status in arXiv B |
|---|---|---|
| 1. Execution / physics validity | gep1 (SM), nBNe, **AC primary** | **Not addressed**; execution-ladder plan removed from view; Fig. 2 still implies execution |
| 2. Writing clarity / jargon | **kEdh primary**, AC | **Largely fixed** (~70%) |
| 3. Small task set / few runs | gep1, nBNe, AC | **Partially** — OpenFOAM 6×, LAMMPS new; GEOS core unchanged |
| 4. Human baseline n=2 | gep1, nBNe, AC | **Partially** — reframed, caveats promoted; not expanded; expertise claim downgraded |
| 5. OpenFOAM under-powered | gep1, AC | **Largely fixed** (5→30, +MetaOpenFOAM); but result partly reverses; still n=1, still lint-only |
| 6. S/X confound | gep1 (SM) | **Not addressed** — better explained, not isolated |
| 7. Native-plugin-prefix bug | gep1 (SM) | **Made worse** — disclosure deleted (though the underlying main-effects arithmetic *was* silently corrected) |
| 8. Limitations wording + placement | gep1 | **Not addressed**; moved to appendix |
| 9. Exact Claude Code version | nBNe | **Not addressed** |
| 10. Venue fit | kEdh | **Indirectly helped** by reframing; hurt by the title change |
| 11. Incremental / no new architecture | nBNe (minor) | **Partially addressed** via the formalism |

## Estimated burden already discharged, per reviewer

These are judgement calls, weighted by how much each reviewer's own text emphasises each item.

| Reviewer | Current | Burden discharged by swapping in B, as-is | Reasoning |
|---|---|---|---|
| **kEdh** (2, conf 4) | Reject | **~65–70%** | Their entire review is "this is not written well". B is a near-total rewrite with a de-jargoned abstract, a defined metric, motivated methodology, and RQ boxes. Residual: no worked example of a "brief" or "structured repair feedback"; Buckley–Leverett still unexplained; Fig. 1 caption regressed; venue objection stands. **This is where the arXiv version moves a score.** |
| **gep1** (4, conf 3) | Borderline accept | **~30%** | Q3 (OpenFOAM) largely answered and Q4 (human reframing) partly. But both score-moving items — execution eval, and the prefix-bug rerun + S/X separation — are unaddressed, and item 7 regresses. gep1 said explicitly *"My score would increase if the reliability gains persist under execution or physical-validity checks"*; B offers nothing there. |
| **nBNe** (5, conf 5) | Accept | **~25%** | Already accepting, so little to gain and something to lose: their weakness #4 (small task set) is partly met, but their three questions — convergence/output validation, human-expertise levels + collaborative setting, exact Claude Code version — are 0/3. B also *weakens* two things nBNe praised: they cited "cross-simulator transfer" and "the human baseline" as major strengths, and B's OpenFOAM reversal plus the downgraded participant description both erode those. **Non-trivial risk of nBNe drifting downward if the changes are read carelessly.** |
| **AC (GKRj)** | Borderline | **~40%** | Two of four AC bullets substantially addressed (clarity: yes; scale: partly). The AC's own decision criterion is stated as a conjunction: *"whether the rebuttal can establish that the structural improvements translate to executable and scientifically valid simulations **and** whether the authors can put significant efforts towards improving the clarity."* B delivers the second conjunct and not the first. Half of a conjunction is not a decision. |

**Aggregate: ~40–45% of the reviewer burden is discharged by the arXiv text alone.**

The structure of what remains is unusually clean: **the writing problem is solved and the evidence problem is not.** Every remaining high-value item is an experiment or a disclosure, not a rewrite — which is a good position to be in with limited rebuttal time, because those items are enumerable and mostly small.
