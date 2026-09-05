from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

from study_os_benchmarker.evaluator import evaluate
from study_os_benchmarker.models import BenchmarkCase, TutorProposal, ViolationCode

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = ROOT / "fixtures" / "public" / "combined-loop"
SCHEMA_DIR = ROOT / "schemas"


def load_case(name: str) -> BenchmarkCase:
    return BenchmarkCase.model_validate_json((FIXTURE_DIR / name).read_text())


def load_proposal(name: str) -> TutorProposal:
    return TutorProposal.model_validate_json((FIXTURE_DIR / name).read_text())


def test_first_box_combination_proposal_passes() -> None:
    report = evaluate(
        load_case("case.after-standalone-max-loop.v1.json"),
        load_proposal("proposal.after-standalone-max-loop.good-first-box.v1.json"),
    )
    assert report.passed is True
    assert report.violations == ()


def test_full_combined_solution_shortcut_is_rejected() -> None:
    report = evaluate(
        load_case("case.after-standalone-max-loop.v1.json"),
        load_proposal("proposal.after-standalone-max-loop.bad-full-solution.v1.json"),
    )
    assert report.passed is False
    assert tuple(v.code for v in report.violations) == (
        ViolationCode.ILLEGAL_NEXT_NODE,
        ViolationCode.MISSING_REQUIRED_BRIDGE,
        ViolationCode.FORBIDDEN_CONCEPT_DISCLOSED,
        ViolationCode.ANSWER_REVEAL_FORBIDDEN,
    )


def test_focused_append_repair_passes() -> None:
    report = evaluate(
        load_case("case.append-partial.v1.json"),
        load_proposal("proposal.append-partial.good-focused-repair.v1.json"),
    )
    assert report.passed is True
    assert report.violations == ()


def test_resetting_correct_max_condition_is_rejected() -> None:
    report = evaluate(
        load_case("case.append-partial.v1.json"),
        load_proposal("proposal.append-partial.bad-reset-branch.v1.json"),
    )
    assert report.passed is False
    assert tuple(v.code for v in report.violations) == (
        ViolationCode.ILLEGAL_NEXT_NODE,
        ViolationCode.MISSING_REQUIRED_BRIDGE,
        ViolationCode.FORBIDDEN_CONCEPT_DISCLOSED,
    )


def test_len_bridge_passes_before_break_code() -> None:
    report = evaluate(
        load_case("case.before-break-code.v1.json"),
        load_proposal("proposal.before-break-code.good-len-bridge.v1.json"),
    )
    assert report.passed is True
    assert report.violations == ()


def test_premature_break_code_is_rejected() -> None:
    report = evaluate(
        load_case("case.before-break-code.v1.json"),
        load_proposal("proposal.before-break-code.bad-reveal-break.v1.json"),
    )
    assert report.passed is False
    assert tuple(v.code for v in report.violations) == (
        ViolationCode.ILLEGAL_NEXT_NODE,
        ViolationCode.MISSING_REQUIRED_BRIDGE,
        ViolationCode.FORBIDDEN_CONCEPT_DISCLOSED,
        ViolationCode.ANSWER_REVEAL_FORBIDDEN,
    )


def test_combined_loop_oracles_are_not_candidate_visible() -> None:
    for case_path in sorted(FIXTURE_DIR.glob("case.*.json")):
        raw = json.loads(case_path.read_text())
        candidate_visible = json.dumps(raw["context"], sort_keys=True)
        for forbidden_literal in raw["oracle"]["forbidden_answer_literals"]:
            assert forbidden_literal not in candidate_visible


def test_all_combined_loop_fixtures_validate_against_wire_schemas() -> None:
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
