import { useQuery } from '@tanstack/react-query'
import api from '@/lib/api'
import { 
  Video, 
  Folder,
  Download,
  Play,
  AlertCircle
} from 'lucide-react'
import { useState } from 'react'

interface ShortsFolder {
  name: string
  count: number
  path: string
}

interface ShortsLibraryData {
  folders: ShortsFolder[]
  total_videos: number
}

export default function ShortsLibrary() {
  const [selectedFolder, setSelectedFolder] = useState<string | null>(null)
  
  const { data, isLoading, error } = useQuery<ShortsLibraryData>({
    queryKey: ['shorts-library'],
    queryFn: async () => {
      const response = await api.get('/shorts-library')
      return response.data
    },
  })

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
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-red-800 dark:text-red-200 font-medium">Error loading shorts library</p>
            <p className="text-red-700 dark:text-red-300 text-sm">
              {error ? (error as any).message : 'No data available'}
            </p>
          </div>
        </div>
      </div>
    )
  }

  const folders = data.folders || []
  const totalVideos = data.total_videos || 0

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold mb-2 flex items-center gap-2">
          <Video className="w-6 h-6 text-primary" />
          Shorts Library
        </h1>
        <p className="text-muted-foreground">Your downloaded YouTube Shorts videos organized by playlist</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-card border border-border rounded-lg p-4">
          <div className="text-3xl font-bold text-primary mb-1">{totalVideos}</div>
          <div className="text-sm text-muted-foreground">Total Videos Downloaded</div>
        </div>
        <div className="bg-card border border-border rounded-lg p-4">
          <div className="text-3xl font-bold text-green-600 mb-1">{folders.length}</div>
          <div className="text-sm text-muted-foreground">Playlists/Folders</div>
        </div>
        <div className="bg-card border border-border rounded-lg p-4">
          <div className="text-3xl font-bold text-blue-600 mb-1">
            {folders.length > 0 ? (totalVideos / folders.length).toFixed(1) : 0}
          </div>
          <div className="text-sm text-muted-foreground">Avg Videos per Playlist</div>
        </div>
      </div>

      {/* Folders Grid */}
      {folders.length === 0 ? (
        <div className="bg-card border border-border rounded-lg p-12 text-center">
          <Download className="w-12 h-12 text-muted-foreground mx-auto mb-3 opacity-50" />
          <p className="text-lg font-medium mb-2">No Shorts Downloaded Yet</p>
          <p className="text-muted-foreground mb-4">
            Download YouTube Shorts from the Settings page first
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {folders.map((folder) => (
            <div
              key={folder.path}
              onClick={() => setSelectedFolder(selectedFolder === folder.path ? null : folder.path)}
              className="bg-card border border-border rounded-lg p-4 cursor-pointer hover:border-primary/50 hover:bg-accent/50 transition-all"
            >
              <div className="flex items-start justify-between mb-3">
                <Folder className="w-6 h-6 text-primary flex-shrink-0" />
                <div className="text-xs bg-primary/10 text-primary px-2 py-1 rounded font-medium">
                  {folder.count} video{folder.count !== 1 ? 's' : ''}
                </div>
              </div>
              <h3 className="font-medium text-sm line-clamp-2 break-words">{folder.name}</h3>
              <div className="mt-3 pt-3 border-t border-border">
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    window.open(`/view-shorts-folder?path=${encodeURIComponent(folder.path)}`, '_blank')
                  }}
                  className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded bg-primary/10 hover:bg-primary/20 text-primary text-sm font-medium transition-colors"
                >
                  <Play className="w-4 h-4" />
                  View Videos
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
