#!/usr/bin/env python3
"""
Thread B — LMaaJ secondary metric. Prompt construction.

Builds, for each (cell, seed, task) held-out deck, a blinded judge prompt containing:
  1. the natural-language task brief
  2. the reference deck (raw XML)
  3. the candidate deck (raw XML)
  4. the TreeSim mismatch report (computed on the RESOLVED trees via judge_geos.match_trees)

Rubric: neurips_review/sprint/artifacts/B_rubric_v1.md (frozen 2026-07-26T22:14:00+00:00).
No cell name, seed, or filesystem path reaches the prompt.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

REPO = Path("/home/matt/sci/repo3")
sys.path.insert(0, str(REPO / "src"))
from eval.judge_geos import (  # noqa: E402
    load_and_resolve_dir,
    match_trees,
    NUMERIC_RTOL,
)

ICL = Path("/data/shared/geophysics_agent_data/data/eval/autocamp_followup_2026-05-02/icl")
RESULTS = Path("/data/shared/geophysics_agent_data/data/eval/autocamp_followup_2026-05-02/_results_icl")
GT = Path("/data/shared/geophysics_agent_data/data/eval/experiments_gt")
SPECS = Path("/data/shared/geophysics_agent_data/data/eval/experiments_from_mined_specs")

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

DECK_CHAR_CAP = 26000       # per deck, raw XML
MISMATCH_CAP = 90           # entries shown to the judge


# --------------------------------------------------------------------------
# Blinding
# --------------------------------------------------------------------------

_PATH_PAT = re.compile(
    r"(/[\w./-]*(?:geophysics_agent_data|autocamp|experiments_gt|sci/repo3|workspace)[\w./-]*)"
)
_CELL_PAT = re.compile(r"\b(autocamp_(?:F\d+|SE)|F\d+_icl_s\d|SE_icl_s\d)\b")


def blind(text: str) -> str:
    """Strip filesystem paths and cell/seed identifiers."""
    text = _PATH_PAT.sub("<path>", text)
    text = _CELL_PAT.sub("<cond>", text)
    return text


# --------------------------------------------------------------------------
# Deck rendering
# --------------------------------------------------------------------------

def render_deck(inputs_dir: Path) -> tuple[str, bool, list[str]]:
    """Raw XML text of every *.xml in inputs_dir. Returns (text, truncated, files)."""
    files = sorted(inputs_dir.glob("*.xml"))
    chunks, names = [], []
    total = 0
    truncated = False
    for f in files:
        body = f.read_text(errors="replace")
        names.append(f.name)
        room = DECK_CHAR_CAP - total
        if room <= 0:
            truncated = True
            break
        if len(body) > room:
            body = body[:room] + "\n<!-- ... TRUNCATED ... -->"
            truncated = True
        total += len(body)
        chunks.append(f"----- FILE: {f.name} -----\n{body}")
    return "\n\n".join(chunks), truncated, names


# --------------------------------------------------------------------------
# TreeSim mismatch report
# --------------------------------------------------------------------------

def _elem_label(e: ET.Element) -> str:
    nm = e.get("name")
    return f"<{e.tag}{f' name={nm!r}' if nm else ''}>"


def build_mismatch_report(gt_dir: Path, gen_dir: Path) -> dict:
    """Every attribute TreeSim scored non-equivalent + unmatched/extra elements.

    Computed on the resolved trees, exactly as TreeSim sees them.
    """
    gt_root = load_and_resolve_dir(gt_dir)
    gen_root = load_and_resolve_dir(gen_dir)
    m = match_trees(gt_root, gen_root, NUMERIC_RTOL)

    entries = []
    for d in m.attr_details:
        if not d["mismatches"]:
            continue
        ctx = f"<{d['gt_tag']}"
        if d["gt_name"] or d["gen_name"]:
            ctx += f" name: REFERENCE={d['gt_name']!r} CANDIDATE={d['gen_name']!r}"
        ctx += ">"
        for raw in d["mismatches"]:
            # judge_geos emits "key: GT='a' GEN='b'" / "key: missing in GEN" / "key: extra in GEN"
            txt = (raw.replace("GT=", "REFERENCE=")
                      .replace("GEN=", "CANDIDATE=")
                      .replace("missing in CANDIDATE=", "missing in CANDIDATE")
                      .replace("missing in GEN", "present in REFERENCE, absent in CANDIDATE")
                      .replace("extra in GEN", "absent in REFERENCE, present in CANDIDATE"))
            entries.append({"kind": "attribute", "element": ctx, "detail": txt})

    # ------------------------------------------------------------------
    # Reconcile the unmatched lists before reporting.
    #
    # TreeSim's `_bipartite_match` only records pairs whose similarity is
    # strictly > 0, and `compute_element_similarity` returns exactly 0 whenever a
    # name-less container's attribute sets are disjoint. The two elements are then
    # BOTH reported as unmatched even though a counterpart plainly exists. Emitting
    # those as "no counterpart in CANDIDATE" would feed the judge a false premise
    # (verified in the smoketest: it drove one judge to label 20/25 entries
    # `severe` for elements that were present). So: pair up unmatched reference and
    # candidate elements that share a tag (and a `name`, when both have one), and
    # report each such case once, showing both sides.
    # ------------------------------------------------------------------
    gen_pool = list(m.gen_unmatched)

    def _take(e: ET.Element) -> ET.Element | None:
        for require_name in (True, False):
            for i, c in enumerate(gen_pool):
                if c.tag != e.tag:
                    continue
                if require_name and (e.get("name") or "") != (c.get("name") or ""):
                    continue
                return gen_pool.pop(i)
        return None

    for e in m.gt_unmatched:
        twin = _take(e)
        if twin is None:
            entries.append({
                "kind": "missing_element",
                "element": _elem_label(e),
                "detail": "present in REFERENCE, no counterpart of this tag in CANDIDATE; "
                          f"REFERENCE attributes: {json.dumps(dict(e.attrib))}",
            })
        else:
            entries.append({
                "kind": "unpaired_same_tag",
                "element": _elem_label(e),
                "detail": ("the structural metric failed to PAIR these two elements, so it scored "
                           "the reference one (and its whole subtree) as absent — but an element of "
                           "the same tag does exist in the CANDIDATE. Judge whether they are the "
                           "same thing. "
                           f"REFERENCE attributes: {json.dumps(dict(e.attrib))} ;; "
                           f"CANDIDATE attributes: {json.dumps(dict(twin.attrib))}"),
            })
    for e in gen_pool:
        entries.append({
            "kind": "extra_element",
            "element": _elem_label(e),
            "detail": "present in CANDIDATE, no counterpart of this tag in REFERENCE; "
                      f"CANDIDATE attributes: {json.dumps(dict(e.attrib))}",
        })

    for i, e in enumerate(entries, 1):
        e["id"] = f"M{i:03d}"
    return {
        "entries": entries,
        "n_total": len(entries),
        "n_paired_elements": len(m.paired),
        "n_ref_unmatched": len(m.gt_unmatched),
        "n_cand_extra": len(m.gen_unmatched),
        "n_unpaired_same_tag": sum(1 for e in entries if e["kind"] == "unpaired_same_tag"),
    }


def render_mismatch_report(rep: dict) -> tuple[str, int]:
    ent = rep["entries"]
    shown = ent[:MISMATCH_CAP]
    lines = [
        f"The structural metric paired {rep['n_paired_elements']} elements and left "
        f"{rep['n_ref_unmatched']} reference elements unmatched.",
        f"It flagged {rep['n_total']} differences in total"
        + (f"; the {len(shown)} listed below are a prefix of that list." if len(shown) < len(ent)
           else "; all are listed below."),
        "",
        "Entry kinds:",
        "  attribute         - both elements were paired; this attribute's value differed, or was "
        "present on only one side.",
        "  unpaired_same_tag - the metric FAILED TO PAIR a reference element with a candidate "
        "element of the same tag, and therefore scored the reference element and its entire "
        "subtree as absent. An element of that tag does exist in the candidate. Both attribute "
        "sets are shown; decide for yourself whether they are the same thing. Note that the "
        "metric's own failure to pair is not itself a defect of the candidate deck.",
        "  missing_element   - present in the reference, no element of that tag anywhere in the "
        "candidate.",
        "  extra_element     - present in the candidate, no element of that tag in the reference.",
        "",
        "Elements may appear in a different FILE in the candidate than in the reference. Both decks "
        "are resolved as a single problem before comparison, so a relocated element is not a "
        "functional difference.",
        "",
    ]
    for e in shown:
        lines.append(f"[{e['id']}] ({e['kind']}) {e['element']}  ::  {e['detail']}")
    return "\n".join(lines), len(shown)


# --------------------------------------------------------------------------
# Prompt assembly
# --------------------------------------------------------------------------

SYSTEM = """You are a computational geomechanics and reservoir-simulation expert reviewing GEOS \
XML input decks. GEOS is an open-source multiphysics simulator for subsurface problems \
(poromechanics, thermo-poro-elasticity, multiphase flow, hydraulic fracturing).

You are being used as a measurement instrument. A structural metric has already compared a \
CANDIDATE deck against a REFERENCE deck by exact attribute-value equality (relative tolerance \
1e-6). That metric cannot tell whether a flagged difference is physically trivial or \
catastrophic: it scores a permeability that is wrong by a factor of two and one that is wrong by \
eighteen orders of magnitude identically, and it scores purely cosmetic differences \
(whitespace inside a list, a renamed but consistently used region, an equivalent unit \
expression) as total failures.

Your job is to supply exactly that missing dimension. Do not re-score structure. Do not reward \
or penalise verbosity, comments, or formatting style. Judge physics and magnitude.

Reply with a single JSON object and nothing else. No markdown fences, no commentary."""

RUBRIC_BLOCK = """## Your task

### 1. Classify every flagged difference

For EVERY entry in the DIFFERENCE REPORT, emit one verdict with exactly one severity label:

- "cosmetic"  - no effect on the simulation. Formatting or whitespace differences inside a list,
                a renamed region/field/set that is used consistently throughout the candidate
                deck, an algebraically identical expression, the same physical quantity in
                equivalent units, an output- or logging-only attribute, or an attribute stated
                explicitly at its default value.
- "minor"     - a physically plausible alternative choice. Same order of magnitude and same
                qualitative behaviour: a solver tolerance, a time-step size, a mesh count, or a
                material constant that is within the normal engineering range for the stated
                material. A domain scientist would accept the deck.
- "material"  - changes the simulation meaningfully, but the value is still physically possible.
                A different boundary-condition magnitude, a different but real material, a
                coarser-but-valid discretization, a different solver that would converge
                differently. Results would differ noticeably.
- "severe"    - unphysical, or the wrong physics. Off by orders of magnitude for the stated
                quantity, wrong sign, wrong units by a large factor, a missing element that the
                requested physics cannot run without, or a hallucinated element that would change
                or break the model.

Give a reason of at most 25 words for each. Judge the physics, not the string.

### 2. Rate physical plausibility of the candidate deck's parameter values (0-10)

Judge the CANDIDATE deck on its own physical terms, independently of the reference. Are the
numerical values ones a geomechanics or reservoir engineer would write? Consider densities,
permeabilities, porosities, Young's moduli and Poisson ratios, Biot coefficients, viscosities,
injection rates, thermal conductivities and expansion coefficients, and time scales - are they in
physically sensible ranges and mutually consistent?

  10  every value physically sensible and internally consistent
  7-9 sensible; one or two values at the edge of the plausible range
  4-6 several questionable values, or one clearly wrong by 2-3 orders of magnitude
  1-3 multiple unphysical values, or a value wrong by more than 6 orders of magnitude
  0   no usable physical parameters at all (empty, placeholder, or nonsense values)

### 3. Rate physics-specification fidelity to the brief (0-10)

Does the CANDIDATE deck specify the physics the SIMULATION BRIEF asked for? Judge the requested
governing physics, coupling, constitutive models, boundary and initial conditions, and event
schedule. Do not judge the numbers here, and do not judge style.

  10  all requested physics present, with the right solvers and constitutive models
  7-9 requested physics present; a secondary requested feature missing or weakened
  4-6 core physics present, but a requested coupling, solver, or constitutive model is absent or
      replaced by something qualitatively different
  1-3 a fundamentally different problem is specified
  0   no recognisable physics specification

### Output format

{
  "mismatch_verdicts": [
    {"id": "M001", "severity": "cosmetic|minor|material|severe", "reason": "..."}
  ],
  "plausibility": <integer 0-10>,
  "plausibility_reason": "...",
  "physics_fidelity": <integer 0-10>,
  "physics_fidelity_reason": "...",
  "unphysical_values": ["..."]
}

Emit a verdict for every id in the DIFFERENCE REPORT. JSON only."""


def build_user_prompt(brief: str, ref_deck: str, cand_deck: str,
                      diff_text: str, order: str) -> str:
    ref_block = f"# REFERENCE DECK (the accepted solution)\n\n```xml\n{ref_deck}\n```"
    cand_block = f"# CANDIDATE DECK (the deck under evaluation)\n\n```xml\n{cand_deck}\n```"
    blocks = [ref_block, cand_block] if order == "A" else [cand_block, ref_block]
    return "\n\n".join([
        f"# SIMULATION BRIEF (what was requested)\n\n{brief}",
        *blocks,
        f"# DIFFERENCE REPORT (differences the structural metric flagged)\n\n{diff_text}",
        RUBRIC_BLOCK,
    ])


# --------------------------------------------------------------------------

def iter_decks(cells=None, seeds=None, tasks=None):
    for cell in (cells or CELLS):
        for seed in (seeds or SEEDS):
            for task in (tasks or TASKS):
                yield cell, seed, task


def build_one(cell: str, seed: int, task: str) -> dict:
    gen_dir = ICL / CELLS[cell] / f"{cell}_icl_s{seed}" / task / "inputs"
    gt_dir = GT / task / "inputs"
    brief = (SPECS / task / "instructions.txt").read_text(errors="replace")

    rec = {
        "deck_id": f"{cell}_s{seed}_{task}",
        "cell": cell, "seed": seed, "task": task,
        "gen_dir": str(gen_dir), "gt_dir": str(gt_dir),
    }

    # TreeSim score of record (may be absent -> we recompute / flag)
    ev = RESULTS / f"{cell}_icl_s{seed}" / CELLS[cell] / f"{task}_eval.json"
    if ev.exists():
        rec["treesim"] = json.load(ev.open()).get("treesim")
        rec["treesim_source"] = "eval_json"
    else:
        rec["treesim"] = None
        rec["treesim_source"] = "missing_eval_json"

    if not gen_dir.exists():
        rec["rung1_fail"] = True
        rec["rung1_reason"] = "no inputs directory"
        return rec

    try:
        rep = build_mismatch_report(gt_dir, gen_dir)
    except (ET.ParseError, ValueError, FileNotFoundError) as exc:
        rec["rung1_fail"] = True
        rec["rung1_reason"] = f"{type(exc).__name__}: {exc}"
        if rec["treesim"] is None:
            rec["treesim"] = 0.0
            rec["treesim_source"] = "rung1_fail_floor"
        return rec

    rec["rung1_fail"] = False
    ref_deck, ref_tr, ref_files = render_deck(gt_dir)
    cand_deck, cand_tr, cand_files = render_deck(gen_dir)
    diff_text, n_shown = render_mismatch_report(rep)

    rec.update({
        "n_mismatch_total": rep["n_total"],
        "n_mismatch_shown": n_shown,
        "mismatch_ids": [e["id"] for e in rep["entries"][:MISMATCH_CAP]],
        "mismatch_kinds": {e["id"]: e["kind"] for e in rep["entries"][:MISMATCH_CAP]},
        "ref_truncated": ref_tr, "cand_truncated": cand_tr,
        "ref_files": ref_files, "cand_files": cand_files,
        "n_paired_elements": rep["n_paired_elements"],
        "n_ref_unmatched": rep["n_ref_unmatched"],
        "n_cand_extra": rep["n_cand_extra"],
    })
    for order in ("A", "B"):
        rec[f"prompt_{order}"] = blind(
            build_user_prompt(brief, ref_deck, cand_deck, diff_text, order))
    rec["system"] = SYSTEM
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--cells", nargs="*", default=None)
    ap.add_argument("--seeds", nargs="*", type=int, default=None)
    ap.add_argument("--tasks", nargs="*", default=None)
    a = ap.parse_args()

    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with out.open("w") as fh:
        for cell, seed, task in iter_decks(a.cells, a.seeds, a.tasks):
            rec = build_one(cell, seed, task)
            fh.write(json.dumps(rec) + "\n")
            n += 1
            flag = "RUNG1-FAIL" if rec.get("rung1_fail") else f"{rec.get('n_mismatch_total')} diffs"
            print(f"{rec['deck_id']:70} {flag}")
    print(f"\nwrote {n} records -> {out}")


if __name__ == "__main__":
    main()
