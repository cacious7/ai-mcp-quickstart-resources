# Zambian Legal AI Assistant

A Vue 3 + TypeScript application that provides access to Zambian laws and legal information through an AI assistant powered by Ollama.

## Features

- **AI Legal Assistant**: Ask questions about Zambian law in plain language
- **Law Browser**: Browse through Zambian legal documents by category
- **Progressive Web App**: Install on your device for offline access
- **Responsive Design**: Works on desktop and mobile devices
- **Real-time Chat**: Interactive chat interface with AI responses
- **Legal Disclaimers**: Proper disclaimers and citations for all legal information

## Technology Stack

- **Frontend**: Vue 3, TypeScript, Vite, Quasar UI
- **State Management**: Pinia
- **Routing**: Vue Router
- **Styling**: Sass/SCSS with Quasar components
- **PWA Support**: Vite PWA Plugin
- **AI Integration**: Ollama API with phi3:mini model
- **HTTP Client**: Axios

## Quick Start

### Prerequisites
1. **Node.js** (version 18+)
2. **Ollama** installed and running
3. **phi3:mini model** pulled in Ollama

### Installation

```bash
# Clone and navigate to the project
cd law-app

# Install dependencies
npm install

# Install Sass preprocessor (if not already installed)
npm install -D sass-embedded

# Start development server
npm run dev
```

### Setup Ollama
```bash
# Install Ollama from https://ollama.ai
# Then pull the phi3 model
ollama pull phi3:mini
```

The application will be available at `http://localhost:3000`

## Development Commands

```bash
# Start development server
npm run dev

# Type checking
npm run type-check

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint

# Format code
npm run format
```

## Testing the Application

1. **Open** http://localhost:3000
2. **Click** "Ask Legal Questions" or use example questions
3. **Ask** questions like:
   - "What are my employment rights in Zambia?"
   - "How do I get married legally in Zambia?"
   - "What should I do if I'm arrested?"

## Troubleshooting

### Common Issues

1. **Sass dependency error**: 
   ```bash
   npm install -D sass-embedded
   ```

2. **Ollama connection failed**: 
   - Ensure Ollama is running on port 11434
   - Check if phi3:mini model is available: `ollama list`

3. **Port 3000 already in use**: 
   - Change port in `vite.config.ts` or kill existing process

## Project Structure

```
src/
├── assets/           # Static assets
├── components/       # Vue components
│   ├── icons/       # SVG icon components
│   └── layout/      # Layout components
├── router/          # Vue Router configuration
├── services/        # API services (Ollama integration)
├── stores/          # Pinia state management
├── views/           # Page components
└── main.ts          # Application entry point
```

## Important Notes

- This application provides general legal information only
- Responses include appropriate disclaimers
- Not a substitute for professional legal advice
- Designed specifically for Zambian legal context
