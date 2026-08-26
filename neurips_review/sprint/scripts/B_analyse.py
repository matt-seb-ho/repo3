#!/usr/bin/env python3
"""
Thread B — LMaaJ analysis. Score table, agreement, TreeSim correlation, execution calibration.

Aggregation is exactly as frozen in B_rubric_v1.md:
  per deck   : median over judge x order calls
  per cell   : mean over the 10 tasks within a seed, then mean +- sd over the 3 seeds
Rung-1-fail decks get lmaaj = 0.0 (floor convention, frozen).
"""
from __future__ import annotations

import csv
import json
import math
import statistics as st
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

ART = Path("/home/matt/sci/repo3/neurips_review/sprint/artifacts")
CELLS = ["F0", "F6", "SE"]
CELL_LABEL = {"F0": "Vanilla (F0)", "F6": "S+X (F6)", "SE": "SE"}
SEEDS = [1, 2, 3]
CREDIT = {"cosmetic": 1.0, "minor": 0.7, "material": 0.3, "severe": 0.0}


# ---------------------------------------------------------------- agreement

def krippendorff_alpha_nominal(units: list[list[str]]) -> tuple[float, int]:
    """Nominal-scale Krippendorff's alpha. units = list of label lists (one per coder)."""
    used = [u for u in units if len(u) >= 2]
    if not used:
        return float("nan"), 0
    o: dict[tuple[str, str], float] = defaultdict(float)
    n = 0
    for u in used:
        m = len(u)
        n += m
        for a, b in combinations(range(m), 2):
            o[(u[a], u[b])] += 1.0 / (m - 1)
            o[(u[b], u[a])] += 1.0 / (m - 1)
    vals = sorted({v for u in used for v in u})
    nc = {c: sum(o.get((c, k), 0.0) for k in vals) for c in vals}
    do = sum(o.get((c, k), 0.0) for c in vals for k in vals if c != k) / n
    de = sum(nc[c] * nc[k] for c in vals for k in vals if c != k) / (n * (n - 1))
    return (1.0 - do / de) if de else float("nan"), len(used)


def fleiss_kappa(units: list[list[str]], cats: list[str]) -> tuple[float, int]:
    """Fleiss' kappa over units rated by exactly the same number of raters."""
    sizes = Counter(len(u) for u in units)
    m = sizes.most_common(1)[0][0] if sizes else 0
    used = [u for u in units if len(u) == m and m >= 2]
    if not used:
        return float("nan"), 0
    N = len(used)
    p_j = {c: 0.0 for c in cats}
    P_i = []
    for u in used:
        cnt = Counter(u)
        for c in cats:
            p_j[c] += cnt[c]
        P_i.append((sum(cnt[c] ** 2 for c in cats) - m) / (m * (m - 1)))
    for c in cats:
        p_j[c] /= N * m
    Pbar = sum(P_i) / N
    Pe = sum(v ** 2 for v in p_j.values())
    return ((Pbar - Pe) / (1 - Pe)) if Pe < 1 else float("nan"), N


def spearman(x: list[float], y: list[float]) -> float:
    def rank(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            avg = (i + j) / 2 + 1
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r
    return pearson(rank(x), rank(y))


def pearson(x: list[float], y: list[float]) -> float:
    n = len(x)
    if n < 2:
        return float("nan")
    mx, my = sum(x) / n, sum(y) / n
    sx = math.sqrt(sum((a - mx) ** 2 for a in x))
    sy = math.sqrt(sum((b - my) ** 2 for b in y))
    if sx == 0 or sy == 0:
        return float("nan")
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / (sx * sy)


def mannwhitney_u_p(a: list[float], b: list[float]) -> tuple[float, float]:
    """Two-sided Mann-Whitney U with normal approximation and tie correction."""
    n1, n2 = len(a), len(b)
    if n1 == 0 or n2 == 0:
        return float("nan"), float("nan")
    allv = sorted(a + b)
    ranks = {}
    i = 0
    while i < len(allv):
        j = i
        while j + 1 < len(allv) and allv[j + 1] == allv[i]:
            j += 1
        ranks[allv[i]] = (i + j) / 2 + 1
        i = j + 1
    r1 = sum(ranks[v] for v in a)
    u1 = r1 - n1 * (n1 + 1) / 2
    mu = n1 * n2 / 2
    ties = Counter(allv)
    n = n1 + n2
    tie_term = sum(t ** 3 - t for t in ties.values())
    sd = math.sqrt(n1 * n2 / 12 * ((n + 1) - tie_term / (n * (n - 1))))
    if sd == 0:
        return u1, float("nan")
    z = (u1 - mu) / sd
    p = 2 * (1 - 0.5 * (1 + math.erf(abs(z) / math.sqrt(2))))
    return u1, p


# ---------------------------------------------------------------- load

def load():
    prompts = {}
    for l in (ART / "B_prompts.jsonl").open():
        r = json.loads(l)
        prompts[r["deck_id"]] = r

    calls = []
    for l in (ART / "B_judge_raw.jsonl").open():
        r = json.loads(l)
        if r.get("cell") not in CELLS:
            continue
        calls.append(r)

    # rungs 1-2 from Thread A1 (per-file -> per-deck)
    rung = {}
    p = ART / "A1_rungs12_perfile.csv"
    if p.exists():
        byd = defaultdict(list)
        for r in csv.DictReader(p.open()):
            c = r["cell"].replace("autocamp_", "")
            if c not in CELLS:
                continue
            byd[f"{c}_s{r['seed'][1:]}_{r['task']}"].append(r)
        for k, v in byd.items():
            rung[k] = {
                "rung1": int(all(x["rung1"] == "1" for x in v)),
                "rung2": int(all(x["rung2"] == "1" for x in v)),
                "categories": sorted({x["category"] for x in v if x["category"] != "valid"}),
            }
    # rung 3 from Thread A1 (per-deck-file geosx --validate-input): deck passes if all files pass
    p = ART / "A1_rung3_raw.jsonl"
    if p.exists():
        byd = defaultdict(list)
        for l in p.open():
            try:
                r = json.loads(l)
            except json.JSONDecodeError:
                continue
            c = (r.get("cell") or "").replace("autocamp_", "")
            if c not in CELLS:
                continue
            byd[f"{c}_s{str(r.get('seed','')).lstrip('s')}_{r.get('task')}"].append(r)
        for k, v in byd.items():
            if k in rung:
                rung[k]["rung3"] = int(all(str(x.get("rung3_pass")) == "1" for x in v))

    # rungs 3/4 from Thread A2 (full GEOS runs on the two rescue tasks)
    p = ART / "A2_ladder_per_run.csv"
    if p.exists():
        for r in csv.DictReader(p.open()):
            c = (r.get("cell") or "").replace("autocamp_", "")
            if c not in CELLS:
                continue
            k = f"{c}_s{str(r.get('seed','')).lstrip('s')}_{r.get('task')}"
            if k not in rung:
                continue
            for src, dst in (("L2", "a2_rung2"), ("L3", "rung3_geosx"), ("L4", "rung4_runs")):
                if r.get(src) not in ("", None):
                    rung[k][dst] = r[src]
    return prompts, calls, rung


def main():
    prompts, calls, rung = load()
    out: dict = {"generated": "thread B", "rubric": "B_rubric_v1"}

    # ---------------- call-level health
    ok = [c for c in calls if c.get("scored") and c["scored"].get("lmaaj") is not None]
    bad = [c for c in calls if c not in ok]
    cost = sum(c.get("cost_usd", 0.0) for c in calls)
    by_judge = Counter(c["judge"] for c in ok)
    print(f"calls: {len(calls)} total, {len(ok)} scored, {len(bad)} failed;  cost ${cost:.4f}")
    print("  scored per judge:", dict(by_judge))
    for c in bad:
        print("  FAILED", c["deck_id"], c["judge"], c["order"],
              str(c.get("parse_error") or c.get("api_error"))[:70])
    out["n_calls"] = len(calls)
    out["n_scored"] = len(ok)
    out["n_failed"] = len(bad)
    out["cost_usd"] = round(cost, 4)
    out["cost_by_model"] = {m: round(sum(c.get("cost_usd", 0) for c in calls if c["model"] == m), 4)
                            for m in sorted({c["model"] for c in calls})}
    out["coverage_mean"] = round(st.mean(c["scored"]["coverage"] for c in ok), 4)

    # ---------------- per-deck aggregation (frozen rule)
    deck = {}
    for did, pr in prompts.items():
        if pr["cell"] not in CELLS:
            continue
        cs = [c for c in ok if c["deck_id"] == did]
        rec = {"cell": pr["cell"], "seed": pr["seed"], "task": pr["task"],
               "treesim": pr.get("treesim"),
               "n_mismatch_total": pr.get("n_mismatch_total"),
               "rung1_fail": bool(pr.get("rung1_fail"))}
        if pr.get("rung1_fail"):
            rec.update(lmaaj=0.0, mismatch_credit=0.0, plausibility=0.0,
                       physics_fidelity=0.0, n_calls=0, floor=True, treesim=0.0)
        elif not cs:
            rec.update(lmaaj=None, n_calls=0, floor=False)
        else:
            rec.update(
                lmaaj=st.median(c["scored"]["lmaaj"] for c in cs),
                mismatch_credit=st.median(c["scored"]["mismatch_credit"] for c in cs),
                plausibility=st.median(c["scored"]["plausibility"] for c in cs),
                physics_fidelity=st.median(c["scored"]["physics_fidelity"] for c in cs),
                n_calls=len(cs), floor=False,
                per_judge={c["judge"] + "_" + c["order"]: round(c["scored"]["lmaaj"], 4) for c in cs},
            )
        rec.update(rung.get(did, {}))
        deck[did] = rec
    out["decks"] = deck

    # ---------------- score table
    print("\n=== SCORE TABLE (held-out, 10 tasks x 3 seeds) ===")
    hdr = f"{'Cell':14} {'TreeSim':>16}   {'LMaaJ':>16}   {'credit':>16} {'plaus':>7} {'physfid':>7}"
    print(hdr)
    table = {}
    for cell in CELLS:
        row = {}
        for key in ("treesim", "lmaaj", "mismatch_credit", "plausibility", "physics_fidelity"):
            sm = []
            for s in SEEDS:
                vs = [d[key] for d in deck.values()
                      if d["cell"] == cell and d["seed"] == s and d.get(key) is not None]
                if vs:
                    sm.append(sum(vs) / len(vs))
            row[key] = (st.mean(sm), st.stdev(sm) if len(sm) > 1 else 0.0, sm)
        table[cell] = row
        print(f"{CELL_LABEL[cell]:14} "
              f"{row['treesim'][0]:.4f} +- {row['treesim'][1]:.4f}   "
              f"{row['lmaaj'][0]:.4f} +- {row['lmaaj'][1]:.4f}   "
              f"{row['mismatch_credit'][0]:.4f} +- {row['mismatch_credit'][1]:.4f} "
              f"{row['plausibility'][0]:7.2f} {row['physics_fidelity'][0]:7.2f}")
    out["score_table"] = {c: {k: [round(v[0], 4), round(v[1], 4), [round(x, 4) for x in v[2]]]
                             for k, v in r.items()} for c, r in table.items()}

    # excluding the TutorialHydraulicFractureWithAdvancedXML artifact task
    print("\n=== SCORE TABLE excluding TutorialHydraulicFractureWithAdvancedXML "
          "(TreeSim artifact, 0.013 floor for every cell) ===")
    t9 = {}
    for cell in CELLS:
        row = {}
        for key in ("treesim", "lmaaj"):
            sm = []
            for s in SEEDS:
                vs = [d[key] for d in deck.values()
                      if d["cell"] == cell and d["seed"] == s
                      and d["task"] != "TutorialHydraulicFractureWithAdvancedXML"
                      and d.get(key) is not None]
                if vs:
                    sm.append(sum(vs) / len(vs))
            row[key] = (st.mean(sm), st.stdev(sm) if len(sm) > 1 else 0.0)
        t9[cell] = row
        print(f"{CELL_LABEL[cell]:14} TreeSim {row['treesim'][0]:.4f} +- {row['treesim'][1]:.4f}   "
              f"LMaaJ {row['lmaaj'][0]:.4f} +- {row['lmaaj'][1]:.4f}")
    out["score_table_9tasks"] = {c: {k: [round(v[0], 4), round(v[1], 4)] for k, v in r.items()}
                                 for c, r in t9.items()}

    # ---------------- severity spectrum
    print("\n=== SEVERITY SPECTRUM of TreeSim-flagged differences (order A, all judges) ===")
    spec = {}
    for cell in CELLS:
        cnt = Counter()
        for c in ok:
            if c["cell"] != cell or c["order"] != "A":
                continue
            cnt.update(c["scored"]["severity_labels"].values())
        tot = sum(cnt.values())
        spec[cell] = {k: round(cnt[k] / tot, 4) for k in CREDIT} | {"n": tot}
        print(f"{CELL_LABEL[cell]:14} n={tot:6}  " +
              "  ".join(f"{k}={cnt[k]/tot:6.1%}" for k in CREDIT))
    out["severity_spectrum"] = spec

    print("\n  by judge (all cells, order A):")
    jspec = {}
    for j in sorted({c["judge"] for c in ok}):
        cnt = Counter()
        for c in ok:
            if c["judge"] == j and c["order"] == "A":
                cnt.update(c["scored"]["severity_labels"].values())
        tot = sum(cnt.values())
        jspec[j] = {k: round(cnt[k] / tot, 4) for k in CREDIT} | {"n": tot}
        print(f"  {j:14} n={tot:6}  " + "  ".join(f"{k}={cnt[k]/tot:6.1%}" for k in CREDIT))
    out["severity_spectrum_by_judge"] = jspec

    # ---------------- agreement
    print("\n=== AGREEMENT ===")
    units = []
    per_deck_units = defaultdict(list)
    by_dm = defaultdict(dict)
    for c in ok:
        if c["order"] != "A":
            continue
        for mid, sev in c["scored"]["severity_labels"].items():
            by_dm[(c["deck_id"], mid)][c["judge"]] = sev
    for (did, mid), d in by_dm.items():
        if len(d) >= 2:
            units.append(list(d.values()))
            per_deck_units[did].append(list(d.values()))
    alpha, n_units = krippendorff_alpha_nominal(units)
    kappa, n_k = fleiss_kappa(units, list(CREDIT))
    exact = sum(1 for u in units if len(set(u)) == 1) / len(units) if units else float("nan")
    # collapsed 2-way: {cosmetic,minor} vs {material,severe}
    coll = [["low" if v in ("cosmetic", "minor") else "high" for v in u] for u in units]
    alpha2, _ = krippendorff_alpha_nominal(coll)
    exact2 = sum(1 for u in coll if len(set(u)) == 1) / len(coll) if coll else float("nan")
    print(f"  severity labels, 4-way: Krippendorff alpha = {alpha:.4f}  "
          f"Fleiss kappa = {kappa:.4f}  (n={n_units} entries x 3 judges)")
    print(f"  exact 3-way label agreement       = {exact:.1%}")
    print(f"  collapsed low/high: alpha = {alpha2:.4f}, exact agreement = {exact2:.1%}")
    out["agreement"] = {"alpha_4way": round(alpha, 4), "fleiss_kappa_4way": round(kappa, 4),
                        "n_units": n_units, "exact_3way": round(exact, 4),
                        "alpha_2way": round(alpha2, 4), "exact_2way": round(exact2, 4)}

    # deck-level judge-vs-judge correlation
    print("\n  per-deck LMaaJ, judge-vs-judge (order A):")
    jd = defaultdict(dict)
    for c in ok:
        if c["order"] == "A":
            jd[c["judge"]][c["deck_id"]] = c["scored"]["lmaaj"]
    js = sorted(jd)
    pairs = {}
    for a, b in combinations(js, 2):
        common = sorted(set(jd[a]) & set(jd[b]))
        x = [jd[a][d] for d in common]
        y = [jd[b][d] for d in common]
        r, rho = pearson(x, y), spearman(x, y)
        pairs[f"{a}|{b}"] = {"n": len(common), "pearson": round(r, 4), "spearman": round(rho, 4)}
        print(f"    {a:14} vs {b:14} n={len(common):3} pearson={r:+.3f} spearman={rho:+.3f}")
    print("  per-judge mean LMaaJ (order A):")
    jmean = {}
    for j in js:
        jmean[j] = round(st.mean(jd[j].values()), 4)
        print(f"    {j:14} {jmean[j]:.4f}  (n={len(jd[j])})")
    out["judge_pair_corr"] = pairs
    out["judge_mean_lmaaj"] = jmean

    # ---------------- THE robustness test: is the cell RANKING stable across judges?
    print("\n  per-judge cell means (order A, rung-1 floors included) -- ranking stability:")
    percell = {}
    for j in js:
        row = {}
        for cell in CELLS:
            sm = []
            for s in SEEDS:
                vals = []
                for did, pr in prompts.items():
                    if pr["cell"] != cell or pr["seed"] != s:
                        continue
                    if pr.get("rung1_fail"):
                        vals.append(0.0)
                        continue
                    cs = [c for c in ok if c["deck_id"] == did and c["judge"] == j
                          and c["order"] == "A"]
                    if cs:
                        vals.append(cs[0]["scored"]["lmaaj"])
                if vals:
                    sm.append(sum(vals) / len(vals))
            row[cell] = [round(st.mean(sm), 4), round(st.stdev(sm), 4) if len(sm) > 1 else 0.0]
        rank = sorted(CELLS, key=lambda c: -row[c][0])
        percell[j] = {"means": row, "rank": rank}
        print(f"    {j:14} " + "  ".join(f"{c}={row[c][0]:.4f}" for c in CELLS)
              + f"   rank: {' > '.join(rank)}")
    ranks = {tuple(v["rank"]) for v in percell.values()}
    print(f"    -> {len(ranks)} distinct cell rankings across {len(js)} judges")
    n_f0_last = sum(1 for v in percell.values() if v["rank"][-1] == "F0")
    print(f"    -> Vanilla (F0) ranked last by {n_f0_last}/{len(js)} judges")
    out["per_judge_cell_means"] = percell
    out["n_distinct_rankings"] = len(ranks)
    out["n_judges_ranking_F0_last"] = n_f0_last


    # ---------------- position bias
    print("\n=== POSITION BIAS (order A vs order B, seed-1 subsample) ===")
    pb = {}
    allsh = []
    for j in js:
        A = {c["deck_id"]: c["scored"]["lmaaj"] for c in ok if c["judge"] == j and c["order"] == "A"}
        B = {c["deck_id"]: c["scored"]["lmaaj"] for c in ok if c["judge"] == j and c["order"] == "B"}
        common = sorted(set(A) & set(B))
        if not common:
            continue
        sh = [B[d] - A[d] for d in common]
        allsh += sh
        pb[j] = {"n": len(common), "mean_signed": round(st.mean(sh), 4),
                 "mean_abs": round(st.mean(abs(s) for s in sh), 4),
                 "max_abs": round(max(abs(s) for s in sh), 4),
                 "sd": round(st.stdev(sh), 4) if len(sh) > 1 else 0.0}
        print(f"  {j:14} n={len(common):3} mean(B-A)={st.mean(sh):+.4f} "
              f"mean|B-A|={st.mean(abs(s) for s in sh):.4f} max|B-A|={max(abs(s) for s in sh):.4f}")
    if allsh:
        pb["pooled"] = {"n": len(allsh), "mean_signed": round(st.mean(allsh), 4),
                        "mean_abs": round(st.mean(abs(s) for s in allsh), 4)}
        print(f"  {'POOLED':14} n={len(allsh):3} mean(B-A)={st.mean(allsh):+.4f} "
              f"mean|B-A|={st.mean(abs(s) for s in allsh):.4f}")
    out["position_bias"] = pb

    # ---------------- TreeSim correlation and divergence
    print("\n=== LMaaJ vs TreeSim ===")
    ds = [d for d in deck.values() if d.get("lmaaj") is not None and d.get("treesim") is not None]
    x = [d["treesim"] for d in ds]
    y = [d["lmaaj"] for d in ds]
    print(f"  all {len(ds)} decks: pearson={pearson(x,y):+.3f} spearman={spearman(x,y):+.3f}")
    ds9 = [d for d in ds if d["task"] != "TutorialHydraulicFractureWithAdvancedXML"]
    x9 = [d["treesim"] for d in ds9]
    y9 = [d["lmaaj"] for d in ds9]
    print(f"  excl. HydraulicFractureAdvancedXML ({len(ds9)}): "
          f"pearson={pearson(x9,y9):+.3f} spearman={spearman(x9,y9):+.3f}")
    out["treesim_corr"] = {
        "all": {"n": len(ds), "pearson": round(pearson(x, y), 4), "spearman": round(spearman(x, y), 4)},
        "excl_advxml": {"n": len(ds9), "pearson": round(pearson(x9, y9), 4),
                        "spearman": round(spearman(x9, y9), 4)},
    }

    print("\n  largest divergences (LMaaJ - TreeSim), the cases TreeSim gets wrong:")
    div = sorted(ds, key=lambda d: -(d["lmaaj"] - d["treesim"]))
    for d in div[:10]:
        print(f"    +{d['lmaaj']-d['treesim']:.3f}  {d['cell']:3} s{d['seed']} "
              f"{d['task'][:42]:43} TreeSim={d['treesim']:.3f} LMaaJ={d['lmaaj']:.3f} "
              f"credit={d['mismatch_credit']:.3f} nmis={d['n_mismatch_total']}")
    print("  ... and the other direction (LMaaJ harsher than TreeSim):")
    for d in div[-5:]:
        print(f"    {d['lmaaj']-d['treesim']:+.3f}  {d['cell']:3} s{d['seed']} "
              f"{d['task'][:42]:43} TreeSim={d['treesim']:.3f} LMaaJ={d['lmaaj']:.3f}")
    out["divergences"] = [
        {k: d[k] for k in ("cell", "seed", "task", "treesim", "lmaaj", "mismatch_credit",
                           "plausibility", "physics_fidelity", "n_mismatch_total")}
        for d in div]

    # ---------------- execution calibration
    print("\n=== EXECUTION CALIBRATION (Thread A1 rungs 1-2) ===")
    cal = {}
    for r in ("rung1", "rung2", "rung3", "rung3_geosx", "rung4_runs"):
        pool = [d for d in deck.values() if r in d and d.get("lmaaj") is not None]
        if not pool:
            continue
        p = [d for d in pool if str(d[r]) in ("1", "True", "pass")]
        f = [d for d in pool if d not in p]
        if not f:
            print(f"  {r}: {len(p)}/{len(pool)} pass, 0 fail -- no contrast available")
            cal[r] = {"n_pass": len(p), "n_fail": 0}
            continue
        for metric in ("lmaaj", "treesim"):
            vp = [d[metric] for d in p]
            vf = [d[metric] for d in f]
            u, pv = mannwhitney_u_p(vf, vp)
            # point-biserial
            xs = [1.0 if d in p else 0.0 for d in pool]
            ys = [d[metric] for d in pool]
            print(f"  {r} {metric:8}: pass n={len(vp)} mean={st.mean(vp):.4f} | "
                  f"fail n={len(vf)} mean={st.mean(vf):.4f} | "
                  f"r_pb={pearson(xs,ys):+.3f} MWU p={pv:.4f}")
            cal.setdefault(r, {})[metric] = {
                "n_pass": len(vp), "mean_pass": round(st.mean(vp), 4),
                "n_fail": len(vf), "mean_fail": round(st.mean(vf), 4),
                "r_pointbiserial": round(pearson(xs, ys), 4), "mwu_p": round(pv, 5),
            }
        cal[r]["fail_decks"] = [f"{d['cell']}_s{d['seed']}_{d['task']}" for d in f]
    out["execution_calibration"] = cal

    # ---------------- the decisive subset: (task, seed) where EVERY cell is schema-valid
    # If LMaaJ only reproduces the rung-1/2 lexical+schema signal it adds nothing.
    # The test is whether it separates cells among runs where all cells cleared rung 2.
    print("\n=== SUBSET: (task, seed) pairs where ALL SIX cells passed rung 2 ===")
    p = ART / "A1_rungs12_perfile.csv"
    clean = set()
    if p.exists():
        byts = defaultdict(lambda: defaultdict(list))
        for r in csv.DictReader(p.open()):
            byts[(r["task"], r["seed"].lstrip("s"))][r["cell"]].append(r)
        for ts, cells in byts.items():
            if len(cells) < 6:
                continue
            if all(all(x["rung2"] == "1" for x in v) for v in cells.values()):
                clean.add(ts)
    print(f"  {len(clean)} of 30 (task, seed) pairs are clean for all six cells")
    sub = [d for d in deck.values()
           if (d["task"], str(d["seed"])) in clean and d.get("lmaaj") is not None]
    print(f"  -> {len(sub)} decks across the three cells reported here")
    subtab = {}
    for cell in CELLS:
        vs_t = [d["treesim"] for d in sub if d["cell"] == cell]
        vs_l = [d["lmaaj"] for d in sub if d["cell"] == cell]
        vs_c = [d["mismatch_credit"] for d in sub if d["cell"] == cell]
        if not vs_l:
            continue
        subtab[cell] = {
            "n": len(vs_l),
            "treesim": [round(st.mean(vs_t), 4),
                        round(st.stdev(vs_t), 4) if len(vs_t) > 1 else 0.0],
            "lmaaj": [round(st.mean(vs_l), 4),
                      round(st.stdev(vs_l), 4) if len(vs_l) > 1 else 0.0],
            "credit": [round(st.mean(vs_c), 4),
                       round(st.stdev(vs_c), 4) if len(vs_c) > 1 else 0.0],
        }
        print(f"  {CELL_LABEL[cell]:14} n={len(vs_l):3}  "
              f"TreeSim {st.mean(vs_t):.4f} (sd {st.stdev(vs_t):.4f})   "
              f"LMaaJ {st.mean(vs_l):.4f} (sd {st.stdev(vs_l):.4f})   "
              f"credit {st.mean(vs_c):.4f}")
    for a, b in combinations([c for c in CELLS if c in subtab], 2):
        for metric in ("treesim", "lmaaj"):
            va = [d[metric] for d in sub if d["cell"] == a]
            vb = [d[metric] for d in sub if d["cell"] == b]
            _, pv = mannwhitney_u_p(va, vb)
            print(f"    {a} vs {b}  {metric:8} delta={st.mean(vb)-st.mean(va):+.4f}  MWU p={pv:.4f}")
            subtab.setdefault("contrasts", {})[f"{a}|{b}|{metric}"] = {
                "delta": round(st.mean(vb) - st.mean(va), 4), "mwu_p": round(pv, 5)}
    out["clean_subset"] = {"n_task_seed_pairs": len(clean),
                           "task_seed_pairs": sorted(f"{t}_s{s}" for t, s in clean),
                           "table": subtab}

    # nuisance variance vs the effect being measured
    cell_range = (max(table[c]["lmaaj"][0] for c in CELLS)
                  - min(table[c]["lmaaj"][0] for c in CELLS))
    ts_range = (max(table[c]["treesim"][0] for c in CELLS)
                - min(table[c]["treesim"][0] for c in CELLS))
    judge_range = max(jmean.values()) - min(jmean.values())
    pos = out["position_bias"].get("pooled", {}).get("mean_abs", float("nan"))
    print(f"\n  NUISANCE vs SIGNAL:")
    print(f"    cell-effect range (LMaaJ)   = {cell_range:.4f}")
    print(f"    cell-effect range (TreeSim) = {ts_range:.4f}")
    print(f"    judge-choice range          = {judge_range:.4f}  "
          f"({judge_range/cell_range:.2f}x the cell effect)")
    print(f"    position instability        = {pos:.4f}  ({pos/cell_range:.2f}x the cell effect)")
    out["nuisance_vs_signal"] = {
        "cell_range_lmaaj": round(cell_range, 4), "cell_range_treesim": round(ts_range, 4),
        "judge_range": round(judge_range, 4),
        "judge_over_cell": round(judge_range / cell_range, 2),
        "position_instability": round(pos, 4),
        "position_over_cell": round(pos / cell_range, 2),
    }

    (ART / "B_analysis.json").write_text(json.dumps(out, indent=1, default=str))
    with (ART / "B_deck_scores.csv").open("w", newline="") as fh:
        cols = ["cell", "seed", "task", "treesim", "lmaaj", "mismatch_credit", "plausibility",
                "physics_fidelity", "n_mismatch_total", "n_calls", "rung1", "rung2", "rung3",
                "rung3_geosx", "rung4_runs", "rung1_fail", "floor"]
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for d in sorted(deck.values(), key=lambda z: (z["cell"], z["seed"], z["task"])):
            w.writerow(d)
    print(f"\nwrote {ART/'B_analysis.json'} and {ART/'B_deck_scores.csv'}")


if __name__ == "__main__":
    main()
