"use client"

import { useEffect, useRef } from 'react'

interface CrawlerLogsProps {
  logs: string[]
}

export default function CrawlerLogs({ logs }: CrawlerLogsProps) {
  const logsEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [logs])

  if (logs.length === 0) return null

  return (
    <div className="logs">
      <h3>Crawl Logs</h3>
      <div className="logs-content">
        {logs.map((log, idx) => (
          <div key={idx} className="log-entry">
            {log}
          </div>
        ))}
        <div ref={logsEndRef} />
      </div>
    </div>
  )
}
