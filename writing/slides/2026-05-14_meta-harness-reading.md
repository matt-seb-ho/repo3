---
marp: true
theme: default
paginate: true
size: 16:9
header: 'Meta-harness reading + Paper 2 proposals — 2026-05-14'
style: |
  section { font-size: 22px; }
  h1 { font-size: 32px; }
  h2 { font-size: 26px; }
  h3 { font-size: 22px; }
  table { font-size: 17px; }
  code { font-size: 17px; }
  .small { font-size: 17px; }
  .tiny { font-size: 14px; }
  .pos { color: #0a7; }
  .neg { color: #c33; }
  .muted { color: #666; }
  .box { border: 1px solid #888; padding: 6px 12px; border-radius: 4px; background: #f6f6f6; }
---

<!-- _class: lead -->

# Documentation-grounded meta-harness
## Reading round-up + Paper-2 method proposals

**Inputs**

- Meta-Harness (Lee et al. 2026) — `LN-003`
- MCE (Ye et al. 2026)
- AHE (Lin et al. 2026)
- **SkillFoundry (Shen et al. 2026)** — newly read, `LN-004`
- MoSciBench (Liu et al. 2026)

**Goal of today's deck.** Where is the white-space for Paper 2, and which concrete novelties land in it?

---

# TL;DR

1. None of the four closest baselines treats **documentation as structured substrate the meta-harness reasons over**. Closest is SkillFoundry's tree — but that tree is over *capabilities*, with docs as one input among many.
2. MoSciBench is a warning: naïve "add domain knowledge" *hurts* (48.4 → 44.9). Workflow scaffolding *helps* (48.4 → 54.1). **Structure has to do real work.**
3. The Paper-2 hook: *meta reads docs to build a harness that reads the docs usefully* — both layers grounded in the same docs.
4. Recommended core: **N1 typed index + N2 bipartite component–section graph + N3 doc-anchored attribution + N5 doc-as-soft-oracle**. Falsifiable ablations across all four.

---

# What I actually did

- Downloaded SkillFoundry PDF (arXiv 2604.03964) → `docs/literature/skill_foundry_2604.03964.pdf`.
- Read end-to-end, including appendix, including prompt templates.
- Wrote `LN-004_skill-foundry.md` — personal note, **not** the GPT summary in `meta_harness_reading/`.
- Re-read the four prior GPT notes (`meta_harness.md`, `meta_context_engineering.md`, `observability_driven_evolution.md`, `moscibench.md`).
- Wrote design memo `docs/2026-05-14_doc-grounded-meta-harness-proposals.md`.

Per stored preference: did **not** dispatch literature-scout — read sources directly.

---

# What SkillFoundry actually is (vs the GPT summary)

The GPT note in `meta_harness_reading/` is roughly right on the pipeline but misses **one architectural detail** that matters for our framing:

> SkillFoundry is **NOT** a coding-agent loop in the Meta-Harness sense. It is a **staged GPT-5.4 pipeline with JSON-schema responses at every stage.**

Stages: `tree_check → resource_search → skill_build → skill_test → refresh` → tree_expansion / tree_refinement.

Model allocation by stage:

| Stage | Model | Reasoning |
|---|---|---|
| **resource_search** | GPT-5.4 | **high** |
| tree_check, skill_build, refresh, design_skill | GPT-5.4 | medium |
| skill_test, layer1_fix, layer2_benchmark, layer2_optimize, novelty_check | GPT-5.4-**mini** | medium |

**Where they spend smarts: resource triage.** Compare MH which spends Opus-4.6 at code-time.

---

# SkillFoundry headline numbers

- **Library**: 286 skills · 27 domains · 254 subdomains · 394 resources · 71.1% novel vs SkillHub/SkillSMP.
- **MoSciBench** (Codex, with/without SF):
  - avg Repo-Acc 61.2 → 66.7
  - avg Paper-Acc 43.9 → 53.1
  - 5/6 datasets up, 1 unchanged
  - **exec stays at 100% throughout** → gains are *procedural*, not executability.
- **Cell-type annotation (MERFISH heart)**:
  - Codex: 81.1% coverage / 68.5% acc
  - Codex + SF: 99.2% / 82.9%
  - SpatialAgent (curated, external ref): 100% / 87.1%
- **scDRS transfer into Biomni** (blinded expert review):
  - Biomni alone: qual 3-4/7, RMSE 0.16 — often **drops the `filter-data` param**
  - Biomni + SF: **qual 7/7 best run**, RMSE 0.02

scDRS is their strongest experiment — external agent + blinded review + workflow not in Biomni's preset catalog.

---

# Key quote — the doc-grounding overlap

> "Resource search prioritizes **authoritative artifacts**, such as official documentation, maintained repositories, package references, workflows, notebooks, and method papers, so that skill induction is grounded in reliable sources rather than generic web text."  
> — SkillFoundry §3.3

This is the **overlap** with our project. But note what it isn't:

- Docs are a **priority list entry**, not a structural commitment.
- Manuals are not modeled differently from a maintained GitHub repo.
- The domain-knowledge tree axis is **capability**, not document section.

Our angle has to add structure they don't.

---

# How the four baselines treat documentation

| System | Doc role | Doc structure exploited? | Outer proposer |
|---|---|---|---|
| **Meta-Harness** | Optional "offline experience" dropped into FS as another directory | **No — flat** | Claude Code (Opus 4.6) free FS access |
| **MCE** | Not a first-class lever | No — generic file/code substrate | MiniMax M2.1 agentic crossover |
| **AHE** | Not modeled — signal comes from distilled trajectories | No — observability is over traces | GPT-5.4-high evolve-agent over NexAU |
| **SkillFoundry** | "Authoritative artifacts" *priority* | **Partial — tree is over capabilities** | Staged GPT-5.4 pipeline with JSON schemas |
| **MoSciBench** (eval) | Negative result: naïve injection *hurts* | n/a | n/a |

**Two takeaways:**

1. No-one treats docs as *structured substrate the meta-harness reasons over*.
2. MoSciBench tells us we can't just dump the manual in — structure must do work.

This is the white-space.

---

# Where we sit on the design axes

| Paper | Outer proposer | Outer interface | Core bet |
|---|---|---|---|
| Meta-Harness | Coding agent (Opus 4.6) | Free FS access | Unrestricted diagnostic reasoning |
| MCE | Agentic crossover | File/code substrate | Learnable skill recombination |
| AHE | Evolve-agent | NexAU file-level edit + distilled traces | Observability + falsifiable edits |
| SkillFoundry | Staged JSON-schema pipeline | Domain tree | Structured branch search |

**Our novelty case is sharpest at the MH end** (where docs are otherwise unstructured) and weakest at the SF end (where docs are already inside a staged pipeline). But the *implementation* is easier on the SF side — JSON schemas give us natural seams to plug in doc-typed components.

Recommended: **staged pipeline + doc-grounded structure**. Lean implementation, sharp comparison to MH on novelty.

---

# Paper-2 problem statement (draft)

> **Given** an elaborate scientific tool (e.g., GEOS, FEniCS, MOOSE) and its authoritative documentation,  
> **automatically discover an agent harness** that operates the tool with measurable fidelity to its documented behavior,  
> **using a meta-harness procedure that co-evolves**  
> (a) the harness's *runtime use of documentation* and  
> (b) a *structured representation of the documentation itself*.

**Distinction from SkillFoundry**: SF is **breadth-first** (many small skills across many subdomains). We're **depth-first** (one tightly-coupled harness for one elaborate tool, with internal components that *jointly* read the same manual).

**Distinction from Meta-Harness**: MH treats docs as flat FS contents. We claim *typed* and *bipartite-grounded* doc structure beats flat-FS even when the proposer is given identical compute.

---

# Proposed novelties — menu

Nine candidates. Each: claim, why-novel-vs-baselines, how-to-falsify.

| ID | Name | Strength | In core? |
|---|---|---|---|
| **N1** | Typed document index as first-class component | High | **Yes** |
| **N2** | Bipartite component–section graph | High | **Yes** |
| **N3** | Doc-anchored failure attribution | High | **Yes** |
| N4 | Doc-bootstrapped seed harness | Medium | Optional |
| **N5** | Doc-as-soft-oracle for tests | High | **Yes** |
| N6 | Doc-utility-weighted search budget | Medium | Optional |
| N7 | Symmetric doc-consultation traces | High but ambitious | Stretch |
| N8 | Negative doc knowledge as constraints | Medium | Future work |
| N9 | Doc-diff as longitudinal signal | Low for Paper 2 | Limitations |

Next slides drill into the four-of-nine recommended core.

---

# N1 — Typed document index

**Claim.** Manuals have stable typed structure: **schema/reference** vs **example/tutorial** vs **concept/background** vs **deprecation/warning**. Expose this typing to the harness as a typed multi-index, and let the meta-harness *edit* the indices.

**Why novel.**

- MH: flat doc dump.
- SF: prioritizes authoritative artifacts but doesn't carry typing through to runtime.
- MCE/AHE: don't model docs at all.

**Falsification.** 3-way ablation: (a) single flat index, (b) typed multi-index, (c) typed + editable. Predict c > b > a. The c→b gap quantifies value of meta-level editing.

**Risk.** Some manuals are messy prose. Empirically checkable up-front on GEOS / FEniCS / MOOSE.

---

# N2 — Bipartite component–section graph

**Claim.** Maintain an explicit, editable bipartite graph:

- nodes-left: harness **components** (skills, prompts, retrieval fns, middleware)
- nodes-right: doc **sections** they cite or serve
- both sides editable, both sides have coverage state

**Why novel.** AHE's three observability pillars are (component, experience, decision). This is a **fourth pillar — *grounding*** — that AHE explicitly doesn't model. SF's tree is single-sided (capability coverage, not bipartite).

**Concrete payoff.**

- Detect **dead sections** (never cited) → prune or build coverage.
- Detect **ungrounded components** (no citation) → flag for justification or removal.
- Every code change *must* declare which sections it depends on or invalidates.

**Falsification.** Compare with/without graph on regression rate and held-out sub-area transfer. If neither moves, complexity isn't earning its keep.

---

# N3 — Doc-anchored failure attribution

**Setup.** AHE finding: evolve-agent predicts fixes okay (precision 33.7%, recall 51.4%) but predicts **regressions near-randomly** (P 11.8%, R 11.1%).

**Claim.** Constrain attribution to a **3-way doc-grounded classification**:

  (a) section the harness should have consulted but didn't,
  (b) section it consulted but misinterpreted,
  (c) genuine gap — section doesn't exist in docs.

**Why novel.** Converts open-ended causal reasoning into a bounded, verifiable classification. None of MH / MCE / AHE / SF do this.

**Falsification.** Re-run AHE's regression-prediction analysis. Target: regression-prediction precision >25% (random ≈ 5.6%, AHE free-form ≈ 11.8%).

---

# N5 — Documentation as soft test oracle

**Claim.** Manuals prescribe workflows ("the correct way to construct X is…") and prohibit patterns ("do not nest A inside B"). Extract both:

- **Adherence tests** — does harness output match documented workflow shape?
- **Constraint tests** — does harness ever violate a documented prohibition?

This is a *fourth* validation layer beyond SkillFoundry's exec / system / synthetic.

**Why this matters.** Available *even when downstream ground truth is expensive* (which is the rule for elaborate scientific tools — running real GEOS / FEniCS per iteration doesn't scale).

**Falsification.** Does adherence/constraint passing **correlate** with downstream task success?

- High correlation → cheap proxy, big efficiency win.
- Low correlation → docs and behavior disagree — interesting but undermines the proxy.

---

# Recommended Paper-2 core

**Question the four novelties collectively answer:**

> Does explicit doc-structure (N1 typing + N2 bipartite grounding + N3 anchored attribution + N5 adherence tests) beat both the unstructured MH upper-bound proposer and the capability-tree SF middle-ground?

**Why pick these four together:**

- N1 earns the doc-structure framing — lowest-risk to implement.
- N2 earns the **symmetric** meta/harness story the project emphasized.
- N3 directly attacks AHE's weakest published number.
- N5 gives us a test surface that works when downstream ground truth is expensive — practical for real scientific tools.

Ablation lattice across the four is small (8 meaningful conditions), and the core question is sharp.

---

# Evaluation shape (borrowed from SF + Cell-Voyager)

**In-tool eval (primary).** Build doc-grounded harness for tool T₁ (GEOS). Compare:

- **Paper-1 SIA recipe** (manual adapter — our own ceiling)
- **MH-baseline** (flat doc directory + free FS coding agent)
- **SF-baseline** (capability tree, docs as artifact)
- **AHE-baseline** (trajectory-distilled, no doc grounding)

Metrics: input-file fidelity, end-to-end task success, blinded expert review of generated artifacts (Cell-Voyager / scDRS style).

**Cross-tool transfer (stretch).** Same meta-harness procedure → tool T₂ (FEniCS or MOOSE). This is the generalization claim Paper 2 needs.

**Doc-only ablation.** Vary fraction of manual visible to meta-harness. Performance should degrade smoothly with less doc access. Flat curve → no doc-grounding story.

---

# Where we land vs each baseline

| Baseline | Their bet | Our delta |
|---|---|---|
| **Meta-Harness** | Unrestricted coding-agent diagnosis | Add typed doc structure + bipartite grounding *without* losing diagnostic richness |
| **MCE** | Skill recombination | We agree skills matter; we make doc grounding a first-class constraint on skill construction |
| **AHE** | Component / experience / decision observability | Add **grounding** as a fourth observability pillar; attack their regression-prediction weakness |
| **SkillFoundry** | Capability tree + staged pipeline | Switch the tree axis from capability → doc section; depth-first single-tool instead of breadth-first |
| **MoSciBench** | "Workflow scaffolding > naïve knowledge" | We treat docs as scaffold-source, not knowledge-injection — directly addresses their negative result |

The story compresses well: **"docs are a substrate, not a corpus."**

---

# Open questions / decisions needed

1. **Proposer style.** Coding-agent (MH-like) vs staged-pipeline (SF-like)?
   - Recommend **staged** — per-stage JSON schemas give natural seams for N1/N2/N3.
   - But this gives up MH's diagnostic richness. Worth a focused ablation.
2. **Doc editability.** SF's tree is editable; MH's offline dir is read-only by convention. Should the meta-harness rewrite source docs?
   - Recommend: **editable derived summaries**, read-only source manuals.
3. **Tool choice.** Which of GEOS / FEniCS / MOOSE has the most cleanly structured documentation?
   - Empirical question — check up-front, pick the cleanest.
4. **N7 (symmetric traces).** Land it in Paper 2 or save for a focused follow-up?
   - Recommend save unless N1/N2/N3/N5 finish ahead of schedule.

---

# Concrete next steps

1. **Clone SkillFoundry repo** (`ma-compbio-lab/SkillFoundry`). Read prompts + JSON schemas in code, not just the appendix. Confirm whether `resource_search` ever parses doc structure or treats pages as plain text.
2. **Read AHE's Agent Debugger** implementation — closest prior art to a doc-grounded attribution layer.
3. **Probe target tool docs** (GEOS / FEniCS / MOOSE). Which manual has the cleanest schema / tutorial / reference typing?
4. **Design smallest Paper-2 contribution** that earns N1+N2+N3+N5 on one tool.
5. **Run `/adversarial-review`** on this proposal once it's solid. Has not been adversarially reviewed yet.

---

# Files written today

- `docs/literature/skill_foundry_2604.03964.pdf` — paper
- `docs/literature/LN-004_skill-foundry.md` — personal note
- `docs/2026-05-14_doc-grounded-meta-harness-proposals.md` — design memo (the full version of this deck)
- `writing/slides/2026-05-14_meta-harness-reading.md` — this deck

**Status.** Draft. Not adversarially reviewed. Numbers in the SkillFoundry summary are from the paper directly; the four-paper comparisons are my characterization and could be wrong on detail — flag what looks off.
