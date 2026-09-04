from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Float, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    resumes = relationship("Resume", back_populates="user", cascade="all, delete-orphan")
    interviews = relationship("Interview", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user")


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer)
    file_type = Column(String(50))
    raw_text = Column(Text)
    is_parsed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="resumes")
    profile = relationship("CandidateProfile", back_populates="resume", uselist=False, cascade="all, delete-orphan")
    interviews = relationship("Interview", back_populates="resume")


class CandidateProfile(Base):
    __tablename__ = "candidate_profiles"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    full_name = Column(String(255))
    email = Column(String(255))
    phone = Column(String(50))
    location = Column(String(255))
    summary = Column(Text)
    total_experience_years = Column(Float)
    education = Column(JSON)  # List of education entries
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    resume = relationship("Resume", back_populates="profile")
    skills = relationship("CandidateSkill", back_populates="profile", cascade="all, delete-orphan")
    experiences = relationship("WorkExperience", back_populates="profile", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="profile", cascade="all, delete-orphan")
    certifications = relationship("Certification", back_populates="profile", cascade="all, delete-orphan")


class SkillCategory(str, enum.Enum):
    PROGRAMMING_LANGUAGE = "programming_language"
    FRAMEWORK = "framework"
    DATABASE = "database"
    TOOL = "tool"
    SOFT_SKILL = "soft_skill"
    OTHER = "other"


class SkillLevel(str, enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class CandidateSkill(Base):
    __tablename__ = "candidate_skills"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("candidate_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_name = Column(String(255), nullable=False, index=True)
    category = Column(SQLEnum(SkillCategory), default=SkillCategory.OTHER)
    claimed_level = Column(SQLEnum(SkillLevel))
    years_of_experience = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    profile = relationship("CandidateProfile", back_populates="skills")


class WorkExperience(Base):
    __tablename__ = "work_experiences"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("candidate_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    company_name = Column(String(255), nullable=False)
    job_title = Column(String(255), nullable=False)
    start_date = Column(String(50))
    end_date = Column(String(50))
    is_current = Column(Boolean, default=False)
    description = Column(Text)
    responsibilities = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    profile = relationship("CandidateProfile", back_populates="experiences")


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("candidate_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    project_name = Column(String(255), nullable=False)
    description = Column(Text)
    technologies = Column(JSON)
    role = Column(String(255))
    duration = Column(String(100))
    url = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    profile = relationship("CandidateProfile", back_populates="projects")


class Certification(Base):
    __tablename__ = "certifications"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("candidate_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    issuing_organization = Column(String(255))
    issue_date = Column(String(50))
    expiry_date = Column(String(50))
    credential_id = Column(String(255))
    url = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    profile = relationship("CandidateProfile", back_populates="certifications")


class JobRole(Base):
    __tablename__ = "job_roles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text)
    required_skills = Column(JSON)
    preferred_skills = Column(JSON)
    responsibilities = Column(JSON)
    experience_level = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    interviews = relationship("Interview", back_populates="job_role")


class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    company_name = Column(String(255))
    raw_text = Column(Text, nullable=False)
    parsed_data = Column(JSON)
    required_skills = Column(JSON)
    preferred_skills = Column(JSON)
    experience_required = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    interviews = relationship("Interview", back_populates="job_description")


class InterviewStatus(str, enum.Enum):
    CREATED = "created"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class InterviewDifficulty(str, enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class Interview(Base):
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id", ondelete="SET NULL"), index=True)
    job_role_id = Column(Integer, ForeignKey("job_roles.id", ondelete="SET NULL"), index=True)
    job_description_id = Column(Integer, ForeignKey("job_descriptions.id", ondelete="SET NULL"), index=True)

    status = Column(SQLEnum(InterviewStatus), default=InterviewStatus.CREATED, nullable=False, index=True)
    difficulty = Column(SQLEnum(InterviewDifficulty), default=InterviewDifficulty.INTERMEDIATE)

    interview_blueprint = Column(JSON)  # Interview plan/structure
    state_data = Column(JSON)  # Current interview state

    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="interviews")
    resume = relationship("Resume", back_populates="interviews")
    job_role = relationship("JobRole", back_populates="interviews")
    job_description = relationship("JobDescription", back_populates="interviews")
    questions = relationship("InterviewQuestion", back_populates="interview", cascade="all, delete-orphan")
    report = relationship("InterviewReport", back_populates="interview", uselist=False, cascade="all, delete-orphan")
    skill_gaps = relationship("SkillGap", back_populates="interview", cascade="all, delete-orphan")
    roadmap = relationship("Roadmap", back_populates="interview", uselist=False, cascade="all, delete-orphan")


class QuestionType(str, enum.Enum):
    TECHNICAL = "technical"
    PROJECT = "project"
    BEHAVIORAL = "behavioral"
    HR = "hr"
    PROBLEM_SOLVING = "problem_solving"
    ROLE_SPECIFIC = "role_specific"


class InterviewQuestion(Base):
    __tablename__ = "interview_questions"

    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id", ondelete="CASCADE"), nullable=False, index=True)
    question_number = Column(Integer, nullable=False)
    question_type = Column(SQLEnum(QuestionType), nullable=False)
    question_text = Column(Text, nullable=False)
    context = Column(JSON)  # Additional context for the question
    difficulty = Column(String(50))
    skill_being_tested = Column(String(255), index=True)
    is_followup = Column(Boolean, default=False)
    parent_question_id = Column(Integer, ForeignKey("interview_questions.id", ondelete="SET NULL"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    interview = relationship("Interview", back_populates="questions")
    answer = relationship("InterviewAnswer", back_populates="question", uselist=False, cascade="all, delete-orphan")
    parent_question = relationship("InterviewQuestion", remote_side=[id], backref="followup_questions")


class InterviewAnswer(Base):
    __tablename__ = "interview_answers"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("interview_questions.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    answer_text = Column(Text, nullable=False)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    question = relationship("InterviewQuestion", back_populates="answer")
    evaluation = relationship("AnswerEvaluation", back_populates="answer", uselist=False, cascade="all, delete-orphan")


class AnswerEvaluation(Base):
    __tablename__ = "answer_evaluations"

    id = Column(Integer, primary_key=True, index=True)
    answer_id = Column(Integer, ForeignKey("interview_answers.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)

    overall_score = Column(Float, nullable=False)
    correctness_score = Column(Float)
    technical_depth_score = Column(Float)
    relevance_score = Column(Float)
    clarity_score = Column(Float)
    problem_solving_score = Column(Float)

    strengths = Column(JSON)
    weaknesses = Column(JSON)
    evidence = Column(JSON)
    skill_level_demonstrated = Column(SQLEnum(SkillLevel))
    feedback = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    answer = relationship("InterviewAnswer", back_populates="evaluation")


class SkillGap(Base):
    __tablename__ = "skill_gaps"

    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_name = Column(String(255), nullable=False, index=True)
    required_level = Column(SQLEnum(SkillLevel))
    claimed_level = Column(SQLEnum(SkillLevel))
    demonstrated_level = Column(SQLEnum(SkillLevel))
    gap_severity = Column(String(50))  # low, medium, high
    priority = Column(String(50))  # low, medium, high
    confidence = Column(Float)
    evidence = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    interview = relationship("Interview", back_populates="skill_gaps")


class Roadmap(Base):
    __tablename__ = "roadmaps"

    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    title = Column(String(255))
    description = Column(Text)
    estimated_duration_days = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    interview = relationship("Interview", back_populates="roadmap")
    items = relationship("RoadmapItem", back_populates="roadmap", cascade="all, delete-orphan")


class RoadmapItem(Base):
    __tablename__ = "roadmap_items"

    id = Column(Integer, primary_key=True, index=True)
    roadmap_id = Column(Integer, ForeignKey("roadmaps.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_name = Column(String(255), nullable=False)
    current_level = Column(SQLEnum(SkillLevel))
    target_level = Column(SQLEnum(SkillLevel))
    priority = Column(String(50))
    day_number = Column(Integer)
    concepts_to_learn = Column(JSON)
    practice_tasks = Column(JSON)
    mini_project = Column(Text)
    resources = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    roadmap = relationship("Roadmap", back_populates="items")


class InterviewReport(Base):
    __tablename__ = "interview_reports"

    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)

    overall_score = Column(Float, nullable=False)
    technical_score = Column(Float)
    project_score = Column(Float)
    problem_solving_score = Column(Float)
    communication_score = Column(Float)
    behavioral_score = Column(Float)

    readiness_percentage = Column(Float)

    strengths = Column(JSON)
    weaknesses = Column(JSON)
    key_findings = Column(JSON)
    recommendations = Column(JSON)

    summary = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    interview = relationship("Interview", back_populates="report")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), index=True)
    action = Column(String(255), nullable=False, index=True)
    resource_type = Column(String(100))
    resource_id = Column(Integer)
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    details = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationships
    user = relationship("User", back_populates="audit_logs")
