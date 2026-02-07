from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.dashboard import DashboardResponse
from app.services.dashboard_service import get_dashboard

router = APIRouter(prefix="/api/engagements/{engagement_id}/dashboard", tags=["dashboard"])


@router.get("/", response_model=DashboardResponse)
def dashboard(engagement_id: int, db: Session = Depends(get_db)):
    try:
        return get_dashboard(db, engagement_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
