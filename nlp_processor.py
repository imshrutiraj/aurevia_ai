import re
from typing import Dict, Any, List

class NLPProcessor:
    """
    NLP Processor for candidate profiling, named entity recognition, contact detail extraction,
    section segmentation, and structured resume summarization.
    """

    # Section header identification patterns
    SECTION_HEADERS = {
        "education": r"(?i)\b(education|academic background|qualification|degrees|university|college)\b",
        "experience": r"(?i)\b(experience|work experience|employment history|work history|professional experience|internships?)\b",
        "projects": r"(?i)\b(projects?|personal projects?|academic projects?|key projects?)\b",
        "skills": r"(?i)\b(technical skills|skills|technologies|competencies|proficiencies|tech stack)\b",
        "certifications": r"(?i)\b(certifications?|certificates?|licenses?|credentials)\b",
        "achievements": r"(?i)\b(achievements?|honors?|awards?|accomplishments?)\b",
        "summary": r"(?i)\b(summary|professional summary|profile|about me|objective|career objective)\b"
    }

    @classmethod
    def extract_contact_info(cls, text: str) -> Dict[str, str]:
        # Email pattern
        email_match = re.search(r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b', text)
        email = email_match.group(0) if email_match else ""

        # Phone pattern
        phone_match = re.search(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b', text)
        if not phone_match:
            phone_match = re.search(r'\+?\d{10,13}\b', text)
        phone = phone_match.group(0).strip() if phone_match else ""

        # Links
        github_match = re.search(r'(?:https?://)?(?:www\.)?github\.com/[a-zA-Z0-9_-]+', text, re.IGNORECASE)
        github = github_match.group(0) if github_match else ""

        linkedin_match = re.search(r'(?:https?://)?(?:www\.)?linkedin\.com/in/[a-zA-Z0-9_-]+', text, re.IGNORECASE)
        linkedin = linkedin_match.group(0) if linkedin_match else ""

        # Extract name: scan top 10 lines
        candidate_name = cls.extract_candidate_name(text)

        # Location heuristic
        location = cls.extract_location(text)

        return {
            "name": candidate_name,
            "email": email,
            "phone": phone,
            "github": github,
            "linkedin": linkedin,
            "location": location
        }

    @classmethod
    def extract_candidate_name(cls, text: str) -> str:
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        for line in lines[:8]:
            # Filter out lines that look like emails, urls, or phone numbers
            if "@" in line or "http" in line or "github" in line or "linkedin" in line or "resume" in line.lower():
                continue
            # Filter out common headings
            if re.search(r'(?i)\b(curriculum|vitae|profile|summary|engineer|developer|education)\b', line):
                continue
            words = line.split()
            if 1 <= len(words) <= 4 and all(w[0].isupper() for w in words if w.isalpha()):
                clean_name = re.sub(r'[^a-zA-Z\s]', '', line).strip()
                if clean_name:
                    return clean_name
        return "Candidate"

    @classmethod
    def extract_location(cls, text: str) -> str:
        # Common city / location hints
        match = re.search(r'\b([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?),\s*([A-Z]{2}|[A-Z][a-zA-Z]+)\b', text)
        if match:
            return match.group(0)
        return ""

    @classmethod
    def segment_sections(cls, text: str) -> Dict[str, str]:
        lines = text.split("\n")
        sections = {k: [] for k in cls.SECTION_HEADERS}
        sections["other"] = []

        current_section = "other"
        for line in lines:
            trimmed = line.strip()
            if not trimmed:
                continue

            # Check if line matches a header
            detected_header = None
            if len(trimmed.split()) <= 4:
                for sec_key, pattern in cls.SECTION_HEADERS.items():
                    if re.fullmatch(pattern, trimmed) or (re.search(pattern, trimmed) and len(trimmed) < 30):
                        detected_header = sec_key
                        break

            if detected_header:
                current_section = detected_header
            else:
                sections[current_section].append(trimmed)

        return {k: "\n".join(v) for k, v in sections.items()}

    @classmethod
    def extract_education_details(cls, text: str) -> List[Dict[str, str]]:
        degrees = []
        degree_patterns = [
            (r"(?i)\b(b\.?tech|b\.?e\.?|bachelor(?:'s)?\s+of\s+engineering|bachelor(?:'s)?\s+of\s+technology|b\.?s\.?|bachelor(?:'s)?\s+of\s+science|bca)\b", "Bachelor's Degree"),
            (r"(?i)\b(m\.?tech|m\.?e\.?|master(?:'s)?\s+of\s+technology|master(?:'s)?\s+of\s+engineering|m\.?s\.?|master(?:'s)?\s+of\s+science|mca)\b", "Master's Degree"),
            (r"(?i)\b(ph\.?d|doctorate)\b", "Doctorate / Ph.D"),
            (r"(?i)\b(diploma|higher secondary|high school)\b", "Diploma / Secondary")
        ]

        year_pattern = r'\b(19\d{2}|20\d{2})\s*(?:-|–|to)\s*(19\d{2}|20\d{2}|present|current)\b|\b(20\d{2})\b'

        for pattern, degree_type in degree_patterns:
            match = re.search(pattern, text)
            if match:
                # find surrounding text
                span_start = max(0, match.start() - 30)
                span_end = min(len(text), match.end() + 100)
                context = text[span_start:span_end].replace("\n", " ").strip()
                
                year_match = re.search(year_pattern, context, re.IGNORECASE)
                duration = year_match.group(0) if year_match else ""

                degrees.append({
                    "degree": degree_type,
                    "details": context,
                    "year": duration
                })

        return degrees

    @classmethod
    def generate_professional_summary(cls, candidate_info: Dict[str, str], skills: List[str], education: List[Dict[str, str]]) -> str:
        name = candidate_info.get("name", "The candidate")
        top_skills = ", ".join(skills[:5]) if skills else "modern software engineering practices"
        
        degree_str = ""
        if education:
            degree_str = f" possessing a background in {education[0]['degree']}"

        summary = (
            f"{name} is a results-driven professional{degree_str} with hands-on expertise across {top_skills}. "
            f"Demonstrates proven ability to architect scalable solutions, collaborate in agile engineering environments, "
            f"and apply technical competencies to solve complex real-world challenges. "
            f"Passionate about continuous learning, performance optimization, and driving business value."
        )
        return summary
