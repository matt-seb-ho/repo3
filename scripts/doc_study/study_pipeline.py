#!/usr/bin/env python3
# ruff: noqa: W605
r"""Study-then-Harness: doc-study pipeline prototype.

Walks the GEOS sphinx + coreComponents docs tree, has DSv4-flash (via
OpenRouter) read each section and emit a structured note, then
hierarchically coalesces per-directory and tool-level summaries.

Output artifact $\hat D = (N, S):
  - N: per-section notes  (out/notes/<sanitized_path>.json)
  - S: hierarchical roll-up  (out/rollup/<topdir>.json + out/global.json)

Usage:
  python3 scripts/doc_study/study_pipeline.py \
      --docs-root /data/shared/geophysics_agent_data/data/GEOS/src \
      --out-dir   data/doc_study/2026-05-18 \
      --max-files 161 \
      --workers   8

Environment:
  Reads OPENROUTER_API_KEY (preferred) or falls back to DEEPSEEK_API_KEY +
  direct DeepSeek API.
"""
from __future__ import annotations
import argparse
import concurrent.futures
import dataclasses
import json
import os
import pathlib
import re
import sys
import time
from typing import Optional

from openai import OpenAI


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SECTION_SCHEMA = {
    "section_id": "string — slugified relative path, e.g. 'userGuide/Index'",
    "type": "one of: schema | tutorial | concept | warning | example | reference | mixed",
    "title": "short title",
    "summary": "2-4 sentence summary in plain English",
    "key_objects": ["list of XML elements / classes / file types / concepts named in the doc"],
    "relations": ["list of cross-references this section makes (filenames, other sections)"],
    "examples_present": "bool — true if the section contains concrete XML/code examples",
    "pitfalls": ["list of warnings, deprecation notices, common mistakes mentioned"],
    "harness_relevance": "one of: high | medium | low — usefulness for an agent writing GEOS XML inputs",
    "citation_anchor": "a short literal phrase from the doc the harness can grep to re-find this section",
}

SECTION_PROMPT = """You are reading one section of the GEOS scientific simulator's
documentation. Your job is to produce a structured note about this section so
that another LLM agent — one that has to write GEOS XML input files — can use
your note efficiently without re-reading the raw section.

The section is delimited by <DOC>...</DOC> below.

Return ONLY a JSON object matching this schema:
{schema}

Rules:
- `type`: choose the dominant role. Schema/reference = formal definitions of
  XML elements or APIs. Tutorial = step-by-step walkthrough. Concept =
  background prose. Warning = mostly cautions. Example = concrete cases.
- `harness_relevance`: be honest. Build/install/CI docs are usually low.
  XML element references and physics solver tutorials are usually high.
- `key_objects`: prefer XML element names (verbatim, including capitalization)
  over English paraphrases. E.g., `SolidMechanicsLagrangianSSLE`, not
  "the solid mechanics solver".
- `citation_anchor`: pick a literal phrase (5-12 words) the agent can grep on.
- Keep `summary` to 2-4 sentences MAX. Be specific, not generic.
- Do NOT include any explanation outside the JSON object.

<DOC path="{path}">
{content}
</DOC>
""".strip()


ROLLUP_PROMPT = """You are coalescing per-section notes from one subtree of the
GEOS documentation into a higher-level summary. The goal: produce a compact
hierarchical artifact an LLM agent can consult to navigate this subtree
without re-reading the individual section notes.

Subtree: {subtree}
Section notes (JSON array):
{notes}

Return ONLY a JSON object with this shape:
{{
  "subtree": "{subtree}",
  "purpose": "1-2 sentence statement of what this subtree covers",
  "primary_xml_elements": ["list of the top ~15 XML elements this subtree defines or uses, by frequency / importance"],
  "primary_workflows": ["list of named workflows or use cases described"],
  "key_files": ["list of section_ids that are most important for a harness — those marked harness_relevance=high"],
  "pitfalls": ["consolidated list of pitfalls, deprecations, warnings (deduplicated)"],
  "navigation_hints": "1-2 sentences telling an agent how to find specific information in this subtree"
}}

Do NOT include any text outside the JSON object.
""".strip()


GLOBAL_ROLLUP_PROMPT = """You are producing the top-level "study artifact" for
the entire GEOS documentation, by coalescing per-subtree rollups. This is the
artifact an LLM agent will see at runtime *instead of* the raw documentation.

Subtree rollups (JSON array):
{rollups}

Return ONLY a JSON object with this shape:
{{
  "tool": "GEOS",
  "elevator_pitch": "2-3 sentences: what GEOS is and what kinds of problems it solves",
  "entrypoints": ["list of where to start: which XML elements / sections are the user-facing entry points"],
  "top_workflows": ["the 5-10 most important workflows: name + 1-line description each"],
  "primary_object_taxonomy": {{"category_name": ["XML elements in this category"]}},
  "top_pitfalls": ["the 10 most important pitfalls or deprecation warnings, ranked by likely impact"],
  "navigation_index": {{"task_type": "subtree_id where to look"}},
  "coverage_note": "honest note about what is NOT covered or is shallow in this artifact"
}}

Be concise. Prefer XML element names verbatim. Do NOT include text outside the JSON.
""".strip()


# ---------------------------------------------------------------------------
# Client setup
# ---------------------------------------------------------------------------

def build_client() -> tuple[OpenAI, str, str]:
    """Build an OpenAI client pointed at OpenRouter (preferred) or DeepSeek-direct."""
    or_key = os.environ.get("OPENROUTER_API_KEY")
    ds_key = os.environ.get("DEEPSEEK_API_KEY")
    if or_key:
        client = OpenAI(api_key=or_key, base_url="https://openrouter.ai/api/v1")
        return client, "deepseek/deepseek-v4-flash", "openrouter"
    if ds_key:
        client = OpenAI(api_key=ds_key, base_url="https://api.deepseek.com/v1")
        return client, "deepseek-v4-flash", "deepseek-direct"
    raise SystemExit("No OPENROUTER_API_KEY or DEEPSEEK_API_KEY in env")


# ---------------------------------------------------------------------------
# File discovery + section note generation
# ---------------------------------------------------------------------------

@dataclasses.dataclass
class StudyTask:
    path: pathlib.Path
    rel_id: str    # e.g., "userGuide/Index"
    content: str


def discover_files(docs_root: pathlib.Path, max_files: Optional[int]) -> list[StudyTask]:
    tasks: list[StudyTask] = []
    rsts = sorted(docs_root.rglob("*.rst"))
    for p in rsts:
        try:
            size = p.stat().st_size
        except OSError:
            continue
        # Filter: skip tiny stubs and huge generated dumps
        if size < 500 or size > 50_000:
            continue
        try:
            content = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        rel = p.relative_to(docs_root)
        # Strip leading "docs/sphinx/" or trailing ".rst"
        rel_id = str(rel.with_suffix(""))
        tasks.append(StudyTask(path=p, rel_id=rel_id, content=content))
    if max_files is not None and len(tasks) > max_files:
        tasks = tasks[:max_files]
    return tasks


def call_with_retry(client: OpenAI, model: str, prompt: str,
                    max_attempts: int = 3, max_tokens: int = 1600) -> tuple[str, dict]:
    last_err: Optional[Exception] = None
    for attempt in range(max_attempts):
        try:
            t0 = time.time()
            resp = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.2,
                response_format={"type": "json_object"},
            )
            elapsed = time.time() - t0
            msg = resp.choices[0].message
            content = msg.content or ""
            usage = resp.usage.model_dump() if resp.usage else {}
            usage["elapsed_s"] = elapsed
            return content, usage
        except Exception as e:
            last_err = e
            sleep_s = 4 * (2 ** attempt)
            print(f"  retry attempt={attempt+1} error={type(e).__name__}: {e}", file=sys.stderr)
            time.sleep(sleep_s)
    raise RuntimeError(f"All attempts failed: {last_err}")


def study_section(client: OpenAI, model: str, task: StudyTask) -> dict:
    schema_str = json.dumps(SECTION_SCHEMA, indent=2)
    # Truncate huge docs gracefully (we already filtered to <=50K char; but keep input bounded)
    content = task.content[:48_000]
    prompt = SECTION_PROMPT.format(schema=schema_str, path=task.rel_id, content=content)
    raw, usage = call_with_retry(client, model, prompt)
    try:
        note = json.loads(raw)
    except json.JSONDecodeError as e:
        # Salvage: try to find first JSON object
        m = re.search(r"\{.*\}", raw, re.S)
        if m:
            note = json.loads(m.group(0))
        else:
            raise RuntimeError(f"Could not parse JSON from response for {task.rel_id}: {e}") from e
    note["_meta"] = {
        "source_path": str(task.path),
        "rel_id": task.rel_id,
        "size_bytes": len(task.content),
        "usage": usage,
    }
    return note


# ---------------------------------------------------------------------------
# Hierarchical roll-up
# ---------------------------------------------------------------------------

def subtree_of(rel_id: str) -> str:
    # Strip the "docs/sphinx/" prefix and "coreComponents/<X>/docs/" prefix
    parts = rel_id.replace("\\", "/").split("/")
    # Heuristic: keep first 1-2 components after stripping common prefixes
    if parts and parts[0] in {"docs", "coreComponents", "pygeosx"}:
        # docs/sphinx/userGuide/X -> userGuide
        if parts[0] == "docs" and len(parts) >= 3 and parts[1] == "sphinx":
            return parts[2] if len(parts) > 2 else "docs"
        # coreComponents/X/docs/Y -> coreComponents/X
        if parts[0] == "coreComponents" and len(parts) >= 2:
            return f"coreComponents/{parts[1]}"
        return parts[0]
    return parts[0] if parts else "root"


def rollup_subtree(client: OpenAI, model: str, subtree: str, notes: list[dict]) -> dict:
    # Strip heavy _meta before sending
    trimmed = []
    for n in notes:
        c = {k: v for k, v in n.items() if k != "_meta"}
        trimmed.append(c)
    prompt = ROLLUP_PROMPT.format(subtree=subtree, notes=json.dumps(trimmed, indent=2))
    raw, usage = call_with_retry(client, model, prompt, max_tokens=2000)
    try:
        rollup = json.loads(raw)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", raw, re.S)
        rollup = json.loads(m.group(0)) if m else {"subtree": subtree, "_parse_error": True}
    rollup["_meta"] = {"subtree": subtree, "n_notes": len(notes), "usage": usage}
    return rollup


def global_rollup(client: OpenAI, model: str, rollups: list[dict]) -> dict:
    trimmed = [{k: v for k, v in r.items() if k != "_meta"} for r in rollups]
    prompt = GLOBAL_ROLLUP_PROMPT.format(rollups=json.dumps(trimmed, indent=2))
    raw, usage = call_with_retry(client, model, prompt, max_tokens=2800)
    try:
        g = json.loads(raw)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", raw, re.S)
        g = json.loads(m.group(0)) if m else {"tool": "GEOS", "_parse_error": True}
    g["_meta"] = {"n_rollups": len(rollups), "usage": usage}
    return g


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def sanitize(rel_id: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_.-]", "_", rel_id)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--docs-root", required=True, type=pathlib.Path)
    ap.add_argument("--out-dir", required=True, type=pathlib.Path)
    ap.add_argument("--max-files", type=int, default=None)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--skip-existing", action="store_true",
                    help="Don't re-call API for sections that already have notes on disk")
    args = ap.parse_args()

    out = args.out_dir
    notes_dir = out / "notes"
    rollup_dir = out / "rollup"
    notes_dir.mkdir(parents=True, exist_ok=True)
    rollup_dir.mkdir(parents=True, exist_ok=True)

    client, model, provider = build_client()
    print(f"Provider: {provider}  Model: {model}", file=sys.stderr)

    tasks = discover_files(args.docs_root, args.max_files)
    print(f"Discovered {len(tasks)} sections under {args.docs_root}", file=sys.stderr)

    # ---- Phase 1: per-section study ----
    def process(task: StudyTask) -> tuple[str, Optional[dict], Optional[str]]:
        out_file = notes_dir / f"{sanitize(task.rel_id)}.json"
        if args.skip_existing and out_file.exists():
            try:
                return task.rel_id, json.loads(out_file.read_text()), None
            except Exception:
                pass
        try:
            note = study_section(client, model, task)
            out_file.write_text(json.dumps(note, indent=2))
            return task.rel_id, note, None
        except Exception as e:
            return task.rel_id, None, f"{type(e).__name__}: {e}"

    notes_by_id: dict[str, dict] = {}
    errors: list[tuple[str, str]] = []
    t_start = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as ex:
        futures = {ex.submit(process, t): t for t in tasks}
        for i, fut in enumerate(concurrent.futures.as_completed(futures), 1):
            rel_id, note, err = fut.result()
            if err:
                errors.append((rel_id, err))
                print(f"[{i}/{len(tasks)}] ERR {rel_id}: {err}", file=sys.stderr)
            else:
                notes_by_id[rel_id] = note
                if i % 10 == 0 or i == len(tasks):
                    elapsed = time.time() - t_start
                    print(f"[{i}/{len(tasks)}] notes ok in {elapsed:.1f}s", file=sys.stderr)

    print(f"Phase 1 done: {len(notes_by_id)} notes, {len(errors)} errors, "
          f"elapsed={time.time()-t_start:.1f}s", file=sys.stderr)
    (out / "phase1_errors.json").write_text(json.dumps(errors, indent=2))

    # ---- Phase 2: per-subtree rollup ----
    by_subtree: dict[str, list[dict]] = {}
    for rid, n in notes_by_id.items():
        by_subtree.setdefault(subtree_of(rid), []).append(n)

    rollups: list[dict] = []
    t_phase2 = time.time()
    for subtree, group in by_subtree.items():
        if not group:
            continue
        print(f"Rollup: {subtree} ({len(group)} notes)", file=sys.stderr)
        try:
            r = rollup_subtree(client, model, subtree, group)
        except Exception as e:
            print(f"  rollup error for {subtree}: {e}", file=sys.stderr)
            r = {"subtree": subtree, "_error": str(e)}
        rollups.append(r)
        (rollup_dir / f"{sanitize(subtree)}.json").write_text(json.dumps(r, indent=2))
    print(f"Phase 2 done in {time.time()-t_phase2:.1f}s", file=sys.stderr)

    # ---- Phase 3: global rollup ----
    t_phase3 = time.time()
    print("Global rollup...", file=sys.stderr)
    try:
        g = global_rollup(client, model, rollups)
    except Exception as e:
        g = {"tool": "GEOS", "_error": str(e)}
    (out / "global.json").write_text(json.dumps(g, indent=2))
    print(f"Phase 3 done in {time.time()-t_phase3:.1f}s", file=sys.stderr)

    # ---- Summary ----
    total_in = sum(n.get("_meta", {}).get("usage", {}).get("prompt_tokens", 0) for n in notes_by_id.values())
    total_out = sum(n.get("_meta", {}).get("usage", {}).get("completion_tokens", 0) for n in notes_by_id.values())
    total_in += sum(r.get("_meta", {}).get("usage", {}).get("prompt_tokens", 0) for r in rollups)
    total_out += sum(r.get("_meta", {}).get("usage", {}).get("completion_tokens", 0) for r in rollups)
    total_in += g.get("_meta", {}).get("usage", {}).get("prompt_tokens", 0)
    total_out += g.get("_meta", {}).get("usage", {}).get("completion_tokens", 0)
    print(json.dumps({
        "n_notes": len(notes_by_id),
        "n_errors": len(errors),
        "n_subtrees": len(rollups),
        "total_prompt_tokens": total_in,
        "total_completion_tokens": total_out,
        "elapsed_total_s": round(time.time() - t_start, 1),
    }, indent=2))


if __name__ == "__main__":
    main()
