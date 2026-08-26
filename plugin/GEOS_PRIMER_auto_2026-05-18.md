# GEOS Primer (auto-generated)

*Auto-generated from data/doc_study/2026-05-18_full via doc-study pipeline (DSv4-flash → studied artifact $\hat D$).*

**Elevator pitch.** GEOS is a multi-physics simulation framework for subsurface applications, including fluid flow, solid mechanics, poromechanics, and hydraulic fracturing. It supports single and multiphase flow, compositional modeling, and coupled processes with flexible constitutive models defined via XML input files.

## Entrypoints
- <Solvers> (physics solvers)
- <Constitutive> (material models)
- <Mesh> (mesh generation/import)
- <Events> (simulation scheduling)
- <FieldSpecifications> (initial/boundary conditions)
- <Functions> (spatiotemporal varying properties)
- tutorials (step01-step04)
- basicExamples (CO2 injection, poromechanics, hydraulic fracturing)

## Top workflows
- Single-phase flow simulation (SinglePhaseFVM): isothermal single-phase flow with compressible fluid, porosity, and permeability models.
- Compositional multiphase flow simulation (CompositionalMultiphaseFVM): multiphase flow with EOS or black-oil PVT, wells, and phase behavior.
- Solid mechanics (SolidMechanicsLagrangianFEM): quasi-static or explicit dynamic solid deformation with elasticity/plasticity.
- Poromechanics (PoroelasticSolver): coupled flow and solid deformation with Biot poroelasticity.
- Hydraulic fracturing (Hydrofracture): fully coupled fluid flow, fracture propagation, and solid deformation.
- Contact mechanics (SolidMechanicsLagrangeContact): fracture contact with friction.
- Fluid property testing (PVTDriver): standalone evaluation of fluid models.
- Triaxial rock test (TriaxialDriver): material calibration with stress/strain control.
- Proppant transport (ProppantTransport): proppant distribution in hydraulic fractures.
- Well modeling (CompositionalMultiphaseWell): multiphase flow with wellbore models.

## Primary object taxonomy
### Solvers Physics
`SinglePhaseFVM`, `CompositionalMultiphaseFVM`, `SolidMechanicsLagrangianFEM`, `PoroelasticSolver`, `Hydrofracture`, `SolidMechanicsLagrangeContact`, `ProppantTransport`

### Constitutive Models
`ElasticIsotropic`, `DruckerPrager`, `ModifiedCamClay`, `CompressibleSinglePhaseFluid`, `CompositionalMultiphaseFluid`, `BlackOilFluid`, `CO2BrinePhillipsFluid`, `BiotPorosity`, `ConstantPermeability`, `BrooksCoreyCapillaryPressure`, `BrooksCoreyBakerRelativePermeability`, `TableRelativePermeability`, `TableCapillaryPressure`

### Mesh
`InternalMesh`, `VTKMesh`, `CellElementRegion`, `WellElementRegion`

### Events
`PeriodicEvent`, `SoloEvent`, `HaltEvent`, `Tasks`, `PackCollection`

### Field Specifications
`FieldSpecification`, `HydrostaticEquilibrium`, `Aquifer`, `CarterTracy`

### Functions
`TableFunction`, `SymbolicFunction`, `CompositeFunction`

### Output
`Silo`, `VTK`, `TimeHistory`

### Linear Algebra
`LinearSolverParameters`, `MGR`, `AMG`, `DofManager`

## Top pitfalls
- 1. Phase names and ordering must match across fluid, relative permeability, and FieldSpecification blocks.
- 2. HydrostaticEquilibrium requires gravity vector aligned with z-axis; it does not support initial phase contacts.
- 3. All imported cellBlocks must be assigned to exactly one CellElementRegion; even inactive cells require assignment.
- 4. Event ordering in XML defines execution order; collection events must precede output events to capture current time data.
- 5. Constitutive model names must be consistent across ElementRegions, Solvers, and Constitutive blocks.
- 6. For Brooks-Corey capillary pressure, capPressureEpsilon must be set to avoid infinite values near zero saturation.
- 7. Compositional/black-oil models require building GEOS with -DENABLE_PVTPACKAGE=ON.
- 8. TableFunction and relative permeability tables must be strictly monotonic; GEOS errors otherwise.
- 9. SymbolicFunction expressions cannot contain spaces and use C-style power (pow(x,3)) not **.
- 10. Stale Numpy views from pygeosx cause segfaults if LvArray buffer is reallocated; do not keep pylvarray objects after pygeosx calls.

## Navigation index
- **getting started** → `tutorials`
- **basic examples** → `basicExamples`
- **advanced examples** → `advancedExamples`
- **solver configuration** → `coreComponents/physicsSolvers`
- **constitutive models** → `coreComponents/constitutive`
- **mesh setup** → `coreComponents/mesh`
- **events and output** → `coreComponents/events`
- **boundary/initial conditions** → `coreComponents/fieldSpecification`
- **functions (spatial/temporal)** → `coreComponents/functions`
- **linear solvers** → `coreComponents/linearAlgebra`
- **input file preprocessing** → `coreComponents/fileIO`
- **building from source** → `buildGuide`
- **developer guide** → `developerGuide`
- **Python interface** → `pygeosx`

## Coverage note
This artifact coalesces all documented subtrees but has gaps: advancedExamples had a parse error and is missing; internal developer details (e.g., FEMKI, dataRepository internals) are summarized but not exhaustive; some pitfall details may lack contextual examples. Shallow on: Doxygen API, Contributors, Publications, and specific module internals.

---

## Subtree navigation hints (from per-subtree rollups)

### `Contributors`
**Find here.** The subtree contains only a single reference section. To find contributor details, consult the section itself for the static snapshot or follow the GitHub link for the current list.

### `Doxygen`
**Purpose.** Documents the GEOS C++ API via Doxygen, providing links to generated class lists and key API pages (Group, Wrapper, ObjectManagerBase, PhysicsSolverBase). Developers are advised to help developers navigate the API after reviewing the Developer Guide's KeyComponents.
**Find here.** Start by reading the KeyComponents section of the Developer Guide, then use the provided links to the Doxygen class list and key API pages (Group, Wrapper, ObjectManagerBase, PhysicsSolverBase) to explore the C++ API.
**Key XML elements:** `Group`, `Wrapper`, `ObjectManagerBase`, `PhysicsSolverBase`

### `Publications`
**Purpose.** This subtree provides a curated list of publications that cite or are related to the GEOS simulator, including a primary reference paper and peer-reviewed works organized by year from 2019 to 2026.
**Find here.** The Publications section is a single page listing papers by year; to find a specific publication, scan the year headings or use the citation anchor for the primary GEOS reference.

### ` : null, /* placeholder to ensure valid JSON starting character */`

### `advancedExamples`

### `basicExamples`
**Purpose.** This subtree provides tutorials for setting up and running GEOS simulations across a range of physics: multiphase flow with and without wells, CO2 injection, poromechanics, hydraulic fracturing, and rock mechanics (triaxial driver). It serves as the primary entry point for learning how to configure solvers, meshes, constitutive models, boundary conditions, and output tasks.
**Find here.** Each section_id corresponds to a self-contained tutorial with XML snippets. For a. CO2 injection, multiphase flow, multiphase flow with wells, poromechanics, hydraulic fracturing, and triaxial driver. For harness use, prioritize the six 'key_files' listed above; each has 'harness_relevance=high' and includes a 'citation_anchor' for retrieval.
**Key XML elements:** `CompositionalMultiphaseFVM`, `SinglePhaseFVM`, `SolidMechanicsLagrangianFEM`, `CompositionalMultiphaseWell`, `SinglePhasePoromechanics`, `Hydrofracture`, `SurfaceGenerator`, `InternalMesh`, `InternalWell`, `CellElementRegion`

### `buildGuide`
**Purpose.** This subtree documents how to build GEOS from source on various platforms, including dependency installation, CMake configuration, CI workflows, and Spack-based dependency management.
**Find here.** For platform-specific build instructions, see 'AppleMacOS' (tutorial). For general build process and CMake options, see 'BuildProcess'. For CI details, see 'ContinuousIntegration'. For Spack-based dependency setup, see 'SpackUberenv'.
**Key XML elements:** `host-config`, `config-build.py`, `ENABLE_MPI`, `ENABLE_OPENMP`, `ENABLE_CUDA`, `ENABLE_HIP`, `CMAKE_BUILD_TYPE`, `GEOS_TPL_DIR`, `CMAKE_INSTALL_PREFIX`, `GEOS_ENABLE_TESTS`

### `coreComponents/constitutive`
**Purpose.** Defines constitutive models for solid, fluid, and porous media behavior in GEOS, including elasticity, plasticity, permeability, porosity, capillary pressure, and multiphase flow relations, configured via XML input files.
**Find here.** Start with the Constitutive overview for XML structure and region assignment. For solids, see SolidModels then drill into ElasticIsotropic, DruckerPrager, or ModifiedCamClay. For fluids, choose CompressibleSinglePhaseFluid, CompositionalMultiphaseFluid, BlackOilFluid, or CO2BrineFluid. For multiphase flow, combine relative permeability (BrooksCoreyBakerRelativePermeability or TableRelativePermeability) and capillary pressure (BrooksCoreyCapillaryPressure, VanGenuchtenCapillaryPressure, or TableCapillaryPressure). Permeability models are under ConstantPermeability, ExponentialDecayPermeability, SlipDependentPermeability, WillisRichardsPermeability, or KozenyCarmanPermeability. Porosity models include BiotPorosity and PressurePorosity. PorousSolids combines solid, porosity, and permeability sub-models for coupled simulations.
**Key XML elements:** `Constitutive`, `ElasticIsotropic`, `CompressibleSinglePhaseFluid`, `BiotPorosity`, `ConstantPermeability`, `BrooksCoreyCapillaryPressure`, `BrooksCoreyBakerRelativePermeability`, `TableRelativePermeability`, `TableCapillaryPressure`, `CompositionalMultiphaseFluid`

### `coreComponents/constitutiveDrivers`
**Purpose.** This subtree provides standalone driver applications (PVTDriver, TriaxialDriver) for testing single-point constitutive models — fluid property models and solid material models — without requiring a full finite-element simulation. The drivers are configured via standard GEOS XML input files and can be used for material calibration and unit testing.
**Find here.** Consult the PVTDriver section for fluid testing and the TriaxialDriver section for solid material testing. Each driver is invoked as a Task/SoloEvent in the XML event queue; examples and test XML files are referenced in the section notes. The PVTDriver section has a dedicated unit test files and an integration test example.
**Key XML elements:** `PVTDriver`, `TriaxialDriver`, `Task`, `SoloEvent`, `Events`, `EventManager`, `Solvers`, `Constitutive`, `Functions`, `output`

### `coreComponents/dataRepository`
**Purpose.** Provides foundational data management abstractions for GEOS: hierarchical storage (Group), typed wrappers for data (Wrapper), a contiguous-plus-associative container (MappedVector), a static factory pattern (ObjectCatalog), and a logging level system (LogLevel) system.
**Find here.** Consult the Group section for hierarchical data tree structure, Wrapper for typed data storage, MappedVector for container details, ObjectCatalog for factory registration, and LogLevel for logging macros.
**Key XML elements:** `Group`, `Wrapper`, `MappedVector`, `ObjectCatalog`, `LogLevel`

### `coreComponents/events`
**Purpose.** The events subtree defines the EventManager and TasksManager, which control the simulation loop and user-specified tasks triggered by events. It enables flexible scheduling via periodic, solo, and halt events, coordinate timesteps, and supports output tasks like PackCollection.
**Find here.** Look under 'coreComponents/events/docs/', the two key section IDs are 'TasksManager' and 'EventManager' (the latter misspelled but central). An agent should consult those for configuration details, XML structure, and pitfalls.
**Key XML elements:** `Events`, `EventManager`, `PeriodicEvent`, `SoloEvent`, `HaltEvent`, `Tasks`, `PackCollection`, `maxTime`, `maxCycle`, `cycleFrequency`

### `coreComponents/fieldSpecification`
**Purpose.** Defines field specifications for initial conditions (hydrostatic equilibrium) and boundary conditions (aquifer models) in GEOS simulations.
**Find here.** Look for section IDs matching 'fieldSpecification' in docs; key sections are EquilibriumInitialCondition and AquiferBoundaryCondition, both marked high relevance.
**Key XML elements:** `HydrostaticEquilibrium`, `FieldSpecifications`, `FieldSpecification`, `ElementRegions`, `TableFunction`, `gravityVector`, `Solvers`, `Constitutive`, `Aquifer`, `CarterTracy`

### `coreComponents/fileIO`
**Purpose.** This subtree covers reading configuration from XML input files and generating various output types (log, CSV, SILO, VTK, HDF5) for simulation monitoring and analysis.
**Find here.** To find details on specific output formats or input preprocessing, refer to the corresponding section. For XML schema or preprocessing tools, see InputXMLFiles; for output triggers and event ordering, see OutputTasks; for CSV/log output configuration, see LogCsvOutputs.
**Key XML elements:** `Outputs`, `Silo`, `VTK`, `TimeHistory`, `PeriodicEvent`, `EventManager`, `Problem`, `Parameters`, `Parameter`, `Included`

### `coreComponents/finiteElement`
**Purpose.** Defines the finite element method kernel interface (FEMKI), an API for launching computational kernels in FE solvers, including element looping functions, a KernelBase class, and a launch function.
**Find here.** The subtree currently contains a single section 'kernelInterface/kernelInterface' which fully describes the FEMKI. Consult that section for all details on the kernel interface API.
**Key XML elements:** `finiteElement::KernelBase`, `KernelBase::kernelLaunch`, `regionBasedKernelApplication`, `launch function`, `StackVariables`, `ImplicitKernelBase`

### `coreComponents/functions`
**Purpose.** This subtree documents the Functions block in GEOS XML input files, which defines values that vary in space, time, or other dimensions using TableFunction, SymbolicFunction, and CompositeFunction types.
**Find here.** The primary reference is the FunctionManager section, which details all function types and their attributes. For specific function subtypes, consult the linked TableFunction, SymbolicFunction, and CompositeFunction documentation files.
**Key XML elements:** `Functions`, `TableFunction`, `SymbolicFunction`, `CompositeFunction`, `inputVarNames`, `coordinateFiles`, `voxelFile`, `variableNames`, `expression`, `functionNames`

### `coreComponents/linearAlgebra`
**Purpose.** Covers linear algebra infrastructure in GEOS, including linear solver options (direct and iterative with preconditioners) and the DoF Manager that handles degrees of freedom mapping and sparsity pattern construction for finite element and finite volume discretizations.
**Find here.** For solver configuration details, consult the LinearSolvers section; for DoF mapping and sparsity pattern construction, see the DofManager section. Both sections contain key objects and relations to external documentation.
**Key XML elements:** `LinearSolverParameters`, `SuperLU`, `HYPRE`, `PETSc`, `Trilinos`, `MGR`, `Block`, `Jacobi`, `ILUK`, `ILUT`

### `coreComponents/mesh`
**Purpose.** Describes how meshes are represented, generated, imported, and partitioned in GEOS, including the hierarchical data structures that manage mesh topology and element regions.
**Find here.** For mesh generation/structural details and XML usage, see 'Meshes' (reference). For internals and class hierarchy, see 'Mesh Hierarchy' (concept). For parallelism and domain partition, see 'Parallel Partitioning' (concept).
**Key XML elements:** `InternalMesh`, `VTKMesh`, `CellElementRegion`, `CellBlocks`, `Mesh`, `ElementRegions`, `FieldSpecification`, `FieldSpecifications`, `NodeManager`, `EdgeManager`

### `coreComponents/physicsSolvers`
**Purpose.** This subtree documents the physics solvers available in GEOS, including their configuration via the `<Solvers>` XML element, shared solution strategies, and individual solver implementations for solid mechanics, fluid flow, contact mechanics, poromechanics, and proppant transport.
**Find here.** Start with the PhysicsSolvers section for an overview and toctree, then navigate to individual solver pages (e.g., SinglePhaseFlow, CompositionalMultiphaseFlow, SolidMechanics) for detailed XML configuration, governing equations, and examples. For initialization workflows, see the multiphysics examples under gravityInducedStressInitialization and userTableStressInitialization.
**Key XML elements:** `Solvers`, `NonlinearSolverParameters`, `SolidMechanicsLagrangianFEM`, `SinglePhaseFVM`, `CompositionalMultiphaseFVM`, `ProppantTransport`, `SolidMechanicsLagrangeContact`, `SolidMechanicsEmbeddedFractures`, `PoroelasticSolver`, `HydrostaticEquilibrium`

### `developerGuide`
**Purpose.** This subtree covers everything a developer needs to contribute to GEOS: coding standards, testing (unit, integrated, benchmarking), profiling with Caliper, Docker-based development, working with data, XML input registration, adding new solvers, and using core components like LvArray.
**Find here.** NSheets:starts with the Index page (developerGuide/Index) which splits into Contributing and KeyComponents. For testing/harness workflows, prioritize IntegratedTests, Benchmarks, and UnitTests under Contributing; for data/XSM/XML, go to KeyComponents (especially WorkingWithData and XML). The AddingNewSolver tutorial is a complete walkthrough for solver development.
**Key XML elements:** `Included`, `File`, `Benchmarks`, `Run`, `name`, `nodes`, `tasksPerNode`, `threads`, `threadsPerTask`, `timeLimit`

### `index`
**Purpose.** This is the main documentation index for GEOS, providing an overview of all available guides and pointing to specific sections for different user needs.
**Find here.** The index section lists all major documentation subsections; agents should consult the relevant subsection for detailed information.

### `pygeosx`
**Purpose.** Documents the pygeosx Python module for controlling GEOS from Python, including lifecycle functions (initialize, run, finalize) and data access via Group and Wrapper objects that yield pylvarray views of C++ LvArray arrays.
**Find here.** This subtree currently contains a single reference document. Consult it for pygeosx API usage, warnings about stale views, and links to pylvarray and mpi4py documentation.

### `tutorials`
**Purpose.** Worked examples that teach GEOS from basic XML input structure through advanced features like external meshes, region-based property specifications, boundary conditions, and solid mechanics, recommended to be followed in sequence.
**Find here.** The tutorials are listed sequentially (step01 through step04) and should be followed in order; each tutorial's section contains a complete XML example and explanation. For harness integration, start with the high-relevance tutorial sections directly.
**Key XML elements:** `Problem`, `Solvers`, `SinglePhaseFVM`, `InternalMesh`, `VTKMesh`, `Box`, `Events`, `PeriodicEvent`, `CellElementRegion`, `FieldSpecifications`

### `userGuide`
**Purpose.** This subtree is the top-level index of the GEOS user guide, providing a table of contents with links to all major documentation sections such as input XML files, meshes, physics solvers, constitutive models, and more.
**Find here.** This subtree is a table of contents; to find documentation on a specific component, consult the key_objects list which maps to the corresponding section links.
**Key XML elements:** `InputXMLFiles`, `Mesh`, `PhysicsSolvers`, `Constitutive`, `ConstitutiveDrivers`, `FieldSpecification`, `EventManager`, `TasksManager`, `FunctionManager`, `LinearSolvers`
