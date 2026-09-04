from typing import List
import json
from app.ai.base import AIProvider, AIMessage, AIResponse


class MockProvider(AIProvider):
    """Mock provider for testing and development"""

    def __init__(self, **kwargs):
        super().__init__(api_key="mock", model="mock-model", **kwargs)

    def validate_config(self) -> bool:
        """Mock provider is always valid"""
        return True

    async def generate(
        self,
        messages: List[AIMessage],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> AIResponse:
        """Generate mock response based on message content"""

        # Get the last user message
        user_message = ""
        for msg in reversed(messages):
            if msg.role == "user":
                user_message = msg.content.lower()
                break

        # Generate contextual mock responses
        if "parse" in user_message and "resume" in user_message:
            response_content = self._get_mock_resume_parse()
        elif "job description" in user_message or "analyze job" in user_message:
            response_content = self._get_mock_jd_analysis()
        elif "question" in user_message and "interview" in user_message:
            response_content = self._get_mock_question()
        elif "evaluate" in user_message and "answer" in user_message:
            response_content = self._get_mock_evaluation()
        elif "skill gap" in user_message:
            response_content = self._get_mock_skill_gaps()
        elif "roadmap" in user_message:
            response_content = self._get_mock_roadmap()
        elif "follow" in user_message or "followup" in user_message:
            response_content = self._get_mock_followup()
        else:
            response_content = json.dumps({
                "response": "This is a mock AI response for testing purposes.",
                "confidence": 0.85
            })

        return AIResponse(
            content=response_content,
            model="mock-model",
            tokens_used=100,
            finish_reason="stop"
        )

    def _get_mock_resume_parse(self) -> str:
        """Mock resume parsing response"""
        return json.dumps({
            "full_name": "John Doe",
            "email": "john.doe@email.com",
            "phone": "+1-555-0123",
            "location": "San Francisco, CA",
            "summary": "Experienced software engineer with 5+ years in full-stack development",
            "total_experience_years": 5.5,
            "education": [
                {
                    "degree": "Bachelor of Science in Computer Science",
                    "institution": "University of California",
                    "graduation_year": "2018"
                }
            ],
            "skills": [
                {"name": "Python", "category": "programming_language", "level": "advanced", "years": 5},
                {"name": "JavaScript", "category": "programming_language", "level": "advanced", "years": 4},
                {"name": "React", "category": "framework", "level": "intermediate", "years": 3},
                {"name": "Django", "category": "framework", "level": "advanced", "years": 4},
                {"name": "PostgreSQL", "category": "database", "level": "intermediate", "years": 3},
                {"name": "Docker", "category": "tool", "level": "intermediate", "years": 2}
            ],
            "experiences": [
                {
                    "company": "Tech Corp",
                    "title": "Senior Software Engineer",
                    "start_date": "2020-01",
                    "end_date": "Present",
                    "is_current": True,
                    "description": "Lead backend development for e-commerce platform",
                    "responsibilities": [
                        "Architected microservices infrastructure",
                        "Mentored junior developers",
                        "Optimized database queries reducing latency by 40%"
                    ]
                },
                {
                    "company": "StartupXYZ",
                    "title": "Software Engineer",
                    "start_date": "2018-06",
                    "end_date": "2019-12",
                    "is_current": False,
                    "description": "Full-stack development for SaaS product"
                }
            ],
            "projects": [
                {
                    "name": "E-commerce Platform",
                    "description": "Built scalable microservices architecture handling 1M+ daily users",
                    "technologies": ["Python", "Django", "PostgreSQL", "Redis", "Docker"],
                    "role": "Lead Developer",
                    "duration": "2 years"
                },
                {
                    "name": "Analytics Dashboard",
                    "description": "Real-time analytics platform with data visualization",
                    "technologies": ["React", "D3.js", "Python", "FastAPI"],
                    "role": "Full-stack Developer",
                    "duration": "6 months"
                }
            ],
            "certifications": [
                {
                    "name": "AWS Certified Solutions Architect",
                    "organization": "Amazon Web Services",
                    "issue_date": "2021-05",
                    "credential_id": "AWS-123456"
                }
            ]
        })

    def _get_mock_jd_analysis(self) -> str:
        """Mock job description analysis"""
        return json.dumps({
            "title": "Senior Python Developer",
            "experience_level": "Senior (5+ years)",
            "required_skills": [
                "Python", "Django/Flask", "PostgreSQL", "REST APIs",
                "Docker", "Git", "Problem Solving"
            ],
            "preferred_skills": [
                "React", "AWS", "Kubernetes", "CI/CD", "Microservices"
            ],
            "technical_requirements": [
                "Strong Python programming skills",
                "Experience with web frameworks",
                "Database design and optimization",
                "API development",
                "Cloud platforms experience"
            ],
            "responsibilities": [
                "Design and develop backend services",
                "Write clean, maintainable code",
                "Collaborate with frontend team",
                "Code reviews and mentoring"
            ],
            "key_focus_areas": ["backend", "apis", "databases", "scalability"]
        })

    def _get_mock_question(self) -> str:
        """Mock interview question"""
        return json.dumps({
            "question": "Can you explain the difference between Django and Flask, and when would you choose one over the other?",
            "type": "technical",
            "difficulty": "intermediate",
            "skill": "Python",
            "context": "Testing framework knowledge and decision-making"
        })

    def _get_mock_followup(self) -> str:
        """Mock follow-up question"""
        return json.dumps({
            "question": "You mentioned using Django. Can you describe a specific challenge you faced with Django's ORM and how you resolved it?",
            "type": "project",
            "difficulty": "intermediate",
            "skill": "Django",
            "is_followup": True,
            "reason": "Probing deeper into claimed Django expertise"
        })

    def _get_mock_evaluation(self) -> str:
        """Mock answer evaluation"""
        return json.dumps({
            "overall_score": 7.5,
            "correctness_score": 8.0,
            "technical_depth_score": 7.0,
            "relevance_score": 8.0,
            "clarity_score": 7.5,
            "problem_solving_score": 7.0,
            "strengths": [
                "Clear explanation of Django vs Flask differences",
                "Mentioned appropriate use cases",
                "Showed understanding of tradeoffs"
            ],
            "weaknesses": [
                "Could have provided more specific examples",
                "Did not mention performance considerations"
            ],
            "evidence": [
                "Correctly identified Django as full-featured framework",
                "Understood Flask's microframework philosophy"
            ],
            "skill_level_demonstrated": "intermediate",
            "feedback": "Good foundational understanding. Consider diving deeper into performance and scalability aspects."
        })

    def _get_mock_skill_gaps(self) -> str:
        """Mock skill gap analysis"""
        return json.dumps({
            "skill_gaps": [
                {
                    "skill": "PostgreSQL",
                    "required_level": "intermediate",
                    "claimed_level": "intermediate",
                    "demonstrated_level": "beginner",
                    "gap_severity": "medium",
                    "priority": "high",
                    "confidence": 0.75,
                    "evidence": [
                        "Basic query knowledge shown",
                        "Limited understanding of query optimization",
                        "No mention of indexing strategies"
                    ]
                },
                {
                    "skill": "Docker",
                    "required_level": "intermediate",
                    "claimed_level": "intermediate",
                    "demonstrated_level": "beginner",
                    "gap_severity": "medium",
                    "priority": "medium",
                    "confidence": 0.70,
                    "evidence": [
                        "Basic container concepts understood",
                        "Limited multi-stage build knowledge"
                    ]
                }
            ]
        })

    def _get_mock_roadmap(self) -> str:
        """Mock improvement roadmap"""
        return json.dumps({
            "title": "PostgreSQL Skill Development Plan",
            "estimated_duration_days": 14,
            "items": [
                {
                    "skill": "PostgreSQL",
                    "current_level": "beginner",
                    "target_level": "intermediate",
                    "priority": "high",
                    "day_number": 1,
                    "concepts": ["Advanced SELECT queries", "JOINs", "Subqueries"],
                    "practice_tasks": [
                        "Write 10 complex JOIN queries",
                        "Practice subquery optimization"
                    ],
                    "mini_project": "Build a reporting system with complex aggregations",
                    "resources": [
                        {"title": "PostgreSQL Tutorial", "type": "documentation"},
                        {"title": "SQL Practice Problems", "type": "exercises"}
                    ]
                },
                {
                    "skill": "PostgreSQL",
                    "current_level": "beginner",
                    "target_level": "intermediate",
                    "priority": "high",
                    "day_number": 7,
                    "concepts": ["Indexes", "Query optimization", "EXPLAIN plans"],
                    "practice_tasks": [
                        "Optimize 5 slow queries",
                        "Create appropriate indexes"
                    ],
                    "mini_project": "Profile and optimize a slow database schema"
                }
            ]
        })
