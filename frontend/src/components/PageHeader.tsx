import { FileText } from "lucide-react"

export default function PageHeader() {
  return (
    <header className="text-center space-y-4 mb-8">
      <div className="flex items-center justify-center gap-3 mb-4">
        <div className="p-3 bg-primary/10 rounded-lg">
          <FileText className="h-8 w-8 text-primary" />
        </div>
        <h1 className="text-4xl font-bold text-foreground">
          llms.txt Generator
        </h1>
      </div>
      <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
        Automatically generate structured <span className="font-mono">llms.txt</span> files
        for any website with real-time crawling and AI enhancement
      </p>
    </header>
  )
}
