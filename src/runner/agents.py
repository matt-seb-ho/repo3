"""Agent definitions.

Mirrors the ``AGENTS`` dict from the original ``scripts/run_experiment.py``
(lines 144-419). Kept as a plain dict because ``main()`` mutates each entry's
``results_dir`` at runtime.

acpx_name: the agent identifier passed to ``acpx <agent> exec``
results_dir: where per-task workspaces land on the host
api_key_env: environment variable name for the agent's API key
"""

from __future__ import annotations

from .constants import DATA_DIR, DEFAULT_CLAUDE_MODEL, REPO_ROOT

AGENTS: dict[str, dict] = {
    "claude_code": {
        "runner": "acpx",
        "acpx_name": "claude",
        "results_dir": DATA_DIR / "eval" / "claude_code",
        "api_key_env": "ANTHROPIC_API_KEY",
        "model": None,  # passed via ANTHROPIC_API_KEY; model set by claude itself
    },
    "claude_code_repo3_plugin": {
        "runner": "claude_native",
        "results_dir": DATA_DIR / "eval" / "claude_code_repo3_plugin",
        "api_key_env": "ANTHROPIC_AUTH_TOKEN",
        "model": DEFAULT_CLAUDE_MODEL,
        "requires_rag": True,
        "plugin_enabled": True,
    },
    # xmllint ablation: CC + RAG + hook with the xmllint-aware primer
    # variant inlined. Caller must pass `--strip-baked-primer
    # --geos-primer-path plugin/GEOS_PRIMER_xmllint.md`.
    # The Stop hook still does the existing parse check (NOT schema
    # validation) — this cell isolates the primer treatment.
    "claude_code_repo3_plugin_xmllint_primer": {
        "runner": "claude_native",
        "results_dir": DATA_DIR / "eval" / "claude_code_repo3_plugin_xmllint_primer",
        "api_key_env": "ANTHROPIC_AUTH_TOKEN",
        "model": DEFAULT_CLAUDE_MODEL,
        "requires_rag": True,
        "plugin_enabled": True,
    },
    # xmllint ablation: CC + RAG + hook with the Stop hook also running
    # `xmllint --schema` after the parse check. Caller must export
    # `GEOS_HOOK_XMLLINT=1` in the host env so the runner forwards it
    # into the container. Primer is the standard one (no special path).
    "claude_code_repo3_plugin_xmllint_hook": {
        "runner": "claude_native",
        "results_dir": DATA_DIR / "eval" / "claude_code_repo3_plugin_xmllint_hook",
        "api_key_env": "ANTHROPIC_AUTH_TOKEN",
        "model": DEFAULT_CLAUDE_MODEL,
        "requires_rag": True,
        "plugin_enabled": True,
    },
    # Both treatments stacked + the explicit MCP validate tool. Caller
    # must pass `--strip-baked-primer --geos-primer-path
    # plugin/GEOS_PRIMER_xmllint.md` AND export `GEOS_HOOK_XMLLINT=1`.
    "claude_code_repo3_plugin_xmllint_all": {
        "runner": "claude_native",
        "results_dir": DATA_DIR / "eval" / "claude_code_repo3_plugin_xmllint_all",
        "api_key_env": "ANTHROPIC_AUTH_TOKEN",
        "model": DEFAULT_CLAUDE_MODEL,
        "requires_rag": True,
        "plugin_enabled": True,
        "xmllint_mcp_enabled": True,
    },
    # Same as `_xmllint_all`, but also stacks the M1-u memory cheatsheet
    # (the hero memory primer from the D-008 ablation). This is the
    # "everything stacked" condition — RAG + parse-check hook + xmllint
    # MCP tool + xmllint hook + memory cheatsheet + (caller's choice of
    # base primer via --geos-primer-path). Use to test whether the
    # memory primer's contribution is additive with the xmllint stack.
    "claude_code_repo3_plugin_xmllint_all_m1u": {
        "runner": "claude_native",
        "results_dir": DATA_DIR / "eval" / "claude_code_repo3_plugin_xmllint_all_m1u",
        "api_key_env": "ANTHROPIC_AUTH_TOKEN",
        "model": DEFAULT_CLAUDE_MODEL,
        "requires_rag": True,
        "plugin_enabled": True,
        "xmllint_mcp_enabled": True,
        "cheatsheet_path": REPO_ROOT / "plugin" / "memory_primer_m1u.md",
    },
    # Plugin + frozen pre-learned cheatsheet (memory experiment, D-001).
    # Same as claude_code_repo3_plugin but prepends plugin/cheatsheet.md to
    # the system prompt. Cheatsheet is derived from a held-out train subset
    # of past plugin-run trajectories.
    "claude_code_repo3_plugin_mem": {
        "runner": "claude_native",
        "results_dir": DATA_DIR / "eval" / "claude_code_repo3_plugin_mem",
        "api_key_env": "ANTHROPIC_AUTH_TOKEN",
        "model": DEFAULT_CLAUDE_MODEL,
        "requires_rag": True,
        "plugin_enabled": True,
        "cheatsheet_path": REPO_ROOT / "plugin" / "cheatsheet.md",
    },
    # Short-cheatsheet variant (E05). Strips task-specific advice, keeps
    # only cross-task-invariant rules + explicit stop criterion. Tests
    # whether the E04 failure was cheatsheet content (specificity +
    # instruction competition) or context bloat.
    "claude_code_repo3_plugin_memshort": {
        "runner": "claude_native",
        "results_dir": DATA_DIR / "eval" / "claude_code_repo3_plugin_memshort",
        "api_key_env": "ANTHROPIC_AUTH_TOKEN",
        "model": DEFAULT_CLAUDE_MODEL,
        "requires_rag": True,
        "plugin_enabled": True,
        "cheatsheet_path": REPO_ROOT / "plugin" / "cheatsheet_short.md",
    },
    # Dynamic Cheatsheet (Cumulative) — cheatsheet evolves across batches
    # of test tasks via an LLM curator between batches. Points at a
    # MUTABLE cheatsheet file that the orchestrator (scripts/memory/
    # dc_cu_orchestrate.py) rewrites between batches. Design in XN-004.
    "claude_code_repo3_plugin_memdccu": {
        "runner": "claude_native",
        "results_dir": DATA_DIR / "eval" / "claude_code_repo3_plugin_memdccu",
        "api_key_env": "ANTHROPIC_AUTH_TOKEN",
        "model": DEFAULT_CLAUDE_MODEL,
        "requires_rag": True,
        "plugin_enabled": True,
        "cheatsheet_path": REPO_ROOT / "plugin" / "cheatsheet_dccu.md",
    },
    # Filetree injection (I08) — adds a precomputed index of /geos_lib/
    # inputFiles XML paths to the system prompt so the agent can
    # locate candidate reference XMLs without Glob/Bash find.
    "claude_code_repo3_plugin_tree": {
        "runner": "claude_native",
        "results_dir": DATA_DIR / "eval" / "claude_code_repo3_plugin_tree",
        "api_key_env": "ANTHROPIC_AUTH_TOKEN",
        "model": DEFAULT_CLAUDE_MODEL,
        "requires_rag": True,
        "plugin_enabled": True,
        "cheatsheet_path": REPO_ROOT / "plugin" / "filetree.md",
    },
    # E09: Cheatsheet delivered via /workspace/CHEATSHEET.md instead of
    # system-prompt injection. Tests whether the E04/E05 failure is
    # about delivery channel (system prompt) or content type (cheatsheet).
    "claude_code_repo3_plugin_memws": {
        "runner": "claude_native",
        "results_dir": DATA_DIR / "eval" / "claude_code_repo3_plugin_memws",
        "api_key_env": "ANTHROPIC_AUTH_TOKEN",
        "model": DEFAULT_CLAUDE_MODEL,
        "requires_rag": True,
        "plugin_enabled": True,
        "cheatsheet_path": REPO_ROOT / "plugin" / "cheatsheet_abstract.md",
        "cheatsheet_in_workspace": True,
    },
    # E11: Frozen G-Memory-lite delivered as MCP tool `memory_lookup`.
    # Agent calls memory_lookup(query) to retrieve past-task example
    # files + productive RAG queries. Concrete (not abstract) memory
    # via tool channel (not system prompt). Tests whether memory-as-tool
    # avoids the failure modes of E04/E05/E07.
    "claude_code_repo3_plugin_gmem": {
        "runner": "claude_native",
        "results_dir": DATA_DIR / "eval" / "claude_code_repo3_plugin_gmem",
        "api_key_env": "ANTHROPIC_AUTH_TOKEN",
        "model": DEFAULT_CLAUDE_MODEL,
        "requires_rag": True,
        "plugin_enabled": True,
        "memory_enabled": True,
    },
    # E13: Same memory_mcp tool available, but NO system-prompt instruction
    # about it. Agent discovers memory_lookup from the tool list / docstring
    # alone. Tests whether the memory *instruction* itself was anchoring
    # behavior (E12 still hurt even though threshold blocked bad matches).
    "claude_code_repo3_plugin_gmemsilent": {
        "runner": "claude_native",
        "results_dir": DATA_DIR / "eval" / "claude_code_repo3_plugin_gmemsilent",
        "api_key_env": "ANTHROPIC_AUTH_TOKEN",
        "model": DEFAULT_CLAUDE_MODEL,
        "requires_rag": True,
        "plugin_enabled": True,
        "memory_enabled": True,
        "memory_prompt_hint": False,
    },
    # PAC-1 A4': plug + silent-memory with hook DISABLED. Needed because E18
    # ran before the Stop hook existed AND before AskUserQuestion was removed
    # from the tool list — so E18 vs E24 is confounded by 2 config changes.
    # This agent gives a clean hook-off baseline with current infra.
    "claude_code_repo3_plugin_gmemsilent_nohook": {
        "runner": "claude_native",
        "results_dir": DATA_DIR / "eval" / "claude_code_repo3_plugin_gmemsilent_nohook",
        "api_key_env": "ANTHROPIC_AUTH_TOKEN",
        "model": DEFAULT_CLAUDE_MODEL,
        "requires_rag": True,
        "plugin_enabled": True,
        "memory_enabled": True,
        "memory_prompt_hint": False,
        "stop_hook_enabled": False,
    },
    # --- E20 hook-ablation variants (4 cells; see docs/XN-010, SESSION_HANDOFF
    # 2026-04-21 §5, RN-002). All share the plain-plugin MCP config (geos-rag
    # only) plus the --settings file. The hook is registered via --settings
    # (not --plugin-dir) so the tool list stays identical to E17/E18.
    #
    # C0: hook OFF, no extra tool  →  E17 replicate.
    "claude_code_repo3_plugin_nohook": {
        "runner": "claude_native",
        "results_dir": DATA_DIR / "eval" / "claude_code_repo3_plugin_nohook",
        "api_key_env": "ANTHROPIC_AUTH_TOKEN",
        "model": DEFAULT_CLAUDE_MODEL,
        "requires_rag": True,
        "plugin_enabled": True,
        "stop_hook_enabled": False,
    },
    # C2: hook OFF, noop MCP present  →  isolates tool-list-shape effect.
    "claude_code_repo3_plugin_noop_nohook": {
        "runner": "claude_native",
        "results_dir": DATA_DIR / "eval" / "claude_code_repo3_plugin_noop_nohook",
        "api_key_env": "ANTHROPIC_AUTH_TOKEN",
        "model": DEFAULT_CLAUDE_MODEL,
        "requires_rag": True,
        "plugin_enabled": True,
        "stop_hook_enabled": False,
        "noop_mcp_enabled": True,
    },
    # C4: hook ON + noop MCP  →  interaction check.
    "claude_code_repo3_plugin_noop": {
        "runner": "claude_native",
        "results_dir": DATA_DIR / "eval" / "claude_code_repo3_plugin_noop",
        "api_key_env": "ANTHROPIC_AUTH_TOKEN",
        "model": DEFAULT_CLAUDE_MODEL,
        "requires_rag": True,
        "plugin_enabled": True,
        "noop_mcp_enabled": True,
    },
    # C1 is just the existing claude_code_repo3_plugin (hook ON by default
    # now that --settings wires it in). Kept distinct so the legacy name
    # still points at the canonical "plain plugin" condition.
    # Ablation: same container, same primer, same prompt — but no repo3
    # plugin, no RAG tools, no vector DB. Baseline for measuring the plugin's
    # contribution. /geos_lib is still the filtered (decontaminated) copy.
    "claude_code_no_plugin": {
        "runner": "claude_native",
        "results_dir": DATA_DIR / "eval" / "claude_code_no_plugin",
        "api_key_env": "ANTHROPIC_AUTH_TOKEN",
        "model": DEFAULT_CLAUDE_MODEL,
        "requires_rag": False,
        "plugin_enabled": False,
    },
    # Vanilla CC, but the system prompt's GEOS Primer block is replaced with
    # the much shorter `plugin/GEOS_PRIMER_minimal.md`. Ablation against
    # `claude_code_no_plugin` to measure whether the bulky primer carries its
    # weight. Caller MUST pass `--strip-baked-primer --geos-primer-path
    # plugin/GEOS_PRIMER_minimal.md` for the swap to actually take effect —
    # the AGENTS.md bake-in suppresses the external primer otherwise (see
    # docs/2026-04-27_4condition-file-tool-comparison.md §"minimal primer").
    "claude_code_no_plugin_minprimer": {
        "runner": "claude_native",
        "results_dir": DATA_DIR / "eval" / "claude_code_no_plugin_minprimer",
        "api_key_env": "ANTHROPIC_AUTH_TOKEN",
        "model": DEFAULT_CLAUDE_MODEL,
        "requires_rag": False,
        "plugin_enabled": False,
    },
    # 2026-04-29 build-up ablation matrix: C0 (true vanilla) - C5 (RAG+SR+mem).
    # All variants assume the caller passes --strip-baked-primer with the
    # appropriate --geos-primer-path; results_dir below routes outputs to
    # the dsv4_ablation_2026-04-29 namespace under /data/shared/.
    # C0: true minimal — no plugin, no RAG, no SR hook, absolute-min primer.
    "abl_c0_true_vanilla": {
        "runner": "claude_native",
        "results_dir": DATA_DIR / "eval" / "abl_c0_true_vanilla",
        "api_key_env": "ANTHROPIC_AUTH_TOKEN",
        "model": DEFAULT_CLAUDE_MODEL,
        "requires_rag": False,
        "plugin_enabled": False,
    },
    # C2: minimal primer + SR hook ON, but RAG MCP NOT loaded and no RAG
    # instruction in the system prompt. Plugin is loaded only so --settings
    # carries the Stop hook (verify_outputs.py). Decoupled via rag_enabled.
    "abl_c2_min_sr_no_rag": {
        "runner": "claude_native",
        "results_dir": DATA_DIR / "eval" / "abl_c2_min_sr_no_rag",
        "api_key_env": "ANTHROPIC_AUTH_TOKEN",
        "model": DEFAULT_CLAUDE_MODEL,
        "requires_rag": False,
        "plugin_enabled": True,
        "rag_enabled": False,
        # stop_hook_enabled defaults True
    },
    # C3: minimal primer + RAG, no SR hook.
    "abl_c3_min_rag_no_sr": {
        "runner": "claude_native",
        "results_dir": DATA_DIR / "eval" / "abl_c3_min_rag_no_sr",
        "api_key_env": "ANTHROPIC_AUTH_TOKEN",
        "model": DEFAULT_CLAUDE_MODEL,
        "requires_rag": True,
        "plugin_enabled": True,
        "stop_hook_enabled": False,
    },
    # C4: minimal primer + RAG + SR hook (no xmllint, no memory).
    "abl_c4_min_rag_sr": {
        "runner": "claude_native",
        "results_dir": DATA_DIR / "eval" / "abl_c4_min_rag_sr",
        "api_key_env": "ANTHROPIC_AUTH_TOKEN",
        "model": DEFAULT_CLAUDE_MODEL,
        "requires_rag": True,
        "plugin_enabled": True,
    },
    # C5: C2 + DSv4-distilled M1-u memory primer (cheatsheet).
    # Memory distilled from harvest_c2_dsv4_s1 trajectories on 18 train tasks
    # via gemini-3-flash-preview (M1-u variant, ungrounded).
    "abl_c5_dsv4_mem": {
        "runner": "claude_native",
        "results_dir": DATA_DIR / "eval" / "abl_c5_dsv4_mem",
        "api_key_env": "ANTHROPIC_AUTH_TOKEN",
        "model": DEFAULT_CLAUDE_MODEL,
        "requires_rag": False,
        "plugin_enabled": True,
        "rag_enabled": False,
        "cheatsheet_path": REPO_ROOT / "plugin" / "memory_primer_dsv4_m1u.md",
    },
    # C6: C2 + xmllint hook (no MCP-tool, no RAG). Isolates the xmllint
    # validation hook on top of parse-check-only SR. The agent is NOT told
    # about xmllint via primer — must learn from the hook's block feedback.
    # Caller MUST export GEOS_HOOK_XMLLINT=1 in host env so it's forwarded.
    "abl_c6_xmllint_hook": {
        "runner": "claude_native",
        "results_dir": DATA_DIR / "eval" / "abl_c6_xmllint_hook",
        "api_key_env": "ANTHROPIC_AUTH_TOKEN",
        "model": DEFAULT_CLAUDE_MODEL,
        "requires_rag": False,
        "plugin_enabled": True,
        "rag_enabled": False,
    },
    # C7: C6 + xmllint MCP tool. Agent can voluntarily call
    # mcp__xmllint__validate_geos_xml during XML authoring (vs only after).
    # This is what the user originally meant by "C2 = SR hook (no RAG)".
    # Caller MUST export GEOS_HOOK_XMLLINT=1.
    "abl_c7_xmllint_full_no_rag": {
        "runner": "claude_native",
        "results_dir": DATA_DIR / "eval" / "abl_c7_xmllint_full_no_rag",
        "api_key_env": "ANTHROPIC_AUTH_TOKEN",
        "model": DEFAULT_CLAUDE_MODEL,
        "requires_rag": False,
        "plugin_enabled": True,
        "rag_enabled": False,
        "xmllint_mcp_enabled": True,
    },
    # C8: C7 + RAG. Tests whether RAG helps when xmllint is providing
    # schema feedback (the user's hypothesis: xmllint says "you used
    # X, expected Y" and RAG search_schema looks up Y's spec).
    "abl_c8_xmllint_full_rag": {
        "runner": "claude_native",
        "results_dir": DATA_DIR / "eval" / "abl_c8_xmllint_full_rag",
        "api_key_env": "ANTHROPIC_AUTH_TOKEN",
        "model": DEFAULT_CLAUDE_MODEL,
        "requires_rag": True,
        "plugin_enabled": True,
        "xmllint_mcp_enabled": True,
    },
    # C10: C6 + DSv4-distilled memory cheatsheet.
    # Tests whether memory + xmllint hook compose (memory primes correct
    # vocab, xmllint catches residuals) or cancel (xmllint already
    # catches what memory was trying to prevent).
    "abl_c10_xmllint_hook_mem": {
        "runner": "claude_native",
        "results_dir": DATA_DIR / "eval" / "abl_c10_xmllint_hook_mem",
        "api_key_env": "ANTHROPIC_AUTH_TOKEN",
        "model": DEFAULT_CLAUDE_MODEL,
        "requires_rag": False,
        "plugin_enabled": True,
        "rag_enabled": False,
        "cheatsheet_path": REPO_ROOT / "plugin" / "memory_primer_dsv4_m1u.md",
    },
    # C11: C7 + DSv4-distilled memory cheatsheet.
    "abl_c11_xmllint_full_mem": {
        "runner": "claude_native",
        "results_dir": DATA_DIR / "eval" / "abl_c11_xmllint_full_mem",
        "api_key_env": "ANTHROPIC_AUTH_TOKEN",
        "model": DEFAULT_CLAUDE_MODEL,
        "requires_rag": False,
        "plugin_enabled": True,
        "rag_enabled": False,
        "xmllint_mcp_enabled": True,
        "cheatsheet_path": REPO_ROOT / "plugin" / "memory_primer_dsv4_m1u.md",
    },
    # C9: C2 with the native-plugin-prefix suppressed in user prompt.
    # Isolates the "phantom RAG instruction" effect (the +0.24 surprise
    # from the C0-C5 ablation). Same primer + same plugin loading as C2,
    # only difference is the absence of the "use mcp__geos-rag__* tools"
    # prefix prepended to the user prompt.
    "abl_c9_no_prefix": {
        "runner": "claude_native",
        "results_dir": DATA_DIR / "eval" / "abl_c9_no_prefix",
        "api_key_env": "ANTHROPIC_AUTH_TOKEN",
        "model": DEFAULT_CLAUDE_MODEL,
        "requires_rag": False,
        "plugin_enabled": True,
        "rag_enabled": False,
        "add_native_plugin_prefix": False,
    },
    # -------------------------------------------------------------------------
    # D-008 memory ablation (post-RN-003). All stacked on RAG+SR
    # (plugin_enabled=True, stop_hook_enabled=True-by-default). Each variant
    # delivers memory content via a different path. All are FROZEN at test time.
    # -------------------------------------------------------------------------
    # M-placebo: equivalent-token generic GEOS text, not trajectory-derived.
    # Placebo control per RN-003 P1 #2.
    "claude_code_repo3_plugin_m_placebo": {
        "runner": "claude_native",
        "results_dir": DATA_DIR / "eval" / "claude_code_repo3_plugin_m_placebo",
        "api_key_env": "ANTHROPIC_AUTH_TOKEN",
        "model": DEFAULT_CLAUDE_MODEL,
        "requires_rag": True,
        "plugin_enabled": True,
        "cheatsheet_path": REPO_ROOT / "plugin" / "memory_primer_placebo.md",
    },
    # M1-u: DC-Cu primer (ungrounded). Self-judged cheatsheet distilled from
    # 18 training trajectories via gemini-3-flash-preview (no TreeSim feedback).
    "claude_code_repo3_plugin_m1u": {
        "runner": "claude_native",
        "results_dir": DATA_DIR / "eval" / "claude_code_repo3_plugin_m1u",
        "api_key_env": "ANTHROPIC_AUTH_TOKEN",
        "model": DEFAULT_CLAUDE_MODEL,
        "requires_rag": True,
        "plugin_enabled": True,
        "cheatsheet_path": REPO_ROOT / "plugin" / "memory_primer_m1u.md",
    },
    # M1-g: DC-Cu primer (grounded). Same corpus as M1-u but the distiller
    # was given TreeSim failure-mode labels, weakest-section scores, and
    # dominant-dimension hints. Paired with M1-u for grounding attribution.
    "claude_code_repo3_plugin_m1g": {
        "runner": "claude_native",
        "results_dir": DATA_DIR / "eval" / "claude_code_repo3_plugin_m1g",
        "api_key_env": "ANTHROPIC_AUTH_TOKEN",
        "model": DEFAULT_CLAUDE_MODEL,
        "requires_rag": True,
        "plugin_enabled": True,
        "cheatsheet_path": REPO_ROOT / "plugin" / "memory_primer_m1g.md",
    },
    # M3-g: RB items via in-run MCP tool. Embedding retrieval over the same
    # items served to M4-g. Uses memory_mcp_embed.py with hard-error on
    # missing OPENROUTER_API_KEY (RN-003 P2 #8). Claim C (locus) is weakened
    # due to tool-list-shape confound (RN-003 P2 #5).
    "claude_code_repo3_plugin_m3g": {
        "runner": "claude_native",
        "results_dir": DATA_DIR / "eval" / "claude_code_repo3_plugin_m3g",
        "api_key_env": "ANTHROPIC_AUTH_TOKEN",
        "model": DEFAULT_CLAUDE_MODEL,
        "requires_rag": True,
        "plugin_enabled": True,
        "memory_enabled": True,
        "memory_prompt_hint": False,  # don't advertise the tool; let tool list speak
        "memory_variant": "embed",
        "memory_items_path": REPO_ROOT / "plugin" / "memory_items_m4g.json",
        "memory_embed_index_path": REPO_ROOT / "plugin" / "memory_items_m4g_embeddings.json",
    },
    # M3-g-hinted: same as M3-g (embedding MCP) but with memory_prompt_hint=True.
    # Distinguishes "tool-locus is bad" from "agent doesn't spontaneously use it"
    # per user's 2026-04-22 follow-up request.
    "claude_code_repo3_plugin_m3g_hinted": {
        "runner": "claude_native",
        "results_dir": DATA_DIR / "eval" / "claude_code_repo3_plugin_m3g_hinted",
        "api_key_env": "ANTHROPIC_AUTH_TOKEN",
        "model": DEFAULT_CLAUDE_MODEL,
        "requires_rag": True,
        "plugin_enabled": True,
        "memory_enabled": True,
        "memory_prompt_hint": True,  # CHANGED from False — nudges agent to call memory_lookup
        "memory_variant": "embed",
        "memory_items_path": REPO_ROOT / "plugin" / "memory_items_m4g.json",
        "memory_embed_index_path": REPO_ROOT / "plugin" / "memory_items_m4g_embeddings.json",
    },
    # M4-u: RB items (ungrounded) via external primer injection. Same items
    # format as M4-g but distilled without TreeSim feedback. Paired with
    # M4-g for attribution claim.
    "claude_code_repo3_plugin_m4u": {
        "runner": "claude_native",
        "results_dir": DATA_DIR / "eval" / "claude_code_repo3_plugin_m4u",
        "api_key_env": "ANTHROPIC_AUTH_TOKEN",
        "model": DEFAULT_CLAUDE_MODEL,
        "requires_rag": True,
        "plugin_enabled": True,
        "cheatsheet_path": REPO_ROOT / "plugin" / "memory_primer_m4u.md",
    },
    # M4-g: RB items (grounded) via external primer injection. Hero run.
    "claude_code_repo3_plugin_m4g": {
        "runner": "claude_native",
        "results_dir": DATA_DIR / "eval" / "claude_code_repo3_plugin_m4g",
        "api_key_env": "ANTHROPIC_AUTH_TOKEN",
        "model": DEFAULT_CLAUDE_MODEL,
        "requires_rag": True,
        "plugin_enabled": True,
        "cheatsheet_path": REPO_ROOT / "plugin" / "memory_primer_m4g.md",
    },
    "cursor_composer2": {
        "runner": "acpx",
        "acpx_name": "cursor",
        "results_dir": DATA_DIR / "eval" / "cursor_composer2",
        "api_key_env": "CURSOR_API_KEY",
        "model": "composer-2",
    },
}
