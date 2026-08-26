---
marp: true
theme: default
paginate: true
size: 16:9
header: 'GEOS coding-agent project — advisor sync, 2026-05-04'
style: |
  section { font-size: 22px; }
  h1 { font-size: 34px; }
  h2 { font-size: 28px; }
  table { font-size: 18px; }
  code { font-size: 18px; }
  .small { font-size: 18px; }
  .tiny { font-size: 14px; }
  .pos { color: #0a7; }
  .neg { color: #c33; }
  .muted { color: #666; }
---

<!-- _class: lead -->

# Coding agents for advanced scientific software
## Advisor sync — 2026-05-04

**Agenda**

1. Latest experiments — auto campaign, cross-model / cross-harness, autonomy
2. Paper changes — title, framing, headline structure
3. Venue decision — **NeurIPS main vs. ICML AI4Science workshop**
4. End-of-May "method paper" direction
5. Items for discussion

---

# Recap of the recipe — Simulator Interface Adapter (SIA)

**Question**: how much can a fixed coding harness (Claude Code) absorb of the deck-authoring bottleneck?

**Adapter** = four simulator-agnostic components plugged into CC's documented extension surface (hooks / MCP / `--append-system-prompt` / skills):

- **R**etrieval — three RAG channels over docs, schema, examples
- **S**top-hook — parse-check + `xmllint --schema` at every termination
- e**X**ec validator MCP — agent-callable `xmllint`
- **M**emory cheatsheet — distilled vocab in the system prompt
- *(SE = self-evolved monolithic plugin, for comparison)*

We measure *each component in isolation and combination*, on the same harness, same backbone, same task set. **Not a new algorithm — a design-space study.**

---

# Resolution-IV factorial — what is it and why

We have **4 binary factors** (R, S, X, M). Full $2^4$ = 16 cells × 3 seeds × 2 task sets = expensive.

A **fractional factorial** runs only a *carefully chosen* subset of cells so that all *main effects* (R alone, S alone, …) can still be estimated unbiasedly, by deliberately confounding *high-order interactions* with each other instead.

**Resolution-IV** $2^{4-1}$ design (8 cells):

- main effects are *not* confounded with any 2-factor interaction
- 2-factor interactions are confounded with *each other*
- generator: `D = ABC` ⇒ run cells where `RSXM ∈ {0000, 0011, 0101, 0110, 1001, 1010, 1100, 1111}`
- gives 8 cells × 3 seeds = 24 runs instead of 48; **half the compute, all 4 main effects**

---

# Why factorial instead of greedy "add-one-at-a-time"?

|  | **Greedy / build-up** | **Resolution-IV factorial** |
|---|---|---|
| Search order | one factor at a time, then keep best | all 8 cells run independently |
| What you measure | a *path* through design space | the **average effect** of each factor across many backgrounds |
| Interactions | invisible; you commit to a config before checking | second-order pairs estimated together |
| Risk of local optima | **high** (e.g. R looks bad with hook off, but might be good with hook on — greedy will discard R) | low (R judged across 4 different on/off configurations of the rest) |
| Compute | linear in #factors + a few extras | $2^{k-1}$, but *full* design space |

**Concrete win for us**: the Resolution-IV result said *RAG is the only factor that clears noise on val, and it's negative*. A greedy run that started "Vanilla → +R" would have stopped at iter 1 and never tested the X+M combo that actually wins.

---

# Auto campaign — headline (DSv4-flash, n=3)

| set | Vanilla | best | $\Delta$ | who wins |
|---|---:|---:|---:|---|
| val (in-distribution) | 0.910 ± 0.024 | **0.921 ± 0.007** | +0.011 | X+M (xmllint MCP + memory) |
| held-out-eval (OOD) | 0.720 ± 0.081 | **0.789 ± 0.012** | +0.069 | SE (self-evolved monolith) |

**What clears noise**:

- val: only main effect that clears noise is **R, and it's negative** (−0.033)
- held-out-eval: spread is real (~7pp) but *concentrated in 3 hard tasks*; the other 7 tasks score ~0.898 vanilla — indistinguishable from val

**Reliability is the headline** on held-out-eval: σ goes from 0.081 (Vanilla) to 0.005–0.012 across adapter cells. **~40× variance reduction.** Adapters prevent catastrophic seed-level failures rather than raising means.

---

# Cross-model — X+M wins on every backbone

CC × {DSv4-flash, minimax-m2.7, gemini-3-flash-preview}, val, n=1 except DSv4 (n=3).

| backbone | Vanilla | X+M | SE | $\Delta$ X+M − Vanilla |
|---|---:|---:|---:|---:|
| DSv4-flash | 0.910 ± 0.024 | **0.921 ± 0.007** | 0.919 ± 0.020 | <span class="pos">+0.011</span> |
| minimax-m2.7 | 0.821 | **0.867** | 0.861 | <span class="pos">+0.046</span> |
| gemini-3-flash-preview | 0.768 | **0.797** | 0.757 | <span class="pos">+0.029</span> |

**Pattern**: lift size is *inversely* proportional to backbone strength — adapters help most where the baseline is most brittle. Same direction as held-out-eval hard-tail story.

<span class="muted">Caveat: n=1 on minimax/gemini. The minimax × X+M number is *post-bug-fix* — the first launch at 0.392 surfaced a `native_plugin_prefix` injection bug (RN-006) that we caught + fixed; the panel is what made the bug visible.</span>

---

# Cross-harness — adapter transfers to OpenHands

OH × DSv4-flash, val, n=3 (X+M port: ~3h of glue: `--xmllint-mcp` flag, m1u prepend in user msg).

| harness | Vanilla | X+M | $\Delta$ |
|---|---:|---:|---:|
| Claude Code | 0.910 ± 0.024 | 0.921 ± 0.007 | +0.011 |
| OpenHands | 0.856 ± 0.061 | **0.881 ± 0.023** | <span class="pos">+0.025</span> |

- OH underperforms CC by ~4–5pp at both Vanilla and X+M cells (consistent gap)
- **Adapter lift is bigger on OH** (+0.025 vs +0.011) — same harness-strength inverse pattern
- Variance reduction is also ~3× on OH (σ 0.061 → 0.023)

**Implication**: the adapter is portable across CC and OH at the *cost of a few hours of glue*. Stronger harness ≠ no need for adapter — just smaller marginal gain.

---

# Autonomy companion #1 — difficulty pipeline

We rewrite specs into 3 difficulty levels using DSv4-pro, with a tier taxonomy:

| Tier | Examples | Easy | Medium | Hard |
|---|---|:-:|:-:|:-:|
| T1 software defaults | restart freq, log levels, output format | ✓ kept | dropped | dropped |
| T2 standard numerics | Newton tol, time-step limits, discretisation | ✓ kept | dropped | dropped |
| T3 domain-inferable | densities, viscosities, porosities, perms | ✓ kept | ✓ kept | dropped |
| T4 problem-defining | geometry, well locations, applied loads | ✓ kept | ✓ kept | ✓ kept |

**Hygiene**: numeric tokens canonicalised (LaTeX, scientific notation, Unicode supers), no leakage post-rewrite. 16 (task × level) rewrites frozen before any run.

**Score drop with relaxation**, 8-task subset:

- F0 (Vanilla): Easy 0.910 → Medium 0.776 → Hard 0.828
- F4 (X+M): Easy 0.921 → Medium 0.829 → Hard 0.835

Hard barely worse than Medium — **example library on disk fills the gap**.

---

# Autonomy companion #2 — interactive supervisor channel

We expose a `consult_supervisor(question)` MCP tool. Handler = a *separate* DSv4-flash instance prompted with the *full* original brief (the "oracle"); responds concisely without volunteering detail.

**Headline**: across **64 trials in two prompt framings**, the agent consults the supervisor in **only 1–3% of trials**.

| difficulty | mode | F0 | F4 | $\Delta$ |
|---|---|---:|---:|---:|
| Medium | non-interactive | 0.776 | 0.829 | +0.053 |
| Medium | **interactive** | **0.884** | 0.875 | −0.009 |
| Hard | non-interactive | 0.828 | 0.835 | +0.008 |
| Hard | **interactive** | 0.710 | **0.840** | +0.130 |

**Why so low?** Mandel/Hard diagnostic: 15 of 26 dropped numeric values appear by literal `grep` in other GEOS examples the agent is allowed to read. **The on-disk example library is a cheaper retrieval substitute for the human channel.**

V0 (mildly discouraging) vs V1 (peer-treating) framings: 1/32 vs 1/32 — framing doesn't move the rate.

---

# Autonomy companion #3 — where the agent looks

Aggregate `Read`/`Glob` calls into `/geos_lib/inputFiles/` (8 tasks per cell):

| cell | Easy | Medium | Hard |
|---|---:|---:|---:|
| F0 (Vanilla) | — | **404** | 142 |
| F4 (X+M) | — | 142 | 142 |

The agent is **not idle** when it doesn't ask — it greps the example library aggressively, especially Vanilla CC under Medium relaxation.

**Implication for AI-for-science / autonomous-discovery research**: studies that want to *measure* consultation behaviour have to remove the on-disk oracle (e.g. block by physics family, not just GT basenames), use synthetic parameter values, or both. We didn't run that intervention; **listed as a follow-up**.

---

# Human baseline — calibration anchor

Two PhD-level geoscience volunteers (P1, P2). Same task: `buckleyLeverettProblem` (the *easy* end of the bench). 1-hour budget. Same files mounted as the agent. No internet beyond GEOS docs / GitHub.

| author | file-level TreeSim | deck-level TreeSim | wall (min) |
|---|---:|---:|---:|
| P1 (PhD) | 0.812 | 0.540 | 48.2 |
| P2 (PhD) | 0.781 | 0.527 | 46.7 |
| Vanilla CC × minimax | ≈0.87 | ≈0.87 | ≈5 |
| SIA (X+M) × DSv4 | ≥0.90 | ≥0.90 | ≈5 |

**Both ran out of time on the first of two required files.** Neither attempted the second.

**Where they looked**: P1 made 29 browser navigations (20 GEOS Sphinx, 5 GEOS GitHub); P2 made 73 (54 Sphinx, 11 GitHub). Both reached for the `EventManager` page; both flagged `Outputs`/`Events` as the time sink. Agent never visits Sphinx — it grep/globs the `inputFiles/` example library.

**Two strategies for one DSL**: humans navigate prose explanations; agent navigates concrete examples.

---

# Paper changes since last sync

- **Title** updated to drop "Grounding": *Simulator Interface Adapters for Scientific Simulation Setup: A Geophysics Case Study*
  - **(open question — see next slide)**
- **Abstract**: rewritten to single paragraph, ~40% shorter; intro now starts on page 1
- **Intro**: added dedicated "Two regimes that test the agent's autonomy" paragraph; contributions reordered
- **Background §3**: GEOS XML reframed as a DSL — elements ↔ classes, attrs ↔ ctor params, nesting ↔ composition, sequencing ↔ Events
- **Metric**: `TreeSim-fa0` → `TreeSim` (failures-as-zero noted inline)
- **Splits**: `test-17` → `val`, `Held-out-10` → `held-out-eval`
- **Table 1**: 7 cols → 5 (`mean ± std` collapsed); fits within page now
- **New §6.8 + Appendix L**: Human baseline + browser-history breakdown + protocol

Build: 28 pp, `pdflatex` clean. CHANGELOG.md tracks every edit.

---

# Title — your concern about pigeonholing

Current: *"Simulator Interface Adapters for Scientific Simulation Setup: A Geophysics Case Study"*

Your point: **simulators aren't the only target**. The same recipe could plausibly help with other advanced-software classes — finite-element preprocessors, CAD scripting, geospatial analysis pipelines, theorem-prover tactics, lab-automation control software, etc.

**Candidate retitles** (room to discuss):

1. *Domain-Interface Adapters for Coding Agents on Advanced Scientific Software: A Geophysics Simulator Case Study*
2. *Wrapping Coding Agents for Advanced Scientific Tooling: A GEOS Geophysics Case Study*
3. *Adapting Coding Agents to Specialized Scientific Software: A Geophysics Simulation Study*
4. *Specialized-Tooling Adapters for Coding Agents: An Empirical Study on GEOS Geophysics Simulation*

Net move: replace "Simulator Interface Adapter (SIA)" → "**Domain Interface Adapter**" or "**Tooling Interface Adapter**" — keeps the four-component recipe, broadens the class.

**Tradeoff**: the more we abstract, the further we drift from the specific empirical claim we *do* support (one simulator, geophysics, GEOS). Workshop venue tolerates broader framing better than NeurIPS main, where reviewers will challenge it.

---

# Where to land it — NeurIPS vs ICML AI4Science workshop

|  | NeurIPS main 2026 | **ICML 2026 AI4Science workshop** |
|---|---|---|
| Audience | broad ML | applied ML × scientific domains |
| Reviewer expectation | new method or strong head-to-head | empirical findings, applied case studies, honest negatives |
| Page limit | 9 + refs/appendix | typically 4–6 pp + appendix |
| Welcomes case-study shape | mixed | **yes, explicitly** |
| Welcomes negative results | sometimes hostile | **yes, explicitly** |
| Risk our paper hits "application" rejection | **moderate-to-high** | low |
| Lets us iterate before end-of-May "method paper" | submission late | **submit now, free up cycles for Paper 2** |

**ICML AI4Science deadlines** (from https://ai4sciencecommunity.github.io/icml26/call):

- **Abstract registration: May 06 11:59 UTC** ≈ May 5 16:59 PDT (≈1.5 days)
- **Submission deadline: May 08 11:59 UTC** ≈ May 7 16:59 PDT (≈3.5 days)

---

# Honest appraisal — is the paper NeurIPS-ready?

**My read: workshop is the better landing zone for *this version*.** Reasons:

**Strong for either venue**:

- Solid 4-component factorial with multi-seed reliability statistics
- Honest negative results (RAG, MCP retrieval-memory, perfect-deck count)
- Cross-model + cross-harness panel that confirms direction
- Autonomy companion + human baseline = two probes neither fakes
- Bottleneck-analysis pipeline is a real artifact

**Risks for NeurIPS main**:

- Self-described as application study, no new algorithm — easy "rejection-by-novelty" target
- n=1 on cross-model panel; n=3 only on DSv4
- Single simulator; no cross-tool pilot
- 28 pp already; trimming to 9 will hurt
- "We customised Claude Code" story can be read as engineering, not science

**Workshop-specific upside**:

- Workshop call literally asks for "applied ML for scientific challenges, including negative results and lessons learned"
- Submission in 3 days frees up the rest of May for the *real* method paper

**Recommendation**: target ICML AI4Science workshop; treat NeurIPS-main as a stretch fallback if we get a strong workshop reception and 2 extra weeks to add cross-tool.

---

# End-of-May "method" paper — the real follow-up

Your motivation: *advanced software adaptation as an interesting **learning problem** that both (a) learns by reading the docs AND (b) designs an agent that itself uses the docs.*

This is **the Meta-Harness shape, with documentation as the prior** (cf. `docs/2026-05-01_harness-adapter-vs-meta-harness-framing.md`):

- Outer-loop proposer (Claude Code-style coding agent) reads the simulator's docs, schema, examples — **not just prior candidate code/traces**
- Proposer outputs **typed extensions** (hooks / MCP / skills / system-prompt prepends) against the base harness's documented ABI — not a fork/monkey-patch
- Search target = our SIA recipe (R, S, X, M and whatever new components the proposer invents) — discovered, not hand-engineered
- Eval = the GEOS benchmark we've now built; later, cross-tool

**Why this is novel vs Meta-Harness**:
- their proposer reads *trajectories*; ours additionally reads *docs* (different prior class)
- their artifact = single-base fork; ours = typed extension that transfers (CC ↔ OH already shown empirically)
- their eval domain = generic agentic coding; ours = specialised scientific tooling where the doc is dense and load-bearing

Workshop submission **doesn't burn the Paper-2 angle** — it sets it up as the natural next paper.

---

# Items for discussion

1. **Venue**: ICML AI4Science workshop or push for NeurIPS main? (My vote: workshop.)
2. **Title**: keep "Simulator Interface Adapter" or broaden to "Domain Interface Adapter" / "Tooling Interface Adapter"?
3. **Abstract length**: workshop abstract requirements — do we want me to also produce a 100-word standalone abstract for the May 6 registration?
4. **Cross-tool pilot**: skip for now, do as Paper 2 lead-in, or carve out 2 days for a 5-task FEniCS/MOOSE/OpenFOAM smoketest?
5. **Human baseline**: $n = 2$ is a calibration anchor only — should we recruit 2–3 more PhD students this week, or land at $n = 2$ with the appropriate caveat?
6. **Method-paper scope** (end of May): which is the right anchor — *documentation-aware proposer* (most novel, hardest), or *typed-extension transfer across base harnesses* (easier to land, builds on what we have)?

**My priority order if we go workshop**:

1. Lock title + abstract + 1-paragraph contribution list **today**
2. Trim to ~6pp body for workshop format **tomorrow**
3. Submit abstract by May 5 16:59 PDT
4. Polish + figures + submit full by May 7 16:59 PDT
5. Then immediately pivot to Paper-2 method scoping

---

<!-- _class: lead -->

# Backup slides

(in case any of the items below come up)

---

# Backup — full Resolution-IV cell map

8 cells run, 16 cells in the full design. Generator: `D = ABC` (here R=A, S=B, X=C, M=D).

| cell | R | S | X | M | val TreeSim |
|---|:-:|:-:|:-:|:-:|---:|
| Vanilla | – | – | – | – | 0.910 |
| R+M | + | – | – | + | 0.885 |
| S+M | – | + | – | + | 0.919 |
| R+S | + | + | – | – | 0.857 |
| X+M | – | – | + | + | **0.921** |
| R+X | + | – | + | – | 0.893 |
| S+X | – | + | + | – | 0.917 |
| R+S+X+M | + | + | + | + | 0.885 |

Plus: S+X+M (the "missing 16th cell" filling in the predicted main-effects-best corner) at 0.911. SE-prose at 0.897. SE at 0.919.

**Main effects** (from these 8): R = −0.032, S = −0.003, X = +0.007, M = +0.004. Only R clears the σ ≈ 0.024 noise floor.

---

# Backup — bottleneck analysis (DSv4-flash classifier, ~650 calls)

| failure category | Vanilla val | X+M val | SE held-out-eval | what it means |
|---|---:|---:|---:|---|
| `missing_block` | 6 | **3** | 4 | adapter helps — schema validation forces required blocks |
| `bad_attribute_value` | 12 | 11 | 0 | adapter does *not* help — schema can't catch wrong-but-valid values |
| `extra_block` | 9 | 11 | 5 | adapter *worsens* — cheatsheet sometimes prompts extras |
| `hallucinated_extras` | 4 | 7 | 4 | same |
| `structural_mismatch` | 6 | 7 | 5 | unchanged |
| `partial_implementation` | 7 | 6 | 5 | small movement |

**Strictly perfect decks (TreeSim ≥ 0.999)**: Vanilla 7/51, X+M 6/51, SE 6/51. Adapter = harm reduction, not correctness gain.

→ Drives the four adapter-design recommendations (per-attribute oracle, closed-loop retry, etc.).

---

# Backup — Meta-Harness (Lee et al. 2026) one-pager

Stanford+MIT+KRAFTON, arXiv 2603.28052. Full notes: `docs/literature/LN-003_meta-harness.md`.

- **Outer loop**: Claude Code (Opus-4.6) proposer reads filesystem `D` of `(source, scores, traces)` for prior candidates, proposes new harnesses, evaluates, appends to `D`.
- **TerminalBench-2 winner**: ~80 LOC `[Environment Snapshot]` injection on top of Terminus-KIRA. **Not a fork** — additive context.
- **Filesystem as feedback** > compressed feedback (Table 3): median 50.0 raw vs 41.3 best-of-summaries.
- **Iter 1–6 regressed**, iter 7 pivoted to additive: 60% wasted iters before convergence — *positive evidence* a structural prior would save iterations.

**Relevance to Paper 2**: their algorithm restricted to *typed-extension* output space + *doc-aware proposer* = our follow-up. Cite as concurrent automated harness search; don't try to head-to-head them on benchmark numbers.
