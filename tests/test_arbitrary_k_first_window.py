from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

from study_os_benchmarker.evaluator import evaluate
from study_os_benchmarker.models import BenchmarkCase, TutorProposal, ViolationCode

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = ROOT / "fixtures" / "public" / "arbitrary-k-first-window"
SCHEMA_DIR = ROOT / "schemas"


def load_case(name: str) -> BenchmarkCase:
    return BenchmarkCase.model_validate_json((FIXTURE_DIR / name).read_text())


def load_proposal(name: str) -> TutorProposal:
    return TutorProposal.model_validate_json((FIXTURE_DIR / name).read_text())


def codes(case_name: str, proposal_name: str) -> tuple[ViolationCode, ...]:
    report = evaluate(load_case(case_name), load_proposal(proposal_name))
    return tuple(violation.code for violation in report.violations)


def test_preserving_existing_s_before_arbitrary_k_passes() -> None:
    report = evaluate(
        load_case("case.before-arbitrary-k.v1.json"),
        load_proposal("proposal.before-arbitrary-k.good-preserve-s.v1.json"),
    )
    assert report.passed is True
    assert report.violations == ()


def test_new_window_sum_accumulator_is_rejected() -> None:
    assert codes(
        "case.before-arbitrary-k.v1.json",
        "proposal.before-arbitrary-k.bad-new-accumulator.v1.json",
    ) == (
        ViolationCode.ILLEGAL_NEXT_NODE,
        ViolationCode.MISSING_REQUIRED_BRIDGE,
        ViolationCode.FORBIDDEN_CONCEPT_DISCLOSED,
        ViolationCode.ANSWER_REVEAL_FORBIDDEN,
    )


def test_slice_sum_shortcut_is_rejected_even_with_box_preserved() -> None:
    assert codes(
        "case.before-arbitrary-k.v1.json",
        "proposal.before-arbitrary-k.bad-slice-sum.v1.json",
    ) == (
        ViolationCode.ILLEGAL_NEXT_NODE,
        ViolationCode.MISSING_REQUIRED_BRIDGE,
        ViolationCode.FORBIDDEN_CONCEPT_DISCLOSED,
        ViolationCode.ANSWER_REVEAL_FORBIDDEN,
    )


def test_same_s_update_probe_passes_without_revealing_line() -> None:
    report = evaluate(
        load_case("case.before-inner-update.v1.json"),
        load_proposal("proposal.before-inner-update.good-probe.v1.json"),
    )
    assert report.passed is True
    assert report.violations == ()


def test_append_per_x_is_rejected_without_resetting_range_bridge() -> None:
    assert codes(
        "case.before-inner-update.v1.json",
        "proposal.before-inner-update.bad-append-per-x.v1.json",
    ) == (
        ViolationCode.ILLEGAL_NEXT_NODE,
        ViolationCode.FORBIDDEN_CONCEPT_DISCLOSED,
    )


def test_revealing_same_s_update_line_is_rejected_independently() -> None:
    assert codes(
        "case.before-inner-update.v1.json",
        "proposal.before-inner-update.bad-reveal-update.v1.json",
    ) == (ViolationCode.ANSWER_REVEAL_FORBIDDEN,)


def test_first_x_state_with_full_state_trace_passes() -> None:
    report = evaluate(
        load_case("case.after-inner-update.v1.json"),
        load_proposal("proposal.after-inner-update.good-x0-state.v1.json"),
    )
    assert report.passed is True
    assert report.violations == ()


def test_detached_correct_code_fails_required_state_representation() -> None:
    assert codes(
        "case.after-inner-update.v1.json",
        "proposal.after-inner-update.bad-detached-code.v1.json",
    ) == (ViolationCode.MISSING_REPRESENTATION,)


def test_final_combined_loop_is_still_premature_before_state_trace() -> None:
    assert codes(
        "case.after-inner-update.v1.json",
        "proposal.after-inner-update.bad-final-loop.v1.json",
    ) == (
        ViolationCode.ILLEGAL_NEXT_NODE,
        ViolationCode.FORBIDDEN_CONCEPT_DISCLOSED,
        ViolationCode.ANSWER_REVEAL_FORBIDDEN,
    )


def test_arbitrary_k_oracles_are_not_candidate_visible() -> None:
    for case_path in sorted(FIXTURE_DIR.glob("case.*.json")):
        raw = json.loads(case_path.read_text())
        candidate_visible = json.dumps(raw["context"], sort_keys=True)
        for forbidden_literal in raw["oracle"]["forbidden_answer_literals"]:
            assert forbidden_literal not in candidate_visible


def test_all_arbitrary_k_fixtures_validate_against_wire_schemas() -> None:
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
