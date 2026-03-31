import api from './index'
import type { UserInfo, UserCreateForm, UserUpdateForm, PaginatedResponse } from '@/types'

export interface UserLog {
  id: number
  action: string
  detail: string | null
  ip_address: string | null
  created_at: string | null
}

export function getUsers(skip = 0, limit = 100, search?: string): Promise<PaginatedResponse<UserInfo>> {
  return api.get('/users', {
    params: { skip, limit, search }
  }).then(res => res.data)
}

export function createUser(data: UserCreateForm): Promise<UserInfo> {
  return api.post('/users', data).then(res => res.data)
}

export function getUser(userId: number): Promise<UserInfo> {
  return api.get(`/users/${userId}`).then(res => res.data)
}

export function updateUser(userId: number, data: UserUpdateForm): Promise<UserInfo> {
  return api.put(`/users/${userId}`, data).then(res => res.data)
}

export function updateUserStatus(userId: number, isActive: boolean): Promise<{ message: string }> {
  return api.put(`/users/${userId}/status`, { is_active: isActive }).then(res => res.data)
}

export function updateUserRole(userId: number, role: 'admin' | 'user'): Promise<{ message: string }> {
  return api.put(`/users/${userId}/role`, { role }).then(res => res.data)
}

export function deleteUser(userId: number): Promise<{ message: string }> {
  return api.delete(`/users/${userId}`).then(res => res.data)
}

export function getUserLogs(userId: number, limit = 100): Promise<PaginatedResponse<UserLog>> {
  return api.get(`/users/${userId}/logs`, {
    params: { limit }
  }).then(res => res.data)
}
