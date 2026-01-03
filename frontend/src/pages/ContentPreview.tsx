import { useQuery } from '@tanstack/react-query'
import api from '@/lib/api'
import { 
  Youtube,
  Linkedin,
  Facebook,
  Instagram,
  Calendar,
  CheckCircle2,
  XCircle,
  AlertCircle,
  Play,
  Eye
} from 'lucide-react'
import { useState } from 'react'
import { cn } from '@/lib/utils'

interface SocialPost {
  platform: string
  post_content: string
  schedule_date: string | null
  status: string
}

interface Video {
  video_id: string
  title: string
  description: string
  video_url: string
  thumbnail: string
  published_at: string
  playlist_name: string
  role: string
  video_type: string
  tags: string
  social_posts: {
    linkedin?: SocialPost
    facebook?: SocialPost
    instagram?: SocialPost
  }
}

interface ContentPreviewData {
  videos: Video[]
}

export default function ContentPreview() {
  const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>(['linkedin', 'facebook', 'instagram'])

  const { data, isLoading, error, refetch } = useQuery<ContentPreviewData>({
    queryKey: ['content-preview'],
    queryFn: async () => {
      const response = await api.get('/content-preview/videos')
      return response.data
    },
  })

  const handleSchedule = async (video: Video) => {
    if (!selectedPlatforms.length) {
      alert('Please select at least one platform')
      return
    }

    const scheduleDate = prompt('Enter schedule date and time (YYYY-MM-DD HH:MM):')
    if (!scheduleDate) return

    try {
      const response = await api.post('/schedule-post', {
        video_id: video.video_id,
        platforms: selectedPlatforms,
        schedule_datetime: scheduleDate,
        post_content: video.social_posts.linkedin?.post_content || video.title
      })

      if (response.data.success) {
        alert('Posts scheduled successfully!')
        refetch()
      } else {
        alert('Error: ' + (response.data.error || 'Failed to schedule'))
      }
    } catch (err: any) {
      alert('Error scheduling posts: ' + (err.response?.data?.error || err.message))
    }
  }

  const handlePublishNow = async (video: Video) => {
    if (!selectedPlatforms.length) {
      alert('Please select at least one platform')
      return
    }

    if (!confirm(`Publish to ${selectedPlatforms.join(', ')} now?`)) return

    try {
      const response = await api.post('/schedule-post', {
        video_id: video.video_id,
        platforms: selectedPlatforms,
        publish_now: true,
        post_content: video.social_posts.linkedin?.post_content || video.title
      })

      if (response.data.success) {
        alert('Posts published successfully!')
        refetch()
      } else {
        alert('Error: ' + (response.data.error || 'Failed to publish'))
      }
    } catch (err: any) {
      alert('Error publishing posts: ' + (err.response?.data?.error || err.message))
    }
  }

  const getPlatformIcon = (platform: string) => {
    const iconClass = "w-4 h-4"
    switch (platform.toLowerCase()) {
      case 'youtube':
        return <Youtube className={iconClass} />
      case 'linkedin':
        return <Linkedin className={iconClass} />
      case 'facebook':
        return <Facebook className={iconClass} />
      case 'instagram':
        return <Instagram className={iconClass} />
      default:
        return null
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'published':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-1 text-xs font-medium bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 rounded-full">
            <CheckCircle2 className="w-3 h-3" />
            Published
          </span>
        )
      case 'scheduled':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-1 text-xs font-medium bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded-full">
            <Calendar className="w-3 h-3" />
            Scheduled
          </span>
        )
      case 'pending':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-1 text-xs font-medium bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300 rounded-full">
            <AlertCircle className="w-3 h-3" />
            Pending
          </span>
        )
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2 py-1 text-xs font-medium bg-gray-100 dark:bg-gray-900/30 text-gray-700 dark:text-gray-300 rounded-full">
            <XCircle className="w-3 h-3" />
            Not Scheduled
          </span>
        )
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
            Error loading content: {error ? (error as any).message : 'No data available'}
          </p>
        </div>
      </div>
    )
  }

  const videos = data.videos || []

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold mb-2">Preview & Schedule</h1>
        <p className="text-muted-foreground">
          Preview videos and schedule posts to social media platforms
        </p>
      </div>

      {/* Platform Selection */}
      <div className="bg-card border border-border rounded-lg p-4">
        <h3 className="text-sm font-semibold mb-3">Select Platforms</h3>
        <div className="flex gap-3">
          {['linkedin', 'facebook', 'instagram'].map((platform) => (
            <label
              key={platform}
              className={cn(
                "flex items-center gap-2 px-4 py-2 rounded-lg border cursor-pointer transition-colors",
                selectedPlatforms.includes(platform)
                  ? "bg-primary text-primary-foreground border-primary"
                  : "bg-background border-border hover:bg-accent"
              )}
            >
              <input
                type="checkbox"
                checked={selectedPlatforms.includes(platform)}
                onChange={(e) => {
                  if (e.target.checked) {
                    setSelectedPlatforms([...selectedPlatforms, platform])
                  } else {
                    setSelectedPlatforms(selectedPlatforms.filter(p => p !== platform))
                  }
                }}
                className="sr-only"
              />
              {getPlatformIcon(platform)}
              <span className="capitalize">{platform}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Videos Grid */}
      {videos.length === 0 ? (
        <div className="bg-card border border-border rounded-lg p-12 text-center">
          <Eye className="w-16 h-16 mx-auto mb-4 text-muted-foreground opacity-50" />
          <h3 className="text-lg font-semibold mb-2">No Videos Found</h3>
          <p className="text-muted-foreground">
            No videos available for preview and scheduling.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {videos.map((video) => (
            <div
              key={video.video_id}
              className="bg-card border border-border rounded-lg overflow-hidden hover:shadow-lg transition-shadow"
            >
              {/* Thumbnail */}
              <div className="relative aspect-video bg-muted">
                {video.thumbnail ? (
                  <img
                    src={video.thumbnail}
                    alt={video.title}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center">
                    <Youtube className="w-12 h-12 text-muted-foreground" />
                  </div>
                )}
                <a
                  href={video.video_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="absolute inset-0 flex items-center justify-center bg-black/50 opacity-0 hover:opacity-100 transition-opacity"
                >
                  <Play className="w-12 h-12 text-white" />
                </a>
              </div>

              {/* Content */}
              <div className="p-4 space-y-3">
                <div>
                  <h3 className="font-semibold line-clamp-2 mb-1">{video.title}</h3>
                  <p className="text-xs text-muted-foreground line-clamp-2">
                    {video.description}
                  </p>
                </div>

                {/* Playlist Info */}
                {video.playlist_name && (
                  <div className="text-xs text-muted-foreground">
                    📁 {video.playlist_name}
                  </div>
                )}

                {/* Social Media Status */}
                <div className="space-y-2">
                  <div className="text-xs font-medium text-muted-foreground">Platform Status:</div>
                  <div className="flex flex-wrap gap-2">
                    {video.social_posts.linkedin && (
                      <div className="flex items-center gap-1">
                        {getPlatformIcon('linkedin')}
                        {getStatusBadge(video.social_posts.linkedin.status)}
                      </div>
                    )}
                    {video.social_posts.facebook && (
                      <div className="flex items-center gap-1">
                        {getPlatformIcon('facebook')}
                        {getStatusBadge(video.social_posts.facebook.status)}
                      </div>
                    )}
                    {video.social_posts.instagram && (
                      <div className="flex items-center gap-1">
                        {getPlatformIcon('instagram')}
                        {getStatusBadge(video.social_posts.instagram.status)}
                      </div>
                    )}
                  </div>
                </div>

                {/* Actions */}
                <div className="flex gap-2 pt-2">
                  <button
                    onClick={() => handleSchedule(video)}
                    className="flex-1 px-3 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors text-sm font-medium flex items-center justify-center gap-2"
                  >
                    <Calendar className="w-4 h-4" />
                    Schedule
                  </button>
                  <button
                    onClick={() => handlePublishNow(video)}
                    className="flex-1 px-3 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm font-medium flex items-center justify-center gap-2"
                  >
                    <CheckCircle2 className="w-4 h-4" />
                    Publish Now
                  </button>
                </div>

                {/* View Post Content */}
                {video.social_posts.linkedin?.post_content && (
                  <details className="text-xs">
                    <summary className="cursor-pointer text-muted-foreground hover:text-foreground">
                      View Post Content
                    </summary>
                    <div className="mt-2 p-2 bg-muted rounded text-xs whitespace-pre-wrap">
                      {video.social_posts.linkedin.post_content}
                    </div>
                  </details>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Stats */}
      {videos.length > 0 && (
        <div className="bg-card border border-border rounded-lg p-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <div className="text-2xl font-bold">{videos.length}</div>
              <div className="text-sm text-muted-foreground">Total Videos</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-green-600">
                {videos.filter(v => 
                  v.social_posts.linkedin?.status === 'published' ||
                  v.social_posts.facebook?.status === 'published' ||
                  v.social_posts.instagram?.status === 'published'
                ).length}
              </div>
              <div className="text-sm text-muted-foreground">Published</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-blue-600">
                {videos.filter(v => 
                  v.social_posts.linkedin?.status === 'scheduled' ||
                  v.social_posts.facebook?.status === 'scheduled' ||
                  v.social_posts.instagram?.status === 'scheduled'
                ).length}
              </div>
              <div className="text-sm text-muted-foreground">Scheduled</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-yellow-600">
                {videos.filter(v => 
                  (!v.social_posts.linkedin || v.social_posts.linkedin.status === 'pending' || v.social_posts.linkedin.status === 'not_scheduled') &&
                  (!v.social_posts.facebook || v.social_posts.facebook.status === 'pending' || v.social_posts.facebook.status === 'not_scheduled') &&
                  (!v.social_posts.instagram || v.social_posts.instagram.status === 'pending' || v.social_posts.instagram.status === 'not_scheduled')
                ).length}
              </div>
              <div className="text-sm text-muted-foreground">Pending</div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
