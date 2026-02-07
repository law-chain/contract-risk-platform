import client from './client';
import type { QuantificationRun, Dashboard } from '../types';

export const runQuantification = (engagementId: number, numSimulations: number = 10000) =>
  client.post<QuantificationRun[]>(`/engagements/${engagementId}/quantification/run`, { num_simulations: numSimulations }).then(r => r.data);

export const listRuns = (engagementId: number) =>
  client.get<QuantificationRun[]>(`/engagements/${engagementId}/quantification/runs`).then(r => r.data);

export const getDashboard = (engagementId: number) =>
  client.get<Dashboard>(`/engagements/${engagementId}/dashboard/`).then(r => r.data);
