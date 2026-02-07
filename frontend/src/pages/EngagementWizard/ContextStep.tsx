import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { updateEngagement } from '../../api/engagements';
import { listParties, createParty, deleteParty } from '../../api/parties';
import { listGoodsServices, createGoodsService, deleteGoodsService } from '../../api/goodsServices';
import type { Engagement } from '../../types';

interface Props {
  engagement: Engagement | null;
  engagementId: number | null;
  onCreate: (data: Record<string, unknown>) => Promise<void>;
  onSaved: () => void;
}

export default function ContextStep({ engagement, engagementId, onCreate, onSaved }: Props) {
  const queryClient = useQueryClient();
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm({
    values: engagement ? {
      name: engagement.name,
      description: engagement.description,
      contract_value: engagement.contract_value ?? 0,
      currency: engagement.currency,
      industry: engagement.industry,
    } : { name: '', description: '', contract_value: 0, currency: 'USD', industry: '' },
  });

  const { data: parties = [] } = useQuery({
    queryKey: ['parties', engagementId],
    queryFn: () => listParties(engagementId!),
    enabled: !!engagementId,
  });

  const { data: goodsServices = [] } = useQuery({
    queryKey: ['goodsServices', engagementId],
    queryFn: () => listGoodsServices(engagementId!),
    enabled: !!engagementId,
  });

  const updateMut = useMutation({
    mutationFn: (data: Partial<Engagement>) => updateEngagement(engagementId!, data),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['engagement', engagementId] }); onSaved(); },
  });

  const addPartyMut = useMutation({
    mutationFn: (data: Record<string, unknown>) => createParty(engagementId!, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['parties', engagementId] }),
  });

  const delPartyMut = useMutation({
    mutationFn: (pid: number) => deleteParty(engagementId!, pid),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['parties', engagementId] }),
  });

  const addGSMut = useMutation({
    mutationFn: (data: Record<string, unknown>) => createGoodsService(engagementId!, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['goodsServices', engagementId] }),
  });

  const delGSMut = useMutation({
    mutationFn: (gsid: number) => deleteGoodsService(engagementId!, gsid),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['goodsServices', engagementId] }),
  });

  const [partyForm, setPartyForm] = useState({ name: '', role: 'buyer' });
  const [gsForm, setGSForm] = useState({ name: '', supply_type: 'goods', description: '', use_context: '', replaceability: 'replaceable' });

  const onSubmit = async (data: Record<string, unknown>) => {
    if (engagementId) {
      updateMut.mutate(data as Partial<Engagement>);
    } else {
      await onCreate(data);
    }
  };

  return (
    <div className="space-y-8">
      <form onSubmit={handleSubmit(onSubmit)} className="bg-white rounded-lg shadow p-6 space-y-4">
        <h2 className="text-lg font-semibold">Engagement Details</h2>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
            <input {...register('name', { required: 'Name is required' })} className={`w-full border rounded-md px-3 py-2 ${errors.name ? 'border-red-500' : 'border-gray-300'}`} />
            {errors.name && <p className="text-red-600 text-sm mt-1">{errors.name.message as string}</p>}
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Industry</label>
            <input {...register('industry')} className="w-full border border-gray-300 rounded-md px-3 py-2" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Contract Value</label>
            <input type="number" {...register('contract_value', { valueAsNumber: true })} className="w-full border border-gray-300 rounded-md px-3 py-2" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Currency</label>
            <select {...register('currency')} className="w-full border border-gray-300 rounded-md px-3 py-2">
              <option value="USD">USD</option>
              <option value="EUR">EUR</option>
              <option value="GBP">GBP</option>
              <option value="AUD">AUD</option>
            </select>
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
          <textarea {...register('description')} rows={2} className="w-full border border-gray-300 rounded-md px-3 py-2" />
        </div>
        <button type="submit" disabled={isSubmitting} className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50">
          {isSubmitting ? 'Creating...' : engagementId ? 'Save & Continue' : 'Create Engagement'}
        </button>
      </form>

      {engagementId && (
        <>
          <div className="bg-white rounded-lg shadow p-6 space-y-4">
            <h2 className="text-lg font-semibold">Parties</h2>
            {parties.map((p) => (
              <div key={p.id} className="flex justify-between items-center py-2 border-b">
                <span>{p.name} <span className="text-sm text-gray-500">({p.role})</span></span>
                <button onClick={() => delPartyMut.mutate(p.id)} className="text-red-600 text-sm">Remove</button>
              </div>
            ))}
            <div className="flex gap-2 items-end">
              <div className="flex-1">
                <label className="block text-sm text-gray-600 mb-1">Name</label>
                <input value={partyForm.name} onChange={(e) => setPartyForm({ ...partyForm, name: e.target.value })} className="w-full border border-gray-300 rounded-md px-3 py-2" />
              </div>
              <div>
                <label className="block text-sm text-gray-600 mb-1">Role</label>
                <select value={partyForm.role} onChange={(e) => setPartyForm({ ...partyForm, role: e.target.value })} className="border border-gray-300 rounded-md px-3 py-2">
                  <option value="buyer">Buyer</option>
                  <option value="supplier">Supplier</option>
                  <option value="third_party">Third Party</option>
                  <option value="end_user">End User</option>
                </select>
              </div>
              <button
                onClick={() => { if (partyForm.name) { addPartyMut.mutate(partyForm); setPartyForm({ name: '', role: 'buyer' }); } }}
                className="bg-gray-800 text-white px-3 py-2 rounded-md text-sm"
              >
                Add
              </button>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6 space-y-4">
            <h2 className="text-lg font-semibold">Goods & Services</h2>
            {goodsServices.map((gs) => (
              <div key={gs.id} className="flex justify-between items-center py-2 border-b">
                <span>{gs.name} <span className="text-sm text-gray-500">({gs.supply_type})</span></span>
                <button onClick={() => delGSMut.mutate(gs.id)} className="text-red-600 text-sm">Remove</button>
              </div>
            ))}
            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="block text-sm text-gray-600 mb-1">Name</label>
                <input value={gsForm.name} onChange={(e) => setGSForm({ ...gsForm, name: e.target.value })} className="w-full border border-gray-300 rounded-md px-3 py-2" />
              </div>
              <div>
                <label className="block text-sm text-gray-600 mb-1">Supply Type</label>
                <select value={gsForm.supply_type} onChange={(e) => setGSForm({ ...gsForm, supply_type: e.target.value })} className="w-full border border-gray-300 rounded-md px-3 py-2">
                  <option value="goods">Goods</option>
                  <option value="services">Services</option>
                  <option value="mixed">Mixed</option>
                </select>
              </div>
              <div>
                <label className="block text-sm text-gray-600 mb-1">Description</label>
                <input value={gsForm.description} onChange={(e) => setGSForm({ ...gsForm, description: e.target.value })} className="w-full border border-gray-300 rounded-md px-3 py-2" />
              </div>
              <div>
                <label className="block text-sm text-gray-600 mb-1">Use Context</label>
                <input value={gsForm.use_context} onChange={(e) => setGSForm({ ...gsForm, use_context: e.target.value })} className="w-full border border-gray-300 rounded-md px-3 py-2" />
              </div>
            </div>
            <button
              onClick={() => { if (gsForm.name) { addGSMut.mutate(gsForm); setGSForm({ name: '', supply_type: 'goods', description: '', use_context: '', replaceability: 'replaceable' }); } }}
              className="bg-gray-800 text-white px-3 py-2 rounded-md text-sm"
            >
              Add Goods/Service
            </button>
          </div>
        </>
      )}
    </div>
  );
}
