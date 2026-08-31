from datetime import timedelta
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from backend.app.core.security import verify_password, get_password_hash, create_access_token
from backend.app.repositories.user_repo import UserRepository
from backend.app.repositories.audit_repo import AuditRepository
from backend.app.models.user import User

class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.audit_repo = AuditRepository(db)

    def register(self, email: str, password: str, full_name: str, role: str = "candidate", ip_address: Optional[str] = None) -> Dict[str, Any]:
        existing = self.user_repo.get_by_email(email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email address already exists."
            )
        
        hashed = get_password_hash(password)
        user = self.user_repo.create(
            email=email,
            password_hash=hashed,
            full_name=full_name,
            role=role
        )
        
        token = create_access_token(subject=user.id, role=user.role)
        self.audit_repo.log(
            user_id=user.id,
            action="USER_REGISTER",
            resource_type="user",
            resource_id=str(user.id),
            ip_address=ip_address,
            details_json={"email": user.email, "role": user.role}
        )
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": user
        }

    def login(self, email: str, password: str, ip_address: Optional[str] = None) -> Dict[str, Any]:
        user = self.user_repo.get_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password."
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This account has been deactivated."
            )

        token = create_access_token(subject=user.id, role=user.role)
        self.audit_repo.log(
            user_id=user.id,
            action="USER_LOGIN",
            resource_type="user",
            resource_id=str(user.id),
            ip_address=ip_address,
            details_json={"email": user.email}
        )
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": user
        }

    def get_current_user(self, user_id: int) -> User:
        user = self.user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found or inactive."
            )
        return user
