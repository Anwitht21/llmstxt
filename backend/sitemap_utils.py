import httpx
import xml.etree.ElementTree as ET
from datetime import datetime
from dataclasses import dataclass

@dataclass
class SitemapPage:
    url: str
    lastmod: datetime | None
    changefreq: str | None
    priority: float | None

@dataclass
class SitemapInfo:
    pages: list[SitemapPage]
    newest_lastmod: datetime | None
    total_pages: int

async def parse_sitemap(sitemap_url: str, timeout: float = 10.0) -> SitemapInfo | None:
    try:
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            response = await client.get(sitemap_url)

            if response.status_code != 200:
                print(f"Failed to fetch sitemap: {response.status_code}")
                return None

            root = ET.fromstring(response.content)

            ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

            sitemaps = root.findall('ns:sitemap', ns)
            if sitemaps:
                return await _parse_sitemap_index(root, ns, timeout)
            else:
                return _parse_regular_sitemap(root, ns)

    except Exception as e:
        print(f"Error parsing sitemap {sitemap_url}: {e}")
        return None

async def _parse_sitemap_index(root: ET.Element, ns: dict, timeout: float) -> SitemapInfo:
    all_pages = []
    newest_lastmod = None

    sitemaps = root.findall('ns:sitemap', ns)

    for sitemap_elem in sitemaps:
        loc_elem = sitemap_elem.find('ns:loc', ns)
        if loc_elem is None or not loc_elem.text:
            continue

        sitemap_url = loc_elem.text.strip()

        sitemap_info = await parse_sitemap(sitemap_url, timeout)
        if sitemap_info:
            all_pages.extend(sitemap_info.pages)

            if sitemap_info.newest_lastmod:
                if newest_lastmod is None or sitemap_info.newest_lastmod > newest_lastmod:
                    newest_lastmod = sitemap_info.newest_lastmod

    return SitemapInfo(
        pages=all_pages,
        newest_lastmod=newest_lastmod,
        total_pages=len(all_pages)
    )

def _parse_regular_sitemap(root: ET.Element, ns: dict) -> SitemapInfo:
    pages = []
    newest_lastmod = None

    urls = root.findall('ns:url', ns)

    for url_elem in urls:
        loc_elem = url_elem.find('ns:loc', ns)
        if loc_elem is None or not loc_elem.text:
            continue

        url = loc_elem.text.strip()

        lastmod = None
        lastmod_elem = url_elem.find('ns:lastmod', ns)
        if lastmod_elem is not None and lastmod_elem.text:
            lastmod = _parse_lastmod(lastmod_elem.text.strip())

            if lastmod:
                if newest_lastmod is None or lastmod > newest_lastmod:
                    newest_lastmod = lastmod

        changefreq = None
        changefreq_elem = url_elem.find('ns:changefreq', ns)
        if changefreq_elem is not None and changefreq_elem.text:
            changefreq = changefreq_elem.text.strip()

        priority = None
        priority_elem = url_elem.find('ns:priority', ns)
        if priority_elem is not None and priority_elem.text:
            try:
                priority = float(priority_elem.text.strip())
            except ValueError:
                pass

        pages.append(SitemapPage(
            url=url,
            lastmod=lastmod,
            changefreq=changefreq,
            priority=priority
        ))

    return SitemapInfo(
        pages=pages,
        newest_lastmod=newest_lastmod,
        total_pages=len(pages)
    )

def _parse_lastmod(lastmod_str: str) -> datetime | None:
    try:
        if 'T' in lastmod_str:
            if lastmod_str.endswith('Z'):
                lastmod_str = lastmod_str[:-1] + '+00:00'
            return datetime.fromisoformat(lastmod_str)
        else:
            return datetime.strptime(lastmod_str, '%Y-%m-%d').replace(tzinfo=None)
    except Exception as e:
        print(f"Failed to parse lastmod '{lastmod_str}': {e}")
        return None

async def has_sitemap_changed(sitemap_url: str, last_check_time: datetime | None) -> tuple[bool, datetime | None]:
    sitemap_info = await parse_sitemap(sitemap_url)

    if not sitemap_info:
        return (True, None)

    if not sitemap_info.newest_lastmod:
        return (True, None)

    if not last_check_time:
        return (True, sitemap_info.newest_lastmod)

    newest = sitemap_info.newest_lastmod
    last_check = last_check_time

    if newest.tzinfo:
        newest = newest.replace(tzinfo=None)
    if last_check.tzinfo:
        last_check = last_check.replace(tzinfo=None)

    has_changed = newest > last_check

    return (has_changed, sitemap_info.newest_lastmod)
