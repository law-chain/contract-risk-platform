"""Core Monte Carlo simulation engine for loss modelling."""

from dataclasses import dataclass, field
from typing import List, Optional
import numpy as np
from numpy.random import default_rng

from app.engine.distributions import sample_frequency, sample_severity


@dataclass
class MitigationEffect:
    """Reduction factors from a single mitigation applied to a failure mode."""
    mitigation_id: int
    name: str
    frequency_reduction: float = 0.0  # 0 to 1, fraction reduction
    severity_reduction: float = 0.0   # 0 to 1, fraction reduction


@dataclass
class LossScenarioInput:
    """Input parameters for a single loss scenario within a failure mode."""
    scenario_id: int
    name: str
    party_id: int
    loss_category: str
    distribution_type: str  # "lognormal", "triangular", "uniform"
    severity_low: float
    severity_mid: float
    severity_high: float


@dataclass
class FailureModeInput:
    """Input parameters for a single failure mode to simulate."""
    failure_mode_id: int
    name: str
    frequency_low: float
    frequency_mid: float
    frequency_high: float
    loss_scenarios: List[LossScenarioInput] = field(default_factory=list)
    mitigations: List[MitigationEffect] = field(default_factory=list)


@dataclass
class SimulationConfig:
    """Configuration for a Monte Carlo simulation run."""
    n_simulations: int = 10000
    seed: Optional[int] = None
    apply_mitigations: bool = False


@dataclass
class ScenarioResult:
    """Result for a single loss scenario."""
    scenario_id: int
    party_id: int
    loss_category: str
    losses: np.ndarray  # array of per-trial losses


@dataclass
class FailureModeResult:
    """Result for a single failure mode across all trials."""
    failure_mode_id: int
    name: str
    total_losses: np.ndarray  # aggregated per-trial losses for this FM
    scenario_results: List[ScenarioResult] = field(default_factory=list)


@dataclass
class SimulationResult:
    """Complete simulation output."""
    total_losses: np.ndarray  # per-trial total across all failure modes
    failure_mode_results: List[FailureModeResult] = field(default_factory=list)
    n_simulations: int = 0


def run_simulation(
    failure_modes: List[FailureModeInput],
    config: SimulationConfig,
) -> SimulationResult:
    """Run Monte Carlo simulation across all failure modes.

    For each trial:
      1. Sample event count for each failure mode (uncertain Poisson)
      2. For each event, sample severity per loss scenario
      3. Sum losses across events within each scenario
      4. Optionally apply mitigation reduction factors
    """
    rng = default_rng(config.seed)
    n = config.n_simulations
    total_losses = np.zeros(n)
    fm_results = []

    for fm in failure_modes:
        freq_low = fm.frequency_low
        freq_mid = fm.frequency_mid
        freq_high = fm.frequency_high

        # Apply mitigation frequency reduction (multiplicative)
        if config.apply_mitigations and fm.mitigations:
            residual = 1.0
            for m in fm.mitigations:
                residual *= (1.0 - m.frequency_reduction)
            freq_low *= residual
            freq_mid *= residual
            freq_high *= residual

        event_counts = sample_frequency(rng, freq_low, freq_mid, freq_high, n)
        fm_total = np.zeros(n)
        scenario_results = []

        for ls in fm.loss_scenarios:
            sev_low = ls.severity_low
            sev_mid = ls.severity_mid
            sev_high = ls.severity_high

            # Apply mitigation severity reduction (multiplicative)
            if config.apply_mitigations and fm.mitigations:
                residual = 1.0
                for m in fm.mitigations:
                    residual *= (1.0 - m.severity_reduction)
                sev_low *= residual
                sev_mid *= residual
                sev_high *= residual

            scenario_losses = np.zeros(n)
            max_events = int(event_counts.max()) if event_counts.max() > 0 else 0

            if max_events > 0:
                # Sample severities for the maximum possible events across all trials
                all_severities = sample_severity(
                    rng, ls.distribution_type,
                    sev_low, sev_mid, sev_high,
                    n * max_events,
                ).reshape(n, max_events)

                # Mask: zero out severities for trials with fewer events
                mask = np.arange(max_events)[None, :] < event_counts[:, None]
                all_severities *= mask
                scenario_losses = all_severities.sum(axis=1)

            fm_total += scenario_losses
            scenario_results.append(ScenarioResult(
                scenario_id=ls.scenario_id,
                party_id=ls.party_id,
                loss_category=ls.loss_category,
                losses=scenario_losses,
            ))

        total_losses += fm_total
        fm_results.append(FailureModeResult(
            failure_mode_id=fm.failure_mode_id,
            name=fm.name,
            total_losses=fm_total,
            scenario_results=scenario_results,
        ))

    return SimulationResult(
        total_losses=total_losses,
        failure_mode_results=fm_results,
        n_simulations=n,
    )
