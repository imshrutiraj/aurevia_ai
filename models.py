import json
from database.db import get_db_connection

class ResumeModel:
    @staticmethod
    def create(filename, file_type, raw_text, candidate_name="", email="", phone="", location="", education="", experience="", skills_dict=None, summary=""):
        skills_json = json.dumps(skills_dict or {})
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO resumes (filename, file_type, raw_text, candidate_name, email, phone, location, education, work_experience, skills_json, summary)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (filename, file_type, raw_text, candidate_name, email, phone, location, education, experience, skills_json, summary))
        resume_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return resume_id

    @staticmethod
    def get_by_id(resume_id):
        conn = get_db_connection()
        resume = conn.execute("SELECT * FROM resumes WHERE id = ?", (resume_id,)).fetchone()
        conn.close()
        if resume:
            data = dict(resume)
            data["skills"] = json.loads(data["skills_json"] or "{}")
            return data
        return None

    @staticmethod
    def get_latest():
        conn = get_db_connection()
        resume = conn.execute("SELECT * FROM resumes ORDER BY id DESC LIMIT 1").fetchone()
        conn.close()
        if resume:
            data = dict(resume)
            data["skills"] = json.loads(data["skills_json"] or "{}")
            return data
        return None

    @staticmethod
    def get_all():
        conn = get_db_connection()
        rows = conn.execute("SELECT id, filename, candidate_name, email, created_at FROM resumes ORDER BY id DESC").fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def delete(resume_id):
        conn = get_db_connection()
        conn.execute("DELETE FROM resumes WHERE id = ?", (resume_id,))
        conn.commit()
        conn.close()
        return True


class AnalysisModel:
    @staticmethod
    def create(resume_id, target_role, job_description, ats_score, readability_score, ats_breakdown, matched_skills, missing_skills, skill_coverage_pct, predicted_roles, recommendations, improvements, roadmap):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO analyses (
                resume_id, target_role, job_description, ats_score, readability_score,
                ats_breakdown_json, matched_skills_json, missing_skills_json,
                skill_coverage_pct, predicted_roles_json, recommendations_json,
                improvements_json, roadmap_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            resume_id, target_role, job_description, ats_score, readability_score,
            json.dumps(ats_breakdown or {}),
            json.dumps(matched_skills or []),
            json.dumps(missing_skills or []),
            skill_coverage_pct,
            json.dumps(predicted_roles or []),
            json.dumps(recommendations or []),
            json.dumps(improvements or []),
            json.dumps(roadmap or {})
        ))
        analysis_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return analysis_id

    @staticmethod
    def get_by_id(analysis_id):
        conn = get_db_connection()
        row = conn.execute("SELECT * FROM analyses WHERE id = ?", (analysis_id,)).fetchone()
        conn.close()
        if not row:
            return None
        return AnalysisModel._deserialize(dict(row))

    @staticmethod
    def get_latest_by_resume(resume_id):
        conn = get_db_connection()
        row = conn.execute("SELECT * FROM analyses WHERE resume_id = ? ORDER BY id DESC LIMIT 1", (resume_id,)).fetchone()
        conn.close()
        if not row:
            return None
        return AnalysisModel._deserialize(dict(row))

    @staticmethod
    def get_history(limit=10):
        conn = get_db_connection()
        rows = conn.execute("""
            SELECT a.id, a.resume_id, a.target_role, a.ats_score, a.skill_coverage_pct, a.created_at, r.filename, r.candidate_name
            FROM analyses a
            JOIN resumes r ON a.resume_id = r.id
            ORDER BY a.id DESC LIMIT ?
        """, (limit,)).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def delete(analysis_id):
        conn = get_db_connection()
        conn.execute("DELETE FROM analyses WHERE id = ?", (analysis_id,))
        conn.commit()
        conn.close()
        return True

    @staticmethod
    def _deserialize(data):
        data["ats_breakdown"] = json.loads(data.get("ats_breakdown_json") or "{}")
        data["matched_skills"] = json.loads(data.get("matched_skills_json") or "[]")
        data["missing_skills"] = json.loads(data.get("missing_skills_json") or "[]")
        data["predicted_roles"] = json.loads(data.get("predicted_roles_json") or "[]")
        data["recommendations"] = json.loads(data.get("recommendations_json") or "[]")
        data["improvements"] = json.loads(data.get("improvements_json") or "[]")
        data["roadmap"] = json.loads(data.get("roadmap_json") or "{}")
        return data


class InterviewModel:
    @staticmethod
    def create(resume_id, target_role, category, question, user_answer, relevance_score, clarity_score, overall_score, feedback, model_answer):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO mock_interviews (resume_id, target_role, category, question, user_answer, relevance_score, clarity_score, overall_score, feedback, model_answer)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (resume_id, target_role, category, question, user_answer, relevance_score, clarity_score, overall_score, feedback, model_answer))
        interview_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return interview_id

    @staticmethod
    def get_history(resume_id=None, limit=20):
        conn = get_db_connection()
        if resume_id:
            rows = conn.execute("SELECT * FROM mock_interviews WHERE resume_id = ? ORDER BY id DESC LIMIT ?", (resume_id, limit)).fetchall()
        else:
            rows = conn.execute("SELECT * FROM mock_interviews ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        conn.close()
        return [dict(r) for r in rows]


class CoverLetterModel:
    @staticmethod
    def create(resume_id, target_role, company_name, job_description, content):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO cover_letters (resume_id, target_role, company_name, job_description, content)
            VALUES (?, ?, ?, ?, ?)
        """, (resume_id, target_role, company_name, job_description, content))
        letter_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return letter_id

    @staticmethod
    def get_by_id(letter_id):
        conn = get_db_connection()
        row = conn.execute("SELECT * FROM cover_letters WHERE id = ?", (letter_id,)).fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def get_history(resume_id=None, limit=10):
        conn = get_db_connection()
        if resume_id:
            rows = conn.execute("SELECT * FROM cover_letters WHERE resume_id = ? ORDER BY id DESC LIMIT ?", (resume_id, limit)).fetchall()
        else:
            rows = conn.execute("SELECT * FROM cover_letters ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        conn.close()
        return [dict(r) for r in rows]
