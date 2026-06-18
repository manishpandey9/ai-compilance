# ADR-0002 — Database: Neon serverless PostgreSQL

- **Status:** Accepted
- **Date:** 2026-06-14
- **Deciders:** Engineering
- **Related:** [technical-design.md §5.3](../technical-design.md) · [data-model.md](../data-model.md) · PRD §14.1

## Context

We need a relational database for a versioned legal knowledge graph, JSONB rule conditions, assessment data, and FTS-based site search. It must be cheap when idle (pre-revenue) and support an AI-driven dev workflow (isolated test databases per change).

## Decision

Use **PostgreSQL 16 on Neon** (serverless), with **SQLAlchemy 2.0 + Alembic**.

## Rationale

- **Scale-to-zero compute** → near-$0 idle cost during validation (cost-model §2).
- **Database branching** per PR/agent run → CI and AI editors run the full rule-engine integration suite against an isolated copy, then discard it.
- **JSONB + GIN** fits `condition_json`, `answer_value_json`, `result_json`, `structured_data_json`.
- **Native FTS** powers initial search with no extra vendor (defer Meilisearch).
- **Relational integrity** protects the immutable, versioned legal graph (single-active-ruleset constraint, source-cited FKs).

## Alternatives considered

| Option | Why rejected |
|---|---|
| Supabase Postgres | Bundles auth+storage (couples concerns we want behind ports); still viable as a fallback. |
| AWS RDS | No scale-to-zero; higher idle cost; heavier ops. |
| PlanetScale / MySQL | Weaker JSONB ergonomics; historically FK constraints limited. |
| SQLite | Insufficient for concurrent web workload + JSONB/FTS needs. |

## Consequences

- **Positive:** lowest idle cost, great dev ergonomics, strong data integrity.
- **Negative:** cold-start latency on first query after idle (acceptable; can keep warm in prod).
- **Migration risk:** standard Postgres → portable to any Postgres host if Neon pricing changes.
