import { useLocation } from 'react-router-dom'
import { Plus, Star, HelpCircle, Gift, User } from 'lucide-react'

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

  return (
    <header className="h-16 border-b border-border bg-card flex items-center justify-between px-6 sticky top-0 z-10">
      <h2 className="text-xl font-semibold">{title}</h2>
      
      {/* Right side actions - Buffer style */}
      <div className="flex items-center gap-3">
        <button className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors flex items-center gap-2 text-sm font-medium">
          <Plus className="w-4 h-4" />
          New
        </button>
        <button className="p-2 hover:bg-accent rounded-md transition-colors">
          <Star className="w-5 h-5 text-muted-foreground" />
        </button>
        <button className="p-2 hover:bg-accent rounded-md transition-colors">
          <HelpCircle className="w-5 h-5 text-muted-foreground" />
        </button>
        <button className="p-2 hover:bg-accent rounded-md transition-colors">
          <Gift className="w-5 h-5 text-muted-foreground" />
        </button>
        <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center">
          <User className="w-4 h-4 text-primary" />
        </div>
      </div>
    </header>
  )
}
