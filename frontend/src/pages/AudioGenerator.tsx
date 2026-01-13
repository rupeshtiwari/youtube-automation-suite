import { useState } from 'react'
import { Download, Loader2, Mic } from 'lucide-react'
import { cn } from '@/lib/utils'

interface AudioResult {
  filename: string
  filesize: number
  filepath: string
}

export default function AudioGenerator() {
  const [text, setText] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [result, setResult] = useState<AudioResult | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSuccess('')

    const trimmed = text.trim()
    if (!trimmed) {
      setError('Please enter some text')
      return
    }

    if (trimmed.length > 10000) {
      setError('Text is too long (max 10,000 characters)')
      return
    }

    setLoading(true)
    try {
      const res = await fetch('/api/generate-audio', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: trimmed }),
      })

      const data = await res.json()
      if (!res.ok) {
        throw new Error(data.error || 'Failed to generate audio')
      }

      setResult({
        filename: data.filename,
        filesize: data.filesize,
        filepath: data.filepath,
      })
      setSuccess('Audio created successfully')
    } catch (err) {
      const message = err instanceof Error ? err.message : 'An error occurred'
      setError(message)
      setResult(null)
    } finally {
      setLoading(false)
    }
  }

  const clear = () => {
    setText('')
    setResult(null)
    setError('')
    setSuccess('')
  }

  const formatFileSize = (bytes: number) => {
    if (!bytes) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return `${Math.round((bytes / Math.pow(k, i)) * 100) / 100} ${sizes[i]}`
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div className="flex items-center gap-3">
        <div className="p-3 rounded-xl bg-primary/10 text-primary">
          <Mic className="w-6 h-6" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-foreground">Audio Generator</h1>
          <p className="text-muted-foreground">Convert text to speech using ElevenLabs</p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-foreground mb-2">Enter your paragraph</label>
          <textarea
            className="w-full min-h-[160px] rounded-xl border border-border bg-card px-3 py-3 text-sm text-foreground shadow-sm focus:outline-none focus:ring-2 focus:ring-primary"
            placeholder="Type or paste your text here..."
            value={text}
            onChange={(e) => setText(e.target.value)}
          />
          <div className="text-xs text-muted-foreground mt-1 flex items-center gap-2">
            <span>{text.length} characters</span>
            {text.length > 5000 && <span className="text-amber-600">Large text may take longer</span>}
          </div>
        </div>

        <div className="flex gap-3">
          <button
            type="submit"
            className={cn(
              'inline-flex items-center justify-center gap-2 rounded-lg px-4 py-2 text-sm font-medium text-white shadow-sm bg-primary hover:bg-primary/90 transition',
              loading && 'opacity-70 cursor-not-allowed'
            )}
            disabled={loading}
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Mic className="w-4 h-4" />}
            {loading ? 'Generating...' : 'Generate Audio'}
          </button>
          <button
            type="button"
            onClick={clear}
            className="inline-flex items-center justify-center gap-2 rounded-lg px-4 py-2 text-sm font-medium text-foreground bg-muted hover:bg-muted/80 transition"
          >
            Clear
          </button>
        </div>

        {error && (
          <div className="rounded-lg border border-destructive/40 bg-destructive/10 text-destructive px-3 py-2 text-sm">
            {error}
          </div>
        )}
        {success && (
          <div className="rounded-lg border border-emerald-500/40 bg-emerald-500/10 text-emerald-700 px-3 py-2 text-sm">
            {success}
          </div>
        )}
      </form>

      {result && (
        <div className="rounded-xl border border-border bg-card p-4 space-y-4 shadow-sm">
          <h3 className="text-sm font-semibold text-foreground">Audio Created</h3>
          <audio className="w-full" controls src={`/audio/${result.filename}`} />
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-sm text-muted-foreground">
            <div>
              <div className="text-foreground font-medium">Filename</div>
              <div className="truncate">{result.filename}</div>
            </div>
            <div>
              <div className="text-foreground font-medium">File Size</div>
              <div>{formatFileSize(result.filesize)}</div>
            </div>
            <div>
              <div className="text-foreground font-medium">Location</div>
              <div className="truncate">{result.filepath}</div>
            </div>
          </div>
          <div>
            <a
              href={`/download-audio/${result.filename}`}
              className="inline-flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium text-white bg-primary hover:bg-primary/90 transition"
            >
              <Download className="w-4 h-4" /> Download Audio
            </a>
          </div>
        </div>
      )}
    </div>
  )
}
