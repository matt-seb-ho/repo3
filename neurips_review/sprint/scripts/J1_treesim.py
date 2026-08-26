#!/usr/bin/env python3
"""
Thread J1 — instrumented, credit-substitutable TreeSim.

Mirrors `src/eval/judge_geos.tree_sim` EXACTLY, but

  (a) emits one addressable SCORING EVENT for every place TreeSim assigns zero
      credit (a non-equivalent / one-sided attribute, an unmatched reference
      child, an extra candidate child), and
  (b) accepts a `credit` mapping event_id -> c in [0,1] that replaces that zero.

`credit = {}` (all zeros) must reproduce the published TreeSim score exactly.
That equality is the correctness test (`--verify`), and it is what makes the
judge metric a *repair of TreeSim on TreeSim's own scale* rather than a
free-floating LLM opinion.

Substitution semantics (frozen with the rubric):
  attribute event   : attr_similarity = (n_exact_match + sum c_k) / |union of keys|
  missing element   : that reference child's child_score = c   (TreeSim: 0.0)
  extra element     : extra_penalty = beta * sum(1 - c_j) / (n_gt + n_extra_raw)
                      (TreeSim: beta * n_extra_raw / (n_gt + n_extra_raw))
"""
from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple

REPO = Path("/home/matt/sci/repo3")
sys.path.insert(0, str(REPO / "src"))
from eval.judge_geos import (  # noqa: E402
    IGNORE_TAGS,
    NUMERIC_RTOL,
    TREESIM_ALPHA,
    TREESIM_BETA,
    _bipartite_match,
    load_and_resolve_dir,
    values_equivalent,
)


# --------------------------------------------------------------------------


def elem_key(e: ET.Element) -> str:
    nm = e.get("name")
    return f"{e.tag}[{nm}]" if nm else e.tag


@dataclass
class Event:
    """One place where TreeSim assigns zero credit."""
    eid: str
    kind: str            # attr_diff | attr_ref_only | attr_cand_only | missing_element | extra_element
    path: str            # address of the enclosing element, from the resolved root
    tag: str
    ref_name: str | None
    cand_name: str | None
    attr: str | None = None
    ref_value: str | None = None
    cand_value: str | None = None
    ref_attrs: Dict[str, str] | None = None
    cand_attrs: Dict[str, str] | None = None
    # structural weight: how much of the final score this event can move
    weight: float = 0.0

    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items() if v is not None}


@dataclass
class Instrumented:
    score: float = 0.0
    events: List[Event] = field(default_factory=list)


# --------------------------------------------------------------------------


def _attr_sim_instrumented(gt: ET.Element, gen: ET.Element, path: str,
                           sink: List[Event], credit: Dict[str, float],
                           rtol: float, counter: List[int], w: float = 0.0) -> float:
    """attr_similarity with per-key events. Identical arithmetic when credit=0."""
    ga, na = dict(gt.attrib), dict(gen.attrib)
    keys = set(ga) | set(na)
    if not keys:
        return 1.0
    total = 0.0
    for k in sorted(keys):
        if k in ga and k in na and values_equivalent(ga[k], na[k], rtol):
            total += 1.0
            continue
        counter[0] += 1
        eid = f"E{counter[0]:05d}"
        if k in ga and k in na:
            kind = "attr_diff"
        elif k in ga:
            kind = "attr_ref_only"
        else:
            kind = "attr_cand_only"
        sink.append(Event(
            eid=eid, kind=kind, path=path, tag=gt.tag,
            ref_name=ga.get("name"), cand_name=na.get("name"),
            attr=k, ref_value=ga.get(k), cand_value=na.get(k),
            ref_attrs=ga, cand_attrs=na, weight=w / len(keys),
        ))
        total += float(credit.get(eid, 0.0))
    return total / len(keys)


def _soft_match(gt_group, gen_group, rtol, soft: bool):
    """Element pairing. `soft=False` is judge_geos._bipartite_match verbatim.

    `soft=True` is LADDER RUNG 2: `_bipartite_match` only records a pair whose
    `compute_element_similarity` is STRICTLY > 0, and that similarity is exactly
    0 whenever a name-less container's attribute sets are disjoint -- so one
    unexpected attribute on an unnamed container (e.g. `gravityVector` on
    <Solvers>, which is GEOS's own schema default) leaves the reference element
    AND ITS WHOLE SUBTREE unpaired and scored 0. Thread B measured this on
    31/90 held-out decks. Soft matching admits zero-similarity same-tag pairs in
    document order after the positive-similarity greedy pass. This is a
    DETERMINISTIC change -- no model is involved.
    """
    matched, un_gt, un_gen = _bipartite_match(gt_group, gen_group, rtol)
    if not soft:
        return matched, un_gt, un_gen
    ug, un = list(un_gt), list(un_gen)
    while ug and un:
        matched.append((ug.pop(0), un.pop(0), 0.0))
    return matched, ug, un


def _tree_sim(gt_node: ET.Element, gen_node: ET.Element, path: str,
              sink: List[Event], credit: Dict[str, float],
              alpha: float, beta: float, rtol: float,
              counter: List[int], soft_match: bool = False, w: float = 1.0) -> float:
    gt_children = [c for c in gt_node if isinstance(c.tag, str) and c.tag not in IGNORE_TAGS]
    gen_children = [c for c in gen_node if isinstance(c.tag, str) and c.tag not in IGNORE_TAGS]
    n_gt = len(gt_children)

    if n_gt == 0 and len(gen_children) == 0:
        # leaf: score is own attribute similarity, scored HERE (not in the parent)
        return _attr_sim_instrumented(gt_node, gen_node, path, sink, credit, rtol, counter, w)

    gt_by_tag: Dict[str, List[ET.Element]] = defaultdict(list)
    gen_by_tag: Dict[str, List[ET.Element]] = defaultdict(list)
    for c in gt_children:
        gt_by_tag[c.tag].append(c)
    for c in gen_children:
        gen_by_tag[c.tag].append(c)
    all_tags = set(gt_by_tag) | set(gen_by_tag)

    child_scores: List[float] = []
    extra_raw = 0
    extra_credit = 0.0

    for tag in sorted(all_tags):
        gt_group = gt_by_tag.get(tag, [])
        gen_group = gen_by_tag.get(tag, [])
        matched, unmatched_gt, unmatched_gen = _soft_match(gt_group, gen_group, rtol, soft_match)

        for gi, gj, _sim in matched:
            gt_elem, gen_elem = gt_group[gi], gen_group[gj]
            cpath = f"{path}/{elem_key(gt_elem)}"
            gt_grand = [c for c in gt_elem if isinstance(c.tag, str) and c.tag not in IGNORE_TAGS]
            if gt_grand:
                a_score = _attr_sim_instrumented(gt_elem, gen_elem, cpath, sink, credit,
                                                 rtol, counter, w * alpha / n_gt)
                subtree = _tree_sim(gt_elem, gen_elem, cpath, sink, credit,
                                    alpha, beta, rtol, counter, soft_match,
                                    w * (1 - alpha) / n_gt)
                child_scores.append(alpha * a_score + (1 - alpha) * subtree)
            else:
                # Reference child is a LEAF. judge_geos branches on the *reference*
                # side only (`if gt_grandchildren:`), so child_score = a_score even
                # when the CANDIDATE counterpart has children. Must not recurse here:
                # recursing would take the n_gt==0 grouping branch and return a flat
                # 0.9. This is what made TutorialHydraulicFractureWithAdvancedXML
                # disagree by 2e-4 on the first --verify pass.
                child_scores.append(
                    _attr_sim_instrumented(gt_elem, gen_elem, cpath, sink, credit,
                                           rtol, counter, w / n_gt))

        for idx in unmatched_gt:
            e = gt_group[idx]
            counter[0] += 1
            eid = f"E{counter[0]:05d}"
            sink.append(Event(
                eid=eid, kind="missing_element", path=f"{path}/{elem_key(e)}", tag=e.tag,
                ref_name=e.get("name"), cand_name=None,
                ref_attrs=dict(e.attrib), cand_attrs=None, weight=w / n_gt,
            ))
            child_scores.append(float(credit.get(eid, 0.0)))

        for idx in unmatched_gen:
            e = gen_group[idx]
            counter[0] += 1
            eid = f"E{counter[0]:05d}"
            sink.append(Event(
                eid=eid, kind="extra_element", path=f"{path}/{elem_key(e)}", tag=e.tag,
                ref_name=None, cand_name=e.get("name"),
                ref_attrs=None, cand_attrs=dict(e.attrib),
            ))
            extra_raw += 1
            extra_credit += float(credit.get(eid, 0.0))

    matched_score = (sum(child_scores) / n_gt) if n_gt > 0 else 1.0
    denom = n_gt + extra_raw
    extra_penalty = beta * ((extra_raw - extra_credit) / denom) if denom > 0 else 0.0
    return max(0.0, min(1.0, matched_score - extra_penalty))


# The top-level `_tree_sim(root, root)` leaf branch is unreachable for real decks
# (a <Problem> always has children); it exists only for symmetry. Every reference
# element's attributes are therefore scored exactly once, in its parent's frame,
# and the ROOT's own attributes are never scored -- matching judge_geos.


def tree_sim_credited(gt_root: ET.Element, gen_root: ET.Element,
                      credit: Dict[str, float] | None = None,
                      alpha: float = TREESIM_ALPHA, beta: float = TREESIM_BETA,
                      rtol: float = NUMERIC_RTOL,
                      soft_match: bool = False) -> Instrumented:
    sink: List[Event] = []
    counter = [0]
    score = _tree_sim(gt_root, gen_root, "", sink, credit or {}, alpha, beta, rtol,
                      counter, soft_match)
    # structural weight of each event: numerical d(score)/d(credit), by finite difference
    return Instrumented(score=score, events=sink)


def event_weights(gt_root: ET.Element, gen_root: ET.Element,
                  eids: List[str], base: float,
                  credit: Dict[str, float] | None = None) -> Dict[str, float]:
    """d(score)/d(credit_e) for each event, by exact finite difference (linear in c)."""
    out = {}
    base_credit = dict(credit or {})
    for e in eids:
        c = dict(base_credit)
        c[e] = 1.0
        out[e] = tree_sim_credited(gt_root, gen_root, c).score - base
    return out


# --------------------------------------------------------------------------

def _verify():
    """credit={} must reproduce the published TreeSim score for every held-out deck."""
    import json
    ICL = Path("/data/shared/geophysics_agent_data/data/eval/autocamp_followup_2026-05-02/icl")
    GT = Path("/data/shared/geophysics_agent_data/data/eval/experiments_gt")
    RES = Path("/data/shared/geophysics_agent_data/data/eval/autocamp_followup_2026-05-02/_results_icl")
    cells = {"F0": "autocamp_F0", "F6": "autocamp_F6", "SE": "autocamp_SE"}
    ok = bad = skip = 0
    worst = 0.0
    for cell, cdir in cells.items():
        for seed in (1, 2, 3):
            summ = RES / f"{cell}_icl_s{seed}" / cdir / "_summary.json"
            if not summ.exists():
                print(f"  !! no _summary.json for {cell}_s{seed}: {summ}")
                continue
            for r in json.load(summ.open())["results"]:
                task = r.get("experiment") or r.get("task") or r.get("name")
                pub = r.get("treesim")
                gen = ICL / cdir / f"{cell}_icl_s{seed}" / task / "inputs"
                gtd = GT / task / "inputs"
                if pub is None or not gen.exists():
                    skip += 1
                    print(f"  -- skip {cell}_s{seed}_{task}: treesim={pub} exists={gen.exists()}")
                    continue
                try:
                    g = load_and_resolve_dir(gtd)
                    c = load_and_resolve_dir(gen)
                except Exception as exc:  # noqa: BLE001
                    skip += 1
                    print(f"  -- skip {cell}_s{seed}_{task}: {type(exc).__name__}")
                    continue
                got = tree_sim_credited(g, c).score
                d = abs(round(got, 4) - float(pub))
                worst = max(worst, d)
                if d <= 1e-4:
                    ok += 1
                else:
                    bad += 1
                    print(f"  MISMATCH {cell}_s{seed}_{task}: published={pub} instrumented={got:.6f}")
    print(f"\nverify: ok={ok} mismatch={bad} skipped={skip} worst_abs_diff={worst:.2e}")
    return bad == 0


if __name__ == "__main__":
    if "--verify" in sys.argv:
        sys.exit(0 if _verify() else 1)
    print(__doc__)
