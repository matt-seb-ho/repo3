"""INTEGRATION_REQUIREMENTS R1: the stop policy must reach the hook.

The predecessor loop failed because `reflect.py` rewrote the adapter with no
scoring step in between. The same failure class was live in this file's subject:
`docker_cmd.py` forwarded `GEOS_EVOLVE_FEEDBACK_SHAPE` and `GEOS_EVOLVE_CHECKS`
across the container boundary and `verify_outputs.py` read neither, so a search
over the stop policy would propose, evaluate, accept and reject candidates
differing only in a setting nothing downstream observed -- and it would look
entirely normal in the logs, because the candidates really are different and the
scores really do differ.

R1's acceptance test is therefore deliberately not a config-level assertion.
`test_r1_feedback_shape_changes_the_hook_event_log` runs the hook twice on the
same deck, varying only the feedback shape, and requires the *hook's own event
log* to differ in the text handed back to the agent. If that diff is empty, R1
is not satisfied no matter what the config reports.

The hook is driven as a subprocess, the way Claude Code drives it, rather than
imported: the env-var read path and the stdout contract are the parts that broke.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

HOOK = Path(__file__).resolve().parents[1] / "plugin" / "hooks" / "verify_outputs.py"

BROKEN_XML = "<Problem><Mesh></Problem>\n"
VALID_XML = '<Problem>\n  <Mesh name="m"/>\n</Problem>\n'


def run_hook(
    tmp_path: Path,
    *,
    env: dict[str, str] | None = None,
    deck: str = BROKEN_XML,
    stdin: str = '{"stop_hook_active": false}',
    plugin_root: Path | None = None,
) -> tuple[dict, list[dict]]:
    """Run the hook once in an isolated workspace.

    Returns the parsed stdout payload and every event it logged.
    """
    inputs_dir = tmp_path / "inputs"
    inputs_dir.mkdir(parents=True, exist_ok=True)
    if deck is not None:
        (inputs_dir / "deck.xml").write_text(deck)
    events = tmp_path / "events.jsonl"

    child = {
        k: v for k, v in os.environ.items()
        # Inherit nothing that could smuggle a policy in from the developer's
        # shell -- that would make this test pass for the wrong reason.
        if not k.startswith(("GEOS_", "GEOSX_", "CLAUDE_"))
    }
    child["GEOS_HOOK_INPUTS_DIR"] = str(inputs_dir)
    child["GEOS_HOOK_EVENTS_PATH"] = str(events)
    if plugin_root is not None:
        child["CLAUDE_PLUGIN_ROOT"] = str(plugin_root)
    child.update(env or {})

    proc = subprocess.run(
        [sys.executable, str(HOOK)],
        input=stdin, capture_output=True, text=True, env=child, timeout=60,
    )
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    logged = [
        json.loads(line)
        for line in events.read_text().splitlines() if line.strip()
    ]
    return payload, logged


def sole_event(events: list[dict]) -> dict:
    assert len(events) == 1, events
    return events[0]


# --- R1: the acceptance test ------------------------------------------------


def test_r1_feedback_shape_changes_the_hook_event_log(tmp_path):
    """The gate. Same deck, two shapes, diff the hook's own log."""
    _, minimal = run_hook(
        tmp_path / "minimal", env={"GEOS_EVOLVE_FEEDBACK_SHAPE": "minimal"}
    )
    _, rich = run_hook(
        tmp_path / "rich", env={"GEOS_EVOLVE_FEEDBACK_SHAPE": "errors_plus_tables"}
    )

    a, b = sole_event(minimal), sole_event(rich)
    # Both must actually have blocked -- two identical allows would "differ" in
    # nothing and would pass a laxer assertion.
    assert a["decision"] == b["decision"] == "block"
    assert a["reason_category"] == b["reason_category"] == "parse_error"

    # The predicate R1 is written against: the feedback *text* differs.
    assert a["reason"] != b["reason"]
    assert a["feedback_shape"] == "minimal"
    assert b["feedback_shape"] == "errors_plus_tables"
    # And it differs in the direction claimed: minimal says less.
    assert len(a["reason"]) < len(b["reason"])
    assert "deck.xml" not in a["reason"]
    assert "deck.xml" in b["reason"]


def test_shape_reaches_the_agent_not_only_the_log(tmp_path):
    """The block payload is the channel the agent actually reads."""
    minimal, _ = run_hook(
        tmp_path / "minimal", env={"GEOS_EVOLVE_FEEDBACK_SHAPE": "minimal"}
    )
    rich, _ = run_hook(
        tmp_path / "rich", env={"GEOS_EVOLVE_FEEDBACK_SHAPE": "errors_plus_tables"}
    )
    assert minimal["decision"] == rich["decision"] == "block"
    assert minimal["reason"] != rich["reason"]
    assert "validation error(s); fix them before finishing" in minimal["reason"]
    assert "verbatim" in rich["reason"]


# --- backwards compatibility ------------------------------------------------


def test_unset_environment_reproduces_the_historical_message(tmp_path):
    """An unset policy must be byte-identical to the pre-R1 hook.

    Every run7/run9 comparison and `tests/test_container_spec.py`'s byte-pinned
    rendering assume this. A knob that silently changes the default rewrites the
    baseline it is supposed to be measured against.
    """
    legacy, legacy_events = run_hook(tmp_path / "legacy")
    explicit, _ = run_hook(
        tmp_path / "explicit",
        env={"GEOS_EVOLVE_FEEDBACK_SHAPE": "structured_errors"},
    )
    assert legacy["reason"] == explicit["reason"]
    assert legacy["reason"] == (
        "Stop blocked by verify_outputs hook: XML parse error in deck.xml: "
        "mismatched tag: line 1, column 17. Open the file, fix the syntax, "
        "then end your turn."
    )
    event = sole_event(legacy_events)
    assert event["feedback_shape"] == "structured_errors"
    assert event["feedback_shape_source"] == "default"
    assert event["checks"] == ["parse"]
    assert event["checks_source"] == "legacy_geos_hook_xmllint"


def test_clean_deck_still_allows(tmp_path):
    payload, events = run_hook(tmp_path, deck=VALID_XML)
    assert payload["continue"] is True
    assert sole_event(events)["reason_category"] == "xml_clean"


# --- GEOS_EVOLVE_CHECKS -----------------------------------------------------


def test_checks_gate_which_checks_run(tmp_path):
    """A policy that does not enable `parse` must not block on a parse error."""
    payload, events = run_hook(
        tmp_path, env={"GEOS_EVOLVE_CHECKS": "geosx_validate"}
    )
    assert payload["continue"] is True
    event = sole_event(events)
    assert event["decision"] == "allow"
    assert event["checks"] == ["geosx_validate"]
    assert event["checks_source"] == "env"


def test_checks_the_hook_cannot_run_are_recorded_not_ignored(tmp_path):
    """An unimplemented check name is the same pathology as an unread shape.

    `required_sections` and `constraints` are legal stop-policy values that this
    hook cannot run until sci-sim-op's `checks/` is vendored into the plugin
    directory. Skipping them is acceptable; skipping them *invisibly* would
    recreate exactly the hole R1 exists to close.
    """
    _, events = run_hook(
        tmp_path, env={"GEOS_EVOLVE_CHECKS": "parse,required_sections,constraints"}
    )
    event = sole_event(events)
    assert event["checks"] == ["parse"]
    assert event["checks_unsupported"] == ["required_sections", "constraints"]
    assert event["decision"] == "block"


def test_checks_override_the_legacy_xmllint_flag(tmp_path, geosx_stub):
    """When GEOS_EVOLVE_CHECKS is set it is authoritative, both ways."""
    _, off = run_hook(
        tmp_path / "off",
        deck=VALID_XML,
        env={"GEOS_HOOK_XMLLINT": "1", "GEOS_EVOLVE_CHECKS": "parse",
             "GEOSX_EXECUTABLE": str(geosx_stub)},
    )
    assert sole_event(off)["decision"] == "allow"

    _, on = run_hook(
        tmp_path / "on",
        deck=VALID_XML,
        env={"GEOS_HOOK_XMLLINT": "0", "GEOS_EVOLVE_CHECKS": "parse,geosx_validate",
             "GEOSX_EXECUTABLE": str(geosx_stub)},
    )
    assert sole_event(on)["reason_category"] == "schema_error"


# --- the validator table, which is what errors_plus_tables is about ----------


@pytest.fixture
def geosx_stub(tmp_path_factory):
    """A geosx that fails the way the real one does.

    Banner text copied from a real `geosx --validate-input` run inside the
    geos-eval container on 2026-08-26 (GEOS 1.1.0, sha1 d7c0c185df). It says
    `***** Error`, not `***** Exception` -- which is why the hook's banner regex
    silently never matched and every schema_error block handed the agent stack
    frames instead of the message. Pinning the real text here stops that
    regressing.
    """
    path = tmp_path_factory.mktemp("bin") / "geosx"
    path.write_text(
        "#!/bin/sh\n"
        "echo '***** Error'\n"
        "echo '***** LOCATION: src/coreComponents/dataRepository/ObjectCatalog.hpp:188'\n"
        "echo '***** Error cause: !hasKeyName( objectTypeName )'\n"
        "echo '***** Rank 0'\n"
        "echo '***** Message :'\n"
        "echo 'The tag \"SolidMechanicsLagrangianSSLE\" is invalid within Solvers "
        "(deck.xml, l.3). Please verify the keywords spelling.'\n"
        "echo 'All available tags are: AcousticDG, LaplaceFEM, SinglePhaseFVM, "
        "SolidMechanicsLagrangianFEM, SurfaceGenerator'\n"
        "echo ''\n"
        "echo '***** StackTrace of 23 frames'\n"
        "echo '  - Frame  0:  /opt/geosx-install/lib/libphysicsSolvers.so'\n"
        "echo '  - Frame  1:  geos::PhysicsSolverManager::createChild'\n"
        "exit 1\n"
    )
    path.chmod(0o755)
    return path


def test_the_validator_message_survives_instead_of_the_stack_trace(tmp_path, geosx_stub):
    """Regression test for the defect the R1 verification surfaced.

    Before the banner-regex fix the agent received Frames 9-22 of a C++ stack
    trace and nothing else. The message names the offending tag; the stack trace
    names none of the agent's own inputs.
    """
    payload, _ = run_hook(
        tmp_path, deck=VALID_XML,
        env={"GEOS_EVOLVE_CHECKS": "parse,geosx_validate",
             "GEOS_EVOLVE_FEEDBACK_SHAPE": "structured_errors",
             "GEOSX_EXECUTABLE": str(geosx_stub)},
    )
    assert "is invalid within Solvers" in payload["reason"]
    assert "Frame" not in payload["reason"]


def test_the_three_shapes_are_a_ladder(tmp_path, geosx_stub):
    """minimal < structured_errors < errors_plus_tables, in that order.

    The rungs have to be far enough apart to be worth ablating. `structured_errors`
    says what failed; only `errors_plus_tables` carries the enumerated set of
    legal names, which is what the shape is named for.
    """
    env = {"GEOS_EVOLVE_CHECKS": "parse,geosx_validate",
           "GEOSX_EXECUTABLE": str(geosx_stub)}
    reasons = {}
    for shape in ("minimal", "structured_errors", "errors_plus_tables"):
        payload, _ = run_hook(
            tmp_path / shape, deck=VALID_XML,
            env={**env, "GEOS_EVOLVE_FEEDBACK_SHAPE": shape},
        )
        reasons[shape] = payload["reason"]

    assert len(reasons["minimal"]) < len(reasons["structured_errors"])
    assert len(reasons["structured_errors"]) < len(reasons["errors_plus_tables"])

    # What failed: absent from minimal, present in both richer shapes.
    assert "is invalid within Solvers" not in reasons["minimal"]
    assert "is invalid within Solvers" in reasons["structured_errors"]
    assert "is invalid within Solvers" in reasons["errors_plus_tables"]

    # The table: only the richest shape carries it. Withholding it from
    # structured_errors is what makes the two conditions distinguishable.
    assert "All available tags are" not in reasons["minimal"]
    assert "All available tags are" not in reasons["structured_errors"]
    assert "All available tags are" in reasons["errors_plus_tables"]
    assert "SolidMechanicsLagrangianFEM" in reasons["errors_plus_tables"]
    assert "Copy one verbatim" in reasons["errors_plus_tables"]


# --- the fallback channel and the degradation path --------------------------


def test_policy_arrives_via_stop_policy_env_file(tmp_path):
    """The channel that survives an env allowlist that drops the names.

    SubprocessRunner writes `stop_policy.env` into the materialized adapter
    directory, which is mounted as the plugin dir. docker_cmd.py's allowlist is
    a fixed list in another repo; a file inside the mount is not.
    """
    plugin_root = tmp_path / "plugin"
    plugin_root.mkdir()
    (plugin_root / "stop_policy.env").write_text(
        "GEOS_HOOK_MAX_RETRIES=2\nGEOS_EVOLVE_FEEDBACK_SHAPE=minimal\n"
        "GEOS_EVOLVE_CHECKS=parse\n"
    )
    _, events = run_hook(tmp_path / "ws", plugin_root=plugin_root)
    event = sole_event(events)
    assert event["feedback_shape"] == "minimal"
    assert event["feedback_shape_source"] == "file"
    assert event["checks_source"] == "file"


def test_environment_beats_the_file(tmp_path):
    plugin_root = tmp_path / "plugin"
    plugin_root.mkdir()
    (plugin_root / "stop_policy.env").write_text(
        "GEOS_EVOLVE_FEEDBACK_SHAPE=minimal\n"
    )
    _, events = run_hook(
        tmp_path / "ws",
        env={"GEOS_EVOLVE_FEEDBACK_SHAPE": "errors_plus_tables"},
        plugin_root=plugin_root,
    )
    event = sole_event(events)
    assert event["feedback_shape"] == "errors_plus_tables"
    assert event["feedback_shape_source"] == "env"


def test_an_invalid_shape_degrades_visibly_rather_than_crashing(tmp_path):
    """A stop hook that raises leaves the agent with no verdict at all."""
    payload, events = run_hook(
        tmp_path, env={"GEOS_EVOLVE_FEEDBACK_SHAPE": "verbose"}
    )
    assert payload["decision"] == "block"
    event = sole_event(events)
    assert event["feedback_shape"] == "structured_errors"
    assert event["feedback_shape_source"] == "invalid:verbose"


def test_the_policy_is_logged_even_when_the_hook_is_disabled(tmp_path):
    """Evidence that the hook read the env, on the one path that runs no checks."""
    _, events = run_hook(
        tmp_path,
        env={"GEOS_HOOK_DISABLE": "1", "GEOS_EVOLVE_FEEDBACK_SHAPE": "minimal"},
    )
    event = sole_event(events)
    assert event["reason_category"] == "disabled"
    assert event["feedback_shape"] == "minimal"
