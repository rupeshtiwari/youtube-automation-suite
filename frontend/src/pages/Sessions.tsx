import { useQuery } from '@tanstack/react-query'
import api from '@/lib/api'
import { 
  FileText, 
  Calendar, 
  Clock, 
  User, 
  CheckCircle2,
  BarChart3,
  Eye
} from 'lucide-react'

interface Session {
  filename: string
  date?: string
  client_name?: string
  role?: string
  type?: string
  status: string
  preview?: string
  has_content?: boolean
  modified?: string
  size?: number
  filepath?: string
}

interface SessionStats {
  total: number
  upcoming: number
  completed: number
  by_role: Record<string, number>
  by_type: Record<string, number>
}

interface SessionsData {
  sessions: Session[]
  statistics: SessionStats
  upcoming: Session[]
  recent: Session[]
  source: string
}

const ROLE_LABELS: Record<string, string> = {
  'swe': 'Software Engineer',
  'pm': 'Product Manager',
  'sa': 'Solutions Architect',
  'tpm': 'Technical Program Manager',
  'em': 'Engineering Manager',
  'mgr': 'Manager',
  'dir': 'Director',
  'vp': 'Vice President',
  'spo': 'Senior Product Owner',
  'spm': 'Senior Program Manager'
}

const TYPE_LABELS: Record<string, string> = {
  'system-design': 'System Design',
  'behavioral': 'Behavioral',
  'coding': 'Coding',
  'leadership': 'Leadership',
  'resume': 'Resume',
  'salary': 'Salary Negotiation',
  'interview': 'Interview Prep',
  'mock': 'Mock Interview'
}

export default function Sessions() {
  const { data, isLoading, error } = useQuery<SessionsData>({
    queryKey: ['sessions'],
    queryFn: async () => {
      const response = await api.get('/sessions')
      return response.data
    },
    retry: 1,
  })

  const formatDate = (dateStr?: string) => {
    if (!dateStr) return 'No date'
    try {
      const date = new Date(dateStr)
      return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric',
        weekday: 'short'
      })
    } catch {
      return dateStr
    }
  }

  const formatFileSize = (bytes?: number) => {
    if (!bytes) return 'Unknown size'
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <p className="text-red-800 dark:text-red-200">
            Error loading sessions: {error instanceof Error ? error.message : 'Unknown error'}
          </p>
        </div>
      </div>
    )
  }

  if (!data || !data.sessions) {
    return (
      <div className="p-6">
        <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
          <p className="text-yellow-800 dark:text-yellow-200">
            Sessions folder not found. Please check the path configuration.
          </p>
          <p className="text-sm text-yellow-700 dark:text-yellow-300 mt-2">
            Expected folder: <code className="bg-yellow-100 dark:bg-yellow-900/40 px-1 rounded">data/sessions</code>
          </p>
        </div>
      </div>
    )
  }

  const stats = data.statistics || {}
  const upcoming = data.upcoming || []
  const recent = data.recent || []

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold mb-2">Mentoring Sessions</h1>
        <p className="text-muted-foreground">
          Manage and view your coaching sessions
          {data.source && (
            <span className="ml-2 text-xs bg-muted px-2 py-0.5 rounded">
              Source: {data.source}
            </span>
          )}
        </p>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-card border border-border rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Total Sessions</p>
              <p className="text-2xl font-bold">{stats.total || 0}</p>
            </div>
            <FileText className="w-8 h-8 text-primary opacity-50" />
          </div>
        </div>

        <div className="bg-card border border-border rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Upcoming</p>
              <p className="text-2xl font-bold text-blue-600">{stats.upcoming || 0}</p>
            </div>
            <Clock className="w-8 h-8 text-blue-600 opacity-50" />
          </div>
        </div>

        <div className="bg-card border border-border rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Completed</p>
              <p className="text-2xl font-bold text-green-600">{stats.completed || 0}</p>
            </div>
            <CheckCircle2 className="w-8 h-8 text-green-600 opacity-50" />
          </div>
        </div>

        <div className="bg-card border border-border rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Top Role</p>
              <p className="text-lg font-semibold">
                {stats.by_role && Object.keys(stats.by_role).length > 0
                  ? ROLE_LABELS[Object.entries(stats.by_role).sort((a, b) => b[1] - a[1])[0][0]] || 
                    Object.entries(stats.by_role).sort((a, b) => b[1] - a[1])[0][0]
                  : 'N/A'}
              </p>
            </div>
            <User className="w-8 h-8 text-purple-600 opacity-50" />
          </div>
        </div>
      </div>

      {/* Upcoming Sessions */}
      {upcoming.length > 0 && (
        <div className="bg-card border border-border rounded-lg p-6">
          <div className="flex items-center gap-2 mb-4">
            <Calendar className="w-5 h-5 text-blue-600" />
            <h2 className="text-xl font-semibold">Upcoming Sessions</h2>
            <span className="ml-auto px-2 py-1 text-xs bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded-full">
              {upcoming.length}
            </span>
          </div>

          <div className="space-y-3">
            {upcoming.map((session, idx) => (
              <div
                key={idx}
                className="border border-border rounded-lg p-4 hover:bg-accent/50 transition-colors"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-2">
                      <h3 className="font-semibold">
                        {session.client_name || session.filename}
                      </h3>
                      {session.role && (
                        <span className="px-2 py-0.5 text-xs bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 rounded">
                          {ROLE_LABELS[session.role] || session.role}
                        </span>
                      )}
                      {session.type && (
                        <span className="px-2 py-0.5 text-xs bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded">
                          {TYPE_LABELS[session.type] || session.type}
                        </span>
                      )}
                    </div>
                    <div className="flex items-center gap-4 text-sm text-muted-foreground">
                      <span className="flex items-center gap-1">
                        <Calendar className="w-4 h-4" />
                        {formatDate(session.date)}
                      </span>
                      <span className="flex items-center gap-1">
                        <FileText className="w-4 h-4" />
                        {session.filename}
                      </span>
                    </div>
                    {session.preview && (
                      <p className="mt-2 text-sm text-muted-foreground line-clamp-2">
                        {session.preview.substring(0, 200)}...
                      </p>
                    )}
                  </div>
                  <button className="px-3 py-1.5 text-sm border border-border rounded-md hover:bg-accent transition-colors flex items-center gap-1">
                    <Eye className="w-4 h-4" />
                    View
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recent Sessions */}
      {recent.length > 0 && (
        <div className="bg-card border border-border rounded-lg p-6">
          <div className="flex items-center gap-2 mb-4">
            <Clock className="w-5 h-5 text-green-600" />
            <h2 className="text-xl font-semibold">Recent Sessions</h2>
            <span className="ml-auto px-2 py-1 text-xs bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 rounded-full">
              {recent.length}
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {recent.map((session, idx) => (
              <div
                key={idx}
                className="border border-border rounded-lg p-4 hover:bg-accent/50 transition-colors"
              >
                <div className="flex items-start justify-between gap-2 mb-2">
                  <h3 className="font-semibold text-sm truncate">
                    {session.client_name || session.filename}
                  </h3>
                  <CheckCircle2 className="w-4 h-4 text-green-600 flex-shrink-0" />
                </div>
                <div className="flex items-center gap-2 mb-2 flex-wrap">
                  {session.role && (
                    <span className="px-2 py-0.5 text-xs bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 rounded">
                      {ROLE_LABELS[session.role] || session.role}
                    </span>
                  )}
                  {session.type && (
                    <span className="px-2 py-0.5 text-xs bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded">
                      {TYPE_LABELS[session.type] || session.type}
                    </span>
                  )}
                </div>
                <div className="text-xs text-muted-foreground">
                  <span>{formatDate(session.date)}</span>
                  {session.size && (
                    <span className="ml-2">• {formatFileSize(session.size)}</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* All Sessions Table */}
      {data.sessions && data.sessions.length > 0 && (
        <div className="bg-card border border-border rounded-lg p-6">
          <div className="flex items-center gap-2 mb-4">
            <BarChart3 className="w-5 h-5" />
            <h2 className="text-xl font-semibold">All Sessions</h2>
            <span className="ml-auto px-2 py-1 text-xs bg-muted rounded-full">
              {data.sessions.length}
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left p-2 font-medium">Filename</th>
                  <th className="text-left p-2 font-medium">Date</th>
                  <th className="text-left p-2 font-medium">Client</th>
                  <th className="text-left p-2 font-medium">Role</th>
                  <th className="text-left p-2 font-medium">Type</th>
                  <th className="text-left p-2 font-medium">Status</th>
                  <th className="text-left p-2 font-medium">Size</th>
                </tr>
              </thead>
              <tbody>
                {data.sessions.map((session, idx) => (
                  <tr key={idx} className="border-b border-border hover:bg-accent/50">
                    <td className="p-2">
                      <div className="flex items-center gap-2">
                        <FileText className="w-4 h-4 text-muted-foreground" />
                        <span className="truncate max-w-xs">{session.filename}</span>
                      </div>
                    </td>
                    <td className="p-2">{formatDate(session.date)}</td>
                    <td className="p-2">{session.client_name || '-'}</td>
                    <td className="p-2">
                      {session.role && (
                        <span className="px-2 py-0.5 text-xs bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 rounded">
                          {ROLE_LABELS[session.role] || session.role}
                        </span>
                      )}
                    </td>
                    <td className="p-2">
                      {session.type && (
                        <span className="px-2 py-0.5 text-xs bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded">
                          {TYPE_LABELS[session.type] || session.type}
                        </span>
                      )}
                    </td>
                    <td className="p-2">
                      {session.status === 'upcoming' ? (
                        <span className="px-2 py-0.5 text-xs bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded flex items-center gap-1 w-fit">
                          <Clock className="w-3 h-3" />
                          Upcoming
                        </span>
                      ) : session.status === 'completed' ? (
                        <span className="px-2 py-0.5 text-xs bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 rounded flex items-center gap-1 w-fit">
                          <CheckCircle2 className="w-3 h-3" />
                          Completed
                        </span>
                      ) : (
                        <span className="px-2 py-0.5 text-xs bg-muted rounded">Unknown</span>
                      )}
                    </td>
                    <td className="p-2 text-muted-foreground">{formatFileSize(session.size)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Empty State */}
      {(!data.sessions || data.sessions.length === 0) && (
        <div className="bg-card border border-border rounded-lg p-12 text-center">
          <FileText className="w-16 h-16 mx-auto mb-4 text-muted-foreground opacity-50" />
          <h3 className="text-lg font-semibold mb-2">No Sessions Found</h3>
          <p className="text-muted-foreground mb-4">
            No session files found in the configured folder.
          </p>
          <a
            href="/docs/SESSION_FOLDER_STRUCTURE.md"
            target="_blank"
            className="text-primary hover:underline text-sm"
          >
            Learn about recommended folder structure →
          </a>
        </div>
      )}
    </div>
  )
}
