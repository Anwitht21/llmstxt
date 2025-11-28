from datetime import datetime, timezone, timedelta
from dataclasses import dataclass
from supabase import create_client, Client
from config import settings

@dataclass
class CrawlSite:
    id: str
    base_url: str
    recrawl_interval_minutes: int
    max_pages: int
    desc_length: int
    last_crawled_at: datetime | None
    latest_llms_hash: str | None
    latest_llms_url: str | None
    next_crawl_at: datetime | None
    last_changed_at: datetime | None
    sentinel_url: str | None
    sitemap_newest_lastmod: datetime | None
    avg_change_interval_minutes: float | None
    webhook_secret: str | None

def get_supabase_client() -> Client | None:
    if not settings.supabase_url or not settings.supabase_key:
        return None
    return create_client(settings.supabase_url, settings.supabase_key)

async def save_site_metadata(
    base_url: str,
    recrawl_interval_minutes: int,
    max_pages: int,
    desc_length: int,
    latest_llms_hash: str,
    latest_llms_url: str,
    sentinel_url: str | None = None
) -> bool:
    client = get_supabase_client()
    if not client:
        return False

    try:
        now = datetime.now(timezone.utc)
        data = {
            "base_url": base_url,
            "recrawl_interval_minutes": recrawl_interval_minutes,
            "max_pages": max_pages,
            "desc_length": desc_length,
            "last_crawled_at": now.isoformat(),
            "last_changed_at": now.isoformat(),
            "next_crawl_at": (now + timedelta(minutes=recrawl_interval_minutes)).isoformat(),
            "sentinel_url": sentinel_url or base_url,
            "avg_change_interval_minutes": float(recrawl_interval_minutes),
            "latest_llms_hash": latest_llms_hash,
            "latest_llms_url": latest_llms_url,
            "updated_at": now.isoformat()
        }

        client.table("crawl_sites").upsert(data, on_conflict="base_url").execute()
        return True
    except Exception as e:
        print(f"Error saving site metadata: {e}")
        return False

async def get_due_sites() -> list[CrawlSite]:
    client = get_supabase_client()
    if not client:
        return []

    try:
        now = datetime.now(timezone.utc)
        result = client.table("crawl_sites") \
            .select("*") \
            .lte("next_crawl_at", now.isoformat()) \
            .execute()

        sites = []
        for row in result.data:
            def parse_datetime(value):
                if value is None:
                    return None
                return datetime.fromisoformat(value.replace("Z", "+00:00"))

            sites.append(CrawlSite(
                id=row["id"],
                base_url=row["base_url"],
                recrawl_interval_minutes=row["recrawl_interval_minutes"],
                max_pages=row["max_pages"],
                desc_length=row["desc_length"],
                last_crawled_at=parse_datetime(row.get("last_crawled_at")),
                latest_llms_hash=row.get("latest_llms_hash"),
                latest_llms_url=row.get("latest_llms_url"),
                next_crawl_at=parse_datetime(row.get("next_crawl_at")),
                last_changed_at=parse_datetime(row.get("last_changed_at")),
                sentinel_url=row.get("sentinel_url"),
                sitemap_newest_lastmod=parse_datetime(row.get("sitemap_newest_lastmod")),
                avg_change_interval_minutes=row.get("avg_change_interval_minutes"),
                webhook_secret=row.get("webhook_secret")
            ))

        return sites
    except Exception as e:
        print(f"Error getting due sites: {e}")
        return []

async def update_scheduling_only(
    site_id: str,
    next_crawl_at: datetime,
    sitemap_newest_lastmod: datetime | None
) -> bool:
    client = get_supabase_client()
    if not client:
        return False

    try:
        now = datetime.now(timezone.utc)
        update_data = {
            "last_crawled_at": now.isoformat(),
            "next_crawl_at": next_crawl_at.isoformat(),
            "updated_at": now.isoformat()
        }

        if sitemap_newest_lastmod:
            update_data["sitemap_newest_lastmod"] = sitemap_newest_lastmod.isoformat()

        client.table("crawl_sites").update(update_data).eq("id", site_id).execute()
        return True
    except Exception as e:
        print(f"Error updating scheduling: {e}")
        return False

async def update_crawl_result(
    site_id: str,
    new_hash: str,
    hosted_url: str,
    next_crawl_at: datetime,
    last_changed_at: datetime | None,
    sitemap_newest_lastmod: datetime | None,
    avg_change_interval_minutes: float | None
) -> bool:
    client = get_supabase_client()
    if not client:
        return False

    try:
        now = datetime.now(timezone.utc)
        update_data = {
            "last_crawled_at": now.isoformat(),
            "next_crawl_at": next_crawl_at.isoformat(),
            "last_changed_at": last_changed_at.isoformat() if last_changed_at else None,
            "avg_change_interval_minutes": avg_change_interval_minutes,
            "latest_llms_hash": new_hash,
            "latest_llms_url": hosted_url,
            "updated_at": now.isoformat()
        }

        if sitemap_newest_lastmod:
            update_data["sitemap_newest_lastmod"] = sitemap_newest_lastmod.isoformat()

        client.table("crawl_sites").update(update_data).eq("id", site_id).execute()
        return True
    except Exception as e:
        print(f"Error updating crawl result: {e}")
        return False
