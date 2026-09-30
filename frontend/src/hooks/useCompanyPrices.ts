import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../api/client'
import type { Price, PriceRange } from '../types'

export function useCompanyPrices(companyId: number, range: PriceRange) {
  return useQuery<Price[], Error>({
    queryKey: ['prices', companyId, range],
    queryFn: () => apiClient<Price[]>(`/api/companies/${companyId}/prices?range=${range}`),
    enabled: Number.isFinite(companyId) && companyId > 0,
  })
}
