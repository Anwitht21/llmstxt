from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import json
from crawler import LLMCrawler, PageInfo
from storage import save_llms_txt
from config import settings

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok"}

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

@app.websocket("/ws/crawl")
async def websocket_crawl(websocket: WebSocket):
    await websocket.accept()

    try:
        data = await websocket.receive_text()
        payload = json.loads(data)

        url = str(payload['url'])
        max_pages = payload.get('maxPages', 50)
        desc_length = payload.get('descLength', 500)

        async def log(message: str):
            await websocket.send_json({"type": "log", "content": message})

        crawler = LLMCrawler(url, max_pages, desc_length, log)
        pages = await crawler.run()

        llms_txt = format_llms_txt(url, pages)
        await websocket.send_json({"type": "result", "content": llms_txt})

        hosted_url = await save_llms_txt(url, llms_txt, log)
        if hosted_url:
            await websocket.send_json({"type": "url", "content": hosted_url})

    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_json({"type": "error", "content": str(e)})
    finally:
        await websocket.close()