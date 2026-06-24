# Public API — testing guide

Base path: `/api/v1`  
Router package: `app/public_api/`  
Files: `assessments.py`, `pages.py`, `documents.py`

Swagger: http://localhost:8000/docs (tags: `assessments`, `pages`, `documents`, `payments`)

---

## Assessments

### `POST /assessments`

Create a draft assessment. Anonymous — no auth required.

```bash
curl -s -X POST http://localhost:8000/api/v1/assessments \
  -H 'Content-Type: application/json' \
  -d '{"company_name":"Acme AI","system_name":"HireRank"}'
```

**Expect (201):**

```json
{
  "assessment_id": "aia_01KV...",
  "status": "draft",
  "question_set_version": 1,
  "claim_token": "tok_..."
}
```

Save `assessment_id` and `claim_token` for later steps.

---

### `GET /assessments/{assessment_id}`

```bash
curl -s http://localhost:8000/api/v1/assessments/{assessment_id}
```

**Expect (200):**

- `status`: `draft` | `in_progress` | `completed`
- `answers`: object of submitted keys
- `next_questions`: array with **one** question (branching wizard)
- `progress.answered` / `progress.remaining_estimate`

**404** if unknown `assessment_id`.

---

### `PATCH /assessments/{assessment_id}`

Update metadata or capture email.

```bash
curl -s -X PATCH http://localhost:8000/api/v1/assessments/{assessment_id} \
  -H 'Content-Type: application/json' \
  -d '{"email":"founder@acme.ai","marketing_consent":true}'
```

**Expect (200):** Same shape as `GET`, with updated fields.

---

### `POST /assessments/{assessment_id}/answers`

Upsert one or more answers. Returns refreshed `next_questions`.

```bash
curl -s -X POST http://localhost:8000/api/v1/assessments/{assessment_id}/answers \
  -H 'Content-Type: application/json' \
  -d '{"answers":[{"question_key":"eu_market_exposure","value":"yes"}]}'
```

**Expect (200):** Updated `answers` map; next question advances.

---

## Assessment & classification flow

Complete this sequence to test **high-risk resume screening** (PRD §18.1).

```bash
AID="<your-assessment_id>"

# 1. EU exposure
curl -s -X POST "http://localhost:8000/api/v1/assessments/$AID/answers" \
  -H 'Content-Type: application/json' \
  -d '{"answers":[{"question_key":"eu_market_exposure","value":"yes"}]}'

# 2. Actor role
curl -s -X POST "http://localhost:8000/api/v1/assessments/$AID/answers" \
  -H 'Content-Type: application/json' \
  -d '{"answers":[{"question_key":"actor_role","value":"provider"}]}'

# 3. Use case
curl -s -X POST "http://localhost:8000/api/v1/assessments/$AID/answers" \
  -H 'Content-Type: application/json' \
  -d '{"answers":[{"question_key":"use_case_category","value":"employment_recruitment"}]}'

# 4. Affects natural persons
curl -s -X POST "http://localhost:8000/api/v1/assessments/$AID/answers" \
  -H 'Content-Type: application/json' \
  -d '{"answers":[{"question_key":"affects_natural_persons","value":true}]}'

# 5. System function (branch question)
curl -s -X POST "http://localhost:8000/api/v1/assessments/$AID/answers" \
  -H 'Content-Type: application/json' \
  -d '{"answers":[{"question_key":"system_function","value":["filter_applications","rank_candidates"]}]}'
```

### `POST /assessments/{assessment_id}/classify`

```bash
curl -s -X POST "http://localhost:8000/api/v1/assessments/$AID/classify"
```

**Expect (200):**

| Field | Expected value |
|---|---|
| `classification_status` | `"classified"` |
| `risk_tier` | `"high_risk"` |
| `confidence` | `"high"` or `"medium"` |
| `primary_actor_role` | `"provider"` |
| `triggered_rules[0].rule_code` | `annex_iii_employment_recruitment_selection` |
| `free_preview.top_obligations` | Non-empty list (if obligations seeded) |
| `rule_version` | `1` (or current active ruleset) |

**Other valid outcomes (also 200, not errors):**

- `classification_status: "insufficient_information"` + `missing_fields[]`
- `classification_status: "needs_expert_review"` for edge cases

### Chatbot → limited risk

Use `use_case_category: "customer_support"` and answer `interacts_with_users: true`.

**Expect:** `risk_tier: "limited_risk"`

### Spam-filter-like → minimal risk

Use `use_case_category: "other"`, `affects_natural_persons: false`.

**Expect:** `risk_tier: "minimal_risk"`

---

### `GET /assessments/{assessment_id}/result`

Returns stored classification (same shape as classify response).

```bash
curl -s "http://localhost:8000/api/v1/assessments/$AID/result"
```

**Expect (200):** Same as classify after completion.  
**404** if not yet classified.

---

## Pages (pSEO)

### `GET /pages?type=&limit=&cursor=`

```bash
curl -s "http://localhost:8000/api/v1/pages?limit=10"
```

**Expect (200):**

```json
{
  "data": [
    {
      "slug": "hr-tech/resume-screening",
      "title": "EU AI Act Compliance for Resume Screening",
      "page_type": "use_case",
      "last_reviewed_at": "2026-..."
    }
  ]
}
```

**Expect ≥55 pages** after `pnpm api:pseo`.

---

### `GET /pages/{slug}`

```bash
curl -s http://localhost:8000/api/v1/pages/hr-tech/resume-screening
```

**Expect (200):**

- `title`, `meta_description`, `content_md` (markdown body)
- `structured_data` (FAQ + Breadcrumb JSON-LD)
- `canonical_url`
- `references[]` with legal citations
- `rule_version`

**404** if slug not `active`.

---

## Payments & documents

### `POST /checkout/session`

```bash
curl -s -X POST http://localhost:8000/api/v1/checkout/session \
  -H 'Content-Type: application/json' \
  -d '{
    "assessment_id": "'"$AID"'",
    "sku": "evidence_pack",
    "success_url": "http://localhost:3000/checkout/success",
    "cancel_url": "http://localhost:3000/pricing"
  }'
```

**SKU:** `evidence_pack`

**Expect (200) — dev mode (no Dodo/Stripe keys):**

```json
{
  "checkout_url": "http://localhost:3000/checkout/success?session_id=cs_dev_...&assessment_id=...&sku=evidence_pack&dev=1",
  "session_id": "cs_dev_..."
}
```

Dev mode **auto-creates an active entitlement**. With Dodo configured, expect a Dodo hosted checkout URL instead.

---

### `POST /documents/generate`

Requires **active entitlement** for the assessment + SKU.

```bash
curl -s -X POST http://localhost:8000/api/v1/documents/generate \
  -H 'Content-Type: application/json' \
  -d '{"assessment_id":"'"$AID"'","sku":"evidence_pack"}'
```

**Expect (202):**

```json
{ "report_id": "rep_01KV...", "status": "queued" }
```

**403** `entitlement_required` if checkout not completed.

**Prerequisite:** Assessment must be **classified** before generation succeeds.

---

### `GET /documents/{report_id}`

Poll until ready (usually 2–5 seconds).

```bash
curl -s "http://localhost:8000/api/v1/documents/rep_01KV..."
```

**Expect when `status: "ready"`:**

| Artifact | Format |
|---|---|
| `01_risk_classification_memo.md` | `md` |
| `02_obligation_matrix.csv` | `csv` |
| `03_procurement_summary.pdf` | `pdf` |
| `04_annex_iv_technical_documentation.docx` | `docx` (high-risk evidence packs) |
| `05_human_oversight_plan.docx` | `docx` (high-risk evidence packs) |
| `10_evidence_tracker.xlsx` | `xlsx` (high-risk evidence packs) |
| `evidence_pack.zip` | `zip` |

Each artifact includes a `download` path like `/api/v1/downloads/sig_...`.

**Expect when `status: "failed"`:** `error` message explaining cause (e.g. missing classification).

---

### `GET /downloads/{signed_token}`

```bash
curl -s -OJ "http://localhost:8000/api/v1/downloads/sig_..."
```

**Expect (200):** File download with `Content-Disposition` attachment.  
**404** invalid token.  
**410** expired token (default TTL: 1 hour).

---

### `POST /dodo/webhook`

Dodo-signed only. Configure the production webhook URL as:

```text
https://aia-api-gsj2jve34a-uc.a.run.app/api/v1/dodo/webhook
```

Subscribed event:

```text
payment.succeeded
```

**Expect (200):** `{"received": true}`; creates/updates entitlement on `payment.succeeded`.

---

### `POST /stripe/webhook`

Legacy Stripe-signed endpoint. Test with Stripe CLI only if Stripe is re-enabled:

```bash
stripe listen --forward-to localhost:8000/api/v1/stripe/webhook
```

**Expect (200):** `{"received": true}`; creates/updates entitlement on `checkout.session.completed`.

---

## Error envelope

All errors use:

```json
{
  "error": {
    "code": "not_found",
    "message": "Human readable",
    "details": []
  }
}
```

Common codes: `not_found`, `entitlement_required`, `forbidden`, `validation_error`.
