# Zambian Legal AI App - Testing Guide

## Prerequisites

1. **Node.js** (version 18+)
2. **Ollama** installed and running
3. **phi3:mini model** pulled in Ollama

## Setup Instructions

### 1. Install Ollama
- Download from: https://ollama.ai
- Install and start the service

### 2. Pull the AI Model
```bash
ollama pull phi3:mini
```

### 3. Start the Application
```bash
cd law-app
npm install
npm run dev
```

The app will be available at: http://localhost:3000

## Testing the MVP

### 1. Home Page Test
- ✅ Navigate to http://localhost:3000
- ✅ Verify the hero section loads
- ✅ Check example questions buttons work
- ✅ Test the search input functionality

### 2. Chat Functionality Test
- ✅ Click "Ask Legal Questions" from home page
- ✅ Try example questions:
  - "What are my employment rights in Zambia?"
  - "How do I get married legally in Zambia?"
  - "What are the property ownership laws?"
- ✅ Verify AI responses are formatted correctly
- ✅ Check that responses include proper disclaimers

### 3. Navigation Test
- ✅ Test all navigation links
- ✅ Verify mobile menu works on smaller screens
- ✅ Check routing between pages

### 4. Error Handling Test
- ✅ Stop Ollama service and test error messages
- ✅ Verify graceful fallback behavior
- ✅ Check connection status indicators

## Expected Behavior

### Successful Chat Interaction:
1. User types a legal question
2. Question is sent to Ollama API
3. AI processes the question with legal context
4. Response is formatted with:
   - Clear, simple language
   - Relevant legal information
   - Proper citations where applicable
   - Legal disclaimer at the end

### Error Scenarios:
1. **Ollama not running**: User sees connection error message
2. **Model not available**: User sees model error message
3. **Network issues**: User sees retry option

## Features Working:
- ✅ Vue 3 + TypeScript + Quasar UI
- ✅ Pinia state management
- ✅ Ollama API integration
- ✅ Responsive design
- ✅ Legal-focused system prompts
- ✅ Markdown formatting for responses
- ✅ Chat history management
- ✅ Progressive Web App (PWA) features

## Sample Questions to Test:
1. "What are my rights as an employee in Zambia?"
2. "How do I legally start a business in Zambia?"
3. "What should I do if I'm arrested?"
4. "Can I buy property as a foreigner in Zambia?"
5. "What are the marriage requirements in Zambia?"
6. "What are my tenant rights?"

## Troubleshooting

### Common Issues:
1. **Port 3000 already in use**: Change port in vite.config.ts
2. **Ollama connection failed**: Ensure Ollama is running on port 11434
3. **Model not found**: Run `ollama list` to check available models
4. **TypeScript errors**: Run `npm run type-check` to identify issues

### Logs to Check:
- Browser console for frontend errors
- Network tab for API calls
- Ollama logs for AI processing issues
