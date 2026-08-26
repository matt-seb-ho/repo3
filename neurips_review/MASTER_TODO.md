# SIGA Rebuttal — Master TODO

**Hard deadline: Aug 3.** Phase 3 (Aug 3–10) is reviewer/AC discussion only — we cannot post or even see it. Anything landing after Aug 3 is worthless for the decision.
**Initial response: Jul 27**, built entirely from data already on disk. Nothing below in "New evidence" may be load-bearing for it.

Owners: **MH** Matthew Ho · **BL** Brian Liu · **AW** Audrey Wang · **LQ** Lianhui Qin

---

## P0 — Blocking. Nothing gets quoted to reviewers until these clear.

| # | Task | Owner | Why blocking |
|---|---|---|---|
| 1 | **Resolve F3 (R+S): is it 0.874 or 0.857?** Recompute from `/data/shared/geophysics_agent_data/data/eval/autocamp_2026-05-01/dsv4/autocamp_F3/`. Determine why it moved (re-score / re-run / replaced seed / failures-as-zero applied later). | MH | The main-effects correction we plan to volunteer depends entirely on which value is right. Publishing a "correction" that is itself wrong is unrecoverable. |
| 2 | **Regenerate every derived table/figure** from current results and diff against the submitted paper. | MH | The appendix main-effects table went stale after F3 moved. If one derived number went stale, others may have. |
| 3 | **Verify the schema-validity ladder** (Vanilla 24/30 vs 30/30 SIGA) against `/data/shared/...`. | MH | Centrepiece of the response to the AC's primary objection. Currently sourced from a plan doc, not from a file we've re-run. |
| 4 | **Verify every number destined for a response** traces to a file on disk. | MH | Standing rule. gep1 recomputes things. |

## P1 — High value, cheap, do this week

| # | Task | Owner | Notes |
|---|---|---|---|
| 5 | **Rung-3 sweep: `geosx --validate-input` across Vanilla / best combo / SE on held-out.** | MH or BL | **Best value-per-hour item on the entire list**, and it was missing from the TODO. It is literally gep1's ask ("does it run in GEOS"), it's minutes per deck, and it needs no QoI machinery. Do this *before* the case studies. Env: `export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH` |
| 6 | **Write up the existing S/X separation.** `C2→C6` (add hook-enforced validator) = **+0.008**; `C6→C7` (add agent-callable validator on top) = **−0.007**. Source: `docs/2026-04-30_dsv4-ablation-final-v2.md`. | MH | This was marked Low Prio, but gep1 flagged S/X as **score-moving** and we already have the answer. It's a writeup, not an experiment. Caveat honestly: val-only, and val is at ceiling. |
| 7 | **Write up the prefix-bug probe.** C2 (prefix) 0.9134 vs C9 (no prefix) 0.9170, **Δ = +0.0036**, zero big-swing tasks, 3 seeds × 17 tasks. | MH | gep1's other score-moving item, also already answered. No rerun needed. |
| 8 | **Fix the "+0.24" mis-citation** in `src/runner/agents.py:425`, `docs/2026-05-03_minimax-pseudo-tool-call-analysis.md`, `docs/2026-05-04_cross-cutting-paper-section.md`, `docs/2026-05-04_remaining-todos.md`. The real number is **+0.004**; +0.24 was the C1→C2 lift being *explained*, not the prefix's effect. | MH | Someone will otherwise quote +0.24 into a rebuttal. |
| 9 | **Confirm Claude Code version** from an autocamp `events.jsonl` (expect `2.1.119`). | MH | 10 minutes. nBNe's cheapest ask. |
| 10 | **Tell BL to stop/deprioritize the GEOS compile** — see P2 #11. | MH | Today. Prevents days of wasted TPL work. |

## P2 — New evidence. Real value, but nothing here may block the Jul 27 response.

| # | Task | Owner | Notes |
|---|---|---|---|
| 11 | **GEOS on server 6** — **downgraded from blocking to optional.** A working binary already exists at `/data/jixuan/geophysics/GEOS/install-your-platform-release/bin/geosx` (needs `LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu`). First action: BL spends 30 min confirming it validates *our* decks. Only pursue a fresh compile as a **parallel, non-blocking** track — TPL builds routinely take days and we have 8. | BL | Value of a fresh build: we own it, current schema (the jixuan binary is 263 elements vs our XSD's 269 — 6 missing, but only 3 of 746 reference decks touch them), and more compute for parallel runs. None of that is worth risking the window. |
| 12 | **LMaaJ as secondary metric (input side)** — judge generated deck vs reference deck, to cover the semantics TreeSim's `rtol=1e-6` cannot express. | MH | Prompt: `prompts/01_lmaaj_metric.md`. No GEOS binary needed → highest feasibility. |
| 13 | **2× execution case study** — run decks through GEOS, show what a TreeSim gap means physically. | MH | Prompt: `prompts/02_execution_case_studies.md`. Smoketest one task before estimating anything. |
| 14 | **Agent-as-a-Judge on GEOS *outputs*** — distinct from #12. #12 judges input decks; this judges simulation results. | BL | **Gated on #5/#13 working.** Do not start until decks actually execute. Overlaps with #13's QoI step — coordinate so you don't build two comparison pipelines. |
| 15 | **Scale OpenFOAM to 3 seeds and record successful runs.** | BL | Quietly one of the best items on the list: "successful runs" is **execution evidence on a second simulator**, and OpenFOAM may be far easier to execute than GEOS. Report runnability as a first-class result, not a footnote. |
| 16 | **Scale LAMMPS to 20 tasks × 3 seeds.** | AW | **Fix the judge before scaling.** The current LAMMPS LLM judge is one of the two backbones it scores — reviewers punish exactly this. Use a third-family judge, or the scale-up buys nothing. |
| 17 | **Per-task QoI definition** ("invent algorithm for each deck for evaluation"). | BL + MH | This is the rung-5 comparison rule. Handled inside #13's procedure — see the prompt for the preference order (injected TimeHistory → VTK final-state summary stats → log-scraped globals). Don't design it separately. |

## P3 — Low priority

| # | Task | Owner |
|---|---|---|
| 18 | New ablations to further isolate S from X beyond what #6 already shows | MH |
| 19 | TreeSim for OpenFOAM (decks are directory trees of dict files, not XML — doesn't port directly) | BL |

## Writing

| # | Task | Owner | Due |
|---|---|---|---|
| 20 | **Draft 4 responses, not 3** — gep1 (~9,500 chars), kEdh (~7,000), nBNe (~3,500), **and a separate AC comment (~5,000)**. The handbook says the meta-review is the guide, so the AC text matters most. | MH | **Jul 27** |
| 21 | Post initial responses early on Jul 27 ("engage early and engage often") | MH | Jul 27 |
| 22 | Monitor and answer follow-ups within a day | MH | Jul 28 – Aug 3 |
| 23 | Post any new evidence as follow-up comments as it lands | MH | → Aug 3 |

Prompt for #20: `prompts/03_rebuttal_drafting.md`

## Awaiting Lianhui

| # | Question |
|---|---|
| 24 | **R2 / clarity posture** — how hard can we commit to the camera-ready rewrite in writing? |
| 25 | Is the arXiv version publicly posted? Governs whether we may quote it verbatim or must paraphrase (anonymity). |
| 26 | Comfortable volunteering the main-effects correction? |
| 27 | Pre-empt tehe human-baseline anomaly (one expert's score drops 0.812 → 0.689 between sessions), or wait to be asked? |

---

## Sequencing — the 36 hours to Jul 27 AOE (05:00 PT, Jul 28)

**Measured today, which changes the scope:** `geosx -v` (validate-input) runs in **~2.5 s/deck**, and a **full** run of a `_smoke.xml` variant takes **~8.9 s** and emits TimeHistory HDF5 (QoI) plus VTK (visualization). Held-out is 30 task-runs per cell. So the entire execution ladder is **~20 minutes of compute** for 3 cells — the cost is harness-building, not simulation.

| Hours | Track | Est. |
|---|---|---|
| 0–2 | **P0 verification** (#1–#4) — blocking, needs judgment, do first | 1–2 h |
| 2–8 | **Track A: execution ladder** — rung 3 across F0/F6/SE × 10 tasks × 3 seeds, then rungs 4–5 on the 2 case-study tasks | 4–6 h |
| 2–8 | **Track B: LMaaJ** — 90 decks × 3 judges × 2 orders ≈ 540 queries, ~30–60 min wall clock; rest is pipeline + rubric + inspection | 4–6 h |
| 2–3 | **Track C: writeups** — S/X (#6), prefix probe (#7), +0.24 fix (#8), version (#9); data already in hand | ~1 h |
| 12–30 | **Draft four responses** — first complete pass from P0 + Track C only, then fold A and B in as they land | 6–10 h |
| 30–36 | Final number check against provenance table · human review · post early | — |

Tracks A, B, C are independent and should run concurrently. **Drafting must not wait on A or B.**

**Scope call:** A, B, and C all fit. The binding constraint is drafting time and human decision latency, not compute.

## After Jul 27

```
Jul 28–31  → OpenFOAM seeds (#15) · LAMMPS (#16) · output-side judge (#14) · rungs 4–5 on more tasks
Aug 1–2    → post whatever landed as follow-up comments
Aug 3      → last day we can post anything. Final summary to the AC.
```

**Do not promise a delivery date for the execution study.** A missed promise lands immediately before Phase 3, when we can no longer respond to it. Post it if it lands — pure upside, no downside.
