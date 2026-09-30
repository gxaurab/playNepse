export type UserRole = 'admin' | 'analyst' | 'viewer'

export interface User {
  id: number
  email: string
  role: UserRole
  is_active: boolean
  created_at: string
}

export interface LoginCredentials {
  email: string
  password: string
}

export interface Company {
  id: number
  symbol: string
  name: string
  sector: string | null
  aliases: string[]
  is_active: boolean
  created_at: string
}

export interface Price {
  company_id: number
  date: string
  open: string | null
  high: string | null
  low: string | null
  close: string | null
  volume: string | null
  turnover: string | null
  trades: string | null
  vwap: string | null
}

export type PriceRange = '7d' | '30d' | '90d'

export interface ApiErrorPayload {
  error: {
    code: string
    message: string
    details?: unknown
  }
}
