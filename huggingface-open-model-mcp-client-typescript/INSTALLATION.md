# Installing and Using Open-Source Models with MCP Client

This guide will help you get started with the Open Model MCP Client for TypeScript, which uses lightweight open-source models for function calling.

## Step 1: Install Ollama

First, you'll need to install Ollama, which is a tool that makes it easy to run open-source large language models locally.

1. Go to [Ollama's website](https://ollama.com/download) and download the installer for your operating system.
2. Install Ollama following the instructions for your platform.
3. Start the Ollama service.

## Step 2: Pull the Required Models

After installing Ollama, you need to pull (download) one of the recommended models:

**Option 1: phi4-mini (recommended for most users)**
```bash
ollama pull phi4-mini
```

**Option 2: dolphin3 (better function calling, higher memory usage)**
```bash
ollama pull dolphin3
```

**Option 3: phi4-mini-reasoning (better reasoning capabilities)**
```bash
ollama pull phi4-mini-reasoning
```

Pulling a model may take a few minutes depending on your internet connection speed.

## Step 3: Configure the Client

### Automatic Setup (Recommended)

We provide a setup utility that tests model function calling and configures your environment automatically:

```bash
npm run setup
```

This utility will:
1. Check if Ollama is running
2. Test all recommended models for function calling capability
3. Pull models that aren't installed yet
4. Configure your .env file with the best-performing model

### Manual Setup

If you prefer to configure manually, make sure your `.env` file is set up correctly:
```
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=phi4-mini  # Or another model you pulled
MODEL_TEMPERATURE=0.7
MODEL_TOP_P=0.9
```

You can adjust the temperature and top_p values as needed to control the model's creativity and focus.

## Step 4: Run the Client

1. Build the project:
```bash
npm run build
```

2. Connect to the weather server:
```bash
# TypeScript weather server
npm start -- ../weather-server-typescript/build/index.js

# OR Python weather server
npm start -- ../weather-server-python/weather.py
```

3. Once connected, you can ask weather-related questions, and the client will use function calling to retrieve the information.

## System Requirements

Different models have different memory requirements:

| Model | Minimum RAM | Recommended RAM |
|-------|-------------|-----------------|
| phi4-mini | 4GB | 8GB |
| dolphin3 | 8GB | 12GB |
| phi4-mini-reasoning | 4GB | 8GB |

## Troubleshooting

**Model is loading slowly:** The first time you use a model, Ollama needs to download and prepare it. Subsequent uses will be faster.

**Out of memory errors:** Try using a smaller model like phi4-mini, or close other applications to free up system memory.

**Function calling not working:** Make sure you're using a model that supports function calling (all three recommended models do). You can verify your model's function calling capability by running:
```bash
npm run verify
# or for a specific model
npm run verify:model dolphin3
```

**Connection refused errors:** Ensure Ollama is running by opening a terminal and running `ollama list` to see available models.

## Testing Model Function Calling

If you want to test the function calling capabilities of a specific model or all models:

```bash
# Test all recommended models
npm run verify

# Test a specific model
npm run verify:model phi4-mini
```

The verification process will:
1. Check if each model is installed
2. Pull models that aren't available locally
3. Test the model with example weather queries
4. Report which models support function calling
5. Recommend the best model based on performance

This is useful to determine which model works best in your environment.
