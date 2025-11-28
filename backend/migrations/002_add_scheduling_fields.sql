-- Add scheduling and change detection fields to crawl_sites table
ALTER TABLE crawl_sites
  ADD COLUMN next_crawl_at TIMESTAMPTZ,
  ADD COLUMN last_changed_at TIMESTAMPTZ,
  ADD COLUMN sentinel_url TEXT,
  ADD COLUMN sentinel_etag TEXT,
  ADD COLUMN sentinel_last_modified TEXT,
  ADD COLUMN avg_change_interval_minutes REAL,
  ADD COLUMN webhook_secret TEXT;

-- Update index for efficient next_crawl_at queries
DROP INDEX IF EXISTS idx_crawl_sites_due;
CREATE INDEX idx_crawl_sites_next_crawl ON crawl_sites(next_crawl_at)
  WHERE next_crawl_at IS NOT NULL;

-- Backfill existing rows with initial values
UPDATE crawl_sites
SET
  next_crawl_at = last_crawled_at + (recrawl_interval_minutes || ' minutes')::INTERVAL,
  last_changed_at = COALESCE(last_crawled_at, created_at),
  sentinel_url = base_url,
  avg_change_interval_minutes = recrawl_interval_minutes
WHERE next_crawl_at IS NULL;
