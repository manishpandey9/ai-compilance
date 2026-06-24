# AI Act Navigator — Agent Guide

Monorepo for the **EU AI Act Compliance Navigator & Evidence Pack Generator**.

## Architecture map

```
apps/web          → Next.js 15 (pSEO, wizard, dashboard) — talks to API via generated client
services/api      → FastAPI (rule engine, docs, payments, admin)
packages/         → shared-types (TS enums), rule-schema (JSON Schema for conditions)
infra/            → docker-compose (Postgres, Redis, MinIO)
docs/             → design source of truth (read before large changes)
```

## Non-negotiable invariants

1. **LLMs never decide legal status** — deterministic rule engine only.
2. **Everything legal is versioned and immutable once published.**
3. **No business logic in ORM models** — behavior in `services/` and `rules/`.
4. **Source-cited everything** — obligations/pages/docs require legal references.
5. **Ambiguity is first-class** — `needs_expert_review`, `insufficient_information`, `conflicting_rules`.

## Where to edit what

| Task | Location |
|---|---|
| Add a risk rule | `data/seeds/rules.json` + fixture in `services/api/tests/fixtures/` + seed loader in `services/api/app/scripts/seed.py` |
| Rule engine logic | `services/api/app/rules/` (pure, no I/O) |
| API endpoints | `services/api/app/public_api/`, `admin_api/` — add `TESTING.md` per package |
| DB schema | `services/api/app/models.py` + Alembic migration |
| pSEO pages | `apps/web/src/app/eu-ai-act/` + `services/api/app/data/pseo_catalog.py` + `services/api/app/scripts/generate_pseo.py` |
| Assessment wizard | `apps/web/src/app/assessment/` + `services/api/app/services/assessment_service.py` |
| Document templates | `services/api/app/documents/` |

## Local dev

See [`docs/testing/README.md`](docs/testing/README.md) for full test flows.

```bash
pnpm db:up          # Postgres + Redis + MinIO
pnpm api:migrate    # run migrations
pnpm api:seed       # seed reference data + sample rules
pnpm api:dev        # API on :8000
cd apps/web && pnpm dev   # web on :3000
```

## Before rule publish

Run `pnpm api:test` — the rule-engine fixture suite gates publishing.
