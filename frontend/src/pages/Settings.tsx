import { useQuery } from '@tanstack/react-query'
import api from '@/lib/api'
import { 
  Settings as SettingsIcon,
  Youtube,
  Linkedin,
  Facebook,
  Instagram,
  ExternalLink,
  CheckCircle2,
  XCircle,
  AlertCircle
} from 'lucide-react'

interface PlatformStatus {
  configured: boolean
  authenticated: boolean
  status: string
  missing: string[]
}

interface StatusData {
  youtube: PlatformStatus
  linkedin: PlatformStatus
  facebook: PlatformStatus
  instagram: PlatformStatus
}

export default function Settings() {

  const { data: statusData, isLoading } = useQuery<StatusData>({
    queryKey: ['platform-status'],
    queryFn: async () => {
      const response = await api.get('/status')
      return response.data.platforms || {}
    },
  })

  const handleConnectClick = (platform: string) => {
    if (platform === 'youtube') {
      // YouTube uses OAuth flow - redirect to config page
      window.location.href = '/config#social-media-connections'
    } else if (platform === 'linkedin') {
      // LinkedIn OAuth
      window.location.href = '/api/linkedin/oauth/authorize'
    } else if (platform === 'facebook' || platform === 'instagram') {
      // Facebook/Instagram OAuth
      window.location.href = '/api/facebook/oauth/authorize'
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'ready':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-1 text-xs font-medium bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 rounded-full">
            <CheckCircle2 className="w-3 h-3" />
            Connected
          </span>
        )
      case 'configured':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-1 text-xs font-medium bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300 rounded-full">
            <AlertCircle className="w-3 h-3" />
            Configured
          </span>
        )
      case 'needs_setup':
        return (
          <span className="inline-flex items-center gap-1 px-2 py-1 text-xs font-medium bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 rounded-full">
            <XCircle className="w-3 h-3" />
            Not Connected
          </span>
        )
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2 py-1 text-xs font-medium bg-gray-100 dark:bg-gray-900/30 text-gray-700 dark:text-gray-300 rounded-full">
            Unknown
          </span>
        )
    }
  }

  const getPlatformIcon = (platform: string) => {
    const iconClass = "w-5 h-5"
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
        return <SettingsIcon className={iconClass} />
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    )
  }

  const platforms = [
    {
      id: 'youtube',
      name: 'YouTube',
      description: 'Connect your YouTube channel to manage videos and playlists',
      status: statusData?.youtube,
    },
    {
      id: 'linkedin',
      name: 'LinkedIn',
      description: 'Connect LinkedIn to post and schedule content',
      status: statusData?.linkedin,
    },
    {
      id: 'facebook',
      name: 'Facebook',
      description: 'Connect Facebook Page to post and schedule content',
      status: statusData?.facebook,
    },
    {
      id: 'instagram',
      name: 'Instagram',
      description: 'Connect Instagram Business Account to post content',
      status: statusData?.instagram,
    },
  ]

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold mb-2">Settings</h1>
        <p className="text-muted-foreground">
          Manage your platform connections and configuration
        </p>
      </div>

      {/* Quick Link to Full Settings */}
      <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-semibold text-blue-900 dark:text-blue-100 mb-1">
              Full Settings Page
            </h3>
            <p className="text-sm text-blue-800 dark:text-blue-200">
              For detailed configuration, API keys, and advanced settings
            </p>
          </div>
          <a
            href="/config"
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
          >
            <ExternalLink className="w-4 h-4" />
            Open Full Settings
          </a>
        </div>
      </div>

      {/* Platform Connections */}
      <div className="bg-card border border-border rounded-lg p-6">
        <h2 className="text-lg font-semibold mb-4">Platform Connections</h2>
        <div className="space-y-4">
          {platforms.map((platform) => {
            const status = platform.status
            const isConnected = status?.status === 'ready'
            const isConfigured = status?.configured || false

            return (
              <div
                key={platform.id}
                className="flex items-start justify-between p-4 border border-border rounded-lg hover:bg-accent/50 transition-colors"
              >
                <div className="flex items-start gap-4 flex-1">
                  <div className={`p-3 rounded-lg ${
                    isConnected 
                      ? 'bg-green-100 dark:bg-green-900/30' 
                      : isConfigured 
                      ? 'bg-yellow-100 dark:bg-yellow-900/30'
                      : 'bg-gray-100 dark:bg-gray-900/30'
                  }`}>
                    {getPlatformIcon(platform.id)}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="font-semibold">{platform.name}</h3>
                      {status && getStatusBadge(status.status)}
                    </div>
                    <p className="text-sm text-muted-foreground mb-2">
                      {platform.description}
                    </p>
                    {status?.missing && status.missing.length > 0 && (
                      <div className="text-xs text-muted-foreground">
                        <span className="font-medium">Missing:</span>{' '}
                        {status.missing.join(', ')}
                      </div>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {!isConnected && (
                    <button
                      onClick={() => handleConnectClick(platform.id)}
                      className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors text-sm font-medium"
                    >
                      {isConfigured ? 'Connect' : 'Setup'}
                    </button>
                  )}
                  {isConnected && (
                    <span className="text-sm text-muted-foreground">
                      Connected
                    </span>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Additional Settings Info */}
      <div className="bg-card border border-border rounded-lg p-6">
        <h2 className="text-lg font-semibold mb-4">Additional Settings</h2>
        <div className="space-y-3">
          <a
            href="/config"
            className="flex items-center justify-between p-3 border border-border rounded-lg hover:bg-accent/50 transition-colors"
          >
            <div>
              <h3 className="font-medium">API Keys & Configuration</h3>
              <p className="text-sm text-muted-foreground">
                Manage API keys, tokens, and platform credentials
              </p>
            </div>
            <ExternalLink className="w-4 h-4 text-muted-foreground" />
          </a>
          <a
            href="/config#targeting-settings"
            className="flex items-center justify-between p-3 border border-border rounded-lg hover:bg-accent/50 transition-colors"
          >
            <div>
              <h3 className="font-medium">Targeting & Tags</h3>
              <p className="text-sm text-muted-foreground">
                Configure role levels, interview types, and content tags
              </p>
            </div>
            <ExternalLink className="w-4 h-4 text-muted-foreground" />
          </a>
          <a
            href="/config#scheduling"
            className="flex items-center justify-between p-3 border border-border rounded-lg hover:bg-accent/50 transition-colors"
          >
            <div>
              <h3 className="font-medium">Scheduling Settings</h3>
              <p className="text-sm text-muted-foreground">
                Configure automation schedules and posting times
              </p>
            </div>
            <ExternalLink className="w-4 h-4 text-muted-foreground" />
          </a>
        </div>
      </div>
    </div>
  )
}
