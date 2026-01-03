import { useQuery } from '@tanstack/react-query'
import api from '@/lib/api'
import {
  BarChart3,
  Clock,
  Youtube,
  Linkedin,
  Facebook,
  AlertCircle,
  Loader2
} from 'lucide-react'

interface InsightsData {
  youtube?: {
    views_data?: any[]
    geography?: any[]
    demographics?: any[]
    hourly_activity?: any[]
    error?: string
  }
  youtube_videos?: {
    total?: number
    total_views?: number
    total_likes?: number
  }
  facebook?: {
    insights?: any[]
    error?: string
  }
  facebook_posts?: {
    count?: number
  }
  linkedin?: {
    error?: string
  }
  linkedin_posts?: {
    count?: number
  }
  optimal_posting_times?: any
}

export default function Insights() {
  const { data, isLoading, error } = useQuery<InsightsData>({
    queryKey: ['insights'],
    queryFn: async () => {
      const response = await api.get('/insights-data')
      return response.data
    },
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <p className="text-red-800 dark:text-red-200">
            Error loading analytics: {(error as any).message}
          </p>
        </div>
      </div>
    )
  }

  const youtubeData = data?.youtube
  const youtubeVideos = data?.youtube_videos
  const facebookData = data?.facebook
  const linkedinData = data?.linkedin

  // Calculate total views from YouTube data
  const totalViews = youtubeData?.views_data?.reduce((sum, row) => sum + (row[1] || 0), 0) || 0
  const totalWatchTime = youtubeData?.views_data?.reduce((sum, row) => sum + (row[2] || 0), 0) || 0

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold mb-2">Analytics</h1>
        <p className="text-muted-foreground">
          View performance metrics across all your platforms
        </p>
      </div>

      {/* YouTube Analytics */}
      <div className="bg-card border border-border rounded-lg p-6">
        <div className="flex items-center gap-2 mb-4">
          <Youtube className="w-5 h-5 text-red-600" />
          <h2 className="text-lg font-semibold">YouTube Analytics</h2>
        </div>
        
        {youtubeData?.error ? (
          <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
            <div className="flex items-start gap-2">
              <AlertCircle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-yellow-800 dark:text-yellow-200 font-medium mb-1">
                  YouTube Analytics Not Available
                </p>
                <p className="text-sm text-yellow-700 dark:text-yellow-300">
                  {youtubeData.error}
                </p>
              </div>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-muted/50 rounded-lg p-4">
              <p className="text-sm text-muted-foreground mb-1">Total Views (30 days)</p>
              <p className="text-2xl font-bold">{totalViews.toLocaleString()}</p>
            </div>
            <div className="bg-muted/50 rounded-lg p-4">
              <p className="text-sm text-muted-foreground mb-1">Watch Time (minutes)</p>
              <p className="text-2xl font-bold">{Math.round(totalWatchTime).toLocaleString()}</p>
            </div>
            <div className="bg-muted/50 rounded-lg p-4">
              <p className="text-sm text-muted-foreground mb-1">Total Videos</p>
              <p className="text-2xl font-bold">{youtubeVideos?.total || 0}</p>
            </div>
          </div>
        )}

        {youtubeVideos && (
          <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-muted/50 rounded-lg p-4">
              <p className="text-sm text-muted-foreground mb-1">Total Video Views</p>
              <p className="text-xl font-semibold">{youtubeVideos.total_views?.toLocaleString() || 0}</p>
            </div>
            <div className="bg-muted/50 rounded-lg p-4">
              <p className="text-sm text-muted-foreground mb-1">Total Likes</p>
              <p className="text-xl font-semibold">{youtubeVideos.total_likes?.toLocaleString() || 0}</p>
            </div>
          </div>
        )}
      </div>

      {/* Facebook Analytics */}
      <div className="bg-card border border-border rounded-lg p-6">
        <div className="flex items-center gap-2 mb-4">
          <Facebook className="w-5 h-5 text-blue-600" />
          <h2 className="text-lg font-semibold">Facebook Insights</h2>
        </div>
        
        {facebookData?.error ? (
          <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
            <div className="flex items-start gap-2">
              <AlertCircle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-yellow-800 dark:text-yellow-200 font-medium mb-1">
                  Facebook Insights Not Available
                </p>
                <p className="text-sm text-yellow-700 dark:text-yellow-300">
                  {facebookData.error}
                </p>
              </div>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-muted/50 rounded-lg p-4">
              <p className="text-sm text-muted-foreground mb-1">Total Posts</p>
              <p className="text-2xl font-bold">{data?.facebook_posts?.count || 0}</p>
            </div>
            {facebookData?.insights && facebookData.insights.length > 0 && (
              <div className="bg-muted/50 rounded-lg p-4">
                <p className="text-sm text-muted-foreground mb-1">Insights Available</p>
                <p className="text-2xl font-bold">{facebookData.insights.length}</p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* LinkedIn Analytics */}
      <div className="bg-card border border-border rounded-lg p-6">
        <div className="flex items-center gap-2 mb-4">
          <Linkedin className="w-5 h-5 text-blue-700" />
          <h2 className="text-lg font-semibold">LinkedIn Analytics</h2>
        </div>
        
        {linkedinData?.error ? (
          <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
            <div className="flex items-start gap-2">
              <AlertCircle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-yellow-800 dark:text-yellow-200 font-medium mb-1">
                  LinkedIn Analytics Not Available
                </p>
                <p className="text-sm text-yellow-700 dark:text-yellow-300">
                  {linkedinData.error || 'LinkedIn Analytics requires specific API access'}
                </p>
              </div>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-muted/50 rounded-lg p-4">
              <p className="text-sm text-muted-foreground mb-1">Total Posts</p>
              <p className="text-2xl font-bold">{data?.linkedin_posts?.count || 0}</p>
            </div>
          </div>
        )}
      </div>

      {/* Optimal Posting Times */}
      {data?.optimal_posting_times && !data.optimal_posting_times.error && (
        <div className="bg-card border border-border rounded-lg p-6">
          <div className="flex items-center gap-2 mb-4">
            <Clock className="w-5 h-5 text-primary" />
            <h2 className="text-lg font-semibold">Optimal Posting Times</h2>
          </div>
          <div className="bg-muted/50 rounded-lg p-4">
            <p className="text-sm text-muted-foreground">
              Based on your audience activity, the best times to post are being calculated.
            </p>
          </div>
        </div>
      )}

      {/* No Data Message */}
      {!youtubeData && !facebookData && !linkedinData && (
        <div className="bg-card border border-border rounded-lg p-12 text-center">
          <BarChart3 className="w-16 h-16 mx-auto mb-4 text-muted-foreground opacity-50" />
          <h3 className="text-lg font-semibold mb-2">No Analytics Data Available</h3>
          <p className="text-muted-foreground mb-4">
            Connect your platforms in Settings to start seeing analytics data.
          </p>
          <a
            href="/settings"
            onClick={(e) => {
              e.preventDefault()
              window.location.href = '/settings'
            }}
            className="inline-flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors cursor-pointer"
          >
            Go to Settings
          </a>
        </div>
      )}
    </div>
  )
}
