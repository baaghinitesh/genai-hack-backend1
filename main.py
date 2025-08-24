import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
import sys

from config.settings import settings
from routers.manga_router import router as manga_router


# Configure logging
def setup_logging():
    """Configure loguru logging."""
    logger.remove()  # Remove default handler
    
    # Add console handler with custom format
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO" if not settings.debug else "DEBUG",
        colorize=True
    )
    
    # Add file handler for production
    logger.add(
        "logs/manga_wellness.log",
        rotation="10 MB",
        retention="7 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="INFO"
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Manga Wellness Backend...")
    setup_logging()
    
    # Initialize services
    try:
        from services.storage_service import storage_service
        from services.story_service import story_service
        from services.image_service import image_service
        from services.audio_service import audio_service
        
        # Test service connections
        storage_healthy = await storage_service.check_bucket_access()
        if not storage_healthy:
            logger.warning("Storage service connection failed")
        
        logger.info("All services initialized successfully")
        
    except Exception as e:
        logger.error(f"Service initialization failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Manga Wellness Backend...")


# Create FastAPI app
app = FastAPI(
    title="Manga Mental Wellness Backend",
    description="A mental wellness platform that generates personalized 6-panel manga stories for youth",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(manga_router, prefix="/api/v1")


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "details": "An unexpected error occurred",
            "timestamp": asyncio.get_event_loop().time()
        }
    )


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Manga Mental Wellness Backend",
        "version": "1.0.0",
        "description": "Generate personalized manga stories for mental wellness",
        "endpoints": {
            "docs": "/docs",
            "health": "/api/v1/health",
            "generate_manga": "/api/v1/generate-manga"
        }
    }


# Health check endpoint (simple)
@app.get("/health")
async def simple_health():
    """Simple health check endpoint."""
    return {"status": "healthy", "service": "manga-wellness-backend"}


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting server on {settings.api_host}:{settings.api_port}")
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level="info"
    )
