# /// script
# dependencies = [
#   "mcp>=1.0.0,<2",
# ]
# ///
"""MCP server exposing a single GEOS deck validation tool.

geosx-validate-input branch: this file's name is historical (it used to
wrap ``xmllint --schema``); it now shells out to ``geosx --validate-input``,
which actually loads the deck through GEOS's own ProblemManager instead of
checking it against the XSD. Same tool the ``GEOS_HOOK_XMLLINT`` Stop-hook
variant uses (plugin/hooks/verify_outputs.py), exposed here as a tool the
agent can call mid-task to pre-validate a draft instead of waiting for the
end-of-turn hook. See docs/GEOSX_VALIDATE.md for what this catches
differently from the old xmllint path.

Tool name (with the ``mcp__xmllint__`` prefix Claude Code applies):

    mcp__xmllint__validate_geos_xml(xml_path: str) -> str

The argument can be either an absolute path inside the container
(e.g. ``/workspace/inputs/foo.xml``) or relative to ``/workspace/`` /
``/workspace/inputs/``. Pass the deck's *entry* file (the one that
<Included>s the rest) — geosx needs a loadable top-level problem, not an
arbitrary fragment. The geosx binary path is configurable via
``GEOSX_EXECUTABLE`` (defaults to ``/opt/geosx-install/bin/geosx``, matching
the mount docker_cmd.py sets up).
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from mcp.server.fastmcp import FastMCP

DEFAULT_GEOSX_EXECUTABLE = os.environ.get(
    "GEOSX_EXECUTABLE",
    "/opt/geosx-install/bin/geosx",
)
DEFAULT_TIMEOUT = int(os.environ.get("GEOSX_VALIDATE_TIMEOUT", "120") or 120)
DEFAULT_WORKSPACE = Path(os.environ.get("XMLLINT_WORKSPACE_DIR", "/workspace"))
INPUTS_DIR = DEFAULT_WORKSPACE / "inputs"

# geosx prints a clean "***** Exception / LOCATION / Error cause / Message"
# banner before a multi-frame stack trace on a genuine loading failure.
# Keep the banner, drop the noisy stack trace.
GEOSX_ERROR_BANNER_RE = re.compile(r"(\*{5}\s*Exception.*?)(?=\*{5}\s*StackTrace|\Z)", re.DOTALL)

mcp = FastMCP("xmllint")


def _resolve(xml_path: str) -> Path:
    p = Path(xml_path)
    if p.is_absolute():
        return p
    # try ./, /workspace/, /workspace/inputs/
    for candidate in (Path.cwd() / p, DEFAULT_WORKSPACE / p, INPUTS_DIR / p):
        if candidate.exists():
            return candidate
    return p  # let geosx emit the not-found error


def _extract_geosx_error(output: str) -> str:
    match = GEOSX_ERROR_BANNER_RE.search(output)
    if match:
        return match.group(1).strip()
    lines = [line for line in output.splitlines() if line.strip()]
    return "\n".join(lines[-15:])


@mcp.tool()
def validate_geos_xml(xml_path: str) -> str:
    """Validate a GEOS deck by actually loading it with geosx --validate-input.

    Use this BEFORE finishing your turn on the deck's entry file (the one
    that <Included>s the rest, if the deck is split across files) — passing
    an include fragment alone will fail even if the fragment is correct,
    since it is missing the blocks (Mesh, Events, ...) only the entry file
    defines. This catches unknown/misspelled element and attribute names,
    referenced names that don't resolve (region, material, set, function,
    task), and malformed/missing required blocks, by actually building
    GEOS's ProblemManager — GEOS enforces its own attribute/tag registry
    natively during this, so in practice it catches at least as much as the
    old xmllint-based version of this tool did. The one gap: a name a
    solver only resolves during an actual solve step (e.g. a discretization
    name with no matching NumericalMethods entry) can still slip through,
    since --validate-input stops before the run loop starts.

    Args:
        xml_path: Path to the deck's entry XML file. Absolute
            (``/workspace/inputs/foo.xml``) or relative to the workspace
            (``inputs/foo.xml`` / ``foo.xml``).

    Returns:
        Either ``"<file>: validates"`` on success, or the geosx exception
        banner (cause + location + message) on failure, with the stack
        trace stripped out.
    """
    executable = DEFAULT_GEOSX_EXECUTABLE
    if not Path(executable).exists():
        return (
            f"ERROR: geosx binary not present at {executable} in this "
            "container. This validator requires the geosx-install/thirdPartyLibs "
            "mounts from docker_cmd.py. Validate by hand if possible."
        )
    target = _resolve(xml_path)
    if not target.exists():
        return f"ERROR: file not found: {target} (resolved from {xml_path!r})"

    scratch = Path(tempfile.mkdtemp(prefix="geosx_validate_"))
    try:
        res = subprocess.run(
            [executable, "-i", str(target), "--validate-input", "-o", str(scratch)],
            cwd=scratch,
            capture_output=True,
            text=True,
            timeout=DEFAULT_TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        return f"ERROR: geosx timed out after {DEFAULT_TIMEOUT}s on {target}"
    finally:
        shutil.rmtree(scratch, ignore_errors=True)

    if res.returncode == 0:
        return f"{target}: validates"
    detail = _extract_geosx_error(res.stdout + res.stderr)
    return f"{target}: FAILS to load (geosx exit={res.returncode})\n{detail}"


if __name__ == "__main__":
    mcp.run()
