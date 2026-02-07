from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Mitigation(Base):
    __tablename__ = "mitigations"

    id = Column(Integer, primary_key=True, index=True)
    engagement_id = Column(Integer, ForeignKey("engagements.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, default="")
    mitigation_type = Column(String, default="operational")
    cost = Column(Float, default=0.0)

    failure_mode_mitigations = relationship("FailureModeMitigation", back_populates="mitigation", cascade="all, delete-orphan")


class FailureModeMitigation(Base):
    __tablename__ = "failure_mode_mitigations"

    id = Column(Integer, primary_key=True, index=True)
    failure_mode_id = Column(Integer, ForeignKey("failure_modes.id"), nullable=False)
    mitigation_id = Column(Integer, ForeignKey("mitigations.id"), nullable=False)
    frequency_reduction = Column(Float, default=0.0)
    severity_reduction = Column(Float, default=0.0)

    failure_mode = relationship("FailureMode", back_populates="failure_mode_mitigations")
    mitigation = relationship("Mitigation", back_populates="failure_mode_mitigations")
