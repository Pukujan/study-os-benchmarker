# SDD — Study OS Benchmarker v0.1

## Architecture

```text
JSON benchmark case
        ↓
strict contract model
        ↓
Candidate adapter
        ↓
normalized TutorProposal
        ↓
deterministic Evaluator
        ↓
Violation[] + metric results
        ↓
canonical BenchmarkReport JSON
```

The evaluator is deliberately independent of candidate implementation.

## Initial package

```text
src/study_os_benchmarker/
    models.py
    evaluator.py
```

No plugin framework in v0.1. Candidate adapters may implement a tiny protocol later.

## Contract objects

### BenchmarkCase

Candidate-visible fields:

- `schema_version`
- `case_id`
- `current_node`
- `allowed_next_nodes`
- `required_bridge_ids`
- `required_representation`
- `forbidden_concepts`
- `answer_reveal_allowed`
- `visible_context`

Evaluator-only expected target text/answers MUST NOT be stored in this candidate-visible object.

### TutorProposal

Normalized candidate output:

- proposed next node;
- claimed bridge IDs traversed/preserved;
- representation components shown;
- disclosed concepts;
- whether target answer was revealed;
- rendered text;
- optional candidate metadata.

### Violation

Stable code + bounded detail.

Initial violation codes:

- `ILLEGAL_NEXT_NODE`
- `MISSING_REQUIRED_BRIDGE`
- `MISSING_REPRESENTATION`
- `FORBIDDEN_CONCEPT_DISCLOSED`
- `ANSWER_REVEAL_FORBIDDEN`

### BenchmarkReport

- case ID;
- evaluator version;
- candidate ID/version;
- pass/fail;
- violations in deterministic stable order;
- canonical input/proposal digests;
- metrics.

## Determinism

Scoring is a pure function of validated `BenchmarkCase` + validated `TutorProposal` + evaluator version.

No current time, randomness, network, environment-specific paths or model calls participate in the v0.1 score.

Violation ordering is fixed by evaluator rule order rather than set/hash iteration.

## Canonical serialization

For v0.1 machine-readable object hashing:

- UTF-8 JSON;
- sorted object keys;
- separators `(',', ':')`;
- no insignificant whitespace;
- Unicode emitted consistently;
- SHA-256 over canonical UTF-8 bytes.

This is an evaluator/report identity mechanism, not a replacement for PIR's own future canonicalization rules.

## Validation layers

1. strict Python boundary models;
2. independent JSON Schema Draft 2020-12 fixtures/contracts;
3. deterministic evaluator invariants;
4. pytest positive/negative fixtures;
5. Hypothesis/property tests;
6. later mutation testing on scoring kernel.

## Failure behavior

Invalid case/proposal input fails closed before scoring.

The evaluator must not guess missing values or coerce structurally invalid data into legal values.

An unsupported/unknown schema version fails explicitly.

## Privacy boundary

No private transcript loader is implemented in this repository. A future private runner may materialize a public benchmark contract from authorized evidence while keeping raw source outside this repository.

## Dependency boundary

v0.1 runtime dependencies should remain limited to typed/schema validation. No donor/LLM framework enters the package before the deterministic evaluator gate passes.

## Compatibility

Readers may support explicitly listed historical schema versions. Writers emit only the current version. Do not silently reinterpret old fixtures under changed semantics.
