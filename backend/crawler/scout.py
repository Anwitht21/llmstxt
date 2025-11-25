from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

SKIP_PATTERNS = ['/logout', '/login', '/admin', '/api/', '/jobs/', '/sitemap', '/_metadata',
                 '.pdf', '.zip', '.jpg', '.png', '.gif', '.xml', '/feed', '/rss', '.atom']

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

def parse_sitemap(xml_content: str, base_url: str) -> list[str]:
    try:
        root = ET.fromstring(xml_content)
        ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        urls = [loc.text for loc in root.findall('.//ns:loc', ns) if loc.text]
        if not urls:
            urls = [loc.text for loc in root.findall('.//loc') if loc.text]

        filtered = [normalize_url(url) for url in urls
                   if same_domain(url, base_url) and not should_skip(url)]
        return filtered
    except:
        return []

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
