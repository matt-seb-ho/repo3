# Research Log

---

<a id="LOG-2026-04-20-1"></a>
### 2026-04-20 — Copilot attached to repo3

Attached research-copilot to existing project `repo3`. This is the third-generation GEOS XML authoring harness, building on vanilla Claude Code. Host docs (evaluation/runner/cc-comparison) are preserved. All copilot state lives in `../.copilot/`.

**Initial DAG: 4 Assumed foundations, 2 completed experiments, 1 pending experiment, 4 exploring ideas.**

- `I01` established task + 36-task eval suite
- `I02` established XMLTreeSim as headline metric
- `I03` established contamination-safe Docker sandbox
- `I04` established the plugin (geos-rag + MCP) as the candidate adaptation surface
- `E01` (completed, 0.643 TreeSim) = no-plugin + deepseek baseline
- `E02` (completed, 0.809 TreeSim) = plugin + minimax — confounded vs E01 (different model)
- `E03` (pending scoring) = plugin + deepseek on `repo3_eval_run4` — the apples-to-apples comparison that fills the main gap identified in `ablation_findings.md`
- `I05` = RQ: find CC adaptation that beats vanilla CC
- `I06`-`I09` = memory / primer / file-tree / simpler-RAG candidate interventions

**Immediate next:** score `repo3_eval_run4` against ground truth to resolve E03. This decides the session's plan: if plugin wins on apples-to-apples, the next move is adaptation-stacking; if flat/negative, we pivot hard into the memory system (user's strongest bet).

-> DAG: I01, I02, I03, I04, E01, E02, I05, E03, I06, I07, I08, I09
-> Evidence: ../misc/ablation_findings.md, ../misc/geophys_todo.md
-> Decision: (initialization)

---

<a id="LOG-2026-04-20-2"></a>
### 2026-04-20 — E03 resolved: plugin wins on deepseek (+0.175 TreeSim)

Scored `repo3_eval_run4` (plugin CC + deepseek-v3.2) against
`experiments_gt`. 35/36 tasks scored (SPE11b produced unparseable XML).

**Headline (paired 35 tasks):**
- plugin+ds mean TreeSim **0.828** vs no-plugin+ds **0.653** -> **+0.175**
- pass >=0.7: **31/35 (88.6%)** vs **19/35 (54.3%)** -> **+34.3 pp**
- Wins on 29/35 tasks, loses on 6 (max loss -0.17)

Biggest wins concentrated on tasks where no-plugin CC produced essentially
empty XML (TutorialSneddon 0.099 -> 0.804; ExampleDPWellbore 0.305 -> 0.992;
ExampleMandel 0.275 -> 0.948). Plugin mostly rescues catastrophic failures;
median gain (+0.144) is smaller than mean gain.

Updated E03 node: status=exploring -> status=good, metric_value=0.828,
decision=keep. Added I10 (memory-on-top-of-plugin) and I11 (plugin
decomposition: skill vs MCP attribution) as child nodes.

**Session pivot:** plugin wins cleanly, so the next contribution is to
show (a) the adaptation stacks (memory on top of plugin) or (b) the gain
is robust across models. I'll focus on (a) for the advisor meeting
because the user explicitly flagged memory as the highest-priority
intervention in `geophys_todo.md`.

-> DAG: E03, I10, I11
-> Evidence: docs/XN-001_plugin-vs-no-plugin-deepseek.md, misc/score_run4.log, misc/e03_vs_e01.txt
-> Decision: E03 decision=keep; promote I10 to next exploration target

---

<a id="LOG-2026-04-20-3"></a>
### 2026-04-20 — E04 (memory) launched

Built the memory-on-top-of-plugin pipeline (D-001). Cheatsheet generated
by deepseek-v3.2 via OpenRouter from 18 train-split trajectories of
repo3_eval_run4. Cheatsheet lives at `../plugin/cheatsheet.md` (~1700
tokens, 6 sections: RAG usage, XML structure, Mesh/Geometry, Solvers,
Constitutive, Field Specs + Common Mistakes).

Runner wired: new agent `claude_code_repo3_plugin_mem` reads
`cheatsheet_path` from agent config; `build_system_prompt` injects
between primer and RAG instructions. Dry-run + unit-level injection
test pass.

First real launch failed: 17/17 tasks errored on tmp_geos creation —
`/data/shared/geophysics_agent_data/data/eval/tmp_geos/` is brianliu-owned.
Relaunched with `--tmp-geos-parent /data/matt/geos_eval_tmp/` (my scratch
dir, confirmed writable). Currently running (bash bg).

-> DAG: E04 (new, status=exploring)
-> Evidence: decisions/D-001_memory-experiment-design.md, plugin/cheatsheet.md, misc/memory_split.json
-> Decision: (pending E04 completion)

---

<a id="LOG-2026-04-20-4"></a>
### 2026-04-20 — E04 resolved: memory cheatsheet HURTS performance (-0.32 TreeSim)

Scored `mem_run1`. Memory-stacking hypothesis NOT supported. Plugin
decisively beats plugin+cheatsheet on deepseek-v3.2.

**Headline (paired 14 scorable test tasks):**
- plugin-only mean TreeSim **0.831** vs plugin+cheatsheet **0.532** -> **-0.322**
- Including 3 no-output failures as 0: memory = 0.438, delta -0.393
- pass >=0.7: plugin 15/17, memory 4/14 (4/17 if failures=0)
- Memory wins on 1/14 tasks (pknViscosityDominated +0.13), loses on 13/14
- Failures: 3 `failed_no_outputs` + 1 timeout in memory run; plugin had 0/17 fails

Dominant failure mode: agent emits `redacted_thinking` block then
`end_turn` after 3-6 turns without calling Write/Edit. Inspected the
`AdvancedExampleModifiedCamClay` trajectory: agent did 3 RAG + 1 Read
(failed path) + 1 Bash, then produced a redacted_thinking and stopped.
Matches the qwen3.5-9b pattern where the model bails on tool-use without
making progress.

**Hypotheses (not tested):**
1. Context bloat — cheatsheet adds 1700 tokens to ~21K-token system
   prompt, possibly past deepseek's attention threshold for long system.
2. Task-specific advice from train-set patterns ("use InternalWellbore",
   "define dummy ElasticIsotropic") conflicts with test-task needs.
3. Cheatsheet guidance slows exploration / reduces agent's willingness
   to iterate.

**Updated E04 node:** status=exploring -> status=negative, decision=discard.
This rules out the specific D-001 design, not memory-as-an-intervention
in general. Future memory experiments should try: shorter
cross-task-only cheatsheet, MCP-tool memory, or stronger-model
environment.

**Advisor story update:** The plugin result (E03, +0.175 TreeSim) stands
as the headline adaptation. The memory follow-up is a negative with a
clear failure signature. Honest reporting: we have ONE adaptation that
beats vanilla CC. Stacking is deferred pending memory-design iteration.

-> DAG: E04 negative/discard
-> Evidence: docs/XN-003_memory-experiment-negative.md, misc/e04_vs_e03_test17.txt, misc/mem_run1.log
-> Decision: D-001 cheatsheet design discarded; revisit memory with restricted-scope / MCP-tool / stronger-model variants

---

<a id="LOG-2026-04-20-5"></a>
### 2026-04-20 — E05 short-cheatsheet also fails; E06 (cross-model) launched

**E05 (short-cheatsheet, ~300 tokens, explicit stop criterion):**
13/17 success = same count as E04; mean TreeSim 0.561 on 14 paired
scored vs plugin-only 0.831. Slightly better than E04's 0.532 but still
decisively negative. Same failure pattern: ModifiedCamClay + Extended
DruckerPrager failed_no_outputs with redacted_thinking -> end_turn;
EDPWellbore + Mandel timed out (BOTH succeeded in E03 and E04; NEW
failures under short cheatsheet). TutorialSneddon wrote malformed XML
(parse error). Length is NOT the cause; cheatsheet-in-system-prompt as
a general pattern is what breaks deepseek. E05 discarded.

**CC native memory audit (user flagged in geophys_todo.md):** checked
all 36 E03 task event files and the per-task `.claude_home` dirs.
Result: CC native memory is a **no-op** in our pipeline. Every task
has the memory_paths setup, but:
- memory directories exist but are empty (0 files written) across
  all sampled tasks in plugin-run4 and ablation-v2
- 0 memory-named tool calls across 36 tasks
- /memory slash command is NOT in the agent's slash_commands list
- per-task /workspace is wiped with container anyway, so any memory
  would not persist
So our baselines + cheatsheet experiments are all running ON A CLEAN
slate with respect to CC's native memory. Not a confound.

**E06 (cross-model, plugin-less minimax on 17 test):** launched with
workers=12 to test concurrency headroom (machine has 128 CPU, 900GB
RAM, 3 L40S GPUs idle). 12 docker containers spun up cleanly, no
rate-limit errors. Will pair with E02 (minimax+plugin, already scored
on 16/17 test tasks) for cross-model analog of E03's paired comparison.
~$60 of OpenRouter spend. If plugin advantage holds on minimax,
generalization claim strengthens; if not, plugin win is deepseek-
specific and the paper story needs reframing.

**Memory direction:** user pushed back on DC-Cu (fair — sequential
curation without trace regeneration is just batched aggregation
dressed up). Agreed to drop further memory experiments this sprint.
Remaining budget focuses on cross-model (E06) + potential filetree
(I08) + multi-seed replication of E03.

-> DAG: E05 negative/discard; E06 exploring
-> Evidence: misc/memshort_run1.log, misc/mm_noplug_run1.log (in progress)
-> Decision: memory via system-prompt-inject design abandoned for sprint; focus shifts to cross-model + filetree

---

<a id="LOG-2026-04-20-6"></a>
### 2026-04-20 — E06 resolved (cross-model POSITIVE); E07 filetree launched

**E06 (minimax-m2.7 no-plugin on 17 test tasks):** 17/17 agent
success, 15/17 scored (2 XML parse errors: ExampleThermalLeakyWell,
TutorialPoroelasticity — minimax wrote malformed XML without RAG help).
Paired against E02 (plugin+minimax) on 15 common scored tasks:
- minimax+plugin 0.809 vs minimax-no-plugin 0.694 -> **plugin wins +0.102**
- Plugin wins 11/15 tasks, no-plugin wins 4/15
- Biggest plugin win: ExampleMandel (+0.659), DeviatedElastic (+0.322)
- Biggest no-plugin win: TutorialSneddon (+0.218), Thermoporoelastic (+0.144)

**Cross-model generalization CONFIRMED.** Plugin advantage holds on
minimax (+0.102) smaller than on deepseek (+0.178), consistent with
minimax being a stronger base model. Updated E06 to status=good,
decision=keep. Interpretation: plugin rescues catastrophic failures
that weaker models hit; stronger models find reference examples
without RAG. Expected pattern.

**Operational finding:** workers=12 safe — 17 tasks in 17 min wall,
0 rate-limit errors from OpenRouter. Machine has 128 CPU / 900GB RAM /
3 L40S GPUs idle. Recommend workers=12 default.

**E07 (filetree injection on 17 test tasks, deepseek-v3.2)
launched:** adds a precomputed `/geos_lib/inputFiles/` path index
(~4.5KB, 746 files across 87 dirs) to the system prompt so the agent
can locate candidate reference XMLs without Glob/Bash find. Tests the
hypothesis that RAG's primary value is file discovery vs. semantic
retrieval. If filetree wins, cheaper alternative to full RAG; if not,
semantic retrieval matters.

Also updated hub SoK and wrote XN-006 (consolidated advisor brief).

-> DAG: E06 good/keep; E07 exploring
-> Evidence: docs/XN-005_cross-model-plugin-win.md, docs/XN-006_advisor-brief-final.md, misc/e06_vs_e02.txt
-> Decision: cross-model claim is now two-model; plugin generalizes. Workers=12 default.

---

<a id="LOG-2026-04-20-7"></a>
### 2026-04-20 — E07 filetree ALSO negative; convergent system-prompt-stacking pattern

**E07 (filetree injection on 17 test):** 17/17 scored (3 timeouts
produced partial XML). 0 redacted_thinking failures — structural
content does NOT trigger the cheatsheet-style stop pattern. BUT mean
TreeSim **0.604 vs plugin-only 0.831 = delta -0.227** paired. Filetree
wins 2/17, plugin-only wins 15/17.

**Striking per-task pattern:** filetree regresses hardest on EXACTLY
the tasks plugin-only rescues most catastrophically. Plugin-only beat
no-plugin on Sneddon +0.705; filetree LOSES vs plugin-only on Sneddon
-0.719. DPWellbore +0.687 -> -0.687. Mandel +0.673 -> -0.637. The
filetree is directly nullifying the plugin's rescue mechanism —
probably by giving agent explicit file paths that bypass the semantic
RAG.

**Cross-experiment pattern now clear:** ANY auxiliary content injected
into system prompt hurts plugin, across 3 experiments:
- E04 long cheatsheet: -0.322
- E05 short cheatsheet: -0.270
- E07 filetree: -0.227

Different content types (instructions vs structure), different
lengths (300-4500 tokens), same qualitative result. Plugin's value
is specifically the MCP RAG + skill prompt. System-prompt stacking
is counterproductive.

**Positive buried in 3 negatives:** this is itself a useful finding.
Future plugin augmentations should target the TOOL layer (new MCP
tools, better retrieval, plugin-internal logic) not the SYSTEM PROMPT
layer. Saves us from several natural but misguided future attempts.

-> DAG: E07 negative/discard; I08 negative
-> Evidence: docs/XN-007_filetree-negative.md, misc/e07_vs_e03_test17.txt
-> Decision: drop system-prompt augmentation as a design direction; focus future work on MCP tool additions.

---

<a id="LOG-2026-04-20-8"></a>
### 2026-04-20 — Extended-session pivot: primer ablation + retry memory via non-system-prompt channels

User went to sleep after advisor brief was ready. Extended-session plan
in D-002. Trajectory analysis (subagent) returned XN-008: plugin
gains are genuine signal, not variance — 3 mechanism classes
(semantic discovery, schema awareness, variant disambiguation).

**New experiments launched / designed:**
- **E08 (primer-minimal):** plugin + ~450-token minimal primer (vs full
  ~10K). Tests whether primer content matters. Running, ~20 min in.
- **E09 (memory-as-workspace-file):** cheatsheet_abstract.md (shortcuts
  + pitfalls, 550 tokens) delivered as /workspace/CHEATSHEET.md with a
  2-line system-prompt pointer. Tests delivery channel vs content.
  Queued.
- **E11 (G-Memory-lite as MCP tool):** new MCP server memory_mcp.py
  exposes memory_lookup(query). Built memory_index.json from 18 train
  trajectories — entries contain task_id, final_treesim, reference_xmls,
  productive_rag_queries, section_strengths, topic_keywords. Keyword
  scoring + treesim-weighted ranking. Smoke tests on 5 queries return
  appropriate past tasks. agent=claude_code_repo3_plugin_gmem. Queued.

**Why G-Memory-lite design choices:**
- Frozen index (build once from train, serve read-only at test)
  preserves parallelism per D-001 constraint.
- Concrete examples (file paths + past RAG queries) instead of abstract
  rules - addresses user's question about whether content type matters.
- MCP tool delivery instead of system-prompt inject — sidesteps the
  E04/E05/E07 failure mode entirely.
- Pure keyword scoring (no embeddings) to avoid heavy deps and stay
  fast/reproducible.

**Not doing this sprint:**
- Full G-Memory with graph + FINCH clustering (too heavy).
- Dynamic Cheatsheet Cumulative with trace regeneration (~3h, rejected
  after user pushback on marginal value over batch aggregation).
- Hard-mode eval set generation (deferred; mine_examples_v2.py exists
  and can generate required_only specs but defer running to later).
- Opus cross-model (cost-deferred).

-> DAG: E08 exploring, E09 pending, E11 pending
-> Evidence: docs/XN-008_plugin-mechanism-trajectory-analysis.md, plugin/memory_index.json, plugin/scripts/memory_mcp.py, scripts/memory/build_gmem_index.py, .copilot/decisions/D-002_extended-session-plan.md
-> Decision: focus extended session on memory via non-system-prompt channels (workspace file + MCP tool) + primer ablation. Frozen at test time.

---

<a id="LOG-2026-04-20-9"></a>
### 2026-04-20 — E08 (minimal primer) NEGATIVE; primer content is load-bearing

Scored minprimer_run1: plugin + ~450-token minimal primer vs E03's
full primer on 17 test tasks. **Paired delta -0.235** (minimal 0.596
vs full 0.831). Minimal-primer wins 1/17, loses 16/17. 4 timeouts
(vs 0 in E03). Largest losses on SAME 3 tasks that E07 filetree
regressed most on: Sneddon -0.723, DPWellbore -0.688, Mandel -0.677.

**Surprising finding:** even with plugin RAG fully present, stripping
the primer's detailed schema-navigation scaffolding catastrophically
hurts the catastrophic-failure-rescue mechanism. The primer is not
just narrative context — it seems to orient the agent's RAG query
strategy in a way that determines whether rescue fires.

Primer (647 lines) + RAG MCP together form the active-ingredient
stack of the plugin. Either one removed → rescue mechanism breaks.

**Updated convergent pattern (four negatives):** E04/E05/E07/E08 all
show that interfering with the plugin+primer+MCP stack hurts
performance on the rescue-task subset:
- E04 long cheatsheet in system prompt: -0.322
- E05 short cheatsheet in system prompt: -0.270
- E07 filetree in system prompt: -0.227
- E08 shrink primer: -0.235

All regress hardest on the SAME 3 rescue tasks. Strong signal that the
current primer + RAG MCP is a tightly-coupled design; pieces must stay
together.

Launched E09 (memory-as-workspace-file) immediately after. E11
(G-Memory-lite MCP tool) queued after that.

-> DAG: E08 negative/discard
-> Evidence: misc/e08_vs_e03_test17.txt, misc/minprimer_run1.log
-> Decision: minimal-primer design discarded; preserve full primer. Future primer work should ADD content, not subtract. Next: test whether memory-via-file (E09) or memory-via-MCP-tool (E11) helps.

---

<a id="LOG-2026-04-20-10"></a>
### 2026-04-20 — E09 (workspace-file memory) NEGATIVE; E11 running

E09 delivered the abstract cheatsheet as /workspace/CHEATSHEET.md
(not in system prompt, just a 2-line pointer). Same result class as
E04/E05/E07/E08: 11/17 agent success, 6 timeouts, 2 scoring failures.
Paired mean 0.622 vs plugin 0.831 = **delta -0.212** on 15 scored.
Wins 2/15, loses 13/15. Largest regressions on Sneddon -0.733,
DPWellbore -0.696, Mandel -0.618 (same 3 rescue tasks).

**Channel distinction doesn't rescue memory.** Whether the content is
in the system prompt, the workspace file, or simply tweaks the
primer's depth, performance degrades by similar magnitudes on the
same 3 rescue tasks. Convergent negative pattern now 5 independent
experiments deep:
- E04 long cheatsheet (sys-prompt, 1700t): -0.322
- E05 short cheatsheet (sys-prompt, 300t): -0.270
- E07 filetree (sys-prompt, 1100t): -0.227
- E08 minimal primer (shrink): -0.235
- E09 workspace cheatsheet (file, 550t): -0.212

One channel left untested: MCP tool. E11 (G-Memory-lite as MCP
`memory_lookup`) launched immediately — uses the same memory_index.json
content but delivered only when the agent calls a tool. If E11 fails
too, we have strong evidence the problem is not delivery at all, it's
that ANY perturbation to the plugin+primer stack destabilizes the
rescue mechanism on Sneddon/DPWellbore/Mandel/Poroelastic-family
tasks.

-> DAG: E09 negative/discard; E11 exploring
-> Evidence: misc/e09_vs_e03_test17.txt, misc/memws_run1.log
-> Decision: workspace-file memory discarded; only MCP-tool channel remaining to test.

---

<a id="LOG-2026-04-20-11"></a>
### 2026-04-20 — E11 (G-Memory MCP tool) NEGATIVE but smallest-magnitude

E11 paired mean 0.638 vs plugin 0.831 = **delta -0.192** on 17 tasks.
Agent called memory_lookup on all 17 tasks (1 call each, early in
trajectory) — MCP tool is discovered and used. Smallest-magnitude
negative in the 6-variant memory/augmentation battery:

| Attempt | Delta | Failure concentration |
|---|---:|---|
| E04 long cheatsheet sysprompt | -0.322 | redacted_thinking failures |
| E05 short cheatsheet sysprompt | -0.270 | redacted_thinking failures |
| E07 filetree sysprompt | -0.227 | all 3 rescue tasks |
| E08 minimal primer (shrink) | -0.235 | all 3 rescue tasks + timeouts |
| E09 workspace cheatsheet | -0.212 | all 3 rescue tasks + timeouts |
| **E11 MCP-tool memory** | **-0.192** | **Sneddon, Mandel; rescues DPWellbore** |

E11 is partially different: it RESCUES DPWellbore (0.939 vs plugin
0.992, only -0.05) where all other memory variants score 0.28-0.40.
Also IMPROVES pknViscosityDominated by +0.142. But still fails on
Sneddon (-0.716) and Mandel (-0.669).

**Final verdict on memory this sprint:** ALL 6 variants hurt
performance on the 17-task test subset. The "rescue mechanism" on
TutorialSneddon and ExampleMandel is extremely fragile — ANY
perturbation to the plugin+primer+RAG stack kills it, regardless of
delivery channel (sys-prompt, file, MCP tool) or content type
(instructions, structure, concrete example-mappings). MCP-tool
delivery is the least-bad channel and shows PARTIAL rescue on some
tasks, which is a direction worth investigating.

**Possible paths forward (not this sprint):**
- Cross-model test of memory — maybe only deepseek-v3.2 has this
  fragility; minimax or Opus may handle memory without breaking.
- Memory designed specifically to avoid perturbing early trajectory
  — e.g., agent asks for memory only mid-task when stuck, not
  proactively.
- Plugin attribution first (skill-only, MCP-only) — understand which
  part of the plugin creates the fragile rescue mechanism.

-> DAG: E11 negative/discard
-> Evidence: misc/e11_vs_e03_test17.txt, misc/gmem_run1.log, plugin/scripts/memory_mcp.py, plugin/memory_index.json
-> Decision: memory experiments paused for this sprint. Full stack (plugin+primer) is stable; augmentations break rescue. Advisor report should frame as: 6 convergent negatives characterizing a fragility pattern, not a single failure.
