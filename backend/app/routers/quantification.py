from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.quantification import QuantificationRun
from app.schemas.quantification import (
    QuantificationRunRequest,
    QuantificationRunResponse,
)
from app.services.quantification_service import run_quantification

router = APIRouter(prefix="/api/engagements/{engagement_id}/quantification", tags=["quantification"])


@router.post("/run", response_model=List[QuantificationRunResponse])
def run_quantification_endpoint(
    engagement_id: int,
    data: QuantificationRunRequest,
    db: Session = Depends(get_db),
):
    try:
        unmit_run, mit_run = run_quantification(db, engagement_id, data.num_simulations)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return [unmit_run, mit_run]


@router.get("/runs", response_model=List[QuantificationRunResponse])
def list_runs(engagement_id: int, db: Session = Depends(get_db)):
    return (
        db.query(QuantificationRun)
        .filter(QuantificationRun.engagement_id == engagement_id)
        .order_by(QuantificationRun.created_at.desc())
        .all()
    )


@router.get("/runs/{run_id}", response_model=QuantificationRunResponse)
def get_run(engagement_id: int, run_id: int, db: Session = Depends(get_db)):
    run = (
        db.query(QuantificationRun)
        .filter(QuantificationRun.id == run_id, QuantificationRun.engagement_id == engagement_id)
        .first()
    )
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run
