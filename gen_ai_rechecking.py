from openai import OpenAI
import openai
import json
from pydantic import BaseModel
from typing import List
import os
class CandidateDetails(BaseModel):
    name: str
    years_experience: int
    skills: List[str]
    designation: str | None
    company_name: str | None
    company_core_work_domain: str | None

class NERValidation(BaseModel):
    correctly_extracted: List[str]
    missed_entities: List[str]
    incorrect_entities: List[str]
    ideal_output: CandidateDetails

# Ollama client

def validate_and_clean(pages: list) -> dict:
    ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    client = OpenAI(
        base_url=f"{ollama_host}/v1",
        api_key="ollama")
    # combine all page text
    full_text = "\n".join([p['page_text'] for p in pages])
    
    # combine all NER output
    ner_text = "\n".join([
        str(entity) 
        for p in pages 
        for entity in p['page_ner']
    ])
    

    try:
        completion = client.beta.chat.completions.parse(
            temperature=0,
            model="gemma2:2b",
            messages=[
                {"role": "user", "content": """
    You are a resume parsing validator.

    Given the raw resume text and NER extracted output,
    return a JSON with:
    - correctly_extracted: entities NER got right
    - missed_entities: entities NER missed  
    - incorrect_entities: entities NER got wrong
    - ideal_output: what perfect extraction looks like for different companies the person worked for 
    

    Raw resume text:
    {0}

    NER extracted output:
    {1}
    """.format(full_text, ner_text)}
            ],
            response_format=NERValidation,
        )

        response = completion.choices[0].message

        if response.parsed:
            return response.parsed.model_dump()
        elif response.refusal:
            print("Model refused:", response.refusal)

    except openai.LengthFinishReasonError as e:
        print("Too many tokens:", e)
    except Exception as e:
        print("Error:", e)