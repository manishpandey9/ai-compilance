"use client";

import { useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";

import { SiteFooter } from "@/components/layout/footer";
import { AppShell, BackLink, MarketingHeader, PageContainer } from "@/components/layout/shell";
import { ButtonLink } from "@/components/ui/button";
import { api } from "@/lib/api";
import { trackEvent } from "@/lib/analytics";
import { EVIDENCE_PACK_SKU } from "@/lib/product";

export default function CheckoutSuccessInner() {
  const params = useSearchParams();
  const assessmentId = params.get("assessment_id");
  const sku = EVIDENCE_PACK_SKU;
  const [status, setStatus] = useState("Confirming purchase…");
  const [reportId, setReportId] = useState<string | null>(null);

  useEffect(() => {
    if (!assessmentId) return;
    (async () => {
      try {
        const label = "evidence-prep pack";
        let gen: { report_id: string; status: string } | null = null;
        for (let attempt = 1; attempt <= 8; attempt += 1) {
          try {
            setStatus(
              attempt === 1
                ? `Generating your ${label}…`
                : `Confirming payment, then generating your ${label}…`,
            );
            gen = await api.generateDocuments(assessmentId, sku);
            break;
          } catch (err) {
            const message = err instanceof Error ? err.message : "";
            if (!message.includes("entitlement_required") && !message.includes("Purchase required")) {
              throw err;
            }
            await new Promise((resolve) => setTimeout(resolve, 2500));
          }
        }
        if (!gen) {
          throw new Error("Payment is still being confirmed. Please refresh this page in a moment.");
        }
        setReportId(gen.report_id);
        setStatus("ready");
        trackEvent("document_generation_completed", { sku });
      } catch (err) {
        setStatus(err instanceof Error ? err.message : "Generation failed");
        trackEvent("document_generation_failed", { sku });
      }
    })();
  }, [assessmentId, sku]);

  if (!assessmentId) {
    return (
      <AppShell variant="light" header={<MarketingHeader variant="light" />} footer={<SiteFooter variant="light" />}>
        <PageContainer width="form" className="py-16">
          <BackLink href="/" variant="light">← Home</BackLink>
          <p className="mt-6 text-zinc-600">
            Missing assessment.{" "}
            <ButtonLink href="/" variant="text" surface="light">
              Go home
            </ButtonLink>
          </p>
        </PageContainer>
      </AppShell>
    );
  }

  return (
    <AppShell variant="light" header={<MarketingHeader variant="light" />} footer={<SiteFooter variant="light" />}>
      <PageContainer width="form" className="py-16 sm:py-20">
        <BackLink href={`/assessment/${assessmentId}`} variant="light">← Results</BackLink>
        <h1 className="text-headline mt-6 text-zinc-900">Payment received</h1>
        {status === "ready" && reportId ? (
          <>
            <p className="mt-3 text-zinc-600">Your files are ready.</p>
            <ButtonLink
              href={`/reports/${reportId}?assessment=${assessmentId}`}
              size="lg"
              surface="light"
              className="mt-8"
            >
              Download documents
            </ButtonLink>
          </>
        ) : (
          <p className="text-mono-ui mt-3 text-sm text-zinc-500" aria-live="polite">
            {status}
          </p>
        )}
      </PageContainer>
    </AppShell>
  );
}
