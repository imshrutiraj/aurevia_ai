import re
from typing import Dict, Any, List
from backend.skill_extractor import SkillExtractor
from backend.similarity_engine import SimilarityEngine
from backend.embedding_engine import EmbeddingEngine
from backend.nlp_processor import NLPProcessor

class RecommendationEngine:
    """
    Holistic Career Recommendation and Advanced Intelligence Engine providing:
    - Career progression pathways
    - Tailored production project recommendations to bridge missing skills
    - Raw Job Description deep-analyzer
    - Resume version comparative evaluation
    """

    CAREER_PATHS = {
        "Software Development Engineer": [
            {"level": "Junior SDE (L3)", "focus": "Core feature implementation, bug fixes, automated unit testing, Git workflows."},
            {"level": "Mid-Level SDE (L4)", "focus": "Autonomous end-to-end service design, caching, database schema optimizations, CI/CD."},
            {"level": "Senior SDE (L5)", "focus": "Distributed systems architecture, system reliability, cross-team mentoring, technical vision."},
            {"level": "Principal Engineer / Staff (L6)", "focus": "Company-wide engineering standards, multi-year strategic roadmap, high-scale resilience."}
        ],
        "Frontend Developer": [
            {"level": "Junior UI Engineer", "focus": "Translating Figma designs into accessible HTML/CSS, basic React components."},
            {"level": "Mid-Level Frontend Engineer", "focus": "State architecture (Redux/Zustand), SSR with Next.js, API contract integration."},
            {"level": "Senior Frontend Architect", "focus": "Design systems, Core Web Vitals optimization, microfrontends, web performance."},
            {"level": "Staff UI/UX Systems Lead", "focus": "Cross-platform mobile/web architecture, developer tooling, accessible frameworks."}
        ],
        "Data Scientist": [
            {"level": "Associate Data Scientist", "focus": "Exploratory data analysis, data cleaning with Pandas, statistical hypothesis testing."},
            {"level": "Data Scientist", "focus": "Predictive model development, feature engineering, Scikit-learn, A/B experiment evaluation."},
            {"level": "Senior Data Scientist", "focus": "Deep learning architectures, production model pipelines, driving business KPI lift."},
            {"level": "Lead AI / Data Strategist", "focus": "Enterprise AI strategy, RAG systems, model governance, research-to-production roadmap."}
        ]
    }

    @classmethod
    def get_career_pathway(cls, target_role: str) -> List[Dict[str, str]]:
        for role_key, path in cls.CAREER_PATHS.items():
            if role_key.lower() in target_role.lower() or target_role.lower() in role_key.lower():
                return path
        return cls.CAREER_PATHS["Software Development Engineer"]

    @classmethod
    def recommend_projects_for_gaps(cls, missing_skills: List[str], target_role: str) -> List[Dict[str, str]]:
        """
        Recommends concrete, portfolio-worthy engineering projects tailored specifically to missing skills.
        """
        projects = []
        missing_lower = [s.lower() for s in missing_skills]

        if any(s in missing_lower for s in ["docker", "kubernetes", "ci/cd", "devops"]):
            projects.append({
                "title": "Containerized Microservice Fleet with Automated CI/CD",
                "target_skills": "Docker, Kubernetes, GitHub Actions, Nginx",
                "description": "Containerize a multi-service web application, orchestrate local development with Docker Compose, and configure GitHub Actions to automatically run unit tests and deploy to a cluster."
            })

        if any(s in missing_lower for s in ["redis", "caching", "kafka", "rabbitmq"]):
            projects.append({
                "title": "Event-Driven Asynchronous Message Broker Service",
                "target_skills": "Redis, Apache Kafka, Python/Node.js, PostgreSQL",
                "description": "Architect a decoupled event processing pipeline that ingests high-frequency clickstream events, buffers them in Redis, and streams them asynchronously through Kafka to analytical storage."
            })

        if any(s in missing_lower for s in ["react", "next.js", "typescript", "tailwind"]):
            projects.append({
                "title": "Modern Interactive SaaS Dashboard with Next.js & TypeScript",
                "target_skills": "React, TypeScript, Next.js, Tailwind CSS, Plotly.js",
                "description": "Build a responsive dark-mode analytics console featuring server-side rendering, dynamic data tables, authentication guards, and interactive charting."
            })

        if any(s in missing_lower for s in ["machine learning", "pytorch", "nlp", "transformers"]):
            projects.append({
                "title": "Production NLP Semantic Search & Text Classification API",
                "target_skills": "PyTorch, Sentence Transformers, FastAPI, Docker",
                "description": "Develop and deploy a REST microservice that takes document queries and returns top-matching records based on vector embeddings and cosine similarity."
            })

        if not projects:
            projects.append({
                "title": f"Production-Grade {target_role} Capstone System",
                "target_skills": f"{target_role} Ecosystem, Clean Architecture, Unit Tests",
                "description": "Design a complete end-to-end application demonstrating unit testing coverage, database indexing, REST API design, and comprehensive documentation."
            })

        return projects[:3]

    @classmethod
    def analyze_raw_job_description(cls, job_description_text: str) -> Dict[str, Any]:
        """
        Feature: Job Description Analyzer
        Extracts required skills, experience level, tools, and key responsibilities from any job posting.
        """
        if not job_description_text or len(job_description_text.strip()) < 20:
            return {"error": "Please provide a job description of at least 20 characters."}

        skills_extracted = SkillExtractor.extract_skills(job_description_text)
        
        # Experience level detection
        exp_match = re.search(r'\b(\d+\+?|\d+\s*-\s*\d+)\s*(?:years?|yrs?)(?:\s+of)?\s+experience\b', job_description_text, re.IGNORECASE)
        experience_required = exp_match.group(0) if exp_match else "Not explicitly specified (Likely 1-3 years / Entry-to-Mid)"

        # Education degree requirements
        deg_match = re.findall(r"(?i)\b(bachelor(?:'s)?|master(?:'s)?|b\.?tech|b\.?e\.?|b\.?s\.?|ph\.?d|computer science)\b", job_description_text)
        degree_required = ", ".join(sorted(list(set(deg_match)))) if deg_match else "Degree in Computer Science or equivalent practical experience"

        return {
            "experience_level": experience_required,
            "education_requirements": degree_required,
            "extracted_skills": skills_extracted["all_skills"],
            "categorized_skills": skills_extracted["categorized"],
            "total_skills_detected": skills_extracted["total_skills"]
        }

    @classmethod
    def compare_resume_versions(cls, text_v1: str, text_v2: str) -> Dict[str, Any]:
        """
        Feature: Resume Version Comparison
        Compares two resumes, highlighting improvements, added skills, readability delta, and score changes.
        """
        skills_v1 = set(SkillExtractor.extract_skills(text_v1)["all_skills"])
        skills_v2 = set(SkillExtractor.extract_skills(text_v2)["all_skills"])

        added_skills = sorted(list(skills_v2 - skills_v1))
        removed_skills = sorted(list(skills_v1 - skills_v2))

        semantic_similarity = EmbeddingEngine.compute_semantic_similarity(text_v1, text_v2)
        words_v1 = len(text_v1.split())
        words_v2 = len(text_v2.split())

        # Quantifiable impact check
        metrics_v1 = len(re.findall(r'\b(?:\d+[%xX+]|\$\d+)\b', text_v1))
        metrics_v2 = len(re.findall(r'\b(?:\d+[%xX+]|\$\d+)\b', text_v2))

        insights = []
        if len(added_skills) > 0:
            insights.append(f"Version 2 incorporated {len(added_skills)} new skills: {', '.join(added_skills[:6])}.")
        if metrics_v2 > metrics_v1:
            insights.append(f"Measurable impact indicators increased from {metrics_v1} to {metrics_v2}.")
        elif metrics_v2 == metrics_v1:
            insights.append("Both versions have the same number of quantifiable metrics.")
        
        return {
            "semantic_similarity_pct": semantic_similarity,
            "v1_word_count": words_v1,
            "v2_word_count": words_v2,
            "added_skills": added_skills,
            "removed_skills": removed_skills,
            "metrics_v1": metrics_v1,
            "metrics_v2": metrics_v2,
            "insights": insights
        }
