from datetime import datetime, timedelta, timezone

MIN_INTERVAL_MINUTES = 60        # 1 hour minimum
MAX_INTERVAL_MINUTES = 10080     # 7 days maximum
EWMA_ALPHA = 0.5                 # Moderate adaptation rate

def compute_next_crawl(
    site_recrawl_interval: int,
    avg_change_interval: float | None,
    content_changed: bool,
    last_changed_at: datetime | None,
    now: datetime,
    adaptive_enabled: bool = False
) -> tuple[datetime, float | None, datetime | None]:
    if not adaptive_enabled:
        interval_minutes = site_recrawl_interval
        return (
            now + timedelta(minutes=interval_minutes),
            avg_change_interval,
            last_changed_at if not content_changed else now
        )

    if avg_change_interval is None:
        avg_change_interval = float(site_recrawl_interval)

    if content_changed and last_changed_at:
        minutes_since_change = (now - last_changed_at).total_seconds() / 60
        avg_change_interval = (
            EWMA_ALPHA * minutes_since_change +
            (1 - EWMA_ALPHA) * avg_change_interval
        )

    effective_interval = max(
        MIN_INTERVAL_MINUTES,
        min(MAX_INTERVAL_MINUTES, avg_change_interval)
    )

    return (
        now + timedelta(minutes=effective_interval),
        avg_change_interval,
        now if content_changed else last_changed_at
    )
