"""Aggregate simulation results across failure modes and parties."""

from dataclasses import dataclass
from typing import List, Dict
import numpy as np

from app.engine.monte_carlo import SimulationResult
from app.engine.risk_metrics import compute_metrics, RiskMetrics


@dataclass
class RankedScenario:
    """A failure mode ranked by expected loss."""
    failure_mode_id: int
    name: str
    expected_loss: float
    var_95: float
    contribution_pct: float  # % of total EL


@dataclass
class PartyExposure:
    """Aggregated exposure for a single party."""
    party_id: int
    metrics: RiskMetrics


@dataclass
class AggregatedResult:
    """Complete aggregated analysis of simulation output."""
    total_metrics: RiskMetrics
    ranked_scenarios: List[RankedScenario]
    party_exposures: Dict[int, PartyExposure]


def aggregate_results(result: SimulationResult) -> AggregatedResult:
    """Aggregate simulation results into ranked and party-level views."""
    total_metrics = compute_metrics(result.total_losses)
    total_el = total_metrics.expected_loss if total_metrics.expected_loss > 0 else 1.0

    # Rank failure modes by expected loss
    ranked = []
    for fm_result in result.failure_mode_results:
        fm_metrics = compute_metrics(fm_result.total_losses)
        ranked.append(RankedScenario(
            failure_mode_id=fm_result.failure_mode_id,
            name=fm_result.name,
            expected_loss=fm_metrics.expected_loss,
            var_95=fm_metrics.var_95,
            contribution_pct=(fm_metrics.expected_loss / total_el) * 100,
        ))
    ranked.sort(key=lambda x: x.expected_loss, reverse=True)

    # Aggregate by party
    party_losses: Dict[int, np.ndarray] = {}
    for fm_result in result.failure_mode_results:
        for sr in fm_result.scenario_results:
            if sr.party_id not in party_losses:
                party_losses[sr.party_id] = np.zeros(result.n_simulations)
            party_losses[sr.party_id] += sr.losses

    party_exposures = {}
    for party_id, losses in party_losses.items():
        party_exposures[party_id] = PartyExposure(
            party_id=party_id,
            metrics=compute_metrics(losses),
        )

    return AggregatedResult(
        total_metrics=total_metrics,
        ranked_scenarios=ranked,
        party_exposures=party_exposures,
    )
