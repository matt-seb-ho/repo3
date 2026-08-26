#!/usr/bin/env python3
"""
Thread J1 — soft-TreeSim judge runner.

Reads `J1_items.jsonl`, selects the judged attribute-level items under the frozen
cap, DEDUPLICATES them on (task, card hash), chunks them, and asks each judge the
frozen three-question decision tree via OpenRouter with an enforced JSON schema.

Rubric: artifacts/J1_rubric_v2.md
  sha256 cb00c83822f250077c6ac1020eb37766c09650e9046c335995a3fffff69b7e46
  frozen 2026-07-27T07:56:36Z, before any call made by this script.

Resumable: skips (unit_key, judge, order, rep) already present in the output.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

REPO = Path("/home/matt/sci/repo3")
load_dotenv(REPO / ".env")

SPECS = Path("/data/shared/geophysics_agent_data/data/eval/experiments_from_mined_specs")

# Five model families. None is DeepSeek (the scored backbone), none is MiniMax
# (the paper's second scored backbone), none is Anthropic (the harness vendor).
JUDGES = {
    # PRIMARY (researcher's directive, rubric v3): the scored backbone's own family.
    "dsv4flash":    "deepseek-v4-flash",
    "dsv4pro":      "deepseek-v4-pro",          # escalation only, see log
    # SAME-FAMILY BIAS CONTROL: independent panel, no DeepSeek, no MiniMax, no Anthropic.
    "gpt54mini":    "openai/gpt-5.4-mini",
    "gemini3flash": "google/gemini-3-flash-preview",
    "qwen3235b":    "qwen/qwen3-235b-a22b-2507",
    "mistralmed31": "mistralai/mistral-medium-3.1",
    "kimik26":      "moonshotai/kimi-k2.6",
}
PANEL_INDEPENDENT = ["gpt54mini", "gemini3flash", "qwen3235b", "mistralmed31"]
# OpenRouter list price, $ per token, captured 2026-07-27 from /api/v1/models.
# Costs are computed from raw token counts x these numbers, NEVER from a
# provider-reported cost field (see the DeepSeek cost-accounting memory).
PRICING = {
    # DeepSeek direct, off-peak list price, $/token. Canonical source:
    # scripts/oh_dsv4_compare.py:56 (INP_C=0.14, INP_H=0.0028, OUT=0.28 per 1M).
    # Cache-read input is billed at 0.0028/1M; we bill ALL input at the cache-MISS
    # rate 0.14/1M, which over-states rather than under-states the cost.
    # NOT taken from any provider-reported cost field (trap 2 in the cost memory).
    "deepseek-v4-flash":              (0.14e-6, 0.28e-6),
    "deepseek-v4-pro":                (0.14e-6, 0.28e-6),   # placeholder; verified at run time
    "openai/gpt-5.4-mini":            (0.75e-6, 4.50e-6),
    "google/gemini-3-flash-preview":  (0.50e-6, 3.00e-6),
    "qwen/qwen3-235b-a22b-2507":      (0.09e-6, 0.55e-6),
    "mistralai/mistral-medium-3.1":   (0.40e-6, 2.00e-6),
    "moonshotai/kimi-k2.6":           (0.646e-6, 2.72e-6),
}

# DeepSeek is called DIRECTLY (not via OpenRouter) so token counts and therefore
# costs come from DeepSeek's own usage fields at DeepSeek's own list price.
_OR = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.environ["OPENROUTER_API_KEY"])
_DS = OpenAI(base_url="https://api.deepseek.com/v1",
             api_key=os.environ.get("DEEPSEEK_API_KEY", "")) if os.environ.get("DEEPSEEK_API_KEY") else None


def client_for(model: str):
    return _DS if model.startswith("deepseek-") else _OR

CAP = 60          # frozen: max judged items per deck per rung
CHUNK = 8         # frozen: max items per call

# ---- frozen terminal -> (severity, credit) -------------------------------
CREDIT = {"cosmetic": 1.0, "minor": 0.7, "material": 0.3, "severe": 0.0, "uncertain": 0.0}


def terminal(v: dict) -> tuple[str, str | None]:
    """Frozen decision tree. Returns (severity, error)."""
    e = str(v.get("effect", "")).strip().lower()
    if e == "cannot_determine":
        return "uncertain", None
    if e == "no":
        return "cosmetic", None
    if e != "yes":
        return "", f"bad effect={e!r}"
    ct = str(v.get("change_type", "")).strip().lower()
    if ct == "magnitude":
        p = str(v.get("value_plausible", "")).strip().lower()
        if p == "yes":
            return "minor", None
        if p == "no":
            return "severe", None
        return "", f"bad value_plausible={p!r}"
    if ct == "qualitative":
        r = str(v.get("requested_physics_preserved", "")).strip().lower()
        if r == "yes":
            return "material", None
        if r == "no":
            return "severe", None
        return "", f"bad requested_physics_preserved={r!r}"
    return "", f"bad change_type={ct!r}"


SYSTEM = """You are a computational geomechanics and reservoir-simulation expert auditing GEOS XML \
input decks. GEOS is an open-source multiphysics simulator for subsurface problems \
(poromechanics, thermo-poro-elasticity, multiphase flow, hydraulic fracturing).

You are being used as a measurement instrument inside a structural metric. That metric compares a \
CANDIDATE deck against a REFERENCE deck attribute by attribute, using exact equality (relative \
tolerance 1e-6). It has already done all the structural work: it matched the elements and found \
the attributes below to be non-identical. It cannot tell whether a non-identical attribute is \
physically irrelevant or catastrophic -- it scores a permeability wrong by a factor of two exactly \
the same as one wrong by eighteen orders of magnitude, and it scores a whitespace difference the \
same as both.

You supply that one missing dimension, and nothing else.

Rules:
- Every ESTABLISHED FACT block is computed from the files by code. It is correct. Use it. Do not \
second-guess arithmetic, schema defaults, or identifier counts that are stated there.
- Judge physics, not text. Do not reward or penalise verbosity, comments, ordering, or style.
- Do not re-score structure. Element matching is not your job and is not affected by your answers.
- Answer each question with one of its permitted values. If the card genuinely does not let you \
decide, answer effect="cannot_determine" rather than guessing."""

QUESTIONS = """## Your task

For EVERY item below, answer this decision tree. Answer only the questions the tree reaches.

Q1  "effect": Does this difference change any quantity GEOS uses to compute the solution?
      "no"               - it does not. Formatting or whitespace inside a list; an identifier
                           renamed and used consistently; an algebraically identical expression;
                           the same physical quantity in equivalent units; an output-, logging- or
                           naming-only attribute; an attribute stated explicitly at the value it
                           would take by default anyway.
      "yes"              - the solver would compute something different.
      "cannot_determine" - the card does not contain enough information to decide.
    -> if "no" or "cannot_determine", STOP for this item.

Q2  "change_type": (only when effect = "yes")
      "magnitude"   - the quantity plays the same role; only its value differs.
      "qualitative" - the FORM of the modelled problem changes: a different governing equation,
                      constitutive model, coupling, or boundary-condition TYPE; a flipped sign;
                      or an input the requested physics requires being removed.

Q3a "value_plausible": (only when change_type = "magnitude")
      Would a domain scientist accept the CANDIDATE value for the material and scenario described
      in the SIMULATION BRIEF?
      "yes" - inside the normal engineering range for the stated material/scenario.
      "no"  - outside physical range, or off by orders of magnitude for that quantity.

Q3b "requested_physics_preserved": (only when change_type = "qualitative")
      Does the candidate still model the physics the BRIEF asked for? A different but real
      material, a different valid solver, or a coarser but still valid discretization all
      PRESERVE it. Removing a required coupling, solving a different problem, or dropping a
      boundary condition the physics needs does NOT.
      "yes" / "no"

Also give "reason": at most 25 words, referring to the physics.

## Output format

Reply with a single json object of exactly this shape and nothing else -- no prose, no markdown
fences. Include one entry for EVERY item id shown above. Omit the keys the decision tree does not
reach, or set them to "n/a".

{"verdicts": [
  {"id": "X01", "effect": "no|yes|cannot_determine", "change_type": "magnitude|qualitative|n/a",
   "value_plausible": "yes|no|n/a", "requested_physics_preserved": "yes|no|n/a",
   "reason": "..."}
]}"""

SCHEMA = {
    "type": "object",
    "properties": {
        "verdicts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "effect": {"type": "string", "enum": ["no", "yes", "cannot_determine"]},
                    "change_type": {"type": "string", "enum": ["magnitude", "qualitative", "n/a"]},
                    "value_plausible": {"type": "string", "enum": ["yes", "no", "n/a"]},
                    "requested_physics_preserved": {"type": "string", "enum": ["yes", "no", "n/a"]},
                    "reason": {"type": "string"},
                },
                "required": ["id", "effect", "change_type", "value_plausible",
                             "requested_physics_preserved", "reason"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["verdicts"],
    "additionalProperties": False,
}

_PATH_PAT = re.compile(
    r"(/[\w./-]*(?:geophysics_agent_data|autocamp|experiments_gt|sci/repo3|workspace)[\w./-]*)")
_CELL_PAT = re.compile(r"\b(autocamp_(?:F\d+|SE)|F\d+_icl_s\d|SE_icl_s\d)\b")


def blind(t: str) -> str:
    return _CELL_PAT.sub("<cond>", _PATH_PAT.sub("<path>", t))


# --------------------------------------------------------------------------

def select_units(items_path: Path, cap: int = CAP):
    """Dedup judged items to (task, card-hash) units. Frozen cap + weight ordering."""
    units: dict[tuple[str, str], dict] = {}
    for line in items_path.open():
        r = json.loads(line)
        if r.get("rung1_fail"):
            continue
        for vn in ("hard", "soft"):
            v = r["variants"][vn]
            j = [i for i in v["items"] if i["judged"]]
            j.sort(key=lambda x: (-abs(x["weight"]), x["item_id"]))
            for it in j[:cap]:
                key = (r["task"], it["cache_key"])
                u = units.setdefault(key, {
                    "task": r["task"], "cache_key": it["cache_key"],
                    "tuple_key": it["tuple_key"],
                    "card_A": it["card"], "card_B": it["card_B"],
                    "occurrences": [], "seeds": set(), "cells": set(),
                })
                u["occurrences"].append([r["deck_id"], vn, it["item_id"]])
                u["seeds"].add(r["seed"])
                u["cells"].add(r["cell"])
    for u in units.values():
        u["seeds"] = sorted(u["seeds"])
        u["cells"] = sorted(u["cells"])
    return units


def make_chunks(units: dict, order: str, only_seed: int | None):
    """Group by task (the brief is per-task), then chunk. Deterministic ordering."""
    bytask = defaultdict(list)
    for (task, ck), u in sorted(units.items()):
        if only_seed is not None and only_seed not in u["seeds"]:
            continue
        bytask[task].append(u)
    chunks = []
    for task, us in sorted(bytask.items()):
        brief = (SPECS / task / "instructions.txt").read_text(errors="replace")
        for s in range(0, len(us), CHUNK):
            grp = us[s:s + CHUNK]
            # order B also reverses item order within the chunk
            grp_ordered = grp if order == "A" else grp[::-1]
            cards = []
            ids = []
            for n, u in enumerate(grp_ordered, 1):
                iid = f"X{n:02d}"
                ids.append((iid, u))
                card = u["card_A"] if order == "A" else u["card_B"]
                cards.append(re.sub(r"^ITEM \S+", f"ITEM {iid}", card))
            prompt = blind("\n\n".join([
                f"# SIMULATION BRIEF (what the deck was asked to model)\n\n{brief}",
                "# FLAGGED DIFFERENCES\n\n" + "\n\n".join(cards),
                QUESTIONS,
            ]))
            chunks.append({
                "chunk_id": f"{task}::{order}::{s // CHUNK:03d}",
                "task": task, "order": order, "prompt": prompt,
                "ids": [[i, u["cache_key"]] for i, u in ids],
            })
    return chunks


def extract_json(text: str):
    t = re.sub(r"\s*```$", "", re.sub(r"^```(?:json)?\s*", "", (text or "").strip())).strip()
    try:
        return json.loads(t)
    except json.JSONDecodeError:
        pass
    st = t.find("{")
    if st < 0:
        return None
    depth = 0
    instr = esc = False
    for i in range(st, len(t)):
        c = t[i]
        if instr:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                instr = False
            continue
        if c == '"':
            instr = True
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(t[st:i + 1])
                except json.JSONDecodeError:
                    return None
    return None


def normalise_verdicts(p) -> dict:
    """Accept any of the three response shapes models actually emit and key them by
    the X\\d+ item token.

      A  {"verdicts": [{"id": "X01", ...}, ...]}     <- the requested schema
      B  {"X01": {...}, "X02": {...}}                <- deepseek-v4-flash
      C  [{"id": "X01", ...}, ...]                   <- deepseek-v4-flash, sometimes

    Response-shape normalisation only. The decision-tree answers and the frozen
    terminal->credit mapping are untouched; ids like "ITEM X01" (qwen3-235b) are
    reduced to "X01".
    """
    out: dict = {}

    def put(key, v):
        if not isinstance(v, dict):
            return
        m = re.search(r"X\d+", str(key).upper())
        if m:
            out.setdefault(m.group(0), v)

    if isinstance(p, dict) and isinstance(p.get("verdicts"), list):
        for v in p["verdicts"]:
            if isinstance(v, dict):
                put(v.get("id", ""), v)
        if out:
            return out
    if isinstance(p, list):
        for v in p:
            if isinstance(v, dict):
                put(v.get("id", ""), v)
        return out
    if isinstance(p, dict):
        for k, v in p.items():
            put(k, v)
    return out


def call(chunk: dict, judge: str, rep: int, max_tokens: int, use_schema: bool,
         retries: int = 3) -> dict:
    model = JUDGES[judge]
    out = {"chunk_id": chunk["chunk_id"], "task": chunk["task"], "order": chunk["order"],
           "judge": judge, "model": model, "rep": rep, "rubric": "J1_rubric_v2",
           "n_items": len(chunk["ids"])}
    last = None
    for attempt in range(retries):
        try:
            kw = {}
            if use_schema:
                # DeepSeek's API implements response_format=json_object but not
                # json_schema; asking for json_schema there just wastes attempts.
                if model.startswith("deepseek-") or attempt >= 1:
                    kw["response_format"] = {"type": "json_object"}
                else:
                    kw["response_format"] = {
                        "type": "json_schema",
                        "json_schema": {"name": "verdicts", "strict": True, "schema": SCHEMA},
                    }
            r = client_for(model).chat.completions.create(
                model=model, temperature=0, max_tokens=max_tokens,
                messages=[{"role": "system", "content": SYSTEM},
                          {"role": "user", "content": chunk["prompt"]}], **kw)
            txt = r.choices[0].message.content or ""
            u = r.usage
            pin = getattr(u, "prompt_tokens", 0) or 0
            pout = getattr(u, "completion_tokens", 0) or 0
            ci, co = PRICING[model]
            out.update({"raw_response": txt, "prompt_tokens": pin, "completion_tokens": pout,
                        "cost_usd": round(pin * ci + pout * co, 8),
                        "finish_reason": r.choices[0].finish_reason, "attempts": attempt + 1})
            p = extract_json(txt)
            if p is None:
                out["parse_error"] = ("truncated (finish_reason=length)"
                                      if r.choices[0].finish_reason == "length"
                                      else "no JSON object found")
                if attempt < retries - 1:
                    max_tokens = int(max_tokens * 2)
                    continue
                return out
            byid = normalise_verdicts(p)
            verdicts = {}
            for iid, ck in chunk["ids"]:
                v = byid.get(iid)
                if not v:
                    continue
                sev, err = terminal(v)
                verdicts[ck] = {"iid": iid, "raw": v, "severity": sev, "error": err,
                                "credit": CREDIT.get(sev)}
            out["verdicts"] = verdicts
            out["coverage"] = len(verdicts) / len(chunk["ids"])
            if not verdicts and attempt < retries - 1:
                continue           # malformed / unmatched ids: one more try
            return out
        except Exception as exc:  # noqa: BLE001
            last = f"{type(exc).__name__}: {exc}"
            time.sleep(2 * (attempt + 1))
    out["api_error"] = last
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--items", default="neurips_review/sprint/artifacts/J1_items.jsonl")
    ap.add_argument("--out", required=True)
    ap.add_argument("--judges", nargs="*", default=list(JUDGES))
    ap.add_argument("--order", default="A")
    ap.add_argument("--only-seed", type=int, default=None,
                    help="restrict to units occurring in this seed (order-B / re-run subsample)")
    ap.add_argument("--rep", type=int, default=0, help="0 = primary, 1 = determinism re-run")
    ap.add_argument("--max-tokens", type=int, default=4000)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--tasks", nargs="*", default=None)
    ap.add_argument("--no-schema", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    units = select_units(REPO / a.items if not a.items.startswith("/") else Path(a.items))
    chunks = make_chunks(units, a.order, a.only_seed)
    if a.tasks:
        chunks = [c for c in chunks if c["task"] in a.tasks]

    # blinding audit over every prompt, before any call
    bad = [c["chunk_id"] for c in chunks
           if re.search(r"autocamp_|_icl_s\d|/data/shared|sci/repo3", c["prompt"])]
    assert not bad, f"BLINDING FAILURE in {len(bad)} chunks: {bad[:3]}"
    print(f"{len(units)} unique units -> {len(chunks)} chunks (order {a.order}, "
          f"seed filter {a.only_seed}); blinding audit clean")

    if a.dry_run:
        ch = max(len(c["prompt"]) for c in chunks)
        tot_in = sum(len(c["prompt"]) for c in chunks) / 3.7
        print(f"max prompt {ch} chars; est input tokens/order = {tot_in:,.0f}")
        est = 0.0
        for j in a.judges:
            ci, co = PRICING[JUDGES[j]]
            e = tot_in * ci + len(chunks) * 8 * 55 * co
            est += e
            print(f"  {j:14} ${e:.3f}")
        print(f"  TOTAL for this pass: ${est:.3f}")
        print("\n--- example prompt (truncated) ---\n" + chunks[0]["prompt"][:1500])
        return

    outp = Path(a.out)
    outp.parent.mkdir(parents=True, exist_ok=True)
    done = set()
    if outp.exists():
        for l in outp.open():
            try:
                r = json.loads(l)
                done.add((r["chunk_id"], r["judge"], r["rep"]))
            except json.JSONDecodeError:
                continue
    jobs = [(c, j) for c in chunks for j in a.judges
            if (c["chunk_id"], j, a.rep) not in done]
    if a.limit:
        jobs = jobs[:a.limit]
    print(f"{len(done)} already done; {len(jobs)} calls to make")

    ok = fail = 0
    cost = 0.0
    with outp.open("a") as fh, ThreadPoolExecutor(max_workers=a.workers) as ex:
        futs = [ex.submit(call, c, j, a.rep, a.max_tokens, not a.no_schema) for c, j in jobs]
        for i, f in enumerate(as_completed(futs), 1):
            r = f.result()
            fh.write(json.dumps(r) + "\n")
            fh.flush()
            cost += r.get("cost_usd", 0.0)
            if r.get("verdicts"):
                ok += 1
                tag = f"cov={r['coverage']:.2f} n={len(r['verdicts'])}"
            else:
                fail += 1
                tag = "FAILED " + str(r.get("parse_error") or r.get("api_error"))[:60]
            print(f"[{i}/{len(jobs)}] {r['chunk_id'][:48]:50} {r['judge']:13} {tag}", flush=True)
    print(f"\nok={ok} failed={fail} cost=${cost:.4f}")


if __name__ == "__main__":
    main()
