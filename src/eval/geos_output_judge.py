"""Agent-as-a-judge evaluation for pairs of GEOS simulation outputs.

Unlike the XML judges in this package, this module compares the artifacts
produced *after* GEOS runs: logs, VTK collections, HDF5 histories, restart
files, plots, and other post-processing products.  Each immediate child
directory is treated as one simulation and judged independently.
"""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

DEFAULT_MODEL = "anthropic/claude-4.6-sonnet"
DEFAULT_MAX_TURNS = 20
DEFAULT_COMMAND_TIMEOUT = 120
MAX_TOOL_OUTPUT = 30_000

SYSTEM_PROMPT = """\
You are a GEOS simulation-output judge and an experienced computational
geophysicist. Compare CANDIDATE outputs against GROUND TRUTH outputs for one
simulation. Decide whether they represent the same physical/numerical result.

You have a shell in a workspace containing:
  candidate -> candidate output directory
  ground_truth -> reference output directory

Inspect evidence; do not judge from filenames alone. Useful approaches include:
- inventory files, sizes, GEOS log completion/errors, and reported time steps;
- parse .pvd/.vtm XML and compare time grids and referenced datasets;
- use Python (including `uv run --with ...`) for HDF5/VTK/numeric statistics;
- use installed headless ParaView (`pvpython`, `pvbatch`, `paraview`) or Python
  VTK/mesh tools when helpful;
- compare field names, mesh topology, time histories, extrema/norms, and plots.

Ignore harmless nondeterminism such as timestamps, paths, rank ordering,
floating-point roundoff, and output partitioning. Do not require byte equality.
Materially different physics, fields, meshes, time evolution, convergence,
missing results, or failed/incomplete runs mean the outputs are not the same.
If an artifact format cannot be opened, use the remaining evidence and state
the limitation. Never modify candidate or ground_truth.

At the end return ONLY one JSON object:
{
  "same": true or false,
  "confidence": number from 0 to 1,
  "summary": "short geophysical justification",
  "evidence": ["concise observation", "..."],
  "limitations": ["anything not inspected"]
}
"""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": (
                "Run a shell command in this simulation's analysis workspace. "
                "Use read-only commands on candidate and ground_truth. You may "
                "create analysis files elsewhere in the workspace."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string"},
                    "timeout_seconds": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 600,
                    },
                },
                "required": ["command"],
                "additionalProperties": False,
            },
        },
    }
]


@dataclass(frozen=True)
class SimulationPair:
    name: str
    candidate: Path
    ground_truth: Path


def _children(root: Path) -> dict[str, Path]:
    return {path.name: path for path in sorted(root.iterdir()) if path.is_dir()}


def discover_pairs(
    candidate_root: Path, ground_truth_root: Path, *, flat: bool = False
) -> tuple[list[SimulationPair], list[str], list[str]]:
    """Match simulations by immediate child-directory name."""
    candidate_root = candidate_root.resolve()
    ground_truth_root = ground_truth_root.resolve()
    if not candidate_root.is_dir() or not ground_truth_root.is_dir():
        raise NotADirectoryError("candidate and ground-truth paths must be directories")

    if flat:
        return [
            SimulationPair(candidate_root.name, candidate_root, ground_truth_root)
        ], [], []

    candidate = _children(candidate_root)
    ground_truth = _children(ground_truth_root)
    common = sorted(candidate.keys() & ground_truth.keys())
    pairs = [
        SimulationPair(name, candidate[name], ground_truth[name]) for name in common
    ]
    return pairs, sorted(candidate.keys() - ground_truth.keys()), sorted(
        ground_truth.keys() - candidate.keys()
    )


def _link_input(source: Path, destination: Path) -> None:
    destination.symlink_to(source.resolve(), target_is_directory=True)


def _run_command(command: str, workspace: Path, timeout: int) -> str:
    env = os.environ.copy()
    env.update(
        {
            "GEOS_JUDGE_CANDIDATE": str(workspace / "candidate"),
            "GEOS_JUDGE_GROUND_TRUTH": str(workspace / "ground_truth"),
            "MPLBACKEND": "Agg",
        }
    )
    try:
        proc = subprocess.run(
            ["bash", "-lc", command],
            check=False,
            cwd=workspace,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
        )
        output = f"exit_code={proc.returncode}\n{proc.stdout}"
    except subprocess.TimeoutExpired as exc:
        partial = exc.stdout or ""
        output = f"timed_out_after={timeout}s\n{partial}"
    if len(output) > MAX_TOOL_OUTPUT:
        omitted = len(output) - MAX_TOOL_OUTPUT
        output = output[:MAX_TOOL_OUTPUT] + f"\n...[truncated {omitted} characters]"
    return output


def _parse_verdict(content: str) -> dict[str, Any]:
    content = content.strip()
    if content.startswith("```"):
        lines = content.splitlines()
        content = "\n".join(lines[1:-1])
        if content.lstrip().startswith("json"):
            content = content.lstrip()[4:].lstrip()
    verdict = json.loads(content)
    if not isinstance(verdict.get("same"), bool):
        raise TypeError("judge verdict must contain boolean field 'same'")
    confidence = float(verdict.get("confidence", 0))
    if not 0 <= confidence <= 1:
        raise ValueError("judge confidence must be between 0 and 1")
    verdict["confidence"] = confidence
    verdict.setdefault("summary", "")
    verdict.setdefault("evidence", [])
    verdict.setdefault("limitations", [])
    return verdict


def judge_pair(
    pair: SimulationPair,
    *,
    model: str = DEFAULT_MODEL,
    api_key: str | None = None,
    max_turns: int = DEFAULT_MAX_TURNS,
    command_timeout: int = DEFAULT_COMMAND_TIMEOUT,
) -> dict[str, Any]:
    """Run one tool-using judge agent for one simulation pair."""
    api_key = api_key or os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable not set")
    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)

    with tempfile.TemporaryDirectory(prefix=f"geos_judge_{pair.name}_") as raw:
        workspace = Path(raw)
        _link_input(pair.candidate, workspace / "candidate")
        _link_input(pair.ground_truth, workspace / "ground_truth")
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Judge simulation {pair.name!r}. Inspect both directories "
                    "with tools, then report whether their GEOS results are the same."
                ),
            },
        ]

        for _ in range(max_turns):
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
                temperature=0,
                max_tokens=4000,
            )
            message = response.choices[0].message
            messages.append(message.model_dump(exclude_none=True))
            if not message.tool_calls:
                verdict = _parse_verdict(message.content or "")
                verdict["simulation"] = pair.name
                return verdict

            for call in message.tool_calls:
                if call.function.name != "run_command":
                    result = f"unsupported tool: {call.function.name}"
                else:
                    arguments = json.loads(call.function.arguments)
                    requested_timeout = int(
                        arguments.get("timeout_seconds", command_timeout)
                    )
                    timeout = min(600, max(1, requested_timeout))
                    result = _run_command(arguments["command"], workspace, timeout)
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": call.id,
                        "content": result,
                    }
                )

        raise RuntimeError(f"judge exceeded {max_turns} tool turns for {pair.name}")


def evaluate_output_directories(
    candidate_root: Path,
    ground_truth_root: Path,
    *,
    flat: bool = False,
    model: str = DEFAULT_MODEL,
    max_turns: int = DEFAULT_MAX_TURNS,
    command_timeout: int = DEFAULT_COMMAND_TIMEOUT,
) -> dict[str, Any]:
    """Judge all matched simulations sequentially and return a report."""
    pairs, candidate_only, ground_truth_only = discover_pairs(
        candidate_root, ground_truth_root, flat=flat
    )
    if not pairs:
        raise ValueError(
            "no matching simulation directories found; use --flat to compare "
            "the two supplied directories as one simulation"
        )

    results = [
        judge_pair(
            pair,
            model=model,
            max_turns=max_turns,
            command_timeout=command_timeout,
        )
        for pair in pairs
    ]
    return {
        "all_same": (
            all(result["same"] for result in results)
            and not candidate_only
            and not ground_truth_only
        ),
        "simulations": results,
        "candidate_only": candidate_only,
        "ground_truth_only": ground_truth_only,
        "model": model,
    }
