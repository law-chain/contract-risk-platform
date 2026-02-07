from pydantic import BaseModel
from typing import Any, Dict


class GenerateFailureModesRequest(BaseModel):
    goods_service_id: int


class EstimateLossesRequest(BaseModel):
    failure_mode_id: int
    loss_scenario_id: int


class SuggestMitigationsRequest(BaseModel):
    pass  # Uses all included failure modes for the engagement


class AIGenerationResponse(BaseModel):
    data: Dict[str, Any]
