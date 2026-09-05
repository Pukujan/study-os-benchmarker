# Verification — Study OS Benchmarker v0.1

A requirement is not closed because an agent says it is done. Each invariant below must resolve to deterministic evidence.

## Traceability matrix

| ID | Invariant / threat | Positive test | Negative / adversarial test | Later strengthening |
|---|---|---|---|---|
| BINV-001 | Legal next node is accepted | exact legal proposal passes | unrelated/forbidden node -> `ILLEGAL_NEXT_NODE` | mutation testing |
| BINV-002 | Required pedagogical bridges cannot disappear | proposal carries every required bridge | delete one bridge -> `MISSING_REQUIRED_BRIDGE` | deletion mutation over every bridge |
| BINV-003 | Required representation persists | all required components shown | remove box/index/array component -> `MISSING_REPRESENTATION` | subset property tests |
| BINV-004 | Forbidden future concepts remain absent | no forbidden disclosures | disclose one -> `FORBIDDEN_CONCEPT_DISCLOSED` | generated forbidden sets |
| BINV-005 | Answer reveal policy is enforced | no reveal when forbidden | reveal target answer -> `ANSWER_REVEAL_FORBIDDEN` | semantic leak detector later |
| BINV-006 | Scoring is deterministic | same input -> identical canonical report | randomized input ordering cannot change semantic score | repeat CI runs |
| BINV-007 | Candidate-visible case contains no evaluator expected answer field | schema inspection | fixture containing forbidden expectation keys rejected | contamination scanner |
| BINV-008 | Invalid types/extra fields fail closed | valid strict model | coercion/unknown field rejected | Hypothesis malformed JSON |
| BINV-009 | Machine report has stable provenance digests | known digest fixture | one semantic input change changes relevant digest | differential property test |
| BINV-010 | Violation order is stable | multi-failure expected order | unordered set implementation mutation killed | mutmut |
| BINV-011 | Benchmark history is revision-addressed | report includes evaluator/candidate versions | missing version rejected | exact Git revision manifest later |
| BINV-012 | Public repo contains only public/redacted fixtures | synthetic fixture classification | private/hidden marker policy test | CI secret/content scan later |

## First fixture

The public synthetic case models the structural shape of a high-sensitivity bridge without embedding a private learner transcript:

```text
current node: write_S0
required bridge: S0_to_Si_when_i0
allowed next node: write_Si
required representation: array, index_row, box, i_equals_0
forbidden concept: max_comparison
answer reveal: forbidden
```

The deterministic legal proposal must pass.

Independent bad proposals must fail for exactly one targeted reason where practical:

1. skip bridge;
2. jump to comparison node/concept;
3. remove box;
4. reveal target answer.

## Property/metamorphic requirements

Add Hypothesis tests for:

- permutation of input list/set-like fields does not change normalized score when semantics are set-valued;
- adding an irrelevant representation component cannot turn a legal proposal illegal;
- removing a required representation component always makes a previously legal proposal fail;
- adding a forbidden disclosed concept always makes a previously legal proposal fail;
- removing a required bridge always makes a previously legal proposal fail;
- repeated evaluation is byte-identical after canonical serialization.

## Mutation gate

Once the trust kernel is stable enough for `mutmut`, mutations in these rules must be killed:

- `in allowed_next_nodes` inverted/removed;
- required bridge subset test weakened;
- required representation subset test weakened;
- forbidden-concept intersection test removed;
- answer-reveal condition inverted;
- one violation branch deleted.

Critical surviving non-equivalent mutants must be zero before declaring benchmarker v0.1 trustworthy.

## What this verification does NOT prove

Passing these tests does not prove tutoring efficacy, generalization, learner benefit, semantic correctness of an LLM response, or correctness of PIR itself. It proves only that the benchmark evaluator enforces its declared structural contract reproducibly.
