import { useQueryClient } from '@tanstack/react-query'
import { useEffect, useRef, useState } from 'react'

export function useLiveUpdates(): { isConnected: boolean } {
  const queryClient = useQueryClient()
  const [isConnected, setIsConnected] = useState(false)
  const reconnectTimeoutRef = useRef<number | null>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const backoffRef = useRef<number>(1000)

  useEffect(() => {
    let isDisposed = false

    const connect = () => {
      if (isDisposed) return

      const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
      const url = `${protocol}://${window.location.host}/ws/updates`
      const ws = new WebSocket(url)
      wsRef.current = ws

      ws.onopen = () => {
        if (isDisposed) {
          ws.close()
          return
        }
        setIsConnected(true)
        backoffRef.current = 1000
      }

      ws.onmessage = (event: MessageEvent) => {
        try {
          const payload = JSON.parse(event.data as string)
          if (payload?.type === 'prices') {
            void queryClient.invalidateQueries({ queryKey: ['prices'] })
          } else if (payload?.type === 'crawl_run') {
            void queryClient.invalidateQueries({ queryKey: ['crawl-runs'] })
          } else if (payload?.type === 'news') {
            void queryClient.invalidateQueries({ queryKey: ['news'] })
          }
        } catch (err) {
          void err
        }
      }

      ws.onclose = () => {
        setIsConnected(false)
        wsRef.current = null
        if (!isDisposed) {
          const nextDelay = Math.min(backoffRef.current * 1.5, 15000)
          backoffRef.current = nextDelay
          reconnectTimeoutRef.current = window.setTimeout(connect, nextDelay)
        }
      }

      ws.onerror = () => {
        ws.close()
      }
    }

    connect()

    return () => {
      isDisposed = true
      if (reconnectTimeoutRef.current !== null) {
        window.clearTimeout(reconnectTimeoutRef.current)
      }
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, [queryClient])

  return { isConnected }
}
