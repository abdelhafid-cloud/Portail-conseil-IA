import type { AuthTokens } from '@/lib/api'

const SESSION_KEY = 'ai_enterprise_session'

export type AuthSession = AuthTokens

export function saveSession(session: AuthSession): void {
  if (typeof window === 'undefined') return
  window.localStorage.setItem(SESSION_KEY, JSON.stringify(session))
}

export function getSession(): AuthSession | null {
  if (typeof window === 'undefined') return null
  const raw = window.localStorage.getItem(SESSION_KEY)
  if (!raw) return null
  try {
    return JSON.parse(raw) as AuthSession
  } catch {
    return null
  }
}

export function clearSession(): void {
  if (typeof window === 'undefined') return
  window.localStorage.removeItem(SESSION_KEY)
}

export function getAccessToken(): string | null {
  return getSession()?.access_token ?? null
}
