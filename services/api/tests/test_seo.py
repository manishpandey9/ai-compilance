"""SEO page uniqueness and index-support tests — PRD §21.3."""

from app.data.pseo_catalog import (
    PSEO_CATALOG,
    coverage_supported_slugs,
    index_supported_slugs,
    is_index_supported,
    legal_review_status_for_slug,
    reviewed_citation_for_slug,
)


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
    slug = "hr-tech/resume-screening"

    assert legal_review_status_for_slug(slug) == "pending_sme"
    assert "NEEDS SME REVIEW" in reviewed_citation_for_slug(slug)
    assert not is_index_supported(slug)
    assert slug not in index_supported_slugs()


def test_pages_ahead_of_rule_coverage_are_not_index_supported():
    assert not is_index_supported("edtech/exam-proctoring")
    assert not is_index_supported("healthtech/diagnostic-support")
    assert not is_index_supported("fintech/kyc-verification")
