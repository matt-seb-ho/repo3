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

**Correction:** an earlier version of this doc claimed `--validate-input`
misses unknown-attribute and unknown-element typos. That claim was wrong —
it was based on a test that edited the wrong deck (`sed` patterns for
`CompositionalMultiphaseFVM`/`name="compflow"` against a file whose actual
solver tag is `<ImmiscibleMultiphaseFlow name="FlowSolver">`; the substitution
matched nothing, so the file was byte-identical to the valid original and of
course "validated"). Redone against the correct tag names, with a diff check
to confirm each edit actually changed the file:

- **Unknown attribute** (`totallyBogusAttribute="xyz"` added to the solver
  tag): **caught**, exit 1 — `"contains unused attribute
  'totallyBogusAttribute'. Valid attributes are: [full table]"`. GEOS's own
  `dataRepository`/`xmlWrapper` layer enforces its attribute registry
  natively, independent of the `.xsd`.
- **Hallucinated element tag** (`ImmiscibleMultiphaseFlow` →
  `ImmiscibleMultiphaseFlowBogus`): **caught**, exit 1 — `"The tag ... is
  invalid within Solvers ... All available tags are: [full list of ~50
  valid solver types]"`.
- **Dangling name reference, resolved at load time** (renamed a
  `<CellElementRegion name="region">` without updating the solver's
  `targetRegions` reference to it): **caught**, exit 1 — `"No child named
  'region' found. The children of elementRegionsGroup are: {
  region_renamed }"`. xmllint would pass this (both are valid XSD strings;
  no keyref constraint ties them together — see below).
- **Dangling name reference, resolved lazily past the load phase**
  (`discretization="TPFA_DOES_NOT_EXIST"`, not matching any defined
  `NumericalMethods` child): **NOT caught**, exit 0. Whatever GEOS does to
  link a solver to its discretization scheme apparently isn't exercised
  until an actual solve step, which `--validate-input` stops short of.

So `--validate-input` is a strict superset of what xmllint catches for
*most* practical agent-authoring mistakes (typo'd/hallucinated element and
attribute names — the actual dominant failure mode per the SIGA paper's
`bad_attribute_value`/`hallucinated_extras` categories) — it just isn't a
perfect substitute for one specific residual class: name references that
solvers resolve only during the run loop rather than during initial
data-repository construction.

**No command closes that residual gap, and combining xmllint doesn't help
either.** I checked: `discretization` is typed `groupNameRef` in
`schema.xsd` — a plain string type, not an enum, and the schema has zero
`xsd:key`/`xsd:keyref` declarations anywhere (`grep -c "keyref\|xs:key "
schema.xsd` → 0). So the XSD has no constraint machinery to express "this
string must equal a sibling `NumericalMethods` child's name" in the first
place — xmllint can't catch this class of error regardless of what runs
alongside it. The only way to catch 100% of these would be to run the deck
past the loading phase (drop `--validate-input` and actually execute), which
is far too slow/expensive to use as a per-turn agent validator.

Net effect: this branch trades a small, structurally-uncatchable residual
gap (lazily-resolved name references) for a materially stronger check on
everything that resolves at load time, which is most of what matters in
practice. Concretely, this branch should catch element/attribute-name
mistakes at least as well as xmllint did (plus some load-time cross-
reference mistakes xmllint never could), and only misses the narrower class
of solver-side name references GEOS itself defers past the load phase —
which `judge_geos.py`'s `bad_attribute_value` category would still flag as
wrong, geosx just won't tell the agent about it mid-trajectory.

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
