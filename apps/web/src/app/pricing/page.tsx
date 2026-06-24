import type { Metadata } from "next";

import { SiteFooter } from "@/components/layout/footer";
import { AppShell, BackLink, MarketingHeader, PageContainer } from "@/components/layout/shell";
import { ButtonLink } from "@/components/ui/button";
import { cn } from "@/lib/cn";
import { EVIDENCE_PACK_PRICE_LABEL } from "@/lib/product";

export const metadata: Metadata = {
  title: "Pricing",
  description: "Free risk preview and a $20 EU AI Act evidence-prep pack.",
};

const PLANS = [
  {
    name: "Risk preview",
    price: "Free",
    summary:
      "Rule-based risk tier, provider/deployer role, obligation preview, and document gaps.",
    highlight: false,
    cta: { label: "Start questionnaire", href: "/eu-ai-act/compliance-checker" },
  },
  {
    name: "Evidence-prep pack",
    price: EVIDENCE_PACK_PRICE_LABEL,
    summary:
      "Editable first drafts for customer, auditor, or internal review: full memo, Annex IV outline, human oversight plan, FRIA template when required, and evidence tracker.",
    highlight: true,
    cta: { label: "Start questionnaire", href: "/eu-ai-act/compliance-checker" },
  },
];

export default function PricingPage() {
  return (
    <AppShell
      variant="light"
      header={<MarketingHeader variant="light" />}
      footer={<SiteFooter variant="light" />}
    >
      <main id="main-content" className="py-16 sm:py-20">
        <PageContainer width="content">
          <BackLink href="/" variant="light">
            ← Home
          </BackLink>
          <h1 className="text-headline mt-6 text-zinc-900">Pricing</h1>
          <p className="mt-3 max-w-lg text-zinc-600">
            Try the preview first. Pay when you need source-cited drafts to send into procurement,
            counsel, auditor, or internal compliance review.
          </p>

          <p className="mt-5 max-w-xl text-sm leading-relaxed text-zinc-500">
            These packs prepare evidence and review materials from a deterministic rule engine. They
            are not legal advice, a notified-body submission, or a final audit approval.
          </p>

          <div className="mt-14 border-y border-zinc-200">
            {PLANS.map((plan) => (
              <div
                key={plan.name}
                className={cn(
                  "grid gap-6 border-t border-zinc-200 py-10 first:border-t-0 sm:grid-cols-[1fr_auto] sm:items-center",
                  plan.highlight && "font-medium",
                )}
              >
                <div>
                  <h2 className="text-lg font-semibold tracking-tight text-zinc-900">{plan.name}</h2>
                  <p className="mt-1 text-2xl font-semibold tracking-tight text-zinc-900">
                    {plan.price}
                  </p>
                  <p className="mt-3 max-w-lg text-sm leading-relaxed text-zinc-600">
                    {plan.summary}
                  </p>
                </div>
                {plan.cta && (
                  <ButtonLink
                    href={plan.cta.href}
                    variant={plan.highlight ? "primary" : "secondary"}
                    surface="light"
                    className="sm:justify-self-end"
                  >
                    {plan.cta.label}
                  </ButtonLink>
                )}
              </div>
            ))}
          </div>
        </PageContainer>
      </main>
    </AppShell>
  );
}
