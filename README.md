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