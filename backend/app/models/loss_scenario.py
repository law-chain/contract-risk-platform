from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
import enum

from app.database import Base


class SeverityLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CATASTROPHIC = "catastrophic"


class DistributionType(str, enum.Enum):
    LOGNORMAL = "lognormal"
    TRIANGULAR = "triangular"
    UNIFORM = "uniform"


class LossScenario(Base):
    __tablename__ = "loss_scenarios"

    id = Column(Integer, primary_key=True, index=True)
    failure_mode_id = Column(Integer, ForeignKey("failure_modes.id"), nullable=False)
    affected_party_id = Column(Integer, ForeignKey("parties.id"), nullable=False)
    name = Column(String, default="")
    loss_category = Column(String, default="direct")
    description = Column(String, default="")
    severity = Column(SAEnum(SeverityLevel), default=SeverityLevel.MEDIUM)
    severity_low = Column(Float, default=1000.0)
    severity_mid = Column(Float, default=10000.0)
    severity_high = Column(Float, default=100000.0)
    distribution_type = Column(SAEnum(DistributionType), default=DistributionType.LOGNORMAL)

    failure_mode = relationship("FailureMode", back_populates="loss_scenarios")
    affected_party = relationship("Party", back_populates="loss_scenarios")
