import hashlib
from crawler import LLMCrawler
from storage import save_llms_txt
from database import get_due_sites, update_crawl_result
from formatter import format_llms_txt, get_md_url_map

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

    for site in sites:
        try:
            crawler = LLMCrawler(site.base_url, site.max_pages, site.desc_length, no_op_log)
            pages = await crawler.run()

            # Check for .md versions (per llmstxt.org spec)
            md_url_map = await get_md_url_map(pages)

            llms_txt = format_llms_txt(site.base_url, pages, md_url_map)
            new_hash = hashlib.sha256(llms_txt.encode()).hexdigest()

            if new_hash != site.latest_llms_hash:
                hosted_url = await save_llms_txt(site.base_url, llms_txt, no_op_log)
                if hosted_url:
                    await update_crawl_result(site.id, new_hash, hosted_url)
                    results["updated"] += 1
                else:
                    await update_crawl_result(site.id, new_hash, site.latest_llms_url or "")
                    results["errors"] += 1
            else:
                await update_crawl_result(site.id, new_hash, site.latest_llms_url or "")
                results["unchanged"] += 1

            results["processed"] += 1

        except Exception as e:
            print(f"Error recrawling {site.base_url}: {e}")
            results["errors"] += 1

    return results
