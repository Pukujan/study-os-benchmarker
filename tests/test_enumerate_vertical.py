from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from study_os_benchmarker.evaluator import EVALUATOR_VERSION, evaluate
from study_os_benchmarker.models import BenchmarkCase, TutorProposal, ViolationCode

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = ROOT / "fixtures" / "public" / "enumerate-vertical"
SCHEMA_DIR = ROOT / "schemas"


def load_case(name: str) -> BenchmarkCase:
    return BenchmarkCase.model_validate_json((FIXTURE_DIR / name).read_text())


def load_proposal(name: str) -> TutorProposal:
    return TutorProposal.model_validate_json((FIXTURE_DIR / name).read_text())


@pytest.mark.parametrize(
    ("case_name", "proposal_name"),
    [
        ("case.after-explain.v1.json", "proposal.after-explain.good-probe.v1.json"),
        (
            "case.after-pair36-response.v1.json",
            "proposal.after-pair36.good-validate.v1.json",
        ),
        (
            "case.after-first-validation.v1.json",
            "proposal.after-first-validation.good-changed-probe.v1.json",
        ),
        (
            "case.after-pair47-response.v1.json",
            "proposal.after-pair47.good-validate.v1.json",
        ),
        (
            "case.after-two-is-enough.v1.json",
            "proposal.after-two-is-enough.good-append.v1.json",
        ),
    ],
)
def test_calibrated_enumerate_moves_pass(case_name: str, proposal_name: str) -> None:
    report = evaluate(load_case(case_name), load_proposal(proposal_name))
    assert report.passed is True
    assert report.violations == ()
    assert report.evaluator_version == EVALUATOR_VERSION
    assert report.metrics.forbidden_representation_absent is True


@pytest.mark.parametrize(
    ("case_name", "proposal_name", "expected_codes"),
    [
        (
            "case.after-explain.v1.json",
            "proposal.after-explain.bad-answer-leak.v1.json",
            (ViolationCode.ANSWER_REVEAL_FORBIDDEN,),
        ),
        (
            "case.after-explain.v1.json",
            "proposal.after-explain.bad-pair-row.v1.json",
            (ViolationCode.FORBIDDEN_REPRESENTATION_PRESENT,),
        ),
        (
            "case.after-explain.v1.json",
            "proposal.after-explain.bad-window-box.v1.json",
            (ViolationCode.FORBIDDEN_REPRESENTATION_PRESENT,),
        ),
        (
            "case.after-explain.v1.json",
            "proposal.after-explain.bad-append-early.v1.json",
            (ViolationCode.ILLEGAL_NEXT_NODE, ViolationCode.FORBIDDEN_CONCEPT_DISCLOSED),
        ),
        (
            "case.after-pair36-response.v1.json",
            "proposal.after-pair36.bad-move-on.v1.json",
            (ViolationCode.ILLEGAL_NEXT_NODE,),
        ),
        (
            "case.after-first-validation.v1.json",
            "proposal.after-first-validation.bad-answer-leak.v1.json",
            (ViolationCode.ANSWER_REVEAL_FORBIDDEN,),
        ),
        (
            "case.after-pair47-response.v1.json",
            "proposal.after-pair47.bad-append-before-validation.v1.json",
            (ViolationCode.ILLEGAL_NEXT_NODE, ViolationCode.FORBIDDEN_CONCEPT_DISCLOSED),
        ),
        (
            "case.after-two-is-enough.v1.json",
            "proposal.after-two-is-enough.bad-third-exercise.v1.json",
            (ViolationCode.ILLEGAL_NEXT_NODE, ViolationCode.FORBIDDEN_CONCEPT_DISCLOSED),
        ),
    ],
)
def test_enumerate_regressions_fail(
    case_name: str,
    proposal_name: str,
    expected_codes: tuple[ViolationCode, ...],
) -> None:
    report = evaluate(load_case(case_name), load_proposal(proposal_name))
    assert report.passed is False
    assert tuple(violation.code for violation in report.violations) == expected_codes


def test_first_probe_oracle_answer_is_not_candidate_visible() -> None:
    raw = json.loads((FIXTURE_DIR / "case.after-explain.v1.json").read_text())
    candidate_visible = json.dumps(raw["context"], sort_keys=True)
    for forbidden_literal in raw["oracle"]["forbidden_answer_literals"]:
        assert forbidden_literal not in candidate_visible


def test_changed_probe_oracle_answer_is_not_candidate_visible() -> None:
    raw = json.loads((FIXTURE_DIR / "case.after-first-validation.v1.json").read_text())
    candidate_visible = json.dumps(raw["context"], sort_keys=True)
    for forbidden_literal in raw["oracle"]["forbidden_answer_literals"]:
        assert forbidden_literal not in candidate_visible


def test_all_enumerate_fixtures_validate_against_independent_wire_schemas() -> None:
    case_schema = json.loads((SCHEMA_DIR / "benchmark-case.v1.schema.json").read_text())
    proposal_schema = json.loads((SCHEMA_DIR / "tutor-proposal.v1.schema.json").read_text())

    for case_path in sorted(FIXTURE_DIR.glob("case.*.json")):
        Draft202012Validator(case_schema).validate(json.loads(case_path.read_text()))

    for proposal_path in sorted(FIXTURE_DIR.glob("proposal.*.json")):
        Draft202012Validator(proposal_schema).validate(json.loads(proposal_path.read_text()))
