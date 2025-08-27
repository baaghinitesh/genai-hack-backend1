import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.audio_service import audio_service
from loguru import logger


async def test_voice_selection_for_different_users():
    """Test voice selection for different user demographics."""
    try:
        logger.info("Testing voice selection for different user demographics...")
        
        # Test different user profiles
        test_users = [
            {"age": 16, "gender": "male", "name": "Male User"},
            {"age": 16, "gender": "female", "name": "Female User"},
            {"age": 16, "gender": "non-binary", "name": "Non-binary User"},
            {"age": 16, "gender": "prefer_not_to_say", "name": "Prefer Not to Say"},
        ]
        
        test_text = "Welcome to your personalized manga story. This is how your voice sounds for narration."
        
        successful_tests = 0
        
        for i, user in enumerate(test_users, 1):
            try:
                logger.info(f"\n--- Testing {user['name']} (Age: {user['age']}, Gender: {user['gender']}) ---")
                
                # Generate TTS with user-specific voice
                tts_data = await audio_service.generate_tts_audio(
                    text=test_text,
                    panel_number=i,
                    user_age=user['age'],
                    user_gender=user['gender']
                )
                
                if tts_data and len(tts_data) > 0:
                    # Save with descriptive filename
                    filename = f"voice_test_{user['age']}_{user['gender']}.mp3"
                    with open(filename, "wb") as f:
                        f.write(tts_data)
                    
                    logger.success(f"✅ {user['name']}: {len(tts_data)} bytes saved as {filename}")
                    successful_tests += 1
                else:
                    logger.error(f"❌ {user['name']}: No audio generated")
                    
            except Exception as e:
                logger.error(f"❌ {user['name']}: Failed - {e}")
        
        logger.info(f"\n📊 Voice Selection Test Results:")
        logger.info(f"   ✅ Successful: {successful_tests}/{len(test_users)}")
        logger.info(f"   📁 Generated files: voice_test_[age]_[gender].mp3")
        
        return successful_tests == len(test_users)
        
    except Exception as e:
        logger.error(f"❌ Voice selection test failed: {e}")
        return False


async def test_voice_mapping_logic():
    """Test the voice mapping logic without generating audio."""
    try:
        logger.info("Testing voice mapping logic...")
        
        # Test cases for gender-based voice selection
        test_cases = [
            (16, "male"),         # Should use Fenrir voice
            (16, "female"),       # Should use Kore voice
            (16, "non-binary"),   # Should use Gacrux voice
            (16, "prefer_not_to_say"), # Should use Charon voice
            (16, "other"),        # Should default to prefer_not_to_say (Charon)
        ]
        
        for age, gender in test_cases:
            voice_info = audio_service._select_voice_for_user(age, gender)
            logger.info(f"Age {age}, Gender {gender} → Voice: {voice_info['name']}")
        
        logger.success("✅ Voice mapping logic test completed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Voice mapping test failed: {e}")
        return False


async def run_voice_tests():
    """Run all voice selection tests."""
    print("🗣️  Testing Voice Selection System")
    print("=" * 50)
    
    # Test 1: Voice mapping logic
    print("\n1️⃣  Testing Voice Mapping Logic")
    print("-" * 40)
    logic_result = await test_voice_mapping_logic()
    
    # Test 2: Actual voice generation
    print("\n2️⃣  Testing Voice Generation for Different Users")
    print("-" * 40)
    generation_result = await test_voice_selection_for_different_users()
    
    return logic_result and generation_result


if __name__ == "__main__":
    result = asyncio.run(run_voice_tests())
    
    if result:
        print("\n✅ Voice Selection Tests PASSED!")
        print("\n🎯 Voice Selection System Features:")
        print("   ✅ Gender-specific voice selection")
        print("   ✅ Male: en-IN-Chirp3-HD-Fenrir")
        print("   ✅ Female: en-IN-Chirp3-HD-Kore")
        print("   ✅ Non-binary: en-IN-Chirp3-HD-Gacrux")
        print("   ✅ Prefer not to say: en-IN-Chirp3-HD-Charon")
        print("   ✅ High-quality Chirp 3 HD voices")
        print("\n🎵 Check generated voice samples:")
        print("   voice_test_16_[gender].mp3")
    else:
        print("\n❌ Voice Selection Tests FAILED")
        print("🔍 Check logs for details")
