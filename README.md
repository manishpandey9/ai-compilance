# EU AI Act Compliance Navigator

Self-serve EU AI Act risk classifier and compliance evidence-pack generator for AI product teams.

## Stack

- **Web:** Next.js 15, TypeScript, Tailwind, shadcn/ui → Vercel
- **API:** Python 3.12, FastAPI, SQLAlchemy, Alembic → Render/Fly
- **DB:** PostgreSQL 16 (Neon in prod; Docker locally)
- **Queue:** Redis + RQ (Upstash in prod)
- **Storage:** S3-compatible (R2 in prod; MinIO locally)

## Quick start

```bash
# Prerequisites: Node 20+, pnpm, Docker, uv

cp .env.example .env
cp .env services/api/.env
pnpm install
pnpm db:up
cd services/api && uv sync && cd ../..
pnpm api:migrate
pnpm api:seed
pnpm api:pseo          # generate 55 pSEO pages

# Terminal 1 — API
pnpm api:dev

# Terminal 2 — Web
cd apps/web && pnpm dev
```

- API: http://localhost:8000/docs
- Web: http://localhost:3000
- Admin: http://localhost:3000/admin (key: `dev-admin-key` from `.env`)

## Dev checkout (no Stripe keys)

With `STRIPE_SECRET_KEY` empty, checkout auto-grants entitlements in dev mode. Complete an assessment → click **Buy evidence pack** → documents generate at `/reports/{reportId}`.

## Tests

```bash
pnpm api:test    # 12 automated tests
```

Full manual + API testing guide: [`docs/testing/README.md`](./docs/testing/README.md)

## Docs

Design specs live in [`docs/`](./docs/). Start with [`docs/technical-design.md`](./docs/technical-design.md).

## Project structure

```
apps/web/              Next.js frontend
services/api/          FastAPI backend + rule engine
packages/shared-types/ Cross-cutting TS types
packages/rule-schema/  JSON Schema for rule conditions
infra/                 docker-compose for local services
data/seeds/            Reference data and rule seeds
docs/                  Technical design + testing documentation
```
