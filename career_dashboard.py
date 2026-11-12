from typing import Dict, Any, List
from database.models import AnalysisModel, InterviewModel, CoverLetterModel
from visualizations.charts import CareerChartVisualizer

class CareerDashboardAggregator:
    """
    Career Dashboard aggregation engine that synthesizes all modular telemetry,
    historical analysis records, interview scores, and chart payloads into a unified view.
    """

    @classmethod
    def get_dashboard_data(cls, analysis_id: int = None, resume_id: int = None) -> Dict[str, Any]:
        # 1. Fetch analysis record
        analysis = None
        if analysis_id:
            analysis = AnalysisModel.get_by_id(analysis_id)
        elif resume_id:
            analysis = AnalysisModel.get_latest_by_resume(resume_id)
        else:
            # Get most recent analysis across system
            history = AnalysisModel.get_history(limit=1)
            if history:
                analysis = AnalysisModel.get_by_id(history[0]["id"])

        # 2. Fetch interview records
        interview_history = InterviewModel.get_history(resume_id=resume_id, limit=10)
        avg_interview_score = 0.0
        if interview_history:
            scores = [i["overall_score"] for i in interview_history if i.get("overall_score")]
            if scores:
                avg_interview_score = round(sum(scores) / len(scores), 1)

        # 3. If no analysis yet, return baseline onboarding dashboard structure
        if not analysis:
            return {
                "has_analysis": False,
                "overall_resume_score": 0,
                "ats_score": 0,
                "skill_coverage_pct": 0,
                "total_skills_identified": 0,
                "skill_gaps_count": 0,
                "interview_readiness_score": 0,
                "interview_sessions_count": 0,
                "recent_history": AnalysisModel.get_history(limit=5),
                "charts": {}
            }

        ats_score = analysis.get("ats_score", 0.0)
        skill_coverage = analysis.get("skill_coverage_pct", 0.0)
        matched_skills = analysis.get("matched_skills", [])
        missing_skills = analysis.get("missing_skills", [])
        predicted_roles = analysis.get("predicted_roles", [])
        target_role = analysis.get("target_role", "Software Development Engineer")
        ats_breakdown = analysis.get("ats_breakdown", {})
        recommendations = analysis.get("recommendations", [])
        roadmap = analysis.get("roadmap", {})

        # Compute overall readiness score (composite of ATS, Skill coverage, Readability)
        overall_score = round(0.45 * ats_score + 0.40 * skill_coverage + 0.15 * max(avg_interview_score, 60), 1)

        # 4. Generate visual chart specs
        charts = {
            "ats_gauge": CareerChartVisualizer.generate_ats_gauge_plotly(ats_score),
            "role_matches": CareerChartVisualizer.generate_role_matches_plotly(predicted_roles) if predicted_roles else None,
            "skill_coverage_pie": CareerChartVisualizer.generate_skill_coverage_pie_matplotlib(len(matched_skills), len(missing_skills))
        }

        return {
            "has_analysis": True,
            "analysis_id": analysis["id"],
            "resume_id": analysis["resume_id"],
            "target_role": target_role,
            "overall_resume_score": overall_score,
            "ats_score": ats_score,
            "ats_breakdown": ats_breakdown,
            "skill_coverage_pct": skill_coverage,
            "total_skills_identified": len(matched_skills),
            "skill_gaps_count": len(missing_skills),
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "predicted_roles": predicted_roles,
            "recommendations": recommendations,
            "roadmap": roadmap,
            "interview_readiness_score": avg_interview_score or 65.0,
            "interview_sessions_count": len(interview_history),
            "interview_history": interview_history,
            "recent_history": AnalysisModel.get_history(limit=5),
            "charts": charts
        }
