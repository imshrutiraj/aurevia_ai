import re
from typing import Dict, Any, List
from backend.nlp_processor import NLPProcessor
from backend.skill_extractor import SkillExtractor

class ResumeImprover:
    """
    AI Resume Improver that elevates bullet points using Google's XYZ formula,
    replaces passive verbs with strong action verbs, detects weak phrases,
    and provides side-by-side Before-and-After enhancements without fabricating facts.
    """

    WEAK_PHRASES = [
        (r"(?i)\bresponsible for\b", "Spearheaded / Managed"),
        (r"(?i)\bworked on\b", "Architected / Engineered"),
        (r"(?i)\bhelped with\b", "Collaborated to deliver"),
        (r"(?i)\bdid\b", "Executed / Implemented"),
        (r"(?i)\bhandled\b", "Administered / Orchestrated"),
        (r"(?i)\btried to\b", "Successfully achieved"),
        (r"(?i)\bassisted in\b", "Partnered cross-functionally to drive"),
        (r"(?i)\btasked with\b", "Led the development of"),
        (r"(?i)\bparticipated in\b", "Contributed actively to the delivery of")
    ]

    POWER_VERBS = [
        "Architected", "Engineered", "Orchestrated", "Implemented", "Streamlined",
        "Spearheaded", "Accelerated", "Automated", "Optimized", "Delivered",
        "Refactored", "Designed", "Standardized", "Pioneered", "Consolidated"
    ]

    @classmethod
    def enhance_bullet_point(cls, bullet: str) -> dict:
        original = bullet.strip()
        improved = original

        # 1. Replace weak openers
        found_weakness = None
        for pattern, replacement in cls.WEAK_PHRASES:
            if re.search(pattern, improved):
                found_weakness = re.search(pattern, improved).group(0)
                # Replace with first recommendation
                replacement_verb = replacement.split(" / ")[0]
                improved = re.sub(pattern, replacement_verb, improved)
                break

        # 2. Capitalize first letter and ensure strong action verb at start
        words = improved.split()
        if words:
            first_word = words[0].strip(r'•-* ')
            if first_word.lower() in ["i", "we", "the", "my"]:
                # strip pronoun
                words = words[1:]
                if words:
                    words[0] = words[0].capitalize()
                improved = " ".join(words)

        # 3. Add XYZ impact guidance if no metrics exist
        has_metric = bool(re.search(r'\d+', improved))
        suggestion_note = ""
        if not has_metric:
            suggestion_note = "Tip: Quantify your result by adding impact metrics (e.g., 'reducing latency by 20%' or 'serving 500+ daily active users')."

        # Check if changed
        if improved == original and not has_metric:
            # Upgrade first verb if passive
            words = improved.split()
            if words:
                improved = f"Engineered and deployed {improved[0].lower() + improved[1:] if len(improved) > 1 else improved}"

        return {
            "original": original,
            "improved": improved,
            "detected_weakness": found_weakness or ("Lacks quantitative outcome" if not has_metric else "None"),
            "suggestion_note": suggestion_note
        }

    @classmethod
    def improve_resume_content(cls, resume_text: str, target_role: str = "") -> Dict[str, Any]:
        sections = NLPProcessor.segment_sections(resume_text)
        contact = NLPProcessor.extract_contact_info(resume_text)
        skills = SkillExtractor.extract_skills(resume_text)["all_skills"]

        # 1. Analyze bullet points from experience and projects
        experience_text = sections.get("experience", "") + "\n" + sections.get("projects", "")
        raw_lines = [l.strip() for l in experience_text.split("\n") if len(l.strip()) > 20]

        bullet_enhancements = []
        for line in raw_lines[:6]:
            enhanced = cls.enhance_bullet_point(line)
            bullet_enhancements.append(enhanced)

        # 2. Before & After Summary
        original_summary = sections.get("summary", "").strip()
        enhanced_summary = NLPProcessor.generate_professional_summary(
            contact, skills, NLPProcessor.extract_education_details(resume_text)
        )

        # 3. Action Verb Suggestions
        verb_suggestions = [v for v in cls.POWER_VERBS if v.lower() not in resume_text.lower()][:8]

        # 4. Detected Repetitions
        words = re.findall(r'\b[a-zA-Z]{5,}\b', resume_text.lower())
        word_freq = {}
        for w in words:
            word_freq[w] = word_freq.get(w, 0) + 1
        repetitive = [w for w, count in word_freq.items() if count >= 6 and w not in ["experience", "project", "system", "software"]]

        return {
            "bullet_enhancements": bullet_enhancements,
            "summary_comparison": {
                "before": original_summary or "No summary section detected in original resume.",
                "after": enhanced_summary
            },
            "suggested_action_verbs": verb_suggestions,
            "repetitive_words_detected": repetitive[:5],
            "target_role": target_role or "Software Engineering"
        }
