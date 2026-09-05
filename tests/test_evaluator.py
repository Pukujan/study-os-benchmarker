from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from pydantic import ValidationError

from study_os_benchmarker.evaluator import evaluate
from study_os_benchmarker.models import (
    BenchmarkCase,
    TutorProposal,
    ViolationCode,
    canonical_json_bytes,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = ROOT / "fixtures" / "public" / "s0-to-si"
SCHEMA_DIR = ROOT / "schemas"


def load_case() -> BenchmarkCase:
    return BenchmarkCase.model_validate_json((FIXTURE_DIR / "case.v1.json").read_text())


def load_proposal(name: str) -> TutorProposal:
    return TutorProposal.model_validate_json((FIXTURE_DIR / name).read_text())


def test_good_proposal_passes() -> None:
    report = evaluate(load_case(), load_proposal("proposal.good.v1.json"))
    assert report.passed is True
    assert report.violations == ()
    assert report.metrics.legal_next_node is True
    assert report.metrics.required_bridges_preserved is True
    assert report.metrics.representation_preserved is True
    assert report.metrics.forbidden_concepts_absent is True
    assert report.metrics.answer_policy_satisfied is True


@pytest.mark.parametrize(
    ("fixture_name", "expected_code"),
    [
        ("proposal.bad-missing-bridge.v1.json", ViolationCode.MISSING_REQUIRED_BRIDGE),
        ("proposal.bad-illegal-next.v1.json", ViolationCode.ILLEGAL_NEXT_NODE),
        ("proposal.bad-missing-representation.v1.json", ViolationCode.MISSING_REPRESENTATION),
        ("proposal.bad-forbidden-concept.v1.json", ViolationCode.FORBIDDEN_CONCEPT_DISCLOSED),
        ("proposal.bad-answer-leak.v1.json", ViolationCode.ANSWER_REVEAL_FORBIDDEN),
    ],
)
def test_each_adversarial_fixture_fails_for_its_targeted_reason(
    fixture_name: str, expected_code: ViolationCode
) -> None:
    report = evaluate(load_case(), load_proposal(fixture_name))
    assert report.passed is False
    assert tuple(violation.code for violation in report.violations) == (expected_code,)


def test_candidate_visible_context_does_not_contain_answer_key() -> None:
    raw_case = json.loads((FIXTURE_DIR / "case.v1.json").read_text())
    candidate_visible = json.dumps(raw_case["context"], sort_keys=True)
    for forbidden_literal in raw_case["oracle"]["forbidden_answer_literals"]:
        assert forbidden_literal not in candidate_visible


def test_evaluation_is_canonically_deterministic() -> None:
    case = load_case()
    proposal = load_proposal("proposal.good.v1.json")
    first = evaluate(case, proposal)
    second = evaluate(case, proposal)
    assert first == second
    assert canonical_json_bytes(first) == canonical_json_bytes(second)


def test_extra_fields_fail_closed_in_strict_model() -> None:
    raw = json.loads((FIXTURE_DIR / "proposal.good.v1.json").read_text())
    raw["unexpected"] = "must fail"
    with pytest.raises(ValidationError):
        TutorProposal.model_validate_json(json.dumps(raw))


def test_public_json_fixtures_validate_against_independent_schemas() -> None:
    case_schema = json.loads((SCHEMA_DIR / "benchmark-case.v1.schema.json").read_text())
    proposal_schema = json.loads((SCHEMA_DIR / "tutor-proposal.v1.schema.json").read_text())
    report_schema = json.loads((SCHEMA_DIR / "benchmark-report.v1.schema.json").read_text())

    raw_case = json.loads((FIXTURE_DIR / "case.v1.json").read_text())
    Draft202012Validator(case_schema).validate(raw_case)

    for proposal_path in sorted(FIXTURE_DIR.glob("proposal.*.json")):
        raw_proposal = json.loads(proposal_path.read_text())
        Draft202012Validator(proposal_schema).validate(raw_proposal)

    report = evaluate(load_case(), load_proposal("proposal.good.v1.json"))
    Draft202012Validator(report_schema).validate(report.model_dump(mode="json"))
