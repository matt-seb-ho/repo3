"""claude_settings.json + claude_mcp_config.json writers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .constants import (
    CONTAINER_MCP_CONFIG_PATH,
    CONTAINER_PLUGIN_DIR,
    CONTAINER_SETTINGS_PATH,
    CONTAINER_VECTOR_DB_DIR,
    REPO_ROOT,
)


def _safe_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(json.dumps(payload, indent=2, sort_keys=True))
    tmp_path.replace(path)


def write_claude_settings(*, result_dir: Path, hook_enabled: bool) -> Path:
    """Write claude_settings.json with the Stop hook (verify_outputs.py).

    Registering the hook via --settings instead of --plugin-dir keeps the
    tool list identical to pre-hook runs (plugin skill does not surface).
    The GEOS_HOOK_DISABLE env var is the runtime kill switch; passing
    hook_enabled=False here omits the hook from settings entirely for
    maximal baseline parity with E17.
    """
    container_hook = CONTAINER_PLUGIN_DIR / "hooks" / "verify_outputs.py"
    settings: dict[str, Any] = {}
    if hook_enabled:
        settings["hooks"] = {
            "Stop": [
                {
                    "matcher": "",
                    "hooks": [
                        {
                            "type": "command",
                            "command": f"python3 {container_hook}",
                            "timeout": 30,
                        }
                    ],
                }
            ]
        }
    path = result_dir / CONTAINER_SETTINGS_PATH.name
    _safe_write_json(path, settings)
    return path


def write_claude_mcp_config(
    *,
    result_dir: Path,
    blocked_xml_filenames: list[str],
    blocked_rst_relpaths: list[str],
    enable_memory: bool = False,
    enable_noop: bool = False,
    memory_variant: str = "lexical",  # "lexical" (memory_mcp.py) or "embed" (memory_mcp_embed.py)
    memory_items_host_path: Path | None = None,
    memory_embed_index_host_path: Path | None = None,
) -> Path:
    """Write the explicit MCP config Claude Code uses inside the container.

    Claude Code loads repo3 plugin skills via --plugin-dir in this eval path, but
    the plugin manifest's mcpServers block is not reliably activated in --bare
    mode.  Passing an explicit --mcp-config keeps the RAG tools available without
    storing API secrets in the workspace file; secrets are supplied through the
    docker process environment.

    If enable_memory=True, additionally register the memory_mcp server that
    serves a frozen G-Memory-lite index from /plugins/repo3/memory_index.json.
    """
    servers: dict[str, Any] = {
        "geos-rag": {
            "type": "stdio",
            "command": "uv",
            "args": [
                "run",
                "--script",
                str(CONTAINER_PLUGIN_DIR / "scripts" / "geos_rag_mcp.py"),
            ],
            "env": {
                "CLAUDE_PLUGIN_ROOT": str(CONTAINER_PLUGIN_DIR),
                "GEOS_VECTOR_DB_DIR": str(CONTAINER_VECTOR_DB_DIR),
                "EXCLUDED_GT_XML_FILENAMES": json.dumps(blocked_xml_filenames),
                "EXCLUDED_RST_PATHS": json.dumps(blocked_rst_relpaths),
            },
        },
    }
    if enable_memory:
        if memory_variant == "embed":
            # M3 — embedding MCP with hard-error on missing key + preflight (RN-003 P2 #8).
            # Host paths under plugin/ mount at /plugins/repo3/ in container; translate.
            def _host_plugin_to_container(host_path: Path | None, default_name: str) -> str:
                if host_path is None:
                    return str(CONTAINER_PLUGIN_DIR / default_name)
                hp = Path(host_path).resolve()
                try:
                    rel = hp.relative_to(REPO_ROOT / "plugin")
                    return str(CONTAINER_PLUGIN_DIR / rel)
                except ValueError:
                    # Not under plugin/; leave as-is (may not mount)
                    return str(hp)

            mem_env = {
                "CLAUDE_PLUGIN_ROOT": str(CONTAINER_PLUGIN_DIR),
                "MEMORY_ITEMS_PATH": _host_plugin_to_container(
                    memory_items_host_path, "memory_items.json"),
                "MEMORY_EMBED_INDEX_PATH": _host_plugin_to_container(
                    memory_embed_index_host_path, "memory_items_embeddings.json"),
            }
            servers["memory"] = {
                "type": "stdio",
                "command": "uv",
                "args": [
                    "run",
                    "--script",
                    "--with", "numpy>=1.26",
                    "--with", "requests>=2.31",
                    str(CONTAINER_PLUGIN_DIR / "scripts" / "memory_mcp_embed.py"),
                ],
                "env": mem_env,
            }
        else:
            servers["memory"] = {
                "type": "stdio",
                "command": "uv",
                "args": [
                    "run",
                    "--script",
                    str(CONTAINER_PLUGIN_DIR / "scripts" / "memory_mcp.py"),
                ],
                "env": {
                    "CLAUDE_PLUGIN_ROOT": str(CONTAINER_PLUGIN_DIR),
                    "MEMORY_INDEX_PATH": str(CONTAINER_PLUGIN_DIR / "memory_index.json"),
                },
            }
    if enable_noop:
        servers["noop"] = {
            "type": "stdio",
            "command": "uv",
            "args": [
                "run",
                "--script",
                str(CONTAINER_PLUGIN_DIR / "scripts" / "noop_mcp.py"),
            ],
            "env": {
                "CLAUDE_PLUGIN_ROOT": str(CONTAINER_PLUGIN_DIR),
            },
        }
    mcp_config_path = result_dir / CONTAINER_MCP_CONFIG_PATH.name
    _safe_write_json(mcp_config_path, {"mcpServers": servers})
    return mcp_config_path
