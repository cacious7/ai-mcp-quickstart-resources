/**
 * MCP Tool definition
 */
export interface Tool {
  name: string;
  description: string;
  input_schema: Record<string, unknown>;
}

/**
 * Message format for conversation context
 */
export interface Message {
  role: 'user' | 'assistant' | 'system' | 'tool';
  content: string;
  name?: string;
}

/**
 * Tool call information
 */
export interface ToolCall {
  name: string;
  arguments: Record<string, unknown>;
}

/**
 * Response from a model
 */
export interface ModelResponse {
  content: string;
  toolCalls: ToolCall[];
}