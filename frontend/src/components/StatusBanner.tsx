import { useQuery } from '@tanstack/react-query'
import api from '@/lib/api'
import { AlertTriangle, ExternalLink, Settings } from 'lucide-react'

interface PlatformStatus {
  configured: boolean
  authenticated: boolean
  redirect_uri: string
  status: 'ready' | 'configured' | 'needs_setup'
  missing: string[]
}

interface StatusData {
  platforms?: {
    youtube?: PlatformStatus
    linkedin?: PlatformStatus
    facebook?: PlatformStatus
    instagram?: PlatformStatus
  }
  youtube?: PlatformStatus
  linkedin?: PlatformStatus
  facebook?: PlatformStatus
  instagram?: PlatformStatus
  overall: {
    ready: number
    total: number
    percentage: number
  }
}

export default function StatusBanner() {
  const { data, isLoading } = useQuery<StatusData>({
    queryKey: ['status'],
    queryFn: async () => {
      const response = await api.get('/status')
      return response.data
    },
    refetchInterval: 30000, // Refresh every 30 seconds
  })

  if (isLoading || !data) {
    return null
  }

  // Handle both response formats: with platforms object or direct properties
  const platforms = data.platforms || {}
  const youtube = platforms.youtube || data.youtube
  const linkedin = platforms.linkedin || data.linkedin
  const facebook = platforms.facebook || data.facebook
  const instagram = platforms.instagram || data.instagram
  const { overall } = data

  // Don't show if everything is ready
  if (overall.percentage === 100) {
    return null
  }

  const platformList = [
    { name: 'YouTube', status: youtube, icon: '🎥' },
    { name: 'LinkedIn', status: linkedin, icon: '💼' },
    { name: 'Facebook', status: facebook, icon: '📘' },
    { name: 'Instagram', status: instagram, icon: '📷' },
  ].filter(p => p.status) // Only include platforms that have status data

  const needsSetup = platformList.filter(p => p.status?.status === 'needs_setup')
  const needsAuth = platformList.filter(p => p.status?.status === 'configured')

  return (
    <div className="bg-yellow-50 dark:bg-yellow-900/20 border-b border-yellow-200 dark:border-yellow-800">
      <div className="p-4">
        <div className="flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-yellow-600 dark:text-yellow-400 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <h3 className="font-semibold text-yellow-900 dark:text-yellow-100 mb-2">
              Setup Required ({overall.ready}/{overall.total} platforms ready)
            </h3>
            
            {needsSetup.length > 0 && (
              <div className="mb-3">
                <p className="text-sm text-yellow-800 dark:text-yellow-200 mb-2 font-medium">
                  Needs Configuration:
                </p>
                <div className="space-y-2">
                  {needsSetup.map((platform) => (
                    <div key={platform.name} className="bg-white dark:bg-gray-800 rounded p-2 text-sm">
                      <div className="flex items-center justify-between">
                        <span className="font-medium">
                          {platform.icon} {platform.name}
                        </span>
                        <a
                          href="/config#social-media-connections"
                          className="text-primary hover:underline flex items-center gap-1 text-xs"
                        >
                          Configure <ExternalLink className="w-3 h-3" />
                        </a>
                      </div>
                      {platform.status?.missing && platform.status.missing.length > 0 && (
                        <ul className="mt-1 ml-4 list-disc text-yellow-700 dark:text-yellow-300">
                          {platform.status.missing.map((item, idx) => (
                            <li key={idx} className="text-xs">{item}</li>
                          ))}
                        </ul>
                      )}
                      {platform.status?.redirect_uri && (
                        <div className="mt-1 text-xs text-muted-foreground">
                          Redirect URI: <code className="bg-gray-100 dark:bg-gray-700 px-1 rounded">{platform.status.redirect_uri}</code>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {needsAuth.length > 0 && (
              <div>
                <p className="text-sm text-yellow-800 dark:text-yellow-200 mb-2 font-medium">
                  Needs Authentication:
                </p>
                <div className="space-y-1">
                  {needsAuth.map((platform) => (
                    <div key={platform.name} className="bg-white dark:bg-gray-800 rounded p-2 text-sm flex items-center justify-between">
                      <span>
                        {platform.icon} {platform.name} - Click "Connect" to authenticate
                      </span>
                      <a
                        href="/config#social-media-connections"
                        className="text-primary hover:underline flex items-center gap-1 text-xs"
                      >
                        Connect <ExternalLink className="w-3 h-3" />
                      </a>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="mt-3 pt-3 border-t border-yellow-200 dark:border-yellow-800">
              <a
                href="/config#social-media-connections"
                className="inline-flex items-center gap-2 px-3 py-1.5 bg-yellow-600 hover:bg-yellow-700 text-white rounded-md text-sm font-medium transition-colors"
              >
                <Settings className="w-4 h-4" />
                Go to Settings
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

