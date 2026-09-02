#!/usr/bin/env python3
"""R1 acceptance: does the stop policy actually reach the hook, in the container?

`tests/test_verify_outputs_hook.py` proves the hook honours
`GEOS_EVOLVE_FEEDBACK_SHAPE` and `GEOS_EVOLVE_CHECKS` on the host. That is half of
R1. The other half is the container boundary: `docker_cmd.py` forwards a *fixed
allowlist*, and a policy that reaches the host process can still die there --
which is exactly the shape of the original defect, one repo removed.

So this drives the real thing. It calls `build_claude_native_command` to get the
genuine rendered invocation (real mounts, real env allowlist, real backend
renderer), swaps the `claude` argv for the hook itself, and runs it inside the
container against a deck on the mounted workspace. Then it diffs the hook's own
event log across feedback shapes.

The control arm strips the two `--env` forwards back out of the rendered command,
reproducing the pre-fix boundary. If the control's two shapes come back identical
while the treated arm's differ, the forwarding is what carries the policy -- and
that is a measurement, not an assertion.

    python3 scripts/verify_r1_feedback_channel.py --out DIR

Exit 0 iff every arm behaved as R1 requires.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from runner.constants import (  # noqa: E402
    DEFAULT_GEOS_LIB_DIR,
    DEFAULT_PLUGIN_DIR,
    DEFAULT_VECTOR_DB_DIR,
)
from runner.container_spec import prepare_enroot_workspace  # noqa: E402
from runner.docker_cmd import build_claude_native_command  # noqa: E402

R1_ENV_NAMES = ("GEOS_EVOLVE_FEEDBACK_SHAPE", "GEOS_EVOLVE_CHECKS")
HOOK_IN_CONTAINER = "/plugins/repo3/hooks/verify_outputs.py"

# Parses, but names an attribute GEOS does not define -- the case where the real
# validator prints its table of legal attribute names, which is the signal
# `errors_plus_tables` exists to preserve.
DECK_UNKNOWN_ATTR = """<?xml version="1.0" ?>
<Problem>
  <Solvers>
    <SolidMechanicsLagrangianSSLE name="s" timeIntegrationOption="QuasiStatic"
                                  discretization="FE1" targetRegions="{Region}"
                                  thisAttributeDoesNotExist="1"/>
  </Solvers>
</Problem>
"""

# Does not parse at all -- the cheapest block, and the largest single block
# category in the run7/run9 lineage.
DECK_BROKEN = "<Problem><Mesh></Problem>\n"


def render_hook_command(result_dir: Path, *, forward_r1: bool) -> list[str]:
    """The real harness command, with the hook substituted for the agent."""
    cmd = build_claude_native_command(
        filtered_geos=DEFAULT_GEOS_LIB_DIR,
        result_dir=result_dir,
        plugin_dir=DEFAULT_PLUGIN_DIR,
        vector_db_dir=DEFAULT_VECTOR_DB_DIR,
        model="stealth/ox-alpha",
        system_prompt="unused",
        prompt="unused",
    )
    if not forward_r1:
        # Reproduce the pre-fix allowlist by deleting the two forwards.
        cmd = _strip_env(cmd, R1_ENV_NAMES)

    inner = f"cd /workspace && exec python3 {HOOK_IN_CONTAINER}"
    if cmd[-3:-1] == ["sh", "-c"]:          # enroot renderer
        return cmd[:-1] + [inner]
    # docker renderer: image followed by argv
    idx = cmd.index("geos-eval")
    return cmd[: idx + 1] + ["sh", "-c", inner]


def _strip_env(cmd: list[str], names: tuple[str, ...]) -> list[str]:
    out: list[str] = []
    i = 0
    while i < len(cmd):
        if cmd[i] in ("-e", "--env") and i + 1 < len(cmd) and cmd[i + 1] in names:
            i += 2
            continue
        out.append(cmd[i])
        i += 1
    return out


def run_arm(
    root: Path,
    name: str,
    *,
    deck: str,
    shape: str,
    checks: str,
    forward_r1: bool = True,
) -> dict:
    """One hook invocation inside the container. Returns its logged event."""
    result_dir = root / name
    (result_dir / "inputs").mkdir(parents=True, exist_ok=True)
    (result_dir / "inputs" / "deck.xml").write_text(deck)
    prepare_enroot_workspace(result_dir)

    cmd = render_hook_command(result_dir, forward_r1=forward_r1)
    env = os.environ.copy()
    env["GEOS_EVOLVE_FEEDBACK_SHAPE"] = shape
    env["GEOS_EVOLVE_CHECKS"] = checks
    env["ANTHROPIC_API_KEY"] = ""

    proc = subprocess.run(
        cmd, input='{"stop_hook_active": false}',
        capture_output=True, text=True, env=env, timeout=900,
    )
    log = result_dir / ".verify_hook_events.jsonl"
    events = []
    if log.is_file():
        events = [json.loads(l) for l in log.read_text().splitlines() if l.strip()]
    return {
        "arm": name,
        "shape_requested": shape,
        "checks_requested": checks,
        "forward_r1": forward_r1,
        "returncode": proc.returncode,
        "stdout": proc.stdout[-4000:],
        "stderr": proc.stderr[-2000:],
        "events": events,
        "event_log": str(log),
        "command": cmd,
    }


def reason_of(arm: dict) -> str:
    for event in arm["events"]:
        if "reason" in event:
            return event["reason"]
    return ""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    out = args.out
    out.mkdir(parents=True, exist_ok=True)

    arms: list[dict] = []
    checks_all = "parse,geosx_validate"

    # A. parse failure, forwarded, two shapes.
    for shape in ("minimal", "errors_plus_tables"):
        arms.append(run_arm(out, f"parse_{shape}", deck=DECK_BROKEN,
                            shape=shape, checks="parse"))
    # B. real geosx --validate-input failure, forwarded, three shapes.
    for shape in ("minimal", "structured_errors", "errors_plus_tables"):
        arms.append(run_arm(out, f"validate_{shape}", deck=DECK_UNKNOWN_ATTR,
                            shape=shape, checks=checks_all))
    # C. control: identical, but with the two forwards stripped from the command.
    for shape in ("minimal", "errors_plus_tables"):
        arms.append(run_arm(out, f"control_{shape}", deck=DECK_BROKEN,
                            shape=shape, checks="parse", forward_r1=False))

    (out / "arms.json").write_text(json.dumps(arms, indent=2))

    by = {a["arm"]: a for a in arms}
    checks_result: list[tuple[str, bool, str]] = []

    def record(label: str, ok: bool, detail: str = "") -> None:
        checks_result.append((label, ok, detail))

    for family, a, b in (
        ("parse", "parse_minimal", "parse_errors_plus_tables"),
        ("validate", "validate_minimal", "validate_errors_plus_tables"),
    ):
        ra, rb = reason_of(by[a]), reason_of(by[b])
        record(f"{family}: both arms blocked", bool(ra) and bool(rb),
               f"{len(ra)} vs {len(rb)} chars")
        record(f"{family}: feedback text differs across shapes", ra != rb,
               f"{len(ra)} vs {len(rb)} chars")
        record(f"{family}: shape recorded as requested",
               by[a]["events"] and by[a]["events"][0].get("feedback_shape") == "minimal"
               and by[b]["events"][0].get("feedback_shape") == "errors_plus_tables",
               "")
        record(f"{family}: shape source is the forwarded env",
               all(e.get("feedback_shape_source") == "env"
                   for arm in (by[a], by[b]) for e in arm["events"]), "")

    cm, ce = reason_of(by["control_minimal"]), reason_of(by["control_errors_plus_tables"])
    record("control (forwards stripped): shapes collapse to identical text",
           cm == ce and bool(cm), f"{len(cm)} vs {len(ce)} chars")
    record("control: shape falls back to the default",
           all(e.get("feedback_shape") == "structured_errors"
               for arm in (by["control_minimal"], by["control_errors_plus_tables"])
               for e in arm["events"]), "")

    vt = reason_of(by["validate_errors_plus_tables"])
    record("validate: real geosx output reached the agent",
           "validate-input" in vt, "")

    hook = REPO / "plugin" / "hooks" / "verify_outputs.py"
    receipt = {
        "ok": all(ok for _, ok, _ in checks_result),
        "verified_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "hook": str(hook),
        # Named so nothing downstream can trust this receipt for a hook that has
        # since changed. See harness_evolve.integration.check_r1.
        "hook_sha256": hashlib.sha256(hook.read_bytes()).hexdigest(),
        "checks": [{"label": l, "ok": ok, "detail": d} for l, ok, d in checks_result],
        "headline": " / ".join(
            f"{a['arm']}={len(reason_of(a))}ch" for a in arms
            if a["arm"].startswith("validate_")
        ),
        "artifacts": str(out),
    }
    (out / "receipt.json").write_text(json.dumps(receipt, indent=2))

    lines = ["# R1 verification — container boundary", ""]
    for label, ok, detail in checks_result:
        lines.append(f"- [{'PASS' if ok else 'FAIL'}] {label}"
                     + (f" ({detail})" if detail else ""))
    lines += ["", "## Feedback text per arm", ""]
    for a in arms:
        r = reason_of(a)
        lines += [f"### {a['arm']} (forward_r1={a['forward_r1']})",
                  f"event log: `{a['event_log']}`", "", "```", r or "(no block)", "```", ""]
    (out / "REPORT.md").write_text("\n".join(lines))

    print("\n".join(lines[: 2 + len(checks_result)]))
    print(f"\nartifacts: {out}")
    return 0 if all(ok for _, ok, _ in checks_result) else 1


if __name__ == "__main__":
    raise SystemExit(main())
