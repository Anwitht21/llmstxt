"use client"

import { useState } from 'react'
import { Play, StopCircle, Globe, Layers, FileText, RefreshCw, Sparkles, Chrome } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'

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
    <Card className="mb-6">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Globe className="h-5 w-5 text-primary" />
          Configuration
        </CardTitle>
        <CardDescription>
          Configure crawling parameters and generate your llms.txt file
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="url" className="flex items-center gap-2">
              <Globe className="h-4 w-4" />
              Website URL
            </Label>
            <Input
              id="url"
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              disabled={isScanning}
              required
              placeholder="https://example.com"
              className="font-mono"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="maxPages" className="flex items-center gap-2">
                <Layers className="h-4 w-4" />
                Max Pages
              </Label>
              <Input
                id="maxPages"
                type="number"
                value={maxPages}
                onChange={(e) => setMaxPages(Number(e.target.value))}
                disabled={isScanning}
                min="1"
                max="500"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="descLength" className="flex items-center gap-2">
                <FileText className="h-4 w-4" />
                Snippet Length
              </Label>
              <Input
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

          <div className="space-y-4 pt-4 border-t">
            <h4 className="text-sm font-medium text-muted-foreground">Advanced Options</h4>

            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <RefreshCw className="h-4 w-4 text-muted-foreground" />
                <div>
                  <Label htmlFor="autoUpdate" className="cursor-pointer">
                    Automated Updates
                  </Label>
                  <p className="text-sm text-muted-foreground">
                    Keep llms.txt synchronized with your website
                  </p>
                </div>
              </div>
              <Switch
                id="autoUpdate"
                checked={enableAutoUpdate}
                onCheckedChange={setEnableAutoUpdate}
                disabled={isScanning}
              />
            </div>

            {enableAutoUpdate && (
              <div className="ml-6 space-y-2 animate-in slide-in-from-top-2">
                <Label htmlFor="recrawlInterval">Recrawl Interval</Label>
                <select
                  id="recrawlInterval"
                  value={recrawlInterval}
                  onChange={(e) => setRecrawlInterval(Number(e.target.value))}
                  disabled={isScanning}
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  <option value={1440}>Daily</option>
                  <option value={10080}>Weekly</option>
                  <option value={43200}>Monthly</option>
                </select>
              </div>
            )}

            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Sparkles className="h-4 w-4 text-muted-foreground" />
                <div>
                  <Label htmlFor="llmEnhance" className="cursor-pointer">
                    LLM Enhancement
                  </Label>
                  <p className="text-sm text-muted-foreground">
                    AI-powered organization and descriptions
                  </p>
                </div>
              </div>
              <Switch
                id="llmEnhance"
                checked={llmEnhance}
                onCheckedChange={setLlmEnhance}
                disabled={isScanning}
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Chrome className="h-4 w-4 text-muted-foreground" />
                <div>
                  <Label htmlFor="useBrightdata" className="cursor-pointer">
                    Smart Scraping
                  </Label>
                  <p className="text-sm text-muted-foreground">
                    Auto-escalate to browser for JS-heavy sites
                  </p>
                </div>
              </div>
              <Switch
                id="useBrightdata"
                checked={useBrightdata}
                onCheckedChange={setUseBrightdata}
                disabled={isScanning}
              />
            </div>
          </div>

          <div className="pt-4">
            {!isScanning ? (
              <Button type="submit" className="w-full" size="lg">
                <Play className="mr-2 h-4 w-4" />
                Generate llms.txt
              </Button>
            ) : (
              <Button
                type="button"
                variant="destructive"
                onClick={onStopScan}
                className="w-full"
                size="lg"
              >
                <StopCircle className="mr-2 h-4 w-4" />
                Stop Scan
              </Button>
            )}
          </div>
        </form>
      </CardContent>
    </Card>
  )
}
