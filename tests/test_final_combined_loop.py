from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

from study_os_benchmarker.evaluator import evaluate
from study_os_benchmarker.models import BenchmarkCase, TutorProposal, ViolationCode

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = ROOT / "fixtures" / "public" / "final-combined-loop"
SCHEMA_DIR = ROOT / "schemas"


def load_case(name: str) -> BenchmarkCase:
    return BenchmarkCase.model_validate_json((FIXTURE_DIR / name).read_text())


def load_proposal(name: str) -> TutorProposal:
    return TutorProposal.model_validate_json((FIXTURE_DIR / name).read_text())


def test_final_solution_exposure_is_allowed_only_after_grounded_bridges() -> None:
    report = evaluate(
        load_case("case.before-final-exposure.v1.json"),
        load_proposal("proposal.before-final-exposure.good.v1.json"),
    )
    assert report.passed is True
    assert report.violations == ()


def test_final_solution_exposure_does_not_authorize_mastery_claim() -> None:
    report = evaluate(
        load_case("case.before-final-exposure.v1.json"),
        load_proposal("proposal.before-final-exposure.bad-mastery.v1.json"),
    )
    assert tuple(violation.code for violation in report.violations) == (
        ViolationCode.FORBIDDEN_CONCEPT_DISCLOSED,
    )


def test_final_combined_loop_fixtures_validate_against_wire_schemas() -> None:
    case_schema = json.loads((SCHEMA_DIR / "benchmark-case.v1.schema.json").read_text())
    proposal_schema = json.loads(
        (SCHEMA_DIR / "tutor-proposal.v1.schema.json").read_text()
    )

    for case_path in sorted(FIXTURE_DIR.glob("case.*.json")):
        Draft202012Validator(case_schema).validate(json.loads(case_path.read_text()))

    for proposal_path in sorted(FIXTURE_DIR.glob("proposal.*.json")):
        Draft202012Validator(proposal_schema).validate(
            json.loads(proposal_path.read_text())
        )
