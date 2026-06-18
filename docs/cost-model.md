# Cost & Revenue Model — EU AI Act Compliance Navigator

| | |
|---|---|
| **Companion to** | [`technical-design.md`](./technical-design.md) §5.5 |
| **Source PRD** | §5 (business model), §5.2 (revenue scenarios), §23 (pricing) |
| **Status** | Draft for review — planning figures, not guarantees |

> **Disclaimer.** All vendor prices are approximate planning figures as of mid-2026 and must be re-checked against live pricing pages before commitment. Treat ranges as order-of-magnitude. The point of this doc is to show the architecture is **cost-effective at zero traffic and high-margin at revenue**, and to map infra cost to the PRD's revenue scenarios.

---

## 1. Design goal: near-zero fixed cost, >99% digital gross margin

The architecture (TDD §5) deliberately favors **scale-to-zero / pay-per-use** vendors so that:

1. **Pre-revenue fixed cost ≈ $0–$40/mo** — you can run the full stack on free/cheap tiers while validating demand (PRD §5.2 conservative wedge).
2. **Marginal cost of one paid pack ≈ cents** — compute to run a deterministic classification (milliseconds, in-memory) + render ~11 documents (seconds of CPU) + store/serve a few MB ZIP (R2, zero egress). Against a **$199–$699** price, gross margin on the digital product is **>99%**.
3. **Break-even ≈ one paid report per month** covers the entire small fixed cost.

---

## 2. Stack cost table (planning estimates)

| Component | Vendor | Free / entry tier | Paid tier when scaling | Cost driver |
|---|---|---|---|---|
| Web hosting | Vercel | Hobby free (non-commercial) → Pro ~$20/mo | Pro/Team | bandwidth, build minutes; ISR keeps compute low |
| API + worker | Render / Fly.io | Free/$0 (sleepy) → ~$7–$25/mo small instance | per-instance | always-on instance(s); scale workers with volume |
| Postgres | Neon | Free (scale-to-zero) → ~$19/mo+ | compute-hours + storage | idle ≈ $0; branches for CI |
| Redis (queue) | Upstash | Free (10k cmd/day) → pay-per-request | per-command | job throughput |
| Object storage | Cloudflare R2 | 10GB free, **$0 egress** | ~$0.015/GB-mo storage | pack storage; downloads free |
| Auth | Clerk | ~10k MAU free → usage pricing | MAU | active users |
| Payments | Stripe | no fixed fee | ~2.9% + $0.30/txn | per transaction (revenue-linked) |
| Email | Resend | ~3k/mo free → ~$20/mo | per email | transactional volume |
| Analytics | PostHog | ~1M events/mo free | usage | event volume |
| Errors | Sentry | dev free tier | usage | error volume |
| LLM (prose only) | provider-agnostic | optional; can ship MVP without | per-token | only on content/regeneration, cacheable |
| Search | Postgres FTS (included) → Meilisearch later | $0 initially | small instance later | corpus size |

**Indicative fixed cost by stage:**

| Stage | Monthly fixed infra |
|---|---|
| Pre-launch / validation | **~$0–$40** (mostly free tiers + maybe one small API instance) |
| Early traction (PRD conservative) | **~$50–$150** |
| Base scenario | **~$200–$500** |
| Aggressive scenario | **~$800–$2,000** (more workers, paid analytics, search, possibly read replica) |

---

## 3. Per-unit marginal cost

| Action | Resources | Est. marginal cost |
|---|---|---|
| pSEO page view | ISR static HTML + CDN | ~$0 (fractions of a cent) |
| Free assessment + classify | in-memory deterministic eval, a few DB rows | < $0.001 |
| Paid pack generation | worker CPU seconds (render 11 docs) + ~2–10MB R2 storage | a few cents |
| Pack download | R2 egress = $0 | $0 |
| Stripe fee on a $699 pack | 2.9% + $0.30 | ~$20.60 |
| Stripe fee on a $199 report | 2.9% + $0.30 | ~$6.07 |
| Optional LLM prose draft per page | tokens (cached, infrequent) | cents, and optional |

**The dominant variable cost is Stripe's percentage** — i.e. cost scales with revenue, which is the healthy shape. Compute/storage are rounding errors against price.

---

## 4. Contribution margin per SKU (PRD §23)

| SKU | Price | Stripe fee | Direct digital cost | Contribution (digital) | Notes |
|---|---|---|---|---|---|
| Starter Report | $199 | ~$6.07 | ~$0.05 | **~$193** (~97%) | pure software |
| Evidence Pack | $699 | ~$20.60 | ~$0.10 | **~$678** (~97%) | pure software |
| Readiness Sprint | $5,000+ | ~$145+ | labor-bound | high $ but **labor-limited** | services = time, not infra |
| Team Workspace | $499/mo | ~$14.77/mo | small infra share | **~$480/mo** recurring | best LTV |

Services (sprint) trade margin for cash velocity and learning; the digital SKUs are the high-margin engine; the subscription is the long-term value (PRD §27).

---

## 5. Revenue scenarios mapped to PRD §5.2 (with infra cost overlay)

> Revenue figures are taken directly from the PRD's planning scenarios; the added column is the *infra cost* implied by this architecture, showing infra stays a tiny fraction of revenue.

| Scenario | PRD monthly revenue | Implied infra fixed cost | Infra as % of revenue |
|---|---|---|---|
| Conservative (service wedge) | $6,000–$10,000 | ~$50–$150 | ~1–2% |
| Base (content + founder sales) | $15,000–$45,000 | ~$200–$500 | ~1–2% |
| Aggressive (SEO + partnerships) | $75,000–$200,000+ | ~$800–$2,000 | ~1% |

Even in the aggressive case, **infrastructure is ~1% of revenue**; Stripe fees (~3%) and human services labor are the real costs. This confirms the "cost-effective + revenue-generating" requirement: the architecture does not become a cost burden as revenue grows.

---

## 6. Break-even analysis

- **Fixed cost to cover at validation stage:** ~$40/mo.
- **Contribution per Starter Report:** ~$193.
- **Break-even:** < **1 paid report per month**.
- **Contribution per Evidence Pack:** ~$678 → a single pack covers months of fixed cost.

This is why the PRD's "free tool → paid pack → sprint → subscription" path (PRD §5.2, §27) is financially safe to pursue: the downside is bounded by trivial fixed cost, the upside is high-margin digital + high-ticket services.

---

## 7. Cost-control levers (build-time decisions)

1. **Ship MVP without the LLM prose layer** if budget/risk dictates — classification and documents are fully deterministic and need no LLM (TDD §21 open question 2). Add prose later, cached.
2. **ISR over SSR** for pSEO so page views cost ~nothing and survive traffic spikes / AI-overview referrals.
3. **Typst over headless Chrome** for PDFs → far lower worker memory/CPU per pack (TDD §5.4).
4. **Scale-to-zero DB (Neon)** and **pay-per-request Redis (Upstash)** so idle periods cost nothing.
5. **R2 zero-egress** so popular sample packs / downloads don't incur bandwidth bills.
6. **Defer Meilisearch/read-replicas** until metrics justify (TDD §13 scaling path).
7. **Ports/adapters for auth + LLM** so you can migrate off premium vendors (Clerk, premium models) when usage-based pricing would exceed a cheaper self-hosted/custom option (TDD §7.6).

---

## 8. Sensitivity & watch-items

| Variable | If it grows | Mitigation |
|---|---|---|
| Auth MAU (Clerk) | crosses free tier | move to custom JWT / Supabase Auth (port already abstracted) |
| LLM tokens | content regeneration spikes | cache prose; regenerate only on record change; cheaper model |
| Worker hours | many concurrent packs | horizontal workers (stateless), batch off-peak |
| Email volume | large list | Resend paid tier (~$20) |
| Search load | large corpus | introduce Meilisearch/Typesense |
| Stripe fees | high volume | negotiate rate; unavoidable but revenue-linked |

---

## 9. Recommendation

Run the **entire MVP on free/entry tiers** during validation (PRD Phase 0–4, §20). Promote individual components to paid tiers only when their specific metric (MAU, events, worker hours, search load) crosses a threshold. Because every component is independently priced and abstracted behind a port where vendor risk exists, **cost grows in small, controllable steps that always trail revenue**.

---

*Companion: [`technical-design.md`](./technical-design.md) · [`adr/0001-stack-and-topology.md`](./adr/0001-stack-and-topology.md).*
