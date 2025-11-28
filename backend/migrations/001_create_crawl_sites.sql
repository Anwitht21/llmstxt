-- Create crawl_sites table for automated recrawling
-- Run this SQL in your Supabase SQL Editor

CREATE TABLE IF NOT EXISTS crawl_sites (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  base_url TEXT UNIQUE NOT NULL,
  recrawl_interval_minutes INTEGER NOT NULL,
  max_pages INTEGER NOT NULL DEFAULT 50,
  desc_length INTEGER NOT NULL DEFAULT 500,
  last_crawled_at TIMESTAMPTZ,
  latest_llms_hash TEXT,
  latest_llms_url TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index for efficient querying of sites due for recrawl
CREATE INDEX IF NOT EXISTS idx_crawl_sites_due
  ON crawl_sites(last_crawled_at, recrawl_interval_minutes);

-- Add comments for documentation
COMMENT ON TABLE crawl_sites IS 'Stores metadata for sites enrolled in automated llms.txt updates';
COMMENT ON COLUMN crawl_sites.base_url IS 'The base URL of the crawled site (unique identifier)';
COMMENT ON COLUMN crawl_sites.recrawl_interval_minutes IS 'How often to recrawl this site (in minutes)';
COMMENT ON COLUMN crawl_sites.max_pages IS 'Maximum number of pages to crawl per scan';
COMMENT ON COLUMN crawl_sites.desc_length IS 'Maximum length of page descriptions/snippets';
COMMENT ON COLUMN crawl_sites.last_crawled_at IS 'Timestamp of the last successful crawl';
COMMENT ON COLUMN crawl_sites.latest_llms_hash IS 'SHA-256 hash of the latest generated llms.txt content';
COMMENT ON COLUMN crawl_sites.latest_llms_url IS 'URL where the latest llms.txt is hosted';
