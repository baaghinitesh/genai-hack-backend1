import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.audio_service import audio_service
from loguru import logger


async def test_complete_audio_pipeline():
    """Test the complete audio pipeline: TTS + Background Music + Synchronization."""
    try:
        logger.info("Testing complete audio pipeline...")
        
        # Simulate 3 manga panels
        panels = [
            {
                'panel_number': 1,
                'dialogue_text': "In a quiet school hallway, Alex feels uncertain about the future.",
                'music_prompt': "gentle piano melody, contemplative mood, soft emotional undertones"
            },
            {
                'panel_number': 2, 
                'dialogue_text': "A teacher's encouraging words spark a glimmer of hope.",
                'music_prompt': "uplifting strings, warm harmony, hopeful atmosphere"
            },
            {
                'panel_number': 3,
                'dialogue_text': "With newfound confidence, Alex takes the first step forward.",
                'music_prompt': "inspiring orchestral, triumphant mood, emotional crescendo"
            }
        ]
        
        story_id = "test_audio_pipeline_123"
        
        logger.info(f"Testing with {len(panels)} panels")
        
        # Test the full audio generation workflow
        background_urls, tts_urls = await audio_service.generate_all_audio(panels, story_id)
        
        if background_urls and tts_urls and len(background_urls) == 3 and len(tts_urls) == 3:
            logger.success(f"✅ Complete audio pipeline successful!")
            logger.info(f"   Background music URLs: {len(background_urls)}")
            logger.info(f"   TTS URLs: {len(tts_urls)}")
            
            # Log the URLs
            for i, (bg_url, tts_url) in enumerate(zip(background_urls, tts_urls), 1):
                logger.info(f"   Panel {i}:")
                logger.info(f"     🎵 Music: {bg_url}")
                logger.info(f"     🗣️  TTS: {tts_url}")
            
            # Test audio synchronization
            logger.info("Testing audio synchronization...")
            final_audio_url = await audio_service.synchronize_audio(background_urls, tts_urls, story_id)
            
            if final_audio_url:
                logger.success(f"✅ Audio synchronization successful!")
                logger.info(f"   🎼 Final audio: {final_audio_url}")
                return True
            else:
                logger.error("❌ Audio synchronization failed")
                return False
        else:
            logger.error("❌ Complete audio pipeline failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Complete audio pipeline test failed: {e}")
        return False


async def test_lyria_prompt_variations():
    """Test different prompt styles to find what works best with Lyria content filters."""
    try:
        logger.info("Testing Lyria prompt variations to avoid content filters...")
        
        # Test different prompt styles
        test_prompts = [
            "ambient instrumental music, peaceful atmosphere",
            "soft piano composition, emotional depth", 
            "gentle orchestral background, contemplative mood",
            "calm synthesized soundscape, meditative tones",
            "atmospheric instrumental piece, subtle harmonies"
        ]
        
        successful_prompts = []
        failed_prompts = []
        
        for i, prompt in enumerate(test_prompts, 1):
            try:
                logger.info(f"Testing prompt {i}: {prompt}")
                music_data = await audio_service.generate_background_music(prompt, i)
                
                # Check if it's real Lyria (large file) or placeholder (small file)
                if len(music_data) > 3000000:  # > 3MB indicates real Lyria
                    successful_prompts.append(prompt)
                    logger.success(f"✅ Real Lyria generation: {len(music_data)} bytes")
                else:
                    failed_prompts.append(prompt)
                    logger.warning(f"⚠️  Fallback audio: {len(music_data)} bytes")
                    
            except Exception as e:
                failed_prompts.append(prompt)
                logger.error(f"❌ Failed: {e}")
        
        logger.info(f"\n📊 Results:")
        logger.info(f"   ✅ Successful prompts: {len(successful_prompts)}")
        logger.info(f"   ❌ Failed prompts: {len(failed_prompts)}")
        
        if successful_prompts:
            logger.info(f"\n🎯 Working prompt patterns:")
            for prompt in successful_prompts:
                logger.info(f"   - {prompt}")
                
        return len(successful_prompts) > 0
        
    except Exception as e:
        logger.error(f"❌ Prompt variation test failed: {e}")
        return False


async def run_complete_audio_tests():
    """Run all audio tests."""
    print("🎼 Complete Audio Pipeline Tests")
    print("=" * 50)
    
    # Test 1: Prompt variations
    print("\n1️⃣  Testing Lyria Prompt Variations")
    print("-" * 40)
    prompt_result = await test_lyria_prompt_variations()
    
    # Test 2: Complete pipeline (if prompts work)
    if prompt_result:
        print("\n2️⃣  Testing Complete Audio Pipeline")
        print("-" * 40)
        pipeline_result = await test_complete_audio_pipeline()
    else:
        logger.warning("Skipping pipeline test due to prompt issues")
        pipeline_result = False
    
    return prompt_result and pipeline_result


if __name__ == "__main__":
    result = asyncio.run(run_complete_audio_tests())
    
    if result:
        print("\n🎉 ALL AUDIO TESTS PASSED!")
        print("🚀 Your complete audio pipeline is working:")
        print("   ✅ Lyria-002 background music generation")
        print("   ✅ Google Cloud Text-to-Speech")
        print("   ✅ Audio synchronization with FFmpeg")
        print("   ✅ Google Cloud Storage upload")
    else:
        print("\n⚠️  SOME TESTS FAILED")
        print("🔍 Check logs for details. May need prompt engineering.")
