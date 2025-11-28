"use client"

import { useCrawler } from '@/hooks/useCrawler'
import PageHeader from '@/components/PageHeader'
import CrawlerControls from '@/components/CrawlerControls'
import CrawlerLogs from '@/components/CrawlerLogs'
import CrawlerResult from '@/components/CrawlerResult'

export default function Home() {
  const { logs, result, hostedUrl, isScanning, startScan, stopScan } = useCrawler()

  const handleStartScan = (url: string, maxPages: number, descLength: number, enableAutoUpdate: boolean, recrawlInterval: number, llmEnhance: boolean, useBrightdata: boolean) => {
    startScan({ url, maxPages, descLength, enableAutoUpdate, recrawlIntervalMinutes: recrawlInterval, llmEnhance, useBrightdata })
  }

  return (
    <main className="min-h-screen bg-gradient-to-b from-background to-background/95">
      <div className="container mx-auto px-4 py-8 max-w-5xl">
        <PageHeader />
        <div className="space-y-6">
          <CrawlerControls
            onStartScan={handleStartScan}
            onStopScan={stopScan}
            isScanning={isScanning}
          />
          <CrawlerLogs logs={logs} />
          <CrawlerResult result={result} hostedUrl={hostedUrl} />
        </div>
      </div>
    </main>
  )
}
