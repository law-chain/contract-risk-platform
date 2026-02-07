"""Frequency and severity distribution sampling for loss modelling."""

import numpy as np
from numpy.random import Generator


def sample_frequency(
    rng: Generator,
    freq_low: float,
    freq_mid: float,
    freq_high: float,
    n_trials: int,
) -> np.ndarray:
    """Sample event counts using an uncertain Poisson process.

    For each trial, first draw a rate lambda from a triangular distribution
    (low, mid, high), then draw an event count from Poisson(lambda).
    This captures parameter uncertainty on top of process uncertainty.
    """
    freq_low = max(freq_low, 0.0)
    freq_mid = max(freq_mid, freq_low)
    freq_high = max(freq_high, freq_mid)

    if freq_high <= 0:
        return np.zeros(n_trials, dtype=np.intp)
    if freq_low == freq_high:
        lambdas = np.full(n_trials, freq_mid)
    else:
        lambdas = rng.triangular(freq_low, freq_mid, freq_high, size=n_trials)

    lambdas = np.maximum(lambdas, 0.0)
    counts = rng.poisson(lambdas)
    return counts


def sample_severity_lognormal(
    rng: Generator,
    sev_low: float,
    sev_mid: float,
    sev_high: float,
    n_samples: int,
) -> np.ndarray:
    """Sample severities from a lognormal distribution.

    We calibrate mu and sigma so that the median equals sev_mid
    and p95 ≈ sev_high.
    """
    if sev_mid <= 0:
        return np.zeros(n_samples)
    mu = np.log(sev_mid)
    if sev_high > sev_mid:
        sigma = (np.log(sev_high) - mu) / 1.645
    else:
        sigma = 0.5
    sigma = max(sigma, 0.01)
    return rng.lognormal(mu, sigma, size=n_samples)


def sample_severity_triangular(
    rng: Generator,
    sev_low: float,
    sev_mid: float,
    sev_high: float,
    n_samples: int,
) -> np.ndarray:
    """Sample severities from a triangular distribution."""
    low = max(sev_low, 0.0)
    mid = max(sev_mid, low)
    high = max(sev_high, mid + 0.01)
    return rng.triangular(low, mid, high, size=n_samples)


def sample_severity_uniform(
    rng: Generator,
    sev_low: float,
    sev_mid: float,
    sev_high: float,
    n_samples: int,
) -> np.ndarray:
    """Sample severities from a uniform distribution (low to high)."""
    low = max(sev_low, 0.0)
    high = max(sev_high, low + 0.01)
    return rng.uniform(low, high, size=n_samples)


SEVERITY_SAMPLERS = {
    "lognormal": sample_severity_lognormal,
    "triangular": sample_severity_triangular,
    "uniform": sample_severity_uniform,
}


def sample_severity(
    rng: Generator,
    distribution_type: str,
    sev_low: float,
    sev_mid: float,
    sev_high: float,
    n_samples: int,
) -> np.ndarray:
    """Sample severities using the specified distribution type."""
    sampler = SEVERITY_SAMPLERS.get(distribution_type, sample_severity_lognormal)
    return sampler(rng, sev_low, sev_mid, sev_high, n_samples)
