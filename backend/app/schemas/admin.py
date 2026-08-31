from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr

class AdminUserItem(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: str
    is_active: bool
    created_at: datetime
    resumes_count: int = 0
    interviews_count: int = 0

    class Config:
        from_attributes = True

class AdminAuditItem(BaseModel):
    id: int
    user_id: Optional[int] = None
    user_email: Optional[str] = None
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    ip_address: Optional[str] = None
    details_json: Dict[str, Any] = {}
    created_at: datetime

    class Config:
        from_attributes = True

class AdminAnalyticsResponse(BaseModel):
    total_users: int
    total_resumes: int
    total_interviews: int
    completed_interviews: int
    average_readiness_score: float
    role_distribution: Dict[str, int]
    top_skill_gaps: List[Dict[str, Any]]
    recent_activity: List[AdminAuditItem]
