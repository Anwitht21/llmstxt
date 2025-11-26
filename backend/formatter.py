from crawler import PageInfo

SECONDARY_PATH_PATTERNS = [
    '/privacy', '/terms', '/legal', '/cookie', '/disclaimer',
    '/sitemap', '/changelog', '/release',
    '/contributing', '/code-of-conduct', '/governance', '/license',
    '/about', '/team', '/career', '/job', '/contact', '/company',
    '/twitter', '/github', '/linkedin', '/facebook', '/social',
    '/archive', '/old', '/legacy', '/deprecated',
]

def is_secondary_section(section_name: str) -> bool:
    section_lower = section_name.lower()
    return any(pattern.strip('/') in section_lower for pattern in SECONDARY_PATH_PATTERNS)

def format_llms_txt(base_url: str, pages: list[PageInfo]) -> str:
    if not pages:
        return f"# {base_url}\n\n> No content available"

    homepage = pages[0]
    lines = [
        f"# {homepage.title}",
        "",
        f"> {homepage.description or homepage.snippet[:200]}",
        ""
    ]

    sections = {}
    for page in pages[1:]:
        path_parts = page.url.replace(base_url, "").strip("/").split("/")
        section = path_parts[0] if path_parts and path_parts[0] and path_parts[0] not in ['http:', 'https:'] else "Main"

        if section not in sections:
            sections[section] = []

        desc = ""
        if page.description:
            truncated = page.description[:150]
            desc = f": {truncated}..." if len(page.description) > 150 else f": {truncated}"
        sections[section].append(f"- [{page.title}]({page.url}){desc}")

    if not sections:
        return "\n".join(lines)

    primary_sections = {}
    secondary_sections = {}

    for section_name, links in sections.items():
        if is_secondary_section(section_name):
            secondary_sections[section_name] = links
        else:
            primary_sections[section_name] = links

    for section_name, links in sorted(primary_sections.items()):
        clean_name = section_name.replace('-', ' ').replace('_', ' ').title()
        lines.extend([
            f"## {clean_name}",
            "",
            *links,
            ""
        ])

    if secondary_sections:
        lines.extend([
            "## Optional",
            "",
        ])

        for section_name, links in sorted(secondary_sections.items()):
            lines.extend(links)

        lines.append("")

    return "\n".join(lines)
