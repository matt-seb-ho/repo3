#!/usr/bin/env python3
"""
Thread B — LMaaJ secondary metric. Judge runner.

Reads prompt records from B_build_prompts.py, calls each judge model via OpenRouter at
temperature 0, parses the strict-JSON verdict, and appends one JSONL row per
(deck, judge, order) with raw response text and token usage preserved.

Resumable: skips (deck_id, judge, order) triples already present in the output file.
Rubric: neurips_review/sprint/artifacts/B_rubric_v1.md (frozen).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv("/home/matt/sci/repo3/.env")

JUDGES = {
    "gpt54mini": "openai/gpt-5.4-mini",
    "gemini3flash": "google/gemini-3-flash-preview",
    "qwen3235b": "qwen/qwen3-235b-a22b-2507",
}

# OpenRouter list price, $ per token, captured 2026-07-26 from /api/v1/models.
PRICING = {
    "openai/gpt-5.4-mini": (0.00000075, 0.0000045),
    "google/gemini-3-flash-preview": (0.0000005, 0.000003),
    "qwen/qwen3-235b-a22b-2507": (0.00000009, 0.00000055),
}

CLIENT = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)

SEVERITIES = {"cosmetic", "minor", "material", "severe"}
CREDIT = {"cosmetic": 1.0, "minor": 0.7, "material": 0.3, "severe": 0.0}


def extract_json(text: str) -> dict | None:
    t = text.strip()
    t = re.sub(r"^```(?:json)?\s*", "", t)
    t = re.sub(r"\s*```$", "", t).strip()
    try:
        return json.loads(t)
    except json.JSONDecodeError:
        pass
    # first balanced {...}
    start = t.find("{")
    if start < 0:
        return None
    depth, instr, esc = 0, False, False
    for i in range(start, len(t)):
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
                    return json.loads(t[start:i + 1])
                except json.JSONDecodeError:
                    return None
    return None


def score_verdict(v: dict, expected_ids: list[str]) -> dict:
    """Apply the frozen rubric arithmetic. No tuning here."""
    got = {}
    bad = []
    for item in (v.get("mismatch_verdicts") or []):
        if not isinstance(item, dict):
            continue
        i = str(item.get("id", "")).strip().upper()
        s = str(item.get("severity", "")).strip().lower()
        if s not in SEVERITIES:
            bad.append(i)
            continue
        if i in got:
            continue
        got[i] = s

    covered = [i for i in expected_ids if i in got]
    labels = [got[i] for i in covered]
    credit = (sum(CREDIT[s] for s in labels) / len(labels)) if labels else (
        1.0 if not expected_ids else None)

    def clamp10(x):
        try:
            x = float(x)
        except (TypeError, ValueError):
            return None
        return max(0.0, min(10.0, x))

    pl = clamp10(v.get("plausibility"))
    pf = clamp10(v.get("physics_fidelity"))

    lmaaj = None
    if pl is not None and pf is not None and credit is not None:
        lmaaj = (pl / 10.0 + credit + pf / 10.0) / 3.0

    return {
        "severity_labels": got,
        "n_expected": len(expected_ids),
        "n_labelled": len(covered),
        "coverage": (len(covered) / len(expected_ids)) if expected_ids else 1.0,
        "n_invalid_severity": len(bad),
        "mismatch_credit": credit,
        "plausibility": pl,
        "physics_fidelity": pf,
        "lmaaj": lmaaj,
        "plausibility_reason": v.get("plausibility_reason"),
        "physics_fidelity_reason": v.get("physics_fidelity_reason"),
        "unphysical_values": v.get("unphysical_values"),
    }


def call_judge(rec: dict, judge_key: str, order: str, max_tokens: int,
               retries: int = 3) -> dict:
    model = JUDGES[judge_key]
    out = {
        "deck_id": rec["deck_id"], "cell": rec["cell"], "seed": rec["seed"],
        "task": rec["task"], "judge": judge_key, "model": model, "order": order,
        "treesim": rec.get("treesim"),
        "n_mismatch_total": rec.get("n_mismatch_total"),
        "rubric": "B_rubric_v1",
    }
    last = None
    for attempt in range(retries):
        try:
            r = CLIENT.chat.completions.create(
                model=model,
                temperature=0,
                max_tokens=max_tokens,
                messages=[
                    {"role": "system", "content": rec["system"]},
                    {"role": "user", "content": rec[f"prompt_{order}"]},
                ],
            )
            txt = r.choices[0].message.content or ""
            u = r.usage
            pin = getattr(u, "prompt_tokens", 0) or 0
            pout = getattr(u, "completion_tokens", 0) or 0
            cin, cout = PRICING[model]
            out.update({
                "raw_response": txt,
                "prompt_tokens": pin, "completion_tokens": pout,
                "cost_usd": round(pin * cin + pout * cout, 6),
                "finish_reason": r.choices[0].finish_reason,
                "attempts": attempt + 1,
            })
            parsed = extract_json(txt)
            if parsed is None:
                out["parse_error"] = "no JSON object found"
                out["scored"] = None
            else:
                out["parsed"] = parsed
                out["scored"] = score_verdict(parsed, rec.get("mismatch_ids", []))
            return out
        except Exception as exc:  # noqa: BLE001 - want the message recorded, not swallowed
            last = f"{type(exc).__name__}: {exc}"
            time.sleep(2 * (attempt + 1))
    out["api_error"] = last
    out["scored"] = None
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompts", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--judges", nargs="*", default=list(JUDGES))
    ap.add_argument("--orders", nargs="*", default=["A"])
    ap.add_argument("--order-b-seeds", nargs="*", type=int, default=[1],
                    help="order B only for these seeds (position-bias subsample)")
    ap.add_argument("--max-tokens", type=int, default=6000)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--limit", type=int, default=None)
    a = ap.parse_args()

    recs = [json.loads(l) for l in Path(a.prompts).open()]
    outp = Path(a.out)
    outp.parent.mkdir(parents=True, exist_ok=True)

    done = set()
    if outp.exists():
        for l in outp.open():
            try:
                r = json.loads(l)
                done.add((r["deck_id"], r["judge"], r["order"]))
            except json.JSONDecodeError:
                continue
    print(f"{len(done)} calls already in {outp}")

    jobs = []
    for rec in recs:
        if rec.get("rung1_fail"):
            continue
        for judge in a.judges:
            for order in a.orders:
                if order == "B" and rec["seed"] not in a.order_b_seeds:
                    continue
                if (rec["deck_id"], judge, order) in done:
                    continue
                jobs.append((rec, judge, order))
    if a.limit:
        jobs = jobs[:a.limit]
    print(f"{len(jobs)} calls to make")

    n_ok = n_bad = 0
    cost = 0.0
    with outp.open("a") as fh, ThreadPoolExecutor(max_workers=a.workers) as ex:
        futs = {ex.submit(call_judge, r, j, o, a.max_tokens): (r["deck_id"], j, o)
                for r, j, o in jobs}
        for i, f in enumerate(as_completed(futs), 1):
            res = f.result()
            fh.write(json.dumps(res) + "\n")
            fh.flush()
            cost += res.get("cost_usd", 0.0)
            s = res.get("scored")
            if s and s.get("lmaaj") is not None:
                n_ok += 1
                tag = (f"lmaaj={s['lmaaj']:.3f} cred={s['mismatch_credit']:.3f} "
                       f"pl={s['plausibility']:.0f} pf={s['physics_fidelity']:.0f} "
                       f"cov={s['coverage']:.2f}")
            else:
                n_bad += 1
                tag = "FAILED " + str(res.get("parse_error") or res.get("api_error"))[:70]
            print(f"[{i}/{len(jobs)}] {res['deck_id'][:46]:47} {res['judge']:13} {res['order']} {tag}")
    print(f"\nok={n_ok} failed={n_bad} cost=${cost:.4f}")


if __name__ == "__main__":
    main()
