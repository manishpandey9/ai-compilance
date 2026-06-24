"""Assessment wizard question definitions and branching."""

from __future__ import annotations

from typing import Any

from app.schemas import NextQuestion, QuestionOption

QUESTION_SET_VERSION = 1

BASE_QUESTIONS: list[dict[str, Any]] = [
    {
        "question_key": "eu_market_exposure",
        "type": "single",
        "label": "Will your AI system be used in the EU, or for people in the EU?",
        "help": (
            "The AI Act applies when your AI is on the EU market or affects people located in the EU.\n\n"
            "Example: You sell hiring software to companies in Germany. Choose Yes.\n\n"
            "Example: Internal analytics for a US-only team with no EU users or data. Choose No."
        ),
        "options": [
            {
                "value": "yes",
                "label": "Yes, we operate in the EU today (customers, users, or data subjects)",
            },
            {
                "value": "planned",
                "label": "Not yet, but EU sales or users are planned within 12 months",
            },
            {
                "value": "no",
                "label": "No EU market, users, or personal data from the EU",
            },
        ],
    },
    {
        "question_key": "actor_role",
        "type": "single",
        "label": "Which role best describes your company for this AI system?",
        "help": (
            "Article 3 assigns obligations by role. Pick what fits this product.\n\n"
            "Provider\n"
            "You develop the AI and place it on the market.\n"
            "Example: You sell HireRank as recruiting SaaS to HR teams.\n\n"
            "Deployer\n"
            "You use another company's AI inside your own organisation.\n"
            "Example: Your HR team uses a third-party API to draft job descriptions. You do not resell the AI.\n\n"
            "Distributor\n"
            "You make someone else's AI available in the EU without changing it.\n"
            "Example: You resell a US vendor's HR product to EU customers unchanged.\n\n"
            "Importer\n"
            "You bring a non-EU provider's AI onto the EU market under your name.\n"
            "Example: You import and brand a US screening tool for sale in France."
        ),
        "options": [
            {
                "value": "provider",
                "label": "We build and sell or license this AI to other companies",
            },
            {
                "value": "deployer",
                "label": "We use a third-party AI system in our own operations",
            },
            {
                "value": "distributor",
                "label": "We supply someone else's AI in the EU without changing it",
            },
            {
                "value": "importer",
                "label": "We import a non-EU provider's AI onto the EU market",
            },
        ],
    },
    {
        "question_key": "use_case_category",
        "type": "single",
        "label": "What is the main thing your AI system does?",
        "help": (
            "Choose the primary purpose. High-risk Annex III categories include employment "
            "(point 4), education (point 3), and credit or insurance (point 5).\n\n"
            "Chatbots and synthetic media often fall under Article 50 transparency rules when "
            "they do not make high-stakes decisions about people."
        ),
        "options": [
            {
                "value": "employment_recruitment",
                "label": "Hiring and HR (screening résumés, ranking candidates, interviews, performance)",
            },
            {
                "value": "credit_financial",
                "label": "Credit and finance (scoring, lending, insurance pricing, KYC/AML)",
            },
            {
                "value": "education",
                "label": "Education (admissions, exams, grading, learner assessment)",
            },
            {
                "value": "healthcare",
                "label": "Healthcare (triage, diagnosis support, treatment or patient-risk decisions)",
            },
            {
                "value": "customer_support",
                "label": "Customer chatbot (answers users without high-stakes decisions about them)",
            },
            {
                "value": "content_generation",
                "label": "Synthetic media (AI-generated images, audio, video, or deepfakes for users)",
            },
            {
                "value": "other",
                "label": "Something else (internal analytics, search, recommendations, and similar)",
            },
        ],
    },
    {
        "question_key": "affects_natural_persons",
        "type": "boolean",
        "label": "Does the system make or influence decisions about identifiable people?",
        "help": (
            "Answer Yes if the output can affect a real person's opportunities or treatment.\n\n"
            "Example: Ranking named job applicants. Choose Yes.\n\n"
            "Example: Aggregating anonymous sales totals with no individual impact. Choose No."
        ),
    },
]

ARTICLE_6_3_QUESTIONS: list[dict[str, Any]] = [
    {
        "question_key": "article_6_3_narrow_procedural_task",
        "type": "boolean",
        "label": "Is the system only performing a narrow procedural task?",
        "help": (
            "NEEDS SME REVIEW: Article 6(3) may exclude some Annex III systems when they do not "
            "pose a significant risk of harm and only perform a narrow procedural task."
        ),
    },
    {
        "question_key": "article_6_3_improves_prior_human_work",
        "type": "boolean",
        "label": "Does it only improve the result of a previously completed human activity?",
        "help": (
            "NEEDS SME REVIEW: This records whether the system merely improves a prior human "
            "result rather than replacing or materially determining the decision."
        ),
    },
    {
        "question_key": "article_6_3_detects_deviation_without_replacing_review",
        "type": "boolean",
        "label": "Does it detect decision patterns or deviations without replacing human review?",
        "help": (
            "NEEDS SME REVIEW: Article 6(3) includes a narrow limb for detecting decision-making "
            "patterns or deviations while preserving meaningful human assessment."
        ),
    },
    {
        "question_key": "article_6_3_preparatory_task",
        "type": "boolean",
        "label": "Is it only a preparatory task for an assessment that a human completes?",
        "help": (
            "NEEDS SME REVIEW: Preparatory tasks may qualify for Article 6(3) treatment only in "
            "limited circumstances. This answer requires legal review."
        ),
    },
    {
        "question_key": "article_6_3_profiling",
        "type": "boolean",
        "label": "Does the system perform profiling of natural persons?",
        "help": (
            "NEEDS SME REVIEW: Profiling overrides the Article 6(3) exception path in this rule "
            "engine and keeps the Annex III high-risk classification route active."
        ),
    },
]

BRANCH_QUESTIONS: dict[str, list[dict[str, Any]]] = {
    "employment_recruitment": [
        {
            "question_key": "system_function",
            "type": "multi",
            "label": "Which of these does your system do? (select all that apply)",
            "help": (
                "Annex III point 4 covers hiring and workforce decisions. Select every function your "
                "product performs.\n\n"
                "Example: An ATS that scores CVs and shortlists candidates. Select filter applications "
                "and rank candidates."
            ),
            "options": [
                {"value": "filter_applications", "label": "Filter or shortlist job applications / CVs"},
                {"value": "rank_candidates", "label": "Rank or score candidates against each other"},
                {"value": "evaluate_candidates", "label": "Evaluate interviews, tests, or assessments"},
                {"value": "monitor_employees", "label": "Monitor or score current employees' performance"},
            ],
            "allow_unknown": True,
        },
        *ARTICLE_6_3_QUESTIONS,
    ],
    "credit_financial": [
        {
            "question_key": "system_function",
            "type": "multi",
            "label": "Which of these does your system do? (select all that apply)",
            "help": (
                "Annex III point 5(b) covers creditworthiness and insurance risk. Credit scoring and "
                "loan decisions are typically high-risk. Pure fraud detection without a credit decision "
                "may fall outside Annex III. Document your reasoning either way."
            ),
            "options": [
                {"value": "credit_scoring", "label": "Credit scoring or creditworthiness assessment"},
                {"value": "loan_eligibility", "label": "Approve or deny loans, or set loan terms"},
                {"value": "fraud_detection_only", "label": "Fraud detection only (no credit or pricing decision)"},
                {"value": "insurance_pricing", "label": "Insurance premium or underwriting risk pricing"},
            ],
        },
        *ARTICLE_6_3_QUESTIONS,
    ],
    "customer_support": [
        {
            "question_key": "interacts_with_users",
            "type": "boolean",
            "label": "Do end users chat with or hear this AI directly?",
            "help": (
                "Article 50(1) requires telling people they interact with AI.\n\n"
                "Example: A website chat widget that answers product questions. Choose Yes.\n\n"
                "Example: AI only used behind the scenes to draft replies a human sends. Choose No."
            ),
        },
        {
            "question_key": "users_informed_ai",
            "type": "boolean",
            "label": "Do you already disclose to users that they are interacting with AI?",
            "help": (
                "Example: “You are chatting with an AI assistant” shown before the first message.\n\n"
                "If users are not clearly informed, choose No. Transparency obligations likely apply."
            ),
        },
    ],
    "content_generation": [
        {
            "question_key": "generates_synthetic_media",
            "type": "boolean",
            "label": "Does the system create synthetic audio, image, or video shown to the public?",
            "help": (
                "Article 50(2) to (4) require labeling of AI-generated or manipulated content.\n\n"
                "Example: A marketing tool that produces deepfake video ads. Choose Yes.\n\n"
                "Example: Internal text drafts never published as synthetic media. Choose No."
            ),
        },
    ],
}


def _to_question(raw: dict[str, Any]) -> NextQuestion:
    options = None
    if "options" in raw:
        options = [QuestionOption(**o) for o in raw["options"]]
    return NextQuestion(
        question_key=raw["question_key"],
        type=raw["type"],
        label=raw["label"],
        options=options,
        help=raw.get("help"),
        allow_unknown=raw.get("allow_unknown", False),
        required=raw.get("required", True),
    )


def get_applicable_questions(answers: dict[str, Any]) -> list[NextQuestion]:
    """Return the next unanswered question only (branching wizard)."""
    ordered: list[dict[str, Any]] = list(BASE_QUESTIONS)
    category = answers.get("use_case_category")
    if isinstance(category, str) and category in BRANCH_QUESTIONS:
        ordered.extend(BRANCH_QUESTIONS[category])

    for raw in ordered:
        key = raw["question_key"]
        if key not in answers:
            return [_to_question(raw)]
    return []


def count_progress(answers: dict[str, Any]) -> tuple[int, int]:
    """Estimate answered count and remaining questions for this branch."""
    ordered_keys = [q["question_key"] for q in BASE_QUESTIONS]
    category = answers.get("use_case_category")
    if isinstance(category, str) and category in BRANCH_QUESTIONS:
        ordered_keys.extend(q["question_key"] for q in BRANCH_QUESTIONS[category])
    elif not category:
        # Before category is chosen, estimate longest branch for remaining hint
        max_branch = max((len(v) for v in BRANCH_QUESTIONS.values()), default=0)
        total = len(BASE_QUESTIONS) + max_branch
    else:
        total = len(ordered_keys)

    if category:
        total = len(ordered_keys)

    answered = sum(1 for key in ordered_keys if key in answers)
    return answered, max(0, total - answered)


def get_ordered_question_defs(answers: dict[str, Any]) -> list[dict[str, Any]]:
    """Full question sequence for the current answer branch."""
    ordered: list[dict[str, Any]] = list(BASE_QUESTIONS)
    category = answers.get("use_case_category")
    if isinstance(category, str) and category in BRANCH_QUESTIONS:
        ordered.extend(BRANCH_QUESTIONS[category])
    return ordered


def get_ordered_question_keys(answers: dict[str, Any]) -> list[str]:
    return [q["question_key"] for q in get_ordered_question_defs(answers)]


def find_question_def(question_key: str, answers: dict[str, Any]) -> dict[str, Any] | None:
    for raw in get_ordered_question_defs(answers):
        if raw["question_key"] == question_key:
            return raw
    return None


def keys_to_clear_after(answers: dict[str, Any], question_key: str) -> list[str]:
    """Answer keys at or after question_key in the current branch order."""
    ordered = get_ordered_question_keys(answers)
    if question_key not in ordered:
        return []
    idx = ordered.index(question_key)
    return ordered[idx:]
