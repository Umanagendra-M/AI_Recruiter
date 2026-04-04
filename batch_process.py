import os
import csv
import sys
import zipfile
import tempfile
from run_pipeline import run_pipe
from db import get_connection, save_pipeline_run, \
               update_pipeline_run

def get_pdfs_from_input(input_path: str) -> tuple[list, str]:
    # Handle ZIP file
    if input_path.endswith('.zip'):
        tmp_dir = tempfile.mkdtemp()
        with zipfile.ZipFile(input_path, 'r') as z:
            z.extractall(tmp_dir)
        working_dir = tmp_dir
    else:
        working_dir = input_path

    # Get only PDF files
    pdf_files = [
        os.path.join(working_dir, f)
        for f in os.listdir(working_dir)
        if f.endswith('.pdf')
    ]
    return pdf_files, working_dir


def batch_process(input_path: str,output_path:str):
    conn = get_connection()
    pdf_files, _ = get_pdfs_from_input(input_path)

    print(f"Found {len(pdf_files)} PDFs")

    # Create one pipeline run for whole batch
    run_id = save_pipeline_run(
        conn, total_resumes=len(pdf_files))

    results = []
    processed = 0
    failed = 0

    for pdf_path in pdf_files:
        print(f"Processing: {pdf_path}")
        try:
            score, justification,candidate_name = run_pipe(pdf_path)
            results.append({
                "candidate_name": candidate_name,
                "filename": os.path.basename(pdf_path),
                "final_score": score,
                "domain_score": justification.get(
                    "domain_relevance", 0),
                "title_score": justification.get(
                    "title_match", 0),
                "company_score": justification.get(
                    "company_match", 0),
                "skills_score": justification.get(
                    "skillmatch", 0),
                "experience_score": justification.get(
                    "exp_match", 0),
                "status": "completed",
                "error_message": ""
            })
            processed += 1

        except Exception as e:
            friendly_error = "Could not process PDF"
            if "label" in str(e).lower():
                friendly_error = "PDF has no readable text content"
            elif "password" in str(e).lower():
                friendly_error = "PDF is password protected"
            else:
                friendly_error = f"Processing failed: {str(e)[:50]}"
            results.append({
                "candidate_name": "unknown",
                "filename": os.path.basename(pdf_path),
                "final_score": -1,
                "domain_score": 0,
                "title_score": 0,
                "company_score": 0,
                "skills_score": 0,
                "experience_score": 0,
                "status": "ERROR",
                "error_message": str(friendly_error)
            })
            failed += 1

    # Sort by score descending
    results.sort(
        key=lambda x: x["final_score"],
        reverse=True)

    # Add rank
    for i, r in enumerate(results):
        r["rank"] = i + 1 if r["status"] == "completed" \
                    else "FAILED"

    # Write CSV
    fieldnames = [
        "rank", "candidate_name","filename", "final_score",
        "domain_score", "title_score",
        "company_score", "skills_score",
        "experience_score", "status",
        "error_message"
    ]

    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    # Update pipeline run
    update_pipeline_run(
        conn, run_id, processed, failed,
        'completed' if failed == 0 else 'completed_with_errors'
    )

    conn.close()
    print(f"\nDone. {processed} processed, "
          f"{failed} failed.")
    print(f"Results saved to: {output_path}")
    return results


if __name__ == "__main__":
    input_path = sys.argv[1]
    output = sys.argv[2] if len(sys.argv) > 2 \
             else "results.csv"
    batch_process(input_path, output)

