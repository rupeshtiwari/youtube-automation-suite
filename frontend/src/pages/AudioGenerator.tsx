import { useEffect, useState } from 'react'
import { Download, Loader2, Mic, RotateCw } from 'lucide-react'
import { cn } from '@/lib/utils'

interface AudioResult {
  filename: string
  filesize: number
  filepath: string
}

interface AudioHistoryItem {
  filename: string
  filesize: number
  created_at: string
  download_url: string
  stream_url: string
}

export default function AudioGenerator() {
  const [text, setText] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [result, setResult] = useState<AudioResult | null>(null)
  const [history, setHistory] = useState<AudioHistoryItem[]>([])
  const [historyDir, setHistoryDir] = useState('')
  const [historyLoading, setHistoryLoading] = useState(false)
  const [historyError, setHistoryError] = useState('')

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
      void fetchHistory()
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

  const downloadFile = async (fname: string) => {
    try {
      const response = await fetch(`/download-audio/${fname}`)
      if (!response.ok) throw new Error('Download failed')
      const blob = await response.blob()
      const blobUrl = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = blobUrl
      link.download = fname
      link.style.display = 'none'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(blobUrl)
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Download failed'
      setError(`Error downloading: ${message}`)
      console.error('Download error:', error)
    }
  }

  const fetchHistory = async () => {
    try {
      setHistoryLoading(true)
      setHistoryError('')
      const res = await fetch('/api/audio-history')
      const data = await res.json()
      if (!res.ok) {
        throw new Error(data.error || 'Failed to load history')
      }
      setHistory(data.files || [])
      setHistoryDir(data.output_dir || '')
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Could not load history'
      setHistoryError(message)
    } finally {
      setHistoryLoading(false)
    }
  }

  // Initial load
  useEffect(() => {
    void fetchHistory()
  }, [])

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
          <div className="text-xs text-muted-foreground">If the player is silent, click Download to verify the file.</div>
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
            <button
              type="button"
              onClick={() => {
                downloadFile(result.filename)
              }}
              className="inline-flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium text-white bg-primary hover:bg-primary/90 transition"
            >
              <Download className="w-4 h-4" /> Download Audio
            </button>
          </div>
        </div>
      )}

      <div className="rounded-xl border border-border bg-card p-4 space-y-3 shadow-sm">
        <div className="flex items-center justify-between gap-3">
          <div>
            <h3 className="text-sm font-semibold text-foreground">History</h3>
            <p className="text-xs text-muted-foreground">
              Files saved in {historyDir || 'static/audio'} (newest first). Click download to re-fetch.
            </p>
          </div>
          <button
            type="button"
            onClick={() => void fetchHistory()}
            className="inline-flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium text-foreground bg-muted hover:bg-muted/80 transition"
          >
            <RotateCw className={cn('w-4 h-4', historyLoading && 'animate-spin')} /> Refresh
          </button>
        </div>

        {historyError && (
          <div className="rounded-lg border border-destructive/40 bg-destructive/10 text-destructive px-3 py-2 text-sm">
            {historyError}
          </div>
        )}

        {!historyLoading && history.length === 0 && !historyError && (
          <div className="text-sm text-muted-foreground">No files yet. Generate audio to see history.</div>
        )}

        {historyLoading && (
          <div className="text-sm text-muted-foreground inline-flex items-center gap-2">
            <Loader2 className="w-4 h-4 animate-spin" /> Loading history...
          </div>
        )}

        {history.length > 0 && (
          <div className="space-y-2">
            {history.map((item) => (
              <div
                key={item.filename}
                className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 rounded-lg border border-border px-3 py-2"
              >
                <div className="min-w-0">
                  <div className="text-sm font-medium text-foreground truncate">{item.filename}</div>
                  <div className="text-xs text-muted-foreground">
                    {new Date(item.created_at).toLocaleString()} • {formatFileSize(item.filesize)}
                  </div>
                </div>
                <div className="flex items-center gap-2 flex-shrink-0">
                  <a
                    className="inline-flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium text-white bg-primary hover:bg-primary/90 transition"
                    href={item.download_url}
                    onClick={(e) => {
                      e.preventDefault()
                      downloadFile(item.filename)
                    }}
                  >
                    <Download className="w-4 h-4" /> Download
                  </a>
                  <audio className="w-40" controls src={item.stream_url} />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
