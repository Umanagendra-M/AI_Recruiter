import sys
import time
import json
from extractor import get_data
from classifier import classify_page
from ner import apply_NER
from gen_ai_rechecking import validate_and_clean
from score import calculate_score
from db import get_connection, save_pipeline_run, \
               save_resume, save_score, update_pipeline_run
rubric = {
    "domain": ["Computer Vision"],
    "preferred_companies": ["Robert Bosch", "Google", "Microsoft"],
    "min_years_of_exp": 3,
    "must_have_skills": ["Python", "Machine Learning", "PyTorch", "NLP"],
    "preferred_skills": ["Docker", "AWS", "LangChain"],
    "minimum_education": "Bachelor",
    "preferred_titles": ["Data Scientist", "ML Engineer", "AI Engineer"]
}
import re
import spacy
nlp = spacy.load("en_core_web_sm")

def extract_and_tokenize_pii(text: str,
                              resume_id: str,
                              conn) -> tuple[str, list]:
    doc = nlp(text)
    redacted = text
    pii_records = []
    counter = {"PERSON": 0, "EMAIL": 0, "PHONE": 0}

    # NER-based entities
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            counter["PERSON"] += 1
            token = f"PII_PERSON_{counter['PERSON']:03d}"
            redacted = redacted.replace(ent.text, token)
            pii_records.append({
                "token": token,
                "pii_type": "PERSON",
                "real_value": ent.text
            })

    # Email
    emails = re.findall(
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        redacted)
    for email in emails:
        counter["EMAIL"] += 1
        token = f"PII_EMAIL_{counter['EMAIL']:03d}"
        redacted = redacted.replace(email, token)
        pii_records.append({
            "token": token,
            "pii_type": "EMAIL",
            "real_value": email
        })

    # Phone
    phones = re.findall(
        r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]',
        redacted)
    for phone in phones:
        counter["PHONE"] += 1
        token = f"PII_PHONE_{counter['PHONE']:03d}"
        redacted = redacted.replace(phone, token)
        pii_records.append({
            "token": token,
            "pii_type": "PHONE",
            "real_value": phone
        })

    return redacted, pii_records


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


def restore_pii(text: str, 
                resume_id: str, 
                conn) -> str:
    cur = conn.cursor()
    cur.execute("""
        SELECT token, real_value 
        FROM pii_vault 
        WHERE resume_id = %s
    """, (resume_id,))
    
    records = cur.fetchall()
    restored = text
    for token, real_value in records:
        restored = restored.replace(token, real_value)
    return restored

def run_pipe(pdf_path: str) -> tuple[float, dict]:
    conn = get_connection()

    # CHANGE 1: create pipeline run at start
    run_id = save_pipeline_run(conn, total_resumes=1)

    t0 = time.time()
    resume_data = get_data(pdf_path)

    print(f"extract: {time.time()-t0:.2f}s")

    t1 = time.time()
    for page_data in resume_data:
        page_data["page_label"] = classify_page(
            page_data["page_text"])
        page_data["page_ner"] = apply_NER(page_data["page_text"])
    print(f"classify+NER: {time.time()-t1:.2f}s")
    t2 = time.time()
    pii_records = []
    resume_id = save_resume(
        conn,
        filename=pdf_path.split("/")[-1],
        s3_path=f"s3://ai-recruiter/{pdf_path}",
        page_text=resume_data,
        pipeline_output={}
    )

    for page in resume_data:
        redacted_text, records = extract_and_tokenize_pii(page["page_text"], resume_id, conn)
        page["page_text"] = redacted_text
        pii_records.extend(records)

    # Save PII vault
    save_pii_vault(conn, resume_id, pii_records)
    validated_data = validate_and_clean(resume_data)
    print(f"LLM clean: {time.time()-t2:.2f}s")
    print(f"TOTAL: {time.time()-t0:.2f}s")
    print("validated_data",validated_data)
    
    real_name = next((r["real_value"] for r in pii_records if r["pii_type"] == "PERSON"), "Unknown")
    score, justification = calculate_score(validated_data, rubric)
    # CHANGE 2: save resume + pipeline output
   
    # CHANGE 3: save score
    save_score(conn, resume_id, run_id, 
               score, justification)

    # CHANGE 4: update pipeline run as completed
    update_pipeline_run(conn, run_id, 1, 0, 'completed')

    conn.close()
    return score, justification, real_name


if __name__=="__main__":
    run_pipe(sys.argv[1])
    

