#!/usr/bin/env python3
"""Stop-hook self-verification for GEOS XML authoring tasks.

Fires when the Claude Code agent ends its turn. Checks that
``/workspace/inputs/`` contains at least one ``.xml`` file and that every XML
file parses. If either check fails, emits ``decision: "block"`` on stdout so
Claude Code re-enters the agent with the reason as feedback; otherwise allows
the stop.

Environment knobs:
    GEOS_HOOK_INPUTS_DIR   Override the workspace inputs directory.
                           Defaults to ``$CLAUDE_PROJECT_DIR/inputs`` if that
                           env var is set, else ``/workspace/inputs``.
    GEOS_HOOK_MAX_RETRIES  Max times this hook will block before giving up.
                           Default 2. Counter lives in
                           ``<inputs-parent>/.verify_retry_count``.
    GEOS_HOOK_DISABLE      If ``1``/``true``/``yes``, hook no-ops.
    GEOS_HOOK_SELF_REFLECT If ``1``/``true``/``yes``, after the XML passes the
                           static checks, also block once with a self-review
                           prompt (off by default — see XN-010 section 6.3).

Input JSON is read from stdin; see Claude Code Stop-hook schema. We only read
``stop_hook_active`` to short-circuit nested stops; the rest we do not need.
"""
from __future__ import annotations

import json
import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def _envflag(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _allow_stop(extra: dict | None = None) -> None:
    """Emit a non-blocking result and exit 0."""
    payload: dict = {"continue": True, "suppressOutput": True}
    if extra:
        payload.update(extra)
    json.dump(payload, sys.stdout)
    sys.stdout.write("\n")
    sys.exit(0)


def _block(reason: str) -> None:
    payload = {
        "decision": "block",
        "reason": reason,
        "hookSpecificOutput": {
            "hookEventName": "Stop",
            "additionalContext": reason,
        },
    }
    json.dump(payload, sys.stdout)
    sys.stdout.write("\n")
    sys.exit(0)


def _inputs_dir() -> Path:
    override = os.environ.get("GEOS_HOOK_INPUTS_DIR")
    if override:
        return Path(override)
    project = os.environ.get("CLAUDE_PROJECT_DIR")
    if project:
        return Path(project) / "inputs"
    return Path("/workspace/inputs")


def _retry_counter(inputs_dir: Path) -> Path:
    parent = inputs_dir.parent if inputs_dir.parent.exists() else Path("/tmp")
    return parent / ".verify_retry_count"


def _bump_counter(counter: Path) -> int:
    try:
        current = int(counter.read_text().strip() or "0")
    except (FileNotFoundError, ValueError):
        current = 0
    current += 1
    try:
        counter.write_text(str(current))
    except OSError:
        pass
    return current


def _list_xml(inputs_dir: Path) -> list[Path]:
    if not inputs_dir.exists():
        return []
    return sorted(p for p in inputs_dir.rglob("*.xml") if p.is_file())


def _first_parse_error(paths: list[Path]) -> tuple[Path, str] | None:
    for p in paths:
        try:
            ET.parse(p)
        except ET.ParseError as exc:
            return p, str(exc)
        except (OSError, UnicodeDecodeError) as exc:
            return p, f"read error: {exc}"
    return None


def main() -> None:
    if _envflag("GEOS_HOOK_DISABLE"):
        _allow_stop()

    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        # If we can't even parse the hook input, don't block — fail open.
        _allow_stop()

    if payload.get("stop_hook_active"):
        _allow_stop()

    inputs_dir = _inputs_dir()
    counter = _retry_counter(inputs_dir)
    max_retries = int(os.environ.get("GEOS_HOOK_MAX_RETRIES", "2") or 2)

    xml_files = _list_xml(inputs_dir)

    if not xml_files:
        if _bump_counter(counter) > max_retries:
            _allow_stop()
        _block(
            "Stop blocked by verify_outputs hook: no .xml files found under "
            f"{inputs_dir}. This is a required output of the task. Produce the "
            "requested GEOS XML files now using the Write tool (write under "
            f"{inputs_dir}/) and then end your turn."
        )

    parse_err = _first_parse_error(xml_files)
    if parse_err is not None:
        path, detail = parse_err
        if _bump_counter(counter) > max_retries:
            _allow_stop()
        rel = path.relative_to(inputs_dir) if path.is_relative_to(inputs_dir) else path
        _block(
            f"Stop blocked by verify_outputs hook: XML parse error in {rel}: "
            f"{detail}. Open the file, fix the syntax, then end your turn."
        )

    if _envflag("GEOS_HOOK_SELF_REFLECT"):
        # One-shot reflection block: only fire once per task to avoid loops.
        flag = counter.parent / ".verify_reflected"
        if not flag.exists():
            try:
                flag.write_text("1")
            except OSError:
                pass
            files = ", ".join(
                str(p.relative_to(inputs_dir)) if p.is_relative_to(inputs_dir) else str(p)
                for p in xml_files
            )
            _block(
                "Stop blocked by verify_outputs hook (self-reflection pass): "
                f"you produced {files}. Before ending the turn, re-read each "
                "file once and verify: (a) the solver block matches the "
                "physics the task describes; (b) all referenced materials, "
                "regions, and BC set-names actually exist elsewhere in the "
                "same file; (c) benchmark/smoke variants import the base via "
                "<Included>. Fix any issues you find, then end your turn. "
                "If everything already looks correct, just end your turn — "
                "this reflection will not repeat."
            )

    _allow_stop()


if __name__ == "__main__":
    main()
