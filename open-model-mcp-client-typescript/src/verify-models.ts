/**
 * Model verification script
 * This script tests each model's function calling capabilities
 */
import { verifyAllModels, verifyModel } from './model-verifier.js';
import { getModelInfo, RECOMMENDED_MODELS } from './model-info.js';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

async function main() {
  console.log("🔍 Open-Source Model Function Calling Test");
  console.log("=========================================");
  console.log("This script tests function calling capabilities with Ollama models.");
  console.log("Make sure Ollama is running before proceeding.\n");

  const args = process.argv.slice(2);
  
  // If a specific model is requested, test only that one
  if (args.length > 0 && args[0] === '--model' && args[1]) {
    const modelId = args[1];
    console.log(`Testing specific model: ${modelId}`);
    
    try {
      const result = await verifyModel(modelId);
      console.log("\n📊 Test Results:");
      console.log(`Model: ${result.modelName} (${result.modelId})`);
      console.log(`Function calling: ${result.supportsFunctionCalling ? '✅ Working' : '❌ Not working'}`);
      console.log(`Average response time: ${Math.round(result.avgResponseTimeMs)}ms`);
      console.log("\n📋 Detailed logs:");
      result.details.forEach((detail) => console.log(detail));
    } catch (error) {
      console.error("❌ Error testing model:", error);
    }
  } 
  // Otherwise test all recommended models
  else {
    console.log("Testing all recommended models:");
    RECOMMENDED_MODELS.forEach(model => {
      console.log(`- ${model.name} (${model.id})`);
    });

    try {
      const results = await verifyAllModels();
      
      console.log("\n📊 Summary Results:");
      results.forEach(result => {
        console.log(`${result.modelName} (${result.modelId}): Function calling ${result.supportsFunctionCalling ? '✅' : '❌'}, Response time: ${Math.round(result.avgResponseTimeMs)}ms`);
      });
      
      // Recommend the best model
      const workingModels = results.filter(r => r.supportsFunctionCalling);
      if (workingModels.length > 0) {
        // Sort by response time
        workingModels.sort((a, b) => a.avgResponseTimeMs - b.avgResponseTimeMs);
        const bestModel = workingModels[0];
        console.log(`\n💡 Recommended model: ${bestModel.modelName} (${bestModel.modelId})`);
        console.log(`To use this model, set OLLAMA_MODEL=${bestModel.modelId} in your .env file`);
      } else {
        console.log("\n❌ No models with working function calling were found.");
      }
    } catch (error) {
      console.error("❌ Error testing models:", error);
    }
  }
}

main().catch(error => {
  console.error("Unhandled error:", error);
  process.exit(1);
});
