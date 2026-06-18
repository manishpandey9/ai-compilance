"use client";

import { useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";

import { SiteFooter } from "@/components/layout/footer";
import { AppShell, BackLink, MarketingHeader, PageContainer } from "@/components/layout/shell";
import { ButtonLink } from "@/components/ui/button";
import { api } from "@/lib/api";

export default function CheckoutSuccessInner() {
  const params = useSearchParams();
  const assessmentId = params.get("assessment_id");
  const sku = (params.get("sku") as "starter_report" | "evidence_pack") || "evidence_pack";
  const [status, setStatus] = useState("Confirming purchase…");
  const [reportId, setReportId] = useState<string | null>(null);

  useEffect(() => {
    if (!assessmentId) return;
    (async () => {
      try {
        const label = sku === "starter_report" ? "starter report" : "evidence pack";
        setStatus(`Generating your ${label}…`);
        const gen = await api.generateDocuments(assessmentId, sku);
        setReportId(gen.report_id);
        setStatus("ready");
      } catch (err) {
        setStatus(err instanceof Error ? err.message : "Generation failed");
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
