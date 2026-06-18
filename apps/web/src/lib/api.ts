const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

export type ApiError = {
  error: { code: string; message: string; details: unknown[] };
};

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
  });
  if (!res.ok) {
    const body = (await res.json().catch(() => null)) as ApiError | null;
    throw new Error(body?.error?.message ?? `API error ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export type CreateAssessmentResponse = {
  assessment_id: string;
  status: string;
  question_set_version: number;
  claim_token: string;
};

export type QuestionOption = { value: string; label: string };

export type NextQuestion = {
  question_key: string;
  type: "single" | "multi" | "boolean" | "text";
  label: string;
  options?: QuestionOption[];
  help?: string;
  allow_unknown?: boolean;
};

export type AssessmentResponse = {
  assessment_id: string;
  status: string;
  company_name?: string;
  system_name?: string;
  answers: Record<string, unknown>;
  next_questions: NextQuestion[];
  progress: { answered: number; remaining_estimate: number };
  question_order: string[];
};

export type ClassifyResponse = {
  assessment_id: string;
  classification_status: string;
  risk_tier?: string;
  confidence?: string;
  primary_actor_role?: string;
  secondary_actor_roles: string[];
  triggered_rules: { rule_code: string; source: string; rationale: string }[];
  missing_fields: string[];
  free_preview?: { top_obligations: string[]; document_gap_preview: string[] };
  rule_version: number;
  source_version: string;
};

export type SEOPageResponse = {
  slug: string;
  page_type: string;
  title: string;
  meta_description: string;
  content_md: string;
  structured_data?: Record<string, unknown>[] | null;
  canonical_url: string;
  last_reviewed_at?: string;
  rule_version?: number;
  references?: { citation_label: string; source_id: string }[];
};

const API_BASE_SERVER = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

/** Server-side page fetch for generateMetadata / RSC */
export async function fetchPage(slug: string): Promise<SEOPageResponse | null> {
  const res = await fetch(`${API_BASE_SERVER}/pages/${slug}`, {
    next: { revalidate: 3600 },
  });
  if (res.status === 404) return null;
  if (!res.ok) throw new Error(`Failed to fetch page: ${res.status}`);
  return res.json() as Promise<SEOPageResponse>;
}

export type ReportStatusResponse = {
  report_id: string;
  status: string;
  rule_version?: number;
  source_version?: string;
  artifacts: { document_type: string; format: string; download: string }[];
  error?: string;
};

const WEB_BASE = process.env.NEXT_PUBLIC_WEB_URL ?? "http://localhost:3000";

export const api = {
  createAssessment: (body: { company_name?: string; system_name?: string }) =>
    apiFetch<CreateAssessmentResponse>("/assessments", {
      method: "POST",
      body: JSON.stringify(body),
    }),

  getAssessment: (id: string) => apiFetch<AssessmentResponse>(`/assessments/${id}`),

  patchAssessment: (
    id: string,
    body: { company_name?: string; system_name?: string },
  ) =>
    apiFetch<AssessmentResponse>(`/assessments/${id}`, {
      method: "PATCH",
      body: JSON.stringify(body),
    }),

  submitAnswers: (id: string, answers: { question_key: string; value: unknown }[]) =>
    apiFetch<AssessmentResponse>(`/assessments/${id}/answers`, {
      method: "POST",
      body: JSON.stringify({ answers }),
    }),

  rewindAssessment: (id: string, questionKey: string) =>
    apiFetch<AssessmentResponse>(`/assessments/${id}/rewind`, {
      method: "POST",
      body: JSON.stringify({ question_key: questionKey }),
    }),

  classify: (id: string) =>
    apiFetch<ClassifyResponse>(`/assessments/${id}/classify`, { method: "POST" }),

  getPage: (slug: string) => apiFetch<SEOPageResponse>(`/pages/${slug}`),

  listPages: () => apiFetch<{ data: { slug: string; title: string }[] }>("/pages?limit=100"),

  createCheckout: (assessmentId: string, sku: "starter_report" | "evidence_pack") =>
    apiFetch<{ checkout_url: string; session_id: string }>("/checkout/session", {
      method: "POST",
      body: JSON.stringify({
        assessment_id: assessmentId,
        sku,
        success_url: `${WEB_BASE}/checkout/success`,
        cancel_url: `${WEB_BASE}/pricing`,
      }),
    }),

  generateDocuments: (assessmentId: string, sku: "starter_report" | "evidence_pack") =>
    apiFetch<{ report_id: string; status: string }>("/documents/generate", {
      method: "POST",
      body: JSON.stringify({ assessment_id: assessmentId, sku }),
    }),

  getReport: (reportId: string) => apiFetch<ReportStatusResponse>(`/documents/${reportId}`),

  downloadUrl: (path: string) => `${API_BASE.replace("/api/v1", "")}${path}`,

  adminPreviewRules: (adminKey: string) =>
    apiFetch<{ all_pass: boolean; results: unknown[] }>("/admin/rules/preview", {
      method: "POST",
      headers: { "X-Admin-Key": adminKey, "Content-Type": "application/json" },
      body: JSON.stringify({}),
    }),

  adminRegenerateSeo: (adminKey: string) =>
    apiFetch<{ queued_pages: number }>("/admin/seo-pages/regenerate", {
      method: "POST",
      headers: { "X-Admin-Key": adminKey, "Content-Type": "application/json" },
      body: JSON.stringify({ scope: "all" }),
    }),
};
