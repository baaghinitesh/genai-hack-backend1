import asyncio
import sys
import os
from langchain_google_vertexai import ChatVertexAI

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.image_service import image_service
from loguru import logger


async def test_image_generation():
    """Test image generation service."""
    try:
        logger.info("Testing image generation service...")
        
        # Test simple image generation with a safer prompt
        test_prompt = "A peaceful landscape with mountains and trees"
        
        logger.info(f"Generating test image with prompt: {test_prompt}")
        
        # Generate image
        image_data = await image_service.generate_image(test_prompt, 1)
        
        if image_data and len(image_data) > 0:
            logger.success(f"✅ Image generation successful! Generated {len(image_data)} bytes")
            
            # Save test image locally
            with open("test_image.png", "wb") as f:
                f.write(image_data)
            logger.info("Test image saved as 'test_image.png'")
            
            return True
        else:
            logger.error("❌ Image generation failed - no data returned")
            return False
            
    except Exception as e:
        logger.error(f"❌ Image generation test failed: {e}")
        return False


if __name__ == "__main__":
    print("🖼️  Testing Image Generation Service")
    print("=" * 50)
    
    result = asyncio.run(test_image_generation())
    
    if result:
        print("\n✅ Image service test PASSED")
    else:
        print("\n❌ Image service test FAILED")
