# Commercial SEO Trust Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Align the live product promise, pSEO indexing, and paid conversion copy with the deterministic rule coverage that exists today.

**Architecture:** Add catalog-level SEO support metadata in the API without a database migration. The API exposes `index_supported` for page listings and individual pages; the web sitemap filters unsupported pSEO URLs, and marketing/product surfaces explain coverage and paid-pack limitations.

**Tech Stack:** Python 3.12, FastAPI, SQLAlchemy, pytest, Next.js 15, React 19, TypeScript.

## Global Constraints

- LLMs never decide legal status; all classification claims must refer to deterministic rules.
- Paid documents are evidence-preparation drafts, not legal advice or final audit approval.
- Do not delete unsupported pSEO pages in this pass; only remove unsupported pages from sitemap exposure.
- Keep existing payment SKUs and prices: `starter_report` at `$199`, `evidence_pack` at `$699`.
- Verify each task before starting the next task.

---

### Task 1: API SEO Support Metadata

**Files:**
- Modify: `services/api/app/data/pseo_catalog.py`
- Modify: `services/api/app/public_api/pages.py`
- Modify: `services/api/app/schemas.py`
- Modify: `services/api/tests/test_seo.py`

**Interfaces:**
- Produces: `index_supported_slugs() -> set[str]`
- Produces: `is_index_supported(slug: str) -> bool`
- Produces API field: `index_supported: bool`

- [ ] **Step 1: Write failing tests**

Add tests that assert supported pages are fewer than all catalog pages, unsupported health/edtech pages remain in the catalog but are not index supported, and supported HR/fintech/transparency pages are index supported.

- [ ] **Step 2: Run tests to verify failure**

Run: `cd services/api && uv run pytest tests/test_seo.py -q`

Expected: fails because `index_supported_slugs` and `is_index_supported` do not exist yet.

- [ ] **Step 3: Implement catalog support metadata**

Add a `SUPPORTED_INDEX_SLUGS` set plus `index_supported_slugs()` and `is_index_supported(slug: str)` helpers in `pseo_catalog.py`.

- [ ] **Step 4: Expose support metadata through API responses**

Add `index_supported: bool` to `SEOPageResponse`, `list_pages`, and `get_page` in `pages.py`.

- [ ] **Step 5: Run tests to verify pass**

Run: `cd services/api && uv run pytest tests/test_seo.py -q`

Expected: all SEO tests pass.

### Task 2: Web Sitemap and Page Robots Metadata

**Files:**
- Modify: `apps/web/src/app/sitemap.ts`
- Modify: `apps/web/src/lib/api.ts`
- Modify: `apps/web/src/app/eu-ai-act/[...slug]/page.tsx`

**Interfaces:**
- Consumes API field: `index_supported: boolean`
- Produces sitemap behavior: unsupported pSEO pages omitted.
- Produces page metadata behavior: unsupported pSEO pages return `robots: { index: false, follow: true }`.

- [ ] **Step 1: Update TypeScript API types**

Add `index_supported?: boolean` to `SEOPageResponse` and to the `listPages` response type.

- [ ] **Step 2: Filter sitemap URLs**

Change `sitemap.ts` to include a pSEO page only when `index_supported !== false`, so old API responses remain compatible but new API responses filter unsupported pages.

- [ ] **Step 3: Add noindex metadata for unsupported pages**

Change `generateMetadata` in `apps/web/src/app/eu-ai-act/[...slug]/page.tsx` to set `robots: { index: false, follow: true }` when `page.index_supported === false`.

- [ ] **Step 4: Run web build verification**

Run: `pnpm --filter web build`

Expected: build exits 0.

### Task 3: Product Positioning and Trust Copy

**Files:**
- Modify: `PRODUCT.md`
- Modify: `docs/technical-design.md`
- Modify: `apps/web/src/app/page.tsx`
- Modify: `apps/web/src/app/pricing/page.tsx`
- Modify: `apps/web/src/app/eu-ai-act/compliance-checker/page.tsx`
- Modify: `apps/web/src/app/assessment/[id]/page.tsx`

**Interfaces:**
- Produces homepage copy that says "evidence-pack prep" rather than final audit readiness.
- Produces pricing copy that explains free, starter memo, and evidence-prep pack.
- Produces checker/result copy showing current coverage and review territory.

- [ ] **Step 1: Update source-of-truth docs**

Replace “audit-ready evidence pack” claims with “review-ready evidence-preparation pack” language in `PRODUCT.md` and the strongest matching claims in `docs/technical-design.md`.

- [ ] **Step 2: Update homepage trust copy**

Add a concise coverage section: current supported areas, review territory, deterministic rule engine.

- [ ] **Step 3: Update pricing copy**

Rename the `$699` plan label to “Evidence-prep pack” and clarify that outputs are editable first drafts for procurement, counsel, auditor, or internal review.

- [ ] **Step 4: Update checker and result page copy**

Add pre-assessment coverage notice and clarify downloadable documents are drafts for review.

- [ ] **Step 5: Run web build verification**

Run: `pnpm --filter web build`

Expected: build exits 0.

### Task 4: Full Verification

**Files:**
- No new files.

**Interfaces:**
- Consumes all prior task outputs.

- [ ] **Step 1: Run API SEO tests**

Run: `cd services/api && uv run pytest tests/test_seo.py -q`

Expected: all SEO tests pass.

- [ ] **Step 2: Run web build**

Run: `pnpm --filter web build`

Expected: build exits 0.

- [ ] **Step 3: Inspect git diff**

Run: `git diff --stat`

Expected: only planned files plus pre-existing deployment changes are present.

