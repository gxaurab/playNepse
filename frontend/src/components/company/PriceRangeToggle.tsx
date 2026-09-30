import type { PriceRange } from '../../types'

interface PriceRangeToggleProps {
  range: PriceRange
  onChange: (range: PriceRange) => void
}

const RANGES: PriceRange[] = ['7d', '30d', '90d']

export function PriceRangeToggle({ range, onChange }: PriceRangeToggleProps) {
  return (
    <div className="inline-flex rounded-lg border border-neutral-200 dark:border-neutral-800 bg-neutral-100 dark:bg-neutral-800/80 p-0.5">
      {RANGES.map((r) => {
        const isActive = r === range
        return (
          <button
            key={r}
            type="button"
            onClick={() => onChange(r)}
            className={`px-3 py-1 text-xs font-semibold rounded-md transition-all ${
              isActive
                ? 'bg-white dark:bg-neutral-900 text-neutral-900 dark:text-neutral-50 shadow-xs'
                : 'text-neutral-600 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-neutral-200'
            }`}
          >
            {r}
          </button>
        )
      })}
    </div>
  )
}
