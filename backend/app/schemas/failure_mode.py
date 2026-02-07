from pydantic import BaseModel
from typing import Optional


class FailureModeCreate(BaseModel):
    goods_service_id: Optional[int] = None
    name: str
    description: str = ""
    category: str = ""
    frequency_low: float = 0.1
    frequency_mid: float = 0.5
    frequency_high: float = 1.0
    detection: str = "medium"
    source: str = "manual"
    confidence: float = 0.5
    is_included: bool = True


class FailureModeUpdate(BaseModel):
    goods_service_id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    frequency_low: Optional[float] = None
    frequency_mid: Optional[float] = None
    frequency_high: Optional[float] = None
    detection: Optional[str] = None
    source: Optional[str] = None
    confidence: Optional[float] = None
    is_included: Optional[bool] = None


class FailureModeResponse(BaseModel):
    id: int
    engagement_id: int
    goods_service_id: Optional[int]
    name: str
    description: str
    category: str
    frequency_low: float
    frequency_mid: float
    frequency_high: float
    detection: str
    source: str
    confidence: float
    is_included: bool

    model_config = {"from_attributes": True}
