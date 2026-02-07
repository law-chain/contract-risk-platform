"""Tests for distribution sampling functions."""

import numpy as np
import pytest
from numpy.random import default_rng

from app.engine.distributions import (
    sample_frequency,
    sample_severity,
    sample_severity_lognormal,
    sample_severity_triangular,
    sample_severity_uniform,
)


@pytest.fixture
def rng():
    return default_rng(42)


class TestSampleFrequency:
    def test_returns_correct_shape(self, rng):
        counts = sample_frequency(rng, 0.5, 1.0, 2.0, 1000)
        assert counts.shape == (1000,)

    def test_returns_nonnegative_integers(self, rng):
        counts = sample_frequency(rng, 0.1, 0.5, 1.0, 10000)
        assert (counts >= 0).all()
        assert counts.dtype in (np.int32, np.int64, np.intp)

    def test_mean_near_mid(self, rng):
        counts = sample_frequency(rng, 0.8, 1.0, 1.2, 50000)
        assert 0.7 < counts.mean() < 1.3

    def test_higher_freq_gives_more_events(self, rng):
        low = sample_frequency(rng, 0.1, 0.2, 0.3, 10000)
        high = sample_frequency(default_rng(42), 5.0, 10.0, 15.0, 10000)
        assert high.mean() > low.mean() * 5


class TestSampleSeverity:
    def test_lognormal_median_near_mid(self, rng):
        samples = sample_severity_lognormal(rng, 1000, 10000, 100000, 50000)
        median = np.median(samples)
        assert 5000 < median < 20000

    def test_lognormal_right_skewed(self, rng):
        samples = sample_severity_lognormal(rng, 1000, 10000, 100000, 50000)
        assert np.mean(samples) > np.median(samples)

    def test_triangular_bounded(self, rng):
        samples = sample_severity_triangular(rng, 100, 500, 1000, 10000)
        assert samples.min() >= 100
        assert samples.max() <= 1000

    def test_uniform_bounded(self, rng):
        samples = sample_severity_uniform(rng, 100, 500, 1000, 10000)
        assert samples.min() >= 100
        assert samples.max() <= 1000

    def test_dispatch(self, rng):
        for dist_type in ["lognormal", "triangular", "uniform"]:
            result = sample_severity(rng, dist_type, 100, 1000, 10000, 100)
            assert len(result) == 100
            assert (result >= 0).all()

    def test_zero_mid_returns_zeros(self, rng):
        samples = sample_severity_lognormal(rng, 0, 0, 0, 100)
        assert (samples == 0).all()
