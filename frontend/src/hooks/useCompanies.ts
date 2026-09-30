import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../api/client'
import type { Company } from '../types'

export function useCompanies() {
  return useQuery<Company[], Error>({
    queryKey: ['companies'],
    queryFn: () => apiClient<Company[]>('/api/companies'),
  })
}
