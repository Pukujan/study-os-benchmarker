"""Independent Study OS pedagogical benchmark harness."""

from .evaluator import EVALUATOR_VERSION, evaluate
from .models import (
    BenchmarkCase,
    BenchmarkOracle,
    BenchmarkReport,
    CandidateContext,
    TutorProposal,
    Violation,
    ViolationCode,
)

__all__ = [
    "EVALUATOR_VERSION",
    "BenchmarkCase",
    "BenchmarkOracle",
    "BenchmarkReport",
    "CandidateContext",
    "TutorProposal",
    "Violation",
    "ViolationCode",
    "evaluate",
]
