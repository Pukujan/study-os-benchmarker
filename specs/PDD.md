# PDD — Study OS Benchmarker v0.1

## Problem

Study OS needs to compare tutoring-control architectures without letting the production system grade itself, cherry-pick stochastic outputs, or smuggle known golden answers into candidate-visible context.

The benchmarker exists to answer a narrow engineering question first:

> Can an independent evaluator reliably distinguish a legal pedagogical proposal from known illegal trajectory mutations under a shared, versioned contract?

## Users

- Study OS developers deciding whether PIR constraints work;
- researchers comparing donor architectures;
- future agents auditing benchmark history.

## Goals

1. Define candidate-neutral benchmark case/proposal/report contracts.
2. Deterministically score machine-checkable pedagogical invariants.
3. Preserve benchmark provenance and exact revision identity.
4. Support positive fixtures and adversarial data/specification mutations.
5. Keep hidden/private evidence out of public candidate-visible assets.
6. Provide the later foundation for repeated stochastic runs, donor comparisons, ablations and prospective human evaluation.

## Non-goals for v0.1

- production tutoring;
- learner-state ownership;
- canonical PIR definition;
- LLM judge as authoritative scorer;
- donor package integration;
- external model API execution;
- hidden holdout storage;
- UI/dashboard;
- population efficacy claims.

## First success gate

Given one synthetic public benchmark case, the benchmarker must:

1. validate the case and proposal contracts;
2. score a deterministic legal proposal as passing;
3. reject at least these independent mutations:
   - required bridge deleted/skipped;
   - shortcut to forbidden future node/concept;
   - target answer leaked when forbidden;
   - required representation component removed;
4. emit a deterministic machine-readable report;
5. produce the same score from the same inputs and evaluator revision;
6. demonstrate that expected answers are evaluator-side and absent from candidate-visible input.

## Trust boundary

```text
candidate-visible BenchmarkCase
          ↓
     TutorCandidate
          ↓
     TutorProposal
          ↓
-------------------------------
 evaluator trust boundary
-------------------------------
          ↓
hidden evaluator expectations
          ↓
 deterministic scoring
          ↓
     BenchmarkReport
```

A candidate may receive only fields explicitly declared candidate-visible by the benchmark case schema.

## Evidence classes

Keep separate:

- deterministic contract result;
- stochastic repeated-run statistics;
- historical replay/fidelity;
- human behavioral outcomes;
- human self-report;
- LLM-judge semantic scores;
- hidden holdout results.

No report may collapse these into one unlabeled quality score.

## Privacy and contamination

This repository is public.

- Use synthetic/redacted fixtures only.
- Private September-4 transcript execution occurs in an authorized local/private lane.
- Hidden holdout answers never enter this repository.
- Once a hidden case is exposed for debugging, it is permanently retired into a normal regression fixture.

## External donor policy

CTAT, StratL, ScaffoldLM and MWPTutor are benchmark candidates/research donors, not automatic dependencies. Each donor requires a reuse assessment containing exact artifact/revision, license, reproducibility status and the component being tested.

## Versioning

Pre-v1 benchmark identity is the exact Git commit plus explicit schema versions. Package versions or mutable branch names are insufficient.

Fixture revisions receive new identities. Existing benchmark results remain historically interpretable.

## Kill/stop conditions

Stop horizontal expansion if the first deterministic gate cannot reliably reject obvious illegal mutations. Do not add LLMs or donors until evaluator trust is established.
