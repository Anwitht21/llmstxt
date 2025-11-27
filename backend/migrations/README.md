# Database Migrations

This directory contains SQL migration files for the llms.txt automated recrawling system.

## Running Migrations

### Supabase Setup

1. Log in to your [Supabase Dashboard](https://app.supabase.com/)
2. Select your project
3. Navigate to the **SQL Editor** in the left sidebar
4. Create a new query
5. Copy and paste the contents of `001_create_crawl_sites.sql`
6. Click **Run** to execute the migration

### Verification

After running the migration, verify the table was created:

```sql
SELECT * FROM crawl_sites LIMIT 1;
```

You should see an empty result set with the following columns:
- id
- base_url
- recrawl_interval_minutes
- max_pages
- desc_length
- last_crawled_at
- latest_llms_hash
- latest_llms_url
- created_at
- updated_at

## Migration Files

- **001_create_crawl_sites.sql** - Creates the `crawl_sites` table and indexes for storing site metadata and tracking recrawl schedules
