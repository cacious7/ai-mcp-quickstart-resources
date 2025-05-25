#!/usr/bin/env node

/**
 * Open MCP Model Setup Utility
 * 
 * This script helps users verify and configure models for the Open MCP Client.
 * - Checks if Ollama is running
 * - Verifies model availability
 * - Sets up the .env configuration with the best model
 */

import { verifyAllModels } from './model-verifier.js';
import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';
import { createInterface } from 'readline/promises';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const ENV_FILE_PATH = path.join(__dirname, '../.env');

// Create readline interface
const rl = createInterface({
  input: process.stdin,
  output: process.stdout
});

async function main() {
  console.log("🚀 Open MCP Model Setup Utility");
  console.log("===============================");
  console.log("This utility will help you set up the best model for your Open MCP Client.");

  try {
    // Check if Ollama is running
    console.log("\n🔍 Checking for Ollama service...");
    
    // Run model tests
    console.log("\n🧪 Testing models for function calling capability...");
    console.log("This may take a few minutes as models are downloaded if needed.");
    
    const modelResults = await verifyAllModels();
    
    // Filter for working models
    const workingModels = modelResults.filter(result => 
      result.success && result.supportsFunctionCalling
    );
    
    if (workingModels.length === 0) {
      console.log("\n❌ No models with working function calling were found.");
      console.log("Please check your Ollama installation and try again.");
      return;
    }
    
    // Sort working models by response time
    workingModels.sort((a, b) => a.avgResponseTimeMs - b.avgResponseTimeMs);
    
    // Show results and recommendations
    console.log("\n📊 Model Test Results:");
    for (const result of workingModels) {
      console.log(`- ${result.modelName} (${result.modelId}): Response time: ${Math.round(result.avgResponseTimeMs)}ms`);
    }
    
    // Get the best model
    const bestModel = workingModels[0];
    console.log(`\n💡 Recommended model: ${bestModel.modelName} (${bestModel.modelId})`);
    
    // Ask user if they want to update .env
    const confirmUpdate = await rl.question(`\nWould you like to update your .env file to use ${bestModel.modelId}? (y/N): `);
    
    if (confirmUpdate.toLowerCase() === 'y') {
      // Read current .env
      let envContent;
      try {
        envContent = await fs.readFile(ENV_FILE_PATH, 'utf8');
      } catch (e) {
        // If .env doesn't exist, create a template
        envContent = `# Configuration for Open Model MCP Client

# Ollama settings
OLLAMA_HOST=http://localhost:11434

# Model parameters
MODEL_TEMPERATURE=0.7
MODEL_TOP_P=0.9
`;
      }
      
      // Check if OLLAMA_MODEL is already set
      if (envContent.includes('OLLAMA_MODEL=')) {
        // Replace the existing line
        envContent = envContent.replace(
          /OLLAMA_MODEL=.*/,
          `OLLAMA_MODEL=${bestModel.modelId}`
        );
      } else {
        // Add the model setting
        envContent += `\n# Current model to use\nOLLAMA_MODEL=${bestModel.modelId}\n`;
      }
      
      // Write back to .env
      await fs.writeFile(ENV_FILE_PATH, envContent);
      console.log(`\n✅ Updated .env file with OLLAMA_MODEL=${bestModel.modelId}`);
    } else {
      console.log('\nNo changes made to .env file.');
    }
    
    console.log('\n🎉 Setup complete! You can now run the Open MCP Client.');
    console.log('To start the client with the weather server:');
    console.log('npm start -- ../weather-server-typescript/build/index.js');
    console.log('or');
    console.log('npm start -- ../weather-server-python/weather.py');
    
  } catch (error) {
    console.error('❌ Error during setup:', error);
    console.log('\nTroubleshooting:');
    console.log('1. Make sure Ollama is installed and running');
    console.log('2. Check your internet connection for model downloads');
    console.log('3. See the INSTALLATION.md file for detailed setup instructions');
  } finally {
    rl.close();
  }
}

main().catch(console.error);
