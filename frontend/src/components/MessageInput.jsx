import { useState, useRef } from 'react'
import { ArrowUp } from 'lucide-react'

export default function MessageInput({ onSend, isLoading }) {
  const [text, setText] = useState('')
  const inputRef = useRef(null)

  const handleSubmit = () => {
    if (!text.trim() || isLoading) return
    onSend(text)
    setText('')
    inputRef.current?.focus()
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  const canSend = text.trim().length > 0 && !isLoading

  return (
    <div className="border-t border-slate-200/80 bg-white/80 backdrop-blur-sm px-4 py-3">
      <div className="max-w-3xl mx-auto">

        {/* Input row */}
        <div className="flex gap-2 items-end bg-white border border-slate-200 rounded-2xl
                        shadow-input focus-within:border-emerald-400 focus-within:shadow-elevated
                        transition-all duration-200 px-4 py-2">

          <textarea
            ref={inputRef}
            value={text}
            onChange={e => setText(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isLoading}
            placeholder={isLoading
              ? "Thinking..."
              : "Describe your situation or ask about a program..."
            }
            rows={1}
            className="flex-1 resize-none text-sm text-slate-800 placeholder:text-slate-400
                       focus:outline-none disabled:text-slate-400 disabled:cursor-not-allowed
                       bg-transparent py-1.5 max-h-32 overflow-y-auto leading-relaxed"
            style={{ minHeight: '36px' }}
          />

          <button
            onClick={handleSubmit}
            disabled={!canSend}
            className={`flex-shrink-0 w-9 h-9 rounded-xl flex items-center justify-center
                       transition-all duration-200
                       ${canSend
                         ? 'bg-navy-800 hover:bg-navy-700 active:scale-95 text-white shadow-soft'
                         : 'bg-slate-100 text-slate-300 cursor-not-allowed'
                       }`}
            aria-label="Send message"
          >
            <ArrowUp className="w-4 h-4" strokeWidth={2.5} />
          </button>

        </div>

        {/* Hint */}
        <p className="text-[11px] text-slate-400 mt-2 text-center">
          <kbd className="px-1 py-0.5 bg-slate-100 rounded text-[10px] font-medium text-slate-500">Enter</kbd>
          {' '}to send ·
          <kbd className="px-1 py-0.5 bg-slate-100 rounded text-[10px] font-medium text-slate-500">Shift + Enter</kbd>
          {' '}for new line · Sourced from official USDA RD data
        </p>

      </div>
    </div>
  )
}
