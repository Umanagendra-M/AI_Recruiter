# Experiment Log

## Exp 001 — Baseline prompt
Date: 2026-03-14
Change: Original vague prompt
Resume: resume_strong.pdf
Output domain: "Document Understanding using PyTorch..."
Score: 0.15
Problem: domain too long, match_list fails

## Exp 002 — Explicit domain instruction
Date: 2026-03-14
Change: Added "company_core_work_domain should be 
        ONE short keyword, 2-3 words maximum"
Resume: resume_strong.pdf
Output domain: "Computer Vision"
Score: 0.45
Problem: title and company still not matching

## Exp 003 — Fixed rubric + prompt
Date: 2026-03-14
Change: Updated rubric to new test rubric
        Fixed prompt for domain extraction
Results:
  resume_strong:         1 
  resume_hard_gate_fail: 0  
  resume_wrong_domain:   0.35 
Status: PASSING
