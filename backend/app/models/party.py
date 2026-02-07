from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
import enum

from app.database import Base


class PartyRole(str, enum.Enum):
    BUYER = "buyer"
    SUPPLIER = "supplier"
    THIRD_PARTY = "third_party"
    END_USER = "end_user"


class Party(Base):
    __tablename__ = "parties"

    id = Column(Integer, primary_key=True, index=True)
    engagement_id = Column(Integer, ForeignKey("engagements.id"), nullable=False)
    name = Column(String, nullable=False)
    role = Column(SAEnum(PartyRole), nullable=False)
    revenue = Column(Float, nullable=True)
    criticality = Column(String, default="medium")
    description = Column(String, default="")

    engagement = relationship("Engagement", back_populates="parties")
    loss_scenarios = relationship("LossScenario", back_populates="affected_party", cascade="all, delete-orphan")
