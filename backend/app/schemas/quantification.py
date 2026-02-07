from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class QuantificationRunRequest(BaseModel):
    num_simulations: int = 10000


class QuantificationResultResponse(BaseModel):
    id: int
    failure_mode_id: Optional[int]
    loss_scenario_id: Optional[int]
    party_id: Optional[int]
    label: str
    expected_loss: float
    var_95: float
    tvar_95: float
    var_99: float
    p5: float
    p25: float
    p50: float
    p75: float
    p95: float
    p99: float
    histogram_bins: List[float]
    histogram_counts: List[int]

    model_config = {"from_attributes": True}


class QuantificationRunResponse(BaseModel):
    id: int
    engagement_id: int
    num_simulations: int
    is_mitigated: bool
    total_expected_loss: float
    total_var_95: float
    total_tvar_95: float
    total_var_99: float
    risk_asymmetry_ratio: float
    histogram_bins: List[float]
    histogram_counts: List[int]
    created_at: datetime
    results: List[QuantificationResultResponse] = []

    model_config = {"from_attributes": True}
