import sys
import time
import json
from extractor import get_data
from classifier import classify_page
from ner import apply_NER
from gen_ai_rechecking import validate_and_clean
from score import calculate_score
rubric={
    "domain":["finance","Computer Vision"],
    "preferred_companies":["Robert Bosch","Goldman","Citi"],
    "min_years_of_exp":2,
    "must_have_skills":['Data Science', 'Machine Learning', 'Generative AI', 'Computer Vision', 'NLP', 'CV', 'LLMs', 'Fine-Tuning LLMs', 'Image Processing', 'Object Detection', 'GANs', 'Signal Processing', 'Time Series Analysis', 'Statistical Modeling', 'Model Building & Deployment', 'Hypothesis Testing', 'Data Mining', 'Data Analytics', 'Python', 'SQL', 'HTML', 'CSS', 'Web Development', 'Pandas', 'Spacy', 'NLTK', 'OpenCV', 'Matplotlib/Seaborn', 'Scikit-learn', 'TensorFlow', 'Pytorch', 'Keras', 'Langchain', 'Chainglit', 'Google Data Studio', 'Jupyter Notebooks', 'Docker', 'Git', 'Github', 'Google Search API', 'Education', "Bachelor's Degree in Computer Science with 78.3% marks.", 'Certifications & Courses', 'IBM Professional Data Scientist Certificate', 'Advanced Deep Learning Course (Ineuron)', 'Python & Web Development', 'Soft Skills: Analytical Thinking, Problem Solving, Collaboration, Communication, Continuous Learning, Adaptability, Time Management, and Teamwork.'],
    "preferred_skills":["A/B testing","Statistics"],
    "minimum_education":"Bachelors",
    "preferred_titles":["Data Scientist / ML Engineer / AI Engineer"]
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