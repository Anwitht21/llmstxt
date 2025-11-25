from bs4 import BeautifulSoup
from crawler.text import extract_title, extract_description, extract_text, create_snippet

def test_extract_title():
    html = "<html><head><title>Test Page</title></head><body></body></html>"
    soup = BeautifulSoup(html, 'html.parser')
    assert extract_title(soup) == "Test Page"

def test_extract_description():
    html = '<html><head><meta name="description" content="Test description"/></head></html>'
    soup = BeautifulSoup(html, 'html.parser')
    assert extract_description(soup) == "Test description"

def test_create_snippet():
    text = "This is a long text " * 50
    snippet = create_snippet(text, 50)
    assert len(snippet) <= 53
    assert snippet.endswith("...")
