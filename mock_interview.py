import random
from typing import Dict, Any, List
from backend.embedding_engine import EmbeddingEngine
from backend.skill_extractor import SkillExtractor

class MockInterviewEngine:
    """
    AI Mock Interview Engine generating dynamic technical, behavioral, and HR interview questions
    tailored to the candidate's actual resume skills and target role, evaluating answers using
    semantic embedding analysis and providing constructive feedback with model benchmark answers.
    """

    QUESTION_BANK = {
        "technical": [
            {
                "skill": "Python",
                "question": "Can you explain the difference between Python's threading and multiprocessing modules, and how does the Global Interpreter Lock (GIL) impact CPU-bound tasks?",
                "key_concepts": ["GIL", "CPU-bound vs I/O-bound", "shared memory", "separate process space", "multiprocessing bypasses GIL"],
                "model_answer": "In CPython, the GIL ensures only one thread executes Python bytecode at a time, making standard threading ideal for I/O-bound tasks (like network calls or disk reads) but ineffective for CPU-heavy tasks. Multiprocessing bypasses the GIL by spawning separate processes, each with its own Python interpreter and memory space, enabling true parallelism across multi-core processors."
            },
            {
                "skill": "SQL",
                "question": "What is the difference between an INNER JOIN, LEFT JOIN, and how do database indexes speed up query performance?",
                "key_concepts": ["INNER JOIN matches both tables", "LEFT JOIN preserves left table rows", "B-Tree index", "O(log N) lookup", "avoids full table scan"],
                "model_answer": "An INNER JOIN returns only records where there is a match in both joined tables, whereas a LEFT JOIN returns all rows from the left table and matched rows from the right (or NULL if no match). Indexes, typically organized as B-Trees, provide balanced pointers to table rows, converting an O(N) full table scan into an O(log N) search on indexed columns."
            },
            {
                "skill": "React",
                "question": "How does React's Virtual DOM reconciliation algorithm work, and why are 'key' props essential when rendering dynamic lists?",
                "key_concepts": ["Virtual DOM", "Diffing algorithm", "keys track element identity", "prevents re-rendering entire list", "reconciliation"],
                "model_answer": "React maintains a lightweight Virtual DOM tree in memory. When state updates occur, it creates a new Virtual DOM tree and runs a diffing heuristic against the previous tree (reconciliation) to identify the minimum set of real DOM mutations. The 'key' prop gives each list item a stable identity, allowing React to match existing elements rather than re-creating and re-rendering all nodes when the order changes."
            },
            {
                "skill": "Docker",
                "question": "What is the distinction between a Docker image and a Docker container, and how do multi-stage builds help optimize production deployments?",
                "key_concepts": ["image is read-only template", "container is running instance", "multi-stage build", "smaller image size", "excludes build dependencies"],
                "model_answer": "A Docker image is an immutable, read-only template containing the application code, runtime, and libraries. A container is a runnable, isolated instance of that image with a read-write layer. Multi-stage builds allow developers to compile and build code in an initial stage (with heavy compilers/SDKs) and copy only the final binary into a lightweight minimal production image (like Alpine or distroless), slashing image size and reducing security vulnerabilities."
            },
            {
                "skill": "Machine Learning",
                "question": "Can you explain the Bias-Variance tradeoff and how regularization techniques (L1 vs L2) prevent overfitting?",
                "key_concepts": ["bias is underfitting", "variance is overfitting", "L1 Lasso feature selection", "L2 Ridge coefficient shrinkage", "generalization"],
                "model_answer": "High bias leads to underfitting due to overly simplistic assumptions, while high variance leads to overfitting by capturing noise in the training set. The goal is to minimize total generalization error. Regularization adds a penalty to the loss function: L1 (Lasso) adds the absolute values of coefficients, pushing uninformative weights to zero (performing feature selection), while L2 (Ridge) adds the squared values, penalizing extreme magnitudes without setting them strictly to zero."
            },
            {
                "skill": "System Design",
                "question": "How would you design a distributed caching layer for an API experiencing high read latency, and how do you handle cache invalidation?",
                "key_concepts": ["Redis / Memcached", "Cache-Aside pattern", "Write-Through", "TTL expiration", "Cache stampede / Cache penetration"],
                "model_answer": "I would place an in-memory distributed store like Redis cluster between the application and database, adopting the Cache-Aside pattern. On a read miss, data is fetched from the database and written to the cache with an appropriate TTL. For updates, I'd implement explicit cache invalidation or Write-Through caching. To mitigate cache stampedes on popular keys, we can use mutex locks or soft expiration."
            }
        ],
        "behavioral": [
            {
                "category": "STAR Behavioral",
                "question": "Tell me about a time when you encountered a severe bug or outage in a project. How did you diagnose and resolve it under pressure?",
                "key_concepts": ["Situation", "Task", "Action", "Result", "root cause analysis", "debugging", "post-mortem / lessons learned"],
                "model_answer": "Structure your response using the STAR method: Clearly outline the Situation (the production incident), your Task (your specific ownership), the systematic Action you took (monitoring logs, isolating the commit, rolling back or hot-patching, writing unit tests to prevent regression), and the quantifiable Result (restored uptime in 20 minutes, added monitoring alert, documented post-mortem)."
            },
            {
                "category": "STAR Behavioral",
                "question": "Describe a scenario where you disagreed with a teammate or technical lead regarding an architectural decision. How did you resolve the conflict?",
                "key_concepts": ["active listening", "data-driven arguments", "benchmarking / prototyping", "consensus", "disagree and commit"],
                "model_answer": "Highlight emotional intelligence and data-driven debate: Explain how you listened to the other perspective, created a quick proof-of-concept (POC) or performance benchmark to evaluate both solutions objectively, discussed trade-offs openly, and either reached mutual agreement or committed wholeheartedly to the team decision."
            }
        ],
        "hr": [
            {
                "category": "HR & Culture",
                "question": "Why are you interested in this specific career path, and where do you see your technical competencies evolving over the next 2-3 years?",
                "key_concepts": ["passion for solving problems", "continuous learning", "mentorship / leadership", "mastering scalable engineering"],
                "model_answer": "Express genuine enthusiasm for solving complex technical problems at scale. Articulate a clear growth plan: solidifying your mastery of production architecture, contributing to high-impact systems, deepening domain expertise, and actively collaborating with or mentoring teammates."
            },
            {
                "category": "HR & Culture",
                "question": "How do you prioritize competing deadlines and manage your time when multiple high-priority tickets or tasks arrive simultaneously?",
                "key_concepts": ["Eisenhower matrix", "business impact", "communicating with stakeholders", "agile sprints", "re-estimating"],
                "model_answer": "Explain that you evaluate tasks by urgency and business impact, communicate proactively with product managers or leads when scope needs adjustments, break work into milestones, and leverage agile tools to maintain transparency without compromising code quality."
            }
        ]
    }

    @classmethod
    def generate_interview_questions(cls, candidate_skills: List[str], target_role: str, count: int = 5) -> List[Dict[str, Any]]:
        questions = []
        c_skills_lower = [s.lower() for s in candidate_skills]

        # 1. Match technical questions with candidate's actual skills
        matched_tech = []
        for q in cls.QUESTION_BANK["technical"]:
            if q["skill"].lower() in c_skills_lower or any(q["skill"].lower() in s for s in c_skills_lower):
                matched_tech.append(q)

        # If not enough matches, add general technical questions
        if len(matched_tech) < 3:
            for q in cls.QUESTION_BANK["technical"]:
                if q not in matched_tech:
                    matched_tech.append(q)

        selected_tech = matched_tech[:3]
        for item in selected_tech:
            questions.append({
                "category": f"Technical ({item['skill']})",
                "question": item["question"],
                "key_concepts": item["key_concepts"],
                "model_answer": item["model_answer"]
            })

        # 2. Add 1 Behavioral Question
        behavioral_q = random.choice(cls.QUESTION_BANK["behavioral"])
        questions.append({
            "category": "Behavioral (STAR Method)",
            "question": behavioral_q["question"],
            "key_concepts": behavioral_q["key_concepts"],
            "model_answer": behavioral_q["model_answer"]
        })

        # 3. Add 1 HR Question
        hr_q = random.choice(cls.QUESTION_BANK["hr"])
        questions.append({
            "category": "HR & Culture Fit",
            "question": hr_q["question"],
            "key_concepts": hr_q["key_concepts"],
            "model_answer": hr_q["model_answer"]
        })

        return questions[:count]

    @classmethod
    def evaluate_answer(cls, question: str, user_answer: str, key_concepts: List[str], model_answer: str) -> Dict[str, Any]:
        """
        Evaluates candidate answer using semantic similarity and concept coverage.
        """
        res = EmbeddingEngine.evaluate_answer_semantics(user_answer, key_concepts, model_answer)

        # Generate constructive feedback
        feedback_lines = []
        if res["overall_score"] >= 80:
            feedback_lines.append("Excellent, comprehensive answer! You clearly demonstrated strong grasp of core concepts.")
        elif res["overall_score"] >= 60:
            feedback_lines.append("Good response with solid foundational reasoning. You touched upon important aspects.")
        else:
            feedback_lines.append("Your response has potential, but needs more depth, technical precision, and structured examples.")

        if res["covered_concepts"]:
            feedback_lines.append(f"Strongly articulated concepts: {', '.join(res['covered_concepts'])}.")
        if res["missed_concepts"]:
            feedback_lines.append(f"Key technical areas to incorporate: {', '.join(res['missed_concepts'])}.")

        return {
            "relevance_score": res["relevance_score"],
            "clarity_score": res["clarity_score"],
            "overall_score": res["overall_score"],
            "covered_concepts": res["covered_concepts"],
            "missed_concepts": res["missed_concepts"],
            "feedback": " ".join(feedback_lines),
            "model_answer": model_answer
        }
