# ADR-0005 — Versioning & legal traceability model

- **Status:** Accepted
- **Date:** 2026-06-14
- **Deciders:** Engineering, Legal/Rules
- **Related:** [technical-design.md §11](../technical-design.md) · [data-model.md §5.1, §12](../data-model.md) · PRD §10, §11.1, §13, §9.4

## Context

Regulations change (PRD §22 risk). Results must be reproducible, results/documents must record exactly what produced them (FR-DG-004), customers must be able to regenerate under the latest law (FR-DG-005), and admins must see the blast radius of a legal change before publishing (FR-ADMIN-004). The product also markets "last reviewed date + rule/source version" on every page (FR-SEO-004).

## Decision

Adopt an **append-only, immutable-version model** across the legal layer:
- **RuleSet** is the unit of publishing: monotonically increasing `version`, `status ∈ {draft,active,superseded,archived}`, **exactly one active** (enforced by partial unique index). Classification pins the active version at assessment time.
- **LegalSource/LegalReference** are versioned with `version_label`, `status`, `effective_date`, `retrieved_at`, and a `supersedes_id` chain.
- **Assessments** snapshot `rule_version + source_version + question_set_version + answers` on completion/lock (FR-AW-003).
- **GeneratedDocuments** embed the same triplet and are never mutated (FR-DG-004).
- **Time-aware evaluation:** rules carry `effective_from/to`; the engine receives `now` explicitly → "correct classification as of date X" is answerable.
- **Publish is guarded + transactional:** a draft can only go `active` if the full fixture suite passes; publishing computes change-impact (pages/templates/assessments) and triggers regeneration + customer notices (PRD §9.4).
- **Rollback is a one-row status flip** to the previous active version (immutability makes this safe).

## Alternatives considered

| Option | Why rejected |
|---|---|
| Mutate rules in place | Destroys reproducibility; old reports become unexplainable. |
| Full event-sourcing | Overkill for MVP; versioned snapshots give the needed guarantees at lower complexity. |
| Git-as-database for rules | Poor query/impact-analysis ergonomics; harder admin UX. |

## Consequences

- **Positive:** reproducible results, safe legal updates, instant rollback, marketable "last reviewed/version" metadata, and a defensible moat (versioned legal graph, PRD §6.3).
- **Negative:** more columns/joins and discipline around immutability; mitigated by DAL-level write guards (no UPDATE on published/generated rows) and DB constraints.
