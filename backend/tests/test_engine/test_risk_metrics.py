"""Tests for risk metric calculations."""

import numpy as np
import pytest

from app.engine.risk_metrics import (
    compute_metrics,
    risk_asymmetry_ratio,
    loss_exceedance_probability,
    mitigation_value,
    generate_histogram,
)


class TestComputeMetrics:
    def test_known_distribution(self):
        rng = np.random.default_rng(42)
        losses = rng.lognormal(mean=np.log(10000), sigma=0.5, size=100000)
        metrics = compute_metrics(losses)

        assert 8000 < metrics.p50 < 12000  # median near 10000
        assert metrics.expected_loss > metrics.p50  # right skewed
        assert metrics.p95 > metrics.p75 > metrics.p50 > metrics.p25 > metrics.p5
        assert metrics.var_95 == pytest.approx(metrics.p95)
        assert metrics.tvar_95 >= metrics.var_95

    def test_empty_array(self):
        metrics = compute_metrics(np.array([]))
        assert metrics.expected_loss == 0
        assert metrics.var_95 == 0

    def test_constant_losses(self):
        losses = np.full(1000, 5000.0)
        metrics = compute_metrics(losses)
        assert metrics.expected_loss == pytest.approx(5000, rel=0.01)
        assert metrics.p50 == pytest.approx(5000, rel=0.01)


class TestRiskAsymmetryRatio:
    def test_basic(self):
        assert risk_asymmetry_ratio(50000, 100000) == pytest.approx(0.5)

    def test_exceeds_contract(self):
        assert risk_asymmetry_ratio(200000, 100000) == pytest.approx(2.0)

    def test_zero_contract(self):
        assert risk_asymmetry_ratio(50000, 0) == 0.0


class TestLossExceedanceProbability:
    def test_basic(self):
        losses = np.array([100, 200, 300, 400, 500, 600, 700, 800, 900, 1000])
        prob = loss_exceedance_probability(losses, 500)
        assert prob == pytest.approx(0.5)

    def test_no_exceedance(self):
        losses = np.array([1, 2, 3])
        assert loss_exceedance_probability(losses, 100) == 0.0

    def test_empty(self):
        assert loss_exceedance_probability(np.array([]), 100) == 0.0


class TestMitigationValue:
    def test_positive_roi(self):
        roi = mitigation_value(100000, 50000, 10000)
        assert roi == pytest.approx(4.0)  # (50000 - 10000) / 10000

    def test_negative_roi(self):
        roi = mitigation_value(100000, 95000, 10000)
        assert roi < 0  # cost exceeds benefit

    def test_zero_cost(self):
        roi = mitigation_value(100000, 50000, 0)
        assert roi == float('inf')


class TestGenerateHistogram:
    def test_returns_correct_bins(self):
        losses = np.random.default_rng(42).lognormal(10, 1, 10000)
        bins, counts = generate_histogram(losses, n_bins=30)
        assert len(bins) == 30
        assert len(counts) == 30
        assert all(c >= 0 for c in counts)
        assert sum(counts) == 10000

    def test_empty(self):
        bins, counts = generate_histogram(np.array([]))
        assert bins == []
        assert counts == []
