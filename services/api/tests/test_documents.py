"""Document renderer tests — PRD §21.2."""

from dataclasses import replace
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

from app.documents.labels import format_answer_value
from app.documents.renderers import (
    build_zip,
    render_markdown,
    render_obligation_csv,
    render_procurement_pdf,
    render_system_card,
)
from app.documents.spec import ObligationRow, RenderContext, TriggeredRuleRow


def _sample_ctx() -> RenderContext:
    return RenderContext(
        assessment_id="aia_TEST123",
        generated_at="2026-06-16 12:00 UTC",
        company_name="Acme AI",
        system_name="HireRank",
        risk_tier="high_risk",
        risk_tier_label="High-risk",
        primary_actor_role="provider",
        actor_role_label="Provider",
        classification_status="classified",
        confidence="high",
        rule_version=1,
        source_version="2024/1689-consolidated-2026-01",
        legal_source_title="Regulation (EU) 2024/1689",
        legal_source_url="https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689",
        triggered_rules=[
            TriggeredRuleRow(
                rule_code="annex_iii_employment_recruitment_selection",
                name="Annex III employment recruitment",
                legal_citation="Regulation (EU) 2024/1689 Annex III point 4(a)",
                legal_summary="AI for recruitment or selection of natural persons",
                rationale="System filters applications and ranks candidates.",
                source_url="https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689",
            )
        ],
        obligations=[
            ObligationRow(
                obligation_id="OBL-001",
                title="Prepare technical documentation (Annex IV)",
                description=None,
                legal_citation="Regulation (EU) 2024/1689 Article 11",
                legal_summary="Technical documentation",
                source_url="https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689",
                mandatory=True,
                evidence_required="Annex IV package",
                document_type="annex-iv-technical-documentation",
                suggested_owner="Engineering / product",
                enforcement_note="2 August 2026",
            )
        ],
        answers={
            "eu_market_exposure": "yes",
            "actor_role": "provider",
            "use_case_category": "employment_recruitment",
            "system_function": ["filter_applications", "rank_candidates"],
            "affects_natural_persons": True,
        },
        answer_rows=[
            ("EU market exposure", format_answer_value("eu_market_exposure", "yes")),
            ("Primary use case", format_answer_value("use_case_category", "employment_recruitment")),
        ],
        required_documents=["annex-iv-technical-documentation"],
    )


def test_risk_memo_contains_assessment_and_citations():
    md = render_markdown(_sample_ctx()).decode()
    assert "aia_TEST123" in md
    assert "HireRank" in md
    assert "Annex III point 4(a)" in md
    assert "Article 11" in md
    assert "Assessment inputs" in md
    assert "Executive summary" in md
    assert "high-risk" in md.lower() or "High-risk" in md


def test_system_card_included():
    card = render_system_card(_sample_ctx()).decode()
    assert "AI System Card" in card
    assert "HireRank" in card
    assert "Classification" in card


def test_obligation_csv_has_legal_columns():
    csv_text = render_obligation_csv(_sample_ctx()).decode()
    assert "legal_citation" in csv_text
    assert "Regulation (EU) 2024/1689 Article 11" in csv_text
    assert "evidence_required" in csv_text


def test_procurement_pdf_generation():
    pdf = render_procurement_pdf(_sample_ctx())
    assert pdf[:4] == b"%PDF"
    assert len(pdf) > 1800


def test_procurement_pdf_text_is_not_clipped_after_wrapped_lines():
    if not shutil.which("pdftotext"):
        pytest.skip("pdftotext is required for PDF text extraction")

    pdf = render_procurement_pdf(_sample_ctx())
    with tempfile.TemporaryDirectory() as tmpdir:
        pdf_path = Path(tmpdir) / "procurement.pdf"
        text_path = Path(tmpdir) / "procurement.txt"
        pdf_path.write_bytes(pdf)
        subprocess.run(["pdftotext", str(pdf_path), str(text_path)], check=True)
        text = text_path.read_text()
        normalized = " ".join(text.split())

    assert "Actor role: Provider" in text
    assert "System filters applications and ranks candidates." in text
    assert "Prepare technical documentation" in text
    assert "Legal source: Regulation (EU) 2024/1689." in normalized


def test_procurement_pdf_does_not_create_orphan_legal_source_page():
    if not shutil.which("pdfinfo"):
        pytest.skip("pdfinfo is required for PDF page-count verification")

    titles = [
        "Establish and maintain risk management system",
        "Implement data and data governance practices",
        "Draw up technical documentation per Annex IV",
        "Maintain automatic logging and record-keeping",
        "Supply instructions for use to deployers",
        "Design for effective human oversight",
        "Ensure accuracy, robustness and cybersecurity",
        "Comply with provider obligations under Article 16",
        "Maintain quality management system",
        "Retain documentation for 10 years",
        "Establish post-market monitoring system",
        "Report serious incidents",
    ]
    base_obligation = _sample_ctx().obligations[0]
    ctx = replace(
        _sample_ctx(),
        company_name="Fresh Render QA Ltd",
        system_name="HireRank Fresh PDF QA",
        answer_rows=[
            (
                "EU market exposure",
                "Operates in the EU today (customers, users, or data subjects in the EU)",
            ),
            ("Actor role", "Provider (develops and places the AI on the market)"),
            ("Primary use case", "Hiring and HR (screening, ranking, interviews, performance)"),
            ("Affects identifiable people", "Yes"),
            (
                "System functions",
                "Filter or shortlist job applications / CVs; Rank or score candidates",
            ),
        ],
        legal_source_title="Regulation (EU) 2024/1689 (Artificial Intelligence Act)",
        obligations=[
            replace(
                base_obligation,
                obligation_id=f"OBL-{idx:03}",
                title=title,
                legal_citation=f"Regulation (EU) 2024/1689 Article {idx + 8}",
            )
            for idx, title in enumerate(titles, start=1)
        ],
        pack_sku="evidence_pack",
        is_high_risk=True,
        needs_provider_conformity=True,
    )

    pdf = render_procurement_pdf(ctx)
    with tempfile.TemporaryDirectory() as tmpdir:
        pdf_path = Path(tmpdir) / "procurement.pdf"
        pdf_path.write_bytes(pdf)
        result = subprocess.run(["pdfinfo", str(pdf_path)], check=True, capture_output=True, text=True)

    assert "Pages:           1" in result.stdout


def test_evidence_zip():
    ctx = _sample_ctx()
    files = {
        "01_risk_classification_memo.md": render_markdown(ctx),
        "02_ai_system_card.md": render_system_card(ctx),
    }
    z = build_zip(files)
    assert len(z) > 200
