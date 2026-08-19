# SIGA follow-up, subgoal (3): which harness-evolution method should we reimplement?

**Date:** 2026-08-19
**Scope:** Technical basis for the SIGA follow-up. Decision document + implementation plan.
**Paper:** SIGA, arXiv:2606.09774 ("Auto-Configuring Scientific Simulators with Lightweight Coding-Agent Adapters").
**Filed here** rather than `.copilot/decisions/` because it is an analysis + plan, not a single decision;
`.copilot/decisions/D-011` points at it. Naming follows the `docs/YYYY-MM-DD_slug.md` convention.

---

## 0. TL;DR

Three things, in order of how much they should change what we do.

1. **The self-evolution loop never received a reward signal.** `run_full_evolution.sh` runs a round and
   then calls `reflect.py` with no scoring step in between; scoring lives in a separate
   `scripts/eval/batch_evaluate.py` invocation that is never made. Every `.reflection_meta.json` in
   `plugin_evolving/v1..v3` records `"round_mean_treesim": 0`. The proposer's prompt therefore read
   *"RECENT ROUND RESULTS (mean treesim 0.0000, n=7)"* with every task line rendered `(treesim N/A)`.
   Eq. (2)'s `argmax` is not weakly approximated — there is no reward anywhere in the loop.
   This is a strictly stronger version of the "no selection" concern.

2. **The paper's own table already shows self-evolution contributed nothing measurable.**
   SE, SE-prose and S+X+M are all the same cell shape (S+X+M, `--disallowedTools Skill`).
   On held-out-eval: S+X+M `0.783 ± 0.022`, SE `0.789 ± 0.012`, SE-prose `0.775 ± 0.024`.
   The headline `+0.069` is `Vanilla → S+X+M` (`+0.063`, the *hand-designed* adapter) plus `+0.006` of
   noise. The entire measured effect of three rounds of self-evolution is `±0.008` against `σ ≈ 0.02` at
   `n = 3`. arXiv:2607.12227's compute-matched critique does not need to be run to sink the SE claim;
   the existing table sinks it. See §4.4.

3. **The two "novel method" candidates I was asked to evaluate hardest are already half-built, and one
   of them is a live contamination hazard.** `geosx --validate-input` (merged in PR #1, commits
   `ffef61b`/`b1666c7`) already catches unknown attributes with the full valid-attribute table inline,
   hallucinated element tags, and load-time dangling cross-references — i.e. most of "attribute-level
   oracles" and all of "cross-section consistency validation" are *engineering already done*, not method.
   Separately, `plugin_evolving/v4/memory/cheatsheet.md` is a task-name → ground-truth-adjacent-XML
   lookup table covering all 17 validation tasks, and it is wired into `scripts/launch_autocamp_v4.sh`.
   It is **not** the paper's SE (SE = v3), so published numbers are unaffected — but it is a loaded gun
   in the tree. See §1.9 and §7.5.

**Recommendation (§8):** rebuild the loop as **SIGA-Evolve v2** = Self-Harness's regression gate +
AHE's three observability pillars + GEPA as the outer-loop library (Pareto archive, budget tracker,
acceptance criterion), with the search space widened from prose to a declarative, schema-checked
adapter manifest and unit-tested check plugins. Run one cheap de-risking experiment first
(§8.2). Do **not** build a DGM/Hyperagents-style open-ended archive over the full harness program (§8.3).

---

## 1. Assessment of the current loop

### What `reflect.py` + `run_round.sh` actually implement

In 2026 vocabulary: a **three-step linear prompt-rewrite chain with no reward channel, no selection
operator, no archive, no attribution, and a fixed prose-only action space.** It is not an instance of
harness evolution as arXiv:2603.28052 / 2604.25850 / 2606.09498 define it — those all require at
minimum (proposal → evaluation → retention decision), and this loop has no evaluation edge.

The mechanism is closest to a *degenerate single-pass ACE* (arXiv:2510.04618): a reflector that reads
an execution summary and a curator that full-rewrites the context, but missing ACE's two defining
features (the grounded reflection signal and the incremental itemized delta update). It is exactly the
configuration ACE names as the collapse-prone one.

### 1.1 Confirmed: no selection *(stated weakness #1 — confirmed and worse)*

`reflect.py:284-296` unconditionally seeds `v{N+1}` from `v{N}` and `reflect.py:337` overwrites with
whatever the proposer emitted. The only rejection paths are `reflect.py:332` (no `<file>` blocks →
inherit), `reflect.py:236` (path traversal), `reflect.py:240-243` (path allowlist). There is no
accept-if-better gate, no regression check, no rollback, no re-evaluation of the parent.

**Worse than stated.** The loop had no reward to gate on even if a gate existed:

- `run_round.sh:59-73` invokes `scripts/run_experiment.py` only. `src/runner/cli.py` contains no
  scoring path (`grep -n "treesim\|batch_evaluate" src/runner/*.py` → no hits). Per-task
  `<task>_eval.json` files are written **only** by `scripts/eval/batch_evaluate.py:68`.
- `run_full_evolution.sh:24-45` alternates `run_round.sh` and `reflect.py` with no scoring call between.
- `reflect.py:104-128 gather_round()` reads `treesim` from `_results/<run>/abl_se_round/<task>_eval.json`.
  Those files did not exist at reflect time, so `treesim` was `None` for every task,
  `treesims` was empty, and `reflect.py:312` set `mean_ts = 0`.
- Corroborated on disk: `plugin_evolving/v1/.reflection_meta.json`, `v2/`, `v3/` all record
  `"round_mean_treesim": 0`. (`v1` also records `"round_n_tasks": 7` for a 6-task round — see §1.8.)

The consequence compounds. `reflect.py:196-197` instructs: *"If the current plugin is already working
well (≥0.85 mean treesim), it's fine to make small additions or no changes."* With `0.0000` rendered,
that branch never fired; the proposer was told it was failing catastrophically at every round and
responded by adding content monotonically:

| version | `PRIMER.md` | `memory/cheatsheet.md` |
|---|---|---|
| v0 | 270 B | — |
| v1 | 1 883 B | 2 838 B |
| v2 | 2 488 B | 4 843 B |
| v3 | 3 159 B | 4 526 B |

This is textbook over-specification — the exact failure mode the paper's efficiency paragraph
(§5.3) claims SIGA guards against. It also plausibly explains the measured `missing_block ↓ 6→3 /
extra_block ↑ 9→11 / hallucinated_extras ↑ 4→7` trade: an always-on artifact that grew 12× while
being told nothing about which of its additions helped.

### 1.2 Confirmed: linear chain, no archive *(weakness #2)*

Single lineage `v0→v1→v2→v3`, one proposer call per reflection (`reflect.py:329`), 3 reflections.
No population, no branching, no re-selection of an earlier candidate, no candidate metadata beyond
`.reflection_meta.json`. Compare GEPA's `GEPAState.program_candidates` + `ParetoCandidateSelector`
(`~/code_ref/gepa/src/gepa/strategies/candidate_selector.py:11`), or DGM's archive.

### 1.3 Confirmed: each round is a different task slice *(weakness #3)*

`run_full_evolution.sh:17-19` splits 17 tasks into disjoint 6/6/5 thirds. Round-over-round score
changes confound adapter quality with task difficulty. The only head-to-head is round 3
(`run_full_evolution.sh:49`, v3 on round 0's tasks) — and since scores were never computed at reflect
time, that comparison could not have influenced the search either.

### 1.4 Confirmed, and the fix is nearly free: the evidence is extremely thin *(weakness #4)*

`reflect.py:69-101 trajectory_summary()` emits a `2500`-char list of tool names with truncated
arguments (`R: <path>`, `B: <cmd[:80]>`, `GR: <pattern[:60]>`, everything else `Name: ...`). No
observations, no errors, no diffs, no validator output, no failure classification, no per-section
scores. In AHE's vocabulary this is a total absence of *experience observability*.

**But the repo already has the replacement.** `scripts/bottleneck/extract.py:278
diagnostic_for_task()` returns, per (agent, run, task): `treesim`, `section_scores` (per_section over
`treesim_detail`), `worst_subtrees(k=8)`, `missing_element_types`, `extra_element_types`,
`gen_n_extra_top`, mined trajectory features (`mine_trajectory`), a 10-turn tail excerpt
(`trajectory_excerpt`), and `status`. `src/eval/judge_geos.py` already emits `treesim_detail`
(`judge_geos.py:756`) and `tree_sim_section_scores` (`judge_geos.py:539`). The per-task LLM failure
classifier is at `scripts/bottleneck/llm_per_task.py`.

So AHE's pillar (2) is a **wiring job of roughly a day**, not a reimplementation. That materially
changes the cost calculus in §6.

### 1.5 Confirmed: prose-only search space *(weakness #5)*

`reflect.py:240-243` allows exactly `PRIMER.md`, `memory/`, `skills/`, `agents/`.
`reflect.py:257-263 copy_scaffolding()` copies `hooks/`, `scripts/`, `.claude-plugin/` verbatim as
untouchable. The loop therefore cannot modify S, X, or R — the components the paper's own ablation
identifies as dominant (S on GEOS/OpenFOAM; M/R on LAMMPS).

AHE's ablation is a direct indictment: it localizes its gain to *"tools, middleware, and long-term
memory rather than the system prompt,"* concluding *"factual harness structure transfers while
prose-level strategy does not."* SIGA searched only the half AHE says does not transfer, which is a
coherent — and testable — explanation for `SE-prose (0.775) < S+X+M (0.783)`.

### 1.6 Confirmed: proposer = inference model *(weakness #6)*

`reflect.py:55 MODEL = "deepseek-v4-flash"`, the same model used for rollouts
(`run_round.sh:72 --claude-model deepseek-v4-flash`). The paper deliberately avoided this when
distilling M offline (used `gemini-3-flash-preview` "to avoid self-distillation").

**I think this one is second-order and you were right to flag it as such.** arXiv:2605.30621 finds
harness-*updating* is flat in base capability (Qwen3.5-9B ≈ Claude Opus 4.6) while harness-*benefit*
is non-monotonic and peaks mid-tier. So the proposer's identity likely costs us little. It is still
worth changing because it is free and it removes a reviewer objection — but it is not the reason SE
did not work.

### 1.7 Confirmed and understated: hygiene is a regex *(weakness #7)*

`reflect.py:248-249`: `re.sub(r"\b([a-z0-9_][a-z0-9_\-]*\.xml)\b", "<file>", body, re.IGNORECASE)`.
`scripts/memory/hygiene_audit.py:41` uses the identical `.xml`-only pattern, so the durable audit gate
has the same blind spot. Three gaps, one of which fired:

- **`.geos` is not matched, and v3 — the shipped SE — leaks it.**
  `plugin_evolving/v3/skills/triaxial-driver-setup.md` contains `tables/time.geos`,
  `tables/radialStress.geos`, `tables/axialStrain.geos`; `v3/skills/copy-dependencies.md` and
  `v3/agents/dependency-copier.md` contain `tables/time.geos`. These are ground-truth *dependency*
  filenames for the triaxialDriver task family, mined from trajectories and passed straight through
  the gate. Severity: **moderate, not fatal** — the `.geos` tables live in the readable example tree
  and are not on the contamination blocklist (`src/runner/contamination.py` blocks GT XML basenames,
  variant siblings, and the source RST). But it is a leak past a gate the paper asserts is closed,
  and it was in the artifact that produced the reported SE number.
- **Directory paths survive.** `poromechanics/PoroElastic_Mandel_base.xml` → `poromechanics/<file>`;
  the physics-family directory name is preserved.
- **Content leaks are not addressed at all.** The regex is a filename filter, and only for `.xml`.

### 1.8 Confirmed: hardcoded paths — plus two more *(weakness #8, extended)*

`reflect.py:49` `REPO_ROOT = Path("/home/matt/sci/repo3")`; `reflect.py:51` and
`analyze_evolution.py:20,22` point at `/data/shared/geophysics_agent_data/...`;
`run_round.sh:12` and `launch_icl_v0_v3.sh:8` `cd /home/matt/sci/repo3`.

**Neither path exists in the current environment** (`/data` is absent; the repo is at `~/repo3`).
Everything in §1.1 is therefore established from committed artifacts (`.reflection_meta.json`,
plugin contents, script source), not from re-running the pipeline. I could not inspect any
`events.jsonl` or `<task>_eval.json`; where a claim depends on run logs I say so.

Two additional path-shaped bugs:

- `reflect.py:113` iterates **every** subdirectory of the run dir as a task. `v1`'s meta records
  `round_n_tasks: 7` for a 6-task round, so at least one non-task directory (a `_logs`-style sibling)
  was fed to the proposer as a task with `treesim N/A`.
- `run_round.sh:29-38` builds a `CHEATSHEET_ARG` that is computed and then never used
  (`run_round.sh:65` passes `--geos-primer-path "$EFFECTIVE_PRIMER"` instead). Harmless, but it means
  M and the primer are **concatenated into a single blob** at `run_round.sh:43-50`; the evolving
  lineage has no separable M. That matters for §3 (we want M as its own budgeted component).

### 1.9 New findings

**(9) `analyze_evolution.py:67` is a runtime-broken f-string.**
`f"...{d.get('round_mean_treesim','?'):.4f if isinstance(...) else ...}"` — a conditional expression
is not a valid format spec. It raises `ValueError` on every line, and the bare `except Exception: pass`
at `analyze_evolution.py:70-71` swallows it, so `render_evolution_log()` always returned an empty
string. The one report that would have printed `round_mean_treesim = 0` to a human never rendered.
Verified by isolating the expression:
`ValueError: Invalid format specifier '.4f if isinstance(...)' for object of type 'float'`.

**(10) The evolving lineage's scaffolding is a stale fork of `plugin/`.**
`copy_scaffolding()` froze `hooks/` and `scripts/` at v0 and they have since diverged:
`diff plugin/hooks/verify_outputs.py plugin_evolving/v3/hooks/verify_outputs.py` → 274 lines;
`grep -c geosx` → `plugin/hooks/verify_outputs.py: 18`, `plugin_evolving/v3/hooks/verify_outputs.py: 0`
(same for `xmllint_mcp.py`: 17 vs 0). Re-running `run_round.sh` today would evolve an adapter against
the **retired `xmllint --schema` validator**, not the `geosx --validate-input` one the repo now ships.
Any v2 loop must resolve scaffolding from `plugin/` at run time rather than snapshotting it.

**(11) `plugin_evolving/v4` is a contamination hazard and was not produced by `reflect.py`.**
`v4/memory/cheatsheet.md` (8 624 B vs v3's 4 526 B) opens with:

> `**Read the listed file(s) FIRST. Do not Grep/Glob to find them — they are already verified.**`
> `| Task name keyword | Canonical XML(s) under /geos_lib/inputFiles/ |`

followed by a row for **each of the 17 validation tasks**, naming files such as
`poromechanics/PoroElastic_Mandel_prism6_base_hybrid.xml`,
`compositionalMultiphaseFlow/benchmarks/buckleyLeverettProblem/buckleyLeverett_base.xml`,
`hydraulicFracturing/pknViscosityDominated_poroelastic_base.xml`.

It cannot have come from `reflect.py` — the `.xml` hygiene regex would have replaced every one of
those with `<file>` and logged the count. Consistent with that, `v4/.reflection_meta.json` is a
byte-identical copy of v3's (it still says `"version": 3, "parent": 2`), i.e. v4 bypassed the
reflection path entirely. `scripts/launch_autocamp_v4.sh:3` describes it honestly as "trajectory-mined
task→canonical XML" and `:56` wires it in as `--plugin-dir plugin_evolving/v4`.

**This did not reach the paper.** SE = v3, per `scripts/efficiency_table.py:234`
("SE uses `plugin_evolving/v3`") and `scripts/self_evolving/launch_icl_v0_v3.sh` (the held-out-eval
transfer run compares v0 vs v3 over exactly the 10 held-out tasks). But v4 exists, is launchable, and
would produce a near-oracle number if anyone re-ran that script. Under arXiv:2607.22368's framing it
is a textbook *exposure*: a memory artifact that hands the agent the answer key's neighbours.
**Action: quarantine before any new work (§7.5).**

**(12) The validator has already moved past the paper.** `docs/GEOSX_VALIDATE.md` (branch merged in
PR #1) documents S and X now running `geosx -i <entry> --validate-input` instead of
`xmllint --schema`. Verified against the real binary, it catches:
unknown attributes (*"contains unused attribute 'X'. Valid attributes are: [full table]"*),
hallucinated element tags (*"All available tags are: [~50 valid solver types]"*),
and load-time dangling name references (`targetRegions` → renamed `CellElementRegion`).
Residual confirmed gap: references resolved lazily past the load phase
(`discretization="TPFA_DOES_NOT_EXIST"` passes). This substantially pre-empts the paper's
recommendation (iv) and the "cross-section consistency hook" future-work item. See §5.4.

### 1.10 Where I think the brief overstated the case

- *"The paper's `argmax` is realized only as post-hoc reporting of a selected variant."* — not even
  that. v3 is not a *selected* variant; it is simply the last link in the chain. No variant was ever
  compared to another.
- *"SE was selected on a held-out split and reported on held-out-eval."* — the splits are actually
  clean. Per §5.2 of the paper, the 46-task pool is partitioned 10 held-out-eval / 18 distillation /
  17 validation-selection; evolution ran on the 17 (`run_full_evolution.sh:17-19`), reporting on the
  10 (`launch_icl_v0_v3.sh:14-25`), disjoint. So arXiv:2607.12227's *second* concern (search and eval
  share a benchmark) does **not** apply to SIGA. Its *first* concern (no compute-matched baseline)
  applies in full. Being precise about this matters: it's the difference between a fixable omission
  and a design flaw.

---

## 2. Ranked shortlist

All arXiv IDs below were fetched and confirmed against the abstract page on 2026-08-19; titles and
claims match the review files. No miscitations found in the candidate set (28/28 verified).

### #1 — Self-Harness (arXiv:2606.09498) — *the regression gate*

**What it does.** Three stages: *Weakness Mining* (model-specific failure patterns from execution
traces) → *Harness Proposal* (diverse but **minimal** modifications tied to specific failures) →
*Proposal Validation* (accept only after regression testing). Nine model×benchmark cells, up to 132%
relative gain, improving **held-in and held-out**.

**Why it fits this bottleneck.** It is the smallest change that converts §1.1's unconditioned
rewriting into actual search, and each of its three stages maps onto a specific SIGA pathology:
- *minimality* is the direct antidote to the 12× monotone growth in §1.1, and it is the only
  proposal discipline compatible with M being a 775-token always-on artifact under a hard efficiency
  constraint;
- *regression testing* is what a reliability-limited, tail-driven objective actually needs — when the
  gain is two rescued tasks and everything else is noise, "did the mean go up" is the wrong question
  and "did any task fall off a cliff" is the right one;
- *model-specific weakness mining* is exactly the frame for our cross-model panel, where the same
  adapter is run on `deepseek-v4-flash`, `minimax-m2.7`, and `gemini-3-flash-preview`.

**Replaces.** `reflect.py:266-359 main()` — the whole propose-and-overwrite path.
**Needs that we lack.** A scored, cached, per-task evaluation callable that the loop can invoke
mid-search (today scoring is a manual shell step). An anchor task slice held fixed across rounds.
**No public implementation** (no repo linked from the abstract page) — we reimplement from the paper,
which is ~200 lines given GEPA supplies the state machine.

### #2 — Agentic Harness Engineering (arXiv:2604.25850) — *the observability pillars*

**What it does.** *Component observability* (file-level representation of every editable component →
explicit, revertible action space), *experience observability* (millions of trajectory tokens → a
layered drill-down evidence corpus an evolving agent can actually consume), *decision observability*
(every edit paired with a self-declared prediction, verified against the next round's outcomes →
every edit becomes a falsifiable contract). Terminal-Bench 2: 69.7% → 77.0% over ten iterations,
beating human-designed Codex-CLI (71.9%) and beating ACE.

**Why it fits.** Pillar (2) is our acute deficiency (§1.4) and the fix is a day of wiring because
`scripts/bottleneck/extract.py` already produces the corpus. Pillar (1) is the argument for widening
the search space beyond prose (§1.5) — and AHE's ablation *"localizes the gain to tools, middleware
and long-term memory rather than the system prompt"* is a pre-registered prediction that SIGA's
prose-only space was the wrong space, which our `SE-prose < S+X+M` observation is weakly consistent
with. Pillar (3) gives us the accept/reject audit trail and, more valuably, a cheap
over-specification detector: an edit whose predicted beneficiaries did not improve is a candidate for
reversion even if the aggregate moved.

**Replaces.** `reflect.py:69-101` (→ `extract.diagnostic_for_task`) and
`reflect.py:257-263 copy_scaffolding` (→ a manifest-driven component registry).
**Needs.** A stable component manifest and a revert path (i.e. an archive — see #3).
No public implementation; reimplement.

### #3 — GEPA (arXiv:2507.19457) — *the outer loop, as a library*

**What it does.** Reflective evolution over a candidate set with a **Pareto frontier over per-instance
scores**, sample-efficient enough to beat GRPO with ~35× fewer rollouts.

**Why it fits, and why it is not a reimplementation.** Sample efficiency is *the* binding constraint
here: 17 validation tasks, `n = 3`, ~1500 s timeout, and a cross-model panel that is already
cost-limited. GEPA is the method in the candidate set explicitly designed for that regime. And
`~/code_ref/gepa` (cloned) hands us the machinery directly:

- `gepa.optimize(seed_candidate: dict[str, str], ...)` — components keyed by name, which maps exactly
  onto `{PRIMER.md, memory/cheatsheet.md, adapter.toml, ...}` (`src/gepa/api.py:47`);
- `candidate_selection_strategy="pareto"` (`src/gepa/strategies/candidate_selector.py:11`) — Pareto
  over per-task scores is *exactly right* for a tail-driven objective: a candidate that rescues
  `ExampleProppantTest` stays on the frontier even if its mean is unremarkable, which mean-based
  hill-climbing would discard;
- `acceptance_criterion` (`src/gepa/strategies/acceptance.py:44`) — the hook where Self-Harness's
  regression gate plugs in;
- `max_metric_calls` + `cache_evaluation` — the rollout budget accounting §4 requires, for free;
- `custom_candidate_proposer` — where the AHE-style evidence-rich proposer plugs in;
- `module_selector` — one component per iteration, which is Self-Harness's minimality by construction.

GEPA also ships a `MetaHarnessEngine` (`src/gepa/oa/engines/meta_harness.py:621`) that drives a Claude
Code subprocess as an agentic proposer against an `EvalServer`. That is arXiv:2603.28052's outer loop
available off the shelf, and it is the natural v2.5 if the v2 proposer proves too weak.

**Replaces.** The `v{N}→v{N+1}` chain in `run_full_evolution.sh` entirely.
**Needs.** Our evaluator wrapped as a `(candidate) -> (per-task scores, info)` callable. That is the
single largest piece of new code (§3.2).

### #4 — ACE (arXiv:2510.04618) — *delta updates for M only, under a token cap*

**What it does.** Generator/Reflector/Curator with **structured incremental itemized delta updates**,
explicitly to prevent *brevity bias* and *context collapse*.

**Why it fits, and where I would cut it.** ACE names the two failure modes we measured. §1.1's
monotone growth is context inflation; the `missing_block↓ / extra_block↑ / hallucinated_extras↑` trade
is what an always-on artifact does when it accumulates positive assertions with no mechanism for
deletion or negative constraint. **Adopt: the itemized delta representation and the
add/update/delete/keep operator set.** **Reject: ACE's playbook scale.** M is 775 tokens, always-on,
and adapter cells must not regress wall-clock. So: a hard token budget on M, and a curator that must
delete before it can add. This is also the natural home for the negative-constraint artifact class
(§5.3). Reference implementation cloned at `~/code_ref/ace` (`ace/core/curator.py`,
`ace/core/reflector.py`, `ace/playbook_utils.py`).

**Replaces.** The full-rewrite semantics of `reflect.py:231-254` for `memory/`.
**Needs.** A tokenizer-aware budget check and an M/primer separation the current
`run_round.sh:43-50` concatenation destroys.

### Mandatory evaluation tier (not optional, see §4)

- **arXiv:2607.12227** — compute-matched baselines. Code exists (`github.com/rethinking-harness-evolution`).
- **arXiv:2605.27922 (Harness-Bench)** — report at the model×harness *configuration* level; its
  *execution-alignment failure* label is a good name for SIGA's silent-incompleteness mode.
- **arXiv:2607.22368 (HackDetect)** — post-hoc exposure audit. Given §1.9(11), not hypothetical here.
- **arXiv:2605.30621** — cheap proposer + expensive evaluator is the correct economics; and which
  *inference* model we run on partly determines the measured gain, so the cross-model panel is
  load-bearing.

### Considered and declined (with reasons)

| Method | Why not now |
|---|---|
| **Meta-Harness (2603.28052)** | The right target in principle, and it is SIGA's cited framing. But its search space is *complete harness implementations*, and the base harness is frozen by SIGA's framing (§Constraints). Available via GEPA's `MetaHarnessEngine` when we want it — I would rather earn it than start there. |
| **DGM (2505.22954) / Hyperagents (2603.19461)** | Open-ended archive search needs cheap, plentiful evaluations. Ours cost ~1500 s/task-run at `n≥3` over ≤17 tasks. Also self-modifying the modification mechanism requires unfreezing more than SIGA's framing allows. See §8.3. |
| **MCE (2601.21557)** | Two-tier meta/base is the right *eventual* shape, but it doubles the search space before we have demonstrated that searching the first tier works at all. |
| **Harness MDP / offline RL (2607.05458)** | Genuinely attractive — we have a large logged corpus and TreeSim-only scoring is a known weakness — but the paper's own caveat (process gains convert to outcome gains only under good offline coverage) plus our corpus size makes this a 2027 item. Its **Harness Maturity Score** is worth stealing *now* as a diagnostic (§4.5). |
| **SkillFoundry (2604.03964)** | Strong fit for subgoal (1)/(2) and its provenance+tests fields speak to §1.7. But SIGA runs `--disallowedTools Skill` at eval, so skills are currently untestable as skills. Sequence it after we re-enable Skill under SkillsBench's paired protocol (`≤3 modules`, arXiv:2602.12670). Cloned at `~/code_ref/SkillFoundry`. |
| **Tool-Genesis (2603.05578)** | Not a method to adopt — a **constraint** on §3.3. "Autonomous tool creation fails one-shot; interface errors compound" is why the loop authors *check plugins against a fixed interface with a required test*, not free-form validators. |
| **Retrieval-based memory (any)** | Killed locally. The `memory_lookup` MCP tool was called **zero** times across every test-set run while verified functional. Any imported method routing knowledge through an optional tool must be benchmarked against always-on delivery of the same content first. |

---

## 3. SIGA-Evolve v2 — concrete design

**One-line spec.** Replace `scripts/self_evolving/` with a GEPA-driven outer loop over a
*manifest-described adapter*, fed an AHE-grade evidence corpus, gated by a Self-Harness regression
test, with every edit carrying a falsifiable prediction.

New code lives in `scripts/siga_evolve/` and `src/evolve/`. Per `.copilot/direction.md`,
`src/runner/` and `src/eval/` are **not modified** — everything below is additive and calls them.

### 3.1 The candidate: an explicit component manifest

Today a candidate is "whatever files happen to be in `plugin_evolving/vN/`". v2 makes it a typed
object (AHE pillar 1), serialized as `adapter/manifest.toml`:

```toml
[meta]
parent = "cand_0007"
generation = 3

[components.primer]          # always-on system context; the c0 ⊕ m interface
kind   = "prose"
path   = "PRIMER.md"
budget_tokens = 400

[components.memory]          # M, kept SEPARATE from the primer (fixes §1.8)
kind   = "itemized"          # ACE delta representation; items have ids
path   = "memory/cheatsheet.md"
budget_tokens = 800          # hard cap; curator must delete to add

[components.constraints]     # NEW artifact class — negative constraints (§5.3)
kind   = "checked"           # each entry compiles to a machine check
path   = "memory/constraints.yaml"

[components.stop_policy]     # the stop_S interface — now IN the search space
kind   = "config"
retries = 2                  # was GEOS_HOOK_MAX_RETRIES, fixed at 2
feedback_shape = "structured_errors"   # | "errors+valid_attr_table" | "minimal"
checks = ["parse", "geosx_validate", "required_sections", "constraints"]

[components.checks]          # sandboxed check plugins, fixed interface + required test
kind   = "code"
dir    = "hooks/checks/"
```

`stop_policy` and `checks` are the point. They put S — the component the paper's own ablation calls
dominant on GEOS and OpenFOAM — inside the search space for the first time. `copy_scaffolding()` is
retired: scaffolding is **resolved from `plugin/` at run time** (fixing §1.9(10)) and only manifest
components are candidate-owned.

### 3.2 Evidence: what the proposer sees

`trajectory_summary()` (`reflect.py:69`) is deleted. The proposer receives a layered corpus
(AHE pillar 2), built by `src/evolve/evidence.py` from existing machinery:

| Layer | Source | Content |
|---|---|---|
| L0 aggregate | `batch_evaluate.summarize` | per-cell mean, σ, failures-as-zero count, tool-call and wall-clock deltas vs parent |
| L1 per-task | `bottleneck/extract.py:278` | `treesim`, `section_scores`, `status`, Δ vs parent per task |
| L2 failure | `bottleneck/extract.py:48,80` + `llm_per_task.py` | `worst_subtrees(k=8)`, `missing/extra_element_types`, category label (`missing_block`, `bad_attribute_value`, …) |
| L3 drill-down | `extract.py:232` + hook event log | 10-turn tail excerpt, **validator output verbatim** (incl. the `geosx --validate-input` valid-attribute table), hook block/retry events |

L3 is *on demand*: the proposer asks for a specific (task, run) rather than receiving all of it. That
is AHE's drill-down, and it is what keeps the proposer prompt inside a sane budget while removing the
2500-char ceiling.

**Contamination containment.** L2/L3 quote ground-truth-adjacent material by construction
(`worst_subtrees` walks the GT tree). Containment: (a) evidence is visible to the **proposer only**,
never persisted into a candidate; (b) every candidate passes an extended hygiene gate
(§3.6) before it can be evaluated; (c) `worst_subtrees` entries are reported as *paths and tags*
(`Constitutive/ElasticIsotropic[rock]`), never attribute values. This is a change in leakage surface
and is flagged as requiring re-audit (§7.5).

### 3.3 Search space and the Tool-Genesis guard

Writable: `PRIMER.md`, `memory/*`, `skills/*`, `agents/*` (as today) **plus** `manifest.toml`'s
`stop_policy` block and `hooks/checks/*.py`.

Check plugins are the one place the loop authors code, and they are fenced hard, because
arXiv:2603.05578 says one-shot tool creation fails and interface errors compound:

```python
# hooks/checks/<name>.py — fixed interface, no network, no imports outside stdlib+lxml
def check(deck: Deck, ctx: CheckContext) -> list[Finding]: ...
# hooks/checks/<name>_test.py — REQUIRED; candidate is rejected without it
```

A candidate whose check plugin fails its own test, raises, or exceeds a 5 s budget is rejected before
any rollout is spent. This is a cheap gate (no API cost) and it is where most bad proposals should die.

**Explicitly out of scope:** `src/runner/`, `src/eval/`, `contamination.py`, the R MCP server, the
base harness, and the model. All frozen, per the paper's framing and `.copilot/direction.md`.

### 3.4 Selection, archive, and the accept/reject criterion

GEPA supplies the archive (`GEPAState.program_candidates`) and parent selection
(`ParetoCandidateSelector` over per-task scores). We supply the acceptance criterion, implementing
Self-Harness's validation stage as a `gepa.strategies.acceptance.AcceptanceCriterion`:

```
accept(child, parent) iff
    (1) hygiene gate passes                         (§3.6, free)
    (2) every check plugin passes its own test      (free)
    (3) no per-task regression:  min_t (s_child[t] - s_parent[t]) > -0.05
    (4) aggregate does not regress: mean(s_child) >= mean(s_parent) - 0.005
    (5) efficiency does not regress: tool_calls, wall <= 1.15x parent
```

Clauses (3) and (5) are the SIGA-specific ones and I want to argue for them explicitly.
**(3) is the tail-driven criterion.** With `σ ≈ 0.02` at `n = 3`, a mean-improvement gate is a noise
amplifier; a *no-cliff* gate is the operationalization of "the gain is reliability, not quality."
**(5) enforces the paper's own efficiency constraint as a hard search constraint** rather than a
post-hoc observation, which is the direct guard against the over-specification failure mode that §1.1
shows already happened.

### 3.5 Decision observability

Every proposal must emit, before evaluation:

```json
{"edit_id": "...", "component": "memory",
 "targets_category": "extra_block",
 "predicted_beneficiaries": ["ExampleProppantTest", "AdvancedExampleThermoPoroElasticWellbore"],
 "predicted_delta": 0.04,
 "rationale": "...", "evidence_refs": ["L2:round3/ExampleProppantTest"]}
```

Verified next round into `.evolve/decision_log.jsonl`. Two payoffs: a calibration curve (do this
model's harness predictions mean anything? — a publishable observation in its own right, and a direct
test of arXiv:2605.30621's "updating is flat in capability" claim in a domain-knowledge-bound setting),
and a targeted reversion signal (an accepted edit whose predicted beneficiaries did not move is
over-specification wearing a disguise).

### 3.6 Hygiene, extended

`src/evolve/hygiene.py`, replacing `reflect.py:248-249` and extending
`scripts/memory/hygiene_audit.py` (which keeps its current gate; we add a superset):

1. Filename regex over **all** simulator-relevant extensions — `.xml`, `.geos`, `.msh`, `.vtk`,
   `.rst`, `.yaml` (fixes §1.7's `.geos` hole).
2. Path-component match against every task's GT directory and physics-family directory name
   (fixes the `poromechanics/<file>` residue).
3. Full blocklist substring match, reusing `contamination.get_blocked_files_for_task` so the two
   never drift apart.
4. **Content** check: n-gram overlap between candidate text and each GT deck, above a threshold → reject.
5. Numeric-token check: canonicalized numeric literals from GT decks (reusing the canonicalizer in
   `scripts/relax_specs.py`) appearing in a candidate → reject.

(4) and (5) are the new capability — the current gate cannot see leaked *content* at all, and §1.9(11)
is what that looks like when it happens.

### 3.7 Round structure — fixing the confound

- **`X_anchor`** — a fixed 8-task slice of the 17 validation tasks, used for *every* candidate
  evaluation. Round-over-round numbers become comparable by construction, which
  `run_full_evolution.sh:17-19` destroyed.
- **`X_probe`** — the remaining 9, sampled per round as the evidence source only (never scored for
  selection). Keeps the proposer seeing fresh failure modes without leaking into the metric.
- **`X_eval`** — the 10 held-out-eval tasks. Touched **once**, at the end, by the single selected
  candidate. Never by the loop.

`n = 2` seeds during search (cost), `n = 5` for the final head-to-head (§4).

### 3.8 Files

```
NEW  src/evolve/{manifest,candidate,hygiene,evidence,acceptance,archive,checks,
                 proposer,evaluator}.py
NEW  scripts/siga_evolve/{seed_from_plugin.py,run_search.py,audit_lineage.py}
NEW  hooks/checks/{README.md,lazy_refs.py,lazy_refs_test.py}
NEW  tests/test_evolve.py
NEW  misc/evolve_anchor.txt            (draft anchor slice; freeze before use)
NEW  .copilot/decisions/D-011_siga-evolve-v2-method-adoption.md
KEEP src/runner/*, src/eval/*, plugin/*, contamination.py   (untouched)
ANNOTATE  scripts/self_evolving/README.md  -- the v1 scripts stay *in place*
          rather than moving to legacy/: docs/ and the paper reference these
          paths, and a rename would break reproduction of the published SE for
          no benefit. The README carries the defect table.
FIX       scripts/self_evolving/analyze_evolution.py:67 -- the invalid f-string
          format spec, and the bare `except: pass` that hid it. It now prints
          the `round_mean_treesim = 0` that was invisible for months.
QUARANTINE plugin_evolving/v4 -> plugin_evolving/_quarantine/v4/ + README;
           scripts/launch_autocamp_v4.sh -> *.QUARANTINED with a fail-fast guard (§7.5)
```

### 3.9 Implementation status (branch `feat/siga-evolve-v2`)

Everything in §3 above is built and unit-tested; nothing has been *run*, because
this environment has no `/data/shared` volume, no Docker, and no GEOS container
(§7.7). `EvaluatorConfig.validate()` reports exactly that rather than failing
obscurely mid-search, and `run_search.py` refuses to start when preflight fails.

| Piece | State |
|---|---|
| Manifest + typed components, stop policy searchable | done |
| Candidate: content-addressed, budgeted, deletion-as-edit, GEPA component view | done |
| Materialization resolving scaffolding from `plugin/` at call time | done |
| Hygiene superset (filenames/paths/task-ids/blocklist/content/numerics) | done |
| Evidence layer wired to `bottleneck/extract.py` | done |
| Regression gate + decision records | done |
| Pareto archive + parent selection (GEPA-deferring) | done |
| Check-plugin sandbox + mandatory tests + `lazy_refs` reference plugin | done |
| Proposer (one component, prediction required, budget-enforced) | done |
| Evaluator (run+score as one operation, per-task, cached) | written, unrunnable here |
| Search driver with preflight | written, unrunnable here |
| `tests/test_evolve.py` | 42 tests, all passing |

Two facts the implementation established that are worth recording:

* **`plugin_evolving/v0/PRIMER.md` is byte-identical to
  `plugin/GEOS_PRIMER_absolute_min.md`** (270 B, the runner's
  `DEFAULT_GEOS_PRIMER_PATH`). So v1 seeded from the harness default stub, and
  spent its whole budget rediscovering content the hand-designed adapter already
  had. The v2 seed starts from `plugin/`'s actual artifacts instead, which also
  makes the thing we have to beat the baseline we start from.
* **The token estimator is calibrated.** It puts `plugin/memory_primer_m1u.md`
  -- the paper's 775-token M -- at ~823 tokens, i.e. ~6% high, which is the safe
  direction for a budget gate.

Reproduce the two contamination findings from a clean checkout:

```bash
python3 scripts/siga_evolve/audit_lineage.py \
    --adapter-dir plugin_evolving/v3 \
    --adapter-dir plugin_evolving/_quarantine/v4 \
    --task-list-from scripts/self_evolving/run_full_evolution.sh
# v3: 5 warn  -- tables/{time,axialStrain,radialStress}.geos past the .xml-only gate
# v4: 1 BLOCK -- names 17 task ids: task->answer lookup table
```

---

## 4. Evaluation protocol upgrade

### 4.1 Compute-matched baselines (arXiv:2607.12227)

The search consumes `R_search` rollouts. Any new SE claim must be accompanied by baselines that spend
`R_search` too. Three, all on `X_eval`, all at `n = 5`:

| Baseline | What it controls for |
|---|---|
| **B1 best-of-k S+X+M**, `k = R_search / (10·5)` | pure parallel test-time scaling |
| **B2 sequential refinement S+X+M**, k self-review passes, same budget | pure sequential test-time scaling |
| **B3 S+X+M at `n = 5`**, no extra budget | the honest "did evolution do anything" control |

B3 is the one that matters most and is the cheapest. If SIGA-Evolve v2 does not beat B3 by more than
the paired-bootstrap CI, we have not demonstrated harness evolution — we have demonstrated a run.

**Selection must not use `X_eval`.** Selection uses `X_anchor` only; `X_eval` is touched once. This
is already SIGA's discipline (§1.10) and it survives — keep it.

### 4.2 Statistics

`n = 5` seeds on the final comparison, not 3. Report **paired per-task deltas** with a paired
bootstrap CI, not just cell means — the effect is 2 tasks out of 10, and a cell mean at `n = 3`
cannot distinguish "rescued the tail" from "got lucky on the tail." Report the tail directly:
count of runs scoring 0, and the per-task min across seeds. Under `failures-as-zero`, the
*zero-rate* is the quantity the paper's own reliability story is about, and it is currently reported
only as a σ.

### 4.3 Add a runnability signal

TreeSim is structural; a 0.8 deck may not run. We now have the ingredient the paper lacked:
`geosx --validate-input` is already mounted in the container (`src/runner/docker_cmd.py`, per
`docs/GEOSX_VALIDATE.md`). So a **loads/does-not-load** binary is nearly free — no solve, ~2-3 s per
deck. Add it as a reported secondary metric immediately. Do **not** promote it to the search objective
yet: S already optimizes against it, so using it as reward invites the loop to satisfy the validator
rather than the science. Full execution (`solve to completion`) stays future work.

### 4.4 Does the published SE result survive? — my view: **no, and we do not need a new run to know**

The three relevant held-out-eval cells are all the same shape (S+X+M, `--disallowedTools Skill`):

```
S+X+M        0.783 ± 0.022
SE           0.789 ± 0.012      Δ vs S+X+M = +0.006
SE-prose     0.775 ± 0.024      Δ vs S+X+M = -0.008
```

So the headline `Vanilla → SE = +0.069` decomposes as `Vanilla → S+X+M = +0.063` (the **hand-designed**
adapter) plus `+0.006` for everything self-evolution contributed. `±0.008` against `σ ≈ 0.02` at
`n = 3` is not a result. Combined with §1.1 — the search had no reward signal, so there is no
mechanism by which it *could* have improved anything except by chance — the honest reading is:

> **Self-evolution as implemented contributed nothing measurable. The reported SE gain is the
> hand-designed S+X+M adapter's gain.**

This is not a claim that needs arXiv:2607.12227's compute-matched machinery to establish; it is
already in Table 1. The compute-matched baselines in §4.1 are needed for the *next* result, not to
retire this one.

**Cheapest confirmation (~$3, ~2 h wall, do it first — §8.2):** re-run S+X+M and SE on `X_eval` at
`n = 5` and compare *paired per-task*. Predicted outcome: paired CI on `SE − S+X+M` spans 0, and the
two "rescue" tasks are the whole variance. If that is what we see, the paper's SE claim needs to be
restated (as "an evolved adapter matches the hand-designed one," which is still a real if smaller
finding) and the v2 program has a clean, honest baseline to beat.

### 4.5 Report at the configuration level, and steal the Harness Maturity Score

Per arXiv:2605.27922: report (model × harness configuration), not "SIGA's score." We already have the
cross-model panel; make it a first-class axis rather than an appendix. And per arXiv:2607.05458, score
*process* separately from *outcome* — a Harness Maturity Score over our hook event log (did the agent
validate before finishing? did it act on the validator's feedback? did retries converge?) is cheap,
derived entirely from data we already log, and directly measures the thing "closed-loop retries raise
the ceiling" is about.

---

## 5. Novel-method opportunities

Ordered by how confident I am that it is a *method contribution* rather than an engineering fix.

### 5.1 Binding-constraint discovery *(real contribution — and the best one)*

The paper's most interesting empirical finding is that **which component binds is interface-dependent**:
S dominates on GEOS/OpenFOAM (structural incompleteness) while M and R dominate on LAMMPS (value
correctness, structure already ≥0.976). Today that is discovered by a human running a factorial.

**The method:** a self-evolution loop whose *first phase* is diagnosis — spend a small fixed probe
budget characterizing an unseen simulator interface's failure distribution, infer which of {S, X, M, R}
binds, and *allocate the remaining search budget to that component*. Concretely: a cheap probe
(`Vanilla`, `n=1`, k tasks) → the existing bottleneck classifier → a binding-constraint posterior →
component-selection prior for GEPA's `module_selector`.

**Why it is a contribution.** Every method in the candidate set searches a *fixed* component set with a
*fixed* evidence channel. None of them decides *where to look* from the interface's own failure
signature. It is the general form of the paper's most transferable observation, it is exactly what
sample-starvation demands (spending your 30 rollouts on the component that cannot help is the dominant
cost), and it is the piece that most directly serves **subgoal (1)** — porting to a new simulator
becomes "run the probe" rather than "run a factorial."

**Testable prediction that makes it falsifiable:** run the probe on LAMMPS and OpenFOAM, whose answers
we already know from the paper. If it recovers "M/R for LAMMPS, S for OpenFOAM" from a probe budget
smaller than the factorial, the method works. That is a cheap, pre-registered, retrospective validation
on data we largely have.

### 5.2 EFC as the search objective *(real contribution — highest risk, highest reward)*

arXiv:2605.29682 defines Effective Feedback Compute — informative, valid, non-redundant, *retained*
feedback as the scaling coordinate, `R² = 0.99/0.93` where raw compute fits near-zero. It is used
there as a scaling coordinate and as a control layer. **Nobody has used it as an optimization target.**

**Why here specifically.** Our binding constraint is that TreeSim gives *one sparse scalar per
expensive rollout* and val is at a ceiling, so there is almost nothing to hill-climb on. EFC is
computable **per trajectory** from data we already log (hook events, validator output, tool calls,
whether feedback changed the next action), giving a dense, cheap, non-ceilinged signal. Optimizing
`TreeSim` with an EFC term is both a sample-efficiency argument and the principled formalization of
recommendation (vi) — "static hooks only raise the floor; closed-loop retries driven by validator
output raise the ceiling" is precisely a claim about *retained, informative feedback*.

**Risk, stated plainly:** EFC could be gameable (a hook that emits informative-looking feedback the
agent nominally acts on) and the paper's own framing is descriptive, not prescriptive. Treat it as a
*shaping* term with a small weight, validate that EFC-improving candidates also improve TreeSim on
`X_anchor`, and kill it if they decouple (§7.2).

### 5.3 Negative constraints as a first-class, checkable artifact class *(real, smaller)*

The paper's recommendation (iii) — cheatsheets need explicit negative constraints ("exactly *k*
`Constitutive` children, no more") — and the measured `missing_block ↓ / extra_block ↑` trade are
currently an observation. The contribution is making constraints a **component type that is
simultaneously prose the model reads and a check the hook enforces**: one `constraints.yaml` entry
compiles to both a cheatsheet line and a `hooks/checks/constraints.py` assertion. That closes the
"the model was told but didn't comply" gap that arXiv:2605.30621 identifies as the weak-tier failure
mode (activate-but-don't-follow), and it is a genuinely new artifact class rather than more text.

It is a *smaller* contribution than 5.1/5.2 because the idea is stated in the paper; the contribution
is the dual prose/check representation and the demonstration that it moves `extra_block`.

### 5.4 Attribute-level oracles and cross-section consistency — *mostly engineering, and mostly done*

I want to be blunt here because it changes the plan. Per `docs/GEOSX_VALIDATE.md`,
`geosx --validate-input` **already** catches unknown attributes (printing the full valid-attribute
table), hallucinated element tags (printing the ~50 valid solver types), and load-time dangling
cross-references including the `targetRegions` → `CellElementRegion` case. The paper's proposed
"cross-section consistency hook" (`<ElementRegion materialList>` vs `<Constitutive>` names) is the
same class of check and is largely covered.

What actually remains:
- **Engineering:** the residual lazily-resolved reference class (`discretization="..."` with no
  matching `NumericalMethods` child) — a ~30-line check plugin, and a good first exercise for §3.3.
- **Not a validator problem at all:** `bad_attribute_value` where the value is *well-formed and
  wrong* — a solver tolerance of `1e-2` where the GT says `1e-6`, a permeability off by three orders.
  No schema, no loader, and no consistency check can see this. It is a *domain-knowledge* problem, and
  the honest options are (a) plausibility ranges mined from the example corpus (engineering, and
  contamination-adjacent — flag it), or (b) accept it as the residue and say so.

**So: do not sell attribute-level oracles as the novel contribution.** Sell the fact that we
*measured* which part of it was a validator problem (solved) and which part is a knowledge problem
(open). That is a more defensible claim and it is now backed by a direct experiment in the repo.

### 5.5 Closed-loop validator-driven retries — *engineering, unless paired with 5.2*

Implementing the paper's own recommendation (vi) is engineering. It becomes method when the *retry
policy itself is searched* — how many retries, what feedback shape, whether to escalate — which is
exactly what `[components.stop_policy]` in §3.1 puts in the search space, scored by §5.2's objective.
That pairing is the interesting version.

---

## 6. Cost and effort

Costs assume `deepseek-v4-flash` at the paper's observed rate (64 runs ≈ $4.20 → ~$0.066/task-run),
1500 s timeout, `workers=4`. **Infrastructure assumption:** none of this is runnable in the current
environment — `/data/shared/...` is absent and there is no Docker/GEOS/geosx image here. Everything
below assumes the original workstation (or an equivalent rebuild) is available; if it is not, add
**1-2 weeks** to re-stand-up the data volume, the `geos-eval` image, and the geosx install mounts.

| # | Item | Impl. hours | API cost | Wall | Needs infra we lack? |
|---|---|---|---|---|---|
| 0 | **De-risk: S+X+M vs SE paired, n=5, X_eval** (§4.4) | 2 | ~$3 | 2 h | no |
| 1 | Quarantine v4, extend hygiene gate (§3.6), re-audit | 6 | $0 | 1 d | no |
| 2 | Evidence layer: `extract.diagnostic_for_task` → proposer (§3.2) | 8 | $0 | 1 d | no |
| 3 | Evaluator callable + manifest + candidate I/O (§3.1) | 20 | $0 | 3 d | no |
| 4 | GEPA integration: Pareto archive, acceptance, budget (§3.4) | 12 | $0 | 2 d | no |
| 5 | Self-Harness regression gate + decision log (§3.4-3.5) | 10 | $0 | 1.5 d | no |
| 6 | Check-plugin sandbox + required tests (§3.3) | 12 | $0 | 2 d | no |
| 7 | **Search run**: 20 candidates × 8 anchor tasks × n=2 | — | ~$21 | ~10 h | no |
| 8 | **Final eval**: 4 cells (v2, SE, S+X+M, Vanilla) × 10 × n=5 | — | ~$13 | ~5 h | no |
| 9 | **Compute-matched B1/B2** (§4.1), budget-matched to (7) | 6 | ~$21 | ~10 h | no |
| 10 | ACE delta-update curator for M (§2 #4) | 10 | ~$2 | 1.5 d | no |
| 11 | Runnability binary via `geosx --validate-input` (§4.3) | 6 | $0 | 1 d | **geosx binary + mounts** |
| 12 | EFC objective (§5.2) | 16 | ~$8 | 3 d | no |
| 13 | Binding-constraint probe (§5.1) + retrospective LAMMPS/OpenFOAM validation | 20 | ~$15 | 4 d | **OpenFOAM/LAMMPS benches** |
| | **Core program (0-9)** | **~76 h** | **~$58** | **~3 wks** | |
| | **+ stretch (10-13)** | **~128 h** | **~$83** | **~5 wks** | |

The API cost is *not* the constraint — under $100 for the whole program. **Implementation hours and
wall-clock are the constraint**, which is itself an argument for using GEPA as a library (item 4 is 12 h
instead of ~40 h of writing an archive and a Pareto selector) and for the evidence layer being wiring
(item 2 is 8 h because `bottleneck/extract.py` exists).

---

## 7. Risk register and kill criteria

| # | Risk | Kill criterion |
|---|---|---|
| 7.1 | **Search finds nothing.** With val at ceiling and a tail-driven objective, 20 candidates may all be within noise on `X_anchor`. | After 20 candidates, if the best `X_anchor` score is within the seed-noise band of the seed candidate, **stop**. Report the null. This is a publishable result given arXiv:2607.12227, and it is the single most likely outcome. |
| 7.2 | **EFC decouples from TreeSim.** The loop learns to manufacture feedback. | If the top-5 EFC candidates' `X_anchor` TreeSim rank-correlates below ρ=0.3 with their EFC, drop the EFC term to weight 0 and continue on TreeSim alone. |
| 7.3 | **Over-specification / efficiency regression.** §1.1 shows this already happened once. | Acceptance clause (5) is a hard gate (1.15× parent). If >50% of proposals are rejected on (5), the proposer is systematically inflating — switch to ACE delta updates with a stricter M budget (item 10) before continuing. |
| 7.4 | **Check-plugin interface errors compound** (Tool-Genesis). | If >30% of authored checks fail their own required test, remove `hooks/checks/` from the writable set and keep only the declarative `stop_policy` block. |
| 7.5 | **Reward hacking / contamination.** §1.9(11) is an existence proof that this happens here. The v2 evidence layer *increases* the leakage surface (§3.2). | **Pre-commitments:** (a) quarantine `plugin_evolving/v4/` before any run; (b) `hygiene.py` gate is blocking, not advisory, and runs before any rollout is spent; (c) run a HackDetect-style post-hoc audit (arXiv:2607.22368) over the final candidate's trajectories, checking for reads of GT-adjacent files whose names appear in the candidate. **Kill:** any accepted candidate containing a GT numeric literal or a blocklisted path component → discard the entire lineage and re-audit, do not patch and continue. |
| 7.6 | **Anchor overfitting.** 8 fixed tasks, 20 candidates — a real risk. | Report `X_anchor` and `X_eval` side by side. If `X_eval` gain is <30% of `X_anchor` gain, we are fitting the anchor; report it as such rather than as a method result. |
| 7.7 | **Infra unavailable.** `/data/shared` and the container are absent here. | Establish availability *before* item 3. If the workstation is gone, items 7-9, 11, 13 are blocked and the program shrinks to items 0-6 as a code deliverable with no numbers — decide explicitly rather than discovering it in week 3. |
| 7.8 | **The de-risk experiment (item 0) confirms SE ≈ S+X+M.** | This is not a kill — it is the *expected* outcome and it makes v2 more interesting, not less: it establishes that a loop with no reward signal produces nothing, which is exactly the control our v2 result needs. But it does require restating the paper's SE claim. |

---

## 8. Recommendation

### 8.1 Primary path — build SIGA-Evolve v2 (items 1-9)

A hybrid, weighted toward **Self-Harness's regression gate** and **AHE's observability**, implemented
on **GEPA** as the outer loop, with the search space widened from prose to include the stop policy and
sandboxed check plugins.

The reasoning in one paragraph: SIGA's loop failed for a *specific, diagnosable* reason — no reward
reached the proposer — and the second-order reasons (thin evidence, prose-only space, no archive) are
each addressed by a named 2026 method that is either available as a library or is a day of wiring
against code this repo already has. The task's own character then picks among those methods: it is
tail-driven, so selection must be Pareto over per-task scores and the gate must be no-regression
rather than mean-improvement; it is sample-starved, so the outer loop must be GEPA rather than DGM;
it is efficiency-constrained, so minimality and delta updates rather than accumulate-and-hope. None of
this requires unfreezing the model or the base harness, and the manifest-based candidate (§3.1) is the
piece that also carries subgoals (1) and (2): a new simulator is a new manifest, not a new codebase.

### 8.2 The cheap parallel de-risking experiment — run this first, this week

**S+X+M vs SE on `X_eval`, `n = 5`, paired per-task, ~$3, ~2 h wall** (item 0).

It costs almost nothing, it needs no new code, and it is decisive for the framing of everything else.
My prediction is stated in §4.4: the paired CI on `SE − S+X+M` will span zero. If so we have a clean,
honest baseline and a much sharper story — *"we show that a reflect-and-rewrite loop with an
unmonitored broken reward channel produces a null result indistinguishable from the hand-designed
adapter, and then we fix it"* is a stronger paper than *"we self-evolved an adapter."* If instead SE
genuinely beats S+X+M at `n = 5`, that is a surprising positive that needs explaining before we
rebuild anything, and I would want to know it before spending 76 hours.

Run item 1 (quarantine v4 + hygiene) in the same week regardless of the outcome. It is 6 hours and it
closes an active hazard.

### 8.3 What explicitly not to do

**Do not build a DGM/Hyperagents-style open-ended archive over the full harness program.**

It is the most attractive-sounding option in the candidate set and it is wrong for this problem on
three independent counts: (i) it needs cheap, plentiful evaluations, and ours cost 25 minutes and a
GEOS container per task-run over a pool of ≤17 tasks; (ii) it requires unfreezing the base harness,
which is SIGA's entire framing and its portability claim; (iii) arXiv:2607.12227 finds that automatic
harness evolution does not consistently beat simple test-time scaling *even on Terminal-Bench 2.1
where sampling is cheap and the benchmark is large* — so the prior that it beats best-of-k on a
17-task sample-starved scientific benchmark is poor. If we want Meta-Harness's full-program search
later, GEPA's `MetaHarnessEngine` gives it to us without a rebuild.

**Second-order don't:** do not reintroduce any retrieval-gated memory module. The local zero-call
result is the single most transferable finding this project has, and every context/memory method in
the candidate set (ACE, MCE, the `(k,v)` framework) assumes agent-initiated lookup. Import their
*update mechanisms*; deliver their *content* always-on.

---

## Appendix A — verification status

All 28 arXiv IDs in the candidate set were fetched from `arxiv.org/abs/<id>` on 2026-08-19 and their
`citation_title` + abstract checked against the claims in the two review files. **28/28 resolved and
matched**; no miscitations found. IDs the reviews had marked `[unverified]` — including 2601.21557
(MCE), 2603.19461 (Hyperagents), 2606.13662 (EurekAgent), 2512.21782 (SAGA), 2605.22343
(Sibyl-AutoResearch) — all resolve to papers matching their described content.

Reference implementations cloned to `~/code_ref/` for local reading:
`meta-harness` (stanford-iris-lab), `gepa` (gepa-ai), `ace` (ace-agent), `dgm` (jennyzzt),
`a-evolve` (A-EVO-Lab, the arXiv:2605.30621 code), `SkillFoundry` (ma-compbio-lab),
`Hyperagents` (facebookresearch). Self-Harness (2606.09498) and AHE (2604.25850) link no public code;
both are reimplemented from their papers in §3.

## Appendix B — claims I could not verify in this environment

- No `events.jsonl`, `<task>_eval.json`, or run artifacts are present (`/data/shared/...` absent).
  Every claim in §1.1 rests on committed artifacts — `.reflection_meta.json`, plugin file contents,
  and script source — not on run logs. The reading that `round_mean_treesim: 0` means *no eval files
  existed at reflect time* (rather than *all scores were genuinely 0*) is inferred from
  `run_full_evolution.sh` containing no scoring step and from the paper reporting SE ≈ 0.919 on val.
  A single `ls` of the round-0 `_results` directory on the original workstation would settle it, and
  it should be the first thing checked.
- Wall-clock and token figures in §6 are extrapolated from the paper's reported $4.20/64-run figure.
- The claim that `geosx --validate-input` catches what `docs/GEOSX_VALIDATE.md` says it catches is
  taken from that document's own direct-against-binary verification; I could not re-run it (no binary,
  no container here).
