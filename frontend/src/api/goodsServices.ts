import client from './client';
import type { GoodsService } from '../types';

export const listGoodsServices = (engagementId: number) =>
  client.get<GoodsService[]>(`/engagements/${engagementId}/goods-services/`).then(r => r.data);

export const createGoodsService = (engagementId: number, data: Partial<GoodsService>) =>
  client.post<GoodsService>(`/engagements/${engagementId}/goods-services/`, data).then(r => r.data);

export const updateGoodsService = (engagementId: number, gsId: number, data: Partial<GoodsService>) =>
  client.put<GoodsService>(`/engagements/${engagementId}/goods-services/${gsId}`, data).then(r => r.data);

export const deleteGoodsService = (engagementId: number, gsId: number) =>
  client.delete(`/engagements/${engagementId}/goods-services/${gsId}`);
