

import re
from typing import List
def extract_years(years_str: str) -> float:
    try:
        return float(years_str)  # handles integer directly
    except (ValueError, TypeError):
        try:
            return float(re.findall('\d+', str(years_str))[0])
        except:
            return -1.0
def match_list(name: str, 
                  preferred_list: list) -> bool:
    for pref_name in preferred_list:
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
# def match_domain(candidate_domain: str, 
#                  rubric_domains: list) -> bool:
#     for domain in rubric_domains:
#         if domain.lower() in candidate_domain.lower():
#             return True
#     return False
# def match_title(candidate_title: str,
#                 preferred_titles: list) -> bool:
#     for title in preferred_titles:
#         if title.lower() in candidate_title.lower():
#             return True
#     return False
# def check_hard_gates(candidate: dict,  rubric: dict) -> tuple[bool, str]:
#     # GATE 1: years
#     years = extract_years(candidate["ideal_output"]["years_experience"])
#     if years < rubric["min_years_of_exp"]:
#         return False, f"years not met: needs {rubric['min_years_of_exp']}, has {years}"

#     candidate_skills = set([s.lower() for s in candidate["ideal_output"]["skills"]])
#     must_have = set([s.lower() for s in rubric["must_have_skills"]])
#     missing = must_have - candidate_skills
#     if missing:
#         return False, f"missing must-have skills: {missing}"
    
#     return True, "passed all hard gates"

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

    company_match=match_list(candidate["ideal_output"]["company_name"],rubric["preferred_companies"])
    if company_match:
        score+=0.1
        breakdown['company_match']=0.1
    skillmatch,_= check_skills_gate(candidate,rubric)
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