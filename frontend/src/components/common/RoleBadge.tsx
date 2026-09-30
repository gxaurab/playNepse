import type { UserRole } from '../../types'

interface RoleBadgeProps {
  role: UserRole
}

const roleStyles: Record<UserRole, string> = {
  admin: 'bg-purple-100 text-purple-800 dark:bg-purple-950/60 dark:text-purple-300 border-purple-200 dark:border-purple-800/60',
  analyst: 'bg-blue-100 text-blue-800 dark:bg-blue-950/60 dark:text-blue-300 border-blue-200 dark:border-blue-800/60',
  viewer: 'bg-neutral-100 text-neutral-800 dark:bg-neutral-800 dark:text-neutral-300 border-neutral-200 dark:border-neutral-700',
}

export function RoleBadge({ role }: RoleBadgeProps) {
  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border uppercase tracking-wider ${
        roleStyles[role] || roleStyles.viewer
      }`}
    >
      {role}
    </span>
  )
}
