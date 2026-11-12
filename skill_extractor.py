import re
from typing import Dict, List, Set, Any

class SkillExtractor:
    """
    Extensible Skill Extraction Engine supporting comprehensive technical and soft skill taxonomies,
    boundary-safe pattern matching, alias normalization, and category organization.
    """

    SKILL_TAXONOMY: Dict[str, Dict[str, List[str]]] = {
        "programming_languages": {
            "Python": ["python", "py"],
            "Java": ["java", "core java"],
            "JavaScript": ["javascript", "js", "ecmascript"],
            "TypeScript": ["typescript", "ts"],
            "C++": ["c++", "cpp"],
            "C#": ["c#", "csharp", "c-sharp"],
            "C": ["c programming", "c lang"],
            "Go": ["golang", "go language"],
            "Rust": ["rust", "rustlang"],
            "Ruby": ["ruby", "ruby on rails"],
            "PHP": ["php"],
            "SQL": ["sql", "structured query language"],
            "HTML5": ["html", "html5"],
            "CSS3": ["css", "css3"],
            "Kotlin": ["kotlin"],
            "Swift": ["swift"],
            "R": ["r programming", "r-lang"],
            "Scala": ["scala"],
            "Bash": ["bash", "shell scripting", "powershell"],
            "Dart": ["dart"]
        },
        "web_development": {
            "React": ["react", "react.js", "reactjs"],
            "Node.js": ["node.js", "nodejs", "node"],
            "Express.js": ["express", "express.js", "expressjs"],
            "Django": ["django"],
            "Flask": ["flask"],
            "FastAPI": ["fastapi", "fast-api"],
            "Angular": ["angular", "angularjs"],
            "Vue.js": ["vue", "vue.js", "vuejs"],
            "Next.js": ["next.js", "nextjs"],
            "Spring Boot": ["spring boot", "springboot", "spring framework"],
            "ASP.NET": ["asp.net", "aspnet", ".net core", "dotnet core"],
            "RESTful APIs": ["rest", "rest api", "restful api", "restful apis", "rest apis"],
            "GraphQL": ["graphql"],
            "Redux": ["redux", "redux toolkit"],
            "Tailwind CSS": ["tailwind", "tailwindcss", "tailwind css"],
            "Bootstrap": ["bootstrap"],
            "WebSockets": ["websockets", "websocket", "socket.io"]
        },
        "databases": {
            "PostgreSQL": ["postgresql", "postgres"],
            "MySQL": ["mysql"],
            "SQLite": ["sqlite", "sqlite3"],
            "MongoDB": ["mongodb", "mongo"],
            "Redis": ["redis"],
            "Cassandra": ["cassandra"],
            "Oracle": ["oracle db", "oracle database"],
            "MS SQL Server": ["sql server", "mssql", "microsoft sql server"],
            "DynamoDB": ["dynamodb", "dynamo db"],
            "Firebase": ["firebase", "firestore"],
            "Elasticsearch": ["elasticsearch", "elastic search"],
            "Snowflake": ["snowflake"],
            "BigQuery": ["bigquery", "big query"]
        },
        "data_science": {
            "Pandas": ["pandas"],
            "NumPy": ["numpy"],
            "SciPy": ["scipy"],
            "Matplotlib": ["matplotlib"],
            "Seaborn": ["seaborn"],
            "Data Analysis": ["data analysis", "data analytics", "exploratory data analysis", "eda"],
            "Statistics": ["statistics", "statistical analysis", "hypothesis testing"],
            "Tableau": ["tableau"],
            "Power BI": ["power bi", "powerbi"],
            "Feature Engineering": ["feature engineering"],
            "Jupyter": ["jupyter", "jupyter notebook"],
            "Excel": ["advanced excel", "excel modelling"]
        },
        "machine_learning_ai": {
            "Machine Learning": ["machine learning", "ml"],
            "Deep Learning": ["deep learning", "dl", "neural networks", "ann", "cnn", "rnn"],
            "Scikit-learn": ["scikit-learn", "sklearn"],
            "PyTorch": ["pytorch", "torch"],
            "TensorFlow": ["tensorflow", "tf"],
            "Keras": ["keras"],
            "Natural Language Processing": ["nlp", "natural language processing", "text mining"],
            "Computer Vision": ["computer vision", "cv", "opencv"],
            "Transformers": ["transformers", "hugging face", "huggingface"],
            "Large Language Models": ["llm", "llms", "large language models"],
            "Sentence Transformers": ["sentence transformers", "sentence-transformers", "embeddings"],
            "XGBoost": ["xgboost", "lightgbm", "catboost"],
            "Random Forest": ["random forest", "decision trees"],
            "MLOps": ["mlops", "model deployment", "model monitoring"]
        },
        "cloud_devops": {
            "Docker": ["docker", "containerization"],
            "Kubernetes": ["kubernetes", "k8s"],
            "AWS": ["aws", "amazon web services", "ec2", "s3", "lambda"],
            "Azure": ["azure", "microsoft azure"],
            "Google Cloud Platform": ["gcp", "google cloud"],
            "CI/CD": ["ci/cd", "ci cd", "continuous integration", "continuous deployment"],
            "Git": ["git"],
            "GitHub": ["github", "gitlab", "bitbucket"],
            "Linux": ["linux", "ubuntu", "unix"],
            "Terraform": ["terraform"],
            "Ansible": ["ansible"],
            "Nginx": ["nginx", "reverse proxy"],
            "Microservices": ["microservices", "microservice architecture"],
            "Jenkins": ["jenkins"]
        },
        "tools_technologies": {
            "Jira": ["jira", "confluence"],
            "Postman": ["postman", "api testing"],
            "VS Code": ["vs code", "visual studio code"],
            "PyTest": ["pytest", "unit testing", "unittest"],
            "Selenium": ["selenium"],
            "Kafka": ["kafka", "apache kafka"],
            "RabbitMQ": ["rabbitmq"],
            "Celery": ["celery"],
            "Webpack": ["webpack", "vite"]
        },
        "soft_skills": {
            "Problem Solving": ["problem solving", "analytical thinking", "critical thinking"],
            "Communication": ["communication", "verbal communication", "written communication"],
            "Leadership": ["leadership", "team lead", "initiative"],
            "Teamwork": ["teamwork", "collaboration", "cross-functional teams"],
            "Time Management": ["time management", "prioritization", "multitasking"],
            "Adaptability": ["adaptability", "fast learner", "quick learner"],
            "Agile / Scrum": ["agile", "scrum", "sprints"]
        }
    }

    @classmethod
    def extract_skills(cls, text: str) -> Dict[str, Any]:
        """
        Extracts skills from text, categorized by domain.
        Returns:
            {
                "categorized": { category: [Skill1, Skill2, ...] },
                "all_skills": [Skill1, Skill2, ...],
                "total_skills": int,
                "counts_by_category": { category: int }
            }
        """
        lowered_text = " " + text.lower() + " "
        extracted_categorized: Dict[str, List[str]] = {}
        all_skills: Set[str] = set()

        for category, skill_map in cls.SKILL_TAXONOMY.items():
            category_found = []
            for standard_name, aliases in skill_map.items():
                matched = False
                for alias in aliases:
                    # Boundary safe regex check
                    # Handle special symbols like c++, c#, .net
                    escaped_alias = re.escape(alias)
                    pattern = rf'(?<![a-zA-Z0-9]){escaped_alias}(?![a-zA-Z0-9])'
                    if re.search(pattern, lowered_text):
                        matched = True
                        break
                if matched:
                    category_found.append(standard_name)
                    all_skills.add(standard_name)
            
            extracted_categorized[category] = sorted(category_found)

        total = len(all_skills)
        counts = {cat: len(skills) for cat, skills in extracted_categorized.items()}

        return {
            "categorized": extracted_categorized,
            "all_skills": sorted(list(all_skills)),
            "total_skills": total,
            "counts_by_category": counts
        }

    @classmethod
    def get_role_skills_profile(cls, target_role: str) -> Dict[str, List[str]]:
        """
        Returns typical required, recommended, and soft skills for a given job role.
        """
        role_lower = target_role.lower()

        if "software development engineer" in role_lower or "sde" in role_lower or "software engineer" in role_lower:
            return {
                "core": ["Python", "Java", "C++", "SQL", "Git", "RESTful APIs", "Microservices"],
                "secondary": ["Docker", "Linux", "PostgreSQL", "CI/CD", "Redis", "Unit Testing"],
                "soft": ["Problem Solving", "Teamwork", "Agile / Scrum", "Communication"]
            }
        elif "frontend" in role_lower:
            return {
                "core": ["JavaScript", "TypeScript", "React", "HTML5", "CSS3", "Tailwind CSS", "Git"],
                "secondary": ["Next.js", "Redux", "RESTful APIs", "WebSockets", "Webpack", "Postman"],
                "soft": ["Problem Solving", "Communication", "Teamwork", "Adaptability"]
            }
        elif "backend" in role_lower:
            return {
                "core": ["Python", "Node.js", "SQL", "PostgreSQL", "RESTful APIs", "Git", "Docker"],
                "secondary": ["FastAPI", "Django", "Express.js", "Redis", "Microservices", "Linux", "AWS"],
                "soft": ["Problem Solving", "Time Management", "Communication", "Agile / Scrum"]
            }
        elif "full stack" in role_lower:
            return {
                "core": ["JavaScript", "TypeScript", "React", "Node.js", "Python", "SQL", "HTML5", "CSS3", "Git"],
                "secondary": ["PostgreSQL", "MongoDB", "Docker", "RESTful APIs", "Tailwind CSS", "AWS", "CI/CD"],
                "soft": ["Problem Solving", "Adaptability", "Teamwork", "Communication"]
            }
        elif "data analyst" in role_lower:
            return {
                "core": ["Python", "SQL", "Pandas", "NumPy", "Excel", "Data Analysis", "Tableau", "Power BI"],
                "secondary": ["Matplotlib", "Seaborn", "Statistics", "PostgreSQL", "Jupyter"],
                "soft": ["Communication", "Problem Solving", "Critical Thinking", "Presentation"]
            }
        elif "data scientist" in role_lower:
            return {
                "core": ["Python", "SQL", "Pandas", "NumPy", "Scikit-learn", "Machine Learning", "Statistics"],
                "secondary": ["Deep Learning", "PyTorch", "TensorFlow", "Feature Engineering", "Matplotlib", "Jupyter"],
                "soft": ["Critical Thinking", "Problem Solving", "Communication", "Leadership"]
            }
        elif "machine learning" in role_lower or "ml intern" in role_lower or "ai" in role_lower:
            return {
                "core": ["Python", "Machine Learning", "Deep Learning", "PyTorch", "TensorFlow", "Scikit-learn", "NumPy", "Pandas"],
                "secondary": ["Natural Language Processing", "Computer Vision", "Transformers", "MLOps", "Git", "Docker", "Linux"],
                "soft": ["Problem Solving", "Adaptability", "Teamwork", "Communication"]
            }
        elif "python developer" in role_lower:
            return {
                "core": ["Python", "Django", "Flask", "FastAPI", "SQL", "PostgreSQL", "Git", "RESTful APIs"],
                "secondary": ["Docker", "Redis", "Celery", "Linux", "PyTest", "MongoDB"],
                "soft": ["Problem Solving", "Agile / Scrum", "Communication"]
            }
        elif "java developer" in role_lower:
            return {
                "core": ["Java", "Spring Boot", "SQL", "PostgreSQL", "MySQL", "RESTful APIs", "Git", "Maven"],
                "secondary": ["Microservices", "Docker", "Kubernetes", "Kafka", "Linux", "Hibernate"],
                "soft": ["Problem Solving", "Teamwork", "Agile / Scrum"]
            }
        elif "business analyst" in role_lower:
            return {
                "core": ["SQL", "Excel", "Data Analysis", "Tableau", "Power BI", "Jira", "Agile / Scrum"],
                "secondary": ["Python", "Statistics", "Communication", "Presentation"],
                "soft": ["Leadership", "Communication", "Problem Solving", "Time Management", "Critical Thinking"]
            }
        else:
            return {
                "core": ["Python", "SQL", "Git", "RESTful APIs"],
                "secondary": ["Docker", "Linux", "PostgreSQL"],
                "soft": ["Problem Solving", "Communication", "Teamwork"]
            }
