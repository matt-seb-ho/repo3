#!/usr/bin/env bash
# Build the geos-eval container image for enroot, without docker.
#
# serv6/9/10/11 withdrew docker access; enroot is the sanctioned replacement.
# enroot cannot execute a Dockerfile, so this reproduces run/Dockerfile's RUN
# steps inside an unprivileged container and exports the result as squashfs.
#
#   bash run/build_enroot_image.sh            # build to the default location
#   bash run/build_enroot_image.sh --force    # rebuild over an existing image
#
# Output: ~/.local/share/enroot/images/geos-eval.sqsh
#         (override with $REPO3_ENROOT_IMAGE)
set -euo pipefail

BASE_URI="docker://ubuntu:24.04"
BUILD_NAME="geos-eval-build"
OUT="${REPO3_ENROOT_IMAGE:-$HOME/.local/share/enroot/images/geos-eval.sqsh}"
FORCE=0
[ "${1:-}" = "--force" ] && FORCE=1

command -v enroot >/dev/null || { echo "enroot not found on PATH" >&2; exit 1; }
mkdir -p "$(dirname "$OUT")"

if [ -f "$OUT" ] && [ "$FORCE" -eq 0 ]; then
  echo "image already exists: $OUT  (use --force to rebuild)"; exit 0
fi

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
cd "$WORK"

echo "==> importing $BASE_URI"
enroot import -o base.sqsh "$BASE_URI"

echo "==> creating build container"
enroot remove -f "$BUILD_NAME" 2>/dev/null || true
enroot create --name "$BUILD_NAME" base.sqsh

# The Dockerfile's RUN steps, verbatim in intent. Run as root inside the
# container (--root is a *namespace* remap, not host privilege) with a writable
# rootfs (--rw), which is what `docker build` gave us.
cat > provision.sh <<'PROVISION'
set -eux
export DEBIAN_FRONTEND=noninteractive

apt-get update
apt-get install -y curl git python3 python3-pip ca-certificates gnupg libxml2-utils
rm -rf /var/lib/apt/lists/*

# Node.js 22.x -- acpx requires >= 22.12.0
curl -fsSL https://deb.nodesource.com/setup_22.x | bash -
apt-get install -y nodejs
rm -rf /var/lib/apt/lists/*

# cursor-agent
curl -fsSL https://cursor.com/install | bash

# uv, in /usr/local/bin so a non-root container user can execute it
export UV_INSTALL_DIR=/usr/local/bin
curl -LsSf https://astral.sh/uv/install.sh | sh

npm install -g @anthropic-ai/claude-code
npm install -g acpx@latest

mkdir -p /workspace

# The Dockerfile sets ENV PATH="/root/.local/bin:${PATH}". enroot does not read
# the OCI config at start time, so persist it where a login shell will find it.
echo 'export PATH="/root/.local/bin:/usr/local/bin:$PATH"' > /etc/profile.d/geos-eval.sh
chmod 0644 /etc/profile.d/geos-eval.sh

# Mountpoints must exist: the rootfs is read-only at run time, and although the
# renderer passes x-create=dir, pre-creating them keeps failures legible.
mkdir -p /geos_lib /plugins/repo3 /supervisor \
         /opt/geosx-install /opt/geosx-tpl /opt/geosx-conda-lib \
         /data/shared/geophysics_agent_data/data/vector_db
PROVISION

echo "==> provisioning (this pulls node + npm packages; several minutes)"
# x-create=dir: /build does not exist in the base image, and enroot -- unlike
# docker -- will not create a missing mountpoint implicitly.
enroot start --root --rw --mount "$WORK:/build:none,bind,ro,x-create=dir" "$BUILD_NAME" \
    bash /build/provision.sh

echo "==> exporting to $OUT"
enroot export --force --output "$OUT" "$BUILD_NAME"
enroot remove -f "$BUILD_NAME"

# The harness starts a *named container*, not the .sqsh: `enroot start IMG.sqsh`
# needs squashfuse to fuse-mount, and squashfuse is not installed on serv6
# (installing it needs admin). `enroot create` unpacks with unsquashfs, which is
# present. The unpacked rootfs is read-only at start, so concurrent starts are
# safe -- verified with three simultaneous starts, which matters at --workers 4.
RUNTIME_NAME="${REPO3_ENROOT_CONTAINER:-geos-eval}"
echo "==> creating runtime container '$RUNTIME_NAME'"
enroot remove -f "$RUNTIME_NAME" 2>/dev/null || true
enroot create --name "$RUNTIME_NAME" "$OUT"

echo
echo "done."
echo "  image:     $OUT"
echo "  container: $RUNTIME_NAME  (enroot list)"
echo
echo "smoke test:"
echo "  enroot start $RUNTIME_NAME sh -lc 'claude --version; uv --version; xmllint --version'"
echo
echo "then run the harness with:"
echo "  export REPO3_CONTAINER_BACKEND=enroot"
