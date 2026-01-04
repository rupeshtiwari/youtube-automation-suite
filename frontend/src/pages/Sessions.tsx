import { useEffect, useMemo, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import api from '@/lib/api'
import {
  FileText,
  Calendar,
  Clock,
  User,
  CheckCircle2,
  BarChart3,
  Eye,
  PlayCircle,
  MessageSquare,
  Mail,
  Link,
  FileAudio,
  Loader2,
  Save,
  Sparkles,
} from 'lucide-react'
import type { LucideIcon } from 'lucide-react'

interface LinkedResources {
  recording: boolean
  transcript: boolean
  chatgpt: boolean
  email: boolean
}

interface SessionMetadata {
  id?: number
  filename?: string
  role?: string | null
  session_type?: string | null
  client_name?: string | null
  session_date?: string | null
  meet_recording_url?: string | null
  meet_recording_drive_id?: string | null
  gemini_transcript_url?: string | null
  gemini_transcript_drive_id?: string | null
  chatgpt_notes?: string | null
  email_thread_id?: string | null
  email_subject?: string | null
  additional_notes?: string | null
  tags?: string | null
  created_at?: string | null
  updated_at?: string | null
}

type SessionMetadataForm = {
  role?: string | null
  session_type?: string | null
  client_name?: string | null
  session_date?: string | null
  meet_recording_url?: string | null
  meet_recording_drive_id?: string | null
  gemini_transcript_url?: string | null
  gemini_transcript_drive_id?: string | null
  chatgpt_notes?: string | null
  email_thread_id?: string | null
  email_subject?: string | null
  additional_notes?: string | null
  tags?: string | null
}

interface Session {
  filename: string
  date?: string
  session_date?: string
  client_name?: string
  role?: string
  type?: string
  status: string
  preview?: string
  has_content?: boolean
  modified?: string
  size?: number
  filepath?: string
  meet_recording_url?: string | null
  gemini_transcript_url?: string | null
  chatgpt_notes?: string | null
  email_thread_id?: string | null
  email_subject?: string | null
  linked_resources?: LinkedResources
  metadata?: SessionMetadata
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

interface SessionDetail {
  filename: string
  content?: string
  metadata?: SessionMetadata | null
}

const ROLE_LABELS: Record<string, string> = {
  swe: 'Software Engineer',
  pm: 'Product Manager',
  sa: 'Solutions Architect',
  tpm: 'Technical Program Manager',
  em: 'Engineering Manager',
  mgr: 'Manager',
  dir: 'Director',
  vp: 'Vice President',
  spo: 'Senior Product Owner',
  spm: 'Senior Program Manager',
}

const TYPE_LABELS: Record<string, string> = {
  'system-design': 'System Design',
  behavioral: 'Behavioral',
  coding: 'Coding',
  leadership: 'Leadership',
  resume: 'Resume',
  salary: 'Salary Negotiation',
  interview: 'Interview Prep',
  mock: 'Mock Interview',
}

const DEFAULT_LINKED_RESOURCES: LinkedResources = {
  recording: false,
  transcript: false,
  chatgpt: false,
  email: false,
}

function ResourcePill({
  label,
  active,
  icon: Icon,
  tone = 'blue',
  compact = false,
}: {
  label: string
  active?: boolean
  icon: LucideIcon
  tone?: 'blue' | 'green' | 'purple' | 'amber'
  compact?: boolean
}) {
  const toneStyles: Record<string, string> = {
    blue: 'bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-200',
    green: 'bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-200',
    purple: 'bg-purple-100 text-purple-700 dark:bg-purple-900/40 dark:text-purple-200',
    amber: 'bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-200',
  }

  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full border border-border ${
        compact ? 'px-2 py-1 text-[11px]' : 'px-2.5 py-1.5 text-xs'
      } ${active ? toneStyles[tone] : 'bg-muted text-muted-foreground'}`}
    >
      <Icon className={compact ? 'h-3.5 w-3.5' : 'h-4 w-4'} />
      {label}
    </span>
  )
}

function InfoRow({ label, value }: { label: string; value?: string | null }) {
  return (
    <div>
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="text-sm font-medium text-foreground">{value || 'Not provided'}</p>
    </div>
  )
}

const formatDate = (dateStr?: string | null) => {
  if (!dateStr) return 'No date'
  try {
    const date = new Date(dateStr)
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      weekday: 'short',
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

const getRecordingEmbedUrl = (url?: string | null) => {
  if (!url) return null

  if (url.includes('drive.google.com')) {
    const idMatch = url.match(/\/d\/([a-zA-Z0-9_-]+)/) || url.match(/id=([a-zA-Z0-9_-]+)/)
    const fileId = idMatch ? idMatch[1] : null
    return fileId ? `https://drive.google.com/file/d/${fileId}/preview` : url
  }

  return url
}

export default function Sessions() {
  const queryClient = useQueryClient()
  const [selectedFilename, setSelectedFilename] = useState<string | null>(null)
  const [metadataForm, setMetadataForm] = useState<SessionMetadataForm>({})
  const [saveMessage, setSaveMessage] = useState<string | null>(null)

  const { data, isLoading, error } = useQuery<SessionsData>({
    queryKey: ['sessions'],
    queryFn: async () => {
      const response = await api.get('/sessions')
      return response.data
    },
    retry: 1,
  })

  const resourceComplete = useMemo(() => {
    if (!data?.sessions) return 0
    return data.sessions.filter((session) => {
      const linked = session.linked_resources || DEFAULT_LINKED_RESOURCES
      return linked.recording && linked.transcript && linked.chatgpt && linked.email
    }).length
  }, [data?.sessions])

  useEffect(() => {
    if (!selectedFilename && data?.sessions?.length) {
      setSelectedFilename(data.sessions[0].filename)
    }
  }, [data?.sessions, selectedFilename])

  const selectedSession = useMemo(
    () => data?.sessions?.find((session) => session.filename === selectedFilename),
    [data?.sessions, selectedFilename]
  )

  const { data: sessionDetail, isLoading: isDetailLoading } = useQuery<SessionDetail | null>({
    queryKey: ['session-detail', selectedFilename],
    queryFn: async () => {
      if (!selectedFilename) return null
      const [contentRes, metadataRes] = await Promise.all([
        api.get(`/sessions/${selectedFilename}`),
        api.get(`/sessions/${selectedFilename}/metadata`),
      ])

      return {
        filename: selectedFilename,
        content: contentRes.data?.content,
        metadata: metadataRes.data?.metadata || contentRes.data?.metadata || null,
      }
    },
    enabled: Boolean(selectedFilename),
    staleTime: 30000,
  })

  useEffect(() => {
    if (!selectedSession) return

    const metadata = sessionDetail?.metadata || selectedSession.metadata
    setMetadataForm({
      role: metadata?.role ?? selectedSession.role ?? '',
      session_type: metadata?.session_type ?? selectedSession.type ?? '',
      client_name: metadata?.client_name ?? selectedSession.client_name ?? '',
      session_date: metadata?.session_date ?? selectedSession.session_date ?? selectedSession.date ?? '',
      meet_recording_url: metadata?.meet_recording_url ?? selectedSession.meet_recording_url ?? '',
      meet_recording_drive_id: metadata?.meet_recording_drive_id ?? '',
      gemini_transcript_url: metadata?.gemini_transcript_url ?? selectedSession.gemini_transcript_url ?? '',
      gemini_transcript_drive_id: metadata?.gemini_transcript_drive_id ?? '',
      chatgpt_notes: metadata?.chatgpt_notes ?? selectedSession.chatgpt_notes ?? '',
      email_thread_id: metadata?.email_thread_id ?? selectedSession.email_thread_id ?? '',
      email_subject: metadata?.email_subject ?? selectedSession.email_subject ?? '',
      additional_notes: metadata?.additional_notes ?? '',
      tags: metadata?.tags ?? '',
    })
  }, [selectedSession, sessionDetail?.metadata])

  const metadataMutation = useMutation({
    mutationFn: async (payload: SessionMetadataForm) => {
      if (!selectedFilename) throw new Error('No session selected')
      return api.put(`/sessions/${selectedFilename}/metadata`, payload)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sessions'] })
      queryClient.invalidateQueries({ queryKey: ['session-detail', selectedFilename] })
    },
  })

  const handleSaveMetadata = async () => {
    setSaveMessage(null)
    try {
      await metadataMutation.mutateAsync(metadataForm)
      setSaveMessage('Session context saved. Your recording, transcript, chat, and email links are now tied to this session.')
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unable to save metadata'
      setSaveMessage(message)
    }
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

  const stats = data.statistics || ({} as SessionStats)
  const upcoming = data.upcoming || []
  const recent = data.recent || []
  const selectedMetadata = sessionDetail?.metadata || selectedSession?.metadata
  const displayDate = selectedSession?.session_date || selectedSession?.date
  const resourceStatus = selectedSession?.linked_resources || DEFAULT_LINKED_RESOURCES
  const transcriptText = sessionDetail?.content || selectedSession?.preview || ''
  const recordingLink = selectedMetadata?.meet_recording_url || metadataForm.meet_recording_url
  const transcriptLink = selectedMetadata?.gemini_transcript_url || metadataForm.gemini_transcript_url
  const gmailLink = selectedMetadata?.email_thread_id
    ? `https://mail.google.com/mail/u/0/#inbox/${selectedMetadata.email_thread_id}`
    : undefined

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <h1 className="text-2xl font-bold mb-1">Mentoring Sessions</h1>
          <p className="text-muted-foreground">
            One-page view of your recordings, transcripts, ChatGPT notes, and scheduling emails
            {data.source && (
              <span className="ml-2 text-xs bg-muted px-2 py-0.5 rounded">Source: {data.source}</span>
            )}
          </p>
        </div>
        <div className="flex gap-2 flex-wrap">
          <ResourcePill label="Recording" active icon={PlayCircle} tone="green" compact />
          <ResourcePill label="Transcript" active icon={FileAudio} tone="purple" compact />
          <ResourcePill label="ChatGPT" active icon={MessageSquare} tone="blue" compact />
          <ResourcePill label="Email" active icon={Mail} tone="amber" compact />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
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

        <div className="bg-card border border-border rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Fully Linked Sessions</p>
              <p className="text-2xl font-bold text-emerald-600">{resourceComplete}</p>
            </div>
            <Sparkles className="w-8 h-8 text-emerald-600 opacity-50" />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <div className="xl:col-span-1 space-y-3">
          <div className="flex items-center gap-2">
            <h2 className="text-lg font-semibold">Session library</h2>
            <span className="px-2 py-0.5 text-xs bg-muted rounded-full">{data.sessions.length}</span>
          </div>
          <div className="bg-card border border-border rounded-lg divide-y divide-border">
            {data.sessions.map((session) => {
              const isSelected = session.filename === selectedFilename
              const linked = session.linked_resources || DEFAULT_LINKED_RESOURCES
              return (
                <button
                  key={session.filename}
                  className={`w-full text-left p-4 transition-colors ${
                    isSelected ? 'bg-primary/5 border-l-2 border-primary' : 'hover:bg-accent/60'
                  }`}
                  onClick={() => setSelectedFilename(session.filename)}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <h3 className="font-semibold text-sm truncate max-w-[220px]">
                          {session.client_name || session.filename}
                        </h3>
                        {session.status === 'completed' && (
                          <CheckCircle2 className="w-4 h-4 text-green-600 flex-shrink-0" />
                        )}
                      </div>
                      <div className="flex flex-wrap items-center gap-1 text-[12px] text-muted-foreground">
                        {(session.session_date || session.date) && (
                          <span>{formatDate(session.session_date || session.date)}</span>
                        )}
                        {session.role && (
                          <span className="px-2 py-0.5 rounded-full bg-purple-100 dark:bg-purple-900/40 text-purple-700 dark:text-purple-200">
                            {ROLE_LABELS[session.role] || session.role}
                          </span>
                        )}
                        {session.type && (
                          <span className="px-2 py-0.5 rounded-full bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-200">
                            {TYPE_LABELS[session.type] || session.type}
                          </span>
                        )}
                      </div>
                      {session.preview && (
                        <p className="text-xs text-muted-foreground line-clamp-2">{session.preview}</p>
                      )}
                      <div className="flex flex-wrap gap-1 mt-1">
                        <ResourcePill label="Rec" active={linked.recording} icon={PlayCircle} tone="green" compact />
                        <ResourcePill label="Tx" active={linked.transcript} icon={FileAudio} tone="purple" compact />
                        <ResourcePill label="Chat" active={linked.chatgpt} icon={MessageSquare} tone="blue" compact />
                        <ResourcePill label="Email" active={linked.email} icon={Mail} tone="amber" compact />
                      </div>
                    </div>
                    <Eye className="w-4 h-4 text-muted-foreground" />
                  </div>
                </button>
              )
            })}
          </div>
        </div>

        <div className="xl:col-span-2 space-y-4">
          <div className="bg-card border border-border rounded-lg p-5 space-y-4">
            <div className="flex items-start justify-between gap-4">
              <div className="space-y-1">
                <p className="text-xs text-muted-foreground">Selected session</p>
                <h2 className="text-xl font-semibold">
                  {selectedSession?.client_name || selectedSession?.filename || 'Choose a session to view details'}
                </h2>
                <div className="flex flex-wrap gap-2 text-sm text-muted-foreground">
                  <span className="flex items-center gap-1">
                    <Calendar className="w-4 h-4" />
                    {formatDate(displayDate)}
                  </span>
                  {selectedSession?.role && (
                    <span className="flex items-center gap-1">
                      <User className="w-4 h-4" />
                      {ROLE_LABELS[selectedSession.role] || selectedSession.role}
                    </span>
                  )}
                  {selectedSession?.type && (
                    <span className="flex items-center gap-1">
                      <BarChart3 className="w-4 h-4" />
                      {TYPE_LABELS[selectedSession.type] || selectedSession.type}
                    </span>
                  )}
                  {selectedSession?.size && <span>{formatFileSize(selectedSession.size)}</span>}
                </div>
              </div>
              <div className="flex flex-wrap gap-2 justify-end">
                <ResourcePill label="Recording" active={resourceStatus.recording} icon={PlayCircle} tone="green" />
                <ResourcePill label="Transcript" active={resourceStatus.transcript} icon={FileAudio} tone="purple" />
                <ResourcePill label="ChatGPT" active={resourceStatus.chatgpt} icon={MessageSquare} tone="blue" />
                <ResourcePill label="Email" active={resourceStatus.email} icon={Mail} tone="amber" />
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <InfoRow label="Client" value={selectedMetadata?.client_name || selectedSession?.client_name} />
              <InfoRow label="Session type" value={TYPE_LABELS[selectedSession?.type || ''] || selectedSession?.type} />
              <InfoRow label="Tags" value={selectedMetadata?.tags} />
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div className="bg-card border border-border rounded-lg p-4 space-y-3">
              <div className="flex items-center gap-2">
                <PlayCircle className="w-5 h-5 text-green-600" />
                <h3 className="font-semibold">Recording</h3>
              </div>
              {recordingLink ? (
                <div className="space-y-3">
                  <div className="aspect-video w-full overflow-hidden rounded-lg border border-border bg-muted">
                    <iframe
                      src={getRecordingEmbedUrl(recordingLink) || recordingLink}
                      className="w-full h-full"
                      allow="autoplay; encrypted-media"
                      allowFullScreen
                      title="Session recording preview"
                    />
                  </div>
                  <a
                    href={recordingLink}
                    target="_blank"
                    className="inline-flex items-center gap-2 text-sm text-primary hover:underline"
                    rel="noreferrer"
                  >
                    <Link className="w-4 h-4" /> Open recording in new tab
                  </a>
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">
                  Link your Google Meet or Drive recording to preview it here.
                </p>
              )}
            </div>

            <div className="bg-card border border-border rounded-lg p-4 space-y-3">
              <div className="flex items-center gap-2">
                <FileAudio className="w-5 h-5 text-purple-600" />
                <h3 className="font-semibold">Transcript</h3>
              </div>
              <div className="border border-border rounded-lg bg-muted/50 p-3 h-48 overflow-y-auto text-sm whitespace-pre-wrap">
                {isDetailLoading ? (
                  <div className="flex items-center justify-center h-full text-muted-foreground">
                    <Loader2 className="w-5 h-5 animate-spin" />
                  </div>
                ) : transcriptText ? (
                  transcriptText
                ) : (
                  <span className="text-muted-foreground">No transcript uploaded yet.</span>
                )}
              </div>
              {transcriptLink && (
                <a
                  href={transcriptLink}
                  target="_blank"
                  className="inline-flex items-center gap-2 text-sm text-primary hover:underline"
                  rel="noreferrer"
                >
                  <Link className="w-4 h-4" /> Open Gemini/Drive transcript
                </a>
              )}
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div className="bg-card border border-border rounded-lg p-4 space-y-3">
              <div className="flex items-center gap-2">
                <MessageSquare className="w-5 h-5 text-blue-600" />
                <h3 className="font-semibold">ChatGPT session notes</h3>
              </div>
              <div className="border border-border rounded-lg bg-muted/40 p-3 h-48 overflow-y-auto text-sm whitespace-pre-wrap">
                {selectedMetadata?.chatgpt_notes || metadataForm.chatgpt_notes ? (
                  selectedMetadata?.chatgpt_notes || metadataForm.chatgpt_notes
                ) : (
                  <span className="text-muted-foreground">
                    Paste your ChatGPT or coaching notes so they stay with this session.
                  </span>
                )}
              </div>
            </div>

            <div className="bg-card border border-border rounded-lg p-4 space-y-3">
              <div className="flex items-center gap-2">
                <Mail className="w-5 h-5 text-amber-600" />
                <h3 className="font-semibold">Scheduling email</h3>
              </div>
              <div className="space-y-2 text-sm">
                <InfoRow label="Email subject" value={selectedMetadata?.email_subject || metadataForm.email_subject} />
                <InfoRow label="Thread ID" value={selectedMetadata?.email_thread_id || metadataForm.email_thread_id} />
                {gmailLink ? (
                  <a
                    href={gmailLink}
                    target="_blank"
                    className="inline-flex items-center gap-2 text-primary hover:underline"
                    rel="noreferrer"
                  >
                    <Link className="w-4 h-4" /> Open Gmail thread
                  </a>
                ) : (
                  <p className="text-muted-foreground text-sm">
                    Add the Gmail thread ID to jump back to the scheduling email.
                  </p>
                )}
              </div>
            </div>
          </div>

          <div className="bg-card border border-border rounded-lg p-5 space-y-4">
            <div className="flex items-start justify-between gap-4">
              <div>
                <h3 className="font-semibold">Link your sources</h3>
                <p className="text-sm text-muted-foreground">
                  Drop in the recording, transcript, chat notes, and email info for this mentoring session.
                </p>
              </div>
              <button
                onClick={handleSaveMetadata}
                disabled={metadataMutation.isPending || !selectedFilename}
                className="inline-flex items-center gap-2 px-3 py-2 rounded-md bg-primary text-primary-foreground text-sm font-medium shadow-sm disabled:opacity-70"
              >
                {metadataMutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
                Save session context
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Client name</label>
                <input
                  type="text"
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  value={metadataForm.client_name || ''}
                  onChange={(e) => setMetadataForm((prev) => ({ ...prev, client_name: e.target.value }))}
                  placeholder="e.g. Jane Doe"
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Session date</label>
                <input
                  type="date"
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  value={metadataForm.session_date || ''}
                  onChange={(e) => setMetadataForm((prev) => ({ ...prev, session_date: e.target.value }))}
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Role</label>
                <input
                  type="text"
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  value={metadataForm.role || ''}
                  onChange={(e) => setMetadataForm((prev) => ({ ...prev, role: e.target.value }))}
                  placeholder="swe, pm, em, etc."
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Session type</label>
                <input
                  type="text"
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  value={metadataForm.session_type || ''}
                  onChange={(e) => setMetadataForm((prev) => ({ ...prev, session_type: e.target.value }))}
                  placeholder="system-design, behavioral, mock"
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Google Meet / Drive recording URL</label>
                <input
                  type="url"
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  value={metadataForm.meet_recording_url || ''}
                  onChange={(e) => setMetadataForm((prev) => ({ ...prev, meet_recording_url: e.target.value }))}
                  placeholder="https://drive.google.com/file/d/..."
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Recording file ID (optional)</label>
                <input
                  type="text"
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  value={metadataForm.meet_recording_drive_id || ''}
                  onChange={(e) => setMetadataForm((prev) => ({ ...prev, meet_recording_drive_id: e.target.value }))}
                  placeholder="Google Drive file id"
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Transcript URL</label>
                <input
                  type="url"
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  value={metadataForm.gemini_transcript_url || ''}
                  onChange={(e) => setMetadataForm((prev) => ({ ...prev, gemini_transcript_url: e.target.value }))}
                  placeholder="Gemini / Drive transcript link"
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Transcript file ID (optional)</label>
                <input
                  type="text"
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  value={metadataForm.gemini_transcript_drive_id || ''}
                  onChange={(e) => setMetadataForm((prev) => ({ ...prev, gemini_transcript_drive_id: e.target.value }))}
                  placeholder="Drive transcript id"
                />
              </div>
              <div className="space-y-2 md:col-span-2">
                <label className="text-sm font-medium">ChatGPT session notes</label>
                <textarea
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm min-h-[96px]"
                  value={metadataForm.chatgpt_notes || ''}
                  onChange={(e) => setMetadataForm((prev) => ({ ...prev, chatgpt_notes: e.target.value }))}
                  placeholder="Paste your ChatGPT chat log, insights, or action items"
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Email subject</label>
                <input
                  type="text"
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  value={metadataForm.email_subject || ''}
                  onChange={(e) => setMetadataForm((prev) => ({ ...prev, email_subject: e.target.value }))}
                  placeholder="Mentoring session scheduled..."
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Gmail thread ID</label>
                <input
                  type="text"
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  value={metadataForm.email_thread_id || ''}
                  onChange={(e) => setMetadataForm((prev) => ({ ...prev, email_thread_id: e.target.value }))}
                  placeholder="Paste the Gmail thread id"
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Tags</label>
                <input
                  type="text"
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  value={metadataForm.tags || ''}
                  onChange={(e) => setMetadataForm((prev) => ({ ...prev, tags: e.target.value }))}
                  placeholder="leadership, system design, pm"
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Additional notes</label>
                <textarea
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm min-h-[96px]"
                  value={metadataForm.additional_notes || ''}
                  onChange={(e) => setMetadataForm((prev) => ({ ...prev, additional_notes: e.target.value }))}
                  placeholder="Any prep reminders or follow-ups"
                />
              </div>
            </div>

            {saveMessage && (
              <div className="text-sm text-muted-foreground bg-muted/50 border border-border rounded-md px-3 py-2">
                {saveMessage}
              </div>
            )}
          </div>
        </div>
      </div>

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
                  {session.size && <span className="ml-2">• {formatFileSize(session.size)}</span>}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

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
                  <th className="text-left p-2 font-medium">Sources</th>
                  <th className="text-left p-2 font-medium">Size</th>
                </tr>
              </thead>
              <tbody>
                {data.sessions.map((session, idx) => {
                  const linked = session.linked_resources || DEFAULT_LINKED_RESOURCES
                  return (
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
                      <td className="p-2">
                        <div className="flex flex-wrap gap-1">
                          <ResourcePill label="R" active={linked.recording} icon={PlayCircle} tone="green" compact />
                          <ResourcePill label="T" active={linked.transcript} icon={FileAudio} tone="purple" compact />
                          <ResourcePill label="C" active={linked.chatgpt} icon={MessageSquare} tone="blue" compact />
                          <ResourcePill label="E" active={linked.email} icon={Mail} tone="amber" compact />
                        </div>
                      </td>
                      <td className="p-2 text-muted-foreground">{formatFileSize(session.size)}</td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

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
