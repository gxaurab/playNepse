import { Navigate } from 'react-router-dom'
import { LoadingSpinner } from '../components/common/LoadingSpinner'
import { useCompanies } from '../hooks/useCompanies'

export function FirstCompanyRedirect() {
  const { data: companies, isLoading, isError } = useCompanies()

  if (isLoading) {
    return <LoadingSpinner className="h-8 w-8 mt-12" />
  }

  if (isError || !companies || companies.length === 0) {
    return (
      <div className="p-8 text-center text-sm text-neutral-500">
        No companies available to display.
      </div>
    )
  }

  return <Navigate to={`/companies/${companies[0].id}`} replace />
}
