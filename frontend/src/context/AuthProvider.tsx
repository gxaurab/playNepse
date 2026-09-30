import { useQuery, useQueryClient } from '@tanstack/react-query'
import type { ReactNode } from 'react'
import { apiClient } from '../api/client'
import type { LoginCredentials, User } from '../types'
import { AuthContext } from './authContext'

export function AuthProvider({ children }: { children: ReactNode }) {
  const queryClient = useQueryClient()

  const { data: user = null, isLoading } = useQuery<User | null>({
    queryKey: ['auth', 'me'],
    queryFn: async () => {
      try {
        return await apiClient<User>('/api/auth/me')
      } catch {
        return null
      }
    },
    retry: false,
    staleTime: 5 * 60 * 1000,
  })

  const login = async (credentials: LoginCredentials): Promise<User> => {
    const loggedInUser = await apiClient<User>('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    })
    queryClient.setQueryData(['auth', 'me'], loggedInUser)
    return loggedInUser
  }

  const logout = async (): Promise<void> => {
    try {
      await apiClient<{ status: string }>('/api/auth/logout', {
        method: 'POST',
      })
    } finally {
      queryClient.setQueryData(['auth', 'me'], null)
      queryClient.clear()
    }
  }

  return (
    <AuthContext.Provider
      value={{
        user: user ?? null,
        role: user?.role ?? null,
        isLoading,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}
