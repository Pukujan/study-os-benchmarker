# SDD — Study OS Benchmarker v0.1

## Architecture

```text
BenchmarkCase envelope
   ├── CandidateContext ──→ candidate adapter
   └── BenchmarkOracle ───→ evaluator only
                               ↑
TutorProposal ─────────────────┘
                               ↓
                    deterministic Evaluator
                               ↓
                 Violation[] + metric results
                               ↓
                 canonical BenchmarkReport JSON
```

The evaluator is deliberately independent of candidate implementation. The runner must pass only `CandidateContext` to a candidate; `BenchmarkOracle` is evaluator-side state.

## Initial package

```text
src/study_os_benchmarker/
    models.py
    evaluator.py
```

No plugin framework in v0.1. Candidate adapters may implement a tiny protocol later.

## Contract objects

### CandidateContext

This is the entire candidate-visible payload for the first contract version:

- `schema_version`
- `case_id`
- `current_node`
- `visible_context`
- `visible_representation`

It must not contain evaluator-only expected next nodes, required bridge lists, forbidden answer literals, or hidden expected outcomes.

### BenchmarkOracle

Evaluator-only expectations:

- `allowed_next_nodes`
- `required_bridge_ids`
- `required_representation`
- `forbidden_concepts`
- `answer_reveal_allowed`
- `forbidden_answer_literals`

A public regression fixture may serialize an oracle beside its context for reproducibility, but candidate adapters must never receive that object. Sealed holdout oracles do not belong in this public repository at all.

### BenchmarkCase

An evaluator envelope containing exactly:

- `CandidateContext`
- `BenchmarkOracle`

The evaluator hashes the full case; the candidate runner exposes only `case.context`.

### TutorProposal

Normalized candidate output:

- proposed next node;
- claimed bridge IDs traversed/preserved;
- representation components shown;
- disclosed concepts;
- whether target answer was revealed;
- rendered text;
- candidate ID/version.

Candidate self-report is not authoritative. For example, `answer_revealed=false` does not prevent the evaluator from detecting a forbidden literal in `rendered_text`.

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
- canonical case/proposal digests;
- immutable metric summary.

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

1. strict/frozen Python boundary models;
2. immutable nested report structures rather than mutable containers hidden inside frozen objects;
3. independent JSON Schema Draft 2020-12 fixtures/contracts;
4. deterministic evaluator invariants;
5. pytest positive/negative fixtures;
6. Hypothesis property/metamorphic tests;
7. later mutation testing on scoring kernel.

## Failure behavior

Invalid case/proposal input fails closed before scoring.

The evaluator must not guess missing values or coerce structurally invalid data into legal values.

An unsupported/unknown schema version fails explicitly.

## Privacy boundary

No private transcript loader is implemented in this repository. A future private runner may materialize a benchmark contract from authorized evidence while keeping raw source and sealed holdout oracles outside this repository.

## Dependency boundary

v0.1 runtime dependencies remain limited to typed/schema validation. No donor/LLM framework enters the package before the deterministic evaluator gate passes.

## Compatibility

Readers may support explicitly listed historical schema versions. Writers emit only the current version. Do not silently reinterpret old fixtures under changed semantics.
