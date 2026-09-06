from __future__ import annotations

from pathlib import Path

from study_os_benchmarker.decomposition import (
    DecompositionOracle,
    DecompositionProjection,
    DecompositionViolationCode,
    ProjectedDecompositionStep,
    evaluate_decomposition,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = ROOT / "fixtures" / "public" / "compiler-development"


def load_oracle(name: str) -> DecompositionOracle:
    return DecompositionOracle.model_validate_json((FIXTURE_DIR / name).read_text())


def project(
    *,
    case_id: str,
    sequence: tuple[str, ...],
    representations: dict[str, tuple[str, ...]],
    invariants: tuple[str, ...],
    extra_concepts: tuple[str, ...] = (),
    candidate_version: str = "good-v1",
) -> DecompositionProjection:
    return DecompositionProjection(
        schema_version="benchmark.decomposition-projection.v1",
        case_id=case_id,
        candidate_id="test-candidate",
        candidate_version=candidate_version,
        concepts=extra_concepts,
        steps=tuple(
            ProjectedDecompositionStep(
                step_id=f"step-{index:02d}-{concept}",
                introduces=(concept,),
                representation_requirements=representations.get(concept, ()),
            )
            for index, concept in enumerate(sequence)
        ),
        invariants=invariants,
    )


def binary_good() -> DecompositionProjection:
    return project(
        case_id="dev.dsa.binary-search.v0",
        sequence=(
            "index",
            "array_value_lookup",
            "sorted_order",
            "target",
            "search_interval",
            "left_bound",
            "right_bound",
            "midpoint",
            "middle_value",
            "compare_target",
            "eliminate_half",
            "repeat_search",
            "termination",
        ),
        representations={
            "index": ("array_with_index_row",),
            "search_interval": ("highlighted_search_region",),
            "midpoint": ("middle_index_marker",),
            "eliminate_half": ("updated_search_region",),
        },
        invariants=("if target exists, it remains inside the active search interval",),
    )


def two_pointers_good() -> DecompositionProjection:
    return project(
        case_id="dev.dsa.two-pointers.v0",
        sequence=(
            "index",
            "sorted_order",
            "left_pointer",
            "right_pointer",
            "crossing_termination",
            "pair_sum",
            "compare_target",
            "move_left",
            "move_right",
            "repeat",
        ),
        representations={
            "left_pointer": ("array_with_two_pointer_markers",),
            "right_pointer": ("array_with_two_pointer_markers",),
            "pair_sum": ("selected_pair_with_sum",),
            "crossing_termination": ("pointer_boundary_state",),
        },
        invariants=(
            "sorted order makes pointer movement directional with respect to the target sum",
        ),
    )


def bfs_good() -> DecompositionProjection:
    return project(
        case_id="dev.dsa.bfs-shortest-path.v0",
        sequence=(
            "graph_node",
            "neighbor",
            "queue_frontier",
            "visited",
            "dequeue",
            "inspect_neighbors",
            "enqueue_unseen",
            "distance",
            "repeat_frontier",
        ),
        representations={
            "graph_node": ("graph_with_node_labels",),
            "queue_frontier": ("graph_with_queue",),
            "visited": ("graph_with_visited_state",),
            "dequeue": ("queue_head_marker",),
            "enqueue_unseen": ("queue_and_graph_transition",),
        },
        invariants=(
            "a node is enqueued at most once",
            "first discovery gives shortest edge distance in an unweighted graph",
        ),
    )


def codes(
    oracle: DecompositionOracle,
    projection: DecompositionProjection,
) -> tuple[DecompositionViolationCode, ...]:
    return tuple(
        violation.code for violation in evaluate_decomposition(oracle, projection).violations
    )


def test_good_decompositions_pass_for_all_three_development_families() -> None:
    cases = (
        ("binary-search.oracle.v1.json", binary_good()),
        ("two-pointers.oracle.v1.json", two_pointers_good()),
        ("bfs-shortest-path.oracle.v1.json", bfs_good()),
    )
    for oracle_name, projection in cases:
        report = evaluate_decomposition(load_oracle(oracle_name), projection)
        assert report.passed is True
        assert report.violations == ()
        assert all(report.metrics.model_dump().values())
        assert len(report.oracle_digest) == 64
        assert len(report.projection_digest) == 64


def test_case_mismatch_is_rejected_independently() -> None:
    oracle = load_oracle("binary-search.oracle.v1.json")
    projection = binary_good().model_copy(update={"case_id": "wrong-case"})
    assert codes(oracle, projection) == (DecompositionViolationCode.CASE_ID_MISMATCH,)


def test_missing_required_concept_is_rejected() -> None:
    oracle = load_oracle("binary-search.oracle.v1.json")
    projection = binary_good()
    steps = tuple(
        step for step in projection.steps if "target" not in step.introduces
    )
    projection = projection.model_copy(update={"steps": steps})
    assert codes(oracle, projection) == (DecompositionViolationCode.MISSING_CONCEPT,)


def test_required_concept_order_is_enforced() -> None:
    oracle = load_oracle("binary-search.oracle.v1.json")
    projection = binary_good()
    concepts = [step.introduces[0] for step in projection.steps]
    left_index = concepts.index("left_bound")
    midpoint_index = concepts.index("midpoint")
    concepts[left_index], concepts[midpoint_index] = concepts[midpoint_index], concepts[left_index]
    projection = project(
        case_id=projection.case_id,
        sequence=tuple(concepts),
        representations={
            "index": ("array_with_index_row",),
            "search_interval": ("highlighted_search_region",),
            "midpoint": ("middle_index_marker",),
            "eliminate_half": ("updated_search_region",),
        },
        invariants=projection.invariants,
        candidate_version="bad-order-v1",
    )
    assert codes(oracle, projection) == (DecompositionViolationCode.ORDERING_VIOLATION,)


def test_representation_must_attach_to_the_concept_step() -> None:
    oracle = load_oracle("binary-search.oracle.v1.json")
    projection = binary_good()
    steps = tuple(
        step.model_copy(update={"representation_requirements": ()})
        if "midpoint" in step.introduces
        else step
        for step in projection.steps
    )
    projection = projection.model_copy(update={"steps": steps})
    assert codes(oracle, projection) == (DecompositionViolationCode.MISSING_REPRESENTATION,)


def test_representation_requirement_fails_when_concept_is_only_declared_not_taught() -> None:
    oracle = load_oracle("binary-search.oracle.v1.json")
    projection = binary_good()
    steps = tuple(
        step for step in projection.steps if "midpoint" not in step.introduces
    )
    projection = projection.model_copy(
        update={"steps": steps, "concepts": ("midpoint",)}
    )
    assert codes(oracle, projection) == (DecompositionViolationCode.MISSING_REPRESENTATION,)


def test_missing_invariant_is_rejected() -> None:
    oracle = load_oracle("binary-search.oracle.v1.json")
    projection = binary_good().model_copy(update={"invariants": ()})
    assert codes(oracle, projection) == (DecompositionViolationCode.MISSING_INVARIANT,)


def test_forbidden_concept_is_rejected() -> None:
    oracle = load_oracle("binary-search.oracle.v1.json").model_copy(
        update={"forbidden_concepts": ("magic_binary_search_jump",)}
    )
    projection = binary_good().model_copy(
        update={"concepts": ("magic_binary_search_jump",)}
    )
    assert codes(oracle, projection) == (DecompositionViolationCode.FORBIDDEN_CONCEPT,)


def test_multi_concept_step_is_rejected_without_other_side_effects() -> None:
    oracle = load_oracle("binary-search.oracle.v1.json")
    projection = binary_good()
    target_step = next(step for step in projection.steps if "target" in step.introduces)
    sorted_step = next(step for step in projection.steps if "sorted_order" in step.introduces)
    combined = sorted_step.model_copy(
        update={"introduces": ("sorted_order", "target")}
    )
    steps = tuple(
        combined
        if step.step_id == sorted_step.step_id
        else step
        for step in projection.steps
        if step.step_id != target_step.step_id
    )
    projection = projection.model_copy(update={"steps": steps})
    assert codes(oracle, projection) == (
        DecompositionViolationCode.TOO_MANY_NEW_CONCEPTS,
    )
