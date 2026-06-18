"""Official template structure tests."""

import io

from app.documents.official_sections import ANNEX_IV_SECTIONS, ANNEX_V_ITEMS, ANNEX_VIII_SECTION_A_FIELDS
from app.documents.pack import build_pack_files
from app.documents.renderers import render_docx_annex_iv, render_docx_declaration
from tests.test_documents import _sample_ctx


def test_annex_iv_has_nine_official_sections():
    assert len(ANNEX_IV_SECTIONS) == 9
    assert ANNEX_IV_SECTIONS[0].number == "1"
    assert "intended purpose" in ANNEX_IV_SECTIONS[0].items[0].lower()


def test_annex_v_has_eight_fields():
    assert len(ANNEX_V_ITEMS) == 8


def test_annex_viii_section_a_has_thirteen_fields():
    assert len(ANNEX_VIII_SECTION_A_FIELDS) == 13


def test_annex_iv_docx_references_official_points():
    docx = render_docx_annex_iv(_sample_ctx())
    assert len(docx) > 5000
    import zipfile

    with zipfile.ZipFile(io.BytesIO(docx)) as zf:
        xml = zf.read("word/document.xml").decode("utf-8")
    assert "Annex IV point" in xml


def test_declaration_docx_generated():
    docx = render_docx_declaration(_sample_ctx())
    assert len(docx) > 3000


def test_high_risk_provider_evidence_pack_manifest():
    ctx = _sample_ctx()
    ctx.pack_sku = "evidence_pack"
    ctx.is_high_risk = True
    ctx.needs_provider_conformity = True
    ctx.needs_fria = False
    files = build_pack_files(ctx, "evidence_pack")
    assert "04_annex_iv_technical_documentation_template.docx" in files
    assert "05_quality_management_system_template.docx" in files
    assert "09_eu_declaration_of_conformity_skeleton.docx" in files
    assert "10_eu_database_registration_data_pack.csv" in files
    assert "08_fria_template.docx" not in files


def test_high_risk_deployer_includes_fria():
    ctx = _sample_ctx()
    ctx.pack_sku = "evidence_pack"
    ctx.is_high_risk = True
    ctx.primary_actor_role = "deployer"
    ctx.needs_fria = True
    ctx.needs_provider_conformity = False
    files = build_pack_files(ctx, "evidence_pack")
    assert "08_fria_template.docx" in files
    assert "09_eu_declaration_of_conformity_skeleton.docx" not in files
