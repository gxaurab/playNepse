import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { ProtectedRoute } from './components/auth/ProtectedRoute'
import { Layout } from './components/layout/Layout'
import { AuthProvider } from './context/AuthProvider'
import { AdminPage } from './pages/AdminPage'
import { CompanyPage } from './pages/CompanyPage'
import { ComparePage } from './pages/ComparePage'
import { FirstCompanyRedirect } from './pages/FirstCompanyRedirect'
import { LoginPage } from './pages/LoginPage'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 60 * 1000,
    },
  },
})

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<LoginPage />} />

            <Route element={<ProtectedRoute />}>
              <Route element={<Layout />}>
                <Route index element={<FirstCompanyRedirect />} />
                <Route path="companies/:id" element={<CompanyPage />} />
                <Route path="compare" element={<ComparePage />} />
                <Route element={<ProtectedRoute requiredRole="admin" />}>
                  <Route path="admin" element={<AdminPage />} />
                </Route>
              </Route>
            </Route>

            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </QueryClientProvider>
  )
}
