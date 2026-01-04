import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '@/lib/api'
import { 
  Video, 
  Youtube, 
  Share2,
  Filter,
  Facebook,
  Linkedin,
  Instagram,
  Calendar,
  CheckCircle2,
  XCircle,
  PlayCircle,
  ExternalLink,
  Grid3x3,
  List
} from 'lucide-react'

interface Platform {
  youtube: boolean
  facebook: boolean
  instagram: boolean
  linkedin: boolean
}

interface VideoData {
  video_id: string
  title: string
  youtube_url: string
  playlist_id: string
  playlist_name: string
  privacy_status: string
  youtube_published_date: string | null
  youtube_schedule_date: string | null
  description: string | null
  video_type: string | null
  role: string | null
  type: string | null
  platforms: Platform
  missing_platforms: string[]
  scheduled_count: number
  posts: any[]
}

interface ShortsData {
  videos: VideoData[]
  total_videos: number
  total_youtube: number
  total_other_platforms: number
  total_not_scheduled: number
  available_roles: string[]
  available_types: string[]
  roles: Record<string, string>
  types: Record<string, string>
  source: string
}

export default function ShortsNew() {
  const [roleFilter, setRoleFilter] = useState('')
  const [typeFilter, setTypeFilter] = useState('')
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('list')
  const queryClient = useQueryClient()

  const { data, isLoading, error } = useQuery<ShortsData>({
    queryKey: ['shorts-videos', roleFilter, typeFilter],
    queryFn: async () => {
      const params = new URLSearchParams()
      if (roleFilter) params.append('role', roleFilter)
      if (typeFilter) params.append('type', typeFilter)
      
      const response = await api.get(`/shorts?${params.toString()}`)
      return response.data
    },
  })

  const scheduleMutation = useMutation({
    mutationFn: async ({ videoId, platform }: { videoId: string; platform: string }) => {
      const response = await api.post('/schedule-to-platform', {
        video_id: videoId,
        platform,
      })
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['shorts-videos'] })
    },
  })

  const handleSchedule = async (videoId: string, platform: string, videoTitle: string) => {
    const confirmation = confirm(
      `Schedule "${videoTitle.substring(0, 50)}${videoTitle.length > 50 ? '...' : ''}" to ${platform.toUpperCase()}?`
    )
    if (!confirmation) return
    
    try {
      const result = await scheduleMutation.mutateAsync({ videoId, platform })
      alert(`✅ ${result.message}`)
    } catch (error: any) {
      alert('❌ Error: ' + (error.response?.data?.error || error.message))
    }
  }

  const getPlatformIcon = (platform: string) => {
    const className = "w-4 h-4"
    switch (platform) {
      case 'facebook':
        return <Facebook className={className} />
      case 'instagram':
        return <Instagram className={className} />
      case 'linkedin':
        return <Linkedin className={className} />
      case 'youtube':
        return <Youtube className={className} />
      default:
        return <Share2 className={className} />
    }
  }

  const getPlatformColor = (platform: string) => {
    switch (platform) {
      case 'youtube':
        return 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800 text-red-700 dark:text-red-300'
      case 'facebook':
        return 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800 text-blue-700 dark:text-blue-300'
      case 'instagram':
        return 'bg-pink-50 dark:bg-pink-900/20 border-pink-200 dark:border-pink-800 text-pink-700 dark:text-pink-300'
      case 'linkedin':
        return 'bg-cyan-50 dark:bg-cyan-900/20 border-cyan-200 dark:border-cyan-800 text-cyan-700 dark:text-cyan-300'
      default:
        return 'bg-gray-50 dark:bg-gray-800/50 border-gray-200 dark:border-gray-700'
    }
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
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <p className="text-red-800 dark:text-red-200">
            Error loading shorts: {error ? (error as any).message : 'No data available'}
          </p>
          <p className="text-sm text-red-600 dark:text-red-400 mt-2">
            Make sure you've synced videos from YouTube first.
          </p>
        </div>
      </div>
    )
  }

  const videos = data.videos || []
  const { total_videos, total_youtube, total_other_platforms, total_not_scheduled } = data

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold mb-2">📺 Shorts - Buffer Style</h1>
          <p className="text-muted-foreground">
            Schedule your YouTube Shorts across all platforms like Buffer.com
          </p>
        </div>
        <div className="flex items-center gap-2">
          {data.source === 'database' && (
            <div className="px-3 py-1 bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-200 rounded text-sm">
              📂 Database Mode
            </div>
          )}
          <div className="flex bg-card border border-border rounded-lg p-1">
            <button
              onClick={() => setViewMode('list')}
              className={`px-3 py-1.5 rounded ${
                viewMode === 'list' ? 'bg-primary text-primary-foreground' : 'hover:bg-secondary'
              }`}
            >
              <List className="w-4 h-4" />
            </button>
            <button
              onClick={() => setViewMode('grid')}
              className={`px-3 py-1.5 rounded ${
                viewMode === 'grid' ? 'bg-primary text-primary-foreground' : 'hover:bg-secondary'
              }`}
            >
              <Grid3x3 className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Stats Bar */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 border border-blue-200 dark:border-blue-800 rounded-xl p-5 shadow-sm">
          <div className="text-4xl font-bold text-blue-600 mb-1">{total_videos}</div>
          <div className="text-sm text-blue-800 dark:text-blue-300 font-medium">Total Videos</div>
        </div>
        <div className="bg-gradient-to-br from-red-50 to-red-100 dark:from-red-900/20 dark:to-red-800/20 border border-red-200 dark:border-red-800 rounded-xl p-5 shadow-sm">
          <div className="text-4xl font-bold text-red-600 mb-1">{total_youtube}</div>
          <div className="text-sm text-red-800 dark:text-red-300 font-medium">On YouTube</div>
        </div>
        <div className="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 border border-green-200 dark:border-green-800 rounded-xl p-5 shadow-sm">
          <div className="text-4xl font-bold text-green-600 mb-1">{total_other_platforms}</div>
          <div className="text-sm text-green-800 dark:text-green-300 font-medium">Multi-Platform</div>
        </div>
        <div className="bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-900/20 dark:to-orange-800/20 border border-orange-200 dark:border-orange-800 rounded-xl p-5 shadow-sm">
          <div className="text-4xl font-bold text-orange-600 mb-1">{total_not_scheduled}</div>
          <div className="text-sm text-orange-800 dark:text-orange-300 font-medium">YouTube Only</div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-card border border-border rounded-xl p-5 shadow-sm">
        <div className="flex items-center gap-2 mb-4">
          <Filter className="w-5 h-5 text-primary" />
          <h3 className="font-semibold text-lg">Filters</h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium mb-2">Role</label>
            <select
              value={roleFilter}
              onChange={(e) => setRoleFilter(e.target.value)}
              className="w-full px-4 py-2.5 bg-background border border-border rounded-lg focus:ring-2 focus:ring-primary"
            >
              <option value="">All Roles</option>
              {Object.entries(data.roles || {}).map(([key, label]) => (
                <option key={key} value={key}>
                  {String(label)}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Type</label>
            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              className="w-full px-4 py-2.5 bg-background border border-border rounded-lg focus:ring-2 focus:ring-primary"
            >
              <option value="">All Types</option>
              {Object.entries(data.types || {}).map(([key, label]) => (
                <option key={key} value={key}>
                  {String(label)}
                </option>
              ))}
            </select>
          </div>
          <div className="flex items-end">
            <button
              onClick={() => {
                setRoleFilter('')
                setTypeFilter('')
              }}
              className="w-full px-4 py-2.5 bg-secondary text-secondary-foreground rounded-lg hover:bg-secondary/80 font-medium transition-colors"
            >
              Clear Filters
            </button>
          </div>
        </div>
      </div>

      {/* Videos List */}
      {videos.length === 0 ? (
        <div className="bg-card border border-border rounded-xl p-12 text-center">
          <Video className="w-20 h-20 mx-auto mb-4 text-muted-foreground opacity-50" />
          <h3 className="text-xl font-semibold mb-2">No Videos Found</h3>
          <p className="text-muted-foreground mb-4">
            {roleFilter || typeFilter
              ? 'Try adjusting your filters to see more videos'
              : 'No shorts found in the database. Sync from YouTube first on the Settings page.'}
          </p>
          {!roleFilter && !typeFilter && (
            <a
              href="/settings"
              className="inline-flex items-center gap-2 px-6 py-3 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
            >
              Go to Settings →
            </a>
          )}
        </div>
      ) : (
        <div className={viewMode === 'grid' ? 'grid grid-cols-1 lg:grid-cols-2 gap-4' : 'space-y-4'}>
          {videos.map((video: VideoData) => (
            <div
              key={video.video_id}
              className="bg-card border border-border rounded-xl p-5 hover:shadow-xl transition-all duration-200"
            >
              <div className="flex gap-4">
                {/* Video Icon */}
                <div className="flex-shrink-0">
                  <div className="w-16 h-16 bg-gradient-to-br from-red-500 to-red-600 rounded-xl flex items-center justify-center shadow-lg">
                    <PlayCircle className="w-8 h-8 text-white" />
                  </div>
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-4 mb-3">
                    <div className="flex-1">
                      <h3 className="font-bold text-lg mb-2 line-clamp-2 hover:text-primary cursor-pointer">
                        {video.title}
                      </h3>
                      <div className="flex flex-wrap items-center gap-2 text-sm text-muted-foreground mb-2">
                        <span className="truncate max-w-xs">{video.playlist_name}</span>
                        {video.role && (
                          <span className="px-2.5 py-1 bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 rounded-full text-xs font-medium">
                            {data.roles[video.role] || video.role}
                          </span>
                        )}
                        {video.type && (
                          <span className="px-2.5 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded-full text-xs font-medium">
                            {data.types[video.type] || video.type}
                          </span>
                        )}
                      </div>
                    </div>
                    <a
                      href={video.youtube_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="p-2.5 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors shadow-sm"
                      title="Watch on YouTube"
                    >
                      <ExternalLink className="w-4 h-4" />
                    </a>
                  </div>

                  {/* Platform Status & Schedule Buttons */}
                  <div className="grid grid-cols-4 gap-2">
                    {(['youtube', 'facebook', 'instagram', 'linkedin'] as const).map((platform) => {
                      const isScheduled = video.platforms[platform]
                      
                      return (
                        <div
                          key={platform}
                          className={`
                            relative border rounded-lg p-3 transition-all
                            ${isScheduled
                              ? getPlatformColor(platform)
                              : 'bg-gray-50 dark:bg-gray-800/50 border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                            }
                          `}
                        >
                          <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center gap-2">
                              {getPlatformIcon(platform)}
                              <span className="text-xs font-semibold capitalize">
                                {platform}
                              </span>
                            </div>
                            {isScheduled ? (
                              <CheckCircle2 className="w-4 h-4 text-green-600" />
                            ) : (
                              <XCircle className="w-4 h-4 text-gray-400" />
                            )}
                          </div>
                          
                          {!isScheduled && platform !== 'youtube' && (
                            <button
                              onClick={() => handleSchedule(video.video_id, platform, video.title)}
                              disabled={scheduleMutation.isPending}
                              className="w-full px-2.5 py-1.5 bg-primary text-primary-foreground text-xs font-medium rounded hover:bg-primary/90 transition-colors disabled:opacity-50 flex items-center justify-center gap-1 shadow-sm"
                            >
                              <Calendar className="w-3 h-3" />
                              Schedule
                            </button>
                          )}
                          
                          {isScheduled && (
                            <div className="text-xs font-medium text-center">
                              ✓ Scheduled
                            </div>
                          )}
                        </div>
                      )
                    })}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
