import { AppShell, MarketingHeader, PageContainer } from "@/components/layout/shell";
import { SiteFooter } from "@/components/layout/footer";
import { JsonLd } from "@/components/seo/json-ld";
import { ButtonLink } from "@/components/ui/button";
import { EVIDENCE_PACK_PRICE_USD } from "@/lib/product";
import { SITE } from "@/lib/site";

const HOME_JSON_LD = [
  {
    "@context": "https://schema.org",
    "@type": "Organization",
    name: SITE.name,
    url: SITE.url,
    email: SITE.contactEmail,
  },
  {
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    name: SITE.name,
    applicationCategory: "BusinessApplication",
    operatingSystem: "Web",
    url: SITE.url,
    description: SITE.description,
    offers: {
      "@type": "Offer",
      price: String(EVIDENCE_PACK_PRICE_USD),
      priceCurrency: "USD",
    },
  },
];

export default function HomePage() {
  return (
    <AppShell
      variant="light"
      header={<MarketingHeader variant="light" />}
      footer={<SiteFooter variant="light" />}
    >
      <JsonLd data={HOME_JSON_LD} />
      <main id="main-content" className="py-20 sm:py-28">
        <PageContainer>
          <div className="max-w-xl">
            <h1 className="text-display text-zinc-900">
              Classify your AI system under the EU AI Act
            </h1>
            <p className="text-body-lg mt-5 text-zinc-600">
              For vendors selling into Europe. Answer questions about your product and market,
              get a risk tier with article references, then prepare the first-draft evidence your
              customer, counsel, or auditor will ask to review.
            </p>
            <div className="mt-9 flex flex-wrap items-center gap-x-6 gap-y-3">
              <ButtonLink href="/eu-ai-act/compliance-checker" size="lg" surface="light">
                Start questionnaire
              </ButtonLink>
              <ButtonLink
                href="/eu-ai-act/hr-tech/resume-screening"
                variant="text"
                surface="light"
              >
                Example: resume screening
              </ButtonLink>
            </div>
          </div>

          <div className="mt-20 max-w-xl space-y-4 border-t border-zinc-200 pt-10 text-[0.9375rem] leading-relaxed text-zinc-600">
            <p>
              The questionnaire takes about five minutes. Classification runs on a published rule
              set. Each conclusion links to the article or annex that triggered it.
            </p>
            <p>
              Current rule-backed coverage focuses on HR recruitment, creditworthiness and insurance
              pricing, chatbot transparency, and synthetic-media disclosure. Other use cases are
              routed to review territory instead of pretending certainty.
            </p>
            <p>
              Paid tiers add editable first drafts: classification memo, obligation checklist, Annex
              IV outline, human oversight plan, FRIA template where it applies, and evidence tracker.
            </p>
            <p className="text-zinc-500">
              Not legal advice. When inputs are incomplete, unsupported, or conflicting, we flag the
              gap instead of guessing.
            </p>
          </div>
        </PageContainer>
      </main>
    </AppShell>
  );
}
