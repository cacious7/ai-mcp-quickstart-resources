// Export all services from a single location
export { ollamaApi, OllamaApiService } from './ollamaApi'

// Re-export types for convenience
export type { 
  OllamaMessage, 
  OllamaResponse, 
  OllamaModel, 
  ModelInfo,
  ChatRequest, 
  LegalContext 
} from './ollamaApi'
