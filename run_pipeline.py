import sys
import time
import json
from extractor import get_data
from classifier import classify_page
from ner import apply_NER
from gen_ai_rechecking import validate_and_clean
from score import calculate_score
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
    
    t0 = time.time()
    resume_data = get_data(pdf_path)
    print(f"extract:  {time.time()-t0:.2f}s")

    t1 = time.time()
    for page_data in resume_data:
        page_data["page_label"] = classify_page(page_data["page_text"])
        page_data["page_ner"] = apply_NER(page_data["page_text"])
    print(f"classify+NER: {time.time()-t1:.2f}s")

    t2 = time.time()
    validated_data = validate_and_clean(resume_data)
    print(f"LLM clean: {time.time()-t2:.2f}s")

    print(f"TOTAL:     {time.time()-t0:.2f}s")
    score,justification=calculate_score(validated_data,rubric)
    return score,justification

if __name__ == "__main__":
    final_score,justification = run_pipe(sys.argv[1])
    with open("final_result.txt", "w") as f:
        f.write(json.dumps({"final_score":final_score,"justification":justification}))