import { LlamaModel, LlamaContext, LlamaChatPrompt } from 'node-llama-cpp';
import { ModelProvider } from '../model-provider.js';
import { Message, Tool } from '../types.js';
import dotenv from 'dotenv';
import path from 'path';

dotenv.config();

export class LlamaCppProvider implements ModelProvider {
  name = 'llama-cpp';
  private model: LlamaModel | null = null;
  private context: LlamaContext | null = null;
  private modelPath: string;
  
  constructor() {
    this.modelPath = process.env.LLAMA_MODEL_PATH || '';
    if (!this.modelPath) {
      throw new Error('LLAMA_MODEL_PATH environment variable is not set');
    }
  }

  async initialize(): Promise<void> {
    try {
      this.model = new LlamaModel({
        modelPath: this.modelPath,
        enableLogging: false,
      });
      
      this.context = new LlamaContext({
        model: this.model,
        contextSize: 4096,
        batchSize: 512,
        threads: 4,
      });
      
      console.log('Llama CPP initialized successfully');
    } catch (error) {
      console.error('Error initializing Llama CPP model:', error);
      throw new Error(`Failed to initialize Llama CPP model: ${error.message}`);
    }
  }

  private formatPrompt(messages: Message[], tools?: Tool[]): string {
    if (!tools || tools.length === 0) {
      // Regular chat prompt without tools
      return messages.map(msg => `${msg.role}: ${msg.content}`).join('\n');
    }
    
    // For tools, we need a special prompt format that asks the model to use tools
    // This is a simple implementation and might need refinement
    let prompt = messages.map(msg => `${msg.role}: ${msg.content}`).join('\n');
    
    // Add tool definitions
    prompt += '\n\nYou have access to the following tools:\n';
    for (const tool of tools) {
      prompt += `\n- ${tool.name}: ${tool.description}\n`;
      prompt += `  Parameters: ${JSON.stringify(tool.input_schema, null, 2)}\n`;
    }
    
    prompt += '\n\nTo use a tool, respond in the format:\n';
    prompt += 'assistant: I need to use a tool\n';
    prompt += 'TOOL_CALL: {"name": "tool_name", "arguments": {"param1": "value1", ...}}\n';
    
    return prompt;
  }

  private parseToolCalls(text: string): {
    content: string;
    toolCalls: {name: string; arguments: Record<string, unknown>}[];
  } {
    const toolCallRegex = /TOOL_CALL: (\{.*\})/g;
    const matches = [...text.matchAll(toolCallRegex)];
    
    const toolCalls: {name: string; arguments: Record<string, unknown>}[] = [];
    let content = text;
    
    for (const match of matches) {
      try {
        const toolCallJson = JSON.parse(match[1]);
        toolCalls.push({
          name: toolCallJson.name,
          arguments: toolCallJson.arguments,
        });
        
        // Remove the tool call from the content
        content = content.replace(match[0], '');
      } catch (error) {
        console.error('Failed to parse tool call:', error);
      }
    }
    
    // Clean up the content
    content = content.replace(/^assistant: /m, '').trim();
    
    return { content, toolCalls };
  }

  async generateResponse(query: string, tools: Tool[], context: Message[]): Promise<{
    content: string;
    toolCalls: {name: string; arguments: Record<string, unknown>}[];
  }> {
    if (!this.context) {
      throw new Error('Llama context is not initialized');
    }
    
    // Add the user query to the context
    const allMessages = [...context, { role: 'user', content: query }];
    
    // Format the prompt with or without tools
    const prompt = this.formatPrompt(allMessages, tools);
    
    try {
      // Generate the response
      const response = await this.context.prompt(prompt, {
        temperature: 0.7,
        maxTokens: 2048,
      });
      
      // Parse potential tool calls from the response
      return this.parseToolCalls(response);
    } catch (error) {
      console.error('Error generating response with Llama CPP:', error);
      return {
        content: 'I encountered an error while processing your request. Please try again.',
        toolCalls: [],
      };
    }
  }

  async generateFollowUp(context: Message[]): Promise<string> {
    if (!this.context) {
      throw new Error('Llama context is not initialized');
    }
    
    // Format the prompt without tools for the follow-up
    const prompt = this.formatPrompt(context);
    
    try {
      // Generate the response
      const response = await this.context.prompt(prompt, {
        temperature: 0.7,
        maxTokens: 2048,
      });
      
      // Clean up the response
      return response.replace(/^assistant: /m, '').trim();
    } catch (error) {
      console.error('Error generating follow-up with Llama CPP:', error);
      return 'I encountered an error while processing the tool results. Please try again.';
    }
  }
}
