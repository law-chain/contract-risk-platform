from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.database import Base


class QuantificationRun(Base):
    __tablename__ = "quantification_runs"

    id = Column(Integer, primary_key=True, index=True)
    engagement_id = Column(Integer, ForeignKey("engagements.id"), nullable=False)
    num_simulations = Column(Integer, default=10000)
    is_mitigated = Column(Boolean, default=False)
    total_expected_loss = Column(Float, default=0.0)
    total_var_95 = Column(Float, default=0.0)
    total_tvar_95 = Column(Float, default=0.0)
    total_var_99 = Column(Float, default=0.0)
    risk_asymmetry_ratio = Column(Float, default=0.0)
    histogram_bins = Column(JSON, default=list)
    histogram_counts = Column(JSON, default=list)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    engagement = relationship("Engagement", back_populates="quantification_runs")
    results = relationship("QuantificationResult", back_populates="run", cascade="all, delete-orphan")


class QuantificationResult(Base):
    __tablename__ = "quantification_results"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("quantification_runs.id"), nullable=False)
    failure_mode_id = Column(Integer, nullable=True)
    loss_scenario_id = Column(Integer, nullable=True)
    party_id = Column(Integer, nullable=True)
    label = Column(String, default="")
    expected_loss = Column(Float, default=0.0)
    var_95 = Column(Float, default=0.0)
    tvar_95 = Column(Float, default=0.0)
    var_99 = Column(Float, default=0.0)
    p5 = Column(Float, default=0.0)
    p25 = Column(Float, default=0.0)
    p50 = Column(Float, default=0.0)
    p75 = Column(Float, default=0.0)
    p95 = Column(Float, default=0.0)
    p99 = Column(Float, default=0.0)
    histogram_bins = Column(JSON, default=list)
    histogram_counts = Column(JSON, default=list)

    run = relationship("QuantificationRun", back_populates="results")
