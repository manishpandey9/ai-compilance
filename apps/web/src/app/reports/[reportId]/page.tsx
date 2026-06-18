"use client";

import { useParams, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";

import { SiteFooter } from "@/components/layout/footer";
import { AppShell, BackLink, MarketingHeader, PageContainer } from "@/components/layout/shell";
import { FormError } from "@/components/ui/input";
import { api, ReportStatusResponse } from "@/lib/api";
import { cn } from "@/lib/cn";
import { focusRingLight } from "@/lib/focus";

const ARTIFACT_LABELS: Record<string, string> = {
  "01_risk_classification_memo.md": "Risk classification memo",
  "02_ai_system_card.md": "AI system card",
  "03_obligation_matrix.csv": "Obligation matrix",
  "04_annex_iv_technical_documentation_template.docx": "Annex IV technical documentation",
  "04_customer_procurement_summary.pdf": "Procurement summary (PDF)",
  "05_quality_management_system_template.docx": "Quality management system (Art. 17)",
  "05_evidence_tracker.xlsx": "Evidence tracker",
  "06_human_oversight_plan_template.docx": "Human oversight plan (Art. 14)",
  "07_instructions_for_use_template.docx": "Instructions for use (Art. 13)",
  "08_fria_template.docx": "FRIA template (Art. 27)",
  "09_eu_declaration_of_conformity_skeleton.docx": "EU declaration of conformity (Annex V)",
  "10_eu_database_registration_data_pack.csv": "EU database registration (Annex VIII)",
  "11_evidence_tracker.xlsx": "Evidence tracker",
  "12_customer_procurement_summary.pdf": "Procurement summary (PDF)",
  "starter_report.zip": "Full starter pack (ZIP)",
  "evidence_pack.zip": "Full evidence pack (ZIP)",
};

function artifactLabel(filename: string): string {
  return ARTIFACT_LABELS[filename] ?? filename;
}

export default function ReportPage() {
  const params = useParams();
  const search = useSearchParams();
  const reportId = params.reportId as string;
  const assessmentId = search.get("assessment");
  const [report, setReport] = useState<ReportStatusResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    const poll = async () => {
      try {
        const data = await api.getReport(reportId);
        if (!active) return;
        setReport(data);
        if (data.status === "queued" || data.status === "generating") {
          setTimeout(poll, 2000);
        }
      } catch (err) {
        if (active) setError(err instanceof Error ? err.message : "Failed to load report");
      }
    };
    poll();
    return () => {
      active = false;
    };
  }, [reportId]);

  return (
    <AppShell variant="light" header={<MarketingHeader variant="light" />} footer={<SiteFooter variant="light" />}>
      <PageContainer width="content" className="py-16">
        <main id="main-content">
          {assessmentId && (
            <BackLink href={`/assessment/${assessmentId}`} variant="light">
              ← Results
            </BackLink>
          )}
          <h1 className="text-headline mt-6 text-zinc-900">Documents</h1>
          {error && <FormError message={error} className="mt-4" />}
          {report && (
            <>
              <p className="text-mono-ui mt-3 text-sm text-zinc-500" aria-live="polite">
                Status: {report.status}
              </p>
              {report.status === "ready" && (
                <ul className="mt-10 divide-y divide-zinc-200 border-y border-zinc-200">
                  {report.artifacts.map((a) => (
                    <li key={a.download} className="flex items-center justify-between gap-4 py-4 text-sm">
                      <div>
                        <span className="font-medium text-zinc-900">{artifactLabel(a.document_type)}</span>
                        <span className="mt-0.5 block text-xs text-zinc-500">{a.format.toUpperCase()}</span>
                      </div>
                      <a
                        href={api.downloadUrl(a.download)}
                        className={cn("text-zinc-600 hover:text-zinc-900 hover:underline", focusRingLight)}
                      >
                        Download
                      </a>
                    </li>
                  ))}
                </ul>
              )}
              {report.error && <FormError message={report.error} className="mt-4" />}
            </>
          )}
        </main>
      </PageContainer>
    </AppShell>
  );
}
