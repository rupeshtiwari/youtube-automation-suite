import { useQuery } from '@tanstack/react-query'
import api from '@/lib/api'
import { 
  Video, 
  Folder,
  Download,
  Play,
  AlertCircle,
  X,
  ArrowUp
} from 'lucide-react'
import { useState } from 'react'

interface ShortsFolder {
  name: string
  count: number
  path: string
  role?: string
  interviewTypes?: string[]
}

interface ShortsLibraryData {
  folders: ShortsFolder[]
  total_videos: number
}

// Senior roles priority (higher = shows first)
const SENIOR_ROLES = {
  'SPO': 5,
  'SPM': 5,
  'Director': 4,
  'VP': 4,
  'TPM': 3,
  'Manager': 2,
  'Architect': 2,
  'Engineer': 1,
  'SRE': 1,
  'SWE': 1,
  'Other': 0
}

// Extract role and interview types from folder name
function extractMetadata(name: string): { role: string; interviewTypes: string[] } {
  const roles = ['SPO', 'SPM', 'VP', 'Director', 'TPM', 'Manager', 'Architect', 'SRE', 'SWE', 'Engineer']
  const interviewTypes = [
    'System Design',
    'Behavioral',
    'Technical',
    'Communication',
    'Coding',
    'Design',
    'Leadership',
    'Mock Interview',
    'Outage Mastery',
    'Concepts',
    'Patterns',
    'Strategy',
    'Growth',
    'Impact'
  ]

  let detectedRole = 'Other'
  const detectedTypes: string[] = []

  // Find role - check for exact matches first (like "SPO" or "SPM")
  for (const role of roles) {
    const roleRegex = new RegExp(`\\b${role}\\b`, 'i')
    if (roleRegex.test(name)) {
      detectedRole = role
      break
    }
  }

  // Find interview types
  for (const type of interviewTypes) {
    if (name.toLowerCase().includes(type.toLowerCase())) {
      detectedTypes.push(type)
    }
  }

  return {
    role: detectedRole,
    interviewTypes: detectedTypes.length > 0 ? detectedTypes : ['General']
  }
}

export default function ShortsLibrary() {
  const [selectedFolder, setSelectedFolder] = useState<string | null>(null)
  const [selectedFilters, setSelectedFilters] = useState<Set<string>>(new Set())
  const [sortBy, setSortBy] = useState<'senior-first' | 'alphabetical'>('senior-first')
  
  const { data, isLoading, error } = useQuery<ShortsLibraryData>({
    queryKey: ['shorts-library'],
    queryFn: async () => {
      const response = await api.get('/shorts-library')
      // Enrich folders with metadata
      const enrichedFolders = response.data.folders.map((folder: ShortsFolder) => {
        const metadata = extractMetadata(folder.name)
        return {
          ...folder,
          role: metadata.role,
          interviewTypes: metadata.interviewTypes
        }
      })
      return {
        ...response.data,
        folders: enrichedFolders
      }
    },
  })

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
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-red-800 dark:text-red-200 font-medium">Error loading shorts library</p>
            <p className="text-red-700 dark:text-red-300 text-sm">
              {error ? (error as any).message : 'No data available'}
            </p>
          </div>
        </div>
      </div>
    )
  }

  const folders = data.folders || []
  const totalVideos = data.total_videos || 0
  
  // Get all unique roles and interview types
  const allRoles = [...new Set(folders.map(f => f.role).filter((role): role is string => !!role))]
  const allInterviewTypes = [...new Set(folders.flatMap(f => f.interviewTypes || []))]
  
  // Sort roles based on selected sort order
  const sortedRoles = [...allRoles].sort((a, b) => {
    if (sortBy === 'senior-first') {
      const priorityA = (SENIOR_ROLES as Record<string, number>)[a] ?? 0
      const priorityB = (SENIOR_ROLES as Record<string, number>)[b] ?? 0
      if (priorityA !== priorityB) {
        return priorityB - priorityA // Higher priority first
      }
    }
    return a.localeCompare(b) // Alphabetical fallback or primary sort
  })
  
  // Filter folders based on selected filters
  const filteredFolders = selectedFilters.size === 0
    ? folders
    : folders.filter(folder => {
        return Array.from(selectedFilters).some(filter => 
          folder.role === filter || folder.interviewTypes?.includes(filter)
        )
      })
  
  // Group folders by role
  const foldersByRole = sortedRoles.reduce((acc, role) => {
    acc[role] = filteredFolders.filter(f => f.role === role)
    return acc
  }, {} as Record<string, ShortsFolder[]>)
  
  const toggleFilter = (filter: string) => {
    const newFilters = new Set(selectedFilters)
    if (newFilters.has(filter)) {
      newFilters.delete(filter)
    } else {
      newFilters.add(filter)
    }
    setSelectedFilters(newFilters)
  }
  
  const clearFilters = () => {
    setSelectedFilters(new Set())
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold mb-2 flex items-center gap-2">
          <Video className="w-6 h-6 text-primary" />
          Shorts Library
        </h1>
        <p className="text-muted-foreground">Your downloaded YouTube Shorts organized by role and interview type</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-card border border-border rounded-lg p-4">
          <div className="text-3xl font-bold text-primary mb-1">{totalVideos}</div>
          <div className="text-sm text-muted-foreground">Total Videos Downloaded</div>
        </div>
        <div className="bg-card border border-border rounded-lg p-4">
          <div className="text-3xl font-bold text-green-600 mb-1">{folders.length}</div>
          <div className="text-sm text-muted-foreground">Total Playlists</div>
        </div>
        <div className="bg-card border border-border rounded-lg p-4">
          <div className="text-3xl font-bold text-blue-600 mb-1">{allRoles.length}</div>
          <div className="text-sm text-muted-foreground">Roles/Categories</div>
        </div>
      </div>

      {/* Sort Options */}
      <div className="flex items-center gap-3 bg-card border border-border rounded-lg p-4">
        <span className="text-sm font-medium text-foreground">Sort by:</span>
        <button
          onClick={() => setSortBy('senior-first')}
          className={`flex items-center gap-1 px-3 py-1.5 rounded-full text-sm font-medium transition-all ${
            sortBy === 'senior-first'
              ? 'bg-primary text-primary-foreground'
              : 'bg-secondary text-secondary-foreground hover:bg-secondary/80'
          }`}
        >
          <ArrowUp className="w-4 h-4" />
          Senior First
        </button>
        <button
          onClick={() => setSortBy('alphabetical')}
          className={`px-3 py-1.5 rounded-full text-sm font-medium transition-all ${
            sortBy === 'alphabetical'
              ? 'bg-primary text-primary-foreground'
              : 'bg-secondary text-secondary-foreground hover:bg-secondary/80'
          }`}
        >
          Alphabetical
        </button>
      </div>

      {/* Filter Tags */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">Filter by Role</h2>
          {selectedFilters.size > 0 && (
            <button
              onClick={clearFilters}
              className="text-xs text-primary hover:text-primary/80 font-medium flex items-center gap-1"
            >
              <X className="w-3 h-3" />
              Clear Filters
            </button>
          )}
        </div>
        <div className="flex flex-wrap gap-2">
          {sortedRoles.map(role => (
            <button
              key={role}
              onClick={() => toggleFilter(role)}
              className={`px-3 py-1.5 rounded-full text-sm font-medium transition-all ${
                selectedFilters.has(role)
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-secondary text-secondary-foreground hover:bg-secondary/80'
              }`}
            >
              {role}
            </button>
          ))}
        </div>
      </div>

      {/* Filter Tags by Interview Type */}
      <div className="space-y-3">
        <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">Filter by Interview Type</h2>
        <div className="flex flex-wrap gap-2">
          {allInterviewTypes.map((type: string) => (
            <button
              key={type}
              onClick={() => toggleFilter(type)}
              className={`px-3 py-1.5 rounded-full text-sm font-medium transition-all ${
                selectedFilters.has(type)
                  ? 'bg-blue-600 text-white'
                  : 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 hover:bg-blue-200 dark:hover:bg-blue-900/50'
              }`}
            >
              {type}
            </button>
          ))}
        </div>
      </div>

      {/* Folders Grouped by Role */}
      {filteredFolders.length === 0 ? (
        <div className="bg-card border border-border rounded-lg p-12 text-center">
          <Download className="w-12 h-12 text-muted-foreground mx-auto mb-3 opacity-50" />
          <p className="text-lg font-medium mb-2">No Shorts Found</p>
          <p className="text-muted-foreground mb-4">
            No playlists match your selected filters
          </p>
          <button
            onClick={clearFilters}
            className="text-primary hover:text-primary/80 font-medium text-sm"
          >
            Clear Filters
          </button>
        </div>
      ) : (
        <div className="space-y-8">
          {sortedRoles.map((role: string) => {
            const roleFolder = foldersByRole[role]
            if (roleFolder.length === 0) return null
            
            return (
              <div key={role} className="space-y-4">
                <div className="flex items-center gap-3 pb-3 border-b border-border">
                  <div className="flex-1">
                    <h2 className="text-lg font-semibold">{role}</h2>
                    <p className="text-sm text-muted-foreground">{roleFolder.length} playlist{roleFolder.length !== 1 ? 's' : ''}</p>
                  </div>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {roleFolder.map((folder: ShortsFolder) => (
                    <div
                      key={folder.path}
                      onClick={() => setSelectedFolder(selectedFolder === folder.path ? null : folder.path)}
                      className="bg-card border border-border rounded-lg p-4 cursor-pointer hover:border-primary/50 hover:bg-accent/50 transition-all"
                    >
                      <div className="flex items-start justify-between mb-3">
                        <Folder className="w-6 h-6 text-primary flex-shrink-0" />
                        <div className="text-xs bg-primary/10 text-primary px-2 py-1 rounded font-medium">
                          {folder.count} video{folder.count !== 1 ? 's' : ''}
                        </div>
                      </div>
                      
                      <h3 className="font-medium text-sm line-clamp-2 break-words mb-3">{folder.name}</h3>
                      
                      {/* Interview Type Tags */}
                      <div className="mb-3 flex flex-wrap gap-1">
                        {folder.interviewTypes?.map((type: string) => (
                          <span
                            key={type}
                            className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 cursor-pointer hover:bg-blue-200 dark:hover:bg-blue-900/50 transition-colors"
                            onClick={(e) => {
                              e.stopPropagation()
                              toggleFilter(type)
                            }}
                          >
                            {type}
                          </span>
                        ))}
                      </div>
                      
                      <div className="pt-3 border-t border-border">
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            window.open(`/view-shorts-folder?path=${encodeURIComponent(folder.path)}`, '_blank')
                          }}
                          className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded bg-primary/10 hover:bg-primary/20 text-primary text-sm font-medium transition-colors"
                        >
                          <Play className="w-4 h-4" />
                          View Videos
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
