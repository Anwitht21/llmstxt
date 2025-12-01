from crawler.llm_crawler import PageInfo
from urllib.parse import urlparse

TAG_PATTERNS = {
    'API': ['api', 'rest-api', 'graphql', 'endpoint', '/api/', 'api-reference'],
    'Guide': ['guide', 'tutorial', 'how-to', 'walkthrough', 'learn'],
    'Quickstart': ['getting-started', 'quickstart', 'quick-start', 'quick start',
                   'get-started', 'getting started', 'start'],
    'Reference': ['reference', 'documentation', '/docs/', 'reference-guide'],
    'Example': ['example', 'sample', 'demo', 'code-sample', 'examples'],
    'SDK': ['sdk', 'library', 'client-library', 'package'],
    'CLI': ['cli', 'command-line', 'terminal', 'commands'],
    'Blog': ['blog', 'article', 'post', '/blog/', 'news'],
    'Changelog': ['changelog', 'release-notes', 'releases', 'updates', 'what-new'],

    'Beginner': ['getting-started', 'intro', 'introduction', 'basics', 'fundamentals'],
    'Advanced': ['advanced', 'expert', 'in-depth', 'deep-dive'],

    'Security': ['security', 'auth', 'authentication', 'authorization', 'oauth'],
    'Performance': ['performance', 'optimization', 'speed', 'caching'],
    'Integration': ['integration', 'webhook', 'third-party', 'connect'],
    'Troubleshooting': ['troubleshoot', 'debug', 'error', 'faq', 'common-issues'],
}

def assign_tags(page: PageInfo, section_name: str = "") -> list[str]:
    parsed_url = urlparse(page.url)
    url_path = parsed_url.path

    text = f"{url_path} {page.title}".lower()
    matched_tags = []

    for tag, patterns in TAG_PATTERNS.items():
        if any(pattern in text for pattern in patterns):
            matched_tags.append(tag)

    content_tags = [t for t in matched_tags if t in ['API', 'Guide', 'Quickstart',
                                                       'Reference', 'Example', 'SDK',
                                                       'CLI', 'Blog', 'Changelog']]
    complexity_tags = [t for t in matched_tags if t in ['Beginner', 'Advanced']]
    topic_tags = [t for t in matched_tags if t not in content_tags + complexity_tags]

    section_lower = section_name.lower()
    filtered_content = []

    for tag in content_tags:
        tag_lower = tag.lower()
        if tag_lower == 'api' and 'api' in section_lower:
            continue
        if tag_lower in ['guide', 'quickstart'] and any(x in section_lower for x in ['getting-started', 'guide', 'quickstart', 'start']):
            continue
        if tag_lower == 'example' and 'example' in section_lower:
            continue
        if tag_lower == 'blog' and 'blog' in section_lower:
            continue
        if tag_lower == 'reference' and any(x in section_lower for x in ['reference', 'docs', 'documentation']):
            continue
        if tag_lower == 'sdk' and 'sdk' in section_lower:
            continue
        if tag_lower == 'cli' and 'cli' in section_lower:
            continue

        filtered_content.append(tag)

    filtered_complexity = []
    for tag in complexity_tags:
        if tag == 'Beginner' and any(x in section_lower for x in ['getting-started', 'quickstart', 'start', 'intro']):
            continue
        filtered_complexity.append(tag)

    result = filtered_complexity[:1] + topic_tags[:2]

    if len(result) < 3 and filtered_content:
        result += filtered_content[:3-len(result)]

    return result[:3]

def format_description_with_tags(description: str, tags: list[str]) -> str:
    if not tags:
        return description

    tag_string = ' '.join(f'[{tag}]' for tag in tags)

    if description:
        return f"{description.rstrip()} {tag_string}"
    else:
        return tag_string
