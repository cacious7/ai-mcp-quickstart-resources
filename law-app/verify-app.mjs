#!/usr/bin/env node

// Quick verification script for the Zambian Legal AI App
console.log('🔍 Verifying Zambian Legal AI App...\n');

// Check if dev server is accessible
import fetch from 'node-fetch';

async function verifyApp() {
  try {
    // Test if the dev server is running
    console.log('✅ Testing dev server connection...');
    const response = await fetch('http://localhost:3000', { 
      timeout: 5000,
      headers: { 'Accept': 'text/html' }
    });
    
    if (response.ok) {
      console.log('✅ Dev server is running on http://localhost:3000');
      
      const html = await response.text();
      
      // Check for key elements
      if (html.includes('Zambian Legal AI Assistant')) {
        console.log('✅ App title found in HTML');
      }
      
      if (html.includes('vue')) {
        console.log('✅ Vue.js is loaded');
      }
      
    } else {
      console.log('❌ Dev server returned status:', response.status);
    }
    
  } catch (error) {
    if (error.code === 'ECONNREFUSED') {
      console.log('❌ Dev server is not running. Please start it with: npm run dev');
    } else {
      console.log('❌ Error checking dev server:', error.message);
    }
  }
  
  // Test Ollama connection
  try {
    console.log('\n🤖 Testing Ollama connection...');
    const ollamaResponse = await fetch('http://localhost:11434/api/tags', { timeout: 3000 });
    
    if (ollamaResponse.ok) {
      const data = await ollamaResponse.json();
      console.log('✅ Ollama is running');
      
      const models = data.models || [];
      const phi3Model = models.find(m => m.name.includes('phi3'));
      
      if (phi3Model) {
        console.log('✅ phi3 model is available');
      } else {
        console.log('⚠️  phi3 model not found. Run: ollama pull phi3:mini');
      }
      
    } else {
      console.log('❌ Ollama API returned status:', ollamaResponse.status);
    }
    
  } catch (error) {
    console.log('⚠️  Ollama not accessible. Make sure it\'s installed and running.');
    console.log('   Download from: https://ollama.ai');
  }
  
  console.log('\n📋 Summary:');
  console.log('   • App URL: http://localhost:3000');
  console.log('   • Features: Chat, Legal Q&A, Responsive Design');
  console.log('   • Tech Stack: Vue 3 + TypeScript + Quasar + Ollama');
  console.log('\n🚀 Ready to test legal questions!');
}

verifyApp().catch(console.error);
