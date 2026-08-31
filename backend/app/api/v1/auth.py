from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.security import get_current_user_id_and_role
from backend.app.core.limiter import rate_limit_dependency
from backend.app.schemas.auth import UserRegister, UserLogin, TokenResponse, UserResponse, UserProfileUpdate
from backend.app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=TokenResponse, dependencies=[Depends(rate_limit_dependency)])
def register(data: UserRegister, request: Request, response: Response, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    client_ip = request.client.host if request.client else "127.0.0.1"
    result = auth_service.register(
        email=data.email,
        password=data.password,
        full_name=data.full_name,
        role=data.role or "candidate",
        ip_address=client_ip
    )
    # Set secure HTTP-only cookie for web app convenience
    response.set_cookie(
        key="access_token",
        value=f"Bearer {result['access_token']}",
        httponly=True,
        samesite="lax",
        secure=False
    )
    return result

@router.post("/login", response_model=TokenResponse, dependencies=[Depends(rate_limit_dependency)])
def login(data: UserLogin, request: Request, response: Response, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    client_ip = request.client.host if request.client else "127.0.0.1"
    result = auth_service.login(
        email=data.email,
        password=data.password,
        ip_address=client_ip
    )
    response.set_cookie(
        key="access_token",
        value=f"Bearer {result['access_token']}",
        httponly=True,
        samesite="lax",
        secure=False
    )
    return result

@router.get("/me", response_model=UserResponse)
def get_me(user_info: dict = Depends(get_current_user_id_and_role), db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    return auth_service.get_current_user(user_info["user_id"])

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(key="access_token")
    return {"message": "Logged out successfully."}
