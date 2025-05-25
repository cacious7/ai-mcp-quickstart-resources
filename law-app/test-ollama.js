// Simple test to check if Ollama is running
import axios from 'axios';

const OLLAMA_HOST = 'http://localhost:11434';

async function testOllamaConnection() {
  try {
    console.log('Testing Ollama connection...');
    
    // Test basic connectivity
    const response = await axios.get(`${OLLAMA_HOST}/api/tags`);
    console.log('✅ Ollama is running!');
    console.log('Available models:', response.data.models?.map(m => m.name) || 'No models found');
    
    // Test if phi3 model is available
    const phi3Model = response.data.models?.find(m => m.name.includes('phi3'));
    if (phi3Model) {
      console.log('✅ phi3 model is available');
    } else {
      console.log('⚠️ phi3 model not found. You may need to pull it with: ollama pull phi3:mini');
    }
    
  } catch (error) {
    if (error.code === 'ECONNREFUSED') {
      console.log('❌ Ollama is not running. Please start Ollama first.');
      console.log('Download and install Ollama from: https://ollama.ai');
      console.log('Then run: ollama pull phi3:mini');
    } else {
      console.log('❌ Error testing Ollama:', error.message);
    }
  }
}

testOllamaConnection();
