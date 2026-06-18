"""
Official EU AI Act section outlines from Regulation (EU) 2024/1689.

Source: EUR-Lex CELEX:32024R1689 (consolidated). Section text is paraphrased for
template prompts; canonical citations are stored on each section.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class OfficialSection:
    number: str
    title: str
    legal_citation: str
    items: list[str] = field(default_factory=list)
    children: list[OfficialSection] = field(default_factory=list)


REGULATION_CITATION = "Regulation (EU) 2024/1689"

ANNEX_IV_SECTIONS: list[OfficialSection] = [
    OfficialSection(
        "1",
        "General description of the AI system",
        f"{REGULATION_CITATION} Annex IV point 1",
        items=[
            "(a) Intended purpose, provider name, and system version (relation to previous versions)",
            "(b) Interaction with hardware, software, or other AI systems outside this system",
            "(c) Relevant software/firmware versions and version-update requirements",
            "(d) Forms placed on market or put into service (packages, downloads, APIs, embedded)",
            "(e) Hardware on which the system is intended to run",
            "(f) If a product component: external features, marking, internal layout (photos/illustrations)",
            "(g) Basic description of the deployer user interface",
            "(h) Instructions for use for the deployer and deployer UI description, where applicable",
        ],
    ),
    OfficialSection(
        "2",
        "Development process and system elements",
        f"{REGULATION_CITATION} Annex IV point 2",
        items=[
            "(a) Development methods and steps, including pre-trained or third-party tools and integration",
            "(b) Design specifications: logic, algorithms, key choices, classification choices, optimisation targets, expected output/quality, trade-offs for Chapter III Section 2 compliance",
            "(c) System architecture, component integration, computational resources for develop/train/test/validate",
            "(d) Data requirements: datasheets, training methodology, datasets (provenance, scope, characteristics, labelling, cleaning)",
            "(e) Assessment of human oversight measures (Art. 14) and deployer output-interpretation measures (Art. 13(3)(d))",
            "(f) Pre-determined changes and technical solutions for continuous compliance",
            "(g) Validation and testing procedures, data, metrics (accuracy, robustness, discriminatory impacts), signed test logs/reports",
            "(h) Cybersecurity measures",
        ],
    ),
    OfficialSection(
        "3",
        "Monitoring, functioning and control",
        f"{REGULATION_CITATION} Annex IV point 3",
        items=[
            "Capabilities and limitations, accuracy for intended persons/groups and overall expected accuracy",
            "Foreseeable unintended outcomes and risks to health, safety, fundamental rights, discrimination",
            "Human oversight measures (Art. 14) and technical measures for deployer output interpretation",
            "Specifications on input data, as appropriate",
        ],
    ),
    OfficialSection(
        "4",
        "Appropriateness of performance metrics",
        f"{REGULATION_CITATION} Annex IV point 4",
        items=["Justify why chosen metrics are appropriate for this specific AI system"],
    ),
    OfficialSection(
        "5",
        "Risk management system",
        f"{REGULATION_CITATION} Annex IV point 5 (cross-ref Art. 9)",
        items=["Detailed description of the risk management system per Article 9"],
    ),
    OfficialSection(
        "6",
        "Lifecycle changes",
        f"{REGULATION_CITATION} Annex IV point 6",
        items=["Description of relevant changes made by the provider through the system lifecycle"],
    ),
    OfficialSection(
        "7",
        "Standards and technical specifications",
        f"{REGULATION_CITATION} Annex IV point 7",
        items=[
            "Harmonised standards applied (OJEU references), or",
            "If none: solutions adopted to meet Chapter III Section 2 requirements and other standards/specs applied",
        ],
    ),
    OfficialSection(
        "8",
        "EU declaration of conformity",
        f"{REGULATION_CITATION} Annex IV point 8 (cross-ref Art. 47, Annex V)",
        items=["Copy of the EU declaration of conformity (see separate Annex V template in this pack)"],
    ),
    OfficialSection(
        "9",
        "Post-market monitoring",
        f"{REGULATION_CITATION} Annex IV point 9 (cross-ref Art. 72)",
        items=[
            "System to evaluate AI performance in the post-market phase",
            "Post-market monitoring plan per Article 72(3) (Commission template expected by 2 Feb 2026)",
        ],
    ),
]

ANNEX_V_ITEMS: list[tuple[str, str]] = [
    ("1", "AI system name, type, and unambiguous reference for identification and traceability"),
    ("2", "Name and address of the provider or authorised representative"),
    ("3", "Statement that the declaration is issued under the sole responsibility of the provider"),
    (
        "4",
        "Statement that the AI system conforms to this Regulation and, where applicable, other relevant Union law requiring this declaration",
    ),
    (
        "5",
        "Where personal data is processed: statement of compliance with Regulations (EU) 2016/679 and (EU) 2018/1725 and Directive (EU) 2016/680",
    ),
    ("6", "References to harmonised standards or common specifications declared"),
    (
        "7",
        "Where applicable: notified body name/ID, conformity assessment procedure, certificate identification",
    ),
    ("8", "Place and date of issue, signatory name and function, signature"),
]

ANNEX_VIII_SECTION_A_FIELDS: list[tuple[str, str]] = [
    ("1", "Name, address and contact details of the provider"),
    ("2", "If submitted by another person on behalf of the provider: their name, address and contact details"),
    ("3", "Authorised representative name, address and contact details, where applicable"),
    ("4", "AI system trade name and unambiguous reference for identification and traceability"),
    ("5", "Description of intended purpose, components and functions"),
    ("6", "Concise description of information used (data, inputs) and operating logic"),
    ("7", "Status of the AI system (on market/in service; withdrawn; recalled)"),
    ("8", "Type, number and expiry date of notified-body certificate and body identification, where applicable"),
    ("9", "Scanned copy of certificate, where applicable"),
    ("10", "Member States where the system is placed on the market, put into service or made available"),
    ("11", "Copy of the EU declaration of conformity (Art. 47)"),
    ("12", "Electronic instructions for use (not required for certain Annex III law-enforcement/migration areas)"),
    ("13", "URL for additional information (optional)"),
]

ARTICLE_13_INSTRUCTIONS: list[str] = [
    "Identity and contact details of the provider and authorised representative (Art. 13(3)(a))",
    "Characteristics, capabilities and limitations, including (Art. 13(3)(b)):",
    "  (i) Intended purpose",
    "  (ii) Accuracy metrics, robustness and cybersecurity tested (Art. 15) and known circumstances affecting them",
    "  (iii) Foreseeable misuse circumstances leading to Art. 9(2) risks",
    "  (iv) Technical capabilities to explain output, where applicable",
    "  (v) Performance regarding specific persons/groups, when appropriate",
    "  (vi) Input data / training-validation-testing specifications, when appropriate",
    "  (vii) Information to interpret output appropriately",
    "Pre-determined changes at initial conformity assessment (Art. 13(3)(c))",
    "Human oversight measures including deployer interpretation measures (Art. 13(3)(d), Art. 14)",
    "Computational/hardware resources, lifetime, maintenance and care including update frequency (Art. 13(3)(e))",
    "Mechanisms for deployers to collect, store and interpret logs per Article 12 (Art. 13(3)(f))",
]

ARTICLE_14_OVERSIGHT: list[str] = [
    "Design measures enabling effective oversight during use (Art. 14(1))",
    "How oversight prevents/minimises health, safety, and fundamental-rights risks (Art. 14(2))",
    "Provider-built measures vs deployer-implemented measures (Art. 14(3))",
    "Enable understanding of capacities/limitations and monitoring for anomalies (Art. 14(4)(a))",
    "Address automation bias for decision-support systems (Art. 14(4)(b))",
    "Ability to decide not to use or override the system (Art. 14(4)(c))",
    "Ability to interrupt/stop the system (Art. 14(4)(d))",
]

ARTICLE_17_QMS: list[str] = [
    "(a) Strategy for regulatory compliance and modification management",
    "(b) Design, design control and design verification techniques",
    "(c) Development, quality control and quality assurance techniques",
    "(d) Examination, test and validation procedures and frequency",
    "(e) Technical specifications and standards; means to comply where harmonised standards not fully applied",
    "(f) Data management procedures across the data lifecycle",
    "(g) Risk management system (Art. 9)",
    "(h) Post-market monitoring system (Art. 72)",
    "(i) Serious incident reporting procedures (Art. 73)",
    "(j) Communication with authorities, notified bodies, operators, customers",
    "(k) Record-keeping systems and procedures",
    "(l) Resource management including security-of-supply",
    "(m) Accountability framework for management and staff",
]

ARTICLE_27_FRIA: list[str] = [
    "(a) Deployer processes in which the system will be used, in line with intended purpose",
    "(b) Period and frequency of use",
    "(c) Categories of natural persons and groups likely affected in context",
    "(d) Specific harm risks for those groups, using provider information under Art. 13",
    "(e) Implementation of human oversight per instructions for use",
    "(f) Measures if risks materialise, including governance and complaint mechanisms",
    "Note: Required for deployers that are public bodies, private entities providing public services, or deployers of certain Annex III systems (Art. 27(1)). Notify market surveillance authority of results (Art. 27(3)).",
]

ARTICLE_72_POST_MARKET: list[str] = [
    "Proportionate post-market monitoring system documentation (Art. 72(1))",
    "Active collection and analysis of deployer/other data on performance and continuous compliance (Art. 72(2))",
    "Post-market monitoring plan (Art. 72(3)) — align with Commission implementing act template when published (expected 2 Feb 2026)",
    "Integration with existing sectoral post-market systems where equivalent (Art. 72(4))",
]
