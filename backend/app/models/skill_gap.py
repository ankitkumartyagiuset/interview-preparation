from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Boolean, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class SkillGap(Base):
    __tablename__ = "skill_gaps"

    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_name = Column(String(100), nullable=False, index=True)
    category = Column(String(50), default="technical")
    
    required_level = Column(String(50), default="intermediate")  # 'beginner', 'intermediate', 'advanced', 'expert'
    claimed_level = Column(String(50), default="intermediate")   # 'beginner', 'intermediate', 'advanced', 'expert'
    demonstrated_level = Column(String(50), default="beginner")  # 'beginner', 'intermediate', 'advanced', 'expert'
    
    gap_severity = Column(String(50), default="medium")  # 'none', 'low', 'medium', 'high'
    priority = Column(String(50), default="medium")      # 'low', 'medium', 'high'
    confidence_score = Column(Float, default=0.8)        # 0.0 to 1.0
    evidence_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    interview = relationship("Interview", back_populates="skill_gaps")

class Roadmap(Base):
    __tablename__ = "roadmaps"

    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    duration_days = Column(Integer, default=7)
    summary = Column(Text, nullable=True)
    overall_recommendation = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    interview = relationship("Interview", back_populates="roadmaps")
    items = relationship("RoadmapItem", back_populates="roadmap", cascade="all, delete-orphan", order_by="RoadmapItem.day_number")

class RoadmapItem(Base):
    __tablename__ = "roadmap_items"

    id = Column(Integer, primary_key=True, index=True)
    roadmap_id = Column(Integer, ForeignKey("roadmaps.id", ondelete="CASCADE"), nullable=False, index=True)
    day_number = Column(Integer, nullable=False)
    skill_name = Column(String(100), nullable=False)
    current_level = Column(String(50), default="beginner")
    target_level = Column(String(50), default="intermediate")
    priority = Column(String(50), default="high")
    
    concepts_json = Column(JSON, default=list)        # List of concept strings
    practice_tasks_json = Column(JSON, default=list)  # List of practical exercises
    mini_project_json = Column(JSON, default=dict)    # {'title': '...', 'description': '...'}
    sample_questions_json = Column(JSON, default=list)# List of practice interview questions
    is_completed = Column(Boolean, default=False)
    
    roadmap = relationship("Roadmap", back_populates="items")
