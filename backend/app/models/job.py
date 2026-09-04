from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class JobRole(Base):
    __tablename__ = "job_roles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), unique=True, nullable=False, index=True)
    department = Column(String(100), nullable=True)
    seniority = Column(String(50), default="intermediate")  # 'junior', 'intermediate', 'senior', 'lead'
    description = Column(Text, nullable=True)
    core_skills_json = Column(JSON, default=list)  # [{'name': 'Python', 'level': 'advanced', 'importance': 'required'}]
    default_blueprint_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    interviews = relationship("Interview", back_populates="job_role")

class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=True)
    raw_text = Column(Text, nullable=False)
    required_skills_json = Column(JSON, default=list)
    preferred_skills_json = Column(JSON, default=list)
    responsibilities_json = Column(JSON, default=list)
    seniority = Column(String(50), default="intermediate")
    experience_years_required = Column(Float, default=2.0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    user = relationship("User", back_populates="job_descriptions")
    interviews = relationship("Interview", back_populates="job_description")
