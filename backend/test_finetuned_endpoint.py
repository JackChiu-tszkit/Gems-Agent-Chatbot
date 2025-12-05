"""
Test script: Find and test Fine-tuned Model Endpoint

This script will:
1. List all available Endpoints
2. Test Fine-tuned Model calls
3. Verify input/output formats
"""

import os
import logging
from google.cloud import aiplatform
import vertexai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration variables
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "your-project-id")
LOCATION = os.getenv("VERTEX_AI_LOCATION", "europe-north1")
MODEL_ID = "5539379163154087936"  # Model ID you provided

# Initialize
try:
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    aiplatform.init(project=PROJECT_ID, location=LOCATION)
    logger.info(f"✅ Vertex AI initialized successfully: project={PROJECT_ID}, location={LOCATION}")
except Exception as e:
    logger.error(f"❌ Vertex AI initialization failed: {e}")
    exit(1)


def list_endpoints():
    """List all available Endpoints"""
    try:
        logger.info("=" * 60)
        logger.info("Finding available Endpoints...")
        logger.info("=" * 60)
        
        # List all endpoints
        endpoints = aiplatform.Endpoint.list(
            filter=f'display_name:"Fine-tuning Gems model"',
            location=LOCATION
        )
        
        if not endpoints:
            logger.info("No matching Endpoints found, trying to list all Endpoints...")
            endpoints = aiplatform.Endpoint.list(location=LOCATION)
        
        if endpoints:
            logger.info(f"Found {len(endpoints)} Endpoints:")
            for i, endpoint in enumerate(endpoints, 1):
                logger.info(f"\n{i}. Endpoint:")
                logger.info(f"   - Name: {endpoint.display_name}")
                logger.info(f"   - ID: {endpoint.resource_name}")
                logger.info(f"   - Full path: {endpoint.resource_name}")
                
                # Extract Endpoint ID (from full path)
                # Format: projects/.../locations/.../endpoints/ENDPOINT_ID
                if "/endpoints/" in endpoint.resource_name:
                    endpoint_id = endpoint.resource_name.split("/endpoints/")[-1]
                    logger.info(f"   - Endpoint ID: {endpoint_id}")
                
                # Get deployed model information
                if hasattr(endpoint, 'deployed_models'):
                    logger.info(f"   - Number of deployed models: {len(endpoint.deployed_models) if endpoint.deployed_models else 0}")
            
            return endpoints
        else:
            logger.warning("No Endpoints found")
            return []
            
    except Exception as e:
        logger.error(f"Error listing Endpoints: {e}")
        import traceback
        traceback.print_exc()
        return []


def find_endpoint_by_model_id(model_id: str):
    """Find Endpoint corresponding to model ID"""
    try:
        logger.info("=" * 60)
        logger.info(f"Finding Endpoint for model ID {model_id}...")
        logger.info("=" * 60)
        
        # List all endpoints
        endpoints = aiplatform.Endpoint.list(location=LOCATION)
        
        for endpoint in endpoints:
            # Check deployed models
            if hasattr(endpoint, 'deployed_models') and endpoint.deployed_models:
                for deployed_model in endpoint.deployed_models:
                    # Check model ID
                    if hasattr(deployed_model, 'model') and model_id in deployed_model.model:
                        logger.info(f"✅ Found matching Endpoint!")
                        logger.info(f"   - Endpoint name: {endpoint.display_name}")
                        logger.info(f"   - Endpoint full path: {endpoint.resource_name}")
                        
                        # Extract Endpoint ID
                        if "/endpoints/" in endpoint.resource_name:
                            endpoint_id = endpoint.resource_name.split("/endpoints/")[-1]
                            logger.info(f"   - Endpoint ID: {endpoint_id}")
                            return endpoint, endpoint_id
        
        logger.warning("No matching Endpoint found")
        return None, None
        
    except Exception as e:
        logger.error(f"Error finding Endpoint: {e}")
        import traceback
        traceback.print_exc()
        return None, None


def test_endpoint_prediction(endpoint_name: str):
    """Test Endpoint prediction functionality"""
    try:
        logger.info("=" * 60)
        logger.info("Testing Endpoint prediction...")
        logger.info("=" * 60)
        
        # Create Endpoint client
        endpoint = aiplatform.Endpoint(endpoint_name)
        
        # Test Prompt
        test_prompt = """User question: What is GEMS Agent?

Retrieved information from knowledge base:
GEMS Agent is an AI assistant for resource management, sales enablement, market analysis, and operational automation.

Instructions:
- Please answer the question STRICTLY based on the retrieved information above.
- Be professional and precise.

Answer:"""
        
        # Try different input formats
        test_formats = [
            # Format 1: Gemini standard format
            {
                "contents": [{
                    "role": "user",
                    "parts": [{
                        "text": test_prompt
                    }]
                }]
            },
            # Format 2: Simple text format
            {
                "text": test_prompt
            },
            # Format 3: Prompt format
            {
                "prompt": test_prompt
            }
        ]
        
        for i, instance_format in enumerate(test_formats, 1):
            try:
                logger.info(f"\nTrying format {i}: {list(instance_format.keys())}")
                
                instances = [instance_format]
                parameters = {
                    "temperature": 0.2,
                    "max_output_tokens": 256,
                }
                
                # Execute prediction
                response = endpoint.predict(
                    instances=instances,
                    parameters=parameters
                )
                
                logger.info(f"✅ Format {i} succeeded!")
                logger.info(f"Response type: {type(response)}")
                logger.info(f"Response content: {response}")
                
                # Parse response
                if response.predictions:
                    prediction = response.predictions[0]
                    logger.info(f"\nPrediction result type: {type(prediction)}")
                    logger.info(f"Prediction result: {prediction}")
                    
                    # Try to extract text
                    if isinstance(prediction, dict):
                        logger.info(f"\nDictionary keys: {list(prediction.keys())}")
                        
                        # Try different extraction methods
                        if "candidates" in prediction:
                            candidates = prediction["candidates"]
                            if candidates and len(candidates) > 0:
                                candidate = candidates[0]
                                logger.info(f"Candidate result: {candidate}")
                                if isinstance(candidate, dict) and "content" in candidate:
                                    content = candidate["content"]
                                    if isinstance(content, dict) and "parts" in content:
                                        parts = content["parts"]
                                        if parts and len(parts) > 0:
                                            text = parts[0].get("text", "")
                                            logger.info(f"✅ Extracted text: {text}")
                                            return text
                        
                        # Other possible keys
                        for key in ["text", "content", "output", "response"]:
                            if key in prediction:
                                logger.info(f"✅ Found key '{key}': {prediction[key]}")
                                return str(prediction[key])
                    
                    elif isinstance(prediction, str):
                        logger.info(f"✅ String response: {prediction}")
                        return prediction
                
                # If format succeeded, don't try other formats
                break
                
            except Exception as e:
                logger.warning(f"Format {i} failed: {e}")
                continue
        
        logger.warning("All formats failed")
        return None
        
    except Exception as e:
        logger.error(f"Error testing Endpoint: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Main function"""
    logger.info("\n" + "=" * 60)
    logger.info("Fine-tuned Model Endpoint Test Script")
    logger.info("=" * 60)
    logger.info(f"Project ID: {PROJECT_ID}")
    logger.info(f"Region: {LOCATION}")
    logger.info(f"Model ID: {MODEL_ID}")
    logger.info("=" * 60 + "\n")
    
    # Step 1: List all Endpoints
    endpoints = list_endpoints()
    
    # Step 2: Find Endpoint by model ID
    endpoint, endpoint_id = find_endpoint_by_model_id(MODEL_ID)
    
    if not endpoint:
        logger.warning("\n⚠️  No matching Endpoint found, trying to use first available Endpoint...")
        if endpoints:
            endpoint = endpoints[0]
            if "/endpoints/" in endpoint.resource_name:
                endpoint_id = endpoint.resource_name.split("/endpoints/")[-1]
                logger.info(f"Using Endpoint: {endpoint_id}")
    
    # Step 3: Test Endpoint
    if endpoint:
        logger.info("\n" + "=" * 60)
        logger.info("Starting Endpoint test...")
        logger.info("=" * 60)
        
        result = test_endpoint_prediction(endpoint.resource_name)
        
        if result:
            logger.info("\n" + "=" * 60)
            logger.info("✅ Test successful!")
            logger.info("=" * 60)
            logger.info(f"\nEndpoint ID: {endpoint_id}")
            logger.info(f"Endpoint full path: {endpoint.resource_name}")
            logger.info(f"\nTest response: {result}")
            logger.info("\n" + "=" * 60)
            logger.info("Please add the following to environment variables:")
            logger.info(f"FINE_TUNED_ENDPOINT_ID={endpoint_id}")
            logger.info("=" * 60)
        else:
            logger.error("\n❌ Test failed, please check Endpoint configuration")
    else:
        logger.error("\n❌ No available Endpoint found")
        logger.info("\nTips:")
        logger.info("1. Confirm model is deployed to Endpoint")
        logger.info("2. Check if PROJECT_ID and LOCATION are correct")
        logger.info("3. Confirm you have access to Vertex AI")


if __name__ == "__main__":
    main()
