# Design Documentation — EU AI Act Compliance Navigator & Evidence Pack Generator

This folder is the **design source of truth** for the product described in the PRD
(`/Users/hme/Downloads/AI_Act_Compliance_pSEO_PRD.md`, v1.0). Implementation follows
these specs — see the monorepo root `README.md` and `AGENTS.md` for how to run it.

## What this product is (one line)

A self-serve, source-cited **EU AI Act risk classifier and compliance evidence-pack generator**
for AI product teams and B2B SaaS vendors selling into the EU. Deterministic rule engine first,
LLM prose second; pSEO for acquisition; paid reports/packs + implementation sprints + subscription
for revenue.

## Read in this order

1. **[technical-design.md](./technical-design.md)** — the comprehensive TDD: goals/non-goals,
   principles, chosen stack + rationale, architecture (with mermaid diagrams), the deterministic
   rule engine, assessment wizard, document/evidence-pack pipeline, pSEO engine, payments, auth,
   security, infra/deploy, observability, testing, recommended project structure, AI-editor
   conventions, risks, and a phased roadmap mapped to the PRD.
2. **[data-model.md](./data-model.md)** — full schema: entities, columns, enums, JSONB shapes,
   indexes, reference DDL, lifecycle/retention, and integrity invariants.
3. **[api-contract.md](./api-contract.md)** — REST contract: every endpoint, request/response
   examples, error envelope, auth matrix, idempotency rules.
4. **[cost-model.md](./cost-model.md)** — unit economics: stack cost table, per-unit marginal
   cost, contribution margin per SKU, revenue scenarios mapped to the PRD, break-even, cost levers.
5. **[testing/README.md](./testing/README.md)** — how to test every feature; links to per-module `TESTING.md` files.
6. **[adr/](./adr/)** — architecture decision records for the key, hard-to-reverse choices.

## Architecture decision records

| ADR | Decision |
|---|---|
| [0001](./adr/0001-stack-and-topology.md) | Polyglot Next.js (web/pSEO) + FastAPI (engine/docs) monorepo |
| [0002](./adr/0002-database-neon-postgres.md) | Neon serverless PostgreSQL + SQLAlchemy/Alembic |
| [0003](./adr/0003-rule-engine-design.md) | Owned, pure, deterministic rule engine with JSON-AST conditions |
| [0004](./adr/0004-document-generation-pipeline.md) | Typst + python-docx + openpyxl + Jinja2 via a unified renderer |
| [0005](./adr/0005-versioning-and-traceability.md) | Append-only, immutable versioning of rules/sources/snapshots |

## Non-negotiable invariants (carried from the PRD)

- **Determinism is sacred** — LLMs never decide legal status (PRD §11.1).
- **Everything legal is versioned and immutable once published** (PRD §10, §13).
- **Source-cited everything** — no obligation/page/document without a legal reference (PRD §10.4, §21).
- **Ambiguity is a first-class result** — never fake certainty (PRD §10.2, §26.8).
- **Strict layer isolation** — engine ≠ API, templates ≠ legal DB, no logic in ORM models (PRD §11.5).

## Status

**All 4 implementation phases complete (MVP).**

| Phase | Status | Deliverables |
|---|---|---|
| Phase 1 | Done | Assessment wizard, deterministic rule engine, classify API, seed rules |
| Phase 2 | Done | Document generation (MD/PDF/DOCX/CSV/XLSX/ZIP), Dodo/dev checkout, entitlements, signed downloads |
| Phase 3 | Done | 55 pSEO pages, sitemap.xml, robots.txt, JSON-LD structured data, page composer |
| Phase 4 | Done | Admin API (rules preview/publish, SEO regenerate, legal sources), admin UI at `/admin` |

See root `README.md` for quick start.
