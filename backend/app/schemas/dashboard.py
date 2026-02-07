from pydantic import BaseModel
from typing import List, Optional


class ScenarioSummary(BaseModel):
    failure_mode_id: int
    name: str
    expected_loss: float
    var_95: float
    contribution_pct: float


class PartyExposureSummary(BaseModel):
    party_id: int
    party_name: str
    expected_loss: float
    var_95: float


class MitigationSummary(BaseModel):
    name: str
    cost: float
    el_reduction: float
    roi: Optional[float]


class DashboardResponse(BaseModel):
    engagement_id: int
    engagement_name: str
    contract_value: Optional[float]
    currency: str

    # Unmitigated
    unmitigated_el: float = 0
    unmitigated_var_95: float = 0
    unmitigated_tvar_95: float = 0
    unmitigated_var_99: float = 0
    unmitigated_risk_asymmetry: float = 0
    unmitigated_histogram_bins: List[float] = []
    unmitigated_histogram_counts: List[int] = []

    # Mitigated
    mitigated_el: float = 0
    mitigated_var_95: float = 0
    mitigated_tvar_95: float = 0
    mitigated_var_99: float = 0
    mitigated_risk_asymmetry: float = 0
    mitigated_histogram_bins: List[float] = []
    mitigated_histogram_counts: List[int] = []

    # Breakdown
    top_scenarios: List[ScenarioSummary] = []
    party_exposures: List[PartyExposureSummary] = []
    mitigation_summary: List[MitigationSummary] = []

    has_results: bool = False
