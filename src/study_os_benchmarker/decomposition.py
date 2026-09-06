from __future__ import annotations

from enum import StrEnum

from pydantic import Field

from .models import StrictFrozenModel, canonical_sha256


class DecompositionViolationCode(StrEnum):
    CASE_ID_MISMATCH = "CASE_ID_MISMATCH"
    MISSING_CONCEPT = "MISSING_CONCEPT"
    ORDERING_VIOLATION = "ORDERING_VIOLATION"
    MISSING_REPRESENTATION = "MISSING_REPRESENTATION"
    MISSING_INVARIANT = "MISSING_INVARIANT"
    FORBIDDEN_CONCEPT = "FORBIDDEN_CONCEPT"
    TOO_MANY_NEW_CONCEPTS = "TOO_MANY_NEW_CONCEPTS"


class RequiredOrdering(StrictFrozenModel):
    before_concept: str = Field(min_length=1)
    after_concept: str = Field(min_length=1)


class RequiredRepresentation(StrictFrozenModel):
    concept_id: str = Field(min_length=1)
    representation_id: str = Field(min_length=1)


class DecompositionOracle(StrictFrozenModel):
    schema_version: str = Field(pattern=r"^benchmark\.decomposition-oracle\.v1$")
    case_id: str = Field(min_length=1)
    required_concepts: tuple[str, ...] = ()
    required_orderings: tuple[RequiredOrdering, ...] = ()
    required_representations: tuple[RequiredRepresentation, ...] = ()
    required_invariants: tuple[str, ...] = ()
    forbidden_concepts: tuple[str, ...] = ()
    max_new_concepts_per_step: int = Field(ge=1)


class ProjectedDecompositionStep(StrictFrozenModel):
    step_id: str = Field(min_length=1)
    introduces: tuple[str, ...] = ()
    representation_requirements: tuple[str, ...] = ()


class DecompositionProjection(StrictFrozenModel):
    schema_version: str = Field(pattern=r"^benchmark\.decomposition-projection\.v1$")
    case_id: str = Field(min_length=1)
    candidate_id: str = Field(min_length=1)
    candidate_version: str = Field(min_length=1)
    concepts: tuple[str, ...] = ()
    steps: tuple[ProjectedDecompositionStep, ...] = Field(min_length=1)
    invariants: tuple[str, ...] = ()


class DecompositionViolation(StrictFrozenModel):
    code: DecompositionViolationCode
    detail: str = Field(min_length=1)


class DecompositionMetrics(StrictFrozenModel):
    case_identity_valid: bool
    concept_coverage_valid: bool
    ordering_valid: bool
    representation_valid: bool
    invariants_valid: bool
    forbidden_concepts_absent: bool
    concept_budget_valid: bool


class DecompositionReport(StrictFrozenModel):
    schema_version: str = Field(pattern=r"^benchmark\.decomposition-report\.v1$")
    evaluator_version: str = Field(min_length=1)
    case_id: str = Field(min_length=1)
    candidate_id: str = Field(min_length=1)
    candidate_version: str = Field(min_length=1)
    passed: bool
    violations: tuple[DecompositionViolation, ...]
    oracle_digest: str = Field(pattern=r"^[0-9a-f]{64}$")
    projection_digest: str = Field(pattern=r"^[0-9a-f]{64}$")
    metrics: DecompositionMetrics


EVALUATOR_VERSION = "study-os-benchmarker.decomposition.v0.1.0"


def _concept_positions(projection: DecompositionProjection) -> dict[str, int]:
    positions: dict[str, int] = {}
    for index, step in enumerate(projection.steps):
        for concept in step.introduces:
            positions.setdefault(concept, index)
    return positions


def evaluate_decomposition(
    oracle: DecompositionOracle,
    projection: DecompositionProjection,
) -> DecompositionReport:
    violations: list[DecompositionViolation] = []

    case_identity_valid = projection.case_id == oracle.case_id
    if not case_identity_valid:
        violations.append(
            DecompositionViolation(
                code=DecompositionViolationCode.CASE_ID_MISMATCH,
                detail=(
                    f"projection case {projection.case_id!r} does not match "
                    f"oracle case {oracle.case_id!r}"
                ),
            )
        )

    introduced = {concept for step in projection.steps for concept in step.introduces}
    all_concepts = set(projection.concepts).union(introduced)
    missing_concepts = sorted(set(oracle.required_concepts) - all_concepts)
    concept_coverage_valid = not missing_concepts
    if missing_concepts:
        violations.append(
            DecompositionViolation(
                code=DecompositionViolationCode.MISSING_CONCEPT,
                detail=f"missing required concept(s): {', '.join(missing_concepts)}",
            )
        )

    positions = _concept_positions(projection)
    bad_orderings: list[str] = []
    for requirement in oracle.required_orderings:
        before = positions.get(requirement.before_concept)
        after = positions.get(requirement.after_concept)
        if before is not None and after is not None and before >= after:
            bad_orderings.append(
                f"{requirement.before_concept}->{requirement.after_concept}"
            )
    ordering_valid = not bad_orderings
    if bad_orderings:
        violations.append(
            DecompositionViolation(
                code=DecompositionViolationCode.ORDERING_VIOLATION,
                detail=f"required ordering violated: {', '.join(sorted(bad_orderings))}",
            )
        )

    representation_failures: list[str] = []
    for requirement in oracle.required_representations:
        matching_steps = tuple(
            step for step in projection.steps if requirement.concept_id in step.introduces
        )
        if not matching_steps or all(
            requirement.representation_id not in step.representation_requirements
            for step in matching_steps
        ):
            representation_failures.append(
                f"{requirement.concept_id}:{requirement.representation_id}"
            )
    representation_valid = not representation_failures
    if representation_failures:
        violations.append(
            DecompositionViolation(
                code=DecompositionViolationCode.MISSING_REPRESENTATION,
                detail=(
                    "missing required representation attachment(s): "
                    f"{', '.join(sorted(representation_failures))}"
                ),
            )
        )

    missing_invariants = sorted(set(oracle.required_invariants) - set(projection.invariants))
    invariants_valid = not missing_invariants
    if missing_invariants:
        violations.append(
            DecompositionViolation(
                code=DecompositionViolationCode.MISSING_INVARIANT,
                detail=f"missing required invariant(s): {', '.join(missing_invariants)}",
            )
        )

    forbidden = sorted(set(oracle.forbidden_concepts).intersection(all_concepts))
    forbidden_concepts_absent = not forbidden
    if forbidden:
        violations.append(
            DecompositionViolation(
                code=DecompositionViolationCode.FORBIDDEN_CONCEPT,
                detail=f"forbidden concept(s) present: {', '.join(forbidden)}",
            )
        )

    oversized_steps = tuple(
        step for step in projection.steps if len(step.introduces) > oracle.max_new_concepts_per_step
    )
    concept_budget_valid = not oversized_steps
    if oversized_steps:
        violations.append(
            DecompositionViolation(
                code=DecompositionViolationCode.TOO_MANY_NEW_CONCEPTS,
                detail=(
                    "step(s) exceed concept budget: "
                    + ", ".join(sorted(step.step_id for step in oversized_steps))
                ),
            )
        )

    metrics = DecompositionMetrics(
        case_identity_valid=case_identity_valid,
        concept_coverage_valid=concept_coverage_valid,
        ordering_valid=ordering_valid,
        representation_valid=representation_valid,
        invariants_valid=invariants_valid,
        forbidden_concepts_absent=forbidden_concepts_absent,
        concept_budget_valid=concept_budget_valid,
    )

    return DecompositionReport(
        schema_version="benchmark.decomposition-report.v1",
        evaluator_version=EVALUATOR_VERSION,
        case_id=oracle.case_id,
        candidate_id=projection.candidate_id,
        candidate_version=projection.candidate_version,
        passed=not violations,
        violations=tuple(violations),
        oracle_digest=canonical_sha256(oracle),
        projection_digest=canonical_sha256(projection),
        metrics=metrics,
    )
