from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.user import User
from app.models.resume import Resume
from app.models.interview import Interview

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email.lower().strip()).first()

    def create(self, email: str, password_hash: str, full_name: str, role: str = "candidate") -> User:
        user = User(
            email=email.lower().strip(),
            password_hash=password_hash,
            full_name=full_name.strip(),
            role=role,
            is_active=True
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_profile(self, user: User, full_name: Optional[str] = None, password_hash: Optional[str] = None) -> User:
        if full_name:
            user.full_name = full_name
        if password_hash:
            user.password_hash = password_hash
        self.db.commit()
        self.db.refresh(user)
        return user

    def list_users(self, skip: int = 0, limit: int = 50) -> List[User]:
        return self.db.query(User).offset(skip).limit(limit).all()

    def count_users(self) -> int:
        return self.db.query(func.count(User.id)).scalar() or 0

    def delete(self, user: User) -> bool:
        self.db.delete(user)
        self.db.commit()
        return True
