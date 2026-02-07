from sqlalchemy import Column, Integer, String, Float, DateTime, Enum as SAEnum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum

from app.database import Base


class EngagementStatus(str, enum.Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"
    ARCHIVED = "archived"


class Engagement(Base):
    __tablename__ = "engagements"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, default="")
    contract_value = Column(Float, nullable=True)
    currency = Column(String, default="USD")
    industry = Column(String, default="")
    status = Column(SAEnum(EngagementStatus), default=EngagementStatus.DRAFT)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    parties = relationship("Party", back_populates="engagement", cascade="all, delete-orphan")
    goods_services = relationship("GoodsService", back_populates="engagement", cascade="all, delete-orphan")
    failure_modes = relationship("FailureMode", back_populates="engagement", cascade="all, delete-orphan")
    quantification_runs = relationship("QuantificationRun", back_populates="engagement", cascade="all, delete-orphan")
