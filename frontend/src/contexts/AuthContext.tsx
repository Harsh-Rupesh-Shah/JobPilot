/**
 * contexts/AuthContext.tsx
 * JWT authentication context. Wraps the entire app.
 * Exposes: user, isAuthenticated, isLoading, login(), register(), logout()
 *
 * Access token is stored in-memory (never localStorage) to avoid XSS.
 * Refresh token is stored in an HttpOnly cookie managed by the backend.
 */

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from 'react'
import {
  authApi,
  setAccessToken,
  type UserResponse,
} from '../api/client'

// ── Types ──────────────────────────────────────────────────────────────────

interface AuthContextValue {
  user: UserResponse | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (fullName: string, email: string, password: string) => Promise<void>
  logout: () => Promise<void>
}

// ── Context ────────────────────────────────────────────────────────────────

const AuthContext = createContext<AuthContextValue | null>(null)

// ── Provider ───────────────────────────────────────────────────────────────

interface AuthProviderProps {
  children: ReactNode
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<UserResponse | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  // Refresh interval ref for cleanup
  const refreshTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  // ── Token refresh scheduling ────────────────────────────────────────────

  const scheduleRefresh = useCallback(() => {
    if (refreshTimerRef.current) clearTimeout(refreshTimerRef.current)
    // Refresh 5 min before the 30-min expiry → every 25 min
    refreshTimerRef.current = setTimeout(async () => {
      try {
        const token = await authApi.refresh()
        setAccessToken(token.access_token)
        setUser(token.user)
        scheduleRefresh()
      } catch {
        setUser(null)
        setAccessToken(null)
      }
    }, 25 * 60 * 1000)
  }, [])

  // ── On mount: attempt silent refresh from HttpOnly cookie ──────────────

  useEffect(() => {
    const tryRestore = async () => {
      try {
        const token = await authApi.refresh()
        setAccessToken(token.access_token)
        setUser(token.user)
        scheduleRefresh()
      } catch {
        // No valid session — user must log in
      } finally {
        setIsLoading(false)
      }
    }
    void tryRestore()

    return () => {
      if (refreshTimerRef.current) clearTimeout(refreshTimerRef.current)
    }
  }, [scheduleRefresh])

  // ── Auth actions ────────────────────────────────────────────────────────

  const login = useCallback(
    async (email: string, password: string): Promise<void> => {
      const token = await authApi.login({ email, password })
      setAccessToken(token.access_token)
      setUser(token.user)
      scheduleRefresh()
    },
    [scheduleRefresh],
  )

  const register = useCallback(
    async (fullName: string, email: string, password: string): Promise<void> => {
      const token = await authApi.register({
        full_name: fullName,
        email,
        password,
      })
      setAccessToken(token.access_token)
      setUser(token.user)
      scheduleRefresh()
    },
    [scheduleRefresh],
  )

  const logout = useCallback(async (): Promise<void> => {
    try {
      await authApi.logout()
    } finally {
      setAccessToken(null)
      setUser(null)
      if (refreshTimerRef.current) clearTimeout(refreshTimerRef.current)
    }
  }, [])

  // ── Context value (memoised) ────────────────────────────────────────────

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      isAuthenticated: user !== null,
      isLoading,
      login,
      register,
      logout,
    }),
    [user, isLoading, login, register, logout],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

// ── Hook ────────────────────────────────────────────────────────────────────

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>')
  return ctx
}
