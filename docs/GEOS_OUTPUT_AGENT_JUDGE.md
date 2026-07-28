# GEOS output agent judge

`scripts/eval/geos_output_judge.py` compares outputs from agent-authored GEOS
decks with outputs from ground-truth decks. It complements the existing XML
judges: it evaluates the simulation results rather than deck syntax.

## Directory contract

The two roots contain matching simulation directories:

```text
candidate/
  ExampleA/       # GEOS outputs from the agent-authored deck
  ExampleB/
ground_truth/
  ExampleA/       # GEOS outputs from the reference deck
  ExampleB/
```

Each matching name is judged independently, one after another. Extra or missing
simulation directories make the aggregate result fail and are listed in the
report. Use `--flat` when each supplied directory is itself one simulation.

## Run

Set `OPENROUTER_API_KEY`, then:

```bash
uv run python scripts/eval/geos_output_judge.py \
  --candidate /path/to/generated/outputs \
  --ground-truth /path/to/ground_truth/outputs \
  --report results/geos_output_verdicts.json
```

For one pair:

```bash
uv run python scripts/eval/geos_output_judge.py \
  --flat \
  --candidate /path/to/generated/run \
  --ground-truth /path/to/reference/run
```

Exit status is zero only when every paired simulation is judged the same and
neither root has unmatched cases.

## Judge environment and tools

Every simulation gets a fresh temporary workspace with `candidate` and
`ground_truth` links. The judge has a command tool and is explicitly instructed
to use geophysical evidence rather than byte equality. It can:

- inspect GEOS completion, convergence, and error logs;
- parse PVD/VTM collections and compare simulation time grids;
- inspect VTK fields, meshes, and numeric field statistics;
- inspect HDF5 histories and restart metadata;
- use headless ParaView tools when installed;
- run Python analysis, including ephemeral packages through
  `uv run --with h5py`, `--with meshio`, or similar commands;
- create temporary analysis scripts and headless plots in its workspace.

The output directories are presented as read-only by policy and the prompt tells
the judge never to modify them. The current command runner is process-isolated
only by its temporary working directory; it is not an OS security boundary.
Run the CLI in a container if judging untrusted artifacts or using an untrusted
model endpoint.

## Verdict

The report intentionally centers the requested binary decision:

```json
{
  "all_same": false,
  "simulations": [
    {
      "simulation": "ExampleA",
      "same": false,
      "confidence": 0.94,
      "summary": "Pressure evolution diverges after the third output step.",
      "evidence": ["..."],
      "limitations": []
    }
  ]
}
```

The judge ignores timestamps, paths, partition order, harmless roundoff, and
equivalent output partitioning. Missing physical fields, materially different
meshes or time histories, solver failure, or incomplete runs count as different.

