/**
 * Mock Provider for testing MCP without a real LLM
 * This provider simulates function calling for weather queries
 */

import { Message, Tool } from '../types.js';

export class MockProvider {
  name = 'Mock Provider';
  private modelName: string;
  
  constructor(modelName = 'mock-model') {
    this.modelName = modelName;
    console.log('⚠️ Using Mock Provider for testing (no real LLM)');
  }
  
  async initialize(): Promise<void> {
    console.log('✅ Mock Provider initialized');
    return Promise.resolve();
  }

  async generateResponse(query: string, tools: Tool[], context: Message[]): Promise<{
    content: string;
    toolCalls: {
      name: string;
      arguments: Record<string, unknown>;
    }[];
  }> {
    console.log(`📋 User query: "${query}"`);
    console.log(`🛠️ Available tools: ${tools.map(t => t.name).join(', ')}`);
    
    // Check if query is weather-related
    const isWeatherQuery = /weather|temperature|forecast|rain|sunny|hot|cold|climate|humid/i.test(query);
    
    // Find the weather tool if available
    const weatherTool = tools.find(tool => 
      tool.name.includes('get_weather') || 
      tool.name.includes('weather') || 
      tool.description.toLowerCase().includes('weather')
    );
    
    if (isWeatherQuery && weatherTool) {
      // Extract location using simple pattern matching
      let location = 'New York';
      const locationMatch = query.match(/(?:in|at|for)\s+([A-Za-z\s]+?)(?:\?|$|\s+)/i);
      if (locationMatch && locationMatch[1]) {
        location = locationMatch[1].trim();
      }
      
      // Extract unit if present
      let unit = 'celsius';
      if (query.toLowerCase().includes('fahrenheit') || query.includes('°F')) {
        unit = 'fahrenheit';
      }
      
      console.log(`🌍 Detected location: ${location}`);
      console.log(`🌡️ Using temperature unit: ${unit}`);
      
      return {
        content: `I'll check the weather for ${location}.`,
        toolCalls: [
          {
            name: weatherTool.name,
            arguments: {
              location,
              unit
            }
          }
        ]
      };
    }
    
    // For non-weather queries, just respond directly
    return {
      content: `I'm a mock provider that can help with weather queries. For example, try asking "What's the weather like in London?" to test function calling.`,
      toolCalls: []
    };
  }
  
  async generateFollowUp(context: Message[]): Promise<string> {
    // Find the most recent tool response
    const toolResponse = [...context]
      .reverse()
      .find(msg => msg.role === 'tool');
    
    if (!toolResponse) {
      return "I don't have any weather information to share at the moment.";
    }
    
    try {
      // Parse the tool response
      const data = typeof toolResponse.content === 'string' 
        ? JSON.parse(toolResponse.content)
        : toolResponse.content;
      
      // Find the most recent user query
      const userQuery = [...context]
        .reverse()
        .find(msg => msg.role === 'user');
      
      const location = data.location || 'the requested location';
      const temperature = data.temperature || Math.floor(Math.random() * 30);
      const condition = data.condition || 'sunny';
      const unit = data.unit || 'celsius';
      
      return `Based on the latest data, the weather in ${location} is ${condition} with a temperature of ${temperature}°${unit === 'celsius' ? 'C' : 'F'}.`;
    } catch (error) {
      console.error('Error generating follow-up from tool data:', error);
      return "I processed the weather data but encountered an issue interpreting the results.";
    }
  }
}