import os
import sys
import unittest
import json
import io
from docx import Document

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app
from config import Config
from database.db import init_db, get_db_connection
from database.models import ResumeModel, AnalysisModel, InterviewModel, CoverLetterModel
from backend.resume_parser import ResumeParser
from backend.text_preprocessing import clean_text, tokenize_words, remove_stopwords, preprocess_for_vectorizer
from backend.skill_extractor import SkillExtractor
from backend.nlp_processor import NLPProcessor
from backend.similarity_engine import SimilarityEngine
from backend.embedding_engine import EmbeddingEngine
from backend.job_predictor import JobPredictor
from backend.ats_analyzer import ATSAnalyzer
from backend.skill_gap_analyzer import SkillGapAnalyzer
from backend.resume_improver import ResumeImprover
from backend.learning_roadmap import LearningRoadmapGenerator
from backend.mock_interview import MockInterviewEngine
from backend.cover_letter_generator import CoverLetterGenerator
from backend.recommendation_engine import RecommendationEngine

SAMPLE_RESUME_TEXT = """
Alex Morgan
Seattle, WA | alex.morgan@email.com | +1 (555) 234-5678
github.com/alexmorgan | linkedin.com/in/alexmorgan

PROFESSIONAL SUMMARY
Results-driven Software Engineer with 3+ years experience building cloud-native microservices in Python, Java, and Go. Proven track record of improving API latency by 35% and supporting 100,000+ daily active users.

EDUCATION
Bachelor of Technology in Computer Science, University of Washington (2018 - 2022)

TECHNICAL SKILLS
• Programming Languages: Python, Java, JavaScript, TypeScript, SQL, C++, HTML5, CSS3
• Web & Backend: Django, FastAPI, Flask, React, Node.js, RESTful APIs, Redis
• Databases & Cloud: PostgreSQL, MySQL, MongoDB, AWS, Docker, Kubernetes, Git, CI/CD
• Soft Skills: Problem Solving, Teamwork, Agile / Scrum, Communication

WORK EXPERIENCE
Software Development Engineer | CloudScale Systems (2022 - Present)
• Architected and deployed 4 asynchronous microservices using Python FastAPI and Redis, handling 5,000 requests/sec.
• Optimized PostgreSQL query execution plans and database indexing, reducing p99 latency by 40%.
• Implemented automated CI/CD deployment pipelines using Docker and GitHub Actions.
• Worked on bug fixes and assisted with weekly team sprint planning meetings.

KEY PROJECTS
Real-Time Distributed Chat Service
• Built full-stack chat application with React, WebSockets, Node.js, and Redis pub/sub.
• Engineered message persistence layer in PostgreSQL with 99.9% uptime.
"""

class TestResumePlatform(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config["TESTING"] = True
        cls.client = app.test_client()
        init_db()

    def test_01_text_preprocessing(self):
        cleaned = clean_text("Hello • World!\n\n\n\nTest   Spaces")
        self.assertIn("Hello", cleaned)
        tokens = tokenize_words("Python, C++, and Node.js are great.")
        self.assertIn("Python", tokens)
        self.assertIn("C++", tokens)
        preprocessed = preprocess_for_vectorizer("Testing python with C++ and Docker!")
        self.assertIn("python", preprocessed)
        self.assertIn("c++", preprocessed)

    def test_02_skill_extraction(self):
        extracted = SkillExtractor.extract_skills(SAMPLE_RESUME_TEXT)
        self.assertGreaterEqual(extracted["total_skills"], 5)
        self.assertIn("Python", extracted["all_skills"])
        self.assertIn("Docker", extracted["all_skills"])
        self.assertIn("PostgreSQL", extracted["all_skills"])
        self.assertIn("React", extracted["all_skills"])
        self.assertTrue(len(extracted["categorized"]["programming_languages"]) > 0)

    def test_03_nlp_processor(self):
        contact = NLPProcessor.extract_contact_info(SAMPLE_RESUME_TEXT)
        self.assertEqual(contact["email"], "alex.morgan@email.com")
        self.assertIn("555", contact["phone"])
        self.assertIn("github.com/alexmorgan", contact["github"])
        
        sections = NLPProcessor.segment_sections(SAMPLE_RESUME_TEXT)
        self.assertTrue("experience" in sections or "skills" in sections)

        degrees = NLPProcessor.extract_education_details(SAMPLE_RESUME_TEXT)
        self.assertTrue(len(degrees) > 0)
        self.assertEqual(degrees[0]["degree"], "Bachelor's Degree")

    def test_04_similarity_engine(self):
        sim = SimilarityEngine.compute_tfidf_similarity(
            "Software engineer building Python microservices with Docker and PostgreSQL.",
            "Seeking Python backend developer with experience in microservices, Docker and SQL."
        )
        self.assertGreater(sim["similarity_score"], 10.0)
        self.assertTrue(len(sim["shared_keywords"]) > 0)

    def test_05_embedding_engine(self):
        sim = EmbeddingEngine.compute_semantic_similarity(
            "Engineered scalable web applications and microservice architectures",
            "Developed cloud-native web applications and backend services"
        )
        self.assertGreater(sim, 20.0)

    def test_06_job_predictor(self):
        roles = JobPredictor.predict_roles(SAMPLE_RESUME_TEXT, top_k=5)
        self.assertEqual(len(roles), 5)
        role_names = [r["role"] for r in roles]
        # Should heavily align with SDE / Backend / Python Developer
        self.assertTrue(any(role in ["Software Development Engineer", "Backend Developer", "Python Developer", "Full Stack Developer"] for role in role_names))

    def test_07_ats_analyzer(self):
        ats = ATSAnalyzer.analyze_resume(SAMPLE_RESUME_TEXT, target_role="Software Development Engineer")
        self.assertGreater(ats["total_ats_score"], 60.0)
        self.assertIn("section_completeness", ats["breakdown"])
        self.assertIn("keyword_relevance", ats["breakdown"])
        self.assertIn("quantifiable_impact", ats["breakdown"])
        self.assertIn("readability_structure", ats["breakdown"])
        self.assertGreater(ats["metrics_found_count"], 0)

    def test_08_skill_gap_analyzer(self):
        extracted = SkillExtractor.extract_skills(SAMPLE_RESUME_TEXT)
        gaps = SkillGapAnalyzer.analyze_gaps(extracted["all_skills"], "Software Development Engineer")
        self.assertGreater(gaps["coverage_percentage"], 40.0)
        self.assertTrue(len(gaps["matched_core_skills"]) > 0)
        self.assertTrue("prioritized_recommendations" in gaps)

    def test_09_resume_improver(self):
        improver = ResumeImprover.improve_resume_content(SAMPLE_RESUME_TEXT, "Software Development Engineer")
        self.assertTrue(len(improver["bullet_enhancements"]) > 0)
        self.assertIn("before", improver["summary_comparison"])
        self.assertIn("after", improver["summary_comparison"])
        self.assertTrue(len(improver["suggested_action_verbs"]) > 0)

    def test_10_learning_roadmap(self):
        extracted = SkillExtractor.extract_skills(SAMPLE_RESUME_TEXT)
        roadmap = LearningRoadmapGenerator.generate_roadmap(extracted["all_skills"], "Software Development Engineer")
        self.assertIn("levels", roadmap)
        self.assertTrue(len(roadmap["levels"]["beginner"]["milestones"]) > 0)
        self.assertTrue(len(roadmap["recommended_projects"]) > 0)
        self.assertTrue(len(roadmap["target_certifications"]) > 0)

    def test_11_mock_interview(self):
        extracted = SkillExtractor.extract_skills(SAMPLE_RESUME_TEXT)
        questions = MockInterviewEngine.generate_interview_questions(extracted["all_skills"], "Software Development Engineer", count=5)
        self.assertEqual(len(questions), 5)
        
        # Test evaluation
        first_q = questions[0]
        eval_res = MockInterviewEngine.evaluate_answer(
            first_q["question"],
            "Python uses the GIL which prevents multiple native threads from executing Python bytecodes simultaneously in a single process. Therefore, for CPU bound tasks, multiprocessing is better.",
            first_q["key_concepts"],
            first_q["model_answer"]
        )
        self.assertGreater(eval_res["overall_score"], 40.0)
        self.assertTrue(len(eval_res["feedback"]) > 0)

    def test_12_cover_letter_generator(self):
        contact = NLPProcessor.extract_contact_info(SAMPLE_RESUME_TEXT)
        skills = SkillExtractor.extract_skills(SAMPLE_RESUME_TEXT)["all_skills"]
        letter = CoverLetterGenerator.generate(contact, skills, "Software Development Engineer", "TechCorp")
        self.assertIn("Alex Morgan", letter)
        self.assertIn("TechCorp", letter)
        self.assertIn("Software Development Engineer", letter)

    def test_13_database_crud(self):
        resume_id = ResumeModel.create(
            filename="test_resume.pdf",
            file_type="pdf",
            raw_text=SAMPLE_RESUME_TEXT,
            candidate_name="Alex Morgan",
            email="alex@test.com",
            phone="555-1234",
            summary="Test Summary"
        )
        self.assertIsNotNone(resume_id)

        fetched = ResumeModel.get_by_id(resume_id)
        self.assertEqual(fetched["candidate_name"], "Alex Morgan")

        # Test Analysis Model creation
        analysis_id = AnalysisModel.create(
            resume_id=resume_id,
            target_role="Software Development Engineer",
            job_description="",
            ats_score=85.5,
            readability_score=70.0,
            ats_breakdown={"section_completeness": 22},
            matched_skills=["Python", "SQL"],
            missing_skills=["Kubernetes"],
            skill_coverage_pct=75.0,
            predicted_roles=[{"role": "Software Development Engineer", "confidence_score": 90}],
            recommendations=[{"title": "Project A"}],
            improvements=[{"original": "a", "improved": "b"}],
            roadmap={"level": "beginner"}
        )
        self.assertIsNotNone(analysis_id)
        
        analysis = AnalysisModel.get_by_id(analysis_id)
        self.assertEqual(analysis["ats_score"], 85.5)
        self.assertEqual(analysis["matched_skills"], ["Python", "SQL"])

    def test_14_flask_routes(self):
        # 1. GET /
        res_home = self.client.get("/")
        self.assertEqual(res_home.status_code, 200)
        self.assertIn(b"Aurevia", res_home.data)

        # 2. POST /api/chat
        res_chat = self.client.post("/api/chat", json={"message": "What is ATS score?"})
        self.assertEqual(res_chat.status_code, 200)
        self.assertTrue(res_chat.json["success"])
        self.assertIn("ATS", res_chat.json["reply"])

        # 3. POST /api/job-description/analyze
        res_jd = self.client.post("/api/job-description/analyze", json={
            "job_description": "We are seeking a Senior Backend Engineer with 5+ years of experience in Python, Django, PostgreSQL and Docker. A Bachelor's degree in Computer Science is required."
        })
        self.assertEqual(res_jd.status_code, 200)
        self.assertIn("Python", res_jd.json["analysis"]["extracted_skills"])

        # 4. POST /api/resume/compare
        res_comp = self.client.post("/api/resume/compare", json={
            "text_v1": "Software Engineer knowing Python and SQL. Built small website.",
            "text_v2": "Software Engineer experienced in Python, SQL, Docker, and Kubernetes. Improved performance by 30%."
        })
        self.assertEqual(res_comp.status_code, 200)
        self.assertTrue(res_comp.json["success"])
        self.assertIn("Docker", res_comp.json["comparison"]["added_skills"])

    def test_15_docx_parser(self):
        # Create in-memory docx
        doc = Document()
        doc.add_heading("Taylor Reed - Software Engineer", level=1)
        doc.add_paragraph("Email: taylor.reed@example.com | Phone: +1 555-888-9999")
        doc.add_paragraph("Experienced in Python, React, Docker, and PostgreSQL.")
        
        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)

        extracted = ResumeParser.extract_text_from_docx(buffer)
        self.assertIn("Taylor Reed", extracted)
        self.assertIn("Python", extracted)
        self.assertIn("PostgreSQL", extracted)

if __name__ == "__main__":
    unittest.main()
