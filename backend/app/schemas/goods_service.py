from pydantic import BaseModel
from typing import Optional


class GoodsServiceCreate(BaseModel):
    name: str
    category: str = ""
    description: str = ""
    use_context: str = ""
    supply_type: str = "goods"
    replaceability: str = "replaceable"


class GoodsServiceUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    use_context: Optional[str] = None
    supply_type: Optional[str] = None
    replaceability: Optional[str] = None


class GoodsServiceResponse(BaseModel):
    id: int
    engagement_id: int
    name: str
    category: str
    description: str
    use_context: str
    supply_type: str
    replaceability: str

    model_config = {"from_attributes": True}
