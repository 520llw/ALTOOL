import api from './index'
import type { LoginForm, TokenResponse, UserInfo, PasswordChangeForm, ApiKeyForm } from '@/types'

export function login(data: LoginForm): Promise<TokenResponse> {
  return api.post('/auth/login', data).then(res => res.data)
}

export function refreshToken(credentials: string): Promise<TokenResponse> {
  return api.post('/auth/refresh', null, {
    params: { credentials }
  }).then(res => res.data)
}

export function logout(): Promise<{ message: string }> {
  return api.post('/auth/logout').then(res => res.data)
}

export function getMe(): Promise<UserInfo> {
  return api.get('/auth/me').then(res => res.data)
}

export function updateMe(data: { username: string }): Promise<{ message: string }> {
  return api.put('/auth/me', data).then(res => res.data)
}

export function changePassword(data: PasswordChangeForm): Promise<{ message: string }> {
  return api.put('/auth/me/password', data).then(res => res.data)
}

export function updateApiKey(data: ApiKeyForm): Promise<{ message: string; has_api_key: boolean }> {
  return api.put('/auth/me/api-key', data).then(res => res.data)
}

export function getApiKeyStatus(): Promise<{ has_api_key: boolean }> {
  return api.get('/auth/me/api-key').then(res => res.data)
}
