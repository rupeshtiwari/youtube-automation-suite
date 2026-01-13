import { useEffect, useState } from 'react'
import { Download, Loader2, Search, Tag, Folder } from 'lucide-react'
import api from '@/lib/api'

interface AudioFile {
  id: number
  filename: string
  filesize: number
  course_name?: string
  module_number?: string
  module_name?: string
  track_number?: string
  track_name?: string
  description?: string
  tags?: string
  created_at: string
  download_url: string
  stream_url: string
}

interface GroupedAudio {
  [course: string]: {
    [module: string]: AudioFile[]
  }
}

interface TagFormData {
  filename: string
  course_name: string
  module_number: string
  module_name: string
  track_number: string
  track_name: string
  description: string
  tags: string
}

export default function AudioLibrary() {
  const [grouped, setGrouped] = useState<GroupedAudio>({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [searchQuery, setSearchQuery] = useState('')
  const [courseFilter, setCourseFilter] = useState('')
  const [searchResults, setSearchResults] = useState<AudioFile[]>([])
  const [showSearch, setShowSearch] = useState(false)
  const [selectedFile, setSelectedFile] = useState<AudioFile | null>(null)
  const [showTagForm, setShowTagForm] = useState(false)
  const [tagForm, setTagForm] = useState<TagFormData>({
    filename: '',
    course_name: '',
    module_number: '',
    module_name: '',
    track_number: '',
    track_name: '',
    description: '',
    tags: ''
  })

  useEffect(() => {
    fetchAudioLibrary()
  }, [])

  const fetchAudioLibrary = async () => {
    try {
      setLoading(true)
      const res = await api.get('/audio/metadata')
      setGrouped(res.data.grouped || {})
      setError('')
    } catch (err) {
      setError('Failed to load audio library')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!searchQuery.trim()) return

    try {
      const res = await api.get('/audio/search', {
        params: {
          q: searchQuery,
          course: courseFilter
        }
      })
      setSearchResults(res.data.results || [])
      setShowSearch(true)
    } catch (err) {
      setError('Search failed')
    }
  }

  const handleTagFile = async (file: AudioFile) => {
    setSelectedFile(file)
    setTagForm({
      filename: file.filename,
      course_name: file.course_name || '',
      module_number: file.module_number || '',
      module_name: file.module_name || '',
      track_number: file.track_number || '',
      track_name: file.track_name || '',
      description: file.description || '',
      tags: file.tags || ''
    })
    setShowTagForm(true)
  }

  const handleSubmitTag = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await api.post('/audio/tag', tagForm)
      setShowTagForm(false)
      setSelectedFile(null)
      await fetchAudioLibrary()
    } catch (err) {
      setError('Failed to tag audio file')
    }
  }

  const downloadFile = async (filename: string) => {
    try {
      const response = await fetch(`/download-audio/${filename}`)
      if (!response.ok) throw new Error('Download failed')
      const blob = await response.blob()
      const blobUrl = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = blobUrl
      link.download = filename
      link.style.display = 'none'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(blobUrl)
    } catch (err) {
      setError('Download failed')
    }
  }

  if (loading) {
    return (
      <div className="p-6 flex items-center justify-center">
        <div className="inline-flex items-center gap-2">
          <Loader2 className="w-4 h-4 animate-spin" />
          Loading audio library...
        </div>
      </div>
    )
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold mb-2">Audio Library</h1>
        <p className="text-muted-foreground">Organize and manage your generated audio files</p>
      </div>

      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 text-red-800 dark:text-red-200">
          {error}
        </div>
      )}

      {/* Search Bar */}
      <form onSubmit={handleSearch} className="space-y-3">
        <div className="flex gap-2">
          <input
            type="text"
            placeholder="Search audio files..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="flex-1 px-4 py-2 border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
          />
          <button
            type="submit"
            className="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition inline-flex items-center gap-2"
          >
            <Search className="w-4 h-4" />
            Search
          </button>
          {showSearch && (
            <button
              type="button"
              onClick={() => setShowSearch(false)}
              className="px-4 py-2 border border-border rounded-lg hover:bg-muted transition"
            >
              Clear
            </button>
          )}
        </div>

        {/* Filters */}
        <div className="flex gap-2">
          <input
            type="text"
            placeholder="Filter by course..."
            value={courseFilter}
            onChange={(e) => setCourseFilter(e.target.value)}
            className="flex-1 px-4 py-2 border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary text-sm"
          />
        </div>
      </form>

      {/* Search Results */}
      {showSearch && (
        <div className="space-y-3">
          <h2 className="text-lg font-semibold">Search Results ({searchResults.length})</h2>
          {searchResults.length === 0 ? (
            <p className="text-muted-foreground">No files found</p>
          ) : (
            <div className="space-y-2">
              {searchResults.map((file) => (
                <AudioFileCard
                  key={file.filename}
                  file={file}
                  onTag={handleTagFile}
                  onDownload={downloadFile}
                />
              ))}
            </div>
          )}
        </div>
      )}

      {/* Grouped Audio Files */}
      {!showSearch && Object.keys(grouped).length > 0 && (
        <div className="space-y-6">
          {Object.entries(grouped).map(([courseName, modules]) => (
            <div key={courseName} className="space-y-3">
              <div className="flex items-center gap-2 sticky top-0 bg-background/80 backdrop-blur z-10 py-2">
                <Folder className="w-5 h-5 text-primary" />
                <h2 className="text-xl font-bold">{courseName}</h2>
                <span className="text-sm text-muted-foreground">
                  {Object.values(modules).flat().length} files
                </span>
              </div>

              <div className="space-y-4 ml-4">
                {Object.entries(modules).map(([moduleName, files]) => (
                  <div key={moduleName} className="space-y-2">
                    <h3 className="font-semibold text-sm text-muted-foreground">{moduleName}</h3>
                    <div className="space-y-2 border-l-2 border-muted pl-4">
                      {files.map((file) => (
                        <AudioFileCard
                          key={file.filename}
                          file={file}
                          onTag={handleTagFile}
                          onDownload={downloadFile}
                        />
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {!showSearch && Object.keys(grouped).length === 0 && (
        <div className="text-center py-12">
          <p className="text-muted-foreground">No audio files yet. Generate some audio first!</p>
        </div>
      )}

      {/* Tag Form Modal */}
      {showTagForm && selectedFile && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-background border border-border rounded-lg p-6 max-w-md w-full space-y-4">
            <h2 className="text-xl font-bold">Tag Audio File</h2>
            <p className="text-sm text-muted-foreground">{selectedFile.filename}</p>

            <form onSubmit={handleSubmitTag} className="space-y-3">
              <div>
                <label className="text-sm font-medium">Course Name</label>
                <input
                  type="text"
                  placeholder="e.g., React Mastery"
                  value={tagForm.course_name}
                  onChange={(e) => setTagForm({ ...tagForm, course_name: e.target.value })}
                  className="w-full px-3 py-2 border border-border rounded-lg text-sm"
                />
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-sm font-medium">Module Number</label>
                  <input
                    type="number"
                    placeholder="1"
                    value={tagForm.module_number}
                    onChange={(e) => setTagForm({ ...tagForm, module_number: e.target.value })}
                    className="w-full px-3 py-2 border border-border rounded-lg text-sm"
                  />
                </div>
                <div>
                  <label className="text-sm font-medium">Module Name</label>
                  <input
                    type="text"
                    placeholder="Basics"
                    value={tagForm.module_name}
                    onChange={(e) => setTagForm({ ...tagForm, module_name: e.target.value })}
                    className="w-full px-3 py-2 border border-border rounded-lg text-sm"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-sm font-medium">Track Number</label>
                  <input
                    type="number"
                    placeholder="1"
                    value={tagForm.track_number}
                    onChange={(e) => setTagForm({ ...tagForm, track_number: e.target.value })}
                    className="w-full px-3 py-2 border border-border rounded-lg text-sm"
                  />
                </div>
                <div>
                  <label className="text-sm font-medium">Track Name</label>
                  <input
                    type="text"
                    placeholder="Introduction"
                    value={tagForm.track_name}
                    onChange={(e) => setTagForm({ ...tagForm, track_name: e.target.value })}
                    className="w-full px-3 py-2 border border-border rounded-lg text-sm"
                  />
                </div>
              </div>

              <div>
                <label className="text-sm font-medium">Description</label>
                <textarea
                  placeholder="Optional description..."
                  value={tagForm.description}
                  onChange={(e) => setTagForm({ ...tagForm, description: e.target.value })}
                  className="w-full px-3 py-2 border border-border rounded-lg text-sm"
                  rows={2}
                />
              </div>

              <div>
                <label className="text-sm font-medium">Tags (comma-separated)</label>
                <input
                  type="text"
                  placeholder="tutorial, beginner, important"
                  value={tagForm.tags}
                  onChange={(e) => setTagForm({ ...tagForm, tags: e.target.value })}
                  className="w-full px-3 py-2 border border-border rounded-lg text-sm"
                />
              </div>

              <div className="flex gap-2">
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition font-medium"
                >
                  Save Tags
                </button>
                <button
                  type="button"
                  onClick={() => setShowTagForm(false)}
                  className="flex-1 px-4 py-2 border border-border rounded-lg hover:bg-muted transition"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

function AudioFileCard({
  file,
  onTag,
  onDownload
}: {
  file: AudioFile
  onTag: (file: AudioFile) => void
  onDownload: (filename: string) => void
}) {
  const formatFileSize = (bytes: number) => {
    if (!bytes) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return `${Math.round((bytes / Math.pow(k, i)) * 100) / 100} ${sizes[i]}`
  }

  return (
    <div className="border border-border rounded-lg p-3 hover:bg-muted/50 transition">
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <div className="font-medium text-sm truncate">{file.track_name || file.filename}</div>
          <div className="text-xs text-muted-foreground mt-1">
            {formatFileSize(file.filesize)} • {new Date(file.created_at).toLocaleDateString()}
          </div>
          {file.tags && (
            <div className="flex gap-1 mt-2 flex-wrap">
              {file.tags.split(',').map((tag) => (
                <span key={tag} className="px-2 py-0.5 text-xs bg-primary/10 text-primary rounded">
                  {tag.trim()}
                </span>
              ))}
            </div>
          )}
        </div>
        <div className="flex items-center gap-1 flex-shrink-0">
          <button
            onClick={() => onTag(file)}
            className="p-2 hover:bg-muted rounded transition"
            title="Tag file"
          >
            <Tag className="w-4 h-4" />
          </button>
          <button
            onClick={() => onDownload(file.filename)}
            className="p-2 hover:bg-muted rounded transition"
            title="Download"
          >
            <Download className="w-4 h-4" />
          </button>
          <audio className="w-32" controls src={file.stream_url} />
        </div>
      </div>
    </div>
  )
}
