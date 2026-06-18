"use client";

import { useRouter } from "next/navigation";
import { FormEvent, useEffect, useState } from "react";

import { SiteFooter } from "@/components/layout/footer";
import { AppShell, BackLink, MarketingHeader, PageContainer } from "@/components/layout/shell";
import { Button } from "@/components/ui/button";
import { Field, FormError, Input } from "@/components/ui/input";
import { api } from "@/lib/api";
import { loadAssessmentDraft, saveAssessmentDraft } from "@/lib/assessment-draft";

export default function ComplianceCheckerPage() {
  const router = useRouter();
  const [company, setCompany] = useState("");
  const [system, setSystem] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [resumeId, setResumeId] = useState<string | null>(null);

  useEffect(() => {
    const draft = loadAssessmentDraft();
    setCompany(draft.company);
    setSystem(draft.system);
    if (!draft.assessmentId) return;

    api
      .getAssessment(draft.assessmentId)
      .then((res) => {
        if (res.status !== "completed" && res.next_questions.length > 0) {
          setResumeId(draft.assessmentId!);
        }
      })
      .catch(() => {
        saveAssessmentDraft({ ...draft, assessmentId: undefined });
      });
  }, []);

  useEffect(() => {
    const draft = loadAssessmentDraft();
    saveAssessmentDraft({
      ...draft,
      company,
      system,
      assessmentId: draft.assessmentId ?? resumeId ?? undefined,
    });
  }, [company, system, resumeId]);

  async function goToAssessment(assessmentId: string, claimToken?: string) {
    if (typeof window !== "undefined" && claimToken) {
      sessionStorage.setItem(`claim_${assessmentId}`, claimToken);
    }
    saveAssessmentDraft({ company, system, assessmentId });
    router.push(`/assessment/${assessmentId}`);
  }

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const draft = loadAssessmentDraft();
      if (draft.assessmentId) {
        try {
          const existing = await api.getAssessment(draft.assessmentId);
          if (existing.status !== "completed" && existing.next_questions.length > 0) {
            await api.patchAssessment(draft.assessmentId, {
              company_name: company || undefined,
              system_name: system || undefined,
            });
            await goToAssessment(draft.assessmentId);
            return;
          }
        } catch {
          /* create a new assessment below */
        }
      }

      const res = await api.createAssessment({
        company_name: company || undefined,
        system_name: system || undefined,
      });
      await goToAssessment(res.assessment_id, res.claim_token);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not start. Is the API running?");
    } finally {
      setLoading(false);
    }
  }

  return (
    <AppShell
      variant="light"
      header={<MarketingHeader variant="light" />}
      footer={<SiteFooter variant="light" />}
    >
      <main id="main-content">
        <PageContainer width="form" className="py-16 sm:py-20">
          <BackLink href="/" variant="light">
            ← Home
          </BackLink>
          <h1 className="text-headline mt-8 text-zinc-900">Before we start</h1>
          <p className="mt-3 text-zinc-600">
            Optional labels for your report. About five minutes of questions after this.
          </p>

          {resumeId && (
            <p className="mt-4 rounded-md border border-zinc-200 bg-zinc-50 px-4 py-3 text-sm text-zinc-600">
              You have an assessment in progress. Continue below to pick up where you left off.
            </p>
          )}

          <form
            onSubmit={onSubmit}
            className="mt-12 space-y-8 border-t border-zinc-200 pt-10"
            aria-label="Start assessment"
          >
            <Field label="Company name" surface="light">
              <Input
                surface="light"
                value={company}
                onChange={(e) => setCompany(e.target.value)}
                placeholder="Acme AI"
                autoComplete="organization"
              />
            </Field>
            <Field label="Product or system name" surface="light">
              <Input
                surface="light"
                value={system}
                onChange={(e) => setSystem(e.target.value)}
                placeholder="HireRank"
              />
            </Field>
            {error && <FormError message={error} />}
            <Button type="submit" surface="light" disabled={loading} className="w-full py-3" aria-busy={loading}>
              {loading ? "Starting…" : resumeId ? "Continue questions" : "Begin questions"}
            </Button>
          </form>
        </PageContainer>
      </main>
    </AppShell>
  );
}
