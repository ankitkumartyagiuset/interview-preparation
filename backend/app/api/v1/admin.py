from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import require_role
from app.schemas.admin import AdminAnalyticsResponse, AdminUserItem
from app.services.admin_service import AdminService

router = APIRouter(prefix="/admin", tags=["Admin Operations"], dependencies=[Depends(require_role(["admin"]))])

@router.get("/analytics", response_model=AdminAnalyticsResponse)
def get_admin_analytics(
    db: Session = Depends(get_db)
):
    admin_service = AdminService(db)
    return admin_service.get_analytics()

@router.get("/users", response_model=List[AdminUserItem])
def list_users(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    admin_service = AdminService(db)
    return admin_service.list_users(skip=skip, limit=limit)

@router.post("/users/{user_id}/toggle-active")
def toggle_user_active(
    user_id: int,
    db: Session = Depends(get_db)
):
    admin_service = AdminService(db)
    user = admin_service.toggle_user_active(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )
    return {"message": f"User active status toggled successfully. Active: {user.is_active}"}
