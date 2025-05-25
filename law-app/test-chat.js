// Quick test of the Ollama chat functionality
const axios = require('axios');

async function testOllamaChat() {
    try {
        console.log('Testing Ollama chat functionality...');
        
        const response = await axios.post('http://localhost:11434/api/chat', {
            model: 'phi3:latest',
            messages: [
                {
                    role: 'system',
                    content: 'You are a helpful AI assistant specializing in Zambian law. Provide accurate, helpful legal information while noting that this is not legal advice.'
                },
                {
                    role: 'user',
                    content: 'What is the legal age of consent in Zambia?'
                }
            ],
            stream: false
        });

        console.log('✅ Ollama response received!');
        console.log('Response:', response.data.message.content);
        
    } catch (error) {
        console.error('❌ Error testing Ollama:', error.message);
        if (error.response) {
            console.error('Status:', error.response.status);
            console.error('Data:', error.response.data);
        }
    }
}

testOllamaChat();
