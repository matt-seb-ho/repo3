"""Path / regex / flag constants used across :mod:`runner`.

Mirrors lines 91-135 of the original ``scripts/run_experiment.py``.
"""

from __future__ import annotations

import re
import subprocess
import threading
from pathlib import Path

# This module lives at src/runner/constants.py, so REPO_ROOT is two
# parents up (repo3/src/runner/ -> repo3/src/ -> repo3/).
REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_DIR = REPO_ROOT / "scripts"  # legacy alias; preserved for parity
RUN_ASSETS_DIR = REPO_ROOT / "run"  # AGENTS_old.md (archived) + Dockerfile live here
DATA_DIR = REPO_ROOT / "data"
EXPERIMENTS_DIR = DATA_DIR / "eval" / "experiments"
GROUND_TRUTH_DIR = DATA_DIR / "eval" / "experiments_gt"
DEFAULT_GEOS_LIB_DIR = Path("/data/shared/geophysics_agent_data/data/GEOS")
GEOS_LIB_DIR = DEFAULT_GEOS_LIB_DIR
# Filtered GEOS trees (hardlink farms) are created here. Must be writable and on
# the same filesystem as --geos-lib-dir for efficient hardlinks (see contamination.py).
TEMP_GEOS_PARENT = Path("/data/shared/geophysics_agent_data/data/eval/tmp_geos")
DOCKER_IMAGE = "geos-eval"
DEFAULT_PLUGIN_DIR = REPO_ROOT / "plugin"  # .claude-plugin/plugin.json lives under plugin/

DEFAULT_VECTOR_DB_DIR = Path("/data/shared/geophysics_agent_data/data/vector_db")

# geosx --validate-input support (geosx-validate-input branch).
# A built GEOS binary + its runtime shared libraries, spread across the main
# install prefix, several thirdPartyLibs install prefixes, and (fragile —
# see docs/GEOSX_VALIDATE.md) one host conda env that happened to supply
# libz.so.1 at build time. None of this lives under DEFAULT_GEOS_LIB_DIR
# (that mount is source-only, no build/ or install/ dir), so it must be
# mounted separately from the existing /geos_lib mount.
#
# These live under /home/brian, NOT /data — confirmed empirically that this
# host's Docker daemon cannot see /data at all as a bind-mount source (a
# direct mount of /data/shared/GEOS/... comes up as an empty directory
# inside the container, even though the same path is completely readable
# from the host shell; a symlink under /home pointing back into /data
# doesn't help either — it's a hard mount-namespace-level constraint of
# this Docker daemon, not a permissions issue). vector_db and the /geos_lib
# filtered-GEOS mount already dodge this by having Python copy them to a
# /home-rooted path before the docker run; these directories needed the
# same one-time treatment (copied via `cp -a`, ~605MB total, see git log
# for the exact commands run). DEFAULT_GEOSX_CONDA_LIB_DIR was already
# under /home/brian, so it never needed moving.
DEFAULT_GEOSX_INSTALL_DIR = Path("/home/brian/.geosx_docker_runtime/install")
DEFAULT_GEOSX_TPL_ROOT = Path("/home/brian/.geosx_docker_runtime/tpl")
DEFAULT_GEOSX_TPL_SUBDIRS = ("hdf5", "suitesparse", "superlu_dist", "vtk")
DEFAULT_GEOSX_CONDA_LIB_DIR = Path("/home/brian/miniconda3/envs/geos-build/lib")

CONTAINER_GEOSX_INSTALL_DIR = Path("/opt/geosx-install")
CONTAINER_GEOSX_TPL_DIR = Path("/opt/geosx-tpl")
CONTAINER_GEOSX_CONDA_LIB_DIR = Path("/opt/geosx-conda-lib")
CONTAINER_GEOSX_EXECUTABLE = CONTAINER_GEOSX_INSTALL_DIR / "bin" / "geosx"
DEFAULT_GEOS_PRIMER_PATH = REPO_ROOT / "plugin" / "GEOS_PRIMER_absolute_min.md"
DEFAULT_CLAUDE_MODEL = "minimax/minimax-m2.7"
CONTAINER_PLUGIN_DIR = Path("/plugins/repo3")
CONTAINER_SETTINGS_PATH = Path("/workspace/claude_settings.json")
CONTAINER_VECTOR_DB_DIR = Path("/data/shared/geophysics_agent_data/data/vector_db")
CONTAINER_MCP_CONFIG_PATH = Path("/workspace/claude_mcp_config.json")
CONTAINER_GEOS_PRIMER_PATH = Path("/workspace/GEOS_PRIMER.md")
RAG_TOOL_NAMES = {"search_navigator", "search_schema", "search_technical"}
PSEUDO_TOOL_RE = re.compile(r"invoke\s+name=[\"']([^\"']+)[\"']", re.IGNORECASE)
NATIVE_CLAUDE_TOOLS = "default"
# Each entry is passed as its own --disallowedTools argument. Skill is blocked
# because the repo3-plugin:geos-rag skill wrapper breaks non-Anthropic providers
# (the RAG instructions are injected directly into the system prompt instead).
# AskUserQuestion is blocked because this harness runs Claude non-interactively
# via `claude -p`; any AskUserQuestion call stalls the turn and is a known
# cause of the premature-end_turn failure mode (see docs/XN-010).
# Task/Agent/TaskCreate are blocked for two independent reasons, both measured
# on 2026-08-26 while pricing models for a budget:
#
#  (1) COST. A gpt-5.6-luna rollout spawned a subagent that ran on
#      anthropic/claude-sonnet-5 for 31 turns. That subagent cost $0.90 of the
#      rollout pair's $1.06 -- 85% of the bill went to a model nobody asked for,
#      at ~18x the per-token price of the one that was requested.
#  (2) VALIDITY, which matters more. A rollout nominally "on model X" was partly
#      executed by a different and stronger model, so any cross-model comparison
#      built on it is measuring an uncontrolled mixture. The frozen-agent premise
#      of this whole evaluation requires that the agent be the model we named.
NATIVE_CLAUDE_DISALLOWED_TOOLS = (
    "Skill", "AskUserQuestion", "Task", "Agent", "TaskCreate",
)

DEFAULT_TIMEOUT = 1200  # seconds per task (20 minutes)
