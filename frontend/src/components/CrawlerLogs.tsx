"use client"

import { useEffect, useRef } from 'react'
import { Terminal, Activity } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { ScrollArea } from '@/components/ui/scroll-area'

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
    <Card className="mb-6">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Terminal className="h-5 w-5 text-primary" />
          Crawl Logs
          <span className="ml-auto flex items-center gap-1 text-sm font-normal text-muted-foreground">
            <Activity className="h-4 w-4 animate-pulse text-primary" />
            {logs.length} events
          </span>
        </CardTitle>
        <CardDescription>
          Real-time crawling progress and status updates
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-[300px] w-full rounded-md border bg-muted/20 p-4">
          <div className="space-y-1">
            {logs.map((log, idx) => (
              <div
                key={idx}
                className="font-mono text-xs text-muted-foreground hover:text-foreground transition-colors"
              >
                <span className="text-primary/60 mr-2">
                  [{String(idx + 1).padStart(3, '0')}]
                </span>
                {log}
              </div>
            ))}
            <div ref={logsEndRef} />
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  )
}
