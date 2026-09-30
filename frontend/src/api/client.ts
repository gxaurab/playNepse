import type { ApiErrorPayload } from '../types'

export class ApiError extends Error {
  readonly status: number
  readonly code: string
  readonly details?: unknown

  constructor(status: number, code: string, message: string, details?: unknown) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.code = code
    this.details = details
  }
}

export async function apiClient<T>(
  endpoint: string,
  options: RequestInit = {},
): Promise<T> {
  const headers = new Headers(options.headers)

  if (!headers.has('Content-Type') && options.body && !(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json')
  }

  const response = await fetch(endpoint, {
    ...options,
    credentials: 'include',
    headers,
  })

  if (!response.ok) {
    let code = `HTTP_${response.status}`
    let message = response.statusText || 'An unexpected error occurred'
    let details: unknown = undefined

    try {
      const errorJson = (await response.json()) as ApiErrorPayload
      if (errorJson?.error) {
        code = errorJson.error.code || code
        message = errorJson.error.message || message
        details = errorJson.error.details
      }
    } catch (err) {
      void err
    }

    if (response.status === 401 && window.location.pathname !== '/login') {
      window.location.href = '/login'
    }

    throw new ApiError(response.status, code, message, details)
  }

  if (response.status === 204) {
    return undefined as unknown as T
  }

  return response.json() as Promise<T>
}
