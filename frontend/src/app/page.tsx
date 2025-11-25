"use client"

import { useCrawler } from '@/hooks/useCrawler'
import PageHeader from '@/components/PageHeader'
import CrawlerControls from '@/components/CrawlerControls'
import CrawlerLogs from '@/components/CrawlerLogs'
import CrawlerResult from '@/components/CrawlerResult'

export default function Home() {
  const { logs, result, hostedUrl, isScanning, startScan, stopScan } = useCrawler()

  const handleStartScan = (url: string, maxPages: number, descLength: number) => {
    startScan({ url, maxPages, descLength })
  }

  return (
    <div className="container">
      <PageHeader />
      <CrawlerControls
        onStartScan={handleStartScan}
        onStopScan={stopScan}
        isScanning={isScanning}
      />
      <CrawlerLogs logs={logs} />
      <CrawlerResult result={result} hostedUrl={hostedUrl} />
    </div>
  )
}
