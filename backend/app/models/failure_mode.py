from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
import enum

from app.database import Base


class FrequencyLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class FailureModeSource(str, enum.Enum):
    MANUAL = "manual"
    AI = "ai"


class FailureMode(Base):
    __tablename__ = "failure_modes"

    id = Column(Integer, primary_key=True, index=True)
    engagement_id = Column(Integer, ForeignKey("engagements.id"), nullable=False)
    goods_service_id = Column(Integer, ForeignKey("goods_services.id"), nullable=True)
    name = Column(String, nullable=False)
    description = Column(String, default="")
    category = Column(String, default="")
    frequency_low = Column(Float, default=0.1)
    frequency_mid = Column(Float, default=0.5)
    frequency_high = Column(Float, default=1.0)
    detection = Column(String, default="medium")
    source = Column(SAEnum(FailureModeSource), default=FailureModeSource.MANUAL)
    confidence = Column(Float, default=0.5)
    is_included = Column(Boolean, default=True)

    engagement = relationship("Engagement", back_populates="failure_modes")
    goods_service = relationship("GoodsService", back_populates="failure_modes")
    loss_scenarios = relationship("LossScenario", back_populates="failure_mode", cascade="all, delete-orphan")
    failure_mode_mitigations = relationship("FailureModeMitigation", back_populates="failure_mode", cascade="all, delete-orphan")
