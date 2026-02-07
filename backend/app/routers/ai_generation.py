from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.engagement import Engagement
from app.models.goods_service import GoodsService
from app.models.failure_mode import FailureMode
from app.models.loss_scenario import LossScenario
from app.schemas.ai_generation import (
    GenerateFailureModesRequest,
    EstimateLossesRequest,
    SuggestMitigationsRequest,
    AIGenerationResponse,
)
from app.services.claude_service import ClaudeService

router = APIRouter(prefix="/api/engagements/{engagement_id}/ai", tags=["ai_generation"])


def _get_engagement(engagement_id: int, db: Session) -> Engagement:
    engagement = db.query(Engagement).filter(Engagement.id == engagement_id).first()
    if not engagement:
        raise HTTPException(status_code=404, detail="Engagement not found")
    return engagement


@router.post("/generate-failure-modes", response_model=AIGenerationResponse)
def generate_failure_modes(
    engagement_id: int,
    data: GenerateFailureModesRequest,
    db: Session = Depends(get_db),
):
    engagement = _get_engagement(engagement_id, db)
    gs = db.query(GoodsService).filter(GoodsService.id == data.goods_service_id).first()
    if not gs:
        raise HTTPException(status_code=404, detail="Goods/Service not found")

    parties = [
        {"name": p.name, "role": p.role.value if hasattr(p.role, 'value') else p.role, "revenue": p.revenue}
        for p in engagement.parties
    ]

    service = ClaudeService()
    try:
        result = service.generate_failure_modes(
            goods_service_name=gs.name,
            goods_service_description=gs.description,
            use_context=gs.use_context,
            supply_type=gs.supply_type.value if hasattr(gs.supply_type, 'value') else gs.supply_type,
            replaceability=gs.replaceability.value if hasattr(gs.replaceability, 'value') else gs.replaceability,
            industry=engagement.industry,
            contract_value=engagement.contract_value or 0,
            currency=engagement.currency,
            parties=parties,
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Claude API error: {str(e)}")

    return AIGenerationResponse(data=result)


@router.post("/estimate-losses", response_model=AIGenerationResponse)
def estimate_losses(
    engagement_id: int,
    data: EstimateLossesRequest,
    db: Session = Depends(get_db),
):
    engagement = _get_engagement(engagement_id, db)
    fm = db.query(FailureMode).filter(FailureMode.id == data.failure_mode_id).first()
    if not fm:
        raise HTTPException(status_code=404, detail="Failure mode not found")
    ls = db.query(LossScenario).filter(LossScenario.id == data.loss_scenario_id).first()
    if not ls:
        raise HTTPException(status_code=404, detail="Loss scenario not found")

    party = ls.affected_party

    service = ClaudeService()
    try:
        result = service.estimate_loss_parameters(
            failure_mode_name=fm.name,
            failure_mode_description=fm.description,
            loss_category=ls.loss_category,
            affected_party_name=party.name if party else "Unknown",
            affected_party_role=party.role.value if party and hasattr(party.role, 'value') else "unknown",
            industry=engagement.industry,
            contract_value=engagement.contract_value or 0,
            currency=engagement.currency,
            current_low=ls.severity_low,
            current_mid=ls.severity_mid,
            current_high=ls.severity_high,
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Claude API error: {str(e)}")

    return AIGenerationResponse(data=result)


@router.post("/suggest-mitigations", response_model=AIGenerationResponse)
def suggest_mitigations(
    engagement_id: int,
    data: SuggestMitigationsRequest,
    db: Session = Depends(get_db),
):
    engagement = _get_engagement(engagement_id, db)
    failure_modes = [
        {
            "name": fm.name,
            "description": fm.description,
            "category": fm.category,
            "frequency_mid": fm.frequency_mid,
        }
        for fm in engagement.failure_modes
        if fm.is_included
    ]

    if not failure_modes:
        raise HTTPException(status_code=400, detail="No failure modes to mitigate")

    service = ClaudeService()
    try:
        result = service.suggest_mitigations(
            failure_modes=failure_modes,
            industry=engagement.industry,
            contract_value=engagement.contract_value or 0,
            currency=engagement.currency,
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Claude API error: {str(e)}")

    return AIGenerationResponse(data=result)
