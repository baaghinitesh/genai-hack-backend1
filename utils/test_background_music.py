import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.audio_service import audio_service
from loguru import logger


async def test_background_music_generation():
    """Test background music generation using Lyria-002."""
    try:
        logger.info("Testing background music generation with Lyria-002...")
        
        # Test music prompt following Lyria best practices
        test_prompt = "peaceful ambient background music for emotional manga scene, gentle and hopeful"
        
        logger.info(f"Generating background music with prompt: {test_prompt}")
        
        # Generate background music
        music_data = await audio_service.generate_background_music(test_prompt, 1)
        
        if music_data and len(music_data) > 0:
            logger.success(f"✅ Background music generation successful! Generated {len(music_data)} bytes")
            
            # Save test music locally
            with open("test_background_music.wav", "wb") as f:
                f.write(music_data)
            logger.info("Test background music saved as 'test_background_music.wav'")
            
            return True
        else:
            logger.error("❌ Background music generation failed - no data returned")
            return False
            
    except Exception as e:
        logger.error(f"❌ Background music generation test failed: {e}")
        return False


async def test_full_audio_generation():
    """Test both TTS and background music generation."""
    try:
        logger.info("Testing full audio generation (TTS + Background Music)...")
        
        # Test data
        test_text = "Welcome to this peaceful manga scene, where hope begins to bloom."
        test_music_prompt = "calm ambient music, soft piano, peaceful mood, emotional undertones"
        
        logger.info("Generating TTS and background music in parallel...")
        
        # Generate both in parallel
        tts_task = audio_service.generate_tts_audio(test_text, 1)
        music_task = audio_service.generate_background_music(test_music_prompt, 1)
        
        tts_data, music_data = await asyncio.gather(tts_task, music_task)
        
        if tts_data and music_data:
            logger.success(f"✅ Full audio generation successful!")
            logger.info(f"   TTS: {len(tts_data)} bytes")
            logger.info(f"   Music: {len(music_data)} bytes")
            
            # Save both files
            with open("test_full_tts.mp3", "wb") as f:
                f.write(tts_data)
            
            with open("test_full_music.wav", "wb") as f:
                f.write(music_data)
                
            logger.info("Files saved: test_full_tts.mp3 and test_full_music.wav")
            
            return True
        else:
            logger.error("❌ Full audio generation failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Full audio generation test failed: {e}")
        return False


async def run_all_music_tests():
    """Run all background music tests."""
    logger.info("Starting background music test suite...")
    
    # Test 1: Background music only
    print("\n1️⃣  Testing Background Music Generation")
    print("-" * 40)
    music_result = await test_background_music_generation()
    
    print("\n2️⃣  Testing Full Audio Generation (TTS + Music)")
    print("-" * 40)
    full_result = await test_full_audio_generation()
    
    return music_result and full_result


if __name__ == "__main__":
    print("🎵 Testing Lyria-002 Background Music Service")
    print("=" * 50)
    
    result = asyncio.run(run_all_music_tests())
    
    if result:
        print("\n✅ Background music tests PASSED")
        print("🎵 Check audio files in project root:")
        print("   - test_background_music.wav")
        print("   - test_full_tts.mp3") 
        print("   - test_full_music.wav")
    else:
        print("\n❌ Background music tests FAILED")
        print("🔍 Check logs for details. May be using fallback placeholder audio.")
