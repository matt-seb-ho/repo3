---
marp: true
theme: default
paginate: true
size: 16:9
header: '2026-05-18 SIGA Update'
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

<!-- # Study-then-Harness
## Documentation-grounded meta-harness construction

**Status as of 2026-05-18** — Paper-2 proposal + overnight prototype

- Feedback memo: `docs/2026-05-18_feedback-on-overnight-ideas.md`
- Advisor proposal: `docs/2026-05-18_paper2-proposal-advisor.md`
- Decision log: `docs/2026-05-18_overnight-decisions.md`
- Prototype: `scripts/doc_study/study_pipeline.py`
- Artifacts: `data/doc_study/2026-05-18_full/` -->

<!-- --- -->

# TL;DR

1. **Core framing.** The meta-harness should *study* the docs before any task — read everything, write structured notes, hierarchically coalesce — and emit a persistent **studied artifact** $\hat D$. Both the meta-harness and the runtime harness consume $\hat D$ instead of raw docs.
2. **Contribution.** $\hat D$ is the load-bearing object. Not "meta-harness reads docs" (vague) — "meta-harness emits a doc-shaped artifact before tasks run" (falsifiable).
3. **Scoped contributions.** N4 (doc-bootstrapped seed) ⊕ N2 (bipartite component–section graph) is the spine. N3 (doc-anchored attribution) and N6 (utility-weighted budget, folded into N2's update rule) are supporting. N1/N5/N7/N8/N9 cut or deferred.
4. **Overnight prototype.** Built a working 3-phase doc-study pipeline; ran it on 161 GEOS docs via DSv4-flash on OpenRouter. ~$0.20, ~10 min wall-clock.

---

# Why "study" ≠ "RAG"

| Mode | Selection function | When the structure is imposed |
|---|---|---|
| RAG | $f$: query → sections | Reactively, at query time |
| Study | $f$: query → studied-structure → sections | Proactively, before any query |

**The pedagogical analogy.** Open-textbook exam. Both students have full access; the one who studied is *faster and more targeted*. We can't fine-tune frontier LLMs cheaply ⇒ externalize "studying" as note-writing + hierarchical coalescing.

**Bitter-lesson rebuttal.** The expensive thing is *evaluating proposed harnesses* (each eval = end-to-end tool run). In NAS-like regimes, informed priors are a multiplier on every subsequent eval. Contribution lives in the few-orders-of-magnitude gap before "infinite compute + grep" wins.

---

# White-space recap

| System | Doc role | Studied artifact? | Outer proposer |
|---|---|---|---|
| **Meta-Harness** (Lee 2026) | Flat FS substrate | <span class="neg">No</span> | Claude Code (Opus 4.6) |
| **MCE** (Ye 2026) | Skill-internal retrieval | <span class="neg">No</span> | M2.1 meta-agent |
| **AHE** (Lin 2026) | Not modeled — trace-only observability | <span class="neg">No</span> | GPT-5.4 evolve-agent |
| **SkillFoundry** (Shen 2026) | Authoritative-artifact priority | <span class="neg">Partial</span> (capability tree, not doc tree) | Staged JSON-schema pipeline |
| **Ours** | **Pre-task distilled $\hat D$; both meta and runtime consume it** | <span class="pos">**Yes — first-class contribution**</span> | Staged pipeline + bipartite-graph state |

<span class="muted">**MoSciBench warning** (Liu 2026): naïve "domain knowledge" injection *hurts* (48.4 → 44.9). Structure has to do real work.</span>

---

# The studied artifact $\hat D = (G, N, S)$

- **$G$** — bipartite component↔section graph. Components (skills, prompts, validators, …) declare which sections they ground in; sections are either cited (live) or uncited (dead).
- **$N$** — per-section structured notes. JSON-schema enforced fields: `type`, `summary`, `key_objects`, `relations`, `examples_present`, `pitfalls`, `harness_relevance`, `citation_anchor`.
- **$S$** — hierarchical roll-up. Per-subtree summary + tool-level summary (entrypoints, top-workflows, object-taxonomy, top-pitfalls, navigation-index).

Built **once** by the meta-harness study phase. **Edited** (not regenerated) by later iterations as citations + utility evidence accumulate.

---

# Method: staged meta-harness $M$

```
study           : D → (N, S)
seed_construct  : (N, S) → H₀
evaluate        : H_t × Task → score, trace
attribute       : (score, trace) → {missed section, misinterpreted, doc gap}
edit            : (H_t, attribution, G) → H_{t+1}, G_{t+1}
update_artifact : (G_t, citation_log_t) → G_{t+1}
```

Staged rather than free-form coding agent — buys us:
1. Schema-enforced outputs at every stage.
2. Per-stage compute allocation (study ≫ optimize).
3. Auditable per-stage I/O for ablations.

---

# Three falsifiable claims

**C1 — Sanity.** $\hat D$ alone (no iteration) > flat-doc-RAG.

**C2 — Symmetry.** $M$ over $\hat D$ > $M$ over raw $D$ in regression rate + generalization to held-out tool sub-areas.

**C3 — Attribution.** Doc-anchored 3-way classification ({missed / misinterpreted / doc-gap}) > AHE free-form attribution on regression prediction. <br><span class="muted">Target: precision > 25% (AHE: 11.8%).</span>

---

# Ablation lattice (6 headline conditions)

| | Substrate available to harness | Meta-iteration |
|---|---|---|
| A0 | None | no |
| A1 | Raw docs (flat FS, MH-style) | no |
| A2 | Raw docs + RAG (SF-style mining without artifact) | no |
| A3 | <span class="pos">$\hat D$ alone (no raw docs)</span> | no |
| A4 | $\hat D$ + raw docs | no |
| A5 | <span class="pos">$\hat D$, iteratively edited by $M$</span> | yes |

Hypothesis order: **A3 > A1 ≈ A2** (artifact standalone value); **A4 ≥ A3** (raw doc availability marginal); **A5 > A4** (iteration adds value on top of artifact).

---

# Honest risk: in-distribution exposure

Frontier LLMs were trained on most public scientific software docs.

If GEOS / FEniCS / MOOSE are effectively "memorized," the study pass may be a no-op.

**Mitigation** — include at least one condition where the model can't have studied:

- A GEOS release version newer than the LLM training cutoff
- A private branch / internal codebase

This is also the *realistic deployment regime* (you'd use this on your lab's private tool, not a published one).

→ Should be the **headline experiment**, not an afterthought.

---

# Overnight prototype — doc-study pipeline

**Script** `scripts/doc_study/study_pipeline.py`. Three phases:

1. **Phase 1.** Per-section JSON note via DSv4-flash (parallel, 8 workers).
2. **Phase 2.** Per-subtree rollup (sequential, ~17 subtrees).
3. **Phase 3.** Global rollup (one call → $\hat D$ tool-level summary).

**Test target** — GEOS sphinx + `coreComponents/*/docs/`, 186 → 161 RST files (filtered 500B–50KB).

**Infra** — `openai==2.30` SDK, OpenRouter base URL, `response_format=json_object`. Fall-back path to DeepSeek-direct already wired.

---

# Sample of what the pipeline emits (per-section)

```json
{
  "section_id": "coreComponents/constitutive/docs/BlackOilFluid",
  "type": "reference",
  "title": "Black-oil fluid model",
  "summary": "The black-oil model handles three pseudo-components ...
              partitioned across liquid, vapor, and aqueous phases. ...",
  "key_objects": ["BlackOilFluid", "fluidType", "phaseNames",
                  "surfaceDensities", "componentMolarWeight",
                  "tableFiles", "PVTPackage"],
  "relations": ["docs/sphinx/datastructure/BlackOilFluid.rst", ...],
  "examples_present": true,
  "pitfalls": [],
  "harness_relevance": "high",
  "citation_anchor": "In the black-oil model three pseudo-components"
}
```

XML element names verbatim, harness-relevance flag, grep-anchor for re-retrieval.

---

# Costs + run characteristics (final run, completed)

- 161 sections discovered → **149 ok / 12 JSON-parse errors** (7.5%).
- 23 subtree rollups + 1 global rollup, all successful.
- Wall-clock: **637 s (10.6 min)** with 8 parallel workers.
- Tokens: 432K prompt + 170K completion.
- Billed cost: **≈ $0.11 total** (DSv4-flash via OpenRouter Parasail provider).
- Recovery: bump `max_tokens` 1.6K → 2.5K + `--skip-existing`; estimated 12 → <3 failures.

---

# What the global rollup actually says about GEOS

Sample of what came out of the pipeline — auto-extracted, 10 min, $0.11:

- **Entrypoints (8):** `<Solvers>`, `<Constitutive>`, `<Mesh>`, `<Events>`, `<FieldSpecifications>`, `<Functions>`, tutorials, basicExamples.
- **Top workflows (10):** `SinglePhaseFVM`, `CompositionalMultiphaseFVM`, `SolidMechanicsLagrangianFEM`, `PoroelasticSolver`, `Hydrofracture`, `SolidMechanicsLagrangeContact`, `PVTDriver`, `TriaxialDriver`, `ProppantTransport`, `CompositionalMultiphaseWell`.
- **Object taxonomy:** 8 categories spanning ~30 named XML elements (verbatim, correct capitalization).
- **Top pitfalls (10):** "phase names must match across fluid/relperm/FieldSpec blocks", "HydrostaticEquilibrium requires gravity vector aligned with z-axis", "stale Numpy views from pygeosx cause segfaults if LvArray buffer is reallocated", ...
- **Honest coverage note:** flags advancedExamples as missing (JSON parse error), notes Doxygen/Publications/internal-dev are shallow.

vs hand `GEOS_PRIMER_minimal.md` — 34 lines, prescriptive (which RAG tools to call), no domain enumeration.

→ Auto-rendered primer: `plugin/GEOS_PRIMER_auto_2026-05-18.md` (191 lines).

---

# What's NOT in the overnight prototype

- **No iteration loop** (A5). Phase-1/2/3 build the artifact once.
- **No bipartite graph** as a runtime object yet. The JSON notes carry the `relations` field that would seed it; the graph proper is week 3 of the proposal.
- **No end-to-end GEOS-task eval** swapping in the auto-generated artifact for the hand-engineered primer. Held off because (a) ~1-2 hour setup risk vs (b) format-mismatch comparison would be misleading. See decision log D8.

The point of the overnight build is *the pipeline exists, output is inspectable, costs are bounded* — not "A3 beats A1 on GEOS today."

---

# Recommended core, sharpened

| | last week's proposals | updated |
|---|---|---|
| Spine | N1 + N2 + N3 + N5 | <span class="pos">**N4 ⊕ N2**</span> |
| Supporting | — | N3 (independent), N6 (folded into N2 update rule) |
| Cut | N7/N8/N9 deferred | + N1 (subsumed under N4) + N5 (deferred) + N7 (overlaps N2) |
| Framing | "Doc-grounded meta-harness" | <span class="pos">**"Study-then-harness: $\hat D$ artifact as contribution"**</span> |

Fewer claims, sharper falsifiability per claim.

---

# Open questions for the meeting

1. **Single-tool depth vs cross-tool transfer in headline.** GEOS deep is feasible; FEniCS / MOOSE adds new infra.
2. **Coding-agent vs staged-pipeline meta-harness.** Leaning staged (per-stage schemas slot in cleanly). Confirm?
3. **Meta-harness proposer model.** OK to step up to Gemini 3 Flash / Pro for $M$ while keeping DSv4-flash for $H$?
4. **End-to-end simulation as eval metric**, beyond treesim — invest for the held-out subset?
5. **External-model adversarial review** (Codex / Cursor) — should this gate the $\hat D$ design lock-in?

---

# Next concrete steps

**This week** (independent of advisor input):

1. Retry the JSON-failed sections with bumped `max_tokens`.
2. Inspect global rollup `data/doc_study/2026-05-18_full/global.json` against `plugin/GEOS_PRIMER_minimal.md` — qualitative comparison doc.
3. Read SkillFoundry **code** (not just paper) for actual prompts/schemas — close LN-004 open questions.
4. Pick the post-cutoff GEOS version / private tool for the in-distribution-risk experiment.

**Then with advisor sign-off:**
- Implement A0–A4 ablation lattice on the existing 17-task / 36-task GEOS grid.
- Stand up the staged meta-harness $M$ for A5.
- Run the doc-anchored attribution study (C3) — can ship independently as appendix or short paper.

---

<!-- _class: lead -->

# Backup slides

---

# Per-proposal feedback summary

- **N2 (bipartite component↔section graph).** Strongly agree. Disentangle: graph as abstraction (yes) vs subagents as implementation (only for parallel-and-isolated parts — initial traversal, batch consistency).
- **N3 (doc-anchored failure attribution).** Worth running. Cheap, independent of the meta-harness loop. Hand-label regressions, beat AHE's 11.8% precision.
- **N4 (doc-bootstrapped seed).** Strongly agree. Reframe: the seed *is* the studied artifact, viewed from the harness side.
- **N6 (doc-utility-weighted budget).** Strongly agree. Fold into N2 as the *update rule* — not a separate proposal.

---

# What was cut and why

| Item | Reason for cut |
|---|---|
| N1 (typed multi-index) | Subsumed under N4 — the studied artifact is already typed |
| N5 (doc-as-soft-oracle) | Nice-to-have; cheap proxy metric. Defer to a follow-up |
| N7 (symmetric consultation traces) | Overlaps N2 if N2 is properly logged |
| N8 (negative knowledge as constraints) | Paper-of-its-own scope |
| N9 (doc-diff longitudinal) | Long-horizon; not feasible in one paper |

<!-- ---

# Search-query bank (for your AI deep-research / Asta / SS / Scholar pass)

**"LLMs reading to learn" branch (highest signal):**
`"pre-task" OR "pre-reading" documentation LLM agent` ·
`agent "study phase" documentation distillation` ·
`LLM "note taking" documentation knowledge artifact` ·
`agent "warmup" "domain adaptation" without fine-tuning` ·
`"hierarchical summarization" technical documentation LLM` ·
`LLM "self-supervised note taking"`

**Closest adjacent prior art:**
`"continued pretraining" technical manual` (related but fine-tuning-based) ·
`Toolformer` / `ToolLLM` / `Gorilla` (function-from-docs, programming-tool) ·
`Voyager` / `ExpeL` / `MemP` / `Reflexion` (trajectory-based, contrast)

**Asta-style question prompts:**
"What is the strongest published result for forcing an LLM agent to pre-read documentation before task execution, and how does it compare to retrieval-only baselines?"
 -->
