from datetime import datetime
from typing import Dict, Any, List

class CoverLetterGenerator:
    """
    AI-powered Cover Letter Generation Engine that synthesizes genuine candidate qualifications,
    projects, and technical competencies into tailored, professional cover letters.
    """

    @classmethod
    def generate(cls, candidate_info: Dict[str, str], skills: List[str], target_role: str, company_name: str = "Hiring Team", job_description: str = "", experience_text: str = "") -> str:
        name = candidate_info.get("name") or "Candidate"
        email = candidate_info.get("email") or "candidate@email.com"
        phone = candidate_info.get("phone") or "+1 (555) 000-0000"
        location = candidate_info.get("location") or "City, State"
        company = company_name.strip() if company_name.strip() else "the Engineering Team"

        date_str = datetime.now().strftime("%B %d, %Y")
        top_skills = ", ".join(skills[:5]) if skills else "modern software engineering practices"

        # Project / experience highlight
        highlight_paragraph = ""
        if experience_text and len(experience_text.strip()) > 50:
            first_few_lines = [l.strip() for l in experience_text.split("\n") if len(l.strip()) > 25][:2]
            highlight_snippet = " ".join(first_few_lines)
            highlight_paragraph = (
                f"Throughout my recent technical experience, I have focused on building robust and scalable solutions. "
                f"Specifically, {highlight_snippet}. This background has equipped me with the discipline to design "
                f"clean code, write automated tests, and collaborate effectively within agile delivery cycles."
            )
        else:
            highlight_paragraph = (
                f"My background centers on hands-on software development and engineering rigor. "
                f"I have developed multiple technical projects applying {top_skills}, with an emphasis on "
                f"performance, reliability, and delivering tangible end-user value."
            )

        letter = f"""{name}
{location} | {email} | {phone}

{date_str}

Hiring Manager & Selection Committee
{company}

Dear Hiring Team at {company},

I am writing to express my enthusiastic interest in the {target_role} position at {company}. With a rigorous foundation in {top_skills} and a commitment to technical excellence, I am excited about the opportunity to contribute directly to your team's mission and engineering initiatives.

{highlight_paragraph}

What particularly excites me about {company} is the opportunity to tackle challenging engineering problems while upholding high architectural and operational standards. My core competencies in {top_skills} position me to quickly ramp up, collaborate across functional teams, and produce immediate, measurable impact.

I welcome the opportunity to discuss how my technical qualifications, problem-solving mindset, and passion for continuous improvement align with your team's objectives. Thank you for your time, consideration, and review of my application.

Sincerely,

{name}
"""
        return letter.strip()
