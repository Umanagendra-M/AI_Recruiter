phase 1:


resume processing page type classification
resume page data extraction
page classification......> skills|experience|other
NER ---> org,name,location,skill,date,job title,domain keyword.
Job title + company + tenure ?
Skills scan                  ?
Domain fit evidence          ?  

LLM reconcilation check the extraction vs reality

create a dummy rubric setup
score the extracted data

sort the resumes.



phase 2 backlog:

create the rubric setup(editable)

resume with multicolumns.



##################################
## Phase 1 — COMPLETE 
Pipeline working end to end.
PDF → extract → classify → NER → 
LLM clean → score → JSON output

## Phase 2 Backlog
- Columnar PDF handling
- NER model replacement
- np.float32 serialization fix
- Score breakdown missing experience_level
- Deduplicate LLM output
- Editable rubric UI for Sarah
- Company domain lookup (Wikipedia Phase 3)

## Tomorrow
- Clean up hardcoded paths
- Move to proper folder structure
- Write Sarah demo script
- Prepare questions for Sarah meeting