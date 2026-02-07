from sqlalchemy import Column, Integer, String, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
import enum

from app.database import Base


class SupplyType(str, enum.Enum):
    GOODS = "goods"
    SERVICES = "services"
    MIXED = "mixed"


class Replaceability(str, enum.Enum):
    EASILY_REPLACEABLE = "easily_replaceable"
    REPLACEABLE = "replaceable"
    DIFFICULT = "difficult"
    IRREPLACEABLE = "irreplaceable"


class GoodsService(Base):
    __tablename__ = "goods_services"

    id = Column(Integer, primary_key=True, index=True)
    engagement_id = Column(Integer, ForeignKey("engagements.id"), nullable=False)
    name = Column(String, nullable=False)
    category = Column(String, default="")
    description = Column(String, default="")
    use_context = Column(String, default="")
    supply_type = Column(SAEnum(SupplyType), default=SupplyType.GOODS)
    replaceability = Column(SAEnum(Replaceability), default=Replaceability.REPLACEABLE)

    engagement = relationship("Engagement", back_populates="goods_services")
    failure_modes = relationship("FailureMode", back_populates="goods_service", cascade="all, delete-orphan")
