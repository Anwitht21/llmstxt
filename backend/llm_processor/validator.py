import re
from typing import Tuple, List, Set

def extract_urls(content: str) -> Set[str]:
    pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
    matches = re.findall(pattern, content)
    return {url for text, url in matches}

def validate_llms_txt(content: str, original_urls: Set[str]) -> Tuple[bool, List[str]]:
    errors = []
    lines = content.split('\n')

    h1_lines = [line for line in lines if line.startswith('# ') and not line.startswith('## ')]
    if len(h1_lines) == 0:
        errors.append("Missing H1 title (must start with '# ')")
    elif len(h1_lines) > 1:
        errors.append(f"Multiple H1 titles found ({len(h1_lines)}), must have exactly one")

    blockquote_lines = [line for line in lines if line.startswith('> ')]
    if len(blockquote_lines) == 0:
        errors.append("Missing blockquote summary (must start with '> ')")
    else:
        for bq in blockquote_lines:
            bq_text = bq[2:].strip()
            if len(bq_text) > 200:
                errors.append(f"Blockquote too long ({len(bq_text)} chars, max 200): {bq_text[:50]}...")

    invalid_headers = [line for line in lines if line.startswith('### ') or line.startswith('#### ')]
    if invalid_headers:
        errors.append(f"Invalid header levels found (use H2 only): {invalid_headers[:3]}")

    generated_urls = extract_urls(content)

    missing_urls = original_urls - generated_urls
    if missing_urls:
        errors.append(f"URLs removed from original ({len(missing_urls)}): {list(missing_urls)[:3]}")

    added_urls = generated_urls - original_urls
    if added_urls:
        errors.append(f"New URLs added (hallucination): {list(added_urls)[:3]}")

    for i, line in enumerate(lines):
        if line.startswith('- ['):
            if not re.match(r'^- \[.+\]\(.+\):[ ].+$', line):
                errors.append(f"Line {i+1}: Invalid link format (should be '- [Text](url): Description'): {line[:60]}")

    return (len(errors) == 0, errors)

def truncate_descriptions(content: str, max_length: int = 150) -> str:
    lines = content.split('\n')
    result_lines = []

    for line in lines:
        if line.startswith('- ['):
            match = re.match(r'^(- \[.+\]\(.+\):[ ])(.+)$', line)
            if match:
                prefix, description = match.groups()
                if len(description) > max_length:
                    truncated = description[:max_length].rsplit(' ', 1)[0]
                    if len(truncated) < max_length - 10:
                        truncated = description[:max_length]
                    line = f"{prefix}{truncated}..."
        result_lines.append(line)

    return '\n'.join(result_lines)
