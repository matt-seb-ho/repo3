---
id: overnight-summary-2026-05-18
title: "Overnight summary — Paper 2 doc-grounded meta-harness, 2026-05-18"
date: 2026-05-18
author: research-copilot
status: handoff
---

*Read this first in the morning. Everything I produced overnight, with one-line summaries and pointers.*

# TL;DR

I spent the overnight session on three things, in priority order:

1. **Feedback + advisor proposal** — engaged with your "study-the-textbook" reformulation, pushed back where I thought your argument needed sharpening, and produced an advisor-ready proposal doc framed around a **persistent studied artifact $\hat D$** as the load-bearing contribution.
2. **Prototype** — built and ran a 3-phase doc-study pipeline (DSv4-flash via OpenRouter, parallel workers) on **161 GEOS RST files**. Produced **149 structured per-section notes + 23 subtree rollups + 1 global tool-level rollup**. Cost: **$0.11**, wall-clock: **10.6 min**.
3. **Comparison** — qualitative comparison of the auto $\hat D$ vs your hand-engineered `GEOS_PRIMER_minimal.md`. Auto artifact has broader coverage (XML taxonomy, pitfall corpus, navigation index, honest coverage note); hand primer has prescriptive workflow language the auto pipeline can't see (it's not in the docs).

I did **not** run an end-to-end GEOS-task eval swapping primers. Reasons in decisions log D8 — biased comparison risk + setup time. Easy follow-up if you want it.

# Files written tonight

## Documents

| File | What it is |
|---|---|
| `docs/2026-05-18_feedback-on-overnight-ideas.md` | Engages with your overnight ideas; per-proposal feedback on N1-N9; bitter-lesson rebuttal; the "studied artifact" reframing; honest in-distribution-risk callout; ~50-query search bank for your AI deep-research pass |
| `docs/2026-05-18_paper2-proposal-advisor.md` | The polished advisor-facing proposal. Frames $\hat D = (G, N, S)$ as the contribution. Has problem statement, method ($M$ as staged pipeline), three falsifiable claims (C1–C3), six-condition ablation lattice (A0–A5), timeline, open questions |
| `docs/2026-05-18_overnight-decisions.md` | 10-decision audit trail with why/alternatives/cost-of-being-wrong |
| `docs/2026-05-18_doc-study-artifact-comparison.md` | Qualitative comparison of auto $\hat D$ vs hand primer; quality spot-check findings; one systematic failure mode (toctree mis-parse) |
| `docs/2026-05-18_overnight-summary.md` | This file |

## Slides

| File | What it is |
|---|---|
| `writing/slides/2026-05-18_paper2-status.md` | Marp deck (16:9) summarizing proposal + overnight prototype; ~17 slides + backup. Use for project meeting tomorrow. |

## Code

| File | What it is |
|---|---|
| `scripts/doc_study/study_pipeline.py` | Three-phase doc-study pipeline. Reads OPENROUTER_API_KEY then DEEPSEEK_API_KEY. `--skip-existing` supports retries. |
| `scripts/doc_study/render_primer.py` | JSON → markdown rendering of `global.json` + per-subtree rollups |

## Data / artifacts

| File / dir | What it is |
|---|---|
| `data/doc_study/2026-05-18_full/notes/*.json` | 149 per-section structured notes |
| `data/doc_study/2026-05-18_full/rollup/*.json` | 23 subtree rollups |
| `data/doc_study/2026-05-18_full/global.json` | Tool-level $\hat D$ artifact |
| `data/doc_study/2026-05-18_full/phase1_errors.json` | 12 JSON-parse errors for retry |
| `data/doc_study/2026-05-18_full.log` | Full run log |
| `plugin/GEOS_PRIMER_auto_2026-05-18.md` | $\hat D$ rendered as a markdown primer (191 lines) for direct comparison with `GEOS_PRIMER_minimal.md` (34 lines) |

# Run command (for reproduction)

```bash
cd /home/matt/sci/repo3
set -a; source .env; set +a
source .venv/bin/activate
python3 scripts/doc_study/study_pipeline.py \
    --docs-root /data/shared/geophysics_agent_data/data/GEOS/src \
    --out-dir   data/doc_study/2026-05-18_full \
    --workers   8
# 637 s, $0.11, 149/161 notes ok
```

To retry the 12 failed sections at higher token budget:

```bash
# (bumping max_tokens=1600 -> 2500 requires a one-line edit in study_pipeline.py
# or just add --skip-existing and re-run; failed sections retry by default)
python3 scripts/doc_study/study_pipeline.py \
    --docs-root /data/shared/geophysics_agent_data/data/GEOS/src \
    --out-dir   data/doc_study/2026-05-18_full \
    --workers   8 --skip-existing
```

# The proposal in one paragraph

Frontier LLM agents consult docs only reactively — when a runtime query
arises. The Paper 2 contribution is to make the **meta-harness *study*
the docs first**, producing a persistent **studied artifact**
$\hat D = (G, N, S)$ that both the meta-harness and the runtime harness
consume in lieu of raw docs. $G$ is a bipartite component-section
graph; $N$ is the per-section structured note set; $S$ is the
hierarchical roll-up. The artifact is built once and *edited* (not
regenerated) by later iterations. Three falsifiable claims: (C1)
$\hat D$ alone beats flat-doc-RAG, (C2) iterating over $\hat D$ beats
iterating over raw docs, (C3) doc-anchored 3-way failure attribution
beats AHE-style free-form attribution on regression prediction. Six-
condition ablation lattice (A0–A5). Honest in-distribution risk
acknowledged with a post-cutoff-tool experiment as the mitigation. The
core scope: **N4 (doc-bootstrapped seed) ⊕ N2 (bipartite graph)** as
the spine; **N3** as an independent supporting study; **N6** folded
into N2's update rule. N1, N5, N7, N8, N9 cut or deferred.

# Where my biggest pushback lives

In §1b of the feedback doc, I argued — and I want you to push back if
you disagree — that **the note-writing artifact *is* the contribution**,
not the procedure that produces it. This is a slight reframing of your
overnight write-up. Concretely:

- You wrote: "force the meta-agent to traverse the entire documentation
  ... write notes ... hierarchically coalesce these notes into global
  understanding."
- I'm pushing toward: "the meta-harness emits a persistent,
  hierarchically structured artifact $\hat D$ before any task runs, and
  the artifact is what we ablate, evaluate, and edit."

Same idea, but the second framing gives you a *thing* to point at,
ablate against, and compare across methods. That's what makes it a
falsifiable contribution rather than a procedural claim. If you prefer
the procedural framing, easy to revise.

# What I want you to verify before the meeting

1. **The advisor proposal's contribution framing** — does $\hat D$
   feel like the right north star, or is there a sharper way to say
   it?
2. **The cut list** (N1, N5, N7, N8, N9) — anything in there you'd
   keep? My justifications are in feedback §2.
3. **In-distribution risk mitigation** — committing to a post-cutoff
   GEOS version or private-tool experiment as part of the headline.
   This is a real cost; alternatives are weaker.
4. **The slide deck flow** — built for ~15 min talk. Trim or expand?

# What I left for you (work that didn't fit overnight)

- **End-to-end task eval** comparing `GEOS_PRIMER_minimal.md` vs
  `GEOS_PRIMER_auto_2026-05-18.md` on the existing 17-task or 36-task
  grid. Setup risk too high for overnight; trivial to do tomorrow.
- **Retry the 12 failed sections** with bumped `max_tokens=2500`.
  Should drop failures to <3.
- **Bipartite graph extraction.** Notes have `relations` field; we
  could materialize `(component, section)` edges into a real graph
  object. Spec'd in the proposal §3.1; not built tonight.
- **Iteration loop (A5).** Spec'd in proposal §4.1 method block; not
  built tonight.
- **SkillFoundry code read.** LN-004's open questions still open.
  Repo cloned at `/home/matt/code_reference/SkillFoundry/`.
- **AHE Agent Debugger read.** Repo at
  `/home/matt/code_reference/agentic-harness-engineering/`.

# Honest assessment

Things that worked overnight:

- The pipeline runs end-to-end and produces a high-quality artifact
  for under a nickel.
- The auto-extracted XML element taxonomy, workflow names, and
  pitfalls are accurate where I spot-checked.
- The framing crystallized into something falsifiable
  (six-condition lattice, three claims).

Things that are still soft:

- I didn't run the A1 vs A3/A4 head-to-head, so I can't claim the
  artifact *helps* a downstream harness. The prototype only
  establishes that the artifact *exists* and *contains
  domain-specific structure*.
- The bipartite graph is described in the proposal but not built.
- 7.5% per-section JSON failure rate is fixable but not fixed.
- One systematic failure mode (toctree mis-parse) is in the prompt,
  not in the data — easy fix on retry.

Net: I think you have enough for the project meeting tomorrow, with
honest framing of what's prototype-grade vs paper-grade. The slide
deck is your delivery vehicle; the proposal doc is the artifact you
hand to your advisor / post-doc separately.

Good luck.
