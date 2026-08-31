from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id", ondelete="CASCADE"), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    overall_readiness_score = Column(Float, nullable=False)  # 0 to 100
    readiness_band = Column(String(50), default="Developing")  # 'Not Ready', 'Beginner', 'Developing', 'Interview Ready', 'Highly Ready'
    
    technical_score = Column(Float, default=0.0)
    project_score = Column(Float, default=0.0)
    problem_solving_score = Column(Float, default=0.0)
    communication_score = Column(Float, default=0.0)
    hr_score = Column(Float, default=0.0)
    role_specific_score = Column(Float, default=0.0)
    
    strengths_json = Column(JSON, default=list)
    weaknesses_json = Column(JSON, default=list)
    verified_claims_json = Column(JSON, default=list)  # [{'skill': 'Python', 'claimed': 'expert', 'demonstrated': 'intermediate', 'verdict': 'Partial Match'}]
    
    summary = Column(Text, nullable=True)
    recommendation = Column(Text, nullable=True)
    disclaimer = Column(Text, default="This assessment is an interview-preparation/readiness assessment and is not a definitive hiring decision.")
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    interview = relationship("Interview", back_populates="report")
