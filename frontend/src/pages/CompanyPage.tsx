import { useState } from 'react'
import { useParams } from 'react-router-dom'
import { LoadingSpinner } from '../components/common/LoadingSpinner'
import { CompanyHeader } from '../components/company/CompanyHeader'
import { CompanyPriceChart } from '../components/company/CompanyPriceChart'
import { PriceRangeToggle } from '../components/company/PriceRangeToggle'
import { useCompanies } from '../hooks/useCompanies'
import { useCompanyPrices } from '../hooks/useCompanyPrices'
import type { PriceRange } from '../types'

export function CompanyPage() {
  const { id } = useParams<{ id: string }>()
  const companyId = Number(id)
  const [range, setRange] = useState<PriceRange>('30d')

  const { data: companies, isLoading: isCompaniesLoading } = useCompanies()
  const { data: prices, isLoading: isPricesLoading, isError: isPricesError } = useCompanyPrices(
    companyId,
    range,
  )

  if (isCompaniesLoading) {
    return <LoadingSpinner className="h-8 w-8 mt-12" />
  }

  const company = companies?.find((c) => c.id === companyId)

  if (!company) {
    return (
      <div className="p-8 text-center text-sm text-neutral-500">
        Company not found. Please select another company from the list.
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <CompanyHeader company={company} prices={prices} />

      <section className="bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 rounded-xl p-4 md:p-5 shadow-xs">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-sm font-semibold tracking-tight text-neutral-800 dark:text-neutral-200">
            Price & Volume History
          </h2>
          <PriceRangeToggle range={range} onChange={setRange} />
        </div>

        {isPricesLoading && <LoadingSpinner className="h-6 w-6 my-16" />}

        {isPricesError && (
          <div className="p-8 text-center text-xs text-rose-500">
            Failed to load price data.
          </div>
        )}

        {!isPricesLoading && !isPricesError && prices && (
          <CompanyPriceChart prices={prices} />
        )}
      </section>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <section className="bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 rounded-xl p-5 shadow-xs">
          <h2 className="text-base font-semibold tracking-tight text-neutral-900 dark:text-neutral-100 mb-2">
            News
          </h2>
          <div className="text-xs text-neutral-500 dark:text-neutral-400">
            No news articles available.
          </div>
        </section>

        <section className="bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 rounded-xl p-5 shadow-xs">
          <h2 className="text-base font-semibold tracking-tight text-neutral-900 dark:text-neutral-100 mb-2">
            Behavior analysis
          </h2>
          <div className="text-xs text-neutral-500 dark:text-neutral-400">
            Behavior and floorsheet analysis will appear here.
          </div>
        </section>
      </div>
    </div>
  )
}
