# backend/main.py

from fastapi import FastAPI
from pydantic import BaseModel
from skill_extractor import SkillExtractor
from matcher import ResumeJDMatcher
from ats_scorer import ATSScorer

app = FastAPI(
    title="AI Resume Analyzer API",
    description="ATS-style resume analysis using NLP and Transformers",
    version="1.0"
)

# -------------------------------
# Load Models Once
# -------------------------------
skill_extractor = SkillExtractor("skill_ontology.json")
matcher = ResumeJDMatcher()
scorer = ATSScorer()

# -------------------------------
# Request Schema
# -------------------------------
class AnalyzeRequest(BaseModel):
    resume_text: str
    job_description: str

# -------------------------------
# Response Schema
# -------------------------------
class AnalyzeResponse(BaseModel):
    ats_score: float
    semantic_match: float
    skill_match: float
    section_completeness: float
    category_balance: float
    formatting: float
    extracted_skills: list

# -------------------------------
# API Endpoint
# -------------------------------
@app.post("/analyze", response_model=AnalyzeResponse)
def analyze_resume(data: AnalyzeRequest):

    resume_text = data.resume_text
    jd_text = data.job_description

    # Skill extraction
    resume_skills = skill_extractor.extract(resume_text)
    jd_skills = skill_extractor.extract(jd_text)["normalized_skills"]

    # Semantic matching
    semantic_score = matcher.match(resume_text, jd_text)

    # Minimal resume JSON for scoring
    resume_json = {
        "skills": resume_skills["normalized_skills"],
        "experience": resume_text,
        "education": resume_text,
        "projects": resume_text
    }

    # ATS scoring
    final_score, breakdown = scorer.calculate_score(
        resume_json=resume_json,
        skill_output=resume_skills,
        jd_skills=jd_skills,
        semantic_score=semantic_score,
        resume_text=resume_text
    )

    return {
        "ats_score": final_score,
        "semantic_match": breakdown["semantic_match"],
        "skill_match": breakdown["skill_match"],
        "section_completeness": breakdown["section_completeness"],
        "category_balance": breakdown["category_balance"],
        "formatting": breakdown["formatting"],
        "extracted_skills": resume_skills["normalized_skills"]
    }
