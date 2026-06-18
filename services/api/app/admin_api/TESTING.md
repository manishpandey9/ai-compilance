# Admin API — testing guide

Base path: `/api/v1/admin`  
Router package: `app/admin_api/`  
Auth: **`X-Admin-Key` header** (default local value: `dev-admin-key` from `.env`)

All admin routes return **403** without a valid key.

Web UI alternative: http://localhost:3000/admin

---

## Authentication

Every request must include:

```bash
-H 'X-Admin-Key: dev-admin-key'
```

**Expect 403** with wrong or missing key:

```json
{
  "error": {
    "code": "forbidden",
    "message": "Invalid admin key",
    "details": []
  }
}
```

---

## Legal sources

### `POST /admin/legal-sources`

Create a draft legal source.

```bash
curl -s -X POST http://localhost:8000/api/v1/admin/legal-sources \
  -H 'Content-Type: application/json' \
  -H 'X-Admin-Key: dev-admin-key' \
  -d '{
    "title": "EU AI Act implementation guidance",
    "source_type": "guidance",
    "jurisdiction": "EU",
    "url": "https://example.com/guidance",
    "version_label": "guidance-2026-06"
  }'
```

**Expect (200):**

```json
{
  "id": 2,
  "title": "EU AI Act implementation guidance",
  "version_label": "guidance-2026-06",
  "status": "draft"
}
```

Writes an `audit_log` entry.

---

## Rules

### `POST /admin/rules/preview`

Run the fixture suite against the active ruleset. **Must pass before publish.**

```bash
curl -s -X POST http://localhost:8000/api/v1/admin/rules/preview \
  -H 'Content-Type: application/json' \
  -H 'X-Admin-Key: dev-admin-key' \
  -d '{}'
```

Optional body:

```json
{
  "rule_set_version": 1,
  "fixtures": ["resume_screening", "credit_scoring", "spam_filter"]
}
```

**Expect (200):**

```json
{
  "results": [
    { "fixture": "resume_screening", "expected_tier": "high_risk", "actual_tier": "high_risk", "pass": true },
    { "fixture": "credit_scoring", "expected_tier": "high_risk", "actual_tier": "high_risk", "pass": true },
    { "fixture": "spam_filter", "expected_tier": "minimal_risk", "actual_tier": "minimal_risk", "pass": true }
  ],
  "all_pass": true
}
```

| Fixture | Input summary | Expected tier |
|---|---|---|
| `resume_screening` | HR recruitment, filters/ranks candidates | `high_risk` |
| `credit_scoring` | Credit financial, scores persons | `high_risk` |
| `spam_filter` | Other use case, no person impact | `minimal_risk` |

**Expect `all_pass: false`** if a rule regression is introduced — do not publish.

---

### `GET /admin/rules/impact?rule_set_version={n}`

Change-impact analysis before publishing.

```bash
curl -s "http://localhost:8000/api/v1/admin/rules/impact?rule_set_version=1" \
  -H 'X-Admin-Key: dev-admin-key'
```

**Expect (200):**

```json
{
  "affected_seo_pages": ["hr-tech/resume-screening", "..."],
  "affected_templates": ["templates/annex-iv-technical-documentation", "..."],
  "affected_assessments": 42
}
```

---

### `POST /admin/rules/publish`

Publish a ruleset version. **Gated on fixture suite.**

```bash
curl -s -X POST http://localhost:8000/api/v1/admin/rules/publish \
  -H 'Content-Type: application/json' \
  -H 'X-Admin-Key: dev-admin-key' \
  -d '{"rule_set_version": 1}'
```

**Expect (200) on success:**

```json
{ "version": 1, "status": "active" }
```

**Expect (409)** if fixtures fail:

```json
{
  "error": {
    "code": "conflict",
    "message": "Fixture suite failed",
    "details": []
  }
}
```

Side effects:

- Previous `active` ruleset → `superseded`
- Target version → `active`
- `audit_log` entry created

---

## pSEO regeneration

### `POST /admin/seo-pages/regenerate`

Rebuild pSEO pages from `app/data/pseo_catalog.py`.

```bash
curl -s -X POST http://localhost:8000/api/v1/admin/seo-pages/regenerate \
  -H 'Content-Type: application/json' \
  -H 'X-Admin-Key: dev-admin-key' \
  -d '{"scope": "all"}'
```

Or specific slugs:

```json
{ "scope": "slugs", "slugs": ["hr-tech/resume-screening", "fintech/credit-scoring"] }
```

**Expect (202):**

```json
{ "queued_pages": 55 }
```

After completion, verify:

```bash
curl -s "http://localhost:8000/api/v1/pages?limit=100" | python3 -c "import sys,json; print(len(json.load(sys.stdin)['data']))"
```

**Expect:** 55 pages with updated `last_reviewed_at`.

---

## Not yet implemented (admin)

Document here when added:

- `PATCH /admin/legal-sources/{id}`
- `POST/PATCH /admin/rules`
- `POST/PATCH /admin/obligations`
- Template editor endpoints
- Rule change customer notification

When implementing, add a section to this file with curl examples and expected responses.
