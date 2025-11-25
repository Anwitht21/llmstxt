from dataclasses import dataclass
from typing import Callable
import httpx
from bs4 import BeautifulSoup
from .state import CrawlState
from .scout import normalize_url, extract_links
from .text import extract_title, extract_description, extract_text, create_snippet

@dataclass
class PageInfo:
    url: str
    title: str
    description: str
    snippet: str

class LLMCrawler:
    def __init__(self, base_url: str, max_pages: int, desc_length: int, log_callback: Callable):
        self.state = CrawlState(base_url=normalize_url(base_url), max_pages=max_pages)
        self.desc_length = desc_length
        self.log = log_callback
        self.state.queue.append(self.state.base_url)

    async def run(self) -> list[PageInfo]:
        pages = []

        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            while self.state.queue and len(self.state.visited) < self.state.max_pages:
                url = self.state.queue.popleft()

                if url in self.state.visited:
                    continue

                try:
                    await self.log(f"Visiting: {url}")
                    response = await client.get(url)
                    response.raise_for_status()

                    soup = BeautifulSoup(response.text, 'html.parser')

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

                    links = extract_links(response.text, url)
                    for link in links:
                        if link not in self.state.visited:
                            self.state.queue.append(link)

                except Exception as e:
                    await self.log(f"Error crawling {url}: {str(e)}")
                    self.state.visited.add(url)

        await self.log(f"Crawl complete: {len(pages)} pages")
        return pages
