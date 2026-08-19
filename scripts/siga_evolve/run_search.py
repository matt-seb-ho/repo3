#!/usr/bin/env python3
"""SIGA-Evolve v2 search driver.

The loop v1 should have been. Per iteration:

    1. select a parent from the Pareto frontier over per-task scores
    2. build the layered evidence corpus for that parent's last evaluation
    3. ask the proposer for ONE minimal edit plus a falsifiable prediction
    4. free gates: manifest validity, token budgets, hygiene, check-plugin tests
       -- all before a single rollout is spent
    5. evaluate the child on the FIXED anchor slice at n seeds
    6. regression gate: no per-task cliff, no aggregate regression, no new
       failures-as-zero, no efficiency regression
    7. record the decision (prediction vs outcome) and archive the candidate

Round structure fixes v1's confound directly. v1 ran rounds 0/1/2 on disjoint
6/6/5-task thirds, so round-over-round score changes conflated adapter quality
with task difficulty. Here every candidate is scored on the same anchor slice;
a separate probe slice supplies fresh failure modes to the proposer but is never
scored for selection; and the held-out split is touched exactly once, at the
end, by the single selected candidate.

Usage (dry run costs nothing and prints the commands it would issue):

    python3 scripts/siga_evolve/run_search.py \
        --seed-dir .evolve/seed \
        --anchor-tasks-file misc/evolve_anchor.txt \
        --results-root /data/shared/.../siga_evolve_2026-08 \
        --experiments-dir /data/shared/.../experiments_test36_template \
        --ground-truth-dir /data/shared/.../experiments_gt \
        --budget 20 --seeds 2 --dry-run
"""
from __future__ import annotations

import argparse
import json
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from evolve.acceptance import DecisionRecord, RegressionGate  # noqa: E402
from evolve.archive import Archive, ArchiveEntry, select_parent_via_gepa  # noqa: E402
from evolve.candidate import Candidate  # noqa: E402
from evolve.checks import validate_plugins  # noqa: E402
from evolve.evaluator import Evaluator, EvaluatorConfig, merge_seeds  # noqa: E402
from evolve.evidence import RoundEvidence, TaskEvidence, build_round_evidence, load_categories  # noqa: E402
from evolve.hygiene import GroundTruthCorpus, check_candidate  # noqa: E402
from evolve.proposer import ProposerConfig, ProposerError, propose  # noqa: E402


def read_tasks(path: Path) -> list[str]:
    return [
        line.strip()
        for line in Path(path).read_text().splitlines()
        if line.strip() and not line.startswith("#")
    ]


def log(msg: str, path: Path | None = None) -> None:
    stamp = datetime.now(timezone.utc).strftime("%H:%M:%S")
    line = f"[{stamp}] {msg}"
    print(line, flush=True)
    if path:
        with path.open("a") as f:
            f.write(line + "\n")


def evidence_for(entry: ArchiveEntry, tasks, cfg, args, categories) -> RoundEvidence:
    """Best-effort evidence corpus; degrade to L1 if trajectories are absent."""
    run_name = f"ev_{entry.cid}_s{args.seeds and 1}"
    try:
        return build_round_evidence(
            entry.cid,
            tasks,
            traj_root=cfg.results_root,
            eval_root=cfg.results_root / "_results",
            agent=cfg.agent,
            run=run_name,
            parent_scores=entry.scores,
            categories=categories,
        )
    except Exception:
        return RoundEvidence(
            candidate_id=entry.cid,
            tasks=[
                TaskEvidence(task=t, run=run_name, treesim=entry.scores.get(t))
                for t in tasks
            ],
        )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--seed-dir", type=Path, required=True)
    ap.add_argument("--anchor-tasks-file", type=Path, required=True,
                    help="the FIXED slice every candidate is scored on")
    ap.add_argument("--results-root", type=Path, required=True)
    ap.add_argument("--experiments-dir", type=Path, required=True)
    ap.add_argument("--ground-truth-dir", type=Path, required=True)
    ap.add_argument("--plugin-dir", type=Path, default=REPO_ROOT / "plugin",
                    help="scaffolding source; resolved fresh per candidate")
    ap.add_argument("--out-dir", type=Path, default=REPO_ROOT / ".evolve" / "run")
    ap.add_argument("--budget", type=int, default=20, help="max candidates")
    ap.add_argument("--seeds", type=int, default=2)
    ap.add_argument("--model", default="deepseek-v4-flash", help="inference model")
    ap.add_argument("--proposer-model", default="gemini-3-flash-preview",
                    help="deliberately NOT the inference model")
    ap.add_argument("--bottleneck-dir", type=Path,
                    help="per-task failure categories from the bottleneck classifier")
    ap.add_argument("--max-task-regression", type=float, default=0.05)
    ap.add_argument("--max-efficiency-ratio", type=float, default=1.15)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    log_path = args.out_dir / "search.log"
    anchor = read_tasks(args.anchor_tasks_file)
    log(f"anchor slice: {len(anchor)} tasks -> {', '.join(anchor)}", log_path)

    # -- preflight: fail loudly and early ---------------------------------
    cfg = EvaluatorConfig(
        results_root=args.results_root,
        experiments_dir=args.experiments_dir,
        ground_truth_dir=args.ground_truth_dir,
        scaffolding_dir=args.plugin_dir,
        model=args.model,
        dry_run=args.dry_run,
    )
    problems = cfg.validate()
    if problems and not args.dry_run:
        for p in problems:
            log(f"PREFLIGHT FAIL: {p}", log_path)
        log("refusing to start a search that cannot evaluate anything", log_path)
        return 2

    plugin_reports = validate_plugins(REPO_ROOT / "hooks" / "checks")
    for r in plugin_reports:
        log(f"check plugin {r.name}: ok={r.ok} {r.error or ''}", log_path)
    if any(not r.ok for r in plugin_reports):
        log("a check plugin is broken; fix it before searching", log_path)
        return 2

    corpus = GroundTruthCorpus.from_ground_truth_dir(args.ground_truth_dir) \
        if args.ground_truth_dir.exists() else GroundTruthCorpus()
    corpus.extend_from_contamination(anchor, args.ground_truth_dir)
    log(
        f"hygiene corpus: {len(corpus.task_ids)} tasks, "
        f"{len(corpus.blocked_basenames)} blocked basenames, "
        f"{len(corpus.numeric_literals)} GT numerics",
        log_path,
    )

    evaluator = Evaluator(cfg)
    gate = RegressionGate(
        max_task_regression=args.max_task_regression,
        max_efficiency_ratio=args.max_efficiency_ratio,
    )
    archive = Archive()
    categories = load_categories(args.bottleneck_dir) if args.bottleneck_dir else {}
    decisions: list[dict] = []
    prop_cfg = ProposerConfig(model=args.proposer_model)

    # -- seed --------------------------------------------------------------
    seed = Candidate.from_dir(args.seed_dir)
    seed.validate()
    log(f"seed candidate {seed.cid}", log_path)
    seed_scores, _ = evaluator.evaluate_multi_seed(
        seed, anchor, seeds=tuple(range(1, args.seeds + 1))
    )
    seed_entry = archive.add(
        ArchiveEntry(seed, scores=seed_scores, accepted=True, reason="seed")
    )
    log(f"seed mean={seed_entry.mean:.4f}", log_path)

    # -- search ------------------------------------------------------------
    n_proposed = 0
    while n_proposed < args.budget:
        n_proposed += 1
        parent = select_parent_via_gepa(archive) or seed_entry
        log(f"--- iter {n_proposed}/{args.budget}: parent {parent.cid} "
            f"(mean {parent.mean:.4f})", log_path)

        evidence = evidence_for(parent, anchor, cfg, args, categories)
        try:
            child = propose(
                parent.candidate, evidence, cfg=prop_cfg, history=decisions[-6:]
            )
        except ProposerError as exc:
            log(f"    proposal rejected (malformed): {exc}", log_path)
            continue
        except Exception:
            log(f"    proposer crashed:\n{traceback.format_exc()}", log_path)
            continue

        # free gates, in cost order
        hyg = check_candidate(child, corpus)
        if hyg.blocked:
            log(f"    HYGIENE BLOCK: {hyg.findings[0]}", log_path)
            archive.add(
                ArchiveEntry(child, accepted=False, reason=f"hygiene: {hyg.findings[0]}",
                             generation=child.generation)
            )
            continue

        if archive.get(child.cid):
            log("    duplicate candidate (content hash already seen); skipping", log_path)
            continue

        # paid gate
        child_scores, child_results = evaluator.evaluate_multi_seed(
            child, anchor, seeds=tuple(range(1, args.seeds + 1))
        )
        child_cost = child_results[0].cost if child_results else {}
        result = gate.evaluate(
            child_scores,
            parent.scores,
            child_cost=child_cost,
            parent_cost=parent.cost,
            hygiene_ok=True,
            checks_ok=True,
        )
        entry = archive.add(
            ArchiveEntry(
                child,
                scores=child_scores,
                cost=child_cost,
                accepted=result.accepted,
                reason=result.reason,
                generation=child.generation,
            )
        )
        log(f"    {'ACCEPT' if result.accepted else 'REJECT'} {entry.cid} "
            f"mean={entry.mean:.4f}: {result.reason}", log_path)

        pred = child.predictions[0] if child.predictions else None
        rec = DecisionRecord(
            candidate_id=child.cid,
            parent_id=parent.cid,
            component=pred.component if pred else "?",
            predicted_beneficiaries=list(pred.predicted_beneficiaries) if pred else [],
            predicted_delta=pred.predicted_delta if pred else 0.0,
            observed_deltas=result.metrics.get("per_task_deltas", {}),
            gate=result,
        )
        decisions.append(rec.to_dict())
        with (args.out_dir / "decision_log.jsonl").open("a") as f:
            f.write(json.dumps(rec.to_dict()) + "\n")
        if rec.is_unearned:
            log("    NOTE: accepted but no predicted beneficiary moved "
                "(over-specification signal)", log_path)

        archive.save(args.out_dir / "archive.json")

    # -- report ------------------------------------------------------------
    log("\n" + archive.summary(), log_path)
    best = archive.best()
    if best:
        best_dir = args.out_dir / "best"
        best.candidate.materialize(
            best_dir, scaffolding_from=args.plugin_dir, overwrite=True
        )
        log(f"best candidate {best.cid} materialized at {best_dir}", log_path)
        log("NOTE: the held-out split has NOT been touched. Evaluate this "
            "candidate on it exactly once, alongside the compute-matched "
            "baselines (see docs/2026-08-19_method-adoption-plan.md sec 4.1).",
            log_path)

    hit_rates = [d["prediction_hit_rate"] for d in decisions
                 if d.get("prediction_hit_rate") is not None]
    if hit_rates:
        log(f"proposer calibration: mean prediction hit rate "
            f"{sum(hit_rates)/len(hit_rates):.2f} over {len(hit_rates)} proposals",
            log_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
