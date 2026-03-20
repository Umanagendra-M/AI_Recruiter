

import re
from typing import List
def extract_years(years_str: str) -> float:
    try:
        return float(years_str)  # handles integer directly
    except (ValueError, TypeError):
        try:
            return float(re.findall(r'\d+', str(years_str))[0])
        except:
            return -1.0
def match_list(name: str, preferred_list: list) -> bool:
    for pref_name in preferred_list:
        print(f"DEBUG comparing: '{pref_name.lower().strip()}' in '{name.lower().strip()}' = {pref_name.lower().strip() in name.lower().strip()}")
        if pref_name.lower().strip() in name.lower().strip():
            return True
    return False

def check_years_gate(candidate: dict, rubric: dict) -> tuple[bool, str]:

    print("years of expericene##############",extract_years(candidate["ideal_output"]["years_experience"]))
    years = float(extract_years(candidate["ideal_output"]["years_experience"]))
    if years < float(rubric["min_years_of_exp"]):
        return False, f"years not met: needs {rubric['min_years_of_exp']}, has {years}"
    return True, "years met"
def check_skills_gate(candidate: dict, rubric: dict) -> tuple[bool, str]:
    candidate_skills = set([s.lower() for s in candidate["ideal_output"]["skills"]])
    must_have = set([s.lower() for s in rubric["must_have_skills"]])
    missing = must_have - candidate_skills
    if missing:
        return False, f"missing must-have skills: {missing}"
    else:
        return True, "skills met"

def calculate_score(candidate: dict, 
                    rubric: dict) -> tuple[float, dict]:
    print("candidate",candidate)
    score = 0
    breakdown = {}
    domain_relevance=match_list(candidate["ideal_output"]["company_core_work_domain"],rubric["domain"])
    if domain_relevance:
        score+=0.3
        breakdown["domain_relevance"]=0.3
    title_match=match_list(candidate["ideal_output"]["designation"],rubric["preferred_titles"])
    if title_match:
        score+=0.2
        breakdown["title_match"]=0.2
    print(f"DEBUG title: {candidate['ideal_output']['designation']}")
    print(f"DEBUG title_match: {title_match}")

    company_match=match_list(candidate["ideal_output"]["company_name"],rubric["preferred_companies"])
    if company_match:
        score+=0.1
        breakdown['company_match']=0.1
    print(f"DEBUG company: {candidate['ideal_output']['company_name']}")
    print(f"DEBUG company_match: {company_match}")
    skillmatch,skill_match_detail= check_skills_gate(candidate,rubric)
    
    print(f"DEBUG company: {candidate['ideal_output']['skills']}")
    print(f"DEBUG company_match: {skill_match_detail}")
    if skillmatch:
        score+=0.25# for skills
        breakdown['skillmatch']=0.25

    exp_match,exp_string=check_years_gate(candidate,rubric)
    if exp_match:
        score+=0.15
        breakdown['exp_match']=0.15
    return score, breakdown


# STEP 2 — WEIGHTED SCORE (only for those who passed gates)
# Domain relevance:       30%
# Title match:            20%
# Company quality signal: 10%  ← I'll explain this
# Skills depth/breadth:   25%
# Experience level:       15%
    

    # returns (passed: bool, reason: str)
    # reason explains WHY they failed if they did
    
    # gate 1: years experience
    # gate 2: must have skills