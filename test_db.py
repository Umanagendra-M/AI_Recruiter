from db import get_connection, save_pipeline_run, save_resume, save_score

conn = get_connection()

# Step 1: create a pipeline run
run_id = save_pipeline_run(conn, total_resumes=1)
print(f"Pipeline run created: {run_id}")

# Step 2: save a fake resume
resume_id = save_resume(
    conn,
    filename="test_resume.pdf",
    s3_path="s3://ai-recruiter/test_resume.pdf",
    page_text={"pages": [{"page_num": 1, "text": "John Smith ML Engineer"}]},
    pipeline_output={"test": "output"}
)
print(f"Resume saved: {resume_id}")

# Step 3: save a fake score
score_id = save_score(
    conn,
    resume_id=resume_id,
    pipeline_run_id=run_id,
    final_score=0.85,
    breakdown={"domain": 0.3, "skills": 0.25}
)
print(f"Score saved: {score_id}")

conn.close()
print("All done!")