from ats_scorer import ATSScorer

resume_json = {
    "skills": ["Python", "Machine Learning", "TensorFlow"],
    "experience": "2 years ML Engineer",
    "education": "B.Tech CSE",
    "projects": "Resume Analyzer"
}

skill_output = {
    "normalized_skills": ["Python", "Machine Learning", "TensorFlow"],
    "skill_categories": {
        "Programming": ["Python"],
        "Machine Learning": ["Machine Learning"],
        "Frameworks": ["TensorFlow"],
        "Tools": []
    }
}

jd_skills = ["Python", "Machine Learning", "Deep Learning"]

semantic_score = 0.72

resume_text = """
Python ML Engineer with experience in TensorFlow.
Worked on Resume Analyzer project.
"""

scorer = ATSScorer()
final_score, breakdown = scorer.calculate_score(
    resume_json,
    skill_output,
    jd_skills,
    semantic_score,
    resume_text
)

print("FINAL ATS SCORE:", final_score)
print("Breakdown:", breakdown)
