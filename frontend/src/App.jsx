import { useState, useEffect } from 'react'
import Header from './components/Header'
import ChatWindow from './components/ChatWindow'
import MessageInput from './components/MessageInput'
import ProgramBrowser from './components/ProgramBrowser'
import { useChat } from './hooks/useChat'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function App() {
  const { messages, isLoading, sendMessage, clearChat } = useChat()

  const [programs, setPrograms] = useState([])
  const [categories, setCategories] = useState([])
  const [sidebarOpen, setSidebarOpen] = useState(() => window.innerWidth >= 768)

  useEffect(() => {
    fetch(`${API_URL}/api/programs`)
      .then(res => res.json())
      .then(data => setPrograms(data.programs || []))
      .catch(err => console.error('Failed to fetch programs:', err))

    fetch(`${API_URL}/api/categories`)
      .then(res => res.json())
      .then(data => setCategories(data.categories || []))
      .catch(err => console.error('Failed to fetch categories:', err))
  }, [])

  const handleSelectProgram = (questionText) => {
    sendMessage(questionText)
    if (window.innerWidth < 768) setSidebarOpen(false)
  }

  const handleSuggestionClick = (text) => {
    sendMessage(text)
  }

  return (
    <div className="h-screen flex flex-col bg-slate-50">

      <Header
        programCount={programs.length}
        onClearChat={clearChat}
        sidebarOpen={sidebarOpen}
        onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
      />

      <div className="flex flex-1 overflow-hidden relative">

        <ProgramBrowser
          programs={programs}
          categories={categories}
          onSelectProgram={handleSelectProgram}
          isOpen={sidebarOpen}
          onClose={() => setSidebarOpen(false)}
        />

        <div className="flex flex-1 flex-col overflow-hidden min-w-0">

          <ChatWindow
            messages={messages}
            isLoading={isLoading}
            onSuggestionClick={handleSuggestionClick}
          />

          <MessageInput
            onSend={sendMessage}
            isLoading={isLoading}
          />

        </div>
      </div>
    </div>
  )
}
