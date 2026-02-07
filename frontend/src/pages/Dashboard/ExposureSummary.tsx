import type { Dashboard } from '../../types';

interface Props {
  dashboard: Dashboard;
}

function fmt(value: number, currency: string) {
  return `${currency} ${value.toLocaleString(undefined, { maximumFractionDigits: 0 })}`;
}

export default function ExposureSummary({ dashboard }: Props) {
  const c = dashboard.currency;
  const reduction = dashboard.unmitigated_el - dashboard.mitigated_el;
  const reductionPct = dashboard.unmitigated_el > 0 ? (reduction / dashboard.unmitigated_el * 100) : 0;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-4">Unmitigated Exposure</h3>
        <div className="space-y-3">
          <div className="flex justify-between">
            <span className="text-gray-600">Expected Loss (EL)</span>
            <span className="font-semibold text-red-700">{fmt(dashboard.unmitigated_el, c)}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">VaR (95%)</span>
            <span className="font-semibold">{fmt(dashboard.unmitigated_var_95, c)}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">TVaR (95%)</span>
            <span className="font-semibold">{fmt(dashboard.unmitigated_tvar_95, c)}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">VaR (99%)</span>
            <span className="font-semibold">{fmt(dashboard.unmitigated_var_99, c)}</span>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-4">Mitigated Exposure</h3>
        <div className="space-y-3">
          <div className="flex justify-between">
            <span className="text-gray-600">Expected Loss (EL)</span>
            <span className="font-semibold text-green-700">{fmt(dashboard.mitigated_el, c)}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">VaR (95%)</span>
            <span className="font-semibold">{fmt(dashboard.mitigated_var_95, c)}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">TVaR (95%)</span>
            <span className="font-semibold">{fmt(dashboard.mitigated_tvar_95, c)}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">VaR (99%)</span>
            <span className="font-semibold">{fmt(dashboard.mitigated_var_99, c)}</span>
          </div>
          {reduction > 0 && (
            <div className="border-t pt-3 mt-3">
              <div className="flex justify-between">
                <span className="text-gray-600">EL Reduction</span>
                <span className="font-semibold text-green-600">
                  {fmt(reduction, c)} ({reductionPct.toFixed(1)}%)
                </span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
