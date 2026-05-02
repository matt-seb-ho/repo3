# GEOS Primer (minimal)

GEOS (Geomechanics and EOS Simulator) is an open-source multiphysics simulator. Tasks require authoring an XML input file (or a small set, sometimes with `<Included>` cross-file references) that specifies the simulation. All values are in SI units.

## Where things live (inside the container)

- `/geos_lib/inputFiles/` — validated example XML files, organized by physics family (e.g., `wellbore/`, `hydraulicFracturing/`, `triaxialDriver/`, `compositionalMultiphaseFlow/`, `thermoPoromechanics/`). Treat these as the authoritative reference.
- `/geos_lib/src/docs/` — GEOS documentation (Sphinx RSTs). Includes tutorials, schema definitions, and the Datastructure Index.
- `/workspace/inputs/` — where you must write the final XML(s). Your output goes here.

## Top-level XML skeleton
```
<Problem>
  <Solvers>...</Solvers>
  <Mesh>...</Mesh>              <!-- or VTKMesh, InternalWellbore, InternalMesh -->
  <Geometry>...</Geometry>      <!-- Box, Cylinder, etc. for fieldspec regions -->
  <Events>...</Events>
  <NumericalMethods>...</NumericalMethods>
  <ElementRegions>...</ElementRegions>
  <Constitutive>...</Constitutive>
  <FieldSpecifications>...</FieldSpecifications>
  <Functions>...</Functions>    <!-- optional: TableFunction for time/space-varying data -->
  <Outputs>...</Outputs>
  <Tasks>...</Tasks>            <!-- optional -->
</Problem>
```

## Additional MCP search tools
Find a similar existing example via RAG (`mcp__geos-rag__search_navigator` for topics; `mcp__geos-rag__search_technical` for XML examples; `mcp__geos-rag__search_schema` for authoritative attribute names/types).