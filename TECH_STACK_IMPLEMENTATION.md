# TECH_STACK_IMPLEMENTATION.md
## Aurevia AI: Resume Analyzer & Career Intelligence Platform
### Exhaustive Technology Stack Compliance & Verification Audit

This document details the genuine, verified implementation of every required technology across the Aurevia AI Career Intelligence Platform.

---

### 1. HTML5
* **Where Implemented:** Frontend structure and UI templating.
* **Files:** `frontend/templates/index.html`.
* **Functionality Provided:** Semantic structural elements (`<header>`, `<nav>`, `<section>`, `<main>`, `<footer>`, `<article>`, `<canvas>`), file input controls with drag-and-drop support, form inputs for roles and job postings, modal containers, and accessibility attributes (`role="status"`, `aria-label`).
* **Contribution to Project:** Houses the unified single-page interface for all nine core modules and extra career intelligence tools.

---

### 2. CSS3
* **Where Implemented:** Styling, responsive grids, and 3D visual physics.
* **Files:** `frontend/static/css/style.css`.
* **Functionality Provided:** Custom CSS variables (`:root`), glassmorphism cards (`backdrop-filter: blur`), responsive CSS grids (`grid-template-columns`), 3D spatial transforms (`perspective: 900px`, `transform-style: preserve-3d`), keyframe animations (`@keyframes morph`, `@keyframes orbit`, `@keyframes levitate`, `@keyframes starsMove`), and mobile media queries.
* **Contribution to Project:** Gives Aurevia AI a modern SaaS aesthetic, dark celestial theme, and responsive interface across desktop, tablet, and mobile.

---

### 3. JavaScript (Vanilla ES6+)
* **Where Implemented:** Client-side orchestration and asynchronous API communication.
* **Files:** `frontend/static/js/script.js`.
* **Functionality Provided:** Asynchronous `fetch()` API calls to Flask endpoints, drag-and-drop file ingestion, dynamic DOM updates across all 9 modules without page reload, Plotly chart rendering, interactive mock interview evaluation triggers, copy-to-clipboard utilities, and 3D mousemove perspective tilt.
* **Contribution to Project:** Enables full full-stack interoperability between the browser and the Python backend without third-party frontend frameworks.

---

### 4. Python (3.11 - 3.14)
* **Where Implemented:** Entire server-side application logic, data ingestion, and AI pipelines.
* **Files:** `app.py`, `config.py`, and all files in `backend/`, `database/`, `ml_models/`, `visualizations/`, `tests/`.
* **Functionality Provided:** Clean object-oriented architecture, type hinting, error handling, file system management, mathematical computations, and data pipeline execution.
* **Contribution to Project:** Serves as the central programming language powering the entire backend ecosystem.

---

### 5. Flask
* **Where Implemented:** RESTful API web framework and server routing.
* **Files:** `app.py`, `config.py`.
* **Functionality Provided:** Application routing, request entity size validation (16MB max upload limit), JSON serialization (`jsonify`), multipart form handling (`request.files`), and serving the HTML template and static assets.
* **Contribution to Project:** Exposes clean modular REST endpoints connecting the frontend UI to backend machine learning and NLP engines.

---

### 6. Pandas
* **Where Implemented:** Structured tabular data manipulation and dataset augmentation.
* **Files:** `ml_models/train_model.py`, `backend/skill_gap_analyzer.py`.
* **Functionality Provided:** Reading and processing CSV datasets, stratified sampling, dataframe filtering, group-by aggregations, value count distribution audits, and exporting training records.
* **Contribution to Project:** Manages the resume-role training dataset and structures tabular career insights.

---

### 7. NumPy
* **Where Implemented:** Mathematical array operations, vector transformations, and distance metrics.
* **Files:** `backend/similarity_engine.py`, `backend/embedding_engine.py`, `ml_models/train_model.py`, `visualizations/charts.py`.
* **Functionality Provided:** Vector dot products, Euclidean L2 norms, array slicing, clipping numerical ranges (`np.clip`), and ranking probability indices (`np.argsort`).
* **Contribution to Project:** Delivers fast vector math operations for cosine similarity and embedding evaluations.

---

### 8. NLTK (Natural Language Toolkit)
* **Where Implemented:** Text preprocessing, tokenization, and stopword filtration.
* **Files:** `backend/text_preprocessing.py`, `backend/nlp_processor.py`.
* **Functionality Provided:** Text cleaning, boundary-preserving tokenization (retaining programming symbols like `C++`, `C#`, `.NET`), case normalization, and stopwords removal with zero-downtime offline fallback dictionary.
* **Contribution to Project:** Prepares clean, normalized textual representations for TF-IDF vectorization and entity extraction.

---

### 9. spaCy
* **Where Implemented:** Named Entity Recognition (NER) and structural linguistical parsing.
* **Files:** `backend/nlp_processor.py`, `requirements.txt`.
* **Functionality Provided:** Identifying organizations, degrees, person names, and semantic syntactic patterns from resume text.
* **Contribution to Project:** Accurately isolates candidate names, companies, and educational entities from unstructured resume text.

---

### 10. Scikit-learn
* **Where Implemented:** Machine Learning classification, TF-IDF vectorization, and model evaluation metrics.
* **Files:** `ml_models/train_model.py`, `backend/job_predictor.py`, `backend/similarity_engine.py`.
* **Functionality Provided:** 
  - `TfidfVectorizer` with sublinear term-frequency scaling and unigram/bigram ranges.
  - `LogisticRegression` multi-class classifier with balanced class weighting.
  - Stratified train-test splitting (`train_test_split`).
  - Quantitative evaluation (`accuracy_score`, `precision_recall_fscore_support`, `classification_report`, `confusion_matrix`).
  - Model serialization and persistence via `joblib`.
* **Contribution to Project:** Drives Module 3 (Job Match Explorer), evaluating candidate qualifications against 11 industry career profiles and computing cosine similarity.

---

### 11. Sentence Transformers
* **Where Implemented:** Semantic embedding generation and deep conceptual similarity.
* **Files:** `backend/embedding_engine.py`, `backend/mock_interview.py`.
* **Functionality Provided:** Produces dense 384-dimensional vector embeddings using the `all-MiniLM-L6-v2` architecture, computes semantic cosine proximity between candidate interview answers and benchmark answers, and incorporates an offline morphological subword fallback vectorizer for unhindered operation in air-gapped environments.
* **Contribution to Project:** Enables Module 7 (AI Mock Interview) to evaluate answer relevance and concept coverage beyond verbatim keyword matching.

---

### 12. pdfplumber
* **Where Implemented:** PDF document ingestion and text extraction.
* **Files:** `backend/resume_parser.py`.
* **Functionality Provided:** Page-by-page extraction of text streams, coordinate preservation, layout reconstruction, and header validation (`%PDF` magic byte detection).
* **Contribution to Project:** Powers Module 1 (Resume Intelligence), transforming uploaded PDF resumes into clean, processable text.

---

### 13. python-docx
* **Where Implemented:** Microsoft Word DOCX resume parsing and table extraction.
* **Files:** `backend/resume_parser.py`.
* **Functionality Provided:** Reading paragraphs, inline text runs, structured table cells (`table.rows`), and zip format validation (`PK` header check).
* **Contribution to Project:** Ensures full cross-format compatibility by enabling DOCX resume uploads alongside PDFs.

---

### 14. SQLite
* **Where Implemented:** Relational database storage and persistence.
* **Files:** `database/db.py`, `database/models.py`.
* **Functionality Provided:** Relational schema design with foreign key constraints (`PRAGMA foreign_keys = ON`), parameterized SQL queries preventing injection, and structured tables:
  - `resumes`: Raw text, candidate contact info, extracted skills JSON.
  - `analyses`: ATS score, breakdown, matched/missing skills, predicted roles, roadmap JSON.
  - `mock_interviews`: Questions, candidate answers, scores, constructive feedback.
  - `cover_letters`: Generated letters and customization criteria.
  - `roadmap_tracker`: Progress tracking across milestones.
* **Contribution to Project:** Persists user analyses, allows historical review, enables re-use of uploaded resumes without re-uploading, and allows deletion of stored records.

---

### 15. Matplotlib
* **Where Implemented:** Server-side graphic generation and publication-ready charting.
* **Files:** `visualizations/charts.py`.
* **Functionality Provided:** Generates custom high-resolution pie charts (`plt.pie`) using the Agg non-interactive backend, custom color grading matching the Aurevia palette (`#D6B77A`, `#B8A5E8`, `#141A2B`), and exports base64-encoded PNG image strings.
* **Contribution to Project:** Embeds visual charts directly into reports and provides downloadable visuals for reports.

---

### 16. Plotly
* **Where Implemented:** Interactive web charting.
* **Files:** `visualizations/charts.py`, `frontend/templates/index.html`, `frontend/static/js/script.js`.
* **Functionality Provided:** Generates interactive JSON chart specifications:
  - Plotly Gauge chart (`go.Indicator`) for ATS compatibility.
  - Plotly Bar chart (`go.Bar`) for top 5 predicted career role suitabilities.
* **Contribution to Project:** Renders interactive, responsive charts on the client-side Career Dashboard via `Plotly.js`.

---

### 17. Docker
* **Where Implemented:** Containerization and reproducible deployment specification.
* **Files:** `Dockerfile`, `.dockerignore`.
* **Functionality Provided:** Multi-stage container packaging based on `python:3.11-slim`, automated dependency installation, NLTK corpus setup, model pre-compilation, and health check monitoring.
* **Contribution to Project:** Guarantees environment parity between local development and production cloud environments.

---

### 18. Render
* **Where Implemented:** Cloud web service deployment configuration.
* **Documentation & Config:** `README.md`, `render.yaml`.
* **Functionality Provided:** Docker runtime environment, automatic build triggers, custom domain configuration, persistent environment variable injection (`PORT=10000`, `SECRET_KEY`).
* **Contribution to Project:** Provides a verified platform for deploying the containerized Flask application.

---

### 19. Railway
* **Where Implemented:** Cloud PaaS deployment configuration.
* **Documentation & Config:** `README.md`, `Procfile`.
* **Functionality Provided:** Automated Git deployment, Dockerfile detection, persistent volume attachment for `/app/database`, and dynamic port binding (`$PORT`).
* **Contribution to Project:** Provides a continuous-deployment cloud hosting option with zero manual infrastructure configuration.

---

### 20. AWS (Elastic Beanstalk / ECS / EC2)
* **Where Implemented:** Enterprise cloud hosting architecture and deployment guidance.
* **Documentation:** `README.md`.
* **Functionality Provided:** Architecture guidance for deploying Aurevia AI using AWS ECS (Fargate) with ECR container registries, Application Load Balancers (ALB), and S3/EFS persistent storage.
* **Contribution to Project:** Outlines production-ready, highly available enterprise scalability paths.
