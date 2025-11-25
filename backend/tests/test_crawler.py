from crawler.scout import normalize_url, same_domain, should_skip, extract_links

def test_normalize_url():
    assert normalize_url("https://example.com/page/") == "https://example.com/page"
    assert normalize_url("https://example.com/") == "https://example.com"

def test_same_domain():
    assert same_domain("https://example.com/page", "https://example.com/other")
    assert not same_domain("https://example.com", "https://other.com")

def test_should_skip():
    assert should_skip("https://example.com/logout")
    assert should_skip("https://example.com/admin/panel")
    assert should_skip("https://example.com/file.pdf")
    assert not should_skip("https://example.com/about")

def test_extract_links():
    html = '''
    <html>
        <body>
            <a href="/about">About</a>
            <a href="https://example.com/contact">Contact</a>
            <a href="https://other.com/external">External</a>
        </body>
    </html>
    '''
    links = extract_links(html, "https://example.com")
    assert "https://example.com/about" in links
    assert "https://example.com/contact" in links
    assert "https://other.com/external" not in links
