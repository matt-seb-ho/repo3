"""Prompt construction helpers for the GEOS eval harness.

Long prompt strings live next to this module in plain ``.txt`` files so the
Python source stays readable. The helper functions here just glue them
together — no semantic changes from the original
``scripts/run_experiment.py`` ``build_*`` / ``*_retry_prompt`` functions.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..constants import CONTAINER_GEOS_PRIMER_PATH, RUN_ASSETS_DIR

_PROMPTS_DIR = Path(__file__).parent


def _load(name: str) -> str:
    return (_PROMPTS_DIR / name).read_text()


_RAG_INSTRUCTIONS_PLUGIN = _load("rag_instructions.txt")
_RAG_INSTRUCTIONS_VANILLA = _load("rag_vanilla.txt")
_MEMORY_INSTRUCTIONS = _load("memory_instructions.txt")
_REAL_TOOL_TAIL = _load("real_tool_tail.txt")
_NATIVE_PLUGIN_PREFIX = _load("native_plugin_prefix.txt")
_PSEUDO_TOOL_RETRY = _load("pseudo_tool_retry.txt")
_NO_OUTPUTS_RETRY = _load("no_outputs_retry.txt")


def load_agents_md(strip_baked_primer: bool = False) -> str:
    """Retired: AGENTS.md was renamed to AGENTS_old.md; nothing is injected.

    The system prompt now consists solely of the primer file selected by
    ``--geos-primer-path`` (default ``plugin/GEOS_PRIMER_absolute_min.md``)
    plus the standard RAG / memory / tool-tail blocks built downstream by
    :func:`build_system_prompt`. Trust the primer to be self-contained.

    The ``strip_baked_primer`` parameter is kept for CLI back-compat — the
    flag is now a no-op since there is no AGENTS.md to strip from.
    """
    return ""


def load_task_instructions(task_dir: Path) -> str:
    path = task_dir / "instructions.txt"
    if not path.exists():
        raise FileNotFoundError(f"instructions.txt not found in {task_dir}")
    return path.read_text()


def build_prompt(agents_context: str, task_instructions: str) -> str:
    return (
        f"{agents_context}\n\n"
        "--- BEGIN SIMULATION SPECIFICATION ---\n"
        f"{task_instructions.strip()}\n"
        "--- END SIMULATION SPECIFICATION ---"
    )


def build_task_prompt(task_instructions: str) -> str:
    return (
        "--- BEGIN SIMULATION SPECIFICATION ---\n"
        f"{task_instructions.strip()}\n"
        "--- END SIMULATION SPECIFICATION ---"
    )


def build_system_prompt(
    agents_context: str,
    geos_primer_path: Path,
    cheatsheet_path: Path | None = None,
    cheatsheet_in_workspace: bool = False,
    memory_enabled: bool = False,
    memory_prompt_hint: bool = True,
    plugin_enabled: bool = True,
    rag_enabled: bool | None = None,
) -> tuple[str, bool]:
    if rag_enabled is None:
        rag_enabled = plugin_enabled
    primer_text = ""
    primer_inlined = False
    if geos_primer_path.exists():
        body = geos_primer_path.read_text().strip()
        if agents_context.strip():
            # Back-compat path for legacy AGENTS.md-style operator context.
            # Suppress the external primer when the operator's text already
            # has its own primer block; otherwise append with a separator.
            if "# GEOS Primer" in agents_context:
                primer_inlined = True
            else:
                primer_text = f"\n\n---\n# GEOS Primer\n\n{body}\n"
                primer_inlined = True
        else:
            # No operator context (the new default): the primer file IS the
            # system prompt. It already carries its own `#`-level header.
            primer_text = f"{body}\n"
            primer_inlined = True

    cheatsheet_text = ""
    if cheatsheet_path is not None and Path(cheatsheet_path).exists():
        if cheatsheet_in_workspace:
            # Just a pointer; content lives in /workspace/CHEATSHEET.md
            cheatsheet_text = (
                "\n\n---\n"
                "A task-authoring cheatsheet is available at "
                "`/workspace/CHEATSHEET.md` with shortcuts and common pitfalls. "
                "Read it early.\n"
            )
        else:
            body = Path(cheatsheet_path).read_text().strip()
            if body:
                cheatsheet_text = f"\n\n---\n{body}\n"

    rag_instructions = _RAG_INSTRUCTIONS_PLUGIN if rag_enabled else _RAG_INSTRUCTIONS_VANILLA

    memory_instructions = (
        _MEMORY_INSTRUCTIONS
        if (plugin_enabled and memory_enabled and memory_prompt_hint) else ""
    )

    return (
        f"{agents_context.strip()}{primer_text}{cheatsheet_text}\n\n"
        "---\n"
        + rag_instructions
        + memory_instructions
        + _REAL_TOOL_TAIL
    ), primer_inlined


def native_plugin_prefix() -> str:
    """Prefix prepended to the prompt when the plugin is enabled (native runner)."""
    return _NATIVE_PLUGIN_PREFIX


def pseudo_tool_retry_prompt(previous_status: str, counts: dict[str, Any]) -> str:
    pseudo_counts = counts.get("pseudo_tool_counts", {})
    pseudo_summary = ", ".join(
        f"{name} x{count}" for name, count in sorted(pseudo_counts.items())
    ) or "unknown pseudo tool"
    return _PSEUDO_TOOL_RETRY.format(
        previous_status=previous_status,
        pseudo_summary=pseudo_summary,
    )


def no_outputs_retry_prompt(previous_status: str) -> str:
    return _NO_OUTPUTS_RETRY.format(previous_status=previous_status)


def redact_command_for_display(cmd: list[str]) -> str:
    redacted: list[str] = []
    secret_markers = ("KEY=", "TOKEN=", "SECRET=", "PASSWORD=")
    prompt_flags = {"--append-system-prompt", "--system-prompt"}
    previous = ""
    for token in cmd:
        if previous in prompt_flags:
            redacted.append("<system_prompt>")
            previous = token
            continue
        if any(marker in token for marker in secret_markers):
            key = token.split("=", 1)[0]
            redacted.append(f"{key}=<redacted>")
        else:
            redacted.append(token)
        previous = token
    return " ".join(redacted)


__all__ = [
    "build_prompt",
    "build_task_prompt",
    "build_system_prompt",
    "load_agents_md",
    "load_task_instructions",
    "native_plugin_prefix",
    "pseudo_tool_retry_prompt",
    "no_outputs_retry_prompt",
    "redact_command_for_display",
]
