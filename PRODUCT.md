# Product

## Register

product

## Users

- **AI vendor founders and product managers** selling AI systems into EU customers (HR-tech, fintech, edtech, healthtech). They need a credible risk tier and document checklist before a customer, auditor, or regulator asks.
- **Compliance and legal leads** who want a source-mapped first draft so expert review is fast and cheap — not a blank template.
- **Consultants, DPOs, and law firms** automating intake and producing first-draft evidence packs for clients.
- **Internal admins** (us) who publish rules and legal sources without breaking reproducibility of past reports.

Context: users are under deadline pressure (EU AI Act enforcement timeline), skeptical of AI-generated legal advice, and evaluating whether this tool is serious enough to trust with procurement or audit conversations.

## Product Purpose

EU AI Act Compliance Navigator turns a structured description of an AI system into a **source-cited compliance path**: risk classification → role classification → obligation matrix → document checklist → evidence pack.

Free risk check is acquisition; the paid output is an **audit-ready evidence pack** ($199–$699), not a generic PDF. Success means a user leaves knowing their tier, obligations, and next documents — and can defend the result to a customer or auditor because every conclusion traces to a versioned rule and legal source.

## Brand Personality

**Sharp. Technical. Confident.**

Voice is expert and direct — like Linear or Stripe for compliance, not a chatbot or legal blog. We show the rule engine and citations; we do not hype "AI-powered" magic. Calm under pressure: regulatory complexity made navigable, not scary or salesy.

Emotional goal after the free check: **confidence** — "I know my tier and can defend this."

## Anti-references

- Generic AI legal templates and ChatGPT-style compliance PDFs with no source trace
- Marketing that implies an LLM decides legal status (we use a deterministic rule engine only)
- AI hype aesthetics: neon accents, purple gradients, glassmorphism, robot illustrations, "Powered by AI" badges
- Over-decorated product UI: mismatched form controls, display fonts on labels, gratuitous motion
- Fear-mongering countdown banners without substance
- Side-stripe card accents, gradient text, and other template SaaS tropes

## Design Principles

1. **Practice what you preach** — the product demonstrates rigorous, source-cited compliance thinking in its own UX and copy.
2. **Show, don't tell** — surface legal references, rule versions, and confidence signals instead of vague claims.
3. **Expert confidence** — typography and layout feel like a serious tool, not a landing-page generator.
4. **Determinism is visible** — ambiguity (`needs_expert_review`, conflicting rules) is first-class, never hidden behind a single "AI says" answer.
5. **Earned familiarity** — product UI uses consistent, standard affordances so users in flow trust every control.

## Accessibility & Inclusion

- Target **WCAG 2.1 AA** for all user-facing surfaces (marketing, wizard, reports).
- Respect `prefers-reduced-motion` — no essential information gated on animation.
- Body and UI text must meet contrast requirements on both dark canvas and light pSEO prose surfaces.
- Form errors, loading, and empty states must be perceivable without color alone.
