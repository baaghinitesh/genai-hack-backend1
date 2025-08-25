#!/usr/bin/env python3
"""
Test script to check existing story assets and orchestrate completion.
"""

import asyncio
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from services.storage_service import storage_service
from services.audio_service import audio_service
from google.cloud import storage
from loguru import logger

async def check_story_assets(story_id: str):
    """Check what assets exist for a given story ID."""
    try:
        logger.info(f"🔍 Checking assets for {story_id}")
        
        # Initialize storage client
        client = storage.Client()
        bucket = client.bucket("calmira-backend")
        
        # List all blobs with the story prefix
        story_prefix = f"stories/{story_id}/"
        blobs = list(bucket.list_blobs(prefix=story_prefix))
        
        # Categorize assets
        images = []
        music = []
        tts = []
        final_audio = []
        
        for blob in blobs:
            name = blob.name
            if "panel_" in name and name.endswith('.png'):
                images.append(name)
            elif "music_panel_" in name and name.endswith('.mp3'):
                music.append(name)
            elif "tts_panel_" in name and name.endswith('.mp3'):
                tts.append(name)
            elif "final_audio" in name and name.endswith('.mp3'):
                final_audio.append(name)
        
        # Sort by panel number
        images.sort()
        music.sort()
        tts.sort()
        
        logger.info(f"📊 Asset Summary for {story_id}:")
        logger.info(f"  Images: {len(images)}/6 panels")
        for img in images:
            panel_num = img.split('_')[1].split('.')[0]
            logger.info(f"    ✅ Panel {panel_num}: {img}")
        
        logger.info(f"  Music: {len(music)}/6 panels")
        for mus in music:
            panel_num = mus.split('_')[2].split('.')[0]
            logger.info(f"    🎵 Panel {panel_num}: {mus}")
            
        logger.info(f"  TTS: {len(tts)}/6 panels")
        for voice in tts:
            panel_num = voice.split('_')[2].split('.')[0]
            logger.info(f"    🎤 Panel {panel_num}: {voice}")
            
        logger.info(f"  Final Audio: {len(final_audio)} files")
        for audio in final_audio:
            logger.info(f"    🎶 Final: {audio}")
        
        # Check for missing assets
        missing_images = []
        missing_music = []
        missing_tts = []
        
        for i in range(1, 7):
            panel_str = f"{i:02d}"
            
            # Check images
            if not any(f"panel_{panel_str}" in img for img in images):
                missing_images.append(f"panel_{panel_str}.png")
                
            # Check music
            if not any(f"music_panel_{panel_str}" in mus for mus in music):
                missing_music.append(f"music_panel_{panel_str}.mp3")
                
            # Check TTS
            if not any(f"tts_panel_{panel_str}" in voice for voice in tts):
                missing_tts.append(f"tts_panel_{panel_str}.mp3")
        
        if missing_images:
            logger.warning(f"❌ Missing Images: {missing_images}")
        if missing_music:
            logger.warning(f"❌ Missing Music: {missing_music}")
        if missing_tts:
            logger.warning(f"❌ Missing TTS: {missing_tts}")
            
        # Return asset URLs (no synchronization)
        base_url = "https://storage.googleapis.com/calmira-backend/"
        asset_data = {
            "story_id": story_id,
            "image_urls": [f"{base_url}{img}" for img in images],
            "music_urls": [f"{base_url}{mus}" for mus in music],
            "tts_urls": [f"{base_url}{voice}" for voice in tts],
            "missing": {
                "images": missing_images,
                "music": missing_music,
                "tts": missing_tts
            }
        }
        
        return asset_data
        
    except Exception as e:
        logger.error(f"Failed to check story assets: {e}")
        raise



async def main():
    """Main test function."""
    try:
        # Test with multiple story IDs
        story_ids = ["story_884416", "story_885418"]
        
        for story_id in story_ids:
            logger.info(f"\n{'='*50}")
            logger.info(f"Testing Story: {story_id}")
            logger.info(f"{'='*50}")
            
            # Check assets
            assets = await check_story_assets(story_id)
            
            # Log asset status
            if len(assets["music_urls"]) >= 3 and len(assets["tts_urls"]) >= 3:
                logger.info(f"📦 Sufficient assets found for {story_id}")
                logger.info(f"🎵 Music files: {len(assets['music_urls'])}")
                logger.info(f"🗣️ TTS files: {len(assets['tts_urls'])}")
                logger.info(f"🖼️ Image files: {len(assets['image_urls'])}")
                return story_id, assets, None
            else:
                logger.warning(f"⚠️ Insufficient assets for {story_id}")
        
        logger.warning("❌ No stories with sufficient assets found")
        return None, None, None
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
