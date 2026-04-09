import SourceCard from './SourceCard'
import FormattedText from './FormattedText'
import { User, Bot, AlertCircle } from 'lucide-react'

export default function MessageBubble({ message }) {
  const isUser = message.role === 'user'

  return (
    <div className={`flex gap-3 animate-slide-up ${isUser ? 'justify-end' : 'justify-start'}`}>

      {/* Bot avatar */}
      {!isUser && (
        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-navy-800 to-navy-900 flex items-center justify-center flex-shrink-0 mt-0.5 shadow-soft">
          <Bot className="w-4 h-4 text-emerald-400" />
        </div>
      )}

      {/* Message content */}
      <div className={`max-w-[80%] sm:max-w-[75%] flex flex-col gap-2 ${isUser ? 'items-end' : 'items-start'}`}>

        {/* Bubble */}
        <div className={`rounded-2xl px-4 py-3 text-sm leading-relaxed
          ${isUser
            ? 'bg-navy-800 text-white rounded-br-md shadow-soft'
            : message.isError
              ? 'bg-red-50 text-red-700 border border-red-200 rounded-bl-md'
              : 'bg-white text-slate-700 border border-slate-200/80 rounded-bl-md shadow-soft'
          }`}
        >
          {message.isError ? (
            <div className="flex items-start gap-2">
              <AlertCircle className="w-4 h-4 text-red-400 mt-0.5 flex-shrink-0" />
              <p className="whitespace-pre-wrap">{message.content}</p>
            </div>
          ) : isUser ? (
            <p className="whitespace-pre-wrap">{message.content}</p>
          ) : (
            <FormattedText text={message.content} />
          )}
        </div>

        {/* Source cards */}
        {!isUser && message.sources && message.sources.length > 0 && (
          <div className="w-full">
            <p className="text-xs text-slate-400 mb-2 ml-0.5 font-medium">
              Referenced programs
            </p>
            <div className="flex flex-col gap-2">
              {message.sources.map((source, index) => (
                <SourceCard key={index} source={source} />
              ))}
            </div>
          </div>
        )}

        {/* Timestamp */}
        <span className={`text-[11px] px-0.5 ${isUser ? 'text-slate-400' : 'text-slate-400'}`}>
          {message.timestamp.toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit'
          })}
        </span>

      </div>

      {/* User avatar */}
      {isUser && (
        <div className="w-8 h-8 rounded-full bg-slate-200 flex items-center justify-center flex-shrink-0 mt-0.5">
          <User className="w-4 h-4 text-slate-500" />
        </div>
      )}

    </div>
  )
}
