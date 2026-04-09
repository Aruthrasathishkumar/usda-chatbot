// useChat.js — Custom hook that manages all chat state and API calls
//
// What is a custom hook?
// A regular function that uses React hooks (useState, useEffect) inside it.
// It lets you extract and reuse stateful logic across components.
// Convention: custom hooks always start with "use"

import { useState, useCallback } from 'react'

// Read the API URL from the .env.local file
// import.meta.env is Vite's way of accessing environment variables
// The fallback 'http://localhost:8000' is used if the variable is not set
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export function useChat() {
  // messages: array of all chat messages (both user and bot)
  // Each message object looks like:
  // { id, role: 'user'|'bot', content, sources, timestamp, isError }
  const [messages, setMessages] = useState([
    {
      id: 1,
      role: 'bot',
      content: "Hello! I'm your USDA Rural Development Assistant. I can help you discover programs for housing, water infrastructure, business loans, broadband, energy, and community facilities in rural areas.\n\nDescribe your situation in plain English and I'll recommend the right programs for you.",
      sources: [],
      timestamp: new Date()
    }
  ])

  // isLoading: true while waiting for the API response
  // Used to show a spinner and disable the input
  const [isLoading, setIsLoading] = useState(false)

  // sessionId: unique ID for this conversation
  // Stays the same across all messages in one session
  // Generated once when the hook first loads
  const [sessionId] = useState(() => crypto.randomUUID())
  // crypto.randomUUID() generates a UUID like "a3f2c1d4-..."
  // The () => syntax is a "lazy initializer" — the function runs
  // only once when the component mounts, not on every render

  // sendMessage: the function called when user submits a question
  // useCallback memoizes this function — prevents it from being
  // recreated on every render (a performance optimization)
  const sendMessage = useCallback(async (userText) => {
    // Don't send empty messages
    if (!userText.trim() || isLoading) return

    // Create the user's message object
    const userMessage = {
      id: Date.now(),         // unique ID using timestamp
      role: 'user',
      content: userText.trim(),
      sources: [],
      timestamp: new Date()
    }

    // Add user message to the chat immediately (before API responds)
    // This makes the UI feel responsive — user sees their message right away
    // prevMessages => [...prevMessages, userMessage] is the React pattern
    // for adding to an array in state without mutating the original
    setMessages(prev => [...prev, userMessage])
    setIsLoading(true)

    try {
      // Call your FastAPI backend
      // fetch() is the browser's built-in HTTP client
      const response = await fetch(`${API_URL}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',  // tells the server we're sending JSON
        },
        body: JSON.stringify({
          message: userText.trim(),
          session_id: sessionId
        })
      })

      // Check if the HTTP response was successful (status 200-299)
      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`)
      }

      // Parse the JSON response body
      // response.json() is async — it reads and parses the response stream
      const data = await response.json()

      // Create the bot's message object from the API response
      const botMessage = {
        id: Date.now() + 1,
        role: 'bot',
        content: data.answer,
        sources: data.sources || [],   // the programs FAISS retrieved
        timestamp: new Date()
      }

      // Add bot message to the chat
      setMessages(prev => [...prev, botMessage])

    } catch (error) {
      // If anything went wrong, show an error message in the chat
      // instead of crashing the whole app
      console.error('Chat error:', error)
      const errorMessage = {
        id: Date.now() + 1,
        role: 'bot',
        content: "Sorry, I couldn't connect to the backend. Please make sure the FastAPI server and Ollama are running.",
        sources: [],
        timestamp: new Date(),
        isError: true
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      // finally runs whether the try succeeded or catch ran
      // Always re-enable the input after the request completes
      setIsLoading(false)
    }
  }, [isLoading, sessionId])

  // clearChat: resets the conversation
  const clearChat = useCallback(() => {
    setMessages([{
      id: Date.now(),
      role: 'bot',
      content: "New conversation started. How can I help you discover USDA Rural Development programs?",
      sources: [],
      timestamp: new Date()
    }])
  }, [])

  // Return everything App.jsx needs
  return { messages, isLoading, sendMessage, clearChat }
}