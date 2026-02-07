import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { listFailureModes } from '../../api/failureModes';
import { listParties } from '../../api/parties';
import { listLossScenarios, createLossScenario, deleteLossScenario } from '../../api/lossScenarios';
import type { LossScenario, FailureMode, Party } from '../../types';

interface Props {
  engagementId: number;
}

const LOSS_CATEGORIES = [
  'Direct / Replacement Cost', 'Revenue Loss / Lost Sales', 'Business Interruption',
  'Regulatory Fines & Penalties', 'Litigation & Legal Costs', 'Remediation & Rectification',
  'Reputational Damage', 'Customer Compensation', 'Third Party Liability',
  'Increased Operating Costs', 'Consequential / Indirect Loss', 'Other',
];

export default function LossMappingStep({ engagementId }: Props) {
  const queryClient = useQueryClient();
  const { data: failureModes = [] } = useQuery({
    queryKey: ['failureModes', engagementId],
    queryFn: () => listFailureModes(engagementId),
  });
  const { data: parties = [] } = useQuery({
    queryKey: ['parties', engagementId],
    queryFn: () => listParties(engagementId),
  });

  const [selectedFM, setSelectedFM] = useState<number | null>(null);
  const activeFMs = failureModes.filter((fm: FailureMode) => fm.is_included);

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">Loss Mapping</h2>
        <p className="text-sm text-gray-600 mb-4">For each failure mode, map out who loses what and how much.</p>

        <div className="flex gap-2 flex-wrap mb-6">
          {activeFMs.map((fm: FailureMode) => (
            <button
              key={fm.id}
              onClick={() => setSelectedFM(fm.id)}
              className={`px-3 py-1.5 rounded-md text-sm ${selectedFM === fm.id ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`}
            >
              {fm.name}
            </button>
          ))}
        </div>

        {selectedFM && (
          <LossScenarioPanel
            engagementId={engagementId}
            failureModeId={selectedFM}
            parties={parties}
            queryClient={queryClient}
          />
        )}
      </div>
    </div>
  );
}

function LossScenarioPanel({ engagementId, failureModeId, parties, queryClient }: {
  engagementId: number; failureModeId: number; parties: Party[]; queryClient: ReturnType<typeof useQueryClient>;
}) {
  const { data: scenarios = [] } = useQuery({
    queryKey: ['lossScenarios', engagementId, failureModeId],
    queryFn: () => listLossScenarios(engagementId, failureModeId),
  });

  const [form, setForm] = useState({
    affected_party_id: parties[0]?.id ?? 0,
    name: '',
    loss_category: LOSS_CATEGORIES[0],
    severity_low: 1000,
    severity_mid: 10000,
    severity_high: 100000,
    distribution_type: 'lognormal',
  });

  const createMut = useMutation({
    mutationFn: (data: Partial<LossScenario>) => createLossScenario(engagementId, failureModeId, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['lossScenarios', engagementId, failureModeId] }),
  });
  const deleteMut = useMutation({
    mutationFn: (lsId: number) => deleteLossScenario(engagementId, failureModeId, lsId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['lossScenarios', engagementId, failureModeId] }),
  });

  return (
    <div className="border-t pt-4">
      {scenarios.map((ls: LossScenario) => (
        <div key={ls.id} className="border rounded-md p-3 mb-2 bg-gray-50">
          <div className="flex justify-between">
            <div>
              <span className="font-medium">{ls.name || ls.loss_category}</span>
              <span className="text-sm text-gray-500 ml-2">
                Party: {parties.find((p: Party) => p.id === ls.affected_party_id)?.name ?? 'Unknown'}
              </span>
            </div>
            <button onClick={() => deleteMut.mutate(ls.id)} className="text-red-600 text-sm">Remove</button>
          </div>
          <div className="text-xs text-gray-500 mt-1">
            {ls.distribution_type} | Low: ${ls.severity_low.toLocaleString()} | Mid: ${ls.severity_mid.toLocaleString()} | High: ${ls.severity_high.toLocaleString()}
          </div>
        </div>
      ))}

      <div className="mt-4 grid grid-cols-2 gap-2">
        <div>
          <label className="text-xs text-gray-500">Affected Party</label>
          <select value={form.affected_party_id} onChange={(e) => setForm({ ...form, affected_party_id: +e.target.value })} className="w-full border border-gray-300 rounded-md px-3 py-2">
            {parties.map((p: Party) => <option key={p.id} value={p.id}>{p.name} ({p.role})</option>)}
          </select>
        </div>
        <div>
          <label className="text-xs text-gray-500">Loss Category</label>
          <select value={form.loss_category} onChange={(e) => setForm({ ...form, loss_category: e.target.value })} className="w-full border border-gray-300 rounded-md px-3 py-2">
            {LOSS_CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
          </select>
        </div>
        <div>
          <label className="text-xs text-gray-500">Name</label>
          <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} className="w-full border border-gray-300 rounded-md px-3 py-2" />
        </div>
        <div>
          <label className="text-xs text-gray-500">Distribution</label>
          <select value={form.distribution_type} onChange={(e) => setForm({ ...form, distribution_type: e.target.value })} className="w-full border border-gray-300 rounded-md px-3 py-2">
            <option value="lognormal">Lognormal</option>
            <option value="triangular">Triangular</option>
            <option value="uniform">Uniform</option>
          </select>
        </div>
        <div>
          <label className="text-xs text-gray-500">Severity Low ($)</label>
          <input type="number" value={form.severity_low} onChange={(e) => setForm({ ...form, severity_low: +e.target.value })} className="w-full border border-gray-300 rounded-md px-3 py-2" />
        </div>
        <div>
          <label className="text-xs text-gray-500">Severity Mid ($)</label>
          <input type="number" value={form.severity_mid} onChange={(e) => setForm({ ...form, severity_mid: +e.target.value })} className="w-full border border-gray-300 rounded-md px-3 py-2" />
        </div>
        <div>
          <label className="text-xs text-gray-500">Severity High ($)</label>
          <input type="number" value={form.severity_high} onChange={(e) => setForm({ ...form, severity_high: +e.target.value })} className="w-full border border-gray-300 rounded-md px-3 py-2" />
        </div>
      </div>
      <button
        onClick={() => { if (form.affected_party_id) { createMut.mutate(form); } }}
        className="mt-2 bg-gray-800 text-white px-4 py-2 rounded-md text-sm"
      >
        Add Loss Scenario
      </button>
    </div>
  );
}
