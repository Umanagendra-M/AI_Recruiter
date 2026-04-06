# tests/test_scorer.py
import pytest
import json
from score import Scorer

# Load rubric once for all tests
with open("rubric.json", "r") as f:
    rubric = json.load(f)

scorer = Scorer(rubric)

# ── Helper: build fake candidate ──────────
def make_candidate(name="Test User",
                   years=4,
                   skills=None,
                   designation="ML Engineer",
                   company="Google",
                   domain="Computer Vision"):
    if skills is None:
        skills = ["Python", "Machine Learning",
                  "PyTorch", "NLP"]
    return {
        "ideal_output": {
            "name": name,
            "years_experience": years,
            "skills": skills,
            "designation": designation,
            "company_name": company,
            "company_core_work_domain": domain
        }
    }

# ── Test 1: Perfect match = high score ────
def test_perfect_match():
    candidate = make_candidate(
        years=5,
        skills=["Python", "Machine Learning",
                "PyTorch", "NLP"],
        designation="ML Engineer",
        company="Google",
        domain="Computer Vision"
    )
    score, breakdown = scorer.calculate_score(
        candidate)
    assert score >= 0.7, \
        f"Perfect match should score >= 0.7, got {score}"

# ── Test 2: Wrong domain = low score ──────
def test_wrong_domain():
    candidate = make_candidate(
        domain="Finance and Banking"
    )
    score, breakdown = scorer.calculate_score(
        candidate)
    assert "domain_relevance" not in breakdown, \
        "Wrong domain should not get domain score"

# ── Test 3: Missing must-have skill ───────
def test_missing_must_have_skill():
    candidate = make_candidate(
        skills=["Python", "SQL"]
        # Missing PyTorch, NLP, Machine Learning
    )
    score, breakdown = scorer.calculate_score(
        candidate)
    assert "skillmatch" not in breakdown, \
        "Missing skills should not get skill score"

# ── Test 4: Years below minimum ───────────
def test_years_below_minimum():
    candidate = make_candidate(years=1)
    score, breakdown = scorer.calculate_score(
        candidate)
    assert "exp_match" not in breakdown, \
        "Below min years should not get exp score"

# ── Test 5: Zero score for bad candidate ──
def test_bad_candidate_zero_score():
    candidate = make_candidate(
        years=1,
        skills=["Excel", "PowerPoint"],
        designation="Sales Manager",
        company="Unknown Corp",
        domain="Real Estate"
    )
    score, breakdown = scorer.calculate_score(
        candidate)
    assert score == 0.0, \
        f"Bad candidate should score 0, got {score}"