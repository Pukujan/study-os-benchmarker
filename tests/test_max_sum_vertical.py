from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from study_os_benchmarker.evaluator import evaluate
from study_os_benchmarker.models import BenchmarkCase, TutorProposal, ViolationCode

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = ROOT / "fixtures" / "public" / "max-sum-vertical"
SCHEMA_DIR = ROOT / "schemas"


def load_case(name: str) -> BenchmarkCase:
    return BenchmarkCase.model_validate_json((FIXTURE_DIR / name).read_text())


def load_proposal(name: str) -> TutorProposal:
    return TutorProposal.model_validate_json((FIXTURE_DIR / name).read_text())


@pytest.mark.parametrize(
    ("case_name", "proposal_name"),
    [
        ("case.after-value-answer.v1.json", "proposal.after-value.good-validate.v1.json"),
        ("case.after-s0-validation.v1.json", "proposal.after-s0.good-bridge-probe.v1.json"),
        ("case.after-si-response.v1.json", "proposal.after-si.good-validate.v1.json"),
        (
            "case.after-si-validation.v1.json",
            "proposal.after-si-validation.good-comparison.v1.json",
        ),
    ],
)
def test_calibrated_next_moves_pass(case_name: str, proposal_name: str) -> None:
    report = evaluate(load_case(case_name), load_proposal(proposal_name))
    assert report.passed is True
    assert report.violations == ()


@pytest.mark.parametrize(
    ("case_name", "proposal_name", "expected_codes"),
    [
        (
            "case.after-value-answer.v1.json",
            "proposal.after-value.bad-next-exercise.v1.json",
            (ViolationCode.ILLEGAL_NEXT_NODE,),
        ),
        (
            "case.after-value-answer.v1.json",
            "proposal.after-value.bad-comparison.v1.json",
            (ViolationCode.ILLEGAL_NEXT_NODE, ViolationCode.FORBIDDEN_CONCEPT_DISCLOSED),
        ),
        (
            "case.after-s0-validation.v1.json",
            "proposal.after-s0.bad-skip-bridge.v1.json",
            (ViolationCode.MISSING_REQUIRED_BRIDGE,),
        ),
        (
            "case.after-s0-validation.v1.json",
            "proposal.after-s0.bad-answer-leak.v1.json",
            (ViolationCode.ANSWER_REVEAL_FORBIDDEN,),
        ),
        (
            "case.after-s0-validation.v1.json",
            "proposal.after-s0.bad-drop-chart.v1.json",
            (ViolationCode.MISSING_REPRESENTATION,),
        ),
        (
            "case.after-s0-validation.v1.json",
            "proposal.after-s0.bad-repeat-s0.v1.json",
            (ViolationCode.ILLEGAL_NEXT_NODE, ViolationCode.MISSING_REQUIRED_BRIDGE),
        ),
        (
            "case.after-si-response.v1.json",
            "proposal.after-si.bad-comparison-before-validation.v1.json",
            (ViolationCode.ILLEGAL_NEXT_NODE, ViolationCode.FORBIDDEN_CONCEPT_DISCLOSED),
        ),
    ],
)
def test_observed_and_semantic_shortcut_mutations_fail(
    case_name: str,
    proposal_name: str,
    expected_codes: tuple[ViolationCode, ...],
) -> None:
    report = evaluate(load_case(case_name), load_proposal(proposal_name))
    assert report.passed is False
    assert tuple(violation.code for violation in report.violations) == expected_codes


def test_si_bridge_case_keeps_oracle_answer_out_of_candidate_context() -> None:
    raw = json.loads((FIXTURE_DIR / "case.after-s0-validation.v1.json").read_text())
    candidate_visible = json.dumps(raw["context"], sort_keys=True)
    for forbidden_literal in raw["oracle"]["forbidden_answer_literals"]:
        assert forbidden_literal not in candidate_visible


def test_all_vertical_fixtures_validate_against_independent_wire_schemas() -> None:
    case_schema = json.loads((SCHEMA_DIR / "benchmark-case.v1.schema.json").read_text())
    proposal_schema = json.loads((SCHEMA_DIR / "tutor-proposal.v1.schema.json").read_text())

    for case_path in sorted(FIXTURE_DIR.glob("case.*.json")):
        Draft202012Validator(case_schema).validate(json.loads(case_path.read_text()))

    for proposal_path in sorted(FIXTURE_DIR.glob("proposal.*.json")):
        Draft202012Validator(proposal_schema).validate(json.loads(proposal_path.read_text()))
