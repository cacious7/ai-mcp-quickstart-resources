import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useChatStore } from '@/stores/chat'
import { ollamaApi } from '@/services'

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn()
}

// Define global localStorage for the test environment
global.localStorage = localStorageMock as any

// Mock the ollama API
vi.mock('@/services', () => ({
  ollamaApi: {
    isHealthy: vi.fn(),
    chat: vi.fn(),
    cancelRequest: vi.fn(),
    getModelInfo: vi.fn(),
    getModels: vi.fn()
  }
}))

describe('Chat Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    
    // Clear localStorage mock
    localStorageMock.getItem.mockReturnValue(null)
    localStorageMock.setItem.mockClear()
    localStorageMock.removeItem.mockClear()
    localStorageMock.clear.mockClear()
    
    // Setup default mock implementations
    vi.mocked(ollamaApi.getModelInfo).mockReturnValue([
      {
        name: 'phi3',
        displayName: 'Phi-3 Mini',
        description: 'Fast and efficient',
        size: '2.3GB',
        capabilities: ['chat']
      }
    ])
    
    vi.mocked(ollamaApi.getModels).mockResolvedValue([
      {
        name: 'phi3',
        model: 'phi3',
        modified_at: '2024-01-01',
        size: 2400000000,
        digest: 'abc123',
        details: {
          parent_model: '',
          format: 'gguf',
          family: 'phi',
          families: ['phi'],
          parameter_size: '3.8B',
          quantization_level: 'Q4_0'
        }
      }
    ])
  })

  describe('Initial State', () => {
    it('should initialize with empty sessions', () => {
      const store = useChatStore()
      
      expect(store.sessions).toEqual([])
      expect(store.currentSessionId).toBeNull()
      expect(store.isTyping).toBe(false)
      expect(store.selectedModel).toBe('phi3')
    })

    it('should load available models on initialization', async () => {
      const store = useChatStore()
      
      // Wait for async initialization
      await new Promise(resolve => setTimeout(resolve, 0))
      
      expect(store.availableModels).toHaveLength(1)
      expect(store.availableModels[0].name).toBe('phi3')
    })
  })

  describe('Session Management', () => {
    it('should create a new session', () => {
      const store = useChatStore()
      
      const sessionId = store.createSession('Test Session')
      
      expect(store.sessions).toHaveLength(1)
      expect(store.currentSessionId).toBe(sessionId)
      expect(store.currentSession?.title).toBe('Test Session')
    })

    it('should create session with selected model', () => {
      const store = useChatStore()
      store.setSelectedModel('llama3')
      
      const sessionId = store.createSession('Test Session')
      
      expect(store.currentSession?.model).toBe('llama3')
    })

    it('should delete a session', () => {
      const store = useChatStore()
      
      const sessionId = store.createSession('Test Session')
      store.deleteSession(sessionId)
      
      expect(store.sessions).toHaveLength(0)
      expect(store.currentSessionId).toBeNull()
    })

    it('should set current session', () => {
      const store = useChatStore()
      
      const sessionId1 = store.createSession('Session 1')
      const sessionId2 = store.createSession('Session 2')
      
      store.setCurrentSession(sessionId1)
      
      expect(store.currentSessionId).toBe(sessionId1)
      expect(store.currentSession?.title).toBe('Session 1')
    })
  })

  describe('Message Management', () => {
    it('should add messages to current session', () => {
      const store = useChatStore()
      
      store.createSession()
      const messageId = store.addMessage('Hello', 'user')
        expect(store.currentMessages).toHaveLength(1)
      expect(store.currentMessages[0].content).toBe('Hello')
      expect(store.currentMessages[0].role).toBe('user')
      expect(store.currentMessages[0].id).toBe(messageId)
    })

    it('should auto-generate session title from first message', () => {
      const store = useChatStore()
      
      store.createSession()
      store.addMessage('What are employment laws in Zambia?', 'user')
      
      expect(store.currentSession?.title).toBe('What are employment laws in Zambia?')
    })

    it('should truncate long titles', () => {
      const store = useChatStore()
      
      store.createSession()
      const longMessage = 'This is a very long message that should be truncated when used as a session title because it exceeds the maximum length'
      store.addMessage(longMessage, 'user')
      
      expect(store.currentSession?.title).toHaveLength(53) // 50 chars + '...'
      expect(store.currentSession?.title?.endsWith('...')).toBe(true)
    })

    it('should update message feedback', () => {
      const store = useChatStore()
      
      store.createSession()
      const messageId = store.addMessage('AI response', 'assistant')
      store.setMessageFeedback(messageId, 'helpful')
      
      const message = store.currentMessages.find(m => m.id === messageId)
      expect(message?.feedback).toBe('helpful')
    })
  })

  describe('Model Selection', () => {
    it('should set selected model', () => {
      const store = useChatStore()
      
      store.setSelectedModel('llama3')
      
      expect(store.selectedModel).toBe('llama3')
    })

    it('should update current session model when changed', () => {
      const store = useChatStore()
      
      store.createSession()
      store.setSelectedModel('llama3')
      
      expect(store.currentSession?.model).toBe('llama3')
    })

    it('should load available models', async () => {
      const store = useChatStore()
      
      await store.loadAvailableModels()
      
      expect(ollamaApi.getModelInfo).toHaveBeenCalled()
      expect(ollamaApi.getModels).toHaveBeenCalled()
      expect(store.availableModels).toHaveLength(1)
    })

    it('should handle model loading errors gracefully', async () => {
      const store = useChatStore()
      
      vi.mocked(ollamaApi.getModels).mockRejectedValue(new Error('Connection failed'))
      
      await store.loadAvailableModels()
      
      // Should still have models from getModelInfo
      expect(store.availableModels).toHaveLength(1)
      expect(store.isLoadingModels).toBe(false)
    })
  })

  describe('Message Sending', () => {
    it('should send message successfully', async () => {
      const store = useChatStore()
      
      vi.mocked(ollamaApi.isHealthy).mockResolvedValue(true)
      vi.mocked(ollamaApi.chat).mockResolvedValue({
        model: 'phi3',
        created_at: '2024-01-01',
        message: {
          role: 'assistant',
          content: 'AI response'
        },
        done: true
      })
      
      store.createSession()
      await store.sendMessage('Hello')
      
      expect(store.currentMessages).toHaveLength(2)
      expect(store.currentMessages[0].content).toBe('Hello')
      expect(store.currentMessages[0].role).toBe('user')
      expect(store.currentMessages[1].content).toBe('AI response')
      expect(store.currentMessages[1].role).toBe('assistant')
    })

    it('should handle health check failure', async () => {
      const store = useChatStore()
      
      vi.mocked(ollamaApi.isHealthy).mockResolvedValue(false)
      
      store.createSession()
      await store.sendMessage('Hello')
      
      expect(store.errorMessage).toContain('AI service is not available')
      expect(store.isTyping).toBe(false)
    })

    it('should handle API errors', async () => {
      const store = useChatStore()
      
      vi.mocked(ollamaApi.isHealthy).mockResolvedValue(true)
      vi.mocked(ollamaApi.chat).mockRejectedValue(new Error('Network error'))
      
      store.createSession()
      await store.sendMessage('Hello')
      
      expect(store.errorMessage).toContain('Network error')
      expect(store.isTyping).toBe(false)
    })

    it('should handle request cancellation', async () => {
      const store = useChatStore()
      
      vi.mocked(ollamaApi.isHealthy).mockResolvedValue(true)
      vi.mocked(ollamaApi.chat).mockRejectedValue(new Error('Request was cancelled'))
      
      store.createSession()
      await store.sendMessage('Hello')
      
      expect(store.errorMessage).toBeNull()
      expect(store.isTyping).toBe(false)
    })

    it('should use specified model for sending', async () => {
      const store = useChatStore()
      
      vi.mocked(ollamaApi.isHealthy).mockResolvedValue(true)
      vi.mocked(ollamaApi.chat).mockResolvedValue({
        model: 'llama3',
        created_at: '2024-01-01',
        message: {
          role: 'assistant',
          content: 'Response from Llama3'
        },
        done: true
      })
      
      store.createSession()
      await store.sendMessage('Hello', 'llama3')
      
      expect(ollamaApi.chat).toHaveBeenCalledWith(
        expect.any(Array),
        'llama3'
      )
    })
  })

  describe('Request Cancellation', () => {
    it('should cancel current request', () => {
      const store = useChatStore()
      
      store.setTyping(true)
      store.cancelCurrentRequest()
      
      expect(ollamaApi.cancelRequest).toHaveBeenCalled()
      expect(store.isTyping).toBe(false)
    })
  })

  describe('State Management', () => {
    it('should set typing state', () => {
      const store = useChatStore()
      
      store.setTyping(true)
      expect(store.isTyping).toBe(true)
      
      store.setTyping(false)
      expect(store.isTyping).toBe(false)
    })

    it('should set connection status', () => {
      const store = useChatStore()
      
      store.setConnectionStatus(true)
      expect(store.isConnected).toBe(true)
      
      store.setConnectionStatus(false)
      expect(store.isConnected).toBe(false)
    })

    it('should set error message', () => {
      const store = useChatStore()
      
      store.setError('Test error')
      expect(store.errorMessage).toBe('Test error')
      
      store.setError(null)
      expect(store.errorMessage).toBeNull()
    })
  })

  describe('Computed Properties', () => {
    it('should compute current session correctly', () => {
      const store = useChatStore()
      
      expect(store.currentSession).toBeNull()
      
      const sessionId = store.createSession()
      expect(store.currentSession?.id).toBe(sessionId)
    })

    it('should compute current messages correctly', () => {
      const store = useChatStore()
      
      expect(store.currentMessages).toEqual([])
      
      store.createSession()
      store.addMessage('Hello', 'user')
      
      expect(store.currentMessages).toHaveLength(1)
    })

    it('should compute hasActiveSessions correctly', () => {
      const store = useChatStore()
      
      expect(store.hasActiveSessions).toBe(false)
        store.createSession()
      expect(store.hasActiveSessions).toBe(true)
    })

    it('should compute recentSessions correctly', () => {
      const store = useChatStore()
      
      // Create multiple sessions with manual timestamp assignment
      const baseTime = Date.now()
      for (let i = 0; i < 7; i++) {
        const sessionId = store.createSession(`Session ${i}`)
        // Manually set updatedAt to ensure proper ordering
        const session = store.sessions.find(s => s.id === sessionId)
        if (session) {
          session.updatedAt = new Date(baseTime + i * 1000) // 1 second apart
        }
      }
      
      expect(store.recentSessions).toHaveLength(5) // Should limit to 5
      expect(store.recentSessions[0].title).toBe('Session 6') // Most recent first
    })
  })
  describe('Persistence', () => {
    it('should save sessions to localStorage', () => {
      const store = useChatStore()
      
      store.createSession('Test Session')
      store.saveSessionsToStorage()
      
      expect(localStorageMock.setItem).toHaveBeenCalledWith('chat-sessions', expect.any(String))
      expect(localStorageMock.setItem).toHaveBeenCalledWith('current-session-id', expect.any(String))
    })

    it('should clear all sessions', () => {
      const store = useChatStore()
      
      store.createSession('Test Session')
      store.clearAllSessions()
      
      expect(store.sessions).toEqual([])
      expect(store.currentSessionId).toBeNull()
    })
  })
})
