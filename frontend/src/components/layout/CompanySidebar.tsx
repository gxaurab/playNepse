import { useMemo, useState } from 'react'
import { NavLink, useParams } from 'react-router-dom'
import { useCompanies } from '../../hooks/useCompanies'
import { LoadingSpinner } from '../common/LoadingSpinner'

export function CompanySidebar() {
  const { data: companies, isLoading, isError } = useCompanies()
  const { id } = useParams<{ id: string }>()
  const [search, setSearch] = useState('')

  const filteredCompanies = useMemo(() => {
    if (!companies) return []
    if (!search.trim()) return companies
    const query = search.toLowerCase()
    return companies.filter(
      (c) =>
        c.symbol.toLowerCase().includes(query) ||
        c.name.toLowerCase().includes(query) ||
        (c.sector && c.sector.toLowerCase().includes(query)),
    )
  }, [companies, search])

  return (
    <aside className="hidden md:flex w-64 flex-col border-r border-neutral-200 dark:border-neutral-800 bg-white dark:bg-neutral-900/50 shrink-0 h-[calc(100vh-3.5rem)] sticky top-14">
      <div className="p-3 border-b border-neutral-200 dark:border-neutral-800">
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Filter companies..."
          className="w-full text-xs px-2.5 py-1.5 rounded border border-neutral-300 dark:border-neutral-700 bg-neutral-50 dark:bg-neutral-800 text-neutral-900 dark:text-neutral-100 placeholder-neutral-400 focus:outline-none focus:ring-1 focus:ring-neutral-400 dark:focus:ring-neutral-500"
        />
      </div>

      <div className="flex-1 overflow-y-auto p-2 space-y-1">
        {isLoading && <LoadingSpinner className="h-5 w-5" />}

        {isError && (
          <div className="p-3 text-xs text-red-500 text-center">
            Failed to load companies
          </div>
        )}

        {!isLoading && filteredCompanies.length === 0 && (
          <div className="p-3 text-xs text-neutral-400 text-center">
            No companies found
          </div>
        )}

        {filteredCompanies.map((company) => {
          const isActive = id === String(company.id)
          return (
            <NavLink
              key={company.id}
              to={`/companies/${company.id}`}
              className={`block px-3 py-2 rounded-md text-xs transition-colors ${
                isActive
                  ? 'bg-neutral-100 dark:bg-neutral-800 text-neutral-900 dark:text-white font-medium border-l-2 border-neutral-900 dark:border-neutral-100'
                  : 'text-neutral-600 dark:text-neutral-400 hover:bg-neutral-50 dark:hover:bg-neutral-800/50 hover:text-neutral-900 dark:hover:text-neutral-200'
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="font-semibold text-neutral-900 dark:text-neutral-100">
                  {company.symbol}
                </span>
                {company.sector && (
                  <span className="text-[10px] text-neutral-400 truncate max-w-[100px]">
                    {company.sector}
                  </span>
                )}
              </div>
              <div className="truncate text-neutral-500 dark:text-neutral-400 mt-0.5 text-[11px]">
                {company.name}
              </div>
            </NavLink>
          )
        })}
      </div>
    </aside>
  )
}
