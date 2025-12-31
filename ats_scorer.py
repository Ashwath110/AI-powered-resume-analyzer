# backend/ats_scorer.py

class ATSScorer:
    def __init__(self):
        self.weights = {
            "skill_match": 0.35,
            "semantic_match": 0.25,
            "section_completeness": 0.20,
            "category_balance": 0.10,
            "formatting": 0.10
        }

    # -------------------------------
    # 1️⃣ Skill Match Score
    # -------------------------------
    def skill_match_score(self, resume_skills, jd_skills):
        if not jd_skills:
            return 0.0
        matched = set(resume_skills).intersection(set(jd_skills))
        return len(matched) / len(jd_skills)

    # -------------------------------
    # 2️⃣ Section Completeness
    # -------------------------------
    def section_score(self, resume_json):
        required_sections = ["skills", "experience", "education", "projects"]
        present = sum(1 for sec in required_sections if resume_json.get(sec))
        return present / len(required_sections)

    # -------------------------------
    # 3️⃣ Skill Category Balance
    # -------------------------------
    def category_balance_score(self, skill_categories):
        if not skill_categories:
            return 0.0
        filled_categories = sum(
            1 for skills in skill_categories.values() if skills
        )
        return min(filled_categories / 4, 1.0)

    # -------------------------------
    # 4️⃣ Formatting Score
    # -------------------------------
    def formatting_score(self, resume_text):
        penalty = 0
        if len(resume_text) < 300:
            penalty += 0.3
        if resume_text.isupper():
            penalty += 0.4
        return max(0.0, 1.0 - penalty)

    # -------------------------------
    # FINAL ATS SCORE
    # -------------------------------
    def calculate_score(
        self,
        resume_json,
        skill_output,
        jd_skills,
        semantic_score,
        resume_text
    ):
        scores = {}

        scores["skill_match"] = self.skill_match_score(
            skill_output["normalized_skills"], jd_skills
        )

        scores["semantic_match"] = semantic_score
        scores["section_completeness"] = self.section_score(resume_json)
        scores["category_balance"] = self.category_balance_score(
            skill_output["skill_categories"]
        )
        scores["formatting"] = self.formatting_score(resume_text)

        final_score = sum(
            scores[k] * self.weights[k] for k in scores
        )

        return round(final_score * 100, 2), scores
