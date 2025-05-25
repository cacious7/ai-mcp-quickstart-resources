# Installation Guide

This guide provides detailed instructions for setting up the Hugging Face MCP Client.

## Prerequisites

- **Node.js**: Version 18 or higher
- **npm**: Usually comes with Node.js
- **TypeScript**: Will be installed via npm
- **Hugging Face Account**: Required for API access
- **Weather Server**: Either the Python or TypeScript version from the quickstart resources

## Step 1: Clone the Repository

If you haven't already, clone the repository containing this project:

```bash
git clone <repository-url>
cd huggingface-mcp-client-typescript
```

## Step 2: Install Dependencies

Run the following command to install all required dependencies:

```bash
npm install
```

## Step 3: Set Up Hugging Face API Access

1. **Create a Hugging Face Account**:
   - Visit [Hugging Face](https://huggingface.co/) and sign up for an account

2. **Generate an API Token**:
   - Go to your profile → Settings → Access Tokens
   - Create a new token with "read" permissions
   - Give it a meaningful name like "MCP Client"
   - Copy the token value

3. **Configure the `.env` File**:
   - Create or edit the `.env` file in the project root
   - Add your API key:
     ```
     HUGGINGFACE_API_KEY=your_api_key_here
     ```

## Step 4: Choose a Model

Select a model by updating the `.env` file:

```
# Current model to use
HUGGINGFACE_MODEL=meta-llama/Llama-2-7b-chat-hf
```

Available options include:
- `mistralai/Mistral-7B-Instruct-v0.2`
- `meta-llama/Llama-2-7b-chat-hf` (default)
- `OpenAssistant/oasst-sft-4-pythia-12b-epoch-3.5`
- `microsoft/phi-2`

## Step 5: Build the Project

Build the TypeScript code:

```bash
npm run build
```

## Step 6: Verify Installation

Verify your setup is working correctly:

```bash
# Test connectivity to Hugging Face API
npm run verify

# Test a model with a simple query
npm run verify:model -- --model microsoft/phi-2
```

If everything is working, you should see successful connection messages and a response from the model.

## Step 7: Run the Client

Connect to a weather server:

```bash
# Using the TypeScript weather server
npm start -- ../weather-server-typescript/build/index.js

# OR using the Python weather server
npm start -- ../weather-server-python/weather.py
```

## Troubleshooting

### API Key Issues

If you see authentication errors:
- Double check your API key in the `.env` file
- Ensure your Hugging Face account has proper permissions
- Try regenerating a new API key

### Model Access Issues

Some models require special access:
- Visit the model page on Hugging Face to request access if needed
- Try using `microsoft/phi-2` which is openly available

### Connection Problems

If the client can't connect to the Hugging Face API:
- Check your internet connection
- Verify there are no firewalls blocking the connection
- Try using a VPN if your network blocks the API

### Weather Server Issues

If the client can't connect to the weather server:
- Make sure the weather server is properly installed
- Check the path to the weather server script
- Try running the weather server separately to verify it works
