import client from './client';
import type { LossScenario } from '../types';

export const listLossScenarios = (engagementId: number, fmId: number) =>
  client.get<LossScenario[]>(`/engagements/${engagementId}/failure-modes/${fmId}/loss-scenarios/`).then(r => r.data);

export const createLossScenario = (engagementId: number, fmId: number, data: Partial<LossScenario>) =>
  client.post<LossScenario>(`/engagements/${engagementId}/failure-modes/${fmId}/loss-scenarios/`, data).then(r => r.data);

export const updateLossScenario = (engagementId: number, fmId: number, lsId: number, data: Partial<LossScenario>) =>
  client.put<LossScenario>(`/engagements/${engagementId}/failure-modes/${fmId}/loss-scenarios/${lsId}`, data).then(r => r.data);

export const deleteLossScenario = (engagementId: number, fmId: number, lsId: number) =>
  client.delete(`/engagements/${engagementId}/failure-modes/${fmId}/loss-scenarios/${lsId}`);
