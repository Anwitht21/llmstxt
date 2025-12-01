SYSTEM_PROMPT = """You are an expert at organizing and improving llms.txt files. Your job is to take a basic llms.txt file and improve it while STRICTLY following these rules:

CRITICAL RULES - NEVER VIOLATE:
1. NEVER modify, add, or remove URLs. Every URL in the input MUST appear exactly once in the output.
2. NEVER hallucinate content, pages, or links that don't exist in the input.
3. ONLY improve: section organization, section names, descriptions, and content ordering.

FORMAT REQUIREMENTS (llmstxt.org spec):
1. Exactly ONE H1 title (starts with `# `)
2. ONE blockquote summary immediately after H1 (starts with `> `, under 200 characters)
3. Sections use H2 headings (`## Section Name`)
4. Links use format: `- [Link Text](url): Description under 150 chars [TAG: Optional]`
5. Keep an "Optional" section for secondary content (privacy, terms, about, etc.)

IMPROVEMENT GOALS:
1. Section Organization: Group related pages into logical, meaningful sections
2. Section Names: Use clear, descriptive names (not just URL paths)
3. Descriptions: Rewrite to be clear, informative, and helpful (under 150 chars each)
4. Content Prioritization: Put most important content first, secondary content in "Optional"
5. Site Summary: Create an informative H1 and blockquote that capture the site's purpose

Output only the improved llms.txt file. Do not add explanations or comments."""

FEW_SHOT_EXAMPLES = """
### Example 1

INPUT:
```markdown
# cipherstash.com

> CipherStash helps secure and encrypt sensitive data for modern applications.

## Home
- [Home](https://cipherstash.com/): CipherStash homepage overview

## Products
- [Protect.js SDK](https://github.com/cipherstash/protectjs): JS/TS encryption SDK [Integration]
- [CipherStash Proxy](https://cipherstash.com/blog/introducing-proxy): Transparent SQL proxy for PostgreSQL [Security]
- [ZeroKMS](https://cipherstash.com/): Key-management service powering encryption and audit logs

## Resources
- [Blog](https://cipherstash.com/blog): Company blog and product updates  
- [Case Studies](https://cipherstash.com/case-studies/journalia.md): Example use cases  
- [Case Studies – BNDRY](https://cipherstash.com/case-studies/bndry.md): Another use case  
- [FAQ](https://cipherstash.com/faq.md): Frequently asked questions
```

OUTPUT:
```markdown
# CipherStash

> If you sell to data security conscious customers you need CipherStash

CipherStash helps customers in the health, finance, insurance, education and legal industries as well as government:

* win and retain data-sensitive clients  
* unlock data-driven insights by enabling safe data capture instead of avoidance  
* smooth the transition to AI-enabled technology via secure, controlled and audited data access  
* meet regulatory compliance requirements

## Trusted data access

CipherStash enables trusted data access:

1. Sensitive data is _only_ ever accessible by the appropriate person at the appropriate time  
2. Every sensitive data access is recorded along with who accessed it for auditing purposes  

## CipherStash Protect
- [Protect.js SDK](https://github.com/cipherstash/protectjs) [Integration]
- [Protect.js README](https://raw.githubusercontent.com/cipherstash/protectjs/refs/heads/main/packages/protect/README.md)  
- [Protect.js Docs](https://raw.githubusercontent.com/cipherstash/protectjs/refs/heads/main/docs/README.md)

## CipherStash Proxy  
- [CipherStash Proxy](https://github.com/cipherstash/proxy) [Security]
- [Proxy README](https://raw.githubusercontent.com/cipherstash/proxy/refs/heads/main/README.md)

##CipherStash ZeroKMS  
- [ZeroKMS](https://cipherstash.com/products/zerokms)

## Case studies
- [Journalia](https://cipherstash.com/case-studies/journalia.md)  
- [BNDRY](https://cipherstash.com/case-studies/bndry.md)

## Blog & FAQ
- [CipherStash Blog](https://cipherstash.com/blog)  
- [FAQ](https://cipherstash.com/faq.md)
```

### Example 2

INPUT:
```markdown
# acme.io

> acme.io

## Products
- [Widget A](https://acme.io/products/widget-a): Widget A product page
- [Widget B](https://acme.io/products/widget-b): Widget B product [Integration]

## Company
- [About](https://acme.io/company/about): About us page
- [Contact](https://acme.io/company/contact): Contact information

## Legal
- [Privacy](https://acme.io/legal/privacy): Privacy policy
```

OUTPUT:
```markdown
# Acme - Enterprise Widget Solutions

> Enterprise-grade widgets and tools for modern businesses. Trusted by thousands of companies worldwide.

## Products
- [Widget A](https://acme.io/products/widget-a): Advanced widget with real-time analytics and automation capabilities
- [Widget B](https://acme.io/products/widget-b): Lightweight widget designed for small to medium businesses [Integration]

## Optional
- [About](https://acme.io/company/about): Learn about Acme's mission and team
- [Contact](https://acme.io/company/contact): Get in touch with our sales and support teams
- [Privacy](https://acme.io/legal/privacy): Privacy policy and data handling practices
```

### Example 3

INPUT:
```markdown
# fasthtml

> FastHTML is a python library which brings together Starlette, Uvicorn, HTMX, and fastcore’s “FT” tags into a minimal framework for building server-rendered hypermedia applications.

## Docs
- [FastHTML concise guide](https://www.fastht.ml/docs/ref/concise_guide.html.md): Overview of FastHTML’s core patterns  
- [HTMX reference](https://raw.githubusercontent.com/bigskysoftware/htmx/master/www/content/reference.md): Documentation for HTMX attributes and events [Reference]
- [Starlette quick guide](https://gist.githubusercontent.com/jph00/e91192e9bdc1640f5421ce3c904f2efb/raw/61a2774912414029edaf1a55b506f0e283b93c46/starlette-quick.md): Reference for Starlette, the ASGI foundation [Guide]

## API
- [API List](https://www.fastht.ml/docs/apilist.txt): List of all FastHTML functions and methods [Reference]
- [MonsterUI API List](https://raw.githubusercontent.com/AnswerDotAI/MonsterUI/refs/heads/main/docs/apilist.txt): API reference for MonsterUI components compatible with FastHTML [Reference]

## Examples
- [Websockets application](https://raw.githubusercontent.com/AnswerDotAI/fasthtml/main/examples/basic_ws.py): Example using WebSockets with HTMX + FastHTML  
- [Todo list application](https://raw.githubusercontent.com/AnswerDotAI/fasthtml/main/examples/adv_app.py): CRUD todo-app example illustrating idiomatic usage  

## Optional
- [Surreal (JS helper)](https://raw.githubusercontent.com/AnswerDotAI/surreal/main/README.md): Optional JS-helper library usable with FastHTML  
- [Starlette docs subset](https://gist.githubusercontent.com/jph00/809e4a4808d4510be0e3dc9565e9cbd3/raw/9b717589ca44cedc8aaf00b2b8cacef922964c0f/starlette-sml.md): Supplementary docs for Starlette features  
```

OUTPUT:
```markdown
# FastHTML

> FastHTML is a lightweight Python web framework that combines Starlette, Uvicorn, HTMX, and fastcore “FT” tags to enable hypermedia-first, server-rendered web apps without frontend frameworks.

FastHTML lets you build modern, interactive web applications entirely in Python — no JS framework required — while preserving full control over HTML, styling, and backend logic. It is ideal for dashboard apps, dynamic content sites, or any web app where you want simplicity and performance.  [oai_citation:0‡fastht.ml](https://www.fastht.ml/docs/index.html?utm_source=chatgpt.com)

## Core Documentation & Quick Start
- [Concise Guide](https://www.fastht.ml/docs/ref/concise_guide.html.md): Core guide explaining FastHTML’s idiomatic patterns and architecture  
- [HTMX Reference](https://raw.githubusercontent.com/bigskysoftware/htmx/master/www/content/reference.md): Full reference of HTMX attributes, events, and usage for dynamic interactivity [Reference]
- [Starlette Quick Guide](https://gist.githubusercontent.com/jph00/e91192e9bdc1640f5421ce3c904f2efb/raw/61a2774912414029edaf1a55b506f0e283b93c46/starlette-quick.md): ASGI fundamentals and Starlette reference used by FastHTML [Guide]

## API Reference
- [FastHTML API List](https://www.fastht.ml/docs/apilist.txt): Complete list of FastHTML methods, routing APIs, and built-in utilities [Reference]
- [MonsterUI API List](https://raw.githubusercontent.com/AnswerDotAI/MonsterUI/refs/heads/main/docs/apilist.txt): Component library API for building UI elements compatible with FastHTML [Reference]

## Example Applications
- [WebSockets Example](https://raw.githubusercontent.com/AnswerDotAI/fasthtml/main/examples/basic_ws.py): Simple real-time app showcasing HTMX + WebSockets with FastHTML  
- [Todo App Example](https://raw.githubusercontent.com/AnswerDotAI/fasthtml/main/examples/adv_app.py): CRUD application example illustrating idiomatic FastHTML patterns, routing, and template usage  

## Optional / Additional Resources
- [Surreal JS Helper Library](https://raw.githubusercontent.com/AnswerDotAI/surreal/main/README.md): Optional lightweight JS helper library compatible with FastHTML for enhanced frontend behavior  
- [Starlette Supplemental Docs](https://gist.githubusercontent.com/jph00/809e4a4808d4510be0e3dc9565e9cbd3/raw/9b717589ca44cedc8aaf00b2b8cacef922964c0f/starlette-sml.md): Additional Starlette reference for advanced backend configurations and middleware usage  
```
"""

def build_user_prompt(llms_txt: str) -> str:
    return f"""{FEW_SHOT_EXAMPLES}

Now improve this llms.txt file following the same pattern:

INPUT:
```markdown
{llms_txt}
```

OUTPUT:
```markdown"""

def build_messages(llms_txt: str) -> list[dict]:
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": build_user_prompt(llms_txt)}
    ]
