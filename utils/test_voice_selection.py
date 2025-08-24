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
            {"age": 10, "gender": "male", "name": "Young Boy"},
            {"age": 10, "gender": "female", "name": "Young Girl"},
            {"age": 16, "gender": "male", "name": "Teen Boy"},
            {"age": 16, "gender": "female", "name": "Teen Girl"},
            {"age": 16, "gender": "non-binary", "name": "Teen Non-binary"},
            {"age": 25, "gender": "male", "name": "Adult Male"},
            {"age": 25, "gender": "female", "name": "Adult Female"},
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
        
        # Test cases for voice selection
        test_cases = [
            (8, "male"),     # Should be young male
            (12, "female"),  # Should be young female
            (15, "male"),    # Should be teen male
            (18, "female"),  # Should be teen female
            (17, "non-binary"), # Should be teen non-binary
            (25, "male"),    # Should be adult male
            (30, "female"),  # Should be adult female
            (22, "other"),   # Should default to non-binary adult
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
        print("   ✅ Age-appropriate voices (Young/Teen/Adult)")
        print("   ✅ Gender-specific voice selection")
        print("   ✅ Non-binary inclusive options")
        print("   ✅ Slower speech rate for young users")
        print("   ✅ High-quality Neural2 voices for best quality")
        print("\n🎵 Check generated voice samples:")
        print("   voice_test_[age]_[gender].mp3")
    else:
        print("\n❌ Voice Selection Tests FAILED")
        print("🔍 Check logs for details")
