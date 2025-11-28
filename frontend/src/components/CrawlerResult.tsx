"use client"

import { useState } from 'react'
import { Copy, Download, ExternalLink, Check, FileText, Code } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { ScrollArea } from '@/components/ui/scroll-area'

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

  const lines = result.split('\n')
  const title = lines[0]?.replace(/^#\s*/, '') || 'llms.txt'
  const sections = result.split(/^##\s/m).slice(1)

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5 text-primary" />
              Generated llms.txt
            </CardTitle>
            <CardDescription>
              Your generated llms.txt file is ready
            </CardDescription>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handleCopy}
              className="gap-2"
            >
              {copied ? (
                <>
                  <Check className="h-4 w-4" />
                  Copied!
                </>
              ) : (
                <>
                  <Copy className="h-4 w-4" />
                  Copy
                </>
              )}
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={handleDownload}
              className="gap-2"
            >
              <Download className="h-4 w-4" />
              Download
            </Button>
            {hostedUrl && (
              <Button
                variant="outline"
                size="sm"
                asChild
                className="gap-2"
              >
                <a href={hostedUrl} target="_blank" rel="noopener noreferrer">
                  <ExternalLink className="h-4 w-4" />
                  View Hosted
                </a>
              </Button>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="formatted" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="formatted" className="gap-2">
              <Code className="h-4 w-4" />
              Formatted
            </TabsTrigger>
            <TabsTrigger value="preview" className="gap-2">
              <FileText className="h-4 w-4" />
              Preview
            </TabsTrigger>
          </TabsList>

          <TabsContent value="formatted" className="mt-4">
            <ScrollArea className="h-[500px] w-full rounded-md border bg-muted/20 p-4">
              <pre className="font-mono text-xs text-foreground whitespace-pre-wrap">
                {result}
              </pre>
            </ScrollArea>
          </TabsContent>

          <TabsContent value="preview" className="mt-4">
            <ScrollArea className="h-[500px] w-full rounded-md border bg-muted/20 p-6">
              <div className="prose prose-invert max-w-none">
                <h1 className="text-2xl font-bold mb-4 text-primary">{title}</h1>
                {sections.map((section, idx) => {
                  const [sectionTitle, ...sectionLines] = section.split('\n')
                  return (
                    <div key={idx} className="mb-6">
                      <h2 className="text-xl font-semibold mb-2 text-foreground">
                        {sectionTitle}
                      </h2>
                      <div className="space-y-1">
                        {sectionLines
                          .filter(line => line.trim())
                          .map((line, lineIdx) => (
                            <div
                              key={lineIdx}
                              className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                            >
                              {line}
                            </div>
                          ))}
                      </div>
                    </div>
                  )
                })}
              </div>
            </ScrollArea>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  )
}
