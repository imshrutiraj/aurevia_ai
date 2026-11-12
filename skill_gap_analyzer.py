from typing import Dict, Any, List
from backend.skill_extractor import SkillExtractor
from backend.similarity_engine import SimilarityEngine

class SkillGapAnalyzer:
    """
    Skill Gap Detection Engine that contrasts extracted candidate proficiencies
    against benchmark role taxonomies, computing gap severity, coverage ratios,
    and prioritized next-learning trajectories.
    """

    @classmethod
    def analyze_gaps(cls, candidate_skills: List[str], target_role: str) -> Dict[str, Any]:
        role_profile = SkillExtractor.get_role_skills_profile(target_role)
        core_reqs = role_profile.get("core", [])
        secondary_reqs = role_profile.get("secondary", [])
        soft_reqs = role_profile.get("soft", [])

        candidate_lower_set = {s.lower() for s in candidate_skills}

        # Evaluate Core
        matched_core = [s for s in core_reqs if s.lower() in candidate_lower_set or any(s.lower() in c or c in s.lower() for c in candidate_lower_set)]
        missing_core = [s for s in core_reqs if s not in matched_core]

        # Evaluate Secondary
        matched_secondary = [s for s in secondary_reqs if s.lower() in candidate_lower_set or any(s.lower() in c or c in s.lower() for c in candidate_lower_set)]
        missing_secondary = [s for s in secondary_reqs if s not in matched_secondary]

        # Evaluate Soft
        matched_soft = [s for s in soft_reqs if s.lower() in candidate_lower_set or any(s.lower() in c or c in s.lower() for c in candidate_lower_set)]
        missing_soft = [s for s in soft_reqs if s not in matched_soft]

        total_reqs = len(core_reqs) + len(secondary_reqs)
        total_matched = len(matched_core) + len(matched_secondary)
        coverage_pct = round((total_matched / max(total_reqs, 1)) * 100, 1)

        # Prioritized recommendations
        prioritized_to_learn = []
        for s in missing_core:
            prioritized_to_learn.append({
                "skill": s,
                "priority": "High",
                "category": "Core Requirement",
                "reason": f"Crucial fundamental competency required for almost every {target_role} position."
            })
        for s in missing_secondary:
            prioritized_to_learn.append({
                "skill": s,
                "priority": "Medium",
                "category": "Secondary / Ecosystem",
                "reason": f"Frequently expected in modern production environments to complement core skills."
            })
        for s in missing_soft:
            prioritized_to_learn.append({
                "skill": s,
                "priority": "Low",
                "category": "Professional Soft Skill",
                "reason": "Enhances behavioral interviews and cross-team collaboration."
            })

        return {
            "target_role": target_role,
            "coverage_percentage": coverage_pct,
            "total_required_count": total_reqs,
            "total_matched_count": total_matched,
            "matched_core_skills": matched_core,
            "missing_core_skills": missing_core,
            "matched_secondary_skills": matched_secondary,
            "missing_secondary_skills": missing_secondary,
            "matched_soft_skills": matched_soft,
            "missing_soft_skills": missing_soft,
            "prioritized_recommendations": prioritized_to_learn
        }
