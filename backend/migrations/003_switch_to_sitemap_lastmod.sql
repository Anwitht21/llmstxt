-- Switch from HTTP ETag/Last-Modified to sitemap lastmod tracking
-- Remove unused HTTP caching fields
ALTER TABLE crawl_sites
  DROP COLUMN IF EXISTS sentinel_etag,
  DROP COLUMN IF EXISTS sentinel_last_modified;

-- Add sitemap lastmod tracking
ALTER TABLE crawl_sites
  ADD COLUMN IF NOT EXISTS sitemap_newest_lastmod TIMESTAMPTZ;

-- No backfill needed - sitemap_newest_lastmod will be populated on next crawl
