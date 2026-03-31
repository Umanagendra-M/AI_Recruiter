from transformers import pipeline
from typing import List

# Known skills that NER often misses
KNOWN_SKILLS = [
    "python", "pytorch", "tensorflow",
    "sklearn", "scikit-learn", "spacy",
    "docker", "kubernetes", "k8s",
    "fastapi", "langchain", "sql",
    "git", "aws", "gcp", "azure",
    "numpy", "pandas", "huggingface",
    "transformers", "bert", "llm",
    "rag", "mlflow", "pydantic",
    "postgresql", "mongodb", "redis"
]

def apply_entity_ruler(page_text: str,
                       existing_entities: list,rubric:dict) -> list:
    already_found = set(
        e["word"].lower() 
        for e in existing_entities
    )
    
    text_lower = page_text.lower()
    new_entities = []
    
    for skill in KNOWN_SKILLS:
        if skill in text_lower and \
           skill not in already_found:
            new_entities.append({
                "entity_group": "SKILL",
                "word": skill,
                "score": 1.0,
                "start": text_lower.find(skill),
                "end": text_lower.find(skill) + len(skill)
            })
    
    return existing_entities + new_entities


def apply_NER(page_text: str,rubric:dict) -> List[dict]:
    ner_pipeline = pipeline(
        "token-classification",
        model="yashpwr/resume-ner-bert-v2",
        aggregation_strategy="simple")
    
    results = ner_pipeline(page_text)
    
    # Add known skills EntityRuler misses
    results = apply_entity_ruler(page_text, results,rubric)
    
    return results