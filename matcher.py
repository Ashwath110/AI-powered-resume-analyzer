# backend/matcher.py

from sklearn.metrics.pairwise import cosine_similarity
from embeddings import EmbeddingModel
import numpy as np

class ResumeJDMatcher:
    def __init__(self):
        self.embedder = EmbeddingModel()

    def build_resume_text(self, resume_json, skill_output):
        """
        Combine important resume sections into one semantic text
        """
        parts = []

        if skill_output.get("normalized_skills"):
            parts.append("Skills: " + ", ".join(skill_output["normalized_skills"]))

        for key in ["experience", "projects", "education"]:
            if resume_json.get(key):
                parts.append(f"{key.capitalize()}: {resume_json[key]}")

        return " ".join(parts)

    def match(self, resume_text, job_description):
        resume_embedding = self.embedder.encode(resume_text)
        jd_embedding = self.embedder.encode(job_description)

        score = cosine_similarity(
            resume_embedding.cpu().numpy(),
            jd_embedding.cpu().numpy()
        )[0][0]

        return round(float(score), 4)
