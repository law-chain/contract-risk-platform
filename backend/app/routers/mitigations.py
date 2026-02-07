from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.mitigation import Mitigation, FailureModeMitigation
from app.schemas.mitigation import (
    MitigationCreate,
    MitigationUpdate,
    MitigationResponse,
    FailureModeMitigationLink,
    FailureModeMitigationResponse,
)

router = APIRouter(prefix="/api/engagements/{engagement_id}/mitigations", tags=["mitigations"])


@router.get("/", response_model=List[MitigationResponse])
def list_mitigations(engagement_id: int, db: Session = Depends(get_db)):
    return db.query(Mitigation).filter(Mitigation.engagement_id == engagement_id).all()


@router.post("/", response_model=MitigationResponse, status_code=201)
def create_mitigation(engagement_id: int, data: MitigationCreate, db: Session = Depends(get_db)):
    mitigation = Mitigation(engagement_id=engagement_id, **data.model_dump())
    db.add(mitigation)
    db.commit()
    db.refresh(mitigation)
    return mitigation


@router.put("/{mit_id}", response_model=MitigationResponse)
def update_mitigation(engagement_id: int, mit_id: int, data: MitigationUpdate, db: Session = Depends(get_db)):
    mitigation = db.query(Mitigation).filter(Mitigation.id == mit_id, Mitigation.engagement_id == engagement_id).first()
    if not mitigation:
        raise HTTPException(status_code=404, detail="Mitigation not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(mitigation, key, value)
    db.commit()
    db.refresh(mitigation)
    return mitigation


@router.delete("/{mit_id}", status_code=204)
def delete_mitigation(engagement_id: int, mit_id: int, db: Session = Depends(get_db)):
    mitigation = db.query(Mitigation).filter(Mitigation.id == mit_id, Mitigation.engagement_id == engagement_id).first()
    if not mitigation:
        raise HTTPException(status_code=404, detail="Mitigation not found")
    db.delete(mitigation)
    db.commit()


@router.post("/{mit_id}/link", response_model=FailureModeMitigationResponse, status_code=201)
def link_mitigation_to_failure_mode(
    engagement_id: int,
    mit_id: int,
    data: FailureModeMitigationLink,
    db: Session = Depends(get_db),
):
    existing = db.query(FailureModeMitigation).filter(
        FailureModeMitigation.mitigation_id == mit_id,
        FailureModeMitigation.failure_mode_id == data.failure_mode_id,
    ).first()
    if existing:
        existing.frequency_reduction = data.frequency_reduction
        existing.severity_reduction = data.severity_reduction
        db.commit()
        db.refresh(existing)
        return existing

    link = FailureModeMitigation(
        mitigation_id=mit_id,
        failure_mode_id=data.failure_mode_id,
        frequency_reduction=data.frequency_reduction,
        severity_reduction=data.severity_reduction,
    )
    db.add(link)
    db.commit()
    db.refresh(link)
    return link


@router.delete("/{mit_id}/unlink/{fm_id}", status_code=204)
def unlink_mitigation_from_failure_mode(
    engagement_id: int,
    mit_id: int,
    fm_id: int,
    db: Session = Depends(get_db),
):
    link = db.query(FailureModeMitigation).filter(
        FailureModeMitigation.mitigation_id == mit_id,
        FailureModeMitigation.failure_mode_id == fm_id,
    ).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    db.delete(link)
    db.commit()
