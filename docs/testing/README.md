# Testing documentation

How to verify the EU AI Act Compliance Navigator works end-to-end. This folder is the **living test guide** — add new `TESTING.md` files alongside new API modules as the product grows.

## Structure

| Document | Scope |
|---|---|
| [This file](./README.md) | Overview, prerequisites, smoke sequence, automated tests |
| [public API](../../services/api/app/public_api/TESTING.md) | Assessments, classify, pages, checkout, documents, downloads |
| [admin API](../../services/api/app/admin_api/TESTING.md) | Rules preview/publish, SEO regenerate, legal sources |
| [pytest suite](../../services/api/tests/README.md) | Automated unit tests (`pnpm api:test`) |
| [web app](../../apps/web/TESTING.md) | Browser flows, pages, UI expectations |

**Convention:** When you add a new API router package under `services/api/app/`, add a `TESTING.md` in that folder with endpoints, sample requests, and expected responses. Link it from this index.

---

## Prerequisites

```bash
cp .env.example .env
cp .env services/api/.env
pnpm install
pnpm db:up
pnpm api:migrate
pnpm api:seed
pnpm api:pseo
```

Start services:

```bash
# Terminal 1
pnpm api:dev          # http://localhost:8000

# Terminal 2
cd apps/web && pnpm dev   # http://localhost:3000
```

**Defaults used in examples below:**

| Variable | Local value |
|---|---|
| API base | `http://localhost:8000/api/v1` |
| Web base | `http://localhost:3000` |
| Admin key | `dev-admin-key` (from `.env`) |

Interactive API explorer: http://localhost:8000/docs

---

## Quick smoke test (5 minutes)

Run these in order. All should succeed before a demo or deploy.

### 1. Health

```bash
curl -s http://localhost:8000/healthz
```

**Expect:** `{"status":"ok","version":"0.2.0"}`

### 2. pSEO pages exist

```bash
curl -s "http://localhost:8000/api/v1/pages?limit=100" | python3 -c "import sys,json; print(len(json.load(sys.stdin)['data']))"
```

**Expect:** `55` (or more after regeneration)

### 3. Full assessment → classify

See [public API — Assessment flow](../../services/api/app/public_api/TESTING.md#assessment--classification-flow) for the full answer sequence.

**Expect after classify:**

- `classification_status`: `"classified"`
- `risk_tier`: `"high_risk"` (for resume screening answers)
- `triggered_rules`: at least one rule with `annex_iii_employment_recruitment_selection`
- `rule_version` and `source_version` populated

### 4. Dev checkout → evidence pack

**Expect:**

- Checkout returns `checkout_url` and `session_id`
- Document generate returns `202` with `report_id`
- After ~3s, `GET /documents/{report_id}` shows `status: "ready"` and 7 artifacts
- ZIP download returns HTTP 200 and a valid zip file

### 5. Admin rules preview

```bash
curl -s -X POST http://localhost:8000/api/v1/admin/rules/preview \
  -H 'Content-Type: application/json' \
  -H 'X-Admin-Key: dev-admin-key' \
  -d '{}'
```

**Expect:** `"all_pass": true`

---

## Automated tests

```bash
pnpm api:test
```

| Suite | File | What it guards |
|---|---|---|
| Rule engine | `tests/test_risk_engine.py` | Deterministic classification (PRD §21.1 fixtures) |
| Documents | `tests/test_documents.py` | MD/PDF/ZIP generation |
| SEO catalog | `tests/test_seo.py` | ≥50 unique pSEO slugs/titles |

**Expect:** `12 passed`

These run **without** a live API server (pure Python). They do not replace the HTTP smoke tests above.

---

## Functionality matrix

What each phase should do and how to verify it.

| Feature | How to test | Expected outcome |
|---|---|---|
| **Phase 1 — Wizard** | Web: `/eu-ai-act/compliance-checker` | Questions branch by use case; progress updates |
| **Phase 1 — Classify** | `POST .../classify` | Source-cited risk tier; never HTTP 500 |
| **Phase 2 — Dev checkout** | Buy button on result page or `POST /checkout/session` | Entitlement created without Stripe keys |
| **Phase 2 — Evidence pack** | `POST /documents/generate` | ZIP with MD, PDF, DOCX, CSV, XLSX |
| **Phase 2 — Downloads** | `GET /downloads/{token}` | File streams; 410 after expiry |
| **Phase 3 — pSEO** | `/eu-ai-act/hr-tech/resume-screening` | Page renders; API returns `content_md` |
| **Phase 3 — Sitemap** | `/sitemap.xml` | Includes static + dynamic page URLs |
| **Phase 4 — Admin preview** | `/admin` or admin API | Fixture suite passes before publish |
| **Phase 4 — SEO regenerate** | `POST /admin/seo-pages/regenerate` | `202`, `queued_pages: 55` |

---

## Known gaps (not yet testable)

Document these so testers don't chase false bugs:

- **Clerk auth** — not implemented; all assessments are anonymous
- **Real Stripe** — requires `STRIPE_SECRET_KEY` + price IDs; use dev checkout locally
- **Email** — no Resend integration yet
- **Playwright E2E** — not in repo; use manual web flows in [web TESTING.md](../../apps/web/TESTING.md)
- **FRIA / Annex IV** — templates aligned to Regulation (EU) 2024/1689 section outlines (Annex IV/V/VIII, Arts. 9–18, 26, 27, 43, 47, 49, 72, 73). Commission implementing-act forms (e.g. Art. 72(3) monitoring template, SME simplified Annex IV) must be ingested when published.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Classify returns 500 | Stale API process | Restart `pnpm api:dev` |
| Report `not_found` right after generate | Job ran before DB commit | Fixed in current code; restart API |
| `password authentication failed` for Postgres | Stale Docker volume | `docker compose -f infra/docker-compose.yml down -v && pnpm db:up` then re-migrate/seed |
| Checkout works but generate returns 403 | No entitlement | Run checkout first (dev mode auto-grants) |
| pSEO pages empty | Seed not run | `pnpm api:pseo` |

---

## Adding new test documentation

1. Create `services/api/app/<your_router>/TESTING.md`
2. Include: purpose, auth, endpoints table, curl examples, expected JSON shapes, failure cases
3. Add a row to the [Structure](#structure) table above
4. If adding pytest coverage, document the file in [tests/README.md](../../services/api/tests/README.md)
