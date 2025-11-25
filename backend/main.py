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
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [
        f"# llms.txt for {base_url}",
        f"# Generated: {timestamp}",
        ""
    ]

    for page in pages:
        lines.extend([
            "[[page]]",
            f'url = "{page.url}"',
            f'title = "{page.title}"',
            f'description = "{page.description}"',
            f'snippet = """{page.snippet}"""',
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
