from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

SKIP_PATTERNS = ['/logout', '/login', '/admin', '/api/', '/jobs/', '.pdf', '.zip', '.jpg', '.png', '.gif']

def normalize_url(url: str) -> str:
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip('/')

def same_domain(url1: str, url2: str) -> bool:
    return urlparse(url1).netloc == urlparse(url2).netloc

def should_skip(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.query and len(parsed.query) > 50:
        return True
    return any(pattern in url for pattern in SKIP_PATTERNS)

def extract_links(html: str, base_url: str) -> list[str]:
    soup = BeautifulSoup(html, 'html.parser')
    links = []

    for tag in soup.find_all('a', href=True):
        href = tag['href']
        absolute_url = urljoin(base_url, href)
        normalized = normalize_url(absolute_url)

        if same_domain(normalized, base_url) and not should_skip(normalized):
            links.append(normalized)

    return list(set(links))
