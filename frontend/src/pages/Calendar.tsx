import { useQuery } from '@tanstack/react-query'
import api from '@/lib/api'
import { 
  Calendar as CalendarIcon,
  Clock,
  Youtube,
  Linkedin,
  Facebook,
  Instagram,
  ChevronLeft,
  ChevronRight,
  AlertCircle
} from 'lucide-react'
import { useState } from 'react'

interface CalendarEvent {
  date: string
  time: string
  datetime: string
  platform: string
  video_title: string
  video_id: string
  youtube_url: string
  status: string
  post_content: string
  playlist_name?: string
  video_type?: string
  privacy_status?: string
  platforms?: {
    youtube: boolean
    facebook: boolean
    instagram: boolean
    linkedin: boolean
    video_title: string
    playlist_name: string
  }
  missing_platforms?: string[]
}

interface CalendarData {
  events: CalendarEvent[]
  optimal_times?: Record<string, any>
  recommendations?: any[]
  video_platforms?: Record<string, any>
}

export default function Calendar() {
  const [currentDate, setCurrentDate] = useState(new Date())
  const [viewMode, setViewMode] = useState<'month' | 'week' | 'day'>('month')

  const { data, isLoading, error } = useQuery<CalendarData>({
    queryKey: ['calendar-data'],
    queryFn: async () => {
      const response = await api.get('/calendar-data')
      return response.data
    },
  })

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
        return <CalendarIcon className={iconClass} />
    }
  }

  const getPlatformColor = (platform: string) => {
    switch (platform.toLowerCase()) {
      case 'youtube':
        return 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 border-red-300'
      case 'linkedin':
        return 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 border-blue-300'
      case 'facebook':
        return 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 border-blue-300'
      case 'instagram':
        return 'bg-pink-100 dark:bg-pink-900/30 text-pink-700 dark:text-pink-300 border-pink-300'
      default:
        return 'bg-gray-100 dark:bg-gray-900/30 text-gray-700 dark:text-gray-300 border-gray-300'
    }
  }

  const getEventsForDate = (date: Date) => {
    if (!data?.events) return []
    const dateStr = date.toISOString().split('T')[0]
    return data.events.filter(event => event.date === dateStr)
  }

  const getDaysInMonth = (date: Date) => {
    const year = date.getFullYear()
    const month = date.getMonth()
    const firstDay = new Date(year, month, 1)
    const lastDay = new Date(year, month + 1, 0)
    const daysInMonth = lastDay.getDate()
    const startingDayOfWeek = firstDay.getDay()

    const days = []
    
    // Add empty cells for days before the first day of the month
    for (let i = 0; i < startingDayOfWeek; i++) {
      days.push(null)
    }
    
    // Add all days of the month
    for (let day = 1; day <= daysInMonth; day++) {
      days.push(new Date(year, month, day))
    }
    
    return days
  }

  const navigateMonth = (direction: 'prev' | 'next') => {
    setCurrentDate(prev => {
      const newDate = new Date(prev)
      if (direction === 'prev') {
        newDate.setMonth(prev.getMonth() - 1)
      } else {
        newDate.setMonth(prev.getMonth() + 1)
      }
      return newDate
    })
  }

  const goToToday = () => {
    setCurrentDate(new Date())
  }

  const formatDate = (date: Date) => {
    return date.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
  }

  const formatTime = (timeStr: string) => {
    if (!timeStr) return ''
    const [hours, minutes] = timeStr.split(':')
    const hour = parseInt(hours)
    const ampm = hour >= 12 ? 'PM' : 'AM'
    const displayHour = hour % 12 || 12
    return `${displayHour}:${minutes} ${ampm}`
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
          <div className="flex items-center gap-2">
            <AlertCircle className="w-5 h-5 text-red-600" />
            <p className="text-red-800 dark:text-red-200">
              Error loading calendar: {error ? (error as any).message : 'No data available'}
            </p>
          </div>
        </div>
      </div>
    )
  }

  const events = data.events || []
  const days = getDaysInMonth(currentDate)
  const today = new Date()
  const isToday = (date: Date | null) => {
    if (!date) return false
    return date.toDateString() === today.toDateString()
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold mb-2">Calendar</h1>
          <p className="text-muted-foreground">
            {events.length} scheduled posts across all platforms
          </p>
        </div>
      </div>

      {/* Calendar Controls */}
      <div className="bg-card border border-border rounded-lg p-4">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <button
              onClick={() => navigateMonth('prev')}
              className="p-2 hover:bg-accent rounded-lg transition-colors"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>
            <button
              onClick={goToToday}
              className="px-4 py-2 text-sm font-medium hover:bg-accent rounded-lg transition-colors"
            >
              Today
            </button>
            <button
              onClick={() => navigateMonth('next')}
              className="p-2 hover:bg-accent rounded-lg transition-colors"
            >
              <ChevronRight className="w-5 h-5" />
            </button>
            <h2 className="text-lg font-semibold ml-4">
              {formatDate(currentDate)}
            </h2>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setViewMode('month')}
              className={`px-3 py-1.5 text-sm font-medium rounded-lg transition-colors ${
                viewMode === 'month'
                  ? 'bg-primary text-primary-foreground'
                  : 'hover:bg-accent'
              }`}
            >
              Month
            </button>
            <button
              onClick={() => setViewMode('week')}
              className={`px-3 py-1.5 text-sm font-medium rounded-lg transition-colors ${
                viewMode === 'week'
                  ? 'bg-primary text-primary-foreground'
                  : 'hover:bg-accent'
              }`}
            >
              Week
            </button>
            <button
              onClick={() => setViewMode('day')}
              className={`px-3 py-1.5 text-sm font-medium rounded-lg transition-colors ${
                viewMode === 'day'
                  ? 'bg-primary text-primary-foreground'
                  : 'hover:bg-accent'
              }`}
            >
              Day
            </button>
          </div>
        </div>

        {/* Calendar Grid */}
        {viewMode === 'month' && (
          <div className="grid grid-cols-7 gap-1">
            {/* Day headers */}
            {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
              <div
                key={day}
                className="p-2 text-center text-sm font-semibold text-muted-foreground"
              >
                {day}
              </div>
            ))}

            {/* Calendar days */}
            {days.map((date, index) => {
              const dayEvents = date ? getEventsForDate(date) : []
              const isCurrentDay = date ? isToday(date) : false

              return (
                <div
                  key={index}
                  className={`min-h-[100px] p-2 border border-border rounded-lg ${
                    isCurrentDay ? 'bg-primary/10 border-primary' : 'bg-card'
                  } ${!date ? 'opacity-30' : ''}`}
                >
                  {date && (
                    <>
                      <div
                        className={`text-sm font-medium mb-1 ${
                          isCurrentDay ? 'text-primary' : 'text-foreground'
                        }`}
                      >
                        {date.getDate()}
                      </div>
                      <div className="space-y-1">
                        {dayEvents.slice(0, 3).map((event, idx) => (
                          <div
                            key={idx}
                            className={`text-xs p-1 rounded border ${getPlatformColor(
                              event.platform
                            )} truncate`}
                            title={`${event.platform}: ${event.video_title} at ${formatTime(event.time)}`}
                          >
                            <div className="flex items-center gap-1">
                              {getPlatformIcon(event.platform)}
                              <span className="truncate">{formatTime(event.time)}</span>
                            </div>
                          </div>
                        ))}
                        {dayEvents.length > 3 && (
                          <div className="text-xs text-muted-foreground">
                            +{dayEvents.length - 3} more
                          </div>
                        )}
                      </div>
                    </>
                  )}
                </div>
              )
            })}
          </div>
        )}

        {/* Week View Placeholder */}
        {viewMode === 'week' && (
          <div className="text-center py-12 text-muted-foreground">
            Week view coming soon
          </div>
        )}

        {/* Day View Placeholder */}
        {viewMode === 'day' && (
          <div className="text-center py-12 text-muted-foreground">
            Day view coming soon
          </div>
        )}
      </div>

      {/* Events List */}
      {events.length > 0 && (
        <div className="bg-card border border-border rounded-lg p-6">
          <h2 className="text-lg font-semibold mb-4">Upcoming Shorts Schedule</h2>
          <div className="space-y-3">
            {events
              .sort((a, b) => new Date(b.datetime).getTime() - new Date(a.datetime).getTime())
              .slice(0, 20)
              .map((event, idx) => (
                <div
                  key={idx}
                  className="flex items-start gap-4 p-4 border border-border rounded-lg hover:bg-accent/50 transition-colors"
                >
                  <div className={`p-2 rounded-lg ${getPlatformColor(event.platform)}`}>
                    {getPlatformIcon(event.platform)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="font-semibold truncate">{event.video_title}</h3>
                      <span className="text-xs text-muted-foreground">
                        {event.platform}
                      </span>
                    </div>
                    <div className="flex items-center gap-4 text-sm text-muted-foreground mb-2">
                      <span className="flex items-center gap-1">
                        <CalendarIcon className="w-4 h-4" />
                        {new Date(event.date).toLocaleDateString()}
                      </span>
                      <span className="flex items-center gap-1">
                        <Clock className="w-4 h-4" />
                        {formatTime(event.time)}
                      </span>
                      {event.playlist_name && (
                        <span className="truncate max-w-xs text-xs bg-accent px-2 py-0.5 rounded">
                          {event.playlist_name}
                        </span>
                      )}
                      {event.privacy_status && (
                        <span className={`text-xs px-2 py-0.5 rounded ${
                          event.privacy_status === 'public' 
                            ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300'
                            : 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300'
                        }`}>
                          {event.privacy_status}
                        </span>
                      )}
                    </div>
                    
                    {/* Cross-Platform Status */}
                    {event.missing_platforms && event.missing_platforms.length > 0 && event.platform.toLowerCase() === 'youtube' && (
                      <div className="mt-2 p-2 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
                        <div className="flex items-start gap-2">
                          <AlertCircle className="w-4 h-4 text-yellow-600 mt-0.5 flex-shrink-0" />
                          <div className="flex-1 min-w-0">
                            <p className="text-xs font-medium text-yellow-800 dark:text-yellow-200 mb-1">
                              Missing on:
                            </p>
                            <div className="flex flex-wrap gap-2">
                              {event.missing_platforms.map(platform => (
                                <button
                                  key={platform}
                                  onClick={() => window.location.href = `/shorts?video_id=${event.video_id}&schedule=${platform}`}
                                  className="inline-flex items-center gap-1 text-xs px-2 py-1 bg-white dark:bg-gray-800 border border-yellow-300 dark:border-yellow-700 rounded hover:bg-yellow-50 dark:hover:bg-yellow-900/40 transition-colors"
                                >
                                  {platform === 'facebook' && <Facebook className="w-3 h-3" />}
                                  {platform === 'instagram' && <Instagram className="w-3 h-3" />}
                                  {platform === 'linkedin' && <Linkedin className="w-3 h-3" />}
                                  <span className="capitalize">{platform}</span>
                                  <span className="text-yellow-600">→ Schedule</span>
                                </button>
                              ))}
                            </div>
                          </div>
                        </div>
                      </div>
                    )}

                    {event.post_content && (
                      <p className="text-sm text-muted-foreground mt-2 line-clamp-2">
                        {event.post_content}
                      </p>
                    )}
                  </div>
                  <a
                    href={event.youtube_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-primary hover:underline text-sm whitespace-nowrap"
                  >
                    View →
                  </a>
                </div>
              ))}
          </div>
        </div>
      )}

      {events.length === 0 && (
        <div className="bg-card border border-border rounded-lg p-12 text-center">
          <CalendarIcon className="w-16 h-16 mx-auto mb-4 text-muted-foreground opacity-50" />
          <h3 className="text-lg font-semibold mb-2">No Scheduled Events</h3>
          <p className="text-muted-foreground">
            You don't have any scheduled posts yet. Schedule some content to see it here.
          </p>
        </div>
      )}
    </div>
  )
}
