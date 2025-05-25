import axios from 'axios'
import type { AxiosInstance, AxiosResponse } from 'axios'

export interface OllamaMessage {
  role: 'user' | 'assistant' | 'system'
  content: string
}

export interface OllamaResponse {
  model: string
  created_at: string
  message: OllamaMessage
  done: boolean
  total_duration?: number
  load_duration?: number
  prompt_eval_count?: number
  prompt_eval_duration?: number
  eval_count?: number
  eval_duration?: number
}

export interface OllamaModel {
  name: string
  model: string
  modified_at: string
  size: number
  digest: string
  details: {
    parent_model: string
    format: string
    family: string
    families: string[]
    parameter_size: string
    quantization_level: string
  }
}

export interface ChatRequest {
  model: string
  messages: OllamaMessage[]
  stream?: boolean
  options?: {
    temperature?: number
    top_p?: number
    top_k?: number
    repeat_penalty?: number
    seed?: number
    num_ctx?: number
    num_predict?: number
  }
}

export interface LegalContext {
  laws: string[]
  categories: string[]
  sources: string[]
}

class OllamaApiService {
  private client: AxiosInstance
  private baseUrl: string
  private defaultModel: string

  constructor(baseUrl: string = 'http://localhost:11434') {
    this.baseUrl = baseUrl
    this.defaultModel = import.meta.env.VITE_OLLAMA_MODEL || 'phi3'
    
    this.client = axios.create({
      baseURL: this.baseUrl,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Request interceptor for logging
    this.client.interceptors.request.use(
      (config) => {
        console.log('Ollama API Request:', config.method?.toUpperCase(), config.url)
        return config
      },
      (error) => {
        console.error('Ollama API Request Error:', error)
        return Promise.reject(error)
      }
    )

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => {
        return response
      },
      (error) => {
        console.error('Ollama API Response Error:', error)
        
        if (error.code === 'ECONNREFUSED') {
          throw new Error('Cannot connect to Ollama. Please ensure Ollama is running on ' + this.baseUrl)
        }
        
        if (error.response?.status === 404) {
          throw new Error('Model not found. Please ensure the model is installed in Ollama.')
        }
        
        throw error
      }
    )
  }

  /**
   * Check if Ollama is running and accessible
   */
  async isHealthy(): Promise<boolean> {
    try {
      const response = await this.client.get('/api/tags')
      return response.status === 200
    } catch {
      return false
    }
  }

  /**
   * Get list of available models
   */
  async getModels(): Promise<OllamaModel[]> {
    try {
      const response: AxiosResponse<{ models: OllamaModel[] }> = await this.client.get('/api/tags')
      return response.data.models || []
    } catch (error: unknown) {
      console.error('Failed to fetch models:', error)
      throw new Error('Failed to fetch available models from Ollama')
    }
  }

  /**
   * Send a chat message to Ollama
   */
  async chat(messages: OllamaMessage[], model?: string, options?: ChatRequest['options']): Promise<OllamaResponse> {
    const request: ChatRequest = {
      model: model || this.defaultModel,
      messages: this.prepareLegalMessages(messages),
      stream: false,
      options: {
        temperature: 0.7,
        top_p: 0.9,
        num_ctx: 4096,
        ...options
      }
    }

    try {
      const response: AxiosResponse<OllamaResponse> = await this.client.post('/api/chat', request)
      return response.data
    } catch (error: unknown) {
      console.error('Chat request failed:', error)
      throw new Error('Failed to get response from AI model')
    }
  }

  /**
   * Stream chat response from Ollama
   */
  async *chatStream(messages: OllamaMessage[], model?: string, options?: ChatRequest['options']): AsyncGenerator<OllamaResponse> {
    const request: ChatRequest = {
      model: model || this.defaultModel,
      messages: this.prepareLegalMessages(messages),
      stream: true,
      options: {
        temperature: 0.7,
        top_p: 0.9,
        num_ctx: 4096,
        ...options
      }
    }

    try {
      const response = await this.client.post('/api/chat', request, {
        responseType: 'stream'
      })

      const reader = response.data
      let buffer = ''

      for await (const chunk of reader) {
        buffer += chunk.toString()
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (line.trim()) {
            try {
              const data: OllamaResponse = JSON.parse(line)
              yield data
            } catch (parseError) {
              console.warn('Failed to parse streaming response:', line)
            }
          }
        }
      }
    } catch (error) {
      console.error('Stream chat request failed:', error)
      throw new Error('Failed to stream response from AI model')
    }
  }

  /**
   * Prepare messages with legal context and system prompts
   */
  private prepareLegalMessages(messages: OllamaMessage[]): OllamaMessage[] {
    const systemPrompt: OllamaMessage = {
      role: 'system',
      content: `You are a helpful AI assistant specialized in Zambian law. Your role is to provide accurate, informative responses about Zambian legal matters while following these guidelines:

IMPORTANT GUIDELINES:
1. Always provide accurate information based on Zambian law
2. Clearly distinguish between general information and legal advice
3. Include appropriate disclaimers about the limitations of AI-generated legal information
4. Cite relevant laws, acts, or regulations when possible
5. Use clear, simple language that non-lawyers can understand
6. When uncertain, acknowledge limitations and recommend consulting legal professionals

DISCLAIMER REQUIREMENT:
Always include a disclaimer that your response is for informational purposes only and does not constitute legal advice. Recommend consulting with qualified legal professionals for specific legal matters.

RESPONSE FORMAT:
- Provide clear, structured responses
- Use bullet points or numbered lists when appropriate
- Include relevant legal sources when available
- End with an appropriate disclaimer

Remember: You are providing general legal information about Zambian law, not personalized legal advice.`
    }

    // Add system prompt if not already present
    if (messages.length === 0 || messages[0].role !== 'system') {
      return [systemPrompt, ...messages]
    }

    return messages
  }
}

export { OllamaApiService }
export const ollamaApi = new OllamaApiService(import.meta.env.VITE_OLLAMA_HOST)
