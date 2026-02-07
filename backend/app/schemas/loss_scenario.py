from pydantic import BaseModel
from typing import Optional


class LossScenarioCreate(BaseModel):
    affected_party_id: int
    name: str = ""
    loss_category: str = "direct"
    description: str = ""
    severity: str = "medium"
    severity_low: float = 1000.0
    severity_mid: float = 10000.0
    severity_high: float = 100000.0
    distribution_type: str = "lognormal"


class LossScenarioUpdate(BaseModel):
    affected_party_id: Optional[int] = None
    name: Optional[str] = None
    loss_category: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[str] = None
    severity_low: Optional[float] = None
    severity_mid: Optional[float] = None
    severity_high: Optional[float] = None
    distribution_type: Optional[str] = None


class LossScenarioResponse(BaseModel):
    id: int
    failure_mode_id: int
    affected_party_id: int
    name: str
    loss_category: str
    description: str
    severity: str
    severity_low: float
    severity_mid: float
    severity_high: float
    distribution_type: str

    model_config = {"from_attributes": True}
