"""
Socket.IO utility functions for story generation progress updates.
"""
from typing import Dict, Any
from loguru import logger

# Global storage for active story generation sessions
active_generations = {}


async def emit_generation_progress(story_id: str, event_type: str, data: dict):
    """
    Emit progress updates for story generation via Socket.IO.

    Args:
        story_id: Unique identifier for the story generation session
        event_type: Type of progress event (e.g., 'panel_ready', 'image_generation_start')
        data: Event-specific data payload
    """
    try:
        # Import here to avoid circular imports
        from main import sio

        event_data = {
            'story_id': story_id,
            'event_type': event_type,
            'data': data,
            'timestamp': data.get('timestamp', None)
        }

        # Emit to specific room (story session)
        await sio.emit(event_type, event_data, room=story_id)

        # Also emit to general progress room for debugging
        await sio.emit('generation_progress', event_data, room='progress_updates')

        logger.info(f"📡 Emitted {event_type} for story {story_id}")

    except Exception as e:
        logger.error(f"❌ Failed to emit progress for story {story_id}: {e}")
        # Don't raise - we don't want progress emission failures to break generation


def add_active_generation(story_id: str, session_data: Dict[str, Any]):
    """Add an active generation session."""
    active_generations[story_id] = session_data
    logger.info(f"📝 Started tracking generation for story {story_id}")


def get_active_generation(story_id: str) -> Dict[str, Any]:
    """Get data for an active generation session."""
    return active_generations.get(story_id, {})


def remove_active_generation(story_id: str):
    """Remove a completed generation session."""
    if story_id in active_generations:
        del active_generations[story_id]
        logger.info(f"🗑️ Stopped tracking generation for story {story_id}")


def get_all_active_generations() -> Dict[str, Any]:
    """Get all active generation sessions."""
    return active_generations.copy()
