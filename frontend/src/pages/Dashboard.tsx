import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import api from '@/lib/api'
import { 
  Plus, 
  List, 
  Calendar, 
  Filter,
  CheckCircle2,
  Clock,
  Send,
  FileText,
  Youtube,
  Linkedin,
  Facebook,
  Instagram
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

  const { data, isLoading, refetch } = useQuery<QueueData>({
    queryKey: ['queue', activeTab],
    queryFn: async () => {
      const response = await api.get('/queue')
      return response.data
    },
  })

  const getPlatformIcon = (platform: string) => {
    switch (platform.toLowerCase()) {
      case 'youtube':
        return <Youtube className="w-4 h-4" />
      case 'linkedin':
        return <Linkedin className="w-4 h-4" />
      case 'facebook':
        return <Facebook className="w-4 h-4" />
      case 'instagram':
        return <Instagram className="w-4 h-4" />
      default:
        return <Send className="w-4 h-4" />
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'published':
        return (
          <span className="px-2 py-0.5 text-xs bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 rounded flex items-center gap-1">
            <CheckCircle2 className="w-3 h-3" />
            Published
          </span>
        )
      case 'scheduled':
        return (
          <span className="px-2 py-0.5 text-xs bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded flex items-center gap-1">
            <Clock className="w-3 h-3" />
            Scheduled
          </span>
        )
      case 'pending':
        return (
          <span className="px-2 py-0.5 text-xs bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300 rounded">
            Pending
          </span>
        )
      case 'error':
        return (
          <span className="px-2 py-0.5 text-xs bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 rounded">
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
    <div className="flex flex-col h-full">
      {/* Top Navigation Tabs */}
      <div className="border-b border-border bg-card">
        <div className="flex items-center justify-between px-6 py-4">
          <div className="flex items-center gap-6">
            <button
              onClick={() => setActiveTab('queue')}
              className={`flex items-center gap-2 px-4 py-2 font-medium text-sm transition-colors ${
                activeTab === 'queue'
                  ? 'text-primary border-b-2 border-primary'
                  : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              Queue
              {data?.queue && data.queue.length > 0 && (
                <span className="px-2 py-0.5 text-xs bg-muted rounded-full">
                  {data.queue.length}
                </span>
              )}
            </button>
            <button
              onClick={() => setActiveTab('drafts')}
              className={`flex items-center gap-2 px-4 py-2 font-medium text-sm transition-colors ${
                activeTab === 'drafts'
                  ? 'text-primary border-b-2 border-primary'
                  : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              Drafts
              {data?.drafts && data.drafts.length > 0 && (
                <span className="px-2 py-0.5 text-xs bg-muted rounded-full">
                  {data.drafts.length}
                </span>
              )}
            </button>
            <button
              onClick={() => setActiveTab('sent')}
              className={`flex items-center gap-2 px-4 py-2 font-medium text-sm transition-colors ${
                activeTab === 'sent'
                  ? 'text-primary border-b-2 border-primary'
                  : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              Sent
              {data?.published && data.published.length > 0 && (
                <span className="px-2 py-0.5 text-xs bg-muted rounded-full">
                  {data.published.length}
                </span>
              )}
            </button>
          </div>

          {/* Right Side Controls */}
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1 border border-border rounded-md">
              <button
                onClick={() => setViewMode('list')}
                className={`p-2 transition-colors ${
                  viewMode === 'list'
                    ? 'bg-primary text-primary-foreground'
                    : 'hover:bg-accent'
                }`}
              >
                <List className="w-4 h-4" />
              </button>
              <button
                onClick={() => setViewMode('calendar')}
                className={`p-2 transition-colors ${
                  viewMode === 'calendar'
                    ? 'bg-primary text-primary-foreground'
                    : 'hover:bg-accent'
                }`}
              >
                <Calendar className="w-4 h-4" />
              </button>
            </div>

            {/* Filter Dropdowns */}
            <select
              value={selectedChannel}
              onChange={(e) => setSelectedChannel(e.target.value)}
              className="px-3 py-2 text-sm border border-border rounded-md bg-background focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="all">All Channels</option>
              <option value="youtube">YouTube</option>
              <option value="linkedin">LinkedIn</option>
              <option value="facebook">Facebook</option>
              <option value="instagram">Instagram</option>
            </select>

            <button className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors flex items-center gap-2 text-sm font-medium">
              <Plus className="w-4 h-4" />
              New Post
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-y-auto bg-background">
        {filteredItems.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full py-12 px-6">
            <div className="w-64 h-48 mb-6 relative">
              {/* Empty State Illustration */}
              <div className="absolute inset-0 flex flex-col gap-2">
                <div className="h-24 bg-muted rounded-lg opacity-60"></div>
                <div className="h-24 bg-muted rounded-lg opacity-40 ml-8"></div>
                <div className="h-24 bg-muted rounded-lg opacity-20 ml-16"></div>
              </div>
              <div className="absolute top-1/2 right-0 transform -translate-y-1/2">
                <div className="w-12 h-12 border-2 border-primary rounded-full flex items-center justify-center">
                  <Send className="w-6 h-6 text-primary" />
                </div>
              </div>
            </div>
            <h3 className="text-xl font-semibold mb-2">
              {activeTab === 'queue' && 'No posts scheduled'}
              {activeTab === 'drafts' && 'No drafts'}
              {activeTab === 'sent' && 'No sent posts'}
            </h3>
            <p className="text-muted-foreground mb-6 text-center max-w-md">
              {activeTab === 'queue' && 'Schedule some posts and they will appear here'}
              {activeTab === 'drafts' && 'Create drafts and they will appear here'}
              {activeTab === 'sent' && 'Your published posts will appear here'}
            </p>
            <button className="px-6 py-3 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors flex items-center gap-2 font-medium">
              <Plus className="w-5 h-5" />
              New Post
            </button>
          </div>
        ) : (
          <div className="p-6">
            <div className="space-y-3">
              {filteredItems.map((item) => (
                <div
                  key={item.id}
                  className="bg-card border border-border rounded-lg p-4 hover:shadow-md transition-shadow"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <div className="p-2 bg-muted rounded-lg">
                          {getPlatformIcon(item.platform)}
                        </div>
                        <div className="flex-1">
                          <h3 className="font-semibold text-sm mb-1">{item.video_title}</h3>
                          {item.playlist_name && (
                            <p className="text-xs text-muted-foreground">{item.playlist_name}</p>
                          )}
                        </div>
                        {getStatusBadge(item.status)}
                      </div>
                      <p className="text-sm text-muted-foreground line-clamp-2 mt-2">
                        {item.post_content}
                      </p>
                      {item.schedule_date && (
                        <div className="flex items-center gap-2 mt-3 text-xs text-muted-foreground">
                          <Clock className="w-3 h-3" />
                          <span>
                            {new Date(item.schedule_date).toLocaleString()}
                          </span>
                        </div>
                      )}
                    </div>
                    <div className="flex items-center gap-2 ml-4">
                      {item.status === 'scheduled' && (
                        <button className="px-3 py-1.5 text-xs border border-border rounded-md hover:bg-accent transition-colors">
                          Edit
                        </button>
                      )}
                      {item.status === 'pending' && (
                        <button className="px-3 py-1.5 text-xs bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors">
                          Schedule
                        </button>
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
