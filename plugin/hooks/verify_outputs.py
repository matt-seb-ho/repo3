#!/usr/bin/env python3
"""Stop-hook self-verification for GEOS XML authoring tasks.

Fires when the Claude Code agent ends its turn. Checks that
``/workspace/inputs/`` contains at least one ``.xml`` file and that every XML
file parses. Optionally also validates the deck by actually loading it with
``geosx --validate-input`` (geosx-validate-input branch — this used to shell
out to ``xmllint --schema``; see docs/GEOSX_VALIDATE.md for why and what
changed). If any check fails, emits ``decision: "block"`` on stdout so
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
    GEOS_HOOK_XMLLINT      If ``1``/``true``/``yes``, run
                           ``geosx -i <entry> --validate-input`` against each
                           deck entry file (see _entry_files) after the parse
                           check; block with the loading errors as feedback
                           if validation fails. Off by default; counts toward
                           the same retry budget as the parse-error block.
                           Name kept from the xmllint-era flag for parity
                           with every launch_*.sh script that already
                           exports it — only the implementation changed.
    GEOS_HOOK_SCHEMA_PATH  Unused on this branch (was the xmllint schema.xsd
                           path). Left defined for interface parity; ignored.
    GEOSX_EXECUTABLE       Path to the geosx binary inside the container.
                           Defaults to ``/opt/geosx-install/bin/geosx``,
                           matching the mount docker_cmd.py sets up.
    GEOSX_VALIDATE_TIMEOUT Per-entry-file timeout in seconds for the
                           validate-input subprocess. Default 120 — geosx's
                           loading phase is much heavier than an xmllint
                           parse (it builds the mesh and data repository).

Input JSON is read from stdin; see Claude Code Stop-hook schema. We only read
``stop_hook_active`` to short-circuit nested stops; the rest we do not need.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_GEOSX_EXECUTABLE = "/opt/geosx-install/bin/geosx"
DEFAULT_GEOSX_TIMEOUT = 120
MAX_FILES_REPORTED = 4
# geosx prints a clean "***** Exception / LOCATION / Error cause / Message"
# banner before a multi-frame stack trace on a genuine loading failure.
# Keep the banner, drop the noisy stack trace.
GEOSX_ERROR_BANNER_RE = re.compile(r"(\*{5}\s*Exception.*?)(?=\*{5}\s*StackTrace|\Z)", re.DOTALL)

# Recurring failure mode on OpenRouter-routed open models (gemma, qwen, etc.):
# the model emits doubled-bracket-with-doubled-name tags like `<<ProblemProblem>`
# instead of `<Problem>`. This is the single biggest cause of parse_error blocks
# in run7/run9. Detect it so we can hand the agent a precise sed-style fix
# instead of letting it rewrite the whole file via Write.
DOUBLE_BRACKET_OPEN_RE = re.compile(r"<<([A-Za-z][A-Za-z0-9_]*)\1\b")
DOUBLE_BRACKET_CLOSE_RE = re.compile(r"<</([A-Za-z][A-Za-z0-9_]*)\1>")


def _doubled_bracket_hint(path: Path) -> str:
    """Return a one-line sed-style fix hint if the file shows the `<<TagTag>` pattern.

    Gated on ``GEOS_HOOK_POSTTOOLUSE``: when unset the hint is suppressed so
    the parse_error block message is byte-identical to the autocamp
    experiment-state harness (tag autocamp-experiment-state).
    """
    if not _envflag("GEOS_HOOK_POSTTOOLUSE"):
        return ""
    try:
        content = path.read_text(errors="ignore")
    except OSError:
        return ""
    if not (DOUBLE_BRACKET_OPEN_RE.search(content) or DOUBLE_BRACKET_CLOSE_RE.search(content)):
        return ""
    return (
        " Detected the `<<TagTag>` doubled-bracket-and-name pattern. "
        "Fix in place with Edit (do NOT rewrite the whole file via Write): "
        r"replace `<<\1\1` with `<\1` and `<</\1\1>` with `</\1>` for each "
        "affected tag name. Example: `<<ProblemProblem>` -> `<Problem>`, "
        "`<</ProblemProblem>` -> `</Problem>`."
    )


def _envflag(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _event_log_path(inputs_dir: Path) -> Path:
    """Location of the hook event log — one JSONL line per hook invocation."""
    override = os.environ.get("GEOS_HOOK_EVENTS_PATH")
    if override:
        return Path(override)
    parent = inputs_dir.parent if inputs_dir.parent.exists() else Path("/tmp")
    return parent / ".verify_hook_events.jsonl"


def _log_event(
    inputs_dir: Path,
    decision: str,
    reason_category: str,
    retries_so_far: int,
    detail: str = "",
) -> None:
    path = _event_log_path(inputs_dir)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "decision": decision,
        "reason_category": reason_category,
        "retries_so_far": retries_so_far,
        "detail": detail,
    }
    try:
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except OSError:
        pass


def _allow_stop(
    inputs_dir: Path | None = None,
    reason_category: str = "allow",
    retries_so_far: int = 0,
    extra: dict | None = None,
) -> None:
    """Emit a non-blocking result and exit 0."""
    if inputs_dir is not None:
        _log_event(inputs_dir, "allow", reason_category, retries_so_far)
    payload: dict = {"continue": True, "suppressOutput": True}
    if extra:
        payload.update(extra)
    json.dump(payload, sys.stdout)
    sys.stdout.write("\n")
    sys.exit(0)


def _block(
    reason: str,
    inputs_dir: Path,
    reason_category: str,
    retries_so_far: int,
    detail: str = "",
) -> None:
    _log_event(inputs_dir, "block", reason_category, retries_so_far, detail)
    # Stop hook schema: {decision: "block", reason: "..."}.
    # Earlier versions of this file included a hookSpecificOutput block which
    # triggered Claude Code "stop-hook-error" notifications — that field is
    # for UserPromptSubmit-style hooks, not Stop hooks. Keep this minimal.
    payload = {"decision": "block", "reason": reason}
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


def _included_targets(path: Path) -> set[Path]:
    """Resolve every <Included><File name="..."/></Included> target of path."""
    targets: set[Path] = set()
    try:
        root = ET.parse(path).getroot()
    except (ET.ParseError, OSError):
        return targets
    for included in root.iter("Included"):
        for file_el in included.findall("File"):
            name = file_el.get("name")
            if not name:
                continue
            targets.add((path.parent / name).resolve())
    return targets


def _entry_files(paths: list[Path]) -> list[Path]:
    """Return the deck entry file(s): XML files nothing else <Included>s.

    geosx needs the top-level file (the one that <Included>s the rest),
    not each fragment individually — unlike xmllint --schema, which validates
    any XML file against the XSD in isolation. A base.xml on its own is
    missing Mesh/Events and will correctly fail --validate-input even when
    it is perfectly correct as an include fragment.
    """
    all_included: set[Path] = set()
    for p in paths:
        all_included |= _included_targets(p)
    entries = [p for p in paths if p.resolve() not in all_included]
    # Fallback for the (unexpected) case every file looks included, e.g. a
    # circular/self <Included>: validating everything beats validating nothing.
    return entries or list(paths)


def _extract_geosx_error(output: str) -> str:
    match = GEOSX_ERROR_BANNER_RE.search(output)
    if match:
        return match.group(1).strip()
    # No banner (e.g. a raw segfault/abort outside GEOS's own exception
    # handling) — fall back to the tail of combined stdout+stderr.
    lines = [line for line in output.splitlines() if line.strip()]
    return "\n".join(lines[-15:])


def _geosx_validate(
    paths: list[Path],
    inputs_dir: Path,
) -> str | None:
    """Load-validate the deck; return formatted error feedback or None.

    Runs ``geosx -i <entry> --validate-input`` per deck entry file (see
    _entry_files); geosx exits 0 and prints "Input validation completed"
    when the deck loads, non-zero with a "***** Exception" banner on
    failure (missing/broken cross-references, unparseable mesh, etc).
    Returns None when every entry validates or when geosx is unavailable
    (we don't penalise the agent for our own infra gap).

    Caveat vs. the old xmllint path: this catches structural/reference
    failures (missing blocks, dangling names) via geosx actually trying to
    build the ProblemManager's data repository, but does NOT strictly
    enforce the XSD (unknown or misspelled attributes that GEOS's parser
    tolerates silently will NOT be flagged here, where xmllint --schema
    would have caught them).
    """
    executable = os.environ.get("GEOSX_EXECUTABLE", DEFAULT_GEOSX_EXECUTABLE)
    if not Path(executable).exists():
        return None
    timeout = int(os.environ.get("GEOSX_VALIDATE_TIMEOUT", DEFAULT_GEOSX_TIMEOUT) or DEFAULT_GEOSX_TIMEOUT)

    files_with_errors: list[tuple[Path, str]] = []
    for entry in _entry_files(paths):
        scratch = Path(tempfile.mkdtemp(prefix="geosx_validate_"))
        try:
            res = subprocess.run(
                [executable, "-i", str(entry), "--validate-input", "-o", str(scratch)],
                cwd=scratch,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        except (subprocess.TimeoutExpired, OSError):
            continue
        finally:
            shutil.rmtree(scratch, ignore_errors=True)
        if res.returncode == 0:
            continue
        detail = _extract_geosx_error(res.stdout + res.stderr)
        try:
            rel = entry.relative_to(inputs_dir)
        except ValueError:
            rel = entry
        files_with_errors.append((rel, detail))

    if not files_with_errors:
        return None

    parts = []
    for rel, detail in files_with_errors[:MAX_FILES_REPORTED]:
        parts.append(f"- {rel}:\n  {detail}")
    extra = len(files_with_errors) - MAX_FILES_REPORTED
    summary = "\n".join(parts)
    if extra > 0:
        summary += f"\n- ...plus {extra} more entry file(s) failing --validate-input."
    return summary


def main() -> None:
    inputs_dir = _inputs_dir()

    if _envflag("GEOS_HOOK_DISABLE"):
        _allow_stop(inputs_dir, reason_category="disabled")

    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        _allow_stop(inputs_dir, reason_category="bad_hook_input")

    # Note: we do NOT early-return on payload["stop_hook_active"]. The
    # max_retries counter is the loop-protection mechanism. Early-return
    # would prevent us from catching malformed XML written by the model
    # after a no_xml block — the model can produce a parseable end_turn
    # with broken XML, and we want the hook to catch that too.
    stop_active = bool(payload.get("stop_hook_active"))

    counter = _retry_counter(inputs_dir)
    max_retries = int(os.environ.get("GEOS_HOOK_MAX_RETRIES", "2") or 2)

    xml_files = _list_xml(inputs_dir)

    if not xml_files:
        retries = _bump_counter(counter)
        if retries > max_retries:
            _allow_stop(
                inputs_dir,
                reason_category="no_xml_max_retries",
                retries_so_far=retries,
            )
        _block(
            "Stop blocked by verify_outputs hook: no .xml files found under "
            f"{inputs_dir}. This is a required output of the task. Produce the "
            "requested GEOS XML files now using the Write tool (write under "
            f"{inputs_dir}/) and then end your turn.",
            inputs_dir=inputs_dir,
            reason_category="no_xml",
            retries_so_far=retries,
        )

    parse_err = _first_parse_error(xml_files)
    if parse_err is not None:
        path, detail = parse_err
        retries = _bump_counter(counter)
        if retries > max_retries:
            _allow_stop(
                inputs_dir,
                reason_category="parse_error_max_retries",
                retries_so_far=retries,
            )
        rel = path.relative_to(inputs_dir) if path.is_relative_to(inputs_dir) else path
        hint = _doubled_bracket_hint(path)
        _block(
            f"Stop blocked by verify_outputs hook: XML parse error in {rel}: "
            f"{detail}.{hint} Open the file, fix the syntax, then end your turn.",
            inputs_dir=inputs_dir,
            reason_category="parse_error",
            retries_so_far=retries,
            detail=f"{rel}: {detail}",
        )

    if _envflag("GEOS_HOOK_XMLLINT"):
        feedback = _geosx_validate(xml_files, inputs_dir)
        if feedback is not None:
            retries = _bump_counter(counter)
            if retries > max_retries:
                _allow_stop(
                    inputs_dir,
                    reason_category="schema_error_max_retries",
                    retries_so_far=retries,
                )
            executable = os.environ.get("GEOSX_EXECUTABLE", DEFAULT_GEOSX_EXECUTABLE)
            _block(
                "Stop blocked by verify_outputs hook: one or more deck entry "
                f"files under {inputs_dir} fail to load with "
                f"`geosx --validate-input`. Errors:\n\n"
                f"{feedback}\n\n"
                "This means GEOS itself could not build the problem from your "
                "XML: a referenced name (region, material, set, function, "
                "task) does not resolve, or a required block/mesh is missing "
                "or malformed. Fix the reported cause, then re-validate "
                "locally with\n"
                f"  {executable} -i <entry_file>.xml --validate-input\n"
                "before ending your turn. Note: this only catches structural/"
                "reference errors caught while loading the deck — it does "
                "not check attribute names/types against the schema the way "
                "xmllint did.",
                inputs_dir=inputs_dir,
                reason_category="schema_error",
                retries_so_far=retries,
                detail=feedback[:500],
            )

    if _envflag("GEOS_HOOK_SELF_REFLECT"):
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
                "this reflection will not repeat.",
                inputs_dir=inputs_dir,
                reason_category="self_reflect",
                retries_so_far=0,
            )

    _allow_stop(inputs_dir, reason_category="xml_clean")


if __name__ == "__main__":
    main()
