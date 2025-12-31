# backend/test_matcher.py

from matcher import ResumeJDMatcher

matcher = ResumeJDMatcher()

resume_text = """
Skills: Python, Machine Learning, Deep Learning, TensorFlow
Experience: Worked as ML Engineer for 2 years building CV models.
Projects: Resume Analyzer, Face Recognition System
"""

job_description = """
Looking for a Machine Learning Engineer with strong Python skills,
experience in deep learning frameworks like TensorFlow or PyTorch,
and hands-on project experience.
"""

score = matcher.match(resume_text, job_description)
print("Resume–JD Similarity Score:", score)
