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
        page_data["page_ner"] = apply_NER(
            page_data["page_text"])
    print(f"classify+NER: {time.time()-t1:.2f}s")

    t2 = time.time()
    validated_data = validate_and_clean(resume_data)
    print(f"LLM clean: {time.time()-t2:.2f}s")
    print(f"TOTAL: {time.time()-t0:.2f}s")
    candidate_name = validated_data.get("ideal_output", {}).get("name", "Unknown")
    score, justification = calculate_score(
        validated_data, rubric)

    # CHANGE 2: save resume + pipeline output
    resume_id = save_resume(
        conn,
        filename=pdf_path.split("/")[-1],
        s3_path=f"s3://ai-recruiter/{pdf_path}",
        page_text=resume_data,
        pipeline_output=validated_data
    )

    # CHANGE 3: save score
    save_score(conn, resume_id, run_id, 
               score, justification)

    # CHANGE 4: update pipeline run as completed
    update_pipeline_run(conn, run_id, 1, 0, 'completed')

    conn.close()
    return score, justification, candidate_name


if __name__=="__main__":
    run_pipe(sys.argv[1])
    

