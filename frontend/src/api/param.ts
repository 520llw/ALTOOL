import api from './index'
import type {
  StandardParam,
  ParamWithVariants,
  ParamCreateForm,
  ParamUpdateForm,
  VariantCreateForm,
  PaginatedResponse,
  ListResponse
} from '@/types'

export function getParams(
  skip = 0,
  limit = 100,
  search?: string,
  category?: string,
  paramType?: string
): Promise<PaginatedResponse<StandardParam>> {
  return api.get('/params', {
    params: { skip, limit, search, category, param_type: paramType }
  }).then(res => res.data)
}

export function createParam(data: ParamCreateForm): Promise<StandardParam> {
  return api.post('/params', data).then(res => res.data)
}

export function getParam(paramId: number): Promise<ParamWithVariants> {
  return api.get(`/params/${paramId}`).then(res => res.data)
}

export function updateParam(paramId: number, data: ParamUpdateForm): Promise<StandardParam> {
  return api.put(`/params/${paramId}`, data).then(res => res.data)
}

export function deleteParam(paramId: number): Promise<{ message: string }> {
  return api.delete(`/params/${paramId}`).then(res => res.data)
}

export function getVariants(paramId: number): Promise<PaginatedResponse<{ id: number; param_id: number; variant_name: string; vendor: string | null; create_time: string }>> {
  return api.get(`/params/${paramId}/variants`).then(res => res.data)
}

export function createVariant(paramId: number, data: VariantCreateForm): Promise<{ id: number; param_id: number; variant_name: string; vendor: string | null; create_time: string }> {
  return api.post(`/params/${paramId}/variants`, data).then(res => res.data)
}

export function deleteVariant(paramId: number, variantId: number): Promise<{ message: string }> {
  return api.delete(`/params/${paramId}/variants/${variantId}`).then(res => res.data)
}

export function getCategories(): Promise<ListResponse<string>> {
  return api.get('/params/categories/list').then(res => res.data)
}

export function getDeviceTypes(): Promise<ListResponse<string>> {
  return api.get('/params/device-types/list').then(res => res.data)
}

export function getAllParamsWithVariants(): Promise<PaginatedResponse<StandardParam & { variants: string[] }>> {
  return api.get('/params/all/with-variants').then(res => res.data)
}
