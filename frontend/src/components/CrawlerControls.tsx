"use client"

import { useState } from 'react'

interface CrawlerControlsProps {
  onStartScan: (url: string, maxPages: number, descLength: number, enableAutoUpdate: boolean, recrawlInterval: number, llmEnhance: boolean, useBrightdata: boolean) => void
  onStopScan: () => void
  isScanning: boolean
}

export default function CrawlerControls({ onStartScan, onStopScan, isScanning }: CrawlerControlsProps) {
  const [url, setUrl] = useState('https://example.com')
  const [maxPages, setMaxPages] = useState(50)
  const [descLength, setDescLength] = useState(500)
  const [enableAutoUpdate, setEnableAutoUpdate] = useState(false)
  const [recrawlInterval, setRecrawlInterval] = useState(10080)
  const [llmEnhance, setLlmEnhance] = useState(false)
  const [useBrightdata, setUseBrightdata] = useState(true)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!isScanning) {
      onStartScan(url, maxPages, descLength, enableAutoUpdate, recrawlInterval, llmEnhance, useBrightdata)
    }
  }

  return (
    <form className="controls" onSubmit={handleSubmit}>
      <div className="input-group">
        <label htmlFor="url">Website URL</label>
        <input
          id="url"
          type="url"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          disabled={isScanning}
          required
        />
      </div>

      <div className="input-row">
        <div className="input-group">
          <label htmlFor="maxPages">Max Pages</label>
          <input
            id="maxPages"
            type="number"
            value={maxPages}
            onChange={(e) => setMaxPages(Number(e.target.value))}
            disabled={isScanning}
            min="1"
            max="500"
          />
        </div>

        <div className="input-group">
          <label htmlFor="descLength">Snippet Length</label>
          <input
            id="descLength"
            type="number"
            value={descLength}
            onChange={(e) => setDescLength(Number(e.target.value))}
            disabled={isScanning}
            min="100"
            max="2000"
          />
        </div>
      </div>

      <div className="input-group">
        <label>
          <input
            type="checkbox"
            checked={enableAutoUpdate}
            onChange={(e) => setEnableAutoUpdate(e.target.checked)}
            disabled={isScanning}
          />
          {' '}Enable automated updates
        </label>
      </div>

      {enableAutoUpdate && (
        <div className="input-group">
          <label htmlFor="recrawlInterval">Recrawl Interval</label>
          <select
            id="recrawlInterval"
            value={recrawlInterval}
            onChange={(e) => setRecrawlInterval(Number(e.target.value))}
            disabled={isScanning}
          >
            <option value={1440}>Daily</option>
            <option value={10080}>Weekly</option>
            <option value={43200}>Monthly</option>
          </select>
        </div>
      )}

      <div className="input-group">
        <label>
          <input
            type="checkbox"
            checked={llmEnhance}
            onChange={(e) => setLlmEnhance(e.target.checked)}
            disabled={isScanning}
          />
          {' '}Enhance with LLM (improves organization and descriptions)
        </label>
      </div>

      <div className="input-group">
        <label>
          <input
            type="checkbox"
            checked={useBrightdata}
            onChange={(e) => setUseBrightdata(e.target.checked)}
            disabled={isScanning}
          />
          {' '}Use browser scraping for JavaScript-heavy sites
        </label>
      </div>

      <div className="button-group">
        {!isScanning ? (
          <button type="submit" className="btn btn-primary">
            Generate llms.txt
          </button>
        ) : (
          <button type="button" className="btn btn-secondary" onClick={onStopScan}>
            Stop Scan
          </button>
        )}
      </div>
    </form>
  )
}
