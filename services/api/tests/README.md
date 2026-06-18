# Automated tests — pytest suite

Location: `services/api/tests/`  
Run: `pnpm api:test` (from repo root) or `uv run pytest` (from `services/api/`)

These tests run **offline** against pure Python logic. They do not start the HTTP server or hit Postgres.

---

## Test files

### `test_risk_engine.py`

Guards the **deterministic rule engine** (PRD §21.1). Highest priority — must pass before any rule publish.

| Test | Facts | Expected |
|---|---|---|
| `test_resume_screening_high_risk` | HR recruitment, filter/rank | `high_risk`, Annex III rule triggered |
| `test_credit_scoring_high_risk` | Credit scoring | `high_risk` |
| `test_customer_chatbot_limited_risk` | Customer support chatbot | `limited_risk` |
| `test_spam_filter_minimal_risk` | Other, no person impact | `minimal_risk` |
| `test_insufficient_information` | Missing required fields | `insufficient_information` |
| `test_no_eu_exposure` | `eu_market_exposure: no` | `minimal_risk`, `outside_eu_scope` flag |

**When adding a new rule:** add a fixture test here before seeding/publishing.

---

### `test_documents.py`

Guards document renderers (`app/documents/renderers.py`).

| Test | Verifies |
|---|---|
| `test_risk_memo_contains_version` | Markdown includes company, tier, version |
| `test_pdf_generation` | PDF starts with `%PDF` magic bytes |
| `test_evidence_zip` | ZIP builder produces non-empty archive |

---

### `test_seo.py`

Guards pSEO catalog data (`app/data/pseo_catalog.py`).

| Test | Verifies |
|---|---|
| `test_catalog_has_at_least_50_pages` | PRD §16 launch batch size |
| `test_unique_slugs` | No duplicate URL paths |
| `test_unique_titles` | SEO title uniqueness (PRD §21.3) |

---

## Running

```bash
# All tests
pnpm api:test

# Single file
cd services/api && uv run pytest tests/test_risk_engine.py -v

# Single test
cd services/api && uv run pytest tests/test_risk_engine.py::test_resume_screening_high_risk -v
```

**Expect:** `12 passed`

---

## Adding new tests

1. Create `tests/test_<module>.py`
2. Prefer pure functions (rules, renderers) over HTTP unless adding integration tests
3. Document the file in this README
4. For HTTP integration tests, consider `tests/test_api_integration.py` (future) with a test DB

---

## Future (not yet in repo)

- `test_api_integration.py` — FastAPI TestClient against ephemeral DB
- Playwright E2E — wizard → checkout → download
- CI workflow running `pytest` + smoke script on every PR

See also: [docs/testing/README.md](../../../docs/testing/README.md)
