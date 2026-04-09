import { useEffect, useRef } from 'react'
import MessageBubble from './MessageBubble'
import WelcomeScreen from './WelcomeScreen'

function TypingIndicator() {
  return (
    <div className="flex gap-3 justify-start animate-fade-in">
      <div className="w-8 h-8 rounded-full bg-gradient-to-br from-navy-800 to-navy-900 flex items-center justify-center flex-shrink-0 shadow-soft">
        <span className="text-[10px] font-bold text-emerald-400">AI</span>
      </div>
      <div className="bg-white border border-slate-200 rounded-2xl rounded-tl-md px-5 py-3.5 shadow-soft">
        <div className="flex gap-1.5 items-center h-4">
          {[0, 1, 2].map(i => (
            <div
              key={i}
              className="typing-dot w-2 h-2 bg-slate-300 rounded-full"
            />
          ))}
        </div>
      </div>
    </div>
  )
}

export default function ChatWindow({ messages, isLoading, onSuggestionClick }) {
  const bottomRef = useRef(null)
  const showWelcome = messages.length <= 1

  useEffect(() => {
    if (!showWelcome) {
      bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
    }
  }, [messages, isLoading, showWelcome])

  if (showWelcome) {
    return <WelcomeScreen onSuggestionClick={onSuggestionClick} isLoading={isLoading} />
  }

  return (
    <div className="flex-1 overflow-y-auto scrollbar-thin px-4 py-6 bg-gradient-to-b from-slate-50 to-slate-100/50">
      <div className="max-w-3xl mx-auto flex flex-col gap-5">
        {messages.slice(1).map(message => (
          <MessageBubble key={message.id} message={message} />
        ))}

        {isLoading && <TypingIndicator />}

        <div ref={bottomRef} />
      </div>
    </div>
  )
}
