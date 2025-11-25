from crawler import PageInfo

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

    for section_name, links in sorted(sections.items()):
        clean_name = section_name.replace('-', ' ').replace('_', ' ').title()
        lines.extend([
            f"## {clean_name}",
            "",
            *links,
            ""
        ])

    return "\n".join(lines)
