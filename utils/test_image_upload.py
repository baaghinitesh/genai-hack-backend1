import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.image_service import image_service
from loguru import logger


async def test_image_upload_to_gcs():
    """Test image generation AND upload to GCS."""
    try:
        logger.info("Testing image generation + GCS upload...")
        
        # Test prompt
        test_prompt = "A peaceful mountain landscape at sunset"
        story_id = "test_story_123"
        panel_number = 1
        
        logger.info(f"Generating and uploading image with prompt: {test_prompt}")
        logger.info(f"Story ID: {story_id}")
        logger.info(f"Panel: {panel_number}")
        
        # Generate image and upload to GCS
        image_url = await image_service.generate_single_panel(test_prompt, story_id, panel_number)
        
        if image_url:
            logger.success(f"✅ Image generated and uploaded successfully!")
            logger.info(f"🔗 GCS URL: {image_url}")
            logger.info(f"📁 Check your GCS bucket 'calmira-backend' for: stories/{story_id}/panel_01.png")
            
            return True
        else:
            logger.error("❌ Image upload failed - no URL returned")
            return False
            
    except Exception as e:
        logger.error(f"❌ Image upload test failed: {e}")
        return False


if __name__ == "__main__":
    print("☁️  Testing Image Generation + GCS Upload")
    print("=" * 50)
    
    result = asyncio.run(test_image_upload_to_gcs())
    
    if result:
        print("\n✅ Image upload test PASSED")
        print("🔗 Check your Google Cloud Console > Storage > calmira-backend bucket")
    else:
        print("\n❌ Image upload test FAILED")
