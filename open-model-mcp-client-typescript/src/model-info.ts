/**
 * Information about supported models for the MCP client
 */
export interface ModelInfo {
  id: string;
  name: string;
  size: string;
  functionCalling: 'Excellent' | 'Good' | 'Basic';
  memoryRequirements: string;
  description: string;
}

/**
 * Recommended models for the MCP client
 */
export const RECOMMENDED_MODELS: ModelInfo[] = [
  {
    id: 'phi4-mini',
    name: 'Phi-4-mini',
    size: '3.8B',
    functionCalling: 'Good',
    memoryRequirements: '4-8GB',
    description: 'Fast, lightweight model with good function calling support. Best for environments with limited resources.'
  },
  {
    id: 'dolphin3',
    name: 'Dolphin 3',
    size: '8B',
    functionCalling: 'Excellent',
    memoryRequirements: '8-12GB',
    description: 'Based on Llama 3.1 8B, specifically designed for function calling. Good balance of performance and resource usage.'
  },
  {
    id: 'phi4-mini-reasoning',
    name: 'Phi-4-mini-reasoning',
    size: '3.8B',
    functionCalling: 'Good',
    memoryRequirements: '4-8GB',
    description: 'Enhanced reasoning capabilities with the same lightweight footprint as Phi-4-mini. Good for complex reasoning tasks.'
  }
];

/**
 * Get model info by model ID
 * @param modelId The model ID to lookup
 * @returns The model info or the first model if not found
 */
export function getModelInfo(modelId: string): ModelInfo {
  return RECOMMENDED_MODELS.find(model => model.id === modelId) || RECOMMENDED_MODELS[0];
}

/**
 * Get default model recommendation based on available system memory
 * @returns The recommended model ID
 */
export function getDefaultModel(): string {
  try {
    // Default to llama3 as it's the most widely supported
    return 'phi4-mini';
  } catch (error) {
    console.error('Error determining default model:', error);
    return 'phi4-mini';
  }
}
