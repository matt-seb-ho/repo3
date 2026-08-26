#!/usr/bin/env python3
"""
Thread J1 — soft-TreeSim analysis. Implements the frozen aggregation of
`J1_rubric_v2.md` (+ the v3 judge-panel amendment) and evaluates the
pre-registered criteria C1-C4 and U1-U4.

All statistics are implemented in this file (no scipy) so every number is
auditable. Writes `J1_analysis.json` and `J1_deck_scores.csv`.
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
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "neurips_review/sprint/scripts"))
from eval.judge_geos import load_and_resolve_dir            # noqa: E402
from J1_treesim import tree_sim_credited                     # noqa: E402

PANEL = ["dsv4flash", "gpt54mini", "gemini3flash", "qwen3235b", "mistralmed31"]
INDEP = ["gpt54mini", "gemini3flash", "qwen3235b", "mistralmed31"]
PRIMARY = "dsv4flash"
CAP = 60
SEV = ["cosmetic", "minor", "material", "severe", "uncertain"]
CREDIT = {"cosmetic": 1.0, "minor": 0.7, "material": 0.3, "severe": 0.0, "uncertain": 0.0}
CREDIT_ALT = {
    "frozen_v1": {"cosmetic": 1.0, "minor": 0.7, "material": 0.3, "severe": 0.0, "uncertain": 0.0},
    "linear":    {"cosmetic": 1.0, "minor": 2 / 3, "material": 1 / 3, "severe": 0.0, "uncertain": 0.0},
    "binary":    {"cosmetic": 1.0, "minor": 1.0, "material": 0.0, "severe": 0.0, "uncertain": 0.0},
    "abstain_07": {"cosmetic": 1.0, "minor": 0.7, "material": 0.3, "severe": 0.0, "uncertain": 0.7},
}
ORD = {"cosmetic": 0, "minor": 1, "material": 2, "severe": 3}


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
            avg = (i + j) / 2 + 1
            for k in range(i, j + 1):
                r[o[k]] = avg
            i = j + 1
        return r
    return pearson(rank(x), rank(y))


def auc(scores, labels):
    """P(score of a positive > score of a negative), ties = 0.5."""
    pos = [s for s, l in zip(scores, labels) if l == 1]
    neg = [s for s, l in zip(scores, labels) if l == 0]
    if not pos or not neg:
        return None
    tot = 0.0
    for p in pos:
        for q in neg:
            tot += 1.0 if p > q else (0.5 if p == q else 0.0)
    return tot / (len(pos) * len(neg))


def krippendorff(units, metric="nominal", levels=None):
    """units: list of dicts coder->value. Standard coincidence-matrix alpha."""
    vals = sorted({v for u in units for v in u.values()}) if levels is None else levels
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
        cnt = Counter(vs)
        for c in cnt:
            for k in cnt:
                v = cnt[c] * cnt[k] - (cnt[c] if c == k else 0)
                o[idx[c]][idx[k]] += v / (m - 1)
    if n_total < 2:
        return None
    nc = [sum(o[i]) for i in range(K)]

    def d(i, j):
        if metric == "nominal":
            return 0.0 if i == j else 1.0
        return (i - j) ** 2                      # ordinal-ish (interval on the rank scale)

    Do = sum(o[i][j] * d(i, j) for i in range(K) for j in range(K)) / n_total
    De = sum(nc[i] * nc[j] * d(i, j) for i in range(K) for j in range(K)) / (n_total * (n_total - 1))
    if De == 0:
        return None
    return 1 - Do / De


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
    m = len(rows[0])
    if any(sum(r) != sum(rows[0]) for r in rows):        # need equal raters
        m = min(sum(r) for r in rows)
        rows = [r for r in rows if sum(r) == max(sum(x) for x in rows)]
        if not rows:
            return None
    n = sum(rows[0])
    N = len(rows)
    if n < 2:
        return None
    P = [(sum(x * x for x in r) - n) / (n * (n - 1)) for r in rows]
    pj = [sum(r[j] for r in rows) / (N * n) for j in range(len(levels))]
    Pbar = mean(P)
    Pe = sum(p * p for p in pj)
    return None if Pe >= 1 else (Pbar - Pe) / (1 - Pe)


def boot_diff(a, b, labels, stat, n=2000, seed=0):
    """Paired bootstrap over decks of stat(a)-stat(b). Returns (point, lo5, hi95)."""
    rng = random.Random(seed)
    N = len(labels)
    p = stat(a, labels) - stat(b, labels)
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
    if not ds:
        return p, None, None
    return p, ds[int(0.05 * len(ds))], ds[int(0.95 * len(ds))]


# ------------------------------ data loading ------------------------------

def load_items():
    return [json.loads(l) for l in (ART / "J1_items.jsonl").open()]


def load_judge(path="J1_judge_raw.jsonl"):
    """verdict[(order, rep)][judge][(task, cache_key)] = severity"""
    v = defaultdict(lambda: defaultdict(dict))
    calls = []
    for l in (ART / path).open():
        try:
            r = json.loads(l)
        except json.JSONDecodeError:
            continue
        calls.append(r)
        for ck, d in (r.get("verdicts") or {}).items():
            if d.get("severity"):
                v[(r["order"], r["rep"])][r["judge"]][(r["task"], ck)] = d["severity"]
    return v, calls


def selected_units(items, cap=CAP):
    """(deck, rung) -> [(eid, (task, cache_key), weight)] under the frozen cap."""
    out = {}
    for r in items:
        if r.get("rung1_fail"):
            continue
        for vn in ("hard", "soft"):
            j = [i for i in r["variants"][vn]["items"] if i["judged"]]
            j.sort(key=lambda x: (-abs(x["weight"]), x["item_id"]))
            out[(r["deck_id"], vn)] = [(i["eid"], (r["task"], i["cache_key"]), i["weight"])
                                       for i in j[:cap]]
    return out


def deck_score(rec, vn, credit_by_eid):
    gt = load_and_resolve_dir(Path(rec["gt_dir"]))
    gen = load_and_resolve_dir(Path(rec["gen_dir"]))
    return tree_sim_credited(gt, gen, credit_by_eid, soft_match=(vn == "soft")).score


# ------------------------------ ground truth ------------------------------

def load_rung3():
    out = {}
    with (ART / "A1_rung3_corrected_by_taskrun.csv").open() as fh:
        for r in csv.DictReader(fh):
            cell = r["cell"].replace("autocamp_", "")
            did = f"{cell}_{r['seed']}_{r['task']}".replace("_s", "_s")
            out[f"{cell}_{r['seed']}_{r['task']}"] = {
                "rung3_lenient": int(r["rung3_lenient"]),
                "categories": r["categories"],
            }
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


# ------------------------------ main --------------------------------------

def cell_table(scores, decks):
    """mean over tasks within seed, then mean +- sd over seeds. Frozen aggregation."""
    by = defaultdict(lambda: defaultdict(list))
    for did, s in scores.items():
        d = decks[did]
        by[d["cell"]][d["seed"]].append(s)
    out = {}
    for cell, seeds in by.items():
        sm = [mean(v) for k, v in sorted(seeds.items())]
        out[cell] = {"mean": mean(sm), "sd": pstdev(sm) if len(sm) > 1 else 0.0,
                     "seeds": sm, "n": sum(len(v) for v in seeds.values())}
    return out


def ranking(tbl):
    return " > ".join(c for c, _ in sorted(tbl.items(), key=lambda x: -x[1]["mean"]))


def main():
    items = load_items()
    decks = {r["deck_id"]: r for r in items}
    sel = selected_units(items)
    verd, calls = load_judge()
    A0 = verd[("A", 0)]
    rung3, (a2lad, a2qoi) = load_rung3(), load_a2()

    res = {"n_decks": len(items), "judges": PANEL}

    # ---------- cost, coverage, abstention, cache ----------
    cost = defaultdict(float)
    tin = defaultdict(int)
    tout = defaultdict(int)
    nfail = defaultdict(int)
    for c in calls:
        cost[c["judge"]] += c.get("cost_usd", 0.0)
        tin[c["judge"]] += c.get("prompt_tokens", 0)
        tout[c["judge"]] += c.get("completion_tokens", 0)
        if not c.get("verdicts"):
            nfail[c["judge"]] += 1
    res["cost"] = {"by_judge": dict(cost), "total_usd": sum(cost.values()),
                   "tokens_in": dict(tin), "tokens_out": dict(tout),
                   "failed_calls": dict(nfail), "n_calls": len(calls)}
    res["abstention_rate"] = {j: (Counter(A0[j].values())["uncertain"] / len(A0[j])) if A0[j] else None
                              for j in PANEL}
    slots = sum(len(v) for v in sel.values())
    uniq = len({u for v in sel.values() for _, u, _ in v})
    tup = len({i["tuple_key"] for r in items if not r.get("rung1_fail")
               for vn in ("hard", "soft") for i in r["variants"][vn]["items"] if i["judged"]})
    res["cache"] = {"judged_item_slots": slots, "unique_card_units": uniq,
                    "card_hit_rate": 1 - uniq / slots,
                    "unique_tuple_keys": tup, "tuple_hit_rate": 1 - tup / slots}

    # ---------- item-level agreement (C1) ----------
    all_units = sorted({u for v in sel.values() for _, u, _ in v})
    def unit_rows(judges, key):
        rows = []
        for u in all_units:
            d = {j: key(A0[j][u]) for j in judges if u in A0[j] and key(A0[j][u]) is not None}
            if len(d) >= 2:
                rows.append(d)
        return rows
    gate = lambda s: None if s == "uncertain" else ("no_effect" if s == "cosmetic" else "effect")
    four = lambda s: None if s == "uncertain" else s
    res["agreement"] = {}
    for name, judges in (("panel5", PANEL), ("independent4", INDEP)):
        g, f = unit_rows(judges, gate), unit_rows(judges, four)
        res["agreement"][name] = {
            "n_units_gate": len(g), "n_units_4level": len(f),
            "alpha_gate_nominal": krippendorff(g, "nominal", ["no_effect", "effect"]),
            "alpha_4level_nominal": krippendorff(f, "nominal", SEV[:4]),
            "alpha_4level_ordinal": krippendorff([{k: ORD[v] for k, v in u.items()} for u in f],
                                                 "ordinal", [0, 1, 2, 3]),
            "fleiss_4level": fleiss(f, SEV[:4]),
            "exact_agreement_gate": mean([1.0 if len(set(u.values())) == 1 else 0.0 for u in g]) if g else None,
            "exact_agreement_4level": mean([1.0 if len(set(u.values())) == 1 else 0.0 for u in f]) if f else None,
        }
    res["severity_share_by_judge"] = {
        j: {s: Counter(A0[j].values())[s] / len(A0[j]) for s in SEV} for j in PANEL if A0[j]}

    # ---------- self-preference control (rubric v3) ----------
    sp = {}
    for j in INDEP:
        n = a = g = 0
        for u in all_units:
            if u in A0[PRIMARY] and u in A0[j]:
                n += 1
                a += A0[PRIMARY][u] == A0[j][u]
                g += gate(A0[PRIMARY][u]) == gate(A0[j][u])
        sp[j] = {"n": n, "agree_4level": a / n if n else None, "agree_gate": g / n if n else None}
    ind_credit = {u: median([CREDIT[A0[j][u]] for j in INDEP if u in A0[j]])
                  for u in all_units if any(u in A0[j] for j in INDEP)}
    pr_credit = {u: CREDIT[A0[PRIMARY][u]] for u in all_units if u in A0[PRIMARY]}
    both = [u for u in all_units if u in ind_credit and u in pr_credit]
    sp["mean_credit_primary"] = mean([pr_credit[u] for u in both]) if both else None
    sp["mean_credit_independent_median"] = mean([ind_credit[u] for u in both]) if both else None
    sp["primary_minus_independent"] = (sp["mean_credit_primary"] - sp["mean_credit_independent_median"]
                                       if both else None)
    res["self_preference"] = sp

    # ---------- deck scores: all rungs, ensemble + per judge ----------
    def credits(deck, vn, getter):
        return {eid: c for eid, u, _ in sel[(deck, vn)]
                if (c := getter(u)) is not None}

    ens = lambda u: (median([CREDIT[A0[j][u]] for j in PANEL if u in A0[j]])
                     if any(u in A0[j] for j in PANEL) else None)
    ens_ind = lambda u: (median([CREDIT[A0[j][u]] for j in INDEP if u in A0[j]])
                         if any(u in A0[j] for j in INDEP) else None)

    rows = []
    scores = defaultdict(dict)
    for r in items:
        did = r["deck_id"]
        if r.get("rung1_fail"):
            for k in ("R0", "R1", "R2a", "R2"):
                scores[k][did] = 0.0
            for j in PANEL:
                scores[f"R1_{j}"][did] = 0.0
                scores[f"R2_{j}"][did] = 0.0
            scores["R1_indep"][did] = 0.0
            scores["R2_indep"][did] = 0.0
            rows.append({"deck_id": did, "cell": r["cell"], "seed": r["seed"], "task": r["task"],
                         "treesim": 0.0, "R0": 0.0, "R1": 0.0, "R2a": 0.0, "R2": 0.0,
                         "rung1_fail": True})
            continue
        gt = load_and_resolve_dir(Path(r["gt_dir"]))
        gen = load_and_resolve_dir(Path(r["gen_dir"]))
        sc = {"R0": tree_sim_credited(gt, gen).score,
              "R2a": tree_sim_credited(gt, gen, soft_match=True).score}
        sc["R1"] = tree_sim_credited(gt, gen, credits(did, "hard", ens)).score
        sc["R2"] = tree_sim_credited(gt, gen, credits(did, "soft", ens), soft_match=True).score
        sc["R1_indep"] = tree_sim_credited(gt, gen, credits(did, "hard", ens_ind)).score
        sc["R2_indep"] = tree_sim_credited(gt, gen, credits(did, "soft", ens_ind), soft_match=True).score
        for j in PANEL:
            gj = (lambda jj: (lambda u: CREDIT[A0[jj][u]] if u in A0[jj] else None))(j)
            sc[f"R1_{j}"] = tree_sim_credited(gt, gen, credits(did, "hard", gj)).score
            sc[f"R2_{j}"] = tree_sim_credited(gt, gen, credits(did, "soft", gj), soft_match=True).score
        for name, cmap in CREDIT_ALT.items():
            gm = (lambda cm: (lambda u: median([cm[A0[j][u]] for j in PANEL if u in A0[j]])
                              if any(u in A0[j] for j in PANEL) else None))(cmap)
            sc[f"R1_credit_{name}"] = tree_sim_credited(gt, gen, credits(did, "hard", gm)).score
        for k, v in sc.items():
            scores[k][did] = v
        cov = [1 for _, u, _ in sel[(did, 'hard')] if any(u in A0[j] for j in PANEL)]
        tw = sum(abs(w) for _, _, w in sel[(did, "hard")])
        rows.append({"deck_id": did, "cell": r["cell"], "seed": r["seed"], "task": r["task"],
                     "treesim_of_record": r["treesim_of_record"],
                     **{k: round(v, 6) for k, v in sc.items() if not k.startswith("R1_credit")},
                     "n_judged_hard": len(sel[(did, "hard")]),
                     "judged_weight": round(tw, 6),
                     "verdict_coverage": round(len(cov) / max(1, len(sel[(did, 'hard')])), 4),
                     "rung1_fail": False})

    res["ladder_cell_table"] = {k: cell_table(scores[k], decks)
                                for k in ("R0", "R1", "R2a", "R2", "R1_indep", "R2_indep")}
    res["per_judge_cell_table"] = {j: {"R1": cell_table(scores[f"R1_{j}"], decks),
                                       "R2": cell_table(scores[f"R2_{j}"], decks)} for j in PANEL}
    res["credit_sensitivity"] = {n: cell_table(scores[f"R1_credit_{n}"], decks) for n in CREDIT_ALT}

    # ---------- C3 / C4 ----------
    res["C3_rankings"] = {"R0": ranking(res["ladder_cell_table"]["R0"]),
                          "R1_ensemble": ranking(res["ladder_cell_table"]["R1"]),
                          "R2_ensemble": ranking(res["ladder_cell_table"]["R2"]),
                          **{f"R1_{j}": ranking(res["per_judge_cell_table"][j]["R1"]) for j in PANEL}}
    jr = [res["C3_rankings"][f"R1_{j}"] for j in PANEL]
    res["C3_all_judges_same_order"] = len(set(jr)) == 1
    res["C3_vanilla_last_all_judges"] = all(r.split(" > ")[-1] == "F0" for r in jr)
    jm = {j: [res["per_judge_cell_table"][j]["R1"][c]["mean"] for c in ("F0", "F6", "SE")]
          for j in PANEL}
    allm = [v for vs in jm.values() for v in vs]
    eff = res["ladder_cell_table"]["R1"]
    effrange = max(v["mean"] for v in eff.values()) - min(v["mean"] for v in eff.values())
    res["C4"] = {"judge_choice_range": max(allm) - min(allm), "cell_effect_range": effrange,
                 "ratio": (max(allm) - min(allm)) / effrange if effrange else None}

    # ---------- C2 position bias ----------
    B0 = verd[("B", 0)]
    pos = {}
    for j in PANEL:
        ds = []
        for r in items:
            if r.get("rung1_fail") or r["seed"] != 1:
                continue
            did = r["deck_id"]
            gt = load_and_resolve_dir(Path(r["gt_dir"]))
            gen = load_and_resolve_dir(Path(r["gen_dir"]))
            ga = (lambda u: CREDIT[A0[j][u]] if u in A0[j] else None)
            gb = (lambda u: CREDIT[B0[j][u]] if u in B0[j] else None)
            if not any(u in B0[j] for _, u, _ in sel[(did, "hard")]):
                continue
            a = tree_sim_credited(gt, gen, credits(did, "hard", ga)).score
            b = tree_sim_credited(gt, gen, credits(did, "hard", gb)).score
            ds.append(b - a)
        if ds:
            pos[j] = {"n": len(ds), "mean_signed": mean(ds),
                      "mean_abs": mean(abs(d) for d in ds), "max_abs": max(abs(d) for d in ds)}
    if pos:
        alld = [d for j in pos for d in [pos[j]["mean_abs"]] * pos[j]["n"]]
        pos["pooled"] = {"n": sum(p["n"] for p in pos.values() if "n" in p),
                         "mean_abs": mean(alld)}
        # item-level flip rate A vs B
        n = f = 0
        for j in PANEL:
            for u in A0[j]:
                if u in B0[j]:
                    n += 1
                    f += A0[j][u] != B0[j][u]
        pos["item_flip_rate"] = f / n if n else None
    res["C2_position"] = pos

    # ---------- determinism (rep 1) ----------
    R1r = verd[("A", 1)]
    n = f = 0
    for j in PANEL:
        for u in A0[j]:
            if u in R1r[j]:
                n += 1
                f += A0[j][u] != R1r[j][u]
    res["determinism"] = {"n_items_rerun": n, "item_flip_rate": (f / n) if n else None}

    # ---------- U1/U2 calibration ----------
    def calib(labels_by_deck, name):
        ks = [d for d in scores["R0"] if d in labels_by_deck]
        y = [labels_by_deck[d] for d in ks]
        out = {"n": len(ks), "n_pos": sum(y), "n_neg": len(y) - sum(y)}
        if len(set(y)) < 2:
            return out
        for m in ("R0", "R1", "R2a", "R2", "R1_indep"):
            x = [scores[m][d] for d in ks]
            out[m] = {"r_pb": pearson(x, y), "auc": auc(x, y),
                      "mean_pos": mean([a for a, b in zip(x, y) if b == 1]),
                      "mean_neg": mean([a for a, b in zip(x, y) if b == 0])}
        for m in ("R1", "R2a", "R2"):
            a = [scores[m][d] for d in ks]
            b = [scores["R0"][d] for d in ks]
            p, lo, hi = boot_diff(a, b, y, auc)
            out[f"{m}_minus_R0_auc"] = {"point": p, "lo5": lo, "hi95": hi}
            p, lo, hi = boot_diff(a, b, y, pearson)
            out[f"{m}_minus_R0_rpb"] = {"point": p, "lo5": lo, "hi95": hi}
        a = [scores["R2"][d] for d in ks]
        b = [scores["R2a"][d] for d in ks]
        p, lo, hi = boot_diff(a, b, y, auc)
        out["R2_minus_R2a_auc"] = {"point": p, "lo5": lo, "hi95": hi}
        return out

    res["U1_rung3"] = calib({d: v["rung3_lenient"] for d, v in rung3.items() if d in scores["R0"]},
                            "rung3_lenient")
    res["U2_rung4"] = calib({d: int(v["L4"]) for d, v in a2lad.items()
                             if d in scores["R0"] and v.get("L4") not in (None, "")}, "rung4")
    qk = [d for d in a2qoi if d in scores["R0"]]
    res["U2_qoi"] = {"n": len(qk)}
    if len(qk) >= 4:
        yq = [a2qoi[d] for d in qk]
        for m in ("R0", "R1", "R2a", "R2"):
            xm = [scores[m][d] for d in qk]
            res["U2_qoi"][m] = {"pearson": pearson(xm, yq), "spearman": spearman(xm, yq)}

    # ---------- U4 blind spots ----------
    ext = {d for d, v in rung3.items() if "missing_external_asset" in v["categories"]}
    ann = {d for d in scores["R0"] if abs(scores["R2a"][d] - scores["R0"][d]) > 1e-9}
    res["U4_blind_spots"] = {
        "external_asset_decks": {
            "n": len(ext & set(scores["R0"])),
            "mean_R0": mean([scores["R0"][d] for d in ext if d in scores["R0"]]) if ext else None,
            "mean_R1": mean([scores["R1"][d] for d in ext if d in scores["R1"]]) if ext else None,
            "rung3_pass_rate": mean([rung3[d]["rung3_lenient"] for d in ext]) if ext else None,
        },
        "annihilation_decks": {
            "n": len(ann), "by_cell": dict(Counter(decks[d]["cell"] for d in ann)),
            "mean_R0": mean([scores["R0"][d] for d in ann]) if ann else None,
            "mean_R2a": mean([scores["R2a"][d] for d in ann]) if ann else None,
            "mean_R2": mean([scores["R2"][d] for d in ann]) if ann else None,
        },
    }
    # deterministic external-file feature vs TreeSim on rung 3
    miss = {}
    for r in items:
        n_missing = 0
        for vn in ("hard",):
            for i in r["variants"].get(vn, {}).get("items", []):
                for key in ("files_ref", "files_cand"):
                    for f in (i.get("evidence", {}).get(key) or []):
                        if not f.get("exists_in_this_deck"):
                            n_missing += 1
        miss[r["deck_id"]] = n_missing
    ks = [d for d in rung3 if d in miss and d in scores["R0"]]
    if ks:
        y = [rung3[d]["rung3_lenient"] for d in ks]
        res["U4_blind_spots"]["deterministic_missing_file_feature"] = {
            "n": len(ks), "auc": auc([-miss[d] for d in ks], y),
            "r_pb": pearson([-miss[d] for d in ks], y)}

    (ART / "J1_analysis.json").write_text(json.dumps(res, indent=2, default=str))
    with (ART / "J1_deck_scores.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=sorted({k for r in rows for k in r}))
        w.writeheader()
        w.writerows(rows)
    print(json.dumps({k: res[k] for k in
                      ("cache", "cost", "agreement", "C3_rankings", "C3_all_judges_same_order",
                       "C4", "C2_position", "self_preference", "abstention_rate")},
                     indent=2, default=str)[:6000])
    print("\n--- ladder cell table ---")
    for k, t in res["ladder_cell_table"].items():
        print(f"{k:10}", {c: f"{v['mean']:.4f}+-{v['sd']:.4f}" for c, v in sorted(t.items())},
              "|", ranking(t))
    print("\n--- U1 rung3 ---")
    print(json.dumps(res["U1_rung3"], indent=2, default=str)[:2500])


if __name__ == "__main__":
    main()
