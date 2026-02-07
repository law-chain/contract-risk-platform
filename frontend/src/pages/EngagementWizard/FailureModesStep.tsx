import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { listFailureModes, createFailureMode, toggleFailureMode, deleteFailureMode } from '../../api/failureModes';
import { listGoodsServices } from '../../api/goodsServices';
import { generateFailureModes } from '../../api/ai';
import type { FailureMode } from '../../types';

interface Props {
  engagementId: number;
}

export default function FailureModesStep({ engagementId }: Props) {
  const queryClient = useQueryClient();
  const { data: failureModes = [] } = useQuery({
    queryKey: ['failureModes', engagementId],
    queryFn: () => listFailureModes(engagementId),
  });
  const { data: goodsServices = [] } = useQuery({
    queryKey: ['goodsServices', engagementId],
    queryFn: () => listGoodsServices(engagementId),
  });

  const [form, setForm] = useState({
    name: '', description: '', category: '', goods_service_id: null as number | null,
    frequency_low: 0.1, frequency_mid: 0.5, frequency_high: 1.0,
  });
  const [aiLoading, setAiLoading] = useState(false);
  const [aiResults, setAiResults] = useState<Record<string, unknown>[] | null>(null);

  const createMut = useMutation({
    mutationFn: (data: Partial<FailureMode>) => createFailureMode(engagementId, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['failureModes', engagementId] }),
  });
  const toggleMut = useMutation({
    mutationFn: (id: number) => toggleFailureMode(engagementId, id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['failureModes', engagementId] }),
  });
  const deleteMut = useMutation({
    mutationFn: (id: number) => deleteFailureMode(engagementId, id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['failureModes', engagementId] }),
  });

  const handleAIGenerate = async (gsId: number) => {
    setAiLoading(true);
    setAiResults(null);
    try {
      const response = await generateFailureModes(engagementId, gsId);
      const fms = (response.data as { failure_modes?: Record<string, unknown>[] }).failure_modes || [];
      setAiResults(fms);
    } catch {
      alert('AI generation failed. Check your API key.');
    }
    setAiLoading(false);
  };

  const acceptAIResult = (fm: Record<string, unknown>) => {
    createMut.mutate({
      name: fm.name as string,
      description: fm.description as string,
      category: fm.category as string,
      frequency_low: fm.frequency_low as number,
      frequency_mid: fm.frequency_mid as number,
      frequency_high: fm.frequency_high as number,
      source: 'ai',
      confidence: (fm.confidence as number) ?? 0.5,
    });
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">Failure Modes</h2>

        {failureModes.map((fm) => (
          <div key={fm.id} className={`border rounded-md p-4 mb-3 ${fm.is_included ? 'border-blue-200 bg-blue-50' : 'border-gray-200 bg-gray-50 opacity-60'}`}>
            <div className="flex justify-between items-start">
              <div>
                <div className="font-medium">{fm.name}</div>
                <div className="text-sm text-gray-600">{fm.category}</div>
                <div className="text-xs text-gray-500 mt-1">
                  Frequency: {fm.frequency_low} / {fm.frequency_mid} / {fm.frequency_high} per year
                  {fm.source === 'ai' && <span className="ml-2 bg-purple-100 text-purple-700 px-1.5 py-0.5 rounded text-xs">AI</span>}
                </div>
              </div>
              <div className="flex gap-2">
                <button onClick={() => toggleMut.mutate(fm.id)} className="text-sm text-blue-600">
                  {fm.is_included ? 'Exclude' : 'Include'}
                </button>
                <button onClick={() => deleteMut.mutate(fm.id)} className="text-sm text-red-600">Delete</button>
              </div>
            </div>
          </div>
        ))}

        <div className="mt-4 border-t pt-4">
          <h3 className="font-medium mb-2">Add Manually</h3>
          <div className="grid grid-cols-3 gap-2 mb-2">
            <input placeholder="Name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} className="border border-gray-300 rounded-md px-3 py-2" />
            <input placeholder="Category" value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })} className="border border-gray-300 rounded-md px-3 py-2" />
            <input placeholder="Description" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} className="border border-gray-300 rounded-md px-3 py-2" />
          </div>
          <div className="grid grid-cols-3 gap-2 mb-2">
            <div>
              <label className="text-xs text-gray-500">Freq Low</label>
              <input type="number" step="0.1" value={form.frequency_low} onChange={(e) => setForm({ ...form, frequency_low: +e.target.value })} className="w-full border border-gray-300 rounded-md px-3 py-2" />
            </div>
            <div>
              <label className="text-xs text-gray-500">Freq Mid</label>
              <input type="number" step="0.1" value={form.frequency_mid} onChange={(e) => setForm({ ...form, frequency_mid: +e.target.value })} className="w-full border border-gray-300 rounded-md px-3 py-2" />
            </div>
            <div>
              <label className="text-xs text-gray-500">Freq High</label>
              <input type="number" step="0.1" value={form.frequency_high} onChange={(e) => setForm({ ...form, frequency_high: +e.target.value })} className="w-full border border-gray-300 rounded-md px-3 py-2" />
            </div>
          </div>
          <button
            onClick={() => { if (form.name) { createMut.mutate(form); setForm({ name: '', description: '', category: '', goods_service_id: null, frequency_low: 0.1, frequency_mid: 0.5, frequency_high: 1.0 }); } }}
            className="bg-gray-800 text-white px-4 py-2 rounded-md text-sm"
          >
            Add Failure Mode
          </button>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">AI-Powered Generation</h2>
        <p className="text-sm text-gray-600 mb-4">Select a goods/service to generate context-specific failure modes.</p>
        <div className="flex gap-2 flex-wrap">
          {goodsServices.map((gs) => (
            <button
              key={gs.id}
              onClick={() => handleAIGenerate(gs.id)}
              disabled={aiLoading}
              className="bg-purple-600 text-white px-4 py-2 rounded-md text-sm hover:bg-purple-700 disabled:opacity-50"
            >
              Generate for: {gs.name}
            </button>
          ))}
        </div>
        {aiLoading && <div className="mt-4 text-purple-600">Generating failure modes with AI...</div>}
        {aiResults && (
          <div className="mt-4 space-y-3">
            <h3 className="font-medium">AI Suggestions (click to accept)</h3>
            {aiResults.map((fm, i) => (
              <div key={i} className="border border-purple-200 bg-purple-50 rounded-md p-3 cursor-pointer hover:bg-purple-100"
                onClick={() => acceptAIResult(fm)}>
                <div className="font-medium">{fm.name as string}</div>
                <div className="text-sm text-gray-600">{fm.description as string}</div>
                <div className="text-xs text-gray-500 mt-1">
                  Freq: {fm.frequency_low as number}/{fm.frequency_mid as number}/{fm.frequency_high as number} | Confidence: {((fm.confidence as number ?? 0) * 100).toFixed(0)}%
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
