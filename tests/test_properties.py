from __future__ import annotations

from hypothesis import given
from hypothesis import strategies as st

from study_os_benchmarker.evaluator import evaluate
from study_os_benchmarker.models import (
    BenchmarkCase,
    BenchmarkOracle,
    CandidateContext,
    TutorProposal,
)

REQUIRED_REPRESENTATION = ("array", "index_row", "box", "i_equals_0")


def base_case(required_representation: tuple[str, ...] = REQUIRED_REPRESENTATION) -> BenchmarkCase:
    return BenchmarkCase(
        schema_version="benchmark.case.v1",
        context=CandidateContext(
            schema_version="benchmark.candidate-context.v1",
            case_id="property.s0-to-si.v1",
            current_node="write_S0",
            visible_context=("i = 0",),
            visible_representation=REQUIRED_REPRESENTATION,
        ),
        oracle=BenchmarkOracle(
            schema_version="benchmark.oracle.v1",
            allowed_next_nodes=("write_Si",),
            required_bridge_ids=("S0_to_Si_when_i0",),
            required_representation=required_representation,
            forbidden_concepts=("max_comparison",),
            answer_reveal_allowed=False,
            forbidden_answer_literals=("max_sum = S[i]",),
        ),
    )


def base_proposal(shown_representation: tuple[str, ...] = REQUIRED_REPRESENTATION) -> TutorProposal:
    return TutorProposal(
        schema_version="benchmark.tutor-proposal.v1",
        candidate_id="property.reference",
        candidate_version="v0.1",
        proposed_next_node="write_Si",
        traversed_bridge_ids=("S0_to_Si_when_i0",),
        shown_representation=shown_representation,
        disclosed_concepts=("S0_equals_Si_when_i0",),
        answer_revealed=False,
        rendered_text="Use the same chart and rewrite the line using S[i].",
    )


@given(st.permutations(REQUIRED_REPRESENTATION))
def test_representation_order_does_not_change_semantic_score(permutation: list[str]) -> None:
    report = evaluate(base_case(), base_proposal(tuple(permutation)))
    assert report.passed is True
    assert report.metrics.representation_preserved is True


@given(st.sampled_from(REQUIRED_REPRESENTATION))
def test_removing_any_required_representation_component_always_fails(missing: str) -> None:
    shown = tuple(item for item in REQUIRED_REPRESENTATION if item != missing)
    report = evaluate(base_case(), base_proposal(shown))
    assert report.passed is False
    assert report.metrics.representation_preserved is False


@given(
    st.text(min_size=1, max_size=16).filter(
        lambda value: value not in set(REQUIRED_REPRESENTATION)
    )
)
def test_adding_irrelevant_representation_cannot_make_legal_proposal_illegal(extra: str) -> None:
    report = evaluate(base_case(), base_proposal(REQUIRED_REPRESENTATION + (extra,)))
    assert report.passed is True


@given(st.permutations(REQUIRED_REPRESENTATION))
def test_oracle_representation_order_does_not_change_score(permutation: list[str]) -> None:
    report = evaluate(base_case(tuple(permutation)), base_proposal())
    assert report.passed is True
    assert report.metrics.representation_preserved is True
