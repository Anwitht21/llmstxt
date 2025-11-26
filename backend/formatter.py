from crawler import PageInfo
from urllib.parse import urlparse, urlunparse

SECONDARY_PATH_PATTERNS = [
    '/privacy', '/terms', '/legal', '/cookie', '/disclaimer',
    '/sitemap', '/changelog', '/release',
    '/contributing', '/code-of-conduct', '/governance', '/license',
    '/about', '/team', '/career', '/job', '/contact', '/company',
    '/twitter', '/github', '/linkedin', '/facebook', '/social',
    '/archive', '/old', '/legacy', '/deprecated',
]

def clean_url(url: str) -> str:
    parsed = urlparse(url)
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', '', ''))

def truncate(text: str, length: int = 150) -> str:
    if not text:
        return ""
    text = text.strip()
    return f"{text[:length]}..." if len(text) > length else text

def get_site_title(homepage: PageInfo, base_url: str) -> str:
    title = homepage.title.strip() if homepage.title else ""

    generic_titles = {'home', 'welcome', 'index', ''}
    if title.lower() in generic_titles:
        domain = urlparse(base_url).netloc
        domain = domain.replace('www.', '').replace('.com', '').replace('.org', '')
        return domain.replace('.', ' ').title()

    return truncate(title, 80)

def get_summary(homepage: PageInfo) -> str:
    desc = homepage.description or homepage.snippet or "No description available"
    return truncate(desc.strip(), 200)

def clean_section_name(name: str) -> str:
    if not name or not name.strip():
        return "Main"

    name = name.strip()
    abbrevs = {'api', 'rest', 'graphql', 'sdk', 'cli', 'ui', 'ux', 'faq', 'rss'}

    name = name.replace('-', ' ').replace('_', ' ')
    words = name.split()

    return ' '.join(
        w.upper() if w.lower() in abbrevs else w.capitalize()
        for w in words
    )

def is_secondary_section(section_name: str) -> bool:
    section_lower = section_name.lower()
    return any(pattern.strip('/') in section_lower for pattern in SECONDARY_PATH_PATTERNS)

def format_llms_txt(base_url: str, pages: list[PageInfo]) -> str:
    if not pages:
        domain = urlparse(base_url).netloc
        return f"# {domain}\n\n> No content available"

    homepage = pages[0]

    lines = [
        f"# {get_site_title(homepage, base_url)}",
        "",
        f"> {get_summary(homepage)}",
        ""
    ]

    sections = {}
    for page in pages[1:]:
        clean = clean_url(page.url)
        path_parts = clean.replace(base_url, "").strip("/").split("/")
        section = path_parts[0] if path_parts and path_parts[0] else "main"

        if section not in sections:
            sections[section] = []

        desc = truncate(page.description, 150) if page.description else ""
        link_text = f"[{page.title}]({clean})"
        full_link = f"- {link_text}: {desc}" if desc else f"- {link_text}"

        sections[section].append(full_link)

    if not sections:
        return "\n".join(lines)

    primary = {}
    secondary = {}

    for section_name, links in sections.items():
        if is_secondary_section(section_name):
            secondary[section_name] = links
        else:
            primary[section_name] = links

    for section_name in sorted(primary.keys()):
        clean_name = clean_section_name(section_name)
        lines.extend([
            f"## {clean_name}",
            "",
            *primary[section_name],
            ""
        ])

    if secondary:
        lines.extend([
            "## Optional",
            "",
        ])

        for section_name in sorted(secondary.keys()):
            lines.extend(secondary[section_name])

        lines.append("")

    return "\n".join(lines)
