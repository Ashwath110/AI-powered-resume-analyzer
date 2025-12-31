# backend/skill_extractor.py

import json
import re

class SkillExtractor:
    def __init__(self, ontology_path):
        with open(ontology_path, "r", encoding="utf-8") as f:
            self.ontology = json.load(f)

    def normalize_text(self, text):
        text = text.lower()
        text = re.sub(r'[^a-z0-9+\s]', ' ', text)
        return text

    def extract(self, resume_text, raw_skills=None):
        text = self.normalize_text(resume_text)
        found_skills = set()
        categorized_skills = {}

        for category, skills in self.ontology.items():
            for canonical, variants in skills.items():
                for variant in variants:
                    if variant in text:
                        found_skills.add(canonical)
                        categorized_skills.setdefault(category, []).append(canonical)

        # Also include raw skill list if provided
        if raw_skills:
            for skill in raw_skills:
                skill_text = self.normalize_text(skill)
                for category, skills in self.ontology.items():
                    for canonical, variants in skills.items():
                        if skill_text in variants:
                            found_skills.add(canonical)
                            categorized_skills.setdefault(category, []).append(canonical)

        # Deduplicate
        for k in categorized_skills:
            categorized_skills[k] = sorted(set(categorized_skills[k]))

        return {
            "normalized_skills": sorted(found_skills),
            "skill_categories": categorized_skills
        }
