#!/usr/bin/env python3
"""
Thread J1 — v2 item extraction with a DETERMINISTIC EVIDENCE LAYER.

For every place TreeSim assigns zero credit (`J1_treesim.Event`), build an *item
card*: the difference itself plus every fact about it that can be established by
code rather than guessed by a language model.

Rationale (see threads/J1_judge_v2.md §2): v1's judges disagreed at 2.6 % on
`missing_element` items because answering "does this missing element matter?"
requires exhaustive search of a 26 kB deck for a renamed or relocated
counterpart. That is a search problem, not a physics problem. Every evidence
function below removes one such non-physics sub-task from the model's plate:

  EV1 numeric        - ratio / orders of magnitude, computed in code
  EV2 format         - whitespace- and brace-normalised equality (TreeSim's
                       _parse_list nested-brace defect class)
  EV3 schema         - the GEOS binary's own XSD default + required flag
  EV4 identifier     - is a renamed identifier DEFINED and USED consistently
                       in the candidate deck (token counts on both sides)
  EV5 external file  - does the referenced data file exist on disk, and what
                       shape is it (blind spot 1: TreeSim never reads these)
  EV6 counterpart    - global same-tag / same-signature search of the candidate
                       tree (blind spot 2: TreeSim's matcher is LOCAL)
  EV7 section        - which top-level GEOS section the element sits in

Outputs `J1_items.jsonl`, one row per deck, containing the deck's TreeSim score,
every event with its structural weight d(score)/d(credit), and the rendered card.
"""
from __future__ import annotations

import argparse
import json
import hashlib
import math
import os
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path("/home/matt/sci/repo3")
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "neurips_review/sprint/scripts"))

from eval.judge_geos import load_and_resolve_dir  # noqa: E402
from J1_treesim import tree_sim_credited, elem_key  # noqa: E402

ICL = Path("/data/shared/geophysics_agent_data/data/eval/autocamp_followup_2026-05-02/icl")
RESULTS = Path("/data/shared/geophysics_agent_data/data/eval/autocamp_followup_2026-05-02/_results_icl")
GT = Path("/data/shared/geophysics_agent_data/data/eval/experiments_gt")
SPECS = Path("/data/shared/geophysics_agent_data/data/eval/experiments_from_mined_specs")
XSD = REPO / "neurips_review/sprint/artifacts/A1_binary_schema.xsd"

CELLS = {"F0": "autocamp_F0", "F6": "autocamp_F6", "SE": "autocamp_SE"}
SEEDS = [1, 2, 3]
TASKS = [
    "AdvancedExampleCasedThermoElasticWellbore",
    "AdvancedExamplePureThermalDiffusionWellbore",
    "AdvancedExampleThermoPoroElasticWellbore",
    "AdvancedExampleViscoExtendedDruckerPrager",
    "ExampleIsothermalHystInjection",
    "ExampleMCCWellbore",
    "ExampleProppantTest",
    "ExampleVerticalPoroElastoPlasticWellbore",
    "ExamplesingleFracCompression",
    "TutorialHydraulicFractureWithAdvancedXML",
]

# Attributes whose value names or points at something else in the deck.
REF_ATTRS = {
    "objectPath", "setNames", "targetRegions", "target", "sources", "materialList",
    "fluidNames", "solidNames", "solidNamesTable", "permeabilityNames", "porosityNames",
    "relPermNames", "capPressureNames", "functionName", "flowSolverName",
    "solidSolverName", "poromechanicsSolverName", "fractureRegion", "contactRelationName",
    "surfaceGeneratorName", "discretization", "cellBlocks", "cellBlockNames",
    "regionAttribute", "childDirectory", "proppantSolverName", "wellRegionName",
    "wellControlsName", "meshBody", "meshLevel", "fieldName", "component",
    "rockToughness", "nodeSets", "faceBlock", "thermalConductivityNames",
    "referenceElasticModulus",
}
# Attributes whose value is a path to a file TreeSim never opens (blind spot 1).
FILE_ATTRS = {
    "coordinateFiles", "voxelFile", "file", "filename", "fileName", "tableFiles",
    "valueFiles", "meshPath", "vtkMesh", "inputFile", "outputFile",
}
FILE_RE = re.compile(r"[\w./-]+\.(?:geos|txt|csv|vtu|vtk|vtm|pvd|h5|hdf5|xml|dat|table)\b")
IDENT_RE = re.compile(r"^[A-Za-z_][\w./-]*$")
TOKEN_SPLIT = re.compile(r"[{},\s]+")

TOP_SECTIONS = {
    "Solvers", "Mesh", "Geometry", "Events", "NumericalMethods", "ElementRegions",
    "Constitutive", "FieldSpecifications", "Outputs", "Tasks", "Functions",
    "Included", "Parameters", "Benchmarks",
}


# --------------------------------------------------------------------------
# EV3 — GEOS XSD schema index (defaults + required)
# --------------------------------------------------------------------------

def load_schema() -> dict:
    NS = "{http://www.w3.org/2001/XMLSchema}"
    root = ET.parse(XSD).getroot()
    out: dict[str, dict] = {}
    for ct in root.findall(f"{NS}complexType"):
        nm = ct.get("name") or ""
        if not nm.endswith("Type"):
            continue
        tag = nm[:-4]
        attrs = {}
        for a in ct.findall(f"{NS}attribute"):
            attrs[a.get("name")] = {
                "default": a.get("default"),
                "required": a.get("use") == "required",
                "type": a.get("type"),
            }
        out[tag] = attrs
    return out


SCHEMA = load_schema()


# --------------------------------------------------------------------------
# EV1 / EV2 — numeric + format
# --------------------------------------------------------------------------

_NUM = re.compile(r"^[+-]?(?:\d+\.?\d*|\.\d+)(?:[eEdD][+-]?\d+)?$")


def _floats(v: str) -> list[float] | None:
    """Robust flatten: handles nested braces and arbitrary whitespace.

    Deliberately MORE permissive than judge_geos._parse_list, which keeps inner
    braces as tokens and therefore falls through to string comparison for nested
    lists. The gap between the two is exactly the cosmetic-mismatch class.
    """
    toks = [t for t in TOKEN_SPLIT.split((v or "").strip()) if t]
    out = []
    for t in toks:
        if not _NUM.match(t):
            return None
        try:
            out.append(float(t.replace("d", "e").replace("D", "e")))
        except ValueError:
            return None
    return out or None


def ev_numeric(ref: str | None, cand: str | None) -> dict | None:
    if ref is None or cand is None:
        return None
    a, b = _floats(ref), _floats(cand)
    if a is None or b is None:
        return None
    ev: dict = {"ref_n": len(a), "cand_n": len(b)}
    if len(a) != len(b):
        ev["same_length"] = False
        return ev
    ev["same_length"] = True
    rels, ratios = [], []
    for x, y in zip(a, b):
        d = max(abs(x), abs(y))
        rels.append(0.0 if d == 0 else abs(x - y) / d)
        if x != 0 and y != 0:
            ratios.append(y / x)
    ev["max_rel_diff"] = max(rels)
    ev["identical_after_normalisation"] = max(rels) <= 1e-9
    if ratios:
        ev["ratio_cand_over_ref"] = ratios[0] if len(ratios) == 1 else [round(r, 6) for r in ratios[:6]]
        mags = [abs(math.log10(abs(r))) for r in ratios if r != 0]
        if mags:
            ev["max_orders_of_magnitude"] = round(max(mags), 3)
        ev["sign_flip"] = any(r < 0 for r in ratios)
    return ev


def ev_format(ref: str | None, cand: str | None) -> bool | None:
    if ref is None or cand is None:
        return None
    norm = lambda s: re.sub(r"\s+", "", s).strip().lower()  # noqa: E731
    if norm(ref) == norm(cand):
        return True
    norm2 = lambda s: re.sub(r"[{}\s]+", "", s).strip().lower()  # noqa: E731
    return norm2(ref) == norm2(cand)


# --------------------------------------------------------------------------
# EV4 — identifier definition + usage counts
# --------------------------------------------------------------------------

def deck_index(root: ET.Element) -> dict:
    names, tokens = Counter(), Counter()
    by_tag: dict[str, list[ET.Element]] = defaultdict(list)
    paths: dict[int, str] = {}

    def walk(e: ET.Element, path: str):
        paths[id(e)] = path
        by_tag[e.tag].append(e)
        if e.get("name"):
            names[e.get("name")] += 1
        for k, v in e.attrib.items():
            for t in TOKEN_SPLIT.split(v or ""):
                t = t.strip()
                if t:
                    tokens[t] += 1
        for c in e:
            if isinstance(c.tag, str):
                walk(c, f"{path}/{elem_key(c)}")

    walk(root, "")
    return {"names": names, "tokens": tokens, "by_tag": by_tag, "paths": paths}


def ev_identifier(val: str | None, ref_ix: dict, cand_ix: dict) -> dict | None:
    if not val:
        return None
    toks = [t for t in TOKEN_SPLIT.split(val.strip()) if t and IDENT_RE.match(t)]
    toks = [t for t in toks if not _NUM.match(t)]
    if not toks:
        return None
    out = []
    for t in toks[:4]:
        base = t.split("/")[-1]
        out.append({
            "token": t,
            "defined_as_name_in_reference": ref_ix["names"].get(base, 0),
            "defined_as_name_in_candidate": cand_ix["names"].get(base, 0),
            "mentions_in_reference": ref_ix["tokens"].get(t, 0),
            "mentions_in_candidate": cand_ix["tokens"].get(t, 0),
        })
    return {"tokens": out} if out else None


# --------------------------------------------------------------------------
# EV5 — external data files (blind spot 1)
# --------------------------------------------------------------------------

def ev_files(val: str | None, attr: str | None, deck_dir: Path, other_dir: Path) -> list | None:
    if not val:
        return None
    cands = set(FILE_RE.findall(val))
    if attr in FILE_ATTRS:
        cands |= {t for t in TOKEN_SPLIT.split(val.strip()) if t and "/" in t or (t and "." in t)}
    cands = {c for c in cands if c and not _NUM.match(c)}
    if not cands:
        return None
    out = []
    for c in sorted(cands)[:4]:
        rec: dict = {"ref_path": c}
        hit = None
        p = Path(c)
        for base in (deck_dir, deck_dir.parent):
            q = (base / c) if not p.is_absolute() else p
            if q.exists():
                hit = q
                break
        if hit is None:
            # last resort: basename anywhere under the deck dir
            m = list(deck_dir.rglob(p.name))
            hit = m[0] if m else None
        rec["exists_in_this_deck"] = hit is not None
        if hit is not None and hit.is_file():
            rec["bytes"] = hit.stat().st_size
            if hit.suffix.lower() in (".geos", ".txt", ".csv", ".dat", ".table") and rec["bytes"] < 400_000:
                try:
                    nums = _floats(re.sub(r"[\n\r]+", " ", hit.read_text(errors="replace")))
                    if nums:
                        rec["n_values"] = len(nums)
                        rec["min"], rec["max"] = min(nums), max(nums)
                        rec["first"] = nums[:4]
                except Exception:  # noqa: BLE001
                    pass
        # does the OTHER deck have a file of this basename?
        rec["basename_present_in_other_deck"] = bool(list(other_dir.rglob(p.name))) if other_dir.exists() else False
        out.append(rec)
    return out or None


# --------------------------------------------------------------------------
# EV6 — global counterpart search (blind spot 2)
# --------------------------------------------------------------------------

SIGNATURE_KEYS = ("fieldName", "objectPath", "component", "setNames", "target",
                  "targetRegions", "phaseNames", "solverType", "flowSolverName")


def ev_counterparts(ev: dict, cand_ix: dict, ref_ix: dict) -> dict | None:
    """For a reference element TreeSim called missing, search the WHOLE candidate
    tree for same-tag elements. TreeSim's matcher only looks at same-tag siblings
    under an already-matched parent, so this is information TreeSim cannot have."""
    if ev["kind"] == "missing_element":
        pool, ix, side = cand_ix["by_tag"].get(ev["tag"], []), cand_ix, "candidate"
        target = ev.get("ref_attrs") or {}
    elif ev["kind"] == "extra_element":
        pool, ix, side = ref_ix["by_tag"].get(ev["tag"], []), ref_ix, "reference"
        target = ev.get("cand_attrs") or {}
    else:
        return None
    out = {"searched_side": side, f"n_same_tag_in_{side}": len(pool)}
    shown = []
    scored = []
    for e in pool:
        share = sum(1 for k in SIGNATURE_KEYS
                    if k in target and e.get(k) is not None and e.get(k) == target[k])
        namehit = 1 if (target.get("name") and e.get("name") == target["name"]) else 0
        scored.append((namehit * 10 + share, e))
    scored.sort(key=lambda x: -x[0])
    for sc, e in scored[:6]:
        shown.append({"path": ix["paths"].get(id(e), "?"), "attrs": dict(e.attrib),
                      "signature_attrs_shared_with_this_element": sc % 10,
                      "same_name": bool(sc >= 10)})
    out["same_tag_elements_found"] = shown
    return out


# --------------------------------------------------------------------------
# Card rendering
# --------------------------------------------------------------------------

def section_of(path: str) -> str:
    parts = [p for p in path.split("/") if p]
    for p in parts:
        base = p.split("[")[0]
        if base in TOP_SECTIONS:
            return base
    return parts[0].split("[")[0] if parts else "?"


def _j(o) -> str:
    return json.dumps(o, default=str)


def render_card(ev: dict, order: str = "A") -> str:
    L = [f"ITEM {ev['item_id']}   kind={ev['kind']}   section=<{ev['section']}>",
         f"  enclosing element : <{ev['tag']}" +
         (f" name=\"{ev.get('ref_name') or ev.get('cand_name')}\"" if (ev.get('ref_name') or ev.get('cand_name')) else "") + ">",
         f"  enclosing element attributes : "
         f"{_j(ev.get('ref_attrs') or ev.get('cand_attrs'))[:600]}"]
    if ev["kind"].startswith("attr"):
        L.append(f"  attribute         : {ev['attr']}")
        # POSITION CONTROL: order A prints REFERENCE first, order B prints CANDIDATE
        # first. Both are explicitly labelled -- the judge must know which side is the
        # reference; the control is for prompt-position primacy/recency only.
        vlines = [f"  REFERENCE value   : {ev.get('ref_value')!r}",
                  f"  CANDIDATE value   : {ev.get('cand_value')!r}"]
        L.extend(vlines if order == "A" else vlines[::-1])
        if ev["kind"] == "attr_ref_only":
            L.append("  (the attribute is present in the reference and ABSENT from the candidate;")
            L.append("   an absent attribute takes the GEOS schema default shown below, if any)")
        if ev["kind"] == "attr_cand_only":
            L.append("  (the attribute is present in the candidate and ABSENT from the reference;")
            L.append("   the reference therefore uses the GEOS schema default shown below, if any)")
    elif ev["kind"] == "missing_element":
        L.append("  the structural metric found NO counterpart for this reference element and")
        L.append("  scored it, and its entire subtree, as zero.")
        L.append(f"  REFERENCE element attributes : {_j(ev.get('ref_attrs'))}")
    elif ev["kind"] == "extra_element":
        L.append("  this element is in the candidate with no counterpart in the reference;")
        L.append("  the structural metric applies a hallucination penalty for it.")
        L.append(f"  CANDIDATE element attributes : {_j(ev.get('cand_attrs'))}")

    e = ev.get("evidence", {})
    L.append("  --- ESTABLISHED FACTS (computed from the files, not inferred) ---")
    if e.get("format_equivalent"):
        L.append("  * The two strings are IDENTICAL after removing whitespace and braces.")
    n = e.get("numeric")
    if n:
        if n.get("identical_after_normalisation"):
            L.append("  * The two values are NUMERICALLY IDENTICAL (max relative difference < 1e-9);")
            L.append("    the structural metric flagged them only because of text formatting.")
        elif n.get("same_length") is False:
            L.append(f"  * Numeric lists of DIFFERENT LENGTH: reference {n['ref_n']}, candidate {n['cand_n']}.")
        else:
            L.append(f"  * Max relative difference {n['max_rel_diff']:.4g}"
                     + (f"; candidate/reference ratio {n['ratio_cand_over_ref']}" if "ratio_cand_over_ref" in n else "")
                     + (f"; up to {n['max_orders_of_magnitude']} orders of magnitude" if "max_orders_of_magnitude" in n else "")
                     + ("; SIGN IS FLIPPED" if n.get("sign_flip") else "") + ".")
    s = e.get("schema")
    if s:
        if s.get("default") is not None:
            L.append(f"  * GEOS schema default for {ev.get('attr')} on <{ev['tag']}> is {s['default']!r}."
                     + (" CANDIDATE value EQUALS the schema default." if s.get("cand_is_default") else "")
                     + (" REFERENCE value EQUALS the schema default." if s.get("ref_is_default") else ""))
        else:
            L.append(f"  * GEOS schema declares {ev.get('attr')} on <{ev['tag']}> with NO default"
                     + (" and marks it REQUIRED." if s.get("required") else "."))
    for label, key in (("REFERENCE value", "ident_ref"), ("CANDIDATE value", "ident_cand")):
        iv = e.get(key)
        if not iv:
            continue
        for t in iv["tokens"]:
            L.append(f"  * {label} token {t['token']!r}: defined as an element name "
                     f"{t['defined_as_name_in_reference']}x in the reference / "
                     f"{t['defined_as_name_in_candidate']}x in the candidate; referenced "
                     f"{t['mentions_in_reference']}x in the reference / "
                     f"{t['mentions_in_candidate']}x in the candidate.")
    # NOTE: external-data-file evidence (EV5) is deliberately NOT rendered into the
    # scoring card. Soft-TreeSim must inherit TreeSim's information set exactly, so
    # that the TreeSim -> soft-TreeSim delta is attributable to the value predicate
    # alone. EV5 is computed and stored on the item, and is reported separately as a
    # zero-LLM diagnostic (see J1_analyse.py, blind-spot 1).
    if len(L) and L[-1].endswith("---"):
        L.append("  (none)")
    return "\n".join(L)


# --------------------------------------------------------------------------

def treesim_of_record() -> dict:
    """Per-deck TreeSim from _summary.json -> results[]. Never globs *_eval.json."""
    out = {}
    for cell, cdir in CELLS.items():
        for seed in SEEDS:
            summ = RESULTS / f"{cell}_icl_s{seed}" / cdir / "_summary.json"
            if not summ.exists():
                continue
            for r in json.load(summ.open())["results"]:
                task = r.get("experiment") or r.get("task") or r.get("name")
                out[f"{cell}_s{seed}_{task}"] = {
                    "treesim": r.get("treesim"), "status": r.get("status"),
                }
    return out


def build_variant(gt_root, gen_root, gt_dir: Path, gen_dir: Path,
                  ref_ix: dict, cand_ix: dict, soft_match: bool) -> dict:
    """One rung of the ladder. `soft_match=False` reproduces TreeSim's pairing."""
    inst = tree_sim_credited(gt_root, gen_root, soft_match=soft_match)
    out = {"treesim_recomputed": round(inst.score, 6), "soft_match": soft_match}
    # ceiling: every softenable (i.e. attribute-level) event at full credit
    attr_eids = {e.eid for e in inst.events if e.kind.startswith("attr")}
    out["ceiling_soft_values"] = round(
        tree_sim_credited(gt_root, gen_root, {e: 1.0 for e in attr_eids},
                          soft_match=soft_match).score, 6)
    items = []
    for i, e in enumerate(inst.events, 1):
        d = e.to_dict()
        d["item_id"] = f"I{i:04d}"
        d["section"] = section_of(e.path)
        # ------------------------------------------------------------------
        # ONLY attribute-level events are judged. Element pairing stays a
        # deterministic property of TreeSim (rung 1) or of the soft matcher
        # (rung 2). This is the coordinator's "soften scoring, keep matching
        # hard" requirement, and it also removes from the model's remit the
        # exact item kind on which v1's judges agreed only 2.6 % of the time
        # (`missing_element`) -- those are search problems, not physics.
        # ------------------------------------------------------------------
        d["judged"] = e.kind.startswith("attr")
        ev: dict = {}
        if d["judged"]:
            if ev_format(e.ref_value, e.cand_value):
                ev["format_equivalent"] = True
            n = ev_numeric(e.ref_value, e.cand_value)
            if n:
                ev["numeric"] = n
            sc = SCHEMA.get(e.tag, {}).get(e.attr)
            if sc:
                sd = dict(sc)
                if sd.get("default") is not None:
                    sd["cand_is_default"] = ev_format(sd["default"], e.cand_value) is True
                    sd["ref_is_default"] = ev_format(sd["default"], e.ref_value) is True
                ev["schema"] = sd
            if e.attr == "name" or e.attr in REF_ATTRS:
                a = ev_identifier(e.ref_value, ref_ix, cand_ix)
                b = ev_identifier(e.cand_value, ref_ix, cand_ix)
                if a:
                    ev["ident_ref"] = a
                if b:
                    ev["ident_cand"] = b
            # EV5 stored but NOT rendered into the card (see render_card)
            fr = ev_files(e.ref_value, e.attr, gt_dir, gen_dir)
            fc = ev_files(e.cand_value, e.attr, gen_dir, gt_dir)
            if fr:
                ev["files_ref"] = fr
            if fc:
                ev["files_cand"] = fc
        else:
            cp = ev_counterparts(d, cand_ix, ref_ix)
            if cp:
                ev["counterparts"] = cp
        d["evidence"] = ev
        if d["judged"]:
            d["card"] = render_card(d, "A")
            d["card_B"] = render_card(d, "B")
            # Cache key: the full card text, which is exactly the information the
            # judge is shown. Two items with the same key are indistinguishable to
            # the model, so one call answers both -- this both cuts cost and makes
            # identical substitutions score identically by construction.
            d["cache_key"] = hashlib.sha256(
                re.sub(r"^ITEM \S+ ", "ITEM ", d["card"]).encode()).hexdigest()[:24]
            # narrow key the coordinator asked for, reported alongside
            d["tuple_key"] = hashlib.sha256(
                json.dumps([e.tag, e.attr, e.ref_value, e.cand_value],
                           default=str).encode()).hexdigest()[:24]
        items.append(d)
    out["items"] = items
    out["n_items"] = len(items)
    out["n_judged"] = sum(1 for i in items if i["judged"])
    return out


def build_deck(cell: str, seed: int, task: str, tsrec: dict) -> dict:
    did = f"{cell}_s{seed}_{task}"
    gen_dir = ICL / CELLS[cell] / f"{cell}_icl_s{seed}" / task / "inputs"
    gt_dir = GT / task / "inputs"
    rec = {"deck_id": did, "cell": cell, "seed": seed, "task": task,
           "gen_dir": str(gen_dir), "gt_dir": str(gt_dir),
           "treesim_of_record": tsrec.get(did, {}).get("treesim"),
           "run_status": tsrec.get(did, {}).get("status")}
    try:
        gt_root = load_and_resolve_dir(gt_dir)
        gen_root = load_and_resolve_dir(gen_dir)
    except Exception as exc:  # noqa: BLE001
        rec.update({"rung1_fail": True, "rung1_reason": f"{type(exc).__name__}: {exc}",
                    "variants": {}})
        return rec
    rec["rung1_fail"] = False
    ref_ix, cand_ix = deck_index(gt_root), deck_index(gen_root)
    rec["variants"] = {
        "hard": build_variant(gt_root, gen_root, gt_dir, gen_dir, ref_ix, cand_ix, False),
        "soft": build_variant(gt_root, gen_root, gt_dir, gen_dir, ref_ix, cand_ix, True),
    }
    rec["treesim_recomputed"] = rec["variants"]["hard"]["treesim_recomputed"]
    # rung R2a: hard values + soft matching (deterministic, no model)
    rec["treesim_softmatch_hardvalues"] = rec["variants"]["soft"]["treesim_recomputed"]
    return rec


def add_weights(rec: dict, cap: int) -> None:
    """No-op. Structural weights d(score)/d(credit) are now produced analytically
    during the traversal (J1_treesim carries the chain of alpha / (1-alpha) / 1/n_gt
    multipliers). Verified against exact finite differences: max abs deviation
    7.9e-17 over all events of a real deck, both matching modes."""
    return


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--cells", nargs="*", default=None)
    ap.add_argument("--seeds", nargs="*", type=int, default=None)
    ap.add_argument("--tasks", nargs="*", default=None)
    ap.add_argument("--weight-cap", type=int, default=80)
    a = ap.parse_args()

    tsrec = treesim_of_record()
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with out.open("w") as fh:
        for cell in (a.cells or CELLS):
            for seed in (a.seeds or SEEDS):
                for task in (a.tasks or TASKS):
                    rec = build_deck(cell, seed, task, tsrec)
                    add_weights(rec, a.weight_cap)
                    fh.write(json.dumps(rec, default=str) + "\n")
                    n += 1
                    v = rec.get("variants", {}).get("hard", {})
                    vs = rec.get("variants", {}).get("soft", {})
                    print(f"{rec['deck_id']:66} "
                          f"ts={rec.get('treesim_recomputed')} "
                          f"(rec {rec.get('treesim_of_record')}) "
                          f"judged={v.get('n_judged')}/{v.get('n_items')} "
                          f"ceil={v.get('ceiling_soft_values')} | "
                          f"softmatch ts={vs.get('treesim_recomputed')} "
                          f"judged={vs.get('n_judged')}/{vs.get('n_items')}"
                          + ("  RUNG1-FAIL" if rec.get("rung1_fail") else ""), flush=True)
    print(f"\nwrote {n} decks -> {out}")


if __name__ == "__main__":
    main()
