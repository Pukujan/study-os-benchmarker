# Holdout and Blind Evaluation Protocol v0.1

## Purpose

Prevent Study OS compiler/runtime evaluation from overfitting to the development agent's knowledge of the September-4 calibration or leaking evaluator-only answers into Luna/fresh-subagent candidate workspaces.

## Evidence lanes

1. **Visible regression** — known/public failures used during development. Prevents regressions; not hidden evidence.
2. **Masked regression** — known source-backed cases with selected evidence systematically withheld from the candidate. Tests reconstruction under omission; not a true hidden holdout because developers know the original case.
3. **Sealed withheld calibration** — evaluator-only evidence/rubric is sealed before compiler/prompt development and never exposed to development agents or candidates. Opening it for debugging permanently contaminates the case.
4. **Prospective unseen evaluation** — a new learning problem/session created after the compiler exists. Strongest generalization lane.

## Luna / fresh-subagent boundary

Luna is an execution orchestrator, not the oracle. A blind candidate run must launch a fresh agent/model in a clean temporary workspace containing only an explicit candidate-input manifest.

Candidate-visible material may include only the problem, allowed learner state/context, the public PIR/compiler contract needed by the candidate, and explicitly permitted source evidence for that lane.

Candidate-visible material must not include:

- evaluator oracle files;
- expected node/edge lists;
- hidden bridge names;
- hidden learner corrections;
- hidden labels/answers/seeds;
- previous scored reports for the same sealed case;
- development-agent conversation/context;
- benchmark issue discussion that reveals the expected answer.

Where practical, oracle directories must not be mounted into the candidate workspace and network access must be disabled or constrained when it could reveal hidden material.

## Candidate-input receipt

Every blind run must retain a machine-readable receipt containing at least:

- case identity and evidence lane;
- exact candidate-visible files and SHA-256 identities;
- model/agent identity and revision;
- compiler prompt identity/revision;
- PIR revision;
- benchmarker revision;
- generation/runtime settings;
- contamination status.

The receipt must not contain hidden oracle content or descriptive hidden names that reveal the answer.

## Systematic masking

Do not cherry-pick only favorable masks. Eligible source-backed regions should support deterministic or seeded masks such as:

- leave-one-required-bridge-out;
- leave-one-learner-correction-out;
- leave-one-representation-calibration-out;
- leave-one-exercise/validation-pair-out;
- contiguous source-span masks at multiple sizes;
- neutral placeholders where needed to preserve parsability.

Retain failed runs and mask identities.

## Scoring boundary

Prefer deterministic scoring for required/forbidden node presence, ordering, representation preservation, explicit bridge presence, cycles, answer/future-information leakage, provenance resolution, and schema/transition legality.

Semantic human/LLM review is reported separately and may not override deterministic invariant failures.

## Contamination ledger

Each case is exactly one of:

- `public_regression`;
- `masked_regression`;
- `sealed_clean`;
- `contaminated_retired`;
- `prospective_clean`.

A sealed case becomes permanently contaminated if its oracle is opened by a development agent, its expected bridge/answer is discussed in development context, a prompt is tuned against it, a previous scored report is exposed to the candidate, or hidden material enters a candidate-readable repo/workspace.

Contaminated cases become regression material and can never again support a hidden-generalization claim.

## First experiment

After the complete September-4 source-backed golden exists:

1. freeze it as visible regression evidence;
2. generate systematic masked-regression cases;
3. run the compiler from fresh Luna subagents with no golden/summary/oracle access;
4. score outputs outside the candidate workspace;
5. preserve every failure and exact revision receipt;
6. do not call masked September-4 results generalization evidence;
7. reserve at least one sealed or prospective case the development agent has never inspected.

## Acceptance

A blind-evaluation run is auditable only when another worker can verify the exact candidate-visible bytes, oracle isolation boundary, model/agent identity, PIR/benchmarker/prompt revisions, deterministic score, mask identity, and contamination status without exposing hidden answers to the candidate.
