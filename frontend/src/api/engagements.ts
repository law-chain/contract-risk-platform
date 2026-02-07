import client from './client';
import type { Engagement, EngagementList } from '../types';

export const listEngagements = () =>
  client.get<EngagementList[]>('/engagements/').then(r => r.data);

export const getEngagement = (id: number) =>
  client.get<Engagement>(`/engagements/${id}`).then(r => r.data);

export const createEngagement = (data: Partial<Engagement>) =>
  client.post<Engagement>('/engagements/', data).then(r => r.data);

export const updateEngagement = (id: number, data: Partial<Engagement>) =>
  client.put<Engagement>(`/engagements/${id}`, data).then(r => r.data);

export const deleteEngagement = (id: number) =>
  client.delete(`/engagements/${id}`);
