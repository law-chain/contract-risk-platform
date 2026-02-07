from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.party import Party
from app.schemas.party import PartyCreate, PartyUpdate, PartyResponse

router = APIRouter(prefix="/api/engagements/{engagement_id}/parties", tags=["parties"])


@router.get("/", response_model=List[PartyResponse])
def list_parties(engagement_id: int, db: Session = Depends(get_db)):
    return db.query(Party).filter(Party.engagement_id == engagement_id).all()


@router.post("/", response_model=PartyResponse, status_code=201)
def create_party(engagement_id: int, data: PartyCreate, db: Session = Depends(get_db)):
    party = Party(engagement_id=engagement_id, **data.model_dump())
    db.add(party)
    db.commit()
    db.refresh(party)
    return party


@router.get("/{party_id}", response_model=PartyResponse)
def get_party(engagement_id: int, party_id: int, db: Session = Depends(get_db)):
    party = db.query(Party).filter(Party.id == party_id, Party.engagement_id == engagement_id).first()
    if not party:
        raise HTTPException(status_code=404, detail="Party not found")
    return party


@router.put("/{party_id}", response_model=PartyResponse)
def update_party(engagement_id: int, party_id: int, data: PartyUpdate, db: Session = Depends(get_db)):
    party = db.query(Party).filter(Party.id == party_id, Party.engagement_id == engagement_id).first()
    if not party:
        raise HTTPException(status_code=404, detail="Party not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(party, key, value)
    db.commit()
    db.refresh(party)
    return party


@router.delete("/{party_id}", status_code=204)
def delete_party(engagement_id: int, party_id: int, db: Session = Depends(get_db)):
    party = db.query(Party).filter(Party.id == party_id, Party.engagement_id == engagement_id).first()
    if not party:
        raise HTTPException(status_code=404, detail="Party not found")
    db.delete(party)
    db.commit()
