import hashlib
from datetime import datetime, timezone
from crawler import LLMCrawler
from storage import save_llms_txt
from database import get_due_sites, update_crawl_result, update_scheduling_only
from formatter import format_llms_txt, get_md_url_map
from config import settings
from sitemap_utils import has_sitemap_changed
from scheduling import compute_next_crawl

async def no_op_log(message: str):
    pass

async def recrawl_due_sites() -> dict:
    sites = await get_due_sites()
    results = {
        "total": len(sites),
        "processed": 0,
        "updated": 0,
        "unchanged": 0,
        "errors": 0
    }
    now = datetime.now(timezone.utc)

    for site in sites:
        try:
            sitemap_has_changed = True
            newest_lastmod = None

            if site.sentinel_url and (site.sentinel_url.endswith('.xml') or 'sitemap' in site.sentinel_url):
                try:
                    sitemap_has_changed, newest_lastmod = await has_sitemap_changed(
                        site.sentinel_url,
                        site.last_changed_at or site.last_crawled_at
                    )

                    if not sitemap_has_changed:
                        print(f"Sitemap unchanged for {site.base_url}, skipping crawl")

                        next_crawl_at, _, _ = compute_next_crawl(
                            site.recrawl_interval_minutes,
                            site.avg_change_interval_minutes,
                            content_changed=False,
                            last_changed_at=site.last_changed_at,
                            now=now,
                            adaptive_enabled=False
                        )

                        await update_scheduling_only(
                            site.id,
                            next_crawl_at,
                            newest_lastmod
                        )
                        results["unchanged"] += 1
                        continue
                    else:
                        print(f"Sitemap shows changes for {site.base_url}, performing full crawl")
                except Exception as e:
                    print(f"Error checking sitemap for {site.base_url}: {e}")

            crawler = LLMCrawler(
                site.base_url,
                site.max_pages,
                site.desc_length,
                no_op_log,
                brightdata_api_key=settings.brightdata_api_key,
                brightdata_enabled=settings.brightdata_enabled,
                brightdata_zone=settings.brightdata_zone,
                brightdata_password=settings.brightdata_password
            )
            pages = await crawler.run()

            # Check for .md versions (per llmstxt.org spec)
            md_url_map = await get_md_url_map(pages)

            llms_txt = format_llms_txt(site.base_url, pages, md_url_map)

            if settings.llm_enhancement_enabled:
                try:
                    from llm_processor import LLMProcessor
                    processor = LLMProcessor(no_op_log)
                    result = await processor.process(llms_txt)

                    if result.success:
                        llms_txt = result.output
                except Exception as e:
                    print(f"LLM enhancement error for {site.base_url}: {e}")

            new_hash = hashlib.sha256(llms_txt.encode()).hexdigest()
            content_changed = (new_hash != site.latest_llms_hash)

            if content_changed:
                hosted_url = await save_llms_txt(site.base_url, llms_txt, no_op_log)
                if hosted_url:
                    results["updated"] += 1
                else:
                    hosted_url = site.latest_llms_url or ""
                    results["errors"] += 1
            else:
                hosted_url = site.latest_llms_url or ""

            next_crawl_at, new_avg_interval, new_last_changed = compute_next_crawl(
                site.recrawl_interval_minutes,
                site.avg_change_interval_minutes,
                content_changed,
                site.last_changed_at,
                now,
                adaptive_enabled=False
            )

            await update_crawl_result(
                site.id,
                new_hash,
                hosted_url,
                next_crawl_at,
                new_last_changed,
                newest_lastmod,
                new_avg_interval
            )

            results["processed"] += 1

        except Exception as e:
            print(f"Error recrawling {site.base_url}: {e}")
            results["errors"] += 1

    return results
