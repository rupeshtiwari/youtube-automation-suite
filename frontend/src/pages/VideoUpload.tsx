import { useEffect, useState } from 'react'
import { Upload, Loader2, AlertCircle, CheckCircle, Youtube, Calendar, Plus, X } from 'lucide-react'
import api from '@/lib/api'

interface Playlist {
  playlistId: string
  playlistTitle: string
  playlistUrl: string
  itemCount: number
}

interface UploadFormData {
  title: string
  description: string
  tags: string
  playlist: string
  publishNow: boolean
  scheduleDate: string
  scheduleTime: string
  visibility: 'public' | 'unlisted' | 'private'
}

export default function VideoUpload() {
  const [file, setFile] = useState<File | null>(null)
  const [playlists, setPlaylists] = useState<Playlist[]>([])
  const [loadingPlaylists, setLoadingPlaylists] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [uploadProgress, setUploadProgress] = useState(0)
  const [showCreatePlaylist, setShowCreatePlaylist] = useState(false)
  const [newPlaylistName, setNewPlaylistName] = useState('')
  const [newPlaylistDescription, setNewPlaylistDescription] = useState('')
  const [creatingPlaylist, setCreatingPlaylist] = useState(false)

  const [formData, setFormData] = useState<UploadFormData>({
    title: '',
    description: '',
    tags: '',
    playlist: '',
    publishNow: true,
    scheduleDate: '',
    scheduleTime: '09:00',
    visibility: 'public'
  })

  // Fetch playlists on mount
  useEffect(() => {
    fetchPlaylists()
  }, [])

  const fetchPlaylists = async () => {
    setLoadingPlaylists(true)
    try {
      const response = await api.get('/api/playlists')
      if (response.data.playlists) {
        setPlaylists(response.data.playlists)
        if (response.data.playlists.length > 0 && !formData.playlist) {
          setFormData(prev => ({
            ...prev,
            playlist: response.data.playlists[0].playlistId
          }))
        }
      }
    } catch (err) {
      console.error('Error fetching playlists:', err)
      setError('Failed to load playlists')
    } finally {
      setLoadingPlaylists(false)
    }
  }

  const handleCreatePlaylist = async () => {
    if (!newPlaylistName.trim()) {
      setError('Playlist name is required')
      return
    }

    setCreatingPlaylist(true)
    setError('')

    try {
      const response = await api.post('/api/create-playlist', {
        title: newPlaylistName.trim(),
        description: newPlaylistDescription.trim() || 'Playlist created via YouTube Automation',
        privacy_status: 'public'
      })

      if (response.data.success) {
        // Refresh playlists
        await fetchPlaylists()
        // Set the new playlist as selected
        if (response.data.playlist_id) {
          setFormData(prev => ({
            ...prev,
            playlist: response.data.playlist_id
          }))
        }
        setNewPlaylistName('')
        setNewPlaylistDescription('')
        setShowCreatePlaylist(false)
        setSuccess('Playlist created successfully!')
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to create playlist'
      setError(message)
    } finally {
      setCreatingPlaylist(false)
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile) {
      if (!['video/mp4', 'video/quicktime', 'video/x-msvideo', 'video/x-matroska', 'video/webm'].includes(selectedFile.type)) {
        setError('Please select a valid video file (MP4, MOV, AVI, MKV, or WebM)')
        setFile(null)
        return
      }
      if (selectedFile.size > 12 * 1024 * 1024 * 1024) { // 12GB limit
        setError('File size exceeds 12GB limit')
        setFile(null)
        return
      }
      setFile(selectedFile)
      setError('')
    }
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target
    if (type === 'checkbox') {
      setFormData(prev => ({
        ...prev,
        [name]: (e.target as HTMLInputElement).checked
      }))
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: value
      }))
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSuccess('')

    // Validation
    if (!file) {
      setError('Please select a video file')
      return
    }

    if (!formData.title.trim()) {
      setError('Please enter a video title')
      return
    }

    if (!formData.publishNow && !formData.scheduleDate) {
      setError('Please select a schedule date')
      return
    }

    const data = new FormData()
    data.append('file', file)
    data.append('title', formData.title)
    data.append('description', formData.description)
    data.append('tags', formData.tags)
    data.append('playlist_id', formData.playlist)
    data.append('publish_now', String(formData.publishNow))
    if (!formData.publishNow) {
      data.append('schedule_datetime', `${formData.scheduleDate}T${formData.scheduleTime}`)
    }
    data.append('visibility', formData.visibility)

    setUploading(true)
    setUploadProgress(0)

    try {
      const response = await api.post('/api/upload-video', data, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent: any) => {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          )
          setUploadProgress(percentCompleted)
        },
      })

      if (response.data.success) {
        setSuccess(`Video uploaded successfully! Video ID: ${response.data.video_id}`)
        setFile(null)
        setFormData({
          title: '',
          description: '',
          tags: '',
          playlist: playlists.length > 0 ? playlists[0].playlistId : '',
          publishNow: true,
          scheduleDate: '',
          scheduleTime: '09:00',
          visibility: 'public'
        })
        setUploadProgress(0)

        // Reset file input
        const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement
        if (fileInput) fileInput.value = ''
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to upload video'
      setError(message)
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="p-6 space-y-6 max-w-4xl">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold mb-2 flex items-center gap-2">
          <Upload className="w-6 h-6 text-primary" />
          Upload Video to YouTube
        </h1>
        <p className="text-muted-foreground">Upload and publish your video with all details and scheduling options</p>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-red-800 dark:text-red-200 font-medium">Error</p>
            <p className="text-red-700 dark:text-red-300 text-sm">{error}</p>
          </div>
        </div>
      )}

      {/* Success Message */}
      {success && (
        <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4 flex items-start gap-3">
          <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-green-800 dark:text-green-200 font-medium">Success</p>
            <p className="text-green-700 dark:text-green-300 text-sm">{success}</p>
          </div>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* File Upload */}
        <div className="bg-card border-2 border-dashed border-border rounded-lg p-8">
          <label className="flex flex-col items-center justify-center cursor-pointer">
            <div className="text-center space-y-2">
              <Upload className="w-12 h-12 text-muted-foreground mx-auto" />
              <div>
                <p className="font-medium text-foreground">
                  {file ? file.name : 'Click to select video file'}
                </p>
                <p className="text-sm text-muted-foreground">
                  {file ? `${(file.size / (1024 * 1024 * 1024)).toFixed(2)} GB` : 'MP4, MOV, AVI, MKV, or WebM (Max 12GB)'}
                </p>
              </div>
            </div>
            <input
              type="file"
              accept="video/mp4,video/quicktime,video/x-msvideo,video/x-matroska,video/webm"
              onChange={handleFileChange}
              className="hidden"
              disabled={uploading}
            />
          </label>
        </div>

        {/* Video Details */}
        <div className="bg-card border border-border rounded-lg p-6 space-y-4">
          <h2 className="text-lg font-semibold">Video Details</h2>

          {/* Title */}
          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              Title <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              name="title"
              value={formData.title}
              onChange={handleInputChange}
              placeholder="Enter video title"
              maxLength={100}
              className="w-full px-3 py-2 rounded border border-border bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary"
              disabled={uploading}
            />
            <p className="text-xs text-muted-foreground mt-1">{formData.title.length}/100</p>
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-foreground mb-2">Description</label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleInputChange}
              placeholder="Enter video description (optional)"
              maxLength={5000}
              rows={4}
              className="w-full px-3 py-2 rounded border border-border bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary"
              disabled={uploading}
            />
            <p className="text-xs text-muted-foreground mt-1">{formData.description.length}/5000</p>
          </div>

          {/* Tags */}
          <div>
            <label className="block text-sm font-medium text-foreground mb-2">Tags</label>
            <input
              type="text"
              name="tags"
              value={formData.tags}
              onChange={handleInputChange}
              placeholder="Enter tags separated by commas (e.g., interview, tutorial, shorts)"
              className="w-full px-3 py-2 rounded border border-border bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary"
              disabled={uploading}
            />
            <p className="text-xs text-muted-foreground mt-1">Separate multiple tags with commas</p>
          </div>

          {/* Visibility */}
          <div>
            <label className="block text-sm font-medium text-foreground mb-2">Visibility</label>
            <select
              name="visibility"
              value={formData.visibility}
              onChange={handleInputChange}
              className="w-full px-3 py-2 rounded border border-border bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
              disabled={uploading}
            >
              <option value="public">Public - Anyone can find and watch</option>
              <option value="unlisted">Unlisted - Only people with link can watch</option>
              <option value="private">Private - Only you can watch</option>
            </select>
          </div>
        </div>

        {/* Playlist & Scheduling */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Playlist Selection */}
          <div className="bg-card border border-border rounded-lg p-6 space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold">Playlist</h2>
              <button
                onClick={() => setShowCreatePlaylist(true)}
                className="flex items-center gap-1 px-2 py-1 text-xs font-medium text-primary hover:text-primary/80 transition-colors"
                title="Create new playlist"
              >
                <Plus className="w-4 h-4" />
                New
              </button>
            </div>

            {loadingPlaylists ? (
              <div className="flex items-center gap-2 text-muted-foreground">
                <Loader2 className="w-4 h-4 animate-spin" />
                Loading playlists...
              </div>
            ) : playlists.length === 0 ? (
              <div className="space-y-3">
                <p className="text-sm text-muted-foreground">No playlists available. Create one to get started.</p>
                <button
                  onClick={() => setShowCreatePlaylist(true)}
                  className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded bg-primary/10 hover:bg-primary/20 text-primary text-sm font-medium transition-colors"
                >
                  <Plus className="w-4 h-4" />
                  Create Playlist
                </button>
              </div>
            ) : (
              <select
                name="playlist"
                value={formData.playlist}
                onChange={handleInputChange}
                className="w-full px-3 py-2 rounded border border-border bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                disabled={uploading}
              >
                <option value="">-- Select a playlist --</option>
                {playlists.map(pl => (
                  <option key={pl.playlistId} value={pl.playlistId}>
                    {pl.playlistTitle} ({pl.itemCount} videos)
                  </option>
                ))}
              </select>
            )}
          </div>

          {/* Scheduling */}
          <div className="bg-card border border-border rounded-lg p-6 space-y-4">
            <h2 className="text-lg font-semibold flex items-center gap-2">
              <Calendar className="w-5 h-5" />
              Scheduling
            </h2>

            {/* Publish Now / Schedule */}
            <div className="space-y-3">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  name="publishNow"
                  checked={formData.publishNow}
                  onChange={() => setFormData(prev => ({ ...prev, publishNow: true }))}
                  disabled={uploading}
                  className="w-4 h-4"
                />
                <span className="text-sm font-medium">Publish Immediately</span>
              </label>

              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  name="publishNow"
                  checked={!formData.publishNow}
                  onChange={() => setFormData(prev => ({ ...prev, publishNow: false }))}
                  disabled={uploading}
                  className="w-4 h-4"
                />
                <span className="text-sm font-medium">Schedule for Later</span>
              </label>
            </div>

            {/* Schedule Date & Time */}
            {!formData.publishNow && (
              <div className="space-y-3 pt-2 border-t border-border">
                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">
                    Date <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="date"
                    name="scheduleDate"
                    value={formData.scheduleDate}
                    onChange={handleInputChange}
                    min={new Date().toISOString().split('T')[0]}
                    className="w-full px-3 py-2 rounded border border-border bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                    disabled={uploading}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">Time</label>
                  <input
                    type="time"
                    name="scheduleTime"
                    value={formData.scheduleTime}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 rounded border border-border bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                    disabled={uploading}
                  />
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Create Playlist Dialog */}
        {showCreatePlaylist && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-card border border-border rounded-lg p-6 max-w-md w-full space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold">Create New Playlist</h3>
                <button
                  onClick={() => {
                    setShowCreatePlaylist(false)
                    setNewPlaylistName('')
                    setNewPlaylistDescription('')
                    setError('')
                  }}
                  className="text-muted-foreground hover:text-foreground transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <div>
                <label className="block text-sm font-medium text-foreground mb-2">Playlist Name *</label>
                <input
                  type="text"
                  value={newPlaylistName}
                  onChange={(e) => setNewPlaylistName(e.target.value)}
                  placeholder="Enter playlist name"
                  maxLength={100}
                  className="w-full px-3 py-2 rounded border border-border bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                  disabled={creatingPlaylist}
                />
                <p className="text-xs text-muted-foreground mt-1">{newPlaylistName.length}/100</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-foreground mb-2">Description (Optional)</label>
                <textarea
                  value={newPlaylistDescription}
                  onChange={(e) => setNewPlaylistDescription(e.target.value)}
                  placeholder="Enter playlist description"
                  maxLength={500}
                  rows={3}
                  className="w-full px-3 py-2 rounded border border-border bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary resize-none"
                  disabled={creatingPlaylist}
                />
                <p className="text-xs text-muted-foreground mt-1">{newPlaylistDescription.length}/500</p>
              </div>

              {/* Show existing playlists */}
              {playlists.length > 0 && (
                <div className="border-t border-border pt-4">
                  <label className="block text-sm font-medium text-foreground mb-2">Existing Playlists ({playlists.length})</label>
                  <div className="max-h-32 overflow-y-auto space-y-1 bg-muted/30 rounded p-2">
                    {playlists.slice(0, 10).map((pl) => (
                      <div key={pl.playlistId} className="text-xs text-muted-foreground flex items-center justify-between py-1 px-2 hover:bg-muted rounded">
                        <span className="truncate flex-1">{pl.playlistTitle}</span>
                        <span className="text-xs bg-background px-1.5 py-0.5 rounded ml-2 flex-shrink-0">{pl.itemCount}</span>
                      </div>
                    ))}
                    {playlists.length > 10 && (
                      <p className="text-xs text-muted-foreground text-center py-1">+ {playlists.length - 10} more playlists</p>
                    )}
                  </div>
                </div>
              )}

              <div className="flex gap-2">
                <button
                  onClick={() => {
                    setShowCreatePlaylist(false)
                    setNewPlaylistName('')
                    setNewPlaylistDescription('')
                    setError('')
                  }}
                  className="flex-1 px-3 py-2 rounded border border-border text-foreground font-medium hover:bg-accent transition-colors"
                  disabled={creatingPlaylist}
                >
                  Cancel
                </button>
                <button
                  onClick={handleCreatePlaylist}
                  disabled={creatingPlaylist || !newPlaylistName.trim()}
                  className="flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded bg-primary text-primary-foreground font-medium hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {creatingPlaylist ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Creating...
                    </>
                  ) : (
                    'Create'
                  )}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Upload Progress */}
        {uploading && uploadProgress > 0 && (
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <p className="text-sm font-medium">Uploading...</p>
              <p className="text-sm text-muted-foreground">{uploadProgress}%</p>
            </div>
            <div className="w-full h-2 bg-border rounded-full overflow-hidden">
              <div
                className="h-full bg-primary transition-all duration-300"
                style={{ width: `${uploadProgress}%` }}
              />
            </div>
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={uploading || !file || !formData.title.trim()}
          className="w-full flex items-center justify-center gap-2 px-6 py-3 rounded-lg bg-primary text-primary-foreground font-medium hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {uploading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Uploading Video...
            </>
          ) : (
            <>
              <Youtube className="w-5 h-5" />
              Upload to YouTube
            </>
          )}
        </button>
      </form>
    </div>
  )
}
