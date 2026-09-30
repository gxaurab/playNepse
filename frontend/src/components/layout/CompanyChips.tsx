import { NavLink, useParams } from 'react-router-dom'
import { useCompanies } from '../../hooks/useCompanies'

export function CompanyChips() {
  const { data: companies, isLoading } = useCompanies()
  const { id } = useParams<{ id: string }>()

  if (isLoading || !companies || companies.length === 0) {
    return null
  }

  return (
    <div className="md:hidden border-b border-neutral-200 dark:border-neutral-800 bg-white dark:bg-neutral-900 px-3 py-2 overflow-x-auto flex gap-1.5 scrollbar-thin">
      {companies.map((company) => {
        const isActive = id === String(company.id)
        return (
          <NavLink
            key={company.id}
            to={`/companies/${company.id}`}
            className={`shrink-0 px-2.5 py-1 rounded-full text-xs font-medium border transition-colors ${
              isActive
                ? 'bg-neutral-900 text-white dark:bg-neutral-100 dark:text-neutral-900 border-transparent shadow-xs'
                : 'bg-neutral-100 dark:bg-neutral-800 text-neutral-700 dark:text-neutral-300 border-neutral-200 dark:border-neutral-700 hover:bg-neutral-200 dark:hover:bg-neutral-700'
            }`}
          >
            {company.symbol}
          </NavLink>
        )
      })}
    </div>
  )
}
