"""Backend-neutral container invocation, rendered for docker or enroot.

Why this exists
---------------
serv6/9/10/11 withdrew docker access ("docker can get sudo privilege") and
point users at enroot instead. This project only ever used a container for
filesystem isolation and a reproducible toolchain -- never for privileged
operations -- so enroot is a straight substitute.

Rather than fork the command builders, they now emit a :class:`ContainerSpec`
(mounts, env, image, argv) and a renderer turns it into an argv list for the
selected backend. The docker renderer is byte-for-byte identical to the
hand-written command it replaced; ``tests/test_container_spec.py`` pins that.

Backend selection: ``REPO3_CONTAINER_BACKEND=docker|enroot`` (default docker).

Semantic differences the renderers absorb
-----------------------------------------
``--user uid:gid``
    docker needs it so the container does not write root-owned files into the
    mounted workspace. enroot is unprivileged by construction: the calling user
    is already the user inside. The flag has no enroot equivalent and none is
    needed.

``--rm``
    enroot's ``start IMAGE`` form is inherently ephemeral -- it instantiates the
    squashfs image, runs, and leaves no named container behind. No flag needed.

mount options
    docker's ``-v src:dst:ro`` becomes enroot's fstab syntax
    ``--mount src:dst:none,bind,ro,x-create=dir``. ``x-create=dir`` matters: the
    enroot rootfs is read-only unless ``--rw``, so a mountpoint that does not
    already exist in the image cannot be created implicitly the way docker does.

WORKDIR
    docker honours the image's ``WORKDIR /workspace``. enroot does not read the
    OCI config at start time, so the renderer wraps the command to ``cd`` first.

``$HOME`` must exist
    enroot chdirs into ``$HOME`` during switchroot and aborts if it is absent.
    See :func:`prepare_enroot_workspace`.
"""

from __future__ import annotations

import os
import shlex
from dataclasses import dataclass, field
from pathlib import Path

DOCKER = "docker"
ENROOT = "enroot"
_VALID_BACKENDS = (DOCKER, ENROOT)

# enroot is driven through a *named container* rather than a .sqsh path.
# `enroot start IMAGE.sqsh` needs squashfuse to fuse-mount the image, and
# squashfuse is not installed on serv6 (installing it needs admin). `enroot
# create` unpacks with unsquashfs instead, which is present, and the resulting
# named container starts with a read-only rootfs -- so concurrent `enroot start`
# calls against one container are safe. Verified on serv6 with three
# simultaneous starts; this matters because the runner defaults to --workers 4.
DEFAULT_ENROOT_CONTAINER = os.environ.get("REPO3_ENROOT_CONTAINER", "geos-eval")

# The image sets WORKDIR /workspace; enroot needs it applied explicitly.
CONTAINER_WORKDIR = "/workspace"


def active_backend() -> str:
    """The container backend for this process, from REPO3_CONTAINER_BACKEND."""
    backend = os.environ.get("REPO3_CONTAINER_BACKEND", DOCKER).strip().lower()
    if backend not in _VALID_BACKENDS:
        raise ValueError(
            f"REPO3_CONTAINER_BACKEND={backend!r} is not one of {_VALID_BACKENDS}"
        )
    return backend


@dataclass(frozen=True)
class Mount:
    source: Path | str
    target: Path | str
    read_only: bool = False


@dataclass
class ContainerSpec:
    """One container invocation, independent of how it is launched."""

    image: str
    argv: list[str]
    mounts: list[Mount] = field(default_factory=list)
    #: ``VAR`` forwards the host value; ``VAR=value`` sets it explicitly.
    env: list[str] = field(default_factory=list)
    workdir: str | None = CONTAINER_WORKDIR

    def render(self, backend: str | None = None) -> list[str]:
        backend = backend or active_backend()
        if backend == DOCKER:
            return render_docker(self)
        if backend == ENROOT:
            return render_enroot(self)
        raise ValueError(f"unknown backend: {backend!r}")


def render_docker(spec: ContainerSpec) -> list[str]:
    cmd = [
        "docker", "run", "--rm",
        "--user", f"{os.getuid()}:{os.getgid()}",
    ]
    for m in spec.mounts:
        suffix = ":ro" if m.read_only else ":rw"
        cmd += ["-v", f"{m.source}:{m.target}{suffix}"]
    for e in spec.env:
        cmd += ["-e", e]
    cmd += [spec.image, *spec.argv]
    return cmd


def render_enroot(spec: ContainerSpec, container: str | None = None) -> list[str]:
    """Render for ``enroot start`` against a named container.

    ``spec.image`` is a docker image *tag*; the enroot container created from it
    by run/build_enroot_image.sh carries the same name by convention. Override
    with ``REPO3_ENROOT_CONTAINER``.
    """
    image = container or _enroot_container_for(spec.image)
    cmd = ["enroot", "start"]
    for m in spec.mounts:
        flags = ["none", "bind", "ro" if m.read_only else "rw", "x-create=dir"]
        cmd += ["--mount", f"{m.source}:{m.target}:{','.join(flags)}"]
    for e in spec.env:
        cmd += ["--env", e]
    cmd += [str(image)]
    if spec.workdir:
        # enroot does not apply the image's WORKDIR, and the argv may legitimately
        # contain a leading `--` separator, so wrap rather than prepend a cd.
        inner = " ".join(shlex.quote(a) for a in spec.argv)
        cmd += ["sh", "-c", f"cd {shlex.quote(spec.workdir)} && exec {inner}"]
    else:
        cmd += spec.argv
    return cmd


def _enroot_container_for(image_tag: str) -> str:
    return os.environ.get("REPO3_ENROOT_CONTAINER") or image_tag


def prepare_enroot_workspace(result_dir: Path) -> None:
    """Create the directories enroot requires to exist *before* the container starts.

    enroot's switchroot chdirs into ``$HOME`` as it enters the container and
    aborts if that directory is missing::

        enroot-switchroot: failed to change directory: /workspace/.claude_home

    docker has no such requirement -- it creates the path or simply starts in
    ``WORKDIR`` -- so this is pure enroot compatibility. ``$HOME`` here points
    inside ``/workspace``, which is a bind mount of ``result_dir``, so creating
    it on the host is what makes it exist in the container.

    Safe and idempotent under docker; call it unconditionally.
    """
    for sub in (".claude_home", ".claude_home/.config", ".uv_cache"):
        (result_dir / sub).mkdir(parents=True, exist_ok=True)
