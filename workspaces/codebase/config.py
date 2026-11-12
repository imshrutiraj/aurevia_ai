import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

class Config:
    BASE_DIR = BASE_DIR
    SECRET_KEY = os.environ.get("SECRET_KEY", "aurevia-secret-key-production-career-platform-2026")
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    REPORTS_FOLDER = os.path.join(BASE_DIR, "reports")
    DATABASE_PATH = os.path.join(BASE_DIR, "database", "career_platform.db")
    # The trained classifier (job_predictor_model.pkl) is stored at the repository root.
    SAVED_MODEL_DIR = BASE_DIR
    DATASETS_DIR = os.path.join(BASE_DIR, "ml_models", "datasets")
    
    # 16 MB max upload
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    ALLOWED_EXTENSIONS = {"pdf", "docx"}
    
    # Semantic model
    EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
    
    # Target Roles supported across the platform
    TARGET_ROLES = [
        "Software Development Engineer",
        "Frontend Developer",
        "Backend Developer",
        "Full Stack Developer",
        "Data Analyst",
        "Data Scientist",
        "Machine Learning Engineer",
        "AI / Machine Learning Intern",
        "Python Developer",
        "Java Developer",
        "Business Analyst"
    ]
