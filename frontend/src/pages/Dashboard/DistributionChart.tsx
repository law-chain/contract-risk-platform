import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import type { Dashboard } from '../../types';

interface Props {
  dashboard: Dashboard;
}

export default function DistributionChart({ dashboard }: Props) {
  const unmitBins = dashboard.unmitigated_histogram_bins;
  const unmitCounts = dashboard.unmitigated_histogram_counts;
  const mitBins = dashboard.mitigated_histogram_bins;
  const mitCounts = dashboard.mitigated_histogram_counts;

  if (!unmitBins.length) return null;

  // Build combined chart data using unmitigated bins as primary x-axis
  const chartData = unmitBins.map((bin, i) => {
    // Find closest mitigated bin
    const mitIdx = mitBins.length > 0
      ? mitBins.reduce((best, b, j) => Math.abs(b - bin) < Math.abs(mitBins[best] - bin) ? j : best, 0)
      : -1;
    return {
      loss: `${(bin / 1000).toFixed(0)}k`,
      lossVal: bin,
      Unmitigated: unmitCounts[i] || 0,
      Mitigated: mitIdx >= 0 ? (mitCounts[mitIdx] || 0) : 0,
    };
  });

  // Downsample if too many bars
  const maxBars = 30;
  const step = Math.max(1, Math.floor(chartData.length / maxBars));
  const displayData = chartData.filter((_, i) => i % step === 0);

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wide mb-4">
        Loss Distribution
      </h3>
      <ResponsiveContainer width="100%" height={350}>
        <BarChart data={displayData} barGap={0}>
          <XAxis dataKey="loss" tick={{ fontSize: 11 }} />
          <YAxis tick={{ fontSize: 11 }} label={{ value: 'Frequency', angle: -90, position: 'insideLeft', style: { fontSize: 12 } }} />
          <Tooltip
            formatter={(value: unknown, name: unknown) => [(value as number).toLocaleString(), name as string]}
            labelFormatter={(label: unknown) => `Loss: ${label}`}
          />
          <Legend />
          <Bar dataKey="Unmitigated" fill="#ef4444" opacity={0.7} />
          <Bar dataKey="Mitigated" fill="#22c55e" opacity={0.7} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
