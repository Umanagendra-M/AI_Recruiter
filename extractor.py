import pdfplumber
import io
from typing import List
import sys

def get_data(pdf_path:str)->List[dict]:
    resume_data=[]
    with pdfplumber.open(pdf_path) as pdf:
        for pagenum,page in enumerate(pdf.pages):
            # Extract the text from the page
            resume_data.append({"page_num":pagenum+1,
                                "page_text":page.extract_text(),
                                "page_label":"",
                                "page_ner":[]})

   
    #print(resume_data)        
    return resume_data

# if __name__=="__main__":
#     get_data(sys.argv[1])


    