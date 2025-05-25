/**
 * A utility for verifying model capabilities with function calling
 */
import { OllamaProvider } from './providers/ollama-provider.js';
import { RECOMMENDED_MODELS } from './model-info.js';
import dotenv from 'dotenv';

// Example weather tool schema
const EXAMPLE_TOOL = {
  name: 'get_weather',
  description: 'Get the current weather for a location',
  input_schema: {
    type: 'object',
    properties: {
      location: {
        type: 'string',
        description: 'The city and state/country'
      },
      unit: {
        type: 'string',
        enum: ['celsius', 'fahrenheit'],
        description: 'The unit for temperature'
      }
    },
    required: ['location']
  }
};

// Example system message for function calling
const SYSTEM_MESSAGE = {
  role: 'system',
  content: 'You are a helpful assistant that can check the weather using tools when asked about weather conditions.'
};

// Example queries that should trigger function calling
const TEST_QUERIES = [
  "What's the weather like in New York?",
  "Tell me the temperature in Tokyo in celsius",
  "Is it raining in London right now?"
];

/**
 * Verify function calling capabilities for a specific model
 * @param modelId The model ID to test
 * @returns Test results object
 */
export async function verifyModel(modelId: string): Promise<{
  modelId: string;
  modelName: string;
  success: boolean;
  supportsFunctionCalling: boolean;
  avgResponseTimeMs: number;
  details: string[];
}> {
  // Set up test environment
  const start = Date.now();
  const modelInfo = RECOMMENDED_MODELS.find(model => model.id === modelId);
  const details: string[] = [];
  let functionCallSuccessCount = 0;
  
  // Create test provider with the specified model
  process.env.OLLAMA_MODEL = modelId;
  const provider = new OllamaProvider();
  
  try {
    // Initialize the provider (and download model if needed)
    await provider.initialize();
    details.push(`✅ Model ${modelId} initialized successfully`);
    
    // Run tests for function calling
    for (const query of TEST_QUERIES) {
      try {
        details.push(`🔍 Testing query: "${query}"`);
        const response = await provider.generateResponse(
          query, 
          [EXAMPLE_TOOL], 
          [SYSTEM_MESSAGE]
        );
        
        // Check for function calls
        if (response.toolCalls && response.toolCalls.length > 0) {
          functionCallSuccessCount++;
          const toolCall = response.toolCalls[0];
          details.push(`✅ Tool called: ${toolCall.name} with args: ${JSON.stringify(toolCall.arguments)}`);
        } else {
          details.push(`❌ No tool calls detected. Model response: "${response.content.substring(0, 100)}..."`);
        }
      } catch (error: any) {
        details.push(`❌ Error during test: ${error.message || error}`);
      }
    }
    
    const duration = Date.now() - start;
    const avgResponseTimeMs = duration / TEST_QUERIES.length;
    
    return {
      modelId,
      modelName: modelInfo?.name || modelId,
      success: true,
      supportsFunctionCalling: functionCallSuccessCount > 0,
      avgResponseTimeMs,
      details
    };
  } catch (error: any) {
    return {
      modelId,
      modelName: modelInfo?.name || modelId,
      success: false,
      supportsFunctionCalling: false,
      avgResponseTimeMs: 0,
      details: [`❌ Failed to test model: ${error.message || error}`]
    };
  }
}

/**
 * Verify all recommended models
 * @returns Test results for all models
 */
export async function verifyAllModels(): Promise<any[]> {
  const results = [];
  for (const model of RECOMMENDED_MODELS) {
    console.log(`\n🔍 Testing model: ${model.name} (${model.id})`);
    const result = await verifyModel(model.id);
    results.push(result);
    
    // Print test results
    console.log(`${result.success ? '✅' : '❌'} ${model.name} test completed`);
    console.log(`Function calling: ${result.supportsFunctionCalling ? '✅ Working' : '❌ Not working'}`);
    console.log(`Average response time: ${Math.round(result.avgResponseTimeMs)}ms`);
    console.log('-----------------------------------');
  }
  return results;
}
