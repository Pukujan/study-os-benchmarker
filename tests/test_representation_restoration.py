from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

from study_os_benchmarker.evaluator import EVALUATOR_VERSION, evaluate
from study_os_benchmarker.models import BenchmarkCase, TutorProposal, ViolationCode

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = ROOT / "fixtures" / "public" / "representation-restoration"
SCHEMA_DIR = ROOT / "schemas"


def load_case(name: str) -> BenchmarkCase:
    return BenchmarkCase.model_validate_json((FIXTURE_DIR / name).read_text())


def load_proposal(name: str) -> TutorProposal:
    return TutorProposal.model_validate_json((FIXTURE_DIR / name).read_text())


def test_restored_source_representation_passes() -> None:
    report = evaluate(
        load_case("case.after-window-loop.v1.json"),
        load_proposal("proposal.after-window-loop.good-restore.v1.json"),
    )
    assert report.passed is True
    assert report.violations == ()
    assert report.evaluator_version == EVALUATOR_VERSION


def test_detached_s_only_validation_is_killed() -> None:
    report = evaluate(
        load_case("case.after-window-loop.v1.json"),
        load_proposal("proposal.after-window-loop.bad-detached-s.v1.json"),
    )
    assert report.passed is False
    assert tuple(violation.code for violation in report.violations) == (
        ViolationCode.MISSING_REPRESENTATION,
    )
    assert report.metrics.legal_next_node is True
    assert report.metrics.required_bridges_preserved is True
    assert report.metrics.representation_preserved is False


def test_restoration_oracle_is_not_candidate_visible() -> None:
    raw = json.loads((FIXTURE_DIR / "case.after-window-loop.v1.json").read_text())
    candidate_visible = json.dumps(raw["context"], sort_keys=True)
    assert "required_representation" not in candidate_visible
    assert "required_bridge_ids" not in candidate_visible
    assert "allowed_next_nodes" not in candidate_visible


def test_restoration_fixtures_validate_against_wire_schemas() -> None:
    case_schema = json.loads((SCHEMA_DIR / "benchmark-case.v1.schema.json").read_text())
    proposal_schema = json.loads((SCHEMA_DIR / "tutor-proposal.v1.schema.json").read_text())

    for case_path in sorted(FIXTURE_DIR.glob("case.*.json")):
        Draft202012Validator(case_schema).validate(json.loads(case_path.read_text()))

    for proposal_path in sorted(FIXTURE_DIR.glob("proposal.*.json")):
        Draft202012Validator(proposal_schema).validate(json.loads(proposal_path.read_text()))
