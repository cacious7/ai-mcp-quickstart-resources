import { HfInference } from '@huggingface/inference';
import dotenv from 'dotenv';
import readline from 'readline/promises';
import fs from 'fs/promises';
import path from 'path';

dotenv.config();

// Available models
const AVAILABLE_MODELS = [
  {
    id: 'mistralai/Mistral-7B-Instruct-v0.2',
    name: 'Mistral 7B Instruct v0.2',
    description: 'Good instruction-tuned model for general purpose tasks'
  },
  {
    id: 'meta-llama/Llama-2-7b-chat-hf',
    name: 'Llama 2 7B Chat',
    description: 'Meta\'s chat model with balanced performance'
  },
  {
    id: 'OpenAssistant/oasst-sft-4-pythia-12b-epoch-3.5',
    name: 'OpenAssistant 12B',
    description: 'Larger model with strong function calling capabilities'
  },
  {
    id: 'microsoft/phi-2',
    name: 'Microsoft Phi-2',
    description: 'Lightweight model (2.7B) good for resource-constrained environments'
  },
  {
    id: 'tiiuae/falcon-7b-instruct',
    name: 'Falcon 7B Instruct',
    description: 'Instruction-tuned model from TII'
  }
];

/**
 * Setup wizard for the Hugging Face MCP client
 */
async function setupModels() {
  console.log('🚀 Welcome to the Hugging Face MCP Client Setup Wizard!');
  console.log('This wizard will help you configure your environment for using Hugging Face models.');
  console.log('------------------------------------------------\n');
  
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });
  
  try {
    // Check for API key
    let apiKey = process.env.HUGGINGFACE_API_KEY;
    if (!apiKey) {
      console.log('❓ No Hugging Face API key found in .env file.');
      apiKey = await rl.question('Please enter your Hugging Face API key: ');
      
      if (!apiKey) {
        console.log('⚠️ No API key provided. You\'ll need to add it to the .env file later.');
      } else {
        // Update .env file
        await updateEnvFile('HUGGINGFACE_API_KEY', apiKey);
        console.log('✅ API key added to .env file.');
      }
    } else {
      console.log('✅ Hugging Face API key found in .env file.');
    }
    
    // Select model
    console.log('\n📋 Available models:');
    AVAILABLE_MODELS.forEach((model, index) => {
      console.log(`${index + 1}. ${model.name}`);
      console.log(`   ${model.description}`);
      console.log(`   ID: ${model.id}`);
    });
    
    const modelSelection = await rl.question('\n❓ Enter the number of the model you want to use (1-5) [default: 2]: ');
    let selectedModelIndex = parseInt(modelSelection) - 1;
    
    if (isNaN(selectedModelIndex) || selectedModelIndex < 0 || selectedModelIndex >= AVAILABLE_MODELS.length) {
      selectedModelIndex = 1; // Default to Llama 2
      console.log(`Using default model: ${AVAILABLE_MODELS[selectedModelIndex].name}`);
    }
    
    const selectedModel = AVAILABLE_MODELS[selectedModelIndex];
    console.log(`✅ Selected model: ${selectedModel.name}`);
    
    // Update .env file with model selection
    await updateEnvFile('HUGGINGFACE_MODEL', selectedModel.id);
    
    // Test API connection if key is provided
    if (apiKey) {
      console.log('\n🔍 Testing connection to Hugging Face API...');
      try {
        const inference = new HfInference(apiKey);
        await inference.httpClient.get('https://api-inference.huggingface.co/status');
        console.log('✅ Successfully connected to Hugging Face API!');
      } catch (error: any) {
        console.error('❌ Failed to connect to Hugging Face API.');
        if (error.response?.status === 401) {
          console.error('   Error: Invalid API key. Please check your credentials.');
        } else {
          console.error(`   Error: ${error.message || 'Unknown error'}`);
        }
      }
    }
    
    console.log('\n🎉 Setup complete!');
    console.log('\n📝 Next steps:');
    console.log('1. Run the model verification: npm run verify');
    console.log('2. Connect to a weather server: npm start -- ../weather-server-typescript/build/index.js');
    
  } catch (error) {
    console.error('❌ Setup failed:', error);
  } finally {
    rl.close();
  }
}

/**
 * Update a value in the .env file
 */
async function updateEnvFile(key: string, value: string): Promise<void> {
  try {
    const envPath = path.join(process.cwd(), '.env');
    let content = '';
    
    try {
      content = await fs.readFile(envPath, 'utf8');
    } catch (error) {
      // File doesn't exist, create it
      content = '# Configuration for Hugging Face MCP Client\n\n';
    }
    
    // Check if key already exists
    const regex = new RegExp(`^${key}=.*$`, 'm');
    if (regex.test(content)) {
      // Replace existing value
      content = content.replace(regex, `${key}=${value}`);
    } else {
      // Add new key/value
      content += `\n${key}=${value}`;
    }
    
    await fs.writeFile(envPath, content, 'utf8');
  } catch (error) {
    console.error(`Failed to update .env file:`, error);
    throw error;
  }
}

// Run the setup
setupModels();
