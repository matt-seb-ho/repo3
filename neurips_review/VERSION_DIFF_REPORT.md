# VERSION_DIFF_REPORT — NeurIPS submission (A) → latest arXiv (B)

**A (NeurIPS submitted)** = `/home/matt/sci/repo3/writing/neurips/neurips_2026.tex` (91 KB, May 7 2026 11:09) → `/home/matt/sci/repo3/siga_neurips_init_sub.pdf` (33 pp = 31 pp paper + checklist). Main body ends p9; References start p10 (verified by `pdftotext`).

**B (latest arXiv)** = `/home/matt/sci/repo3/writing/arxiv/siga_arxiv_2.tex` (140,724 B, Jun 25 2026 18:23) → `siga_arxiv_2.pdf` (31 pp, Jun 25 18:26). Main body ends p12; References start p13. `arxiv_upload/siga_arxiv_2.tex` is byte-identical (md5 `59e4c3bc…`) — confirmed newest.

Lineage confirmed: `jun5_start.tex` → `jun7_v0.tex` → `jun8_v1.tex`/`arxiv_v1.tex` (arXiv v1) → `jun24_v2.tex` → `siga_arxiv_2.tex` (arXiv v2). `jun24.tex` is a stale Overleaf master (still `Anonymous Authors`, missing the TreeSim appendix) — **not** in the lineage. Jun 8 → Jun 25 is undocumented by any changelist; a direct diff gives 12 hunks: title, abstract, Fig. 1 image, and a full Introduction rewrite — **no body/results/table/number changes after Jun 8**.

Verification convention below: **[V]** = I verified it in the source myself (with file:line). **[C]** = taken from the author's own changelists. **[I]** = my inference.

---

## Executive summary (10 bullets)

1. **The main body is effectively a rewrite, not a revision.** Only **20 of 163** main-body sentences from A survive verbatim into B's 248 (~12%). [V, difflib on both `.tex`, intro→`\appendix`]
2. **The title changed twice** and the paper's own name was dropped from it: A `Simulator-Interface Grounding Adapters for Scientific Simulation Setup: A Geophysics Case Study` → (arXiv v1) `SIGA: Self-Evolving Coding-Agent Adapters for Scientific Simulation` → B `Auto-Configuring Scientific Simulators with Lightweight Coding-Agent Adapters`. "SIGA", "Self-Evolving", and "Geophysics case study" are all gone from the title. [V `neurips_2026.tex:52`, `siga_arxiv_2.tex:81`; C]
3. **B is de-anonymized.** `\usepackage[preprint]{neurips_2026}` (`siga_arxiv_2.tex:10`) plus a 5-author UCSD block (`:87-90`). Same `.sty` as A — reverting is a one-token change. [V]
4. **The headline reliability number moved: 40× → 16×.** No data changed; the reference cell changed (0.081/0.002 = 40.5× for S+X vs 0.081/0.005 = 16.2× for X+M). B is the more conservative and defensible choice. [V + C]
5. **Three arithmetic errors in A were silently corrected in B**, all of which I re-derived independently: the Resolution-IV main effects (A's table does not reconcile with A's own Table 1), the harness-less recovery delta (+0.164 → +0.488), and the 46-task split that summed to 45. [V]
6. **A's abstract claim "roughly 16% fewer tool calls" was an overclaim** contradicted by A's own efficiency table (SE uses *more* tool calls than Vanilla on held-out-eval: 97.4 vs 90.5). B corrects it and drops it from the abstract. Efficiency table is byte-identical in both. [V]
7. **OpenFOAM was rebuilt at 6× scale (5 → 30 tasks) and a second native baseline (MetaOpenFOAM) added — and the result partly reversed.** A's "every S-enabled cell gets full coverage, Vanilla only 3/5" becomes "*every* SIGA cell including Vanilla is 30/30". The S factor effect halved (+0.328 → +0.168); M flipped sign (+0.192 → −0.007). [V]
8. **LAMMPS is entirely new** (0 occurrences of "LAMMPS" in A or in the submitted PDF): 9 tasks × 12 configs × **single run**, two backbones, scored by a regex structural check plus an LLM judge that is *itself one of the two scored backbones*. **LAMMPS is never executed** — B states this outright. [V]
9. **Content was removed, not only added.** The native-plugin-prefix bug disclosure is gone entirely; Limitations moved out of the main body into an appendix; the Future-work appendix (including the "Execution-correctness ladder" plan) is compiled out via `\iffalse`; two appendices deleted; one quantitative honesty statement (the 0.898 held-out control) dropped.
10. **B contains zero execution or physics-validity evidence for any of the three simulators**, and now says so in a less prominent place than A did.

---

## 1. Title, abstract, framing

### Title

| | Text | Source |
|---|---|---|
| A | *Simulator-Interface Grounding Adapters for Scientific Simulation Setup: A Geophysics Case Study* | `neurips_2026.tex:52` |
| arXiv v1 (Jun 8) | *SIGA: Self-Evolving Coding-Agent Adapters for Scientific Simulation* | `arxiv_v1.tex:81` |
| B (Jun 25) | *Auto-Configuring Scientific Simulators with Lightweight Coding-Agent Adapters* | `siga_arxiv_2.tex:81` |

Both prior titles are retained as comments at `siga_arxiv_2.tex:79-80`.

### Authorship / anonymity

- A: `\author{Anonymous Authors}` (`neurips_2026.tex:56-58`); submitted PDF p1 reads "Anonymous Author(s) / Affiliation / Address / email". [V]
- B: `Matthew Ho \quad Brian Liu \quad Jixuan Chen \quad Audrey Wang \quad Lianhui Qin \\ University of California, San Diego` (`siga_arxiv_2.tex:87-90`), rendered on p1. [V]
- B additionally **anonymizes a third party** that A named: A credits "Dr.~Chris Sherman (LLNL, GEOS developer)" (`neurips_2026.tex:238`) and names participants "Liam"/"Sahchit" in the appendix; B says "a GEOS expert and developer" (`siga_arxiv_2.tex:410`) and "Expert 1 / Expert 2" throughout. [V]

### Abstract — before / after

**A** (`neurips_2026.tex:66`, verbatim excerpt):

> "…A Resolution-IV factorial surfaces three benefits over vanilla Claude Code. First, SIGA improves **reliability**, reducing across-seed variance by roughly $40\times$ by preventing unparseable or empty decks on a hard tail of compound multi-physics tasks. Second, it improves **quality**, raising mean structural similarity by about $+7$ percentage points on the same hard tail. Third, a self-evolved variant matches the best hand-designed cell with roughly $16\%$ fewer tool calls… A preliminary human baseline finds that geoscience-domain-expert volunteers new to GEOS take between 8 and 36 times as long as the agent… An explicit human-consultation tool is used in only about $3\%$ of under-specified trials… A small OpenFOAM transfer study indicates that the recipe is not specific to GEOS XML…"

**B** (`siga_arxiv_2.tex:98`, verbatim excerpt):

> "Configuring an advanced scientific simulator, translating a modeling goal into a valid, runnable input deck, is a persistent bottleneck that costs domain scientists hours to days… We introduce SIGA, a coding-agent adapter that supplies this contract through retrieval, procedural memory, agent-callable validation, and validation-gated termination while leaving the model and loop frozen… On GEOS… **SIGA's main gain is reliability**: on harder held-out tasks it improves TreeSim from 0.720 to 0.789 and reduces across-run standard deviation by about **16×** by preventing empty or invalid decks. In a human calibration, SIGA reaches in about five minutes the deck quality a domain expert reached in about three hours. Transfers to OpenFOAM and LAMMPS show the recipe is portable but interface-dependent: completion gates help when structural completeness is the bottleneck, while memory and retrieval help when value correctness is."

**What changed in framing:**

| Dimension | A | B |
|---|---|---|
| Opening move | "Frontier LLMs are increasingly capable of expert-level scientific reasoning…" (LLM-capability framing) | "Configuring an advanced scientific simulator … is a persistent bottleneck that costs domain scientists hours to days" (**user-pain framing; defines "input deck" in sentence one**) |
| Named artifacts in abstract | Resolution-IV factorial, TreeSim, `consult_supervisor`, 3%, 16% fewer tool calls | none of these — all removed |
| Scope | GEOS + "a small OpenFOAM transfer study" | GEOS + OpenFOAM + LAMMPS, framed as an interface-dependence *finding* |
| Contribution claim | benchmark + component evaluation + cautionary findings | "adapt an existing coding agent rather than rebuild the agent" |
| Jargon load | high | markedly lower |

Four claims were deleted from the abstract and never restored: **"roughly 16% fewer tool calls"**, **"about 3% of under-specified trials"**, **"at no added wall-clock cost"**, and (added Jun 8, removed Jun 25) **"TreeSim above 0.90"** and **"a roughly 10% relative gain"**. [C `jun5_changelist.md:7-9`, `jun8_changelist.md`; V absence in `siga_arxiv_2.tex:98`]

### Intro reframing — exact quotes

A's positioning (`neurips_2026.tex:82`):
> "We take Claude Code as a fixed coding harness… We study how much of the gap to a usable GEOS setup assistant can be closed by a **Simulator-Interface Grounding Adapter (SIGA)**…"

B's positioning (`siga_arxiv_2.tex:126`):
> "Many of these systems build simulator specific agent loops from scratch… We study a different design point: **adapt an existing coding agent rather than rebuild the agent**… What they lack is the simulator executable contract… Preserving the native coding agent harness also preserves the tool use and self correction behavior that frontier models learn inside that harness."

B adds a "why this target" argument absent from A (`siga_arxiv_2.tex:122`):
> "We view simulator configuration as a valuable first target for AI for science because it is **important, bounded, and verifiable**… It is verifiable because the output is an artifact that can be parsed, validated, compared to reference decks, **and eventually executed**."

Note the last three words: B's own framing paragraph concedes that execution is future tense.

---

## 2. Section-by-section structural diff

| Section | A (`neurips_2026.tex`) | B (`siga_arxiv_2.tex`) | What changed |
|---|---|---|---|
| Title/authors | :52, anon | :81, 5 named authors | Title changed; de-anonymized |
| Abstract | :66 | :98 | Rewritten; de-jargoned; 4 claims dropped; 40×→16× |
| 1 Introduction | :71 | :103 | **Fully rewritten twice** (Jun 5, Jun 25). Four-findings bold list deleted; new "important, bounded, verifiable" argument; new "Our contributions are threefold" |
| 2 Related work | :97 | :139 | +MetaOpenFOAM as comparator; **new "harness-as-code / meta-harness" paragraph** with 4 new cites; `kim2024mdagents` removed (MDAgents is medical, not MD) |
| 3 Background: GEOS as DSL | :108 | :154 | Mostly intact; corrected — a *deck* is no longer called a DSL, the *language* is [C `jun7_changelist.md:37-41`] |
| 4 Method | :115 | :161 | **Restructured from 2 → 3 subsections.** A: "System overview and adaptation factors" + "Resolution-IV factorial". B: "Overview" (motivation + minimality), "The grounding adapter" (**new formalism**: $H_0=(c_0,\mathcal T_0,\mathrm{stop}_0)$, Eq. `adapter`), "Self-evolving the adapter" (**new** Eq. `selfevolve`). S and X merged into one paragraph as "two faces of validator-driven self-refinement" |
| 5 Evaluation setup / Experiments | :164 `\section{Evaluation setup}` | :237 `\section{Experiments}` | Renamed. **Five explicit RQs added** (:250-253). Benchmark/metric/baselines subsections commented out and re-prosed (:295-307 commented). **TreeSim now formally defined in main text** with Eq. `treesim` (α=0.3, β=0.1) |
| 6 Results | :175, 5 subsections | :342, **7 subsections** | +LAMMPS; OpenFOAM promoted to a full main-text table; **`rqanswer` boxes added after every subsection** |
| 6.x order | quality → bottleneck → OpenFOAM → autonomy → human | quality → bottleneck → **human** → autonomy → OpenFOAM → **LAMMPS** | Human baseline promoted ahead of autonomy/transfer |
| 7 Discussion | :263 — **contains Limitations, "what transfers", design recommendations** | — | **Deleted from main body** |
| 7' Broader impact | (a paragraph inside Discussion) | :517 — **the entire main-body section** | Limitations + analysis pushed to App. `app:discussion` |
| 8 Conclusion | :278 | :525 | Rewritten; "harm-reduction regime, not a correctness regime" line **removed**; 36× speedup added |
| App: Benchmark details | :299 | :547 | +"dropping one task" |
| App: **Cell definitions** (`tab:cells`) | :308 | **removed** | "redundant with Table 1" [C `jun5_changelist.md:144`] |
| App: Bottleneck pipeline | :336 | :556 | ~unchanged |
| App: Per-task held-out | :371 (own section) | :591 **section header commented out**, table retained | Demoted |
| App: **Resolution-IV main effects** (`tab:main-effects`) | :398 | **removed** | Numbers moved inline **and corrected** |
| App: Cross-model/cross-harness | :420 | :618 | **Native-plugin-prefix bug paragraph + table note deleted**; +0.164→+0.488 |
| App: OpenFOAM transfer | :452 | :648 | **Rebuilt at 30 tasks**, +MetaOpenFOAM, +cost accounting |
| App: **LAMMPS transfer** | — | :686 | **New** |
| App: **Extended discussion** | — | :742 | **New** — absorbs A's §7 |
| App: Future work | :538 | :757-772 **wrapped in `\iffalse…\fi`** | **Compiled out of the PDF** (verified: "Execution-correctness ladder" appears in `siga_neurips_init_sub.pdf`, 0 hits in `siga_arxiv_2.pdf`) |
| App: **TreeSim full definition** | — | :774 | **New** — parsing, node labels, child matching, scoring recursion |
| App: Implementation details | :555 | :787 | ~unchanged; "filename pending final confirmation" footnote removed |
| App: Autonomy protocol | :568 | :800 | ~unchanged |
| App: Human baseline | :606 | :838 | Names anonymized; **ChatGPT-navigation disclosure deleted**; browser table counts corrected |
| App: Example deck / Efficiency / Cheatsheet / Trajectory | :644/:668/:690/:730 | :874/:898/:920/:960 | Efficiency table **byte-identical**; others ~unchanged |
| NeurIPS checklist | `\input{checklist.tex}`, 2 extra PDF pages | **commented out** | [C `jun8_changelist.md:30`] |

**Page budget consequence:** A's main body is 9 pp (NeurIPS limit). B's is 12 pp. **B is 3 pages over.** [V, `pdftotext` scan for the References heading]

---

## 3. New experiments and results

### 3.1 LAMMPS transfer study — entirely new

- **Present in B only.** `grep -ci lammps` on the submitted PDF → **0** (vs 48 for "OpenFOAM"). [V]
- Source material: `/home/matt/sci/repo3/writing/arxiv/audrey_lammps.md` (Jun 5). Numerically identical to the tex; the `.md` has extra analysis paragraphs compressed into `siga_arxiv_2.tex:737`.
- **Scale:** 9 tasks (`lj_melt`, `lj_melt_minimal`, `lj_solid`, `crack_2d`, `lj_indent`, `couette_flow`, `msd_diffusion`, `nvt_water`, `uniaxial_tension`) × 12 configs × **1 run** = 108 runs. Configs = 6 cells (Vanilla, M+R, M+S, M+R+S, M+S+X, M+R+S+X) × 2 backbones (Claude Sonnet 4.6, `deepseek-v4-flash`), both inside the Claude Code harness. (`siga_arxiv_2.tex:494, 690, 696`)
- **Metric — non-executing.** `siga_arxiv_2.tex:696`, verbatim: *"Each task provides a detailed natural-language specification; **the agent writes the input script without executing LAMMPS.**"* Scoring = (i) a deterministic **regex** check over 11–15 per-task criteria that "verifies presence and rough plausibility, **not value-correctness**", and (ii) an integer 0–10 **LLM judge**, Claude Sonnet 4.6, single pass, explicitly "not fully deterministic at temperature 0".
- **No LAMMPS-native baseline.** Unlike OpenFOAM (Foam-Agent + MetaOpenFOAM), the only comparator is Vanilla per backbone.
- **The judge is one of the two scored backbones** (`:690`: "``Claude'' denotes the Claude Sonnet 4.6 backbone model (also used as the LLM judge)"). Stated as fact, never treated as a confound.
- **The factor design is unbalanced.** M is present in 5 of 6 cells and absent only from Vanilla, so M's "main effect" is arithmetically identical to *any-adapter-vs-vanilla*: DeepSeek M-cells mean (6.89+6.11+6.67+6.00+7.78)/5 = 6.69; 6.69 − 4.56 = **+2.13**, exactly the reported M effect. The same contamination applies to R, S, X, whose "off" groups all contain the Vanilla cell. [V, arithmetic]
- **Results** (`tab:lammps-headline` :505-506; `tab:lammps-percell` :708-720): DeepSeek Vanilla **4.56** → M+R+S+X **7.78** (+3.22); Claude Vanilla **6.33** → M+R **6.89** (+0.56, tie with M+R+S+X). Per-cell Claude: 6.33 / 6.89 / 6.33 / 6.22 / 5.78 / 6.89. Per-cell DeepSeek: 4.56 / 6.89 / 6.11 / 6.67 / 6.00 / 7.78. Factor readout (:727-730) Claude R +0.52, S −0.30, X −0.10, M +0.09; DeepSeek R +1.55, S +0.91, X +0.83, M +2.13. Structural scores ≥ 0.976 across all 12 configs.
- **No LAMMPS artifacts exist in this repo.** No task specs, ground truths, result JSONs, runner, or validator; no `repo3_lammps` sibling (unlike `~/sci/repo3_openfoam`, which exists). The study is not locally reproducible or auditable.
- B's own caveat (`:740`): *"We do not claim this has the same evidentiary weight as the GEOS benchmark; it is single-run, scored by a non-deterministic LLM judge, and uses a different metric."*

### 3.2 OpenFOAM — rebuilt at 6× scale, with partial reversal

| | A (5 tasks) | B (30 tasks, `foamgpt_subset_seed42_n30_hybrid`) |
|---|---|---|
| Tasks | 5, named at `neurips_2026.tex:462` | 30, spanning incompressible/compressible/multiphase/combustion/heat-transfer/lagrangian/mesh/DNS/MD/discrete |
| Runs | 1 | 1 (unchanged) |
| Metric | 0.7·mean_sim + 0.3·coverage | identical |
| Native baselines | Foam-Agent only | Foam-Agent **+ MetaOpenFOAM**, both lint-only |
| Best cell | R+S **0.871** | R+S **0.870** |
| Vanilla | **0.466**, 3/5 coverage | **0.681**, 30/30 coverage |
| Foam-Agent (lint) | 0.569, 3/5 | **0.516**, 19/30, 8 zero-score |
| MetaOpenFOAM (lint) | — | **0.379**, 10/30, 12 zero-score |
| Factor readout | R −0.050, **S +0.328**, X −0.073, **M +0.192** | R +0.005, **S +0.168**, X +0.007, **M −0.007** |
| Catastrophic cell | R+X 0.145, 1/5 coverage | R+X **0.685, 30/30** — the catastrophe vanishes |
| Cost | not reported | **new**: SIGA $23.20 total (270 task-runs) vs Foam-Agent $0.30, MetaOpenFOAM $0.17; B concedes SIGA is "roughly an order of magnitude more expensive per task" |
| Instrumentation | — | B discloses a pre/post-instrumentation shift: "repo3 R+S $0.887\to0.870$" (`:660`) |

**This is the most consequential experimental change, and it is a partial reversal.** A's headline OpenFOAM claim (`neurips_2026.tex:224`) was:

> "every $\mathrm{S}$-enabled cell achieves full required-file coverage with no zero-score failures; Vanilla covers 3/5 and R+X covers 1/5."

B's (`siga_arxiv_2.tex:456`):

> "**every** SIGA cell, **including Vanilla**, produces all required files on all 30 tasks with no zero-score outputs."

The within-SIGA reliability story on OpenFOAM does not survive scale-up; the contrast is relocated to SIGA-vs-native-agents. The author's own changelist says exactly this [C `jun5_changelist.md:84`]. Read plainly: **the 5-task OpenFOAM result in the submitted paper was noise-dominated**, and the S factor's apparent dominance there was roughly half artifact.

### 3.3 Not new but newly formalized

- **TreeSim** gains a main-text equation (`siga_arxiv_2.tex:325`, Eq. `treesim`) and a full appendix (`:774`) covering `<Included>` resolution, `tag[name]` node labels, Jaccard attribute similarity with 1e-6 numeric tolerance, unordered greedy bipartite child matching, α=0.3 interior blend, β=0.1 surplus penalty. A had **no formal definition anywhere**. [V]
- **Self-evolution** gains an objective (Eq. `selfevolve`, `:229`) and a meta-harness framing. But a dedicated appendix (`app:selfevolve` + `tab:se-configs`) was added and **deleted the same day** [C `jun8_changelist.md:93, :132`], so the pipeline remains underspecified.
- **Cross-harness OpenHands** panel exists in both (`tab:cross-cutting-full`).

---

## 4. Changed numbers — full table

Any row marked 🚩 is a number whose *value* moved.

| # | Quantity | A | B | Verified cause |
|---|---|---|---|---|
| 1 🚩 | Across-run σ reduction (abstract + body + discussion) | **≈40×** (`:66, :86, :268`) | **≈16×** (`:98`) / "roughly an order of magnitude" (`:373`) | **No data change.** Table 1 is identical in both: Vanilla σ=0.081, X+M σ=0.005, S+X σ=0.002. A quoted the tightest cell (0.081/0.002=40.5); B quotes X+M (0.081/0.005=16.2). [V arithmetic; C `jun5_changelist.md:21` states the switch explicitly] |
| 2 🚩 | Res-IV main effect **R** on val | **−0.032** (`tab:main-effects`, :414) — and **−0.033** in A's own Limitations (:272), internally inconsistent | **−0.037** (`:388`) | **A was wrong.** I recomputed from the eight factorial val cells (identical in both): R **−0.0368**. B is correct. |
| 3 🚩 | Res-IV main effect **S** | −0.003 | −0.008 | Recomputed: **−0.0077**. B correct. |
| 4 🚩 | Res-IV main effect **X** | +0.007 | +0.011 | Recomputed: **+0.0112**. B correct. |
| 5 🚩 | Res-IV main effect **M** | +0.004 | +0.008 | Recomputed: **+0.0083**. B correct. |
| 6 🚩 | Harness-less recovery (vanilla CC over the 0.333 floor, minimax) | **+0.164** (`:566`) | **+0.488** (`:798`) | **A was wrong by 3×.** `tab:cross-cutting-full` gives minimax Vanilla 0.821; 0.821 − 0.333 = 0.488. [V] |
| 7 🚩 | SE efficiency | abstract: "roughly **16% fewer tool calls**"; body: "SE matches Vanilla on val tools per task (68.9 vs 81.5) and runs about **16% faster**" (:220) | "SE makes fewer tool calls than Vanilla on val (68.9 vs 81.5, **−15.5%**) but **more on held-out-eval (97.4 vs 90.5, +7.6%)**; the val efficiency does not transfer" (`:401`) | **`tab:efficiency` is byte-identical in both files.** A cherry-picked the val column. B corrects it; claim dropped from the abstract. [V] |
| 8 🚩 | Task-split arithmetic | "The 46 tasks are split into 10 held-out-eval, 18 distillation, and 17 validation-selection" (= **45**) (:161) | "From the 46-task pool we reserve 10 / 18 / 17…, **dropping one task**" (`:293`) | Arithmetic fix [V + C `jun8_changelist.md:73`] |
| 9 🚩 | Human-baseline speedup, abstract | "between **8 and 36 times** as long" | "about five minutes … about three hours" (≈36×; 36× also at `:437`, `:528`) | The 8× lower bound (1-hour-budget participants) is dropped from the abstract; only the most favorable end survives. Table 2 numbers unchanged. [V] |
| 10 🚩 | Browser-history table (`tab:human-browser`), Expert 1 extended | GEOS docs **89**, GitHub 21, Search 6, Other **7** (sum 123 ≠ stated total 106) | docs **73**, GitHub 21, Search 6, Other **6** (sum = 106) | Arithmetic fix [C `jun8_changelist.md:76`; V B's row sums] |
| 11 🚩 | Claude LAMMPS effect bound | n/a | "at most **0.52**" | Intermediate drafts said "within ±0.5" while R = +0.52 [C] |
| 12 🚩 | OpenFOAM: **all** values | see §3.2 | see §3.2 | Benchmark replaced 5→30 tasks |
| 13 | Held-out-eval quality | "+7 percentage points"; Table 0.720→0.789 | "TreeSim from 0.720 to 0.789" | **Value unchanged** (0.069 ≈ 7pp); only presentation |
| 14 | GEOS Table 1 (all 11 cells, val + held-out) | `:186-207` | `:365-384` | **Identical, cell for cell.** B only adds a component-indicator block and renames SE-prose/SE |
| 15 | Human baseline Table 2 | `:245-256` | `:418-430` | **Identical numbers**; adds ↑/↓ grouping headers; P1/P2 → Expert 1/2 |
| 16 | Cross-model panel | `:432-441` | `:630-639` | **Identical numbers**; A's caption note "[was *0.392*]" **deleted** |
| 17 | Bottleneck counts (6→3 missing_block, 12/11/15 bad_attribute_value, 9→11 extra_block, 4→7 hallucinated_extras, 7/6/6 perfect) | `:216` | `:397` | Unchanged |
| 18 | Autonomy (3.1%, 64 trials, 1/32 neutral rerun, 15/26 grep-findable, 0.829/0.835/0.921) | `:229-231` | `:449` | Unchanged |
| 19 | Efficiency table | `:678-686` | `:908-916` | **Byte-identical** |
| 20 | Dropped quantitative control | "The remaining seven held-out-eval tasks have a Vanilla mean of **0.898**, indistinguishable from val's 0.910" (:211) | replaced by "within-noise differences on the remaining tasks" (`:380`) | **Removed.** A quantitative honesty statement became a qualitative one |
| 21 | `yue2025foamagent` bib year | 2026 | 2025 | Corrected (arXiv:2505.04997) [C] |

**Summary of the numeric picture:** every number that moved either (a) moved because the underlying experiment was replaced (OpenFOAM), (b) moved because A contained an arithmetic error (rows 2–6, 8, 10), or (c) moved because A cherry-picked (rows 1, 7, 9, 20). **I found no case where B reports a number that A got right and B got wrong.** The direction of travel is uniformly toward correctness and conservatism. That is good news for a rebuttal — but it means the submitted PDF contains at least five verifiably wrong numbers that a determined reviewer could recompute from the submitted paper's own tables.

---

## 5. Figures

| | A | B |
|---|---|---|
| Fig. 1 image | `assets/siga_fig1.png` (0.92\textwidth) | `assets/siga_fig1_redux4.png` (\textwidth) — swapped Jun 25, undocumented; prior `siga_f1_jun5.png` left commented at `:107` |
| Fig. 1 caption | "**Comparison of manual and Simulator-Interface Grounding Adapter (SIGA) workflows.** While the manual workflow **(a)** requires hours of iteratively navigating documentation and debugging, the SIGA workflow **(b)** reduces setup to minutes… Both approaches **(c)** ultimately generate a valid XML deck to execute complex, coupled multi-physics simulations in the GEOSX engine." | "Illustrative example of advanced tooling usage bottleneck for the geophysics domain. Here, the GEOS simulator's extensive documentation helps as a translation guide for its elaborate configuration that is a custom XML (domain specific language/DSL) to produce results such as simulating carbon sequestration in deep saline formations (top right) or reservoir flow in heterogeneous hydrocarbon (bottom right)." |
| Fig. 2 image | `assets/siga_fig2.png` | `assets/siga_f2.png` |
| Fig. 2 caption | "**Execution trace of the SIGA agent loop.** … until the deck is structurally valid and ready for simulation." | "**The SIGA method.** … a frozen harness $H_0$ wrapping a frozen model $\pi$ … The SIGA adapter grounds this loop at three interfaces … The *self-evolution* loop (dashed) reflects offline on logged trajectories…" |
| Count | 2 figures | 2 figures |

Two observations:

1. **Fig. 1's caption got *less* informative, not more.** A's caption explicitly walked the reader through the manual-vs-SIGA contrast in three labelled panels — precisely the kind of scaffolding kEdh asked for. B's caption is a descriptive gloss of a picture. For a NeurIPS revision aimed at a clarity complaint, this is a regression. [I]
2. **Fig. 2 has a known, unfixed overclaim.** The author's own changelist flags it: Fig. 2 shows "simulation outputs" / "post-process artifacts" although decks are never executed; *"Can't fix in TeX — needs the figure source (`assets/siga_f2.png`) regenerated"* [C `jun8_changelist.md:122`]. It is still unfixed in `siga_arxiv_2.tex`. Given that the AC's headline objection is "you never execute anything", a method figure that depicts execution outputs is an active liability.

Asset directories: `neurips/assets/` has 5 files (2 PNGs); `arxiv/assets/` has 15 (many superseded drafts). The shipped `arxiv_upload/assets/` contains only `siga_fig1_redux4.png`, `siga_f2.png`, two XMLs, and the trajectory text.

---

## 6. Related work and bibliography

`references.bib`: A 48 entries → B 56.

**Added (9):**
| Key | Role |
|---|---|
| `LAMMPS` | LAMMPS simulator citation (used in `:494` transfer section) |
| `weller1998tensorial` | OpenFOAM citation (new in intro) |
| `lewis2021rag` | RAG properly cited — direct response to internal feedback that RAG was used but never defined |
| `lee2026metaharness` | meta-harness design; now anchors the formalism (Eqs. `adapter`, `selfevolve`) |
| `ning2026codeagentharness` | harness-as-code |
| `lin2026agenticharnessengineer` | agentic harness engineering |
| `yang2026skillopt` | skill optimization |
| `cursor2026composer2` | cited for "models learn tool-use inside a harness" |
| `mirza2024chembench` | replaces `mirza2025chembench` (year fix) |

**Removed (1):** `mirza2025chembench` (superseded). Additionally `kim2024mdagents` was dropped from the MD-agent list in the prose — MDAgents is *medical* decision-making, not molecular dynamics [C `jun8_changelist.md:84`]. Compiled `.bbl` count: 37 → 36.

**Related-work prose deltas:**
- A's self-evolving-agents paragraph was largely a list. B adds a substantive positioning paragraph on **treating the agent's own scaffolding as a learnable object** and explicitly locates SE inside that subfield: *"Our self-evolved variant adopts this reflect-and-rewrite paradigm… Our focus is different: we study whether such self-revision helps on a task whose bottleneck is domain knowledge and procedural guidance rather than general programming competence."* (`:150`)
- MetaOpenFOAM promoted to a named comparator alongside Foam-Agent (`:145`).
- **Potential defect:** two different LAMMPS bibliography keys coexist and are both cited — `holbrook2026lammps` in the intro (`:118`) and `LAMMPS` in the transfer section (`:494`). Worth reconciling before any further posting. [V]

---

## 7. Limitations section

**This is the most important structural regression.**

- **A**: Limitations live in the **main body**, §7 Discussion, `neurips_2026.tex:272`, in a paragraph that names: the X/S conflation, n=3 on one model, single-seed cross-model, no OpenCode, OpenFOAM 5 tasks/n=1 with lint-only Foam-Agent, *"TreeSim is structural, not physical: a 0.8 deck is not guaranteed to run"*, and **the native-plugin-prefix bug contaminating the R = −0.033 estimate**.
- **B**: The main body has no limitations section. Main-body §7 is `Broader impact` only (`:517`), a single paragraph that ends: *"Limitations, an extended cross-simulator analysis, the procedural-memory-tool negative result, and concrete adapter-design recommendations are collected in App.~\ref{app:discussion}."* The Limitations paragraph now lives at `:749`, page ~14 of a 31-page PDF.

**Content deltas inside the Limitations paragraph:**

| Item | A | B |
|---|---|---|
| X/S conflation | ✅ | ✅ |
| n=3 on one model | ✅ ("seeds") | ✅ ("runs") |
| Cross-model single-seed | ✅ | ✅ ("single-run") |
| Cross-harness | "we did not run OpenCode" | "We validated cross-harness transfer only on OpenHands; time and cost constraints prevented us from extending to the other coding harnesses now available (e.g. OpenCode, Pi, Hermes Agent)" — softened, no longer singles out one harness [C] |
| Transfer studies | "OpenFOAM is 5 tasks, n=1" | "OpenFOAM (30 tasks) … and LAMMPS (9 tasks) is scored by a non-deterministic LLM judge" |
| "TreeSim is structural, not physical: a 0.8 deck is not guaranteed to run" | ✅ **main body** | ✅ **appendix** |
| **Native-plugin-prefix bug** | ✅ named, with the contaminated estimate | ❌ **deleted** |
| Held-out lift concentrated in 2 tasks | ❌ | ✅ **new** |
| Human baseline n=2, one task | ❌ (in appendix caveats only) | ✅ **new, in Limitations** |
| Autonomy "supervisor" was an LLM simulator, not a human | ❌ | ✅ **new** [C `jun7_changelist.md:71`] |

So B's limitations paragraph is *better written and adds three honest admissions* — but it is **less prominent** and it **deletes the one item a reviewer asked about by name**.

---

## 8. Appendix deltas — summary

**Added:** LAMMPS transfer study (`:686`); Extended discussion (`:742`, absorbing A's §7 Discussion); TreeSim full definition (`:774`).

**Removed / suppressed:**
- `Cell definitions` + `tab:cells` — deleted [C: "redundant with Table 1"].
- `Resolution-IV main effects on val` + `tab:main-effects` — deleted (numbers moved inline and corrected). Note the stated Jun-6 rationale for deleting it (*"body already states R≈−0.032 and X/M/S within ±0.007"*) was itself based on the numbers that turned out to be wrong.
- `Per-task held-out-eval results` — section header commented out (`:591`), table retained under the bottleneck appendix.
- `Future work — open follow-ups` — wrapped in `\iffalse…\fi` at `:757-772`, "commented out per advisor". **Compiled out of the arXiv PDF.** This removed six items from public view, including:
  - *"**Execution-correctness ladder.** Run a sample of agent-produced decks through actual GEOS execution to convert TreeSim into a runnability metric. Even a small panel (5 tasks × 2 cells × 1 run) would convert the structural-similarity metric into a ladder."*
  - *"**Clean re-run of autocamp factorial cells with the prefix-gate fix**… Estimate: ~1.5h wall-clock, low API spend."* (A's version; B's rewritten version drops this item entirely.)
  - *"Multi-run native baselines in execute mode."*
- `Self-evolution pipeline details` (`app:selfevolve` + `tab:se-configs`) — added and deleted the same day, Jun 8 [C `:93`, `:132`]. GPT's review had named self-evolution underspecification as one of "the two biggest reproducibility gaps"; the fix was reverted within hours.
- **ChatGPT-navigation disclosure** in the human-baseline appendix — deleted [C `jun5_changelist.md:150`]. A disclosed that Expert 1's extended session included one navigation to `chatgpt.com` and argued it did not affect the deck. B does not mention it, while retaining the extended-session score (0.931) and asserting in `tab:human-browser`'s caption that *"No participant visited any LLM chatbot"* — which is now the only statement on the matter, and it is scoped to the one-hour sessions. [V: 0 hits for "chatgpt" in `siga_arxiv_2.tex`]

---

## 9. Everything that was removed or weakened (consolidated)

This section exists because "the arXiv version is strictly better" is the natural but wrong summary.

**Removed transparency:**
1. **Native-plugin-prefix bug: fully deleted.** A devoted a table caption note (`[was 0.392]`) and a ~150-word paragraph to it, naming `src/runner/prompts/native_plugin_prefix.txt`, `src/runner/orchestrator.py`, the RN-006 adversarial review, and the corrected re-run (0.867, 0 failures). B retains the corrected 0.867 number with **no provenance at all**. Stated rationale: *"overstated, solved by new results"* [C `jun5_changelist.md:143`]. Reviewer gep1 raised this as one of two **score-moving** questions.
2. **Future-work appendix compiled out**, taking the execution-ladder plan with it.
3. **ChatGPT-navigation disclosure deleted.**
4. **The "[was 0.392]" table-caption annotation deleted.**
5. **The 0.898 seven-task control statement deleted.**

**Weakened or softened claims** (mostly appropriate, but they are concessions a reviewer can quote back):
6. Human-baseline protocol: A "no LLM chatbots or web search" → B "working primarily from the GEOS documentation and source tree"; the instruction is now described as discouraged rather than enforced [C `jun5_changelist.md:123`].
7. Participant description: A "multi-year subsurface-modelling experience" → B "grad-level geoscientists" — a **downgrade of the claimed expertise level** of the human baseline.
8. A's blunt framings deleted: *"The harness operates in a harm-reduction regime, not a correctness regime"* (:216) and *"raise the floor rather than solve simulator reasoning"* [C `jun5_changelist.md:90-94`, tone pass described as reversing "honest and humble to a fault"].
9. RQ2 attribute-level residue reframed from a limitation into "the next problem to solve rather than a shortcoming of the approach" (`:399`) — with a new argument that the flat `bad_attribute_value` count is "partly mechanical".
10. §5.3 "the returned workspace is **executable** or at least structurally inspectable" → "…is at least structurally inspectable" — the word **executable** was deliberately removed [C `jun8_changelist.md:100`].
11. §6.2 "since schema validation **requires** these blocks" → "the validator's structural pressure discourages finishing without them" (xmllint checks XSD validity, not required-block presence) [C `:99`].
12. Bold formatting deliberately withdrawn from negative findings so that "bold is reserved for positive findings" [C `jun5_changelist.md:94`].

**Known-unfixed items still live in B:**
13. **Figure 2 still depicts simulation outputs / post-process artifacts** for decks that are never run.
14. **Expert 1's file-level score *drops* 0.812 → 0.689 between the 1-hour and the extended session** (`tab:human-baseline`) with no explanation in either version. The internal review rated this **blocking**; the changelist records it as deliberately skipped [C `claude_feedback.md:9`, `jun8_changelist.md:125`]. A reviewer noticing that a human got *worse* at the file level after three hours will ask.
15. Self-evolution pipeline remains underspecified (appendix added then reverted).
16. Two coexisting LAMMPS bib keys.
17. `tab:bottleneck` caption says n=29–30 while a column header says n=30.

**Also stale, if it matters:** `writing/poster/REPORT.md` (Jun 3) is built entirely on pre-Jun-5 numbers — it states "adapters collapse across-seed σ **~10×**" (a *third* value for the same claim, alongside 40× and 16×) and reproduces the 5-task OpenFOAM figures including "R+X dives to −0.321 with 1/5 coverage" and "S +0.328 dominant", all of which are now superseded.
