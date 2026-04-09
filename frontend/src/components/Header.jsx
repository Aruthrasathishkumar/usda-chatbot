import { Wheat, Plus, PanelLeftOpen, PanelLeftClose } from 'lucide-react'

export default function Header({ programCount, onClearChat, sidebarOpen, onToggleSidebar }) {
  return (
    <header className="bg-white/80 backdrop-blur-md border-b border-slate-200/80 px-4 sm:px-6 py-3 flex items-center justify-between sticky top-0 z-30">

      {/* Left — brand */}
      <div className="flex items-center gap-3">
        {/* Sidebar toggle */}
        <button
          onClick={onToggleSidebar}
          className="p-2 -ml-2 rounded-lg text-slate-400 hover:text-navy-700 hover:bg-slate-100 transition-colors"
          aria-label={sidebarOpen ? 'Close program browser' : 'Open program browser'}
        >
          {sidebarOpen
            ? <PanelLeftClose className="w-5 h-5" />
            : <PanelLeftOpen className="w-5 h-5" />
          }
        </button>

        {/* Logo mark */}
        <div className="flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-navy-800 to-navy-900 flex items-center justify-center shadow-soft">
            <Wheat className="w-5 h-5 text-emerald-400" />
          </div>
          <div>
            <h1 className="text-base font-bold text-navy-900 leading-tight tracking-tight">
              USDA Rural Development
            </h1>
            <p className="text-xs text-slate-400 font-medium leading-tight hidden sm:block">
              {programCount > 0
                ? `AI Assistant · ${programCount} programs`
                : 'AI Assistant · Loading...'}
            </p>
          </div>
        </div>
      </div>

      {/* Right — actions */}
      <button
        onClick={onClearChat}
        className="flex items-center gap-1.5 text-sm font-medium text-navy-700
                   bg-slate-100 hover:bg-slate-200 active:bg-slate-300
                   px-3.5 py-2 rounded-lg transition-all duration-150"
      >
        <Plus className="w-4 h-4" />
        <span className="hidden sm:inline">New Chat</span>
      </button>

    </header>
  )
}
