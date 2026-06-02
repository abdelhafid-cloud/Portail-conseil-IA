const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

export type ConsultantResponse = {
  reply: string
  suggested_services: string[]
  follow_up_questions: string[]
}

export type HealthResponse = {
  status: string
  service: string
}

export type AuthTokens = {
  access_token: string
  refresh_token: string
  user: {
    id: number
    email: string
    full_name: string
    company_name?: string
    role: string
  }
}

export type Appointment = {
  id: number
  lead_id: number
  scheduled_at: string
  duration_minutes: number
  status: string
  meeting_url: string | null
  calendar_event_id: string | null
}

export type Lead = {
  id: number
  full_name: string
  email: string
  phone?: string
  company_name: string
  lead_score: number
  priority_level: string
}

function authHeaders(token?: string): Record<string, string> {
  const headers: Record<string, string> = { 'Content-Type': 'application/json' }
  if (token) headers.Authorization = `Bearer ${token}`
  return headers
}

async function parseJson<T>(response: Response): Promise<T> {
  const data = await response.json()
  if (!response.ok) {
    const message = typeof data?.error === 'string' ? data.error : 'Erreur API'
    throw new Error(message)
  }
  return data as T
}

export async function checkHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE}/api/health`, { cache: 'no-store' })
  return parseJson<HealthResponse>(response)
}

export async function consultantRespond(message: string, context?: Record<string, unknown>): Promise<ConsultantResponse> {
  const response = await fetch(`${API_BASE}/api/consultant/respond`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, context }),
  })
  return parseJson<ConsultantResponse>(response)
}

export async function registerUser(payload: {
  email: string
  password: string
  full_name: string
  company_name?: string
}): Promise<AuthTokens> {
  const response = await fetch(`${API_BASE}/api/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  return parseJson<AuthTokens>(response)
}

export async function loginUser(email: string, password: string): Promise<AuthTokens> {
  const response = await fetch(`${API_BASE}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  })
  return parseJson<AuthTokens>(response)
}

export async function createLead(
  payload: {
    full_name: string
    email: string
    phone?: string
    company_name?: string
    business_goals?: string
    challenges?: string
    source?: string
  },
  accessToken?: string,
): Promise<{ lead: Lead }> {
  const response = await fetch(`${API_BASE}/api/leads`, {
    method: 'POST',
    headers: authHeaders(accessToken),
    body: JSON.stringify(payload),
  })
  return parseJson<{ lead: Lead }>(response)
}

export async function createAppointment(
  payload: {
    lead_id: number
    scheduled_at: string
    duration_minutes?: number
    notes?: string
  },
  accessToken?: string,
): Promise<{
  appointment: Appointment
  whatsapp?: { sent: boolean; reason?: string; detail?: string; action?: string }
  google?: {
    calendar?: { synced?: boolean; reason?: string; detail?: string }
    sheets?: { synced?: boolean; reason?: string; detail?: string }
  }
}> {
  const response = await fetch(`${API_BASE}/api/appointments`, {
    method: 'POST',
    headers: authHeaders(accessToken),
    body: JSON.stringify(payload),
  })
  return parseJson<{
    appointment: Appointment
    whatsapp?: { sent: boolean; reason?: string; detail?: string; action?: string }
    google?: {
      calendar?: { synced?: boolean; reason?: string; detail?: string }
      sheets?: { synced?: boolean; reason?: string; detail?: string }
    }
  }>(response)
}

export async function listAppointments(accessToken?: string): Promise<{ items: Appointment[] }> {
  const response = await fetch(`${API_BASE}/api/appointments`, {
    headers: authHeaders(accessToken),
    cache: 'no-store',
  })
  return parseJson<{ items: Appointment[] }>(response)
}

export function getApiBaseUrl(): string {
  return API_BASE
}
