import client from './client';
import type { Party } from '../types';

export const listParties = (engagementId: number) =>
  client.get<Party[]>(`/engagements/${engagementId}/parties/`).then(r => r.data);

export const createParty = (engagementId: number, data: Partial<Party>) =>
  client.post<Party>(`/engagements/${engagementId}/parties/`, data).then(r => r.data);

export const updateParty = (engagementId: number, partyId: number, data: Partial<Party>) =>
  client.put<Party>(`/engagements/${engagementId}/parties/${partyId}`, data).then(r => r.data);

export const deleteParty = (engagementId: number, partyId: number) =>
  client.delete(`/engagements/${engagementId}/parties/${partyId}`);
