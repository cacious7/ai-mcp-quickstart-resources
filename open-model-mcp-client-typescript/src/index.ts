import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import readline from "readline/promises";

import dotenv from "dotenv";
import { ModelFactory } from "./model-factory.js";
import { Message, Tool, ToolCall } from "./types.js";

dotenv.config(); // load environment variables from .env

class MCPClient {
  private mcp: Client;
  private transport: StdioClientTransport | null = null;
  private tools: Tool[] = [];
  private modelProvider: any;
  private conversationHistory: Message[] = [];
  constructor() {
    // Initialize MCP client and Ollama model provider with Mistral Small 3.1
    this.mcp = new Client({ name: "open-mcp-client-cli", version: "1.0.0" });
    this.modelProvider = ModelFactory.createProvider();
    
    // Add a system message to the conversation history
    this.conversationHistory.push({
      role: 'system',
      content: 'You are a helpful assistant that can answer questions about the weather using tools.'
    });
  }
  async initialize() {
    try {
      console.log(`\n🚀 Initializing ${this.modelProvider.name} model provider...`);
      console.log(`💡 Using model: ${process.env.OLLAMA_MODEL || 'default'}`);
      await this.modelProvider.initialize();
      console.log(`✅ Model provider initialized successfully\n`);
    } catch (error) {
      console.error(`❌ Failed to initialize model provider: ${error.message}`);
      throw error;
    }
  }

  async connectToServer(serverScriptPath: string) {
    /**
     * Connect to an MCP server
     *
     * @param serverScriptPath - Path to the server script (.py or .js)
     */
    try {
      // Determine script type and appropriate command
      const isJs = serverScriptPath.endsWith(".js");
      const isPy = serverScriptPath.endsWith(".py");
      if (!isJs && !isPy) {
        throw new Error("Server script must be a .js or .py file");
      }
      const command = isPy
        ? process.platform === "win32"
          ? "python"
          : "python3"
        : process.execPath;

      // Initialize transport and connect to server
      this.transport = new StdioClientTransport({
        command,
        args: [serverScriptPath],
      });
      this.mcp.connect(this.transport);

      // List available tools
      const toolsResult = await this.mcp.listTools();
      this.tools = toolsResult.tools.map((tool) => {
        return {
          name: tool.name,
          description: tool.description,
          input_schema: tool.inputSchema,
        };
      });
      console.log(
        "Connected to server with tools:",
        this.tools.map(({ name }) => name),
      );
    } catch (e) {
      console.log("Failed to connect to MCP server: ", e);
      throw e;
    }
  }

  async processQuery(query: string) {
    /**
     * Process a query using the model provider and available tools
     *
     * @param query - The user's input query
     * @returns Processed response as a string
     */
    try {
      // Add query to conversation history
      this.conversationHistory.push({
        role: 'user',
        content: query,
      });

      // Get response from model with tool options
      console.log("Sending query to model...");
      
      const response = await this.modelProvider.generateResponse(
        query, 
        this.tools,
        this.conversationHistory
      );

      // Process response and handle tool calls
      const finalText = [];
      
      // Add the initial response to conversation history
      this.conversationHistory.push({
        role: 'assistant',
        content: response.content,
      });
      
      if (response.content) {
        finalText.push(response.content);
      }

      // Handle any tool calls
      if (response.toolCalls && response.toolCalls.length > 0) {
        for (const toolCall of response.toolCalls) {
          try {
            // Execute tool call
            const toolName = toolCall.name;
            const toolArgs = toolCall.arguments;

            console.log(`Calling tool ${toolName}...`);
            const result = await this.mcp.callTool({
              name: toolName,
              arguments: toolArgs,
            });
            
            finalText.push(
              `[Used tool: ${toolName} with args ${JSON.stringify(toolArgs)}]`
            );

            // Add tool response to conversation history
            this.conversationHistory.push({
              role: 'tool',
              name: toolName,
              content: JSON.stringify(result),
            });

            // Continue conversation with tool results
            if (result && (result.content || result.outputs)) {
              let toolContent = '';
              if (typeof result.content === 'string') {
                toolContent = result.content;
              } else if (result.content && Array.isArray(result.content)) {
                // Handle array of content objects (text, etc.)
                toolContent = result.content
                  .filter(item => item.type === 'text' && item.text)
                  .map(item => item.text)
                  .join('\n');
              } else if (result.outputs) {
                toolContent = JSON.stringify(result.outputs);
              }

              // Get follow-up response from model
              console.log("Getting follow-up response from model...");
              const followUpResponse = await this.modelProvider.generateFollowUp(this.conversationHistory);
              
              // Add the follow-up to conversation history
              this.conversationHistory.push({
                role: 'assistant',
                content: followUpResponse,
              });

              finalText.push(followUpResponse);
            }
          } catch (toolError) {
            console.error("Error during tool execution:", toolError);
            finalText.push(`Error calling tool: ${toolError.message}`);
          }
        }
      }

      return finalText.join("\n");
    } catch (error) {
      console.error("Error in processQuery:", error);
      return `Error processing query: ${error.message}. Please try again.`;
    }
  }
  async chatLoop() {
    /**
     * Run an interactive chat loop
     */
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout,
    });    try {
      console.log("\nOpen MCP Client Started!");
      console.log(`Using ${this.modelProvider.name}`);      console.log("\n📝 Type your queries or 'quit' to exit.");
      console.log("🌦️  Try asking about the weather, like: \"What's the weather like in New York?\"");
      console.log("🔍 This will demonstrate function calling with the open-source model.");

      while (true) {
        const message = await rl.question("\nQuery: ");
        if (message.toLowerCase() === "quit") {
          break;
        }
        console.log("\n⏳ Processing your query...");
        const response = await this.processQuery(message);
        console.log("\n" + response);
      }
    } finally {
      rl.close();
    }
  }

  async cleanup() {
    /**
     * Clean up resources
     */
    await this.mcp.close();
  }
}

async function main() {
  // Parse command line arguments
  const args = process.argv.slice(2);
  let serverPath = '';

  // Process arguments - only look for server path now
  for (let i = 0; i < args.length; i++) {
    if (!serverPath) {
      serverPath = args[i];
    }
  }

  // Ensure we have a server path
  if (!serverPath) {
    console.log("Usage: node build/index.js <path_to_server_script>");
    return;
  }

  const mcpClient = new MCPClient();
  
  try {
    await mcpClient.initialize();
    console.log(`Connecting to server script: ${serverPath}`);
    await mcpClient.connectToServer(serverPath);
    await mcpClient.chatLoop();
  } catch (error) {
    console.error("Error in main:", error);
    console.log("The application encountered an error. Please check the server script path and try again.");
  } finally {
    console.log("Cleaning up resources...");
    try {
      await mcpClient.cleanup();
    } catch (cleanupError) {
      console.error("Error during cleanup:", cleanupError);
    }
    console.log("Exiting application.");
    process.exit(0);
  }
}

main();
