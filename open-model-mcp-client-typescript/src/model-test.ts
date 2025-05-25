// Model comparison test script
import { ModelFactory } from './model-factory.js';
import dotenv from 'dotenv';
import * as fs from 'fs';
import * as path from 'path';

// Function to log test results
function logResults(model: string, startTime: number, endTime: number, success: boolean, error?: string) {
  const resultDir = path.join(process.cwd(), 'test-results');
  if (!fs.existsSync(resultDir)) {
    fs.mkdirSync(resultDir);
  }
  
  const timestamp = new Date().toISOString().replace(/:/g, '-');
  const responseTime = endTime - startTime;
  
  const resultLine = `${timestamp},${model},${responseTime}ms,${success ? 'SUCCESS' : 'FAILURE'},${error || ''}\n`;
  fs.appendFileSync(path.join(resultDir, 'model-tests.csv'), resultLine);

  console.log(`\n===== TEST RESULTS =====`);
  console.log(`Model: ${model}`);
  console.log(`Response time: ${responseTime}ms (${responseTime / 1000} seconds)`);
  console.log(`Status: ${success ? 'SUCCESS' : 'FAILURE'}`);
  if (error) {
    console.log(`Error: ${error}`);
  }
  console.log(`========================\n`);
}

// Main test function
async function testModel() {
  dotenv.config();
  const model = process.env.OLLAMA_MODEL || 'unknown';
  
  console.log(`Testing model: ${model}`);
  console.log(`Temperature: ${process.env.MODEL_TEMPERATURE || '0.7'}`);
  console.log(`Top_p: ${process.env.MODEL_TOP_P || '0.9'}`);
  
  try {
    // Initialize provider
    const provider = ModelFactory.createProvider();
    await provider.initialize();
    
    // Test function calling with a weather-related query
    const weatherTool = {
      name: 'get_weather',
      description: 'Get the current weather in a given location',
      input_schema: {
        type: 'object',
        required: ['location'],
        properties: {
          location: {
            type: 'string',
            description: 'The city and state, e.g. San Francisco, CA'
          },
          unit: {
            type: 'string',
            enum: ['celsius', 'fahrenheit'],
            description: 'The unit of temperature'
          }
        }
      }
    };

    console.log('Sending query with function calling...');
    const startTime = Date.now();

    const response = await provider.generateResponse(
      'What is the weather like in Boston right now?',
      [weatherTool],
      [{ role: 'system', content: 'You are a helpful assistant with access to up-to-date information.' }]
    );

    const endTime = Date.now();
    
    console.log('Response content:', response.content);
    console.log('Tool calls:', JSON.stringify(response.toolCalls, null, 2));
    
    // Check if the tool was called and with the right parameters
    const success = response.toolCalls.length > 0 && 
                    response.toolCalls[0].name === 'get_weather' && 
                    response.toolCalls[0].arguments.location === 'Boston';
    
    logResults(model, startTime, endTime, success);
  } catch (error) {
    console.error('Error during test:', error);
    logResults(model, Date.now(), Date.now(), false, error?.toString());
  }
}

// Run the test
testModel().catch(err => {
  console.error('Unhandled error:', err);
  process.exit(1);
});
