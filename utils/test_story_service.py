import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.story_service import story_service
from models.schemas import StoryInputs
from loguru import logger


def test_story_service():
    """Test story generation service."""
    try:
        logger.info("Testing story generation service...")
        
        # Create test inputs
        test_inputs = StoryInputs(
            mood="hopeful",
            vibe="peaceful",
            archetype="the_seeker",
            dream="become_confident",
            mangaTitle="Journey to Confidence",
            nickname="Alex",
            hobby="reading",
            age=16,
            gender="non-binary"
        )
        
        logger.info(f"Generating story with inputs: {test_inputs}")
        
        # Generate story plan
        panels = asyncio.run(story_service.generate_story_plan(test_inputs))
        
        if panels and len(panels) == 6:
            logger.success(f"✅ Story generation successful! Generated {len(panels)} panels")
            
            # Log panel details
            for i, panel in enumerate(panels, 1):
                logger.info(f"Panel {i}: {panel.get('dialogue_text', 'No dialogue')[:50]}...")
            
            return True
        else:
            logger.error(f"❌ Story generation failed - expected 6 panels, got {len(panels) if panels else 0}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Story generation test failed: {e}")
        return False


if __name__ == "__main__":
    print("📖 Testing Story Generation Service")
    print("=" * 50)
    
    result = test_story_service()
    
    if result:
        print("\n✅ Story service test PASSED")
    else:
        print("\n❌ Story service test FAILED")
