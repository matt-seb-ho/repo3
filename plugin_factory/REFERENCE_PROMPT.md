# SIGA Adaptation Goal Prompt

> Structured version of the original Codex `/goal` prompt that one-shotted the
> GEOS → OpenFOAM adaptation in ~1 hour. The `siga-adapt` skill loads this
> file and fills the `{{...}}` placeholders before driving the four-component
> adaptation.

## Background

You are adapting the **SIGA** four-component template, originally built for the
GEOS multiphysics simulator, to a new simulator: **{{simulator_name}}**.

SIGA is a Claude Code plugin that augments an LLM agent with the four supports
shown to materially help scientific-simulation input-file authoring:

1. **RAG** — a Chroma vector DB with separate collections for navigation
   (concepts/tutorials), technical examples (real input files), and schema
   (authoritative attribute specs). Exposed as MCP tools the agent calls
   before writing.
2. **XML lint tool** — the simulator's own schema/syntax validator wrapped as
   an MCP tool the agent can call mid-turn, *plus* a `PostToolUse` hook that
   re-runs it after every `Write|Edit|MultiEdit` so the agent gets sub-second
   feedback on malformed output.
3. **Memory (primer)** — a short authored document (`<SIM>_PRIMER_*.md`) that
   orients the agent on file layout, idiomatic skeletons, and recommended
   workflow. Multiple variants (minimal / full / xmllint-aware) for ablation.
4. **Self-refinement (end-of-turn verifier)** — a `Stop` hook that runs the
   lint tool against the agent's outputs before allowing the turn to end;
   blocks with structured feedback on parse/schema errors so the agent
   re-enters with a concrete fix prompt.

Reference implementation (read-only): `{{reference_plugin_root}}` (the GEOS
plugin). The four components live at:

- RAG: `scripts/geos_rag_mcp.py`, `skills/geos-rag/SKILL.md`
- Lint: `scripts/xmllint_mcp.py`, `hooks/verify_xml_post_write.py`
- Memory: `GEOS_PRIMER_*.md`, `scripts/memory_mcp.py`, `scripts/memory_mcp_embed.py`
- Self-refine: `hooks/verify_outputs.py`, `hooks/hooks.json`

## Target

Generate a new Claude Code plugin at `{{target_plugin_root}}` named
`{{target_plugin_name}}` that adapts all four components to
**{{simulator_name}}**.

Simulator context provided by the user:

- **Input-file format**: {{input_format}} (e.g. XML, dictionary-style, JSON, YAML)
- **Validator**: {{validator_command}} (e.g. `xmllint --schema X`, `foamDictionary -checkSyntax`)
- **Source repo / docs**: {{simulator_source_path}}
- **Notes from researcher**: {{researcher_notes}}

## The four adaptations

For each component below: **(a)** read the reference implementation in
`{{reference_plugin_root}}`, **(b)** produce the {{simulator_name}}-specific
counterpart in `{{target_plugin_root}}`, **(c)** run the smoke check listed,
**(d)** record what you did in `{{target_plugin_root}}/ADAPTATION_LOG.md`.

### 1. RAG (Chroma collections)

Survey `{{simulator_source_path}}` for analogues to GEOS's three corpora:

- `geos_navigator` — Sphinx RSTs, tutorials, conceptual docs → for
  {{simulator_name}}, look for: {{rag_navigator_hint}}
- `geos_technical` — validated example input files → look for:
  {{rag_technical_hint}}
- `geos_schema` — XSD-derived authoritative attribute specs → look for:
  {{rag_schema_hint}}

Produce `scripts/{{slug}}_rag_mcp.py` modeled on `scripts/geos_rag_mcp.py`:
keep the three-collection structure, rename collections to
`{{slug}}_navigator|technical|schema`, point `DEFAULT_VECTOR_DB_DIR` at a
{{simulator_name}}-appropriate path, and update the docstring + tool
descriptions. Produce `skills/{{slug}}-rag/SKILL.md` modeled on
`skills/geos-rag/SKILL.md` with simulator-appropriate workflow advice.

If {{simulator_name}} does not have a schema-spec corpus (some simulators
don't), say so explicitly in `ADAPTATION_LOG.md` and ship a two-collection
build — do not invent a fake schema.

**Smoke check**: `python scripts/{{slug}}_rag_mcp.py --help` runs without
import errors. Three collections are referenced by name in the code.

### 2. Lint / validator

Identify the simulator's native validator (`{{validator_command}}`). Produce
`scripts/{{slug}}_lint_mcp.py` modeled on `scripts/xmllint_mcp.py`: same
MCP-tool shape (`validate_{{slug}}_input(path: str) -> str`), wrapping the
real validator subprocess. Produce `hooks/verify_input_post_write.py` modeled
on `hooks/verify_xml_post_write.py`: matches `Write|Edit|MultiEdit`, scopes
to `$CLAUDE_PROJECT_DIR/inputs` (or `{{inputs_dir}}` if the simulator has a
convention), parses the file in the cheapest way the format allows, blocks
with a one-line fix hint on failure.

**Smoke check**: hand-craft one invalid input file and confirm the hook
blocks with a useful message. Hand-craft one valid file and confirm it
passes silently.

### 3. Memory (primer)

Read `{{reference_plugin_root}}/GEOS_PRIMER_minimal.md` and
`GEOS_PRIMER_xmllint.md`. Produce `{{target_plugin_root}}/{{SIM}}_PRIMER_minimal.md`
and `{{SIM}}_PRIMER_lint.md` with the same structure but
{{simulator_name}}-specific content:

- *Where things live* — paths inside the container where the simulator's
  examples, docs, and the workspace `inputs/` directory will be.
- *Top-level skeleton* — the canonical empty input file for this simulator.
- *Recommended workflow* — RAG-call order tailored to the simulator's
  authoring task.

The `_lint` variant should additionally call out the validator MCP tool and
encourage pre-end-of-turn validation.

**Smoke check**: a domain reviewer (or you in a fresh read) can follow the
primer's "Recommended workflow" without external context.

### 4. Self-refinement (Stop hook)

Produce `hooks/verify_outputs.py` modeled on the reference. Same env-var
contract (`{{SIM}}_HOOK_INPUTS_DIR`, `{{SIM}}_HOOK_MAX_RETRIES`,
`{{SIM}}_HOOK_DISABLE`, `{{SIM}}_HOOK_VALIDATE`, `{{SIM}}_HOOK_SCHEMA_PATH`).
Same retry-counter pattern. Same JSONL event log. The validator step calls
the same subprocess the lint MCP server calls — share a helper if it makes
sense.

Produce `hooks/hooks.json` wiring `verify_outputs.py` as `Stop` and
`verify_input_post_write.py` as `PostToolUse: Write|Edit|MultiEdit`. Copy
the structure from the reference verbatim; only the script paths change.

**Smoke check**: with the agent producing a malformed file in `inputs/`,
the Stop hook should emit `decision: "block"` with the validator error
verbatim; with a valid file, no output.

## Do-not list

- **Do not** invent validator behavior. If the simulator's validator does
  not exist as a CLI, say so and propose the closest substitute (e.g. a
  Python parse-and-emit check) — do not pretend a fake validator works.
- **Do not** copy GEOS-specific constants (schema path, hard-coded VRAM
  paths, OpenRouter model IDs) into the new plugin. Replace them with
  env-driven defaults appropriate to the new simulator.
- **Do not** ship if any smoke check is red.

## Deliverable

A complete, loadable Claude Code plugin at `{{target_plugin_root}}` with:

- `.claude-plugin/plugin.json` (already scaffolded by `scripts/scaffold.py`)
- `skills/{{slug}}-rag/SKILL.md`
- `scripts/{{slug}}_rag_mcp.py`, `scripts/{{slug}}_lint_mcp.py`
- `hooks/verify_outputs.py`, `hooks/verify_input_post_write.py`, `hooks/hooks.json`
- `{{SIM}}_PRIMER_minimal.md`, `{{SIM}}_PRIMER_lint.md`
- `ADAPTATION_LOG.md` — per-component notes on what was adapted, what was
  substituted, and which smoke checks passed
- `README.md` — how to load the plugin and what env vars it needs
