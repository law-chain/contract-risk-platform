from pydantic import BaseModel
from typing import Optional


class PartyCreate(BaseModel):
    name: str
    role: str
    revenue: Optional[float] = None
    criticality: str = "medium"
    description: str = ""


class PartyUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    revenue: Optional[float] = None
    criticality: Optional[str] = None
    description: Optional[str] = None


class PartyResponse(BaseModel):
    id: int
    engagement_id: int
    name: str
    role: str
    revenue: Optional[float]
    criticality: str
    description: str

    model_config = {"from_attributes": True}
