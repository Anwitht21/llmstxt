from datetime import datetime, timezone
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
    latest_llms_url: str
) -> bool:
    client = get_supabase_client()
    if not client:
        return False

    try:
        data = {
            "base_url": base_url,
            "recrawl_interval_minutes": recrawl_interval_minutes,
            "max_pages": max_pages,
            "desc_length": desc_length,
            "last_crawled_at": datetime.now(timezone.utc).isoformat(),
            "latest_llms_hash": latest_llms_hash,
            "latest_llms_url": latest_llms_url,
            "updated_at": datetime.now(timezone.utc).isoformat()
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
        result = client.table("crawl_sites").select("*").execute()

        sites = []
        now = datetime.now(timezone.utc)

        for row in result.data:
            last_crawled = None
            if row.get("last_crawled_at"):
                last_crawled = datetime.fromisoformat(row["last_crawled_at"].replace("Z", "+00:00"))

            if last_crawled is None:
                is_due = True
            else:
                minutes_since_crawl = (now - last_crawled).total_seconds() / 60
                is_due = minutes_since_crawl >= row["recrawl_interval_minutes"]

            if is_due:
                sites.append(CrawlSite(
                    id=row["id"],
                    base_url=row["base_url"],
                    recrawl_interval_minutes=row["recrawl_interval_minutes"],
                    max_pages=row["max_pages"],
                    desc_length=row["desc_length"],
                    last_crawled_at=last_crawled,
                    latest_llms_hash=row.get("latest_llms_hash"),
                    latest_llms_url=row.get("latest_llms_url")
                ))

        return sites
    except Exception as e:
        print(f"Error getting due sites: {e}")
        return []

async def update_crawl_result(site_id: str, new_hash: str, hosted_url: str) -> bool:
    client = get_supabase_client()
    if not client:
        return False

    try:
        client.table("crawl_sites").update({
            "last_crawled_at": datetime.now(timezone.utc).isoformat(),
            "latest_llms_hash": new_hash,
            "latest_llms_url": hosted_url,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }).eq("id", site_id).execute()
        return True
    except Exception as e:
        print(f"Error updating crawl result: {e}")
        return False
