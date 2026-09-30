interface LiveIndicatorProps {
  isConnected: boolean
}

export function LiveIndicator({ isConnected }: LiveIndicatorProps) {
  return (
    <div
      className="inline-flex items-center gap-1.5 px-2 py-1 rounded-full text-xs font-medium border border-neutral-200 dark:border-neutral-800 bg-neutral-100/60 dark:bg-neutral-900/60"
      title={isConnected ? 'Connected to live updates' : 'Reconnecting to live updates'}
    >
      <span
        className={`inline-block h-2 w-2 rounded-full transition-colors duration-300 ${
          isConnected
            ? 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.7)] animate-pulse'
            : 'bg-neutral-400 dark:bg-neutral-600'
        }`}
      />
      <span
        className={
          isConnected
            ? 'text-emerald-700 dark:text-emerald-400 font-semibold'
            : 'text-neutral-500 dark:text-neutral-400'
        }
      >
        {isConnected ? 'Live' : 'Offline'}
      </span>
    </div>
  )
}
