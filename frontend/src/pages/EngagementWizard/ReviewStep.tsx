import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { getEngagement } from '../../api/engagements';
import { listParties } from '../../api/parties';
import { listFailureModes } from '../../api/failureModes';
import { listLossScenarios } from '../../api/lossScenarios';
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

  // Query loss scenarios for each active failure mode to check readiness
  const { data: lossScenarioCounts = {} } = useQuery({
    queryKey: ['lossScenarioCounts', engagementId, activeFMs.map(fm => fm.id)],
    queryFn: async () => {
      const counts: Record<number, number> = {};
      await Promise.all(activeFMs.map(async (fm) => {
        const scenarios = await listLossScenarios(engagementId, fm.id);
        counts[fm.id] = scenarios.length;
      }));
      return counts;
    },
    enabled: activeFMs.length > 0,
  });

  const fmsWithScenarios = activeFMs.filter(fm => (lossScenarioCounts[fm.id] ?? 0) > 0);
  const fmsWithoutScenarios = activeFMs.filter(fm => (lossScenarioCounts[fm.id] ?? 0) === 0);
  const canRun = fmsWithScenarios.length > 0;

  const handleRun = async () => {
    setRunning(true);
    try {
      await runQuantification(engagementId, simCount);
      navigate(`/engagement/${engagementId}/dashboard`);
    } catch (err) {
      let msg = 'Unknown error';
      if (axios.isAxiosError(err) && err.response?.data?.detail) {
        msg = err.response.data.detail;
      } else if (err instanceof Error) {
        msg = err.message;
      }
      alert(`Quantification failed: ${msg}`);
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
            {activeFMs.map((fm) => {
              const scenarioCount = lossScenarioCounts[fm.id] ?? 0;
              return (
                <p key={fm.id} className="text-sm">
                  {fm.name} <span className="text-gray-500">({fm.category}, freq: {fm.frequency_mid}/yr)</span>
                  {scenarioCount > 0
                    ? <span className="ml-2 text-green-600">{scenarioCount} loss scenario{scenarioCount !== 1 ? 's' : ''}</span>
                    : <span className="ml-2 text-red-500">no loss scenarios mapped</span>}
                </p>
              );
            })}
          </div>
          {fmsWithoutScenarios.length > 0 && (
            <p className="text-amber-600 text-sm mt-2">
              {fmsWithoutScenarios.length} failure mode{fmsWithoutScenarios.length !== 1 ? 's have' : ' has'} no loss scenarios.
              Go to Step 3 (Loss Mapping) to add loss scenarios before running.
            </p>
          )}
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
            disabled={running || !canRun}
            className="bg-blue-600 text-white px-6 py-3 rounded-md font-medium hover:bg-blue-700 disabled:opacity-50"
          >
            {running ? 'Running Simulation...' : 'Run Monte Carlo Simulation'}
          </button>
        </div>
        {activeFMs.length === 0 && (
          <p className="text-red-600 text-sm mt-2">Add at least one failure mode to run. Go to Step 2 (Failure Modes).</p>
        )}
        {activeFMs.length > 0 && !canRun && (
          <p className="text-red-600 text-sm mt-2">Your failure modes need loss scenarios before you can run. Go to Step 3 (Loss Mapping) to map losses.</p>
        )}
      </div>
    </div>
  );
}
