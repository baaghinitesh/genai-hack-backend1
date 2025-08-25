from datetime import datetime
from typing import List, Literal, Dict, Any
from pydantic import BaseModel, Field
import uuid


class StoryInputs(BaseModel):
    mood: Literal['happy', 'stressed', 'neutral', 'frustrated', 'sad']
    vibe: Literal['calm', 'adventure', 'musical', 'motivational']
    archetype: Literal['mentor', 'hero', 'companion', 'comedian']
    dream: str = Field(..., min_length=1, max_length=500)
    mangaTitle: str = Field(..., min_length=1, max_length=100)
    nickname: str = Field(..., min_length=1, max_length=50)
    hobby: str = Field(..., min_length=1, max_length=100)
    age: int = Field(..., ge=10, le=35, description="User age for voice selection")
    gender: Literal['male', 'female', 'non-binary', 'prefer-not-to-say']


class CharacterSheet(BaseModel):
    name: str
    age: str
    appearance: str
    personality: str
    goals: str
    fears: str
    strengths: str


class PropSheet(BaseModel):
    items: List[str]
    environment: str
    lighting: str
    mood_elements: List[str]


class StyleGuide(BaseModel):
    art_style: str
    color_palette: str
    panel_layout: str
    visual_elements: List[str]


class PanelData(BaseModel):
    panel_number: int
    character_sheet: CharacterSheet
    prop_sheet: PropSheet
    style_guide: StyleGuide
    dialogue_text: str
    image_prompt: str
    music_prompt: str
    emotional_tone: str


class GeneratedStory(BaseModel):
    story_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    panels: List[PanelData]
    image_urls: List[str] = Field(default_factory=list)  # GCS URLs
    audio_url: str = ""  # Audio URL (separate background music and TTS files available)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "pending"


class StoryGenerationRequest(BaseModel):
    inputs: StoryInputs


class StoryGenerationResponse(BaseModel):
    story_id: str
    status: str
    message: str
    story: GeneratedStory = None


class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    services: Dict[str, str]
