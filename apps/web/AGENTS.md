# Web app — AI Act Navigator

Next.js 15 App Router frontend for pSEO, assessment wizard, and dashboard.

## Routes

| Route | Purpose |
|---|---|
| `/` | Marketing homepage |
| `/eu-ai-act/compliance-checker` | Start free assessment |
| `/assessment/[id]` | Wizard + free result |
| `/eu-ai-act/[...slug]` | pSEO pages (ISR via API fetch) |
| `/pricing` | Pricing tiers |

## API client

- `src/lib/api.ts` — hand-written for MVP; will be replaced by OpenAPI-generated client.
- Base URL: `NEXT_PUBLIC_API_URL` (default `http://localhost:8000/api/v1`).

## Conventions

- Server Components for pSEO pages; Client Components for wizard interactivity.
- Do not hand-roll types that duplicate Pydantic schemas long-term — generate from OpenAPI.
- pSEO pages must fetch from API, never hard-code legal conclusions in components.
