---
id: RN-006
source: adversarial-reviewer
model: claude-opus
title: "Adversarial code review: minimax X+M pseudo MCP-tool-call leakage path"
date: 2026-05-02
invoked_at: 2026-05-02T00:00:00Z
dag_nodes: []
trigger: "pre-findings"
priority_issues: 1
blocker_for_campaign: true
links:
  evidence_against: []
---

# Adversarial Code Review: minimax × X+M pseudo-MCP-tool-call leakage

## Bottom line up front

**The "training-data prior, not in-prompt suggestion" framing in
`docs/2026-05-03_minimax-pseudo-tool-call-analysis.md` is wrong.** The exact
strings `mcp__geos-rag__search_navigator`, `mcp__geos-rag__search_schema`, and
`mcp__geos-rag__search_technical` are injected into the **user prompt** of every
autocamp_F4 (X+M) run via `src/runner/prompts/native_plugin_prefix.txt`. They
are also injected into the **system prompt** via
`src/runner/prompts/rag_instructions.txt` whenever `rag_enabled=True` — and even
when `rag_enabled=False`, the user-prompt prefix still fires because the
prefix gate in `orchestrator.py:267` keys off `enable_plugin`, not `_rag_on`.

minimax did not pattern-complete from a generic Anthropic MCP prior. It
emitted those three exact tool names because **the harness literally asked it
to**, in the user-prompt text that is concatenated to the task spec. The doc's
grep for `geos-rag` was performed against `run/AGENTS.md`,
`plugin/GEOS_PRIMER_contract.md`, and `plugin/memory_primer_dsv4_m1u.md` only
— it did not include the user-prompt prefix.

This is a P1 finding. It invalidates the doc's framing and its prescription.
The proposed fix (Option A: `--anti-pseudo-mcp-block` disclaimer) papers over
the symptom while leaving the **command** to call those tools intact, which
explains the partial recovery (3/17 still fail).

## Scope

Files I read line-by-line:

- `/home/matt/sci/repo3/src/runner/prompts/__init__.py` — the prompt assembler
- `/home/matt/sci/repo3/src/runner/prompts/native_plugin_prefix.txt` — the injected user-prompt prefix
- `/home/matt/sci/repo3/src/runner/prompts/rag_instructions.txt` — the RAG-enabled system-prompt block
- `/home/matt/sci/repo3/src/runner/prompts/rag_vanilla.txt` — the RAG-disabled system-prompt block
- `/home/matt/sci/repo3/src/runner/prompts/missing_rag_disclaimer.txt` — the Option-A disclaimer text
- `/home/matt/sci/repo3/src/runner/orchestrator.py` (lines 100-300) — agent dispatch + prompt assembly
- `/home/matt/sci/repo3/src/runner/docker_cmd.py` — the `claude` invocation
- `/home/matt/sci/repo3/src/runner/agents.py` — autocamp_F4 cell config
- `/home/matt/sci/repo3/plugin/.claude-plugin/plugin.json` — plugin manifest
- `/home/matt/sci/repo3/plugin/skills/geos-rag/SKILL.md` — skill metadata
- `/home/matt/sci/repo3/plugin/scripts/geos_rag_mcp.py` — MCP server (line numbers only)
- `/home/matt/sci/repo3/docs/2026-05-03_minimax-pseudo-tool-call-analysis.md` — the doc under audit

Failed-run artefacts I read:

- `…/cross_model_2026-05-03/minimax_minimax-m2.7/autocamp_F4/minimax_minimax-m2.7_F4_s1/TutorialSneddon/events.jsonl` (system/init + first assistant message)
- `…/TutorialSneddon/status.json` (pseudo_tool_counts, mcp_server_statuses)
- `…/TutorialSneddon/eval_metadata.json` (plugin_enabled, mcp_config_path)
- `…/TutorialSneddon/claude_mcp_config.json` (only xmllint registered)
- `…/minimax_minimax-m2.7_F4_disclaim_s1/{TutorialSneddon,ExampleThermalLeakyWell,buckleyLeverettProblem,kgdExperimentValidation}/status.json`

## Findings

### P1: User-prompt prefix injects the three tool names verbatim, even when RAG is disabled   [BLOCKER for the doc's framing]

**Location 1:** `src/runner/prompts/native_plugin_prefix.txt:1`

Verbatim (the entire file is one paragraph):

```
Do not call the Skill tool. Use the GEOS RAG MCP tools directly:
mcp__geos-rag__search_navigator, mcp__geos-rag__search_schema, and
mcp__geos-rag__search_technical. Before writing XML, call at least one
of the plugin RAG tools: search_navigator, search_schema, or
search_technical.
```

**Location 2:** `src/runner/orchestrator.py:267-271`

```python
_add_prefix = bool(agent.get("add_native_plugin_prefix", enable_plugin))
if _add_prefix:
    native_prompt = f"{native_plugin_prefix()}{prompt}"
else:
    native_prompt = prompt
```

**Location 3:** `src/runner/agents.py:614-625` (autocamp_F4 / X+M cell)

```python
"autocamp_F4": {
    ...
    "requires_rag": False,
    "plugin_enabled": True,
    "rag_enabled": False,
    "stop_hook_enabled": False,
    "xmllint_mcp_enabled": True,
    "cheatsheet_path": REPO_ROOT / "plugin" / "memory_primer_dsv4_m1u.md",
},
```

`autocamp_F4` does **not** set `add_native_plugin_prefix`. The orchestrator's
default in line 267 is `enable_plugin`, which is `True` here (because
`plugin_enabled=True` even though `rag_enabled=False`). Therefore the user
prompt sent to minimax begins with the eight-line block above, which **names
the three pseudo-call tool names** as imperatives ("Use the GEOS RAG MCP
tools directly: …"), and then redundantly tells the agent it MUST call at
least one of them before writing XML.

**Direct evidence the prefix was active:** `eval_metadata.json` for the failed
TutorialSneddon run shows `plugin_enabled: true`. The agent's first
assistant message (`events.jsonl` line 2) emits exactly the three tools in
exactly the order listed in the prefix:

```
<minimax:tool_call>
<invoke name="mcp__geos-rag__search_navigator">...</invoke>
<invoke name="mcp__geos-rag__search_schema">...</invoke>
<invoke name="mcp__geos-rag__search_technical">...</invoke>
</minimax:tool_call>
```

This is not pattern completion from a training prior. The model was instructed
to use these tools and complied, in the syntax minimax thinks tool calls take
on this provider (Together-routed minimax-m2.7 emits `<minimax:tool_call>`
wrappers because that is its native function-calling format). The model has
no way to know that `--strict-mcp-config` is set or that the geos-rag server
is absent — it just reads the prompt.

**Why it invalidates the doc's claim:**

The doc (lines 73-89) explicitly states:

> *Not in any prompt or cheatsheet*: grep for geos-rag|mcp__geos|search_navigator|search_schema|search_technical across run/AGENTS.md, plugin/GEOS_PRIMER_contract.md, and plugin/memory_primer_dsv4_m1u.md returns zero matches. None of the text the agent saw in its system prompt mentions any geos-rag tool name.

The grep was done against the wrong files. The agent's prompt content is
the **concatenation** of:

1. system prompt = AGENTS.md + primer + cheatsheet + rag_instructions (or
   rag_vanilla) + memory + supervisor + real_tool_tail + (optional disclaimer)
2. user prompt = native_plugin_prefix + task spec

The doc grep'd subset (1) only and missed subset (2). Subset (2) contains the
exact three strings.

**Additionally — for a sibling RAG-enabled cell (e.g., autocamp_F3 or any
F\* with `rag_enabled=True`)** the names also leak via the **system prompt** at
`src/runner/prompts/rag_instructions.txt:1`:

```
GEOS RAG instructions: Use the MCP tools named mcp__geos-rag__search_navigator,
mcp__geos-rag__search_schema, and mcp__geos-rag__search_technical before
answering questions about GEOS XML syntax, examples, schema, or documentation.
…
```

For F4 specifically `rag_enabled=False`, so `_RAG_INSTRUCTIONS_VANILLA`
(rag_vanilla.txt) is used in the system prompt — that file does not name
the tools. Good. But the user-prompt prefix still fires. Bad.

**Recommended action:**

Two-part fix.

1. **Make `add_native_plugin_prefix` track `rag_enabled`, not `plugin_enabled`.**
   Change `orchestrator.py:267` from:

   ```python
   _add_prefix = bool(agent.get("add_native_plugin_prefix", enable_plugin))
   ```

   to:

   ```python
   _add_prefix = bool(agent.get("add_native_plugin_prefix", _rag_on))
   ```

   This is the conceptually correct gate — the prefix's content is "use the
   RAG MCP tools", which is only meaningful when RAG MCP is registered.
   Setting `rag_enabled=False` should silence it. The current behaviour is
   what the orchestrator comment itself describes as "confusing" (line 264-265).

2. **Re-run minimax × X+M with the fix in place** and the disclaimer OFF.
   The expectation is that fa0 recovers cleanly without needing the disclaimer
   workaround. If pseudo-calls still appear at all, that residual is the
   genuine training-prior signal and the doc's training-data framing kicks
   in for that residual only.

   If the user wants to preserve cross-model parity with the original X+M
   semantics on DSv4 (where the prefix was always on), then DSv4's X+M cell
   has the same issue but DSv4 is disciplined enough about tool lists not to
   pseudo-call. The fairness consideration is to fix the bug for **all**
   backbones, accept that the resulting "X+M" cell has slightly different
   semantics from the original, and re-run DSv4 too. This is the honest
   apples-to-apples comparison the cross-model panel is supposed to provide.

### P2: Disclaimer text reinforces the same channel rather than removing it

**Location:** `src/runner/prompts/missing_rag_disclaimer.txt:5-8`

```
The following MCP tools are NOT registered and NOT available in this configuration:
- `mcp__geos-rag__search_navigator`
- `mcp__geos-rag__search_schema`
- `mcp__geos-rag__search_technical`
```

**Why it matters:**

The Option-A disclaimer adds the SAME three strings to the system prompt with
a "do not call" wrapper, while the user prompt continues to say "Use the GEOS
RAG MCP tools directly: <three names>". The agent now sees both messages.
For minimax, this is a contradictory instruction: the user prompt says "use",
the system prompt says "do not call". The recovery from 0.392 → 0.711 is
explained by minimax mostly resolving the contradiction in favour of "do not
call", but not always — hence the residual 3/17 failures
(ExampleThermalLeakyWell, buckleyLeverettProblem, kgdExperimentValidation).

I verified the residual: each of those three disclaim-run status.json files
shows non-empty `pseudo_tool_counts` and `status: failed_no_outputs`. So the
disclaimer is fighting an upstream injection of the same names, not removing
the names.

**Recommended action:**

Apply the P1 fix first. After the fix, the disclaimer becomes either
unnecessary (if pseudo-calls go to zero) or a much narrower targeted patch (if
a small training-prior residual remains). Either way, the right intervention
is **subtraction** of the prefix, not **addition** of the disclaimer.

### P3: The doc's training-prior section is unfalsifiable as written

**Location:** `docs/2026-05-03_minimax-pseudo-tool-call-analysis.md` lines 95-103

The doc speculates that minimax emits these names because of generic
Claude-Code MCP-namespace priors and the suspicious specificity of
"navigator/schema/technical". With the P1 finding, this section becomes a
post-hoc rationalisation of an artefact: the names ARE in the prompt, the model
ISN'T extrapolating, and the specificity is straightforwardly the file content
of `native_plugin_prefix.txt`.

**Recommended action:**

The doc needs a substantial rewrite. Suggested replacement narrative:

> The X+M cell silently injects `Use the GEOS RAG MCP tools directly:
> mcp__geos-rag__search_navigator, …, search_technical` into the **user
> prompt** via `src/runner/prompts/native_plugin_prefix.txt`, gated on
> `plugin_enabled` rather than `rag_enabled`. minimax-m2.7's pseudo-call
> behaviour is direct compliance with this instruction, expressed in
> minimax's native `<minimax:tool_call>` function-calling syntax. DSv4-flash
> and gemini do not pseudo-call because they discipline their tool emissions
> against the runtime tool list — but that is an instruction-following
> robustness property, not training-prior absence. The X+M factor is
> non-orthogonal to the prefix bug; the cross-model panel should be re-run
> after the prefix is gated on `rag_enabled`.

## Clean checks (what I verified and found OK)

- **MCP config truly registers only xmllint.** Read
  `claude_mcp_config.json` for the failed run: `mcpServers: {xmllint: {…}}`
  only. No geos-rag entry. So the agent's `system/init` event correctly
  reflects the registered server set; that's not the leakage path.
- **plugins: [] in system/init.** Confirmed via events.jsonl line 1. Claude
  Code's plugin auto-discovery from `CLAUDE_PLUGIN_ROOT=/plugins/repo3` is
  suppressed by `--strict-mcp-config`. Skill SKILL.md contents are NOT being
  injected by Claude Code into the system prompt for this run. So path (b) in
  the dispatch prompt — Claude Code's own plugin metadata leakage — is ruled
  out as the source. The leak is in OUR code, not Claude Code's.
- **Plugin manifest contents.** `plugin/.claude-plugin/plugin.json` does
  contain `"geos-rag"` as the mcpServers key, but the plugin loader is gated
  by `--strict-mcp-config` + `--mcp-config <our-file>` and is therefore
  unused. plugin.json's `mcpServers.geos-rag` does not surface to the agent.
- **rag_vanilla.txt is clean.** When `rag_enabled=False`,
  `_RAG_INSTRUCTIONS_VANILLA` is the system-prompt block. It does not name
  any geos-rag tool. The system prompt for autocamp_F4 is therefore clean of
  these strings — only the user prompt is contaminated.
- **system_prompt for F4 does not contain the names.** I traced
  `build_system_prompt` with the F4 args (rag_enabled=False, memory_enabled
  False, supervisor_enabled False) and the resulting concatenation has no
  occurrences of `geos-rag`, `search_navigator`, `search_schema`, or
  `search_technical`. So it is precisely the **user-prompt prefix** that is
  the channel.
- **MCP server self-introspection (item f) is irrelevant here.** The minimax
  pseudo-call appears in turn 1 with zero prior tool calls; the model never
  invokes the geos-rag MCP server (which isn't registered) and never reads any
  file describing it. So even if `geos_rag_mcp.py` had a list-tools
  introspection endpoint readable from the container, it would not matter for
  this leakage path. (For completeness: `geos_rag_mcp.py:199, 232, 271`
  defines the three functions, but they're only reachable via MCP RPC, which
  isn't connected.)
- **AGENTS.md and primer are clean.** I re-grep'd
  `run/AGENTS.md`, `plugin/GEOS_PRIMER_contract.md`,
  `plugin/memory_primer_dsv4_m1u.md` for `geos-rag|search_navigator|search_schema|search_technical`
  — zero matches. The doc's grep was correct as far as it went; it just didn't
  include the user-prompt prefix file.

## Overall assessment

- **Blocker for campaign?** Yes for the cross-model story specifically. The
  current minimax × X+M numbers (0.392 raw, 0.711 disclaim) are measured on
  a contaminated prompt. The doc's prescription (Option A disclaimer) is a
  workaround that addresses the symptom by adding a contradictory instruction;
  it leaves the underlying injection intact, which is why 3/17 tasks still
  pseudo-call. Until the orchestrator gate is fixed and re-run, the cell's
  minimax number is uninterpretable: it is half "X+M without RAG" and half
  "X+M told to use absent RAG tools".
- **Confidence the corrected claim ('the harness instructed minimax to call
  the tools that don't exist') is valid:** High. Code path is direct
  (`agents.py` cell config → `orchestrator.py:267-269` →
  `prompts/__init__.py:204-206` → `native_plugin_prefix.txt` content), and
  the failed run's first-turn output mirrors the prefix file's tool ordering
  exactly.
- **Most likely undiscovered failure mode:** That the same prefix bug
  contaminates **every** `plugin_enabled=True, rag_enabled=False` cell
  retroactively, not just minimax X+M. The cells I see with that combo:
  `abl_c2_min_sr_no_rag`, `abl_c5_dsv4_mem`, `abl_c6_xmllint_hook`,
  `abl_c7_xmllint_full_no_rag`, `abl_c10_xmllint_hook_mem`,
  `abl_c11_xmllint_full_mem`, `autocamp_F2`, `autocamp_F4`, `autocamp_F6`,
  `autocamp_F8`, `autocamp_F11`, `ia_F4_noninteractive`, `ia_F0_interactive`,
  `ia_F4_interactive`, `ia_F0_interactive_v1`, `ia_F4_interactive_v1`. All of
  these have been telling DSv4 to "use the GEOS RAG MCP tools directly" while
  not registering them. DSv4 was disciplined enough not to pseudo-call, so the
  bug was invisible — but the agent may have wasted turns trying real
  `tool_use` invocations, getting "tool not found" errors, and adapting. Worth
  re-running at least the `autocamp_F2/F4/F6/F8` cells under the corrected
  gate to check whether DSv4's published numbers move; if they do, the
  paper's main-effects analysis (`M=+0.004, X=+0.007, S=-0.003, R=-0.033`)
  needs revision. The `R=-0.033` main effect in particular is suspicious —
  if R+ cells got the prefix legitimately and R- cells got it spuriously,
  the contrast is closer to "RAG-tools-with-server vs RAG-tools-without-server"
  than to "RAG vs no-RAG", and the negative R coefficient may partly be
  measuring "agent gets stuck trying to call a missing server".

  Cells that explicitly opt out via `add_native_plugin_prefix=False`
  (`abl_se_round`, `abl_c9_no_prefix`, `autocamp_SE`, `autocamp_v4`) are
  clean. Note in particular: `abl_c9_no_prefix` was created precisely to
  isolate "the +0.24 surprise from the C0-C5 ablation" caused by the
  prefix — so the team has previously detected that this prefix has a
  measurable effect. That effect on minimax is catastrophic; on DSv4 it is
  evidently smaller but non-zero. The full-fleet re-run is warranted.
