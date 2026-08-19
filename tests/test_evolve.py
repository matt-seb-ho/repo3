"""Tests for SIGA-Evolve v2.

Several of these are regression tests for defects found in the v1 loop while
writing docs/2026-08-19_method-adoption-plan.md; each names the defect it locks
out.
"""
from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from evolve.acceptance import DecisionRecord, RegressionGate
from evolve.archive import Archive, ArchiveEntry, pareto_front
from evolve.candidate import Candidate, CandidateError, Prediction, estimate_tokens
from evolve.checks import (
    CheckContext, Deck, render_constraints_prose, render_feedback, run_checks,
    validate_plugins,
)
from evolve.hygiene import (
    GroundTruthCorpus, canonical_numerics, canonicalize_number, check_texts,
)
from evolve.manifest import Manifest, ManifestError
from evolve.proposer import ProposerError, propose

REPO_ROOT = Path(__file__).resolve().parents[1]

MANIFEST_TOML = """
[meta]
generation = 0
[components.primer]
kind = "prose"
path = "PRIMER.md"
budget_tokens = 100
[components.memory]
kind = "itemized"
path = "memory/cheatsheet.md"
budget_tokens = 200
[components.stop_policy]
kind = "config"
retries = 2
feedback_shape = "structured_errors"
checks = ["parse", "geosx_validate"]
"""


@pytest.fixture
def manifest() -> Manifest:
    return Manifest.from_toml(MANIFEST_TOML)


@pytest.fixture
def candidate(manifest: Manifest) -> Candidate:
    return Candidate(
        manifest=manifest,
        files={"PRIMER.md": "seed primer", "memory/cheatsheet.md": "- one"},
    )


# --------------------------------------------------------------------------
# manifest
# --------------------------------------------------------------------------

def test_stop_policy_is_searchable(manifest):
    """v1 could not touch S at all: copy_scaffolding() made it untouchable."""
    assert manifest.stop_policy.retries == 2
    env = manifest.stop_policy.to_env()
    assert env["GEOS_HOOK_MAX_RETRIES"] == "2"
    assert env["GEOS_HOOK_XMLLINT"] == "1"


def test_manifest_rejects_path_escape():
    with pytest.raises(ManifestError):
        Manifest.from_toml(
            '[components.x]\nkind = "prose"\npath = "../../etc/passwd"\n'
        )


def test_manifest_rejects_unknown_check():
    with pytest.raises(ManifestError):
        Manifest.from_toml(
            '[components.stop_policy]\nkind = "config"\nchecks = ["rm_rf"]\n'
        )


def test_writable_set_comes_from_manifest(manifest):
    assert manifest.is_writable("memory/cheatsheet.md")
    # Scaffolding is never candidate-owned; it is resolved from plugin/ at
    # materialization time so the lineage cannot fork a stale validator, which
    # is what happened to plugin_evolving/v*/hooks/verify_outputs.py.
    assert not manifest.is_writable("hooks/verify_outputs.py")
    assert not manifest.is_writable("../escape.md")


# --------------------------------------------------------------------------
# candidate
# --------------------------------------------------------------------------

def test_token_budget_is_a_hard_gate(candidate):
    """v1's primer grew 270B -> 3159B across three unmonitored rounds."""
    fat = candidate.with_edits({"PRIMER.md": "word " * 500})
    with pytest.raises(CandidateError, match="token budget"):
        fat.validate()


def test_deletion_is_a_first_class_edit(candidate):
    """A curator that can only add is how context collapse happens (ACE)."""
    child = candidate.with_edits({"memory/cheatsheet.md": ""})
    assert "memory/cheatsheet.md" not in child.files


def test_cid_is_content_addressed(candidate):
    same = Candidate(manifest=candidate.manifest, files=dict(candidate.files))
    assert same.cid == candidate.cid
    assert candidate.with_edits({"PRIMER.md": "different"}).cid != candidate.cid


def test_materialize_resolves_scaffolding_fresh(candidate, tmp_path):
    plugin = tmp_path / "plugin"
    (plugin / "hooks").mkdir(parents=True)
    (plugin / "hooks" / "verify_outputs.py").write_text("# current implementation\n")
    dest = tmp_path / "adapter"
    candidate.materialize(dest, scaffolding_from=plugin)
    assert (dest / "hooks" / "verify_outputs.py").read_text().startswith("# current")
    assert (dest / "PRIMER.md").exists()
    assert (dest / "manifest.toml").exists()


def test_gepa_component_roundtrip(candidate):
    comps = candidate.to_component_dict()
    assert set(comps) >= {"primer", "memory", "manifest.toml"}
    back = Candidate.from_component_dict({**comps, "primer": "edited"}, candidate)
    assert back.files["PRIMER.md"] == "edited"
    assert back.files["memory/cheatsheet.md"] == "- one"


# --------------------------------------------------------------------------
# hygiene
# --------------------------------------------------------------------------

def test_geos_extension_is_caught():
    """v1's regex was .xml-only, so plugin_evolving/v3 -- the shipped SE
    adapter -- carries tables/time.geos, tables/radialStress.geos and
    tables/axialStrain.geos past the gate."""
    corpus = GroundTruthCorpus(blocked_basenames={"time.geos"})
    report = check_texts({"skills/x.md": "then copy tables/time.geos"}, corpus)
    assert report.blocked
    assert any(f.rule == "filename" for f in report.findings)


def test_task_lookup_table_is_blocked():
    """The plugin_evolving/v4 signature: a task-name -> canonical-XML table."""
    corpus = GroundTruthCorpus(task_ids={"ExampleMandel", "TutorialSneddon"})
    report = check_texts(
        {"memory/cheatsheet.md": "| ExampleMandel | ... |\n| TutorialSneddon | ... |"},
        corpus,
    )
    assert report.blocked
    assert any(f.rule == "task_id_table" for f in report.findings)


def test_numeric_leak_is_caught():
    corpus = GroundTruthCorpus(numeric_literals={"1e-12", "0.375", "66.667"})
    report = check_texts(
        {"memory/cheatsheet.md": "use permeability 1.0e-12, porosity 0.375, K 66.667"},
        corpus,
    )
    assert report.blocked
    assert any(f.rule == "numeric_leak" for f in report.findings)


def test_content_overlap_is_caught():
    deck = " ".join(f"attribute_{i} value_{i}" for i in range(40))
    corpus = GroundTruthCorpus(deck_texts={"t/base.xml": deck})
    report = check_texts({"memory/cheatsheet.md": deck}, corpus)
    assert report.blocked
    assert any(f.rule == "content_overlap" for f in report.findings)


def test_clean_text_passes():
    corpus = GroundTruthCorpus(
        task_ids={"ExampleMandel"}, blocked_basenames={"a.xml"},
        numeric_literals={"1e-12"},
    )
    report = check_texts(
        {"PRIMER.md": "Poroelastic problems need a coupled solver and a "
                      "matching constitutive block."},
        corpus,
    )
    assert report.passed


@pytest.mark.parametrize(
    "raw,expected",
    [("1.0e-4", "0.0001"), ("1e-12", "1e-12"), ("0.375", "0.375")],
)
def test_numeric_canonicalization(raw, expected):
    assert canonicalize_number(raw) == expected


def test_latex_numeric_canonicalization():
    assert "0.0001" in canonical_numerics(r"tolerance $1.0\times10^{-4}$")


def test_trivial_numbers_are_not_leaks():
    assert canonical_numerics("use 1, 2, 3 and 10 children") == set()


# --------------------------------------------------------------------------
# acceptance
# --------------------------------------------------------------------------

def test_gate_accepts_a_clean_improvement():
    assert RegressionGate().evaluate({"a": 0.9, "b": 0.8}, {"a": 0.85, "b": 0.79})


def test_gate_rejects_a_per_task_cliff():
    """Mean-improvement would accept this; a tail-driven objective must not."""
    r = RegressionGate().evaluate(
        {"a": 0.99, "b": 0.65}, {"a": 0.80, "b": 0.79}
    )
    assert not r.accepted
    assert "per-task regression on b" in r.reason
    # ...and note the mean actually rose.
    assert r.metrics["mean_delta"] > 0


def test_gate_rejects_new_failures_as_zero():
    r = RegressionGate().evaluate({"a": 0.95, "b": 0.0}, {"a": 0.80, "b": 0.04})
    assert not r.accepted
    assert "failures-as-zero" in r.reason


def test_gate_rejects_efficiency_regression():
    """The paper's efficiency framing, as a hard search constraint."""
    r = RegressionGate().evaluate(
        {"a": 0.95}, {"a": 0.80},
        child_cost={"tool_calls": 200.0}, parent_cost={"tool_calls": 100.0},
    )
    assert not r.accepted
    assert "efficiency regression" in r.reason


def test_gate_rejects_when_it_cannot_compare():
    assert not RegressionGate().evaluate({"a": 0.9}, {"b": 0.5})


def test_unearned_edit_is_flagged():
    gate = RegressionGate().evaluate({"a": 0.90, "b": 0.79}, {"a": 0.89, "b": 0.79})
    rec = DecisionRecord(
        candidate_id="c1", parent_id="c0", component="memory",
        predicted_beneficiaries=["b"], predicted_delta=0.05,
        observed_deltas=gate.metrics["per_task_deltas"], gate=gate,
    )
    assert gate.accepted
    assert rec.prediction_hit_rate == 0.0
    assert rec.is_unearned


# --------------------------------------------------------------------------
# archive
# --------------------------------------------------------------------------

def test_pareto_frontier_keeps_a_tail_specialist(manifest):
    """The reported held-out lift is two task rescues out of ten. Mean-based
    hill climbing discards the candidate that produced them."""
    def mk(tag):
        return Candidate(manifest=manifest, files={"PRIMER.md": tag,
                                                   "memory/cheatsheet.md": tag})
    a = Archive()
    generalist = a.add(ArchiveEntry(mk("g"), {"t1": 0.9, "t2": 0.5, "t3": 0.7}))
    specialist = a.add(ArchiveEntry(mk("s"), {"t1": 0.4, "t2": 0.95, "t3": 0.3}))
    a.add(ArchiveEntry(mk("d"), {"t1": 0.3, "t2": 0.4, "t3": 0.2}))

    front = {e.cid for e in a.frontier()}
    assert generalist.cid in front and specialist.cid in front
    assert a.best().cid == generalist.cid          # mean-best sees only one
    assert len(front) == 2                          # the dominated one is dropped


def test_pareto_front_mapping():
    class E:
        def __init__(self, cid, scores):
            self.cid, self.scores = cid, scores
    front = pareto_front([E("a", {"t": 0.5}), E("b", {"t": 0.9})])
    assert front["t"] == {"b"}


# --------------------------------------------------------------------------
# checks
# --------------------------------------------------------------------------

DECK_XML = """
<Problem>
  <Solvers/><Mesh/><Events/><NumericalMethods/>
  <ElementRegions><CellElementRegion name="r" materialList="rock,water"/></ElementRegions>
  <Constitutive><ElasticIsotropic name="rock"/></Constitutive>
</Problem>
"""


def _deck(xml=DECK_XML):
    return Deck(files={"base.xml": xml}, roots={"base.xml": ET.fromstring(xml)})


def test_cross_section_refs_catches_dangling_material():
    findings = run_checks(_deck(), CheckContext(inputs_dir=Path(".")),
                          ["cross_section_refs"])
    assert len(findings) == 1
    assert "water" in findings[0].message


def test_constraints_enforce_a_maximum():
    ctx = CheckContext(
        inputs_dir=Path("."),
        constraints=[{"kind": "count", "parent": "Constitutive", "child": "*", "max": 0}],
    )
    findings = run_checks(_deck(), ctx, ["constraints"])
    assert findings and "at most 0 expected" in findings[0].message


def test_constraints_have_a_prose_rendering():
    """One source, two surfaces: prose the model reads, check the hook runs."""
    prose = render_constraints_prose(
        [{"kind": "count", "parent": "Constitutive", "child": "*", "min": 2, "max": 2}]
    )
    assert "exactly 2" in prose and "no more" in prose


def test_empty_workspace_is_an_error():
    findings = run_checks(Deck(), CheckContext(inputs_dir=Path(".")), ["parse"])
    assert findings and "no .xml files" in findings[0].message


def test_a_raising_check_does_not_block_forever():
    def boom(deck, ctx):
        raise RuntimeError("kaboom")
    findings = run_checks(_deck(), CheckContext(inputs_dir=Path(".")), ["boom"],
                          plugins={"boom": boom})
    assert all(f.severity == "warn" for f in findings)
    assert render_feedback(findings) == ""


def test_feedback_shape_is_a_real_knob():
    findings = run_checks(_deck(), CheckContext(inputs_dir=Path(".")),
                          ["cross_section_refs"])
    assert "materialList" not in render_feedback(findings, "minimal")
    assert "materialList" in render_feedback(findings, "structured_errors")
    assert "verbatim" in render_feedback(findings, "errors_plus_tables")


def test_shipped_check_plugins_pass_their_own_tests():
    reports = validate_plugins(REPO_ROOT / "hooks" / "checks")
    assert reports, "no check plugins found"
    for r in reports:
        assert r.ok, f"{r.name}: {r.error}"


# --------------------------------------------------------------------------
# proposer
# --------------------------------------------------------------------------

def _response(component="memory", body="- one\n- two", pred=None):
    import json
    pred = pred or {"targets_category": "missing_block",
                    "predicted_beneficiaries": ["A"], "predicted_delta": 0.03}
    return (f'<file component="{component}">\n{body}\n</file>\n'
            f"<prediction>{json.dumps(pred)}</prediction>")


def _evidence():
    from evolve.evidence import RoundEvidence, TaskEvidence
    return RoundEvidence("c0", [TaskEvidence("A", "r1", 0.4, "success")])


def test_proposer_produces_a_child_with_a_prediction(candidate):
    child = propose(candidate, _evidence(), _call=lambda p: _response())
    assert child.parent_id == candidate.cid
    assert child.files["memory/cheatsheet.md"] == "- one\n- two"
    assert child.predictions[0].predicted_beneficiaries == ("A",)


def test_proposer_enforces_one_component_per_edit(candidate):
    two = _response() + _response(component="primer", body="x")
    with pytest.raises(ProposerError, match="exactly one"):
        propose(candidate, _evidence(), _call=lambda p: two)


def test_proposer_requires_a_prediction(candidate):
    with pytest.raises(ProposerError, match="prediction"):
        propose(candidate, _evidence(),
                _call=lambda p: '<file component="memory">x</file>')


def test_malformed_proposal_is_loud_not_silent(candidate):
    """v1 silently inherited the parent on unparseable output, burning a call."""
    with pytest.raises(ProposerError):
        propose(candidate, _evidence(), _call=lambda p: "I have no idea")


def test_proposer_output_still_faces_the_budget(candidate):
    with pytest.raises(CandidateError):
        propose(candidate, _evidence(),
                _call=lambda p: _response(body="word " * 500))


# --------------------------------------------------------------------------
# evidence
# --------------------------------------------------------------------------

def test_evidence_reports_reward_and_deltas():
    """v1's proposer saw 'mean treesim 0.0000' and 'treesim N/A' per task,
    because the round was never scored before reflection."""
    from evolve.evidence import RoundEvidence, TaskEvidence
    ev = RoundEvidence(
        "c1",
        [TaskEvidence("A", "r", 0.9, "success"), TaskEvidence("B", "r", 0.0, "empty")],
        parent_scores={"A": 0.8, "B": 0.5},
    )
    text = ev.render(level=2)
    assert "mean=0.4500" in text
    assert "zero_rate=0.50" in text
    assert "B-0.500" in text
    assert "N/A" not in text


def test_bottleneck_extractor_is_importable():
    """The evidence layer is wiring, not a reimplementation."""
    from evolve.evidence import _load_extract_module
    mod = _load_extract_module()
    assert mod is not None and hasattr(mod, "diagnostic_for_task")


def test_token_estimate_is_biased_high():
    assert estimate_tokens("word " * 100) >= 100
