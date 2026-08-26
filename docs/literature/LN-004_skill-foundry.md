---
id: LN-004
title: "SkillFoundry: Building Self-Evolving Agent Skill Libraries from Heterogeneous Scientific Resources (Shen et al., 2026)"
date: 2026-05-14
arxiv: 2604.03964v1
url: https://arxiv.org/abs/2604.03964
project_page: https://ma-compbio-lab.github.io/SkillFoundry/
code: https://github.com/ma-compbio-lab/SkillFoundry
authors: Shuaike Shen, Wenduo Cheng, Mingqian Ma, Alistair Turcan, Martin Jinye Zhang, Jian Ma
groups: CMU (Ray and Stephanie Lane Computational Biology Dept; ML Dept)
dag_nodes: []
related_to: [LN-002_memp, LN-003_meta-harness]
---

# SkillFoundry — Personal Reading Note

Read directly from the PDF (19pp + appendix). The GPT summary in
`meta_harness_reading/skill_foundry.md` is roughly accurate on the
high-level pipeline but **misses the most important architectural
detail**: this is **not** a coding-agent loop in the Meta-Harness sense.
It is a **staged GPT-5.4 pipeline** with structured JSON schemas at every
stage. That changes how the work compares to MH/MCE/AHE and to us.

## What it actually is

A self-evolving framework that converts heterogeneous scientific
artifacts (repos, APIs, scripts, notebooks, databases, docs, papers)
into a library of **executable, validated, novel skill packages**.

- 286 skills, 27 domains, 254 subdomains, 394 mined resources at
  paper time.
- 71.1% claimed novel vs SkillHub + SkillSMP (the rest get merged or
  pruned).
- Improves Codex on 5/6 MoSciBench datasets (Repo-Acc 61.2 → 66.7;
  Paper-Acc 43.9 → 53.1; exec stays 100%).
- Boosts Biomni on the scDRS workflow that wasn't in its preset
  catalog (qual 7/7 in best run; RMSE 0.11 → 0.02 vs expert).

The skill-package contract is the unit of contribution: scope,
inputs/outputs, dependencies, execution steps, env assumptions,
provenance, examples, executable scripts, repo-level tests.

## How the loop actually runs

Six stages, staged-prompt pipeline (not a free-form coding agent):

```
tree_check → resource_search → skill_build → skill_test → refresh
                                              ↓
                                      tree_expansion / tree_refinement
```

Every stage has a **system prompt with `Response Contract: JSON
matching stage schema`** (App. A.1.7). Different GPT-5.4 variants
allocated by stage:

- `resource_search` — GPT-5.4 **high reasoning** (the only default
  high-effort stage; authors say search/triage is the most
  reasoning-intensive part).
- `tree_check`, `skill_build`, `refresh`, `design_skill` — GPT-5.4
  medium.
- `skill_test`, `layer1_fix`, `layer2_benchmark`, `layer2_optimize`,
  `novelty_check` — GPT-5.4-**mini**.

This is meaningful: SkillFoundry buys most of its smarts at *resource
triage*, not at coding. Compare to Meta-Harness, where the entire
proposer is Claude Code (Opus-4.6) with free file access. **Different
bet about where the bottleneck is** — for SF it's "which authoritative
artifact to mine"; for MH it's "what diagnosis to do over prior
runs."

## The domain knowledge tree

- Rooted tree `T = (V, E)`. Internal nodes = domains/subdomains; leaves
  = actionable skill targets.
- **Initial taxonomy is manually curated** ("intentionally broad,"
  spans computational biology + chemistry + visualization + workflows
  + spatial transcriptomic analysis + scientific agents). Updates are
  data-driven but the seed is human.
- Branch prioritization: pick branches with *abundant resources but
  weak verified skill coverage* — high marginal value first. Not
  uniform search. (App. A.1.1.)
- Branches split when stable subareas emerge; stale/redundant leaves
  merged/pruned.
- The tree doubles as (a) ontology over the domain and (b) index of
  current library state.

This is their headline structural choice and the part most relevant to
us.

## Resource mining and skill extraction

Key quote (§3.3): "Resource search prioritizes **authoritative
artifacts**, such as official documentation, maintained repositories,
package references, workflows, notebooks, and method papers, so that
skill induction is grounded in reliable sources rather than generic
web text."

This is the doc-grounding overlap with our project — but it's a
*priority list*, not a structural commitment. Docs are one source
among several; they're not modeled differently from a maintained
GitHub repo.

The extracted "operational contract" goes into a compiled skill
package: human-readable instructions + machine-readable metadata +
executable scripts + tests + provenance.

## Three-layer validation + repair

Layer 1: **Execution testing** — does the skill run under its
declared contract? Failures trigger a repair loop.

Layer 2: **System testing** — for skills depending on SLURM /
cluster / env modules.

Layer 2': **Synthetic-data testing** — mock inputs when real
execution is expensive/unstable. Checks **contract completeness**
(does the skill accept all declared args, produce declared outputs?)
and **behavioral stability** (same input → same output without hidden
state). Explicitly **not** a downstream-task correctness check.

App. A.1.3 adds a "Layer 2 benchmark" stage: build a **no-skill
baseline** for task-specific cases, compare skill vs no-skill; if
gain is weak, enter optimization loop. This is a kind of within-loop
ablation.

## Novelty + tree update

Novelty check is heuristic — searches SkillHub and SkillSMP by
keywords from the task description, plus considers scope, provenance,
intended use. Three possible outcomes: accept-as-new-leaf, merge,
prune. Outcomes write back to the tree.

## Experiment summary

**MoSciBench** (Codex agent, with/without SF library):
- avg Repo-Acc 61.2 → 66.7; Paper-Acc 43.9 → 53.1
- 5/6 datasets improve, 1 unchanged (nurse_stress, strong baseline)
- Largest gains: health_spa, pop_genetics, cyclone
- Exec stays at 100% throughout — so gains are *procedural*, not
  *executability*.

**Cell type annotation** (MERFISH developing human heart):
- Codex alone: 81.1% coverage / 68.5% accuracy
- Codex + SF (skill synthesized on-the-fly): 99.2% / 82.9%
- SpatialAgent (curated, uses external reference): 100% / 87.1%
- SF closes most of the gap to a domain-specific agent **without**
  external reference data.

**scDRS workflow** (transferred into Biomni):
- Biomni: qual 3-4/7, RMSE 0.16
- Biomni + SF: qual 7/7 in best run, RMSE 0.02
- Biomni *without* skill consistently dropped the `filter-data`
  param → noisy unfiltered scoring. Procedural-detail failure mode.

The strongest experiment is scDRS because it's a **transfer test**
into an external agent (Biomni didn't have scDRS in its preset
catalog) and uses **blinded expert review**.

## Limitations the paper admits

- Coverage limited (~286 skills, biomedical-heavy).
- Most skills validated only via internal tests, not broad downstream
  validation.
- Narrow eval scope (a few domains/tasks).
- Cautions against use in high-stakes settings.
- No ablation isolating which components matter most.
- Novelty metric is heuristic (lexical against two external libs).

## What's genuinely useful for us

1. **Domain tree as combined ontology + state-tracker.** The bipartite
   role (taxonomy + coverage index) is a structural primitive worth
   borrowing for documentation-section coverage.
2. **Branch prioritization by "abundant resources / weak verified
   coverage."** Concrete signal for budget allocation we could apply
   to *doc-section* coverage rather than capability coverage.
3. **Operational contract format.** A clean way to define what a
   harness component must declare.
4. **Three-layer validation (exec / system / synthetic).** The
   synthetic layer's distinction between *contract completeness* and
   *behavioral stability* is a useful frame.
5. **Layer-2 benchmark is a within-loop ablation.** Build the
   no-skill baseline automatically — they're auto-comparing
   with/without on task-specific cases. Worth borrowing for any
   doc-grounded harness component.
6. **scDRS transfer experiment is the template.** External agent
   takes the synthesized artifact; we evaluate on real workflow with
   blinded expert review. Strong evaluation shape.

## What's different from our problem

Skill-Foundry is **breadth-first** — mining many small skills across
many subdomains. We're **depth-first** — building one tightly
coupled harness for one elaborate tool (GEOS, FEniCS, MOOSE class
of system). Concrete divergences:

- **Granularity.** SF skill = single capability extracted from a
  resource. Ours = entire harness around a tool, with internal
  components that *jointly* read the same doc.
- **Tree axis.** SF's tree axis is *capability / subdomain*. For us
  the relevant axis is *document section* and/or *tool concept*.
- **Loop target.** SF iterates to *expand coverage* of the skill
  library. We iterate to *deepen fidelity* of a single harness to
  one tool's documented behavior.
- **Validation target.** SF tests skills in isolation. Our test
  surface is an end-to-end harness output (e.g., generated GEOS
  input XML) — composition matters, not unit correctness.
- **Doc role.** SF treats docs as one of several authoritative
  artifacts to mine *for skills*. We want docs as the **primary
  substrate the harness retrieves from at runtime** and the
  **primary signal the meta-harness uses to attribute failures**.

## Where SF is conceptually similar

- Priority for authoritative artifacts (their words) — same instinct
  as our doc-grounded framing.
- Tree-state controller for adaptive mining → analogous to
  doc-section coverage tracking.
- Multi-layer validation → analogous to the staged doc-grounded
  tests we'd want.
- Staged pipeline with JSON schemas → an architectural alternative
  to MH's free-form coding agent that we should compare against.

## Note on the "GPT vs coding-agent" axis

This is the most interesting design-space division across the four
papers:

| Paper | Outer proposer | Outer interface | Bet |
|---|---|---|---|
| Meta-Harness | Claude Code (Opus 4.6) | free FS access | unrestricted diagnostic reasoning |
| MCE | MiniMax M2.1 meta-agent | agentic skill evolution over file/code artifacts | learnable skill recombination |
| AHE | GPT-5.4-high evolve-agent | NexAU file-level edit substrate + distilled traces | observability + falsifiable edits |
| SkillFoundry | GPT-5.4 mix per stage | staged prompts + JSON schemas | structured branch search over a tree |

We need to choose deliberately where on this axis to operate. The
docs-grounded angle works for any of these, but the *novelty case*
is strongest at the Meta-Harness end (where docs are otherwise
unstructured) and weakest at the SkillFoundry end (where docs are
already prioritized inside a staged pipeline).

## Open questions / things to check

- SF code is on GitHub (`ma-compbio-lab/SkillFoundry`). Worth
  cloning to read the actual prompts and schemas — paper appendix
  shows abbreviated templates.
- Does SF's resource search actually parse documentation structure
  (headings, schema vs example vs tutorial), or just treat doc pages
  as text? Paper does not say — code may reveal.
- For the scDRS experiment, can we get the synthesized skill itself
  (it's "exported to Biomni as an external resource") and inspect
  what doc-derived knowledge ended up in it?
- No ablation on whether the *tree structure* matters vs flat skill
  library — a natural baseline for us to also probe in our setting.
