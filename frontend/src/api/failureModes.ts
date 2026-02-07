import client from './client';
import type { FailureMode } from '../types';

export const listFailureModes = (engagementId: number) =>
  client.get<FailureMode[]>(`/engagements/${engagementId}/failure-modes/`).then(r => r.data);

export const createFailureMode = (engagementId: number, data: Partial<FailureMode>) =>
  client.post<FailureMode>(`/engagements/${engagementId}/failure-modes/`, data).then(r => r.data);

export const updateFailureMode = (engagementId: number, fmId: number, data: Partial<FailureMode>) =>
  client.put<FailureMode>(`/engagements/${engagementId}/failure-modes/${fmId}`, data).then(r => r.data);

export const toggleFailureMode = (engagementId: number, fmId: number) =>
  client.patch<FailureMode>(`/engagements/${engagementId}/failure-modes/${fmId}/toggle`).then(r => r.data);

export const deleteFailureMode = (engagementId: number, fmId: number) =>
  client.delete(`/engagements/${engagementId}/failure-modes/${fmId}`);
