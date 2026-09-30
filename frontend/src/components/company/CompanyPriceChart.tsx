import { useMemo } from 'react'
import {
  Bar,
  CartesianGrid,
  ComposedChart,
  Legend,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import type { Price } from '../../types'

interface CompanyPriceChartProps {
  prices: Price[]
}

interface TooltipPayloadItem {
  name: string
  value: number | string | null
  color?: string
  dataKey?: string | number
}

interface CustomTooltipProps {
  active?: boolean
  payload?: TooltipPayloadItem[]
  label?: string
}

function CustomChartTooltip({ active, payload, label }: CustomTooltipProps) {
  if (!active || !payload || payload.length === 0) return null

  return (
    <div className="bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 p-2.5 rounded-lg shadow-lg text-xs space-y-1 z-50">
      <div className="font-semibold text-neutral-800 dark:text-neutral-200 border-b border-neutral-100 dark:border-neutral-800 pb-1">
        {label}
      </div>
      {payload.map((item) => (
        <div key={String(item.dataKey || item.name)} className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-1.5">
            <span
              className="w-2 h-2 rounded-full"
              style={{ backgroundColor: item.color }}
            />
            <span className="text-neutral-500 dark:text-neutral-400 capitalize">
              {item.name}
            </span>
          </div>
          <span className="font-medium text-neutral-900 dark:text-neutral-100">
            {typeof item.value === 'number'
              ? item.name === 'Volume'
                ? item.value.toLocaleString()
                : item.value.toFixed(2)
              : (item.value ?? '—')}
          </span>
        </div>
      ))}
    </div>
  )
}

export function CompanyPriceChart({ prices }: CompanyPriceChartProps) {
  const chartData = useMemo(() => {
    return prices.map((p) => ({
      date: p.date,
      close: p.close !== null && p.close !== undefined ? parseFloat(p.close) : null,
      vwap: p.vwap !== null && p.vwap !== undefined ? parseFloat(p.vwap) : null,
      volume: p.volume !== null && p.volume !== undefined ? parseFloat(p.volume) : 0,
    }))
  }, [prices])

  if (chartData.length === 0) {
    return (
      <div className="h-80 flex items-center justify-center text-xs text-neutral-400 border border-dashed border-neutral-200 dark:border-neutral-800 rounded-lg">
        No price data recorded for this time range.
      </div>
    )
  }

  return (
    <div className="h-96 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart data={chartData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" vertical={false} opacity={0.15} />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 11 }}
            tickLine={false}
          />
          <YAxis
            yAxisId="price"
            domain={['auto', 'auto']}
            tick={{ fontSize: 11 }}
            tickLine={false}
            axisLine={false}
            tickFormatter={(val: number) => val.toFixed(0)}
          />
          <YAxis
            yAxisId="volume"
            orientation="right"
            domain={[0, (dataMax: number) => (dataMax ? dataMax * 4 : 1000)]}
            tick={{ fontSize: 10 }}
            tickLine={false}
            axisLine={false}
            tickFormatter={(v: number) =>
              v >= 1000000 ? `${(v / 1000000).toFixed(1)}M` : v >= 1000 ? `${(v / 1000).toFixed(0)}k` : `${v}`
            }
          />
          <Tooltip content={<CustomChartTooltip />} />
          <Legend wrapperStyle={{ paddingTop: '10px', fontSize: '12px' }} />
          <Bar
            yAxisId="volume"
            dataKey="volume"
            name="Volume"
            fill="#94a3b8"
            opacity={0.35}
            radius={[2, 2, 0, 0]}
          />
          <Line
            yAxisId="price"
            type="monotone"
            dataKey="vwap"
            name="VWAP"
            stroke="#f59e0b"
            strokeWidth={1.75}
            strokeDasharray="4 4"
            dot={false}
          />
          <Line
            yAxisId="price"
            type="monotone"
            dataKey="close"
            name="Close"
            stroke="#3b82f6"
            strokeWidth={2}
            dot={false}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  )
}
