from fastapi import FastAPI, UploadFile, File
from fastapi import HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager
import os
import uuid
from run_pipeline import run_pipe
from batch_process import batch_process
from minio_storage import upload_file, download_to_temp, ensure_bucket, delete_file

# ─── Lifespan (replaces on_event startup) ──
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs on startup
    ensure_bucket()
    print("Storage bucket ready")
    yield
    # Runs on shutdown (cleanup if needed)

app = FastAPI(
    title="AI Recruiter API",
    version="1.0.0",
    lifespan=lifespan
)

# ─── Response Models ────────────────────────
class ScoreResponse(BaseModel):
    candidate_name: str
    final_score: float
    breakdown: dict
    status: str

class HealthResponse(BaseModel):
    status: str
    version: str

class BatchResponse(BaseModel):
    job_id: str
    status: str
    message: str

class UploadResponse(BaseModel):
    filename: str
    s3_path: str
    size: int
    status: str

# ─── Health ─────────────────────────────────
@app.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(
        status="ok",
        version="1.0.0"
    )

# ─── Upload Only ─────────────────────────────
# Just stores the file, no processing
@app.post("/upload", response_model=UploadResponse)
async def upload_resume(
        file: UploadFile = File(...)):

    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files accepted"
        )

    content = await file.read()

    # Give it a unique name to avoid conflicts
    unique_name = f"{uuid.uuid4()}_{file.filename}"

    # Upload to MinIO/S3
    s3_path = upload_file(content, unique_name)

    return UploadResponse(
        filename=file.filename,
        s3_path=s3_path,
        size=len(content),
        status="uploaded"
    )

# ─── Score Single Resume ─────────────────────
@app.post("/score", response_model=ScoreResponse)
async def score_resume(
        file: UploadFile = File(...)):

    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files accepted"
        )

    content = await file.read()
    unique_name = f"{uuid.uuid4()}_{file.filename}"
    local_path = None

    try:
        # Step 1: Upload to MinIO
        s3_path = upload_file(content, unique_name)

        # Step 2: Download to temp for pipeline
        # Pipeline needs local file path
        local_path = download_to_temp(s3_path)

        # Step 3: Run pipeline
        score, justification, candidate_name = \
            run_pipe(local_path)

        return ScoreResponse(
            candidate_name=candidate_name,
            final_score=round(float(score), 3),
            breakdown=justification,
            status="completed"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Pipeline failed: {str(e)}"
        )
    finally:
        # Clean up local temp file
        if local_path and os.path.exists(local_path):
            os.unlink(local_path)
        # Note: keep file in MinIO for audit trail

# ─── Batch Score ─────────────────────────────
@app.post("/batch", response_model=BatchResponse)
async def batch_score(
        file: UploadFile = File(...)):

    if not file.filename.endswith(".zip"):
        raise HTTPException(
            status_code=400,
            detail="Only ZIP files accepted"
        )

    content = await file.read()
    unique_name = f"{uuid.uuid4()}_{file.filename}"
    local_path = None

    try:
        # Upload ZIP to MinIO
        s3_path = upload_file(content, unique_name)

        # Download to local for processing
        local_path = download_to_temp(s3_path)

        # Output CSV
        output_path = local_path.replace(
            ".zip", "_results.csv")

        # Run batch
        results = batch_process(
            local_path, output_path)

        job_id = unique_name.split("_")[0]

        return BatchResponse(
            job_id=job_id,
            status="completed",
            message=f"Processed {len(results)} resumes"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Batch failed: {str(e)}"
        )
    finally:
        if local_path and os.path.exists(local_path):
            os.unlink(local_path)

# ─── Job Status ──────────────────────────────
@app.get("/job/{job_id}")
def get_job(job_id: str):
    # Phase 3: query PostgreSQL for real status
    return {
        "job_id": job_id,
        "status": "completed"
    }