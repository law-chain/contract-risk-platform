"""Risk metric calculations from simulation results."""

from dataclasses import dataclass
from typing import List, Tuple
import numpy as np


@dataclass
class RiskMetrics:
    """Computed risk metrics for a loss distribution."""
    expected_loss: float
    var_95: float
    tvar_95: float
    var_99: float
    p5: float
    p25: float
    p50: float
    p75: float
    p95: float
    p99: float


def compute_metrics(losses: np.ndarray) -> RiskMetrics:
    """Compute standard risk metrics from an array of loss samples."""
    if len(losses) == 0:
        return RiskMetrics(0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

    el = float(np.mean(losses))
    percentiles = np.percentile(losses, [5, 25, 50, 75, 95, 99])
    var_95 = float(percentiles[4])
    var_99 = float(percentiles[5])

    # TVaR (Tail Value at Risk) = expected loss given loss >= VaR
    tail_mask = losses >= var_95
    tvar_95 = float(np.mean(losses[tail_mask])) if tail_mask.any() else var_95

    return RiskMetrics(
        expected_loss=el,
        var_95=var_95,
        tvar_95=tvar_95,
        var_99=var_99,
        p5=float(percentiles[0]),
        p25=float(percentiles[1]),
        p50=float(percentiles[2]),
        p75=float(percentiles[3]),
        p95=float(percentiles[4]),
        p99=float(percentiles[5]),
    )


def risk_asymmetry_ratio(var_95: float, contract_value: float) -> float:
    """Ratio of 95th percentile loss to contract value.

    Values > 1 indicate potential losses exceeding contract value.
    """
    if contract_value <= 0:
        return 0.0
    return var_95 / contract_value


def loss_exceedance_probability(losses: np.ndarray, threshold: float) -> float:
    """Probability that losses exceed a given threshold."""
    if len(losses) == 0:
        return 0.0
    return float(np.mean(losses > threshold))


def mitigation_value(
    unmitigated_el: float,
    mitigated_el: float,
    mitigation_cost: float,
) -> float:
    """ROI of mitigation: (EL reduction - cost) / cost."""
    if mitigation_cost <= 0:
        return float('inf') if unmitigated_el > mitigated_el else 0.0
    reduction = unmitigated_el - mitigated_el
    return (reduction - mitigation_cost) / mitigation_cost


def generate_histogram(
    losses: np.ndarray,
    n_bins: int = 50,
) -> Tuple[List[float], List[int]]:
    """Generate histogram bins and counts for charting."""
    if len(losses) == 0:
        return [], []
    counts, bin_edges = np.histogram(losses, bins=n_bins)
    bins = [(float(bin_edges[i]) + float(bin_edges[i + 1])) / 2 for i in range(len(counts))]
    return bins, counts.tolist()
