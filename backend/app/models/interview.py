from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Boolean, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class Interview(Base):
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="SET NULL"), nullable=True, index=True)
    job_role_id = Column(Integer, ForeignKey("job_roles.id", ondelete="SET NULL"), nullable=True, index=True)
    job_description_id = Column(Integer, ForeignKey("job_descriptions.id", ondelete="SET NULL"), nullable=True, index=True)
    
    title = Column(String(255), nullable=False)
    interview_type = Column(String(50), default="mixed", nullable=False)  # 'technical', 'project', 'behavioral', 'hr', 'mixed', 'role_specific'
    difficulty = Column(String(50), default="intermediate", nullable=False)  # 'beginner', 'intermediate', 'advanced', 'expert'
    status = Column(String(50), default="created", nullable=False)  # 'created', 'in_progress', 'completed', 'abandoned'
    
    blueprint_json = Column(JSON, default=dict)  # Category weights & target skill distribution
    current_question_index = Column(Integer, default=0)
    total_questions = Column(Integer, default=5)
    overall_score = Column(Float, nullable=True)
    
    # State tracking for adaptive engine
    state_json = Column(JSON, default=dict)  # Tracks skill confidence, answered counts, follow-up flags
    
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="interviews")
    resume = relationship("Resume", back_populates="interviews")
    job_role = relationship("JobRole", back_populates="interviews")
    job_description = relationship("JobDescription", back_populates="interviews")
    questions = relationship("InterviewQuestion", back_populates="interview", cascade="all, delete-orphan", order_by="InterviewQuestion.sequence_num")
    skill_gaps = relationship("SkillGap", back_populates="interview", cascade="all, delete-orphan")
    roadmaps = relationship("Roadmap", back_populates="interview", cascade="all, delete-orphan")
    report = relationship("Report", back_populates="interview", uselist=False, cascade="all, delete-orphan")

class InterviewQuestion(Base):
    __tablename__ = "interview_questions"

    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id", ondelete="CASCADE"), nullable=False, index=True)
    sequence_num = Column(Integer, nullable=False)
    category = Column(String(50), default="technical", nullable=False)  # 'technical', 'project', 'problem_solving', 'communication', 'behavioral', 'role_specific'
    target_skill = Column(String(100), nullable=True)
    difficulty = Column(String(50), default="intermediate", nullable=False)
    question_text = Column(Text, nullable=False)
    context_rationale = Column(Text, nullable=True)
    is_follow_up = Column(Boolean, default=False)
    parent_question_id = Column(Integer, ForeignKey("interview_questions.id"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    interview = relationship("Interview", back_populates="questions")
    answer = relationship("InterviewAnswer", back_populates="question", uselist=False, cascade="all, delete-orphan")

class InterviewAnswer(Base):
    __tablename__ = "interview_answers"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("interview_questions.id", ondelete="CASCADE"), unique=True, nullable=False)
    answer_text = Column(Text, nullable=False)
    time_taken_seconds = Column(Integer, default=0)
    audio_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    question = relationship("InterviewQuestion", back_populates="answer")
    evaluation = relationship("AnswerEvaluation", back_populates="answer", uselist=False, cascade="all, delete-orphan")

class AnswerEvaluation(Base):
    __tablename__ = "answer_evaluations"

    id = Column(Integer, primary_key=True, index=True)
    answer_id = Column(Integer, ForeignKey("interview_answers.id", ondelete="CASCADE"), unique=True, nullable=False)
    score = Column(Float, nullable=False)  # 0 to 10
    correctness = Column(Float, default=0.0)
    technical_depth = Column(Float, default=0.0)
    relevance = Column(Float, default=0.0)
    clarity = Column(Float, default=0.0)
    communication = Column(Float, default=0.0)
    problem_solving = Column(Float, default=0.0)
    
    strengths_json = Column(JSON, default=list)
    weaknesses_json = Column(JSON, default=list)
    evidence_json = Column(JSON, default=list)  # Concrete quotes/observations
    demonstrated_skill_level = Column(String(50), default="intermediate")  # 'beginner', 'intermediate', 'advanced', 'expert'
    feedback_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    answer = relationship("InterviewAnswer", back_populates="evaluation")
