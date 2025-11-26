from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import json
import hashlib
from crawler import LLMCrawler, PageInfo
from storage import save_llms_txt
from config import settings
from database import save_site_metadata
from recrawl import recrawl_due_sites
from formatter import format_llms_txt, get_md_url_map

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

@app.post("/internal/cron/recrawl")
async def trigger_recrawl(x_cron_secret: str = Header(None)):
    if not settings.cron_secret or x_cron_secret != settings.cron_secret:
        raise HTTPException(status_code=401, detail="Unauthorized")

    results = await recrawl_due_sites()
    return {"status": "completed", "results": results}

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

        await log("Checking for .md versions of pages...")
        md_url_map = await get_md_url_map(pages)
        md_count = sum(1 for orig, md in md_url_map.items() if orig != md)
        if md_count > 0:
            await log(f"Found {md_count} pages with .md versions")

        llms_txt = format_llms_txt(url, pages, md_url_map)
        await websocket.send_json({"type": "result", "content": llms_txt})

        hosted_url = await save_llms_txt(url, llms_txt, log)
        if hosted_url:
            await websocket.send_json({"type": "url", "content": hosted_url})

            enable_auto_update = payload.get('enableAutoUpdate', False)
            recrawl_interval = payload.get('recrawlIntervalMinutes', 10080)

            if enable_auto_update:
                llms_hash = hashlib.sha256(llms_txt.encode()).hexdigest()
                await save_site_metadata(
                    base_url=url,
                    recrawl_interval_minutes=recrawl_interval,
                    max_pages=max_pages,
                    desc_length=desc_length,
                    latest_llms_hash=llms_hash,
                    latest_llms_url=hosted_url
                )
                await log("Auto-update enabled for this site")

    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_json({"type": "error", "content": str(e)})
    finally:
        await websocket.close()