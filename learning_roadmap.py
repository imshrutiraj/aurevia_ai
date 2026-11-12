from typing import Dict, Any, List
from backend.skill_gap_analyzer import SkillGapAnalyzer

class LearningRoadmapGenerator:
    """
    Generates tailored, multi-tier learning roadmaps based on genuine candidate skill gaps,
    complete with weekly milestones, hands-on portfolio projects, and certification tracks.
    """

    ROADMAP_BLUEPRINTS = {
        "Software Development Engineer": {
            "beginner": [
                {"topic": "Data Structures & Complexity Analysis", "duration": "3 Weeks", "description": "Master arrays, hash maps, linked lists, trees, and Big-O asymptotic analysis."},
                {"topic": "Advanced OOP & Core Language Internals", "duration": "2 Weeks", "description": "Deep dive into memory management, generics, concurrency primitives in Java/C++/Python."}
            ],
            "intermediate": [
                {"topic": "Relational & NoSQL Database Optimization", "duration": "3 Weeks", "description": "Query execution plans, indexing strategies, normalization, Redis caching layers."},
                {"topic": "RESTful Microservice Architecture & Docker", "duration": "3 Weeks", "description": "Decomposing monoliths, building containerized services, Docker Compose, Postman testing."}
            ],
            "advanced": [
                {"topic": "Distributed Systems & Asynchronous Messaging", "duration": "4 Weeks", "description": "Event-driven design with Kafka/RabbitMQ, CAP theorem, eventual consistency, load balancers."},
                {"topic": "Cloud Deployment & Production CI/CD", "duration": "3 Weeks", "description": "Deploying Kubernetes clusters, automated GitHub Actions pipelines, Prometheus observability."}
            ],
            "projects": [
                {"title": "High-Throughput Distributed Rate Limiter", "skills": "Redis, Go/Python, Docker, Algorithms", "description": "Build a token-bucket distributed rate-limiting microservice handling 15,000 requests/sec."},
                {"title": "Real-time Collaborative Code Editor", "skills": "WebSockets, React, Node.js, Docker", "description": "Architect a multi-user simultaneous document editor with operational transformation."}
            ],
            "certifications": ["AWS Certified Developer - Associate", "CKAD: Certified Kubernetes Application Developer"]
        },
        "Frontend Developer": {
            "beginner": [
                {"topic": "Modern JavaScript (ES2024) & TypeScript Fundamentals", "duration": "2 Weeks", "description": "Closures, async/await, DOM APIs, type definitions, generics, interfaces."},
                {"topic": "Modern Responsive Layouts & Tailwind CSS", "duration": "2 Weeks", "description": "Mobile-first CSS Grid, Flexbox, accessible semantic markup, responsive design."}
            ],
            "intermediate": [
                {"topic": "React 19 & Component Architecture", "duration": "3 Weeks", "description": "Custom hooks, state management with Redux Toolkit / Zustand, memoization, lifecycle."},
                {"topic": "Next.js App Router & Server Components", "duration": "3 Weeks", "description": "SSR, SSG, client vs server components, SEO optimization, API routes."}
            ],
            "advanced": [
                {"topic": "Web Performance, Accessibility & Core Web Vitals", "duration": "3 Weeks", "description": "Bundle splitting, lazy loading, Lighthouse 100/100 audits, WCAG 2.1 AA compliance."},
                {"topic": "Automated Testing & Microfrontends", "duration": "2 Weeks", "description": "Component unit testing with Vitest/Jest, E2E testing with Playwright, Module Federation."}
            ],
            "projects": [
                {"title": "Enterprise Analytics Dashboard", "skills": "Next.js, TypeScript, Tailwind, Chart.js/Plotly", "description": "Build an interactive dark-mode SaaS dashboard with real-time filters and dynamic charts."},
                {"title": "Design System & Component Library", "skills": "React, Storybook, NPM, Accessibility", "description": "Publish a reusable headless UI design system with documentation and theme switching."}
            ],
            "certifications": ["Meta Front-End Developer Professional Certificate", "OpenJS Node.js Application Developer (JSNAD)"]
        },
        "Backend Developer": {
            "beginner": [
                {"topic": "API Design & REST Architectural Principles", "duration": "2 Weeks", "description": "HTTP verbs, status codes, OpenAPI/Swagger specifications, idempotent APIs."},
                {"topic": "Database Modeling & PostgreSQL", "duration": "3 Weeks", "description": "Complex joins, indexing, transactions (ACID), connection pooling, migrations."}
            ],
            "intermediate": [
                {"topic": "FastAPI / Node.js Production Backend", "duration": "3 Weeks", "description": "Async request handling, Pydantic validation, JWT authentication, middleware."},
                {"topic": "Caching & Message Queues", "duration": "3 Weeks", "description": "Redis pub/sub, background job processing with Celery/BullMQ, cache invalidation."}
            ],
            "advanced": [
                {"topic": "Microservices & Distributed Tracing", "duration": "4 Weeks", "description": "Service discovery, gRPC RPCs, circuit breaker pattern, OpenTelemetry tracing."},
                {"topic": "Security Hardening & Cloud Deployments", "duration": "3 Weeks", "description": "OWASP Top 10 mitigation, Docker multi-stage builds, AWS ECS/Fargate deployment."}
            ],
            "projects": [
                {"title": "Scalable Video Transcoding Pipeline", "skills": "Python/Go, Celery, Redis, FFmpeg, AWS S3", "description": "Asynchronous backend that accepts video uploads, segments them into HLS streams, and uploads to S3."},
                {"title": "Financial Transaction Processing Service", "skills": "PostgreSQL, Docker, ACID Transactions, Unit Tests", "description": "Build an idempotent double-entry bookkeeping ledger API with audit trails."}
            ],
            "certifications": ["AWS Certified Solutions Architect - Associate", "HashiCorp Certified: Terraform Associate"]
        },
        "Data Analyst": {
            "beginner": [
                {"topic": "Advanced SQL & Relational Queries", "duration": "3 Weeks", "description": "Window functions, Common Table Expressions (CTEs), subqueries, aggregations."},
                {"topic": "Excel Modeling & Pivot Tables", "duration": "2 Weeks", "description": "VLOOKUP/XLOOKUP, index-match, financial formulas, executive charts."}
            ],
            "intermediate": [
                {"topic": "Python Data Manipulation with Pandas & NumPy", "duration": "3 Weeks", "description": "Cleaning messy data, reshaping dataframes, date-time parsing, merging datasets."},
                {"topic": "Business Intelligence with Tableau & Power BI", "duration": "3 Weeks", "description": "Calculated fields, parameters, interactive executive dashboards, DAX queries."}
            ],
            "advanced": [
                {"topic": "Exploratory Data Analysis & Statistical Testing", "duration": "3 Weeks", "description": "Hypothesis testing, p-values, correlation vs causation, A/B experiment design."},
                {"topic": "Data Storytelling & Executive Presentations", "duration": "2 Weeks", "description": "Synthesizing analytical metrics into actionable business recommendations."}
            ],
            "projects": [
                {"title": "Customer Retention & Churn BI Dashboard", "skills": "Tableau, SQL, Pandas", "description": "Analyzed cohort retention for an e-commerce platform and highlighted revenue leakage factors."},
                {"title": "Automated ETL Pipeline & KPI Reporting", "skills": "Python, SQLite, Power BI", "description": "Engineered daily automated data aggregation script replacing 10 hours of manual work."}
            ],
            "certifications": ["Google Data Analytics Professional Certificate", "Microsoft Certified: Power BI Data Analyst Associate"]
        },
        "Machine Learning Engineer": {
            "beginner": [
                {"topic": "Mathematics for ML: Linear Algebra & Calculus", "duration": "3 Weeks", "description": "Vector spaces, matrix decomposition, partial derivatives, gradient descent."},
                {"topic": "Scikit-learn & Statistical Learning", "duration": "3 Weeks", "description": "Classification, regression, cross-validation, regularization (L1/L2), hyperparameter tuning."}
            ],
            "intermediate": [
                {"topic": "Deep Learning Fundamentals with PyTorch", "duration": "4 Weeks", "description": "Tensors, autograd, backpropagation, CNNs for computer vision, RNNs/LSTMs."},
                {"topic": "Natural Language Processing & Transformers", "duration": "4 Weeks", "description": "Self-attention mechanisms, HuggingFace library, fine-tuning BERT and Sentence Transformers."}
            ],
            "advanced": [
                {"topic": "MLOps: Model Deployment & Monitoring", "duration": "3 Weeks", "description": "Packaging models into FastAPI microservices, Dockerizing inference, MLflow tracking."},
                {"topic": "LLMs & Retrieval-Augmented Generation (RAG)", "duration": "3 Weeks", "description": "Vector databases (Chroma/FAISS), prompt engineering, LangChain integration."}
            ],
            "projects": [
                {"title": "End-to-End Semantic Search & Recommendation Engine", "skills": "PyTorch, Sentence Transformers, FastAPI, Docker", "description": "Trained and deployed a dual-encoder semantic search system across 50,000 articles."},
                {"title": "Computer Vision Defect Detection Pipeline", "skills": "OpenCV, PyTorch, YOLO, Flask", "description": "Implemented automated image segmentation model with 94% precision."}
            ],
            "certifications": ["TensorFlow Developer Certificate", "DeepLearning.AI Machine Learning Specialization", "AWS Certified Machine Learning - Specialty"]
        }
    }

    @classmethod
    def generate_roadmap(cls, candidate_skills: List[str], target_role: str) -> Dict[str, Any]:
        # Identify default blueprint
        blueprint = cls.ROADMAP_BLUEPRINTS.get(target_role)
        if not blueprint:
            # Fallback to Software Development Engineer blueprint
            blueprint = cls.ROADMAP_BLUEPRINTS["Software Development Engineer"]

        # Run skill gap analysis to tailor the roadmap
        gap_results = SkillGapAnalyzer.analyze_gaps(candidate_skills, target_role)
        missing_core = gap_results["missing_core_skills"]

        # Calculate estimated total duration
        total_weeks = 18

        return {
            "target_role": target_role,
            "estimated_duration": f"{total_weeks} Weeks",
            "weekly_commitment": "10-15 Hours / Week",
            "skill_gaps_addressed": missing_core[:5],
            "levels": {
                "beginner": {
                    "level_title": "Level 1: Foundations & Core Competencies",
                    "milestones": blueprint["beginner"]
                },
                "intermediate": {
                    "level_title": "Level 2: Systems, Frameworks & Implementation",
                    "milestones": blueprint["intermediate"]
                },
                "advanced": {
                    "level_title": "Level 3: Architecture, Optimization & Production",
                    "milestones": blueprint["advanced"]
                }
            },
            "recommended_projects": blueprint["projects"],
            "target_certifications": blueprint["certifications"]
        }
