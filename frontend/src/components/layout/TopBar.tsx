import { Link, NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/authContext'
import { LiveIndicator } from '../common/LiveIndicator'
import { RoleBadge } from '../common/RoleBadge'

interface TopBarProps {
  isConnected: boolean
}

export function TopBar({ isConnected }: TopBarProps) {
  const { user, role, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  return (
    <header className="h-14 border-b border-neutral-200 dark:border-neutral-800 bg-white/80 dark:bg-neutral-900/80 backdrop-blur sticky top-0 z-30 px-4 flex items-center justify-between">
      <div className="flex items-center gap-6">
        <Link to="/" className="flex items-center gap-2 font-bold text-lg tracking-tight text-neutral-900 dark:text-neutral-50 hover:opacity-90">
          <span className="w-6 h-6 rounded bg-neutral-900 dark:bg-neutral-100 text-white dark:text-neutral-900 text-xs font-black flex items-center justify-center">
            P
          </span>
          <span>playNepse</span>
        </Link>

        <nav className="hidden sm:flex items-center gap-1 text-sm">
          <NavLink
            to="/compare"
            className={({ isActive }) =>
              `px-2.5 py-1.5 rounded-md font-medium transition-colors ${
                isActive
                  ? 'bg-neutral-100 dark:bg-neutral-800 text-neutral-900 dark:text-neutral-100'
                  : 'text-neutral-600 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-neutral-200'
              }`
            }
          >
            Compare
          </NavLink>

          {role === 'admin' && (
            <NavLink
              to="/admin"
              className={({ isActive }) =>
                `px-2.5 py-1.5 rounded-md font-medium transition-colors ${
                  isActive
                    ? 'bg-neutral-100 dark:bg-neutral-800 text-neutral-900 dark:text-neutral-100'
                    : 'text-neutral-600 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-neutral-200'
                }`
              }
            >
              Admin
            </NavLink>
          )}
        </nav>
      </div>

      <div className="flex items-center gap-3">
        <LiveIndicator isConnected={isConnected} />

        {user && (
          <div className="hidden sm:flex items-center gap-2 text-xs text-neutral-600 dark:text-neutral-400">
            <span className="max-w-[140px] truncate" title={user.email}>
              {user.email}
            </span>
            {role && <RoleBadge role={role} />}
          </div>
        )}

        <button
          type="button"
          onClick={handleLogout}
          className="text-xs font-medium px-2.5 py-1.5 rounded border border-neutral-300 dark:border-neutral-700 hover:bg-neutral-100 dark:hover:bg-neutral-800 text-neutral-700 dark:text-neutral-300 transition-colors"
        >
          Logout
        </button>
      </div>
    </header>
  )
}
