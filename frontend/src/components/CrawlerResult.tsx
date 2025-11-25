"use client"

import { useState } from 'react'

interface CrawlerResultProps {
  result: string
  hostedUrl: string
}

export default function CrawlerResult({ result, hostedUrl }: CrawlerResultProps) {
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    await navigator.clipboard.writeText(result)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const handleDownload = () => {
    const blob = new Blob([result], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'llms.txt'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  if (!result) return null

  return (
    <div className="result">
      <div className="result-header">
        <h3>Generated llms.txt</h3>
        <div className="result-actions">
          <button className="btn btn-small" onClick={handleCopy}>
            {copied ? 'Copied!' : 'Copy'}
          </button>
          <button className="btn btn-small" onClick={handleDownload}>
            Download
          </button>
          {hostedUrl && (
            <a href={hostedUrl} target="_blank" rel="noopener noreferrer" className="btn btn-small">
              View Hosted
            </a>
          )}
        </div>
      </div>
      <pre className="result-content">{result}</pre>
    </div>
  )
}
