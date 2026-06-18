# Web app — testing guide

App: `apps/web` (Next.js 15)  
Local URL: http://localhost:3000

Requires API running at `http://localhost:8000` (`pnpm api:dev`).

---

## Pages to verify

| URL | What to check |
|---|---|
| `/` | Hero, CTAs to checker and sample pSEO page |
| `/eu-ai-act/compliance-checker` | Form creates assessment → redirects to wizard |
| `/assessment/{id}` | Branching questions, progress bar, result preview |
| `/eu-ai-act/hr-tech/resume-screening` | pSEO content from API, CTA to checker |
| `/pricing` | Three tier cards |
| `/checkout/success?assessment_id=...&sku=evidence_pack&dev=1` | Triggers doc generation after dev checkout |
| `/reports/{reportId}?assessment={id}` | Polls until `ready`, download links work |
| `/admin` | Rules preview + SEO regenerate (needs admin key) |
| `/sitemap.xml` | Lists static + pSEO URLs |
| `/robots.txt` | Points to sitemap |

---

## Manual flow: free assessment

1. Open http://localhost:3000/eu-ai-act/compliance-checker
2. Enter company + system name → **Start assessment**
3. Answer questions in order:
   - EU exposure → **Yes**
   - Role → **Provider**
   - Use case → **Employment / recruitment**
   - Affects natural persons → **Yes**
   - System function → **Filter** + **Rank candidates** → Continue
4. **Expect on result page:**
   - Risk tier: **high risk** (green badge)
   - At least one triggered rule with legal citation
   - Likely obligations list (if seeded)
   - Buy buttons for starter report and evidence pack

---

## Manual flow: dev purchase + download

1. Complete assessment flow above
2. Click **Buy evidence pack — $699**
3. **Expect:** Redirect to `/checkout/success` (dev mode, no Stripe)
4. Page shows "Generating…" then **View downloads**
5. On `/reports/{reportId}`:
   - Status moves to **ready** within ~5 seconds
   - List of files including `evidence_pack.zip`
6. Click **Download** on ZIP
7. **Expect:** Browser downloads a valid ZIP containing `.md`, `.pdf`, `.docx`, `.csv`, `.xlsx`

---

## Manual flow: pSEO

1. Open http://localhost:3000/eu-ai-act/fintech/credit-scoring
2. **Expect:**
   - Title mentions Credit Scoring
   - Markdown sections (Quick answer, Documents, FAQ)
   - Last reviewed date
   - "Check your system" CTA

If **404**: run `pnpm api:pseo` and ensure page `status` is `active` in DB.

---

## Manual flow: admin UI

1. Open http://localhost:3000/admin
2. Enter admin key: `dev-admin-key`
3. Click **Preview rules**
4. **Expect:** `"all_pass": true` in JSON output
5. Click **Regenerate SEO pages**
6. **Expect:** Message showing `55` pages queued

---

## Environment variables

| Variable | Purpose |
|---|---|
| `NEXT_PUBLIC_API_URL` | API base (default `http://localhost:8000/api/v1`) |
| `NEXT_PUBLIC_WEB_URL` | Used in checkout success/cancel URLs |

---

## Build verification

```bash
cd apps/web && pnpm build
```

**Expect:** No TypeScript or ESLint errors; routes listed including `/sitemap.xml`.

---

## Known UI limitations

- No Clerk login / user dashboard
- No saved assessment resume via email (claim token stored in sessionStorage only)
- Checkout success page does not handle real Stripe redirect params yet (only dev mode)

When adding new routes, document them in this file with expected behavior.
