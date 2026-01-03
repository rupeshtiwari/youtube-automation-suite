import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import api from '@/lib/api'
import { Video, Youtube, Share2, AlertTriangle, Rocket, Filter, X } from 'lucide-react'
import { Link } from 'react-router-dom'

interface Playlist {
  playlistId: string
  playlistTitle: string
  total_videos: number
  youtube_count: number
  other_platforms_count: number
  not_scheduled_count: number
  playlistUrl: string
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
  available_roles?: string[]
  available_types?: string[]
  roles?: Record<string, string>
  types?: Record<string, string>
}

export default function Shorts() {
  const [roleFilter, setRoleFilter] = useState<string>('')
  const [typeFilter, setTypeFilter] = useState<string>('')

  const { data, isLoading } = useQuery<ShortsData>({
    queryKey: ['shorts', roleFilter, typeFilter],
    queryFn: async () => {
      const params = new URLSearchParams()
      if (roleFilter) params.append('role', roleFilter)
      if (typeFilter) params.append('type', typeFilter)
      const response = await api.get(`/shorts?${params.toString()}`)
      return response.data
    },
  })

  const handleAutoPilot = async () => {
    if (!confirm('Run Auto-Pilot? This will automatically select one video from each playlist and schedule them to all platforms.')) {
      return
    }
    
    try {
      const response = await api.post('/autopilot/run')
      alert(`Success! ${response.data.videos_selected} videos selected, ${response.data.posts_scheduled} posts scheduled.`)
      window.location.href = '/activity'
    } catch (error: any) {
      alert('Error: ' + (error.response?.data?.error || error.message))
    }
  }

  const clearFilters = () => {
    setRoleFilter('')
    setTypeFilter('')
  }

  const hasActiveFilters = roleFilter || typeFilter

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    )
  }

  if (!data) return null

  return (
    <div className="space-y-6">
      {/* Filters */}
      <div className="bg-card border border-border rounded-lg p-4">
        <div className="flex items-center gap-4 flex-wrap">
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-muted-foreground" />
            <span className="text-sm font-medium">Filters:</span>
          </div>
          
          {/* Role Filter */}
          <select
            value={roleFilter}
            onChange={(e) => setRoleFilter(e.target.value)}
            className="px-3 py-1.5 text-sm border border-border rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-primary"
          >
            <option value="">All Roles</option>
            {data.available_roles?.map((role) => (
              <option key={role} value={role}>
                {data.roles?.[role] || role}
              </option>
            ))}
          </select>

          {/* Type Filter */}
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="px-3 py-1.5 text-sm border border-border rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-primary"
          >
            <option value="">All Types</option>
            {data.available_types?.map((type) => (
              <option key={type} value={type}>
                {data.types?.[type] || type}
              </option>
            ))}
          </select>

          {hasActiveFilters && (
            <button
              onClick={clearFilters}
              className="px-3 py-1.5 text-sm text-muted-foreground hover:text-foreground flex items-center gap-1"
            >
              <X className="w-3 h-3" />
              Clear
            </button>
          )}

          {hasActiveFilters && (
            <span className="text-xs text-muted-foreground ml-auto">
              Showing {data.playlists?.length || 0} playlist{data.playlists?.length !== 1 ? 's' : ''}
            </span>
          )}
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <div className="bg-card border border-border rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-primary">{data.playlists?.length || 0}</div>
          <div className="text-xs text-muted-foreground uppercase tracking-wide mt-1">Playlists</div>
        </div>
        <div className="bg-card border border-border rounded-lg p-4 text-center">
          <div className="text-2xl font-bold">{data.total_videos || 0}</div>
          <div className="text-xs text-muted-foreground uppercase tracking-wide mt-1">Total Videos</div>
        </div>
        <div className="bg-card border border-border rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-red-600">{data.total_youtube || 0}</div>
          <div className="text-xs text-muted-foreground uppercase tracking-wide mt-1">On YouTube</div>
        </div>
        <div className="bg-card border border-border rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-green-600">{data.total_other_platforms || 0}</div>
          <div className="text-xs text-muted-foreground uppercase tracking-wide mt-1">Other Channels</div>
        </div>
        <div className="bg-card border border-border rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-yellow-600">{data.total_not_scheduled || 0}</div>
          <div className="text-xs text-muted-foreground uppercase tracking-wide mt-1">Not Scheduled</div>
        </div>
      </div>

      {/* Warning */}
      {data.total_not_scheduled > 0 && (
        <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
          <div className="flex items-center gap-2 text-yellow-800 dark:text-yellow-200">
            <AlertTriangle className="w-5 h-5" />
            <span className="font-medium">
              {data.total_not_scheduled} videos not scheduled on other channels.{' '}
              <Link to="/content-preview" className="underline font-semibold hover:text-primary">Schedule now →</Link>
            </span>
          </div>
        </div>
      )}

      {/* Auto-Pilot Card */}
      <div className="bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2 text-green-700 dark:text-green-300 font-semibold">
            <Rocket className="w-5 h-5" />
            One-Click Automation
          </div>
          <span className="text-xs text-muted-foreground">
            Weekly: {data.schedule_day} {data.weekly_schedule}
          </span>
        </div>
        <p className="text-sm text-muted-foreground mb-3">
          Selects 1 video per playlist → Generates posts → Schedules to LinkedIn, Facebook, Instagram
        </p>
        <button
          onClick={handleAutoPilot}
          className="w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-2.5 px-4 rounded-lg transition-colors flex items-center justify-center gap-2"
        >
          <Rocket className="w-4 h-4" />
          Run Auto-Pilot
        </button>
      </div>

      {/* Playlists - Now at top after filters */}
      <div className="space-y-2">
        {data.playlists && data.playlists.length > 0 ? (
          data.playlists.map((playlist) => (
            <div
              key={playlist.playlistId}
              className="bg-card border border-border rounded-lg p-4 hover:shadow-md transition-shadow"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3 flex-1">
                  <Video className="w-5 h-5 text-primary" />
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <h3 className="font-semibold text-sm">{playlist.playlistTitle}</h3>
                      {playlist.role_label && (
                        <span className="px-2 py-0.5 text-xs bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded">
                          {playlist.role_label}
                        </span>
                      )}
                      {playlist.type_label && (
                        <span className="px-2 py-0.5 text-xs bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 rounded">
                          {playlist.type_label}
                        </span>
                      )}
                    </div>
                    <div className="flex items-center gap-4 mt-1 text-xs text-muted-foreground">
                      <span className="flex items-center gap-1">
                        <Video className="w-3 h-3" />
                        <strong className="text-foreground">{playlist.total_videos}</strong>
                      </span>
                      <span className="flex items-center gap-1 text-red-600">
                        <Youtube className="w-3 h-3" />
                        <strong>{playlist.youtube_count}</strong>
                      </span>
                      <span className="flex items-center gap-1 text-green-600">
                        <Share2 className="w-3 h-3" />
                        <strong>{playlist.other_platforms_count}</strong>
                      </span>
                      {playlist.not_scheduled_count > 0 && (
                        <span className="flex items-center gap-1 text-yellow-600">
                          <AlertTriangle className="w-3 h-3" />
                          <strong>{playlist.not_scheduled_count}</strong>
                        </span>
                      )}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <a
                    href="/content-preview"
                    className="px-3 py-1.5 bg-primary text-primary-foreground text-xs font-medium rounded-md hover:bg-primary/90 transition-colors"
                  >
                    Schedule
                  </a>
                  <a
                    href={playlist.playlistUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="px-3 py-1.5 bg-red-600 text-white text-xs font-medium rounded-md hover:bg-red-700 transition-colors"
                  >
                    <Youtube className="w-3 h-3 inline" />
                  </a>
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="bg-card border border-border rounded-lg p-8 text-center">
            <p className="text-muted-foreground">
              {hasActiveFilters 
                ? 'No playlists match the selected filters.' 
                : 'No Shorts playlists found.'}
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
