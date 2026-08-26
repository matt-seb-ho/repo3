# siga-factory

Claude Code plugin that adapts the **SIGA four-component template** (RAG +
lint MCP + memory primer + end-of-turn verifier) to a new scientific
simulator. Companion to the GEOS-specific `plugin/` in this repo — that is
the reference implementation; this is the meta-tool that ports it.

The structured workflow that drives the adaptation lives in
`REFERENCE_PROMPT.md` and is executed by the `siga-adapt` skill.

## Background

The GEOS SIGA plugin (`../plugin/`) bundles four supports that materially
improve LLM agent performance on simulation input-file authoring:

1. **RAG** — Chroma vector DB with `navigator | technical | schema`
   collections, exposed as MCP tools.
2. **Lint tool** — wraps `xmllint --schema` as both an MCP tool (agent can
   pre-validate) and a `PostToolUse` hook (sub-second feedback after each
   `Write|Edit|MultiEdit`).
3. **Primer (memory)** — short authored document that orients the agent on
   file layout, idiomatic skeletons, and recommended RAG-call order.
4. **End-of-turn verifier** — `Stop` hook that runs the validator and
   blocks turn-end on parse or schema errors, with structured feedback.

Adapting this to a new simulator (OpenFOAM, LAMMPS, MOOSE, …) was first done
by hand: a single Codex `/goal` prompt that one-shotted the port in about an
hour with a few bugs to clean up. The `siga-adapt` skill is the structured
form of that prompt, with per-component smoke checks so the bugs are caught
while context is fresh.

## Requirements

- This `plugin_factory/` directory and the reference `plugin/` directory at
  the same parent (i.e. clone the full repo3 tree).
- A target simulator's source / docs / examples on disk and accessible to
  read.
- The simulator's native validator command (or honest acknowledgement that
  none exists — the skill handles this case).

## Usage

From the `plugin_factory/` directory:

```bash
claude --plugin-dir .
```

Inside Claude Code:

```text
/reload-plugins
/siga-factory:siga-adapt
```

The skill will:

1. Ask for the simulator name, source path, input format, and validator.
2. Run `scripts/scaffold.py` to lay down `../plugin_<slug>/` with
   placeholder files marked `raise NotImplementedError`.
3. Walk the four components in order (RAG → lint → primer → verifier),
   adapting each by reading the GEOS reference and writing the
   simulator-specific counterpart.
4. Run a smoke check after each component before moving on.
5. Run a final end-to-end load test against the new plugin.
6. Document everything in `../plugin_<slug>/ADAPTATION_LOG.md`.

Expect ~30–90 minutes wall-clock depending on the simulator's complexity
and how complete its docs are.

## Direct scaffold (no adaptation)

If you only want the empty skeleton (for a hand adaptation, or to inspect
the layout):

```bash
python scripts/scaffold.py --simulator "OpenFOAM" --target ../plugin_openfoam
```

The scaffold writes placeholder files; nothing is functional until the
`siga-adapt` skill (or a human) fills them in.

## Files

- `REFERENCE_PROMPT.md` — the structured adaptation goal-prompt, loaded by
  the skill.
- `skills/siga-adapt/SKILL.md` — the orchestrator. The phase-by-phase
  workflow.
- `scripts/scaffold.py` — generates the target plugin skeleton.
- `.claude-plugin/plugin.json` — Claude Code plugin manifest.

## What the factory does *not* do

- It does not build a Chroma index from the new simulator's docs. That is a
  separate offline-prep step; the skill points at where to call it but does
  not run it (it can take hours, varies by corpus size, and needs an
  embedding API key).
- It does not write a paper-grade evaluation harness. The smoke checks are
  enough to confirm the plugin loads and the hooks fire — not enough to
  claim "SIGA matches GEOS performance on simulator X."
- It does not invent simulator behavior. If a component has no analogue in
  the target simulator (e.g. no schema corpus), the skill ships a partial
  plugin and documents the gap.
