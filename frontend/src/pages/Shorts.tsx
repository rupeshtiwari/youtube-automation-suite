import { useQuery } from '@tanstack/react-query'
import api from '@/lib/api'
import { 
  Video, 
  Youtube, 
  Share2, 
  AlertTriangle,
  Rocket,
  PlayCircle
} from 'lucide-react'

interface Playlist {
  playlistId: string
  playlistTitle: string
  playlistUrl: string
  itemCount: number
  total_videos: number
  youtube_count: number
  other_platforms_count: number
  not_scheduled_count: number
  role?: string
  type?: string
  role_label?: string
  type_label?: string
}

interface ShortsData {
  playlists: Playlist[]
  total_videos: number
  total_youtube: number
  total_other_platforms: number
  total_not_scheduled: number
  weekly_schedule: string
  schedule_day: string
  available_roles: string[]
  available_types: string[]
  roles: Record<string, string>
  types: Record<string, string>
}

export default function Shorts() {
  const { data, isLoading, error } = useQuery<ShortsData>({
    queryKey: ['shorts'],
    queryFn: async () => {
      const response = await api.get('/shorts')
      return response.data
    },
  })

  const runAutoPilot = async () => {
    if (!confirm('Run Auto-Pilot? This will automatically select one video from each playlist and schedule them to all platforms.')) {
      return
    }
    
    try {
      const response = await api.post('/autopilot/run')
      if (response.data.success) {
        alert(`Auto-Pilot Complete! ${response.data.videos_selected} videos selected, ${response.data.posts_scheduled} posts scheduled.`)
        window.location.href = '/activity'
      } else {
        alert('Error: ' + response.data.error)
      }
    } catch (error: any) {
      alert('Error running auto-pilot: ' + (error.response?.data?.error || error.message))
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
        </div>
      </div>
    )
  }

  const playlists = data.playlists || []
  const totalVideos = data.total_videos || 0
  const totalYoutube = data.total_youtube || 0
  const totalOtherPlatforms = data.total_other_platforms || 0
  const totalNotScheduled = data.total_not_scheduled || 0

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold mb-2">Shorts</h1>
        <p className="text-muted-foreground">Manage and schedule your YouTube Shorts</p>
      </div>

      {/* Stats Bar */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <div className="bg-card border border-border rounded-lg p-4">
          <div className="text-2xl font-bold text-primary">{playlists.length}</div>
          <div className="text-sm text-muted-foreground uppercase tracking-wide">Playlists</div>
        </div>
        <div className="bg-card border border-border rounded-lg p-4">
          <div className="text-2xl font-bold text-primary">{totalVideos}</div>
          <div className="text-sm text-muted-foreground uppercase tracking-wide">Total Videos</div>
        </div>
        <div className="bg-card border border-border rounded-lg p-4">
          <div className="text-2xl font-bold text-red-600">{totalYoutube}</div>
          <div className="text-sm text-muted-foreground uppercase tracking-wide">On YouTube</div>
        </div>
        <div className="bg-card border border-border rounded-lg p-4">
          <div className="text-2xl font-bold text-green-600">{totalOtherPlatforms}</div>
          <div className="text-sm text-muted-foreground uppercase tracking-wide">Other Channels</div>
        </div>
        <div className="bg-card border border-border rounded-lg p-4">
          <div className="text-2xl font-bold text-orange-600">{totalNotScheduled}</div>
          <div className="text-sm text-muted-foreground uppercase tracking-wide">Not Scheduled</div>
        </div>
      </div>

      {/* Warning Banner */}
      {totalNotScheduled > 0 && (
        <div className="bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800 rounded-lg p-4">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-orange-600" />
            <p className="text-orange-800 dark:text-orange-200">
              <strong>{totalNotScheduled} videos</strong> not scheduled on other channels.{' '}
              <a 
                href="/content-preview" 
                onClick={(e) => {
                  e.preventDefault()
                  window.location.href = '/content-preview'
                }}
                className="text-primary hover:underline font-semibold"
              >
                Schedule now →
              </a>
            </p>
          </div>
        </div>
      )}

      {/* Auto-Pilot Card */}
      <div className="bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 border border-green-200 dark:border-green-800 rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Rocket className="w-5 h-5 text-green-600" />
            <h2 className="text-lg font-semibold text-green-900 dark:text-green-100">One-Click Automation</h2>
          </div>
          <div className="text-sm text-green-700 dark:text-green-300">
            Weekly: {data.schedule_day ? data.schedule_day.charAt(0).toUpperCase() + data.schedule_day.slice(1) : 'Wednesday'} {data.weekly_schedule || '23:00'}
          </div>
        </div>
        <p className="text-sm text-green-800 dark:text-green-200 mb-4">
          Selects 1 video per playlist → Generates posts → Schedules to LinkedIn, Facebook, Instagram
        </p>
        <button
          onClick={runAutoPilot}
          className="w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors flex items-center justify-center gap-2"
        >
          <Rocket className="w-4 h-4" />
          Run Auto-Pilot
        </button>
      </div>

      {/* Playlists List */}
      {playlists.length === 0 ? (
        <div className="bg-card border border-border rounded-lg p-12 text-center">
          <Video className="w-16 h-16 mx-auto mb-4 text-muted-foreground opacity-50" />
          <h3 className="text-lg font-semibold mb-2">No Shorts Playlists Found</h3>
          <p className="text-muted-foreground">
            No playlists with "short" in the name were found in your YouTube channel.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {playlists.map((playlist) => (
            <div
              key={playlist.playlistId}
              className="bg-card border border-border rounded-lg p-4 hover:shadow-md transition-all"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-3 mb-2">
                    <PlayCircle className="w-5 h-5 text-primary flex-shrink-0" />
                    <h3 className="font-semibold text-lg truncate">{playlist.playlistTitle}</h3>
                  </div>
                  
                  {playlist.role_label && (
                    <div className="flex items-center gap-2 mb-2 flex-wrap">
                      {playlist.role_label && (
                        <span className="px-2 py-1 text-xs bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 rounded">
                          {playlist.role_label}
                        </span>
                      )}
                      {playlist.type_label && (
                        <span className="px-2 py-1 text-xs bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded">
                          {playlist.type_label}
                        </span>
                      )}
                    </div>
                  )}

                  <div className="flex items-center gap-4 text-sm text-muted-foreground">
                    <span className="flex items-center gap-1">
                      <Video className="w-4 h-4" />
                      <strong>{playlist.total_videos || playlist.itemCount}</strong> videos
                    </span>
                    <span className="flex items-center gap-1 text-red-600">
                      <Youtube className="w-4 h-4" />
                      <strong>{playlist.youtube_count || 0}</strong> on YouTube
                    </span>
                    <span className="flex items-center gap-1 text-green-600">
                      <Share2 className="w-4 h-4" />
                      <strong>{playlist.other_platforms_count || 0}</strong> other channels
                    </span>
                    {playlist.not_scheduled_count > 0 && (
                      <span className="flex items-center gap-1 text-orange-600">
                        <AlertTriangle className="w-4 h-4" />
                        <strong>{playlist.not_scheduled_count}</strong> not scheduled
                      </span>
                    )}
                  </div>
                </div>
                
                <div className="flex items-center gap-2 flex-shrink-0">
                  <a
                    href="/content-preview"
                    onClick={(e) => {
                      e.preventDefault()
                      window.location.href = '/content-preview'
                    }}
                    className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors text-sm font-medium cursor-pointer"
                  >
                    Schedule
                  </a>
                  <a
                    href={playlist.playlistUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="p-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                  >
                    <Youtube className="w-4 h-4" />
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
