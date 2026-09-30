import { useMemo } from 'react'
import type { Company, Price } from '../../types'

interface CompanyHeaderProps {
  company: Company
  prices?: Price[]
}

export function CompanyHeader({ company, prices }: CompanyHeaderProps) {
  const priceStats = useMemo(() => {
    if (!prices || prices.length === 0) {
      return { lastClose: null, change: null, pctChange: null }
    }

    const validClosePrices = prices.filter(
      (p) => p.close !== null && p.close !== undefined && !Number.isNaN(parseFloat(p.close)),
    )

    if (validClosePrices.length === 0) {
      return { lastClose: null, change: null, pctChange: null }
    }

    const latest = validClosePrices[validClosePrices.length - 1]
    const lastClose = parseFloat(latest.close!)

    if (validClosePrices.length === 1) {
      return { lastClose, change: null, pctChange: null }
    }

    const previous = validClosePrices[validClosePrices.length - 2]
    const prevClose = parseFloat(previous.close!)
    const change = lastClose - prevClose
    const pctChange = (change / prevClose) * 100

    return { lastClose, change, pctChange }
  }, [prices])

  const isPositive = priceStats.change !== null && priceStats.change > 0
  const isNegative = priceStats.change !== null && priceStats.change < 0

  return (
    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-neutral-200 dark:border-neutral-800">
      <div>
        <div className="flex items-center gap-2.5">
          <h1 className="text-2xl font-bold tracking-tight text-neutral-900 dark:text-neutral-50">
            {company.symbol}
          </h1>
          {company.sector && (
            <span className="text-xs px-2 py-0.5 rounded-full bg-neutral-100 dark:bg-neutral-800 text-neutral-600 dark:text-neutral-300 border border-neutral-200 dark:border-neutral-700">
              {company.sector}
            </span>
          )}
        </div>
        <div className="text-xs text-neutral-500 dark:text-neutral-400 mt-0.5">
          {company.name}
        </div>
      </div>

      <div className="flex flex-col sm:items-end">
        <div className="text-2xl font-bold tracking-tight text-neutral-900 dark:text-neutral-50">
          {priceStats.lastClose !== null ? `NPR ${priceStats.lastClose.toFixed(2)}` : '—'}
        </div>
        {priceStats.pctChange !== null && priceStats.change !== null ? (
          <div
            className={`text-xs font-semibold flex items-center gap-1 ${
              isPositive
                ? 'text-emerald-600 dark:text-emerald-400'
                : isNegative
                  ? 'text-rose-600 dark:text-rose-400'
                  : 'text-neutral-500'
            }`}
          >
            <span>{isPositive ? '+' : ''}{priceStats.change.toFixed(2)}</span>
            <span>({isPositive ? '+' : ''}{priceStats.pctChange.toFixed(2)}%)</span>
          </div>
        ) : (
          <div className="text-xs text-neutral-400">—</div>
        )}
      </div>
    </div>
  )
}
