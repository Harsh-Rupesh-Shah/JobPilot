/**
 * api/client.ts
 * Typed API client for all backend endpoints.
 * All application routes require Authorization: Bearer <access_token>.
 */

import axios, { type AxiosInstance } from 'axios'

// ── Types ─────────────────────────────────────────────────────────────────

export interface UserResponse {
  user_id: string
  email: string
  full_name: string
  created_at: string
}

export interface Token {
  access_token: string
  token_type: 'bearer'
  user: UserResponse
}

export interface RunStatusResponse {
  run_id: string
  status: 'running' | 'pending_approval' | 'complete' | 'failed'
  current_agent?: string
  interrupt_payload?: {
    message: string
    outputs: {
      tailored_resume: string
      cover_letter: string
      interview_qa: string
      outreach_draft: string
      research_brief: string
    }
  }
}

export interface ApplicationRecord {
  _id: string
  user_id: string
  job_url?: string
  company: string
  role: string
  status: 'running' | 'pending_approval' | 'complete' | 'failed'
  created_at: string
  updated_at: string
}

export interface VaultRecord {
  _id: string
  company: string
  role: string
  interview_qa: string
  created_at: string
}

export interface ApplicationOutput {
  output_type: 'resume' | 'cover_letter' | 'research' | 'interview_qa' | 'outreach'
  content: string
  file_path?: string
  approved: boolean
  created_at: string
}

export interface RunRequest {
  job_url?: string
  job_description?: string
  resume_id: string
}

export interface ApproveRequest {
  tailored_resume: string
  cover_letter: string
  outreach_draft: string
}

export interface ParsedResume {
  resume_id: string
  text: string
  filename: string
}

// ── Axios instance ────────────────────────────────────────────────────────

/** Base URL — proxied to http://localhost:8000 via vite.config.ts */
const BASE_URL = '/api'

const apiClient: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  withCredentials: true, // Required for HttpOnly refresh cookie
})

// Attach access token from memory on every request
let _accessToken: string | null = null

export function setAccessToken(token: string | null): void {
  _accessToken = token
}

export function getAccessToken(): string | null {
  return _accessToken
}

apiClient.interceptors.request.use((config) => {
  if (_accessToken) {
    config.headers['Authorization'] = `Bearer ${_accessToken}`
  }
  return config
})

// ── Auth endpoints ────────────────────────────────────────────────────────

export const authApi = {
  register: (data: { full_name: string; email: string; password: string }): Promise<Token> =>
    apiClient.post<Token>('/auth/register', data).then((r) => r.data),

  login: (data: { email: string; password: string }): Promise<Token> =>
    apiClient.post<Token>('/auth/login', data).then((r) => r.data),

  logout: (): Promise<void> =>
    apiClient.post('/auth/logout').then(() => undefined),

  refresh: (): Promise<Token> =>
    apiClient.post<Token>('/auth/refresh').then((r) => r.data),

  me: (): Promise<UserResponse> =>
    apiClient.get<UserResponse>('/auth/me').then((r) => r.data),
}

// ── Resume endpoints ──────────────────────────────────────────────────────

export const resumeApi = {
  upload: async (file: File): Promise<ParsedResume> => {
    const form = new FormData()
    form.append('file', file)
    return apiClient
      .post<ParsedResume>('/upload/resume', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      .then((r) => r.data)
  },
  getLatest: async (): Promise<ParsedResume | null> => {
    try {
      const response = await apiClient.get<ParsedResume>('/upload/resume')
      return response.data
    } catch (err: any) {
      if (err.response?.status === 404) return null
      throw err
    }
  },
  update: async (text: string): Promise<ParsedResume> => {
    return apiClient.put<ParsedResume>('/upload/resume', { text }).then(r => r.data)
  }
}

// ── Run / Application endpoints ───────────────────────────────────────────

export const runApi = {
  start: (data: RunRequest): Promise<{ run_id: string }> =>
    apiClient.post<{ run_id: string }>('/run', data).then((r) => r.data),

  status: (runId: string): Promise<RunStatusResponse> =>
    apiClient.get<RunStatusResponse>(`/status/${runId}`).then((r) => r.data),

  approve: (runId: string, data: ApproveRequest): Promise<void> =>
    apiClient.post(`/approve/${runId}`, data).then(() => undefined),
}

export const applicationsApi = {
  list: (): Promise<ApplicationRecord[]> =>
    apiClient.get<ApplicationRecord[]>('/applications').then((r) => r.data),

  get: (id: string): Promise<{ application: ApplicationRecord; outputs: ApplicationOutput[] }> =>
    apiClient
      .get<{ application: ApplicationRecord; outputs: ApplicationOutput[] }>(`/applications/${id}`)
      .then((r) => r.data),

  getVault: (): Promise<VaultRecord[]> =>
    apiClient.get<VaultRecord[]>('/applications/vault').then((r) => r.data),

  exportUrl: (id: string, format: 'pdf' | 'docx'): string =>
    `${BASE_URL}/applications/export/${id}/${format}${_accessToken ? `?token=${encodeURIComponent(_accessToken)}` : ''}`,
    
  delete: (id: string): Promise<void> =>
    apiClient.delete(`/applications/${id}`).then((r) => r.data),
}

// ── SSE helper ────────────────────────────────────────────────────────────

/**
 * Opens an SSE connection to /stream/{runId}.
 * Returns an EventSource. Caller is responsible for closing it.
 */
export function openSSEStream(runId: string): EventSource {
  const url = `${BASE_URL}/stream/${runId}${_accessToken ? `?token=${encodeURIComponent(_accessToken)}` : ''}`
  return new EventSource(url, { withCredentials: true })
}

export default apiClient
