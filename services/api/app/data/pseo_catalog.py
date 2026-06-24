"""50 high-intent pSEO pages catalog — PRD §16.2."""

from __future__ import annotations

import json
from pathlib import Path

PSEO_CATALOG = [
    ("hr-tech", "HR Tech", "resume-screening", "Resume Screening", "high_risk", "Annex III point 4(a)"),
    ("hr-tech", "HR Tech", "candidate-ranking", "Candidate Ranking", "high_risk", "Annex III point 4(a)"),
    ("hr-tech", "HR Tech", "interview-analysis", "AI Interview Analysis", "high_risk", "Annex III point 4(a)"),
    ("hr-tech", "HR Tech", "employee-monitoring", "Employee Performance Monitoring", "high_risk", "Annex III point 4(b)"),
    ("hr-tech", "HR Tech", "workforce-scheduling", "Workforce Scheduling AI", "limited_risk", "Article 50"),
    ("hr-tech", "HR Tech", "job-matching", "Job Matching AI", "high_risk", "Annex III point 4(a)"),
    ("hr-tech", "HR Tech", "salary-benchmarking", "Salary Benchmarking AI", "limited_risk", "Article 50"),
    ("hr-tech", "HR Tech", "attrition-prediction", "Employee Attrition Prediction", "high_risk", "Annex III point 4(b)"),
    ("hr-tech", "HR Tech", "skills-assessment", "Skills Assessment AI", "high_risk", "Annex III point 4(a)"),
    ("hr-tech", "HR Tech", "background-check-ai", "Background Check AI", "high_risk", "Annex III point 4(a)"),
    ("fintech", "Fintech", "credit-scoring", "Credit Scoring", "high_risk", "Annex III point 5(b)"),
    ("fintech", "Fintech", "loan-eligibility", "Loan Eligibility", "high_risk", "Annex III point 5(b)"),
    ("fintech", "Fintech", "fraud-detection", "Fraud Detection AI", "limited_risk", "Article 50"),
    ("fintech", "Fintech", "insurance-pricing", "Insurance Risk Pricing", "high_risk", "Annex III point 5(b)"),
    ("fintech", "Fintech", "kyc-verification", "KYC Verification AI", "high_risk", "Annex III point 5(b)"),
    ("fintech", "Fintech", "aml-monitoring", "AML Transaction Monitoring", "high_risk", "Annex III point 5(b)"),
    ("fintech", "Fintech", "robo-advisor", "Robo-Advisor", "limited_risk", "Article 50"),
    ("fintech", "Fintech", "payment-fraud", "Payment Fraud Scoring", "limited_risk", "Article 50"),
    ("fintech", "Fintech", "underwriting-ai", "Insurance Underwriting AI", "high_risk", "Annex III point 5(b)"),
    ("fintech", "Fintech", "collections-ai", "Debt Collections AI", "high_risk", "Annex III point 5(b)"),
    ("edtech", "Edtech", "exam-proctoring", "Exam Proctoring", "high_risk", "Annex III point 3"),
    ("edtech", "Edtech", "student-admission", "Student Admission AI", "high_risk", "Annex III point 3"),
    ("edtech", "Edtech", "learning-outcome-evaluation", "Learning Outcome Evaluation", "high_risk", "Annex III point 3"),
    ("edtech", "Edtech", "student-risk-classification", "Student Risk Classification", "high_risk", "Annex III point 3"),
    ("edtech", "Edtech", "essay-grading", "Automated Essay Grading", "high_risk", "Annex III point 3"),
    ("edtech", "Edtech", "tutoring-chatbot", "AI Tutoring Chatbot", "limited_risk", "Article 50"),
    ("edtech", "Edtech", "plagiarism-detection", "Plagiarism Detection", "limited_risk", "Article 50"),
    ("edtech", "Edtech", "course-recommendation", "Course Recommendation", "minimal_risk", "General provisions"),
    ("edtech", "Edtech", "attendance-tracking", "Attendance Tracking AI", "limited_risk", "Article 50"),
    ("edtech", "Edtech", "accessibility-ai", "Accessibility AI Tools", "minimal_risk", "General provisions"),
    ("healthtech", "Healthtech", "medical-triage", "Medical Triage AI", "high_risk", "Annex III point 5(a)"),
    ("healthtech", "Healthtech", "diagnostic-support", "Diagnostic Support AI", "high_risk", "Annex III point 5(a)"),
    ("healthtech", "Healthtech", "patient-risk-scoring", "Patient Risk Scoring", "high_risk", "Annex III point 5(a)"),
    ("healthtech", "Healthtech", "radiology-ai", "Radiology AI", "high_risk", "Annex III point 5(a)"),
    ("healthtech", "Healthtech", "mental-health-chatbot", "Mental Health Chatbot", "limited_risk", "Article 50"),
    ("healthtech", "Healthtech", "clinical-documentation", "Clinical Documentation AI", "limited_risk", "Article 50"),
    ("healthtech", "Healthtech", "drug-interaction-checker", "Drug Interaction Checker", "high_risk", "Annex III point 5(a)"),
    ("healthtech", "Healthtech", "hospital-bed-allocation", "Hospital Bed Allocation", "high_risk", "Annex III point 5(a)"),
    ("healthtech", "Healthtech", "wellness-coaching", "Wellness Coaching AI", "minimal_risk", "General provisions"),
    ("healthtech", "Healthtech", "symptom-checker", "Symptom Checker AI", "high_risk", "Annex III point 5(a)"),
    ("general", "General", "customer-support-chatbot", "Customer Support Chatbot", "limited_risk", "Article 50"),
    ("general", "General", "ai-generated-content", "AI-Generated Content Labeling", "limited_risk", "Article 50"),
    ("general", "General", "deepfake-disclosure", "Deepfake Disclosure", "limited_risk", "Article 50"),
    ("general", "General", "emotion-recognition", "Emotion Recognition AI", "limited_risk", "Article 50"),
    ("general", "General", "biometric-categorization", "Biometric Categorization", "limited_risk", "Article 50"),
    ("general", "General", "synthetic-voice", "Synthetic Voice Generation", "limited_risk", "Article 50"),
    ("general", "General", "ai-search-ranking", "AI Search Ranking", "minimal_risk", "General provisions"),
    ("general", "General", "spam-filter", "Email Spam Filter", "minimal_risk", "General provisions"),
    ("general", "General", "content-moderation", "Content Moderation AI", "limited_risk", "Article 50"),
    ("general", "General", "recommendation-engine", "Recommendation Engine", "minimal_risk", "General provisions"),
    ("roles", "Roles", "provider-vs-deployer-hr", "Provider vs Deployer for HR AI", "high_risk", "Article 16 / Article 26"),
    ("roles", "Roles", "provider-vs-deployer-fintech", "Provider vs Deployer for Fintech AI", "high_risk", "Article 16 / Article 26"),
    ("templates", "Templates", "annex-iv-technical-documentation", "Annex IV Technical Documentation Template", "high_risk", "Annex IV"),
    ("templates", "Templates", "fundamental-rights-impact-assessment", "FRIA Template", "high_risk", "Article 27"),
    ("templates", "Templates", "human-oversight-plan", "Human Oversight Plan Template", "high_risk", "Article 14"),
]


def _repo_data_path() -> Path:
    for parent in Path(__file__).resolve().parents:
        candidate = parent / "data" / "seeds" / "rules.json"
        if candidate.exists():
            return candidate
    return Path("data/seeds/rules.json").resolve()


RULES_JSON_PATH = _repo_data_path()

RULE_BACKED_SLUGS_BY_RULE_CODE = {
    "annex_iii_employment_recruitment_selection": {
        "hr-tech/resume-screening",
        "hr-tech/candidate-ranking",
        "hr-tech/interview-analysis",
        "hr-tech/job-matching",
        "hr-tech/skills-assessment",
        "hr-tech/background-check-ai",
    },
    "annex_iii_credit_scoring": {
        "fintech/credit-scoring",
        "fintech/loan-eligibility",
        "fintech/insurance-pricing",
        "fintech/underwriting-ai",
    },
    "limited_risk_chatbot_transparency": {
        "general/customer-support-chatbot",
    },
    "limited_risk_deepfake": {
        "general/ai-generated-content",
        "general/deepfake-disclosure",
        "general/synthetic-voice",
    },
}

ACQUISITION_SLUGS = {
    "roles/provider-vs-deployer-hr",
    "roles/provider-vs-deployer-fintech",
    "templates/annex-iv-technical-documentation",
    "templates/fundamental-rights-impact-assessment",
    "templates/human-oversight-plan",
}

LEGAL_REVIEW_PENDING = "pending_sme"
LEGAL_REVIEW_APPROVED = "approved"


def _active_rule_codes() -> set[str]:
    try:
        payload = json.loads(RULES_JSON_PATH.read_text())
    except FileNotFoundError:
        return set()
    return {
        str(row.get("rule_code"))
        for row in payload.get("rules", [])
        if isinstance(row, dict) and row.get("rule_code")
    }


def coverage_supported_slugs() -> set[str]:
    """Return slugs backed by current rule coverage or acquisition-only pages."""
    all_slugs = {f"{industry}/{use_case}" for industry, _, use_case, *_ in PSEO_CATALOG}
    rule_codes = _active_rule_codes()
    covered: set[str] = set()
    for rule_code in rule_codes:
        covered.update(RULE_BACKED_SLUGS_BY_RULE_CODE.get(rule_code, set()))
    covered.update(ACQUISITION_SLUGS)
    return covered & all_slugs


def legal_review_status_for_slug(slug: str) -> str:
    """Return SME review status for index gating."""
    if slug in coverage_supported_slugs():
        return LEGAL_REVIEW_PENDING
    return LEGAL_REVIEW_PENDING


def reviewed_citation_for_slug(slug: str) -> str:
    """Return catalog citation annotated for SME review until approved."""
    citations = {
        f"{industry}/{use_case}": citation
        for industry, _, use_case, _, _, citation in PSEO_CATALOG
    }
    citation = citations.get(slug, "General provisions")
    if legal_review_status_for_slug(slug) == LEGAL_REVIEW_PENDING:
        return f"{citation} — NEEDS SME REVIEW"
    return citation


def index_supported_slugs() -> set[str]:
    """Return pSEO slugs that are rule-backed and approved for indexing."""
    return {
        slug
        for slug in coverage_supported_slugs()
        if legal_review_status_for_slug(slug) == LEGAL_REVIEW_APPROVED
    }


def is_index_supported(slug: str) -> bool:
    return slug in index_supported_slugs()
