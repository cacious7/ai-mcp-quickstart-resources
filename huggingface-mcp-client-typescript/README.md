# Hugging Face MCP Client for TypeScript

This project is a TypeScript implementation of a Model Context Protocol (MCP) client that uses Hugging Face's hosted models via their Inference API.

## Features

- Uses the [Model Context Protocol](https://github.com/microsoftgraph/model-context-protocol) to communicate with MCP servers
- Integrates with Hugging Face's Inference API for LLM capabilities
- Includes tool call handling for interacting with MCP servers
- Compatible with the provided Weather Server example
- Supports multiple Hugging Face models with function calling capabilities

## Supported Models

This client supports the following models:

| Model | Size | Features | Memory Requirements |
|-------|------|----------|---------------------|
| Mistral 7B Instruct | 7B | Good instruction following | 8-16GB |
| Llama 2 7B Chat | 7B | Balanced performance | 8-16GB |
| OpenAssistant 12B | 12B | Strong function calling | 16-24GB |
| Phi-2 | 2.7B | Lightweight, good reasoning | 4-8GB |

## Prerequisites

- Node.js (v18+)
- Hugging Face account with API key
- TypeScript

## Installation

1. Clone the repository
2. Install dependencies:

```bash
npm install
```

3. Configure your `.env` file:

```
# Hugging Face settings
HUGGINGFACE_API_KEY=your_api_key_here
HUGGINGFACE_MODEL=meta-llama/Llama-2-7b-chat-hf
```

4. Build the project:

```bash
npm run build
```

## Running the Client

### Connecting to the Weather Server

```bash
npm start -- ../weather-server-typescript/build/index.js
# Or
npm start -- ../weather-server-python/weather.py
node build/index.js /path/to/weather-server.js
```

### Specifying a Different Model

```bash
npm start -- /path/to/weather-server.js --model mistralai/Mistral-7B-Instruct-v0.2
```

## Using Different Models

### Creating a Hugging Face Account & Getting API Key

1. Sign up for a Hugging Face account at https://huggingface.co/
2. Go to your profile > Settings > Access Tokens
3. Create a new token with "read" permissions
4. Copy the token to your `.env` file as HUGGINGFACE_API_KEY

### Model Selection Guide

- **Mistral 7B Instruct** - Good general purpose model with instruction following
- **Llama 2 7B Chat** - Meta's chat model with balanced performance
- **OpenAssistant 12B** - Larger model with improved tool calling capabilities
- **Phi-2** - Lightweight model with good reasoning, suitable for simpler tasks

## Troubleshooting

If you encounter issues:

1. Verify your API key is correct
2. Check if you have access to the model you're trying to use
3. Try running `npm run verify` to test the API connection
4. Try a different model with `npm run verify:model -- --model microsoft/phi-2`

## License

ISC
