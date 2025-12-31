# ai_detector.py
"""
AI-Generated Content Detector for Resumes
Detects whether a resume is human-written or AI-generated
"""

import re
import numpy as np
from collections import Counter
import math

class AIContentDetector:
    def __init__(self):
        # Common AI-generated content markers
        self.ai_phrases = [
            "extensive experience in",
            "proven track record",
            "detail-oriented professional",
            "results-driven",
            "dynamic professional",
            "highly motivated",
            "team player",
            "excellent communication skills",
            "strong analytical skills",
            "proficient in",
            "demonstrated ability",
            "as a seasoned professional",
            "leveraging",
            "spearheaded",
            "orchestrated",
            "synergy",
            "paradigm",
            "core competencies",
            "value-added",
            "best practices"
        ]
        
        self.ai_patterns = [
            r'\b(extensive|proven|strong|excellent)\s+(experience|track\s+record|skills?)\b',
            r'\b(detail-oriented|results-driven|highly\s+motivated)\s+(professional|individual)\b',
            r'\b(demonstrated|proven)\s+ability\s+to\b',
            r'\bproficient\s+in\b',
            r'\bleverag(e|ed|ing)\b',
            r'\b(spearhead|orchestrat)(e|ed|ing)\b'
        ]
    
    def calculate_perplexity(self, text):
        """
        Calculate text perplexity - AI text tends to have lower perplexity
        """
        words = text.lower().split()
        if len(words) < 10:
            return 50  # Neutral score for very short text
        
        # Calculate word frequency distribution
        word_freq = Counter(words)
        total_words = len(words)
        
        # Calculate entropy (simplified perplexity)
        entropy = 0
        for count in word_freq.values():
            probability = count / total_words
            entropy += probability * math.log2(probability)
        
        perplexity = 2 ** (-entropy)
        return perplexity
    
    def calculate_burstiness(self, text):
        """
        Calculate burstiness - human text has more variation
        AI text tends to be more uniform
        """
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) < 3:
            return 50  # Neutral score
        
        # Calculate sentence length variation
        lengths = [len(s.split()) for s in sentences]
        if len(lengths) < 2:
            return 50
        
        mean_length = np.mean(lengths)
        std_length = np.std(lengths)
        
        # Coefficient of variation
        if mean_length > 0:
            cv = (std_length / mean_length) * 100
        else:
            cv = 0
        
        # Higher CV indicates more human-like variation
        return min(cv, 100)
    
    def detect_ai_phrases(self, text):
        """
        Detect common AI-generated phrases
        """
        text_lower = text.lower()
        phrase_count = 0
        
        # Check for exact phrase matches
        for phrase in self.ai_phrases:
            if phrase in text_lower:
                phrase_count += 1
        
        # Check for pattern matches
        for pattern in self.ai_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            phrase_count += len(matches)
        
        return phrase_count
    
    def calculate_repetition_score(self, text):
        """
        AI text often has repetitive structures
        """
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip().lower() for s in sentences if s.strip()]
        
        if len(sentences) < 3:
            return 0
        
        # Check for sentences starting with similar patterns
        starters = [s.split()[:3] if len(s.split()) >= 3 else s.split() 
                   for s in sentences]
        starter_strings = [' '.join(starter) for starter in starters]
        
        # Count duplicates
        starter_counts = Counter(starter_strings)
        repetitions = sum(count - 1 for count in starter_counts.values() if count > 1)
        
        # Normalize by sentence count
        repetition_rate = (repetitions / len(sentences)) * 100
        return min(repetition_rate, 100)
    
    def calculate_formality_score(self, text):
        """
        AI text tends to be overly formal
        """
        formal_words = [
            'utilize', 'facilitate', 'leverage', 'implement', 'execute',
            'demonstrate', 'establish', 'conduct', 'perform', 'achieve',
            'collaborate', 'coordinate', 'optimize', 'enhance', 'streamline'
        ]
        
        words = text.lower().split()
        if len(words) < 10:
            return 50
        
        formal_count = sum(1 for word in words if any(fw in word for fw in formal_words))
        formality_rate = (formal_count / len(words)) * 100
        
        return min(formality_rate * 5, 100)  # Scale up for visibility
    
    def detect_ai_content(self, text):
        """
        Main detection function
        Returns: (is_ai_generated: bool, confidence: float, details: dict)
        """
        if not text or len(text.strip()) < 50:
            return False, 0, {"error": "Text too short to analyze"}
        
        # Calculate various metrics
        perplexity = self.calculate_perplexity(text)
        burstiness = self.calculate_burstiness(text)
        ai_phrase_count = self.detect_ai_phrases(text)
        repetition = self.calculate_repetition_score(text)
        formality = self.calculate_formality_score(text)
        
        # Normalize scores (0-100, where higher = more likely AI)
        # Low perplexity = AI (invert the score)
        perplexity_score = max(0, 100 - perplexity)
        
        # Low burstiness = AI (invert the score)
        burstiness_score = max(0, 100 - burstiness)
        
        # High phrase count = AI
        phrase_score = min(ai_phrase_count * 5, 100)
        
        # Calculate weighted AI probability
        weights = {
            'perplexity': 0.15,
            'burstiness': 0.25,
            'phrases': 0.30,
            'repetition': 0.15,
            'formality': 0.15
        }
        
        ai_score = (
            perplexity_score * weights['perplexity'] +
            burstiness_score * weights['burstiness'] +
            phrase_score * weights['phrases'] +
            repetition * weights['repetition'] +
            formality * weights['formality']
        )
        
        # Determine if AI-generated (threshold: 60%)
        is_ai = ai_score > 60
        
        details = {
            'ai_probability': round(ai_score, 2),
            'human_probability': round(100 - ai_score, 2),
            'metrics': {
                'perplexity': round(perplexity, 2),
                'burstiness': round(burstiness, 2),
                'ai_phrases_found': ai_phrase_count,
                'repetition_rate': round(repetition, 2),
                'formality_score': round(formality, 2)
            },
            'verdict': 'AI-Generated' if is_ai else 'Human-Written',
            'confidence': round(abs(ai_score - 50) * 2, 2)  # Distance from neutral
        }
        
        return is_ai, ai_score, details
    
    def get_recommendation(self, is_ai, confidence):
        """
        Get recommendation based on detection results
        """
        if is_ai:
            if confidence > 80:
                return "❌ REJECTED: This resume appears to be AI-generated with high confidence. Please submit a human-written resume."
            elif confidence > 60:
                return "⚠️ WARNING: This resume shows strong signs of AI generation. Please review and rewrite in your own words."
            else:
                return "⚠️ CAUTION: This resume may contain AI-generated content. Consider personalizing it further."
        else:
            if confidence > 80:
                return "✅ ACCEPTED: This resume appears to be genuinely human-written."
            elif confidence > 60:
                return "✅ LIKELY HUMAN: This resume shows good signs of human authorship."
            else:
                return "✓ PASSED: This resume appears to be human-written, though some sections may benefit from more personality."


# Quick test function
if __name__ == "__main__":
    detector = AIContentDetector()
    
    # Test with sample text
    sample_ai = """
    Results-driven professional with extensive experience in data science and machine learning.
    Proven track record of leveraging advanced analytics to drive business outcomes.
    Detail-oriented individual with strong analytical skills and excellent communication abilities.
    Demonstrated ability to spearhead complex projects and orchestrate cross-functional teams.
    Proficient in Python, R, and SQL with a strong foundation in statistical modeling.
    """
    
    sample_human = """
    I've been working as a data scientist for 3 years now. Started at a small startup
    where I wore many hats - everything from data cleaning to building ML models.
    My favorite project was predicting customer churn, which actually helped us retain
    15% more customers. I'm pretty good with Python and love experimenting with new
    algorithms. Outside of work, I contribute to open-source projects and run a small
    data science blog.
    """
    
    print("Testing AI-generated text:")
    is_ai, score, details = detector.detect_ai_content(sample_ai)
    print(f"Is AI: {is_ai}, Score: {score}")
    print(f"Details: {details}\n")
    
    print("Testing human-written text:")
    is_ai, score, details = detector.detect_ai_content(sample_human)
    print(f"Is AI: {is_ai}, Score: {score}")
    print(f"Details: {details}")
