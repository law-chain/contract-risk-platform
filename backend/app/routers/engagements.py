from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.engagement import Engagement
from app.schemas.engagement import (
    EngagementCreate,
    EngagementUpdate,
    EngagementResponse,
    EngagementListResponse,
)

router = APIRouter(prefix="/api/engagements", tags=["engagements"])


@router.get("/", response_model=List[EngagementListResponse])
def list_engagements(db: Session = Depends(get_db)):
    return db.query(Engagement).order_by(Engagement.created_at.desc()).all()


@router.post("/", response_model=EngagementResponse, status_code=201)
def create_engagement(data: EngagementCreate, db: Session = Depends(get_db)):
    engagement = Engagement(**data.model_dump())
    db.add(engagement)
    db.commit()
    db.refresh(engagement)
    return engagement


@router.get("/{engagement_id}", response_model=EngagementResponse)
def get_engagement(engagement_id: int, db: Session = Depends(get_db)):
    engagement = db.query(Engagement).filter(Engagement.id == engagement_id).first()
    if not engagement:
        raise HTTPException(status_code=404, detail="Engagement not found")
    return engagement


@router.put("/{engagement_id}", response_model=EngagementResponse)
def update_engagement(engagement_id: int, data: EngagementUpdate, db: Session = Depends(get_db)):
    engagement = db.query(Engagement).filter(Engagement.id == engagement_id).first()
    if not engagement:
        raise HTTPException(status_code=404, detail="Engagement not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(engagement, key, value)
    db.commit()
    db.refresh(engagement)
    return engagement


@router.delete("/{engagement_id}", status_code=204)
def delete_engagement(engagement_id: int, db: Session = Depends(get_db)):
    engagement = db.query(Engagement).filter(Engagement.id == engagement_id).first()
    if not engagement:
        raise HTTPException(status_code=404, detail="Engagement not found")
    db.delete(engagement)
    db.commit()
