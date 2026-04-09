import { ExternalLink, Phone } from 'lucide-react'

export default function SourceCard({ source }) {
  return (
    <div className="group bg-white border border-slate-200 rounded-xl p-3.5 text-sm
                    shadow-soft hover:shadow-card hover:border-emerald-300
                    transition-all duration-200 relative overflow-hidden">

      {/* Left accent bar */}
      <div className="absolute left-0 top-0 bottom-0 w-1 bg-emerald-500 rounded-l-xl
                      opacity-0 group-hover:opacity-100 transition-opacity duration-200" />

      {/* Program link */}
      <a
        href={source.source_url}
        target="_blank"
        rel="noopener noreferrer"
        className="font-semibold text-navy-800 hover:text-emerald-700 flex items-center gap-1.5 mb-1.5
                   transition-colors duration-150"
      >
        <span className="line-clamp-1">{source.program_name}</span>
        <ExternalLink className="w-3.5 h-3.5 flex-shrink-0 text-slate-400 group-hover:text-emerald-500 transition-colors" />
      </a>

      {/* Category badge */}
      <span className="inline-block bg-slate-100 text-slate-600 text-xs font-medium
                       px-2 py-0.5 rounded-md mb-2">
        {source.category}
      </span>

      {/* Contact info */}
      {source.contact && (
        <div className="flex items-start gap-1.5 text-slate-500 text-xs leading-relaxed">
          <Phone className="w-3 h-3 mt-0.5 flex-shrink-0" />
          <span className="line-clamp-1">{source.contact.substring(0, 100)}</span>
        </div>
      )}
    </div>
  )
}
