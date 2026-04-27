# Session summary — 2026-04-27

A roughly day-long working session covering: harness bug discovery & fix,
codebase refactor, model migration (minimax → DSv4-flash), schema-validation
infrastructure (xmllint), several cross-cutting analyses, and seven new
agent variants. This doc cross-references the dated finding docs and is
intended as the single entry point for "what happened today."

## Quick links to artifacts produced

- `docs/2026-04-27_vanilla-cc-stale-plugin-call-bug.md` — the harness bug
- `docs/2026-04-27_dsv4_migration.md` — model migration design + smoketest evidence
- `docs/2026-04-27_4condition-file-tool-comparison.md` — file-access + tool-usage comparison across the 4 canonical conditions, with Bash analysis and the read-math breakdown the user asked about
- `docs/2026-04-27_file-access-and-tool-usage-analysis.md` — broader cross-run analysis
- `docs/xmllint_validation.md` — schema-validation investigation
- `docs/2026-04-27_xmllint-validation-summary.md` — index entry
- `scripts/api_probe.py` — multi-provider latency probe (OpenRouter / DeepSeek / OpenAI / Anthropic)
- `scripts/analysis/analyze_file_access.py`, `analyze_tool_usage.py`,
  `compare_4conditions.py` — cross-run analysis tooling
- `src/runner/` — refactor of the 3500-line run_experiment.py into 17 modules

## Threads, in approximate order

### 1. Vanilla-CC stale-plugin-call bug

**Symptom**: An earlier gemma-4-31b vanilla-CC smoketest looked like it had
plugin tools loaded — its `status.json` showed `plugin_tool_calls: 4` and
non-zero `mcp__geos-rag__*` counts.

**Root cause** (two real bugs):
1. `build_system_prompt` unconditionally appended a paragraph saying "Use
   the MCP tools mcp__geos-rag__search_*" regardless of `enable_plugin`.
   Vanilla CC saw a system prompt instructing it to call tools that were
   not loaded. Some models (gemma-4, deepseek-v3.2) bit and emitted
   phantom tool_use blocks; minimax m2.7 and qwen 3.5 ignored.
2. `per_tool_counts` increments on attempted tool calls, including ones
   that error with "No such tool available".

**Cross-model audit**: 0 stale calls in 52 minimax m2.7 task-runs, 100% in
gemma-4-31b (1/1 sampled), 94% in deepseek-v3.2 v2 era. The phenomenon was
model-specific.

**Fix**: thread `plugin_enabled` into `build_system_prompt` and gate the
RAG instruction paragraph behind it. When false, replace with a short
"use Read/Glob/Grep/Bash" fallback. The metrics-quality bug
(`per_tool_counts` over-counts) is acknowledged but not fixed in code;
the new `analyze_tool_usage.py` script computes
`succeeded_count = attempted - errored` from events.jsonl as the
source-of-truth column for fair comparisons.

Implication: prior `claude_code_no_plugin` baselines on minimax m2.7
were unaffected; ones on deepseek-v3.2 v2 / gemma-4 should be re-run if
those numbers ever appear in the paper.

### 2. xmllint validation investigation

**Premise**: A meaningful chunk of failures fall in the "F1 schema
hallucination" class (invented element/attribute names). The user
proposed wiring schema validation into the harness.

**Findings**:
- `xmllint --schema $GEOS_SCHEMA input.xml` works perfectly. Errors are
  highly actionable: bad element names get the *expected alternatives*
  listed; missing required attributes get the attribute name; bad
  attribute spellings get the offending attribute.
- The agent already invokes xmllint **91 times across 87 task-runs** in
  ~10% of all tasks without us prompting it explicitly — but the prompt
  buries the mention inside a "Validating Input Files" subsection, the
  schema path is not in the prompt at all, and only ~10% of tasks bite.
- The chromadb is path-scoped to `src/docs/sphinx/`. **87 GEOS rst files
  exist outside that path and are invisible to RAG**, including
  `InputXMLFiles.rst` (which documents xmllint usage). Vanilla CC reads
  these via Glob/Grep; plugin variants do not.

**Three integration paths implemented**:
1. **xmllint-aware primer** (`plugin/GEOS_PRIMER_xmllint.md`) — prominent
   "REQUIRED before declaring done" section with the absolute schema
   path and 3-bullet hint about reading xmllint errors. Activated via
   `--strip-baked-primer --geos-primer-path plugin/GEOS_PRIMER_xmllint.md`.
2. **MCP tool** (`plugin/scripts/xmllint_mcp.py`) — exposes
   `mcp__xmllint__validate_geos_xml(xml_path)`. Wired via the
   `xmllint_mcp_enabled: True` flag in the agent dict.
3. **Stop-hook xmllint check** in `plugin/hooks/verify_outputs.py` —
   gated on `GEOS_HOOK_XMLLINT=1`. After the existing parse check, runs
   `xmllint --schema` per file and blocks with formatted errors as
   feedback (capped at 8 errors/file × 4 files). Counts toward the
   existing retry budget.

The container `geos-eval` was rebuilt to add `libxml2-utils`. Verified
the hook end-to-end on a known-bad model output (`m4g_s2 /
pknViscosityDominated_base.xml`); the hook correctly blocks with
structured feedback identifying the hallucinated
`CompressibleSolidCappedPlatesPorosity` element and the missing
`defaultViscosity` attribute.

### 3. Refactor of `scripts/run_experiment.py`

Single 3500-line file → `src/runner/` package with 17 modules (largest
584 lines). Long prompt strings extracted to `src/runner/prompts/*.txt`;
dashboard HTML to `src/runner/dashboard/template.html`. The CLI shim at
`scripts/run_experiment.py` is now 16 lines.

Verified by:
- SHA-256 fingerprint of `build_system_prompt` output across 4 agents
  matches pre-refactor baseline byte-for-byte.
- `--help` byte-identical to baseline.
- `--dry-run` docker command lines for 3 agents identical to baseline
  (modulo timestamps).
- 16 module imports clean.

Followup merge: the leftover `src/runner/contamination.py` was absorbed
into the new package; the awkward `repo3_runner` working name was
renamed to `runner`.

### 4. Cross-run analyses

Two new analysis scripts run across all 908 completed task-runs:

**`scripts/analysis/analyze_file_access.py`** — categorizes Read /
Glob / Grep / Bash invocations per (agent, run, task), buckets file
paths into rst_sphinx / rst_nonsphinx / xml_input_files / xml_workspace
/ xsd_schema / python / other.

**`scripts/analysis/analyze_tool_usage.py`** — re-derives tool counts
from events.jsonl, splits attempted vs succeeded, flags discrepancies
with status.json (25 found out of 908 runs, all minor).

**Headline findings (4-condition comparison, minimax m2.7, 17-task test set)**:

| Condition | Tool calls/task | RST sphinx/task | RST non-sphinx/task | XML examples/task | xmllint/task |
|---|---:|---:|---:|---:|---:|
| CC (vanilla) | 37.1 | 1.55 | **0.55** | **8.1** | 0.06 |
| CC + RAG | 31.1 | 0.00 | 0.00 | 0.1 | 0.06 |
| CC + RAG + hook | 27.9 | 0.01 | 0.00 | 1.1 | 0.07 |
| CC + RAG + hook + memory (M1-u) | 23.9 | 0.02 | 0.00 | **2.4** | 0.08 |

Key observations:
- **Vanilla CC discovers non-sphinx rst files** that plugin variants miss.
  Plugin variants are anchored to whatever the indexer covered — the
  chromadb gap is a structural confound for the plugin-vs-vanilla
  comparison.
- **Memory primer doubles XML example reads** (1.1 → 2.4) because the
  primer names specific reference XMLs.
- **xmllint usage is harness-independent** at ~0.06-0.08/task; baking it
  in (hook or tool) amplifies an existing behavior.
- **Vanilla CC uses Bash for filesystem search** ~3× more than the
  dedicated Glob/Grep tools (find/ls 59% of Bash, grep/rg 26%). Total
  filesystem-search effort: ~15.5 calls/task vs 12.4 Reads/task — the
  agent's main activity is searching, not reading.

### 5. Model migration: minimax → DSv4-flash

DeepSeek released v4-pro and v4-flash. v4-flash is roughly an order of
magnitude cheaper than minimax m2.7 and benchmarked faster
(~75 TPS vs ~40-50).

**The smoketest stalemate**:
- DSv4-flash via OpenRouter — 40-min timeout, **30 OpenRouter
  rate_limit retries** ate ~25 minutes. The model itself is fast; the
  provider was throttling sustained CC sessions.
- Gemma-4-31b — 40-min timeout with 0 retries. Just genuinely slow
  per-turn (~4 min between assistant messages).

**Probe** (`scripts/api_probe.py`) confirmed simple-prompt latency:

| Target | Latency (mean) |
|---|---:|
| `deepseek:deepseek-v4-flash` (direct) | 0.97s |
| `openrouter:deepseek/deepseek-v4-flash` | 1.20s |
| `openrouter:minimax/minimax-m2.7` | 4.60s |

**The fix**: route through DeepSeek's Anthropic-compatible endpoint at
`https://api.deepseek.com/anthropic` with `DEEPSEEK_API_KEY`. Docs:
<https://api-docs.deepseek.com/guides/coding_agents>. No code changes —
just two env vars (`ANTHROPIC_BASE_URL` + `ANTHROPIC_AUTH_TOKEN`).

**Validation**:
- `dsv4flash_direct_smoke` (single-task) — 5m 14s success, 0 retries,
  treesim 0.301 (within minimax variance).
- `dsv4flash_direct_s1` (full 17-task) — **17/17 success, mean treesim
  0.647, 0 retries**. Beats best minimax seed (0.66 mm_noplug_run1)
  within rounding.

### 6. Minimal-primer ablation (botched test, then fixed)

Discovered that the prior `minprimer_run1` (April 20) was a NULL
ablation: AGENTS.md already contained `# GEOS Primer` baked in, and the
`build_system_prompt` guard suppressed any external primer when
AGENTS.md already had one. The minimal primer file was loaded but
discarded — system prompt was byte-identical to the regular condition.

**Fix**: added `--strip-baked-primer` flag that strips the `# GEOS
Primer` block out of AGENTS.md before injection. Then the file passed
via `--geos-primer-path` is actually inlined.

**Real ablation** (single seed, minimax m2.7, vanilla CC):
- Full primer baseline mean treesim (3 seeds): 0.558 (range 0.45-0.66)
- Minimal primer (1 seed): 0.625

Within seed variance — single-seed result is suggestive but not
conclusive. A 3-seed DSv4 follow-up was launched at session end to
disambiguate (see "Open campaigns" below).

The minimal primer is also vanilla-CC-friendly: created
`plugin/GEOS_PRIMER_minimal_vanilla.md` as a copy of the original
minimal primer with the `mcp__geos-rag__search_*` mention replaced by a
"Glob / Grep / Read against /geos_lib/inputFiles/" workflow step. This
prevents the same phantom-tool problem from recurring under the
ablation.

### 7. xmllint ablation cells

Two cells launched on top of CC + RAG + hook + minimax m2.7:

| Cell | Treatment | n_scored | Mean treesim |
|---|---|---:|---:|
| baseline (existing pac1_plug_hook) | none | varies | ~0.50 |
| primer-only (`xmllint_primer_mm_s1`) | xmllint primer + path | 17/17 | 0.556 |
| hook-only (`xmllint_hook_mm_s1`) | hook validates against schema | 17/17 | 0.567 |

Both treatments hit **17/17 completion** vs the baseline's typical
14-16/17 — the strongest signal: schema awareness pushes the agent to
finish authoring rather than ending with broken or absent XML. Single
seed; quality on scored tasks is statistically indistinguishable from
baseline at this n.

## New artifacts (code, configs, primers)

### Source code
- `src/runner/` — full eval-harness package (refactor)
- `scripts/api_probe.py` — multi-provider latency probe
- `scripts/analysis/analyze_file_access.py`
- `scripts/analysis/analyze_tool_usage.py`
- `scripts/analysis/compare_4conditions.py`
- `plugin/scripts/xmllint_mcp.py`
- `plugin/hooks/verify_outputs.py` (extended)
- `run/Dockerfile` (added `libxml2-utils`)

### Primers
- `plugin/GEOS_PRIMER_xmllint.md` — full primer + xmllint-aware section + absolute schema path
- `plugin/GEOS_PRIMER_minimal_vanilla.md` — vanilla-CC-compatible minimal primer

### CLI flags added
- `--strip-baked-primer` (in `runner.cli`) — drops the embedded primer
  out of AGENTS.md so `--geos-primer-path` actually takes effect.

### Agent variants registered (in `src/runner/agents.py`)
- `claude_code_no_plugin_minprimer`
- `claude_code_repo3_plugin_xmllint_primer`
- `claude_code_repo3_plugin_xmllint_hook`
- `claude_code_repo3_plugin_xmllint_all`

### Env vars (passed through to container)
- `GEOS_HOOK_XMLLINT` — enable hook schema validation
- `GEOS_HOOK_SCHEMA_PATH` — override schema path

## Headline result table (everything we know after this session)

Mean treesim, 17-task test set unless noted. Seed counts in parens.

| Condition | Model | n_seeds | Mean treesim | Notes |
|---|---|---:|---:|---|
| Vanilla CC + full primer | minimax m2.7 | 3 | 0.558 ± 0.087 | range 0.45-0.66 |
| Vanilla CC + minimal primer | minimax m2.7 | 1 | 0.625 | within minimax variance |
| Vanilla CC + full primer | DSv4-flash | 1 | 0.647 | 17/17 scored |
| CC + RAG + hook | minimax m2.7 | 4 (existing) | ~0.50 | from prior data |
| CC + RAG + hook + xmllint primer | minimax m2.7 | 1 | 0.556 | 17/17 |
| CC + RAG + hook + xmllint hook | minimax m2.7 | 1 | 0.567 | 17/17 |
| CC + RAG + hook + memory (M1-u) | minimax m2.7 | 3 (existing) | varies | best of plugin variants |

## Open campaigns at end of session

In flight at the time of writing this doc:

- **Primer ablation on DSv4 vanilla CC** — full primer s2/s3 + minimal
  primer s1/s2/s3 (5 campaigns, workers=4 each). Decides which primer
  to anchor the canonical "best" setup on. ETA ~30 min wall.
- **(planned, blocked on the above)** "Best setup" campaign:
  `claude_code_repo3_plugin_xmllint_all` (RAG + hook + xmllint MCP
  tool + xmllint hook + winning primer) at 1 seed minimax + 3 seeds
  DSv4-flash on the 17-task test set.

This document will be updated with those results when they land.

## Open work / followups (not done this session)

- [ ] Brian to confirm whether chromadb indexer is path-scoped (the
      data strongly suggests yes; 87 non-sphinx rst files unindexed).
      Re-index plan if confirmed.
- [ ] Decide whether to fix `per_tool_counts` to exclude
      `is_error: true` tool calls (currently the analysis script
      papers over this; the metric in `status.json` is contaminated).
- [ ] If we want a permanent home for DSv4-direct routing, add an
      `anthropic_base_url` field per agent (currently env-var-driven).
- [ ] Re-run any DSv4 / gemma-4 / deepseek-v3.2-v2 vanilla baselines
      that appear in the paper, with the post-fix harness.
- [ ] Consider the third xmllint cell (combined primer + hook + MCP
      tool) if the primer/hook ablation is inconclusive.
