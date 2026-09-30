import { createContext, useContext } from 'react'
import type { LoginCredentials, User, UserRole } from '../types'

export interface AuthContextValue {
  user: User | null
  role: UserRole | null
  isLoading: boolean
  login: (credentials: LoginCredentials) => Promise<User>
  logout: () => Promise<void>
}

export const AuthContext = createContext<AuthContextValue | undefined>(undefined)

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
