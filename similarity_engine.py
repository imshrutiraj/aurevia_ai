import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from backend.text_preprocessing import preprocess_for_vectorizer

class SimilarityEngine:
    """
    TF-IDF Vectorization and Cosine Similarity Engine for comparing resume content,
    job descriptions, role taxonomies, and candidate qualifications.
    """

    @classmethod
    def compute_tfidf_similarity(cls, text_a: str, text_b: str) -> dict:
        """
        Computes cosine similarity between two texts using TF-IDF with unigrams and bigrams.
        Returns:
            {
                "similarity_score": float (0-100),
                "shared_keywords": list[str],
                "vector_dimension": int
            }
        """
        clean_a = preprocess_for_vectorizer(text_a)
        clean_b = preprocess_for_vectorizer(text_b)

        if not clean_a or not clean_b:
            return {
                "similarity_score": 0.0,
                "shared_keywords": [],
                "vector_dimension": 0
            }

        vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            stop_words="english",
            max_features=2500,
            sublinear_tf=True
        )

        try:
            tfidf_matrix = vectorizer.fit_transform([clean_a, clean_b])
            cos_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            similarity_pct = round(float(np.clip(cos_sim * 100, 0, 100)), 2)

            feature_names = np.array(vectorizer.get_feature_names_out())
            vec_a = tfidf_matrix[0].toarray().flatten()
            vec_b = tfidf_matrix[1].toarray().flatten()

            # Find shared features with highest non-zero product
            shared_weights = vec_a * vec_b
            top_shared_indices = np.argsort(shared_weights)[::-1]
            shared_keywords = []
            for idx in top_shared_indices:
                if shared_weights[idx] > 0:
                    shared_keywords.append(feature_names[idx])
                if len(shared_keywords) >= 12:
                    break

            return {
                "similarity_score": similarity_pct,
                "shared_keywords": shared_keywords,
                "vector_dimension": int(tfidf_matrix.shape[1])
            }
        except Exception as e:
            return {
                "similarity_score": 0.0,
                "shared_keywords": [],
                "vector_dimension": 0,
                "error": str(e)
            }

    @classmethod
    def compare_skills_vectorized(cls, resume_skills: list[str], job_skills: list[str]) -> dict:
        """
        Calculates exact and partial overlap between candidate skills and required skills.
        """
        if not job_skills:
            return {"match_percentage": 100.0, "matched": resume_skills, "missing": []}

        resume_set = {s.lower() for s in resume_skills}
        matched = []
        missing = []

        for req in job_skills:
            req_lower = req.lower()
            if req_lower in resume_set:
                matched.append(req)
            elif any(req_lower in s or s in req_lower for s in resume_set):
                matched.append(req)
            else:
                missing.append(req)

        coverage = round((len(matched) / len(job_skills)) * 100, 2)
        return {
            "match_percentage": coverage,
            "matched_skills": matched,
            "missing_skills": missing
        }
