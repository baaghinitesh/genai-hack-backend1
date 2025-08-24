import json
import uuid
from datetime import datetime, UTC
from typing import Dict, Any, List
from loguru import logger


# Mangaka-Sensei System Prompt
MANGAKA_SENSEI_PROMPT = """
You are Mangaka-Sensei, an expert storyteller and manga artist AI. Your purpose is to transform a user's real-life feelings and experiences into a powerful, metaphorical, 6-panel manga story for mental wellness.

Core Mission: To craft a visually and emotionally resonant shōnen-style manga narrative that transforms the user's current emotional state into an optimistic, growth-oriented journey. Each panel should be a stepping stone toward emotional resilience and self-discovery.

Story Structure Requirements:
- Panel 1: Introduction - Establish the character and their current emotional state
- Panel 2: Challenge - Present the emotional obstacle or stressor
- Panel 3: Reflection - Character begins to process and understand their feelings
- Panel 4: Discovery - Character finds inner strength or support
- Panel 5: Transformation - Character takes positive action or gains new perspective
- Panel 6: Resolution - Character emerges stronger, with hope for the future

Character Development:
- Create a relatable protagonist based on the user's inputs
- Ensure character consistency across all panels
- Show emotional growth and resilience
- Use the user's nickname, age, and interests to personalize the character

Visual Style Guidelines:
- Shōnen manga aesthetic with clean, expressive art
- Emotional facial expressions and body language
- Dynamic panel compositions
- Consistent character design throughout
- Use lighting and color to convey emotional states

Content Guidelines:
- Always maintain an optimistic, uplifting tone
- Focus on emotional growth and resilience
- Include metaphorical elements that relate to mental wellness
- Ensure age-appropriate content for youth
- Avoid triggering or negative themes
- Emphasize hope, friendship, and personal strength

Output Format:
You must structure your response exactly as follows:

CHARACTER_SHEET:
{
  "name": "Character Name",
  "age": "Character Age",
  "appearance": "Detailed physical description",
  "personality": "Character traits and behaviors",
  "goals": "What the character wants to achieve",
  "fears": "What the character is afraid of",
  "strengths": "Character's positive qualities"
}

PROP_SHEET:
{
  "items": ["item1", "item2", "item3"],
  "environment": "Setting description",
  "lighting": "Lighting mood and style",
  "mood_elements": ["element1", "element2"]
}

STYLE_GUIDE:
{
  "art_style": "Detailed art style description",
  "color_palette": "Color scheme and mood",
  "panel_layout": "Layout style for panels",
  "visual_elements": ["element1", "element2", "element3"]
}

PANEL_1:
dialogue_text: "Character dialogue and narration for panel 1"
image_prompt: "Detailed image generation prompt for panel 1"
music_prompt: "Music description for panel 1 emotional tone"

PANEL_2:
dialogue_text: "Character dialogue and narration for panel 2"
image_prompt: "Detailed image generation prompt for panel 2"
music_prompt: "Music description for panel 2 emotional tone"

PANEL_3:
dialogue_text: "Character dialogue and narration for panel 3"
image_prompt: "Detailed image generation prompt for panel 3"
music_prompt: "Music description for panel 3 emotional tone"

PANEL_4:
dialogue_text: "Character dialogue and narration for panel 4"
image_prompt: "Detailed image generation prompt for panel 4"
music_prompt: "Music description for panel 4 emotional tone"

PANEL_5:
dialogue_text: "Character dialogue and narration for panel 5"
image_prompt: "Detailed image generation prompt for panel 5"
music_prompt: "Music description for panel 5 emotional tone"

PANEL_6:
dialogue_text: "Character dialogue and narration for panel 6"
image_prompt: "Detailed image generation prompt for panel 6"
music_prompt: "Music description for panel 6 emotional tone"

Remember: Every story should end with hope, growth, and the message that challenges make us stronger. Focus on emotional resilience and the power of self-discovery.
"""


def generate_story_id() -> str:
    """Generate a unique story ID."""
    return str(uuid.uuid4())


def create_timestamp() -> str:
    """Create a formatted timestamp."""
    return datetime.now(UTC).isoformat()


def log_api_call(endpoint: str, request_data: Dict[str, Any], response_data: Dict[str, Any] = None):
    """Log API calls with timestamps."""
    logger.info(f"API Call - {endpoint} - {create_timestamp()}")
    logger.debug(f"Request: {json.dumps(request_data, indent=2)}")
    if response_data:
        logger.debug(f"Response: {json.dumps(response_data, indent=2)}")


def validate_story_consistency(panels: List[Dict[str, Any]]) -> bool:
    """Validate character consistency across panels."""
    if not panels or len(panels) != 6:
        return False
    
    # Check if character name is consistent
    character_names = set()
    for panel in panels:
        if 'character_sheet' in panel and 'name' in panel['character_sheet']:
            character_names.add(panel['character_sheet']['name'])
    
    return len(character_names) == 1


def create_structured_image_prompt(panel_data: Dict[str, Any]) -> str:
    """Create structured image generation prompt with dialogue typography support."""
    character = panel_data.get('character_sheet', {})
    props = panel_data.get('prop_sheet', {})
    style = panel_data.get('style_guide', {})
    dialogue = panel_data.get('dialogue_text', '')
    
    # Extract character details
    char_name = character.get('name', 'Character')
    char_appearance = character.get('appearance', 'anime character with expressive eyes')
    char_clothing = character.get('clothing', 'casual modern outfit')
    
    # Extract prop details
    main_item = props.get('items', ['symbolic item'])[0] if props.get('items') else 'symbolic item'
    item_description = f"a {main_item} that represents {character.get('goals', 'hope')}"
    
    # Extract style details
    art_style = style.get('art_style', 'shonen manga style')
    visual_details = style.get('visual_elements', ['dynamic composition', 'emotional expression'])
    
    # Create structured prompt
    structured_prompt = f"""CHARACTER_SHEET(
  character_name: {char_name},
  appearance: {char_appearance},
  clothing: {char_clothing}
),

PROP_SHEET(
  item: {main_item},
  description: {item_description}
),

STYLE_GUIDE(
  art_style: masterpiece, {art_style},
  details: strong dynamic ink lines, detailed cross-hatching for shadows, high-contrast lighting, expressive faces, shōnen manga aesthetic,
  framing: cinematic composition,
  negative_prompt: (color, text, signature, watermark, blurry, bad anatomy, ugly, deformed)
)

DIALOGUE: "{dialogue}" """

    return structured_prompt.strip()

def get_manga_style_by_mood(mood: str, vibe: str) -> str:
    """Map user mood and vibe to famous manga art styles."""
    
    manga_styles = {
        # Action/Adventure styles
        ("frustrated", "adventure"): "Attack on Titan by Hajime Isayama - intense action scenes with dramatic perspectives",
        ("stressed", "motivational"): "Demon Slayer (Kimetsu no Yaiba) by Koyoharu Gotouge - dynamic sword action with determination",
        ("neutral", "adventure"): "My Hero Academia by Kohei Horikoshi - heroic poses with modern superhero aesthetic",
        
        # Emotional/Calm styles  
        ("sad", "calm"): "Your Name (Kimi no Na wa) by Makoto Shinkai - emotional, soft lighting with gentle expressions",
        ("happy", "calm"): "Studio Ghibli style by Hayao Miyazaki - warm, peaceful scenes with natural beauty",
        ("neutral", "calm"): "Violet Evergarden by Akiko Takase - elegant, detailed character art with soft atmosphere",
        
        # Intense/Dark styles
        ("frustrated", "motivational"): "Jujutsu Kaisen by Gege Akutami - intense battle scenes with supernatural elements",
        ("stressed", "adventure"): "Tokyo Ghoul by Sui Ishida - dark, psychological thriller aesthetic with dramatic shadows",
        
        # Musical/Creative styles
        ("happy", "musical"): "Your Lie in April by Arakawa Naoshi - music-themed scenes with emotional performance moments",
        ("neutral", "musical"): "Beck: Mongolian Chop Squad by Harold Sakuishi - rock music aesthetic with urban settings",
        
        # Motivational styles
        ("sad", "motivational"): "Naruto by Masashi Kishimoto - underdog determination with inspiring character growth",
        ("happy", "motivational"): "Haikyuu!! by Haruichi Furudate - sports motivation with dynamic team spirit",
    }
    
    # Get specific style or fallback to general mood mapping
    style_key = (mood, vibe)
    if style_key in manga_styles:
        return manga_styles[style_key]
    
    # Fallback by mood only
    mood_fallbacks = {
        "happy": "Studio Ghibli style - warm, joyful expressions with bright atmosphere",
        "stressed": "Demon Slayer style - intense emotion with determination and resolve", 
        "frustrated": "Jujutsu Kaisen style - powerful expressions with dynamic action lines",
        "sad": "Your Name style - emotional depth with gentle, melancholic beauty",
        "neutral": "My Hero Academia style - balanced, heroic character design"
    }
    
    return mood_fallbacks.get(mood, "classic shonen manga style with expressive characters")

def create_image_prompt(panel_data: Dict[str, Any]) -> str:
    """Legacy function - redirects to structured prompt."""
    return create_structured_image_prompt(panel_data)


def create_music_prompt(panel_data: Dict[str, Any], emotional_tone: str) -> str:
    """Create music generation prompt for panel emotional tone."""
    return f"Generate a {emotional_tone}-toned ambient track for a manga panel. Duration: 15-20 seconds. Emotional and atmospheric background music."


def format_error_response(error: str, details: str = None) -> Dict[str, Any]:
    """Format error response for API."""
    return {
        "error": error,
        "details": details,
        "timestamp": create_timestamp()
    }
