# Open Model MCP Client for TypeScript

This project is a TypeScript implementation of a Model Context Protocol (MCP) client that uses lightweight open-source language models via Ollama instead of proprietary APIs like Anthropic Claude.

## Features

- Uses the [Model Context Protocol](https://github.com/microsoftgraph/model-context-protocol) to communicate with MCP servers
- Integrates with Ollama for local LLM inference
- Includes tool call handling for interacting with MCP servers
- Compatible with the provided Weather Server example
- Supports multiple lightweight models with function calling capabilities

## Supported Models

This client supports the following models:

| Model | Size | Features | Memory Requirements |
|-------|------|----------|---------------------|
| phi4-mini | 3.8B | Fast, good function calling | 4-8GB |
| dolphin3 | 8B | Excellent function calling | 8-12GB |
| phi4-mini-reasoning | 3.8B | Enhanced reasoning | 4-8GB |

For more details, see [model-comparison.md](./model-comparison.md).

## Prerequisites

- Node.js (v18+)
- Ollama installed and running locally (or accessible via network)
- TypeScript

## Installation

For detailed installation instructions and troubleshooting, see the [Installation Guide](./INSTALLATION.md).

Quick setup:

1. Clone the repository
2. Install dependencies:

```bash
npm install
```

3. Install the desired model via Ollama:

```bash
ollama pull phi4-mini  # Default recommended model
# or
ollama pull dolphin3
# or
ollama pull phi4-mini-reasoning
```

4. Configure your `.env` file:

```
# Ollama settings
OLLAMA_HOST=http://localhost:11434  # Change if using a remote Ollama instance
OLLAMA_MODEL=phi4-mini              # Choose your model here
```

5. Build the project:

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
npm start -- /path/to/weather-server.js --model ollama
```

## Supported Models

We've evaluated multiple open-source models for their function calling capabilities, which is essential for MCP integration. Here are our recommendations:

### Top Recommended Models

1. **Mistral Small 3.1** (24B) - Best balance of performance and resource usage
   - Excellent low-latency function calling
   - 128K token context length
   - Apache 2.0 license
   - Can run on consumer hardware (RTX 4090 or Mac with 32GB RAM)

2. **Phi 4 Mini** (3.8B) - Best for resource-constrained environments
   - Lightweight with function calling support
   - Good for systems with limited resources
   - Shorter context length (4K tokens)

3. **Llama 3.1** (8B/70B/405B) - Meta's powerful models
   - State-of-the-art tool use capabilities
   - 128K token context length
   - Flexible size options depending on available resources

4. **Qwen 3** (Multiple sizes from 0.6B to 235B)
   - Strong agent capabilities with external tool integration
   - 40K token context length
   - Supports 100+ languages

Make sure you've pulled your chosen model in Ollama before using it:

```bash
# Pull the recommended model
ollama pull mistral-small3.1

# Alternative lightweight option
ollama pull phi4-mini
```

## Example Usage

```
Query: What's the weather forecast for New York?

I need to get the weather forecast for New York. Let me check that for you.

[Used tool: get-forecast with args {"city":"New York","state":"NY"}]

Looking at the weather forecast for New York, NY:

Today: 76°F, Partly Sunny with a chance of showers and thunderstorms.
Tonight: 68°F, Mostly Cloudy with a chance of showers and thunderstorms.
Tomorrow: 82°F, Partly Sunny with a chance of showers and thunderstorms.

The wind will be from the Southwest at about 5-10 mph. Overall, it looks like somewhat unsettled weather with chances of rain and storms throughout the period, but temperatures will be warm and pleasant when the sun is out.
```

## Model Comparison for MCP Integration

| Model | Size | Tool Support | Context Length | Multilingual | Resource Requirements |
|-------|------|-------------|----------------|-------------|----------------------|
| **Mistral Small 3.1** | 24B | Excellent, low-latency | 128K | Yes | RTX 4090 or Mac with 32GB RAM |
| **Phi 4 Mini** | 3.8B | Good | 4K | Yes | Very low (2.5GB model size) |
| **Llama 3.1** | 8B, 70B, 405B | Excellent | 128K | Yes | Varies by size, medium to very high |
| **Qwen 3** | 0.6B to 235B | Excellent | 40K | 100+ languages | Varies by size, low to very high |
| **Llama 4** | 109B/400B MoE | Good, multimodal | 10M/1M | 12 languages | Very high |
| **Qwen 2.5** | 0.5B to 72B | Good | 32K-128K | 29+ languages | Varies by size |

## Project Structure

- `src/index.ts`: Main entry point for the MCP client
- `src/model-provider.ts`: Interface for model providers
- `src/model-factory.ts`: Factory for creating model providers
- `src/providers/`: Directory containing model provider implementations
  - `src/providers/ollama-provider.ts`: Implementation for Ollama API
  - `src/providers/llama-cpp-provider.ts`: Implementation for direct local model usage
- `src/types.ts`: TypeScript type definitions

## Why We Chose Mistral Small 3.1

After evaluating multiple open-source models, we selected Mistral Small 3.1 as our primary recommendation for the following reasons:

1. **Specialized for function calling**: It explicitly mentions "low-latency function calling" which is exactly what MCP requires
2. **Performance**: Outperforms many other models in its class, including Gemma 3 and GPT-4o Mini
3. **Resource balance**: Provides excellent capabilities while still being runnable on high-end consumer hardware
4. **Open license**: Apache 2.0 license makes it suitable for commercial applications
5. **Long context**: 128K token context allows for complex multi-turn conversations
6. **Stability**: While relatively new, it builds on the solid foundation of Mistral's previous models

We also recommend Phi 4 Mini as an excellent alternative for resource-constrained environments, as it's significantly smaller while still supporting function calling capabilities.

## Development

To add support for additional models, create a new provider class in the `src/providers/` directory that implements the `ModelProvider` interface, then update the `ModelFactory` to include your new provider.

## License

ISC License

## Verifying Model Function Calling

This project includes a model verification tool to test if each model properly supports function calling with the MCP protocol. This helps you choose the best model for your needs.

To test all configured models:

```bash
npm run verify
```

To test a specific model:

```bash
npm run verify:model phi4-mini
# or 
npm run verify:model dolphin3
# or any other Ollama model ID
```

The verification tool will:

1. Check if each model is available in your Ollama installation
2. Pull models that aren't yet installed
3. Test function calling with realistic weather-related queries
4. Report which models support function calling
5. Recommend the best model based on response time and success rate

Example output:

```
📊 Summary Results:
Phi-4-mini (phi4-mini): Function calling ✅, Response time: 1254ms
Dolphin 3 (dolphin3): Function calling ✅, Response time: 2145ms
Phi-4-mini-reasoning (phi4-mini-reasoning): Function calling ✅, Response time: 1321ms

💡 Recommended model: Phi-4-mini (phi4-mini)
To use this model, set OLLAMA_MODEL=phi4-mini in your .env file
```
