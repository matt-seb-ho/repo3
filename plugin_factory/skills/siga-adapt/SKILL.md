---
name: siga-adapt
description: Adapt the SIGA four-component template (RAG, lint, primer, end-of-turn verifier) to a new scientific simulator. Use when a researcher wants to create a SIGA-style Claude Code plugin for a simulator other than GEOS.
---

You are driving an end-to-end adaptation of the SIGA plugin to a new
simulator. This is the analogue of what the original GEOS → OpenFOAM port
did in one Codex `/goal` invocation, but structured so each of the four
components is adapted, smoke-tested, and logged in turn.

## Inputs you need from the researcher

Ask up front (one consolidated question, not four):

1. **Simulator name** — the display name (e.g. `OpenFOAM`, `LAMMPS`, `MOOSE`).
2. **Source repo / docs path** — where the simulator's source, examples, and
   docs live on disk. You'll be reading this for RAG corpora + lint
   discovery + primer authoring.
3. **Input-file format** — XML / dictionary-style / JSON / YAML / Python /
   custom.
4. **Native validator** — the CLI or library call the simulator uses to
   check a draft input file (e.g. `xmllint --schema X` for GEOS,
   `foamDictionary -checkSyntax` for OpenFOAM, or "none — propose one").
5. **Researcher notes** — anything else that constrains the adaptation
   (e.g. "no schema corpus exists", "validator is flaky on Windows").

Also confirm:

- **Reference plugin path** — defaults to `../plugin/` relative to this
  plugin. Verify it contains `.claude-plugin/plugin.json` with
  `name: repo3-plugin`. If not, ask.
- **Target plugin path** — defaults to `../plugin_<slug>/` (sibling to
  the reference plugin).

## Workflow

### Phase 0 — Orient

1. Confirm `${CLAUDE_PLUGIN_ROOT}` resolves to the siga-factory plugin
   directory. The reference GEOS plugin should be at `${CLAUDE_PLUGIN_ROOT}/../plugin`.
2. Read `${CLAUDE_PLUGIN_ROOT}/REFERENCE_PROMPT.md` — it is the structured
   version of the original Codex prompt and lists the exact deliverables.
3. Read the reference plugin's four-component anchor files so you know what
   you're adapting:
   - `${CLAUDE_PLUGIN_ROOT}/../plugin/scripts/geos_rag_mcp.py`
   - `${CLAUDE_PLUGIN_ROOT}/../plugin/scripts/xmllint_mcp.py`
   - `${CLAUDE_PLUGIN_ROOT}/../plugin/hooks/verify_outputs.py`
   - `${CLAUDE_PLUGIN_ROOT}/../plugin/hooks/verify_xml_post_write.py`
   - `${CLAUDE_PLUGIN_ROOT}/../plugin/GEOS_PRIMER_minimal.md`
   - `${CLAUDE_PLUGIN_ROOT}/../plugin/GEOS_PRIMER_xmllint.md`
   - `${CLAUDE_PLUGIN_ROOT}/../plugin/skills/geos-rag/SKILL.md`
   - `${CLAUDE_PLUGIN_ROOT}/../plugin/hooks/hooks.json`

### Phase 1 — Scaffold the target plugin

Run the scaffolder. It creates the directory tree, `plugin.json`, and
stubbed files marked `raise NotImplementedError` so anything that tries to
load the plugin before adaptation fails loudly.

```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/scaffold.py \
    --simulator "<Simulator Display Name>" \
    --target <path/to/plugin_simulator>
```

If the target already exists with a `plugin.json`, ask the researcher
before passing `--force`.

### Phase 2 — Survey the simulator source

Before adapting, build a one-paragraph map of the target simulator:

- Where are example/validated input files? (analogue of
  `/geos_lib/inputFiles/`)
- Where are tutorial / conceptual docs?
- Is there a schema / authoritative attribute spec? If not, note it — you
  will ship a two-collection RAG instead of three.
- What does the simulator validate against? Locate the validator binary
  and try `--help` once to confirm the invocation.

Write this paragraph into `ADAPTATION_LOG.md` under "Phase 2 survey" — it
grounds every later decision.

### Phase 3 — Adapt the four components, one at a time

Do these in the order below. **After each, run its smoke check before
moving on.** If a smoke check fails, fix in place — do not push errors
downstream.

#### 3a. RAG MCP + skill

- Copy `scripts/geos_rag_mcp.py` → `scripts/<slug>_rag_mcp.py`. Rename
  collections (`geos_navigator` → `<slug>_navigator`, etc.), update the
  `DEFAULT_VECTOR_DB_DIR`, rewrite the module docstring, and update tool
  descriptions to talk about this simulator's domain.
- Copy `skills/geos-rag/SKILL.md` → `skills/<slug>-rag/SKILL.md`. Replace
  the GEOS-specific workflow paragraph with one tailored to this
  simulator (which RAG call to make first, what authoring pattern to
  follow).
- Smoke: `python scripts/<slug>_rag_mcp.py --help` runs without import
  errors. Grep the file: three (or two — see survey) collection names
  appear. No stray `geos_` strings remain.

#### 3b. Lint MCP + PostToolUse hook

- Copy `scripts/xmllint_mcp.py` → `scripts/<slug>_lint_mcp.py`. Replace
  the `xmllint --schema` subprocess invocation with whatever
  `<validator_command>` the researcher provided. Rename the exposed tool
  to `validate_<slug>_input`. Keep the path-resolution helper
  (`/workspace`, `/workspace/inputs`, cwd fallback).
- Copy `hooks/verify_xml_post_write.py` → `hooks/verify_input_post_write.py`.
  Replace the XML-specific parse step with whatever cheap parse-test the
  target format supports (e.g. `yaml.safe_load`, `pyfoam parse`, or
  shelling out to the validator). Keep the env-var contract
  (`<SIM>_HOOK_*`) and the JSONL event log.
- Update `hooks/hooks.json` so the `PostToolUse` matcher targets the
  right script path.
- Smoke: hand-craft a known-bad input file in the target plugin's
  `inputs/` test directory and confirm the hook returns
  `decision: "block"` with a useful one-line hint. Hand-craft a valid
  file and confirm it passes silently.

#### 3c. Primer (memory)

- Copy `GEOS_PRIMER_minimal.md` → `<SIM>_PRIMER_minimal.md`. Rewrite each
  section for the new simulator:
  - *Where things live* — the paths from Phase 2's survey.
  - *Top-level skeleton* — the canonical empty input file. Verify by
    reading one real example from the simulator's source.
  - *Recommended workflow* — RAG-call order tailored to this simulator.
- Copy `GEOS_PRIMER_xmllint.md` → `<SIM>_PRIMER_lint.md`. Add the
  lint-tool-aware workflow: "before ending your turn, call
  `mcp__<slug>__validate_<slug>_input` on every file you produced."
- Do not invent simulator behavior. If a section in the GEOS primer talks
  about a concept that has no analogue (e.g. GEOS's `<Solvers>` block has
  no parallel in some simulators), say so explicitly rather than
  fabricating a fake one. The primer's value is being right.
- Smoke: a fresh reader (you, in a separate read pass) can follow the
  "Recommended workflow" section without external context.

#### 3d. Self-refinement (Stop hook)

- Copy `hooks/verify_outputs.py` → `hooks/verify_outputs.py` in the new
  plugin. Replace `GEOS_HOOK_*` env vars with `<SIM>_HOOK_*`. Replace the
  XML parse + `xmllint --schema` step with the same validator the lint
  MCP uses (share a helper module if it's worth it). Keep the retry
  counter, the JSONL event log, and the `decision: "block"` shape.
- Update `hooks/hooks.json` so the `Stop` hook points at the right
  script and the description names this simulator.
- Smoke: produce a malformed `inputs/` file and run the Stop hook
  manually (`echo '{}' | python hooks/verify_outputs.py`) — confirm it
  blocks with the validator error. Produce a valid file and confirm it
  exits cleanly.

### Phase 4 — Final smoke test

1. From the new plugin's directory: `claude --plugin-dir .` should load
   without errors.
2. Inside Claude Code: `/reload-plugins`, then check that
   `/<slug>-plugin:<slug>-rag` is listed.
3. Run a tiny end-to-end: ask the agent to author one trivial input file
   for this simulator with the plugin loaded. Confirm at minimum:
   - The agent calls the RAG tools (visible in tool-use trace).
   - The PostToolUse hook fires after `Write` (visible in the JSONL event log).
   - The Stop hook validates before ending the turn.

### Phase 5 — Document

Update `ADAPTATION_LOG.md` with, for each component:

- **What was kept verbatim** (e.g. retry-counter pattern, JSONL log shape)
- **What was substituted** (e.g. `xmllint --schema` → `foamDictionary -checkSyntax`)
- **What was dropped or stubbed** (e.g. "no schema corpus exists for this
  simulator; RAG ships with two collections, not three")
- **Smoke-check result** (pass / fail + how confirmed)

Then update the target plugin's `README.md` with the env vars it needs
(`<SIM>_HOOK_DISABLE`, `<SIM>_HOOK_SCHEMA_PATH`, `<SIM>_VECTOR_DB_DIR`,
etc.) and how to load it.

## Failure modes to watch for

- **Invented validator**: if the simulator has no native validator and the
  researcher said so, do not write a fake one. Document the gap and ship
  the parse-only PostToolUse hook + a Stop hook that does the same parse.
  Note this prominently in `ADAPTATION_LOG.md` — it materially affects
  what claims a paper can make.
- **Copied GEOS constants**: grep the final plugin for `geos`, `GEOS`,
  `/geos_lib`, `qwen/qwen3-embedding-8b` (only if the embedding model
  changes), and the GEOS schema path. Anything that survives without
  being explicitly chosen is a bug.
- **Half-adapted skill metadata**: the `name:` field in `SKILL.md` must
  match the directory name, and the `description:` must mention the new
  simulator. The plugin name in `plugin.json` should match the directory
  name minus the `plugin_` prefix.
- **Skipped smoke checks**: do not move to the next component until the
  current one's smoke check passes. The original Codex one-shot had "a
  few bugs here and there" — explicit per-component smoke-testing is the
  cheapest way to catch them while context is fresh.

## When you are done

Hand the researcher:

1. The path to the new plugin directory.
2. The contents of `ADAPTATION_LOG.md` (paste it inline so they can review
   without opening the file).
3. The output of the final end-to-end smoke test.
4. A short list of any places you stubbed (`raise NotImplementedError`
   should not appear in any shipped file — flag any that remain).
