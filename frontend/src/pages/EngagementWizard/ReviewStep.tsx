import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { getEngagement } from '../../api/engagements';
import { listParties } from '../../api/parties';
import { listFailureModes } from '../../api/failureModes';
import { listMitigations } from '../../api/mitigations';
import { runQuantification } from '../../api/quantification';

interface Props {
  engagementId: number;
}

export default function ReviewStep({ engagementId }: Props) {
  const navigate = useNavigate();
  const [running, setRunning] = useState(false);
  const [simCount, setSimCount] = useState(10000);

  const { data: engagement } = useQuery({
    queryKey: ['engagement', engagementId],
    queryFn: () => getEngagement(engagementId),
  });
  const { data: parties = [] } = useQuery({
    queryKey: ['parties', engagementId],
    queryFn: () => listParties(engagementId),
  });
  const { data: failureModes = [] } = useQuery({
    queryKey: ['failureModes', engagementId],
    queryFn: () => listFailureModes(engagementId),
  });
  const { data: mitigations = [] } = useQuery({
    queryKey: ['mitigations', engagementId],
    queryFn: () => listMitigations(engagementId),
  });

  const activeFMs = failureModes.filter((fm) => fm.is_included);

  const handleRun = async () => {
    setRunning(true);
    try {
      await runQuantification(engagementId, simCount);
      navigate(`/engagement/${engagementId}/dashboard`);
    } catch (err) {
      alert('Quantification failed: ' + (err instanceof Error ? err.message : 'Unknown error'));
      setRunning(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">Review</h2>

        <div className="grid grid-cols-2 gap-6">
          <div>
            <h3 className="font-medium text-gray-700 mb-2">Engagement</h3>
            <p className="text-sm">{engagement?.name}</p>
            <p className="text-sm text-gray-500">{engagement?.industry} &middot; {engagement?.currency} {engagement?.contract_value?.toLocaleString()}</p>
          </div>
          <div>
            <h3 className="font-medium text-gray-700 mb-2">Parties ({parties.length})</h3>
            {parties.map((p) => (
              <p key={p.id} className="text-sm">{p.name} <span className="text-gray-500">({p.role})</span></p>
            ))}
          </div>
        </div>

        <div className="mt-4">
          <h3 className="font-medium text-gray-700 mb-2">Active Failure Modes ({activeFMs.length})</h3>
          <div className="space-y-1">
            {activeFMs.map((fm) => (
              <p key={fm.id} className="text-sm">
                {fm.name} <span className="text-gray-500">({fm.category}, freq: {fm.frequency_mid}/yr)</span>
              </p>
            ))}
          </div>
        </div>

        <div className="mt-4">
          <h3 className="font-medium text-gray-700 mb-2">Mitigations ({mitigations.length})</h3>
          <div className="space-y-1">
            {mitigations.map((m) => (
              <p key={m.id} className="text-sm">{m.name} <span className="text-gray-500">(cost: ${m.cost.toLocaleString()})</span></p>
            ))}
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">Run Quantification</h2>
        <div className="flex items-center gap-4">
          <div>
            <label className="text-sm text-gray-600 mr-2">Simulations:</label>
            <select value={simCount} onChange={(e) => setSimCount(+e.target.value)} className="border border-gray-300 rounded-md px-3 py-2">
              <option value={1000}>1,000</option>
              <option value={5000}>5,000</option>
              <option value={10000}>10,000</option>
              <option value={50000}>50,000</option>
            </select>
          </div>
          <button
            onClick={handleRun}
            disabled={running || activeFMs.length === 0}
            className="bg-blue-600 text-white px-6 py-3 rounded-md font-medium hover:bg-blue-700 disabled:opacity-50"
          >
            {running ? 'Running Simulation...' : 'Run Monte Carlo Simulation'}
          </button>
        </div>
        {activeFMs.length === 0 && (
          <p className="text-red-600 text-sm mt-2">Add at least one failure mode with loss scenarios to run.</p>
        )}
      </div>
    </div>
  );
}
