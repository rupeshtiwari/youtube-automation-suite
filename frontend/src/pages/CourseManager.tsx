import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '@/lib/api'
import {
  BookOpen,
  FolderOpen,
  Music,
  Plus,
  ChevronDown,
  ChevronRight,
  Trash2,
  X
} from 'lucide-react'

interface Track {
  id: string
  name: string
  audio_file: string
  duration?: number
  created_at: string
}

interface Module {
  id: string
  name: string
  description?: string
  tracks: Track[]
  created_at: string
}

interface Course {
  id: string
  name: string
  description?: string
  modules: Module[]
  created_at: string
}

export default function CourseManager() {
  const [expandedCourses, setExpandedCourses] = useState<Set<string>>(new Set())
  const [expandedModules, setExpandedModules] = useState<Set<string>>(new Set())
  const [showCreateCourse, setShowCreateCourse] = useState(false)
  const [showCreateModule, setShowCreateModule] = useState<string | null>(null)
  const [showAddTrack, setShowAddTrack] = useState<string | null>(null)
  const [newCourseName, setNewCourseName] = useState('')
  const [newCourseDesc, setNewCourseDesc] = useState('')
  const [newModuleName, setNewModuleName] = useState('')
  const [newModuleDesc, setNewModuleDesc] = useState('')
  const [trackText, setTrackText] = useState('')
  const [trackName, setTrackName] = useState('')

  const queryClient = useQueryClient()

  // Fetch courses
  const { data: courses, isLoading } = useQuery<Course[]>({
    queryKey: ['courses'],
    queryFn: async () => {
      const response = await api.get('/courses')
      return response.data.courses || []
    },
  })

  // Create course mutation
  const createCourseMutation = useMutation({
    mutationFn: async (data: { name: string; description: string }) => {
      const response = await api.post('/courses', data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['courses'] })
      setShowCreateCourse(false)
      setNewCourseName('')
      setNewCourseDesc('')
    },
  })

  // Create module mutation
  const createModuleMutation = useMutation({
    mutationFn: async (data: { courseId: string; name: string; description: string }) => {
      const response = await api.post(`/courses/${data.courseId}/modules`, {
        name: data.name,
        description: data.description,
      })
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['courses'] })
      setShowCreateModule(null)
      setNewModuleName('')
      setNewModuleDesc('')
    },
  })

  // Create track mutation
  const createTrackMutation = useMutation({
    mutationFn: async (data: { moduleId: string; name: string; text: string }) => {
      const response = await api.post(`/modules/${data.moduleId}/tracks`, {
        name: data.name,
        text: data.text,
      })
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['courses'] })
      setShowAddTrack(null)
      setTrackText('')
      setTrackName('')
    },
  })

  // Delete course mutation
  const deleteCourseMutation = useMutation({
    mutationFn: async (courseId: string) => {
      await api.delete(`/courses/${courseId}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['courses'] })
    },
  })

  // Delete module mutation
  const deleteModuleMutation = useMutation({
    mutationFn: async ({ courseId, moduleId }: { courseId: string; moduleId: string }) => {
      await api.delete(`/courses/${courseId}/modules/${moduleId}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['courses'] })
    },
  })

  // Delete track mutation
  const deleteTrackMutation = useMutation({
    mutationFn: async ({ moduleId, trackId }: { moduleId: string; trackId: string }) => {
      await api.delete(`/modules/${moduleId}/tracks/${trackId}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['courses'] })
    },
  })

  const toggleCourse = (courseId: string) => {
    const newExpanded = new Set(expandedCourses)
    if (newExpanded.has(courseId)) {
      newExpanded.delete(courseId)
    } else {
      newExpanded.add(courseId)
    }
    setExpandedCourses(newExpanded)
  }

  const toggleModule = (moduleId: string) => {
    const newExpanded = new Set(expandedModules)
    if (newExpanded.has(moduleId)) {
      newExpanded.delete(moduleId)
    } else {
      newExpanded.add(moduleId)
    }
    setExpandedModules(newExpanded)
  }

  const handleCreateCourse = () => {
    if (newCourseName.trim()) {
      createCourseMutation.mutate({
        name: newCourseName.trim(),
        description: newCourseDesc.trim(),
      })
    }
  }

  const handleCreateModule = (courseId: string) => {
    if (newModuleName.trim()) {
      createModuleMutation.mutate({
        courseId,
        name: newModuleName.trim(),
        description: newModuleDesc.trim(),
      })
    }
  }

  const handleCreateTrack = (moduleId: string) => {
    if (trackName.trim() && trackText.trim()) {
      createTrackMutation.mutate({
        moduleId,
        name: trackName.trim(),
        text: trackText.trim(),
      })
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    )
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold mb-2 flex items-center gap-2">
            <BookOpen className="w-6 h-6 text-primary" />
            Course Manager
          </h1>
          <p className="text-muted-foreground">Organize your audio content into courses, modules, and tracks</p>
        </div>
        <button
          onClick={() => setShowCreateCourse(true)}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 transition-colors"
        >
          <Plus className="w-4 h-4" />
          New Course
        </button>
      </div>

      {/* Create Course Modal */}
      {showCreateCourse && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-card border border-border rounded-lg p-6 w-full max-w-md">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">Create New Course</h2>
              <button
                onClick={() => setShowCreateCourse(false)}
                className="text-muted-foreground hover:text-foreground"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Course Name</label>
                <input
                  type="text"
                  value={newCourseName}
                  onChange={(e) => setNewCourseName(e.target.value)}
                  className="w-full px-3 py-2 border border-border rounded-lg bg-background"
                  placeholder="e.g., Python Fundamentals"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Description (Optional)</label>
                <textarea
                  value={newCourseDesc}
                  onChange={(e) => setNewCourseDesc(e.target.value)}
                  className="w-full px-3 py-2 border border-border rounded-lg bg-background"
                  rows={3}
                  placeholder="Brief description of the course..."
                />
              </div>
              <div className="flex gap-3">
                <button
                  onClick={handleCreateCourse}
                  disabled={!newCourseName.trim() || createCourseMutation.isPending}
                  className="flex-1 px-4 py-2 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {createCourseMutation.isPending ? 'Creating...' : 'Create Course'}
                </button>
                <button
                  onClick={() => setShowCreateCourse(false)}
                  className="px-4 py-2 rounded-lg border border-border hover:bg-accent"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Courses List */}
      <div className="space-y-4">
        {!courses || courses.length === 0 ? (
          <div className="bg-card border border-border rounded-lg p-12 text-center">
            <BookOpen className="w-12 h-12 text-muted-foreground mx-auto mb-3 opacity-50" />
            <p className="text-lg font-medium mb-2">No Courses Yet</p>
            <p className="text-muted-foreground mb-4">Create your first course to get started</p>
            <button
              onClick={() => setShowCreateCourse(true)}
              className="px-4 py-2 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90"
            >
              Create Course
            </button>
          </div>
        ) : (
          courses.map((course) => (
            <div key={course.id} className="bg-card border border-border rounded-lg">
              {/* Course Header */}
              <div className="p-4 flex items-center justify-between">
                <div className="flex items-center gap-3 flex-1">
                  <button
                    onClick={() => toggleCourse(course.id)}
                    className="text-muted-foreground hover:text-foreground"
                  >
                    {expandedCourses.has(course.id) ? (
                      <ChevronDown className="w-5 h-5" />
                    ) : (
                      <ChevronRight className="w-5 h-5" />
                    )}
                  </button>
                  <BookOpen className="w-5 h-5 text-primary" />
                  <div className="flex-1">
                    <h3 className="font-semibold">{course.name}</h3>
                    {course.description && (
                      <p className="text-sm text-muted-foreground">{course.description}</p>
                    )}
                    <p className="text-xs text-muted-foreground mt-1">
                      {course.modules.length} module{course.modules.length !== 1 ? 's' : ''}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setShowCreateModule(course.id)}
                    className="px-3 py-1.5 rounded text-sm bg-primary/10 text-primary hover:bg-primary/20"
                  >
                    <Plus className="w-4 h-4 inline mr-1" />
                    Add Module
                  </button>
                  <button
                    onClick={() => {
                      if (confirm(`Delete course "${course.name}"?`)) {
                        deleteCourseMutation.mutate(course.id)
                      }
                    }}
                    className="p-2 rounded text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>

              {/* Create Module Form */}
              {showCreateModule === course.id && (
                <div className="px-4 pb-4 border-t border-border pt-4">
                  <div className="bg-accent/50 border border-border rounded-lg p-4 space-y-3">
                    <h4 className="font-medium">Add New Module</h4>
                    <input
                      type="text"
                      value={newModuleName}
                      onChange={(e) => setNewModuleName(e.target.value)}
                      className="w-full px-3 py-2 border border-border rounded-lg bg-background"
                      placeholder="Module name..."
                    />
                    <textarea
                      value={newModuleDesc}
                      onChange={(e) => setNewModuleDesc(e.target.value)}
                      className="w-full px-3 py-2 border border-border rounded-lg bg-background"
                      rows={2}
                      placeholder="Module description (optional)..."
                    />
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleCreateModule(course.id)}
                        disabled={!newModuleName.trim() || createModuleMutation.isPending}
                        className="px-4 py-2 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
                      >
                        {createModuleMutation.isPending ? 'Creating...' : 'Create Module'}
                      </button>
                      <button
                        onClick={() => setShowCreateModule(null)}
                        className="px-4 py-2 rounded-lg border border-border hover:bg-accent"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                </div>
              )}

              {/* Modules */}
              {expandedCourses.has(course.id) && (
                <div className="px-4 pb-4 space-y-3">
                  {course.modules.length === 0 ? (
                    <div className="text-center py-8 text-muted-foreground">
                      <FolderOpen className="w-8 h-8 mx-auto mb-2 opacity-50" />
                      <p className="text-sm">No modules yet. Add your first module.</p>
                    </div>
                  ) : (
                    course.modules.map((module) => (
                      <div key={module.id} className="bg-accent/30 border border-border rounded-lg">
                        {/* Module Header */}
                        <div className="p-3 flex items-center justify-between">
                          <div className="flex items-center gap-2 flex-1">
                            <button
                              onClick={() => toggleModule(module.id)}
                              className="text-muted-foreground hover:text-foreground"
                            >
                              {expandedModules.has(module.id) ? (
                                <ChevronDown className="w-4 h-4" />
                              ) : (
                                <ChevronRight className="w-4 h-4" />
                              )}
                            </button>
                            <FolderOpen className="w-4 h-4 text-blue-600" />
                            <div className="flex-1">
                              <h4 className="font-medium text-sm">{module.name}</h4>
                              {module.description && (
                                <p className="text-xs text-muted-foreground">{module.description}</p>
                              )}
                              <p className="text-xs text-muted-foreground mt-0.5">
                                {module.tracks.length} track{module.tracks.length !== 1 ? 's' : ''}
                              </p>
                            </div>
                          </div>
                          <div className="flex items-center gap-2">
                            <button
                              onClick={() => setShowAddTrack(module.id)}
                              className="px-2 py-1 rounded text-xs bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 hover:bg-blue-200 dark:hover:bg-blue-900/50"
                            >
                              <Plus className="w-3 h-3 inline mr-1" />
                              Add Track
                            </button>
                            <button
                              onClick={() => {
                                if (confirm(`Delete module "${module.name}"?`)) {
                                  deleteModuleMutation.mutate({ courseId: course.id, moduleId: module.id })
                                }
                              }}
                              className="p-1.5 rounded text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20"
                            >
                              <Trash2 className="w-3 h-3" />
                            </button>
                          </div>
                        </div>

                        {/* Add Track Form */}
                        {showAddTrack === module.id && (
                          <div className="px-3 pb-3 border-t border-border pt-3">
                            <div className="bg-background border border-border rounded-lg p-3 space-y-3">
                              <h5 className="font-medium text-sm">Generate Audio Track</h5>
                              <input
                                type="text"
                                value={trackName}
                                onChange={(e) => setTrackName(e.target.value)}
                                className="w-full px-3 py-2 border border-border rounded-lg bg-background text-sm"
                                placeholder="Track name..."
                              />
                              <textarea
                                value={trackText}
                                onChange={(e) => setTrackText(e.target.value)}
                                className="w-full px-3 py-2 border border-border rounded-lg bg-background text-sm"
                                rows={3}
                                placeholder="Enter text to convert to audio..."
                              />
                              <div className="flex gap-2">
                                <button
                                  onClick={() => handleCreateTrack(module.id)}
                                  disabled={!trackName.trim() || !trackText.trim() || createTrackMutation.isPending}
                                  className="px-3 py-1.5 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50 text-sm"
                                >
                                  {createTrackMutation.isPending ? 'Generating...' : 'Generate & Add Track'}
                                </button>
                                <button
                                  onClick={() => setShowAddTrack(null)}
                                  className="px-3 py-1.5 rounded-lg border border-border hover:bg-accent text-sm"
                                >
                                  Cancel
                                </button>
                              </div>
                            </div>
                          </div>
                        )}

                        {/* Tracks */}
                        {expandedModules.has(module.id) && (
                          <div className="px-3 pb-3 space-y-2">
                            {module.tracks.length === 0 ? (
                              <div className="text-center py-6 text-muted-foreground">
                                <Music className="w-6 h-6 mx-auto mb-2 opacity-50" />
                                <p className="text-xs">No tracks yet. Add your first audio track.</p>
                              </div>
                            ) : (
                              module.tracks.map((track) => (
                                <div
                                  key={track.id}
                                  className="flex items-center justify-between p-2 bg-background border border-border rounded"
                                >
                                  <div className="flex items-center gap-2 flex-1">
                                    <Music className="w-3 h-3 text-green-600" />
                                    <span className="text-sm">{track.name}</span>
                                    {track.duration && (
                                      <span className="text-xs text-muted-foreground">
                                        ({Math.round(track.duration)}s)
                                      </span>
                                    )}
                                  </div>
                                  <div className="flex items-center gap-2">
                                    <a
                                      href={track.audio_file}
                                      target="_blank"
                                      rel="noopener noreferrer"
                                      className="text-xs text-primary hover:underline"
                                    >
                                      Play
                                    </a>
                                    <button
                                      onClick={() => {
                                        if (confirm(`Delete track "${track.name}"?`)) {
                                          deleteTrackMutation.mutate({ moduleId: module.id, trackId: track.id })
                                        }
                                      }}
                                      className="p-1 rounded text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20"
                                    >
                                      <Trash2 className="w-3 h-3" />
                                    </button>
                                  </div>
                                </div>
                              ))
                            )}
                          </div>
                        )}
                      </div>
                    ))
                  )}
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  )
}
