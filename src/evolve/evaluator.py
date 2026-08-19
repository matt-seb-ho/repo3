"""Turn a candidate adapter into per-task scores.

This is the edge v1 was missing. ``run_full_evolution.sh`` alternated
``run_round.sh`` and ``reflect.py`` with **no scoring step between them**; the
only thing that writes ``<task>_eval.json`` is ``scripts/eval/batch_evaluate.py``
and it was never called. So ``gather_round()`` found no eval files, every task
came back ``treesim=None``, and ``mean_ts`` was 0 — which is exactly what every
``plugin_evolving/v*/.reflection_meta.json`` records.

Here run-then-score is one operation that cannot be half-performed, it returns
**per-task** scores (a Pareto frontier over tasks is the right selection
structure for a tail-driven objective, not a scalar mean), and results are
cached by candidate content hash so re-selecting an archived candidate is free.

Nothing in ``src/runner`` or ``src/eval`` is modified; both are invoked as
subprocesses exactly as the existing ``launch_*.sh`` scripts do.
"""

from __future__ import annotations

import json
import os
import shutil
import statistics
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Sequence

from evolve.candidate import Candidate

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_AGENT = "abl_se_round"


@dataclass
class EvalResult:
    """Per-task outcome for one candidate at one seed."""

    candidate_id: str
    seed: int
    scores: dict[str, float] = field(default_factory=dict)
    statuses: dict[str, str] = field(default_factory=dict)
    cost: dict[str, float] = field(default_factory=dict)
    run_name: str = ""
    error: str | None = None

    @property
    def mean(self) -> float:
        return statistics.mean(self.scores.values()) if self.scores else 0.0

    @property
    def zero_tasks(self) -> list[str]:
        return sorted(t for t, s in self.scores.items() if s <= 1e-9)

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "seed": self.seed,
            "run_name": self.run_name,
            "scores": self.scores,
            "statuses": self.statuses,
            "cost": self.cost,
            "mean": self.mean,
            "zero_tasks": self.zero_tasks,
            "error": self.error,
        }


def merge_seeds(results: Sequence[EvalResult]) -> dict[str, float]:
    """Mean per task across seeds, under failures-as-zero.

    A task that failed to produce output at one seed contributes 0 at that seed
    rather than being dropped, which is the convention the headline numbers use
    and the only one under which the reliability story is coherent.
    """
    by_task: dict[str, list[float]] = {}
    for r in results:
        for task, score in r.scores.items():
            by_task.setdefault(task, []).append(score)
    return {t: statistics.mean(v) for t, v in sorted(by_task.items()) if v}


@dataclass
class EvaluatorConfig:
    """Paths and knobs. Every default is overridable — v1 hardcoded
    ``/home/matt/sci/repo3`` and ``/data/shared/...``, neither of which survives
    a move to a different machine."""

    results_root: Path
    experiments_dir: Path
    ground_truth_dir: Path
    scaffolding_dir: Path = REPO_ROOT / "plugin"
    work_dir: Path = REPO_ROOT / ".evolve" / "candidates"
    cache_dir: Path = REPO_ROOT / ".evolve" / "cache"
    agent: str = DEFAULT_AGENT
    model: str = "deepseek-v4-flash"
    workers: int = 4
    timeout_s: int = 1500
    tmp_geos_parent: Path | None = None
    python: str = sys.executable
    dry_run: bool = False

    def validate(self) -> list[str]:
        """Return human-readable reasons this config cannot run here."""
        problems = []
        for name in ("experiments_dir", "ground_truth_dir", "scaffolding_dir"):
            p = Path(getattr(self, name))
            if not p.exists():
                problems.append(f"{name} does not exist: {p}")
        if shutil.which("docker") is None:
            problems.append("docker not on PATH (the runner launches containers)")
        return problems


class Evaluator:
    """Run a candidate over a task slice and score it, with caching."""

    def __init__(self, config: EvaluatorConfig) -> None:
        self.cfg = config
        self.cfg.work_dir.mkdir(parents=True, exist_ok=True)
        self.cfg.cache_dir.mkdir(parents=True, exist_ok=True)

    # -- caching ----------------------------------------------------------
    def _cache_path(self, candidate: Candidate, tasks: Sequence[str], seed: int) -> Path:
        import hashlib

        key = hashlib.sha256(
            (candidate.cid + "|" + ",".join(sorted(tasks)) + f"|s{seed}").encode()
        ).hexdigest()[:16]
        return self.cfg.cache_dir / f"{key}.json"

    def _load_cached(self, path: Path) -> EvalResult | None:
        if not path.exists():
            return None
        try:
            d = json.loads(path.read_text())
        except Exception:
            return None
        return EvalResult(
            candidate_id=d["candidate_id"],
            seed=d["seed"],
            scores=d.get("scores", {}),
            statuses=d.get("statuses", {}),
            cost=d.get("cost", {}),
            run_name=d.get("run_name", ""),
            error=d.get("error"),
        )

    # -- the two phases ---------------------------------------------------
    def _run_cmd(self, candidate: Candidate, adapter_dir: Path, run_name: str,
                 tasks: Sequence[str]) -> list[str]:
        primer = adapter_dir / candidate.manifest.path_for("primer")
        cmd = [
            self.cfg.python, str(REPO_ROOT / "scripts" / "run_experiment.py"),
            "--run", run_name,
            "--agents", self.cfg.agent,
            "--workers", str(self.cfg.workers),
            "--timeout", str(self.cfg.timeout_s),
            "--strip-baked-primer",
            "--geos-primer-path", str(primer),
            "--plugin-dir", str(adapter_dir),
            "--experiments-dir", str(self.cfg.experiments_dir),
            "--ground-truth-dir", str(self.cfg.ground_truth_dir),
            "--results-root-dir", str(self.cfg.results_root),
            "--claude-model", self.cfg.model,
            "--include", *tasks,
        ]
        if self.cfg.tmp_geos_parent:
            cmd += ["--tmp-geos-parent", str(self.cfg.tmp_geos_parent)]
        return cmd

    def _score_cmd(self, run_name: str) -> list[str]:
        return [
            self.cfg.python, str(REPO_ROOT / "scripts" / "eval" / "batch_evaluate.py"),
            "--experiments-dir", str(self.cfg.results_root / self.cfg.agent / run_name),
            "--ground-truth-dir", str(self.cfg.ground_truth_dir),
            "--results-dir", str(self.cfg.results_root / "_results" / run_name / self.cfg.agent),
        ]

    def _collect(self, run_name: str, tasks: Sequence[str]) -> tuple[dict, dict]:
        """Read the scores the scoring phase just wrote.

        Iterates the *requested task list*, not the directory listing —
        ``reflect.py:113`` iterated every subdirectory of the run dir and so
        fed at least one non-task directory to the proposer as a task
        (``v1/.reflection_meta.json`` records ``round_n_tasks: 7`` for a
        six-task round).
        """
        eval_dir = self.cfg.results_root / "_results" / run_name / self.cfg.agent
        scores: dict[str, float] = {}
        statuses: dict[str, str] = {}
        for task in tasks:
            p = eval_dir / f"{task}_eval.json"
            if not p.exists():
                scores[task] = 0.0
                statuses[task] = "missing_eval"
                continue
            try:
                d = json.loads(p.read_text())
            except Exception as exc:
                scores[task] = 0.0
                statuses[task] = f"unreadable_eval: {type(exc).__name__}"
                continue
            ts = d.get("treesim")
            statuses[task] = str(d.get("status", "?"))
            scores[task] = float(ts) if isinstance(ts, (int, float)) else 0.0
        return scores, statuses

    def _collect_cost(self, run_name: str, tasks: Sequence[str]) -> dict[str, float]:
        """Tool-call and wall-clock totals, for the efficiency clause of the gate."""
        cost = {"tool_calls": 0.0, "wall_seconds": 0.0}
        base = self.cfg.results_root / self.cfg.agent / run_name
        for task in tasks:
            tc = base / task / "tool_calls.json"
            if tc.exists():
                try:
                    data = json.loads(tc.read_text())
                    cost["tool_calls"] += float(
                        data.get("total") if isinstance(data, dict) else len(data)
                    )
                except Exception:
                    pass
            meta = base / task / "meta.json"
            if meta.exists():
                try:
                    cost["wall_seconds"] += float(
                        json.loads(meta.read_text()).get("wall_seconds") or 0.0
                    )
                except Exception:
                    pass
        return cost

    # -- public API -------------------------------------------------------
    def evaluate(
        self,
        candidate: Candidate,
        tasks: Sequence[str],
        *,
        seed: int = 1,
        use_cache: bool = True,
    ) -> EvalResult:
        cache = self._cache_path(candidate, tasks, seed)
        if use_cache:
            hit = self._load_cached(cache)
            if hit is not None:
                return hit

        run_name = f"ev_{candidate.cid}_s{seed}"
        adapter_dir = self.cfg.work_dir / candidate.cid
        result = EvalResult(candidate_id=candidate.cid, seed=seed, run_name=run_name)

        try:
            candidate.materialize(
                adapter_dir,
                scaffolding_from=self.cfg.scaffolding_dir,
                overwrite=True,
            )
        except Exception as exc:
            result.error = f"materialize failed: {type(exc).__name__}: {exc}"
            return result

        env = dict(os.environ)
        env.update(candidate.manifest.stop_policy.to_env())

        if self.cfg.dry_run:
            result.error = "dry_run"
            result.cost = {"cmd_run": " ".join(
                self._run_cmd(candidate, adapter_dir, run_name, tasks))}
            return result

        for phase, cmd in (
            ("run", self._run_cmd(candidate, adapter_dir, run_name, tasks)),
            ("score", self._score_cmd(run_name)),
        ):
            proc = subprocess.run(
                cmd, env=env, cwd=str(REPO_ROOT), capture_output=True, text=True
            )
            if proc.returncode != 0:
                # Do not abort: a partially-completed round still yields
                # per-task scores, and failures-as-zero handles the rest.
                result.error = (
                    f"{phase} phase exit {proc.returncode}: "
                    + (proc.stderr or proc.stdout or "")[-800:]
                )

        result.scores, result.statuses = self._collect(run_name, tasks)
        result.cost = self._collect_cost(run_name, tasks)
        cache.write_text(json.dumps(result.to_dict(), indent=2))
        return result

    def evaluate_multi_seed(
        self, candidate: Candidate, tasks: Sequence[str], seeds: Sequence[int] = (1, 2)
    ) -> tuple[dict[str, float], list[EvalResult]]:
        results = [self.evaluate(candidate, tasks, seed=s) for s in seeds]
        return merge_seeds(results), results
