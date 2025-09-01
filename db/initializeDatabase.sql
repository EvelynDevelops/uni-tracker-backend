-- Required extensions
CREATE EXTENSION IF NOT EXISTS pgcrypto;  -- for gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS citext;    -- case-insensitive text for domain
CREATE EXTENSION IF NOT EXISTS pg_trgm;


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

CREATE INDEX IF NOT EXISTS idx_universities_country_code ON public.universities(country_code);
CREATE INDEX IF NOT EXISTS idx_universities_created_at ON public.universities(created_at);
CREATE INDEX IF NOT EXISTS gin_universities_name_trgm ON public.universities USING gin (name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_universities_domain ON public.universities(domain);


-- ========= Enums =========
CREATE TYPE role_type AS ENUM ('student','parent','teacher');
CREATE TYPE application_status AS ENUM (
  'NOT_STARTED','IN_PROGRESS','SUBMITTED','UNDER_REVIEW',
  'ACCEPTED','WAITLISTED','REJECTED'
);
CREATE TYPE application_type AS ENUM ('Early_Decision','Early_Action','Regular_Decision','Rolling_Admission');
CREATE TYPE requirement_status AS ENUM ('not_started','in_progress','completed');

-- ========= Profiles (no longer reference auth.users)=========
CREATE TABLE profiles (
  -- directly store Supabase Auth's user.id (JWT's sub)
  user_id    UUID PRIMARY KEY,
  role       role_type NOT NULL,
  first_name VARCHAR(255),
  last_name  VARCHAR(255),
  email      VARCHAR(255) UNIQUE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ========= Student profile =========
CREATE TABLE student_profile (
  user_id          UUID PRIMARY KEY REFERENCES profiles(user_id) ON DELETE CASCADE,
  graduation_year  INTEGER,
  gpa              DECIMAL(3,2),
  sat_score        INTEGER,
  act_score        INTEGER,
  target_countries TEXT[],
  intended_majors  TEXT[]
);

-- ========= Parent ↔ Student =========
CREATE TABLE parent_links (
  parent_user_id  UUID NOT NULL REFERENCES profiles(user_id) ON DELETE CASCADE,
  student_user_id UUID NOT NULL REFERENCES profiles(user_id) ON DELETE CASCADE,
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  PRIMARY KEY (parent_user_id, student_user_id),
  CONSTRAINT chk_parent_student_not_same CHECK (parent_user_id <> student_user_id)
);
CREATE INDEX idx_parent_links_parent  ON parent_links(parent_user_id);
CREATE INDEX idx_parent_links_student ON parent_links(student_user_id);

-- Role check (parent must be parent; student must be student)
CREATE OR REPLACE FUNCTION ensure_parent_student_roles()
RETURNS TRIGGER AS $fn$
DECLARE
  parent_ok  BOOLEAN;
  student_ok BOOLEAN;
BEGIN
  SELECT EXISTS (
    SELECT 1 FROM profiles p WHERE p.user_id = NEW.parent_user_id AND p.role = 'parent'
  ) INTO parent_ok;
  IF NOT parent_ok THEN
    RAISE EXCEPTION 'parent_user_id % must be role=parent', NEW.parent_user_id
      USING ERRCODE = 'check_violation';
  END IF;

  SELECT EXISTS (
    SELECT 1 FROM profiles p WHERE p.user_id = NEW.student_user_id AND p.role = 'student'
  ) INTO student_ok;
  IF NOT student_ok THEN
    RAISE EXCEPTION 'student_user_id % must be role=student', NEW.student_user_id
      USING ERRCODE = 'check_violation';
  END IF;

  RETURN NEW;
END;
$fn$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_parent_student_roles ON parent_links;
CREATE TRIGGER trg_parent_student_roles
  BEFORE INSERT OR UPDATE ON parent_links
  FOR EACH ROW
  EXECUTE FUNCTION ensure_parent_student_roles();

-- ========= Teacher profile =========
CREATE TABLE teacher_profile (
  user_id       UUID PRIMARY KEY REFERENCES profiles(user_id) ON DELETE CASCADE,
  subjects      TEXT[],
  organization  TEXT,
  timezone      TEXT,
  bio           TEXT,
  max_advisees  INTEGER DEFAULT 50,
  created_at    TIMESTAMPTZ DEFAULT NOW()
);

-- ========= Teacher ↔ Student =========
CREATE TABLE teacher_student_links (
  teacher_user_id UUID NOT NULL REFERENCES profiles(user_id) ON DELETE CASCADE,
  student_user_id UUID NOT NULL REFERENCES profiles(user_id) ON DELETE CASCADE,
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  PRIMARY KEY (teacher_user_id, student_user_id),
  CONSTRAINT chk_teacher_student_not_same CHECK (teacher_user_id <> student_user_id)
);
CREATE INDEX idx_tsl_teacher ON teacher_student_links(teacher_user_id);
CREATE INDEX idx_tsl_student ON teacher_student_links(student_user_id);

CREATE OR REPLACE FUNCTION ensure_teacher_student_roles()
RETURNS TRIGGER AS $fn$
DECLARE
  teacher_ok BOOLEAN;
  student_ok BOOLEAN;
BEGIN
  SELECT EXISTS (
    SELECT 1 FROM profiles p WHERE p.user_id = NEW.teacher_user_id AND p.role = 'teacher'
  ) INTO teacher_ok;
  IF NOT teacher_ok THEN
    RAISE EXCEPTION 'teacher_user_id % must be role=teacher', NEW.teacher_user_id
      USING ERRCODE = 'check_violation';
  END IF;

  SELECT EXISTS (
    SELECT 1 FROM profiles p WHERE p.user_id = NEW.student_user_id AND p.role = 'student'
  ) INTO student_ok;
  IF NOT student_ok THEN
    RAISE EXCEPTION 'student_user_id % must be role=student', NEW.student_user_id
      USING ERRCODE = 'check_violation';
  END IF;

  RETURN NEW;
END;
$fn$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_teacher_student_roles ON teacher_student_links;
CREATE TRIGGER trg_teacher_student_roles
  BEFORE INSERT OR UPDATE ON teacher_student_links
  FOR EACH ROW
  EXECUTE FUNCTION ensure_teacher_student_roles();
