from skill_extractor import SkillExtractor

extractor = SkillExtractor("skill_ontology.json")

resume_text = """
Experienced ML Engineer with strong python skills.
Worked on deep learning using tensorflow and pytorch.
Used git and docker for deployment.
"""

raw_skills = ["ML", "Python", "Tensor Flow", "Docker"]

output = extractor.extract(resume_text, raw_skills)
print(output)
