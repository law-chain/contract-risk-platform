import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { listMitigations, createMitigation, deleteMitigation, linkMitigation } from '../../api/mitigations';
import { listFailureModes } from '../../api/failureModes';
import { suggestMitigations } from '../../api/ai';
import type { Mitigation, FailureMode } from '../../types';

interface Props {
  engagementId: number;
}

export default function MitigationsStep({ engagementId }: Props) {
  const queryClient = useQueryClient();
  const { data: mitigations = [] } = useQuery({
    queryKey: ['mitigations', engagementId],
    queryFn: () => listMitigations(engagementId),
  });
  const { data: failureModes = [] } = useQuery({
    queryKey: ['failureModes', engagementId],
    queryFn: () => listFailureModes(engagementId),
  });
  const activeFMs = failureModes.filter((fm: FailureMode) => fm.is_included);

  const [form, setForm] = useState({ name: '', description: '', mitigation_type: 'operational', cost: 0 });
  const [linkForm, setLinkForm] = useState({ mitigation_id: 0, failure_mode_id: 0, frequency_reduction: 0.2, severity_reduction: 0.1 });
  const [aiLoading, setAiLoading] = useState(false);
  const [aiResults, setAiResults] = useState<Record<string, unknown>[] | null>(null);

  const createMut = useMutation({
    mutationFn: (data: Partial<Mitigation>) => createMitigation(engagementId, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['mitigations', engagementId] }),
  });
  const deleteMut = useMutation({
    mutationFn: (id: number) => deleteMitigation(engagementId, id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['mitigations', engagementId] }),
  });
  const linkMut = useMutation({
    mutationFn: (data: { mitigation_id: number; failure_mode_id: number; frequency_reduction: number; severity_reduction: number }) =>
      linkMitigation(engagementId, data.mitigation_id, {
        failure_mode_id: data.failure_mode_id,
        frequency_reduction: data.frequency_reduction,
        severity_reduction: data.severity_reduction,
      }),
  });

  const handleAISuggest = async () => {
    setAiLoading(true);
    setAiResults(null);
    try {
      const response = await suggestMitigations(engagementId);
      const mits = (response.data as { mitigations?: Record<string, unknown>[] }).mitigations || [];
      setAiResults(mits);
    } catch {
      alert('AI suggestion failed. Check your API key.');
    }
    setAiLoading(false);
  };

  const acceptAIMitigation = (mit: Record<string, unknown>) => {
    createMut.mutate({
      name: mit.name as string,
      description: mit.description as string,
      mitigation_type: mit.mitigation_type as string,
      cost: mit.estimated_cost as number ?? 0,
    });
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">Mitigations</h2>

        {mitigations.map((m: Mitigation) => (
          <div key={m.id} className="border rounded-md p-4 mb-3 bg-green-50 border-green-200">
            <div className="flex justify-between items-start">
              <div>
                <div className="font-medium">{m.name}</div>
                <div className="text-sm text-gray-600">{m.description}</div>
                <div className="text-xs text-gray-500 mt-1">Type: {m.mitigation_type} | Cost: ${m.cost.toLocaleString()}</div>
              </div>
              <button onClick={() => deleteMut.mutate(m.id)} className="text-red-600 text-sm">Remove</button>
            </div>
          </div>
        ))}

        <div className="mt-4 border-t pt-4">
          <h3 className="font-medium mb-2">Add Mitigation</h3>
          <div className="grid grid-cols-2 gap-2 mb-2">
            <input placeholder="Name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} className="border border-gray-300 rounded-md px-3 py-2" />
            <input placeholder="Description" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} className="border border-gray-300 rounded-md px-3 py-2" />
            <input type="number" placeholder="Cost" value={form.cost} onChange={(e) => setForm({ ...form, cost: +e.target.value })} className="border border-gray-300 rounded-md px-3 py-2" />
          </div>
          <button onClick={() => { if (form.name) { createMut.mutate(form); setForm({ name: '', description: '', mitigation_type: 'operational', cost: 0 }); } }}
            className="bg-gray-800 text-white px-4 py-2 rounded-md text-sm">
            Add Mitigation
          </button>
        </div>
      </div>

      {mitigations.length > 0 && activeFMs.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">Link Mitigations to Failure Modes</h2>
          <div className="grid grid-cols-2 gap-2 mb-2">
            <div>
              <label className="text-xs text-gray-500">Mitigation</label>
              <select value={linkForm.mitigation_id} onChange={(e) => setLinkForm({ ...linkForm, mitigation_id: +e.target.value })} className="w-full border border-gray-300 rounded-md px-3 py-2">
                <option value={0}>Select...</option>
                {mitigations.map((m: Mitigation) => <option key={m.id} value={m.id}>{m.name}</option>)}
              </select>
            </div>
            <div>
              <label className="text-xs text-gray-500">Failure Mode</label>
              <select value={linkForm.failure_mode_id} onChange={(e) => setLinkForm({ ...linkForm, failure_mode_id: +e.target.value })} className="w-full border border-gray-300 rounded-md px-3 py-2">
                <option value={0}>Select...</option>
                {activeFMs.map((fm: FailureMode) => <option key={fm.id} value={fm.id}>{fm.name}</option>)}
              </select>
            </div>
            <div>
              <label className="text-xs text-gray-500">Frequency Reduction (0-1)</label>
              <input type="number" step="0.05" min="0" max="1" value={linkForm.frequency_reduction} onChange={(e) => setLinkForm({ ...linkForm, frequency_reduction: +e.target.value })} className="w-full border border-gray-300 rounded-md px-3 py-2" />
            </div>
            <div>
              <label className="text-xs text-gray-500">Severity Reduction (0-1)</label>
              <input type="number" step="0.05" min="0" max="1" value={linkForm.severity_reduction} onChange={(e) => setLinkForm({ ...linkForm, severity_reduction: +e.target.value })} className="w-full border border-gray-300 rounded-md px-3 py-2" />
            </div>
          </div>
          <button
            onClick={() => { if (linkForm.mitigation_id && linkForm.failure_mode_id) linkMut.mutate(linkForm); }}
            className="bg-green-700 text-white px-4 py-2 rounded-md text-sm"
          >
            Link
          </button>
        </div>
      )}

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">AI-Suggested Mitigations</h2>
        <button onClick={handleAISuggest} disabled={aiLoading} className="bg-purple-600 text-white px-4 py-2 rounded-md text-sm hover:bg-purple-700 disabled:opacity-50">
          {aiLoading ? 'Generating...' : 'Suggest Mitigations with AI'}
        </button>
        {aiResults && (
          <div className="mt-4 space-y-3">
            {aiResults.map((mit, i) => (
              <div key={i} className="border border-purple-200 bg-purple-50 rounded-md p-3 cursor-pointer hover:bg-purple-100" onClick={() => acceptAIMitigation(mit)}>
                <div className="font-medium">{mit.name as string}</div>
                <div className="text-sm text-gray-600">{mit.description as string}</div>
                <div className="text-xs text-gray-500 mt-1">Est. cost: ${(mit.estimated_cost as number ?? 0).toLocaleString()}</div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
