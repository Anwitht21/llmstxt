import pytest
from formatter import is_secondary_section, format_llms_txt, SECONDARY_PATH_PATTERNS
from crawler import PageInfo


class TestSecondaryClassification:

    def test_legal_sections_are_secondary(self):
        assert is_secondary_section("privacy")
        assert is_secondary_section("Privacy")
        assert is_secondary_section("terms")
        assert is_secondary_section("legal")
        assert is_secondary_section("cookie")

    def test_about_sections_are_secondary(self):
        assert is_secondary_section("about")
        assert is_secondary_section("team")
        assert is_secondary_section("career")
        assert is_secondary_section("contact")

    def test_meta_sections_are_secondary(self):
        assert is_secondary_section("changelog")
        assert is_secondary_section("sitemap")
        assert is_secondary_section("release")

    def test_social_sections_are_secondary(self):
        assert is_secondary_section("twitter")
        assert is_secondary_section("github")
        assert is_secondary_section("linkedin")

    def test_docs_sections_are_primary(self):
        assert not is_secondary_section("docs")
        assert not is_secondary_section("documentation")
        assert not is_secondary_section("api")
        assert not is_secondary_section("guide")
        assert not is_secondary_section("tutorial")

    def test_product_sections_are_primary(self):
        assert not is_secondary_section("features")
        assert not is_secondary_section("pricing")
        assert not is_secondary_section("products")
        assert not is_secondary_section("solutions")

    def test_blog_sections_are_primary(self):
        assert not is_secondary_section("blog")
        assert not is_secondary_section("news")
        assert not is_secondary_section("articles")

    def test_case_insensitive(self):
        assert is_secondary_section("PRIVACY")
        assert is_secondary_section("Privacy")
        assert is_secondary_section("privacy")


class TestFormatterOutput:

    def test_no_pages_returns_fallback(self):
        result = format_llms_txt("https://example.com", [])
        assert "# https://example.com" in result
        assert "No content available" in result

    def test_only_homepage_no_sections(self):
        pages = [
            PageInfo(
                url="https://example.com",
                title="Example Site",
                description="A test site",
                snippet="Test snippet"
            )
        ]
        result = format_llms_txt("https://example.com", pages)
        assert "# Example Site" in result
        assert "> A test site" in result
        assert "##" not in result

    def test_primary_sections_before_optional(self):
        pages = [
            PageInfo("https://example.com", "Home", "Homepage", ""),
            PageInfo("https://example.com/docs", "Docs", "Documentation", ""),
            PageInfo("https://example.com/privacy", "Privacy", "Privacy policy", ""),
        ]
        result = format_llms_txt("https://example.com", pages)

        lines = result.split('\n')
        docs_index = next(i for i, line in enumerate(lines) if '## Docs' in line)
        optional_index = next(i for i, line in enumerate(lines) if '## Optional' in line)

        assert docs_index < optional_index, "Primary sections should come before Optional"

    def test_optional_section_contains_secondary_pages(self):
        pages = [
            PageInfo("https://example.com", "Home", "Homepage", ""),
            PageInfo("https://example.com/docs", "Docs", "Documentation", ""),
            PageInfo("https://example.com/privacy", "Privacy", "Privacy policy", ""),
            PageInfo("https://example.com/terms", "Terms", "Terms of service", ""),
        ]
        result = format_llms_txt("https://example.com", pages)

        assert "## Optional" in result
        assert "[Privacy]" in result
        assert "[Terms]" in result

    def test_no_optional_section_when_no_secondary_pages(self):
        pages = [
            PageInfo("https://example.com", "Home", "Homepage", ""),
            PageInfo("https://example.com/docs", "Docs", "Documentation", ""),
            PageInfo("https://example.com/api", "API", "API reference", ""),
        ]
        result = format_llms_txt("https://example.com", pages)

        assert "## Optional" not in result
        assert "## Docs" in result
        assert "## Api" in result

    def test_all_secondary_pages_creates_only_optional(self):
        pages = [
            PageInfo("https://example.com", "Home", "Homepage", ""),
            PageInfo("https://example.com/privacy", "Privacy", "Privacy policy", ""),
            PageInfo("https://example.com/terms", "Terms", "Terms of service", ""),
        ]
        result = format_llms_txt("https://example.com", pages)

        assert "## Optional" in result
        h2_sections = [line for line in result.split('\n') if line.startswith('## ')]
        assert h2_sections == ["## Optional"]

    def test_description_truncation(self):
        long_desc = "x" * 200
        pages = [
            PageInfo("https://example.com", "Home", "Homepage", ""),
            PageInfo("https://example.com/docs", "Docs", long_desc, ""),
        ]
        result = format_llms_txt("https://example.com", pages)

        assert "x" * 150 in result
        assert "..." in result
        assert "x" * 151 not in result

    def test_link_format_compliance(self):
        pages = [
            PageInfo("https://example.com", "Home", "Homepage", ""),
            PageInfo("https://example.com/docs", "Docs", "Documentation page", ""),
        ]
        result = format_llms_txt("https://example.com", pages)

        assert "- [Docs](https://example.com/docs): Documentation page" in result

    def test_mixed_primary_and_secondary(self):
        pages = [
            PageInfo("https://example.com", "Home", "Homepage", ""),
            PageInfo("https://example.com/docs", "Docs", "Documentation", ""),
            PageInfo("https://example.com/api", "API", "API reference", ""),
            PageInfo("https://example.com/about", "About", "About us", ""),
            PageInfo("https://example.com/privacy", "Privacy", "Privacy policy", ""),
        ]
        result = format_llms_txt("https://example.com", pages)

        assert "## Docs" in result
        assert "## Api" in result
        assert "## Optional" in result

        lines = result.split('\n')
        docs_index = next(i for i, line in enumerate(lines) if '## Docs' in line)
        optional_index = next(i for i, line in enumerate(lines) if '## Optional' in line)
        assert docs_index < optional_index

    def test_section_name_cleaning(self):
        pages = [
            PageInfo("https://example.com", "Home", "Homepage", ""),
            PageInfo("https://example.com/api-reference", "API Ref", "API reference", ""),
            PageInfo("https://example.com/user_guide", "Guide", "User guide", ""),
        ]
        result = format_llms_txt("https://example.com", pages)

        assert "## Api Reference" in result
        assert "## User Guide" in result

    def test_empty_description_uses_snippet(self):
        pages = [
            PageInfo("https://example.com", "Home", "", "This is the snippet"),
        ]
        result = format_llms_txt("https://example.com", pages)

        assert "> This is the snippet" in result

    def test_fallback_to_main_section(self):
        pages = [
            PageInfo("https://example.com", "Home", "Homepage", ""),
            PageInfo("https://example.com", "Root", "Another root page", ""),
        ]
        result = format_llms_txt("https://example.com", pages)

        assert "# Home" in result


class TestPatternCoverage:

    def test_all_legal_patterns_work(self):
        legal_patterns = ['privacy', 'terms', 'legal', 'cookie', 'disclaimer']
        for pattern in legal_patterns:
            assert any(pattern in p for p in SECONDARY_PATH_PATTERNS)
            assert is_secondary_section(pattern)

    def test_all_meta_patterns_work(self):
        meta_patterns = ['sitemap', 'changelog', 'release']
        for pattern in meta_patterns:
            assert any(pattern in p for p in SECONDARY_PATH_PATTERNS)
            assert is_secondary_section(pattern)

    def test_all_contributing_patterns_work(self):
        contrib_patterns = ['contributing', 'code-of-conduct', 'governance', 'license']
        for pattern in contrib_patterns:
            assert any(pattern in p for p in SECONDARY_PATH_PATTERNS)
            assert is_secondary_section(pattern)

    def test_all_company_patterns_work(self):
        company_patterns = ['about', 'team', 'career', 'job', 'contact', 'company']
        for pattern in company_patterns:
            assert any(pattern in p for p in SECONDARY_PATH_PATTERNS)
            assert is_secondary_section(pattern)

    def test_all_social_patterns_work(self):
        social_patterns = ['twitter', 'github', 'linkedin', 'facebook', 'social']
        for pattern in social_patterns:
            assert any(pattern in p for p in SECONDARY_PATH_PATTERNS)
            assert is_secondary_section(pattern)

    def test_all_archive_patterns_work(self):
        archive_patterns = ['archive', 'old', 'legacy', 'deprecated']
        for pattern in archive_patterns:
            assert any(pattern in p for p in SECONDARY_PATH_PATTERNS)
            assert is_secondary_section(pattern)
