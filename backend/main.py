from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Header, HTTPException, Request, Body
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone
import json
import hashlib
import httpx
from crawler import LLMCrawler, PageInfo
from storage import save_llms_txt
from config import settings
from database import save_site_metadata, get_supabase_client
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

@app.post("/internal/hooks/site-changed")
async def trigger_site_recrawl(
    request: Request,
    base_url: str = Body(...),
    webhook_secret: str = Body(None)
):
    try:
        client = get_supabase_client()
        if not client:
            raise HTTPException(status_code=503, detail="Database unavailable")

        result = client.table("crawl_sites") \
            .select("*") \
            .eq("base_url", base_url) \
            .execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Site not enrolled")

        site = result.data[0]

        if site.get("webhook_secret") and webhook_secret != site.get("webhook_secret"):
            raise HTTPException(status_code=401, detail="Invalid webhook secret")

        now = datetime.now(timezone.utc)
        client.table("crawl_sites").update({
            "next_crawl_at": now.isoformat(),
            "updated_at": now.isoformat()
        }).eq("base_url", base_url).execute()

        return {"status": "scheduled", "base_url": base_url, "next_crawl_at": now.isoformat()}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/crawl")
async def websocket_crawl(websocket: WebSocket, api_key: str = None):
    if settings.api_key and api_key != settings.api_key:
        await websocket.close(code=1008, reason="Unauthorized")
        return

    await websocket.accept()

    try:
        data = await websocket.receive_text()
        payload = json.loads(data)

        url = str(payload['url'])
        max_pages = payload.get('maxPages', 50)
        desc_length = payload.get('descLength', 500)
        use_brightdata = payload.get('useBrightdata', settings.brightdata_enabled)

        async def log(message: str):
            await websocket.send_json({"type": "log", "content": message})

        crawler = LLMCrawler(
            url,
            max_pages,
            desc_length,
            log,
            brightdata_api_key=settings.brightdata_api_key,
            brightdata_enabled=use_brightdata,
            brightdata_zone=settings.brightdata_zone,
            brightdata_password=settings.brightdata_password
        )
        pages = await crawler.run()

        await log("Checking for .md versions of pages...")
        md_url_map = await get_md_url_map(pages)
        md_count = sum(1 for orig, md in md_url_map.items() if orig != md)
        if md_count > 0:
            await log(f"Found {md_count} pages with .md versions")

        llms_txt = format_llms_txt(url, pages, md_url_map)

        llm_enhance = payload.get('llmEnhance', False)
        if llm_enhance and settings.llm_enhancement_enabled:
            try:
                await log("Enhancing with LLM...")
                from llm_processor import LLMProcessor
                processor = LLMProcessor(log)
                result = await processor.process(llms_txt)

                if result.success:
                    llms_txt = result.output
                    await log(f"LLM enhancement: {result.stats}")
                else:
                    await log(f"LLM enhancement failed, using original: {result.error}")
            except Exception as e:
                await log(f"LLM enhancement error: {e}")

        await websocket.send_json({"type": "result", "content": llms_txt})

        hosted_url = await save_llms_txt(url, llms_txt, log)
        if hosted_url:
            await websocket.send_json({"type": "url", "content": hosted_url})

            enable_auto_update = payload.get('enableAutoUpdate', False)
            recrawl_interval = payload.get('recrawlIntervalMinutes', 10080)

            if enable_auto_update:
                llms_hash = hashlib.sha256(llms_txt.encode()).hexdigest()

                # Detect sentinel URL
                sentinel_url = None
                if hasattr(crawler, 'discovered_sitemap_url'):
                    sentinel_url = crawler.discovered_sitemap_url
                else:
                    # Try to find sitemap
                    async with httpx.AsyncClient(timeout=5.0) as client:
                        for path in ['/sitemap.xml', '/sitemap_index.xml']:
                            try:
                                resp = await client.head(f"{url}{path}")
                                if resp.status_code == 200:
                                    sentinel_url = f"{url}{path}"
                                    break
                            except:
                                continue

                await save_site_metadata(
                    base_url=url,
                    recrawl_interval_minutes=recrawl_interval,
                    max_pages=max_pages,
                    desc_length=desc_length,
                    latest_llms_hash=llms_hash,
                    latest_llms_url=hosted_url,
                    sentinel_url=sentinel_url
                )
                await log("Auto-update enabled for this site")

    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_json({"type": "error", "content": str(e)})
    finally:
        await websocket.close()