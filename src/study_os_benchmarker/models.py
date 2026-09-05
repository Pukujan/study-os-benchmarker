from __future__ import annotations

import hashlib
import json
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class StrictFrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)


class CandidateContext(StrictFrozenModel):
    """Only this object may be passed to a candidate adapter."""

    schema_version: str = Field(pattern=r"^benchmark\.candidate-context\.v1$")
    case_id: str = Field(min_length=1)
    current_node: str = Field(min_length=1)
    visible_context: tuple[str, ...] = ()
    visible_representation: tuple[str, ...] = ()


class BenchmarkOracle(StrictFrozenModel):
    """Evaluator-side expectations. Never pass this object to the candidate."""

    schema_version: str = Field(pattern=r"^benchmark\.oracle\.v1$")
    allowed_next_nodes: tuple[str, ...] = ()
    required_bridge_ids: tuple[str, ...] = ()
    required_representation: tuple[str, ...] = ()
    forbidden_concepts: tuple[str, ...] = ()
    answer_reveal_allowed: bool = False
    forbidden_answer_literals: tuple[str, ...] = ()


class BenchmarkCase(StrictFrozenModel):
    schema_version: str = Field(pattern=r"^benchmark\.case\.v1$")
    context: CandidateContext
    oracle: BenchmarkOracle


class TutorProposal(StrictFrozenModel):
    schema_version: str = Field(pattern=r"^benchmark\.tutor-proposal\.v1$")
    candidate_id: str = Field(min_length=1)
    candidate_version: str = Field(min_length=1)
    proposed_next_node: str = Field(min_length=1)
    traversed_bridge_ids: tuple[str, ...] = ()
    shown_representation: tuple[str, ...] = ()
    disclosed_concepts: tuple[str, ...] = ()
    answer_revealed: bool = False
    rendered_text: str = ""


class ViolationCode(StrEnum):
    ILLEGAL_NEXT_NODE = "ILLEGAL_NEXT_NODE"
    MISSING_REQUIRED_BRIDGE = "MISSING_REQUIRED_BRIDGE"
    MISSING_REPRESENTATION = "MISSING_REPRESENTATION"
    FORBIDDEN_CONCEPT_DISCLOSED = "FORBIDDEN_CONCEPT_DISCLOSED"
    ANSWER_REVEAL_FORBIDDEN = "ANSWER_REVEAL_FORBIDDEN"


class Violation(StrictFrozenModel):
    code: ViolationCode
    detail: str = Field(min_length=1)


class MetricSummary(StrictFrozenModel):
    legal_next_node: bool
    required_bridges_preserved: bool
    representation_preserved: bool
    forbidden_concepts_absent: bool
    answer_policy_satisfied: bool


class BenchmarkReport(StrictFrozenModel):
    schema_version: str = Field(pattern=r"^benchmark\.report\.v1$")
    evaluator_version: str = Field(min_length=1)
    case_id: str = Field(min_length=1)
    candidate_id: str = Field(min_length=1)
    candidate_version: str = Field(min_length=1)
    passed: bool
    violations: tuple[Violation, ...]
    case_digest: str = Field(pattern=r"^[0-9a-f]{64}$")
    proposal_digest: str = Field(pattern=r"^[0-9a-f]{64}$")
    metrics: MetricSummary


def canonical_json_bytes(value: BaseModel | dict[str, Any]) -> bytes:
    if isinstance(value, BaseModel):
        payload: dict[str, Any] = value.model_dump(mode="json")
    else:
        payload = value
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def canonical_sha256(value: BaseModel | dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()
