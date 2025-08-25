#!/usr/bin/env python3
"""
Test script for Chirp 3: HD TTS using Google Cloud Text-to-Speech.
"""

import asyncio
import sys
import os
from google.cloud import texttospeech

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loguru import logger


async def test_chirp_tts_simple():
    """Test Chirp 3: HD TTS with simple case using Google Cloud TTS."""
    try:
        logger.info("Testing Chirp 3: HD TTS with Google Cloud Text-to-Speech...")

        # Initialize Google Cloud TTS client
        tts_client = texttospeech.TextToSpeechClient()

        # Simple test case - just one test with the exact voice specified
        test_text = "Hello, this is a test of Chirp 3 HD voice using Google Cloud Text-to-Speech."

        logger.info("Simple Chirp 3: HD Test")
        logger.info(f"Text: {test_text}")
        logger.info("Voice: en-IN-Chirp3-HD-Charon")

        # Create synthesis input
        synthesis_input = texttospeech.SynthesisInput(text=test_text)

        # Configure voice - exactly as specified
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-IN",
            name="en-IN-Chirp3-HD-Charon",
        )

        # Configure audio
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=1.0,
            pitch=0.0,
            volume_gain_db=0.0
        )

        # Generate speech
        response = await asyncio.to_thread(
            tts_client.synthesize_speech,
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )

        # Get audio data
        audio_data = response.audio_content

        if audio_data and len(audio_data) > 0:
            # Save the audio file
            filename = "chirp_test_simple.mp3"
            with open(filename, "wb") as f:
                f.write(audio_data)

            logger.success("✅ Simple Chirp 3: HD test: Audio generated successfully!")
            logger.info(f"   📁 Saved as: {filename}")
            logger.info(f"   📊 Size: {len(audio_data)} bytes")
            return True
        else:
            logger.error("❌ Simple test: No audio data generated")
            return False

    except Exception as e:
        logger.error(f"❌ Chirp TTS test failed: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        return False


async def run_chirp_tests():
    """Run Chirp 3: HD tests."""
    print("🎤 Chirp 3: HD TTS Test (Google Cloud Text-to-Speech)")
    print("=" * 55)

    # Test: Simple Chirp 3: HD TTS
    print("\n1️⃣  Testing Simple Chirp 3: HD TTS")
    print("-" * 40)
    result = await test_chirp_tts_simple()

    return result


if __name__ == "__main__":
    result = asyncio.run(run_chirp_tests())

    if result:
        print("\n🎉 CHIRP 3: HD TEST PASSED!")
        print("🚀 Your Chirp 3: HD integration is working:")
        print("   ✅ Using Google Cloud Text-to-Speech")
        print("   ✅ Voice: en-US-Chirp3-HD-Charon")
        print("   ✅ No fallback needed")
        print("\n🎵 Check the generated MP3 file for audio quality!")
    else:
        print("\n⚠️  TEST FAILED")
        print("🔍 Check logs for details. Make sure:")
        print("   - Google Cloud credentials are configured")
        print("   - Text-to-Speech API is enabled")
        print("   - Voice name 'en-US-Chirp3-HD-Charon' is correct")
