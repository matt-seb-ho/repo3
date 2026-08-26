#!/usr/bin/env python3
"""
Thread J1 — SECTION-level soft-TreeSim judge runner (design C, shipped).

One call per (deck, section) unit. Rubric: artifacts/J1_rubric_v4.md
  sha256 5ee738e008d94c31e884cbeca1d1d7b1213642f82732ad8b0428373a06a9bb4d
  frozen 2026-07-27T08:23:41Z, before any section-level call.

Resumable: skips (deck_id, unit_id, judge, order, rep) already in the output.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

REPO = Path("/home/matt/sci/repo3")
load_dotenv(REPO / ".env")
ART = REPO / "neurips_review/sprint/artifacts"
SPECS = Path("/data/shared/geophysics_agent_data/data/eval/experiments_from_mined_specs")

JUDGES = {
    "hy3":          "tencent/hy3",                      # primary, researcher's directive
    "qwen3235b":    "qwen/qwen3-235b-a22b-2507",        # second, researcher's directive
    "gemini3flash": "google/gemini-3-flash-preview",    # for C1/C3/C4
    "gpt54mini":    "openai/gpt-5.4-mini",              # for C1/C3/C4
    "dsv4flash":    "deepseek-v4-flash",                # fallback only, see rubric v4 §7
}
# OpenRouter list price, $/token, captured 2026-07-27 from /api/v1/models.
# DeepSeek direct: off-peak list from scripts/oh_dsv4_compare.py:56.
# Costs are computed from raw token counts x these numbers, NEVER from a provider
# cost field (trap 2 of the DeepSeek cost-accounting memory).
PRICING = {
    "tencent/hy3":                   (0.132e-6, 0.528e-6),
    "qwen/qwen3-235b-a22b-2507":     (0.09e-6, 0.55e-6),
    "google/gemini-3-flash-preview": (0.50e-6, 3.00e-6),
    "openai/gpt-5.4-mini":           (0.75e-6, 4.50e-6),
    "deepseek-v4-flash":             (0.14e-6, 0.28e-6),
}
_OR = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.environ["OPENROUTER_API_KEY"])
_DS = (OpenAI(base_url="https://api.deepseek.com/v1", api_key=os.environ["DEEPSEEK_API_KEY"])
       if os.environ.get("DEEPSEEK_API_KEY") else None)

LEVELS = ["equivalent", "minor_deviation", "material_deviation", "wrong"]
CREDIT = {"equivalent": 1.0, "minor_deviation": 0.7, "material_deviation": 0.3, "wrong": 0.0}

SYSTEM = """You are a computational geomechanics and reservoir-simulation expert auditing GEOS XML \
input decks. GEOS is an open-source multiphysics simulator for subsurface problems \
(poromechanics, thermo-poro-elasticity, multiphase flow, hydraulic fracturing).

You are a measurement instrument inside a structural metric. That metric compares a CANDIDATE deck \
against a REFERENCE deck by exact attribute equality (relative tolerance 1e-6). It therefore scores \
a permeability wrong by a factor of two exactly the same as one wrong by eighteen orders of \
magnitude, and scores a consistent identifier rename or a whitespace difference as a total failure. \
You supply the physical judgment it cannot make, for ONE section of the deck at a time.

Rules:
- Judge physics and numerical setup, not text. Ignore comments, ordering, indentation, and verbosity.
- An identifier renamed and used consistently within the candidate is NOT a difference.
- An attribute stated explicitly at the value GEOS would use by default is NOT a difference.
- Extra output, logging or restart declarations are NOT physical differences.
- Judge only the section you are given. Do not speculate about the rest of the deck.
- Reply with a single json object and nothing else."""


def questions(section: str) -> str:
    return f"""## Your task

Assess the CANDIDATE <{section}> section against the REFERENCE <{section}> section, for the
simulation described in the brief. Choose exactly one level.

  "equivalent"          The candidate specifies the same physics and the same numerical setup as
                        the reference. Any differences are immaterial: identifiers renamed and used
                        consistently, formatting, attributes stated at their GEOS default, extra
                        output or logging, reordering. A domain scientist would call the two
                        interchangeable.

  "minor_deviation"     Physically plausible alternative choices only. Same governing physics, same
                        constitutive models, same boundary-condition types. Differences are solver
                        tolerances, time steps, mesh counts, or material constants inside the normal
                        engineering range for the stated material. A domain scientist would accept
                        the candidate for this task.

  "material_deviation"  Meaningfully different, but still modelling the requested physics: a
                        different but real material, a coarser-but-valid discretization, a different
                        valid solver or preconditioner, or a boundary condition of the right type
                        with a different magnitude. Results would differ noticeably.

  "wrong"               The section does not specify the physics the brief asks for, contains
                        unphysical values, has a wrong sign or wrong units by a large factor, or
                        omits content the requested physics cannot run without.

Reply with a single json object of exactly this shape and nothing else -- no prose, no markdown
fences:

{{"level": "equivalent|minor_deviation|material_deviation|wrong",
  "reason": "at most 40 words, about the physics",
  "unphysical_values": ["attribute and why, at most 20 words each"]}}"""


SCHEMA = {
    "type": "object",
    "properties": {
        "level": {"type": "string", "enum": LEVELS},
        "reason": {"type": "string"},
        "unphysical_values": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["level", "reason", "unphysical_values"],
    "additionalProperties": False,
}

_PATH_PAT = re.compile(
    r"(/[\w./-]*(?:geophysics_agent_data|autocamp|experiments_gt|sci/repo3|workspace)[\w./-]*)")
_CELL_PAT = re.compile(r"\b(autocamp_(?:F\d+|SE)|F\d+_icl_s\d|SE_icl_s\d)\b")


def blind(t: str) -> str:
    return _CELL_PAT.sub("<cond>", _PATH_PAT.sub("<path>", t))


def build_prompt(brief: str, sec: dict, order: str) -> str:
    s = sec["section"]
    ref = f"# REFERENCE <{s}> SECTION (the accepted solution)\n\n```xml\n{sec['ref_xml']}\n```"
    cand = f"# CANDIDATE <{s}> SECTION (under evaluation)\n\n```xml\n{sec['cand_xml']}\n```"
    blocks = [ref, cand] if order == "A" else [cand, ref]
    return blind("\n\n".join([
        f"# SIMULATION BRIEF (what the deck was asked to model)\n\n{brief}",
        *blocks, questions(s)]))


def units(path: Path, only_seed: int | None, tasks=None, cells=None):
    out = []
    for line in path.open():
        r = json.loads(line)
        if r.get("rung1_fail"):
            continue
        if only_seed is not None and r["seed"] != only_seed:
            continue
        if tasks and r["task"] not in tasks:
            continue
        if cells and r["cell"] not in cells:
            continue
        brief = (SPECS / r["task"] / "instructions.txt").read_text(errors="replace")
        for s in r["sections"]:
            if not s["present_in_candidate"]:
                continue
            out.append({"deck_id": r["deck_id"], "cell": r["cell"], "seed": r["seed"],
                        "task": r["task"], "unit_id": s["unit_id"], "section": s["section"],
                        "treesim_section_score": s["treesim_section_score"],
                        "brief": brief, "sec": s})
    return out


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


def norm_level(p) -> str | None:
    """Tolerant level extraction. Shape normalisation only; never changes a verdict."""
    if not isinstance(p, dict):
        return None
    v = p.get("level") or p.get("verdict") or p.get("assessment")
    if v is None:
        for k in p:
            if isinstance(p[k], dict) and p[k].get("level"):
                v = p[k]["level"]
                break
    if v is None:
        return None
    s = str(v).strip().lower().replace(" ", "_").replace("-", "_")
    if s in CREDIT:
        return s
    for lv in LEVELS:                       # e.g. "minor" -> "minor_deviation"
        if s and (lv.startswith(s) or s.startswith(lv.split("_")[0])):
            return lv
    return None


def call(u: dict, judge: str, order: str, rep: int, max_tokens: int, retries: int = 3) -> dict:
    model = JUDGES[judge]
    cl = _DS if model.startswith("deepseek-") else _OR
    out = {"deck_id": u["deck_id"], "cell": u["cell"], "seed": u["seed"], "task": u["task"],
           "unit_id": u["unit_id"], "section": u["section"],
           "treesim_section_score": u["treesim_section_score"],
           "judge": judge, "model": model, "order": order, "rep": rep, "rubric": "J1_rubric_v4"}
    prompt = build_prompt(u["brief"], u["sec"], order)
    last = None
    for attempt in range(retries):
        try:
            kw = {}
            if model.startswith("deepseek-") or attempt >= 1:
                kw["response_format"] = {"type": "json_object"}
            else:
                kw["response_format"] = {"type": "json_schema",
                                         "json_schema": {"name": "section_verdict",
                                                         "strict": True, "schema": SCHEMA}}
            r = cl.chat.completions.create(
                model=model, temperature=0, max_tokens=max_tokens,
                messages=[{"role": "system", "content": SYSTEM},
                          {"role": "user", "content": prompt}], **kw)
            txt = r.choices[0].message.content or ""
            us = r.usage
            pin = getattr(us, "prompt_tokens", 0) or 0
            pout = getattr(us, "completion_tokens", 0) or 0
            ci, co = PRICING[model]
            out.update({"raw_response": txt, "prompt_tokens": pin, "completion_tokens": pout,
                        "cost_usd": round(pin * ci + pout * co, 8),
                        "finish_reason": r.choices[0].finish_reason, "attempts": attempt + 1})
            p = extract_json(txt)
            lv = norm_level(p)
            if lv is None:
                out["parse_error"] = ("truncated" if r.choices[0].finish_reason == "length"
                                      else f"no level in {str(txt)[:80]!r}")
                if attempt < retries - 1:
                    max_tokens = int(max_tokens * 2)
                    continue
                return out
            out.update({"level": lv, "credit": CREDIT[lv],
                        "reason": (p or {}).get("reason"),
                        "unphysical_values": (p or {}).get("unphysical_values")})
            return out
        except Exception as exc:  # noqa: BLE001
            last = f"{type(exc).__name__}: {exc}"
            time.sleep(2 * (attempt + 1))
    out["api_error"] = last
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sections", default=str(ART / "J1_sections.jsonl"))
    ap.add_argument("--out", required=True)
    ap.add_argument("--judges", nargs="*", default=["hy3", "qwen3235b", "gemini3flash", "gpt54mini"])
    ap.add_argument("--order", default="A")
    ap.add_argument("--only-seed", type=int, default=None)
    ap.add_argument("--rep", type=int, default=0)
    ap.add_argument("--tasks", nargs="*", default=None)
    ap.add_argument("--cells", nargs="*", default=None)
    ap.add_argument("--max-tokens", type=int, default=900)
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    us = units(Path(a.sections), a.only_seed, a.tasks, a.cells)
    bad = [u["deck_id"] for u in us
           if re.search(r"autocamp_|_icl_s\d|/data/shared|sci/repo3",
                        build_prompt(u["brief"], u["sec"], a.order))]
    assert not bad, f"BLINDING FAILURE in {len(bad)} units: {bad[:3]}"
    print(f"{len(us)} judgeable section units (order {a.order}, seed {a.only_seed}); "
          f"blinding audit clean")

    if a.dry_run:
        tin = sum(len(build_prompt(u["brief"], u["sec"], a.order)) for u in us) / 3.7
        print(f"est input tokens per judge = {tin:,.0f}")
        tot = 0.0
        for j in a.judges:
            ci, co = PRICING[JUDGES[j]]
            e = tin * ci + len(us) * 140 * co
            tot += e
            print(f"  {j:14} ${e:.3f}")
        print(f"  TOTAL this pass: ${tot:.3f}")
        print("\n--- example prompt (truncated) ---\n"
              + build_prompt(us[0]["brief"], us[0]["sec"], a.order)[:1800])
        return

    outp = Path(a.out)
    outp.parent.mkdir(parents=True, exist_ok=True)
    done = set()
    if outp.exists():
        for l in outp.open():
            try:
                r = json.loads(l)
                done.add((r["deck_id"], r["unit_id"], r["judge"], r["order"], r["rep"]))
            except json.JSONDecodeError:
                continue
    jobs = [(u, j) for u in us for j in a.judges
            if (u["deck_id"], u["unit_id"], j, a.order, a.rep) not in done]
    if a.limit:
        jobs = jobs[:a.limit]
    print(f"{len(done)} already done; {len(jobs)} calls to make")

    ok = fail = 0
    cost = 0.0
    with outp.open("a") as fh, ThreadPoolExecutor(max_workers=a.workers) as ex:
        futs = [ex.submit(call, u, j, a.order, a.rep, a.max_tokens) for u, j in jobs]
        for i, f in enumerate(as_completed(futs), 1):
            r = f.result()
            fh.write(json.dumps(r) + "\n")
            fh.flush()
            cost += r.get("cost_usd", 0.0)
            if r.get("level"):
                ok += 1
                tag = f"{r['level']:18} (treesim {r['treesim_section_score']:.3f})"
            else:
                fail += 1
                tag = "FAILED " + str(r.get("parse_error") or r.get("api_error"))[:60]
            if i % 25 == 0 or fail and i % 5 == 0:
                print(f"[{i}/{len(jobs)}] {r['deck_id'][:38]:40}{r['section'][:16]:17}"
                      f"{r['judge']:13} {tag}", flush=True)
    print(f"\nok={ok} failed={fail} cost=${cost:.4f}")


if __name__ == "__main__":
    main()
