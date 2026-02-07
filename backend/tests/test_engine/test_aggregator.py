"""Tests for loss aggregation."""

import numpy as np
import pytest

from app.engine.monte_carlo import (
    FailureModeInput,
    LossScenarioInput,
    SimulationConfig,
    run_simulation,
)
from app.engine.loss_aggregator import aggregate_results


def test_ranking_by_expected_loss():
    """Higher-severity failure mode should rank first."""
    fm_small = FailureModeInput(
        failure_mode_id=1, name="Small FM",
        frequency_low=0.5, frequency_mid=1.0, frequency_high=1.5,
        loss_scenarios=[LossScenarioInput(
            1, "S1", party_id=1, loss_category="direct",
            distribution_type="lognormal",
            severity_low=100, severity_mid=1000, severity_high=5000,
        )],
    )
    fm_large = FailureModeInput(
        failure_mode_id=2, name="Large FM",
        frequency_low=0.5, frequency_mid=1.0, frequency_high=1.5,
        loss_scenarios=[LossScenarioInput(
            2, "S2", party_id=1, loss_category="direct",
            distribution_type="lognormal",
            severity_low=10000, severity_mid=100000, severity_high=500000,
        )],
    )

    config = SimulationConfig(n_simulations=10000, seed=42)
    result = run_simulation([fm_small, fm_large], config)
    agg = aggregate_results(result)

    assert agg.ranked_scenarios[0].failure_mode_id == 2
    assert agg.ranked_scenarios[0].expected_loss > agg.ranked_scenarios[1].expected_loss


def test_party_exposure_split():
    """Losses should be correctly attributed to different parties."""
    fm = FailureModeInput(
        failure_mode_id=1, name="Multi-party FM",
        frequency_low=0.8, frequency_mid=1.0, frequency_high=1.2,
        loss_scenarios=[
            LossScenarioInput(1, "Buyer loss", party_id=10, loss_category="direct",
                              distribution_type="lognormal",
                              severity_low=1000, severity_mid=10000, severity_high=50000),
            LossScenarioInput(2, "Supplier loss", party_id=20, loss_category="indirect",
                              distribution_type="triangular",
                              severity_low=500, severity_mid=5000, severity_high=25000),
        ],
    )

    config = SimulationConfig(n_simulations=10000, seed=42)
    result = run_simulation([fm], config)
    agg = aggregate_results(result)

    assert 10 in agg.party_exposures
    assert 20 in agg.party_exposures
    assert agg.party_exposures[10].metrics.expected_loss > 0
    assert agg.party_exposures[20].metrics.expected_loss > 0


def test_contribution_percentages_sum():
    """Contribution percentages should approximately sum to 100."""
    fm1 = FailureModeInput(
        failure_mode_id=1, name="FM1",
        frequency_low=0.5, frequency_mid=1.0, frequency_high=1.5,
        loss_scenarios=[LossScenarioInput(
            1, "S1", party_id=1, loss_category="direct",
            distribution_type="lognormal",
            severity_low=1000, severity_mid=10000, severity_high=50000,
        )],
    )
    fm2 = FailureModeInput(
        failure_mode_id=2, name="FM2",
        frequency_low=0.5, frequency_mid=1.0, frequency_high=1.5,
        loss_scenarios=[LossScenarioInput(
            2, "S2", party_id=1, loss_category="direct",
            distribution_type="lognormal",
            severity_low=2000, severity_mid=20000, severity_high=100000,
        )],
    )

    config = SimulationConfig(n_simulations=10000, seed=42)
    result = run_simulation([fm1, fm2], config)
    agg = aggregate_results(result)

    total_pct = sum(s.contribution_pct for s in agg.ranked_scenarios)
    assert 95 < total_pct < 105
