import type { Dashboard } from '../../types';

interface Props {
  dashboard: Dashboard;
}

export default function RiskAsymmetryCard({ dashboard }: Props) {
  const ratio = dashboard.unmitigated_risk_asymmetry;
  const mitigatedRatio = dashboard.mitigated_risk_asymmetry;

  if (!dashboard.contract_value) return null;

  const riskLevel = ratio >= 2 ? 'Critical' : ratio >= 1 ? 'High' : ratio >= 0.5 ? 'Moderate' : 'Low';
  const riskColor = ratio >= 2 ? 'text-red-700 bg-red-50 border-red-200' : ratio >= 1 ? 'text-orange-700 bg-orange-50 border-orange-200' : ratio >= 0.5 ? 'text-yellow-700 bg-yellow-50 border-yellow-200' : 'text-green-700 bg-green-50 border-green-200';

  return (
    <div className={`rounded-lg shadow p-6 border ${riskColor}`}>
      <h3 className="text-sm font-medium uppercase tracking-wide mb-3">Risk Asymmetry</h3>
      <div className="grid grid-cols-3 gap-4">
        <div>
          <div className="text-2xl font-bold">{ratio.toFixed(2)}x</div>
          <div className="text-sm opacity-75">Unmitigated (P95 / Contract)</div>
        </div>
        <div>
          <div className="text-2xl font-bold">{mitigatedRatio.toFixed(2)}x</div>
          <div className="text-sm opacity-75">Mitigated (P95 / Contract)</div>
        </div>
        <div>
          <div className="text-2xl font-bold">{riskLevel}</div>
          <div className="text-sm opacity-75">
            {ratio >= 1
              ? 'P95 loss exceeds contract value'
              : `P95 loss is ${(ratio * 100).toFixed(0)}% of contract value`}
          </div>
        </div>
      </div>
    </div>
  );
}
