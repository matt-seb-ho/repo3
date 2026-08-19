---
id: D-011
title: Adopt Self-Harness + AHE + GEPA as SIGA-Evolve v2; retire the v1 reflection loop
date: 2026-08-19
dag_nodes: [I12]
links:
  supersedes: [D-007, D-008]
  evidence: [docs/2026-08-19_method-adoption-plan.md]
---

# D-011 — SIGA-Evolve v2

## Decision

Rebuild the self-evolution loop as a **regression-gated, evidence-rich,
archive-backed search** over a *manifest-described* adapter:

- **Self-Harness** (arXiv:2606.09498) — weakness mining → minimal proposal →
  regression-gated validation. Supplies the selection operator v1 lacked.
- **AHE** (arXiv:2604.25850) — component / experience / decision observability.
  Supplies the evidence layer and the argument for widening the search space
  beyond prose.
- **GEPA** (arXiv:2507.19457) — used *as a library* for the Pareto archive,
  acceptance hook, and rollout budget. Sample efficiency is the binding
  constraint here, and GEPA is the candidate designed for that regime.
- **ACE** (arXiv:2510.04618) — delta-update discipline for the memory component
  only, under a hard token budget.

## Why

Three findings, established from committed artifacts (`docs/2026-08-19_method-adoption-plan.md` §1):

1. **The v1 loop had no reward channel.** `run_full_evolution.sh` never scored a
   round before reflecting on it; every `.reflection_meta.json` records
   `round_mean_treesim: 0`. There is no mechanism by which the search could have
   improved anything except by chance.
2. **The paper's own table already shows self-evolution contributed nothing.**
   Held-out-eval: S+X+M `0.783 ± 0.022`, SE `0.789 ± 0.012`,
   SE-prose `0.775 ± 0.024` — all the same cell shape. The headline `+0.069` is
   `Vanilla → S+X+M` plus `±0.008` of noise at `n = 3`.
3. **`plugin_evolving/v4` is a ground-truth exposure** (task → canonical-XML
   table for all 17 val tasks), wired into `scripts/launch_autocamp_v4.sh`. Not
   used by any published number (SE = v3), but live in the tree.

## Sequencing

1. **De-risk first** (~$3, ~2 h): S+X+M vs SE on the held-out split at `n = 5`,
   paired per-task. Predicted: the paired CI spans zero.
2. **Quarantine + hygiene** (~6 h): done on `feat/siga-evolve-v2`.
3. Build v2 (~76 h, ~$58 API) — see §6 of the plan.
4. Compute-matched baselines are **mandatory**, not optional (arXiv:2607.12227).

## Explicitly rejected

- **DGM / Hyperagents open-ended archive over the full harness program.** Needs
  cheap plentiful evaluations (ours are ~25 min/task-run over ≤17 tasks) and
  requires unfreezing the base harness, which is SIGA's framing.
- **Any retrieval-gated memory module.** The local zero-call result on the
  `memory_lookup` MCP tool is decisive: import update mechanisms, deliver
  content always-on.

## Constraints honoured

`src/runner/` and `src/eval/` untouched (`.copilot/direction.md`); model and base
harness frozen; contamination logic extended by a *superset* gate in
`src/evolve/hygiene.py` rather than modified in place — but the evidence layer
does increase the leakage surface and needs a re-audit before any run
(plan §7.5).
