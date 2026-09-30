export function LoadingSpinner({ className = 'h-6 w-6' }: { className?: string }) {
  return (
    <div className="flex items-center justify-center p-4">
      <div
        className={`animate-spin rounded-full border-2 border-neutral-300 border-t-neutral-800 dark:border-neutral-700 dark:border-t-neutral-200 ${className}`}
      />
    </div>
  )
}
