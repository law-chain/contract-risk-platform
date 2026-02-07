from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class EngagementCreate(BaseModel):
    name: str
    description: str = ""
    contract_value: Optional[float] = None
    currency: str = "USD"
    industry: str = ""
    status: str = "draft"


class EngagementUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    contract_value: Optional[float] = None
    currency: Optional[str] = None
    industry: Optional[str] = None
    status: Optional[str] = None


class EngagementResponse(BaseModel):
    id: int
    name: str
    description: str
    contract_value: Optional[float]
    currency: str
    industry: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class EngagementListResponse(BaseModel):
    id: int
    name: str
    industry: str
    contract_value: Optional[float]
    currency: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
