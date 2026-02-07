import client from './client';
import type { AIGenerationResponse } from '../types';

export const generateFailureModes = (engagementId: number, goodsServiceId: number) =>
  client.post<AIGenerationResponse>(`/engagements/${engagementId}/ai/generate-failure-modes`, { goods_service_id: goodsServiceId }).then(r => r.data);

export const estimateLosses = (engagementId: number, failureModeId: number, lossScenarioId: number) =>
  client.post<AIGenerationResponse>(`/engagements/${engagementId}/ai/estimate-losses`, { failure_mode_id: failureModeId, loss_scenario_id: lossScenarioId }).then(r => r.data);

export const suggestMitigations = (engagementId: number) =>
  client.post<AIGenerationResponse>(`/engagements/${engagementId}/ai/suggest-mitigations`, {}).then(r => r.data);
