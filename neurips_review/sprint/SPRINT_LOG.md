# SIGA Rebuttal — Autonomous Sprint Log

**Mission:** four NeurIPS 2026 author responses for submission 31642 (SIGA) + as much new evidence as fits, by **Jul 27 AOE (05:00 PT Jul 28)**.
**Sprint start:** 2026-07-26 21:57 UTC.
**Scores:** gep1 4 (borderline accept, conf 3) · kEdh 2 (reject, conf 4) · nBNe 5 (accept, conf 5) · AC borderline.
**Deliverable dir:** `neurips_review/responses/`. **Provenance:** `neurips_review/sprint/PROVENANCE.md`.

Master log. Per-thread detail lives in `threads/`. Newest entries at the bottom of each section.

---

## Thread register

| Thread | Owner | Scope | Log | Status |
|---|---|---|---|---|
| **P0** | main | Phase 0 item 1: resolve F3 (R+S) = 0.874 or 0.857, and why it moved | `threads/P0_verification.md` | — |
| **A1** | subagent | Ladder rungs 1–3: `xmllint` schema validity (all 6 held-out cells) + `geosx -v` rung 3, with failure classification | `threads/A1_ladder_rungs123.md` | — |
| **A2** | subagent | Ladder rungs 4–5: reference-deck gate, smoketest, full runs, QoI extraction, case studies | `threads/A2_execution_rungs45.md` | — |
| **B** | subagent | LMaaJ secondary metric, 3 cells × 10 tasks × 3 seeds, multi-judge + position swap | `threads/B_lmaaj.md` | — |
| **C** | subagent | Track C writeups: S/X separation, prefix-bug probe, "+0.24" mis-citation fix, Claude Code version | `threads/C_writeups.md` | — |
| **D** | subagent | Phase 0 item 3: regenerate every derived table/figure, diff against submitted `writing/neurips/neurips_2026.tex` | `threads/D_derived_tables.md` | — |
| **E** | main | Phase 2: draft the four responses | `threads/E_drafting.md` | — |

---

## Environment verified at sprint start

| Fact | Value | Verified how |
|---|---|---|
| GEOS binary | `/data/jixuan/geophysics/GEOS/install-your-platform-release/bin/geosx` (228640 bytes, mtime Jan 15 2026, owner `jixuan`) | `ls -la`; `--help` prints usage incl. `-v, --validate-input` |
| `LD_LIBRARY_PATH` fix | `export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH` required | per plan §0; binary responds |
| Held-out generated decks | `/data/shared/geophysics_agent_data/data/eval/autocamp_followup_2026-05-02/icl/{autocamp_F0,F4,F6,F8,F11,SE}` | `ls` — 6 cells present |
| Held-out scores | `…/autocamp_followup_2026-05-02/_results_icl/{F0,F4,F6,F8,F11,SE}_icl_s{1,2,3}` | `ls` — 18 dirs present |
| Val (17-task) results | `/data/shared/geophysics_agent_data/data/eval/autocamp_2026-05-01/dsv4/autocamp_{F0..F8,F11,SE,v4,p_contract,p_method}` | `ls` — all cells present |

---

## Decisions log

| # | Time (UTC) | Decision | Rationale |
|---|---|---|---|
| D1 | 07-26 21:57 | Merged Phase 0 item 2 (verify schema-validity ladder) into Track **A1** rather than running it separately | Rungs 1–2 are the same `xmllint` sweep A1 needs anyway; splitting risks two agents publishing inconsistent validity numbers. A1 is instructed to deliver the rung 1–2 table *first*, before touching rung 3, since it is blocking. |
| D2 | 07-26 21:57 | Split Track A into **A1** (rungs 1–3, cheap/certain) and **A2** (rungs 4–5, expensive/risky) | Rung 3 is gep1's literal ask and must not be delayed behind full-run harness building. Independent agents = rung 3 lands even if rungs 4–5 stall. |
| D3 | 07-26 21:57 | Skipped `/loop 15m` checkpoint writer; maintaining this sprint log + thread logs continuously instead | A 15-min re-invocation loop interleaves with subagent orchestration and would fragment the main thread. This log serves the same recovery purpose and is what the operator asked for. Flagged for the human. |
| D4 | 07-26 21:57 | Track C also owns Phase 0 item 4 (Claude Code version from `events.jsonl`) | 10-minute task, same class of work (verify-a-number-from-disk), no reason to occupy a slot. |

---

## Overnight experiment round — dispatched 2026-07-27 ~00:0x UTC

Requested by the researcher after reviewing the gep1 draft. Response revisions are being handled in a separate thread; this round is new experiments only.

| Thread | Scope | Log | Note |
|---|---|---|---|
| **J1** | Physical-plausibility judge, **v2** | `threads/J1_judge_v2.md` | **v1 = Thread B, which FAILED its reliability checks.** J1 is a redesign, not a fresh start: v1's failure modes are its binding constraints. Key lever — v1's deck-level scalar scoring failed (α 0.21, 3 judges → 3 rankings) while its item-level material-vs-cosmetic classification held (all judges agreed `cosmetic` is modal). v2 decomposes the scalar into forced-choice item judgments aggregated in code. Success criterion **pre-registered before running**; ranking stability across judges is mandatory since that is what killed v1. |
| **J2** | Simulation-output-side evaluation metric | `threads/J2_output_metric.md` | Builds on A2's first pass, does not restart. Must fix A2's weakness: its errors clustered at 0.00 / 10.47 / 99.97%, so a 10% pass/fail threshold "did all the work" — J2 must be **continuous and scale-free**. Headline deliverable is the TreeSim-vs-output-similarity correlation, which is the AC's actual question. Validates on the 3 tasks × 6 cells × 3 seeds already executed. |
| **J3** | Re-run best setting with **`geosx -v`** in the stop hook instead of `xmllint` | `threads/J3_geosx_validation.md` | **Step 0 is a hard feasibility gate:** the hook runs in the agent container; the binary is on the host at `/data/jixuan/…`. If it is not reachable there, stop before spending. Cell = `autocamp_F6` (S+X), held-out, 10 tasks × 3 seeds, everything held constant except the validator. **Cost gate: estimate from the smoketest; stop and report above $60.** |

### Evidence behind J3, computed this session

**49 of 180 held-out task-runs (27%) pass `xmllint --schema` but are rejected by `geosx -v`:**

| Cell | xmllint OK | geosx OK | xmllint OK / **geosx FAIL** | xmllint FAIL / geosx OK |
|---|---:|---:|---:|---:|
| Vanilla | 24 | 19 | **7** | 2 |
| X+M | 30 | 21 | **9** | 0 |
| S+X | 30 | 20 | **10** | 0 |
| S+X+M | 30 | 21 | **9** | 0 |
| SE-prose | 30 | 23 | **7** | 0 |
| SE | 30 | 23 | **7** | 0 |

The asymmetry is stark: `xmllint` **misses 49 real defects and over-flags 2**. Every adapter cell reports a perfect 30/30 while GEOS refuses 7–10 of the same decks — **our stop hook is certifying decks the simulator will not load.** Source: `artifacts/A1_rungs12_perfile.csv` × `artifacts/A1_rung3_corrected_by_taskrun.csv` (`rung3_lenient`).

Motivating context, also confirmed: GEOS's own docs (`data/GEOS/src/coreComponents/fileIO/doc/InputXMLFiles.rst`) recommend exactly the `xmllint --schema` command we used. **We followed the simulator's documented advice and it does not match its loader** — that reframes this from our error to a finding about GEOS's documentation.

### Two other results computed this session (in support of the researcher's questions)

**Convergence is not the bottleneck — loading is.** On the two tasks whose reference deck converges cleanly, **every deck GEOS accepted also ran to completion and converged: 31 of 31** (ThermoPoro 14/14, ViscoExtendedDruckerPrager 17/17). So `geosx -v` at ~2.5 s/deck captures essentially all the execution signal — which is itself the argument for J3.

**Efficiency gains are real and are larger on held-out than val**, consistent with the reliability story (Vanilla thrashes on hard tasks):

| Cell | held-out tools/task | vs Vanilla | held-out wall s/task | vs Vanilla |
|---|---:|---:|---:|---:|
| Vanilla | 90.5 | — | 416.5 | — |
| X+M | 75.0 | −17.1% | 339.5 | −18.5% |
| S+X | 74.7 | −17.5% | 345.1 | −17.2% |
| S+X+M | 82.9 | −8.4% | 358.1 | −14.0% |
| SE-prose | 70.9 | −21.6% | 362.1 | −13.1% |
| SE | 97.4 | **+7.7%** | 389.8 | −6.4% |

⚠ **SE is the one cell that uses *more* tool calls on held-out.** The abstract's "~16% fewer tool calls" is SE-on-**val** (−15.5%) and **reverses on held-out**. If efficiency is emphasised, anchor on the hand-designed cells and on held-out.

**Per-seed mechanism of the two rescue tasks — they are NOT the same effect:**

| task | Vanilla seeds | SE seeds | Δ |
|---|---|---|---:|
| ExampleProppantTest | 0.806, 0.817, **0** | 0.819, 0.829, 0.827 | +0.284 |
| AdvancedExampleThermoPoroElasticWellbore | 0.235, 0.772, **0.058** | 0.815, 0.729, 0.739 | +0.406 |

ProppantTest is a true unscorable-output rescue — Vanilla's two *scored* seeds match SE's — but that zero is the double-hyphen deck GEOS loads fine. ThermoPoro is **graded collapse**, not a zero-score failure. So the defensible framing is **bad-run prevention**, not catastrophic-failure elimination. (Vanilla also *beats* SE on 2 of 10 tasks: PureThermalDiffusion −0.083, IsothermalHystInjection −0.039.)

**On external data files (scope of TreeSim's blind spot):** briefs name the files but not their contents — verbatim, *"`strainFunction`: A table reading time coordinates from `tables/time.geos` and target values from `tables/axialStrain.geos`"* — while giving in-XML parameters explicitly. **4 of 10 held-out tasks reference external data files**, and they are the troublesome ones (ceiling control 3 refs; IsothermalHystInjection 19; singleFracCompression 1 `.vtu`; TutorialHydraulicFracture 22 refs / 35 non-XML files — the task scoring 0.013 in every cell). The researcher's decision: **treat external-file values as provided/out of scope for the benchmark**, keeping TreeSim as a deterministic ground-truth-checked proxy.

---

### F43 · J3 · ⚠⚠ **Thread F's "hook fires on the hard tail" was a different campaign. The corrected finding is stronger.** (07-27 ~01:xx)

J3 reconciled its zero-block control result against F's 32/123. **Both reproduce exactly; they are different campaigns:**

| source | path | events | blocks |
|---|---|---:|---:|
| Thread F | `…/eval/se_icl_2026-04-30/` (`abl_c6_xmllint_hook`, `abl_se_round`) | 123 | **32** (11 parse_error, 21 schema_error) |
| J3 | `…/eval/autocamp_followup_2026-05-02/icl/autocamp_F6/` | 30 | **0** |

F had already flagged this itself: its table is headed "32 block events across **9 cell-seeds**" from `se_icl_2026-04-30`, and its own NOT-FOUND list records that it never located a block instance from a cell named `autocamp_F6/F7/F8/SE`. **F's cell-name mapping was inferred, not confirmed** — and I propagated it into a draft without noticing that caveat.

**The dangerous explanation is ruled out by construction:** J3 did not re-run the control. The numbers are read from the original May-2 campaign's own files; the event log shares an mtime with `status.json`, and the recorded `claude_settings.json` shows the Stop hook registered and live with `xmllint: connected` and 2 validator calls. The hook was installed, enabled, and invoked once per run — it simply had nothing to say. Nothing under `/data/shared` was written.

**Corroboration:** J3's independently re-derived ladder reproduces A1's F6 numbers **row-for-row with 0 disagreements** (r1 = 30, r2 = 30, **r3 = 20**). And it is a logical necessity — rung 2 = 30/30 means an `xmllint --schema` hook *cannot* block; zero is the only possible outcome.

**Corrected headline, and it is better than the version it replaces:** on held-out F6 the stop hook fired **zero times in 30 runs because every deck was already schema-valid, while the simulator refuses 10 of those same 30 decks.** On this split S contributes nothing through its intended mechanism — **the defects were not absent, they were invisible to the validator we chose.**

⚠ **Draft impact, already applied.** `gep1.md` Q2b — a *score-moving* section — claimed the hook "fired 32 times in 123 invocations" on held-out and concluded that "on the hard tail the hook catches what self-validation missed." **Both were wrong.** Rewritten to: the hook never intervenes on either split when X is present (0/410 val, 0/30 held-out), the components are substitutes, and we explicitly state this does **not** establish stop-hook dominance on the hard tail. That converts part of a claimed win into a concession — but it is honest, and it makes the validator-swap the constructive answer. → human decision **H20**.

**Process note:** J3's first ladder run returned r3 = 0/30 for the control — a bug in its own measurement harness (host-side RPATH pulling jixuan's anaconda `libstdc++`), caught only by cross-checking against A1's CSV. A silent all-fail would have looked like a spectacular improvement for the treatment arm. That is now **five** harness bugs this sprint, every one biasing toward our own conclusion, every one caught by a *different* thread's measurement.

**F8 estimate (not launched, as instructed):** control F8 is $0.3975/30 runs, rung 3 = 21/30 — comparable headroom to F6. Treatment ≈ **$0.58** ($1.16 with 2× buffer), ~25 min wall-clock; F6+F8 together ≈ $1.20 and about an hour. J3 will refresh the 1.45× treatment ratio from the completed F6 arm before proposing a launch, since it currently rests on one smoketest run.

### F44 · J3 · Analysis plan pre-registered before the numbers land (07-27 ~02:xx)

Recorded in `threads/J3_geosx_validation.md` **before** the treatment arm completed, so the framing cannot be chosen to fit the result. Committed in `J3_analyze.py`:

1. **Four quadrants per task, printed by name — never a single mean.** rung3↑/TreeSim↑ · **rung3↑/TreeSim↓ (objective mismatch)** · rung3↑/flat · unchanged · rung3↓. `EPS = 0.005` defines flat.
2. **The script itself fires `*** OBJECTIVE MISMATCH CONFIRMED ***`** when rung 3 rises and mean TreeSim falls — detection is not left to the analyst's attention.
3. **Efficiency as a first-class row**, per task, benchmarked against the rebuttal's live −17.5% tools / −17.2% wall-clock claim, with the explicit note that a swap costing more than that erases the efficiency story.
4. **Retry outcomes in four distinct buckets**, because "blocked and repaired" ≠ "blocked, failed, terminated anyway": `clean_first_try` · `blocked_then_repaired` · `BLOCKED_EXHAUSTED_terminated_with_defect` · `blocked_allowed_but_ladder_still_fails`.

**Disclosed asymmetry (sound, and flagged by J3 unprompted):** the *hook* exempts `missing_external_asset` / `unsupported_by_binary` as infrastructure rather than authoring defects — blocking on them would burn the retry budget on something unfixable and could push the agent to delete a correct reference. The *ladder* still counts them as rung-3 failures, to stay comparable with A1. So a run can legitimately show "hook allowed" while "ladder says rung3 = 0" on the two asset-confounded tasks. **J3's rung-3 numbers are therefore the conservative ones.**

**Addition requested:** report the **achievable ceiling**, decomposing the 10 control rung-3 failures into actionable-by-the-hook / exempt-by-construction / surfaced-but-unfixable-in-2-retries. "20/30 → 24/30" reads completely differently if the ceiling was 24 rather than 30 — **+4 of a possible 6 is strong, +4 of a possible 10 is middling** — and a reviewer will ask. Also requested as a secondary view on the 8 non-asset-confounded tasks, keeping all-10 as the conservative headline.

**Interim (seed 1, 2 of 10 tasks blocked):** `TutorialHydraulicFractureWithAdvancedXML` blocked on *"coupled solid constitutive model not found on subregion cb1"* → repaired → allowed (1 of 2 retries). `ExampleIsothermalHystInjection` blocked on *"numberOfMeshBodies == 0"* → repairing. 8 of 10 clean at exit 0. **Efficiency cost already visible:** blocked tasks ran 764 s and 512 s against a control mean of 345 s.

⚠ **The risk under test:** the treatment optimises "GEOS will load this deck"; TreeSim scores "this deck matches the reference." Those are different objectives, and repair turns driven by the first can walk a deck away from the second. Both seed-1 cases are where that could bite — `ExampleIsothermalHystInjection`'s *own* GT deck fails rung 3 (19 external refs), and `TutorialHydraulicFracture` sits at 0.013 in every cell because its reference expands to ~3,333 elements against ~50 generated. **If mean TreeSim falls while rung 3 rises, that is the finding**, not a disappointment.

### F46 · J3 · **Scale correction to F45 — the fabrication is n=1 task-run, and 2 of 3 candidates were legitimate** (07-27 ~04:xx)

J3's differential scan caught a false positive **in its own finding** before shipping it. Raw token totals were `ground truth 3 · control 16 · treatment 28`, which naively reads as "the treatment fabricated 12 more elements." It did not.

**The ground truth itself carries a 1×1×1 dummy `InternalMesh`** on `triaxialDriver_base.xml` — TriaxialDriver drives a constitutive model point-wise and legitimately needs no real mesh — and all three control seeds reproduce it. Counting raw tokens would have excluded 2 perfectly good treatment runs and **manufactured a fabrication finding out of correct behaviour**.

Differential test (token absent from **both** GT and control for that task):

```
LEGITIMATE  s1  AdvancedExampleViscoExtendedDruckerPrager  (in GROUND TRUTH; in CONTROL)
FABRICATED  s1  ExampleIsothermalHystInjection             ['dummy','standalone','trivial_1x1x1_InternalMesh']
LEGITIMATE  s2  AdvancedExampleViscoExtendedDruckerPrager  (in GROUND TRUTH; in CONTROL)
=> 1 validator-induced fabrication task-run
```

Written to `J3_fabrication_affected.json`, which the analyzer reads — so the exclusion is data-driven rather than hand-picked.

**⚠ I overstated F45 to the researcher.** The "6 and 5 dummy occurrences" are two files **within a single task-run** (`ExampleIsothermalHystInjection` s1), not a pattern across the arm. Corrected proportion: **1 fabricated task-run out of the 20 completed so far.**

**The mechanism finding stands; the scale claim does not.** And the cause is J3's **own root-rule bug**, not GEOS validation as such — so this is evidence that a *mis-specified* in-loop validator can induce fabrication, not that in-loop simulator validation does so inherently. Whether a correctly-specified validator avoids it entirely is exactly what the corrected re-run would settle.

**Predicted shape confirmed, and checked rather than assumed:** `ExampleIsothermalHystInjection` is in the exempt-6, so the ceiling stays 24/30 and contamination lands on TreeSim only. The analyzer tests this per-run and prints a warning if a non-exempt task is ever touched. TreeSim reported twice — as-run and excluding contaminated runs, **both arms subset identically to stay paired** — with the output stating that the swap's TreeSim effect may only be read from the corrected row.

**Corrected re-run costed from real data** (20 completed treatment runs): control $0.0134/run, treatment $0.0173/run → **1.29×** (the smoketest's 1.45× over-stated it, resting on a single blocking run). **30 × $0.0134 × 1.29 = $0.52; $1.05 with a 2× buffer; ~25–30 min.** Likely less, since removing spurious blocks removes the repair turns they caused. Corrected rule: keep the lenient include graph, but treat an unreferenced deck whose *only* hard failure is `numberOfMeshBodies == 0` as `orphan_fragment` — skip and record, don't block. **Only delta from the current arm is the root rule**, making it a clean A/B for the fabrication question. **Not launched** (→ **H21**).

### F45 · J3 · ⚠⚠ **An in-loop simulator validator induced the agent to fabricate physics** (07-27 ~03:xx) — *see F46 for the corrected scale (n=1 task-run)*

The most consequential result of the overnight round, and it **tempers the recommendation we were about to make in the rebuttal**.

**My hypothesis was refuted cleanly.** I suspected `numberOfMeshBodies == 0` was a downstream symptom of an unstaged asset, i.e. the exemption leaking. J3 tested it in three steps on the control's uncorrupted copy — assets as-staged → all 17 real `tables/` + 6 `fc_tables/` added → remaining unresolvable paths stubbed — and `numberOfMeshBodies == 0` **survives full asset staging**. The exemption never leaked.

**The real mechanism — orphan-fragment-as-root, a harness defect.** `class09_pb3_drainageOnly_iterative_base.xml` has zero `<Mesh>` blocks and **nothing `<Included>`s it**; its own header says *"Intended to be `<Included>` by a mesh-specific benchmark file."* J3's root rule is "root = not referenced by anything", which is precisely wrong for an **orphan** fragment — validating it standalone can only ever fail. In the control the missing-asset error fired first and **masked** the structural one; in the treatment the agent authored resolvable CSVs, the mask vanished, and the next error surfaced.

**What the agent then did.** Its only way to satisfy "this fragment has no mesh" was to invent one:

| file | control `dummy` occurrences | treatment |
|---|---:|---:|
| `class09_pb3_drainageOnly_iterative_base.xml` | 0 | **6** |
| `class09_pb3_hystRelperm_iterative_base.xml` | 0 | **5** |

A fabricated `standaloneDummyMesh` (1×1×1 `InternalMesh`, `dummyBlock`) and a `dummyWell`, injected into **both** base files — including `_hystRelperm_`, which is legitimately included and never needed one.

**This is the objective-mismatch risk arriving in the wild**, via our harness rather than via GEOS. Hand a capable agent an unsatisfiable validation demand and it will satisfy it by inventing the missing physics.

**Lesson, in J3's formulation: *unreferenced is not the same as root*.** An in-loop simulator validator must distinguish a standalone problem from an orphan fragment. Recorded negative detail: "no `<Mesh>` block" does **not** work as the discriminator — `triaxialDriver_ViscoExtendedDruckerPrager.xml` has none and passes all three control seeds.

**Consequences, all wired into `J3_analyze.py` so they cannot be forgotten:** blocks matching `numberOfMeshBodies == 0` tagged `SPURIOUS_BLOCK_ONLY_harness_defect`; genuine vs spurious block counts reported separately; budget-binding measured on **genuine** blocks only; efficiency reported **as-run and excluding spurious-touched runs**. I have additionally required the **TreeSim comparison to be reported twice** — all-10 as-run and excluding spurious-touched runs — since fabricated elements are penalised by TreeSim's β term and would otherwise show up as a validator-swap regression that is really a harness artifact.

Expected shape: the affected task (`ExampleIsothermalHystInjection`) sits in the **exempt-6**, so it cannot move the rung-3 ceiling; contamination should hit the TreeSim comparison while leaving the rung-3 headline intact. To be confirmed, not assumed.

**Not patched mid-campaign** — correct, that would break hold-everything-constant. A corrected re-run (~$0.58) is being costed and will be **proposed, not launched**. It answers a question the current arm cannot: was the fabrication caused by the bad root rule, or does in-loop simulator validation induce fabrication more generally? → human decision **H21**.

**Rebuttal impact:** we were preparing to recommend replacing the in-loop `xmllint` gate with `geosx --validate-input`. That recommendation should now be made **with this failure mode attached** — proposing it naively would be proposing something we have evidence can backfire.

### F49 · J2 · ⚠⚠⚠ **THE VIVID ONE: the worst-scoring deck in the study produces a physically indistinguishable simulation** (07-27 ~09:xx)

`ExampleProppantTest` **`F0_s3`** — the Vanilla deck with the illegal `--` XML comment:

| property | value |
|---|---|
| TreeSim | **0.000** — the lowest structural score in the entire study |
| our scorer | unparseable; this single run causes Vanilla's held-out σ = 0.081 |
| the "≈40× variance reduction" claim | rests on this one run |
| `geosx -v` | **exit 0 — loads fine** |
| runs to completion | **yes** |
| **simulation output fidelity vs reference** | **SOF = 1.0000 — indistinguishable** |

**A deck our metric scores 0.000 produces the reference simulation exactly.** Its only defect is a prose double hyphen inside an XML comment.

This is the single most quotable illustration of the structural/physical gap in the whole sprint, and it lands squarely on our own flagship number. It converges with everything else already established about this run (F13, F41): the paper's headline catastrophic failure is **a metric artifact end to end** — parseable by the simulator, runs to completion, and physically correct.

It also strengthens the "**portability defect, not execution failure**" reframe already in `gep1.md`: we can now say the deck not only loads but reproduces the reference physics.

Found only because J2 caught that **A2's published artifacts are stale by 2 of 38 records** — `A2_grid_qoi.jsonl` and `A2_qoi_per_run.csv` predate `A2_scratch/qoi_v2.jsonl`. ProppantTest `F0_s3` and `SE_s2` are published as QoI failures but **succeeded**, verified on disk. Both corrections run *against* A2's failure counts. → **H23: A2's published CSVs must be corrected before anything is quoted from them.**

### F48 · J2 · ⚠⚠ **CORRECTION to F47 — doubling the tasks reversed the decomposition** (07-27 ~09:xx)

**F47 (3 tasks) is superseded.** It was *underpowered, not wrong*: min detectable |ρ| was 0.38 against an estimate of 0.29. At 6 tasks × 6 cells × 3 seeds = **108 runs, 91 with output**:

| scope | n | ρ | p | 95% CI |
|---|---:|---:|---:|---|
| **Pooled (within-task ranks), `SOF_all`** | **108** | **0.402** | **<1e-4** | **[0.23, 0.55]** |
| Meta-analysis (Fisher-z over 6 tasks) | 108 | 0.411 | 1e-4 | [0.22, 0.57] |
| Pooled, conditional on running | 91 | 0.450 | <1e-4 | [0.26, 0.61] |
| Meta-analysis, conditional on running | 91 | **0.504** | <1e-4 | [0.31, 0.66] |
| **TreeSim vs runnability (0/1)** | 108 | **0.150** | **0.119** | [−0.02, 0.32] |

**⚠ I reported the opposite decomposition to the researcher and must correct it.** I said TreeSim was "a weak proxy for *runnability* and close to uninformative about *fidelity*." The 6-task data says the reverse: it **is** a fidelity signal (ρ 0.40–0.50, and the correlation *strengthens* conditional on running), and it is **not** a runnability signal (ρ = 0.150, non-significant).

**ρ² ≈ 0.17–0.25** — TreeSim explains roughly a sixth to a quarter of the rank variance in simulation fidelity, leaving three quarters unexplained. **Per-task ρ spans 0.11 → 0.83**, with 2 of 6 tasks at ~0.11 (p ≈ 0.66) and I² = 42%. **Never quote the pooled number without the range.** Robustness: jackknife [0.387, 0.427]; holds dropping TreeSim = 0 points (0.433) and within SIGA cells only (0.425).

**Cell separation: still none, and the point estimate now favours Vanilla.** Pooled Kruskal–Wallis p = 0.468. SIGA (n = 90, 0.8054) vs Vanilla (n = 18, **0.8140**): **Δ = −0.0086**, Mann–Whitney p = 0.292. Every within-cell sd (0.25–0.45) dwarfs every between-cell difference. Third independent corroboration of Thread B and Thread D.

**J2's framing of the split is the right one and should be reused verbatim:**
> *Does structure track simulation?* → partly (ρ ≈ 0.41). *Do SIGA's structural gains produce better simulations?* → **not detectably.**

**⚠ Largest analytic sensitivity in the study, and it must be disclosed:** 11 of 13 sensitivity arms give ρ ∈ 0.28–0.40, all p ≤ 0.004 — but **replacing mean-over-reductions with the worst reduction drops ρ to 0.148, p = 0.127, non-significant.** A reader preferring the worst-case aggregator should read "no significant association." Interpolation does *not* drive anything (interpolated relative-L2 agrees with SOF at ρ = 0.91–0.95).

**Power:** at n = 108 the min detectable |ρ| is ≈0.27. Resolving ρ = 0.2 or modelling the heterogeneity needs **n ≈ 206 (~12 tasks)**. The SIGA-vs-Vanilla cell contrast would need **n ≈ 26,000 per arm** at the observed effect size — i.e. that contrast is not merely unproven, it is unprovable at any realistic scale.

**Also found:** `ExampleIsothermalHystInjection`'s **ground truth cannot run** — its top deck `<Included>`s `class09_pb3_hystRelperm_direct_base.xml`, which **does not exist anywhere in the GT tree**. A broken reference in our own benchmark (→ **H24**). And **four metric bugs J2 found and fixed in its own work**, including a reference/generated canonicalisation asymmetry that changed **17 of 108 scores**, caught only via the per-quantity breakdown.

### F47 · J2 · ~~Measured answer to the AC's question~~ — **SUPERSEDED by F48** (3-task result, underpowered) (07-27 ~08:xx)

Spearman ρ against the new simulation-output-fidelity metric (SOF), 20,000-permutation p, 10,000-sample percentile bootstrap CI, over 54 runs on 3 executed tasks:

| scope | n | ρ | p | 95% CI |
|---|---:|---:|---:|---|
| ThermoPoro | 18 | 0.110 | 0.662 | [−0.41, 0.59] |
| DruckerPrager | 18 | 0.109 | 0.660 | [−0.46, 0.59] |
| ProppantTest | 18 | **0.609** | **0.008** | [0.18, 0.90] |
| **POOLED (within-task ranks)** | **54** | **0.292** | **0.034** | **[0.01, 0.53]** |
| POOLED, conditioned on the deck running | 45 | 0.223 | 0.141 | [−0.09, 0.49] |
| POOLED: TreeSim vs binary "produced output" | 54 | 0.239 | 0.082 | [0.01, 0.45] |

**TreeSim explains ≈9% of the rank variance in output fidelity (ρ² ≈ 0.085).** Two of the three tasks show *no* association at all. The pooled association is carried by a single task and by the **runnability** component — TreeSim vs the binary "produced output" is ρ = 0.24, essentially the same size as the fidelity correlation — and it **disappears once you condition on the deck actually running**.

**So a structural similarity score on the input deck is a weak proxy for runnability and close to uninformative about fidelity.** This is the AC's primary question, measured rather than argued, and the answer does not favour us.

**Corroboration of the reliability-first framing, by a third independent route.** Per-cell SOF shows **no separation**: Kruskal–Wallis pooled p = 0.550 (per-task 0.945 / 0.888 / 0.241); SIGA cells (n = 45, mean 0.791) vs Vanilla (n = 9, 0.745) Δ = **+0.046**, Mann–Whitney **p = 0.653**. Every cell's sd exceeds every between-cell difference. Same conclusion as Thread B's clean-subset null and Thread D's bootstrap, reached by a completely different instrument.

**The metric passes its own sanity check.** Known-good vs known-bad separate by +0.219 under the declared primary and +0.433 under the worst-reduction variant; the two byte-identical-tables runs score exactly **1.0000**.

**Methodological discipline worth recording:** J2 reported a weakness in its *own* declared primary — averaging over four reductions dilutes a catastrophic failure (`F8_s1` ThermoPoro is 99.97% wrong on peak pressure yet scores Ψ = 0.646, because the reference pressure field is a sharp near-wellbore spike whose mean is only 10% of its max; the worst-reduction variant gives 0.0003). **It kept the declared primary anyway**, on the grounds that swapping after seeing which separates better is exactly the tuning the metric exists to avoid. Both are reported for every run, and the headline is invariant to the choice.

**Power caveat, stated by J2 itself:** 3 tasks and 54 runs is too small for a stable answer; it is extending to 6 tasks with the reference gate applied first, plus Fisher-z pooling with heterogeneity. → human decision **H22**: whether to volunteer ρ ≈ 0.29 to reviewers. My lean is **yes, with the power caveat and the CI** — the AC made this the decision criterion, we are already conceding we cannot claim physical validity, and a measured concession with an interval is stronger than a vague one. But the decision should wait for the 6-task extension.

Also flagged by J2 and to be folded in: a **data-integrity finding about A2's published artifacts** (§4b of its log) and **three metric bugs**, one an order-dependent canonicalisation caught only by the task extension.

### F50 · J1 · **soft-TreeSim FAILS its pre-registered bar — but a 3-line deterministic fix beats the $12.70 four-judge panel** (07-27 ~10:xx)

Rubric frozen at `J1_rubric_v4.md`, sha256 `5ee738e0…`, hash verified unchanged post-run; **criterion thresholds fixed at 07:56Z, before any judge call of any kind.** Verdict: `VALID = false`, `USEFUL = true`, **`SHIPPABLE = false`**.

| # | Criterion | Bar | Measured | | v1 |
|---|---|---|---|:--:|---|
| C1 | Krippendorff α (gate / 4-level) | ≥0.667 / ≥0.40 | **0.391 / 0.288** | FAIL | 0.257 / 0.214 |
| C2 | pooled mean \|order B − A\| | ≤0.0232 | **0.0264** | FAIL | 0.0552 |
| C3 | all judges same order, Vanilla last | both | **2 orderings**; Vanilla last **4/4** | FAIL | 3 orderings, Vanilla *not* last |
| C4 | judge-choice ÷ cell-effect range | ≤1.0 | **1.81** (centred 1.16) | FAIL | 4.76 |
| U1 | beats TreeSim at predicting rung 3 | both stats, CI excl. 0 | **yes** | **PASS** | no |

**Two independently designed judge metrics have now failed their own pre-registered reliability tests on this task.** J1 did **not** re-tune and re-run — correct discipline.

**Implementation validated:** soft-TreeSim reproduces all 89 published TreeSim scores **bit-exact** (`ok=89 mismatch=0 worst=0.00e+00`) when the LLM layer is disabled. So the delta is attributable to the judge, as designed.

**C1's failure is a prevalence artifact, and this matters for how we report it.** Raw exact agreement is **70.3% (4-level) / 73.3% (gate)**, up from v1's 41.5%. But 74–94% of verdicts are `equivalent`, so α collapses — the kappa paradox. **Gwet's AC1 = 0.811.** The honest summary is *chance-corrected reliability cannot be established on this label distribution*, **not** *the judges disagree*. Three of four judges agree pairwise at 86–92%; `gpt-5.4-mini` is the outlier (18.1% `material_deviation` vs 1.0–4.7% for the others). Report **both** α and AC1 with the explanation — → **H25**.

**C3 was probably an impossible bar for two of the three cells:** the F6−SE ensemble gap is **0.0001** against seed sds ~0.009. No metric can order those. Vanilla-last held 4/4. Do not retroactively relax the pre-registration — report it as failed with this context.

**Score table** (held-out, 10 tasks × 3 seeds):

| Cell | TreeSim | soft-TreeSim |
|---|---:|---:|
| Vanilla | 0.7196 ± 0.0661 | 0.7246 ± 0.0629 |
| S+X | 0.7814 ± 0.0015 | 0.8043 ± 0.0097 |
| SE | 0.7891 ± 0.0101 | 0.8042 ± 0.0086 |

Contrary to my prediction, softening **slightly widens** the gap (SIGA +0.015/+0.023 vs Vanilla +0.005) — TreeSim was penalising SIGA's harmless variation marginally *more*. ⚠ **But it does not reproduce the σ-collapse**: S+X sd goes 0.0015 → 0.0097. The judge *adds* seed variance, so the variance-reduction claim does not survive under soft-TreeSim.

**U1, the one PASS:** soft-TreeSim beats TreeSim at predicting whether a deck loads — r_pb 0.394 → **0.476**, AUC 0.803 → **0.848**; paired bootstrap ΔAUC **+0.045 [+0.007, +0.087]**, Δr_pb **+0.082 [+0.041, +0.132]**, both excluding zero. v1 could not do this. But no gain at rung 4 (AUC 0.712 → 0.697).

⚠ **Apparent conflict with J2, probably resolved by J2's own correction:** J1 reports *neither* metric predicts QoI error (|Spearman| < 0.04, **n = 20**), while J2 finds TreeSim–SOF ρ = 0.402 (**n = 108**, 6 tasks). J1's QoI numbers come from **A2's published CSVs, which J2 proved stale by 2 of 38 records** (F49). J1's n=20 is also badly underpowered. Treat **J2's n=108 as authoritative**; flag for reconciliation.

**The genuinely shippable deliverable — a per-section audit of TreeSim.** Judge more lenient on `Outputs` **+0.100**, `Events` +0.101, `ElementRegions` +0.069, `Tasks` +0.056; harsher on `Solvers` **−0.050**, `Constitutive` −0.031, `FieldSpecifications` −0.016. And `Outputs` correlates with TreeSim at r = 0.098 while `Constitutive` reaches r = 0.751. **This claim does not require the judge to be a reliable cell discriminator** — it audits the metric, not the systems. → **H26: ship this table without the cell score table.**

**Blind spot 1 — a strong zero-LLM argument.** 10 decks fail rung 3 as `missing_external_asset` (largest class, 22/53). **0 of 10 load — yet TreeSim scores them 0.840, above the 0.763 held-out mean** (soft-TreeSim 0.787). That is the cleanest available demonstration that an input-side metric cannot answer the execution objection, and it needs no LLM at all. → **H27: ship.**

**Blind spot 2 — and this is the sprint's most deflating result for the LLM-judge direction.** 79.4% of units (5237/6597, 49 of 89 decks) have **no candidate counterpart**, and soft-TreeSim gives no improvement there (0.633 vs 0.627) because matching stays hard by design. The value-level arm shows a **deterministic 3-line fix to `_bipartite_match`, no model at all**, lifts that subgroup 0.661 → 0.727 and rung-3 AUC 0.803 → **0.830** — **more than the entire four-judge LLM panel delivers, for free.** That is the honest headline of the judge work: *the cheap deterministic fix beats the expensive semantic one.* → ties to **H16/H28** (the annihilation fix; Thread B advised disclose-not-fix since re-scoring moves every paper number).

**Determinism:** 5.2% verdict flip rate at temperature 0. TreeSim is reproducible; soft-TreeSim is not — so it can only ever be a complement, never a replacement.

**Cost $12.70** against the $40 gate (sections $10.71 / 9,056 calls / 21 failures; value-level arm $1.54; smoketests $0.31). `tencent/hy3` emitted **2.68 M completion tokens, 21× the other judges** — it is a reasoning model, worth knowing for future budgeting; 61 calls returned empty at a 3,600-token cap and all recovered at 8,000, evenly spread across cells.

### F51 · J3 · **FINAL: the validator swap captures 100% of the rung-3 headroom — but only half is attributable, and it erases the efficiency story** (07-27 ~10:xx)

| | control (xmllint) | treatment (`geosx -v`) | delta |
|---|---|---|---|
| **rung 3** | 20/30 | **24/30** | **+4 = 100% of the 24/30 ceiling** |
| rung 2 | 30/30 | 30/30 | 0 |
| TreeSim as-run | 0.7814 (σ **0.0018**) | 0.7861 (σ **0.0240**) | +0.0047 |
| TreeSim excl. contaminated | 0.7830 | 0.7899 | +0.0070 |
| hook blocks | **0** | 6 (3 genuine, 3 spurious) | +6 |
| **tools/task** | 74.7 | **115.7** | **+54.9%** |
| sec/task | 345.1 | 330.7 | −4.2% (n.s.) |

Quadrants: Q1 1 task · **Q2 1** · Q3 1 · Q4 7 · Q5 0. Cost estimated $0.58, actual **$0.6255** including smoketest — **1.0% of the $60 gate**.

**⚠ Attribution: only +2 of the +4 is the hook's.** Two of the four flips occurred on runs the hook **never blocked** — unpaired replicate variance. **The defensible claim is +2 of a possible 4.** Sharpening this: the single largest TreeSim move in the whole experiment (−0.071) is on a **zero-block** task, which measures how little of any TreeSim delta here is signal rather than noise.

**⚠⚠ The swap ERASES the efficiency story, and this directly conflicts with the framing the researcher asked for.** 115.7 tools/task is **+27.8% above Vanilla's 90.5**, against the **−17.5%** we were preparing to claim for F6. Robust: the lowest treatment seed (104.4) exceeds the highest control seed (76.9). The xmllint-MCP confound is ruled out (connected in all 60 runs). **We cannot claim both the efficiency gain and the validator swap from the same configuration** — see the brief for how to phrase the trade.

**Also: across-seed σ rises 13×** (0.0018 → 0.0240). S+X's near-zero seed variance is one of the paper's headline reliability numbers, and the swap destroys it.

**✅ The clean, quotable result — Q3.** `TutorialHydraulicFractureWithAdvancedXML` went **1/3 → 3/3 loading** via 3 genuine blocks **while TreeSim stayed pinned at 0.013**. **Loadability and structural similarity are orthogonal, demonstrated rather than argued.** This is the single best illustration of the input-metric gap the sprint has produced, and it needs no LLM and no QoI machinery.

**Retry budget NOT binding — J3 withdrew its own interim claim.** 25/30 clean, 3 blocked-then-repaired, 2 spurious-only, **0/30 exhausted the budget on genuine blocks.** The earlier "the budget IS binding" reading rested on a spurious block.

**Smoketest evidence the mechanism is real:** the agent's own repair was *"`rockThermalCond` needed to be included in the `CellElementRegion`'s `materialList`"* — a cross-reference fix `xmllint` structurally cannot see. And 0 `geosx` mentions in `tool_calls.json`, so the signal arrived through the hook rather than the agent invoking GEOS itself.

**Engineering notes worth keeping.** Feasibility required a **388 MB self-contained bundle** (binary + 102 libs) because the eval container mounts only four paths, none of them `/data/jixuan` — and it must **exclude all of OpenMPI**, since bundling the host's 4.1.6→4.1.2 mismatch breaks `MPI_Init`. GEOS writes validation errors to **stdout, not stderr**. The hook change is **+286 lines, 0 deletions**, so the xmllint path remains byte-identical and reproducible. And J3 found a **latent bug**: the Stop-hook timeout was 30 s, raised to 240 s — harmless with fast `xmllint` but it would have silently dropped blocks on slow decks under any heavier validator.

J3's decision items 2 and 3 (corrected root rule; F8 as a second cell) were **already authorised and are running as Thread K4 Arms A and B**.

### F52 · K2 + main · 🛑🛑🛑 **STOP — the val scoring pass raced the val campaign. DO NOT VOLUNTEER THE MAIN-EFFECTS CORRECTION.** (07-27 ~11:xx)

**This supersedes my Phase 0 finding F1 and reverses decision H3.** I verified it myself rather than taking K2's word for it.

`_summary.json` for `autocamp_F3_s1` finished scoring at **14:25:28**. The candidate decks it was supposed to score were written *afterwards*:

```
_summary.json (scoring done)                       14:25:28
TutorialSneddon/Sneddon_base.xml                   14:30:01   <- 4.5 min LATER
TutorialSneddon/…hydroFrac_benchmark.xml           14:32:37   <- 7 min later (7 files total)
TutorialPoroelasticity/…_smoke.xml                 14:25:41
TutorialPoroelasticity/…_benchmark.xml             14:25:51
ExampleIsothermalLeakyWell/…_benchmark.xml         14:25:51
```

Published verdicts for those three tasks: `TutorialSneddon` **treesim=None, status='error'** · `TutorialPoroelasticity` **0.2371** · `ExampleIsothermalLeakyWell` **0.7032**.

**`TutorialSneddon` did not fail. The scorer looked before the agent had written anything.** The other two were scored on partial decks — `TutorialPoroelasticity`'s 0.2371 came from `base_direct.xml` alone, without the smoke or benchmark files.

**The defensible framing, which does not require proving the mechanism:** whatever the cause, **the published val numbers cannot be reproduced from the decks now on disk.** Root cause per K2: `batch_evaluate.py:203` timestamps `_summary.json` after scoring, so the ordering is unambiguous. K2's systematic mtime audit over 73 run-cells found one further case — `F11_s2_pknViscosityDominated`, published as a hard failure, actually scores **0.9795**.

**Consequences, in order of severity:**

1. **🛑 H3 flips to DO NOT VOLUNTEER.** Both the published effects (−0.032/−0.003/+0.007/+0.004) and the "corrected" ones I verified in Phase 0 (−0.037/−0.008/+0.011/+0.008) rest on raced scores. De-raced: **R −0.0313 · S −0.0002 · X +0.0054 · M +0.0023.** Publishing our planned correction would mean **publishing a correction that is itself wrong** — precisely the unrecoverable move the sprint brief warned against. The evidence for the correction was sound; its *input* was not.

2. **F3 (R+S) is ≈0.887 ± 0.011, not 0.857 ± 0.045.** My Phase 0 conclusion — that 0.857 is correct under failures-as-zero and 0.874 is the drop-nulls artifact — **described the right convention applied to raced data.** The convention analysis stands; the number does not.

3. **⚡ The paper's §5.1 sentence turns out to be TRUE on clean data.** *"X, M and S all fall within ±0.007"* — de-raced, S = −0.0002, X = +0.0054, M = +0.0023, **all inside ±0.007**. So H9, which required rewriting that sentence because the correction falsified it, dissolves: **the correction would have broken a correct sentence.** R remains largest and negative, so the paper's val conclusion survives and gets *cleaner*.

4. **✅ Held-out is UNAFFECTED — this is the crucial containment.** K2's verification: `published == strict` on **all 180** held-out runs, worst absolute difference **0.00e+00**, cross-checked against J1's independently written scorer. So **every headline claim in the drafts is safe**: the +0.069 Vanilla→SE contrast, the per-cell σ table, the reliability story, and all the execution work. Only **val** is contaminated, and only the appendix main-effects table depends on val.

**Actions taken:** `PROVENANCE.md` rows 1/1b/1c re-marked; `threads/P0_verification.md` marked superseded; the revision brief's H3 recommendation flipped. No draft text needs changing, because **no current draft quotes a val main effect** — the correction lived only in a `[[BLOCKED]]` slot awaiting H3, which is now answered: cut it.

**This is harness bug #6, and the sixth consecutive one biasing toward a wrong conclusion of ours.** Every one was caught by a *different* thread's independent measurement — never by the thread that produced the number.

### F1 · P0 · ~~F3 resolved: 0.857 is correct~~ — **SUPERSEDED by F52.** The convention analysis stands; the underlying score was raced.

### F53 · K1 · 🛑🛑 **The aggregate rung-3 claim does not survive the staging fix. Vanilla ties X+M.** (07-27 ~11:xx)

K1 reproduced A1 exactly first (**0/180 disagreements**, same taxonomy imported rather than re-implemented), then staged the missing non-XML assets and re-measured. `missing_external_asset` went **32 → 0**.

| cell | A1 (confounded) | **K1 (staged, clean)** |
|---|---|---|
| Vanilla | 19/30 | **21/30** |
| X+M | 21/30 | **21/30** |
| S+X | 20/30 | **23/30** |
| S+X+M | 21/30 | **24/30** |
| SE-prose | 23/30 | **23/30** |
| SE | 23/30 | **24/30** |

**New ceiling 30/30** (27/30 with assets staged; 30/30 once the GT's own dangling XML include is staged, after which GT passes all 10 tasks). **Both of A1's exclusions become unnecessary — the honest denominator is all 10 tasks, n = 30.**

**The direction does NOT survive:**
- **Vanilla is no longer strictly lowest — it ties X+M at 21/30, Fisher p = 1.0000 exactly.**
- Gap 8.7 pp → 6.7 pp; pooled Fisher 0.3822 → **0.4865**; per-cell p **0.55–1.00**.
- Task-stratified exact permutation (respecting the task/seed clustering A1 flagged): 0.1734 → **0.3109**.
- **The statistic nobody had computed — per-task sign test: Vanilla worse on 4/10 tasks, BETTER on 3/10, tied on 3/10, p = 1.0000.** Same counts before staging, so this is not caused by the fix — but it is the honest summary of a 6.7 pp gap on 10 clustered tasks, and **a reviewer will read it straight off the per-task table.**

**Two survivors, and they are what the claim should rest on:**
1. **Rung 2 is untouched** — 24/30 vs 30/30, p = 0.0237. The clean rung-3 null actually **sharpens** the rung-2-vs-rung-3 contrast.
2. **`bad_attribute_value` failures: 6 for Vanilla vs 0–1 per adapter cell.** Narrow, mechanism-matched, and it holds.

**⚠ NEW DEFECT CLASS — 26% of provided assets contain fabricated numbers.** Content-hashing all 240 staged assets: 178 authentic, **58 authentic-name-with-fabricated-content, 4 fabricated name+content = 26% fabricated**, present in **all six cells** (F6 15, F11 13 worst). **No rung can see this, and SIGA does not reduce it.** This bears directly on the researcher's scope decision that external-file values are "provided" — empirically, the agents are authoring 26% of them and getting them wrong. → **H29.** Also 21 refs in F0/s1 are absolute `/geos_lib/...` container paths — a genuine portability defect staging cannot fix.

**Corrections to three other threads:**
- **J3's `tables/elevation.txt` claim is wrong twice** — it *does* exist in the GEOS repo, and F6/s1 *wrote* it, so it was never a dangling reference.
- **J2's "`ExampleIsothermalHystInjection` GT cannot run" is two stacked harvest bugs.** Staged, **GT passes 1/1**. The 18 cell-seeds still fail on real defects. So H24 softens: the GT is recoverable, our harvest was broken.
- **A1's "exactly 2 symlinks in the whole dataset" is wrong** — F6/s2 and F8/s2 each ship ~21 dangling per-file symlinks plus a literal unexpanded `*`.

**⚠⚠ Val is worse and asymmetric.** 103/561 task-runs (18.4%) affected, and **it tracks cell identity: F11 0/51 and SE 0/51 vs F3 16/51, F5 15/51 — the two cleanest cells are the two SE cells.** And **A1's premise fails on val: only 34/51 (task, seed) groups have identical asset sets across the 11 cells**, so on val the missing assets differ *by condition*. That is a fairness bug favouring SE, not just noise. Combined with F52's scoring race, **val is contaminated on both axes.** Warned K3.

Fairness invariant **proven, not assumed**: `K1_build_pools.py` dry-stages 10 tasks × 19 environments and exits non-zero on violation. No API spend; `/data/shared` and `/data/jixuan` verified unwritten.

**Draft impact, already applied.** `gep1.md`, `AC.md` and `gep1_post2.md` claimed "the baseline is lowest at every denominator" with 19/30 vs 21–23/30. **That is now false.** All three rewritten to the staged numbers, stating that we do **not** claim a loading advantage and giving the sign test. All six texts remain under cap. → **H30: rebuild the rung-3 story on rung 2 + the `bad_attribute_value` decomposition (K1's recommendation and mine), or report rung 3 with the sign test up front.**

### F54 · K3 · **n = 489 across 18 tasks. ρ comes DOWN with power — and on the clean split the aggregator decides significance.** (07-27 ~11:3x)

*K3 was killed three times by transient platform 529s. Its statistics completed and are on disk; I read them directly from `artifacts/K3_validation_report.txt` rather than waiting on another resume. Its formal write-up may add meta-analysis and jackknife; these numbers are from its own validated output.*

**Primary (SOF = mean over reductions, within-task ranks):**

| scope | n | ρ | 95% CI |
|---|---:|---:|---|
| **held-out (clean on both axes — PRIMARY)** | 126 | **0.362** | [0.197, 0.505] |
| val (staged + re-scored, secondary) | 363 | 0.283 | [0.181, 0.379] |
| **POOLED** | **489** | **0.310** | **[0.227, 0.391]** |

**⚠ The estimate falls with power: J2's 0.402 at n = 108 → 0.310 at n = 489.** That is exactly what scaling up was for — J2's figure was inflated by small-sample noise. It remains clearly non-zero. Per-task heterogeneity is large and must always accompany the pooled figure: held-out spans **0.109 → 0.735**, val spans **−0.118 → 0.706**.

**⚠⚠ The aggregator sensitivity is now decisive, and it lands on the clean split.** Under the worst-reduction aggregator:

| scope | n | ρ | p |
|---|---:|---:|---:|
| **held-out** | 126 | **0.121** | **0.176 — NOT SIGNIFICANT** |
| val | 363 | 0.303 | <0.001 |
| POOLED | 489 | 0.261 | <0.001 |

**On the only split clean on both axes, whether TreeSim predicts simulation fidelity depends entirely on which summary statistic you choose.** J2 flagged this as its largest analytic sensitivity; at proper power it is no longer a footnote. **Any use of ρ must report both aggregators.** → **H31.**

**✅ Power target cleared:** pooled n = 489 gives min detectable |ρ| = **0.130**; val alone 0.151. Held-out alone (n = 126) is 0.254 and does *not* clear ρ = 0.2 — so the pooled figure is the powered one, and held-out remains the clean one. That tension should be stated, not resolved by picking the flattering split.

**⚡ The most useful new result — conditional on running, the physics is usually right.**

| | mean | frac ≥ 0.999 | frac = 0 |
|---|---:|---:|---:|
| held-out SOF (all) | 0.692 | 33.3% | 27.8% |
| **held-out SOF \| ran** | **0.958** | **46.2%** | 0% |
| val SOF (all) | 0.810 | 58.1% | 11.6% |
| **val SOF \| ran** | **0.913** | **65.5%** | 0.3% |

**The physics gap is concentrated in decks that fail to run, not in decks that run wrong.** Conditional on producing output, roughly half of all runs reproduce the reference to ≥0.999. This is a **strong, independent argument for the reliability-first framing**: what matters is whether a deck runs at all, and that is precisely the axis the paper's reliability claim is about. → recommend using this prominently.

**Cell separation: NOT DETECTABLE on any split** — and the held-out point estimate favours Vanilla.

| split | SIGA | Vanilla | Δ | MW p | n/arm for 80% power |
|---|---:|---:|---:|---:|---:|
| held-out | 0.6904 | 0.6977 | **−0.0073** | 0.409 | **56,162** |
| val | 0.8124 | 0.7843 | +0.0281 | 0.767 | 2,358 |
| pooled | 0.7829 | 0.7506 | +0.0323 | 0.902 | 2,101 |

Fourth independent corroboration (B, D, J2, now K3 at 4.5× the n). **Always "not detectable", never "no difference."**

⚠ One caution I am flagging rather than K3: the val per-cell means put **SE (0.910) and F11 (0.918) far above F0 (0.784)** — and those are exactly the two cells K1 found had **zero** unstaged-asset failures on val (F11 0/51, SE 0/51) while F3 had 16/51. K3 applied K1's staging and re-proved the fairness invariant across 34 environments per task, so this *should* be resolved — but the residual pattern matches the confound too closely to accept without a check. **Do not quote val per-cell SOF means until someone verifies this is not a staging remnant.** → **H32.**

### F55 · K4 · **Arm C: a single simulator-grounded hook matches the full adapter — but the attributable effect is +1 run, three times over** (07-27 ~12:xx)

Three arms, $1.7371 of the $10 cap, 91/91 runs succeeded, zero null TreeSim.

**✅ Arm A — the corrected root rule ELIMINATES the fabrication. H21 answered.** 1 → **0** validator-induced fabrications; spurious blocks 3 → **0**; the orphan rule fired 9× and redirected validation to the real root. Arms B and C also 0. So **"unreferenced ≠ root" is a correct and *sufficient* fix — in-loop simulator validation does NOT induce fabrication in general.** K4 unit-tested the rule three ways against the real binary first, including J3's recorded non-discriminator. **The cautionary finding stands as a lesson about implementation, not about the approach.**

**⚠ Arm B — J3's sigma claim does not generalise, and I reported it to the researcher.** On F8 sigma **fell 3.5×**; on Vanilla **4.5×**. F6's control sigma (0.0018) is the anomaly. Correct statement: **the hook pulls sigma toward ~0.006–0.018 either way — it makes outcomes *more* uniform.** K4's own note: *"I'd have shipped J3's claim as general had I run only one cell."* My earlier report that "the swap destroys S+X's near-zero seed variance" is **withdrawn**.

**✅ Arm C — the novel result. One hook, no other adapter, delivers everything:**

| | Vanilla | S+X (full adapter) | **hook only** |
|---|---:|---:|---:|
| TreeSim | 0.7196 | 0.7814 | **0.7839** |
| rung 1 / rung 2 | 24/30 | 30/30 | **30/30** |
| rung 3 (staged) | 21/30 | 23/30 | **26/30 — above every published cell** |
| tools vs Vanilla | — | −17.5% | **+8.0%** |
| wall-clock vs Vanilla | — | −17.2% | **−24.4%** |

The cell is F6 minus one line, **proven prompt-identical to Vanilla by sha256**. So a single simulator-grounded stop hook matches the full hand-designed adapter on TreeSim and beats every published cell at loading, at a quarter less wall-clock.

**🛑 The negative that outranks all three.** On K1's clean staged ladder (ceiling 30/30):

| arm | control | treatment | raw | **attributable** |
|---|---:|---:|---:|---:|
| A · F6 | 23/30 | 27/30 | +4 (57%) | **+1 (14%)** |
| B · F8 | 24/30 | 25/30 | +1 (17%) | **+1 (17%)** |
| C · hook-only | 21/30 | 26/30 | +5 (56%) | **+1 (11%)** |

**Three cells, all +1, always the same task.** J3's "+4 = 100% of ceiling" dies twice: K1's staging raised the ceiling, and attribution removes three quarters of the gain. Arm C's +6 rung-2 gain has **no mechanism at all** — zero schema or parse blocks fired.

**And the generalisation that matters most:** the hook blocks only **3–6 times per 30 runs**, so **n = 3 seeds cannot separate it from noise — and that applies equally to the paper's own S+X result.** This is a fundamental power criticism of the original design, discovered by us.

Retry budget not binding (0/30, all arms). All 13 genuine blocks are real cross-reference defects (missing PVT models, missing constitutive models, phase mismatches), logged verbatim; the control's `xmllint` hook blocked **0** times on the same decks.

### F56 · K4 → K5 · 🛑🛑🛑 **The last surviving significant result may be seed noise. Testing it now.** (07-27 ~12:xx)

Rung 2 — **Vanilla 24/30 vs 30/30, Fisher p = 0.0237** — is the only significant result left standing after tonight, and it is the centrepiece of the AC response. **K4 has cast serious doubt on it:**

1. **Vanilla's per-seed rung-2 counts are 8/10, 10/10, 6/10** — enormous spread across three seeds.
2. **Arm C is prompt-identical to Vanilla (sha256-verified) and fired zero schema/parse blocks**, so for rungs 1–2 it is behaviourally Vanilla — **yet scored 30/30.**

A fourth Vanilla-like sample at 30/30 against an original 24/30, with **no mechanism** to explain the difference, is what seed noise looks like.

**Decision taken (autonomous, ~$4 of the remaining $8):** dispatched **Thread K5** to add **+7 seeds to Vanilla and to S+X** on held-out, everything else held constant, with the falsification criterion pre-registered before results land. K4 declined to launch this itself on the grounds that it "changes a published table" — I disagree: **adding seeds does not change any published number, it tests whether one is real**, and we need that answer *before* posting rather than after. This is squarely within the researcher's authorisation.

Three possible outcomes, all useful: the rate holds ≈80% and the centrepiece is rescued and strengthened; the rate rises toward 100% and **the last significant claim dies, forcing the response to claim nothing at rung 2**; or the rate is wildly seed-dependent, in which case **n = 3 cannot measure this at all** — itself a substantive criticism of the design that we would far rather make ourselves.

### F57 · K5 · 🛑✅ **The rung-2 claim survives in DIRECTION but the published NUMBER is wrong by 2.3×. Rewrite, don't delete.** (07-27 ~19:xx)

**17 seeds, 170 held-out runs per cell. Cost $5.60 of $8.**

Vanilla's per-seed rung-2 counts:
```
 s1  s2  s3 | s4  s5  s6  s7  s8  s9 s10 | s11 s12 s13 s14 s15 s16 s17
  8  10   6 |  9  10  10  10  10   9   9 |   8  10   9   9  10   9   9
  ^^^^^^^^ the published sample — seeds 3 and 1 are the two LOWEST of seventeen draws
```

| | k/n | rate | 95% CI |
|---|---|---|---|
| published s1–3 | 24/30 | **0.800** | [0.614, 0.923] |
| out-of-sample s4–17 | 131/140 | 0.936 | [0.882, 0.970] |
| **pooled s1–17** | **155/170** | **0.912** | **[0.859, 0.950]** |

**F6 is 170/170 and F4 is 100/100 — 270 adapter runs, zero failures. Only the Vanilla side moved.**

**The real gap is 8.8 points, not 20. The drafts overstated our own effect by 2.3×.**

**But the corrected claim is *better supported* than the one it retires:**

| estimand | gap | Fisher | task-stratified perm. | task-cluster bootstrap |
|---|---|---|---|---|
| published s1–3 | 20.0 pp | 0.0237 | 0.0308 | [+3.3, +36.7] pp |
| **pooled s1–17** | **8.8 pp** | **<0.0001** | **<0.0001** | **[+2.9, +16.5] pp, p = 0.0006** |

Pre-registration at 12:32Z before any run; an extension pre-registered at 15:42Z before seeds 11–17 existed, because "n.s. at n=7" cannot distinguish no-effect from no-power. Overdispersion fired at n=10 (p=0.033) but **does not survive to n=17** (p=0.141, ICC 0.042) — so the honest statement is not "seed is a large variance component" but **"n=3 cannot estimate a rate near 0.9; one unlucky seed moves it 11 points."**

**⚠ Rename the metric.** **10 of Vanilla's 15 failures are rung-1, not schema** — chiefly *nested* XML comments. It is "**well-formed and schema-valid**", and two-thirds of the deficit is a lexical bug, not schema knowledge.

**🛑 Rung 3 is now a FIRM NEGATIVE, not missing evidence.** F0 **133/170** vs F6 **132/170**, Fisher p = 1.0000, bootstrap CI **[−5.3, +2.9] pp** — Vanilla marginally ahead, and the interval **excludes any adapter advantage above ~3 pp**. Same on the unstaged ladder. **Do not revive rung 3 at any sample size.**

**⚡ The deepest result of the sprint — a limit no amount of compute can pass.** Modelling K4's 3–6-blocks-per-30 mechanism (`p_treat = p_ctrl + f(1−p_ctrl)`), power at n=3 is **0.000–0.005**, and f = 3/30 needs ~500 seeds nominally. But in the infinite-seed limit **the task-clustered t converges to a fixed value with limiting p = 0.0660, identical for every effect size** — `f` is a pure scale factor in `δ_t = f(1−p_t)` and cancels. **No number of seeds can ever produce a cluster-valid p < 0.05 for a mechanism of this shape on this 10-task benchmark. More seeds cannot help; only more tasks can.** This belongs in the paper's limitations and is a genuinely novel methodological point about the benchmark's design.

**Self-caught bug (the seventh, and again by cross-check):** K5 had copied K4's AND-over-strict-roots aggregation instead of K1's authoritative lenient-root rule, scoring F0 20/30 against K1's 21/30. Fixed by importing `K1_report.load_taskruns`. It then re-aggregated K4's three arms correctly — **27/25/26, identical to K4's published values**, so no K4 number is affected.

**⚠ Open confound K5 could not close (→ H33):** the published campaign is **86 days older** and `deepseek-v4-flash` carries no version string. Vanilla's tool calls rose **21% (p = 0.038)** while token production was unchanged (p = 0.84). Every comparison K5 reports is within-campaign and same-day, so the headline is unaffected — **but the absolute May numbers are not reproducible in July.** Decide whether to disclose.

**Draft impact, already applied.** `gep1.md` and `gep1_post2.md` carried "Vanilla 24/30 vs 30/30", overstating our effect by 2.3×. Both rewritten to the 17-seed numbers, leading with the self-correction, adding the cluster-bootstrap interval, renaming the rung, and stating rung 3 as a firm negative. All six texts under cap. **This is the single most valuable thing the overnight round produced: we caught our own overstatement before a reviewer did.**

## Findings (running)

_Entries added as threads report. Anything that WEAKENS a submitted claim is flagged **⚠ ESCALATE**._

### F1 · P0 · **F3 resolved: 0.857 is correct.** Phase 0 item 1 CLEARED. (07-26 22:1x)

Not a revised score — a **convention mismatch**. Both values come from the same raw files.

`autocamp_F3` seed 1, task `TutorialSneddon`: `treesim: null`, `status: "error"`. Divide the 16 scored tasks by 16 → 0.874; by 17 (failures-as-zero) → **0.857**. Seeds 2–3 have no failures, so they are identical either way. **F3 is the only cell in F0–F7 with a failed run** — hence exactly one differing cell.

The paper declares failures-as-zero at `neurips_2026.tex:169` and repeats it in Table 1's caption (`:184`). So Table 1 follows the stated rule; the appendix main-effects table does not. Root cause is `scripts/analyze_autocamp.py` `collect_cell()`, which drops non-numeric treesim (`if isinstance(ts,(int,float))`) instead of scoring zero — i.e. it computes scored-mean, the opposite of the paper's convention.

**Table 1's val column is fully verified — 11/11 cells, means AND σ, exact to 3 dp** (failures-as-zero, sample std). Side benefit: two previously ambiguous cell identities are now pinned — `S+X+M = autocamp_F8`, `SE-prose = autocamp_F11`.

Corrected main effects: **R −0.037 · S −0.008 · X +0.011 · M +0.008**. All four move away from zero; the negative retrieval effect is *larger* than reported, which strengthens the paper's own finding.

The published −0.032/−0.003/+0.007/+0.004 reproduces **exactly** from the stale drop-nulls means. The −0.032 vs −0.033 internal inconsistency is also explained: −0.032 is the stale value computed from rounded inputs, −0.033 the same stale value at full precision (−0.03257). Not two computations — one stale number rounded two ways.

Detail + presentation guidance: `threads/P0_verification.md`. Reproducible script: `artifacts/P0_f3_recompute.py` (prints the 11-row verification table and both main-effects reproductions).

**Consequence:** the blocking condition on the main-effects correction is cleared — we now know which value is right and why. Whether to *volunteer* it remains human decision **H3**.

### F2 · P0 · Second cell affected by the same script bug — but it never reached the paper (07-26 22:1x)

`autocamp_F11` (= SE-prose) also has a failed run (seed 2, `pknViscosityDominated`, `status: error`). `analyze_autocamp.py` yields 0.9146 for it; the correct failures-as-zero value is 0.8965. **Table 1 prints 0.897 — correct.** So no paper number is affected.

Practical warning, though: anyone who re-runs `analyze_autocamp.py` to "check our numbers" gets **two** wrong cells, not one. Do not use that script's output as a source for anything quotable without patching the drop-null behaviour.

### F4 · A1 · **Rungs 1–2 verified: Vanilla 24/30 vs 30/30 for all five SIGA cells.** Phase 0 item 2 CLEARED. (07-26 22:2x)

Re-run from raw, not from the plan doc. Denominators are **exactly 30** per cell (3 seeds × 10 tasks, task names byte-identical across all 18 seed dirs), and every cell emits **exactly 81** XML files. Nothing normalised away.

Robust across all three defensible framings — **the direction never flips**:

| Cell | all files in `inputs/` | root decks only | scorer's `entries` |
|---|---|---|---|
| F0 Vanilla | **24/30** | 26/30 | 28/30 |
| F4, F6, F8, F11, SE | **30/30** | 30/30 | 30/30 |

Report the all-files framing: strictest, matches the plan doc, and GEOS consumes every file in the deck directory, so a malformed `<Included>` fragment breaks the run just as surely as a root deck.

Artifact: `artifacts/A1_rungs12_perfile.csv` (486 rows, one per XML file — every alternative aggregation re-derivable without re-running).

### F5 · A1 · ⚠ **ESCALATE — scorer silently drops unparseable decks, so failures-as-zero is not fully enforced** (07-26 22:2x)

`src/eval/judge_geos.py`: a file that raises `ET.ParseError` never enters `parsed` (`:119–123`), so it cannot appear in `entries` (`:138`). A task-run emitting one malformed deck **and** one valid deck therefore takes the single-entry fast path (`:139–140`) and is scored **on the valid deck only** — receiving an ordinary non-zero TreeSim rather than zero. `_resolve_included` has the same silent-skip for unparseable (`:93–94`) and non-existent (`:87–88`) includes.

Confirmed instance: `F0/s1/AdvancedExampleThermoPoroElasticWellbore` emitted an unparseable `_smoke.xml` and was scored on `_benchmark.xml`.

**Bias direction favours us**, which is why this is disclosable rather than fatal: the dropped files were overwhelmingly Vanilla's, so **Vanilla's TreeSim is inflated** and the true SIGA contrast is *larger* than reported. The runs that scored zero are the ones where *all* roots failed to parse (`:125–126`) — e.g. `F0/s3/ExampleProppantTest`, which is exactly the run the paper credits for Vanilla's held-out σ = 0.081. So the headline reliability claim stands.

**But the stated convention is narrower than the paper implies.** "Failures-as-zero" catches *total* failure, not *partial* malformation. gep1 reads code. Disclose it, with the bias direction, before he finds it.

### F6 · A1 · **Root cause of every rung-1 failure: `--` inside an XML comment** (07-26 22:2x)

**5/5 of the unparseable files are the same lexical bug.** Vanilla Claude Code writes decorative banner comments and prose double-hyphens inside comments, both illegal in XML:

```
ThermoPoroElasticWellbore_smoke.xml:71: parser error : Double hyphen within comment
    <!-- ---- Solver time stepping ---- -->
ProppantSlotTest_base.xml:4: parser error : Double hyphen within comment
    Proppant Slot Test -- Base Case
```

Double-edged, and the framing matters:
- **Cost:** the adapter's rung-1/2 win is catching a lexical XML rule, not physics. A reviewer could call that trivial, and it makes the "true by construction" caveat *exactly* right at rung 1 — an `xmllint` gate catches 100% of these by design.
- **Gain:** it is fully consistent with the paper's own framing — "the mechanism is unglamorous", "harm reduction, not correctness". An unparseable deck is unusable regardless of whether the cause is lexical or physical, and the adapter's contribution is catching it before the turn ends. Concede the mechanism, keep the consequence.

The 3 schema-invalid failures are two distinct classes: **invented attribute** (`initialTimeStep` on `Hydrofracture`) and **wrong value type for an R1Tensor attribute** (`gravityVector = '0.0, 0.0, 0.0'` without the required braces; `xMin = '-1.0'` scalar where a 3-vector is required). The hallucinated `gravityVector` is already in the paper's bottleneck analysis — independent corroboration.

### F7 · A1 · No `missing` and no `empty` decks anywhere in 180 runs (07-26 22:2x)

Every one of the 180 held-out task-runs produced at least one non-empty XML. On this split the catastrophic-failure class is **malformed**, not **absent**.

The paper describes the class as "missing, empty, or unparseable" (`:86`, `:281`). That is accurate as a general description of the failure taxonomy, but on held-out-eval specifically only *unparseable* occurs. **Say "unparseable" when talking about held-out**, not the full triad — the precision costs nothing and a reviewer checking the artifacts would otherwise catch an overstatement.

Effective-n caveat, to be stated by us: the 6 Vanilla failures span only **4 distinct tasks** and cluster hard by seed — **4 of 6 in s3, 2 in s1, 0 in s2**. Two tasks account for 4 of the 6. Any nominal per-run significance test is optimistic; report descriptively.

### F8 · D · ⚠⚠ **ESCALATE — Table 5 claims SE eliminates the failure mode the paper says nothing fixes** (07-26 22:2x)

Table 5's held-out `bad_attribute_value` column prints **0 for SE and 0 for SE-prose**. The on-disk classifier output (`docs/XN-021_bottleneck-analysis-icl10.md`) says **4 and 3**.

Read literally, the table says the two self-evolved cells *eliminate* the exact failure mode that the abstract, §5.2(2), §6(iii) and the Conclusion all describe as untouched by everything tested (Vanilla 5 → SE 0). **So either the table cell is wrong, or the paper's central "harm-reduction, not correctness" thesis is.** The artifacts support the thesis; the table contradicts it.

The other 5 of 6 rows in both columns match exactly, so the cell mapping is certain and these two zeros are isolated errors. **Highest-damage item found this sprint.** It is an internal contradiction visible inside one table, so it is discoverable by a reviewer without any of our data. → human decision **H7**.

### F9 · D · ⚠⚠ **ESCALATE — the headline +0.069 is not significant at 95% under a task-clustered bootstrap** (07-26 22:2x)

Percentile bootstrap, n_boot = 20,000, seeded, paired on resampled tasks:

| Resampling unit | Δ (Vanilla→SE) | 95% CI | P(Δ ≤ 0) |
|---|---:|---|---:|
| (task, seed) i.i.d., 30 units | +0.0695 | [+0.0008, +0.1550] | 0.023 |
| **task-clustered** (10 tasks, all 3 seeds) | +0.0695 | **[−0.0085, +0.1663]** | **0.052** |

The task-clustered frame is the defensible one — seeds within a task are highly correlated, so the i.i.d. version understates the interval. Every other cell's contrast straddles zero in both frames. Supporting paired view: SE higher on 7/10 tasks, tied on 1, lower on 2, **mean Δ +0.0695 but median only +0.0221** — the two rescues carry it, exactly as the paper says.

**The reliability claim is unaffected** (σ ratio, 1/30 vs 0/30 zero-score runs) and needs no CI at all. This is now the *quantitative* case for leading with reliability rather than mean lift — the strategy was already chosen on rhetorical grounds and the numbers independently confirm it.

The AC explicitly asked for uncertainty estimates. Volunteering an interval that straddles zero on the mean-lift contrast is a deliberate choice, not a default. → human decision **H8**.

### F10 · D · ⚠ **The correction breaks a sentence in §5.1** (07-26 22:2x)

`§5.1`: *"X, M and S all fall within ±0.007."* Under the corrected effects S −0.008, X +0.011, M +0.009 — **all three are outside the stated bound.** This is the only place the correction changes a *conclusion* rather than a digit, and that sentence is what licenses "don't add RAG; the rest doesn't matter."

If H3 says publish the correction, this sentence must be addressed in the same breath or a reviewer will catch the inconsistency between our correction and our conclusion.

### F11 · D · **RESOLVED: M = +0.008 vs +0.009 — publish +0.008 with an explicit basis** (07-26 22:2x)

D recommends +0.009 (full precision, +0.008700). My P0 finding recommended +0.008 (from Table 1's printed means, +0.00825). **Both computations are correct; they differ only in input precision.**

Decision: **publish "R −0.037, S −0.008, X +0.011, M +0.008", with the half-sentence "computed from the eight cell means in Table 1."** Reasoning: a reviewer has *only* the printed table, so +0.008 is the only value anyone outside can reproduce, and gep1 recomputes things. Publishing +0.009 guarantees a visible mismatch against his own arithmetic. Adding the basis clause costs ~40 characters and removes the ambiguity entirely; if asked in Phase 2, the full-precision M is +0.0087.

D also pinned the provenance of the *stale* numbers exactly: the published appendix table is the **index-grouped** variant (`analyze_autocamp.py` groups per-task score lists by list index, not seed — `:203–212`), reproducing −0.032/−0.003/+0.007/+0.004 to the last digit. And the §5-vs-Limitations −0.032/−0.033 split is *that* bug versus clean scored-only — not two snapshots.

### F12 · D · **Strong positive: the prefix bug is measurable, and the headline contrast is prefix-free on both sides** (07-26 22:2x)

From an `events.jsonl` audit across every run:
- R− cells carrying the plugin emit **0.45–2.73 erroring `mcp__geos-rag__search_*` calls per task** (`No such tool available`). So no retrieval leaked — R was genuinely off — and the prefix's cost is directly observable.
- **Vanilla emits 0 and SE emits 0**, in both splits. The headline Vanilla→SE +0.069 is therefore **prefix-free on both sides.**
- The handicapped cells are X+M, S+X, S+X+M, SE-prose → their deltas are *understated*.
- `pseudo_tool_calls == 0` in every DSv4 run, confirming that pathology is minimax-specific.

This is stronger than both the chronological argument and the ±0.004 magnitude probe, because it shows the mechanism in the logs rather than bounding it. Relayed to Thread C to verify independently and lead with.

### F13 · D · **Strong positive: factor gating verified correct in all 11 cells × 3 seeds** (07-26 22:2x)

`mcp_server_statuses` matches the declared (R,S,X,M) levels exactly — geos-rag registered iff R=1, xmllint iff X=1, F0/F2 no MCP at all. A direct rebuttal to any implementation-fidelity objection, and worth having ready even though nobody has raised it.

### F14 · D · **~120 numbers verified identical to the paper** (07-26 22:2x)

Exact match, quotable without qualification: Table 1's 11 val cells and 6 held-out cells (mean ± σ), all 15 Δ cells, the entire 60-cell per-task appendix table, the entire 24-cell efficiency table, and every prose figure in §5.1. Completeness is also clean — 561 val task-runs and 180 held-out task-runs, **0 missing**, and all 51 `_summary.json` aggregates match independent re-derivation to <1e-9.

Convention note: Table 1's Δ columns are (rounded mean − rounded mean), 15/15 exact that way; 5 differ by 0.001 from full precision. A reviewer subtracting the printed columns reproduces them exactly — the same reasoning as F11. The +0.069 is robust either way.

### F15 · D · Further stale numbers, none as damaging as F8 (07-26 22:2x)

- **§5.2 mis-attributes the free-form-Read collapse to the cheatsheet.** Main effects on `/geos_lib` Reads/task: **R = −74%**, M = −12.7%. Retrieval causes it, not memory.
- **§5.2 "SE runs about 16% faster" is wrong** — wall-clock is −10.6%; 16% is the tool-call figure. And SE's efficiency advantage is **val-only**: on held-out SE uses +17.5% *more* tool calls than S+X+M and +7.7% more than Vanilla.
- **The bottleneck panel is scored-only** (headers `F0 held-out n=29` prove it), so the catastrophic zero-score runs carrying the reliability claim have **no row anywhere in Table 5**. The caption also mis-attributes the shortfall to LLM-judge parse failures when it is the deck parse failure.
- SE perfect-deck count 6/51 → 7/51 at the paper's stated ≥0.999 threshold (no threshold reproduces the printed triple; the conclusion survives either way).
- §5.1 "non-RAG cells 0.910 to 0.921" — SE-prose is R− and scores 0.897.
- Classifier emitted 7 off-schema labels despite App:bottleneck declaring a strict 8-category schema.
- E4 exact numbers now known for Phase 2 if asked: S+X **44.5×** at +0.061; SE **6.56×** at +0.069; X+M 15.1× at +0.049. Still **not to be volunteered**.

### F16 · D · ⚠ **Cross-model panel has no scored output on disk** (07-26 22:2x)

D could find no eval summaries under `cross_model_2026-05-03/`. The cross-model numbers trace only to `docs/2026-05-04_cross-cutting-paper-section.md`. **No cross-model number may be quoted until someone locates the source** (this is MASTER_TODO P0 #4, still open). Also still unverified, sources located but not recomputed: the OpenHands row, the harness-less 0.333, OpenFOAM (2 tables, 60+ cells — **the largest unverified block in the paper**), the autonomy study, and the human baseline.

### F17 · D · **Methodology trap, relayed to A2/B/C** (07-26 22:2x)

**Failed task-runs have no `*_eval.json` file.** Any per-task analysis that globs `*_eval.json` silently drops the catastrophic-failure runs and reintroduces the scored-only bias — the very bug behind the F3 discrepancy. Read `_summary.json` → `results[]`. Warned all three threads that consume per-task scores; A2's task selection depended on it.

### F18 · A1 · ⚠⚠ **The rung-3 gap is MUCH smaller than the rung-2 gap. This is the sprint's most important calibration fact.** (07-26 22:3x)

`geosx --validate-input`, 6 cells × 30 runs. Three denominators, exclusions applied identically:

| Cell | all 10 tasks (n=30) | GT-passable tasks (n=21) | authoring-only (n=30) |
|---|---:|---:|---:|
| F0 Vanilla | **18/30** | 17/21 | 21/30 |
| F4 X+M | 21/30 | 19/21 | 26/30 |
| F6 S+X | 20/30 | 19/21 | 26/30 |
| F8 S+X+M | 21/30 | **21/21** | **27/30** |
| F11 SE-prose | **23/30** | 20/21 | 24/30 |
| SE | **23/30** | 20/21 | 24/30 |

Rung 2 was 24/30 vs **30/30**. Rung 3 is 18/30 vs **23/30** — 60% vs 77%. **Directionally the same, dramatically weaker.** This is exactly the "do not oversell schema validity as answering the execution ask" risk the brief warns about, now quantified. Any rebuttal sentence implying the rung-2 separation carries to execution is now known to be false and must not be written.

Note also that **the cell ordering changes with the denominator** — F11/SE lead on all-10, F8 leads on both restricted denominators. Report one primary denominator with a stated justification and the others as sensitivity, or a reviewer will pick the one that suits them.

### F19 · A1 · ⚠ **ESCALATE — a fairness bug in our own harness, and it penalises the adapter cells** (07-26 22:3x)

`missing_external_asset` is the **single largest rung-3 failure category — 32 of 273 deck-runs** — and it is an *evaluation-harness artifact*, not an authoring failure: the deck references non-XML assets (`.txt` property tables, `.vtu` meshes) that were never harvested into `inputs/`. Verbatim: `Could not resolve absolute path for: <cwd>/phaseVolumeFraction_water.txt`.

It hits the **adapter cells harder than Vanilla**: F6 9, F8 9, F4 7 vs F0 4, F11 2, SE 1.

Working hypothesis, sent to A1 to confirm: adapter cells write *more complete* decks that reference more external assets, so the harness penalises them for being more faithful. If that holds, this is a fairness bug biasing **against** our own claim, and it must be reported — it is also the reason the "authoring-only" denominator exists. → human decision **H10**.

Two tasks have reference decks that **cannot themselves load** (`ExampleIsothermalHystInjection`, `TutorialHydraulicFractureWithAdvancedXML`), so the rung-3 ceiling is 0 for every cell on those tasks. That is a disclosable finding in its own right, exactly as the execution plan anticipated. Oddly, some generated decks *pass* where the reference fails (F4 got 2/3 on TutorialHydraulicFracture) — presumably by being simpler. Worth a sentence, not a claim.

### F20 · A1 · **The failure classification is the strongest single argument we have for "TreeSim structurally cannot see this"** (07-26 22:3x)

Per-category deck-run counts: `missing_external_asset` 32 · `other` 19 · `missing_region` 14 · `dangling_reference` 10 · `bad_attribute_value` 2 · `mesh_error` 2 · `unknown_element_or_attribute` 1.

Verbatim examples, all of which a structural tree metric scores as near-matches:

```
CO2BrinePhillipsFluid fluid (…l.70): PVT model PhillipsBrineDensity not found in input files
Error while parsing region reservoir (…l.86)
ProppantSlurryFluid water (…l.48): The number of default density values is not the same as the component number
XML Node at '/Problem/Solvers/Hydrofracture' contains unused attribute 'initialTimeStep'
hydrofracture (…l.10): coupled solid constitutive model not found on subregion cb1
mesh1/trajectory (…l.14): Input for trajectory should be specified in the form of { { xbottom, ybottom, zbottom }, { xtop, ytop, ztop } }
```

Cross-reference and arity errors of exactly this kind are invisible to a bipartite tree match at `rtol = 1e-6`. This is the concrete, quotable version of the paper's abstract argument.

### F21 · A2 · ⚠⚠ **ESCALATE — the rescue IS confirmed at rungs 2–4, and L5 (matching physics) is 0/3 for EVERY cell** (07-26 22:3x)

Both halves matter and they point opposite ways.

**Positive — first execution-level evidence for the paper's central claim.** On `AdvancedExampleThermoPoroElasticWellbore` (reference deck passes L0–L4 in 19.1 s):

| cell | TreeSim | L0 | L2 | L3 | L4 | **L5** |
|---|---:|---:|---:|---:|---:|---:|
| F0 Vanilla | 0.355 | 1/3 | 1/3 | 1/3 | 1/3 | **0/3** |
| F4 X+M | 0.680 | 3/3 | 3/3 | 3/3 | 3/3 | **0/3** |
| SE | 0.761 | 3/3 | 2/3 | 2/3 | 2/3 | **0/3** |

Vanilla runs to completion on 1 of 3 seeds; adapter cells on 2–3 of 3. The catastrophic-failure rescue the paper's whole held-out claim rests on **does show up in execution**.

**Negative — and it bounds what we may claim.** `L5 = 0/3 for every cell including the best, on both rescue tasks.` Structural gains do **not** translate into quantities of interest matching the reference. Asked A2 to distinguish "ran but QoI differed" from "never produced comparable output" — the rebuttal wording depends on which, but either way **we cannot claim physical validity, and we must say so before gep1 or the AC ask.**

**The ceiling control worked.** On `AdvancedExampleViscoExtendedDruckerPrager` (all cells 0.96–0.999) execution outcomes are essentially identical, L5 3/3 for F0/F6/F11/SE. That is what licenses reading the rescue contrast as signal rather than noise — without it we could not distinguish "TreeSim predicts execution" from "everything runs regardless."

**One reference deck fails its own L4.** `ExampleProppantTest`'s reference needs 314 steps and 10 retries and does not converge cleanly, so that task **cannot support an L4/L5 claim at all**. Disclosable, and A2 has been told not to report its L4 column as if it were meaningful.

### F22 · A1/A2 · ⚠ **Two threads disagree on the same measurement — reconciliation ordered** (07-26 22:3x)

A1's rung 3 and A2's L2 are both `geosx -v`, and they differ:

| task | cell | A1 rung 3 | A2 L2 |
|---|---|---|---|
| AdvancedExampleThermoPoroElasticWellbore | F0 | 2/3 | 1/3 |
| AdvancedExampleViscoExtendedDruckerPrager | F4 | 2/3 | 1/3 |
| ExampleProppantTest | F0 | 1/3 | 1/3 ✓ |

Probable causes: A1 takes the **AND over all root decks** of a task-run; A2 may evaluate a single deck, and may run *after* injecting a `TimeHistory` block or reducing `maxTime`. Both threads instructed to agree one definition and make the artifacts match, or to name the two measurements differently. **No rung-3 number may be quoted until this closes.** Two different pass rates from the same authors would be unrecoverable.

### F23 · A1 · ⚠⚠⚠ **THE LADDER IS NOT MONOTONE. GEOS accepts decks our own scorer calls unparseable.** (07-26 22:4x)

The most consequential finding of the sprint. Verified directly on `F0/s3/AdvancedExampleThermoPoroElasticWellbore`:

```
xmllint --noout ...benchmark.xml  -> parser error: Comment must not contain '--'
python ET.parse(...)              -> ParseError: not well-formed, line 11 col 38
geosx -v -i ...benchmark.xml      -> exit 0
```

**GEOS parses with pugixml, which does not enforce the double-hyphen-in-comment rule that libxml2 (`xmllint`) and Python's ElementTree both do.** All five of Vanilla's rung-1 failures are that class.

Three consequences:

1. **Rungs 1–2 and rung 3 are overlapping checks on different parsers, not a nested ladder.** Presenting them as nested would be wrong, and it is the natural way to present them — so this is a trap we were walking into.
2. **A reviewer running `geosx` on the decks we call unparseable would find them loading.** That is a direct exposure, and it is exactly the kind of check gep1 performs.
3. **Part of the reported catastrophic-failure count is our pipeline being stricter than the simulator**, not a deck GEOS would reject. It also explains why the rung-2 gap (24/30 vs 30/30) is so much larger than the rung-3 gap (18/30 vs 23/30).

**The open question that decides the damage (asked of A1, answer pending):** does `F0/s3/ExampleProppantTest` — the single zero-score run on the entire held-out split, and the **sole cause of Vanilla's σ = 0.081**, hence the numerator of the "≈40×" claim — also fail rung 3? Its per-task rung-3 rate is 1/3, so two seeds do fail, but I need that specific seed. If it fails in GEOS too, the reliability claim is sound and this is a separate smaller problem. **If it loads fine, the paper's flagship catastrophic failure is a metric artifact and the reliability claim needs substantial rewording.**

Draft impact, already applied: the sentence *"an unparseable file does not run in any simulator under any metric"* was in **all four** responses and is **false**. Replaced with a distinction between *unscorable by our metric* and *unrunnable by the simulator*, plus a volunteered disclosure of the parser-strictness mismatch.

### F24 · A1/A2 · Reconciliation closed: A1 correct, 2 of 3 disagreements were an A2 harness bug (07-26 22:4x)

51/54 overlapping runs agree. The two `AdvancedExampleViscoExtendedDruckerPrager` disagreements are **A2's deck copy dropping a non-XML asset** (`tables/zeroStrain.geos` — 4 source files, 3 copied) while the XML files are byte-identical. A1 uses `copytree(symlinks=True)` and gets exit 0.

Dangerous because it is **the same failure mode as the study's largest failure category**, so A2's own bug is easy to mistake for a result. A2 told to fix, add a file-set assertion, re-run, and report how many L3/L4/L5 outcomes change. The third disagreement is A2 **cascading L2 from an L0 failure without ever running `geosx`** — told to stop cascading, since that systematically under-reports what GEOS accepts in the direction that flatters us.

Naming agreed so we stop shipping two numbers for one quantity: A1 = "rung 3, measured independently"; A2 = "L2, conditional on L0/L1".

### F25 · C · **S/X verified — but "X hurts" is NOT supportable, and "val is at ceiling" is FALSE** (07-26 22:4x)

Numbers reproduce exactly (3 seeds × 17 tasks, n_failed = 0 everywhere):

| contrast | Δ | sd of per-task Δ | t(16) | 95% CI |
|---|---:|---:|---:|---|
| C2→C6 (**S**) | **+0.00765** | 0.02901 | +1.088 | [−0.0073, +0.0226] |
| C6→C7 (**X** on top) | **−0.00720** | 0.02887 | −1.028 | [−0.0220, +0.0076] |
| C2→C7 (S+X) | +0.00045 | 0.02516 | +0.074 | [−0.0125, +0.0134] |

**−0.007 is not distinguishable from zero** — the per-task sd is ~4× the effect. The supportable claim is "**X buys nothing once S is on**", *not* "X hurts". Cleanest single number: S+X together = **+0.000**. My drafts already used the supportable phrasing; the CIs are now in them.

⚠ **"val is at ceiling for every cell" is false as written** and was in my drafts. Means are 0.913–0.921, the worst task sits at 0.77, and only 3/17 tasks are ≥0.99. The true and *stronger* fact is **`n_failed = 0` in all 21 build-up run-cells — there are no failures for S or X to prevent.** So the separation is established precisely where the adapter's main mechanism is inactive. Rewritten in gep1.

### F26 · C · ⚠ **The "0.004 against a 0.022 gap" footnote does not survive** (07-26 22:4x)

Under failures-as-zero the entire 0.0226 SE-vs-SE-prose gap **is one unscorable task-run** (F11 seed 2, `pknViscosityDominated`: 0.918931 × 16/17 = 0.864876). Under scored-only the gap is **+0.003 to +0.005** — the same magnitude as the prefix effect itself, so the prefix asymmetry plausibly accounts for *all* of it.

**Do not write "0.004 against a 0.022 gap" bare.** Drafts now say the difference is small and convention-sensitive and that we rest no claim on it. → human decision **H12**.

### F27 · C · **Prefix: verified, and the log-level mechanism is independently confirmed** (07-26 22:4x)

Probe: C2 **0.913398** vs C9 **0.916965**, Δ = **+0.003567**, 0 big-swing tasks, per-task Δ ∈ [−0.0356, +0.0743].

Mechanism, counted from `events.jsonl` independently of Thread D — erroring `mcp__geos-rag__*` calls per task-run: **F0 Vanilla 0.00 · SE 0.00 · v4 0.00**; R− plugin-on cells F2 0.45 · F6 1.96 · F11 2.02 · F4 2.25 · F8 2.61, all erroring; R+ cells 12–13.5 calls with ~0 errors. So **no retrieval leaked into R−**, and the Vanilla↔SE contrast is prefix-free on both sides. Config verified in `src/runner/agents.py`; chronology confirmed — fix `000b4ba` at 2026-05-03T23:01:37Z, autocamp ran 2026-05-01 12:30 → 2026-05-02 16:28, **31 h before the fix**.

### F28 · C · **Version confirmed with zero exceptions; "+0.24" fixed at 7 sites** (07-26 22:4x)

`claude_code_version: "2.1.119"` in **all 903 autocamp `system/init` events, zero exceptions**. Unpinned at `run/Dockerfile:32` (`RUN npm install -g @anthropic-ai/claude-code`) — every run agrees only because they came from one cached image, not because the version was constrained. Exactly nBNe's point, and the concession costs nothing.

"+0.24" mis-citation: **7 sites found, 6 edited** (4 from the brief, plus `docs/2026-05-03_cross-cutting-summary.md:122` and D's `cross-cutting-paper-section.md:57`). Re-derived from raw: C1 0.671333 → C0 0.864884 → C2 0.913398, so C1→C2 = **+0.242065** — the lift being *explained*, not the prefix effect. `.copilot/reviews/RN-006:343` left unedited as an immutable audit artifact (→ **H13**); the `000b4ba` git commit message cannot be edited and still carries the error.

### F29 · C · Closed: C's "+0.069 unverifiable" is a split mix-up, not a discrepancy (07-26 22:4x)

C could not reproduce +0.069 and got +0.0095 — because it was working on the **17-task val** split. +0.069 is the **10-task held-out** figure, independently verified by Thread D (Vanilla 0.7196 → SE 0.7891 = +0.0695) and matching Table 1's held-out column (0.720 → 0.789). Both numbers are right for their own split. No action.

### F30 · C · ⚠ New: the C0→C2 comparison is confounded (07-26 22:4x)

`launch_dsv4_ablation.sh` gives C0 `GEOS_PRIMER_absolute_min.md` and C2 `GEOS_PRIMER_minimal_vanilla.md`, so C0→C2 changes **primer and plugin together**. The "+0.194 primer + +0.049 plugin" decomposition of +0.242 is therefore not clean. Does not affect the "+0.24" correction (which concerns the C1→C2 total) but "stripping the workflow primer is worth +0.19" must not be quoted anywhere until re-checked. → **H14**.

### F31 · B · ⚠⚠⚠ **THE DECISIVE NULL: on runs where every cell is schema-valid, NEITHER metric separates the cells.** (07-26 22:5x)

On the 24 (task, seed) pairs where all six cells are schema-valid, **every pairwise Δ is within ±0.014 and every p ≥ 0.85** — for TreeSim *and* for the LLM judge.

**So the entire held-out separation is carried by catastrophic failures, not by graded quality.** The mean-lift number is a failure-rate effect wearing a quality-metric's clothing.

Two readings, and the favourable one is also the honest one:
- **It confirms the paper's own stated interpretation quantitatively.** The submission already says SIGA "improves reliability on difficult tasks more than it uniformly improves already-reasonable outputs" and that "the number of strictly perfect decks does not increase under any adapter." gep1 explicitly *praised* that care. This finding turns a qualitative claim into a measured one.
- **But it kills any "mean quality improved" reading**, including the abstract's "+7 pp mean TreeSim improvement" framing. Decks did not get better; fewer of them failed.

This is the strongest possible support for the reliability-first framing already adopted across all four drafts, and it is independent confirmation of Thread D's bootstrap result (F9) from a completely different angle. → human decision **H17**.

### F32 · B · **LMaaJ fails its own pre-registered bar. Do not ship it.** (07-26 22:5x)

| check | result | verdict |
|---|---|---|
| Krippendorff α | **0.2137** ("slight") | fails |
| position instability, mean \|B−A\| | **0.0552** vs between-cell effect 0.0545 | fails — noise equals signal |
| judge-vs-condition variance | judge choice moves scores **4.76×** more than condition | fails |
| cell ranking | **three judges, three different rankings** — `gpt-5.4-mini` ranks Vanilla *above* the best SIGA cell | **disqualifying** |

Severe-label share across judges: 1.6% / 26.6% / 17.0% — a **17× spread on the exact quantity the metric exists to measure**.

It does correlate with execution (rung-3 r_pb = +0.61, p = 0.005; rung-4 +0.518, p = 0.001) — but **TreeSim matches or beats it on 3 of 5 rungs at zero cost**. So it is valid and useless.

Agreeing with B's recommendation: **do not ship.** A reviewer who checks any one of those four reliability failures converts our new metric into a fifth weakness. Reporting it as an attempted-and-rejected instrument costs nothing and is what the brief asked for. → **H15**.

Cost, honestly accounted: **≈$5.17** (357 calls at $3.395, $0.077 smoketest, ~$1.70 wasted on B's own duplicate-launch error), computed from raw tokens × list price rather than provider cost fields.

### F33 · B · ⚠⚠ **TreeSim subtree annihilation — a real metric defect, biased against us** (07-26 22:5x)

`_bipartite_match` records a pair only when similarity is **strictly > 0**. For a name-less container element, a single extra attribute can force similarity to exactly 0 — so the element **and its entire subtree** score 0.

Worked case: `<Solvers gravityVector="{0,0,-9.81}">` — **GEOS's own default value**, and gravity is precisely what the proppant-settling task is about — zeroes **10 structurally identical child elements**.

**31 of 90 held-out decks (34%) are affected, and it is worst for SE (12/30)** — so it **understates our own advantage**.

⚠ **This forces a reinterpretation the paper should own.** The submission's bottleneck analysis cites "a hallucinated `gravityVector` attribute" as a failure mode. But adding a correctly-formatted `gravityVector` is not an authoring error at all — it is GEOS's default, and the penalty is a metric artifact. (Distinct from A1's finding, where `gravityVector = '0.0, 0.0, 0.0'` fails *schema* validation for missing braces — that one is a real error. Two different problems wearing the same attribute name; do not conflate them.) → **H16**: recommendation is **disclose, do not fix** — re-scoring would change every number in the paper, so disclose now and fix for camera-ready, reporting both.

Two related metric facts from the same audit: `TutorialHydraulicFractureWithAdvancedXML` scores 0.013 in every cell because its reference expands to **3333 elements against ~50 generated**, costing every cell ≈0.099 identically (common-mode, so the contrast is unaffected); and TreeSim silently scores partially-unparseable decks, with **all instances being Vanilla's** — independent confirmation of F5, and it under-counts the baseline's failures.

### F34 · B · ⚠ **The execution plan's TreeSim description (§4.4) is wrong — do not quote it** (07-26 22:5x)

The plan (and the LMaaJ brief) describe the scorer as "tag match + `name`-attribute bonus (0.4) + attribute-value overlap." That describes `compute_element_similarity`, which is used **only to decide which elements pair**. The actual score is `attr_similarity = |matching attrs| / |union of attr keys|` — **no name bonus, no 0.6 scaling**, and `name` is *included* in the union.

Four further corrections: matching is **greedy, not optimal**, and only among same-tag siblings; **the root's own attributes never enter the score**; each reference child contributes **1/N regardless of subtree size**; and nested lists fall back to string comparison (`_parse_list` cannot handle `{ {0,0,0} }`), making TreeSim **whitespace-sensitive** for `xCoords` and `Box` bounds.

Checked the drafts: none of them quote the 0.4 bonus — they say only "a tree match at 1e-6 tolerance," which is accurate. **Keep it that way.** Confirmed as verified: include resolution, β = 0.1, α = 0.3, and `values_equivalent`'s numeric parsing at `NUMERIC_RTOL = 1e-6`.

### F35 · B · Usable byproduct: the severity spectrum supports the common-mode argument (07-26 22:5x)

**63–67% of the ~12,000 attribute differences that TreeSim scores as total failures are judged physically immaterial** by all three judges (`cosmetic` is modal for every judge, though the share ranges 40–85%).

This is the one judge output worth using, and only framed **strictly as a within-deck audit of TreeSim's absolute level** — never as a cell comparison, since the judges cannot rank cells reliably (F32). It is direct evidence for the non-uniqueness / common-mode argument already in all four drafts: TreeSim's absolute level is depressed for everyone, which is why the contrast survives and the level does not mean much.

Also for the record: B chose F6 (S+X) as "best combo" on held-out mean 0.7814 and seed sd 0.0018, **decided before any judge call**, and declined to switch to F4 afterwards even though F4 is the less circular cell — correctly refusing a post-hoc choice.

### F36 · F · ⚠⚠ **Hook telemetry answers gep1's S/X question mechanistically — better than the ablation does** (07-26 22:5x)

Verified in `scripts/launch_autocamp_phase2.sh:41-53, 64-73, 79-90` and confirmed by a second independent search agent (global counts matched exactly: 1571 `allow/xml_clean`, 88 `parse_error`, 83 `no_xml`, 80 `schema_error`; zero blocks in all 14 dsv4 cells triple-confirmed).

**On val the stop hook never intervened — 0 interventions in 410 invocations — for two distinct reasons:**

1. **S-without-X cells (F2, F3) ran with `GEOS_HOOK_XMLLINT=0`**, so the hook did parse-checking only. Documented at `tex:312`, but it means **the S treatment is not constant across cells**: S alone = parse-check; S+X = parse + schema check. This is a sharper and more concrete statement of the construct overlap than the paper's own §3 wording.
2. **S-with-X cells (F6, F7, F8, SE) had schema checking active and it still never fired**, because the agent had already self-validated mid-turn via `mcp__xmllint__validate_geos_xml` (~3 calls/task, `tex:141`).

**On held-out-eval the hook fired 32 times in 123 invocations.** So S is *not* redundant on the hard tail.

**This converges with three other threads on the same conclusion, from four independent directions:**

| thread | evidence | says |
|---|---|---|
| B (F31) | clean-subset null: no metric separates cells where all are schema-valid | effect is failure-driven |
| D (F9) | bootstrap CI on mean lift straddles zero | mean lift not established |
| C (F25) | `n_failed = 0` in all 21 val build-up run-cells | nothing to prevent on val |
| **F (this)** | **0 hook firings in 410 val invocations vs 32/123 on held-out** | **the mechanism is literally inactive on val** |

The defensible two-part claim: **on in-distribution tasks the agent's own validator makes the hook redundant; on the hard tail the hook catches what self-validation missed.** That is a *better* answer to gep1 than the build-up deltas, because it is mechanistic rather than a difference of two noisy means — and it reconciles the two conditionals that looked contradictory ("X adds nothing given S" from C6→C7; "S adds nothing given X" from the telemetry). On val they are **substitutes**; on the hard tail they are not. gep1's Q2b rewritten accordingly.

### F37 · F · The worked repair example for kEdh, and one to avoid (07-26 22:5x)

**Use `A2`:** a complete two-stage repair that **succeeded in 45 s** on `deepseek-v4-flash` on a paper **held-out-eval** task. Ledger is three lines: `block/parse_error` → `block/schema_error` → **`allow/xml_clean`**. Unparseable → fixed → schema-invalid → fixed → clean stop. Ideal: real, short, on the paper's own backbone and split, and it shows the mechanism working end to end.

**Do NOT use `B3`** (the buckleyLeverett candidate): its ledger ends `allow/schema_error_max_retries` — **the repair failed.** It was originally offered as a fallback and would have been presented as the hook working. Caught by F's second agent on re-check.

Third instance exists in a cell literally named `autocamp_SE` (cross-model gemini, `ExampleMandel`, block → allow in 17 s) — the only one whose cell name *and* model both appear in the paper (`tex:424/438`) — but its message is 3,224 chars dominated by raw XSD regex facets, unreadable at the length kEdh's response can afford. Keep in reserve for Phase 2 if challenged.

Hook registration source for the record: `plugin/hooks/hooks.json:4-15`, with a separate `PostToolUse` hook at `:16-27`.

### F38 · A2 · ⚠⚠ **The execution-level rescue does NOT survive. Do not claim it.** (07-26 23:0x)

A2 found and fixed **three bugs in its own harness — all of which had biased toward our claim** (a deck-copy that deleted agent-authored `tables/*.geos`; a strict-parser injector; L2 cascading from L0/L1 without ever invoking `geosx`). After the fixes:

Vanilla reaches clean convergence on the hardest rescue task at **2/3 seeds, not 1/3**. Against SIGA's 12/15 (80%) that is **indistinguishable at n=3**.

My earlier report of "Vanilla 1/3 vs adapters 3/3 — first execution-level evidence for the paper's central claim" came from A2's pre-fix table and **is retracted.** I checked: it never entered any draft, so nothing needs unwinding in the responses — but it is exactly the failure mode the sprint is meant to catch, and it was caught by A1 auditing A2 rather than by either agent alone.

Also retracted: my earlier "the ceiling control worked — execution outcomes are identical where TreeSim is at ceiling." **The opposite is true** (F39). Both oddities I flagged to A2 on that task were its own bugs.

### F39 · A2 · ⚠⚠⚠ **THE STUDY'S REAL RESULT: TreeSim never reads the files that set the physics** (07-26 23:0x)

On the ceiling-control task, where **every cell scores TreeSim 0.963–0.999**, **11 of 17 runs differ from the reference by 40–99%** on the primary quantity of interest.

Verified mechanism: these simulations are driven by tabulated property data in separate **non-XML** files (`tables/*.geos`) that the agents author, and **TreeSim compares XML only — it never opens them.** The two runs whose tables are byte-identical to ground truth reproduce it at exactly **0%** error. **A deck scoring 0.999 sat on a 99% error in peak pressure.**

Three corroborating specifics, each independently quotable:
- **Convergence is not correctness:** `F8_s1` is L4-clean — every solver tolerance met — and **99.97% wrong**, on a 16-cell mesh.
- **Schema-valid is not loadable:** one deck declares `ElasticIsotropic` with no elastic constants. TreeSim 0.99, schema-valid, GEOS refuses it.
- On ThermoPoro the QoI errors take only **three distinct values** — 0.00%, 10.47%, 99.97% — so the declared 10% tolerance falls *between* clusters and does all the work. At ≤15% every cell reaches ≥2/3. **Tolerance-sensitive; disclose the threshold whenever the number is quoted.** Exact reproduction: SE 2/3, Vanilla 1/3, F11 1/3, others 0/3.

**This is a limitation of the paper's instrument, not just of this study, and it cuts toward the AC's position rather than away from it.** It is also the single best answer available to "does structural improvement translate to valid simulation?" — the honest answer is no, *and here is precisely why*. Folded into gep1 post 2, AC post 2, and nBNe.

Method quality is good: preference option (a) — identical injected `<VTK>` and final-time event in reference *and* generated decks, then mesh-independent reductions (min/max/mean/L2), **no interpolation anywhere**. Every exclusion and cap applied identically to reference and generated; the two asymmetries A2 introduced were caught and removed; `maxTime` reduction never invoked.

### F40 · A2 · Reference-deck gate, and GEOS is bitwise deterministic (07-26 23:0x)

| task | usable for rungs 4–5? |
|---|---|
| ThermoPoroElasticWellbore (`_smoke`) | **yes, fully** — reference L4 clean in 3.5 s |
| ExampleProppantTest (`_benchmark`) | **L0–L3 + L5 only** — reference itself needs 10 retried timesteps (reproducible), so its absolute L4 is uninformative |
| ViscoExtDruckerPrager | **yes** — ceiling control, reference L4 clean in 10 s |
| ExampleMCCWellbore | **no** — reference hits the 600 s cap at t=0.75/1.0. Excluded on reference behaviour alone |

**GEOS verified bitwise deterministic** — 16/16 statistics identical across two runs — which justifies one run per deck and independently supports the "deck is a sufficient statistic" framing used in all four responses.

Selection rule returned exactly the pre-registered pair (ThermoPoro 0.355→0.761, ProppantTest 0.541→0.825). A2's first pass got it wrong via the `*_eval.json` glob trap (F17) and reproduced 0.541 exactly after switching to `_summary.json`. Its cell means match Thread D to 4 dp.

**Proppant rung-5 is provisional** (pre-fix pass, flagged `qoi_provenance`) — **do not quote it** without a re-run. → **H18**.

### F41 · main · ⚠⚠⚠ **ANSWERED: the flagship catastrophic failure LOADS FINE in GEOS.** (07-26 23:1x)

I ran the blocking question myself rather than wait on A1. `F0/s3/ExampleProppantTest` — the **single zero-score run on the entire held-out split**, and the **sole cause of Vanilla's σ = 0.081**, hence the numerator of the paper's "≈40×" variance-reduction claim:

```
inputs/: ProppantSlotTest_base.xml, ProppantSlotTest_benchmark.xml
benchmark.xml: <Included><File name="./ProppantSlotTest_base.xml"/></Included>

xmllint --noout benchmark.xml  -> parser error: Double hyphen within comment
geosx -v -i benchmark.xml      -> exit 0      <-- THE ROOT DECK LOADS
geosx -v -i base.xml           -> exit 1 (numberOfMeshBodies == 0)  <-- expected; it is a fragment
```

The offending text is a **prose double hyphen in a title line**: `Proppant Slot Test -- Base Case`.

**So the paper's flagship catastrophic failure is a metric artifact.** Our scorer's XML parser rejects a deck that GEOS accepts. The σ = 0.081 figure and the variance-reduction claim built on it are real facts *about our metric*, but the natural reading — "Vanilla sometimes emits a deck that cannot be used" — is **not supported for this instance**.

Honest framing available, and I think defensible: the decks *are* invalid XML per the specification and would break any spec-compliant consumer, so this is a **portability defect** rather than an execution failure. That is a real defect, just a smaller and different one than the paper implies. → human decision **H19**, and it is now the most consequential open item in the sprint.

### F42 · main · ⚠⚠ **A1's rung-3 numbers are probably undercounting Vanilla — same parser asymmetry** (07-26 23:1x)

Testing all three Vanilla seeds of that task on the **root deck only**:

| seed | xmllint | `geosx -v` on benchmark.xml |
|---|---|---|
| s1 | OK | **exit 1** — `m_defaultComponentDensity.size() != NC` (genuine authoring error) |
| s2 | OK | exit 0 |
| s3 | **fails** | **exit 0** |

That is **2/3**, but A1's per-task table reports ProppantTest F0 at **1/3**.

Diagnosis (sent to A1 to confirm): A1 already documented that *"F0 has 47 roots because unparseable files break `<File>` reference detection."* When ElementTree cannot parse `benchmark.xml`, the harness never sees its `<Included><File>` edge, so `base.xml` is misclassified as a **root** instead of a fragment — and the AND-over-roots rule then fails the task-run on a file never meant to load standalone. GEOS resolves the include and exits 0.

**The adapter cells have no unparseable files, so this bug can only hurt Vanilla — meaning it inflates our own reported advantage.** The rung-3 gap of 18/30 vs 23/30 currently sits in three draft responses and must be treated as **provisional** until A1 re-derives it with GEOS-tolerant root detection (recover the include graph by regex or a lenient parser). Requested, along with the corrected table for all six cells and an explicit statement of whether the *direction* changes.

**Standing lesson, and it is the sprint's clearest methodological result:** every harness bug found so far — three in A2, one suspected in A1 — biased **toward** our own conclusion, and in each case it was a *different thread's independent measurement* that caught it, not the owning agent's self-checking. A2 said this itself unprompted. Any single-thread execution number here should be treated as provisional until cross-checked, and a larger campaign before Aug 3 must keep the redundancy.

### F3 · P0 · ⚠ Precision trap for drafting: M is rounding-sensitive (07-26 22:1x)

| effect | full precision | from Table 1's printed 3-dp means |
|---|---:|---:|
| R | −0.03676 | −0.03675 |
| S | −0.00772 | −0.00775 |
| X | +0.01146 | +0.01125 |
| **M** | **+0.00870 → +0.009** | **+0.00825 → +0.008** |

**Quote M = +0.008.** gep1 recomputes things, and he will recompute from the eight printed cell means. Our arithmetic must match his. Full-precision M is +0.0087 if asked; it changes nothing.

---

## Open questions for the human

| # | Question | Source |
|---|---|---|
| H1 | Include the OpenFOAM n=30 reversal? (Vanilla coverage 3/5 → 30/30, S +0.328 → +0.168, M +0.192 → −0.007) | sprint prompt "Escalate"; `SIGA_weaknesses_and_responses.md` Q3 |
| H2 | R2 / clarity posture — how hard to commit to the camera-ready rewrite in writing | sprint prompt; Q1 |
| H3 | Volunteer the main-effects correction? | sprint prompt; Q4 |
| H4 | Is the arXiv version publicly posted? (governs verbatim quoting vs paraphrase) | Q6 |
| H5 | Pre-empt the human-baseline anomaly (one expert 0.812 → 0.689 between sessions) or wait to be asked? | Q5 |
| H6 | Include LAMMPS (preliminary, judge-family flaw) for nBNe + AC scale bullet? | Q2 |
| **H7** | **Disclose the Table 5 `bad_attribute_value` error proactively?** The table prints 0 for SE and SE-prose where artifacts say 4 and 3 — read literally it contradicts the paper's own central thesis, and it is discoverable from the table alone. My recommendation: **disclose**. It costs almost nothing, the artifacts support our thesis while the table undermines it, and being second to our own error here is much worse than volunteering it. | finding F8 |
| **H8** | **Volunteer the bootstrap CIs?** The AC asked for uncertainty estimates. The honest task-clustered interval on the mean-lift contrast is [−0.0085, +0.1663], P(Δ≤0)=0.052 — it straddles zero. My recommendation: **yes, but lead with reliability** (σ ratio and 1/30 vs 0/30 zero-score runs, where no CI is needed) and present the CI as the reason for that framing rather than as a buried caveat. Refusing the AC's explicit request is worse than an honest wide interval, and the reliability claim survives it intact. | finding F9 |
| **H10** | **Disclose the `missing_external_asset` harness bug?** It is the largest rung-3 failure category (32/273) and it penalises the adapter cells harder than Vanilla, so it biases *against* our own claim. My recommendation: **yes, and use it** — it justifies the authoring-only denominator and it is the kind of self-caught fairness bug that buys credibility cheaply. | finding F19 |
| **H11** | **How hard to state the rung-5 negative?** L5 = 0/3 for every cell on both rescue tasks: structural gains do not translate to matching QoI. The AC made execution the decision criterion, so this is the most consequential number in the sprint. My recommendation: **state it plainly and early**, paired with the rung 2–4 rescue confirmation, and use it to justify the narrowed "structural authoring reliability, not validated correctness" claim gep1 already asked for. Burying it is the one move that could lose the paper outright if a reviewer reproduces it. | finding F21 |
| **H18** | Re-run `ExampleProppantTest` rung-5 QoI? A2 flagged it `qoi_provenance` (pre-bug-fix pass). **Do not quote it without a re-run** — though J2's 6-task SOF study now supersedes it as the output-side instrument. | F40 |
| **H19** | ⚠ **How far to walk back the reliability framing?** The flagship σ = 0.081 run is a metric artifact end to end — it loads in GEOS (exit 0), runs to completion, and reproduces the reference physics exactly (SOF = 1.0000). Recommendation: reframe as **portability defects, not execution failures**; drafted that way. | F41, F49 |
| **H20** | ⚠ **How to pitch the Q2b concession to gep1?** His stated bar was "confidence would increase if the stop-hook effect remains dominant after removing this confound." **We can no longer claim dominance on the hard tail** — the hook never fires on either split when X is present. Recommendation: pair the concession with the diagnosis (the chosen validator could not see the defects GEOS catches) plus the proposed fix. | F43 |
| **H21** | Spend ~$0.52 on a corrected-root-rule re-run of the J3 treatment arm? It separates "the bad root rule caused the fabrication" from "in-loop validation induces fabrication generally." Costed, **not launched**. | F45, F46 |
| **H22** | **Volunteer ρ ≈ 0.40 (TreeSim vs simulation-output fidelity)?** Recommendation: **yes**, with the per-task range (0.11–0.83) and the aggregator sensitivity. It answers the AC's decision criterion with a real instrument. | F48 |
| **H23** | ⚠ **Correct A2's published CSVs before quoting them.** Stale by 2 of 38 records; both corrections run *against* A2's failure counts. Not optional if any A2 number reaches a reviewer. | F49 |
| **H24** | Disclose that `ExampleIsothermalHystInjection`'s **ground truth cannot run** (its top deck includes a file absent from the GT tree)? Affects what "similarity to ground truth" means for that task. | F48 |
| **H25** | Which reliability statistic to report for the judge — **α = 0.391 or Gwet's AC1 = 0.811**? α collapses under 74–94% single-label prevalence (kappa paradox); raw agreement is 70.3%. Recommendation: **report both**, phrased as "chance-corrected reliability cannot be established on this label distribution," never "the judges disagreed." | F50 |
| **H26** | **Ship the per-section TreeSim audit table without the cell score table?** Recommendation: **yes** — it audits the metric, not the systems, so it does not depend on the judge discriminating cells (which is what failed). | F50 |
| **H27** | **Ship the zero-LLM execution argument?** 10 decks, **0 of 10 load**, yet TreeSim scores them 0.840 — above the 0.763 held-out mean. Recommendation: **yes**; strongest available demonstration that an input-side metric cannot answer the execution objection. | F50 |
| **H28** | **Fix `_bipartite_match` for camera-ready?** A 3-line deterministic change lifts the unmatched-section subgroup 0.661 → 0.727 and rung-3 AUC 0.803 → 0.830 — **more than the $12.70 four-judge panel delivers, free.** Re-scoring moves every number in the paper, so: **disclose now, fix for camera-ready, report both.** | F50, and H16 |
| **H15** | **Ship the LMaaJ table? Recommendation: NO.** It fails four pre-registered reliability checks, and one judge reverses the paper's central contrast. Report it as an instrument we built, tested and rejected — that is credible and costs nothing. Shipping it hands a reviewer a fifth weakness. | finding F32 |
| **H16** | **Disclose the TreeSim subtree-annihilation defect? Recommendation: disclose, do NOT fix.** Re-scoring would change every number in the paper mid-response. It affects 34% of held-out decks and is worst for SE, so it biases *against* us. Also decide whether to correct the paper's "hallucinated `gravityVector`" reading, which this shows to be a metric artifact rather than an authoring error. | finding F33 |
| **H17** | **How to handle the clean-subset null.** On runs where every cell is schema-valid, neither metric separates the cells (all Δ within ±0.014, all p ≥ 0.85) — the entire separation is catastrophic-failure-driven. My recommendation: **volunteer it**, because it converts the paper's own qualitative claim into a measured one and gep1 already praised that framing. It does, however, require dropping any "mean quality improved" reading, including the abstract's "+7 pp" phrasing. | finding F31 |
| **H12** | The SE-vs-SE-prose footnote: the "0.004 against a 0.022 gap" phrasing does not survive (the whole gap is one unscorable run under failures-as-zero; ≈0.003–0.005 under scored-only). Name the convention, drop the footnote, or reframe. Drafts currently take the third option. | finding F26 |
| **H13** | Correct `.copilot/reviews/RN-006:343`, the origin of the "+0.24" error? Left unedited as an immutable audit artifact. The `000b4ba` commit message carries it too and cannot be edited. | finding F28 |
| **H14** | Is "stripping the workflow primer is worth +0.19" still a claim we want anywhere? The C0→C2 comparison changes primer *and* plugin together, so the decomposition is not clean. | finding F30 |
| **H9** | If H3 publishes the correction, **§5.1's "X, M and S all fall within ±0.007" must be addressed in the same breath** — it is false under the corrected effects and it is the sentence licensing "don't add RAG; the rest doesn't matter." Decide whether to rewrite it in the response or simply flag it for camera-ready. | finding F10 |

---

## Timeline

| Time (UTC) | Event |
|---|---|
| 07-26 21:49 | Sprint prompt received |
| 07-26 21:57 | Read the five briefing docs + both track specs; verified GEOS binary and all four data locations; sprint scaffolding created |
