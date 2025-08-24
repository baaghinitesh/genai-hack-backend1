import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Simple test without importing the full audio service
from loguru import logger

async def test_simple_tts():
    """Test TTS generation directly without complex dependencies."""
    try:
        # Import TTS directly
        from google.cloud import texttospeech
        
        logger.info("✅ TTS import successful!")
        
        # Initialize TTS client
        client = texttospeech.TextToSpeechClient()
        logger.info("✅ TTS client initialized!")
        
        # Test text
        test_text = "Hello, this is a test of the text-to-speech system."
        
        # Prepare TTS request
        synthesis_input = texttospeech.SynthesisInput(text=test_text)
        
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name="en-US-Standard-C",  # Female voice
            ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
        )
        
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )
        
        logger.info("Generating TTS audio...")
        
        # Generate TTS
        response = await asyncio.to_thread(
            client.synthesize_speech,
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
        
        # Save the audio
        audio_data = response.audio_content
        
        if audio_data and len(audio_data) > 0:
            with open("test_simple_tts.mp3", "wb") as f:
                f.write(audio_data)
            
            logger.success(f"✅ TTS generation successful! Generated {len(audio_data)} bytes")
            logger.info("✅ Audio saved as 'test_simple_tts.mp3'")
            return True
        else:
            logger.error("❌ No audio data generated")
            return False
            
    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        logger.info("💡 You need to enable the Text-to-Speech API in Google Cloud Console")
        return False
    except Exception as e:
        logger.error(f"❌ TTS test failed: {e}")
        return False

if __name__ == "__main__":
    print("🗣️  Testing Simple TTS (Direct)")
    print("=" * 50)
    
    result = asyncio.run(test_simple_tts())
    
    if result:
        print("\n✅ Simple TTS test PASSED")
        print("🎵 Check 'test_simple_tts.mp3' file")
    else:
        print("\n❌ Simple TTS test FAILED")
        print("\n📋 Required API to enable:")
        print("   - Cloud Text-to-Speech API")
