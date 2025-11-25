"use client"

import { useState, useCallback, useRef } from 'react'

interface CrawlPayload {
  url: string
  maxPages: number
  descLength: number
}

export function useCrawler() {
  const [logs, setLogs] = useState<string[]>([])
  const [result, setResult] = useState<string>("")
  const [hostedUrl, setHostedUrl] = useState<string>("")
  const [isScanning, setIsScanning] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)

  const startScan = useCallback((payload: CrawlPayload) => {
    setLogs(["Connecting to crawler..."])
    setResult("")
    setHostedUrl("")
    setIsScanning(true)

    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/ws/crawl"
    const ws = new WebSocket(wsUrl)
    wsRef.current = ws

    ws.onopen = () => {
      setLogs((prev) => [...prev, `Starting crawl of ${payload.url}...`])
      ws.send(JSON.stringify(payload))
    }

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)

      if (data.type === "log") {
        setLogs((prev) => [...prev, data.content])
      } else if (data.type === "result") {
        setResult(data.content)
      } else if (data.type === "url") {
        setHostedUrl(data.content)
      } else if (data.type === "error") {
        setLogs((prev) => [...prev, `ERROR: ${data.content}`])
      }
    }

    ws.onerror = () => {
      setLogs((prev) => [...prev, "Connection error - is backend running?"])
      setIsScanning(false)
    }

    ws.onclose = () => {
      setIsScanning(false)
    }
  }, [])

  const stopScan = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }
    setIsScanning(false)
  }, [])

  return {
    logs,
    result,
    hostedUrl,
    isScanning,
    startScan,
    stopScan,
  }
}
