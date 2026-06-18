# ADR-0003 — Deterministic rule engine design

- **Status:** Accepted
- **Date:** 2026-06-14
- **Deciders:** Engineering, Legal/Rules
- **Related:** [technical-design.md §7.3, §11](../technical-design.md) · PRD §3, §10.2, §11.1, §14.3

## Context

Legal risk classification carries liability (PRD §19, §22) and must be **deterministic, explainable, source-traceable, and versioned**. An LLM must never decide legal status (PRD §11.1, FR-RE-001). The engine must flag ambiguity rather than guess (FR-RE-003).

## Decision

Build a **small, owned, pure-function rule engine**:
- Signature: `classify(facts, ruleset, sources, now) -> Classification` — no I/O, no randomness, time passed explicitly.
- Conditions expressed as a **JSON boolean AST** (`all/any/none` + typed leaf operators), interpreted by a sandboxed recursive evaluator (no `eval`).
- Fixed execution order: validate → EU scope → role → **prohibited** → high-risk (Annex I then Annex III) → limited-risk/transparency → minimal-risk fallback → obligations → documents → trace (PRD §14.3, FR-RE-004…007).
- First-class ambiguity states: `needs_expert_review`, `insufficient_information`, `possibly_high_risk`, `conflicting_rules`.
- Every result carries a full **source trace** (triggered + non-triggered relevant rules, legal references, inputs used, rationale, confidence).
- Rules grouped into **immutable, versioned rulesets**; each classification pins `rule_version` + `source_version`.

## Alternatives considered

| Option | Why rejected |
|---|---|
| LLM-based classification | Non-deterministic, unexplainable, legally unsafe — violates PRD §11.1. |
| External rules engine (Drools, etc.) | Heavy, JVM/foreign DSL, poor AI-editor legibility, large footprint. |
| Hard-coded Python `if/else` rules | Not data-editable; admin can't add use cases without a deploy; harder to version. |

## Consequences

- **Positive:** reproducible, auditable, testable; adding a use case is a **data edit + a fixture**, the safest possible change for an AI editor; the engine is the moat (PRD §6.3).
- **Negative:** we maintain a small interpreter and AST schema; mitigated by exhaustive unit tests + JSON Schema validation.
- **Guardrail:** every new `RiskRule` ships with a fixture; the full fixture suite (PRD §21.1) gates rule publishing (TDD §7.7, §15).
