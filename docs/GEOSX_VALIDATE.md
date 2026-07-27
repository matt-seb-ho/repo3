# geosx --validate-input in place of xmllint (branch: geosx-validate-input)

## What changed

The S (stop-hook) and X (agent-callable MCP tool) validators previously shelled
out to `xmllint --schema <schema.xsd> --noout <file>`. On this branch they
instead run `geosx -i <entry_file> --validate-input`, which actually loads the
deck through GEOS's own `ProblemManager` (builds the data repository, resolves
cross-references, parses the mesh) rather than checking it against the XSD.

Changed files:
- `plugin/hooks/verify_outputs.py` — `_xmllint_validate` replaced by
  `_geosx_validate` (+ new `_entry_files`/`_included_targets`/
  `_extract_geosx_error` helpers). Same `GEOS_HOOK_XMLLINT` env flag name
  kept (every `launch_*.sh` script already exports it) — only the
  implementation swapped.
- `plugin/scripts/xmllint_mcp.py` — same swap; tool name (`validate_geos_xml`,
  server key `xmllint`) kept for interface parity, docstrings updated.
- `src/runner/constants.py` — new `DEFAULT_GEOSX_*` / `CONTAINER_GEOSX_*`
  path constants.
- `src/runner/docker_cmd.py` — mounts the geosx binary + its runtime shared
  libraries into the container whenever `enable_plugin=True`, and sets
  `GEOSX_EXECUTABLE` / `LD_LIBRARY_PATH`.
- `src/runner/claude_settings.py` — forwards `GEOSX_EXECUTABLE` /
  `LD_LIBRARY_PATH` into the `xmllint` MCP server's explicit env block (MCP
  stdio servers get their own env, not a free inherit from the parent).

## The exact flag (this matters)

`geosx --validate` **does not exist**. `geosx --help` and the source's own
option table (`src/coreComponents/mainInterface/initialization.cpp:123`) only
define `-v` / `--validate-input`. The Sphinx docs (`QuickStart.rst:388`)
call it `--validate-only` — that name is **wrong**; I tested it directly and
it crashes (exit 1) before even reaching argument-dependent logic. Use
`--validate-input`.

Confirmed working directly against the real binary at
`/data/shared/GEOS/GEOS/install-ds-serv6-conda-release/bin/geosx`:
`geosx -i buckleyLeverett_benchmark.xml --validate-input` loads the deck,
prints "Input validation completed, terminating GEOS...", exits 0, in ~2-3s
for a small deck.

## Semantics differ from xmllint — read this before trusting a "validates" result

`--validate-input` is a **loading-phase** check, not a schema linter:

- **Catches**: missing required top-level blocks (a base-only fragment
  missing `Mesh`/`Events` crashes with a clean exception), and — more
  usefully than xmllint — **dangling cross-references**. I renamed a
  `<CellElementRegion name="region">` to `region_renamed` in one file
  without updating the solver's `targetRegions` reference in the other file;
  xmllint would pass this (both are valid XSD strings) but `--validate-input`
  correctly failed with `No child named 'region' found. The children of
  elementRegionsGroup are: { region_renamed }`.
- **Does NOT catch**: unknown/misspelled attribute names or wrong attribute
  types that GEOS's parser tolerates or silently defaults. I renamed a
  `name="compflow"` attribute and added a bogus extra attribute on the
  solver tag and `--validate-input` exited 0 — xmllint would have flagged
  both against the XSD.

Net effect: this branch trades "strict schema/attribute compliance" for
"does this deck actually build," which is a materially different error class
from what `judge_geos.py`'s `bad_attribute_value` failure category measures
(§6.2 of the SIGA paper). Don't assume this is a strict superset or subset of
the xmllint behavior — it's a different check.

## Docker mount is untested — flagging clearly

The GEOS tree repo3 actually mounts into the sandbox
(`/data/shared/geophysics_agent_data/data/GEOS`, `DEFAULT_GEOS_LIB_DIR`) is
**source-only** — no `build*`/`install*` dir, no `geosx` binary. The built
binary lives in a completely separate checkout
(`/data/shared/GEOS/GEOS/install-ds-serv6-conda-release`), and `ldd` on it
resolves 126 shared libraries across **five** distinct host roots:

1. `GEOS/install-ds-serv6-conda-release/lib`
2. `thirdPartyLibs/install-ds-serv6-conda-release/hdf5/lib`
3. `thirdPartyLibs/install-ds-serv6-conda-release/suitesparse/lib`
4. `thirdPartyLibs/install-ds-serv6-conda-release/superlu_dist/lib`
5. `thirdPartyLibs/install-ds-serv6-conda-release/vtk/lib`
6. `/home/brian/miniconda3/envs/geos-build/lib` (supplies `libz.so.1`) — this
   one is **not** a proper install prefix, just an incidental host conda env
   that happened to be active at build time. It's the most fragile part of
   this setup: it's not portable to another machine and isn't really "GEOS's"
   directory to depend on.

`docker_cmd.py` now mounts roots 1-5 read-only and sets `LD_LIBRARY_PATH`
accordingly whenever the plugin is enabled. **I could not test any of this
inside the actual `geos-eval` Docker image** — the `brian` user on this host
isn't in the `docker` group and there's no passwordless sudo, so every
`docker run`/`docker images` call in this session returned a permission
error. Everything above (the exact flag, the entry-file logic, the error-
banner extraction, the dangling-reference catch) was verified by importing
`verify_outputs.py`'s functions directly and running the real `geosx` binary
on the host, outside any container. What's specifically unverified:

- Whether the `geos-eval` image's base OS/glibc is ABI-compatible with this
  conda-built binary at all (mounting libraries doesn't fix an incompatible
  libc).
- Whether `--user <uid>:<gid>` (docker_cmd.py always runs unprivileged)
  can read/exec everything under the five mounted roots.
- Actual wall-clock cost of `--validate-input` per task at eval scale (my
  timing was on one small single-region deck; harder held-out tasks with
  bigger meshes will take longer than the ~2-3s I measured, and I set the
  per-entry timeout to 120s as a guess, not a measurement).

Once `docker` group access is sorted out, the right next step is a `--dry-run`
+ one real `claude_code_repo3_plugin_xmllint_hook`-style task run to confirm
the container can actually exec `geosx` and load a deck before trusting any
aggregate numbers off this branch.
