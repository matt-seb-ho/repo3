#!/usr/bin/env python3
"""
Thread J1 — SECTION-level units for soft-TreeSim (design C, the shipped design).

Unit of judgment = one (deck, top-level GEOS section). For each, emit the
reference section and the candidate section as XML, serialised from the RESOLVED
trees so the judge sees exactly what TreeSim compares, plus TreeSim's own score
for that section.

Aggregation identity that makes this a drop-in replacement (verified by --verify):

    TreeSim(deck) = ( sum over reference top-level sections of section_score )
                    / n_reference_sections
                    - beta * n_extra_sections / (n_reference + n_extra)

i.e. TreeSim weights sections UNIFORMLY at 1/N. Soft-TreeSim substitutes the
judge's ordinal credit for `section_score` and leaves that arithmetic alone.
"""
from __future__ import annotations

import argparse
import json
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

REPO = Path("/home/matt/sci/repo3")
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "neurips_review/sprint/scripts"))
from eval.judge_geos import (  # noqa: E402
    IGNORE_TAGS, NUMERIC_RTOL, TREESIM_ALPHA, TREESIM_BETA,
    _bipartite_match, load_and_resolve_dir, tree_sim,
)

ICL = Path("/data/shared/geophysics_agent_data/data/eval/autocamp_followup_2026-05-02/icl")
RESULTS = Path("/data/shared/geophysics_agent_data/data/eval/autocamp_followup_2026-05-02/_results_icl")
GT = Path("/data/shared/geophysics_agent_data/data/eval/experiments_gt")
SPECS = Path("/data/shared/geophysics_agent_data/data/eval/experiments_from_mined_specs")

CELLS = {"F0": "autocamp_F0", "F6": "autocamp_F6", "SE": "autocamp_SE"}
SEEDS = [1, 2, 3]
TASKS = [
    "AdvancedExampleCasedThermoElasticWellbore", "AdvancedExamplePureThermalDiffusionWellbore",
    "AdvancedExampleThermoPoroElasticWellbore", "AdvancedExampleViscoExtendedDruckerPrager",
    "ExampleIsothermalHystInjection", "ExampleMCCWellbore", "ExampleProppantTest",
    "ExampleVerticalPoroElastoPlasticWellbore", "ExamplesingleFracCompression",
    "TutorialHydraulicFractureWithAdvancedXML",
]
SECTION_CHAR_CAP = 18000     # per side, per section; disclosed in the rubric


def ser(e: ET.Element) -> str:
    """Pretty-printed XML of one section, from the resolved tree."""
    def walk(el, ind=0):
        pad = "  " * ind
        kids = [c for c in el if isinstance(c.tag, str)]
        attrs = "".join(f' {k}="{v}"' for k, v in el.attrib.items())
        if not kids:
            return [f"{pad}<{el.tag}{attrs}/>"]
        out = [f"{pad}<{el.tag}{attrs}>"]
        for c in kids:
            out += walk(c, ind + 1)
        out.append(f"{pad}</{el.tag}>")
        return out
    return "\n".join(walk(e))


def cap(t: str) -> tuple[str, bool]:
    if len(t) <= SECTION_CHAR_CAP:
        return t, False
    return t[:SECTION_CHAR_CAP] + "\n<!-- ... TRUNCATED ... -->", True


def treesim_of_record() -> dict:
    """Per-deck TreeSim from _summary.json -> results[]. Never globs *_eval.json."""
    out = {}
    for cell, cdir in CELLS.items():
        for seed in SEEDS:
            s = RESULTS / f"{cell}_icl_s{seed}" / cdir / "_summary.json"
            if not s.exists():
                continue
            for r in json.load(s.open())["results"]:
                t = r.get("experiment") or r.get("task") or r.get("name")
                out[f"{cell}_s{seed}_{t}"] = {"treesim": r.get("treesim"),
                                              "status": r.get("status"),
                                              "sections": r.get("treesim_section_scores")}
    return out


def deck_sections(gt_root: ET.Element, gen_root: ET.Element) -> dict:
    """Reproduce TreeSim's top-level decomposition exactly.

    The root frame of `tree_sim` groups children by tag, bipartite-matches within
    each tag group, scores each matched reference child, scores unmatched
    reference children 0, and counts unmatched candidate children as `extra`.
    """
    gt_children = [c for c in gt_root if isinstance(c.tag, str) and c.tag not in IGNORE_TAGS]
    gen_children = [c for c in gen_root if isinstance(c.tag, str) and c.tag not in IGNORE_TAGS]
    gt_by, gen_by = defaultdict(list), defaultdict(list)
    for c in gt_children:
        gt_by[c.tag].append(c)
    for c in gen_children:
        gen_by[c.tag].append(c)

    secs, extra = [], 0
    for tag in sorted(set(gt_by) | set(gen_by)):
        g, n = gt_by.get(tag, []), gen_by.get(tag, [])
        matched, un_gt, un_gen = _bipartite_match(g, n, NUMERIC_RTOL)
        for gi, gj, _s in matched:
            ge, ne = g[gi], n[gj]
            grand = [c for c in ge if isinstance(c.tag, str) and c.tag not in IGNORE_TAGS]
            if grand:
                sc, _ = tree_sim(ge, ne, TREESIM_ALPHA, TREESIM_BETA, NUMERIC_RTOL)
                from eval.judge_geos import attr_similarity
                a = attr_similarity(ge, ne, NUMERIC_RTOL)
                sc = TREESIM_ALPHA * a + (1 - TREESIM_ALPHA) * sc
            else:
                from eval.judge_geos import attr_similarity
                sc = attr_similarity(ge, ne, NUMERIC_RTOL)
            secs.append({"section": tag, "present_in_candidate": True,
                         "treesim_section_score": sc,
                         "ref_xml": ser(ge), "cand_xml": ser(ne),
                         "n_ref_elements": sum(1 for _ in ge.iter()),
                         "n_cand_elements": sum(1 for _ in ne.iter())})
        for i in un_gt:
            secs.append({"section": tag, "present_in_candidate": False,
                         "treesim_section_score": 0.0,
                         "ref_xml": ser(g[i]), "cand_xml": None,
                         "n_ref_elements": sum(1 for _ in g[i].iter()),
                         "n_cand_elements": 0})
        extra += len(un_gen)
    return {"sections": secs, "n_ref_sections": len(gt_children), "n_extra_sections": extra}


def aggregate(secs_credit: list[float], n_ref: int, n_extra: int) -> float:
    """TreeSim's own root-frame arithmetic. Frozen."""
    if n_ref == 0:
        return 1.0
    ms = sum(secs_credit) / n_ref
    den = n_ref + n_extra
    pen = TREESIM_BETA * (n_extra / den) if den else 0.0
    return max(0.0, min(1.0, ms - pen))


def build(cell: str, seed: int, task: str, tsrec: dict) -> dict:
    did = f"{cell}_s{seed}_{task}"
    gen_dir = ICL / CELLS[cell] / f"{cell}_icl_s{seed}" / task / "inputs"
    gt_dir = GT / task / "inputs"
    rec = {"deck_id": did, "cell": cell, "seed": seed, "task": task,
           "gen_dir": str(gen_dir), "gt_dir": str(gt_dir),
           "treesim_of_record": tsrec.get(did, {}).get("treesim"),
           "run_status": tsrec.get(did, {}).get("status")}
    try:
        g = load_and_resolve_dir(gt_dir)
        n = load_and_resolve_dir(gen_dir)
    except Exception as exc:  # noqa: BLE001
        rec.update({"rung1_fail": True, "rung1_reason": f"{type(exc).__name__}: {exc}",
                    "sections": [], "n_ref_sections": 0, "n_extra_sections": 0})
        return rec
    rec["rung1_fail"] = False
    rec.update(deck_sections(g, n))
    for i, s in enumerate(rec["sections"], 1):
        s["unit_id"] = f"S{i:02d}"
        s["ref_xml"], s["ref_truncated"] = cap(s["ref_xml"])
        if s["cand_xml"] is not None:
            s["cand_xml"], s["cand_truncated"] = cap(s["cand_xml"])
    rec["treesim_reconstructed"] = aggregate(
        [s["treesim_section_score"] for s in rec["sections"]],
        rec["n_ref_sections"], rec["n_extra_sections"])
    rec["treesim_ceiling_all_sections_1"] = aggregate(
        [1.0] * len(rec["sections"]), rec["n_ref_sections"], rec["n_extra_sections"])
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--verify", action="store_true")
    a = ap.parse_args()
    tsrec = treesim_of_record()
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    ok = bad = skip = 0
    worst = 0.0
    with out.open("w") as fh:
        for cell in CELLS:
            for seed in SEEDS:
                for task in TASKS:
                    r = build(cell, seed, task, tsrec)
                    fh.write(json.dumps(r) + "\n")
                    pub = r.get("treesim_of_record")
                    if r.get("rung1_fail") or pub is None:
                        skip += 1
                        flag = "RUNG1-FAIL/no-record"
                    else:
                        d = abs(round(r["treesim_reconstructed"], 4) - float(pub))
                        worst = max(worst, d)
                        if d <= 1e-4:
                            ok += 1
                            flag = "exact"
                        else:
                            bad += 1
                            flag = f"MISMATCH published={pub} rebuilt={r['treesim_reconstructed']:.6f}"
                    print(f"{r['deck_id']:66} sections={len(r.get('sections', [])):3} "
                          f"n_ref={r.get('n_ref_sections')} extra={r.get('n_extra_sections')} "
                          f"ts={r.get('treesim_reconstructed')} {flag}", flush=True)
    print(f"\nsection decomposition vs published TreeSim: ok={ok} mismatch={bad} "
          f"skipped={skip} worst={worst:.2e}")
    print(f"wrote -> {out}")
    if a.verify:
        sys.exit(0 if bad == 0 else 1)


if __name__ == "__main__":
    main()
