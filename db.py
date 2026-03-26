import psycopg2
import json
from datetime import datetime

RECRUITER_ID = "d7dee341-b369-4e9f-9606-e1cd3c807642"
JD_ID = "bb015a13-f875-4b95-a4d7-195cf18bd27a"
RUBRIC_ID = "f6d882e4-d52b-4ad1-9c2b-d47474b2612b"
import numpy as np

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.float32):
            return float(obj)
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)
    
def get_connection():
    return psycopg2.connect(
        host="127.0.0.1",
        port=5433,
        database="ai_recruiter",
        user="uma",
        password="password123"
    )

def save_resume(conn, filename, s3_path,
                page_text, pipeline_output):
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO resumes 
            (jd_id, recruiter_id, filename, 
             s3_path, page_text, pipeline_output)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id
    """, (
        JD_ID, RECRUITER_ID, filename,
        s3_path,
        json.dumps(page_text,cls=NumpyEncoder),
        json.dumps(pipeline_output)
    ))
    conn.commit()
    return cur.fetchone()[0]

def save_pipeline_run(conn, total_resumes):
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO pipeline_runs
            (jd_id, rubric_id, rubric_version,
             total_resumes, status, started_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id
    """, (
        JD_ID, RUBRIC_ID, 1,
        total_resumes, 'running', datetime.now()
    ))
    conn.commit()
    return cur.fetchone()[0]

def update_pipeline_run(conn, run_id, 
                        processed, failed, status):
    cur = conn.cursor()
    cur.execute("""
        UPDATE pipeline_runs
        SET processed_resumes = %s,
            failed_resumes = %s,
            status = %s,
            completed_at = %s
        WHERE id = %s
    """, (processed, failed, status, 
          datetime.now(), run_id))
    conn.commit()

def save_score(conn, resume_id,
               pipeline_run_id,
               final_score, breakdown):
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO scores
            (resume_id, rubric_id, pipeline_run_id,
             final_score, breakdown, status)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id
    """, (
        resume_id, RUBRIC_ID, pipeline_run_id,
        final_score,
        json.dumps(breakdown),
        'completed'
    ))
    conn.commit()
    return cur.fetchone()[0]

def save_pii_vault(conn, resume_id, pii_records):
    cur = conn.cursor()
    for record in pii_records:
        cur.execute("""
            INSERT INTO pii_vault
                (resume_id, token, pii_type, real_value)
            VALUES (%s, %s, %s, %s)
        """, (
            resume_id,
            record["token"],
            record["pii_type"],
            record["real_value"]
        ))
    conn.commit()