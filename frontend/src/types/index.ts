export interface Engagement {
  id: number;
  name: string;
  description: string;
  contract_value: number | null;
  currency: string;
  industry: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface EngagementList {
  id: number;
  name: string;
  industry: string;
  contract_value: number | null;
  currency: string;
  status: string;
  created_at: string;
}

export interface Party {
  id: number;
  engagement_id: number;
  name: string;
  role: string;
  revenue: number | null;
  criticality: string;
  description: string;
}

export interface GoodsService {
  id: number;
  engagement_id: number;
  name: string;
  category: string;
  description: string;
  use_context: string;
  supply_type: string;
  replaceability: string;
}

export interface FailureMode {
  id: number;
  engagement_id: number;
  goods_service_id: number | null;
  name: string;
  description: string;
  category: string;
  frequency_low: number;
  frequency_mid: number;
  frequency_high: number;
  detection: string;
  source: string;
  confidence: number;
  is_included: boolean;
}

export interface LossScenario {
  id: number;
  failure_mode_id: number;
  affected_party_id: number;
  name: string;
  loss_category: string;
  description: string;
  severity: string;
  severity_low: number;
  severity_mid: number;
  severity_high: number;
  distribution_type: string;
}

export interface Mitigation {
  id: number;
  engagement_id: number;
  name: string;
  description: string;
  mitigation_type: string;
  cost: number;
}

export interface QuantificationResult {
  id: number;
  failure_mode_id: number | null;
  loss_scenario_id: number | null;
  party_id: number | null;
  label: string;
  expected_loss: number;
  var_95: number;
  tvar_95: number;
  var_99: number;
  p5: number;
  p25: number;
  p50: number;
  p75: number;
  p95: number;
  p99: number;
  histogram_bins: number[];
  histogram_counts: number[];
}

export interface QuantificationRun {
  id: number;
  engagement_id: number;
  num_simulations: number;
  is_mitigated: boolean;
  total_expected_loss: number;
  total_var_95: number;
  total_tvar_95: number;
  total_var_99: number;
  risk_asymmetry_ratio: number;
  histogram_bins: number[];
  histogram_counts: number[];
  created_at: string;
  results: QuantificationResult[];
}

export interface ScenarioSummary {
  failure_mode_id: number;
  name: string;
  expected_loss: number;
  var_95: number;
  contribution_pct: number;
}

export interface PartyExposure {
  party_id: number;
  party_name: string;
  expected_loss: number;
  var_95: number;
}

export interface MitigationSummary {
  name: string;
  cost: number;
  el_reduction: number;
  roi: number | null;
}

export interface Dashboard {
  engagement_id: number;
  engagement_name: string;
  contract_value: number | null;
  currency: string;
  unmitigated_el: number;
  unmitigated_var_95: number;
  unmitigated_tvar_95: number;
  unmitigated_var_99: number;
  unmitigated_risk_asymmetry: number;
  unmitigated_histogram_bins: number[];
  unmitigated_histogram_counts: number[];
  mitigated_el: number;
  mitigated_var_95: number;
  mitigated_tvar_95: number;
  mitigated_var_99: number;
  mitigated_risk_asymmetry: number;
  mitigated_histogram_bins: number[];
  mitigated_histogram_counts: number[];
  top_scenarios: ScenarioSummary[];
  party_exposures: PartyExposure[];
  mitigation_summary: MitigationSummary[];
  has_results: boolean;
}

export interface AIGenerationResponse {
  data: Record<string, unknown>;
}
