"""SEO page uniqueness and index-support tests — PRD §21.3."""

from app.data.pseo_catalog import PSEO_CATALOG, index_supported_slugs, is_index_supported


def test_catalog_has_at_least_50_pages():
    assert len(PSEO_CATALOG) >= 50


def test_unique_slugs():
    slugs = [f"{ind}/{uc}" for ind, _, uc, *_ in PSEO_CATALOG]
    assert len(slugs) == len(set(slugs))


def test_unique_titles():
    titles = [name for *_, name, _, _ in PSEO_CATALOG]
    assert len(titles) == len(set(titles))


def test_index_supported_pages_are_a_deliberate_subset():
    supported = index_supported_slugs()
    all_slugs = {f"{industry}/{use_case}" for industry, _, use_case, *_ in PSEO_CATALOG}

    assert supported
    assert supported < all_slugs


def test_current_rule_backed_pages_are_index_supported():
    assert is_index_supported("hr-tech/resume-screening")
    assert is_index_supported("hr-tech/candidate-ranking")
    assert is_index_supported("fintech/credit-scoring")
    assert is_index_supported("general/customer-support-chatbot")
    assert is_index_supported("general/deepfake-disclosure")


def test_pages_ahead_of_rule_coverage_are_not_index_supported():
    assert not is_index_supported("edtech/exam-proctoring")
    assert not is_index_supported("healthtech/diagnostic-support")
    assert not is_index_supported("fintech/kyc-verification")
