import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.audio_service import audio_service
from loguru import logger


async def test_tts_generation():
    """Test TTS generation using Google Cloud Text-to-Speech."""
    try:
        logger.info("Testing TTS generation...")
        
        # Test text for TTS
        test_text = "Welcome to our manga story. This is a test of the text-to-speech system."
        
        logger.info(f"Generating TTS with text: {test_text}")
        
        # Generate TTS audio
        audio_data = await audio_service.generate_tts_audio(test_text, 1)
        
        if audio_data and len(audio_data) > 0:
            logger.success(f"✅ TTS generation successful! Generated {len(audio_data)} bytes")
            
            # Save test audio locally
            with open("test_tts.mp3", "wb") as f:
                f.write(audio_data)
            logger.info("Test TTS saved as 'test_tts.mp3'")
            
            return True
        else:
            logger.error("❌ TTS generation failed - no data returned")
            return False
            
    except Exception as e:
        logger.error(f"❌ TTS generation test failed: {e}")
        return False


if __name__ == "__main__":
    print("🗣️  Testing Text-to-Speech Service")
    print("=" * 50)
    
    result = asyncio.run(test_tts_generation())
    
    if result:
        print("\n✅ TTS service test PASSED")
        print("🎵 Check 'test_tts.mp3' file in project root")
    else:
        print("\n❌ TTS service test FAILED")
