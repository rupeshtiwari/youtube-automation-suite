import { useQuery } from '@tanstack/react-query'
import api from '@/lib/api'
import { Video, AlertCircle, ArrowLeft, Play, Download } from 'lucide-react'
import { useNavigate, useSearchParams } from 'react-router-dom'

interface VideoFile {
  name: string
  path: string
  size: number
  modified: number
}

interface ShortsFolderData {
  folder_name: string
  folder_path: string
  videos: VideoFile[]
  count: number
}

export default function ShortsFolder() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const folderPath = searchParams.get('path')

  const { data, isLoading, error } = useQuery<ShortsFolderData>({
    queryKey: ['shorts-folder', folderPath],
    queryFn: async () => {
      if (!folderPath) throw new Error('No folder path provided')
      const response = await api.get(`/shorts-folder-videos?path=${encodeURIComponent(folderPath)}`)
      return response.data
    },
    enabled: !!folderPath,
  })

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
  }

  const formatDate = (timestamp: number) => {
    return new Date(timestamp * 1000).toLocaleDateString()
  }

  if (!folderPath) {
    return (
      <div className="p-6">
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <p className="text-red-800 dark:text-red-200">No folder path specified</p>
        </div>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    )
  }

  if (error || !data) {
    return (
      <div className="p-6">
        <button
          onClick={() => navigate('/shorts-library')}
          className="mb-4 flex items-center gap-2 text-primary hover:text-primary/80"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Library
        </button>
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-red-800 dark:text-red-200 font-medium">Error loading videos</p>
            <p className="text-red-700 dark:text-red-300 text-sm">
              {error ? (error as any).message : 'No data available'}
            </p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <button
          onClick={() => navigate('/shorts-library')}
          className="mb-4 flex items-center gap-2 text-primary hover:text-primary/80 font-medium"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Library
        </button>
        <h1 className="text-2xl font-bold mb-2 flex items-center gap-2">
          <Video className="w-6 h-6 text-primary" />
          {data.folder_name}
        </h1>
        <p className="text-muted-foreground">{data.count} video{data.count !== 1 ? 's' : ''}</p>
      </div>

      {/* Videos Grid */}
      {data.videos.length === 0 ? (
        <div className="bg-card border border-border rounded-lg p-12 text-center">
          <Video className="w-12 h-12 mx-auto mb-4 text-muted-foreground opacity-50" />
          <p className="text-muted-foreground">No videos found in this folder</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {data.videos.map((video) => (
            <div
              key={video.path}
              className="bg-card border border-border rounded-lg overflow-hidden hover:border-primary/50 transition-all group"
            >
              {/* Video Player */}
              <div className="relative aspect-video bg-black">
                <video
                  className="w-full h-full object-contain"
                  controls
                  preload="metadata"
                >
                  <source src={`/${video.path}`} type="video/mp4" />
                  Your browser does not support the video tag.
                </video>
              </div>

              {/* Video Info */}
              <div className="p-4 space-y-3">
                <h3 className="font-medium text-sm line-clamp-2 break-words" title={video.name}>
                  {video.name}
                </h3>
                
                <div className="flex items-center justify-between text-xs text-muted-foreground">
                  <span>{formatFileSize(video.size)}</span>
                  <span>{formatDate(video.modified)}</span>
                </div>

                {/* Actions */}
                <div className="flex gap-2 pt-2 border-t border-border">
                  <a
                    href={`/${video.path}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded bg-primary/10 hover:bg-primary/20 text-primary text-sm font-medium transition-colors"
                  >
                    <Play className="w-4 h-4" />
                    Play
                  </a>
                  <a
                    href={`/${video.path}`}
                    download
                    className="flex items-center justify-center gap-2 px-3 py-2 rounded border border-border hover:bg-accent text-sm font-medium transition-colors"
                  >
                    <Download className="w-4 h-4" />
                  </a>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
