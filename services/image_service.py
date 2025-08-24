import asyncio
import io
from typing import List, Optional
import vertexai
from vertexai.preview.vision_models import ImageGenerationModel
from loguru import logger
from config.settings import settings
from services.storage_service import storage_service


class ImageService:
    def __init__(self):
        # Hardcoded configuration - SDK uses GOOGLE_APPLICATION_CREDENTIALS automatically
        self.project_id = settings.vertex_ai_project_id
        self.seed = settings.imagen_seed
        self.model = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Vertex AI client with hardcoded configuration."""
        try:
            # Initialize Vertex AI with project and location
            vertexai.init(project=self.project_id, location="us-central1")
            
            # Load the Imagen 3 model
            self.model = ImageGenerationModel.from_pretrained("imagen-4.0-generate-001")
            logger.info("Image service initialized with Imagen 4.0")
            
        except Exception as e:
            logger.error(f"Failed to initialize image service: {e}")
            raise
    
    async def generate_image(self, prompt: str, panel_number: int) -> bytes:
        """Generate a single image using Imagen 4 API."""
        try:
            logger.info(f"Generating manga panel {panel_number} with typography")
            logger.info(f"Structured prompt preview: {prompt[:150]}...")
            
            # Generate image using Imagen 4.0 with typography support (run in thread)
            # Disable watermark to allow seed usage for character consistency
            response = await asyncio.to_thread(
                self.model.generate_images,
                prompt=prompt,
                number_of_images=1,
                aspect_ratio="1:1",  # Square aspect ratio for manga panels
                seed=self.seed,  # Use consistent seed for character consistency
                add_watermark=False  # Must disable watermark to use seed
            )
            
            # Access the images from the response
            if response and hasattr(response, 'images') and response.images:
                # Get the first (and only) generated image
                image = response.images[0]
                
                # Convert GeneratedImage to bytes using temporary file approach
                import tempfile
                import os
                import time
                
                # Create temp file and ensure it's closed before using it
                tmp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
                tmp_file_path = tmp_file.name
                tmp_file.close()  # Close the file handle immediately
                
                try:
                    # Save image to temp file
                    image.save(tmp_file_path)
                    
                    # Read the image data
                    with open(tmp_file_path, 'rb') as f:
                        image_data = f.read()
                        
                finally:
                    # Clean up temp file with retry for Windows
                    try:
                        os.unlink(tmp_file_path)
                    except PermissionError:
                        # Windows file lock issue - wait a bit and retry
                        time.sleep(0.1)
                        try:
                            os.unlink(tmp_file_path)
                        except:
                            logger.warning(f"Could not delete temp file {tmp_file_path}, but image data was retrieved successfully")
                
                logger.info(f"Image generated successfully for panel {panel_number} - {len(image_data)} bytes")
                return image_data
            else:
                raise Exception("No images generated")
                
        except Exception as e:
            logger.error(f"Failed to generate image for panel {panel_number}: {e}")
            raise
    
    async def generate_panel_images(self, panels: List[dict], story_id: str) -> List[str]:
        """Generate manga panels with dialogue typography and structured prompts in parallel."""
        try:
            from utils.helpers import create_structured_image_prompt
            
            async def generate_single_panel(panel: dict, panel_num: int) -> str:
                """Generate a single panel image and upload it."""
                logger.info(f"Generating manga panel {panel_num} with dialogue typography")
                
                # Create structured prompt with typography support
                structured_prompt = create_structured_image_prompt(panel)
                
                # Generate image with dialogue typography
                image_data = await self.generate_image(structured_prompt, panel_num)
                
                # Upload to GCS
                image_url = await storage_service.upload_image(image_data, story_id, panel_num)
                
                logger.info(f"Panel {panel_num} image uploaded: {image_url}")
                return image_url
            
            # Generate all panels in parallel
            tasks = [generate_single_panel(panel, i) for i, panel in enumerate(panels, 1)]
            image_urls = await asyncio.gather(*tasks)
            
            logger.info(f"All {len(image_urls)} manga panels generated with typography")
            return image_urls
            
        except Exception as e:
            logger.error(f"Failed to generate panel images: {e}")
            raise
    
    async def generate_single_panel(self, prompt: str, story_id: str, panel_number: int) -> str:
        """Generate a single panel image and upload to GCS."""
        try:
            image_data = await self.generate_image(prompt, panel_number)
            image_url = await storage_service.upload_image(image_data, story_id, panel_number)
            logger.info(f"Single panel {panel_number} generated and uploaded: {image_url}")
            return image_url
            
        except Exception as e:
            logger.error(f"Failed to generate single panel {panel_number}: {e}")
            raise
    
    async def retry_generation(self, prompt: str, panel_number: int, max_retries: int = 3) -> Optional[bytes]:
        """Retry image generation with exponential backoff."""
        for attempt in range(max_retries):
            try:
                logger.info(f"Attempt {attempt + 1} for panel {panel_number}")
                return await self.generate_image(prompt, panel_number)
                
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed for panel {panel_number}: {e}")
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"All {max_retries} attempts failed for panel {panel_number}")
                    return None
        
        return None


# Global image service instance
image_service = ImageService()
