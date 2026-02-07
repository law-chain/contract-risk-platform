"""Orchestrates quantification: reads DB → builds engine inputs → runs simulation → stores results."""

from sqlalchemy.orm import Session

from app.models.engagement import Engagement
from app.models.failure_mode import FailureMode
from app.models.quantification import QuantificationRun, QuantificationResult
from app.engine.monte_carlo import (
    FailureModeInput,
    LossScenarioInput,
    MitigationEffect,
    SimulationConfig,
    run_simulation,
)
from app.engine.risk_metrics import (
    compute_metrics,
    risk_asymmetry_ratio,
    generate_histogram,
)
from app.engine.loss_aggregator import aggregate_results


def build_engine_inputs(engagement: Engagement) -> list[FailureModeInput]:
    """Build engine input dataclasses from DB models."""
    inputs = []
    for fm in engagement.failure_modes:
        if not fm.is_included:
            continue
        scenarios = []
        for ls in fm.loss_scenarios:
            scenarios.append(LossScenarioInput(
                scenario_id=ls.id,
                name=ls.name,
                party_id=ls.affected_party_id,
                loss_category=ls.loss_category,
                distribution_type=ls.distribution_type.value if hasattr(ls.distribution_type, 'value') else ls.distribution_type,
                severity_low=ls.severity_low,
                severity_mid=ls.severity_mid,
                severity_high=ls.severity_high,
            ))
        mitigations = []
        for fmm in fm.failure_mode_mitigations:
            mitigations.append(MitigationEffect(
                mitigation_id=fmm.mitigation_id,
                name=fmm.mitigation.name,
                frequency_reduction=fmm.frequency_reduction,
                severity_reduction=fmm.severity_reduction,
            ))
        if scenarios:
            inputs.append(FailureModeInput(
                failure_mode_id=fm.id,
                name=fm.name,
                frequency_low=fm.frequency_low,
                frequency_mid=fm.frequency_mid,
                frequency_high=fm.frequency_high,
                loss_scenarios=scenarios,
                mitigations=mitigations,
            ))
    return inputs


def run_quantification(
    db: Session,
    engagement_id: int,
    num_simulations: int = 10000,
) -> tuple[QuantificationRun, QuantificationRun]:
    """Run both unmitigated and mitigated simulations, store results."""
    engagement = db.query(Engagement).filter(Engagement.id == engagement_id).first()
    if not engagement:
        raise ValueError("Engagement not found")

    fm_inputs = build_engine_inputs(engagement)
    if not fm_inputs:
        raise ValueError("No failure modes with loss scenarios to simulate")

    contract_value = engagement.contract_value or 0

    # Unmitigated run
    config_unmit = SimulationConfig(n_simulations=num_simulations, apply_mitigations=False)
    result_unmit = run_simulation(fm_inputs, config_unmit)
    unmit_run = _store_run(db, engagement_id, num_simulations, False, result_unmit, contract_value)

    # Mitigated run
    config_mit = SimulationConfig(n_simulations=num_simulations, apply_mitigations=True)
    result_mit = run_simulation(fm_inputs, config_mit)
    mit_run = _store_run(db, engagement_id, num_simulations, True, result_mit, contract_value)

    db.commit()
    db.refresh(unmit_run)
    db.refresh(mit_run)
    return unmit_run, mit_run


def _store_run(
    db: Session,
    engagement_id: int,
    num_simulations: int,
    is_mitigated: bool,
    sim_result,
    contract_value: float,
) -> QuantificationRun:
    """Store simulation results in the database."""
    agg = aggregate_results(sim_result)
    total_metrics = agg.total_metrics
    hist_bins, hist_counts = generate_histogram(sim_result.total_losses)

    run = QuantificationRun(
        engagement_id=engagement_id,
        num_simulations=num_simulations,
        is_mitigated=is_mitigated,
        total_expected_loss=total_metrics.expected_loss,
        total_var_95=total_metrics.var_95,
        total_tvar_95=total_metrics.tvar_95,
        total_var_99=total_metrics.var_99,
        risk_asymmetry_ratio=risk_asymmetry_ratio(total_metrics.var_95, contract_value),
        histogram_bins=hist_bins,
        histogram_counts=hist_counts,
    )
    db.add(run)
    db.flush()

    # Per failure-mode results
    for rs in agg.ranked_scenarios:
        fm_result = next(
            (fr for fr in sim_result.failure_mode_results if fr.failure_mode_id == rs.failure_mode_id),
            None,
        )
        if fm_result is None:
            continue
        fm_metrics = compute_metrics(fm_result.total_losses)
        fm_bins, fm_counts = generate_histogram(fm_result.total_losses)
        db.add(QuantificationResult(
            run_id=run.id,
            failure_mode_id=rs.failure_mode_id,
            label=rs.name,
            expected_loss=fm_metrics.expected_loss,
            var_95=fm_metrics.var_95,
            tvar_95=fm_metrics.tvar_95,
            var_99=fm_metrics.var_99,
            p5=fm_metrics.p5,
            p25=fm_metrics.p25,
            p50=fm_metrics.p50,
            p75=fm_metrics.p75,
            p95=fm_metrics.p95,
            p99=fm_metrics.p99,
            histogram_bins=fm_bins,
            histogram_counts=fm_counts,
        ))

    # Per party results
    for party_id, pe in agg.party_exposures.items():
        p_bins, p_counts = generate_histogram(
            next(
                fr.total_losses for fr in sim_result.failure_mode_results
                if any(sr.party_id == party_id for sr in fr.scenario_results)
            ) if sim_result.failure_mode_results else __import__('numpy').zeros(0)
        )
        db.add(QuantificationResult(
            run_id=run.id,
            party_id=party_id,
            label=f"Party {party_id}",
            expected_loss=pe.metrics.expected_loss,
            var_95=pe.metrics.var_95,
            tvar_95=pe.metrics.tvar_95,
            var_99=pe.metrics.var_99,
            p5=pe.metrics.p5,
            p25=pe.metrics.p25,
            p50=pe.metrics.p50,
            p75=pe.metrics.p75,
            p95=pe.metrics.p95,
            p99=pe.metrics.p99,
            histogram_bins=p_bins,
            histogram_counts=p_counts,
        ))

    return run
