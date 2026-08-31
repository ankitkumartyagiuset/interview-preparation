import re
import json
from typing import Dict, Any, Optional, List
from backend.app.ai.providers.base import AIProvider

class MockProvider(AIProvider):
    """
    Intelligent, deterministic heuristic AI provider for offline testing and development.
    Analyzes prompt context, extracts real entities from resumes and JDs,
    evaluates answers using multi-dimensional rubrics, and dynamically generates next steps.
    """

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 1500
    ) -> str:
        prompt_lower = prompt.lower()
        if "summary" in prompt_lower:
            return "Candidate demonstrates strong technical foundational knowledge with notable clarity in system design concepts, but would benefit from deepening practical hands-on experience in distributed database indexing and high-concurrency caching."
        return "Assessment completed successfully based on job requirements and candidate responses."

    async def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        schema: Optional[Dict[str, Any]] = None,
        temperature: float = 0.1,
        max_tokens: int = 2000
    ) -> Dict[str, Any]:
        prompt_lower = prompt.lower()
        
        # 1. Resume Extraction Prompt
        if "extract structured information from this resume" in prompt_lower or "candidate profile" in prompt_lower:
            return self._mock_resume_extraction(prompt)
            
        # 2. Job Description Analysis Prompt
        elif "analyze the following job description" in prompt_lower or "job profile" in prompt_lower:
            return self._mock_jd_analysis(prompt)
            
        # 3. Interview Planning Prompt
        elif "interview blueprint" in prompt_lower or "interview plan" in prompt_lower:
            return self._mock_interview_plan(prompt)
            
        # 4. Question Generation Prompt
        elif "generate the next interview question" in prompt_lower or "interview question" in prompt_lower:
            return self._mock_question_generation(prompt)
            
        # 5. Follow-up Generation Prompt
        elif "follow-up" in prompt_lower or "generate follow-up" in prompt_lower:
            return self._mock_follow_up_generation(prompt)
            
        # 6. Answer Evaluation Prompt
        elif "evaluate the candidate's answer" in prompt_lower or "evaluation rubric" in prompt_lower:
            return self._mock_answer_evaluation(prompt)
            
        # 7. Skill Gap Analysis Prompt
        elif "skill gap" in prompt_lower or "claimed skills vs demonstrated" in prompt_lower:
            return self._mock_skill_gap_analysis(prompt)
            
        # 8. Roadmap Generation Prompt
        elif "improvement roadmap" in prompt_lower or "7-day learning" in prompt_lower:
            return self._mock_roadmap_generation(prompt)
            
        # 9. Final Report Prompt
        elif "final interview report" in prompt_lower or "readiness report" in prompt_lower:
            return self._mock_final_report(prompt)

        return {"status": "success", "message": "Structured output generated successfully"}

    def _mock_resume_extraction(self, prompt: str) -> Dict[str, Any]:
        # Extract keywords from raw text in prompt
        skills = []
        known_skills = [
            ("Python", "programming", "advanced"),
            ("FastAPI", "framework", "intermediate"),
            ("Django", "framework", "advanced"),
            ("SQL", "database", "intermediate"),
            ("PostgreSQL", "database", "intermediate"),
            ("Docker", "cloud", "intermediate"),
            ("Redis", "database", "intermediate"),
            ("JavaScript", "programming", "intermediate"),
            ("React", "framework", "intermediate"),
            ("Git", "tool", "advanced"),
            ("AWS", "cloud", "beginner"),
            ("REST APIs", "architecture", "advanced"),
            ("Microservices", "architecture", "intermediate"),
            ("Celery", "framework", "intermediate")
        ]
        
        for name, cat, level in known_skills:
            if name.lower() in prompt.lower():
                skills.append({
                    "skill_name": name,
                    "category": cat,
                    "claimed_level": level,
                    "years_of_exp": 3.0 if level == "advanced" else 2.0,
                    "context_evidence": f"Mentioned in projects/work experience with {name}."
                })
        
        if not skills:
            skills = [
                {"skill_name": "Python", "category": "programming", "claimed_level": "advanced", "years_of_exp": 3.0, "context_evidence": "Built multiple web services"},
                {"skill_name": "FastAPI", "category": "framework", "claimed_level": "intermediate", "years_of_exp": 2.0, "context_evidence": "Engineered REST APIs"},
                {"skill_name": "PostgreSQL", "category": "database", "claimed_level": "intermediate", "years_of_exp": 2.5, "context_evidence": "Database schema modeling"},
                {"skill_name": "Docker", "category": "cloud", "claimed_level": "intermediate", "years_of_exp": 2.0, "context_evidence": "Containerized services"}
            ]

        # Extract projects
        projects = [
            {
                "title": "E-Commerce Microservices Engine",
                "role": "Lead Backend Developer",
                "description": "Designed and deployed event-driven checkout and inventory microservices handling 10,000+ daily orders.",
                "tech_stack_json": ["Python", "FastAPI", "PostgreSQL", "Redis", "Docker"],
                "achievements_json": [
                    "Reduced p99 API response latency from 450ms to 85ms using Redis caching",
                    "Implemented idempotent webhook delivery system with 99.99% reliability"
                ],
                "url": "https://github.com/candidate/ecommerce-backend"
            },
            {
                "title": "Real-time Telemetry & Analytics Dashboard",
                "role": "Full Stack Engineer",
                "description": "Built real-time metric ingestion pipelines and interactive visual dashboards for IoT sensor telemetry.",
                "tech_stack_json": ["Python", "WebSockets", "React", "PostgreSQL"],
                "achievements_json": [
                    "Streamed 500+ events/sec using asynchronous WebSockets",
                    "Integrated automated data backup pipelines"
                ],
                "url": "https://github.com/candidate/telemetry-portal"
            }
        ]

        experiences = [
            {
                "company": "TechNova Solutions",
                "title": "Backend Software Engineer",
                "location": "San Francisco, CA (Remote)",
                "start_date": "2022-01",
                "end_date": "Present",
                "is_current": True,
                "responsibilities_json": [
                    "Spearheaded backend architecture for SaaS customer portals using FastAPI and PostgreSQL",
                    "Optimized database queries, reducing query execution time by 40%",
                    "Mentored junior engineers and led sprint planning and code reviews"
                ]
            }
        ]

        education = [
            {
                "institution": "State University of Technology",
                "degree": "Bachelor of Science in Computer Science",
                "field_of_study": "Computer Science & Engineering",
                "graduation_year": "2021",
                "gpa": "3.8 / 4.0"
            }
        ]

        certifications = [
            {
                "name": "AWS Certified Solutions Architect – Associate",
                "issuer": "Amazon Web Services",
                "issue_date": "2023-05",
                "credential_id": "AWS-PSA-88912"
            }
        ]

        # Extract name if present
        name_match = re.search(r"(?:name|candidate):\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)", prompt, re.IGNORECASE)
        candidate_name = name_match.group(1) if name_match else "Alex Mercer"

        return {
            "full_name": candidate_name,
            "email": "alex.mercer@example.com",
            "phone": "+1 (555) 234-5678",
            "headline": "Senior Python Backend & Cloud Architecture Engineer",
            "summary": "Results-driven Software Engineer with 3+ years of experience engineering scalable microservices, REST APIs, and event-driven backends using Python, FastAPI, and PostgreSQL.",
            "total_experience_years": 3.5,
            "education_json": education,
            "skills": skills,
            "projects": projects,
            "experiences": experiences,
            "certifications": certifications
        }

    def _mock_jd_analysis(self, prompt: str) -> Dict[str, Any]:
        return {
            "title": "Senior Python Backend Engineer",
            "seniority": "senior",
            "experience_years_required": 3.0,
            "required_skills_json": [
                {"name": "Python", "level": "advanced", "category": "programming"},
                {"name": "FastAPI", "level": "advanced", "category": "framework"},
                {"name": "PostgreSQL", "level": "advanced", "category": "database"},
                {"name": "Docker", "level": "intermediate", "category": "cloud"},
                {"name": "System Design", "level": "advanced", "category": "architecture"}
            ],
            "preferred_skills_json": [
                {"name": "Redis", "level": "intermediate", "category": "database"},
                {"name": "Celery", "level": "intermediate", "category": "framework"},
                {"name": "Kubernetes", "level": "intermediate", "category": "cloud"},
                {"name": "AWS", "level": "intermediate", "category": "cloud"}
            ],
            "responsibilities_json": [
                "Design, build, and maintain high-throughput backend APIs and services",
                "Architect resilient database schemas and perform query optimization",
                "Collaborate across cross-functional product and frontend engineering teams",
                "Implement automated CI/CD deployment pipelines and maintain test coverage"
            ]
        }

    def _mock_interview_plan(self, prompt: str) -> Dict[str, Any]:
        return {
            "title": "Python Backend & Architecture Technical Assessment",
            "total_questions": 5,
            "difficulty": "intermediate",
            "blueprint_json": {
                "technical_weight": 30,
                "project_weight": 20,
                "problem_solving_weight": 20,
                "communication_weight": 10,
                "behavioral_weight": 10,
                "role_specific_weight": 10
            },
            "topics": ["Python Concurrency & Memory", "Database Indexing & Transactions", "Microservice Project Architecture", "Error Handling & Idempotency", "System Scalability"]
        }

    def _mock_question_generation(self, prompt: str) -> Dict[str, Any]:
        # Sequence-based question bank logic
        if "sequence: 1" in prompt or "sequence_num\": 1" in prompt or "first question" in prompt.lower():
            return {
                "sequence_num": 1,
                "category": "technical",
                "target_skill": "Python",
                "difficulty": "intermediate",
                "question_text": "How does Python handle asynchronous concurrency with asyncio under the hood, and when would you choose multi-threading or multi-processing over async coroutines?",
                "context_rationale": "Validates candidate's claimed advanced knowledge of Python concurrency paradigms.",
                "is_follow_up": False
            }
        elif "sequence: 2" in prompt or "sequence_num\": 2" in prompt:
            return {
                "sequence_num": 2,
                "category": "project",
                "target_skill": "FastAPI",
                "difficulty": "advanced",
                "question_text": "In your 'E-Commerce Microservices Engine' project, how did you implement cache invalidation and ensure data consistency between PostgreSQL and Redis during high write traffic?",
                "context_rationale": "Deep-dives into candidate's actual architectural implementation and trade-off decisions.",
                "is_follow_up": False
            }
        elif "sequence: 3" in prompt or "sequence_num\": 3" in prompt:
            return {
                "sequence_num": 3,
                "category": "technical",
                "target_skill": "PostgreSQL",
                "difficulty": "advanced",
                "question_text": "Explain the difference between B-tree and GIN indexes in PostgreSQL. What index strategy would you choose for full-text search versus range queries on timestamp columns, and why?",
                "context_rationale": "Validates database depth and indexing selection capability.",
                "is_follow_up": False
            }
        elif "sequence: 4" in prompt or "sequence_num\": 4" in prompt:
            return {
                "sequence_num": 4,
                "category": "problem_solving",
                "target_skill": "System Design",
                "difficulty": "advanced",
                "question_text": "Suppose a third-party payment gateway sends webhook notifications that may arrive duplicated, out of order, or delayed. How would you design a robust, idempotent webhook receiver in FastAPI?",
                "context_rationale": "Tests real-world defensive engineering and distributed systems reliability.",
                "is_follow_up": False
            }
        else:
            return {
                "sequence_num": 5,
                "category": "behavioral",
                "target_skill": "Communication",
                "difficulty": "intermediate",
                "question_text": "Describe a scenario where you disagreed with a senior engineer or product manager on a technical architecture decision. How did you articulate trade-offs and reach a consensus?",
                "context_rationale": "Evaluates professional communication, teamwork, and rational conflict resolution.",
                "is_follow_up": False
            }

    def _mock_follow_up_generation(self, prompt: str) -> Dict[str, Any]:
        return {
            "is_follow_up": True,
            "category": "technical",
            "target_skill": "Python / Concurrency",
            "difficulty": "advanced",
            "question_text": "You mentioned using threading for I/O bounds, but how does Python's Global Interpreter Lock (GIL) specifically impact CPU-bound versus I/O-bound tasks in that scenario?",
            "context_rationale": "Probes deeper into core GIL mechanics following a broad answer."
        }

    def _mock_answer_evaluation(self, prompt: str) -> Dict[str, Any]:
        # Extract candidate answer length and keywords to score dynamically
        answer_text = ""
        if "answer:" in prompt.lower():
            answer_text = prompt.split("answer:")[-1].strip()
            
        word_count = len(answer_text.split())
        
        # Calculate dynamic realistic score based on depth and clarity
        if word_count > 40:
            score = 8.5
            correctness = 8.8
            tech_depth = 8.2
            relevance = 9.0
            clarity = 8.5
            communication = 8.6
            problem_solving = 8.4
            level = "advanced"
            strengths = [
                "Accurately differentiated asynchronous event loop scheduling from OS-level threading",
                "Demonstrated concrete understanding of I/O non-blocking execution vs CPU-bound processing",
                "Clearly articulated architecture trade-offs with structured examples"
            ]
            weaknesses = [
                "Could have elaborated slightly more on specific lock contention issues with shared memory in multi-processing"
            ]
            evidence = [
                f"Candidate provided well-reasoned explanation ({word_count} words) referencing event loops and CPU vs I/O boundaries."
            ]
        elif word_count > 15:
            score = 7.0
            correctness = 7.2
            tech_depth = 6.8
            relevance = 7.5
            clarity = 7.0
            communication = 7.2
            problem_solving = 6.8
            level = "intermediate"
            strengths = [
                "Understood the basic core distinction between async and sync workflows",
                "Answer was relevant to the problem posed"
            ]
            weaknesses = [
                "Lacked in-depth implementation specifics regarding memory overhead and GIL mechanics"
            ]
            evidence = [
                "Candidate identified key concepts but did not provide deep architectural details."
            ]
        else:
            score = 5.5
            correctness = 5.8
            tech_depth = 4.8
            relevance = 6.0
            clarity = 5.5
            communication = 6.0
            problem_solving = 5.0
            level = "beginner"
            strengths = [
                "Identified the general topic correctly"
            ]
            weaknesses = [
                "Response was brief and lacked substantive technical evidence",
                "Did not explain underlying concurrency runtime or process boundaries"
            ]
            evidence = [
                "Answer was minimal and did not address architectural trade-offs."
            ]

        return {
            "score": score,
            "correctness": correctness,
            "technical_depth": tech_depth,
            "relevance": relevance,
            "clarity": clarity,
            "communication": communication,
            "problem_solving": problem_solving,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "evidence": evidence,
            "demonstrated_skill_level": level,
            "feedback_summary": f"Solid response highlighting primary principles. Demonstrated competency at the {level} level."
        }

    def _mock_skill_gap_analysis(self, prompt: str) -> Dict[str, Any]:
        return {
            "skill_gaps": [
                {
                    "skill_name": "Python",
                    "category": "programming",
                    "required_level": "advanced",
                    "claimed_level": "advanced",
                    "demonstrated_level": "intermediate",
                    "gap_severity": "low",
                    "priority": "medium",
                    "confidence_score": 0.88,
                    "evidence_notes": "Candidate demonstrated solid mastery of asyncio and OOP; minor gap in low-level memory profiler tooling."
                },
                {
                    "skill_name": "PostgreSQL Indexing & Optimization",
                    "category": "database",
                    "required_level": "advanced",
                    "claimed_level": "intermediate",
                    "demonstrated_level": "beginner",
                    "gap_severity": "high",
                    "priority": "high",
                    "confidence_score": 0.92,
                    "evidence_notes": "Candidate struggled with explaining GIN index internals and query planner execution tree analysis."
                },
                {
                    "skill_name": "FastAPI Microservices",
                    "category": "framework",
                    "required_level": "intermediate",
                    "claimed_level": "advanced",
                    "demonstrated_level": "intermediate",
                    "gap_severity": "low",
                    "priority": "low",
                    "confidence_score": 0.90,
                    "evidence_notes": "Clean understanding of dependency injection and Pydantic schemas; good project alignment."
                },
                {
                    "skill_name": "Distributed System Idempotency",
                    "category": "architecture",
                    "required_level": "advanced",
                    "claimed_level": "intermediate",
                    "demonstrated_level": "intermediate",
                    "gap_severity": "medium",
                    "priority": "high",
                    "confidence_score": 0.85,
                    "evidence_notes": "Understands unique constraint deduplication, but needs deeper practice with distributed 2PC or Saga patterns."
                }
            ]
        }

    def _mock_roadmap_generation(self, prompt: str) -> Dict[str, Any]:
        return {
            "title": "7-Day Targeted Mastery Plan: High-Concurrency Backend & Database Optimization",
            "duration_days": 7,
            "summary": "This structured 7-day curriculum is calibrated to bridge your detected gaps in PostgreSQL indexing, concurrency bottlenecks, and distributed idempotency.",
            "overall_recommendation": "Focus intently on Day 2 & Day 3 SQL query execution plans and Day 5 distributed locking before your next interview round.",
            "items": [
                {
                    "day_number": 1,
                    "skill_name": "Python Asyncio Internals",
                    "current_level": "intermediate",
                    "target_level": "advanced",
                    "priority": "medium",
                    "concepts_json": [
                        "Event Loop Architecture & Tasks vs Futures",
                        "Async Context Managers & Custom Transports",
                        "Debugging Coroutine Leaks with asyncio.all_tasks()"
                    ],
                    "practice_tasks_json": [
                        "Build an async rate-limited HTTP batch scraper with max 5 concurrent workers",
                        "Profile CPU vs I/O bound execution using cProfile and yappi"
                    ],
                    "mini_project_json": {
                        "title": "Async Worker Pool",
                        "description": "Construct a custom priority-based asynchronous worker pool in Python without third-party libraries."
                    },
                    "sample_questions_json": [
                        "What happens if a synchronous blocking call is executed inside an async def coroutine?",
                        "How do you handle graceful shutdown of pending asyncio tasks on SIGTERM?"
                    ]
                },
                {
                    "day_number": 2,
                    "skill_name": "PostgreSQL Indexing & EXPLAIN ANALYZE",
                    "current_level": "beginner",
                    "target_level": "intermediate",
                    "priority": "high",
                    "concepts_json": [
                        "B-Tree vs GIN vs GiST index internals",
                        "Reading EXPLAIN (ANALYZE, BUFFERS) query execution plans",
                        "Partial indexes and covering indexes with INCLUDE clause"
                    ],
                    "practice_tasks_json": [
                        "Generate 1,000,000 mock rows and optimize a slow JOIN query from 1.2s to <5ms",
                        "Identify sequential scans causing table locks in pg_stat_activity"
                    ],
                    "mini_project_json": {
                        "title": "Query Optimizer Lab",
                        "description": "Create a benchmark suite comparing composite vs partial indexes on high-cardinality audit tables."
                    },
                    "sample_questions_json": [
                        "Why might PostgreSQL choose a sequential scan even when an index exists?",
                        "How do multi-column composite index ordering rules affect query filtering?"
                    ]
                },
                {
                    "day_number": 3,
                    "skill_name": "Database Concurrency & Isolation Levels",
                    "current_level": "intermediate",
                    "target_level": "advanced",
                    "priority": "high",
                    "concepts_json": [
                        "Read Committed vs Repeatable Read vs Serializable",
                        "Phantom reads, non-repeatable reads, and serialization anomalies",
                        "Optimistic vs Pessimistic Locking (SELECT FOR UPDATE)"
                    ],
                    "practice_tasks_json": [
                        "Write a concurrent balance-transfer transaction that prevents race conditions",
                        "Simulate deadlock scenarios in two parallel psql sessions and verify resolution"
                    ],
                    "mini_project_json": {
                        "title": "Concurrent Wallet Service",
                        "description": "Develop a double-entry ledger API handling concurrent balance deductions without negative balances."
                    },
                    "sample_questions_json": [
                        "How does MVCC (Multi-Version Concurrency Control) work in PostgreSQL?",
                        "When would you choose SELECT FOR UPDATE SKIP LOCKED in message queue designs?"
                    ]
                },
                {
                    "day_number": 4,
                    "skill_name": "Redis Caching Strategies & Invalidation",
                    "current_level": "intermediate",
                    "target_level": "advanced",
                    "priority": "medium",
                    "concepts_json": [
                        "Cache-Aside, Write-Through, and Write-Behind patterns",
                        "Cache Stampede / Dogpiling prevention using mutex locks",
                        "Redis Data Structures: Hashes, Sorted Sets (ZSET), Bitmaps"
                    ],
                    "practice_tasks_json": [
                        "Implement probabilistic early expiration (XFetch algorithm) for hot cache keys",
                        "Build a sliding-window rate limiter using Redis ZSET"
                    ],
                    "mini_project_json": {
                        "title": "High-Throughput Leaderboard API",
                        "description": "Create a real-time gaming leaderboard serving top-100 ranks under 10k RPS."
                    },
                    "sample_questions_json": [
                        "How do you resolve stale data reads in a Cache-Aside architecture?",
                        "Explain Redis eviction policies (e.g. volatile-lru vs allkeys-lfu)."
                    ]
                },
                {
                    "day_number": 5,
                    "skill_name": "Idempotency & Distributed Webhooks",
                    "current_level": "intermediate",
                    "target_level": "advanced",
                    "priority": "high",
                    "concepts_json": [
                        "Idempotency keys and atomic state transitions",
                        "At-least-once vs exactly-once processing realities",
                        "Exponential backoff retry with jitter algorithms"
                    ],
                    "practice_tasks_json": [
                        "Create a FastAPI middleware checking Idempotency-Key header against Redis",
                        "Implement dead-letter queue (DLQ) processing for failed webhook payloads"
                    ],
                    "mini_project_json": {
                        "title": "Idempotent Payment Webhook Engine",
                        "description": "Build an ultra-resilient webhook handler with deduplication and replay attack protection."
                    },
                    "sample_questions_json": [
                        "How do you ensure a payment charge is never processed twice if the network drops before response?",
                        "What is the role of HMAC-SHA256 signature verification in webhook security?"
                    ]
                },
                {
                    "day_number": 6,
                    "skill_name": "System Design & Architecture Trade-offs",
                    "current_level": "intermediate",
                    "target_level": "advanced",
                    "priority": "high",
                    "concepts_json": [
                        "CAP theorem and PACELC trade-offs in distributed data stores",
                        "Event-driven architecture with message brokers (Kafka/RabbitMQ)",
                        "Microservice database decomposition patterns"
                    ],
                    "practice_tasks_json": [
                        "Draw an end-to-end architecture diagram for a URL shortener with 100M daily clicks",
                        "Calculate capacity planning metrics (RPS, storage per year, bandwidth requirements)"
                    ],
                    "mini_project_json": {
                        "title": "System Architecture Blueprint",
                        "description": "Author an RFC design document for scaling an e-commerce order processing pipeline."
                    },
                    "sample_questions_json": [
                        "How would you design a distributed unique ID generator like Twitter Snowflake?",
                        "How do you handle distributed transactions across independent microservices?"
                    ]
                },
                {
                    "day_number": 7,
                    "skill_name": "Full Mock Technical Interview Reassessment",
                    "current_level": "intermediate",
                    "target_level": "advanced",
                    "priority": "high",
                    "concepts_json": [
                        "Comprehensive review of Days 1 through 6",
                        "STAR method communication for technical deep dives",
                        "Whiteboard system design pacing and proactive clarifying questions"
                    ],
                    "practice_tasks_json": [
                        "Complete a timed 45-minute mock backend interview on TalentPulse.ai",
                        "Review comparative scorecard vs initial baseline attempt"
                    ],
                    "mini_project_json": {
                        "title": "Final Reassessment Session",
                        "description": "Execute a full technical re-test targeting previously identified gap areas."
                    },
                    "sample_questions_json": [
                        "Walk me through how you would architect, index, and cache an enterprise notification service."
                    ]
                }
            ]
        }

    def _mock_final_report(self, prompt: str) -> Dict[str, Any]:
        return {
            "readiness_score": 81.5,
            "readiness_band": "Interview Ready",
            "technical_score": 84.0,
            "project_score": 86.0,
            "problem_solving_score": 78.0,
            "communication_score": 82.0,
            "hr_score": 80.0,
            "role_specific_score": 77.5,
            "strengths": [
                "Excellent structural understanding of Python asynchronous concurrency and event loop mechanics",
                "Proven ability to articulate architectural trade-offs in real-world microservice projects",
                "High clarity and professional communication when answering system resilience questions"
            ],
            "weaknesses": [
                "Demonstrated proficiency in deep PostgreSQL index internals was below the claimed advanced level",
                "Could provide more concrete algorithmic nuance when discussing distributed consensus edge cases"
            ],
            "verified_claims": [
                {"skill": "Python", "claimed_level": "advanced", "demonstrated_level": "advanced", "verdict": "Validated Match"},
                {"skill": "FastAPI", "claimed_level": "intermediate", "demonstrated_level": "advanced", "verdict": "Exceeds Claim"},
                {"skill": "PostgreSQL", "claimed_level": "advanced", "demonstrated_level": "intermediate", "verdict": "Partial Match (Needs Practice)"},
                {"skill": "Docker", "claimed_level": "intermediate", "demonstrated_level": "intermediate", "verdict": "Validated Match"}
            ],
            "summary": "Alex Mercer exhibited strong technical aptitude for the Senior Python Backend role. Candidate demonstrated mature project leadership, clear problem-solving logic, and deep familiarity with modern REST architecture.",
            "recommendation": "Interview Ready. Recommended to complete the 7-day Database & Concurrency roadmap to solidify PostgreSQL indexing depth prior to final on-site interviews."
        }
