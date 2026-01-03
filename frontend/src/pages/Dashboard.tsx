import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '@/lib/api'
import StatusBanner from '@/components/StatusBanner'
import { 
  Plus, 
  List, 
  Calendar, 
  CheckCircle2,
  Clock,
  Send,
  Youtube,
  Linkedin,
  Facebook,
  Instagram,
  Edit,
  Calendar as CalendarIcon
} from 'lucide-react'

interface QueueItem {
  id: number
  video_id: string
  video_title: string
  platform: string
  post_content: string
  schedule_date: string
  status: 'pending' | 'scheduled' | 'published' | 'error'
  playlist_name?: string
}

interface QueueData {
  queue: QueueItem[]
  scheduled: QueueItem[]
  published: QueueItem[]
  drafts: QueueItem[]
}

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState<'queue' | 'drafts' | 'sent'>('queue')
  const [viewMode, setViewMode] = useState<'list' | 'calendar'>('list')
  const [selectedChannel, setSelectedChannel] = useState<string>('all')
  const [editingItem, setEditingItem] = useState<number | null>(null)
  const [scheduleDate, setScheduleDate] = useState<string>('')
  const queryClient = useQueryClient()

  const { data, isLoading } = useQuery<QueueData>({
    queryKey: ['queue', activeTab],
    queryFn: async () => {
      const response = await api.get('/queue')
      return response.data
    },
  })

  const scheduleMutation = useMutation({
    mutationFn: async ({ postId, scheduleDate, item }: { postId: number, scheduleDate: string, item: QueueItem }) => {
      // Format date for API (YYYY-MM-DD HH:MM)
      const formattedDate = new Date(scheduleDate).toISOString().slice(0, 16).replace('T', ' ')
      
      // If post already exists (has id), update it; otherwise create new schedule
      if (item.status === 'scheduled' || item.status === 'pending') {
        const response = await api.put(`/queue/${postId}`, {
          schedule_date: formattedDate,
        })
        return response.data
      } else {
        // Create new scheduled post
        const response = await api.post('/schedule-post', {
          video_id: item.video_id,
          platform: item.platform,
          post_content: item.post_content,
          schedule_datetime: formattedDate,
        })
        return response.data
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['queue'] })
      setEditingItem(null)
      setScheduleDate('')
    },
  })

  const publishNowMutation = useMutation({
    mutationFn: async (postId: number) => {
      const response = await api.post(`/queue/${postId}/publish`)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['queue'] })
    },
  })

  const handleSchedule = (item: QueueItem) => {
    setEditingItem(item.id)
    // Set default schedule date to tomorrow at 7:30 PM
    const tomorrow = new Date()
    tomorrow.setDate(tomorrow.getDate() + 1)
    tomorrow.setHours(19, 30, 0, 0)
    setScheduleDate(tomorrow.toISOString().slice(0, 16))
  }

  const handleEdit = (item: QueueItem) => {
    setEditingItem(item.id)
    if (item.schedule_date) {
      setScheduleDate(new Date(item.schedule_date).toISOString().slice(0, 16))
    } else {
      const tomorrow = new Date()
      tomorrow.setDate(tomorrow.getDate() + 1)
      tomorrow.setHours(19, 30, 0, 0)
      setScheduleDate(tomorrow.toISOString().slice(0, 16))
    }
  }

  const handleSaveSchedule = (item: QueueItem) => {
    if (!scheduleDate) {
      alert('Please select a date and time')
      return
    }
    scheduleMutation.mutate({ postId: item.id, scheduleDate, item })
  }

  const handlePublishNow = (item: QueueItem) => {
    if (confirm(`Publish this post to ${item.platform} now?`)) {
      publishNowMutation.mutate(item.id)
    }
  }

  const handleCancelEdit = () => {
    setEditingItem(null)
    setScheduleDate('')
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
        return <Send className={iconClass} />
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'published':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 text-xs font-medium bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 rounded-full">
            <CheckCircle2 className="w-3 h-3" />
            Published
          </span>
        )
      case 'scheduled':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 text-xs font-medium bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded-full">
            <Clock className="w-3 h-3" />
            Scheduled
          </span>
        )
      case 'pending':
        return (
          <span className="inline-flex items-center px-2 py-0.5 text-xs font-medium bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300 rounded-full">
            Pending
          </span>
        )
      case 'error':
        return (
          <span className="inline-flex items-center px-2 py-0.5 text-xs font-medium bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 rounded-full">
            Error
          </span>
        )
      default:
        return null
    }
  }

  const getItemsForTab = () => {
    if (!data) return []
    switch (activeTab) {
      case 'queue':
        return data.queue || []
      case 'drafts':
        return data.drafts || []
      case 'sent':
        return data.published || []
      default:
        return []
    }
  }

  const items = getItemsForTab()
  const filteredItems = selectedChannel === 'all' 
    ? items 
    : items.filter(item => item.platform.toLowerCase() === selectedChannel.toLowerCase())

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full bg-background">
      {/* Status Banner - Shows what's not configured */}
      <StatusBanner />
      
      {/* Top Navigation Tabs */}
      <div className="border-b border-border bg-card">
        <div className="flex items-center justify-between px-6 py-3">
          <div className="flex items-center gap-1">
            <button
              onClick={() => setActiveTab('queue')}
              className={`relative flex items-center gap-2 px-4 py-2 font-medium text-sm transition-colors ${
                activeTab === 'queue'
                  ? 'text-primary'
                  : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              Queue
              {data?.queue && data.queue.length > 0 && (
                <span className="ml-1 px-1.5 py-0.5 text-xs bg-muted rounded-full min-w-[20px] text-center">
                  {data.queue.length}
                </span>
              )}
              {activeTab === 'queue' && (
                <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary"></span>
              )}
            </button>
            <button
              onClick={() => setActiveTab('drafts')}
              className={`relative flex items-center gap-2 px-4 py-2 font-medium text-sm transition-colors ${
                activeTab === 'drafts'
                  ? 'text-primary'
                  : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              Drafts
              {data?.drafts && data.drafts.length > 0 && (
                <span className="ml-1 px-1.5 py-0.5 text-xs bg-muted rounded-full min-w-[20px] text-center">
                  {data.drafts.length}
                </span>
              )}
              {activeTab === 'drafts' && (
                <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary"></span>
              )}
            </button>
            <button
              onClick={() => setActiveTab('sent')}
              className={`relative flex items-center gap-2 px-4 py-2 font-medium text-sm transition-colors ${
                activeTab === 'sent'
                  ? 'text-primary'
                  : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              Sent
              {data?.published && data.published.length > 0 && (
                <span className="ml-1 px-1.5 py-0.5 text-xs bg-muted rounded-full min-w-[20px] text-center">
                  {data.published.length}
                </span>
              )}
              {activeTab === 'sent' && (
                <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary"></span>
              )}
            </button>
          </div>

          {/* Right Side Controls */}
          <div className="flex items-center gap-2">
            <div className="flex items-center gap-0.5 border border-border rounded-lg p-0.5 bg-muted/50">
              <button
                onClick={() => setViewMode('list')}
                className={`p-1.5 rounded transition-colors ${
                  viewMode === 'list'
                    ? 'bg-background text-foreground shadow-sm'
                    : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                <List className="w-4 h-4" />
              </button>
              <button
                onClick={() => setViewMode('calendar')}
                className={`p-1.5 rounded transition-colors ${
                  viewMode === 'calendar'
                    ? 'bg-background text-foreground shadow-sm'
                    : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                <Calendar className="w-4 h-4" />
              </button>
            </div>

            <select
              value={selectedChannel}
              onChange={(e) => setSelectedChannel(e.target.value)}
              className="px-3 py-1.5 text-sm border border-border rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-0"
            >
              <option value="all">All Channels</option>
              <option value="youtube">YouTube</option>
              <option value="linkedin">LinkedIn</option>
              <option value="facebook">Facebook</option>
              <option value="instagram">Instagram</option>
            </select>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-y-auto">
        {filteredItems.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full py-12 px-6">
            <div className="w-64 h-48 mb-6 relative opacity-60">
              {/* Empty State Illustration */}
              <div className="absolute inset-0 flex flex-col gap-2">
                <div className="h-20 bg-gradient-to-br from-muted to-muted/50 rounded-lg"></div>
                <div className="h-20 bg-gradient-to-br from-muted/80 to-muted/40 rounded-lg ml-8"></div>
                <div className="h-20 bg-gradient-to-br from-muted/60 to-muted/20 rounded-lg ml-16"></div>
              </div>
              <div className="absolute top-1/2 right-0 transform -translate-y-1/2">
                <div className="w-10 h-10 border-2 border-primary/30 rounded-full flex items-center justify-center bg-primary/5">
                  <Send className="w-5 h-5 text-primary/50" />
                </div>
              </div>
            </div>
            <h3 className="text-lg font-semibold mb-1">
              {activeTab === 'queue' && 'No posts scheduled'}
              {activeTab === 'drafts' && 'No drafts'}
              {activeTab === 'sent' && 'No sent posts'}
            </h3>
            <p className="text-sm text-muted-foreground mb-6 text-center max-w-md">
              {activeTab === 'queue' && 'Schedule some posts and they will appear here'}
              {activeTab === 'drafts' && 'Create drafts and they will appear here'}
              {activeTab === 'sent' && 'Your published posts will appear here'}
            </p>
            <button className="px-5 py-2.5 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-all duration-200 flex items-center gap-2 font-medium shadow-sm hover:shadow">
              <Plus className="w-4 h-4" />
              New Post
            </button>
          </div>
        ) : (
          <div className="p-6">
            <div className="space-y-3">
              {filteredItems.map((item) => (
                <div
                  key={item.id}
                  className="bg-card border border-border rounded-lg p-4 hover:shadow-md transition-all duration-200 hover:border-primary/20"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start gap-3 mb-2">
                        <div className="p-2 bg-muted rounded-lg flex-shrink-0">
                          {getPlatformIcon(item.platform)}
                        </div>
                        <div className="flex-1 min-w-0">
                          <h3 className="font-semibold text-sm mb-1 truncate">{item.video_title}</h3>
                          {item.playlist_name && (
                            <p className="text-xs text-muted-foreground truncate">{item.playlist_name}</p>
                          )}
                        </div>
                        <div className="flex-shrink-0">
                          {getStatusBadge(item.status)}
                        </div>
                      </div>
                      <p className="text-sm text-muted-foreground line-clamp-2 mt-2 ml-11">
                        {item.post_content}
                      </p>
                      {item.schedule_date && (
                        <div className="flex items-center gap-2 mt-3 ml-11 text-xs text-muted-foreground">
                          <Clock className="w-3 h-3" />
                          <span>
                            {new Date(item.schedule_date).toLocaleString()}
                          </span>
                        </div>
                      )}
                    </div>
                    <div className="flex items-center gap-2 flex-shrink-0">
                      {editingItem === item.id ? (
                        <div className="flex items-center gap-2">
                          <input
                            type="datetime-local"
                            value={scheduleDate}
                            onChange={(e) => setScheduleDate(e.target.value)}
                            className="px-2 py-1 text-xs border border-border rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-primary"
                          />
                          <button
                            onClick={() => handleSaveSchedule(item)}
                            disabled={scheduleMutation.isPending}
                            className="px-3 py-1.5 text-xs bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors disabled:opacity-50"
                          >
                            {scheduleMutation.isPending ? 'Saving...' : 'Save'}
                          </button>
                          <button
                            onClick={handleCancelEdit}
                            className="px-3 py-1.5 text-xs border border-border rounded-md hover:bg-accent transition-colors"
                          >
                            Cancel
                          </button>
                        </div>
                      ) : (
                        <>
                          {item.status === 'scheduled' && (
                            <>
                              <button
                                onClick={() => handleEdit(item)}
                                className="px-3 py-1.5 text-xs border border-border rounded-md hover:bg-accent transition-colors flex items-center gap-1"
                              >
                                <Edit className="w-3 h-3" />
                                Edit
                              </button>
                              <button
                                onClick={() => handlePublishNow(item)}
                                disabled={publishNowMutation.isPending}
                                className="px-3 py-1.5 text-xs bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors disabled:opacity-50 flex items-center gap-1"
                              >
                                <Send className="w-3 h-3" />
                                Publish Now
                              </button>
                            </>
                          )}
                          {item.status === 'pending' && (
                            <>
                              <button
                                onClick={() => handleSchedule(item)}
                                className="px-3 py-1.5 text-xs bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors flex items-center gap-1"
                              >
                                <CalendarIcon className="w-3 h-3" />
                                Schedule
                              </button>
                              <button
                                onClick={() => handlePublishNow(item)}
                                disabled={publishNowMutation.isPending}
                                className="px-3 py-1.5 text-xs bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors disabled:opacity-50 flex items-center gap-1"
                              >
                                <Send className="w-3 h-3" />
                                Publish Now
                              </button>
                            </>
                          )}
                        </>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
