import { NavLink } from 'react-router-dom'
import { 
  LayoutDashboard, 
  Calendar, 
  Video, 
  FileText, 
  Eye, 
  BarChart3, 
  Activity, 
  Settings,
  ChevronDown,
  Youtube,
  Linkedin,
  Facebook,
  Instagram,
  Plus
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { useState } from 'react'

const navItems = [
  { path: '/', icon: LayoutDashboard, label: 'Queue' },
  { path: '/calendar', icon: Calendar, label: 'Calendar' },
  { path: '/shorts', icon: Video, label: 'Shorts' },
  { path: '/sessions', icon: FileText, label: 'Sessions' },
  { path: '/content-preview', icon: Eye, label: 'Preview & Schedule' },
  { path: '/insights', icon: BarChart3, label: 'Analytics' },
  { path: '/activity', icon: Activity, label: 'Activity' },
  { path: '/config', icon: Settings, label: 'Settings' },
]

// Mock channels - in real app, fetch from API
const channels = [
  { id: 'all', name: 'All Channels', icon: LayoutDashboard, count: 0 },
  { id: 'youtube', name: 'YouTube Channel', icon: Youtube, count: 0 },
  { id: 'linkedin', name: 'LinkedIn', icon: Linkedin, count: 0 },
  { id: 'facebook', name: 'Facebook', icon: Facebook, count: 0 },
  { id: 'instagram', name: 'Instagram', icon: Instagram, count: 0 },
]

export default function Sidebar() {
  const [showMoreChannels, setShowMoreChannels] = useState(false)

  return (
    <aside className="w-64 bg-card border-r border-border flex flex-col">
      {/* Logo/Brand */}
      <div className="p-6 border-b border-border">
        <h1 className="text-xl font-bold text-primary flex items-center gap-2">
          <Video className="w-6 h-6" />
          YouTube Automation
        </h1>
      </div>

      {/* Channels Section - Buffer Style */}
      <div className="flex-1 overflow-y-auto">
        <div className="p-4">
          <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-3">
            Channels
          </h3>
          <div className="space-y-1">
            {channels.map((channel) => {
              const Icon = channel.icon
              return (
                <button
                  key={channel.id}
                  className={cn(
                    'w-full flex items-center justify-between px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                    channel.id === 'all'
                      ? 'bg-primary text-primary-foreground'
                      : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
                  )}
                >
                  <div className="flex items-center gap-3">
                    <Icon className="w-5 h-5" />
                    <span>{channel.name}</span>
                  </div>
                  {channel.count > 0 && (
                    <span className="px-2 py-0.5 text-xs bg-muted rounded-full">
                      {channel.count}
                    </span>
                  )}
                </button>
              )
            })}
          </div>

          {/* Connect New Channels */}
          <div className="mt-4 space-y-1">
            <button className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-muted-foreground hover:bg-accent hover:text-accent-foreground transition-colors">
              <Plus className="w-5 h-5" />
              <span>Connect YouTube</span>
            </button>
            <button className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-muted-foreground hover:bg-accent hover:text-accent-foreground transition-colors">
              <Plus className="w-5 h-5" />
              <span>Connect LinkedIn</span>
            </button>
            <button className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-muted-foreground hover:bg-accent hover:text-accent-foreground transition-colors">
              <Plus className="w-5 h-5" />
              <span>Connect Facebook</span>
            </button>
            <button className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-muted-foreground hover:bg-accent hover:text-accent-foreground transition-colors">
              <Plus className="w-5 h-5" />
              <span>Connect Instagram</span>
            </button>
          </div>

          {channels.length > 5 && (
            <button
              onClick={() => setShowMoreChannels(!showMoreChannels)}
              className="w-full mt-2 text-xs text-muted-foreground hover:text-foreground flex items-center gap-1"
            >
              <ChevronDown className={cn('w-3 h-3 transition-transform', showMoreChannels && 'rotate-180')} />
              Show more channels
            </button>
          )}
        </div>

        {/* Navigation */}
        <div className="border-t border-border p-4">
          <nav className="space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon
              return (
                <NavLink
                  key={item.path}
                  to={item.path}
                  className={({ isActive }) =>
                    cn(
                      'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                      isActive
                        ? 'bg-primary text-primary-foreground'
                        : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
                    )
                  }
                >
                  <Icon className="w-5 h-5" />
                  {item.label}
                </NavLink>
              )
            })}
          </nav>
        </div>
      </div>

      {/* Bottom Actions */}
      <div className="border-t border-border p-4 space-y-1">
        <button className="w-full text-left px-3 py-2 text-sm text-muted-foreground hover:text-foreground hover:bg-accent rounded-lg transition-colors">
          Manage Tags
        </button>
        <button className="w-full text-left px-3 py-2 text-sm text-muted-foreground hover:text-foreground hover:bg-accent rounded-lg transition-colors">
          Manage Channels
        </button>
      </div>
    </aside>
  )
}
