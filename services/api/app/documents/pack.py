"""Evidence pack file manifest per Regulation (EU) 2024/1689 templates."""

from __future__ import annotations

from collections.abc import Callable

from app.documents.renderers import (
    render_annex_viii_csv,
    render_docx_annex_iv,
    render_docx_declaration,
    render_docx_fria,
    render_docx_instructions,
    render_docx_oversight,
    render_docx_qms,
    render_evidence_xlsx,
    render_markdown,
    render_obligation_csv,
    render_procurement_pdf,
    render_system_card,
)
from app.documents.spec import RenderContext


def build_pack_files(ctx: RenderContext, sku: str) -> dict[str, bytes]:
    """Return ordered artifact bytes for the evidence_pack SKU."""
    if sku != "evidence_pack":
        raise ValueError(f"Unsupported document SKU: {sku}")

    builders: dict[str, Callable[[], bytes]] = {
        "01_risk_classification_memo.md": lambda: render_markdown(ctx),
        "02_ai_system_card.md": lambda: render_system_card(ctx),
        "03_obligation_matrix.csv": lambda: render_obligation_csv(ctx),
    }

    if ctx.is_high_risk:
        builders["04_annex_iv_technical_documentation_template.docx"] = (
            lambda: render_docx_annex_iv(ctx)
        )
        builders["05_quality_management_system_template.docx"] = lambda: render_docx_qms(ctx)
        builders["06_human_oversight_plan_template.docx"] = lambda: render_docx_oversight(ctx)
        builders["07_instructions_for_use_template.docx"] = lambda: render_docx_instructions(ctx)
        if ctx.needs_fria:
            builders["08_fria_template.docx"] = lambda: render_docx_fria(ctx)
        if ctx.needs_provider_conformity:
            builders["09_eu_declaration_of_conformity_skeleton.docx"] = (
                lambda: render_docx_declaration(ctx)
            )
            builders["10_eu_database_registration_data_pack.csv"] = lambda: render_annex_viii_csv(
                ctx
            )
        builders["11_evidence_tracker.xlsx"] = lambda: render_evidence_xlsx(ctx)
        builders["12_customer_procurement_summary.pdf"] = lambda: render_procurement_pdf(ctx)
    else:
        builders["04_customer_procurement_summary.pdf"] = lambda: render_procurement_pdf(ctx)
        builders["05_evidence_tracker.xlsx"] = lambda: render_evidence_xlsx(ctx)

    return {name: fn() for name, fn in builders.items()}
