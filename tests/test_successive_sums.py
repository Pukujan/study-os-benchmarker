from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from study_os_benchmarker.evaluator import EVALUATOR_VERSION, evaluate
from study_os_benchmarker.models import BenchmarkCase, TutorProposal, ViolationCode

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = ROOT / "fixtures" / "public" / "successive-sums"
SCHEMA_DIR = ROOT / "schemas"


def load_case(name: str) -> BenchmarkCase:
    return BenchmarkCase.model_validate_json((FIXTURE_DIR / name).read_text())


def load_proposal(name: str) -> TutorProposal:
    return TutorProposal.model_validate_json((FIXTURE_DIR / name).read_text())


@pytest.mark.parametrize(
    ("case_name", "proposal_name"),
    [
        (
            "case.after-sum-i.v1.json",
            "proposal.after-sum-i.good-successive-probe.v1.json",
        ),
        (
            "case.after-first-successive-validation.v1.json",
            "proposal.after-first-successive-validation.good-changed-probe.v1.json",
        ),
        (
            "case.after-general-recurrence.v1.json",
            "proposal.after-general-recurrence.good-repeat-i.v1.json",
        ),
    ],
)
def test_calibrated_successive_sum_moves_pass(case_name: str, proposal_name: str) -> None:
    report = evaluate(load_case(case_name), load_proposal(proposal_name))
    assert report.passed is True
    assert report.violations == ()
    assert report.evaluator_version == EVALUATOR_VERSION


@pytest.mark.parametrize(
    ("case_name", "proposal_name", "expected_codes"),
    [
        (
            "case.after-sum-i.v1.json",
            "proposal.after-sum-i.bad-direct-recurrence.v1.json",
            (
                ViolationCode.ILLEGAL_NEXT_NODE,
                ViolationCode.MISSING_REQUIRED_BRIDGE,
                ViolationCode.FORBIDDEN_CONCEPT_DISCLOSED,
            ),
        ),
        (
            "case.after-first-successive-validation.v1.json",
            "proposal.after-first-successive-validation.bad-skip-to-i3.v1.json",
            (
                ViolationCode.ILLEGAL_NEXT_NODE,
                ViolationCode.MISSING_REQUIRED_BRIDGE,
            ),
        ),
        (
            "case.after-general-recurrence.v1.json",
            "proposal.after-general-recurrence.bad-python-loop.v1.json",
            (
                ViolationCode.ILLEGAL_NEXT_NODE,
                ViolationCode.MISSING_REQUIRED_BRIDGE,
                ViolationCode.FORBIDDEN_CONCEPT_DISCLOSED,
            ),
        ),
        (
            "case.after-general-recurrence.v1.json",
            "proposal.after-general-recurrence.bad-detached.v1.json",
            (ViolationCode.MISSING_REPRESENTATION,),
        ),
    ],
)
def test_successive_sum_regressions_fail(
    case_name: str,
    proposal_name: str,
    expected_codes: tuple[ViolationCode, ...],
) -> None:
    report = evaluate(load_case(case_name), load_proposal(proposal_name))
    assert report.passed is False
    assert tuple(violation.code for violation in report.violations) == expected_codes


@pytest.mark.parametrize(
    "case_name",
    [
        "case.after-sum-i.v1.json",
        "case.after-first-successive-validation.v1.json",
        "case.after-general-recurrence.v1.json",
    ],
)
def test_oracle_answers_are_not_candidate_visible(case_name: str) -> None:
    raw = json.loads((FIXTURE_DIR / case_name).read_text())
    candidate_visible = json.dumps(raw["context"], sort_keys=True)
    for forbidden_literal in raw["oracle"]["forbidden_answer_literals"]:
        assert forbidden_literal not in candidate_visible


def test_all_successive_sum_fixtures_validate_against_wire_schemas() -> None:
    case_schema = json.loads((SCHEMA_DIR / "benchmark-case.v1.schema.json").read_text())
    proposal_schema = json.loads((SCHEMA_DIR / "tutor-proposal.v1.schema.json").read_text())

    for case_path in sorted(FIXTURE_DIR.glob("case.*.json")):
        Draft202012Validator(case_schema).validate(json.loads(case_path.read_text()))

    for proposal_path in sorted(FIXTURE_DIR.glob("proposal.*.json")):
        Draft202012Validator(proposal_schema).validate(json.loads(proposal_path.read_text()))
