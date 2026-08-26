"""Docker command building, MCP preflight, vector-DB copy, and primer-file management."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from .container_spec import ContainerSpec, Mount
from .constants import (
    CONTAINER_GEOS_PRIMER_PATH,
    CONTAINER_GEOSX_CONDA_LIB_DIR,
    CONTAINER_GEOSX_EXECUTABLE,
    CONTAINER_GEOSX_INSTALL_DIR,
    CONTAINER_GEOSX_TPL_DIR,
    CONTAINER_MCP_CONFIG_PATH,
    CONTAINER_PLUGIN_DIR,
    CONTAINER_SETTINGS_PATH,
    CONTAINER_VECTOR_DB_DIR,
    DEFAULT_GEOSX_CONDA_LIB_DIR,
    DEFAULT_GEOSX_INSTALL_DIR,
    DEFAULT_GEOSX_TPL_ROOT,
    DEFAULT_GEOSX_TPL_SUBDIRS,
    DOCKER_IMAGE,
    NATIVE_CLAUDE_DISALLOWED_TOOLS,
    NATIVE_CLAUDE_TOOLS,
)


def create_runtime_vector_db_copy(vector_db_src: Path, result_dir: Path) -> Path:
    """Create a writable per-task ChromaDB copy.

    ChromaDB opens its sqlite backing files in a way that can write lock files
    even for read-oriented queries, so the container cannot mount the shared DB
    read-only.  Copying keeps the shared source untouched while allowing each
    parallel task to run independently.
    """
    vector_db_dest = result_dir / ".vector_db_runtime"
    if vector_db_dest.exists():
        shutil.rmtree(vector_db_dest)
    shutil.copytree(vector_db_src, vector_db_dest, symlinks=True)
    return vector_db_dest


def remove_workspace_geos_primer(result_dir: Path) -> None:
    primer_dest = result_dir / CONTAINER_GEOS_PRIMER_PATH.name
    if primer_dest.is_dir():
        shutil.rmtree(primer_dest)
    elif primer_dest.exists() or primer_dest.is_symlink():
        primer_dest.unlink()


def build_claude_native_mcp_smoke_command(
    *,
    result_dir: Path,
    plugin_dir: Path,
    vector_db_dir: Path,
) -> list[str]:
    spec = ContainerSpec(
        image=DOCKER_IMAGE,
        mounts=[
            Mount(result_dir, "/workspace"),
            Mount(plugin_dir, "/plugins/repo3", read_only=True),
            Mount(vector_db_dir, CONTAINER_VECTOR_DB_DIR),
        ],
        env=[
            "HOME=/workspace/.claude_home",
            "UV_CACHE_DIR=/workspace/.uv_cache",
            "CLAUDE_PLUGIN_ROOT=/plugins/repo3",
            f"GEOS_VECTOR_DB_DIR={CONTAINER_VECTOR_DB_DIR}",
        ],
        argv=[
            "uv",
            "run",
            "--script",
            str(CONTAINER_PLUGIN_DIR / "scripts" / "geos_rag_mcp.py"),
            "--smoke",
        ],
    )
    return spec.render()


def preflight_claude_native_mcp(
    *,
    result_dir: Path,
    plugin_dir: Path,
    vector_db_dir: Path,
    timeout: int = 180,
) -> dict[str, Any]:
    """Warm the uv script env and prove the repo3 MCP server can open its DB."""
    cmd = build_claude_native_mcp_smoke_command(
        result_dir=result_dir,
        plugin_dir=plugin_dir,
        vector_db_dir=vector_db_dir,
    )
    started = time.time()
    completed = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=timeout,
    )
    result = {
        "command": cmd,
        "exit_code": completed.returncode,
        "elapsed_seconds": round(time.time() - started, 1),
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "updated": datetime.now().isoformat(),
    }
    (result_dir / "mcp_preflight.json").write_text(json.dumps(result, indent=2))
    if completed.returncode != 0:
        detail = "\n".join(
            part.strip()
            for part in (completed.stdout, completed.stderr)
            if part.strip()
        )
        raise RuntimeError(
            "repo3 GEOS RAG MCP preflight failed before launching Claude. "
            "Rebuild the geos-eval image if uv is missing, then rerun. "
            f"Details: {detail or 'no output'}"
        )
    return result


def build_claude_native_command(
    *,
    filtered_geos: Path,
    result_dir: Path,
    plugin_dir: Path | None,
    vector_db_dir: Path | None,
    model: str,
    system_prompt: str,
    prompt: str,
    enable_plugin: bool = True,
    supervisor_spec_host_path: Path | None = None,
) -> list[str]:
    mounts: list[Mount] = [
        Mount(filtered_geos, "/geos_lib", read_only=True),
        Mount(result_dir, "/workspace"),
    ]
    env: list[str] = []
    if enable_plugin:
        if plugin_dir is None or vector_db_dir is None:
            raise ValueError("plugin_dir and vector_db_dir required when enable_plugin=True")
        mounts += [
            Mount(plugin_dir, "/plugins/repo3", read_only=True),
            Mount(vector_db_dir, CONTAINER_VECTOR_DB_DIR),
            # geosx --validate-input runtime (geosx-validate-input branch):
            # the built binary + its shared libs live outside the /geos_lib
            # source mount, so they get their own read-only mounts. See
            # constants.py for why there are three separate host roots.
            Mount(DEFAULT_GEOSX_INSTALL_DIR, CONTAINER_GEOSX_INSTALL_DIR, read_only=True),
            Mount(DEFAULT_GEOSX_CONDA_LIB_DIR, CONTAINER_GEOSX_CONDA_LIB_DIR, read_only=True),
        ]
        for subdir in DEFAULT_GEOSX_TPL_SUBDIRS:
            mounts.append(
                Mount(
                    DEFAULT_GEOSX_TPL_ROOT / subdir,
                    CONTAINER_GEOSX_TPL_DIR / subdir,
                    read_only=True,
                )
            )
    if supervisor_spec_host_path is not None:
        # Mounted at a fixed container path consumed by supervisor_mcp.py.
        mounts.append(Mount(supervisor_spec_host_path, "/supervisor/spec.md", read_only=True))
    env += [
        "HOME=/workspace/.claude_home",
        "XDG_CONFIG_HOME=/workspace/.claude_home/.config",
        "UV_CACHE_DIR=/workspace/.uv_cache",
        "ANTHROPIC_BASE_URL",
        "ANTHROPIC_AUTH_TOKEN",
        "ANTHROPIC_API_KEY",
        "OPENROUTER_API_KEY",
        "OPENAI_API_KEY",
        "DEEPSEEK_API_KEY",
        # Forwards for plugin/hooks/verify_outputs.py knobs. Absent vars
        # are fine -- hook has sane defaults.
        "GEOS_HOOK_DISABLE",
        "GEOS_HOOK_MAX_RETRIES",
        "GEOS_HOOK_SELF_REFLECT",
        "GEOS_HOOK_XMLLINT",
        "GEOS_HOOK_SCHEMA_PATH",
        # INTEGRATION_REQUIREMENTS R1: the stop policy is a searchable
        # component, so these two must reach the hook or a search would vary a
        # knob nothing reads. Forwarding them here is necessary but NOT
        # sufficient -- verify_outputs.py must also read them. See docs/ENROOT.md
        # and sci-sim-op docs/INTEGRATION_REQUIREMENTS.md.
        "GEOS_EVOLVE_FEEDBACK_SHAPE",
        "GEOS_EVOLVE_CHECKS",
    ]
    if model and "/" in model:
        # Claude Code treats a "provider/model" string as a real Anthropic
        # model ID unless told otherwise, and 404s with "model_not_found"
        # against a multi-provider gateway like OpenRouter's Anthropic-
        # compatible endpoint. These two vars are the missing signal (see
        # scripts/openfoam/run_repo3_openfoam_ablation.py's identical
        # handling -- this harness was missing it for the native-Docker path).
        env += [
            f"ANTHROPIC_CUSTOM_MODEL_OPTION={model}",
            f"ANTHROPIC_CUSTOM_MODEL_OPTION_NAME={model} via gateway",
        ]
    if enable_plugin:
        env += [
            "GEOS_VECTOR_DB_DIR",
            "EXCLUDED_GT_XML_FILENAMES",
            "EXCLUDED_RST_PATHS",
            # CLAUDE_PLUGIN_ROOT is used by the plugin's hooks.json to locate
            # the hook script (python3 ${CLAUDE_PLUGIN_ROOT}/hooks/verify_outputs.py).
            f"CLAUDE_PLUGIN_ROOT={CONTAINER_PLUGIN_DIR}",
            # geosx --validate-input runtime, consumed by verify_outputs.py's
            # _geosx_validate() and geosx_validate_mcp's validate_geos_xml().
            f"GEOSX_EXECUTABLE={CONTAINER_GEOSX_EXECUTABLE}",
            (
                "LD_LIBRARY_PATH="
                f"{CONTAINER_GEOSX_INSTALL_DIR}/lib:"
                + ":".join(
                    str(CONTAINER_GEOSX_TPL_DIR / subdir / "lib")
                    for subdir in DEFAULT_GEOSX_TPL_SUBDIRS
                )
                + f":{CONTAINER_GEOSX_CONDA_LIB_DIR}"
            ),
        ]
    argv = [
        "claude",
        "-p",
        "--verbose",
        "--model", model,
        "--append-system-prompt", system_prompt,
        "--tools", NATIVE_CLAUDE_TOOLS,
    ]
    for disallowed in NATIVE_CLAUDE_DISALLOWED_TOOLS:
        argv += ["--disallowedTools", disallowed]
    if enable_plugin:
        argv += [
            f"--mcp-config={CONTAINER_MCP_CONFIG_PATH}",
            "--strict-mcp-config",
            # The Stop hook (verify_outputs.py) is registered via --settings
            # rather than --plugin-dir so the tool list matches pre-hook runs
            # (E17/E18) exactly. Loading the plugin as a plugin would surface
            # its skill in the tool list and confound hook-effect experiments
            # with tool-list-shape effects. See RN-002 / XN-010.
            "--settings", str(CONTAINER_SETTINGS_PATH),
        ]
    argv += [
        "--output-format", "stream-json",
        "--permission-mode", "bypassPermissions",
        # Separator so a prompt starting with `--` (e.g. the task spec opens
        # with `--- BEGIN SIMULATION SPECIFICATION ---`) isn't parsed as a flag.
        "--",
        prompt,
    ]
    return ContainerSpec(image=DOCKER_IMAGE, mounts=mounts, env=env, argv=argv).render()


def build_claude_native_env(
    *,
    blocked_xml_filenames: list[str],
    blocked_rst_relpaths: list[str],
    vector_db_dir: Path | None,
) -> dict[str, str]:
    env = os.environ.copy()
    env["ANTHROPIC_BASE_URL"] = os.environ.get(
        "ANTHROPIC_BASE_URL",
        "https://openrouter.ai/api",
    )
    # This runner always authenticates via ANTHROPIC_AUTH_TOKEN against a
    # gateway (OpenRouter, DeepSeek's native endpoint, etc.), never a direct
    # Anthropic API key. A real ANTHROPIC_API_KEY sitting in the host .env
    # (e.g. for other tooling) still gets forwarded by docker_cmd.py's `-e
    # ANTHROPIC_API_KEY` passthrough otherwise, and Claude Code appears to
    # prioritize it over ANTHROPIC_CUSTOM_MODEL_OPTION's gateway-routing hint
    # — causing a "model_not_found" 404 on any provider/model gateway string
    # (e.g. deepseek/deepseek-v4-flash, or even the default
    # minimax/minimax-m2.7). Blank it so the gateway hint wins, matching
    # scripts/openfoam/run_repo3_openfoam_ablation.py's identical handling.
    env["ANTHROPIC_API_KEY"] = ""
    if vector_db_dir is not None:
        env["GEOS_VECTOR_DB_DIR"] = str(CONTAINER_VECTOR_DB_DIR)
        env["EXCLUDED_GT_XML_FILENAMES"] = json.dumps(blocked_xml_filenames)
        env["EXCLUDED_RST_PATHS"] = json.dumps(blocked_rst_relpaths)

        # The repo3 MCP server uses OPENROUTER_API_KEY for embeddings.  For this
        # eval path, the OpenRouter Claude auth token is a suitable fallback without
        # putting a secret in the docker command line.
        if not env.get("OPENROUTER_API_KEY") and env.get("ANTHROPIC_AUTH_TOKEN"):
            env["OPENROUTER_API_KEY"] = env["ANTHROPIC_AUTH_TOKEN"]

        # Keep the host path available in metadata/debug logs without overriding the
        # container-visible GEOS_VECTOR_DB_DIR used by the MCP server.
        env["HOST_GEOS_VECTOR_DB_DIR"] = str(vector_db_dir)
    return env
