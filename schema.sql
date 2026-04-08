-- AI Recruiter Database Schema
-- Created: 2026-03-20

CREATE TABLE IF NOT EXISTS recruiters (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    designation TEXT,
    company TEXT,
    department TEXT,
    username TEXT UNIQUE,
    password_hash TEXT NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS jds (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    recruiter_id UUID NOT NULL REFERENCES recruiters(id),
    title TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'open',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS rubrics (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    jd_id UUID NOT NULL REFERENCES jds(id),
    version_number INTEGER NOT NULL DEFAULT 1,
    config JSONB NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_by UUID NOT NULL REFERENCES recruiters(id),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS resumes (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    jd_id UUID NOT NULL REFERENCES jds(id),
    recruiter_id UUID NOT NULL REFERENCES recruiters(id),
    filename TEXT NOT NULL,
    s3_path TEXT NOT NULL,
    page_text JSONB,
    uploaded_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS pipeline_runs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    jd_id UUID NOT NULL REFERENCES jds(id),
    rubric_id UUID NOT NULL REFERENCES rubrics(id),
    rubric_version INTEGER NOT NULL,
    total_resumes INTEGER DEFAULT 0,
    processed_resumes INTEGER DEFAULT 0,
    failed_resumes INTEGER DEFAULT 0,
    status TEXT DEFAULT 'pending',
    message TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS scores (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    resume_id UUID NOT NULL REFERENCES resumes(id),
    rubric_id UUID NOT NULL REFERENCES rubrics(id),
    pipeline_run_id UUID NOT NULL REFERENCES pipeline_runs(id),
    final_score FLOAT,
    breakdown JSONB,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS resumes (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    jd_id UUID NOT NULL REFERENCES jds(id),
    recruiter_id UUID NOT NULL REFERENCES recruiters(id),
    filename TEXT NOT NULL,
    s3_path TEXT NOT NULL,
    page_text JSONB,
    pipeline_output JSONB,    -- ADD THIS LINE
    uploaded_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS pii_vault (id UUID DEFAULT gen_random_uuid() PRIMARY KEY, 
                                    resume_id UUID NOT NULL REFERENCES resumes(id), 
                                    token TEXT NOT NULL, 
                                    pii_type TEXT NOT NULL, 
                                    real_value TEXT NOT NULL,
                                     created_at TIMESTAMP DEFAULT NOW());

INSERT INTO recruiters (id, name, email, designation, company, username, password_hash)
VALUES (
    'd7dee341-b369-4e9f-9606-e1cd3c807642',
    'Sarah Johnson',
    'sarah@recruiter.com',
    'Senior Recruiter',
    'TechCorp',
    'sarah',
    'placeholder_hash'
) ON CONFLICT (id) DO NOTHING;

INSERT INTO jds (id, recruiter_id, title, description, status)
VALUES (
    'bb015a13-f875-4b95-a4d7-195cf18bd27a',
    'd7dee341-b369-4e9f-9606-e1cd3c807642',
    'ML Engineer - Computer Vision',
    'Looking for ML Engineer with Python, PyTorch, NLP experience',
    'open'
) ON CONFLICT (id) DO NOTHING;

INSERT INTO rubrics (id, jd_id, version_number, config, is_active, created_by)
VALUES (
    'f6d882e4-d52b-4ad1-9c2b-d47474b2612b',
    'bb015a13-f875-4b95-a4d7-195cf18bd27a',
    1,
    '{"domain": ["Computer Vision"], "preferred_companies": ["Robert Bosch", "Google", "Microsoft"], "min_years_of_exp": 3, "must_have_skills": ["Python", "Machine Learning", "PyTorch", "NLP"], "preferred_skills": ["Docker", "AWS", "LangChain"], "minimum_education": "Bachelor", "preferred_titles": ["Data Scientist", "ML Engineer", "AI Engineer"]}',
    true,
    'd7dee341-b369-4e9f-9606-e1cd3c807642'
) ON CONFLICT (id) DO NOTHING;