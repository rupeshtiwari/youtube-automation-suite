import { useLocation } from 'react-router-dom'
import { Plus, Star, HelpCircle, Gift } from 'lucide-react'

const pageTitles: Record<string, string> = {
  '/': 'Queue',
  '/calendar': 'Calendar',
  '/shorts': 'Shorts',
  '/sessions': 'Sessions',
  '/content-preview': 'Preview & Schedule',
  '/insights': 'Analytics',
  '/activity': 'Activity',
  '/config': 'Settings',
}

export default function Header() {
  const location = useLocation()
  const title = pageTitles[location.pathname] || 'Dashboard'

  const handleNewPost = () => {
    // Try to open the quick compose modal (available globally in base.html)
    if (typeof (window as any).openQuickCompose === 'function') {
      (window as any).openQuickCompose()
    } else {
      // If function not available yet, wait a bit and try again
      setTimeout(() => {
        if (typeof (window as any).openQuickCompose === 'function') {
          (window as any).openQuickCompose()
        } else {
          // Fallback: navigate to dashboard where modal definitely exists
          window.location.href = '/'
          setTimeout(() => {
            if (typeof (window as any).openQuickCompose === 'function') {
              (window as any).openQuickCompose()
            }
          }, 500)
        }
      }, 100)
    }
  }

  const handleHelp = () => {
    // Open documentation page
    window.open('/docs', '_blank')
  }

  const handleStar = () => {
    // Toggle favorites or show favorites view
    // For now, just show a message
    alert('Favorites feature coming soon!')
  }

  const handleGift = () => {
    // Show promotions/referrals
    // For now, just show a message
    alert('Referral program coming soon!')
  }

  return (
    <header className="h-14 border-b border-border bg-card/95 backdrop-blur-sm sticky top-0 z-50">
      <div className="h-full flex items-center justify-between px-6">
        <h2 className="text-lg font-semibold text-foreground">{title}</h2>
        
        {/* Right side actions - Buffer style */}
        <div className="flex items-center gap-2">
          <button 
            onClick={handleStar}
            className="hidden sm:flex items-center gap-2 px-3 py-1.5 text-sm text-muted-foreground hover:text-foreground hover:bg-accent rounded-md transition-colors"
            title="Favorites"
          >
            <Star className="w-4 h-4" />
          </button>
          <button 
            onClick={handleHelp}
            className="hidden sm:flex items-center gap-2 px-3 py-1.5 text-sm text-muted-foreground hover:text-foreground hover:bg-accent rounded-md transition-colors"
            title="Help & Documentation"
          >
            <HelpCircle className="w-4 h-4" />
          </button>
          <button 
            onClick={handleGift}
            className="hidden sm:flex items-center gap-2 px-3 py-1.5 text-sm text-muted-foreground hover:text-foreground hover:bg-accent rounded-md transition-colors"
            title="Referrals & Promotions"
          >
            <Gift className="w-4 h-4" />
          </button>
          <button 
            onClick={handleNewPost}
            className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-all duration-200 text-sm font-medium shadow-sm hover:shadow"
            title="Create New Post"
          >
            <Plus className="w-4 h-4" />
            <span className="hidden sm:inline">New</span>
          </button>
        </div>
      </div>
    </header>
  )
}
