import os
import sys
import json
from flask import Flask, request, jsonify, render_template, send_from_directory, Response
from werkzeug.exceptions import RequestEntityTooLarge

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from config import Config
from database.db import init_db
from database.models import ResumeModel, AnalysisModel, InterviewModel, CoverLetterModel
from backend.resume_parser import ResumeParser
from backend.nlp_processor import NLPProcessor
from backend.skill_extractor import SkillExtractor
from backend.similarity_engine import SimilarityEngine
from backend.embedding_engine import EmbeddingEngine
from backend.job_predictor import JobPredictor
from backend.ats_analyzer import ATSAnalyzer
from backend.skill_gap_analyzer import SkillGapAnalyzer
from backend.resume_improver import ResumeImprover
from backend.learning_roadmap import LearningRoadmapGenerator
from backend.mock_interview import MockInterviewEngine
from backend.cover_letter_generator import CoverLetterGenerator
from backend.career_dashboard import CareerDashboardAggregator
from backend.recommendation_engine import RecommendationEngine

# Initialize Flask application pointing to frontend templates and static folders
app = Flask(
    __name__,
    template_folder=os.path.join(Config.BASE_DIR, "frontend", "templates"),
    static_folder=os.path.join(Config.BASE_DIR, "frontend", "static")
)
app.config.from_object(Config)

# Ensure required directories exist and initialize database
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
os.makedirs(Config.REPORTS_FOLDER, exist_ok=True)
os.makedirs(Config.SAVED_MODEL_DIR, exist_ok=True)
init_db()


# -----------------------------------------------------------------------------
# ERROR HANDLERS
# -----------------------------------------------------------------------------

@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(e):
    return jsonify({"success": False, "error": "File size exceeds the 16MB maximum upload limit."}), 413

@app.errorhandler(404)
def handle_not_found(e):
    return jsonify({"success": False, "error": "API route or resource not found."}), 404

@app.errorhandler(500)
def handle_server_error(e):
    return jsonify({"success": False, "error": f"Internal server error: {str(e)}"}), 500


# -----------------------------------------------------------------------------
# FRONTEND VIEWS
# -----------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


# -----------------------------------------------------------------------------
# API: MODULE 1 - RESUME INTELLIGENCE & UPLOAD
# -----------------------------------------------------------------------------

@app.route("/api/upload", methods=["POST"])
def upload_resume():
    if "resume" not in request.files:
        return jsonify({"success": False, "error": "No resume file attached in the request."}), 400

    file = request.files["resume"]
    try:
        parsed_doc = ResumeParser.parse_file(file, Config.UPLOAD_FOLDER)
        raw_text = parsed_doc["raw_text"]
        
        # NLP Extraction
        contact_info = NLPProcessor.extract_contact_info(raw_text)
        education_details = NLPProcessor.extract_education_details(raw_text)
        sections = NLPProcessor.segment_sections(raw_text)
        
        # Skill Extraction
        skills_data = SkillExtractor.extract_skills(raw_text)
        
        # Professional Summary
        summary = NLPProcessor.generate_professional_summary(
            contact_info, skills_data["all_skills"], education_details
        )

        # Store in SQLite database
        resume_id = ResumeModel.create(
            filename=parsed_doc["filename"],
            file_type=parsed_doc["file_type"],
            raw_text=raw_text,
            candidate_name=contact_info.get("name", "Candidate"),
            email=contact_info.get("email", ""),
            phone=contact_info.get("phone", ""),
            location=contact_info.get("location", ""),
            education=json.dumps(education_details),
            experience=sections.get("experience", ""),
            skills_dict=skills_data,
            summary=summary
        )

        return jsonify({
            "success": True,
            "resume_id": resume_id,
            "filename": parsed_doc["filename"],
            "candidate_info": contact_info,
            "skills": skills_data,
            "education": education_details,
            "summary": summary,
            "message": "Resume parsed and structured successfully."
        })

    except ValueError as ve:
        return jsonify({"success": False, "error": str(ve)}), 400
    except Exception as e:
        return jsonify({"success": False, "error": f"Failed to process resume: {str(e)}"}), 500


# -----------------------------------------------------------------------------
# API: CORE ANALYSIS (MODULES 2, 3, 4, 5, 6)
# -----------------------------------------------------------------------------

@app.route("/api/analyze", methods=["POST"])
def analyze_career():
    try:
        data = request.form if request.form else (request.get_json() or {})
        resume_id = data.get("resume_id")
        target_role = data.get("target_role") or "Software Development Engineer"
        job_description = data.get("job_description", "").strip()

        # Check if direct file was uploaded with form
        if not resume_id and "resume" in request.files:
            file = request.files["resume"]
            parsed_doc = ResumeParser.parse_file(file, Config.UPLOAD_FOLDER)
            raw_text = parsed_doc["raw_text"]
            contact_info = NLPProcessor.extract_contact_info(raw_text)
            education_details = NLPProcessor.extract_education_details(raw_text)
            sections = NLPProcessor.segment_sections(raw_text)
            skills_data = SkillExtractor.extract_skills(raw_text)
            summary = NLPProcessor.generate_professional_summary(contact_info, skills_data["all_skills"], education_details)
            
            resume_id = ResumeModel.create(
                filename=parsed_doc["filename"],
                file_type=parsed_doc["file_type"],
                raw_text=raw_text,
                candidate_name=contact_info.get("name", "Candidate"),
                email=contact_info.get("email", ""),
                phone=contact_info.get("phone", ""),
                location=contact_info.get("location", ""),
                education=json.dumps(education_details),
                experience=sections.get("experience", ""),
                skills_dict=skills_data,
                summary=summary
            )
        
        if not resume_id:
            return jsonify({"success": False, "error": "No resume provided or resume_id missing."}), 400

        resume = ResumeModel.get_by_id(int(resume_id))
        if not resume:
            return jsonify({"success": False, "error": "Resume record not found in database."}), 404

        raw_text = resume["raw_text"]
        candidate_skills = resume["skills"]["all_skills"]

        # Module 2: ATS Evaluation
        ats_result = ATSAnalyzer.analyze_resume(raw_text, target_role, job_description)

        # Module 3: ML Job Match Explorer (Top 5 role predictions)
        predicted_roles = JobPredictor.predict_roles(raw_text, candidate_skills, top_k=5)
        role_match_eval = JobPredictor.evaluate_target_role_match(raw_text, target_role, job_description)

        # Module 4: Skill Gap Detector
        gap_result = SkillGapAnalyzer.analyze_gaps(candidate_skills, target_role)

        # Module 5: AI Resume Improver
        improver_result = ResumeImprover.improve_resume_content(raw_text, target_role)

        # Module 6: Learning Roadmap
        roadmap_result = LearningRoadmapGenerator.generate_roadmap(candidate_skills, target_role)

        # Additional Feature: Tailored Project Recommendations
        project_recs = RecommendationEngine.recommend_projects_for_gaps(gap_result["missing_core_skills"], target_role)
        career_path = RecommendationEngine.get_career_pathway(target_role)

        # Store Analysis Record in SQLite
        analysis_id = AnalysisModel.create(
            resume_id=resume["id"],
            target_role=target_role,
            job_description=job_description,
            ats_score=ats_result["total_ats_score"],
            readability_score=ats_result["readability"]["score"],
            ats_breakdown=ats_result["breakdown"],
            matched_skills=gap_result["matched_core_skills"] + gap_result["matched_secondary_skills"],
            missing_skills=gap_result["missing_core_skills"] + gap_result["missing_secondary_skills"],
            skill_coverage_pct=gap_result["coverage_percentage"],
            predicted_roles=predicted_roles,
            recommendations=project_recs,
            improvements=improver_result["bullet_enhancements"],
            roadmap=roadmap_result
        )

        return jsonify({
            "success": True,
            "analysis_id": analysis_id,
            "resume_id": resume["id"],
            "target_role": target_role,
            "candidate_name": resume.get("candidate_name"),
            "ats_analysis": ats_result,
            "job_match": {
                "target_role_evaluation": role_match_eval,
                "top_predicted_roles": predicted_roles
            },
            "skill_gaps": gap_result,
            "resume_improver": improver_result,
            "learning_roadmap": roadmap_result,
            "project_recommendations": project_recs,
            "career_pathway": career_path,
            "message": "Complete multi-module career intelligence analysis completed successfully."
        })

    except Exception as e:
        return jsonify({"success": False, "error": f"Analysis execution failed: {str(e)}"}), 500


# -----------------------------------------------------------------------------
# API: MODULE 7 - AI MOCK INTERVIEW
# -----------------------------------------------------------------------------

@app.route("/api/interview/generate", methods=["POST"])
def generate_interview_questions():
    data = request.get_json() or {}
    resume_id = data.get("resume_id")
    target_role = data.get("target_role") or "Software Development Engineer"

    candidate_skills = []
    if resume_id:
        resume = ResumeModel.get_by_id(int(resume_id))
        if resume:
            candidate_skills = resume["skills"]["all_skills"]

    questions = MockInterviewEngine.generate_interview_questions(candidate_skills, target_role, count=5)
    return jsonify({"success": True, "questions": questions})


@app.route("/api/interview/evaluate", methods=["POST"])
def evaluate_interview_answer():
    data = request.get_json() or {}
    question = data.get("question", "")
    user_answer = data.get("user_answer", "").strip()
    key_concepts = data.get("key_concepts", [])
    model_answer = data.get("model_answer", "")
    target_role = data.get("target_role", "Software Development Engineer")
    category = data.get("category", "Technical")
    resume_id = data.get("resume_id")

    if not user_answer:
        return jsonify({"success": False, "error": "Please provide an answer before submitting for evaluation."}), 400

    evaluation = MockInterviewEngine.evaluate_answer(question, user_answer, key_concepts, model_answer)

    # Persist in SQLite database
    interview_id = InterviewModel.create(
        resume_id=int(resume_id) if resume_id else None,
        target_role=target_role,
        category=category,
        question=question,
        user_answer=user_answer,
        relevance_score=evaluation["relevance_score"],
        clarity_score=evaluation["clarity_score"],
        overall_score=evaluation["overall_score"],
        feedback=evaluation["feedback"],
        model_answer=model_answer
    )

    return jsonify({
        "success": True,
        "interview_id": interview_id,
        "evaluation": evaluation
    })


@app.route("/api/interview/history", methods=["GET"])
def get_interview_history():
    resume_id = request.args.get("resume_id")
    history = InterviewModel.get_history(resume_id=int(resume_id) if resume_id else None, limit=20)
    return jsonify({"success": True, "history": history})


# -----------------------------------------------------------------------------
# API: MODULE 8 - COVER LETTER GENERATOR
# -----------------------------------------------------------------------------

@app.route("/api/cover-letter/generate", methods=["POST"])
def generate_cover_letter():
    data = request.get_json() or {}
    resume_id = data.get("resume_id")
    target_role = data.get("target_role") or "Software Development Engineer"
    company_name = data.get("company_name", "the Hiring Organization")
    job_description = data.get("job_description", "")

    candidate_info = {"name": "Candidate", "email": "candidate@example.com", "phone": "+1 (555) 000-0000", "location": "City, State"}
    skills = []
    experience_text = ""

    if resume_id:
        resume = ResumeModel.get_by_id(int(resume_id))
        if resume:
            candidate_info = {
                "name": resume.get("candidate_name", "Candidate"),
                "email": resume.get("email", ""),
                "phone": resume.get("phone", ""),
                "location": resume.get("location", "")
            }
            skills = resume["skills"]["all_skills"]
            experience_text = resume.get("work_experience", "")

    content = CoverLetterGenerator.generate(
        candidate_info, skills, target_role, company_name, job_description, experience_text
    )

    letter_id = CoverLetterModel.create(
        resume_id=int(resume_id) if resume_id else None,
        target_role=target_role,
        company_name=company_name,
        job_description=job_description,
        content=content
    )

    return jsonify({
        "success": True,
        "letter_id": letter_id,
        "content": content
    })


# -----------------------------------------------------------------------------
# API: MODULE 9 - CAREER DASHBOARD
# -----------------------------------------------------------------------------

@app.route("/api/dashboard", methods=["GET"])
def get_dashboard():
    analysis_id = request.args.get("analysis_id")
    resume_id = request.args.get("resume_id")
    
    dashboard_data = CareerDashboardAggregator.get_dashboard_data(
        analysis_id=int(analysis_id) if analysis_id else None,
        resume_id=int(resume_id) if resume_id else None
    )
    return jsonify({"success": True, "dashboard": dashboard_data})


# -----------------------------------------------------------------------------
# API: AURE AI COMPANION (BACKEND CHAT INTELLIGENCE)
# -----------------------------------------------------------------------------

@app.route("/api/chat", methods=["POST"])
def aure_chat():
    data = request.get_json() or {}
    message = data.get("message", "").strip().lower()
    resume_id = data.get("resume_id")

    if not message:
        return jsonify({"success": False, "reply": "I'm here! What career or resume question would you like to explore?"})

    # Retrieve candidate context if resume_id is available
    candidate_name = "there"
    skills_list = []
    if resume_id:
        resume = ResumeModel.get_by_id(int(resume_id))
        if resume:
            candidate_name = resume.get("candidate_name") or "there"
            skills_list = resume["skills"]["all_skills"]

    skills_snippet = f"Your extracted skills include: {', '.join(skills_list[:6])}." if skills_list else ""

    if "resume" in message or "cv" in message:
        reply = (
            f"Here are my top 4 recommendations for your resume, {candidate_name}:<br><br>"
            "1. <strong>Use Google's XYZ Formula:</strong> 'Accomplished [X] as measured by [Y], by doing [Z]'.<br>"
            "2. <strong>Front-load action verbs:</strong> Replace passive terms ('helped', 'worked on') with 'Engineered', 'Orchestrated', 'Architected'.<br>"
            "3. <strong>Quantify achievements:</strong> Always include metrics (percentages, latency reductions, user counts).<br>"
            "4. <strong>ATS Keywords:</strong> Check your Skill Gap detector to verify all core job criteria are clearly listed.<br><br>"
            f"{skills_snippet}"
        )
    elif "ats" in message:
        reply = (
            "<strong>Understanding ATS (Applicant Tracking Systems):</strong><br><br>"
            "ATS software screens resumes for keywords, structural clarity, and role alignment before human review.<br><br>"
            "• <strong>Formatting:</strong> Use standard single-column sections (Education, Skills, Experience).<br>"
            "• <strong>Keywords:</strong> Ensure skills required by the job posting appear verbatim in your text.<br>"
            "• <strong>Scoring:</strong> Aurevia computes an estimated 0-100 ATS readiness score based on section completeness, keyword density, and quantifiable metrics."
        )
    elif "interview" in message:
        reply = (
            "<strong>Interview Preparation Strategy:</strong><br><br>"
            "1. <strong>Master the STAR Method:</strong> For behavioral questions, explain the Situation, Task, Action, and Result.<br>"
            "2. <strong>Deep Technical Concepts:</strong> Revise language internals, complexity analysis (Big-O), and architectural trade-offs.<br>"
            "3. <strong>Practice with Aurevia Mock Interview:</strong> Jump to Module 7 to answer real technical questions and get evaluated by our Semantic AI engine."
        )
    elif "skill" in message or "learn" in message:
        reply = (
            "<strong>Strategic Skill Acquisition:</strong><br><br>"
            "Prioritize skills that appear repeatedly in target job descriptions.<br><br>"
            "• <strong>Foundational:</strong> Data Structures, Algorithms, Git, and SQL.<br>"
            "• <strong>Production Ecosystem:</strong> Docker, RESTful APIs, and Relational Databases.<br>"
            "• <strong>Specialization:</strong> Check your personalized Learning Roadmap (Module 6) for a week-by-week curriculum tailored to your gaps."
        )
    elif "career" in message or "job" in message:
        reply = (
            "<strong>Building a High-Trajectory Career:</strong><br><br>"
            "1. <strong>Define your north star:</strong> Choose your target role in the Analyzer.<br>"
            "2. <strong>Bridge skill gaps:</strong> Build the recommended portfolio projects.<br>"
            "3. <strong>Practice mock interviews regularly:</strong> Polish both communication and technical accuracy."
        )
    else:
        # Semantic general fallback
        reply = (
            f"That's a thoughtful question, {candidate_name}! ✦<br><br>"
            "As your Aurevia Career Buddy, I can assist you with:<br>"
            "• Evaluating and improving resume bullet points<br>"
            "• Explaining ATS compatibility and missing keywords<br>"
            "• Structuring your learning path and interview preparation<br><br>"
            "Feel free to ask a specific question or test an interview response!"
        )

    return jsonify({"success": True, "reply": reply})


# -----------------------------------------------------------------------------
# API: ADDITIONAL FEATURES (JD ANALYZER, VERSION COMPARISON, HISTORY, EXPORT)
# -----------------------------------------------------------------------------

@app.route("/api/job-description/analyze", methods=["POST"])
def analyze_job_description():
    data = request.get_json() or {}
    jd_text = data.get("job_description", "")
    analysis = RecommendationEngine.analyze_raw_job_description(jd_text)
    return jsonify({"success": True, "analysis": analysis})


@app.route("/api/resume/compare", methods=["POST"])
def compare_resumes():
    data = request.get_json() or {}
    text_v1 = data.get("text_v1", "")
    text_v2 = data.get("text_v2", "")

    if not text_v1 or not text_v2:
        return jsonify({"success": False, "error": "Please provide text for both resume versions."}), 400

    comparison = RecommendationEngine.compare_resume_versions(text_v1, text_v2)
    return jsonify({"success": True, "comparison": comparison})


@app.route("/api/history", methods=["GET"])
def get_history():
    history = AnalysisModel.get_history(limit=15)
    return jsonify({"success": True, "history": history})


@app.route("/api/analysis/<int:analysis_id>", methods=["DELETE"])
def delete_analysis(analysis_id):
    AnalysisModel.delete(analysis_id)
    return jsonify({"success": True, "message": f"Analysis #{analysis_id} deleted successfully."})


@app.route("/api/export-report/<int:analysis_id>", methods=["GET"])
def export_analysis_report(analysis_id):
    analysis = AnalysisModel.get_by_id(analysis_id)
    if not analysis:
        return jsonify({"success": False, "error": "Analysis not found."}), 404

    report_md = f"""# AUREVIA AI - COMPREHENSIVE CAREER INTELLIGENCE REPORT
Date Generated: {analysis.get('created_at')}
Target Role: {analysis.get('target_role')}

## 1. ATS COMPATIBILITY EVALUATION
Overall Estimated ATS Score: {analysis.get('ats_score')}/100
Readability Index: {analysis.get('readability_score')}/100

### Score Breakdown:
- Section Completeness: {analysis.get('ats_breakdown', {}).get('section_completeness', {}).get('score', 0)}/25
- Keyword Relevance: {analysis.get('ats_breakdown', {}).get('keyword_relevance', {}).get('score', 0)}/35
- Quantifiable Impact: {analysis.get('ats_breakdown', {}).get('quantifiable_impact', {}).get('score', 0)}/20
- Readability & Structure: {analysis.get('ats_breakdown', {}).get('readability_structure', {}).get('score', 0)}/20

## 2. SKILL ALIGNMENT & GAP ANALYSIS
Skill Coverage Ratio: {analysis.get('skill_coverage_pct')}%
- Matched Skills: {', '.join(analysis.get('matched_skills', []))}
- Critical Missing Skills: {', '.join(analysis.get('missing_skills', []))}

## 3. PREDICTED CAREER ROLES (ML CLASSIFIER)
"""
    for role in analysis.get('predicted_roles', []):
        report_md += f"- **{role['role']}**: {role['confidence_score']}% Match (Coverage: {role['skill_coverage_pct']}%)\n"

    report_md += "\n## 4. RECOMMENDED CAPSTONE PROJECTS\n"
    for proj in analysis.get('recommendations', []):
        report_md += f"### {proj.get('title')}\nTarget Skills: {proj.get('target_skills')}\n{proj.get('description')}\n\n"

    return Response(
        report_md,
        mimetype="text/markdown",
        headers={"Content-Disposition": f"attachment;filename=Aurevia_Career_Report_{analysis_id}.md"}
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
