from transformers import pipeline
from typing import List
def apply_NER(page_text:str)->List[dict]:
    ner_pipeline = pipeline("token-classification",
                            model="yashpwr/resume-ner-bert-v2",
                            aggregation_strategy="simple")
    #labels = ["Name", "skill", "date", "competitions", "company","work domain","job title","years of experince","Resume section"]
    results=ner_pipeline(page_text)
    return results


# with open(r'C:\Users\umall\Documents\Interview_Readiness\AI_recruiter\page_data\page1.txt','r',encoding='utf8') as f:
#     data=f.read()







# for entity in results:
#     print(f"{entity['entity_group']}: {entity['word']} (confidence: {entity['score']:.3f})")
