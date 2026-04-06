import sys
import time
import json
import re
import spacy
from extractor import get_data
from classifier import classify_page
from ner import apply_NER
from gen_ai_rechecking import validate_and_clean
#from score import calculate_score
from db import get_connection, save_pipeline_run, \
               save_resume, save_score, update_pipeline_run, \
               save_pii_vault
from score import Scorer
nlp = spacy.load("en_core_web_sm")

import json
import mlflow

# At start of run_pipe():
mlflow.set_experiment("ai-recruiter")

# Load rubric at startup
with open("rubric.json", "r") as f:
    rubric = json.load(f)
score_obj=Scorer(rubric)

def extract_name_spacy(resume_data: list) -> str:
    first_page = resume_data[0].get("page_text", "")
    doc = nlp(first_page)

    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text

    # Fallback to first line
    skip = ["resume", "cv", "curriculum vitae"]
    lines = [l.strip() for l in
             first_page.split("\n") if l.strip()]
    for line in lines[:3]:
        if line.lower() not in skip:
            return line

    return "Unknown"


def extract_and_tokenize_pii(text: str) -> tuple[str, list]:
    doc = nlp(text)
    redacted = text
    pii_records = []
    counter = {"PERSON": 0, "EMAIL": 0, "PHONE": 0}

    # spaCy NER for PERSON
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

    # Regex for email
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

    # Regex for phone
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

    # LinkedIn
    redacted = re.sub(
        r'linkedin\.com/in/[^\s]+',
        'LINKEDIN_REDACTED', redacted)

    return redacted, pii_records


def run_pipe(pdf_path: str) -> tuple[float, dict, str]:
    with mlflow.start_run():
    
        conn = get_connection()
        mlflow.log_param("model", "gemma2:2b")
        mlflow.log_param("pdf", pdf_path)
        run_id = save_pipeline_run(conn, total_resumes=1)

        t0 = time.time()
        resume_data = get_data(pdf_path)
        print(f"extract: {time.time()-t0:.2f}s")

        t1 = time.time()
        for page_data in resume_data:
            page_data["page_label"] = classify_page(
                page_data["page_text"])
            page_data["page_ner"] = apply_NER(
                page_data["page_text"],rubric)
        print(f"classify+NER: {time.time()-t1:.2f}s")

        # Extract name BEFORE masking
        real_name = extract_name_spacy(resume_data)
        print(f"Real name extracted: {real_name}")

        # Save resume first to get resume_id
        resume_id = save_resume(
            conn,
            filename=pdf_path.split("/")[-1],
            s3_path=f"s3://ai-recruiter/{pdf_path}",
            page_text=resume_data,
            pipeline_output={}
        )

        # Tokenize PII in each page
        all_pii_records = []
        for page in resume_data:
            redacted_text, records = extract_and_tokenize_pii(
                page["page_text"])
            page["page_text"] = redacted_text
            all_pii_records.extend(records)

        # Save PII vault
        save_pii_vault(conn, resume_id, all_pii_records)
        print(f"PII tokens saved: {len(all_pii_records)}")

        # LLM sees masked text only
        t2 = time.time()
        validated_data = validate_and_clean(resume_data)
        print(f"LLM clean: {time.time()-t2:.2f}s")
        print(f"TOTAL: {time.time()-t0:.2f}s")

        # Restore real name in output
        if validated_data and validated_data.get("ideal_output"):
            validated_data["ideal_output"]["name"] = real_name

        score, justification = score_obj.calculate_score(validated_data)

        save_score(conn, resume_id, run_id,
                score, justification)

        update_pipeline_run(conn, run_id, 1, 0, 'completed')

        conn.close()
        mlflow.log_metric("final_score", score)
        mlflow.log_metric("pipeline_time", time.time() - t0)
        return score, justification, real_name


if __name__ == "__main__":

    score, justification, name = run_pipe(sys.argv[1])
    print(f"\nCandidate: {name}")
    print(f"Score: {score}")
    print(f"Breakdown: {justification}")