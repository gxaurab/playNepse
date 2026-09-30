import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '../../context/authContext'
import { LoadingSpinner } from '../common/LoadingSpinner'
import type { UserRole } from '../../types'

interface ProtectedRouteProps {
  requiredRole?: UserRole
}

export function ProtectedRoute({ requiredRole }: ProtectedRouteProps) {
  const { user, role, isLoading } = useAuth()
  const location = useLocation()

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-neutral-50 dark:bg-neutral-950">
        <LoadingSpinner className="h-8 w-8" />
      </div>
    )
  }

  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  if (requiredRole === 'admin' && role !== 'admin') {
    return <Navigate to="/" replace />
  }

  return <Outlet />
}
