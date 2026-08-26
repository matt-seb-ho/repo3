---
id: paper2-proposal-2026-05-18
title: "Paper 2 Proposal — Study-then-Harness: Documentation-Grounded Meta-Harness Construction"
date: 2026-05-18
authors:
  - Matt
  - "with research-copilot scaffolding"
status: draft for advisor + post-doc collaborator
related:
  - docs/2026-05-14_doc-grounded-meta-harness-proposals.md (internal design memo, full menu N1–N9)
  - docs/2026-05-18_feedback-on-overnight-ideas.md (internal deliberation)
  - docs/2026-05-02_neurips-paper-plan.md (Paper-1 / Paper-2 scope split)
---

*Draft for advisor + post-doc review. Comments welcome inline or via shared doc once converted.*

# Study-then-Harness
## Documentation-Grounded Meta-Harness Construction via Pre-Task Doc Distillation

---

## TL;DR

Frontier LLM agents tasked with operating elaborate scientific tools
(GEOS, FEniCS, MOOSE, …) consult documentation only *reactively* — when a
specific runtime query arises. We propose that the **meta-harness** —
the agent that builds a tool-specialized harness — should instead
*proactively study* the documentation: read every relevant section, write
structured notes, hierarchically coalesce them into a persistent
**studied artifact**, and use that artifact (not the raw docs) as the
substrate both for the meta-harness's own reasoning and for the
runtime harness it produces. This converts open-ended doc retrieval into
a structured, falsifiable, maintainable contribution.

This builds directly on Paper 1 (manual SimAdapter for one tool) and
fills the methodological white-space across the four closest baselines
(Meta-Harness, MCE, AHE, SkillFoundry) — none of which treat
documentation as a structured substrate the meta-harness reasons over.

---

## 1. Motivation

### 1.1 Paper 1 → Paper 2 transition

Paper 1 (in submission) introduces the **SimAdapter** recipe — a manual
specialization of an agent harness for one elaborate scientific tool
(GEOS). It demonstrates that careful hand-engineering of primer,
retrieval surface, validation hooks, and memory components produces
large gains over a vanilla coding agent, even on tools the underlying
LLM has substantial training-data exposure to.

The natural follow-up: **automate the recipe**. Given a tool's
documentation, can a meta-procedure construct a SimAdapter without human
hand-engineering? This is Paper 2.

### 1.2 What current meta-harness work misses

The four closest baselines — Meta-Harness (Lee et al. 2026), MCE (Ye et
al. 2026), AHE (Lin et al. 2026), SkillFoundry (Shen et al. 2026) —
treat documentation in one of two impoverished ways:

- **Flat substrate.** MH/AHE/MCE put docs in the file system as
  another directory the proposer can grep.
- **Authoritative source list.** SkillFoundry prioritizes "authoritative
  artifacts" during resource search but does not preserve doc *structure*
  in the runtime skill format.

None of them produce a doc-derived artifact that the meta-harness's
later iterations consume. Meanwhile MoSciBench (Liu et al. 2026)
delivers a warning shot for naïve approaches: simply injecting "domain
knowledge" into the agent's context *hurts* performance (48.4% →
44.9% on average). Structure has to do real work.

### 1.3 The pedagogical analogy

The argument by analogy: a CS undergraduate with full Google access
still benefits enormously from having studied compilers before sitting
down to write a parser. They aren't memorizing the textbook — they're
internalizing structure, so their on-the-job lookups are faster and
more targeted. We can't fine-tune frontier LLMs cheaply enough to give
them this "studied" state via training, but we *can* externalize the
studying: have the meta-harness traverse the docs, write structured
notes, coalesce them, and use the result as a persistent artifact.

The bitter-lesson counterargument ("general methods + compute win
eventually") deserves a direct rebuttal: in our regime, each
"evaluation" of a harness costs an end-to-end tool-task run.
Bitter-lesson scaling assumes cheap inference per data point; we have
the opposite — expensive evaluation. Just as Neural Architecture
Search benefits from informed priors despite the bitter lesson at scale,
so does meta-harness construction. The contribution lives in the
several-orders-of-magnitude gap before "infinite compute + grep" wins.

---

## 2. Problem statement

> **Given** an elaborate scientific tool $T$ and its authoritative
> documentation $D$, **automatically construct an agent harness $H$**
> that operates $T$ with measurable fidelity to its documented
> behavior, using a meta-harness procedure $M$ such that **both $M$ and
> $H$ ground in $D$ via a shared distilled artifact $\hat D$** which
> $M$ produces in a deliberate pre-task study phase.

The contribution is the existence, structure, and empirical value of
$\hat D$.

---

## 3. The studied artifact $\hat D$

$\hat D$ is the load-bearing object of this paper. We define it as:

$$\hat D = (G, N, S)$$

where:

- $G$ is a **bipartite component–section graph** with two node sets:
  *harness components* (skills, prompts, retrievers, validators,
  middleware) and *doc sections* (typed: schema, tutorial, concept,
  warning). Edges declare grounding ("component $c$ uses section $s$").
- $N$ is a **section-level note set** — one structured note per
  reachable doc section, written by $M$ during the study phase.
- $S$ is a **hierarchical roll-up** — section notes coalesced
  into chapter-level and tool-level structured summaries
  ("entrypoints," "primary workflows," "common pitfalls," "schema
  index").

$\hat D$ is constructed once, before any task evaluation, by a study
pass of $M$ over $D$. It is then **edited** (not regenerated) by
subsequent meta-harness iterations as new evidence accumulates.

### 3.1 Concrete operationalization

- **Traversal coverage.** $M$ visits every section of $D$ down to a
  declared depth. Coverage is logged and ablatable.
- **Per-section structured notes.** Each section produces a fixed
  schema: `{section_id, type, summary, key_objects, relations,
  examples, pitfalls, citation_anchor}`. Schema is enforced via JSON
  output validation.
- **Subagent traversal.** Section reading is parallelized by
  subagents, each with bounded context, returning structured notes.
  This isolates per-section reading and keeps per-iteration cost
  linear in $|D|$.
- **Hierarchical coalescing.** Chapter-level summaries merge their
  section notes; tool-level summaries merge chapter summaries. Merge
  prompts are themselves structured.
- **Bipartite graph maintenance.** Whenever the runtime harness $H$
  cites a section in its operation, the citation is logged as an
  edge. Sections that accumulate citations from successful runs are
  *strengthened*; sections cited alongside failures are *flagged*. The
  meta-harness uses these signals to allocate its next round of
  attention.

---

## 4. Method

### 4.1 The meta-harness $M$

$M$ is a staged pipeline (rather than a free-form coding agent) for
three reasons:

1. **Structured-output enforcement** is natural at each stage — every
   stage emits JSON conforming to a schema.
2. **Per-stage compute allocation** allows expensive reasoning only
   where it pays off (study and triage), cheaper reasoning elsewhere.
   This is SkillFoundry's design choice and we adopt it.
3. **Auditability.** Each stage's input, output, and rationale is
   loggable independently.

The stage map:

```
study          : D → (N, S)               // pre-task; once
seed_construct : (N, S) → H₀              // produce initial harness from artifact
evaluate       : H_t × Task → score, trace
attribute      : (score, trace) → {(a) missed section,
                                   (b) misinterpreted section,
                                   (c) doc gap}     // doc-anchored 3-way attribution
edit           : (H_t, attribution, G) → H_{t+1}, G_{t+1}
                                          // edits respect bipartite consistency
update_artifact: (G_t, citation_log_t) → (G_{t+1})
                                          // sections strengthened/demoted
```

### 4.2 The runtime harness $H$

$H$ is a coding-agent–style harness that has access to $\hat D$ at
runtime (specifically: $G$ for navigation, $S$ for global orientation,
$N$ for section-level retrieval). It does *not* have raw access to $D$
by default — the artifact is the substrate. (We ablate this; see §6.)

### 4.3 Three claims to test empirically

C1. **Sanity.** $\hat D$ alone, used as a static substrate for a
non-iterated harness, beats a flat-doc-RAG baseline.

C2. **Symmetry.** $M$ operating over $\hat D$ produces better edits
than $M$ operating over raw $D$.

C3. **Attribution.** Doc-anchored 3-way classification (missed /
misinterpreted / doc-gap) outperforms AHE-style free-form attribution
on regression prediction (target: precision > 25%, vs AHE's reported
11.8%).

---

## 5. Evaluation plan

### 5.1 Tool selection

Primary: **GEOS**. Infrastructure exists (`scripts/run_experiment.py`,
17-task and 36-task evaluation grids, treesim metric, xmllint
validation, docker-isolated runner). Paper 1's evaluation surface
transfers directly.

Stretch: **FEniCS** or **MOOSE** as a cross-tool transfer test. The
same $M$ pipeline applied to a different tool's docs should yield a
working harness without re-engineering the procedure. This earns the
"meta-procedure" claim its name.

### 5.2 Metrics

- **Input-file fidelity (treesim).** Existing metric; tree-edit
  distance between generated and reference XML inputs.
- **End-to-end task success.** Where ground truth simulation is
  feasible, full execution + downstream validation. Slower; reserved
  for a held-out subset.
- **Coverage** of $\hat D$: fraction of $D$ sections actually consumed
  by the harness in successful runs.
- **Regression-prediction precision/recall** for C3.

### 5.3 Ablation lattice

Six headline conditions:

| | Substrate available to harness | Iteration |
|---|---|---|
| A0 | None | no |
| A1 | Raw docs (flat FS, MH-style) | no |
| A2 | Raw docs + RAG (SF-style mining without artifact) | no |
| A3 | $\hat D$ alone (no raw docs) | no |
| A4 | $\hat D$ + raw docs | no |
| A5 | $\hat D$, iteratively edited by $M$ | yes |

The hypotheses:

- A3 > A1 ≈ A2 — demonstrates the artifact's standalone value.
- A4 ≥ A3 — raw doc availability either helps marginally or not.
- A5 > A4 — meta-iteration does useful work *on top of* the studied
  artifact, not as a substitute for it.

### 5.4 Honest risk: in-distribution exposure

Frontier LLMs are trained on most public scientific software docs. The
study phase may be a no-op for tools the model has effectively
memorized. **Mitigation:** include one tool or tool version
substantially post-dating the LLM training cutoff (e.g., a GEOS
release with newly-added solvers, or a private branch of FEniCS), where
the model's prior knowledge is provably incomplete. This is the
realistic deployment regime and should be the headline experiment, not
an afterthought.

---

## 6. Relation to prior work

| System | Doc role | Studied artifact? | Outer proposer |
|---|---|---|---|
| Meta-Harness (Lee 2026) | Flat FS substrate | No | Coding agent |
| MCE (Ye 2026) | Skill-internal retrieval, no first-class doc model | No | Skill-recombining meta-agent |
| AHE (Lin 2026) | Not modeled — observability is over traces, not docs | No | Evolve-agent over file substrate |
| SkillFoundry (Shen 2026) | Priority for "authoritative artifacts," docs alongside repos | Partial (capability tree, not doc tree) | Staged JSON-schema pipeline |
| **Ours** | **Pre-task distilled artifact $\hat D$; both meta and runtime consume it** | **Yes — explicit object of contribution** | **Staged pipeline with bipartite-graph state** |

The contribution is unambiguous: the **pre-task structured study and
its persistent artifact** is novel relative to all four.

Supporting prior art we cite as related-but-different:

- *Programming-from-docs* systems (Toolformer, ToolLLM, Gorilla) —
  function-call grounding, not structural study.
- *Skill induction* systems (Voyager, ExpeL, MemP) — trajectory-based,
  not doc-based.
- *Hierarchical retrieval* over long documents — retrieval mechanics,
  not artifact-as-contribution.

---

## 7. Contributions (proposed)

1. **The $\hat D$ artifact:** a typed, hierarchical, bipartite-
   structured distillation of tool documentation that serves as the
   shared substrate for both meta-harness reasoning and runtime
   harness operation.
2. **A staged meta-harness procedure** that constructs, maintains, and
   edits $\hat D$ across iterations — with explicit doc-anchored
   attribution and citation-weighted section utility tracking.
3. **A six-condition ablation lattice** isolating the value of the
   studied artifact vs. raw doc access vs. iterative meta-harness
   editing.
4. **Doc-anchored 3-way regression attribution** as an independent
   contribution attacking AHE's regression-prediction weakness.
5. **Empirical demonstration** on GEOS, with cross-tool transfer to
   FEniCS/MOOSE as a stretch goal — including a deliberately
   post-training-cutoff condition to neutralize the
   "model-already-knows-this" critique.

---

## 8. Risks and how we'll address them

| Risk | Likelihood | Mitigation |
|---|---|---|
| Frontier LLMs already know the docs; $\hat D$ is a no-op | Medium | Post-cutoff tool-version condition; private-doc condition if accessible |
| Subagent traversal hits cost/wall-clock issues (Matt's prior negative experience) | Medium | Restrict subagent use to bounded-context section reading only; serial controller for graph maintenance |
| Hierarchical coalescing loses information at higher levels | Medium | Ablate the levels of hierarchy; show degradation with each loss |
| MoSciBench-style: structure hurts in some tools | Low-Medium | Run A0 (no docs) as a sanity baseline; show A3 beats it |
| Doc-anchored attribution doesn't beat AHE | Medium | This is the hypothesis; negative result is publishable as "constraining attribution doesn't help, here's why" |
| Single-tool result fails to generalize | Medium-High | Cross-tool transfer is the stretch goal precisely because this is the high-risk part of the claim |

---

## 9. Timeline (rough)

- **Weeks 1–2:** Build study pipeline (subagent traversal + section
  notes + hierarchical roll-up); validate $\hat D$ structure on GEOS
  docs end-to-end; produce inspectable artifact.
- **Weeks 3–4:** Implement A0–A4 ablations; collect treesim/end-to-end
  metrics on existing 17-task and 36-task grids.
- **Weeks 5–6:** Build the iterative meta-harness $M$ (A5);
  bipartite-graph editing rules; attribution loop (C3).
- **Weeks 7–8:** Post-cutoff / private-doc experiments; honest write-up
  of in-distribution risk.
- **Weeks 9–10:** Cross-tool transfer to FEniCS or MOOSE.
- **Weeks 11+:** Write-up.

---

## 10. Concrete next steps (this week)

1. Sharpen this proposal with advisor + post-doc input.
2. Implement the minimum viable study pipeline on GEOS sphinx docs
   (overnight sanity-check artifact ships with this document — see
   `docs/2026-05-18_overnight-summary.md`).
3. Read SkillFoundry's repo code (not just paper) for actual prompts
   and schemas — LN-004's open questions need closing.
4. Read AHE's Agent Debugger implementation for prior-art comparison
   to doc-anchored attribution.
5. Pick the post-cutoff tool/version for the in-distribution-risk
   experiment.

---

## 11. Open questions for advisor + post-doc

1. **Single-tool depth vs cross-tool breadth.** Is Paper 2 better as a
   deep GEOS study with cross-tool as future work, or do we need
   cross-tool transfer in the headline result?
2. **Coding-agent vs staged-pipeline meta-harness.** We're leaning
   staged. Comfortable?
3. **Meta-harness proposer model.** Iteration budget is the dominant
   cost. Acceptable to use a stronger model (Gemini 3 Pro / Opus 4.6)
   for $M$ while using DSv4-flash for $H$, or do we hold the line on a
   single cheap model throughout?
4. **End-to-end simulation as a metric.** Treesim is what we have
   working. End-to-end is slower but more meaningful. Worth investing
   in for at least the held-out subset?
5. **Adversarial review.** Should we get external (Codex / Cursor /
   another lab) review of $\hat D$'s structure before locking it in?
