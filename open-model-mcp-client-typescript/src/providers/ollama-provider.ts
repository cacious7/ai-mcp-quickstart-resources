import Ollama from 'ollama';
import { Message, Tool } from '../types.js';
import dotenv from 'dotenv';

dotenv.config();

export class OllamaProvider {
  name = 'Ollama';
  private client: any;
  private model: string;
  private host: string;
  private temperature: number;
  private top_p: number;
  
  constructor() {
    this.model = process.env.OLLAMA_MODEL || 'phi4-mini';
    this.host = process.env.OLLAMA_HOST || 'http://localhost:11434';
    this.temperature = parseFloat(process.env.MODEL_TEMPERATURE || '0.7');
    this.top_p = parseFloat(process.env.MODEL_TOP_P || '0.9');
    this.client = Ollama;
  }  async initialize(): Promise<void> {
    try {
      // Check if Ollama service is running
      console.log("Checking if Ollama service is running...");
      
      try {
        // Just verify that the Ollama service is accessible
        const modelsList = await this.client.list({ host: this.host });
        console.log(`✅ Ollama service is running`);
        
        // Log available models but don't pull anything
        const availableModels = modelsList.models.map((m: any) => m.name).join(', ');
        console.log(`Available models: ${availableModels}`);
        
        // Check if our model is available
        const isModelAvailable = modelsList.models.some((m: any) => m.name === this.model);
        if (!isModelAvailable) {
          console.log(`⚠️ Warning: Model '${this.model}' not found locally.`);
          console.log(`Please run 'ollama pull ${this.model}' in a terminal before using this model.`);
        } else {
          console.log(`✅ Model '${this.model}' is available locally.`);
        }
      } catch (error) {
        console.error('❌ Failed to connect to Ollama service');
        console.error('Make sure Ollama is running at:', this.host);
        throw new Error('Failed to connect to Ollama service. Is Ollama running?');
      }
      
      console.log(`Ollama initialized with model: ${this.model} (temperature: ${this.temperature}, top_p: ${this.top_p})`);
    } catch (error: any) {
      console.error('Error initializing Ollama client:', error);
      throw new Error(`Failed to initialize Ollama: ${error.message || error}`);
    }
  }

  private formatToolsForOllama(tools: Tool[]): any[] {
    return tools.map(tool => ({
      name: tool.name,
      description: tool.description,
      parameters: tool.input_schema,
    }));
  }  async generateResponse(query: string, tools: Tool[], context: Message[]): Promise<{
    content: string;
    toolCalls: {
      name: string;
      arguments: Record<string, unknown>;
    }[];
  }> {
    const formattedTools = this.formatToolsForOllama(tools);
    
    // Add explicit instructions to use tools when appropriate
    let systemMessage = context.find(msg => msg.role === 'system');
    if (systemMessage) {
      // Enhance the system message with tool usage instructions
      if (!systemMessage.content.includes('When you need to get weather information')) {
        systemMessage.content += '\nWhen you need to get weather information, you MUST use the available weather tool instead of making up information. Analyze the user query to determine if weather information is requested.';
      }
    }
    
    // Convert context to Ollama format
    const messages = [...context];
    if (query) {
      messages.push({ role: 'user', content: query });
    }
    
    try {
      // Configure the request based on the model
      const requestConfig = {
        host: this.host,
        model: this.model,
        messages,
        stream: false,
        options: {
          temperature: this.temperature,
          top_p: this.top_p,
        }
      };
      
      // Add tools if available
      if (tools.length > 0) {
        Object.assign(requestConfig, {
          tools: formattedTools,
          tool_choice: 'auto'
        });
      }
      
      // Make the API call
      console.log(`Sending request to ${this.model}...`);
      const response = await this.client.chat(requestConfig);

      // Debug the raw response if needed
      // console.log('Raw response:', JSON.stringify(response.message, null, 2));

      const toolCalls: {name: string; arguments: Record<string, unknown>}[] = [];
      
      // Extract tool calls if present
      if (response.message.tool_calls && response.message.tool_calls.length > 0) {
        console.log(`Model returned ${response.message.tool_calls.length} tool calls`);
        
        for (const toolCall of response.message.tool_calls) {
          console.log(`Processing tool call for: ${toolCall.name}`);
            try {
            // Handle different formats of tool arguments
            let toolArguments = {};
            if (typeof toolCall.arguments === 'string') {
              try {
                toolArguments = JSON.parse(toolCall.arguments);
              } catch (e) {
                console.error('Error parsing tool arguments JSON:', e);
                // Try to extract key-value pairs from malformed JSON
                toolArguments = this.extractArgumentsFromString(toolCall.arguments);
              }
            } else {
              toolArguments = toolCall.arguments || {};
            }
            
            toolCalls.push({
              name: toolCall.name,
              arguments: toolArguments
            });          } catch (parseError: any) {
            console.error(`Error processing tool call arguments: ${parseError.message || parseError}`);
          }
        }
      } else {
        console.log('Model did not return any tool calls');
      }

      return {
        content: response.message.content || '',
        toolCalls,
      };
    } catch (error) {
      console.error('Error generating response from Ollama:', error);
      return {
        content: `I encountered an error while processing your request with the ${this.model} model. Please try again or try a different model.`,
        toolCalls: [],
      };
    }
  }
  
  // Helper method to extract arguments from a string when JSON parsing fails
  private extractArgumentsFromString(argsString: string): Record<string, unknown> {
    const result: Record<string, unknown> = {};
    
    // Look for patterns like "key": "value" or "key": value
    const regex = /"([^"]+)":\s*(?:"([^"]+)"|(\S+))/g;
    let match;
    
    while ((match = regex.exec(argsString)) !== null) {
      const key = match[1];
      // Use the quoted value if available, otherwise use the unquoted value
      const value = match[2] !== undefined ? match[2] : match[3];
      result[key] = value;
    }
    
    return result;
  }  async generateFollowUp(context: Message[]): Promise<string> {
    try {
      // Find the most recent tool response for better context
      const toolResponses = context.filter(msg => msg.role === 'tool');
      
      // Check if we have recent tool responses to guide the model
      if (toolResponses.length > 0) {
        const lastToolMsg = toolResponses[toolResponses.length - 1];
        const lastUserMsg = [...context].reverse().find(msg => msg.role === 'user');
        
        // Add a hint for the model to interpret the tool response correctly
        context.push({
          role: 'system',
          content: 'You have received data from a tool. Interpret this data in natural language to answer the user query. Focus on providing a concise and helpful response.'
        });
      }
      
      // Make the API call with improved context
      const response = await this.client.chat({
        host: this.host,
        model: this.model,
        messages: context,
        stream: false,
        options: {
          temperature: this.temperature,
          top_p: this.top_p
        }
      });

      return response.message.content || '';
    } catch (error) {
      console.error('Error generating follow-up response from Ollama:', error);
      return 'I encountered an error while processing the tool results. Please try again.';
    }
  }
}
