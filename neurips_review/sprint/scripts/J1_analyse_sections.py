#!/usr/bin/env python3
"""
Thread J1 — SECTION-level soft-TreeSim analysis (design C, shipped).

Implements the frozen aggregation of `J1_rubric_v4.md` and evaluates the
pre-registered criteria C1-C4 (VALID) and U1/U2/U4 (USEFUL).

All statistics are implemented in this file (no scipy) so every number is
auditable. Writes `J1_section_analysis.json` and `J1_section_deck_scores.csv`.
"""
from __future__ import annotations

import csv
import json
import math
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean, median, pstdev

REPO = Path("/home/matt/sci/repo3")
ART = REPO / "neurips_review/sprint/artifacts"
sys.path.insert(0, str(REPO / "neurips_review/sprint/scripts"))
from J1_sections import aggregate  # noqa: E402  (TreeSim's own root-frame arithmetic)

JUDGES = ["hy3", "qwen3235b", "gemini3flash", "gpt54mini"]
PRIMARY_PAIR = ["hy3", "qwen3235b"]          # the researcher's instructed pair
LEVELS = ["equivalent", "minor_deviation", "material_deviation", "wrong"]
CREDIT = {"equivalent": 1.0, "minor_deviation": 0.7, "material_deviation": 0.3, "wrong": 0.0}
CREDIT_ALT = {
    "frozen":  {"equivalent": 1.0, "minor_deviation": 0.7, "material_deviation": 0.3, "wrong": 0.0},
    "linear":  {"equivalent": 1.0, "minor_deviation": 2 / 3, "material_deviation": 1 / 3, "wrong": 0.0},
    "binary":  {"equivalent": 1.0, "minor_deviation": 1.0, "material_deviation": 0.0, "wrong": 0.0},
}
ORD = {l: i for i, l in enumerate(LEVELS)}


# ------------------------------ statistics --------------------------------

def pearson(x, y):
    n = len(x)
    if n < 3:
        return None
    mx, my = mean(x), mean(y)
    sx = math.sqrt(sum((a - mx) ** 2 for a in x))
    sy = math.sqrt(sum((b - my) ** 2 for b in y))
    if sx == 0 or sy == 0:
        return None
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / (sx * sy)


def spearman(x, y):
    def rank(v):
        o = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(o):
            j = i
            while j + 1 < len(o) and v[o[j + 1]] == v[o[i]]:
                j += 1
            for k in range(i, j + 1):
                r[o[k]] = (i + j) / 2 + 1
            i = j + 1
        return r
    return pearson(rank(x), rank(y))


def auc(scores, labels):
    pos = [s for s, l in zip(scores, labels) if l == 1]
    neg = [s for s, l in zip(scores, labels) if l == 0]
    if not pos or not neg:
        return None
    t = sum(1.0 if p > q else (0.5 if p == q else 0.0) for p in pos for q in neg)
    return t / (len(pos) * len(neg))


def krippendorff(units, metric="nominal", levels=None):
    vals = levels if levels is not None else sorted({v for u in units for v in u.values()})
    idx = {v: i for i, v in enumerate(vals)}
    K = len(vals)
    if K < 2:
        return None
    o = [[0.0] * K for _ in range(K)]
    n_total = 0.0
    for u in units:
        vs = [v for v in u.values() if v in idx]
        m = len(vs)
        if m < 2:
            continue
        n_total += m
        c = Counter(vs)
        for a in c:
            for b in c:
                o[idx[a]][idx[b]] += (c[a] * c[b] - (c[a] if a == b else 0)) / (m - 1)
    if n_total < 2:
        return None
    nc = [sum(r) for r in o]
    d = (lambda i, j: 0.0 if i == j else 1.0) if metric == "nominal" else (lambda i, j: (i - j) ** 2)
    Do = sum(o[i][j] * d(i, j) for i in range(K) for j in range(K)) / n_total
    De = sum(nc[i] * nc[j] * d(i, j) for i in range(K) for j in range(K)) / (n_total * (n_total - 1))
    return None if De == 0 else 1 - Do / De


def fleiss(units, levels):
    idx = {v: i for i, v in enumerate(levels)}
    rows = []
    for u in units:
        vs = [v for v in u.values() if v in idx]
        if len(vs) < 2:
            continue
        r = [0] * len(levels)
        for v in vs:
            r[idx[v]] += 1
        rows.append(r)
    if not rows:
        return None
    top = max(sum(r) for r in rows)
    rows = [r for r in rows if sum(r) == top]
    n, N = top, len(rows)
    if n < 2 or N == 0:
        return None
    P = [(sum(x * x for x in r) - n) / (n * (n - 1)) for r in rows]
    pj = [sum(r[j] for r in rows) / (N * n) for j in range(len(levels))]
    Pe = sum(p * p for p in pj)
    return None if Pe >= 1 else (mean(P) - Pe) / (1 - Pe)


def gwet_ac1(units, levels):
    """Gwet's AC1. DIAGNOSTIC ONLY -- not part of the frozen criterion.

    Krippendorff's alpha and Fleiss' kappa both estimate chance agreement from the
    observed marginals, so when one category dominates they report near-zero even
    when raters agree almost always (the "kappa paradox" / prevalence problem).
    Here 74-94 % of section verdicts are `equivalent`, exactly that regime. AC1
    replaces the chance term with one that does not blow up under skew, so the two
    together bracket the truth: alpha is the pessimistic bound, AC1 the optimistic.
    """
    idx = {v: i for i, v in enumerate(levels)}
    K = len(levels)
    pa, pis = [], [0.0] * K
    n_units = 0
    for u in units:
        vs = [v for v in u.values() if v in idx]
        m = len(vs)
        if m < 2:
            continue
        n_units += 1
        c = Counter(vs)
        pa.append(sum(c[x] * (c[x] - 1) for x in c) / (m * (m - 1)))
        for x in c:
            pis[idx[x]] += c[x] / m
    if not n_units:
        return None
    pis = [x / n_units for x in pis]
    Pa = mean(pa)
    Pe = sum(pi * (1 - pi) for pi in pis) / (K - 1)
    return None if Pe >= 1 else (Pa - Pe) / (1 - Pe)


def boot_diff(a, b, labels, stat, n=2000, seed=0):
    rng = random.Random(seed)
    N = len(labels)
    try:
        p = stat(a, labels) - stat(b, labels)
    except TypeError:
        return None, None, None
    ds = []
    for _ in range(n):
        ix = [rng.randrange(N) for _ in range(N)]
        la = [labels[i] for i in ix]
        if len(set(la)) < 2:
            continue
        try:
            ds.append(stat([a[i] for i in ix], la) - stat([b[i] for i in ix], la))
        except (TypeError, ZeroDivisionError):
            continue
    ds.sort()
    return (p, ds[int(0.05 * len(ds))], ds[int(0.95 * len(ds))]) if ds else (p, None, None)


# ------------------------------ ground truth ------------------------------

def load_rung3():
    out = {}
    with (ART / "A1_rung3_corrected_by_taskrun.csv").open() as fh:
        for r in csv.DictReader(fh):
            cell = r["cell"].replace("autocamp_", "")
            out[f"{cell}_{r['seed']}_{r['task']}"] = {
                "rung3_lenient": int(r["rung3_lenient"]), "categories": r["categories"]}
    return out


def load_a2():
    lad, qoi = {}, defaultdict(list)
    with (ART / "A2_ladder_per_run.csv").open() as fh:
        for r in csv.DictReader(fh):
            lad[f"{r['cell']}_s{r['seed']}_{r['task']}"] = r
    with (ART / "A2_qoi_per_run.csv").open() as fh:
        for r in csv.DictReader(fh):
            if r.get("rel_error"):
                try:
                    qoi[f"{r['cell']}_s{r['seed']}_{r['task']}"].append(float(r["rel_error"]))
                except ValueError:
                    pass
    return lad, {k: mean(v) for k, v in qoi.items()}


# ------------------------------ aggregation -------------------------------

def cell_table(scores, decks):
    by = defaultdict(lambda: defaultdict(list))
    for did, s in scores.items():
        d = decks[did]
        by[d["cell"]][d["seed"]].append(s)
    out = {}
    for cell, seeds in by.items():
        sm = [mean(v) for _, v in sorted(seeds.items())]
        out[cell] = {"mean": mean(sm), "sd": pstdev(sm) if len(sm) > 1 else 0.0,
                     "seeds": [round(x, 6) for x in sm], "n": sum(len(v) for v in seeds.values())}
    return out


def ranking(t):
    return " > ".join(c for c, _ in sorted(t.items(), key=lambda x: -x[1]["mean"]))


def deck_scores(decks, lv, cmap=CREDIT, judges=JUDGES):
    """Frozen: median credit across judges per unit, then TreeSim's root arithmetic."""
    out, cov = {}, {}
    for did, r in decks.items():
        if r.get("rung1_fail"):
            out[did] = 0.0
            cov[did] = 0.0
            continue
        credits, n_judged, n_present = [], 0, 0
        for s in r["sections"]:
            if not s["present_in_candidate"]:
                credits.append(0.0)                      # TreeSim's verdict, no call made
                continue
            n_present += 1
            got = [cmap[lv[(did, s["unit_id"], j)]] for j in judges
                   if (did, s["unit_id"], j) in lv]
            if got:
                credits.append(median(got))
                n_judged += 1
            else:
                credits.append(s["treesim_section_score"])   # not yet judged: leave TreeSim
        out[did] = aggregate(credits, r["n_ref_sections"], r["n_extra_sections"])
        cov[did] = n_judged / n_present if n_present else 1.0
    return out, cov


# ------------------------------ main --------------------------------------

def main():
    decks = {}
    for l in (ART / "J1_sections.jsonl").open():
        r = json.loads(l)
        decks[r["deck_id"]] = r

    lv = defaultdict(dict)       # (order, rep) -> {(deck, unit, judge): level}
    calls = []
    # Order A / order B / the determinism re-run each write their own file so that
    # no two processes ever append to one file (thread B lost ~$1.70 to two
    # concurrent writers). Dedup on the full key in case a pass was resumed.
    seen = set()
    for path in sorted(ART.glob("J1_sections_raw*.jsonl")):
        for l in path.open():
            try:
                r = json.loads(l)
            except json.JSONDecodeError:
                continue
            k = (r["deck_id"], r["unit_id"], r["judge"], r["order"], r["rep"])
            if k in seen:
                continue
            seen.add(k)
            calls.append(r)
            if r.get("level"):
                lv[(r["order"], r["rep"])][(r["deck_id"], r["unit_id"], r["judge"])] = r["level"]
    A0, B0, A1 = lv[("A", 0)], lv[("B", 0)], lv[("A", 1)]

    res = {"n_decks": len(decks), "judges": JUDGES, "rubric": "J1_rubric_v4",
           "rubric_sha256": "5ee738e008d94c31e884cbeca1d1d7b1213642f82732ad8b0428373a06a9bb4d"}

    # ---------- cost / coverage ----------
    cost, tin, tout, nfail = defaultdict(float), defaultdict(int), defaultdict(int), defaultdict(int)
    for c in calls:
        cost[c["judge"]] += c.get("cost_usd", 0.0) or 0.0
        tin[c["judge"]] += c.get("prompt_tokens", 0) or 0
        tout[c["judge"]] += c.get("completion_tokens", 0) or 0
        if not c.get("level"):
            nfail[c["judge"]] += 1
    res["cost"] = {"by_judge": dict(cost), "total_usd": sum(cost.values()),
                   "tokens_in": dict(tin), "tokens_out": dict(tout),
                   "failed_calls": dict(nfail), "n_calls": len(calls)}
    judgeable = [(d, s["unit_id"]) for d, r in decks.items() if not r.get("rung1_fail")
                 for s in r["sections"] if s["present_in_candidate"]]
    res["units"] = {
        "total_section_units": sum(len(r.get("sections", [])) for r in decks.values()),
        "judgeable": len(judgeable),
        "absent_in_candidate_no_call": sum(1 for r in decks.values()
                                           for s in r.get("sections", [])
                                           if not s["present_in_candidate"]),
        "verdicts_per_judge": {j: sum(1 for k in A0 if k[2] == j) for j in JUDGES},
        "completeness": {j: sum(1 for k in A0 if k[2] == j) / max(1, len(judgeable)) for j in JUDGES},
    }
    res["level_share_by_judge"] = {
        j: {l: sum(1 for k, v in A0.items() if k[2] == j and v == l) /
            max(1, sum(1 for k in A0 if k[2] == j)) for l in LEVELS} for j in JUDGES}

    # ---------- C1 agreement ----------
    def rows(judges, key):
        out = []
        for du in judgeable:
            d = {j: key(A0[(du[0], du[1], j)]) for j in judges if (du[0], du[1], j) in A0}
            if len(d) >= 2:
                out.append(d)
        return out
    gate = lambda l: "equivalent" if l == "equivalent" else "not_equivalent"
    res["C1_agreement"] = {}
    for nm, js in (("panel4", JUDGES), ("instructed_pair", PRIMARY_PAIR)):
        g, f = rows(js, gate), rows(js, lambda l: l)
        res["C1_agreement"][nm] = {
            "n_units": len(f),
            "alpha_gate": krippendorff(g, "nominal", ["equivalent", "not_equivalent"]),
            "alpha_4level_nominal": krippendorff(f, "nominal", LEVELS),
            "alpha_4level_ordinal": krippendorff([{k: ORD[v] for k, v in u.items()} for u in f],
                                                 "ordinal", list(range(4))),
            "fleiss_4level": fleiss(f, LEVELS),
            "exact_agreement_gate": mean([1.0 if len(set(u.values())) == 1 else 0.0 for u in g]) if g else None,
            "exact_agreement_4level": mean([1.0 if len(set(u.values())) == 1 else 0.0 for u in f]) if f else None,
            "gwet_ac1_gate_DIAGNOSTIC": gwet_ac1(g, ["equivalent", "not_equivalent"]),
            "gwet_ac1_4level_DIAGNOSTIC": gwet_ac1(f, LEVELS),
        }
    pw = {}
    for i in range(len(JUDGES)):
        for k in range(i + 1, len(JUDGES)):
            a, b = JUDGES[i], JUDGES[k]
            n = ex = gt = 0
            for du in judgeable:
                ka, kb = (du[0], du[1], a), (du[0], du[1], b)
                if ka in A0 and kb in A0:
                    n += 1
                    ex += A0[ka] == A0[kb]
                    gt += gate(A0[ka]) == gate(A0[kb])
            if n:
                pw[f"{a}|{b}"] = {"n": n, "exact_4level": ex / n, "gate": gt / n}
    res["C1_pairwise"] = pw

    # ---------- deck & cell tables ----------
    R0 = {d: (r["treesim_reconstructed"] if not r.get("rung1_fail") else 0.0)
          for d, r in decks.items()}
    SOFT, cov = deck_scores(decks, A0)
    res["coverage_by_deck_mean"] = mean(cov.values())
    per_judge = {j: deck_scores(decks, A0, CREDIT, [j])[0] for j in JUDGES}
    pair_only = deck_scores(decks, A0, CREDIT, PRIMARY_PAIR)[0]
    res["cell_table"] = {"TreeSim": cell_table(R0, decks),
                         "soft_TreeSim_panel4": cell_table(SOFT, decks),
                         "soft_TreeSim_instructed_pair": cell_table(pair_only, decks),
                         **{f"soft_TreeSim_{j}": cell_table(per_judge[j], decks) for j in JUDGES}}
    res["credit_sensitivity"] = {
        n: cell_table(deck_scores(decks, A0, cm)[0], decks) for n, cm in CREDIT_ALT.items()}

    # ---------- C3 / C4 ----------
    res["C3_rankings"] = {k: ranking(v) for k, v in res["cell_table"].items()}
    jr = [res["C3_rankings"][f"soft_TreeSim_{j}"] for j in JUDGES]
    res["C3"] = {"per_judge_rankings": {j: res["C3_rankings"][f"soft_TreeSim_{j}"] for j in JUDGES},
                 "all_judges_same_order": len(set(jr)) == 1,
                 "vanilla_last_all_judges": all(r.split(" > ")[-1] == "F0" for r in jr),
                 "ensemble_ranking": res["C3_rankings"]["soft_TreeSim_panel4"],
                 "treesim_ranking": res["C3_rankings"]["TreeSim"]}
    res["C3"]["PASS"] = res["C3"]["all_judges_same_order"] and res["C3"]["vanilla_last_all_judges"]
    cells = ("F0", "F6", "SE")
    allm = [res["cell_table"][f"soft_TreeSim_{j}"][c]["mean"] for j in JUDGES for c in cells]
    eff = res["cell_table"]["soft_TreeSim_panel4"]
    er = max(v["mean"] for v in eff.values()) - min(v["mean"] for v in eff.values())
    res["C4"] = {"judge_choice_range": max(allm) - min(allm), "cell_effect_range": er,
                 "ratio": (max(allm) - min(allm)) / er if er else None}
    res["C4"]["PASS"] = res["C4"]["ratio"] is not None and res["C4"]["ratio"] <= 1.0
    # SECONDARY DIAGNOSTIC, not the pre-registered test: the criterion as frozen
    # conflates a judge being uniformly harsher (a LEVEL shift, which cannot change
    # any ranking) with a judge distorting the CONTRASTS (which can). Centering each
    # judge on its own grand mean isolates the second. Reported alongside, never
    # instead of, the frozen number.
    cent = []
    for j in JUDGES:
        m = [res["cell_table"][f"soft_TreeSim_{j}"][c]["mean"] for c in cells]
        gm = mean(m)
        cent += [x - gm for x in m]
    res["C4"]["centered_judge_range_DIAGNOSTIC"] = max(cent) - min(cent)
    res["C4"]["centered_ratio_DIAGNOSTIC"] = (max(cent) - min(cent)) / er if er else None
    res["C4"]["per_judge_grand_mean"] = {
        j: mean([res["cell_table"][f"soft_TreeSim_{j}"][c]["mean"] for c in cells]) for j in JUDGES}

    # ---------- C2 position ----------
    pos = {}
    if B0:
        for j in JUDGES:
            ds = []
            for did, r in decks.items():
                if r.get("rung1_fail") or r["seed"] != 1:
                    continue
                if not any((did, s["unit_id"], j) in B0 for s in r["sections"]):
                    continue
                a = deck_scores({did: r}, A0, CREDIT, [j])[0][did]
                b = deck_scores({did: r}, B0, CREDIT, [j])[0][did]
                ds.append(b - a)
            if ds:
                pos[j] = {"n": len(ds), "mean_signed": mean(ds),
                          "mean_abs": mean(abs(x) for x in ds), "max_abs": max(abs(x) for x in ds)}
        n = f = 0
        for k, v in A0.items():
            if k in B0:
                n += 1
                f += v != B0[k]
        allabs = [x for j in pos for x in [pos[j]["mean_abs"]] * pos[j]["n"]]
        pos["pooled"] = {"n": sum(p["n"] for p in pos.values() if isinstance(p, dict) and "n" in p),
                         "mean_abs": mean(allabs) if allabs else None,
                         "unit_flip_rate": (f / n) if n else None, "n_units_both_orders": n}
        pos["PASS"] = pos["pooled"]["mean_abs"] is not None and pos["pooled"]["mean_abs"] <= 0.0232
    res["C2_position"] = pos

    # ---------- determinism ----------
    n = f = 0
    for k, v in A0.items():
        if k in A1:
            n += 1
            f += v != A1[k]
    res["determinism"] = {"n_units_rerun": n, "unit_flip_rate": (f / n) if n else None}

    # ---------- named deliverable: per-section LLM vs per-section TreeSim ----------
    sec = defaultdict(lambda: {"ts": [], "llm": [], "levels": Counter()})
    for did, r in decks.items():
        if r.get("rung1_fail"):
            continue
        for s in r["sections"]:
            if not s["present_in_candidate"]:
                continue
            got = [CREDIT[A0[(did, s["unit_id"], j)]] for j in JUDGES
                   if (did, s["unit_id"], j) in A0]
            if not got:
                continue
            e = sec[s["section"]]
            e["ts"].append(s["treesim_section_score"])
            e["llm"].append(median(got))
            for j in JUDGES:
                if (did, s["unit_id"], j) in A0:
                    e["levels"][A0[(did, s["unit_id"], j)]] += 1
    res["per_section"] = {
        k: {"n": len(v["ts"]), "mean_treesim": mean(v["ts"]), "mean_llm_credit": mean(v["llm"]),
            "gap_llm_minus_treesim": mean(v["llm"]) - mean(v["ts"]),
            "pearson": pearson(v["ts"], v["llm"]), "spearman": spearman(v["ts"], v["llm"]),
            "level_share": {l: v["levels"][l] / max(1, sum(v["levels"].values())) for l in LEVELS}}
        for k, v in sorted(sec.items(), key=lambda x: -len(x[1]["ts"]))}

    # ---------- U1 / U2 calibration ----------
    rung3 = load_rung3()
    a2lad, a2qoi = load_a2()

    def calib(labels):
        ks = [d for d in R0 if d in labels]
        y = [labels[d] for d in ks]
        out = {"n": len(ks), "n_pos": sum(y), "n_neg": len(y) - sum(y)}
        if len(set(y)) < 2:
            return out
        for nm, sc in (("TreeSim", R0), ("soft_TreeSim", SOFT),
                       ("soft_TreeSim_instructed_pair", pair_only)):
            x = [sc[d] for d in ks]
            out[nm] = {"r_pb": pearson(x, y), "auc": auc(x, y),
                       "mean_pass": mean([a for a, b in zip(x, y) if b == 1]),
                       "mean_fail": mean([a for a, b in zip(x, y) if b == 0])}
        a, b = [SOFT[d] for d in ks], [R0[d] for d in ks]
        p, lo, hi = boot_diff(a, b, y, auc)
        out["soft_minus_treesim_auc"] = {"point": p, "lo5": lo, "hi95": hi}
        p, lo, hi = boot_diff(a, b, y, pearson)
        out["soft_minus_treesim_rpb"] = {"point": p, "lo5": lo, "hi95": hi}
        return out

    res["U1_rung3"] = calib({d: v["rung3_lenient"] for d, v in rung3.items() if d in R0})
    u1 = res["U1_rung3"]
    res["U1_PASS"] = bool(
        u1.get("soft_TreeSim") and u1.get("TreeSim")
        and u1["soft_TreeSim"]["r_pb"] > u1["TreeSim"]["r_pb"]
        and u1["soft_TreeSim"]["auc"] > u1["TreeSim"]["auc"]
        and (u1["soft_minus_treesim_auc"]["lo5"] or -1) > 0
        and (u1["soft_minus_treesim_rpb"]["lo5"] or -1) > 0)
    res["U2_rung4"] = calib({d: int(v["L4"]) for d, v in a2lad.items()
                             if d in R0 and v.get("L4") not in (None, "")})
    qk = [d for d in a2qoi if d in R0]
    res["U2_qoi"] = {"n": len(qk)}
    if len(qk) >= 4:
        yq = [a2qoi[d] for d in qk]
        for nm, sc in (("TreeSim", R0), ("soft_TreeSim", SOFT)):
            res["U2_qoi"][nm] = {"pearson": pearson([sc[d] for d in qk], yq),
                                 "spearman": spearman([sc[d] for d in qk], yq)}

    # ---------- U4 blind spots ----------
    ext = {d for d, v in rung3.items() if "missing_external_asset" in v["categories"]}
    ann = set()
    for did, r in decks.items():
        if r.get("rung1_fail"):
            continue
        for s in r["sections"]:
            if not s["present_in_candidate"] and s["n_ref_elements"] > 1:
                ann.add(did)
                break
    res["U4_blind_spots"] = {
        "external_asset_decks": {
            "n": len(ext & set(R0)),
            "rung3_pass_rate": mean([rung3[d]["rung3_lenient"] for d in ext]) if ext else None,
            "mean_TreeSim": mean([R0[d] for d in ext if d in R0]) if ext else None,
            "mean_soft": mean([SOFT[d] for d in ext if d in SOFT]) if ext else None,
            "note": "neither metric reads external data files; largest rung-3 failure class"},
        "unmatched_subtree_decks": {
            "n": len(ann), "by_cell": dict(Counter(decks[d]["cell"] for d in ann)),
            "mean_TreeSim": mean([R0[d] for d in ann]) if ann else None,
            "mean_soft": mean([SOFT[d] for d in ann]) if ann else None,
            "note": "reference sections with no candidate counterpart keep credit 0 (TreeSim's verdict)"},
    }

    res["VERDICT"] = {
        "C1_PASS": bool(res["C1_agreement"]["panel4"]["alpha_gate"] is not None
                        and res["C1_agreement"]["panel4"]["alpha_gate"] >= 0.667
                        and (res["C1_agreement"]["panel4"]["alpha_4level_nominal"] or 0) >= 0.40),
        "C2_PASS": res["C2_position"].get("PASS"),
        "C3_PASS": res["C3"]["PASS"],
        "C4_PASS": res["C4"]["PASS"],
        "U1_PASS": res["U1_PASS"],
    }
    v = res["VERDICT"]
    v["VALID"] = all(v[k] for k in ("C1_PASS", "C2_PASS", "C3_PASS", "C4_PASS")
                     if v[k] is not None) and None not in [v[k] for k in
                                                           ("C1_PASS", "C2_PASS", "C3_PASS", "C4_PASS")]
    v["SHIPPABLE"] = bool(v["VALID"] and v["U1_PASS"])

    (ART / "J1_section_analysis.json").write_text(json.dumps(res, indent=2, default=str))
    rows_out = []
    for did, r in decks.items():
        rows_out.append({"deck_id": did, "cell": r["cell"], "seed": r["seed"], "task": r["task"],
                         "treesim_of_record": r.get("treesim_of_record"),
                         "TreeSim": round(R0[did], 6), "soft_TreeSim": round(SOFT[did], 6),
                         "soft_pair": round(pair_only[did], 6),
                         **{f"soft_{j}": round(per_judge[j][did], 6) for j in JUDGES},
                         "n_ref_sections": r.get("n_ref_sections"),
                         "n_judgeable": sum(1 for s in r.get("sections", [])
                                            if s["present_in_candidate"]),
                         "judge_coverage": round(cov[did], 4),
                         "rung1_fail": r.get("rung1_fail")})
    with (ART / "J1_section_deck_scores.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=sorted({k for r in rows_out for k in r}))
        w.writeheader()
        w.writerows(rows_out)

    print(json.dumps({k: res[k] for k in
                      ("units", "cost", "C1_agreement", "C1_pairwise", "C3", "C4",
                       "C2_position", "determinism", "level_share_by_judge", "VERDICT")},
                     indent=2, default=str))
    print("\n=== CELL TABLE ===")
    for k, t in res["cell_table"].items():
        print(f"{k:32}", {c: f"{t[c]['mean']:.4f}+-{t[c]['sd']:.4f}" for c in cells if c in t},
              "|", ranking(t))
    print("\n=== PER-SECTION: LLM credit vs TreeSim ===")
    print(f"{'section':22}{'n':>5}{'TreeSim':>9}{'LLM':>9}{'gap':>9}{'pearson':>9}")
    for k, v2 in res["per_section"].items():
        pr = f"{v2['pearson']:.3f}" if v2["pearson"] is not None else "  n/a"
        print(f"{k:22}{v2['n']:5}{v2['mean_treesim']:9.3f}{v2['mean_llm_credit']:9.3f}"
              f"{v2['gap_llm_minus_treesim']:+9.3f}{pr:>9}")
    print("\n=== U1 rung-3 ===")
    print(json.dumps(res["U1_rung3"], indent=2, default=str))


if __name__ == "__main__":
    main()
