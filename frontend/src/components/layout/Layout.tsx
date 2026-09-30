import { Outlet } from 'react-router-dom'
import { useLiveUpdates } from '../../hooks/useLiveUpdates'
import { CompanyChips } from './CompanyChips'
import { CompanySidebar } from './CompanySidebar'
import { TopBar } from './TopBar'

export function Layout() {
  const { isConnected } = useLiveUpdates()

  return (
    <div className="min-h-screen flex flex-col bg-neutral-50 dark:bg-neutral-950 text-neutral-900 dark:text-neutral-100">
      <TopBar isConnected={isConnected} />
      <CompanyChips />
      <div className="flex-1 flex flex-col md:flex-row">
        <CompanySidebar />
        <main className="flex-1 min-w-0 p-4 md:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
