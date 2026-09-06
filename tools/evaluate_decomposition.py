from __future__ import annotations

import argparse
from pathlib import Path

from study_os_benchmarker.decomposition import (
    DecompositionOracle,
    DecompositionProjection,
    evaluate_decomposition,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate one normalized canonical decomposition projection."
    )
    parser.add_argument("--oracle", type=Path, required=True)
    parser.add_argument("--projection", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    oracle = DecompositionOracle.model_validate_json(args.oracle.read_text())
    projection = DecompositionProjection.model_validate_json(args.projection.read_text())
    report = evaluate_decomposition(oracle, projection)

    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(report.model_dump_json(indent=2))

    print(f"passed={str(report.passed).lower()}")
    for violation in report.violations:
        print(f"{violation.code.value}: {violation.detail}")

    return 0 if report.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
