"""SEO page uniqueness tests — PRD §21.3."""

from app.data.pseo_catalog import PSEO_CATALOG


def test_catalog_has_at_least_50_pages():
    assert len(PSEO_CATALOG) >= 50


def test_unique_slugs():
    slugs = [f"{ind}/{uc}" for ind, _, uc, *_ in PSEO_CATALOG]
    assert len(slugs) == len(set(slugs))


def test_unique_titles():
    titles = [name for *_, name, _, _ in PSEO_CATALOG]
    assert len(titles) == len(set(titles))
