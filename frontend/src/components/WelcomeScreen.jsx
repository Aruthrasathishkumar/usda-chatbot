import { Home, Droplets, Briefcase, Wifi, Zap, Building2, ArrowRight } from 'lucide-react'
import RuralIllustration from './RuralIllustration'

const SUGGESTIONS = [
  {
    icon: Droplets,
    label: 'Water & Infrastructure',
    text: "My rural town's water system was damaged in a flood. What help is available?",
  },
  {
    icon: Home,
    label: 'Housing Assistance',
    text: "I'm a low-income farmer looking to buy a home in a rural area.",
  },
  {
    icon: Building2,
    label: 'Community Facilities',
    text: 'We want to build a health clinic in our rural community.',
  },
  {
    icon: Wifi,
    label: 'Broadband Access',
    text: 'Our rural area has no high-speed internet. What broadband programs exist?',
  },
  {
    icon: Briefcase,
    label: 'Business & Loans',
    text: 'I run a small rural business and need a loan.',
  },
  {
    icon: Zap,
    label: 'Energy Programs',
    text: 'What USDA programs help rural communities with renewable energy?',
  },
]

export default function WelcomeScreen({ onSuggestionClick, isLoading }) {
  return (
    <div className="flex-1 flex items-center justify-center px-4 py-8 overflow-y-auto">
      <div className="max-w-2xl w-full animate-fade-in">

        {/* Illustration */}
        <div className="flex justify-center mb-6">
          <RuralIllustration className="w-full max-w-md h-auto opacity-90" />
        </div>

        {/* Heading */}
        <div className="text-center mb-8">
          <h2 className="text-2xl sm:text-3xl font-bold text-navy-900 tracking-tight mb-3">
            How can I help you today?
          </h2>
          <p className="text-slate-500 text-sm sm:text-base max-w-lg mx-auto leading-relaxed">
            Describe your situation in plain English and I'll recommend the right
            USDA Rural Development programs for you.
          </p>
        </div>

        {/* Suggestion cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 mb-8">
          {SUGGESTIONS.map((s, i) => {
            const Icon = s.icon
            return (
              <button
                key={i}
                onClick={() => onSuggestionClick(s.text)}
                disabled={isLoading}
                className="group flex items-start gap-3 text-left p-3.5 rounded-xl
                           bg-white border border-slate-200 shadow-soft
                           hover:border-emerald-300 hover:shadow-card
                           active:scale-[0.98]
                           transition-all duration-200
                           disabled:opacity-50 disabled:cursor-not-allowed"
                style={{ animationDelay: `${i * 60}ms` }}
              >
                <div className="w-9 h-9 rounded-lg bg-slate-50 group-hover:bg-emerald-50
                                flex items-center justify-center flex-shrink-0
                                transition-colors duration-200">
                  <Icon className="w-4.5 h-4.5 text-slate-400 group-hover:text-emerald-600 transition-colors" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-xs font-semibold text-navy-800 mb-0.5">{s.label}</p>
                  <p className="text-xs text-slate-500 leading-relaxed line-clamp-2">{s.text}</p>
                </div>
                <ArrowRight className="w-4 h-4 text-slate-300 group-hover:text-emerald-500 mt-1
                                       opacity-0 group-hover:opacity-100 -translate-x-1 group-hover:translate-x-0
                                       transition-all duration-200 flex-shrink-0" />
              </button>
            )
          })}
        </div>

        {/* Trust badge */}
        <div className="flex items-center justify-center gap-2 text-xs text-slate-400">
          <div className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
          <span>Powered by official USDA Rural Development program data</span>
        </div>

      </div>
    </div>
  )
}
