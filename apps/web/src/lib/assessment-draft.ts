const DRAFT_KEY = "aia_assessment_draft";

export type AssessmentDraft = {
  assessmentId?: string;
  company: string;
  system: string;
  answers?: Record<string, unknown>;
};

export function loadAssessmentDraft(): AssessmentDraft {
  if (typeof window === "undefined") return { company: "", system: "" };
  try {
    const raw = sessionStorage.getItem(DRAFT_KEY);
    if (!raw) return { company: "", system: "" };
    return { company: "", system: "", ...JSON.parse(raw) };
  } catch {
    return { company: "", system: "" };
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
