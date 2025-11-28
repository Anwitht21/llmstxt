import pytest
from formatter import is_secondary_section, format_llms_txt, get_md_url, get_md_url_map, SECONDARY_PATH_PATTERNS
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
        assert "# example.com" in result
        assert "> No content available" in result

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
        assert "## API" in result

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
        assert "## API" in result
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

        assert "## API Reference" in result
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

        assert "# Example" in result  # Generic "Home" falls back to domain
        assert "## Main" in result  # Root-level pages go to Main section


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


class TestSpecCompliance:
    """Test llmstxt.org specification compliance."""

    def test_query_params_stripped(self):
        """URLs with query params should have clean section names."""
        pages = [
            PageInfo("https://example.com", "Home", "Site", ""),
            PageInfo("https://example.com/docs?page=2", "Page 2", "Docs", ""),
        ]
        result = format_llms_txt("https://example.com", pages)
        assert "## Docs" in result
        assert "?page=2" not in result

    def test_url_fragments_stripped(self):
        """URLs with fragments should have clean section names."""
        pages = [
            PageInfo("https://example.com", "Home", "Site", ""),
            PageInfo("https://example.com/api#section", "API", "API docs", ""),
        ]
        result = format_llms_txt("https://example.com", pages)
        assert "## API" in result
        assert "#section" not in result

    def test_generic_title_uses_domain(self):
        """Generic homepage titles should fallback to domain."""
        pages = [
            PageInfo("https://example.com", "Home", "A test site", ""),
        ]
        result = format_llms_txt("https://example.com", pages)
        assert "# Example" in result
        assert "# Home" not in result

    def test_welcome_title_uses_domain(self):
        """'Welcome' title should fallback to domain."""
        pages = [
            PageInfo("https://docs.python.org", "Welcome", "Python docs", ""),
        ]
        result = format_llms_txt("https://docs.python.org", pages)
        assert "# Docs Python" in result
        assert "# Welcome" not in result

    def test_abbreviations_preserved(self):
        """Common abbreviations should be uppercase."""
        pages = [
            PageInfo("https://example.com", "Home", "Site", ""),
            PageInfo("https://example.com/api-docs", "API Docs", "API", ""),
            PageInfo("https://example.com/rest-api", "REST", "REST API", ""),
            PageInfo("https://example.com/sdk", "SDK", "Software Development Kit", ""),
        ]
        result = format_llms_txt("https://example.com", pages)
        assert "## API Docs" in result
        assert "## REST API" in result
        assert "## SDK" in result

    def test_empty_description_no_colon(self):
        """Links without descriptions should not have trailing colon."""
        pages = [
            PageInfo("https://example.com", "Home", "Site", ""),
            PageInfo("https://example.com/docs", "Docs", "", ""),
        ]
        result = format_llms_txt("https://example.com", pages)
        assert "- [Docs](https://example.com/docs)\n" in result
        assert "- [Docs](https://example.com/docs):" not in result

    def test_blockquote_fallback_chain(self):
        """Blockquote should fallback: description → snippet → generic."""
        # Test empty description uses snippet
        pages = [PageInfo("https://example.com", "Site", "", "This is snippet")]
        result = format_llms_txt("https://example.com", pages)
        assert "> This is snippet" in result

        # Test both empty uses generic
        pages = [PageInfo("https://example.com", "Site", "", "")]
        result = format_llms_txt("https://example.com", pages)
        assert "> No description available" in result

    def test_blockquote_truncation_with_ellipsis(self):
        """Blockquote descriptions over 200 chars should get ellipsis."""
        long_desc = "x" * 250
        pages = [PageInfo("https://example.com", "Site", long_desc, "")]
        result = format_llms_txt("https://example.com", pages)
        assert "> " + "x" * 200 + "..." in result

    def test_link_description_truncation_with_ellipsis(self):
        """Link descriptions over 150 chars should get ellipsis."""
        long_desc = "y" * 200
        pages = [
            PageInfo("https://example.com", "Home", "Site", ""),
            PageInfo("https://example.com/docs", "Docs", long_desc, ""),
        ]
        result = format_llms_txt("https://example.com", pages)
        assert "y" * 150 + "..." in result

    def test_empty_pages_uses_domain_in_title(self):
        """Empty pages list should use domain in fallback."""
        result = format_llms_txt("https://www.example.com", [])
        assert "# www.example.com" in result
        assert "> No content available" in result

    def test_api_section_uppercase(self):
        """API in section names should be fully uppercase."""
        pages = [
            PageInfo("https://example.com", "Site", "Test", ""),
            PageInfo("https://example.com/api", "API", "API docs", ""),
        ]
        result = format_llms_txt("https://example.com", pages)
        assert "## API" in result
        assert "## Api" not in result

class TestMarkdownVersions:
    """Test .md version URL handling per llmstxt.org spec."""

    def test_md_url_construction_html_file(self):
        """HTML files should append .md to the full filename."""
        result = get_md_url("https://example.com/page.html")
        assert result == "https://example.com/page.html.md"

    def test_md_url_construction_directory(self):
        """Directories should append index.html.md."""
        result = get_md_url("https://example.com/docs/")
        assert result == "https://example.com/docs/index.html.md"

    def test_md_url_construction_no_extension(self):
        """URLs without extensions should append .md."""
        result = get_md_url("https://example.com/api")
        assert result == "https://example.com/api.md"

    def test_md_url_construction_root(self):
        """Root URLs should get index.html.md."""
        result = get_md_url("https://example.com/")
        assert result == "https://example.com/index.html.md"

    def test_format_with_md_url_map(self):
        """formatter should use .md URLs when provided in map."""
        pages = [
            PageInfo("https://example.com", "Home", "Homepage", ""),
            PageInfo("https://example.com/docs", "Docs", "Documentation", ""),
            PageInfo("https://example.com/api", "API", "API reference", ""),
        ]

        # Simulate that docs has .md version but api doesn't
        md_map = {
            "https://example.com/docs": "https://example.com/docs.md",
            "https://example.com/api": "https://example.com/api",
        }

        result = format_llms_txt("https://example.com", pages, md_map)

        # Docs should use .md URL
        assert "https://example.com/docs.md" in result
        # API should use regular URL
        assert "https://example.com/api)" in result
        assert "https://example.com/api.md" not in result

    def test_format_without_md_url_map(self):
        """formatter should work normally without md_url_map."""
        pages = [
            PageInfo("https://example.com", "Home", "Homepage", ""),
            PageInfo("https://example.com/docs", "Docs", "Documentation", ""),
        ]

        # No md_map provided
        result = format_llms_txt("https://example.com", pages)

        # Should use regular URLs
        assert "https://example.com/docs)" in result
        assert ".md" not in result

    @pytest.mark.asyncio
    async def test_get_md_url_map_rejects_html_content_type(self, monkeypatch):
        """get_md_url_map should reject URLs that return text/html (SPA shells)"""
        from unittest.mock import AsyncMock, MagicMock
        import httpx

        pages = [
            PageInfo("https://resy.com/about", "About", "About page", ""),
        ]

        # Mock httpx.AsyncClient to return text/html content-type
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'text/html'}

        mock_client = MagicMock()
        mock_client.head = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        monkeypatch.setattr("httpx.AsyncClient", lambda *args, **kwargs: mock_client)

        result = await get_md_url_map(pages)

        # Should NOT use .md URL because content-type is text/html
        assert result["https://resy.com/about"] == "https://resy.com/about"
        assert ".md" not in result["https://resy.com/about"]

    @pytest.mark.asyncio
    async def test_get_md_url_map_accepts_text_plain_content_type(self, monkeypatch):
        """get_md_url_map should accept URLs that return text/plain"""
        from unittest.mock import AsyncMock, MagicMock

        pages = [
            PageInfo("https://example.com/docs", "Docs", "Documentation", ""),
        ]

        # Mock httpx.AsyncClient to return text/plain content-type
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'text/plain; charset=utf-8'}

        mock_client = MagicMock()
        mock_client.head = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)

        monkeypatch.setattr("httpx.AsyncClient", lambda *args, **kwargs: mock_client)

        result = await get_md_url_map(pages)

        # Should use .md URL because content-type is text/plain
        assert result["https://example.com/docs"] == "https://example.com/docs.md"
