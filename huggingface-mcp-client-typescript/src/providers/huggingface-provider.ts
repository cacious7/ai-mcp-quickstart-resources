import { HfInference } from '@huggingface/inference';
import { Message, Tool } from '../types.js';
import dotenv from 'dotenv';
import { ModelProvider } from '../model-provider.js';

dotenv.config();

export class HuggingFaceProvider implements ModelProvider {
  name = 'HuggingFace';
  private client: HfInference;
  private model: string;
  private apiUrl: string;
  private temperature: number;
  private top_p: number;
  private maxTokens: number;
  
  constructor() {
    this.model = process.env.HUGGINGFACE_MODEL || 'meta-llama/Llama-2-7b-chat-hf';
    this.apiUrl = process.env.HUGGINGFACE_API_URL || 'https://api-inference.huggingface.co/models';
    this.temperature = parseFloat(process.env.MODEL_TEMPERATURE || '0.7');
    this.top_p = parseFloat(process.env.MODEL_TOP_P || '0.9');
    this.maxTokens = parseInt(process.env.MODEL_MAX_TOKENS || '1000');
    
    const apiKey = process.env.HUGGINGFACE_API_KEY;
    if (!apiKey) {
      throw new Error('HUGGINGFACE_API_KEY is not set in the .env file');
    }
    
    this.client = new HfInference(apiKey);
  }

  async initialize(): Promise<void> {
    try {
      console.log("Initializing Hugging Face provider...");
      console.log(`Using model: ${this.model}`);
      console.log(`API URL: ${this.apiUrl}`);
      console.log(`Parameters: temperature=${this.temperature}, top_p=${this.top_p}, max_tokens=${this.maxTokens}`);
      
      // Test the API connection
      // We'll just ping the model info endpoint to ensure we can connect
      try {
        // A simple ping to verify credentials and connectivity
        await this.client.httpClient.get(`${this.apiUrl.replace('/models', '')}/status`);
        console.log("✅ Successfully connected to Hugging Face API");
      } catch (error: any) {
        console.error('❌ Failed to connect to Hugging Face API');
        if (error.response?.status === 401) {
          console.error('Invalid API key. Please check your HUGGINGFACE_API_KEY in the .env file.');
        } else {
          console.error(`Error: ${error.message || 'Unknown error'}`);
        }
        throw new Error('Failed to connect to Hugging Face API');
      }
      
    } catch (error: any) {
      console.error('Error initializing Hugging Face client:', error);
      throw error;
    }
  }

  // Helper method to format messages for the model
  private formatMessages(messages: Message[]): string {
    let prompt = '';
    
    for (const message of messages) {
      switch (message.role) {
        case 'system':
          prompt += `<|system|>\n${message.content}\n`;
          break;
        case 'user':
          prompt += `<|user|>\n${message.content}\n`;
          break;
        case 'assistant':
          prompt += `<|assistant|>\n${message.content}\n`;
          break;
        case 'tool':
          prompt += `<|tool|>\n${message.name}: ${message.content}\n`;
          break;
        default:
          prompt += `${message.content}\n`;
      }
    }
    
    // Add the final assistant marker for the model to continue from
    prompt += `<|assistant|>\n`;
    
    return prompt;
  }

  // Helper method to format available tools as part of the system prompt
  private formatToolsForPrompt(tools: Tool[]): string {
    if (!tools || tools.length === 0) {
      return '';
    }
    
    let toolsPrompt = 'You have access to the following tools:\n\n';
    
    for (const tool of tools) {
      toolsPrompt += `Tool: ${tool.name}\n`;
      toolsPrompt += `Description: ${tool.description}\n`;
      toolsPrompt += `Parameters: ${JSON.stringify(tool.input_schema, null, 2)}\n\n`;
    }
    
    toolsPrompt += `When you need to use a tool, respond with:
\`\`\`json
{
  "tool_calls": [
    {
      "name": "tool_name",
      "arguments": {
        "param1": "value1",
        "param2": "value2"
      }
    }
  ]
}
\`\`\`

After receiving tool results, provide a helpful response based on the information.
`;
    
    return toolsPrompt;
  }

  // Parse the model output for tool calls
  private parseToolCalls(text: string): { content: string, toolCalls: { name: string, arguments: Record<string, unknown> }[] } {
    const toolCallRegex = /```json\s*({[\s\S]*?})\s*```/g;
    const toolCalls: { name: string, arguments: Record<string, unknown> }[] = [];
    let content = text;
    
    let match;
    while ((match = toolCallRegex.exec(text)) !== null) {
      try {
        const jsonStr = match[1];
        const jsonData = JSON.parse(jsonStr);
        
        if (jsonData.tool_calls && Array.isArray(jsonData.tool_calls)) {
          for (const call of jsonData.tool_calls) {
            if (call.name && call.arguments) {
              toolCalls.push({
                name: call.name,
                arguments: call.arguments
              });
            }
          }
        }
        
        // Remove the tool call JSON from the content
        content = content.replace(match[0], '');
      } catch (error) {
        console.error('Error parsing tool call JSON:', error);
      }
    }
    
    // Clean up the content
    content = content.trim();
    
    return { content, toolCalls };
  }

  async generateResponse(query: string, tools: Tool[], context: any[] = []): Promise<{
    content: string;
    toolCalls: { name: string; arguments: Record<string, unknown> }[];
  }> {
    try {
      // Format context as messages
      const messages: Message[] = Array.isArray(context) ? context : [];
      
      // Add system message with tool descriptions if there are tools
      if (tools && tools.length > 0) {
        messages.unshift({
          role: 'system',
          content: `You are a helpful assistant that can use tools to answer questions. ${this.formatToolsForPrompt(tools)}`
        });
      } else {
        messages.unshift({
          role: 'system',
          content: 'You are a helpful assistant.'
        });
      }
      
      // Add user query
      messages.push({
        role: 'user',
        content: query
      });
      
      // Format messages for the model
      const prompt = this.formatMessages(messages);
      
      console.log('Sending request to Hugging Face API...');
      
      // Make API request to Hugging Face
      const response = await this.client.textGeneration({
        model: this.model,
        inputs: prompt,
        parameters: {
          temperature: this.temperature,
          top_p: this.top_p,
          max_new_tokens: this.maxTokens,
          return_full_text: false
        }
      });
      
      const text = response.generated_text || '';
      console.log('Response received from Hugging Face API');
      
      // Parse tool calls and content
      const { content, toolCalls } = this.parseToolCalls(text);
      
      return { content, toolCalls };
    } catch (error) {
      console.error('Error generating response:', error);
      throw error;
    }
  }

  async generateFollowUp(context: any[] = []): Promise<string> {
    try {
      // Format context as messages
      const messages: Message[] = Array.isArray(context) ? context : [];
      
      // Add system message
      messages.unshift({
        role: 'system',
        content: 'You are a helpful assistant. Based on the tool results, provide a helpful response.'
      });
      
      // Format messages for the model
      const prompt = this.formatMessages(messages);
      
      console.log('Sending follow-up request to Hugging Face API...');
      
      // Make API request to Hugging Face
      const response = await this.client.textGeneration({
        model: this.model,
        inputs: prompt,
        parameters: {
          temperature: this.temperature,
          top_p: this.top_p,
          max_new_tokens: this.maxTokens,
          return_full_text: false
        }
      });
      
      const text = response.generated_text || '';
      console.log('Follow-up response received from Hugging Face API');
      
      return text;
    } catch (error) {
      console.error('Error generating follow-up response:', error);
      throw error;
    }
  }
}
