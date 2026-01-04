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
  AlertCircle,
  RefreshCw
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
      // YouTube uses client_secret.json file upload
      // Open a dialog or file upload interface
      const youtubeStatus = statusData?.youtube
      if (youtubeStatus?.configured && youtubeStatus?.authenticated) {
        alert('✅ YouTube is already connected and authenticated!')
        return
      }
      
      if (!youtubeStatus?.configured) {
        alert('⚠️ YouTube client_secret.json not found.\n\nPlease:\n1. Go to Google Cloud Console\n2. Create OAuth 2.0 credentials\n3. Download client_secret.json\n4. Upload it in the Settings')
        return
      }
      
      // If configured but not authenticated, show auth link
      alert('✅ client_secret.json is set up.\n\nClick OK to authenticate with your Google account.')
      window.location.replace('/settings#youtube-auth')
    } else if (platform === 'linkedin') {
      const linkedinStatus = statusData?.linkedin
      if (!linkedinStatus?.configured) {
        alert('⚠️ LinkedIn Client ID and Secret must be configured first!\n\nPlease go to Settings → API Keys and enter your LinkedIn credentials.')
        window.location.replace('/settings#social-media-connections')
        return
      }
      window.location.replace('/api/linkedin/oauth/authorize')
    } else if (platform === 'facebook' || platform === 'instagram') {
      // Open OAuth popup for Facebook/Instagram
      const popupUrl = '/api/facebook/oauth/start-auto'
      const popup = window.open(popupUrl, 'facebook-connect', 'width=500,height=700,scrollbars=yes,resizable=yes')
      
      // Check if popup was blocked
      if (!popup) {
        alert('⚠️ Popup was blocked! Please allow popups for this site and try again.')
        return
      }

      // Listen for popup close and refresh status
      const checkPopupInterval = setInterval(() => {
        if (popup.closed) {
          clearInterval(checkPopupInterval)
          // Refresh the page to show updated status
          setTimeout(() => {
            window.location.reload()
          }, 500)
        }
      }, 500)
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
          <button
            onClick={() => window.location.replace('/settings')}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
          >
            <ExternalLink className="w-4 h-4" />
            Open Full Settings
          </button>
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
                      : 'bg-red-100 dark:bg-red-900/30'
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
                      <div className="flex items-start gap-2 mt-2 p-2 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                        <AlertCircle className="w-4 h-4 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
                        <div className="flex-1">
                          <p className="text-xs font-semibold text-red-800 dark:text-red-200 mb-1">Missing Configuration:</p>
                          <ul className="text-xs text-red-700 dark:text-red-300 space-y-1">
                            {status.missing.map((item, idx) => (
                              <li key={idx} className="flex items-center gap-1">
                                <XCircle className="w-3 h-3" />
                                {item}
                              </li>
                            ))}
                          </ul>
                        </div>
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
                    <button
                      onClick={() => handleConnectClick(platform.id)}
                      className="px-4 py-2 bg-secondary text-secondary-foreground rounded-lg hover:bg-secondary/80 transition-colors text-sm font-medium flex items-center gap-2"
                      title="Reconnect to refresh tokens (useful if tokens expired)"
                    >
                      <RefreshCw className="w-4 h-4" />
                      Reconnect
                    </button>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* YouTube Client Secret Upload */}
      <div className="bg-card border border-border rounded-lg p-6">
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Youtube className="w-5 h-5" />
          YouTube Setup
        </h2>
        <p className="text-sm text-muted-foreground mb-4">
          YouTube requires a client_secret.json file for authentication. Download it from Google Cloud Console.
        </p>
        
        <div className="space-y-3">
          <div className="p-4 border border-border rounded-lg bg-accent/50">
            <h3 className="font-medium mb-2">Step 1: Get client_secret.json</h3>
            <ol className="text-sm text-muted-foreground space-y-1 list-decimal list-inside">
              <li>Go to <a href="https://console.cloud.google.com" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">Google Cloud Console</a></li>
              <li>Create a new project or select existing one</li>
              <li>Enable YouTube Data API v3</li>
              <li>Go to Credentials → Create OAuth 2.0 Client ID (Desktop application)</li>
              <li>Download the JSON file</li>
            </ol>
          </div>

          <div className="p-4 border border-border rounded-lg bg-accent/50">
            <h3 className="font-medium mb-3">Step 2: Upload client_secret.json</h3>
            <input 
              type="file" 
              accept=".json"
              onChange={async (e) => {
                const file = e.target.files?.[0]
                if (!file) return
                
                const formData = new FormData()
                formData.append('file', file)
                
                try {
                  const response = await fetch('/api/config/upload-client-secret', {
                    method: 'POST',
                    body: formData
                  })
                  
                  if (response.ok) {
                    alert('✅ YouTube client_secret.json uploaded successfully!\n\nPlease refresh the page.')
                    setTimeout(() => window.location.reload(), 1000)
                  } else {
                    const error = await response.json()
                    alert('❌ Upload failed: ' + error.error)
                  }
                } catch (error) {
                  alert('❌ Upload error: ' + String(error))
                }
              }}
              className="block w-full"
            />
            <p className="text-xs text-muted-foreground mt-2">
              Select your downloaded client_secret.json file
            </p>
          </div>

          {statusData?.youtube?.configured && (
            <div className="p-3 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 rounded-lg flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4" />
              <span>✅ client_secret.json is configured</span>
            </div>
          )}
        </div>
      </div>

      <div className="bg-card border border-border rounded-lg p-6">
        <h2 className="text-lg font-semibold mb-4">Additional Settings</h2>
        <div className="space-y-3">
          <button
            onClick={() => window.location.replace('/settings')}
            className="w-full flex items-center justify-between p-3 border border-border rounded-lg hover:bg-accent/50 transition-colors text-left"
          >
            <div>
              <h3 className="font-medium">API Keys & Configuration</h3>
              <p className="text-sm text-muted-foreground">
                Manage API keys, tokens, and platform credentials
              </p>
            </div>
            <ExternalLink className="w-4 h-4 text-muted-foreground" />
          </button>
          <button
            onClick={() => window.location.replace('/settings#targeting-settings')}
            className="w-full flex items-center justify-between p-3 border border-border rounded-lg hover:bg-accent/50 transition-colors text-left"
          >
            <div>
              <h3 className="font-medium">Targeting & Tags</h3>
              <p className="text-sm text-muted-foreground">
                Configure role levels, interview types, and content tags
              </p>
            </div>
            <ExternalLink className="w-4 h-4 text-muted-foreground" />
          </button>
          <button
            onClick={() => window.location.replace('/settings#scheduling')}
            className="w-full flex items-center justify-between p-3 border border-border rounded-lg hover:bg-accent/50 transition-colors text-left"
          >
            <div>
              <h3 className="font-medium">Scheduling Settings</h3>
              <p className="text-sm text-muted-foreground">
                Configure automation schedules and posting times
              </p>
            </div>
            <ExternalLink className="w-4 h-4 text-muted-foreground" />
          </button>
        </div>
      </div>
    </div>
  )
}
