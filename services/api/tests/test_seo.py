"""SEO page uniqueness and index-support tests — PRD §21.3."""

from app.data.pseo_catalog import (
    PSEO_CATALOG,
    coverage_supported_slugs,
    index_supported_slugs,
    is_index_supported,
    legal_review_status_for_slug,
    reviewed_citation_for_slug,
)
from app.scripts.generate_pseo import citation_reference_candidates
from app.services.seo_service import build_structured_data


def test_catalog_has_at_least_50_pages():
    assert len(PSEO_CATALOG) >= 50


def test_unique_slugs():
    slugs = [f"{ind}/{uc}" for ind, _, uc, *_ in PSEO_CATALOG]
    assert len(slugs) == len(set(slugs))


def test_unique_titles():
    titles = [name for *_, name, _, _ in PSEO_CATALOG]
    assert len(titles) == len(set(titles))


def test_coverage_supported_pages_are_a_deliberate_subset():
    supported = coverage_supported_slugs()
    all_slugs = {f"{industry}/{use_case}" for industry, _, use_case, *_ in PSEO_CATALOG}

    assert supported
    assert supported < all_slugs


def test_current_rule_backed_pages_have_rule_coverage():
    supported = coverage_supported_slugs()

    assert "hr-tech/resume-screening" in supported
    assert "hr-tech/candidate-ranking" in supported
    assert "fintech/credit-scoring" in supported
    assert "general/customer-support-chatbot" in supported
    assert "general/deepfake-disclosure" in supported


def test_pending_sme_pages_are_not_index_supported():
    slug = "hr-tech/interview-analysis"

    assert legal_review_status_for_slug(slug) == "pending_sme"
    assert "NEEDS SME REVIEW" in reviewed_citation_for_slug(slug)
    assert not is_index_supported(slug)
    assert slug not in index_supported_slugs()


def test_approved_high_intent_pages_are_index_supported():
    approved_slugs = {
        "hr-tech/resume-screening",
        "hr-tech/candidate-ranking",
        "fintech/credit-scoring",
        "fintech/insurance-pricing",
        "general/customer-support-chatbot",
        "general/deepfake-disclosure",
        "templates/annex-iv-technical-documentation",
        "templates/fundamental-rights-impact-assessment",
        "templates/human-oversight-plan",
        "roles/provider-vs-deployer-hr",
    }

    assert approved_slugs <= index_supported_slugs()
    for slug in approved_slugs:
        assert is_index_supported(slug)
        assert legal_review_status_for_slug(slug) == "approved"
        assert "NEEDS SME REVIEW" not in reviewed_citation_for_slug(slug)


def test_pages_ahead_of_rule_coverage_are_not_index_supported():
    assert not is_index_supported("edtech/exam-proctoring")
    assert not is_index_supported("healthtech/diagnostic-support")
    assert not is_index_supported("fintech/kyc-verification")


def test_indexed_pages_have_product_structured_data():
    schema_types = {
        item["@type"]
        for item in build_structured_data(
            "EU AI Act Compliance for Resume Screening",
            "hr-tech/resume-screening",
            "Resume Screening",
            "high_risk",
        )
    }

    assert {"FAQPage", "BreadcrumbList", "SoftwareApplication"} <= schema_types


def test_pseo_citations_map_to_specific_legal_references():
    assert citation_reference_candidates("Annex III point 4(a)") == [
        "Regulation (EU) 2024/1689 Annex III point 4(a)"
    ]
    assert citation_reference_candidates("Annex IV") == [
        "Regulation (EU) 2024/1689 Annex IV",
        "Regulation (EU) 2024/1689 Article 11",
    ]
    assert citation_reference_candidates("Article 16 / Article 26") == [
        "Regulation (EU) 2024/1689 Article 16",
        "Regulation (EU) 2024/1689 Article 26",
    ]
