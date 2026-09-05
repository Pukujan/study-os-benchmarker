from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

from study_os_benchmarker.evaluator import evaluate
from study_os_benchmarker.models import BenchmarkCase, TutorProposal, ViolationCode

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = ROOT / "fixtures" / "public" / "max-loop"
SCHEMA_DIR = ROOT / "schemas"


def load_case(name: str) -> BenchmarkCase:
    return BenchmarkCase.model_validate_json((FIXTURE_DIR / name).read_text())


def load_proposal(name: str) -> TutorProposal:
    return TutorProposal.model_validate_json((FIXTURE_DIR / name).read_text())


def test_fixed_index_next_move_passes_after_first_comparison() -> None:
    report = evaluate(
        load_case("case.after-first-comparison.v1.json"),
        load_proposal("proposal.after-first-comparison.good-fixed-index.v1.json"),
    )
    assert report.passed is True
    assert report.violations == ()


def test_premature_standalone_max_loop_is_rejected() -> None:
    report = evaluate(
        load_case("case.after-first-comparison.v1.json"),
        load_proposal("proposal.after-first-comparison.bad-jump-max-loop.v1.json"),
    )
    assert report.passed is False
    assert tuple(v.code for v in report.violations) == (
        ViolationCode.ILLEGAL_NEXT_NODE,
        ViolationCode.FORBIDDEN_CONCEPT_DISCLOSED,
    )


def test_enumerate_source_probe_passes_after_symbolic_comparison() -> None:
    report = evaluate(
        load_case("case.after-symbolic-comparison.v1.json"),
        load_proposal(
            "proposal.after-symbolic-comparison.good-enumerate-blank.v1.json"
        ),
    )
    assert report.passed is True
    assert report.violations == ()


def test_full_max_loop_reveal_is_rejected() -> None:
    report = evaluate(
        load_case("case.after-symbolic-comparison.v1.json"),
        load_proposal("proposal.after-symbolic-comparison.bad-show-full-loop.v1.json"),
    )
    assert report.passed is False
    assert tuple(v.code for v in report.violations) == (
        ViolationCode.ILLEGAL_NEXT_NODE,
        ViolationCode.MISSING_REQUIRED_BRIDGE,
        ViolationCode.FORBIDDEN_CONCEPT_DISCLOSED,
        ViolationCode.ANSWER_REVEAL_FORBIDDEN,
    )


def test_max_loop_oracles_are_not_candidate_visible() -> None:
    for case_path in sorted(FIXTURE_DIR.glob("case.*.json")):
        raw = json.loads(case_path.read_text())
        candidate_visible = json.dumps(raw["context"], sort_keys=True)
        for forbidden_literal in raw["oracle"]["forbidden_answer_literals"]:
            assert forbidden_literal not in candidate_visible


def test_all_max_loop_fixtures_validate_against_wire_schemas() -> None:
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
