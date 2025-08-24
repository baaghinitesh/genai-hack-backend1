import os
import asyncio
from typing import Optional, List
from google.cloud import storage
from google.auth import default
from loguru import logger
from config.settings import settings


class StorageService:
    def __init__(self):
        self.bucket_name = settings.gcs_bucket_name
        self.client = None
        self.bucket = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Google Cloud Storage client with hardcoded configuration."""
        try:
            # SDK uses GOOGLE_APPLICATION_CREDENTIALS environment variable automatically
            self.client = storage.Client()
            self.bucket = self.client.bucket(self.bucket_name)
            
            # Ensure bucket exists
            if not self.bucket.exists():
                logger.warning(f"Bucket {self.bucket_name} does not exist. Creating...")
                self.bucket = self.client.create_bucket(self.bucket_name)
            
            logger.info(f"Storage service initialized with bucket: {self.bucket_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize storage service: {e}")
            raise
    
    async def upload_file(self, file_path: str, destination_blob_name: str) -> str:
        """Upload a file to GCS and return the public URL."""
        try:
            blob = self.bucket.blob(destination_blob_name)
            
            # Upload the file
            blob.upload_from_filename(file_path)
            
            # With uniform bucket-level access, we don't need to make individual blobs public
            # The bucket-level permissions handle access control
            
            # Return the public URL
            url = f"https://storage.googleapis.com/{self.bucket_name}/{destination_blob_name}"
            logger.info(f"File uploaded successfully: {url}")
            
            return url
            
        except Exception as e:
            logger.error(f"Failed to upload file {file_path}: {e}")
            raise
    
    async def upload_bytes(self, data: bytes, destination_blob_name: str, content_type: str = "application/octet-stream") -> str:
        """Upload bytes data to GCS and return the public URL."""
        try:
            blob = self.bucket.blob(destination_blob_name)
            blob.content_type = content_type
            
            # Upload the bytes
            blob.upload_from_string(data, content_type=content_type)
            
            # With uniform bucket-level access, we don't need to make individual blobs public
            # The bucket-level permissions handle access control
            
            # Return the public URL
            url = f"https://storage.googleapis.com/{self.bucket_name}/{destination_blob_name}"
            logger.info(f"Bytes uploaded successfully: {url}")
            
            return url
            
        except Exception as e:
            logger.error(f"Failed to upload bytes to {destination_blob_name}: {e}")
            raise
    
    async def upload_image(self, image_data: bytes, story_id: str, panel_number: int) -> str:
        """Upload an image for a specific story panel."""
        filename = f"stories/{story_id}/panel_{panel_number:02d}.png"
        return await self.upload_bytes(image_data, filename, "image/png")
    
    async def upload_audio(self, audio_data: bytes, story_id: str, audio_type: str = "final") -> str:
        """Upload audio file for a story."""
        filename = f"stories/{story_id}/{audio_type}_audio.mp3"
        return await self.upload_bytes(audio_data, filename, "audio/mpeg")
    
    async def upload_background_music(self, music_data: bytes, story_id: str, panel_number: int) -> str:
        """Upload background music for a specific panel."""
        filename = f"stories/{story_id}/music_panel_{panel_number:02d}.mp3"
        return await self.upload_bytes(music_data, filename, "audio/mpeg")
    
    async def upload_tts_audio(self, tts_data: bytes, story_id: str, panel_number: int) -> str:
        """Upload TTS audio for a specific panel."""
        filename = f"stories/{story_id}/tts_panel_{panel_number:02d}.mp3"
        return await self.upload_bytes(tts_data, filename, "audio/mpeg")
    
    async def delete_story_assets(self, story_id: str):
        """Delete all assets for a specific story."""
        try:
            blobs = self.client.list_blobs(self.bucket_name, prefix=f"stories/{story_id}/")
            
            for blob in blobs:
                blob.delete()
                logger.info(f"Deleted blob: {blob.name}")
            
            logger.info(f"Deleted all assets for story: {story_id}")
            
        except Exception as e:
            logger.error(f"Failed to delete story assets for {story_id}: {e}")
            raise
    
    async def get_story_assets(self, story_id: str) -> List[str]:
        """Get all asset URLs for a specific story."""
        try:
            blobs = self.client.list_blobs(self.bucket_name, prefix=f"stories/{story_id}/")
            urls = []
            
            for blob in blobs:
                url = f"https://storage.googleapis.com/{self.bucket_name}/{blob.name}"
                urls.append(url)
            
            return urls
            
        except Exception as e:
            logger.error(f"Failed to get story assets for {story_id}: {e}")
            raise
    
    async def check_bucket_access(self) -> bool:
        """Check if we have access to the GCS bucket."""
        try:
            # Try to list blobs to test access
            blobs = list(self.client.list_blobs(self.bucket_name, max_results=1))
            return True
        except Exception as e:
            logger.error(f"Bucket access check failed: {e}")
            return False


# Global storage service instance
storage_service = StorageService()
