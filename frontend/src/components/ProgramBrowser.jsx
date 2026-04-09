import { useState } from 'react'
import { ExternalLink, ChevronDown, ChevronUp, Search, X, BookOpen } from 'lucide-react'

export default function ProgramBrowser({ programs, categories, onSelectProgram, isOpen, onClose }) {
  const [selectedCategory, setSelectedCategory] = useState(null)
  const [expandedProgram, setExpandedProgram] = useState(null)
  const [searchQuery, setSearchQuery] = useState('')

  // Filter programs by category and search
  const filteredPrograms = programs.filter(p => {
    const matchesCategory = !selectedCategory || p.category === selectedCategory
    const matchesSearch = !searchQuery ||
      p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (p.description && p.description.toLowerCase().includes(searchQuery.toLowerCase()))
    return matchesCategory && matchesSearch
  })

  if (!isOpen) return null

  return (
    <>
      {/* Mobile overlay backdrop */}
      <div
        className="fixed inset-0 bg-navy-950/30 backdrop-blur-sm z-20 md:hidden"
        onClick={onClose}
      />

      <aside className="sidebar-enter fixed md:relative z-20 inset-y-0 left-0 w-80
                         bg-white border-r border-slate-200 flex flex-col overflow-hidden
                         shadow-elevated md:shadow-none mt-[57px] md:mt-0">

        {/* Header */}
        <div className="p-4 border-b border-slate-100">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <BookOpen className="w-4 h-4 text-navy-700" />
              <h2 className="font-semibold text-navy-900 text-sm">Program Browser</h2>
            </div>
            <span className="text-xs text-slate-400 font-medium bg-slate-100 px-2 py-0.5 rounded-md">
              {filteredPrograms.length} of {programs.length}
            </span>
          </div>

          {/* Search input */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search programs..."
              className="w-full text-xs bg-slate-50 border border-slate-200 rounded-lg pl-8 pr-8 py-2
                         placeholder:text-slate-400 text-slate-700
                         focus:outline-none focus:ring-2 focus:ring-emerald-500/30 focus:border-emerald-400
                         transition-all duration-150"
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            )}
          </div>
        </div>

        {/* Category chips */}
        <div className="px-4 py-3 border-b border-slate-100">
          <div className="flex flex-wrap gap-1.5">
            <button
              onClick={() => setSelectedCategory(null)}
              className={`text-xs px-2.5 py-1 rounded-lg font-medium transition-all duration-150
                ${selectedCategory === null
                  ? 'bg-navy-800 text-white shadow-soft'
                  : 'bg-slate-50 text-slate-600 border border-slate-200 hover:bg-slate-100'
                }`}
            >
              All
            </button>

            {categories.map(cat => {
              const shortName = cat.replace(' Programs', '').replace(' & Environmental', '')
              return (
                <button
                  key={cat}
                  onClick={() => setSelectedCategory(selectedCategory === cat ? null : cat)}
                  className={`text-xs px-2.5 py-1 rounded-lg font-medium transition-all duration-150
                    ${selectedCategory === cat
                      ? 'bg-navy-800 text-white shadow-soft'
                      : 'bg-slate-50 text-slate-600 border border-slate-200 hover:bg-slate-100'
                    }`}
                >
                  {shortName}
                </button>
              )
            })}
          </div>
        </div>

        {/* Program list */}
        <div className="flex-1 overflow-y-auto scrollbar-thin p-3 flex flex-col gap-1.5">
          {filteredPrograms.map(program => (
            <div
              key={program.id}
              className={`group border rounded-xl overflow-hidden transition-all duration-200
                ${expandedProgram === program.id
                  ? 'border-emerald-300 shadow-card bg-white'
                  : 'border-slate-200 hover:border-slate-300 bg-white'
                }`}
            >
              <div
                className="flex items-start justify-between p-3 cursor-pointer
                           hover:bg-slate-50/80 transition-colors duration-150"
                onClick={() => setExpandedProgram(expandedProgram === program.id ? null : program.id)}
              >
                <div className="flex-1 min-w-0 pr-2">
                  <p className="text-xs font-semibold text-navy-800 leading-snug line-clamp-2">
                    {program.name}
                  </p>
                  <span className="text-[11px] text-slate-400 mt-0.5 block font-medium">
                    {program.category}
                  </span>
                </div>

                <div className={`p-0.5 rounded transition-transform duration-200
                  ${expandedProgram === program.id ? 'rotate-180' : ''}`}>
                  <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
                </div>
              </div>

              {expandedProgram === program.id && (
                <div className="px-3 pb-3 border-t border-slate-100 animate-fade-in">
                  <p className="text-xs text-slate-600 mt-2.5 leading-relaxed line-clamp-3">
                    {program.description}
                  </p>

                  <div className="flex gap-2 mt-3">
                    <button
                      onClick={() =>
                        onSelectProgram(
                          `Tell me about the ${program.name} program and who is eligible for it.`
                        )
                      }
                      className="flex-1 text-xs font-medium bg-navy-800 text-white
                                 px-3 py-2 rounded-lg hover:bg-navy-700
                                 active:scale-[0.97] transition-all duration-150"
                    >
                      Ask about this
                    </button>

                    <a
                      href={program.source_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs font-medium border border-slate-200 text-slate-600
                                 px-3 py-2 rounded-lg hover:bg-slate-50 hover:border-slate-300
                                 transition-all duration-150 flex items-center gap-1"
                    >
                      <ExternalLink className="w-3 h-3" />
                      Visit
                    </a>
                  </div>
                </div>
              )}
            </div>
          ))}

          {filteredPrograms.length === 0 && (
            <div className="text-center py-12">
              <Search className="w-8 h-8 text-slate-300 mx-auto mb-2" />
              <p className="text-xs text-slate-400">No programs found</p>
              <button
                onClick={() => { setSearchQuery(''); setSelectedCategory(null) }}
                className="text-xs text-emerald-600 hover:text-emerald-700 mt-1 font-medium"
              >
                Clear filters
              </button>
            </div>
          )}
        </div>

      </aside>
    </>
  )
}
