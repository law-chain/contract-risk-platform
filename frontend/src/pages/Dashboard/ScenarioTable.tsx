import type { ScenarioSummary } from '../../types';

interface Props {
  scenarios: ScenarioSummary[];
  currency: string;
}

export default function ScenarioTable({ scenarios, currency }: Props) {
  if (!scenarios.length) return null;

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-4">
        Top Scenarios by Expected Loss
      </h3>
      <table className="w-full">
        <thead>
          <tr className="text-left text-xs font-medium text-gray-500 uppercase border-b">
            <th className="pb-2">Scenario</th>
            <th className="pb-2 text-right">Expected Loss</th>
            <th className="pb-2 text-right">VaR (95%)</th>
            <th className="pb-2 text-right">Contribution</th>
          </tr>
        </thead>
        <tbody>
          {scenarios.map((s) => (
            <tr key={s.failure_mode_id} className="border-b border-gray-100">
              <td className="py-3 text-sm">{s.name}</td>
              <td className="py-3 text-sm text-right font-medium">
                {currency} {s.expected_loss.toLocaleString(undefined, { maximumFractionDigits: 0 })}
              </td>
              <td className="py-3 text-sm text-right">
                {currency} {s.var_95.toLocaleString(undefined, { maximumFractionDigits: 0 })}
              </td>
              <td className="py-3 text-sm text-right">
                <div className="flex items-center justify-end gap-2">
                  <div className="w-16 bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full"
                      style={{ width: `${Math.min(s.contribution_pct, 100)}%` }}
                    />
                  </div>
                  <span className="w-12 text-right">{s.contribution_pct.toFixed(1)}%</span>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
