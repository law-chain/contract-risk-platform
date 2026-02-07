from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.loss_scenario import LossScenario
from app.models.failure_mode import FailureMode
from app.schemas.loss_scenario import LossScenarioCreate, LossScenarioUpdate, LossScenarioResponse

router = APIRouter(
    prefix="/api/engagements/{engagement_id}/failure-modes/{fm_id}/loss-scenarios",
    tags=["loss_scenarios"],
)


def _verify_fm(engagement_id: int, fm_id: int, db: Session) -> FailureMode:
    fm = db.query(FailureMode).filter(
        FailureMode.id == fm_id,
        FailureMode.engagement_id == engagement_id,
    ).first()
    if not fm:
        raise HTTPException(status_code=404, detail="Failure mode not found")
    return fm


@router.get("/", response_model=List[LossScenarioResponse])
def list_loss_scenarios(engagement_id: int, fm_id: int, db: Session = Depends(get_db)):
    _verify_fm(engagement_id, fm_id, db)
    return db.query(LossScenario).filter(LossScenario.failure_mode_id == fm_id).all()


@router.post("/", response_model=LossScenarioResponse, status_code=201)
def create_loss_scenario(engagement_id: int, fm_id: int, data: LossScenarioCreate, db: Session = Depends(get_db)):
    _verify_fm(engagement_id, fm_id, db)
    ls = LossScenario(failure_mode_id=fm_id, **data.model_dump())
    db.add(ls)
    db.commit()
    db.refresh(ls)
    return ls


@router.put("/{ls_id}", response_model=LossScenarioResponse)
def update_loss_scenario(engagement_id: int, fm_id: int, ls_id: int, data: LossScenarioUpdate, db: Session = Depends(get_db)):
    _verify_fm(engagement_id, fm_id, db)
    ls = db.query(LossScenario).filter(LossScenario.id == ls_id, LossScenario.failure_mode_id == fm_id).first()
    if not ls:
        raise HTTPException(status_code=404, detail="Loss scenario not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(ls, key, value)
    db.commit()
    db.refresh(ls)
    return ls


@router.delete("/{ls_id}", status_code=204)
def delete_loss_scenario(engagement_id: int, fm_id: int, ls_id: int, db: Session = Depends(get_db)):
    _verify_fm(engagement_id, fm_id, db)
    ls = db.query(LossScenario).filter(LossScenario.id == ls_id, LossScenario.failure_mode_id == fm_id).first()
    if not ls:
        raise HTTPException(status_code=404, detail="Loss scenario not found")
    db.delete(ls)
    db.commit()
