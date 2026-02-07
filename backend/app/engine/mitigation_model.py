"""Mitigation modelling: combine multiple mitigations and run mitigated simulations."""

from typing import List

from app.engine.monte_carlo import (
    FailureModeInput,
    MitigationEffect,
    SimulationConfig,
    SimulationResult,
    run_simulation,
)


def combine_mitigations(mitigations: List[MitigationEffect]) -> MitigationEffect:
    """Combine multiple mitigations using multiplicative residual approach.

    If mitigation A reduces frequency by 30% and B by 20%,
    residual = 0.7 * 0.8 = 0.56, so combined reduction = 44%.
    """
    freq_residual = 1.0
    sev_residual = 1.0
    for m in mitigations:
        freq_residual *= (1.0 - m.frequency_reduction)
        sev_residual *= (1.0 - m.severity_reduction)

    return MitigationEffect(
        mitigation_id=0,
        name="combined",
        frequency_reduction=1.0 - freq_residual,
        severity_reduction=1.0 - sev_residual,
    )


def run_mitigated_simulation(
    failure_modes: List[FailureModeInput],
    config: SimulationConfig,
) -> SimulationResult:
    """Run simulation with mitigations applied."""
    mitigated_config = SimulationConfig(
        n_simulations=config.n_simulations,
        seed=config.seed,
        apply_mitigations=True,
    )
    return run_simulation(failure_modes, mitigated_config)


def compute_mitigation_savings(
    unmitigated_el: float,
    mitigated_el: float,
) -> float:
    """Compute the absolute EL reduction from mitigations."""
    return unmitigated_el - mitigated_el
