import os
import joblib
import numpy as np
from config import Config
from backend.text_preprocessing import preprocess_for_vectorizer
from backend.skill_extractor import SkillExtractor
from backend.similarity_engine import SimilarityEngine

class JobPredictor:
    """
    ML-based Job Role Predictor using Scikit-learn trained TF-IDF + Classifier pipeline.
    Predicts top career matches, calculates suitability probabilities, and evaluates skill alignment.
    """
    _pipeline = None

    @classmethod
    def get_pipeline(cls):
        if cls._pipeline is None:
            model_path = os.path.join(Config.SAVED_MODEL_DIR, "job_predictor_model.pkl")
            if os.path.exists(model_path):
                cls._pipeline = joblib.load(model_path)
            else:
                # Train if missing
                from ml_models.train_model import train_and_save_model
                cls._pipeline, _ = train_and_save_model()
        return cls._pipeline

    @classmethod
    def predict_roles(cls, resume_text: str, candidate_skills: list[str] = None, top_k: int = 5) -> list[dict]:
        """
        Returns top_k predicted job roles with confidence percentages, required skills,
        matching skills, and missing skills.
        """
        pipeline = cls.get_pipeline()
        clean = preprocess_for_vectorizer(resume_text)

        if not clean:
            # Default fallbacks
            return []

        classes = list(pipeline.classes_)
        probabilities = pipeline.predict_proba([clean])[0]

        # Sort by highest probability
        ranked_indices = np.argsort(probabilities)[::-1][:top_k]

        results = []
        if candidate_skills is None:
            extracted = SkillExtractor.extract_skills(resume_text)
            candidate_skills = extracted["all_skills"]

        for idx in ranked_indices:
            role_name = classes[idx]
            prob = float(probabilities[idx])
            suitability_score = round(prob * 100, 1)

            # Get skills required for this role
            role_profile = SkillExtractor.get_role_skills_profile(role_name)
            all_required = role_profile["core"] + role_profile["secondary"]

            overlap = SimilarityEngine.compare_skills_vectorized(candidate_skills, all_required)

            results.append({
                "role": role_name,
                "confidence_score": suitability_score,
                "required_skills": all_required,
                "matched_skills": overlap["matched_skills"],
                "missing_skills": overlap["missing_skills"],
                "skill_coverage_pct": overlap["match_percentage"]
            })

        return results

    @classmethod
    def evaluate_target_role_match(cls, resume_text: str, target_role: str, custom_job_description: str = "") -> dict:
        """
        Compares candidate resume against a specific target role and optional job description.
        """
        extracted = SkillExtractor.extract_skills(resume_text)
        candidate_skills = extracted["all_skills"]

        role_profile = SkillExtractor.get_role_skills_profile(target_role)
        all_required = role_profile["core"] + role_profile["secondary"]

        skill_overlap = SimilarityEngine.compare_skills_vectorized(candidate_skills, all_required)

        # Text similarity if custom JD provided
        jd_similarity = 0.0
        shared_keywords = []
        if custom_job_description and len(custom_job_description.strip()) > 20:
            sim_res = SimilarityEngine.compute_tfidf_similarity(resume_text, custom_job_description)
            jd_similarity = sim_res["similarity_score"]
            shared_keywords = sim_res["shared_keywords"]

        # Combined match score
        if jd_similarity > 0:
            overall_match = round(0.6 * skill_overlap["match_percentage"] + 0.4 * jd_similarity, 1)
        else:
            overall_match = round(skill_overlap["match_percentage"], 1)

        return {
            "target_role": target_role,
            "overall_match_score": overall_match,
            "skill_coverage_pct": skill_overlap["match_percentage"],
            "jd_similarity_score": jd_similarity,
            "matched_skills": skill_overlap["matched_skills"],
            "missing_skills": skill_overlap["missing_skills"],
            "core_required_skills": role_profile["core"],
            "secondary_skills": role_profile["secondary"],
            "shared_keywords": shared_keywords
        }
