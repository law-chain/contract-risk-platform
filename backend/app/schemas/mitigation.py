from pydantic import BaseModel
from typing import Optional


class MitigationCreate(BaseModel):
    name: str
    description: str = ""
    mitigation_type: str = "operational"
    cost: float = 0.0


class MitigationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    mitigation_type: Optional[str] = None
    cost: Optional[float] = None


class MitigationResponse(BaseModel):
    id: int
    engagement_id: int
    name: str
    description: str
    mitigation_type: str
    cost: float

    model_config = {"from_attributes": True}


class FailureModeMitigationLink(BaseModel):
    failure_mode_id: int
    frequency_reduction: float = 0.0
    severity_reduction: float = 0.0


class FailureModeMitigationResponse(BaseModel):
    id: int
    failure_mode_id: int
    mitigation_id: int
    frequency_reduction: float
    severity_reduction: float

    model_config = {"from_attributes": True}
