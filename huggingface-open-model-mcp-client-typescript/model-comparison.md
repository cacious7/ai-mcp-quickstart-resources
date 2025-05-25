# Open-Source LLM Comparison for Function Calling

This document compares lightweight open-source models that can be used with our MCP client, focusing on function calling capabilities, response time, and memory requirements.

## Selected Models for Implementation

After research, we've selected these three models for our MCP client:

| Model | Size | Function Calling | Response Time | Memory Requirements | Notes |
|-------|------|-----------------|---------------|---------------------|-------|
| Phi-4-mini | 3.8B | Yes | Fast | Low (4-8GB) | Lightweight model with function calling added in recent version |
| Dolphin3 | 8B | Yes | Medium | Medium (8-12GB) | Based on Llama 3.1 8B, specifically designed for function calling |
| Phi4-mini-reasoning | 3.8B | Good | Fast | Low (4-8GB) | Improved reasoning capabilities over standard Phi4-mini |

These models were selected because they:
1. Are lightweight enough to run on consumer hardware
2. Support function calling capabilities required by our MCP client
3. Provide a good balance of performance and resource usage

## Model Details

### Phi-4-mini
- **Size**: 3.8B parameters
- **Function Calling Quality**: Good function calling support
- **Pros**: Very low memory footprint, fast inference, well-suited for edge devices
- **Cons**: Smaller model size may affect complex reasoning
- **Installation**: `ollama pull phi4-mini`

### Dolphin3
- **Size**: 8B parameters
- **Function Calling Quality**: Specifically designed for function calling
- **Pros**: Good balance of size vs capability, optimized for tool use
- **Cons**: Requires more memory than Phi models
- **Installation**: `ollama pull dolphin3`

### Phi4-mini-reasoning
- **Size**: 3.8B parameters
- **Function Calling Quality**: Good with enhanced reasoning capabilities
- **Pros**: Improved reasoning over standard Phi4-mini while maintaining small size
- **Cons**: Newer model with less community testing
- **Installation**: `ollama pull phi4-mini-reasoning`

## Usage Instructions

1. Install the desired model using Ollama:
   ```
   ollama pull [model-name]
   ```

2. Update the `.env` file to select the model:
   ```
   OLLAMA_MODEL=[model-name]
   ```

3. Run the MCP client:
   ```
   npm start
   ```

The client will automatically use the model specified in the `.env` file.
