"""Tests for Monte Carlo simulation engine."""

import numpy as np
import pytest

from app.engine.monte_carlo import (
    FailureModeInput,
    LossScenarioInput,
    MitigationEffect,
    SimulationConfig,
    run_simulation,
)
from app.engine.risk_metrics import compute_metrics


def make_simple_fm(
    freq_mid=1.0,
    sev_mid=10000.0,
    distribution_type="lognormal",
    mitigations=None,
):
    """Helper to create a simple failure mode input."""
    return FailureModeInput(
        failure_mode_id=1,
        name="Test FM",
        frequency_low=freq_mid * 0.5,
        frequency_mid=freq_mid,
        frequency_high=freq_mid * 1.5,
        loss_scenarios=[
            LossScenarioInput(
                scenario_id=1,
                name="Test Scenario",
                party_id=1,
                loss_category="direct",
                distribution_type=distribution_type,
                severity_low=sev_mid * 0.1,
                severity_mid=sev_mid,
                severity_high=sev_mid * 10,
            )
        ],
        mitigations=mitigations or [],
    )


class TestRunSimulation:
    def test_basic_simulation(self):
        fm = make_simple_fm(freq_mid=1.0, sev_mid=10000.0)
        config = SimulationConfig(n_simulations=10000, seed=42)
        result = run_simulation([fm], config)

        assert result.n_simulations == 10000
        assert len(result.total_losses) == 10000
        assert len(result.failure_mode_results) == 1

    def test_expected_loss_reasonable(self):
        fm = make_simple_fm(freq_mid=1.0, sev_mid=10000.0)
        config = SimulationConfig(n_simulations=50000, seed=42)
        result = run_simulation([fm], config)
        metrics = compute_metrics(result.total_losses)

        # EL should be in the right ballpark (freq ~1, sev_median ~10000)
        # Lognormal mean > median, so EL should be > 10000
        assert 3000 < metrics.expected_loss < 100000

    def test_right_skewed_distribution(self):
        fm = make_simple_fm(freq_mid=1.0, sev_mid=10000.0)
        config = SimulationConfig(n_simulations=50000, seed=42)
        result = run_simulation([fm], config)
        metrics = compute_metrics(result.total_losses)

        assert metrics.p95 > metrics.p50

    def test_multiple_failure_modes_sum(self):
        fm1 = make_simple_fm(freq_mid=1.0, sev_mid=5000.0)
        fm1.failure_mode_id = 1
        fm2 = make_simple_fm(freq_mid=1.0, sev_mid=5000.0)
        fm2.failure_mode_id = 2
        config = SimulationConfig(n_simulations=10000, seed=42)

        result_single = run_simulation([fm1], config)
        result_double = run_simulation([fm1, fm2], SimulationConfig(n_simulations=10000, seed=42))

        el_single = np.mean(result_single.total_losses)
        el_double = np.mean(result_double.total_losses)
        # Two identical FMs should roughly double the EL
        assert 1.5 * el_single < el_double < 2.5 * el_single

    def test_zero_frequency(self):
        fm = make_simple_fm(freq_mid=0.0, sev_mid=10000.0)
        fm.frequency_low = 0.0
        fm.frequency_high = 0.0
        config = SimulationConfig(n_simulations=1000, seed=42)
        result = run_simulation([fm], config)

        assert np.mean(result.total_losses) == pytest.approx(0, abs=1)

    def test_deterministic_with_seed(self):
        fm = make_simple_fm()
        config = SimulationConfig(n_simulations=1000, seed=123)
        r1 = run_simulation([fm], config)
        r2 = run_simulation([fm], SimulationConfig(n_simulations=1000, seed=123))
        np.testing.assert_array_equal(r1.total_losses, r2.total_losses)

    def test_scenario_results_per_party(self):
        fm = FailureModeInput(
            failure_mode_id=1,
            name="Test",
            frequency_low=0.5,
            frequency_mid=1.0,
            frequency_high=1.5,
            loss_scenarios=[
                LossScenarioInput(1, "S1", party_id=10, loss_category="direct",
                                  distribution_type="lognormal",
                                  severity_low=100, severity_mid=1000, severity_high=10000),
                LossScenarioInput(2, "S2", party_id=20, loss_category="indirect",
                                  distribution_type="triangular",
                                  severity_low=50, severity_mid=500, severity_high=5000),
            ],
        )
        config = SimulationConfig(n_simulations=1000, seed=42)
        result = run_simulation([fm], config)

        fm_result = result.failure_mode_results[0]
        assert len(fm_result.scenario_results) == 2
        assert fm_result.scenario_results[0].party_id == 10
        assert fm_result.scenario_results[1].party_id == 20


class TestMitigatedSimulation:
    def test_mitigation_reduces_losses(self):
        fm_unmitigated = make_simple_fm(freq_mid=2.0, sev_mid=10000.0)
        fm_mitigated = make_simple_fm(
            freq_mid=2.0,
            sev_mid=10000.0,
            mitigations=[
                MitigationEffect(1, "Control A", frequency_reduction=0.3, severity_reduction=0.2)
            ],
        )

        config_unmit = SimulationConfig(n_simulations=20000, seed=42, apply_mitigations=False)
        config_mit = SimulationConfig(n_simulations=20000, seed=42, apply_mitigations=True)

        result_unmit = run_simulation([fm_unmitigated], config_unmit)
        result_mit = run_simulation([fm_mitigated], config_mit)

        el_unmit = np.mean(result_unmit.total_losses)
        el_mit = np.mean(result_mit.total_losses)

        assert el_mit < el_unmit

    def test_full_mitigation_zeroes_losses(self):
        fm = make_simple_fm(
            freq_mid=1.0,
            sev_mid=10000.0,
            mitigations=[
                MitigationEffect(1, "Full block", frequency_reduction=1.0, severity_reduction=0.0)
            ],
        )
        config = SimulationConfig(n_simulations=1000, seed=42, apply_mitigations=True)
        result = run_simulation([fm], config)
        assert np.mean(result.total_losses) == pytest.approx(0, abs=1)
