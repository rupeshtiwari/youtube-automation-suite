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
  Eye,
  X,
  Clock,
  CalendarCheck,
  Send,
  Loader2,
  User,
  Video as VideoIcon,
  Hash
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

interface PlatformStatus {
  configured: boolean
  authenticated: boolean
  status: string
  missing: string[]
}

interface StatusData {
  platforms: {
    linkedin?: PlatformStatus
    facebook?: PlatformStatus
    instagram?: PlatformStatus
  }
}

export default function ContentPreview() {
  const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>(['linkedin', 'facebook', 'instagram'])
  const [scheduleModalOpen, setScheduleModalOpen] = useState(false)
  const [selectedVideo, setSelectedVideo] = useState<Video | null>(null)
  const [scheduleDate, setScheduleDate] = useState('')
  const [scheduleTime, setScheduleTime] = useState('')
  const [modalPlatforms, setModalPlatforms] = useState<string[]>([])
  const [isScheduling, setIsScheduling] = useState(false)
  const [publishModalOpen, setPublishModalOpen] = useState(false)
  const [isPublishing, setIsPublishing] = useState(false)
  const [scheduleError, setScheduleError] = useState<string | null>(null)
  const [scheduleSuccess, setScheduleSuccess] = useState<string | null>(null)
  const [editablePostContent, setEditablePostContent] = useState('')

  const { data, isLoading, error, refetch } = useQuery<ContentPreviewData>({
    queryKey: ['content-preview'],
    queryFn: async () => {
      const response = await api.get('/content-preview/videos')
      return response.data
    },
  })

  // Get platform status to show warnings
  const { data: platformStatus } = useQuery<StatusData>({
    queryKey: ['platform-status'],
    queryFn: async () => {
      const response = await api.get('/status')
      return response.data
    },
  })

  // Get scheduled posts to find next available Wednesday
  const { data: scheduledPosts } = useQuery({
    queryKey: ['scheduled-posts'],
    queryFn: async () => {
      const response = await api.get('/calendar-data')
      return response.data
    },
  })

  const openScheduleModal = (video: Video) => {
    setSelectedVideo(video)
    // Get available platforms for this video
    const availablePlatforms = []
    if (video.social_posts.linkedin && (video.social_posts.linkedin.status === 'pending' || video.social_posts.linkedin.status === 'not_scheduled')) {
      availablePlatforms.push('linkedin')
    }
    if (video.social_posts.facebook && (video.social_posts.facebook.status === 'pending' || video.social_posts.facebook.status === 'not_scheduled')) {
      availablePlatforms.push('facebook')
    }
    if (video.social_posts.instagram && (video.social_posts.instagram.status === 'pending' || video.social_posts.instagram.status === 'not_scheduled')) {
      availablePlatforms.push('instagram')
    }
    
    setModalPlatforms(availablePlatforms.length > 0 ? availablePlatforms : ['linkedin', 'facebook', 'instagram'])
    
    // Set default post content
    setEditablePostContent(video.social_posts.linkedin?.post_content || video.social_posts.facebook?.post_content || video.social_posts.instagram?.post_content || video.title)
    
    // Smart scheduling: Find next available Wednesday at 11:00 PM
    const now = new Date()
    let nextWednesday = new Date(now)
    
    // Get all scheduled dates (Wednesday 11pm slots)
    const scheduledWednesdays = new Set<string>()
    if (scheduledPosts?.events) {
      scheduledPosts.events.forEach((event: any) => {
        if (event.datetime) {
          const eventDate = new Date(event.datetime)
          // Check if it's a Wednesday at 11pm (23:00)
          if (eventDate.getDay() === 3 && eventDate.getHours() === 23) {
            const dateKey = eventDate.toISOString().split('T')[0]
            scheduledWednesdays.add(dateKey)
          }
        }
      })
    }
    
    // Find next available Wednesday
    let attempts = 0
    while (attempts < 52) { // Max 52 weeks (1 year)
      const currentDay = nextWednesday.getDay()
      let daysUntilWednesday = 3 - currentDay // 3 is Wednesday
      
      if (daysUntilWednesday < 0) {
        daysUntilWednesday += 7
      } else if (daysUntilWednesday === 0) {
        // If today is Wednesday, check if it's before 11 PM
        if (nextWednesday.getHours() >= 23) {
          daysUntilWednesday = 7
        }
      }
      
      nextWednesday.setDate(nextWednesday.getDate() + daysUntilWednesday)
      nextWednesday.setHours(23, 0, 0, 0)
      
      const dateKey = nextWednesday.toISOString().split('T')[0]
      
      // If this Wednesday is not scheduled, use it
      if (!scheduledWednesdays.has(dateKey)) {
        break
      }
      
      // Otherwise, try next Wednesday
      nextWednesday.setDate(nextWednesday.getDate() + 7)
      attempts++
    }
    
    setScheduleDate(nextWednesday.toISOString().split('T')[0])
    setScheduleTime('23:00')
    
    setScheduleModalOpen(true)
  }

  const openPublishModal = (video: Video) => {
    setSelectedVideo(video)
    const availablePlatforms = []
    if (video.social_posts.linkedin && (video.social_posts.linkedin.status === 'pending' || video.social_posts.linkedin.status === 'not_scheduled')) {
      availablePlatforms.push('linkedin')
    }
    if (video.social_posts.facebook && (video.social_posts.facebook.status === 'pending' || video.social_posts.facebook.status === 'not_scheduled')) {
      availablePlatforms.push('facebook')
    }
    if (video.social_posts.instagram && (video.social_posts.instagram.status === 'pending' || video.social_posts.instagram.status === 'not_scheduled')) {
      availablePlatforms.push('instagram')
    }
    setModalPlatforms(availablePlatforms.length > 0 ? availablePlatforms : ['linkedin', 'facebook', 'instagram'])
    setPublishModalOpen(true)
  }

  const handleSchedule = async () => {
    // Clear previous messages
    setScheduleError(null)
    setScheduleSuccess(null)

    // Defensive validation
    if (!selectedVideo) {
      setScheduleError('❌ No video selected. Please try again.')
      return
    }

    // Filter out platforms that don't support scheduling
    const schedulablePlatforms = modalPlatforms.filter(p => p !== 'linkedin' && p !== 'instagram')
    
    if (schedulablePlatforms.length === 0 && modalPlatforms.length > 0) {
      setScheduleError('❌ LinkedIn and Instagram don\'t support scheduling via API. Please use "Publish Now" for these platforms, or select Facebook to schedule.')
      return
    }
    
    if (modalPlatforms.length === 0) {
      setScheduleError('❌ Please select at least one platform to schedule.')
      return
    }

    if (!scheduleDate || !scheduleTime) {
      setScheduleError('❌ Please select both date and time for scheduling.')
      return
    }

    // Validate post content
    const postContent = editablePostContent || selectedVideo.social_posts.linkedin?.post_content || selectedVideo.social_posts.facebook?.post_content || selectedVideo.social_posts.instagram?.post_content || selectedVideo.title || ''
    
    if (!postContent || postContent.trim().length === 0) {
      setScheduleError('❌ Post content cannot be empty. Please enter content to post.')
      return
    }

    if (postContent.trim().length < 10) {
      const proceed = confirm(`⚠️ Warning: Post content is very short (${postContent.trim().length} characters). Continue anyway?`)
      if (!proceed) return
    }

    // Validate date is in future
    const scheduleDateTime = `${scheduleDate}T${scheduleTime}:00`
    const scheduleDateObj = new Date(scheduleDateTime)
    const now = new Date()
    if (scheduleDateObj <= now) {
      setScheduleError('❌ Schedule date/time must be in the future. Please select a future date and time.')
      return
    }

    setIsScheduling(true)
    setScheduleError(null)

    // Schedule for each platform individually (API expects single platform)
    const results: { platform: string; success: boolean; error?: string }[] = []
    
    try {
      // Schedule each platform separately (only platforms that support scheduling)
      const platformsToSchedule = modalPlatforms.filter(p => p !== 'linkedin' && p !== 'instagram')
      
      if (platformsToSchedule.length === 0) {
        setScheduleError('❌ None of the selected platforms support scheduling. LinkedIn and Instagram require "Publish Now". Please select Facebook to schedule, or use "Publish Now" for all platforms.')
        setIsScheduling(false)
        return
      }
      
      for (const platform of platformsToSchedule) {
        try {
          const response = await api.post('/schedule-post', {
            video_id: selectedVideo.video_id,
            platform: platform, // Single platform, not array
            schedule_datetime: scheduleDateTime,
            post_content: postContent.trim()
          })

          if (response.data.success) {
            results.push({ platform, success: true })
          } else {
            results.push({ 
              platform, 
              success: false, 
              error: response.data.error || 'Unknown error' 
            })
          }
        } catch (err: any) {
          const errorMsg = err.response?.data?.error || err.message || 'Network error'
          results.push({ 
            platform, 
            success: false, 
            error: errorMsg 
          })
        }
      }

      // Show results
      const successful = results.filter(r => r.success)
      const failed = results.filter(r => !r.success)

      if (successful.length > 0 && failed.length === 0) {
        // All succeeded
        setScheduleSuccess(`✅ Successfully scheduled posts to ${successful.map(r => r.platform).join(', ')}!`)
        setTimeout(() => {
          setScheduleModalOpen(false)
          setSelectedVideo(null)
          setEditablePostContent('')
          setScheduleSuccess(null)
          refetch()
        }, 2000)
      } else if (successful.length > 0 && failed.length > 0) {
        // Partial success
        const failedPlatforms = failed.map(r => `${r.platform}: ${r.error}`).join(', ')
        setScheduleError(`⚠️ Partial success. Scheduled: ${successful.map(r => r.platform).join(', ')}. Failed: ${failedPlatforms}. Check Settings.`)
        refetch() // Refresh to show what was scheduled
      } else {
        // All failed - check for token expiration
        const hasTokenError = failed.some(r => r.error?.includes('TOKEN_EXPIRED') || r.error?.includes('TOKEN_INVALID') || r.error?.includes('token expired'))
        if (hasTokenError) {
          const tokenErrorPlatforms = failed.filter(r => r.error?.includes('TOKEN_EXPIRED') || r.error?.includes('TOKEN_INVALID') || r.error?.includes('token expired'))
          const platformNames = tokenErrorPlatforms.map(r => r.platform).join(', ')
          setScheduleError(`🔐 ${platformNames.charAt(0).toUpperCase() + platformNames.slice(1)} access token has expired. Please reconnect in Settings.`)
        } else {
          const errorDetails = failed.map(r => `${r.platform}: ${r.error}`).join('; ')
          setScheduleError(`❌ Failed to schedule: ${errorDetails}. Check platform credentials in Settings.`)
        }
      }
    } catch (err: any) {
      const errorMsg = err.response?.data?.error || err.message || 'Unknown error occurred'
      const hasTokenError = errorMsg.includes('TOKEN_EXPIRED') || errorMsg.includes('TOKEN_INVALID') || errorMsg.includes('token expired')
      if (hasTokenError) {
        setScheduleError(`🔐 Access token has expired. Please reconnect Facebook in Settings.`)
      } else {
        const errorDetails = err.response?.data?.missing_fields ? `Missing: ${err.response.data.missing_fields.join(', ')}. ` : ''
        setScheduleError(`❌ Error: ${errorDetails}${errorMsg}. Please check your settings and try again.`)
      }
    } finally {
      setIsScheduling(false)
    }
  }

  const handlePublishNow = async () => {
    if (!selectedVideo || modalPlatforms.length === 0) {
      return
    }

    setIsPublishing(true)

    try {
      const response = await api.post('/schedule-post', {
        video_id: selectedVideo.video_id,
        platforms: modalPlatforms,
        publish_now: true,
        post_content: editablePostContent || selectedVideo.social_posts.linkedin?.post_content || selectedVideo.title
      })

      if (response.data.success) {
        setPublishModalOpen(false)
        setSelectedVideo(null)
        refetch()
      } else {
        alert('Error: ' + (response.data.error || 'Failed to publish'))
      }
    } catch (err: any) {
      alert('Error publishing posts: ' + (err.response?.data?.error || err.message))
    } finally {
      setIsPublishing(false)
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

  const formatScheduleDate = (dateString: string | null) => {
    if (!dateString) return null
    try {
      const date = new Date(dateString)
      return {
        date: date.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' }),
        time: date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true })
      }
    } catch {
      return null
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

                {/* Video Metadata */}
                <div className="space-y-2 pt-2 border-t border-border">
                  {/* Tags */}
                  {video.tags && (
                    <div className="flex items-start gap-2">
                      <Hash className="w-3 h-3 mt-0.5 text-muted-foreground flex-shrink-0" />
                      <div className="flex flex-wrap gap-1">
                        {video.tags.split(',').slice(0, 3).map((tag, idx) => (
                          <span key={idx} className="text-xs px-1.5 py-0.5 bg-muted rounded text-muted-foreground">
                            {tag.trim()}
                          </span>
                        ))}
                        {video.tags.split(',').length > 3 && (
                          <span className="text-xs text-muted-foreground">+{video.tags.split(',').length - 3} more</span>
                        )}
                      </div>
                    </div>
                  )}
                  
                  {/* Role, Type, Playlist */}
                  <div className="flex flex-wrap gap-3 text-xs">
                    {video.role && (
                      <div className="flex items-center gap-1">
                        <User className="w-3 h-3 text-muted-foreground" />
                        <span className="text-muted-foreground">Role:</span>
                        <span className="font-medium">{video.role}</span>
                      </div>
                    )}
                    {video.video_type && (
                      <div className="flex items-center gap-1">
                        <VideoIcon className="w-3 h-3 text-muted-foreground" />
                        <span className="text-muted-foreground">Type:</span>
                        <span className="font-medium">{video.video_type}</span>
                      </div>
                    )}
                    {video.playlist_name && (
                      <div className="flex items-center gap-1">
                        <Youtube className="w-3 h-3 text-muted-foreground" />
                        <span className="text-muted-foreground">Shorts:</span>
                        <span className="font-medium">{video.playlist_name}</span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Social Media Status */}
                <div className="space-y-2 pt-2 border-t border-border">
                  <div className="text-xs font-medium text-muted-foreground">Platform Status:</div>
                  <div className="space-y-2">
                    {video.social_posts.linkedin && (
                      <div className="flex items-start justify-between gap-2">
                        <div className="flex items-center gap-1">
                          {getPlatformIcon('linkedin')}
                          {getStatusBadge(video.social_posts.linkedin.status)}
                        </div>
                        {video.social_posts.linkedin.status === 'scheduled' && video.social_posts.linkedin.schedule_date && (
                          <div className="text-xs text-muted-foreground text-right">
                            {(() => {
                              const formatted = formatScheduleDate(video.social_posts.linkedin.schedule_date)
                              return formatted ? (
                                <div className="flex items-center gap-1">
                                  <Clock className="w-3 h-3" />
                                  <span>{formatted.date} at {formatted.time}</span>
                                </div>
                              ) : null
                            })()}
                          </div>
                        )}
                      </div>
                    )}
                    {video.social_posts.facebook && (
                      <div className="flex items-start justify-between gap-2">
                        <div className="flex items-center gap-1">
                          {getPlatformIcon('facebook')}
                          {getStatusBadge(video.social_posts.facebook.status)}
                        </div>
                        {video.social_posts.facebook.status === 'scheduled' && video.social_posts.facebook.schedule_date && (
                          <div className="text-xs text-muted-foreground text-right">
                            {(() => {
                              const formatted = formatScheduleDate(video.social_posts.facebook.schedule_date)
                              return formatted ? (
                                <div className="flex items-center gap-1">
                                  <Clock className="w-3 h-3" />
                                  <span>{formatted.date} at {formatted.time}</span>
                                </div>
                              ) : null
                            })()}
                          </div>
                        )}
                      </div>
                    )}
                    {video.social_posts.instagram && (
                      <div className="flex items-start justify-between gap-2">
                        <div className="flex items-center gap-1">
                          {getPlatformIcon('instagram')}
                          {getStatusBadge(video.social_posts.instagram.status)}
                        </div>
                        {video.social_posts.instagram.status === 'scheduled' && video.social_posts.instagram.schedule_date && (
                          <div className="text-xs text-muted-foreground text-right">
                            {(() => {
                              const formatted = formatScheduleDate(video.social_posts.instagram.schedule_date)
                              return formatted ? (
                                <div className="flex items-center gap-1">
                                  <Clock className="w-3 h-3" />
                                  <span>{formatted.date} at {formatted.time}</span>
                                </div>
                              ) : null
                            })()}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>

                {/* Actions */}
                <div className="flex gap-2 pt-2">
                  <button
                    onClick={() => openScheduleModal(video)}
                    className="flex-1 px-3 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors text-sm font-medium flex items-center justify-center gap-2"
                  >
                    <Calendar className="w-4 h-4" />
                    Schedule
                  </button>
                  <button
                    onClick={() => openPublishModal(video)}
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

      {/* Schedule Modal - Buffer Style */}
      {scheduleModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
          <div className="bg-card border border-border rounded-xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col">
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-border">
              <div>
                <h2 className="text-xl font-bold">Schedule Post</h2>
                <p className="text-sm text-muted-foreground mt-1">Choose when to publish this content</p>
              </div>
              <button
                onClick={() => setScheduleModalOpen(false)}
                className="p-2 hover:bg-accent rounded-lg transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6">
              {/* Video Preview */}
              {selectedVideo && (
                <div className="bg-muted/50 rounded-lg p-4">
                  <div className="flex gap-4">
                    {selectedVideo.thumbnail && (
                      <img
                        src={selectedVideo.thumbnail}
                        alt={selectedVideo.title}
                        className="w-24 h-16 object-cover rounded"
                      />
                    )}
                    <div className="flex-1 min-w-0">
                      <h3 className="font-semibold text-sm line-clamp-2">{selectedVideo.title}</h3>
                      <p className="text-xs text-muted-foreground mt-1 line-clamp-2">{selectedVideo.description}</p>
                    </div>
                  </div>
                </div>
              )}

              {/* Platform Selection */}
              <div>
                <label className="text-sm font-semibold mb-3 block">Select Platforms</label>
                <div className="flex flex-col gap-3">
                  {['linkedin', 'facebook', 'instagram'].map((platform) => {
                    const isAvailable = selectedVideo && (
                      (platform === 'linkedin' && selectedVideo.social_posts.linkedin && (selectedVideo.social_posts.linkedin.status === 'pending' || selectedVideo.social_posts.linkedin.status === 'not_scheduled')) ||
                      (platform === 'facebook' && selectedVideo.social_posts.facebook && (selectedVideo.social_posts.facebook.status === 'pending' || selectedVideo.social_posts.facebook.status === 'not_scheduled')) ||
                      (platform === 'instagram' && selectedVideo.social_posts.instagram && (selectedVideo.social_posts.instagram.status === 'pending' || selectedVideo.social_posts.instagram.status === 'not_scheduled'))
                    )
                    const isSelected = modalPlatforms.includes(platform)
                    const platformStatusData = platformStatus?.platforms?.[platform as keyof typeof platformStatus.platforms]
                    const isNotConfigured = !platformStatusData || platformStatusData.status === 'needs_setup' || (!platformStatusData.configured && !platformStatusData.authenticated)
                    
                    // LinkedIn and Instagram don't support scheduling via API
                    const schedulingNotSupported = platform === 'linkedin' || platform === 'instagram'
                    
                    return (
                      <div key={platform} className="space-y-1">
                        <label
                          className={cn(
                            "flex items-center gap-2 px-4 py-3 rounded-lg border cursor-pointer transition-all",
                            (!isAvailable || schedulingNotSupported) && "opacity-50 cursor-not-allowed",
                            isNotConfigured && "border-red-300 dark:border-red-700 bg-red-50 dark:bg-red-900/20",
                            schedulingNotSupported && "border-yellow-300 dark:border-yellow-700 bg-yellow-50 dark:bg-yellow-900/20",
                            isSelected && isAvailable && !isNotConfigured && !schedulingNotSupported
                              ? "bg-primary text-primary-foreground border-primary shadow-md"
                              : isAvailable && !isNotConfigured && !schedulingNotSupported
                              ? "bg-background border-border hover:bg-accent hover:border-primary/50"
                              : !isNotConfigured && "bg-muted border-border"
                          )}
                        >
                          <input
                            type="checkbox"
                            checked={isSelected}
                            disabled={!isAvailable || isNotConfigured || schedulingNotSupported}
                            onChange={(e) => {
                              if (e.target.checked) {
                                setModalPlatforms([...modalPlatforms, platform])
                              } else {
                                setModalPlatforms(modalPlatforms.filter(p => p !== platform))
                              }
                            }}
                            className="sr-only"
                          />
                          {getPlatformIcon(platform)}
                          <span className="capitalize font-medium">{platform}</span>
                          {!isAvailable && !isNotConfigured && !schedulingNotSupported && (
                            <span className="text-xs opacity-75">(Already scheduled)</span>
                          )}
                          {schedulingNotSupported && (
                            <span className="text-xs text-yellow-700 dark:text-yellow-300 ml-auto">(Use Publish Now)</span>
                          )}
                          {isNotConfigured && (
                            <XCircle className="w-4 h-4 text-red-600 dark:text-red-400 ml-auto" />
                          )}
                        </label>
                        {schedulingNotSupported && (
                          <div className="flex items-start gap-2 px-4 py-2 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
                            <AlertCircle className="w-4 h-4 text-yellow-600 dark:text-yellow-400 flex-shrink-0 mt-0.5" />
                            <div className="flex-1">
                              <p className="text-xs font-semibold text-yellow-800 dark:text-yellow-200">
                                {platform === 'linkedin' 
                                  ? 'LinkedIn API doesn\'t support scheduled posts'
                                  : 'Instagram requires native video upload for scheduling'}
                              </p>
                              <p className="text-xs text-yellow-700 dark:text-yellow-300 mt-1">
                                {platform === 'linkedin'
                                  ? 'Please use "Publish Now" button to post immediately to LinkedIn.'
                                  : 'Please use "Publish Now" or Facebook Business Suite to post to Instagram.'}
                              </p>
                            </div>
                          </div>
                        )}
                        {isNotConfigured && (
                          <div className="flex items-start gap-2 px-4 py-2 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                            <AlertCircle className="w-4 h-4 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
                            <div className="flex-1">
                              <p className="text-xs font-semibold text-red-800 dark:text-red-200">
                                {platform.charAt(0).toUpperCase() + platform.slice(1)} is not configured
                              </p>
                              <p className="text-xs text-red-700 dark:text-red-300 mt-1">
                                {platformStatusData?.missing && platformStatusData.missing.length > 0
                                  ? `Missing: ${platformStatusData.missing.join(', ')}`
                                  : 'Please configure this platform in Settings before scheduling posts.'}
                              </p>
                              <a
                                href="/settings"
                                onClick={(e) => {
                                  e.preventDefault()
                                  window.location.href = '/settings'
                                }}
                                className="text-xs text-red-600 dark:text-red-400 hover:underline mt-1 inline-block font-medium cursor-pointer"
                              >
                                Go to Settings →
                              </a>
                            </div>
                          </div>
                        )}
                      </div>
                    )
                  })}
                </div>
              </div>

              {/* Date & Time Selection */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-semibold mb-2 block">Date</label>
                  <div className="relative">
                    <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                    <input
                      type="date"
                      value={scheduleDate}
                      onChange={(e) => setScheduleDate(e.target.value)}
                      min={new Date().toISOString().split('T')[0]}
                      className="w-full pl-10 pr-4 py-2 border border-border rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                    />
                  </div>
                </div>
                <div>
                  <label className="text-sm font-semibold mb-2 block">Time</label>
                  <div className="relative">
                    <Clock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                    <input
                      type="time"
                      value={scheduleTime}
                      onChange={(e) => setScheduleTime(e.target.value)}
                      className="w-full pl-10 pr-4 py-2 border border-border rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                    />
                  </div>
                </div>
              </div>

              {/* Editable Post Content */}
              <div>
                <label className="text-sm font-semibold mb-2 block">
                  Post Content <span className="text-muted-foreground text-xs font-normal">(Editable)</span>
                </label>
                <textarea
                  value={editablePostContent}
                  onChange={(e) => setEditablePostContent(e.target.value)}
                  rows={6}
                  className="w-full px-4 py-3 border border-border rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent resize-y text-sm font-mono"
                  placeholder="Enter post content for social media platforms..."
                />
                <p className="text-xs text-muted-foreground mt-1.5">
                  This content will be posted to all selected platforms. You can edit it before scheduling.
                </p>
              </div>
            </div>

            {/* Error/Success Messages */}
            {scheduleError && (
              <div className="mx-6 mb-4 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                <div className="flex items-start gap-2">
                  <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
                  <div className="flex-1">
                    <p className="text-sm text-red-800 dark:text-red-200">{scheduleError}</p>
                    {(scheduleError.includes('token expired') || scheduleError.includes('TOKEN_EXPIRED') || scheduleError.includes('TOKEN_INVALID')) && (
                      <a
                        href="/config#social-media-connections"
                        className="mt-2 inline-block text-sm font-medium text-red-700 dark:text-red-300 hover:text-red-900 dark:hover:text-red-100 underline"
                      >
                        Go to Settings to reconnect →
                      </a>
                    )}
                  </div>
                  <button
                    onClick={() => setScheduleError(null)}
                    className="text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-200"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              </div>
            )}
            {scheduleSuccess && (
              <div className="mx-6 mb-4 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
                <div className="flex items-start gap-2">
                  <CheckCircle2 className="w-5 h-5 text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5" />
                  <p className="text-sm text-green-800 dark:text-green-200 flex-1">{scheduleSuccess}</p>
                </div>
              </div>
            )}

            {/* Footer */}
            <div className="flex items-center justify-end gap-3 p-6 border-t border-border bg-muted/30">
              <button
                onClick={() => {
                  setScheduleModalOpen(false)
                  setScheduleError(null)
                  setScheduleSuccess(null)
                }}
                className="px-4 py-2 text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleSchedule}
                disabled={isScheduling || modalPlatforms.length === 0 || !scheduleDate || !scheduleTime || !editablePostContent.trim()}
                className="px-6 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors text-sm font-medium flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isScheduling ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Scheduling...
                  </>
                ) : (
                  <>
                    <CalendarCheck className="w-4 h-4" />
                    Schedule Post
                  </>
                )}
              </button>
              {modalPlatforms.length > 0 && modalPlatforms.some(p => {
                const status = platformStatus?.platforms?.[p as keyof typeof platformStatus.platforms]
                return !status || status.status === 'needs_setup' || (!status.configured && !status.authenticated)
              }) && (
                <div className="flex items-start gap-2 px-4 py-2 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg mt-2">
                  <AlertCircle className="w-4 h-4 text-yellow-600 dark:text-yellow-400 flex-shrink-0 mt-0.5" />
                  <p className="text-xs text-yellow-800 dark:text-yellow-200">
                    Some selected platforms are not configured. Please configure them in Settings before scheduling.
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Publish Now Modal - Buffer Style */}
      {publishModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
          <div className="bg-card border border-border rounded-xl shadow-2xl w-full max-w-lg">
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-border">
              <div>
                <h2 className="text-xl font-bold">Publish Now</h2>
                <p className="text-sm text-muted-foreground mt-1">Publish this content immediately</p>
              </div>
              <button
                onClick={() => setPublishModalOpen(false)}
                className="p-2 hover:bg-accent rounded-lg transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Content */}
            <div className="p-6 space-y-4">
              {/* Video Preview */}
              {selectedVideo && (
                <div className="bg-muted/50 rounded-lg p-4">
                  <div className="flex gap-4">
                    {selectedVideo.thumbnail && (
                      <img
                        src={selectedVideo.thumbnail}
                        alt={selectedVideo.title}
                        className="w-20 h-14 object-cover rounded"
                      />
                    )}
                    <div className="flex-1 min-w-0">
                      <h3 className="font-semibold text-sm line-clamp-2">{selectedVideo.title}</h3>
                    </div>
                  </div>
                </div>
              )}

              {/* Platform Selection */}
              <div>
                <label className="text-sm font-semibold mb-3 block">Select Platforms</label>
                <div className="flex flex-col gap-3">
                  {['linkedin', 'facebook', 'instagram'].map((platform) => {
                    const isAvailable = selectedVideo && (
                      (platform === 'linkedin' && selectedVideo.social_posts.linkedin && (selectedVideo.social_posts.linkedin.status === 'pending' || selectedVideo.social_posts.linkedin.status === 'not_scheduled')) ||
                      (platform === 'facebook' && selectedVideo.social_posts.facebook && (selectedVideo.social_posts.facebook.status === 'pending' || selectedVideo.social_posts.facebook.status === 'not_scheduled')) ||
                      (platform === 'instagram' && selectedVideo.social_posts.instagram && (selectedVideo.social_posts.instagram.status === 'pending' || selectedVideo.social_posts.instagram.status === 'not_scheduled'))
                    )
                    const isSelected = modalPlatforms.includes(platform)
                    const platformStatusData = platformStatus?.platforms?.[platform as keyof typeof platformStatus.platforms]
                    const isNotConfigured = !platformStatusData || platformStatusData.status === 'needs_setup' || (!platformStatusData.configured && !platformStatusData.authenticated)
                    
                    return (
                      <div key={platform} className="space-y-1">
                        <label
                          className={cn(
                            "flex items-center gap-2 px-4 py-3 rounded-lg border cursor-pointer transition-all",
                            !isAvailable && "opacity-50 cursor-not-allowed",
                            isNotConfigured && "border-red-300 dark:border-red-700 bg-red-50 dark:bg-red-900/20",
                            isSelected && isAvailable && !isNotConfigured
                              ? "bg-primary text-primary-foreground border-primary shadow-md"
                              : isAvailable && !isNotConfigured
                              ? "bg-background border-border hover:bg-accent hover:border-primary/50"
                              : !isNotConfigured && "bg-muted border-border"
                          )}
                        >
                          <input
                            type="checkbox"
                            checked={isSelected}
                            disabled={!isAvailable || isNotConfigured}
                            onChange={(e) => {
                              if (e.target.checked) {
                                setModalPlatforms([...modalPlatforms, platform])
                              } else {
                                setModalPlatforms(modalPlatforms.filter(p => p !== platform))
                              }
                            }}
                            className="sr-only"
                          />
                          {getPlatformIcon(platform)}
                          <span className="capitalize font-medium">{platform}</span>
                          {isNotConfigured && (
                            <XCircle className="w-4 h-4 text-red-600 dark:text-red-400 ml-auto" />
                          )}
                        </label>
                        {isNotConfigured && (
                          <div className="flex items-start gap-2 px-4 py-2 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                            <AlertCircle className="w-4 h-4 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
                            <div className="flex-1">
                              <p className="text-xs font-semibold text-red-800 dark:text-red-200">
                                {platform.charAt(0).toUpperCase() + platform.slice(1)} is not configured
                              </p>
                              <p className="text-xs text-red-700 dark:text-red-300 mt-1">
                                {platformStatusData?.missing && platformStatusData.missing.length > 0
                                  ? `Missing: ${platformStatusData.missing.join(', ')}`
                                  : 'Please configure this platform in Settings before publishing.'}
                              </p>
                              <a
                                href="/settings"
                                onClick={(e) => {
                                  e.preventDefault()
                                  window.location.href = '/settings'
                                }}
                                className="text-xs text-red-600 dark:text-red-400 hover:underline mt-1 inline-block font-medium cursor-pointer"
                              >
                                Go to Settings →
                              </a>
                            </div>
                          </div>
                        )}
                      </div>
                    )
                  })}
                </div>
              </div>
            </div>

            {/* Footer */}
            <div className="flex items-center justify-end gap-3 p-6 border-t border-border bg-muted/30">
              <button
                onClick={() => setPublishModalOpen(false)}
                className="px-4 py-2 text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handlePublishNow}
                disabled={isPublishing || modalPlatforms.length === 0}
                className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm font-medium flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isPublishing ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Publishing...
                  </>
                ) : (
                  <>
                    <Send className="w-4 h-4" />
                    Publish Now
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
