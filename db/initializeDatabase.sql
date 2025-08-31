-- Required extensions
CREATE EXTENSION IF NOT EXISTS pgcrypto;  -- for gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS citext;    -- case-insensitive text for domain

-- =========================================
-- Universities (global baseline)
-- =========================================
CREATE TABLE public.universities (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),      -- unique identifier
  name             TEXT NOT NULL,                                   -- university name
  country_code     CHAR(2) NOT NULL,                                -- ISO 3166-1 alpha-2 (e.g., US/GB/AU)
  state_province   TEXT,                                            -- state/province (nullable)
  city             TEXT,                                            -- city (nullable)
  website          TEXT,                                            -- full website URL (e.g., https://www.harvard.edu/)
  domain           CITEXT UNIQUE,                                   -- canonical primary domain (e.g., harvard.edu), nullable unique
  aliases          TEXT[] DEFAULT '{}'::TEXT[],                     -- alternative names/abbreviations
  external_ids     JSONB  DEFAULT '{}'::JSONB,                      -- external IDs (e.g., {"openalex":"...","ror":"...","scorecard":"..."})
  apply_portals    JSONB  DEFAULT '[]'::JSONB,                      -- application portals (e.g., [{"type":"common_app","url":"..."}])
  created_at       TIMESTAMPTZ DEFAULT NOW(),                       -- creation timestamp
  updated_at       TIMESTAMPTZ DEFAULT NOW()                        -- last update timestamp (maintained by trigger below)
);

-- Trigger function to automatically update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to automatically update updated_at on universities table
CREATE TRIGGER update_universities_updated_at 
    BEFORE UPDATE ON public.universities 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

