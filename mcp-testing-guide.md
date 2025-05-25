# MCP Client Testing Guide with Memory Optimizations

Due to memory constraints with language models, here are the steps to properly test the MCP client with the weather server:

## Setup Steps

1. **Check available Ollama models**:
   ```
   C:\Users\csiam\AppData\Local\Programs\Ollama\ollama.exe list
   ```

2. **Pull a small model** if you don't have one:
   ```
   C:\Users\csiam\AppData\Local\Programs\Ollama\ollama.exe pull tinyllama
   ```
   TinyLlama is only 1.1B parameters and should work even with minimal memory.

3. **Update the `.env` file** in the `open-model-mcp-client-typescript` directory:
   ```
   # Using the smallest model to avoid memory issues
   OLLAMA_MODEL=tinyllama
   
   # Force CPU mode with minimal memory usage
   OLLAMA_GPU_LAYERS=0
   OLLAMA_NUM_GPU=0
   OLLAMA_KEEP_ALIVE=0
   ```

4. **Build the MCP client**:
   ```
   cd "C:\Users\csiam\Documents\Local AI Interests\ai-mcp-quickstart-resources\open-model-mcp-client-typescript"
   npm run build
   ```

5. **Run the MCP client**:
   ```
   cd "C:\Users\csiam\Documents\Local AI Interests\ai-mcp-quickstart-resources\open-model-mcp-client-typescript"
   $env:OLLAMA_GPU_LAYERS=0
   $env:OLLAMA_NUM_GPU=0
   $env:OLLAMA_KEEP_ALIVE=0
   node build/index.js "../weather-server-typescript/build/index.js"
   ```

6. **Test Weather Queries**:
   Once the client is running, try these queries:
   - "What's the weather like in Tokyo?"
   - "Is it raining in New York?" 

## Important Notes

- Even a smaller model like TinyLlama may have limited function calling capabilities compared to Mistral Small 3.1
- If memory issues persist, you may need to close other applications or restart your computer before testing
- The optimal setup is to use Mistral Small 3.1 on a system with at least 24GB RAM

## Rollback to Mistral When Possible

When you have access to a system with sufficient memory (24+ GB), update the `.env` file to use:
```
OLLAMA_MODEL=mistral-small3.1
```

This will give you the best function calling capabilities for the MCP client.
