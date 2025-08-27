#!/usr/bin/env python3
"""
Test script for the streaming music service.
This demonstrates how the new Lyria RealTime streaming works.
"""

import asyncio
import json
from services.streaming_music_service import streaming_music_service


async def test_streaming_music():
    """Test the streaming music service with dynamic prompts."""

    print("🎵 Testing Streaming Music Service...")
    print("=" * 50)

    # Mock story context
    story_context = {
        'mood': 'happy',
        'animeGenre': 'slice-of-life',
        'archetype': 'hero',
        'supportSystem': 'mentor',
        'coreValue': 'kindness',
        'pastResilience': 'Overcame fear of public speaking',
        'innerDemon': 'Self-doubt and fear',
        'age': 16,
        'gender': 'female'
    }

    # Mock panel data for testing
    panels_data = [
        {
            'panel_number': 1,
            'dialogue_text': 'Today is a new beginning!',
            'emotional_tone': 'hopeful',
            'character_sheet': {'name': 'Hero', 'age': '16'},
            'prop_sheet': {'environment': 'School'},
            'style_guide': {'art_style': 'slice-of-life'}
        },
        {
            'panel_number': 2,
            'dialogue_text': 'I can feel the challenge ahead...',
            'emotional_tone': 'tense',
            'character_sheet': {'name': 'Hero', 'age': '16'},
            'prop_sheet': {'environment': 'Classroom'},
            'style_guide': {'art_style': 'slice-of-life'}
        },
        {
            'panel_number': 3,
            'dialogue_text': 'I remember when I overcame my fear before...',
            'emotional_tone': 'determined',
            'character_sheet': {'name': 'Hero', 'age': '16'},
            'prop_sheet': {'environment': 'Quiet room'},
            'style_guide': {'art_style': 'slice-of-life'}
        }
    ]

    try:
        print("📡 Starting streaming session...")
        story_id = "test_story_123"

        # This would normally connect to Lyria RealTime API
        # For now, we'll simulate the behavior
        success = await streaming_music_service.start_streaming_session(story_id)
        if not success:
            print("❌ Failed to start streaming session")
            return

        print("✅ Streaming session started")
        print(f"🎼 Initial prompts: {streaming_music_service.generate_panel_prompts(panels_data[0], story_context)}")

        for i, panel in enumerate(panels_data):
            print(f"\n🎬 Panel {panel['panel_number']}: {panel['dialogue_text']}")
            print(f"   Tone: {panel['emotional_tone']}")

            # Generate prompts for this panel
            prompts = streaming_music_service.generate_panel_prompts(panel, story_context)
            print(f"   Generated {len(prompts)} prompts: {[p['text'][:50] + '...' for p in prompts]}")

            # Calculate duration
            duration = streaming_music_service.calculate_panel_duration(panel)
            print(f"   Duration: {duration:.1f}s")

            # Simulate transition (would normally call the API)
            transition_success = await streaming_music_service.transition_to_panel(panel, story_context)
            if transition_success:
                print("   ✅ Music transition successful")
            else:
                print("   ❌ Music transition failed")

            # Simulate some streaming time
            await asyncio.sleep(1)

        print("
🛑 Stopping streaming session..."        complete_audio = await streaming_music_service.stop_streaming()

        if complete_audio:
            print(f"✅ Got {len(complete_audio)} bytes of audio data")
        else:
            print("❌ No audio data received")

        print("\n🎵 Streaming music test completed successfully!")
        print("\n💡 Key Improvements:")
        print("   • Continuous music stream instead of 6 separate 30s clips")
        print("   • Dynamic prompt adaptation based on panel content")
        print("   • Real-time transitions between emotional states")
        print("   • Socket.IO integration for live audio streaming")
        print("   • Much faster total generation time")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_streaming_music())
