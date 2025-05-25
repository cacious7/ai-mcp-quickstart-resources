#!/usr/bin/env node
import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';
import readline from 'readline/promises';
import { ModelFactory } from './model-factory.js';
import { Tool, Message } from './types.js';
import dotenv from 'dotenv';

dotenv.config();

class MCPClient {
  private mcp: Client;
  private provider: any;
  private transport: StdioClientTransport | null = null;
  private tools: Tool[] = [];
  private conversationHistory: Message[] = [];

  constructor() {
    // Initialize MCP client
    this.mcp = new Client({ name: 'huggingface-mcp-client', version: '1.0.0' });
    
    // Create model provider
    this.provider = ModelFactory.createProvider();
  }

  async connectToServer(serverScriptPath: string) {
    /**
     * Connect to an MCP server
     *
     * @param serverScriptPath - Path to the server script (.py or .js)
     */
    try {
      // Determine script type and appropriate command
      const isJs = serverScriptPath.endsWith('.js');
      const isPy = serverScriptPath.endsWith('.py');
      if (!isJs && !isPy) {
        throw new Error('Server script must be a .js or .py file');
      }

      const command = isPy
        ? process.platform === 'win32'
          ? 'python'
          : 'python3'
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
        'Connected to server with tools:',
        this.tools.map(({ name }) => name),
      );
    } catch (e) {
      console.log('Failed to connect to MCP server: ', e);
      throw e;
    }
  }

  async processQuery(query: string): Promise<string> {
    /**
     * Process a query using model and available tools
     *
     * @param query - The user's input query
     * @returns Processed response as a string
     */
    try {
      // Initialize provider if needed
      await this.provider.initialize();
      
      // Add user message to history
      this.conversationHistory.push({
        role: 'user',
        content: query,
      });
      
      // Generate response with tool access
      console.log('Sending query to LLM...');
      const response = await this.provider.generateResponse(
        query,
        this.tools,
        this.conversationHistory
      );

      // Process response and handle tool calls
      const finalText = [];
      const toolResults = [];

      // Add assistant's response to history
      this.conversationHistory.push({
        role: 'assistant',
        content: response.content,
      });
      
      finalText.push(response.content);

      // Handle any tool calls
      if (response.toolCalls && response.toolCalls.length > 0) {
        for (const toolCall of response.toolCalls) {
          try {
            const toolName = toolCall.name;
            const toolArgs = toolCall.arguments;

            console.log(`Calling tool ${toolName}...`);
            finalText.push(
              `[Calling tool ${toolName} with args ${JSON.stringify(toolArgs)}]`,
            );

            const result = await this.mcp.callTool({
              name: toolName,
              arguments: toolArgs,
            });
            
            toolResults.push(result);

            // Add tool result to history
            if (result && result.content) {
              this.conversationHistory.push({
                role: 'tool',
                name: toolName,
                content: typeof result.content === 'string' 
                  ? result.content 
                  : JSON.stringify(result.content),
              });

              // Generate follow-up response
              console.log('Getting follow-up response...');
              const followUpResponse = await this.provider.generateFollowUp(
                this.conversationHistory
              );

              // Add follow-up to history
              this.conversationHistory.push({
                role: 'assistant',
                content: followUpResponse,
              });

              finalText.push(followUpResponse);
            } else {
              finalText.push('Warning: Tool returned an invalid result.');
            }
          } catch (toolError: any) {
            console.error('Error during tool execution:', toolError);
            finalText.push(`Error calling tool: ${toolError.message}`);
          }
        }
      }

      return finalText.join('\n');
    } catch (error: any) {
      console.error('Error in processQuery:', error);
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
    });

    try {
      console.log('\nMCP Client Started!');
      console.log('Type your queries or \'quit\' to exit.');

      while (true) {
        const message = await rl.question('\nQuery: ');
        if (message.toLowerCase() === 'quit') {
          break;
        }
        const response = await this.processQuery(message);
        console.log('\n' + response);
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
  if (process.argv.length < 3) {
    console.log('Usage: node build/index.js <path_to_server_script> [--model <model_id>]');
    return;
  }

  // Check for --model flag
  const modelFlagIndex = process.argv.indexOf('--model');
  if (modelFlagIndex !== -1 && modelFlagIndex + 1 < process.argv.length) {
    process.env.HUGGINGFACE_MODEL = process.argv[modelFlagIndex + 1];
    console.log(`Using model: ${process.argv[modelFlagIndex + 1]}`);
  }
  
  const mcpClient = new MCPClient();
  try {
    console.log(`Connecting to server script: ${process.argv[2]}`);
    await mcpClient.connectToServer(process.argv[2]);
    await mcpClient.chatLoop();
  } catch (error) {
    console.error('Error in main:', error);
    console.log('The application encountered an error. Please check the server script path and try again.');
  } finally {
    console.log('Cleaning up resources...');
    try {
      await mcpClient.cleanup();
    } catch (cleanupError) {
      console.error('Error during cleanup:', cleanupError);
    }
    console.log('Exiting application.');
    process.exit(0);
  }
}

main();
