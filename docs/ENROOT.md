# Running without docker: the enroot backend

serv6/9/10/11 withdrew docker access — *"Due to safety reasons (e.g., docker can
get sudo privilege), we have stopped docker access... Please use enroot instead."*

This project only ever used a container for **filesystem isolation and a
reproducible toolchain**, never for anything privileged, so enroot is a straight
substitute. Nothing about the experiment changes.

## TL;DR

```bash
bash run/build_enroot_image.sh          # once per machine, ~10 min (network installs)
export REPO3_CONTAINER_BACKEND=enroot
# ...then run the harness exactly as before
```

## How the backend switch works

`src/runner/container_spec.py` holds a backend-neutral `ContainerSpec` (mounts,
env, image, argv). `docker_cmd.py`'s two builders emit a spec; a renderer turns
it into argv for the selected backend, chosen by `REPO3_CONTAINER_BACKEND`
(`docker` by default, so existing setups are unaffected).

`tests/test_container_spec.py` pins the docker rendering to the exact argv the
hand-written builder produced. The refactor was verified byte-for-byte against
the pre-refactor implementation for the plugin, no-plugin, and MCP-smoke cases —
the *only* difference is the two R1 env forwards added deliberately (below).

## What differs between docker and enroot, and why

Each of these was found by running it on serv6, not by reading docs.

| Concern | docker | enroot | How it is handled |
|---|---|---|---|
| User identity | needs `--user uid:gid` or it writes root-owned files into the mounted workspace | already unprivileged; you *are* the calling user inside (verified `uid=1009`) | renderer omits `--user`; host files come out correctly owned |
| Ephemerality | `--rm` | named container, read-only rootfs, nothing to clean up | renderer omits `--rm` |
| Mounts | `-v src:dst:ro` | `--mount src:dst:none,bind,ro,x-create=dir` | `x-create=dir` is required: the rootfs is read-only, so a missing mountpoint cannot be created implicitly |
| `WORKDIR` | honoured from the image | **not** read at start time | renderer wraps the command as `sh -c 'cd /workspace && exec …'`, with `shlex.quote` so a prompt beginning `--- BEGIN SIMULATION SPECIFICATION ---` still survives |
| `$HOME` | may be absent | **switchroot chdirs into `$HOME` and aborts if missing** | `prepare_enroot_workspace()` creates `result_dir/.claude_home{,/.config}` and `.uv_cache` before launch; called from `orchestrator.py`, no-op under docker |
| Image | tag `geos-eval` | a *named container*, not the `.sqsh` | see below |

### Why a named container rather than the `.sqsh` directly

`enroot start image.sqsh` needs **squashfuse** to fuse-mount the image, and
squashfuse is not installed on serv6 (installing it needs admin — the thing we
are working around). `enroot create` unpacks with `unsquashfs`, which *is*
present, producing a named container whose rootfs is read-only at start.

That read-only rootfs is what makes this safe for the runner's `--workers 4`:
concurrent `enroot start` calls against one container do not interfere. Verified
with three simultaneous starts. All writes go to the `/workspace` bind mount.

Override the container name with `REPO3_ENROOT_CONTAINER` (default `geos-eval`).

## Building the image without docker

`enroot` cannot execute a Dockerfile, so `run/build_enroot_image.sh` reproduces
`run/Dockerfile`'s `RUN` steps inside an unprivileged container:

1. `enroot import docker://ubuntu:24.04`
2. `enroot create` a scratch build container
3. `enroot start --root --rw` it and run the provisioning script — `--root` is a
   *user-namespace* remap, not host privilege, which is exactly the property the
   admins wanted
4. `enroot export` to squashfs, then `enroot create` the runtime container

The provisioning script also pre-creates the mountpoints (`/geos_lib`,
`/plugins/repo3`, `/opt/geosx-*`, the vector-db path) and writes
`/etc/profile.d/geos-eval.sh` for the `PATH` the Dockerfile set via `ENV`, since
enroot does not apply the image's OCI environment.

## Verifying it works

```bash
enroot list                                    # geos-eval present?
enroot start geos-eval sh -lc 'claude --version; uv --version; xmllint --version'
```

Then a single real task before trusting any aggregate — see
`sci-sim-op/docs/INTEGRATION_REQUIREMENTS.md` R3.

## Verified end to end on serv6 (2026-08-26)

Built with `run/build_enroot_image.sh` — image 1.3 GB at
`~/.local/share/enroot/images/geos-eval.sqsh`, runtime container `geos-eval`.

```
toolchain     claude 2.1.246 · uv 0.12.5 · libxml 20914 · node v22.23.2 · python 3.12.3
rendered cmd  REPO3_CONTAINER_BACKEND=enroot -> "enroot start", 10 mounts, 24 envs,
              R1 vars forwarded, no --user/--rm/-v leakage
mounts        /geos_lib, /opt/geosx-*, GT tree all visible read-only inside
isolation     read-only mounts enforced; rootfs read-only; writes land in /workspace
ownership     files created in the workspace are owned by the calling user, no --user
concurrency   3 simultaneous `enroot start` against one container, all succeeded
geosx         `geosx --validate-input -i <real GT deck>` ran to completion inside the
              container with the harness's LD_LIBRARY_PATH
```

The last line is the one that mattered most: the `--validate-input` oracle is the
attribute/element-typo checker the hook depends on, it needs six separate
read-only mounts plus a hand-built `LD_LIBRARY_PATH`, and it works unchanged.

## Host paths the container still needs

These are host-side and unchanged by the backend switch. All confirmed present
on serv6:

- `/data/shared/geophysics_agent_data/data/{eval/experiments_gt,eval/experiments_test36_template,GEOS,vector_db}`
- `/home/brian/.geosx_docker_runtime/{install,tpl}` and
  `/home/brian/miniconda3/envs/geos-build/lib` — the `geosx --validate-input`
  runtime (see `constants.py` for why there are three separate roots)
- `/data/matt/geos_eval_tmp` — scratch

## R1, and what is still not done

`INTEGRATION_REQUIREMENTS` R1 (from `sci-sim-op`) says the stop policy is a
*searchable component*, so `GEOS_EVOLVE_FEEDBACK_SHAPE` and `GEOS_EVOLVE_CHECKS`
must reach the hook — otherwise a search proposes, evaluates, accepts and rejects
candidates that differ only in a setting nothing reads, and every result is
run-to-run noise wearing the label of a mechanism.

**Done here:** both variables are now in the forwarded env allowlist, for both
backends.

**Still to do:** `plugin/hooks/verify_outputs.py` does not read them — it reads
only `GEOS_HOOK_INPUTS_DIR`. Forwarding is necessary but not sufficient. Making
the hook honour a feedback shape (`minimal` / `structured_errors` /
`errors_plus_tables`) changes what the agent sees on a failed termination, which
is a genuine experimental design decision and should be made together with
whichever search implementation you continue. Until then, **do not vary the stop
policy in a search and believe the result.**

The verification R1 asks for, once the hook reads them: run one task at
`feedback_shape=minimal` and one at `errors_plus_tables`, and diff the hook's own
event log. Identical feedback text means R1 is not satisfied, whatever the config
says.
