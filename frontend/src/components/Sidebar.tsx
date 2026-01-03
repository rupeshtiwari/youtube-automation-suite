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
  ChevronDown,
  Youtube,
  Linkedin,
  Facebook,
  Instagram,
  Plus
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { useState } from 'react';

// All routes are now handled by React Router
const navItems = [
  { path: '/', icon: LayoutDashboard, label: 'Queue', isFlask: false },
  { path: '/calendar', icon: Calendar, label: 'Calendar', isFlask: false },
  { path: '/shorts', icon: Video, label: 'Shorts', isFlask: false },
  { path: '/sessions', icon: FileText, label: 'Sessions', isFlask: false },
  { path: '/content-preview', icon: Eye, label: 'Preview & Schedule', isFlask: false },
  { path: '/insights', icon: BarChart3, label: 'Analytics', isFlask: false },
  { path: '/activity', icon: Activity, label: 'Activity', isFlask: false },
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
                      window.location.href = '/';
                    } else {
                      // Navigate to settings to manage this channel
                      window.location.href = '/config';
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
                // Navigate to Settings page where YouTube OAuth can be initiated
                window.location.href = '/config';
                setTimeout(() => {
                  // Scroll to YouTube section if it exists
                  const youtubeSection = document.querySelector('[data-platform="youtube"]') ||
                    document.querySelector('input[name*="youtube"]')?.closest('.card');
                  if (youtubeSection) {
                    (youtubeSection as HTMLElement).scrollIntoView({ behavior: 'smooth', block: 'start' });
                  }
                }, 1000);
              }}
              className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-muted-foreground hover:bg-accent hover:text-accent-foreground transition-colors"
              title="Connect YouTube account"
            >
              <Plus className="w-4 h-4 flex-shrink-0" />
              <span className="truncate">Connect YouTube</span>
            </button>
            <button
              onClick={() => {
                // Navigate to Settings and trigger LinkedIn OAuth
                window.location.href = '/api/linkedin/oauth/authorize';
              }}
              className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-muted-foreground hover:bg-accent hover:text-accent-foreground transition-colors"
              title="Connect LinkedIn account"
            >
              <Plus className="w-4 h-4 flex-shrink-0" />
              <span className="truncate">Connect LinkedIn</span>
            </button>
            <button
              onClick={() => {
                // Navigate to Settings and trigger Facebook OAuth
                window.location.href = '/api/facebook/oauth/authorize';
              }}
              className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-muted-foreground hover:bg-accent hover:text-accent-foreground transition-colors"
              title="Connect Facebook account (includes Instagram)"
            >
              <Plus className="w-4 h-4 flex-shrink-0" />
              <span className="truncate">Connect Facebook</span>
            </button>
            <button
              onClick={() => {
                // Instagram uses Facebook OAuth, navigate to Facebook connection
                window.location.href = '/api/facebook/oauth/authorize';
              }}
              className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-muted-foreground hover:bg-accent hover:text-accent-foreground transition-colors"
              title="Connect Instagram account (via Facebook)"
            >
              <Plus className="w-4 h-4 flex-shrink-0" />
              <span className="truncate">Connect Instagram</span>
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

        {/* Navigation */}
        <div className="border-t border-border p-4">
          <nav className="space-y-0.5">
            {navItems.map((item) => {
              const Icon = item.icon;

              // Use NavLink for all routes (React Router handles everything)
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
            // Navigate to settings page - tags are managed in the Targeting section
            window.location.href = '/config';
            // After page loads, try to scroll to targeting section
            setTimeout(() => {
              // Look for targeting-related inputs
              const targetingInput = document.querySelector('input[name="target_audience"]');
              if (targetingInput) {
                const card = targetingInput.closest('.card') as HTMLElement;
                if (card) {
                  card.scrollIntoView({ behavior: 'smooth', block: 'start' });
                  // Highlight briefly
                  card.style.transition = 'box-shadow 0.3s';
                  card.style.boxShadow = '0 0 0 3px rgba(37, 99, 235, 0.3)';
                  setTimeout(() => {
                    card.style.boxShadow = '';
                  }, 2000);
                }
              }
            }, 1000);
          }}
          className="w-full text-left px-3 py-2 text-sm text-muted-foreground hover:text-foreground hover:bg-accent rounded-lg transition-colors"
          title="Manage video tags, categories, and role levels (in Targeting section)"
        >
          Manage Tags
        </button>
        <button
          onClick={() => {
            // Navigate to settings page - channels are your connected social media accounts
            window.location.href = '/config';
            // After page loads, try to scroll to social media connections section
            setTimeout(() => {
              // Look for LinkedIn connection button or social media section
              const linkedinButton = document.querySelector('a[href*="linkedin/oauth"]');
              if (linkedinButton) {
                const card = linkedinButton.closest('.card') as HTMLElement;
                if (card) {
                  card.scrollIntoView({ behavior: 'smooth', block: 'start' });
                  // Highlight briefly
                  card.style.transition = 'box-shadow 0.3s';
                  card.style.boxShadow = '0 0 0 3px rgba(37, 99, 235, 0.3)';
                  setTimeout(() => {
                    card.style.boxShadow = '';
                  }, 2000);
                }
              }
            }, 1000);
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
