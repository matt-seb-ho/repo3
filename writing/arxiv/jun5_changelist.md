# Jun 5 Changelist — neurips_2026.tex

Feedback incorporated section by section. Newest changes appended within each section.

## Abstract

- Removed held-out absolute numbers (`0.720 → 0.789`, `+7 points`); now reports only `~10%` relative improvement over the bare agent.
- Dropped TreeSim metric/terminology throughout the abstract; replaced with "quality score" (applies to both the held-out result and the Buckley–Leverett `>0.90` line).
- Removed the "at no added wall-clock cost over the bare agent" clause.
- Self-evolution given its own sentence, with mechanism spelled out: the agent edits its own tools, memories, and prompts rather than drawing from a fixed component set.
- Generalization given its own sentence: "we additionally explore generalization on two more simulators, OpenFOAM and LAMMPS..."
- "Contract" framing reviewed and kept (recommended "executable contract"). Open note: "quality score above 0.90" now implies a 0–1 scale without naming the metric — revisit if we'd rather drop the 0.90 absolute too.
- Added a closing thesis sentence (summarized from the last intro paragraph): small self-improvable grounding layer = reliable operator of existing scientific software + a recipe for adapting to new simulators.

### Abstract — round 2 (Jun 5)

- Removed all em dashes (`---`); replaced with commas/separate sentences.
- Added a standalone sentence stating we primarily study GEOS (open-source multiphysics simulator, subsurface science).
- Split out the 36× claim into its own sentence and made explicit it is measured against a human baseline (domain scientist new to GEOS).
- "across-seed variance" → "score variance".
- Replaced "order of magnitude" variance reduction with a concrete figure: ~16× (from the held-out std 0.081 → 0.005). NOTE: body reports this as a std reduction; abstract calls it "score variance" loosely per request — keep terminology consistent if a reviewer probes.
- Simplified the OpenFOAM/LAMMPS sentence: now just states SIGA improves performance there too and that different modules are most effective according to each simulator's dominant challenge (dropped the validation-vs-memory/retrieval specifics for the abstract).

## Introduction

- Added a Figure 1 reference (`Fig.~\ref{fig:1}`) in the DSL/translation paragraph (para describing the runnable-deck bottleneck).
- Added motivation for building on the SOTA harness: **frontier models are increasingly post-trained inside specific agent harnesses**, so planning/tool-use/self-correction are calibrated to that scaffolding; re-implementing orchestration from scratch discards this alignment. Placed in the method-wise gap paragraph. NOTE: still open whether this belongs here or in the Method section — currently in intro.
- Rewrote the results paragraph as four numbered insights (bold lead-ins), removed detailed absolute numbers (kept relative gains only), and removed "wall-clock" terminology in favor of "setup efficiency"/"efficiency" (advisor: wall-clock is out-of-domain for non-systems ML readers).
- Answered advisor's "can we automatically adapt to new simulators?" — closing paragraph now states we do *not* claim fully automatic adaptation, but the four-slot decomposition + self-evolution pipeline give a concrete recipe for adapting with modest effort. Also reflected in results insight (4).
- Last intro paragraph summarized into the abstract's new closing sentence (see Abstract).

### Introduction — round 2 (Jun 5)

- Added "to the best of our knowledge" to the "no agent has been designed for GEOS in particular" claim.
- Insights/findings paragraph: removed em dashes; dropped "Buckley–Leverett" (now "a representative GEOS task"); replaced "order of magnitude" with concrete numbers (~36× setup-efficiency gain in finding 1, ~16× variance reduction in finding 2).
- Finding 3 reframed from "The best adapter can be found automatically" to "Further improvements can be discovered automatically."
- Regularization motivation for the light adapter: DECIDED to put this in the Method section (not intro), since the intro already carries the "compact optimization surface" point. Added as a third design rationale in the Method "This design choice is intentional" paragraph — thin adapter avoids overfitting to one model/harness version and should degrade gracefully across upgrades/swaps.

## Related Work

- Added the four harness-engineering citations to the "agent scaffolding as a learnable object" sentence, mapping each heading to its bib entry: meta-harness design `lee2026metaharness`, harness-as-code `ning2026codeagentharness`, agentic harness engineering `lin2026agenticharnessengineer`, skill optimization `yang2026skillopt`.

## Background

- Added GEOS citation (`\citep{geos2024}`) at the first body mention ("A GEOS deck is one or more XML files...").

## Method

- **New `\subsection{Overview and formalization}`** (`\label{subsec:method-overview}`) inserted at the top of the Method, before Design-space components. Two parts:
  - *Motivation recap* (2 paras): restates the interface-grounding framing (coding agent has the generic loop, lacks the simulator's "executable contract") and the three rationales for the thin adapter (portability / optimization surface / regularization), cross-referencing intro + related work rather than re-arguing them.
  - *Math formalization* (3 `\paragraph`s, 2 display equations), modeled on the Meta-Harness paper (`lee2026metaharness`, LN-003):
    - **Base harness + objective**: frozen model `\pi`, frozen harness `H_0`, task `x ~ X`, rollout `\tau ~ p_\pi(H_0, x)`, reward `r(\tau,x) = TreeSim(\hat y, y\star) ∈ [0,1]` (failures-as-zero, cites `\S\ref{sec:eval}`), objective `max E[r]` over the harness not the weights (cites `\citet{lee2026metaharness}`).
    - **Grounding adapter** (Eq. `eq:adapter`): base harness as `H_0 = (c_0, T_0, stop_0)`; adapter modifies exactly three interfaces — context `c_0 ↦ c_0 ⊕ m` (M), tools `T_0 ↦ T_0 ∪ T_R ∪ T_X` (R, X), termination `stop_0 ↦ stop_S` (S). Adapter = subset `b ∈ {0,1}^{R,S,X,M}`; `b=0` is Vanilla. Maps each of the four components onto a slot.
    - **Self-evolution** (Eq. `eq:selfevolve`): adapter contents `\theta` (primer, cheatsheet `m`, skills); `\theta\star = argmax_\theta E_{x~X_sel}[r]` on the validation-selection split; offline coding-agent proposer reading prior contents/trajectories/rewards from a filesystem (mirrors the meta-harness outer loop); base harness + model stay frozen.
- **Trimmed** the now-redundant motivation paragraphs that opened `\subsection{Design-space components}` (interface-grounding framing + three-rationale "This design choice is intentional" para) down to a one-paragraph lead-in, since the Overview now carries them. Kept `\label{subsec:overview}` on the components subsection (still referenced by the appendix cells table at the old `\S\ref{subsec:overview}`).
- **Self-evolved adapter contents** subsection: tied its opening to `Eq.~\ref{eq:selfevolve}` and named the contents `\theta` for consistency with the formalization.
- **Figure 2 caption** rewritten from "Execution trace of the SIGA agent loop" to "**The SIGA method**", describing the (already-updated) method-diagram asset: input brief → base agent (frozen `H_0` + `\pi`) running its context→act→observe loop, the three adapter grounding interfaces (M context, R/X tools, S stop hook), validated-deck output, and the dashed self-evolution loop that revises adapter contents offline. The Fig. 2 reference in the method text was moved from the components lead-in into the Overview (no longer described as an "execution trace").
- Note: `assets/siga_f2.png` is already a pure method diagram (Inputs / Base coding agent / Outputs + SIGA adapter modules + Self-evolution), so the new caption matches the current figure; no image swap needed.

### Build hygiene (Method pass)

- Fixed two unescaped `&` in `references.bib` titles (`Q&A` → `Q\&A` in `gpqa` and `shi2026mdagent2`) that caused a fatal "Misplaced alignment tab character &" in the `.bbl`. Full `pdflatex → bibtex → pdflatex ×2` now builds clean (36 pp, all new `eq:`/`fig:2`/`lee2026metaharness` refs resolve).

### Method — round 2 (Jun 5): de-duplication + reorg

Advisor feedback: (a) "graceful degradation" is wrong framing — we want generality/non-overfitting, not to degrade; (b) the formalism walked through all four components + SE, then the following subsections walked through them *again* (felt redundant). Restructured into three single-pass subsections so each idea appears exactly once.

- **Rationale (iii) reworded** from "Regularization and graceful degradation" → **"Generality"**: grounding only the simulator contract avoids overfitting to one model/harness version, so the layer carries over to updated/swapped models+harnesses, improvements in the base agent *compound with* (not invalidate) the adapter, and adapting to new model/harness behavior stays cheap. Dropped all "degrade" language.
- **New `\subsection{Overview}`** (`subsec:method-overview`) = **motivation only** (no equations, no per-component walk): interface-grounding intuition + the three adaptation-over-reconstruction rationales + a new **minimality** paragraph. The minimality para frames R/S/X/M as three *well-established* agent ideas (not arbitrary): (1) retrieval = alternate interface to domain knowledge via semantic query (R); (2) validator-driven self-refinement, agent-managed (X) + externally enforced (S); (3) procedural memory = write-down-and-reuse experience (M). Ends by naming the three harness interfaces (context/tools/termination).
- **New `\subsection{The grounding adapter}`** (keeps label `subsec:overview` so existing refs resolve) = **formalism + components interleaved, one pass**:
  - `\paragraph{Base harness and objective}` (frozen π, H₀, rollout, TreeSim reward, objective; cites Meta-Harness).
  - `\paragraph{Three grounding interfaces}` + Eq. `eq:adapter` (context⊕m / tools∪T_R∪T_X / stop_S).
  - Component paragraphs in **R, S/X, M** order. S and X **merged into one paragraph** ("validator-driven self-refinement, termination and tool interfaces") since they're two faces of one idea — externally enforced (S) + agent-managed (X). Each paragraph names its formal slot, failure mode, and impl detail (MCP tools, retry-bounded stop hook, ~3 X-calls/task, 775-tok cheatsheet). **This absorbs the old standalone "Design-space components" subsection** — no more second pass.
  - `\paragraph{The SIGA design space}` (subset b ∈ {0,1}^{R,S,X,M}; Vanilla = 0; object of the factorial study).
- **`\subsection{Self-evolved adapter contents}` → `\subsection{Self-evolving the adapter}`** (`subsec:self-evolved`): now opens with the formal `\theta` setup + Eq. `eq:selfevolve` (moved here from the old Overview formal paragraph, so SE is introduced once), then SE and SE-prose paragraphs. Removed the duplicate formal "Self-evolution over adapter contents" paragraph that previously previewed it in the Overview.
- **Cross-ref fix**: appendix cells table (SE row) pointed at `\S\ref{subsec:overview}` for the "self-evolved v3 plugin"; repointed to `\S\ref{subsec:self-evolved}` (correct target). `checklist.tex`'s ref to `subsec:overview` (cheatsheet distiller) still resolves correctly — the M/cheatsheet paragraph now lives in "The grounding adapter" = `subsec:overview`.
- Net: motivation once → formal setup once → each component once (fused with its slot) → SE machinery once + two variants. Builds clean (36 pp). Pre-existing unrelated undefined ref `subsec:cross-cutting` in `checklist.tex:221` is NOT from this work (flagged for separate fix).

## New experiments + tone/format pass (Jun 5, eve)

Sources: undergrad write-ups `audrey_lammps.md` (LAMMPS) and `docs/openfoam_n30/*` (OpenFOAM scaled 5→30 tasks + MetaOpenFOAM baseline + token instrumentation).

### Experiments / Results / Discussion — new studies
- **OpenFOAM transfer scaled 5 → 30 tasks** (`foamgpt_subset_seed42_n30_hybrid`, DSv4-flash, single seed). Rewrote the RQ5 OpenFOAM Results subsection and the OpenFOAM appendix. Key shift in the narrative: at n=30 **every** SIGA cell (incl. Vanilla) holds 30/30 full coverage with 0 zero-score, so the reliability contrast moved from *within* SIGA cells (the old "Vanilla 3/5, R+X 1/5") to **SIGA harness vs. native agents**. Added a second native baseline **MetaOpenFOAM** (`chen2024metaopenfoam`) alongside Foam-Agent, both lint-only. New numbers: best cell R+S 0.870; Vanilla 0.681; Foam-Agent 0.516 (19/30 cov, 8 zero); MetaOpenFOAM 0.379 (10/30 cov, 12 zero). New n30 factor readout R:+0.005 S:+0.168 X:+0.007 M:−0.007 (S still dominant, recomputed from the 8 factorial cells). Added cost accounting (SIGA ~10× pricier/task than native agents).
- **New main-text Table 3** (`tab:openfoam-main`): 30-task leaderboard (9 SIGA cells + 2 native agents) with Mean score↑ / Full cov↑ / Zero↓ / Wall s / Est. cost. Old 5-task summary + per-task tables removed from appendix (superseded).
- **New LAMMPS transfer study** (RQ5 second simulator). Added a Results subsection + new **Appendix `app:lammps-transfer`** with per-cell Table 10 (`tab:lammps-percell`, 12 cells × 9 tasks, 2 backbones Claude Sonnet 4.6 / DeepSeek). Headline Table 4 (`tab:lammps-headline`): DeepSeek 4.56→7.78 (M+R+S+X, +3.22), Claude 6.33→6.89 (M+R). **Mechanism shift**: on LAMMPS structural scores are ceiling (≥0.976), so completeness is solved and value-correctness is the bottleneck → M (+2.13 DeepSeek) and R (+1.55) dominate, not S. Factor readouts reported per backbone.
- **Discussion "What transfers across simulators"** rewritten: dominant component is interface-dependent (S for GEOS/OpenFOAM completeness; M+R for LAMMPS value-correctness). Conclusion + Experimental-Design RQ5 + Related-Work OpenFOAM-comparator sentence updated to name both transfer studies and both native baselines. Future-work bullets updated (5→30 OpenFOAM already done; multi-seed + deterministic LAMMPS judge as the open items).
- Abstract/intro already named OpenFOAM+LAMMPS (round-2 pass) — no change needed.

### Tone pass on RQ sub-headers (advisor: "honest and humble to a fault")
- RQ1 sub-header `SIGA raises the reliability floor rather than the quality ceiling` → **`Reliability is SIGA's biggest gain`** (dropped "rather than quality ceiling"; leads with the gain).
- RQ2 sub-header `... fix block-level omissions; attribute errors persist` → **`... fix block-level omissions`** (dropped "attribute errors persist").
- Results-intro paragraph softened to lead with reliability; residual-error caveat kept but framed forward-looking ("where future grounding can extend the gains"), dropped "raise the floor rather than solve simulator reasoning" and "harm-reduction regime, not a correctness regime".
- **De-bolded the drawback lead-ins** in the RQ2 bottleneck list (items (2) `bad_attribute_value` and (4) `strictly-perfect`); kept the positive findings (1),(3) bold. Limitations remain in text for transparency, just not visually highlighted.

### RQ "Answer" boxes (advisor's reference-paper style: grey box, thick darker-grey left border, bold "Answer to RQ...")
- Added a **prototype** in the preamble (after `\usepackage{xspace}`): `\usepackage{mdframed}`, colors `rqboxbg`/`rqboxrule`, a `\newif\ifrqfancy` toggle (set `\rqfancytrue`), an `rqbox` mdframed env, and an `rqanswer` environment.
- **Easily revertable**: flip `\rqfancytrue` → `\rqfancyfalse` to fall back to plain inline `\textbf{Answer to RQ...}` paragraphs (the `\usepackage{mdframed}` line then becomes harmless / can also be commented).
- Converted all five `\textbf{Takeaway (RQn).}` lines to `\begin{rqanswer}{RQn} ... \end{rqanswer}`. RQ5 has two boxes: `RQ5 (OpenFOAM)` and `RQ5 (LAMMPS)`.

### Table 2 (human baseline) header clarity (advisor couldn't parse columns)
- Added a grouping header row: **Quality (↑ better)** spanning File-level + Deck-level (cmidrule), **Efficiency (↓ better)** over Wall (min); per-column ↑/↓ arrows added; caption now states which direction is better for each metric.

### Build
- `mdframed` + `tcolorbox` confirmed present in TeX Live. Full `pdflatex → bibtex → pdflatex ×2` builds clean at **39 pp**. No new undefined refs / no new overfull boxes from the added tables; only the pre-existing `subsec:cross-cutting` warning remains.

## Section-feedback pass (Jun 5, round 2)

Advisor feedback on §6.1–6.4, Discussion, Conclusion.

### Terminology: "seeds" → "runs" (paper-wide)
- Decision (advisor): we don't set an RNG seed; we repeat each config under temperature sampling. Renamed globally to **runs**: `$n=3$ seeds`→`$n=3$ runs`, `across-seed`→`across-run`, `seed noise`→`run-to-run noise`, `single-seed`→`single-run`, `multi-seed`→`multi-run`/`repeated runs`, `(cell, seed, task)`→`(cell, run, task)`, `seed-noise floor`→`run-to-run noise floor`, etc. **Kept** `seed42` (real dataset-subsampling seed in the benchmark filename). Also updated `checklist.tex` for consistency (3-run factorial, across-run σ, single-run transfer cells).

### §6.1 (RQ1)
- Retitled sub-header (prev round) `Reliability is SIGA's biggest gain`. Hard-tail paragraph **generalized**: now leads with "the bare harness's high variance comes from a small number of catastrophic (zero-score) outputs, not broad spread," then keeps the ExampleProppantTest case as a parenthetical illustration (advisor: prefer the general statement, single example shouldn't be the headline).
- Killed the "we are honest that..." phrasing in the Val-ceiling paragraph.

### §6.2 (RQ2)
- De-bolded item (3) ("Adapters trade catastrophic absence...") — bold reserved for positive findings only.
- **Reframed attribute errors** as task difficulty, not system failure: added that correct attribute values require domain knowledge not in the schema/docs (would need primary-literature sourcing or scientific-reasoning capability), and that the flat `bad_attribute_value` count is partly mechanical (filling missing blocks surfaces more attributes to be judged). Now framed as "egregiousness reduced (block→attribute), remaining problem to solve" not a shortcoming. RQ2 answer box updated to match.

### §6.3 (RQ3)
- Softened the "no LLM chatbots or web search" claim (advisor: we weren't strict) → "working primarily from the GEOS documentation and source tree"; appendix protocol now "discouraged but not strictly enforced (see disclosure)".
- Fixed the confusing "ran out of time at 47–48 min" framing → "each one-hour session opened with ~10 min of task explanation/setup; in the remaining authoring time both completed only base.xml". Table rows relabeled `(1 h cutoff)`→`(1 h session)`.

### §6.4 (RQ4)
- Added a benchmark-design conclusion to the RQ4 box: eliciting genuine consultation needs tasks whose missing info isn't recoverable from accessible examples; our relaxed briefs didn't clear that bar, so designing forcing-function tasks is itself an open methodological problem.

### Discussion → appendix (advisor: redundant with RQ boxes + Conclusion)
- **Moved** the whole analytical Discussion to new **App. I `Extended discussion`** (`app:discussion`): "What transfers across simulators", "New tools are not used just because exposed", "Adapter-design recommendations".
- Main-text §7 retitled **`Limitations and broader impact`** (keeps `\label{sec:discussion}` so all refs resolve): a concise, updated **Limitations** paragraph (uncommented + refreshed: 30-task OpenFOAM, LAMMPS, runs terminology, two native baselines) + the **Broader impact** paragraph + a pointer to App. I. (Kept Limitations in main text despite "only Broader Impact" — the NeurIPS checklist promises a main-text limitations statement and the prior one was commented out; flag if you'd rather push it to the appendix too.)
- Repointed the Related-Work procedural-memory ref from `\S\ref{sec:discussion}` → `App.~\ref{app:discussion}`. The S/X-conflation ref (§ Ablation design) stays `sec:discussion` (still covered by the new Limitations paragraph).

### Conclusion
- Added the domain-expert result: now states that for domain experts new to the simulator SIGA compresses a multi-hour task to minutes (~36× speedup at matched quality), alongside the experienced-user time-envelope point.

### Build
- Clean `pdflatex ×2` at **39 pp**; no leftover `seed` (except `seed42`); `app:discussion` resolves; only the pre-existing `subsec:cross-cutting` warning remains.

## Appendix cleanup pass (Jun 6)

- **Limitations → appendix.** Main-text §7 is now **`Broader impact`** only (kept `\label{sec:discussion}` so refs resolve); the Limitations paragraph moved into **App. `Extended discussion`** (`app:discussion`) with `\label{subsec:limitations}`. Repointed body + `checklist.tex` limitations refs from `sec:discussion` → `app:discussion`.
- **Native-plugin-prefix bug removed** (advisor: overstated, solved by new results). Dropped from the Limitations paragraph; App. F R-factor note reframed as backbone/benchmark dependence (R helps weaker models; near-ceiling deepseek-v4-flash val barely moves) instead of "the bug"; deleted the `%`-commented bug line in §6.1; removed it from the checklist limitations list.
- **Removed Appendix B (Cell definitions / `tab:cells`)** — redundant with Table 1; dropped the in-text "Full settings are in App.~\ref{app:cells}" and repointed the S/X-conflation aside to `app:discussion`. Fixed two `checklist.tex` refs to `app:cells`.
- **Removed Appendix E (Resolution-IV main effects on val / `tab:main-effects`)** — body already states R≈−0.032 and X/M/S within ±0.007; dropped the lone in-text ref.
- **Commented out the Future-work appendix** via `\iffalse ... \fi` (retained in source). No active refs to `app:future-work` remained.
- **Factor-style readouts.** LAMMPS readout reformatted from one overflowing `\[...\]` line into a two-line `align*` (Claude Sonnet 4.6 / DeepSeek v4-flash). OpenFOAM readout left as one line (single model, fits).
- **Model naming (LAMMPS).** Table backbone column → "Claude Sonnet 4.6" / "DeepSeek v4-flash"; prose now "deepseek-v4-flash"; added an explicit harness-vs-model note ("both backbones run inside the Claude Code harness; 'Claude' = the Sonnet 4.6 model, not the harness; CC is used everywhere except the OpenHands cross-harness run").
- **Table 1.** Spelled out `SE-prose`/`SE` → **Self-Evolve-prose / Self-Evolve** (caption notes the SE/SE-prose abbreviations used elsewhere).
- **Human-baseline appendix.** Deleted the ChatGPT-navigation disclosure paragraph and its referring clause.
- **OpenCode limitation reworded** (advisor: don't single out one harness) → "time and cost constraints prevented us from extending to the other coding harnesses now available (e.g. OpenCode, Pi, Hermes Agent)".
- **Appendix review subagent** (general-purpose, fresh context) swept the whole appendix: 0 em dashes, no stale seed/bug/5-task/dangling-ref content, harness-vs-model handled. Acted on its two findings: removed an internal "filename pending final confirmation" footnote (Implementation details) and softened a "should be redacted in any future iteration" parenthetical (autonomy supervisor-channel leak note).
- **Also fixed** the pre-existing dangling `subsec:cross-cutting` ref in `checklist.tex` (pointed only to `app:cross-model-detail`).
- Build: clean `pdflatex ×2`, **38 pp**, **0 undefined references**, no rendered `seed` (one `%`-commented old-intro draft still contains the word, not rendered).
