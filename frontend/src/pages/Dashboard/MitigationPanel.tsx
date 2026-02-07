import type { Dashboard } from '../../types';

interface Props {
  dashboard: Dashboard;
}

export default function MitigationPanel({ dashboard }: Props) {
  const { mitigation_summary, party_exposures, currency } = dashboard;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      {mitigation_summary.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-4">
            Mitigation Value
          </h3>
          {mitigation_summary.map((m, i) => (
            <div key={i} className="space-y-2">
              <div className="font-medium">{m.name}</div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Total Mitigation Cost</span>
                <span>{currency} {m.cost.toLocaleString(undefined, { maximumFractionDigits: 0 })}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">EL Reduction</span>
                <span className="text-green-600 font-medium">
                  {currency} {m.el_reduction.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                </span>
              </div>
              {m.roi !== null && (
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">ROI</span>
                  <span className={`font-medium ${m.roi >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {(m.roi * 100).toFixed(0)}%
                  </span>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {party_exposures.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-4">
            Exposure by Party
          </h3>
          <div className="space-y-3">
            {party_exposures.map((pe) => (
              <div key={pe.party_id} className="flex justify-between items-center">
                <span className="text-sm font-medium">{pe.party_name}</span>
                <div className="text-right">
                  <div className="text-sm font-medium">
                    EL: {currency} {pe.expected_loss.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                  </div>
                  <div className="text-xs text-gray-500">
                    VaR 95%: {currency} {pe.var_95.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
