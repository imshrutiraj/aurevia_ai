import re
from typing import Dict, Any, List
from backend.skill_extractor import SkillExtractor
from backend.nlp_processor import NLPProcessor
from backend.similarity_engine import SimilarityEngine

class ATSAnalyzer:
    """
    Applicant Tracking System (ATS) evaluation engine.
    Calculates explainable resume scores, detects missing sections, keywords,
    measures quantifiable impact, evaluates text readability, and generates actionable advice.
    """

    DISCLAIMER = (
        "Note: This score is an estimated, internally calculated evaluation based on standard ATS "
        "parsing benchmarks, keyword presence, structural integrity, and quantifiable achievements. "
        "It does not claim to represent any specific proprietary ATS algorithm."
    )

    @classmethod
    def evaluate_readability(cls, text: str) -> dict:
        words = re.findall(r'\b[a-zA-Z]+\b', text)
        sentences = [s for s in re.split(r'[.!?]+', text) if s.strip()]
        
        num_words = max(len(words), 1)
        num_sentences = max(len(sentences), 1)
        
        avg_sentence_length = round(num_words / num_sentences, 1)

        # Count syllables approximately
        syllables = 0
        for word in words:
            w = word.lower()
            count = len(re.findall(r'[aeiouy]+', w))
            syllables += max(count, 1)

        avg_syllables_per_word = syllables / num_words
        
        # Flesch Reading Ease Formula
        flesch_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
        flesch_score = round(max(0.0, min(100.0, flesch_score)), 1)

        if flesch_score >= 60:
            level = "Optimal Readability (Easy to scan for recruiters and ATS)"
        elif flesch_score >= 45:
            level = "Moderate Readability (Technical density is well balanced)"
        else:
            level = "Dense / Complex (Consider shortening bullet points)"

        return {
            "score": flesch_score,
            "word_count": num_words,
            "sentence_count": num_sentences,
            "avg_sentence_length": avg_sentence_length,
            "level": level
        }

    @classmethod
    def analyze_resume(cls, resume_text: str, target_role: str = "", job_description: str = "") -> Dict[str, Any]:
        contact = NLPProcessor.extract_contact_info(resume_text)
        sections = NLPProcessor.segment_sections(resume_text)
        skills_info = SkillExtractor.extract_skills(resume_text)
        readability = cls.evaluate_readability(resume_text)

        # 1. Section Completeness Check (Max 25 pts)
        expected_sections = [
            ("contact", bool(contact["email"] and contact["phone"]), "Contact Information (Email & Phone)"),
            ("summary", bool(len(sections.get("summary", "")) > 40), "Professional Summary / Objective"),
            ("skills", bool(skills_info["total_skills"] >= 5), "Technical Skills List"),
            ("experience", bool(len(sections.get("experience", "")) > 60), "Work Experience / Internships"),
            ("education", bool(len(sections.get("education", "")) > 30), "Education & Degree Details"),
            ("projects", bool(len(sections.get("projects", "")) > 50), "Key Projects Section")
        ]

        section_score = 0
        section_checklist = []
        for sec_key, is_present, label in expected_sections:
            pts = 4.16 if sec_key != "contact" else 4.2
            if is_present:
                section_score += pts
                section_checklist.append({"section": label, "status": "Found", "passed": True})
            else:
                section_checklist.append({"section": label, "status": "Missing or insufficient", "passed": False})
        
        section_score = round(min(25.0, section_score), 1)

        # 2. Keyword & Skill Relevance (Max 35 pts)
        target = target_role or "Software Development Engineer"
        role_profile = SkillExtractor.get_role_skills_profile(target)
        required_skills = role_profile["core"] + role_profile["secondary"]

        overlap = SimilarityEngine.compare_skills_vectorized(skills_info["all_skills"], required_skills)
        skill_pct = overlap["match_percentage"]
        keyword_score = round((skill_pct / 100.0) * 35.0, 1)

        # If job description provided, factor JD semantic overlap
        jd_score_add = 0.0
        missing_jd_keywords = []
        if job_description and len(job_description.strip()) > 30:
            jd_sim = SimilarityEngine.compute_tfidf_similarity(resume_text, job_description)
            # Find missing words from JD
            jd_words = set(re.findall(r'\b[a-zA-Z]{4,}\b', job_description.lower()))
            resume_words = set(re.findall(r'\b[a-zA-Z]{4,}\b', resume_text.lower()))
            missing_jd_keywords = sorted(list(jd_words - resume_words))[:8]

        # 3. Quantifiable Impact & Metrics (Max 20 pts)
        # Scan for numbers, percentages, currency, multipliers (e.g. 25%, $10k, 3x, 500+ users)
        metric_matches = re.findall(r'\b(?:\d+[%xX+]|\$\d+|\d+\s*(?:users|clients|requests|ms|seconds|teams|engineers|reduction|increase|improved))\b', resume_text, re.IGNORECASE)
        metric_count = len(metric_matches)
        if metric_count >= 6:
            quant_score = 20.0
        elif metric_count >= 4:
            quant_score = 16.0
        elif metric_count >= 2:
            quant_score = 11.0
        elif metric_count >= 1:
            quant_score = 6.0
        else:
            quant_score = 3.0

        # 4. Readability & Structure (Max 20 pts)
        read_score = round(min(20.0, (readability["score"] / 100.0) * 20.0), 1)

        # Total ATS Score
        total_ats = round(section_score + keyword_score + quant_score + read_score, 1)
        total_ats = float(min(100.0, max(10.0, total_ats)))

        # Specific actionable suggestions
        suggestions = []
        if not contact["email"] or not contact["phone"]:
            suggestions.append("Add clear direct contact info (email and phone number) at the top header.")
        if not contact["github"] and not contact["linkedin"]:
            suggestions.append("Include your LinkedIn profile and GitHub URL to validate technical credibility.")
        if quant_score < 15.0:
            suggestions.append("Add measurable achievements (e.g., 'improved API latency by 35%', 'handled 10,000+ daily queries').")
        if len(overlap["missing_skills"]) > 0:
            top_miss = ", ".join(overlap["missing_skills"][:4])
            suggestions.append(f"Consider integrating relevant skills for {target}: {top_miss}.")
        if readability["avg_sentence_length"] > 25:
            suggestions.append("Some bullet points are too wordy. Keep bullet points between 12-20 words for faster ATS and recruiter parsing.")
        if len(skills_info["all_skills"]) < 8:
            suggestions.append("Expand your Technical Skills section into categories: Languages, Frameworks, Databases, Tools.")

        return {
            "total_ats_score": total_ats,
            "breakdown": {
                "section_completeness": {"score": section_score, "max": 25},
                "keyword_relevance": {"score": keyword_score, "max": 35},
                "quantifiable_impact": {"score": quant_score, "max": 20},
                "readability_structure": {"score": read_score, "max": 20}
            },
            "readability": readability,
            "section_checklist": section_checklist,
            "matched_role_skills": overlap["matched_skills"],
            "missing_role_skills": overlap["missing_skills"],
            "metrics_found_count": metric_count,
            "suggestions": suggestions,
            "disclaimer": cls.DISCLAIMER
        }
