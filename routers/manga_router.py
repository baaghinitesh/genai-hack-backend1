from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Dict, Any
from loguru import logger
from datetime import datetime

from models.schemas import (
    StoryInputs, 
    GeneratedStory, 
    StoryGenerationRequest, 
    StoryGenerationResponse,
    HealthResponse
)
from services.story_service import story_service
from services.image_service import image_service
from services.audio_service import audio_service
from services.storage_service import storage_service
from utils.helpers import create_timestamp, log_api_call

# Create router instance
router = APIRouter()


@router.post("/generate-manga", response_model=StoryGenerationResponse)
async def generate_manga_story(request: StoryGenerationRequest) -> StoryGenerationResponse:
    """
    Generate a complete 6-panel manga story for mental wellness.
    
    This endpoint orchestrates the complete pipeline:
    1. Story planning with Mangaka-Sensei
    2. Image generation with Imagen 4.0
    3. Audio generation with personalized voices (background music and TTS)
    4. Final delivery with separate audio files
    """
    try:
        logger.info(f"🎬 Manga generation request received for: {request.inputs.nickname}")
        log_api_call("/generate-manga", request.dict())
        
        # Validate inputs
        if not request.inputs.nickname or not request.inputs.mangaTitle:
            raise HTTPException(
                status_code=400, 
                detail="Nickname and manga title are required"
            )
        
        # Generate the complete story using the orchestrated workflow
        story = await story_service.generate_complete_story(request.inputs)
        
        if not story or story.status != "completed":
            raise HTTPException(
                status_code=500,
                detail="Story generation failed or incomplete"
            )
        
        # Create success response
        response = StoryGenerationResponse(
            story_id=story.story_id,
            status="completed",
            message=f"Manga story '{request.inputs.mangaTitle}' generated successfully!",
            story=story
        )
        
        logger.success(f"✅ Manga story generated: {story.story_id}")
        log_api_call("/generate-manga", request.dict(), response.dict())
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Manga generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Story generation failed: {str(e)}"
        )


@router.get("/story/{story_id}/status")
async def get_story_status(story_id: str) -> Dict[str, Any]:
    """Get the status of a story generation."""
    try:
        status = await story_service.get_story_status(story_id)
        return status
        
    except Exception as e:
        logger.error(f"Failed to get story status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get story status: {str(e)}"
        )


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint to verify all services are operational.
    
    Checks:
    - ChatVertexAI (Story generation)
    - Imagen 4.0 (Image generation) 
    - Google Cloud TTS (Voice generation)
    - Lyria-002 (Music generation)
    - Google Cloud Storage (Asset storage)
    """
    try:
        services_status = {}
        
        # Check Story service (ChatVertexAI)
        try:
            if story_service.llm is not None:
                services_status["story_service"] = "healthy"
            else:
                services_status["story_service"] = "unhealthy - LLM not initialized"
        except Exception as e:
            services_status["story_service"] = f"error - {str(e)}"
        
        # Check Image service (Imagen)
        try:
            if image_service.model is not None:
                services_status["image_service"] = "healthy"
            else:
                services_status["image_service"] = "unhealthy - Imagen not initialized"
        except Exception as e:
            services_status["image_service"] = f"error - {str(e)}"
        
        # Check Audio service (TTS + Lyria)
        try:
            if audio_service.tts_client is not None and audio_service.prediction_client is not None:
                services_status["audio_service"] = "healthy"
            else:
                services_status["audio_service"] = "unhealthy - Audio clients not initialized"
        except Exception as e:
            services_status["audio_service"] = f"error - {str(e)}"
        
        # Check Storage service (GCS)
        try:
            if storage_service.client is not None:
                services_status["storage_service"] = "healthy"
            else:
                services_status["storage_service"] = "unhealthy - GCS not initialized"
        except Exception as e:
            services_status["storage_service"] = f"error - {str(e)}"
        
        # Determine overall health
        all_healthy = all("healthy" in status for status in services_status.values())
        overall_status = "healthy" if all_healthy else "degraded"
        
        response = HealthResponse(
            status=overall_status,
            timestamp=create_timestamp(),
            services=services_status
        )
        
        logger.info(f"Health check completed: {overall_status}")
        return response
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Health check failed: {str(e)}"
        )


@router.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Manga Mental Wellness Backend API",
        "version": "1.0.0",
        "description": "Generate personalized 6-panel manga stories for youth mental wellness",
        "endpoints": {
            "generate_manga": "/generate-manga",
            "health": "/health",
            "story_status": "/story/{story_id}/status"
        },
        "features": [
            "Mangaka-Sensei AI storytelling",
            "Imagen 4.0 image generation",
            "Personalized voice selection (age/gender)",
            "Lyria-002 background music",
            "Separate background music and TTS audio files"
        ]
    }