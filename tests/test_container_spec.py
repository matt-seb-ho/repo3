"""The docker rendering must not drift, and the enroot rendering must be faithful.

The docker cases pin the exact argv the hand-written builder produced before the
ContainerSpec refactor (commit on feat/enroot-backend), minus the two
INTEGRATION_REQUIREMENTS R1 forwards that were deliberately added at the same
time. If a future edit changes the docker command, these fail loudly rather than
silently altering every historical comparison's runtime.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from runner.container_spec import (
    DOCKER,
    ENROOT,
    ContainerSpec,
    Mount,
    active_backend,
    render_docker,
    render_enroot,
)

SPEC = ContainerSpec(
    image="geos-eval",
    mounts=[
        Mount("/geos/filtered", "/geos_lib", read_only=True),
        Mount("/res/task1", "/workspace"),
    ],
    env=["HOME=/workspace/.claude_home", "OPENROUTER_API_KEY"],
    argv=["claude", "-p", "--", "-- BEGIN SPEC"],
)


def test_docker_rendering_is_stable():
    assert render_docker(SPEC) == [
        "docker", "run", "--rm",
        "--user", f"{os.getuid()}:{os.getgid()}",
        "-v", "/geos/filtered:/geos_lib:ro",
        "-v", "/res/task1:/workspace:rw",
        "-e", "HOME=/workspace/.claude_home",
        "-e", "OPENROUTER_API_KEY",
        "geos-eval",
        "claude", "-p", "--", "-- BEGIN SPEC",
    ]


def test_enroot_rendering():
    cmd = render_enroot(SPEC, container="geos-eval")
    assert cmd[:2] == ["enroot", "start"]
    # read-only and read-write mounts both carry x-create=dir: the enroot rootfs
    # is read-only, so a missing mountpoint cannot be created implicitly.
    assert "--mount" in cmd
    assert "/geos/filtered:/geos_lib:none,bind,ro,x-create=dir" in cmd
    assert "/res/task1:/workspace:none,bind,rw,x-create=dir" in cmd
    assert "--env" in cmd and "OPENROUTER_API_KEY" in cmd
    assert "geos-eval" in cmd
    # no docker-only flags leak through
    assert "--user" not in cmd and "--rm" not in cmd and "-v" not in cmd


def test_enroot_applies_workdir_because_it_ignores_the_image_WORKDIR():
    cmd = render_enroot(SPEC, container="geos-eval")
    assert cmd[-3:-1] == ["sh", "-c"]
    assert cmd[-1].startswith("cd /workspace && exec ")


def test_enroot_quotes_arguments_that_would_otherwise_resplit():
    """The prompt legitimately contains spaces and a leading `--`."""
    spec = ContainerSpec(
        image="geos-eval",
        argv=["claude", "--", "--- BEGIN SIMULATION SPECIFICATION ---"],
    )
    inner = render_enroot(spec, container="geos-eval")[-1]
    assert "'--- BEGIN SIMULATION SPECIFICATION ---'" in inner


def test_backend_selection(monkeypatch):
    monkeypatch.delenv("REPO3_CONTAINER_BACKEND", raising=False)
    assert active_backend() == DOCKER
    monkeypatch.setenv("REPO3_CONTAINER_BACKEND", "enroot")
    assert active_backend() == ENROOT
    monkeypatch.setenv("REPO3_CONTAINER_BACKEND", "podman")
    with pytest.raises(ValueError):
        active_backend()


def test_spec_render_dispatches_on_env(monkeypatch):
    monkeypatch.setenv("REPO3_CONTAINER_BACKEND", "enroot")
    monkeypatch.setenv("REPO3_ENROOT_CONTAINER", "geos-eval")
    assert SPEC.render()[0] == "enroot"
    monkeypatch.setenv("REPO3_CONTAINER_BACKEND", "docker")
    assert SPEC.render()[0] == "docker"


def test_prepare_enroot_workspace_creates_HOME(tmp_path):
    """enroot aborts in switchroot if $HOME is missing; docker does not."""
    from runner.container_spec import prepare_enroot_workspace

    prepare_enroot_workspace(tmp_path)
    assert (tmp_path / ".claude_home").is_dir()
    assert (tmp_path / ".claude_home/.config").is_dir()
    assert (tmp_path / ".uv_cache").is_dir()
    prepare_enroot_workspace(tmp_path)  # idempotent


def test_r1_forwards_are_present_in_the_real_builder():
    """R1: the stop policy must reach the hook, or a search varies nothing."""
    from runner.docker_cmd import build_claude_native_command

    cmd = build_claude_native_command(
        filtered_geos=Path("/g"), result_dir=Path("/r"),
        plugin_dir=Path("/p"), vector_db_dir=Path("/v"),
        model="m", system_prompt="s", prompt="p",
    )
    assert "GEOS_EVOLVE_FEEDBACK_SHAPE" in cmd
    assert "GEOS_EVOLVE_CHECKS" in cmd
