from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.failure_mode import FailureMode
from app.schemas.failure_mode import FailureModeCreate, FailureModeUpdate, FailureModeResponse

router = APIRouter(prefix="/api/engagements/{engagement_id}/failure-modes", tags=["failure_modes"])


@router.get("/", response_model=List[FailureModeResponse])
def list_failure_modes(engagement_id: int, db: Session = Depends(get_db)):
    return db.query(FailureMode).filter(FailureMode.engagement_id == engagement_id).all()


@router.post("/", response_model=FailureModeResponse, status_code=201)
def create_failure_mode(engagement_id: int, data: FailureModeCreate, db: Session = Depends(get_db)):
    fm = FailureMode(engagement_id=engagement_id, **data.model_dump())
    db.add(fm)
    db.commit()
    db.refresh(fm)
    return fm


@router.get("/{fm_id}", response_model=FailureModeResponse)
def get_failure_mode(engagement_id: int, fm_id: int, db: Session = Depends(get_db)):
    fm = db.query(FailureMode).filter(FailureMode.id == fm_id, FailureMode.engagement_id == engagement_id).first()
    if not fm:
        raise HTTPException(status_code=404, detail="Failure mode not found")
    return fm


@router.put("/{fm_id}", response_model=FailureModeResponse)
def update_failure_mode(engagement_id: int, fm_id: int, data: FailureModeUpdate, db: Session = Depends(get_db)):
    fm = db.query(FailureMode).filter(FailureMode.id == fm_id, FailureMode.engagement_id == engagement_id).first()
    if not fm:
        raise HTTPException(status_code=404, detail="Failure mode not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(fm, key, value)
    db.commit()
    db.refresh(fm)
    return fm


@router.patch("/{fm_id}/toggle", response_model=FailureModeResponse)
def toggle_failure_mode(engagement_id: int, fm_id: int, db: Session = Depends(get_db)):
    fm = db.query(FailureMode).filter(FailureMode.id == fm_id, FailureMode.engagement_id == engagement_id).first()
    if not fm:
        raise HTTPException(status_code=404, detail="Failure mode not found")
    fm.is_included = not fm.is_included
    db.commit()
    db.refresh(fm)
    return fm


@router.delete("/{fm_id}", status_code=204)
def delete_failure_mode(engagement_id: int, fm_id: int, db: Session = Depends(get_db)):
    fm = db.query(FailureMode).filter(FailureMode.id == fm_id, FailureMode.engagement_id == engagement_id).first()
    if not fm:
        raise HTTPException(status_code=404, detail="Failure mode not found")
    db.delete(fm)
    db.commit()
