import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.audio_service import audio_service
from loguru import logger


async def test_background_music():
    """Test background music generation."""
    try:
        logger.info("Testing background music generation...")
        
        test_prompt = "Peaceful and hopeful ambient music for emotional manga scene"
        
        logger.info(f"Generating test music with prompt: {test_prompt}")
        
        # Generate background music
        music_data = await audio_service.generate_background_music(test_prompt, 1)
        
        if music_data and len(music_data) > 0:
            logger.success(f"✅ Background music generation successful! Generated {len(music_data)} bytes")
            
            # Save test audio locally
            with open("test_music.mp3", "wb") as f:
                f.write(music_data)
            logger.info("Test music saved as 'test_music.mp3'")
            
            return True
        else:
            logger.error("❌ Background music generation failed - no data returned")
            return False
            
    except Exception as e:
        logger.error(f"❌ Background music test failed: {e}")
        return False


async def test_tts_generation():
    """Test TTS generation."""
    try:
        logger.info("Testing TTS generation...")
        
        test_text = "This is a test of the text-to-speech system for our manga story."
        
        logger.info(f"Generating TTS with text: {test_text}")
        
        # Generate TTS
        tts_data = await audio_service.generate_tts_audio(test_text, 1)
        
        if tts_data and len(tts_data) > 0:
            logger.success(f"✅ TTS generation successful! Generated {len(tts_data)} bytes")
            
            # Save test TTS locally
            with open("test_tts.mp3", "wb") as f:
                f.write(tts_data)
            logger.info("Test TTS saved as 'test_tts.mp3'")
            
            return True
        else:
            logger.error("❌ TTS generation failed - no data returned")
            return False
            
    except Exception as e:
        logger.error(f"❌ TTS test failed: {e}")
        return False


async def run_audio_tests():
    """Run all audio tests."""
    music_result = await test_background_music()
    print()
    tts_result = await test_tts_generation()
    
    return music_result and tts_result


if __name__ == "__main__":
    print("🎵 Testing Audio Generation Services")
    print("=" * 50)
    
    result = asyncio.run(run_audio_tests())
    
    if result:
        print("\n✅ Audio services test PASSED")
    else:
        print("\n❌ Audio services test FAILED")
