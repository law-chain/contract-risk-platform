import client from './client';
import type { Mitigation } from '../types';

export const listMitigations = (engagementId: number) =>
  client.get<Mitigation[]>(`/engagements/${engagementId}/mitigations/`).then(r => r.data);

export const createMitigation = (engagementId: number, data: Partial<Mitigation>) =>
  client.post<Mitigation>(`/engagements/${engagementId}/mitigations/`, data).then(r => r.data);

export const updateMitigation = (engagementId: number, mitId: number, data: Partial<Mitigation>) =>
  client.put<Mitigation>(`/engagements/${engagementId}/mitigations/${mitId}`, data).then(r => r.data);

export const deleteMitigation = (engagementId: number, mitId: number) =>
  client.delete(`/engagements/${engagementId}/mitigations/${mitId}`);

export const linkMitigation = (engagementId: number, mitId: number, data: { failure_mode_id: number; frequency_reduction: number; severity_reduction: number }) =>
  client.post(`/engagements/${engagementId}/mitigations/${mitId}/link`, data).then(r => r.data);

export const unlinkMitigation = (engagementId: number, mitId: number, fmId: number) =>
  client.delete(`/engagements/${engagementId}/mitigations/${mitId}/unlink/${fmId}`);
