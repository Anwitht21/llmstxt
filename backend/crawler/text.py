from bs4 import BeautifulSoup

def extract_title(soup: BeautifulSoup) -> str:
    if soup.title:
        return soup.title.string.strip()
    h1 = soup.find('h1')
    return h1.get_text().strip() if h1 else "Untitled"

def extract_description(soup: BeautifulSoup) -> str:
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    if meta_desc and meta_desc.get('content'):
        return meta_desc['content'].strip()

    meta_og = soup.find('meta', attrs={'property': 'og:description'})
    if meta_og and meta_og.get('content'):
        return meta_og['content'].strip()

    return ""

def extract_text(soup: BeautifulSoup) -> str:
    for script in soup(['script', 'style', 'nav', 'footer', 'header']):
        script.decompose()

    text = soup.get_text(separator=' ', strip=True)
    return ' '.join(text.split())

def create_snippet(text: str, length: int) -> str:
    if len(text) <= length:
        return text
    return text[:length].rsplit(' ', 1)[0] + '...'
