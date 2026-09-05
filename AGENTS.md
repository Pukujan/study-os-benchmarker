# AGENTS.md — Study OS Benchmarker Contract

This repository is an **independent evaluator**, not Study OS runtime code.

## Non-negotiable invariants

1. Do not place private/raw learner transcripts in this public repository.
2. Do not place sealed hidden-holdout expected answers in candidate-visible files.
3. The evaluator owns scoring; candidates do not grade themselves.
4. Deterministic invariants outrank LLM-judge opinions.
5. Historical fidelity, prospective learner evaluation, and hidden holdout performance are separate evidence classes.
6. Benchmark fixtures and reports are versioned; do not rewrite old benchmark history to fit a new evaluator.
7. Every report pins exact evaluator, candidate, PIR/schema, donor, model/runtime and fixture revisions where applicable.
8. No manual cherry-picking of stochastic outputs.
9. Donor code requires exact source/revision/license provenance before import or adaptation.
10. This repository must not become a second canonical definition of Study OS PIR semantics.

## Change protocol

For substantive work:

1. Read issue #1 and `specs/PDD.md`, `specs/SDD.md`, `specs/VERIFICATION.md`.
2. State which benchmark invariant or gate the change closes.
3. Add deterministic positive and negative fixtures first where possible.
4. Add/update property, metamorphic or mutation tests for trust-kernel changes.
5. Run the full local check lane before declaring completion.
6. Record unresolved limitations explicitly.

## Scope lock

Until the first deterministic benchmark gate passes, do not add:

- live LLM API calls;
- donor packages;
- vector databases;
- orchestration frameworks;
- hidden holdout content;
- prospective human-study machinery;
- dashboards/UI.

The first gate is intentionally narrow: validate contracts, run a deterministic good candidate and intentionally bad proposals, detect bridge deletion/shortcut/answer leakage/representation loss, and emit a reproducible machine-readable report.
