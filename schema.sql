-- AI Recruiter Database Schema
-- Created: 2026-03-20

CREATE TABLE recruiters (
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

CREATE TABLE jds (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    recruiter_id UUID NOT NULL REFERENCES recruiters(id),
    title TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'open',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE rubrics (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    jd_id UUID NOT NULL REFERENCES jds(id),
    version_number INTEGER NOT NULL DEFAULT 1,
    config JSONB NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_by UUID NOT NULL REFERENCES recruiters(id),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE resumes (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    jd_id UUID NOT NULL REFERENCES jds(id),
    recruiter_id UUID NOT NULL REFERENCES recruiters(id),
    filename TEXT NOT NULL,
    s3_path TEXT NOT NULL,
    page_text JSONB,
    uploaded_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE pipeline_runs (
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

CREATE TABLE scores (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    resume_id UUID NOT NULL REFERENCES resumes(id),
    rubric_id UUID NOT NULL REFERENCES rubrics(id),
    pipeline_run_id UUID NOT NULL REFERENCES pipeline_runs(id),
    final_score FLOAT,
    breakdown JSONB,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW()
);