from dataclasses import dataclass
from typing import Callable
import httpx
from bs4 import BeautifulSoup
from .state import CrawlState
from .scout import normalize_url, extract_links, parse_sitemap
from .text import extract_title, extract_description, extract_text, create_snippet
from .scraping_browser_client import has_meaningful_content, ScrapingBrowserClient

@dataclass
class PageInfo:
    url: str
    title: str
    description: str
    snippet: str

class LLMCrawler:
    def __init__(self, base_url: str, max_pages: int, desc_length: int, log_callback: Callable,
                 brightdata_api_key: str | None = None, brightdata_enabled: bool = True,
                 brightdata_zone: str = "scraping_browser1", brightdata_password: str | None = None):
        self.state = CrawlState(base_url=normalize_url(base_url), max_pages=max_pages)
        self.desc_length = desc_length
        self.log = log_callback
        self.state.queue.append(self.state.base_url)

        self.brightdata_client = None
        if brightdata_enabled and brightdata_api_key:
            self.brightdata_client = ScrapingBrowserClient(brightdata_api_key, brightdata_enabled, brightdata_zone, brightdata_password)

    async def _try_sitemap(self, client: httpx.AsyncClient) -> list[str]:
        for path in ['/sitemap.xml', '/sitemap_index.xml']:
            try:
                resp = await client.get(f"{self.state.base_url}{path}")
                if resp.status_code == 200:
                    return parse_sitemap(resp.text, self.state.base_url)
            except:
                continue
        return []

    async def run(self) -> list[PageInfo]:
        pages = []
        max_attempts = self.state.max_pages * 3  # Try up to 3x the target to handle failures
        attempts = 0

        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            sitemap_urls = await self._try_sitemap(client)
            if sitemap_urls:
                await self.log(f"Using sitemap: found {len(sitemap_urls)} URLs")
                self.state.queue.clear()
                self.state.queue.append(self.state.base_url)
                for url in sitemap_urls[:max_attempts]:  # Load more URLs to handle failures
                    if url != self.state.base_url:
                        self.state.queue.append(url)
            else:
                await self.log("No sitemap found, using BFS crawl")

            while (self.state.queue and
                   len(pages) < self.state.max_pages and
                   attempts < max_attempts):
                attempts += 1
                url = self.state.queue.popleft()

                if url in self.state.visited:
                    continue

                try:
                    await self.log(f"Visiting: {url}")
                    html = None
                    httpx_html = None

                    try:
                        await self.log(f"  → Trying httpx...")
                        response = await client.get(url)
                        response.raise_for_status()
                        httpx_html = response.text

                        if has_meaningful_content(httpx_html):
                            await self.log(f"  ✓ httpx succeeded")
                            html = httpx_html
                        else:
                            await self.log(f"  ✗ httpx returned empty/blocked content")
                    except Exception as httpx_error:
                        await self.log(f"  ✗ httpx failed: {str(httpx_error)}")

                    if html is None and self.brightdata_client is not None:
                        try:
                            await self.log(f"  → Escalating to Bright Data Scraping Browser...")
                            html = await self.brightdata_client.fetch(url)
                            await self.log(f"  ✓ Scraping Browser succeeded")
                        except Exception as brightdata_error:
                            await self.log(f"  ✗ Scraping Browser failed: {str(brightdata_error)}")
                            if httpx_html is not None:
                                await self.log(f"  → Falling back to httpx result")
                                html = httpx_html

                    if html is None:
                        raise ValueError("Failed to fetch content")

                    soup = BeautifulSoup(html, 'html.parser')

                    title = extract_title(soup)
                    description = extract_description(soup)
                    text = extract_text(soup)
                    snippet = create_snippet(text, self.desc_length)

                    pages.append(PageInfo(
                        url=url,
                        title=title,
                        description=description,
                        snippet=snippet
                    ))

                    self.state.visited.add(url)

                    links = extract_links(html, url)
                    for link in links:
                        if link not in self.state.visited:
                            self.state.queue.append(link)

                except Exception as e:
                    await self.log(f"Error crawling {url}: {str(e)}")
                    self.state.visited.add(url)

        if self.brightdata_client:
            stats = self.brightdata_client.get_usage_stats()
            if stats['requests'] > 0:
                success_rate = (stats['successful'] / stats['requests'] * 100) if stats['requests'] > 0 else 0
                await self.log(
                    f"Scraping Browser usage: {stats['requests']} requests, "
                    f"{stats['successful']} successful ({success_rate:.0f}%), "
                    f"~${stats['estimated_cost_usd']} estimated cost"
                )

        if len(pages) < self.state.max_pages:
            await self.log(f"Warning: Only found {len(pages)} pages (requested {self.state.max_pages})")

        await self.log(f"Crawl complete: {len(pages)} pages")
        return pages
