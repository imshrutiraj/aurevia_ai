import sqlite3
import os
from config import Config

def get_db_connection():
    """
    Establish and return a connection to the SQLite database.
    Row factory is set to sqlite3.Row for dictionary-like column access.
    """
    os.makedirs(os.path.dirname(Config.DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    """
    Initializes database schema with proper relational tables.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Resumes table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS resumes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL,
        file_type TEXT NOT NULL,
        raw_text TEXT NOT NULL,
        candidate_name TEXT,
        email TEXT,
        phone TEXT,
        location TEXT,
        education TEXT,
        work_experience TEXT,
        skills_json TEXT,
        summary TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 2. Analyses table (stores ATS, Match, Skill Gap, Recommendations)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS analyses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        resume_id INTEGER NOT NULL,
        target_role TEXT NOT NULL,
        job_description TEXT,
        ats_score REAL NOT NULL,
        readability_score REAL,
        ats_breakdown_json TEXT,
        matched_skills_json TEXT,
        missing_skills_json TEXT,
        skill_coverage_pct REAL,
        predicted_roles_json TEXT,
        recommendations_json TEXT,
        improvements_json TEXT,
        roadmap_json TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (resume_id) REFERENCES resumes (id) ON DELETE CASCADE
    );
    """)

    # 3. Mock Interview Sessions
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mock_interviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        resume_id INTEGER,
        target_role TEXT NOT NULL,
        category TEXT NOT NULL,
        question TEXT NOT NULL,
        user_answer TEXT,
        relevance_score REAL,
        clarity_score REAL,
        overall_score REAL,
        feedback TEXT,
        model_answer TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (resume_id) REFERENCES resumes (id) ON DELETE SET NULL
    );
    """)

    # 4. Cover Letters table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cover_letters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        resume_id INTEGER,
        target_role TEXT NOT NULL,
        company_name TEXT,
        job_description TEXT,
        content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (resume_id) REFERENCES resumes (id) ON DELETE SET NULL
    );
    """)

    # 5. Roadmap progress tracking
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS roadmap_tracker (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        analysis_id INTEGER NOT NULL,
        topic_title TEXT NOT NULL,
        level TEXT NOT NULL,
        is_completed INTEGER DEFAULT 0,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (analysis_id) REFERENCES analyses (id) ON DELETE CASCADE
    );
    """)

    conn.commit()
    conn.close()
