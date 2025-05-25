import { HuggingFaceProvider } from './providers/huggingface-provider.js';
import { getModelInfo, getDefaultModel } from './model-info.js';
import dotenv from 'dotenv';

export class ModelFactory {
  /**
   * Create the model provider
   * @returns HuggingFace provider instance
   */
  static createProvider(): HuggingFaceProvider {
    // Ensure environment variables are loaded
    dotenv.config();
    
    // Get the model ID from environment or use default
    const modelId = process.env.HUGGINGFACE_MODEL || getDefaultModel();
    
    // Get model information
    const modelInfo = getModelInfo(modelId);
    
    console.log(`Creating model provider for ${modelInfo.name} (${modelInfo.size})`);
    console.log(`Model description: ${modelInfo.description}`);
    console.log(`Function calling quality: ${modelInfo.functionCalling}`);
    console.log(`Memory requirements: ${modelInfo.memoryRequirements}`);
    
    return new HuggingFaceProvider();
  }
}
