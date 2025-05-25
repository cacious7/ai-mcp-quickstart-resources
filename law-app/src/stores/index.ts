// Export all stores from a single location
export { useChatStore } from './chat'
export { useLegalDataStore } from './legalData'

// Re-export types for convenience
export type { ChatMessage, ChatSession } from './chat'
export type { LegalDocument, LegalCategory, LegalUpdate, SearchFilters } from './legalData'
