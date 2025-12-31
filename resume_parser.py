# backend/resume_parser.py

import pandas as pd
import json
from tqdm import tqdm
import re

class ResumeParser:
    def __init__(self, csv_path):
        self.df = pd.read_csv(csv_path)
        self.df.fillna("", inplace=True)
        print(f"Loaded {len(self.df)} resumes from {csv_path}")
        print(f"Columns: {self.df.columns.tolist()}")

    def clean_text(self, text):
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def extract_skills(self, resume_text):
        """Extract skills from resume text using simple pattern matching"""
        skills = []
        
        # Common skill keywords and patterns
        skill_patterns = [
            r'Skills?\s*:?\s*([^\n]+)',
            r'Technical Skills?\s*:?\s*([^\n]+)',
            r'Programming Languages?\s*:?\s*([^\n]+)',
            r'Tools?\s*:?\s*([^\n]+)'
        ]
        
        for pattern in skill_patterns:
            matches = re.findall(pattern, resume_text, re.IGNORECASE)
            for match in matches:
                # Split by common delimiters
                skill_list = re.split(r',|\||;|•|·', match)
                skills.extend([s.strip() for s in skill_list if s.strip()])
        
        return sorted(set(skills))

    def extract_education(self, resume_text):
        """Extract education information"""
        edu_patterns = [
            r'Education\s*(?:Details)?\s*:?\s*([^\n]+(?:\n(?!\w+:)[^\n]+)*)',
            r'(?:Bachelor|Master|PhD|B\.E|B\.Tech|M\.Tech|M\.S)\s+[^\n]+'
        ]
        
        education = []
        for pattern in edu_patterns:
            matches = re.findall(pattern, resume_text, re.IGNORECASE)
            education.extend(matches)
        
        return ' '.join(education) if education else ""

    def extract_experience(self, resume_text):
        """Extract experience information"""
        exp_patterns = [
            r'Experience\s*:?\s*([^\n]+(?:\n(?!\w+:)[^\n]+)*)',
            r'Work Experience\s*:?\s*([^\n]+(?:\n(?!\w+:)[^\n]+)*)',
        ]
        
        experience = []
        for pattern in exp_patterns:
            matches = re.findall(pattern, resume_text, re.IGNORECASE)
            experience.extend(matches)
        
        return ' '.join(experience) if experience else resume_text[:500]

    def parse(self):
        parsed_resumes = []

        for idx, row in tqdm(self.df.iterrows(), total=len(self.df), desc="Parsing resumes"):
            resume_text = str(row.get("Resume", ""))
            category = str(row.get("Category", ""))
            
            resume_json = {
                "resume_id": idx,
                "category": category,
                "skills": self.extract_skills(resume_text),
                "education": self.clean_text(self.extract_education(resume_text)),
                "experience": self.clean_text(self.extract_experience(resume_text)),
                "projects": "",  # Not available in this dataset
                "certifications": "",  # Not available in this dataset
                "full_text": self.clean_text(resume_text)[:1000]  # Store first 1000 chars
            }
            parsed_resumes.append(resume_json)

        return parsed_resumes

    def save_json(self, output_path):
        data = self.parse()
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"\n✓ Parsed {len(data)} resumes saved to {output_path}")
        return data
