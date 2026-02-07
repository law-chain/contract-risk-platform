import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { getDashboard } from '../../api/quantification';
import ExposureSummary from './ExposureSummary';
import ScenarioTable from './ScenarioTable';
import MitigationPanel from './MitigationPanel';
import RiskAsymmetryCard from './RiskAsymmetryCard';
import DistributionChart from './DistributionChart';

export default function DashboardPage() {
  const { id } = useParams<{ id: string }>();
  const engagementId = parseInt(id!);

  const { data: dashboard, isLoading, error } = useQuery({
    queryKey: ['dashboard', engagementId],
    queryFn: () => getDashboard(engagementId),
  });

  if (isLoading) return <div className="text-gray-500">Loading dashboard...</div>;
  if (error) return <div className="text-red-600">Error loading dashboard.</div>;
  if (!dashboard) return null;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{dashboard.engagement_name}</h1>
          <p className="text-sm text-gray-500">
            Contract Value: {dashboard.currency} {dashboard.contract_value?.toLocaleString() ?? 'N/A'}
          </p>
        </div>
        <div className="flex gap-2">
          <Link to={`/engagement/${engagementId}/wizard`} className="bg-blue-100 text-blue-700 px-4 py-2 rounded-md text-sm">
            Edit Engagement
          </Link>
          <Link to="/" className="bg-gray-100 text-gray-700 px-4 py-2 rounded-md text-sm">
            Back to List
          </Link>
        </div>
      </div>

      {!dashboard.has_results ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <p className="text-gray-500 mb-4">No quantification results yet.</p>
          <Link to={`/engagement/${engagementId}/wizard`} className="bg-blue-600 text-white px-6 py-3 rounded-md">
            Go to Wizard to Run Simulation
          </Link>
        </div>
      ) : (
        <>
          <ExposureSummary dashboard={dashboard} />
          <RiskAsymmetryCard dashboard={dashboard} />
          <DistributionChart dashboard={dashboard} />
          <ScenarioTable scenarios={dashboard.top_scenarios} currency={dashboard.currency} />
          <MitigationPanel dashboard={dashboard} />
        </>
      )}
    </div>
  );
}
