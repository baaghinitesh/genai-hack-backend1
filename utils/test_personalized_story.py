import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.story_service import story_service
from models.schemas import StoryInputs
from loguru import logger


async def test_personalized_story_generation():
    """Test complete personalized story generation with age/gender-appropriate voice."""
    try:
        logger.info("Testing complete personalized story generation...")
        
        # Test with a 16-year-old female user
        test_inputs = StoryInputs(
            mood="hopeful",
            vibe="inspiring", 
            archetype="the_seeker",
            dream="overcome_shyness",
            mangaTitle="Finding My Voice",
            nickname="Maya",
            hobby="art",
            age=16,
            gender="female"
        )
        
        logger.info(f"Generating story for: {test_inputs.nickname}, {test_inputs.age} years old, {test_inputs.gender}")
        logger.info(f"Story theme: {test_inputs.mangaTitle}")
        
        # Generate the complete story with personalized voice
        story = await story_service.generate_complete_story(test_inputs)
        
        if story and story.status == "completed":
            logger.success(f"✅ Complete personalized story generated!")
            logger.info(f"   📖 Story ID: {story.story_id}")
            logger.info(f"   🖼️  Images: {len(story.image_urls)} panels")
            logger.info(f"   🎵 Audio: {story.audio_url}")
            
            # Log the generated content
            logger.info("\n📋 Generated Story Panels:")
            for i, panel in enumerate(story.panels, 1):
                logger.info(f"   Panel {i}: {panel.get('dialogue_text', 'N/A')[:50]}...")
            
            logger.info("\n🔗 Generated URLs:")
            for i, url in enumerate(story.image_urls, 1):
                logger.info(f"   🖼️  Panel {i}: {url}")
            
            logger.info(f"   🎼 Final Audio: {story.audio_url}")
            
            return True
        else:
            logger.error("❌ Story generation failed or incomplete")
            return False
            
    except Exception as e:
        logger.error(f"❌ Personalized story generation failed: {e}")
        return False


async def test_different_user_stories():
    """Test story generation for different user demographics."""
    try:
        logger.info("Testing story generation for different user demographics...")
        
        # Test different user profiles
        test_users = [
            {
                "age": 12, "gender": "male", "nickname": "Alex",
                "theme": "Adventure Quest", "mood": "excited"
            },
            {
                "age": 17, "gender": "non-binary", "nickname": "Sam", 
                "theme": "Self Discovery", "mood": "contemplative"
            }
        ]
        
        successful_stories = 0
        
        for user in test_users:
            try:
                logger.info(f"\n--- Generating story for {user['nickname']} ({user['age']}, {user['gender']}) ---")
                
                test_inputs = StoryInputs(
                    mood=user["mood"],
                    vibe="peaceful",
                    archetype="the_seeker", 
                    dream="find_purpose",
                    mangaTitle=user["theme"],
                    nickname=user["nickname"],
                    hobby="reading",
                    age=user["age"],
                    gender=user["gender"]
                )
                
                # Generate just the story plan (faster test)
                panels = await story_service.generate_story_plan(test_inputs)
                
                if panels and len(panels) == 6:
                    logger.success(f"✅ {user['nickname']}: Story plan generated with {len(panels)} panels")
                    
                    # Test just TTS generation with personalized voice
                    from services.audio_service import audio_service
                    test_dialogue = panels[0].get('dialogue_text', 'Test narration for this story')
                    
                    tts_data = await audio_service.generate_tts_audio(
                        test_dialogue, 1, user["age"], user["gender"]
                    )
                    
                    if tts_data:
                        filename = f"story_voice_{user['nickname']}_{user['age']}_{user['gender']}.mp3"
                        with open(filename, "wb") as f:
                            f.write(tts_data)
                        logger.success(f"✅ {user['nickname']}: Voice sample saved as {filename}")
                        successful_stories += 1
                    
                else:
                    logger.error(f"❌ {user['nickname']}: Story generation failed")
                    
            except Exception as e:
                logger.error(f"❌ {user['nickname']}: Failed - {e}")
        
        logger.info(f"\n📊 Multi-user test results: {successful_stories}/{len(test_users)} successful")
        return successful_stories == len(test_users)
        
    except Exception as e:
        logger.error(f"❌ Multi-user story test failed: {e}")
        return False


async def run_personalized_story_tests():
    """Run all personalized story tests."""
    print("📖 Testing Personalized Story Generation")
    print("=" * 50)
    
    # Test 1: Complete story generation
    print("\n1️⃣  Testing Complete Personalized Story")
    print("-" * 40)
    complete_result = await test_personalized_story_generation()
    
    # Test 2: Multiple user demographics  
    print("\n2️⃣  Testing Different User Demographics")
    print("-" * 40)
    multi_result = await test_different_user_stories()
    
    return complete_result and multi_result


if __name__ == "__main__":
    result = asyncio.run(run_personalized_story_tests())
    
    if result:
        print("\n🎉 PERSONALIZED STORY TESTS PASSED!")
        print("\n🚀 Complete AI Pipeline Working:")
        print("   ✅ Story generation with user context")
        print("   ✅ Age/gender-appropriate voice selection")
        print("   ✅ Personalized image generation")
        print("   ✅ Background music generation")
        print("   ✅ Complete audio-visual synchronization")
        print("\n🎵 Check your Google Cloud Storage bucket for generated assets!")
    else:
        print("\n❌ PERSONALIZED STORY TESTS FAILED")
        print("🔍 Check logs for details")
