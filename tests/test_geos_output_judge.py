from pathlib import Path

from eval.geos_output_judge import (
    SimulationPair,
    _parse_verdict,
    discover_pairs,
)


def test_discover_pairs_and_unmatched(tmp_path: Path) -> None:
    candidate = tmp_path / "candidate"
    ground_truth = tmp_path / "ground_truth"
    for root, names in (
        (candidate, ("same_case", "candidate_only")),
        (ground_truth, ("same_case", "ground_truth_only")),
    ):
        root.mkdir()
        for name in names:
            (root / name).mkdir()

    pairs, candidate_only, ground_truth_only = discover_pairs(
        candidate, ground_truth
    )

    assert pairs == [
        SimulationPair(
            "same_case", candidate / "same_case", ground_truth / "same_case"
        )
    ]
    assert candidate_only == ["candidate_only"]
    assert ground_truth_only == ["ground_truth_only"]


def test_flat_pair(tmp_path: Path) -> None:
    candidate = tmp_path / "candidate"
    ground_truth = tmp_path / "ground_truth"
    candidate.mkdir()
    ground_truth.mkdir()

    pairs, candidate_only, ground_truth_only = discover_pairs(
        candidate, ground_truth, flat=True
    )

    assert len(pairs) == 1
    assert pairs[0].candidate == candidate
    assert pairs[0].ground_truth == ground_truth
    assert candidate_only == []
    assert ground_truth_only == []


def test_parse_fenced_verdict() -> None:
    result = _parse_verdict(
        """```json
{"same": true, "confidence": 0.9, "summary": "equivalent"}
```"""
    )
    assert result["same"] is True
    assert result["confidence"] == 0.9
    assert result["evidence"] == []

