# Study OS Benchmarker

Independent, versioned evaluation harness for Study OS Pedagogical IR (PIR) and tutoring-control donor architectures.

Parent design tracker: https://github.com/Pukujan/Study-os/issues/65
Benchmark tracker: https://github.com/Pukujan/study-os-benchmarker/issues/1

## Boundary

This repository evaluates candidates. It is not Study OS runtime code and it does not define canonical PIR semantics.

It may contain:

- public synthetic/redacted benchmark fixtures;
- candidate adapters;
- deterministic scorers;
- mutation/metamorphic generators;
- benchmark schemas and reports;
- donor/reuse assessments.

It must not contain:

- private raw learner transcripts;
- sealed hidden-holdout expected answers;
- Study OS production learner state;
- secrets/API credentials;
- copied donor code without reviewed license provenance.

## First vertical slice

The first gate intentionally does not call an LLM. It proves the evaluator can distinguish a legal trajectory proposal from known illegal pedagogical mutations.

```text
public synthetic case
        ↓
deterministic reference candidate
        ↓
deterministic evaluator
        ↓
versioned machine-readable report

plus intentionally bad proposals:
- required bridge deleted
- shortcut over required state
- answer leaked
- required representation removed
```

Only after this gate passes should nondeterministic or external donor candidates be added.

## Development

Python 3.12+.

```bash
python -m pip install -e '.[dev]'
pytest
ruff check .
mypy src tests
```

The eventual benchmark report must pin exact evaluator, candidate, PIR/schema and model/runtime revisions. Mutable branch names are not sufficient experimental identity.
