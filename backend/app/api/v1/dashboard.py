from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.security import get_current_user_id_and_role
from backend.app.schemas.dashboard import DashboardSummaryResponse
from backend.app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/stats", response_model=DashboardSummaryResponse)
def get_dashboard_stats(
    user_info: dict = Depends(get_current_user_id_and_role),
    db: Session = Depends(get_db)
):
    dashboard_service = DashboardService(db)
    return dashboard_service.get_dashboard_data(user_id=user_info["user_id"])
