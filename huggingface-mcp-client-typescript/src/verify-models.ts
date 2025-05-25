#!/usr/bin/env node
import { ModelFactory } from './model-factory.js';
import dotenv from 'dotenv';

dotenv.config();

async function verifyModels() {
  console.log('🔍 Verifying Hugging Face models...');
  
  try {
    // Create provider
    const provider = ModelFactory.createProvider();
    
    // Initialize provider (which checks connection)
    await provider.initialize();
    
    console.log('✅ Model verification completed successfully!');
    
    // Quick test with a simple query
    if (process.argv.includes('--model')) {
      console.log('🧪 Testing model with a simple query...');
      const response = await provider.generateResponse(
        'What is the capital of France?', 
        [], // no tools
        [] // no context
      );
      
      console.log('\nModel Response:');
      console.log('---------------');
      console.log(response.content);
      console.log('---------------');
      
      if (response.toolCalls && response.toolCalls.length > 0) {
        console.log('Tool calls detected:', response.toolCalls.length);
      }
    }
    
  } catch (error) {
    console.error('❌ Model verification failed:', error);
    process.exit(1);
  }
}

verifyModels();
