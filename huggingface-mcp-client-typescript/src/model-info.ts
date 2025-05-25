/**
 * Information about supported models
 */
export interface ModelInfo {
  id: string;
  name: string;
  size: string;
  description: string;
  functionCalling: 'Poor' | 'Basic' | 'Good' | 'Excellent';
  memoryRequirements: string;
}

/**
 * All supported models
 */
const SUPPORTED_MODELS: ModelInfo[] = [
  {
    id: 'mistralai/Mistral-7B-Instruct-v0.2',
    name: 'Mistral 7B Instruct',
    size: '7B',
    description: 'Instruction-tuned model with good general purpose capabilities',
    functionCalling: 'Good',
    memoryRequirements: '8-16GB',
  },
  {
    id: 'meta-llama/Llama-2-7b-chat-hf',
    name: 'Llama 2 7B Chat',
    size: '7B',
    description: 'Meta\'s chat-tuned model with balanced performance',
    functionCalling: 'Basic',
    memoryRequirements: '8-16GB',
  },
  {
    id: 'OpenAssistant/oasst-sft-4-pythia-12b-epoch-3.5',
    name: 'OpenAssistant 12B',
    size: '12B',
    description: 'Open Assistant model with strong function calling capabilities',
    functionCalling: 'Good',
    memoryRequirements: '16-24GB',
  },
  {
    id: 'tiiuae/falcon-7b-instruct',
    name: 'Falcon 7B Instruct',
    size: '7B',
    description: 'Instruction-tuned model from TII',
    functionCalling: 'Basic',
    memoryRequirements: '8-16GB',
  },
  {
    id: 'microsoft/phi-2',
    name: 'Phi-2',
    size: '2.7B',
    description: 'Lightweight model with strong reasoning capabilities',
    functionCalling: 'Basic',
    memoryRequirements: '4-8GB',
  },
];

/**
 * Default model ID to use if none is specified
 */
export function getDefaultModel(): string {
  return 'meta-llama/Llama-2-7b-chat-hf';
}

/**
 * Get information about a specific model by ID
 */
export function getModelInfo(modelId: string): ModelInfo {
  const model = SUPPORTED_MODELS.find(m => m.id === modelId);
  if (!model) {
    // If model not found, return default with warning
    console.warn(`Model '${modelId}' not found in supported models. Using generic info.`);
    return {
      id: modelId,
      name: modelId.split('/').pop() || modelId,
      size: 'Unknown',
      description: 'Custom model',
      functionCalling: 'Basic',
      memoryRequirements: 'Unknown',
    };
  }
  return model;
}
