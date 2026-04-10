planned architecture

PDF Upload
    |
Extraction (pdfplumber)
    |
Page Classification (bart-large-mnli)
    |
NER + EntityRuler (BERT + spaCy)
    |
PII Tokenization (spaCy + regex)
    |
LLM Extraction (Gemma2:2b via Ollama)
    |
Scorer (rubric-based weighted scoring)
    |
PostgreSQL + MinIO + MLflow
    |
FastAPI REST API(user view the data)

API endpoints
GET  /health   - system status
POST /upload   - upload PDF to MinIO
POST /score    - score single resume
POST /batch    - score ZIP of resumes

tech stack
API Framework   FastAPI + Pydantic
Page Classifier facebook/bart-large-mnli
NER Model       yashpwr/resume-ner-bert-v2
PII Detection   spaCy en_core_web_sm + regex
LLM             Gemma2:2b via Ollama
Database        PostgreSQL with JSONB
File Storage    MinIO (S3 compatible)
Experiment      MLflow
CI/CD           GitHub Actions
Cloud           AWS EC2, AWS EKS
Containers      Docker + Docker Compose

run local commands:

git clone https://github.com/Umanagendra-M/AI_Recruiter
cd AI_Recruiter
docker compose up -d


testing
curl http://localhost:8000/health
curl -X POST http://localhost:8000/score -F "file=@data/resume.pdf"

Project Phases
Phase 1 - Foundation
Built the core pipeline locally. PDF extraction, page classification, NER with EntityRuler for known skills, LLM-based structured extraction using Gemma2, and rubric-based scoring. Verified end to end on test resumes.
Phase 2 - Production Pipeline
Refactored into Pipeline and Scorer classes so models load once at startup. Added PII tokenization vault using spaCy NER and regex, mapping tokens to real values in PostgreSQL. Built FastAPI with four endpoints, MinIO file storage, MLflow experiment tracking, and batch processing for ZIP uploads. Dockerized all services with healthchecks and auto-seeding on first startup. Deployed on AWS EC2.
Phase 3 - DevOps (In Progress)
Added GitHub Actions CI/CD pipeline. Tests run on every push, deployment triggers on merge to main with health check verification. Remaining work includes ECS Fargate for managed container orchestration, CloudWatch monitoring, pgvector for resume similarity search, Celery workers for concurrent processing, and a Streamlit UI for non-technical recruiters.

Database Schema
Seven tables: recruiters, jds, rubrics, resumes, pipeline_runs, scores, pii_vault. Resumes store extracted page text and pipeline output as JSONB. PII vault maps tokens back to real values by resume ID for audit retrieval.

Known Issues
PII masking occasionally over-redacts context that the LLM needs for accurate extraction, which can result in lower scores. This is being addressed in Phase 3 with more targeted masking logic.