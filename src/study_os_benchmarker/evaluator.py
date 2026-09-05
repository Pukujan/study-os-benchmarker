from __future__ import annotations

from .models import (
    BenchmarkCase,
    BenchmarkReport,
    MetricSummary,
    TutorProposal,
    Violation,
    ViolationCode,
    canonical_sha256,
)

EVALUATOR_VERSION = "study-os-benchmarker.evaluator.v0.1.0"


def evaluate(case: BenchmarkCase, proposal: TutorProposal) -> BenchmarkReport:
    """Evaluate a normalized proposal against evaluator-side expectations.

    Rule order is part of deterministic report semantics. Do not replace the ordered
    checks below with unordered iteration over sets/maps.
    """

    oracle = case.oracle
    violations: list[Violation] = []

    legal_next_node = proposal.proposed_next_node in oracle.allowed_next_nodes
    if not legal_next_node:
        violations.append(
            Violation(
                code=ViolationCode.ILLEGAL_NEXT_NODE,
                detail=f"proposed next node {proposal.proposed_next_node!r} is not allowed",
            )
        )

    missing_bridges = sorted(set(oracle.required_bridge_ids) - set(proposal.traversed_bridge_ids))
    required_bridges_preserved = not missing_bridges
    if missing_bridges:
        violations.append(
            Violation(
                code=ViolationCode.MISSING_REQUIRED_BRIDGE,
                detail=f"missing required bridge(s): {', '.join(missing_bridges)}",
            )
        )

    missing_representation = sorted(
        set(oracle.required_representation) - set(proposal.shown_representation)
    )
    representation_preserved = not missing_representation
    if missing_representation:
        violations.append(
            Violation(
                code=ViolationCode.MISSING_REPRESENTATION,
                detail=f"missing required representation: {', '.join(missing_representation)}",
            )
        )

    disclosed_forbidden = sorted(
        set(oracle.forbidden_concepts).intersection(proposal.disclosed_concepts)
    )
    forbidden_concepts_absent = not disclosed_forbidden
    if disclosed_forbidden:
        violations.append(
            Violation(
                code=ViolationCode.FORBIDDEN_CONCEPT_DISCLOSED,
                detail=f"forbidden concept(s) disclosed: {', '.join(disclosed_forbidden)}",
            )
        )

    leaked_literals = sorted(
        literal
        for literal in oracle.forbidden_answer_literals
        if literal and literal in proposal.rendered_text
    )
    answer_policy_satisfied = oracle.answer_reveal_allowed or not (
        proposal.answer_revealed or leaked_literals
    )
    if not answer_policy_satisfied:
        reasons: list[str] = []
        if proposal.answer_revealed:
            reasons.append("proposal marked answer_revealed=true")
        if leaked_literals:
            reasons.append(f"forbidden literal(s) present: {', '.join(leaked_literals)}")
        violations.append(
            Violation(
                code=ViolationCode.ANSWER_REVEAL_FORBIDDEN,
                detail="; ".join(reasons),
            )
        )

    metrics = MetricSummary(
        legal_next_node=legal_next_node,
        required_bridges_preserved=required_bridges_preserved,
        representation_preserved=representation_preserved,
        forbidden_concepts_absent=forbidden_concepts_absent,
        answer_policy_satisfied=answer_policy_satisfied,
    )

    return BenchmarkReport(
        schema_version="benchmark.report.v1",
        evaluator_version=EVALUATOR_VERSION,
        case_id=case.context.case_id,
        candidate_id=proposal.candidate_id,
        candidate_version=proposal.candidate_version,
        passed=not violations,
        violations=tuple(violations),
        case_digest=canonical_sha256(case),
        proposal_digest=canonical_sha256(proposal),
        metrics=metrics,
    )
