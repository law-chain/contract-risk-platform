"""Assembles dashboard response from latest quantification runs."""

from sqlalchemy.orm import Session

from app.models.engagement import Engagement
from app.models.quantification import QuantificationRun
from app.models.mitigation import Mitigation
from app.models.party import Party
from app.schemas.dashboard import (
    DashboardResponse,
    ScenarioSummary,
    PartyExposureSummary,
    MitigationSummary,
)
from app.engine.risk_metrics import mitigation_value


def get_dashboard(db: Session, engagement_id: int) -> DashboardResponse:
    engagement = db.query(Engagement).filter(Engagement.id == engagement_id).first()
    if not engagement:
        raise ValueError("Engagement not found")

    response = DashboardResponse(
        engagement_id=engagement.id,
        engagement_name=engagement.name,
        contract_value=engagement.contract_value,
        currency=engagement.currency,
    )

    # Get latest unmitigated and mitigated runs
    unmit_run = (
        db.query(QuantificationRun)
        .filter(QuantificationRun.engagement_id == engagement_id, QuantificationRun.is_mitigated == False)
        .order_by(QuantificationRun.created_at.desc())
        .first()
    )
    mit_run = (
        db.query(QuantificationRun)
        .filter(QuantificationRun.engagement_id == engagement_id, QuantificationRun.is_mitigated == True)
        .order_by(QuantificationRun.created_at.desc())
        .first()
    )

    if not unmit_run:
        return response

    response.has_results = True

    # Unmitigated metrics
    response.unmitigated_el = unmit_run.total_expected_loss
    response.unmitigated_var_95 = unmit_run.total_var_95
    response.unmitigated_tvar_95 = unmit_run.total_tvar_95
    response.unmitigated_var_99 = unmit_run.total_var_99
    response.unmitigated_risk_asymmetry = unmit_run.risk_asymmetry_ratio
    response.unmitigated_histogram_bins = unmit_run.histogram_bins or []
    response.unmitigated_histogram_counts = unmit_run.histogram_counts or []

    # Mitigated metrics
    if mit_run:
        response.mitigated_el = mit_run.total_expected_loss
        response.mitigated_var_95 = mit_run.total_var_95
        response.mitigated_tvar_95 = mit_run.total_tvar_95
        response.mitigated_var_99 = mit_run.total_var_99
        response.mitigated_risk_asymmetry = mit_run.risk_asymmetry_ratio
        response.mitigated_histogram_bins = mit_run.histogram_bins or []
        response.mitigated_histogram_counts = mit_run.histogram_counts or []

    # Top scenarios from unmitigated run
    for result in unmit_run.results:
        if result.failure_mode_id is not None:
            total_el = unmit_run.total_expected_loss or 1
            response.top_scenarios.append(ScenarioSummary(
                failure_mode_id=result.failure_mode_id,
                name=result.label,
                expected_loss=result.expected_loss,
                var_95=result.var_95,
                contribution_pct=(result.expected_loss / total_el) * 100,
            ))
    response.top_scenarios.sort(key=lambda x: x.expected_loss, reverse=True)

    # Party exposures
    party_map = {p.id: p.name for p in engagement.parties}
    for result in unmit_run.results:
        if result.party_id is not None:
            response.party_exposures.append(PartyExposureSummary(
                party_id=result.party_id,
                party_name=party_map.get(result.party_id, f"Party {result.party_id}"),
                expected_loss=result.expected_loss,
                var_95=result.var_95,
            ))

    # Mitigation summary
    mitigations = db.query(Mitigation).filter(Mitigation.engagement_id == engagement_id).all()
    total_mit_cost = sum(m.cost for m in mitigations)
    if mit_run and unmit_run:
        el_reduction = unmit_run.total_expected_loss - mit_run.total_expected_loss
        roi = mitigation_value(unmit_run.total_expected_loss, mit_run.total_expected_loss, total_mit_cost) if total_mit_cost > 0 else None
        response.mitigation_summary.append(MitigationSummary(
            name="All mitigations (combined)",
            cost=total_mit_cost,
            el_reduction=el_reduction,
            roi=roi,
        ))

    return response
