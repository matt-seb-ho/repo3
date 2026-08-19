# Quarantine

Adapter artifacts that must not be used in any evaluation run.

## `v4/` — quarantined 2026-08-19

`v4/memory/cheatsheet.md` contains a **task-name → canonical-XML lookup table**
covering all 17 validation tasks:

```
**Read the listed file(s) FIRST. Do not Grep/Glob to find them — they are already verified.**

| Task name keyword | Canonical XML(s) under `/geos_lib/inputFiles/` |
| ExampleMandel | poromechanics/PoroElastic_Mandel_prism6_base_hybrid.xml, ... |
| buckleyLeverettProblem | .../buckleyLeverettProblem/buckleyLeverett_base.xml |
...
```

This converts the agent's search problem into a table lookup against
ground-truth-adjacent decks. Under arXiv:2607.22368's framing it is a textbook
*exposure*, and any TreeSim measured with it is inflated by an unknown amount.

**Provenance.** It did not come from `reflect.py`: that path's `.xml` hygiene
regex would have replaced every filename with `<file>` and logged the count.
Consistent with that, `v4/.reflection_meta.json` is a byte-identical copy of
v3's (it still reads `"version": 3, "parent": 2`), so v4 bypassed the reflection
path entirely. `scripts/launch_autocamp_v4.sh` describes it accurately as
"trajectory-mined task→canonical XML".

**Published results are unaffected.** The paper's SE cell is `v3`, per
`scripts/efficiency_table.py:234` ("SE uses `plugin_evolving/v3`") and
`scripts/self_evolving/launch_icl_v0_v3.sh`, which runs the held-out transfer
comparison as v0 vs v3. No reported number used v4.

**Why quarantine rather than delete.** It is evidence: it is the concrete
example that motivates the content- and task-id-level rules in
`src/evolve/hygiene.py`, and `tests/test_evolve.py::test_task_lookup_table_is_blocked`
locks out its signature. Deleting it would remove the regression target.

Reproduce the finding:

```bash
python3 scripts/siga_evolve/audit_lineage.py \
    --adapter-dir plugin_evolving/_quarantine/v4 \
    --task-list-from scripts/self_evolving/run_full_evolution.sh
```

## Also worth knowing: `v3` is not clean either

`v3` — the adapter the paper reports as SE — leaks ground-truth *dependency*
filenames past the `.xml`-only gate: `tables/time.geos`,
`tables/radialStress.geos`, `tables/axialStrain.geos`, across
`skills/triaxial-driver-setup.md`, `skills/copy-dependencies.md`, and
`agents/dependency-copier.md`. Severity is lower (those tables are readable in
the example tree and are not on the contamination blocklist), so `v3` is left in
place — but it is a leak past a gate the paper asserts is closed, and
`scripts/memory/hygiene_audit.py` has the same `.xml`-only blind spot.
