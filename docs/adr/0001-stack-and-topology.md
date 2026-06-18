# ADR-0001 — Stack & topology: polyglot Next.js + FastAPI

- **Status:** Accepted
- **Date:** 2026-06-14
- **Deciders:** Engineering, Product
- **Related:** [technical-design.md §5, §6, §16](../technical-design.md) · PRD §14.1

## Context

The PRD recommends Astro/Next + FastAPI + Postgres + SQLAlchemy + queue + doc-gen + Stripe (§14.1). We must commit to a concrete topology that is (a) excellent for pSEO, (b) excellent for deterministic rule logic + document generation, (c) cost-effective at zero traffic, and (d) friendly to AI editors.

## Decision

Adopt a **polyglot monorepo**:
- **Web tier:** Next.js 15 (App Router) + TypeScript + Tailwind + shadcn/ui, deployed on Vercel with ISR for pSEO.
- **Engine tier:** Python 3.12 + FastAPI + Pydantic v2, hosting the deterministic rule engine, document generation, payments, and admin.
- **Contract:** FastAPI emits OpenAPI; a typed TS client is generated for the web tier (single source of truth). CI fails on drift.

## Alternatives considered

| Option | Why rejected |
|---|---|
| All-TypeScript (Node services) | Weak DOCX/XLSX/PDF + legal-rule-DSL ecosystem vs. Python; the engine deserves Python. |
| All-Python (server-rendered HTML) | Worse SEO/interaction ergonomics; loses RSC/ISR cost+perf wins for the pSEO surface that is the entire acquisition channel. |
| Microservices from day one | Premature complexity; the monolith-API + workers split is enough until scale demands more. |

## Consequences

- **Positive:** each tier uses its best tool; generated client neutralizes most polyglot drift; pSEO and doc-gen are both first-class; cheap to operate (TDD §5.5, cost-model).
- **Negative:** two toolchains (pnpm/Turbo + uv) and two deploy targets; mitigated by clear `AGENTS.md`, one-command scripts, and CI parity checks.
- **AI-editor impact:** strong — types/schemas are the source of truth; an agent edits one place and regenerates the client.
