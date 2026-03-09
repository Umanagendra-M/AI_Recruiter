from transformers import pipeline

def classify_page(page_text:str)->str:
    pipe = pipeline(model="facebook/bart-large-mnli")
    page_label=pipe(page_text,candidate_labels=['Tech Skills','Work experience',"other"])
    return page_label['labels'][0]


