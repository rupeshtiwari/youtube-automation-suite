import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Calendar,
  Video,
  FileText,
  Eye,
  BarChart3,
  Activity,
  Settings,
  Mic,
  ChevronDown,
  Youtube,
  Linkedin,
  Facebook,
  Instagram,
  Plus,
  PlaySquare
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { useState, useEffect } from 'react';
import api from '@/lib/api';

// All routes are now handled by React Router
const navItems = [
  { path: '/', icon: LayoutDashboard, label: 'Queue', isFlask: false },
  { path: '/calendar', icon: Calendar, label: 'Calendar', isFlask: false },
  { path: '/shorts', icon: Video, label: 'Shorts', isFlask: false },
  { path: '/sessions', icon: FileText, label: 'Sessions', isFlask: false },
  { path: '/content-preview', icon: Eye, label: 'Preview & Schedule', isFlask: false },
  { path: '/insights', icon: BarChart3, label: 'Analytics', isFlask: false },
  { path: '/activity', icon: Activity, label: 'Activity', isFlask: false },
  { path: '/audio-generator', icon: Mic, label: 'Audio Generator', isFlask: false },
  { path: '/audio-library', icon: Mic, label: 'Audio Library', isFlask: false },
  { path: '/settings', icon: Settings, label: 'Settings', isFlask: false },
];

// Mock channels - in real app, fetch from API
const channels = [
  { id: 'all', name: 'All Channels', icon: LayoutDashboard, count: 0 },
  { id: 'youtube', name: 'YouTube Channel', icon: Youtube, count: 0 },
  { id: 'linkedin', name: 'LinkedIn', icon: Linkedin, count: 0 },
  { id: 'facebook', name: 'Facebook', icon: Facebook, count: 0 },
  { id: 'instagram', name: 'Instagram', icon: Instagram, count: 0 },
];

export default function Sidebar() {
  const [showMoreChannels, setShowMoreChannels] = useState(false);
  const [showShortsPlaylists, setShowShortsPlaylists] = useState(true);
  const [shortsPlaylists, setShortsPlaylists] = useState<Array<{playlistId: string; playlistTitle: string; playlistUrl: string; itemCount: number}>>([]);
  const [loadingPlaylists, setLoadingPlaylists] = useState(false);

  useEffect(() => {
    // Fetch shorts playlists on mount
    const fetchShortsPlaylists = async () => {
      setLoadingPlaylists(true);
      try {
        const response = await api.get('/api/shorts-playlists');
        if (response.data.playlists) {
          setShortsPlaylists(response.data.playlists);
        }
      } catch (error) {
        console.error('Error fetching shorts playlists:', error);
      } finally {
        setLoadingPlaylists(false);
      }
    };

    fetchShortsPlaylists();
  }, []);

  return (
    <aside className="w-64 bg-card border-r border-border flex flex-col flex-shrink-0">
      {/* Logo/Brand */}
      <div className="p-5 border-b border-border">
        <h1 className="text-lg font-bold text-primary flex items-center gap-2">
          <Video className="w-5 h-5" />
          <span className="truncate">YouTube Automation</span>
        </h1>
      </div>

      {/* Channels Section - Buffer Style */}
      <div className="flex-1 overflow-y-auto">
        <div className="p-4">
          <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-3 px-1">
            Channels
          </h3>
          <div className="space-y-0.5">
            {channels.map((channel) => {
              const Icon = channel.icon;
              return (
                <button
                  key={channel.id}
                  onClick={() => {
                    // Filter view by channel - for now just navigate to dashboard
                    // In future, this could filter the queue/content by channel
                    if (channel.id === 'all') {
                      // Use React Router navigation for internal routes
                      window.location.href = '/';
                    } else {
                      // Navigate to settings to manage this channel
                      window.location.href = '/settings';
                    }
                  }}
                  className={cn(
                    'w-full flex items-center justify-between px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                    channel.id === 'all'
                      ? 'bg-primary text-primary-foreground'
                      : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
                  )}
                  title={channel.id === 'all' ? 'View all channels' : `Manage ${channel.name}`}
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <Icon className="w-4 h-4 flex-shrink-0" />
                    <span className="truncate">{channel.name}</span>
                  </div>
                  {channel.count > 0 && (
                    <span className="px-1.5 py-0.5 text-xs bg-background/50 rounded-full flex-shrink-0 ml-2">
                      {channel.count}
                    </span>
                  )}
                </button>
              );
            })}
          </div>

          {/* Connect New Channels */}
          <div className="mt-4 space-y-0.5">
            <button
              onClick={() => {
                // Navigate to Settings page which handles all connections
                window.location.href = '/settings';
              }}
              className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-muted-foreground hover:bg-accent hover:text-accent-foreground transition-colors cursor-pointer"
              title="Manage all social media connections"
            >
              <Plus className="w-4 h-4 flex-shrink-0" />
              <span className="truncate">Add Channel</span>
            </button>
          </div>

          {channels.length > 5 && (
            <button
              onClick={() => setShowMoreChannels(!showMoreChannels)}
              className="w-full mt-2 text-xs text-muted-foreground hover:text-foreground flex items-center gap-1 px-1"
            >
              <ChevronDown className={cn('w-3 h-3 transition-transform', showMoreChannels && 'rotate-180')} />
              Show more channels
            </button>
          )}
        </div>

        {/* Shorts Playlists Section */}
        {shortsPlaylists.length > 0 && (
          <div className="border-t border-border p-4">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">
                Shorts Playlists
              </h3>
              <button
                onClick={() => setShowShortsPlaylists(!showShortsPlaylists)}
                className="p-0 hover:text-foreground transition-colors"
                title={showShortsPlaylists ? 'Collapse' : 'Expand'}
              >
                <ChevronDown className={cn('w-3 h-3 transition-transform', !showShortsPlaylists && '-rotate-90')} />
              </button>
            </div>

            {showShortsPlaylists && (
              <div className="space-y-1 max-h-48 overflow-y-auto">
                {loadingPlaylists ? (
                  <div className="text-xs text-muted-foreground px-3 py-2">Loading...</div>
                ) : (
                  shortsPlaylists.map((playlist) => (
                    <a
                      key={playlist.playlistId}
                      href={playlist.playlistUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center justify-between px-3 py-2 rounded-lg text-sm text-muted-foreground hover:bg-accent hover:text-accent-foreground transition-colors group"
                      title={`${playlist.playlistTitle} (${playlist.itemCount} videos)`}
                    >
                      <div className="flex items-center gap-2 min-w-0 flex-1">
                        <PlaySquare className="w-3.5 h-3.5 flex-shrink-0 text-primary" />
                        <span className="truncate text-xs">{playlist.playlistTitle}</span>
                      </div>
                      <span className="ml-2 px-1.5 py-0.5 text-xs bg-background/50 rounded-full flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity">
                        {playlist.itemCount}
                      </span>
                    </a>
                  ))
                )}
              </div>
            )}
          </div>
        )}

        {/* Navigation */}
        <div className="border-t border-border p-4">
          <nav className="space-y-0.5">
            {navItems.map((item) => {
              const Icon = item.icon;

              // Flask-backed routes should bypass React Router
              if (item.isFlask) {
                return (
                  <a
                    key={item.path}
                    href={item.path}
                    className={cn(
                      'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                      'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
                    )}
                  >
                    <Icon className="w-4 h-4 flex-shrink-0" />
                    <span className="truncate">{item.label}</span>
                  </a>
                );
              }

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
                  <Icon className="w-4 h-4 flex-shrink-0" />
                  <span className="truncate">{item.label}</span>
                </NavLink>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Bottom Actions */}
      <div className="border-t border-border p-4 space-y-0.5">
        <button
          onClick={() => {
            // Navigate to config page with hash anchor - use replace to bypass React Router
            window.location.replace('/config#targeting-settings');
          }}
          className="w-full text-left px-3 py-2 text-sm text-muted-foreground hover:text-foreground hover:bg-accent rounded-lg transition-colors"
          title="Manage video tags, categories, and role levels (in Targeting section)"
        >
          Manage Tags
        </button>
        <button
          onClick={() => {
            // Navigate to config page with hash anchor - use replace to bypass React Router
            window.location.replace('/config#social-media-connections');
          }}
          className="w-full text-left px-3 py-2 text-sm text-muted-foreground hover:text-foreground hover:bg-accent rounded-lg transition-colors"
          title="Manage connected social media channels (LinkedIn, Facebook, Instagram)"
        >
          Manage Channels
        </button>
      </div>
    </aside>
  );
}
