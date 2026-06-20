# Commercial SEO Trust Design

## Purpose

Make the live EU AI Act Navigator more credible before paid acquisition by aligning the product promise, SEO index surface, and pricing/trust copy with the rule coverage that exists today.

## Scope

This pass is a credibility and conversion hardening pass. It does not expand the legal rule engine across every AI Act category. It makes the current product safer to sell while preserving the existing free assessment, report, checkout, document generation, and deployment flow.

## Decisions

### Positioning

The product should say it creates a source-cited classification and evidence-pack prep materials, not a final audit approval. Paid artifacts should be described as review-ready first drafts for customer, counsel, auditor, or internal compliance workflows.

### SEO Exposure

Only pages backed by current deterministic rule coverage should be indexed in the first pass. The indexed pSEO surface should focus on:

- HR-tech: resume screening, candidate ranking, interview analysis, job matching, skills assessment, background-check AI.
- Fintech: credit scoring, loan eligibility, insurance pricing, underwriting AI.
- General transparency: customer-support chatbot, AI-generated content, deepfake disclosure, synthetic voice.
- Templates and roles that do not assert unsupported use-case classification.

Pages outside this set may still exist for later, but they should not be included in sitemap output until their legal rules and citations are backed by fixtures.

### Product Trust

The free and paid surfaces should show:

- What the engine currently covers.
- What remains review territory.
- That classification comes from deterministic rules, not an LLM.
- That generated documents are evidence-preparation drafts, not legal advice.

### Pricing

Keep the existing price points, but change copy to reduce legal overclaim:

- Free risk preview.
- $199 starter classification memo.
- $699 evidence-prep pack.

Pricing should make the value concrete by showing likely use cases: procurement response, internal compliance kickoff, counsel review, and customer/auditor preparation.

## Files

- `services/api/app/data/pseo_catalog.py`: mark which catalog pages are supported for indexing.
- `services/api/app/scripts/generate_pseo.py`: carry supported-indexing metadata into generated pages.
- `services/api/tests/test_seo.py`: test supported pages and sitemap eligibility helpers.
- `apps/web/src/app/sitemap.ts`: include only index-supported pSEO pages when the API exposes support metadata.
- `apps/web/src/app/page.tsx`: tighten homepage promise and add coverage/trust copy.
- `apps/web/src/app/pricing/page.tsx`: reposition paid tiers.
- `apps/web/src/app/eu-ai-act/compliance-checker/page.tsx`: add lightweight coverage notice before assessment.
- `apps/web/src/app/assessment/[id]/page.tsx`: clarify paid-pack claims on the result page.
- `PRODUCT.md` and docs references: update the strongest overclaims.

## Verification

Each implementation step must be verified before moving to the next:

1. API SEO catalog tests pass after adding support metadata.
2. Web sitemap logic passes its unit/type check or the project build catches route errors.
3. Copy changes compile through the web build.
4. Production-relevant flow is not broken locally: pages render, sitemap emits supported URLs, and no TypeScript errors are introduced.

