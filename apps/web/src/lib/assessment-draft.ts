const DRAFT_KEY = "aia_assessment_draft";

export type AssessmentDraft = {
  assessmentId?: string;
  company: string;
  system: string;
  email: string;
  answers?: Record<string, unknown>;
};

export function loadAssessmentDraft(): AssessmentDraft {
  if (typeof window === "undefined") return { company: "", system: "", email: "" };
  try {
    const raw = sessionStorage.getItem(DRAFT_KEY);
    if (!raw) return { company: "", system: "", email: "" };
    return { company: "", system: "", email: "", ...JSON.parse(raw) };
  } catch {
    return { company: "", system: "", email: "" };
  }
}

export function saveAssessmentDraft(draft: AssessmentDraft) {
  if (typeof window === "undefined") return;
  sessionStorage.setItem(DRAFT_KEY, JSON.stringify(draft));
}

export function clearAssessmentDraft() {
  if (typeof window === "undefined") return;
  sessionStorage.removeItem(DRAFT_KEY);
}
