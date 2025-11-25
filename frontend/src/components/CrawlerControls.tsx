"use client"

import { useState } from 'react'

interface CrawlerControlsProps {
  onStartScan: (url: string, maxPages: number, descLength: number) => void
  onStopScan: () => void
  isScanning: boolean
}

export default function CrawlerControls({ onStartScan, onStopScan, isScanning }: CrawlerControlsProps) {
  const [url, setUrl] = useState('https://example.com')
  const [maxPages, setMaxPages] = useState(50)
  const [descLength, setDescLength] = useState(500)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!isScanning) {
      onStartScan(url, maxPages, descLength)
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
