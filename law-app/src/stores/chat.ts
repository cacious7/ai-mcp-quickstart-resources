import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { ollamaApi, type OllamaMessage } from '@/services'

export interface ChatMessage {
  id: string
  content: string
  role: 'user' | 'assistant'
  timestamp: Date
  sources?: string[]
  feedback?: 'helpful' | 'not-helpful'
  isTyping?: boolean
}

export interface ChatSession {
  id: string
  title: string
  messages: ChatMessage[]
  createdAt: Date
  updatedAt: Date
}

export const useChatStore = defineStore('chat', () => {
  // State
  const sessions = ref<ChatSession[]>([])
  const currentSessionId = ref<string | null>(null)
  const isTyping = ref(false)
  const isConnected = ref(false)
  const errorMessage = ref<string | null>(null)

  // Getters
  const currentSession = computed(() => {
    if (!currentSessionId.value) return null
    return sessions.value.find(session => session.id === currentSessionId.value) || null
  })

  const currentMessages = computed(() => {
    return currentSession.value?.messages || []
  })

  const hasActiveSessions = computed(() => {
    return sessions.value.length > 0
  })

  const recentSessions = computed(() => {
    return sessions.value
      .slice()
      .sort((a, b) => b.updatedAt.getTime() - a.updatedAt.getTime())
      .slice(0, 5)
  })

  // Actions
  const createSession = (title?: string): string => {
    const sessionId = generateId()
    const newSession: ChatSession = {
      id: sessionId,
      title: title || 'New Chat',
      messages: [],
      createdAt: new Date(),
      updatedAt: new Date()
    }
    
    sessions.value.push(newSession)
    currentSessionId.value = sessionId
    
    // Auto-save to localStorage
    saveSessionsToStorage()
    
    return sessionId
  }

  const deleteSession = (sessionId: string) => {
    const index = sessions.value.findIndex(session => session.id === sessionId)
    if (index !== -1) {
      sessions.value.splice(index, 1)
      
      // If we deleted the current session, clear current session
      if (currentSessionId.value === sessionId) {
        currentSessionId.value = null
      }
      
      saveSessionsToStorage()
    }
  }

  const setCurrentSession = (sessionId: string) => {
    const session = sessions.value.find(s => s.id === sessionId)
    if (session) {
      currentSessionId.value = sessionId
    }
  }

  const addMessage = (content: string, role: 'user' | 'assistant', sources?: string[]) => {
    if (!currentSession.value) {
      createSession()
    }

    const message: ChatMessage = {
      id: generateId(),
      content,
      role,
      timestamp: new Date(),
      sources
    }

    const session = currentSession.value!
    session.messages.push(message)
    session.updatedAt = new Date()

    // Auto-generate title from first user message
    if (session.messages.length === 1 && role === 'user') {
      session.title = content.slice(0, 50) + (content.length > 50 ? '...' : '')
    }

    saveSessionsToStorage()
    return message.id
  }

  const updateMessage = (messageId: string, updates: Partial<ChatMessage>) => {
    if (!currentSession.value) return

    const messageIndex = currentSession.value.messages.findIndex(m => m.id === messageId)
    if (messageIndex !== -1) {
      const message = currentSession.value.messages[messageIndex]
      Object.assign(message, updates)
      currentSession.value.updatedAt = new Date()
      saveSessionsToStorage()
    }
  }

  const setMessageFeedback = (messageId: string, feedback: 'helpful' | 'not-helpful') => {
    updateMessage(messageId, { feedback })
  }

  const clearCurrentSession = () => {
    if (currentSession.value) {
      currentSession.value.messages = []
      currentSession.value.updatedAt = new Date()
      saveSessionsToStorage()
    }
  }

  const setTyping = (typing: boolean) => {
    isTyping.value = typing
  }

  const setConnectionStatus = (connected: boolean) => {
    isConnected.value = connected
  }

  const setError = (error: string | null) => {
    errorMessage.value = error
  }
  // Send message to AI
  const sendMessage = async (content: string): Promise<void> => {
    try {
      setError(null)
      
      // Check if Ollama is healthy
      const isHealthy = await ollamaApi.isHealthy()
      if (!isHealthy) {
        throw new Error('AI service is not available. Please ensure Ollama is running.')
      }
      
      // Add user message
      addMessage(content, 'user')
      
      // Set typing indicator
      setTyping(true)
      
      // Prepare messages for API
      const messages: OllamaMessage[] = currentMessages.value.map(msg => ({
        role: msg.role,
        content: msg.content
      }))
      
      // Call Ollama API
      const response = await ollamaApi.chat(messages)
      
      // Add AI response
      addMessage(response.message.content, 'assistant')
      
    } catch (error) {
      console.error('Error sending message:', error)
      setError(error instanceof Error ? error.message : 'Failed to send message')
    } finally {
      setTyping(false)
    }
  }

  // Local storage functions
  const saveSessionsToStorage = () => {
    try {
      localStorage.setItem('chat-sessions', JSON.stringify(sessions.value))
      localStorage.setItem('current-session-id', currentSessionId.value || '')
    } catch (error) {
      console.error('Failed to save sessions to localStorage:', error)
    }
  }

  const loadSessionsFromStorage = () => {
    try {
      const storedSessions = localStorage.getItem('chat-sessions')
      const storedCurrentId = localStorage.getItem('current-session-id')
      
      if (storedSessions) {
        const parsedSessions = JSON.parse(storedSessions)
        // Convert date strings back to Date objects
        sessions.value = parsedSessions.map((session: any) => ({
          ...session,
          createdAt: new Date(session.createdAt),
          updatedAt: new Date(session.updatedAt),
          messages: session.messages.map((message: any) => ({
            ...message,
            timestamp: new Date(message.timestamp)
          }))
        }))
      }
      
      if (storedCurrentId) {
        currentSessionId.value = storedCurrentId || null
      }
    } catch (error) {
      console.error('Failed to load sessions from localStorage:', error)
    }
  }

  const clearAllSessions = () => {
    sessions.value = []
    currentSessionId.value = null
    localStorage.removeItem('chat-sessions')
    localStorage.removeItem('current-session-id')
  }
  // Helper functions
  const generateId = (): string => {
    return Date.now().toString(36) + Math.random().toString(36).substr(2)
  }

  // Initialize store
  loadSessionsFromStorage()

  return {
    // State
    sessions,
    currentSessionId,
    isTyping,
    isConnected,
    errorMessage,
    
    // Getters
    currentSession,
    currentMessages,
    hasActiveSessions,
    recentSessions,
    
    // Actions
    createSession,
    deleteSession,
    setCurrentSession,
    addMessage,
    updateMessage,
    setMessageFeedback,
    clearCurrentSession,
    setTyping,
    setConnectionStatus,
    setError,
    sendMessage,
    saveSessionsToStorage,
    loadSessionsFromStorage,
    clearAllSessions
  }
})
