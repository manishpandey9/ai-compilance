"""Document renderer tests — PRD §21.2."""

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
    assert len(pdf) > 2000


def test_evidence_zip():
    ctx = _sample_ctx()
    files = {
        "01_risk_classification_memo.md": render_markdown(ctx),
        "02_ai_system_card.md": render_system_card(ctx),
    }
    z = build_zip(files)
    assert len(z) > 200
