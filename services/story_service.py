import asyncio
import json
import re
from typing import List, Dict, Any, Optional
from langchain_google_vertexai import ChatVertexAI
from langchain.prompts import PromptTemplate
from loguru import logger
from config.settings import settings
from models.schemas import StoryInputs, GeneratedStory, PanelData
from utils.helpers import MANGAKA_SENSEI_PROMPT, validate_story_consistency, create_structured_image_prompt, get_manga_style_by_mood
from services.image_service import image_service
from services.audio_service import audio_service
from services.storage_service import storage_service


class StoryService:
    def __init__(self):
        self.llm = None
        self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize ChatVertexAI LLM with hardcoded configuration."""
        try:
            # Hardcoded configuration - SDK uses GOOGLE_APPLICATION_CREDENTIALS automatically
            self.llm = ChatVertexAI(
                model_name=settings.model_name,
                project=settings.vertex_ai_project_id,
                temperature=0.7,
                max_output_tokens=8192
            )
            logger.info("Story service ChatVertexAI initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize story service LLM: {e}")
            raise
    
    async def generate_story_plan(self, inputs: StoryInputs) -> List[Dict[str, Any]]:
        """Generate the complete 6-panel story plan using Mangaka-Sensei."""
        try:
            # Fallback if LLM is not initialized (hackathon-safe default)
            if self.llm is None:
                logger.warning("LLM not initialized; using fallback story plan")
                return self._create_fallback_panels()

            # Create the input context for the LLM
            input_context = f"""
            User Inputs:
            - Mood: {inputs.mood}
            - Vibe: {inputs.vibe}
            - Archetype: {inputs.archetype}
            - Dream: {inputs.dream}
            - Manga Title: {inputs.mangaTitle}
            - Nickname: {inputs.nickname}
            - Hobby: {inputs.hobby}
            - Age: {inputs.age}
            - Gender: {inputs.gender}
            
            Please create a complete 6-panel manga story following the Mangaka-Sensei guidelines.
            """
            
            # Combine system prompt with user inputs
            full_prompt = MANGAKA_SENSEI_PROMPT + "\n\n" + input_context
            
            logger.info("Generating story plan with Mangaka-Sensei")
            
            # Generate the story using ChatVertexAI
            response = await asyncio.to_thread(self.llm.invoke, full_prompt)
            
            # Extract content from ChatVertexAI response
            if hasattr(response, 'content'):
                response_text = response.content
            else:
                response_text = str(response)
            
            # Parse the response into structured data  
            panels = self._parse_story_response(response_text, inputs)
            
            # Validate consistency
            if not validate_story_consistency(panels):
                logger.warning("Story consistency validation failed, regenerating...")
                return await self.generate_story_plan(inputs)
            
            logger.info("Story plan generated successfully")
            return panels
            
        except Exception as e:
            logger.error(f"Failed to generate story plan: {e}")
            raise
    
    def _parse_story_response(self, response: str, inputs: StoryInputs = None) -> List[Dict[str, Any]]:
        """Parse the LLM response into structured panel data."""
        try:
            panels = []
            
            # Extract character sheet
            character_match = re.search(r'CHARACTER_SHEET:\s*({.*?})', response, re.DOTALL)
            character_sheet = json.loads(character_match.group(1)) if character_match else {}
            
            # Extract prop sheet
            prop_match = re.search(r'PROP_SHEET:\s*({.*?})', response, re.DOTALL)
            prop_sheet = json.loads(prop_match.group(1)) if prop_match else {}
            
            # Extract style guide
            style_match = re.search(r'STYLE_GUIDE:\s*({.*?})', response, re.DOTALL)
            style_guide = json.loads(style_match.group(1)) if style_match else {}
            
            # Extract each panel
            for i in range(1, 7):
                panel_pattern = rf'PANEL_{i}:\s*dialogue_text:\s*"([^"]*)"\s*image_prompt:\s*"([^"]*)"\s*music_prompt:\s*"([^"]*)"'
                panel_match = re.search(panel_pattern, response, re.DOTALL)
                
                if panel_match:
                    panel_data = {
                        'panel_number': i,
                        'character_sheet': character_sheet,
                        'prop_sheet': prop_sheet,
                        'style_guide': style_guide,
                        'dialogue_text': panel_match.group(1),
                        'image_prompt': panel_match.group(2),
                        'music_prompt': panel_match.group(3),
                        'emotional_tone': self._determine_emotional_tone(i, panel_match.group(1))
                    }
                    panels.append(panel_data)
                else:
                    # Fallback if parsing fails
                    panel_data = {
                        'panel_number': i,
                        'character_sheet': character_sheet,
                        'prop_sheet': prop_sheet,
                        'style_guide': style_guide,
                        'dialogue_text': f"Panel {i} dialogue",
                        'image_prompt': f"Manga panel {i} illustration",
                        'music_prompt': f"Emotional music for panel {i}",
                        'emotional_tone': 'neutral'
                    }
                    panels.append(panel_data)
            
            return panels
            
        except Exception as e:
            logger.error(f"Failed to parse story response: {e}")
            # Return fallback panels with user context
            return self._create_fallback_panels(inputs)
    
    def _determine_emotional_tone(self, panel_number: int, dialogue: str) -> str:
        """Determine emotional tone based on panel number and dialogue."""
        emotional_arc = {
            1: 'neutral',      # Introduction
            2: 'tense',        # Challenge
            3: 'contemplative', # Reflection
            4: 'hopeful',      # Discovery
            5: 'determined',   # Transformation
            6: 'uplifting'     # Resolution
        }
        return emotional_arc.get(panel_number, 'neutral')
    
    def _create_fallback_panels(self, inputs: StoryInputs = None) -> List[Dict[str, Any]]:
        """Create fallback panels with manga style mapping."""
        panels = []
        
        # Get manga style based on user mood/vibe
        manga_style = "classic shonen manga style"
        if inputs:
            manga_style = get_manga_style_by_mood(inputs.mood, inputs.vibe)
        
        for i in range(1, 7):
            panel_data = {
                'panel_number': i,
                'character_sheet': {
                    'name': inputs.nickname if inputs else 'Hero',
                    'age': str(inputs.age) if inputs else 'young',
                    'appearance': f"determined {inputs.gender if inputs else 'person'} with expressive eyes and {inputs.hobby if inputs else 'creative'} aesthetic",
                    'clothing': 'modern casual outfit that reflects their personality',
                    'personality': 'determined and hopeful',
                    'goals': inputs.dream if inputs else 'overcome challenges',
                    'fears': f'struggles with {inputs.mood if inputs else "uncertainty"}',
                    'strengths': 'inner resilience and creativity'
                },
                'prop_sheet': {
                    'items': [inputs.hobby if inputs else 'symbolic item', 'meaningful object'],
                    'environment': f'{inputs.vibe if inputs else "inspiring"} setting that supports growth',
                    'lighting': 'dynamic lighting that conveys emotional state',
                    'mood_elements': [inputs.vibe if inputs else 'hope', 'growth', 'determination']
                },
                'style_guide': {
                    'art_style': manga_style,
                    'visual_elements': ['dynamic composition', 'emotional expression', 'typography dialogue'],
                    'framing': 'cinematic manga panel composition',
                    'details': 'strong ink lines, detailed cross-hatching, high contrast'
                },
                'dialogue_text': f"Panel {i}: The journey of {inputs.nickname if inputs else 'our hero'} continues with {inputs.hobby if inputs else 'determination'}...",
                'image_prompt': f"Manga panel showing character's emotional journey in {manga_style}",
                'music_prompt': f"Emotional {inputs.vibe if inputs else 'inspiring'} music for panel {i}",
                'emotional_tone': self._determine_emotional_tone(i, '')
            }
            panels.append(panel_data)
        return panels
    
    async def generate_complete_story(self, inputs: StoryInputs) -> GeneratedStory:
        """Generate a complete story with images and audio."""
        try:
            story_id = f"story_{asyncio.get_event_loop().time():.0f}"
            logger.info(f"Starting story generation for ID: {story_id}")
            
            # Step 1: Generate story plan
            panels = await self.generate_story_plan(inputs)
            
            # Step 2: Generate images (async)
            image_task = asyncio.create_task(
                image_service.generate_panel_images(panels, story_id)
            )
            
            # Step 3: Generate audio with personalized voices (async)  
            # Convert age string to int if needed for voice selection
            user_age = inputs.age if isinstance(inputs.age, int) else 16  # Default fallback
            audio_task = asyncio.create_task(
                audio_service.generate_all_audio(panels, story_id, user_age, inputs.gender)
            )
            
            # Wait for both tasks to complete
            image_urls, (background_urls, tts_urls) = await asyncio.gather(
                image_task, audio_task
            )
            
            # Step 4: Synchronize audio
            final_audio_url = await audio_service.synchronize_audio(
                background_urls, tts_urls, story_id
            )
            
            # Step 5: Create final story object
            story = GeneratedStory(
                story_id=story_id,
                panels=panels,
                image_urls=image_urls,
                audio_url=final_audio_url,
                status="completed"
            )
            
            logger.info(f"Story generation completed: {story_id}")
            return story
            
        except Exception as e:
            logger.error(f"Failed to generate complete story: {e}")
            raise
    
    async def get_story_status(self, story_id: str) -> Dict[str, Any]:
        """Get the status of a story generation."""
        try:
            # Check if assets exist in storage
            assets = await storage_service.get_story_assets(story_id)
            
            status = {
                'story_id': story_id,
                'status': 'completed' if len(assets) >= 13 else 'in_progress',  # 6 images + 6 music + 6 tts + 1 final audio
                'assets_count': len(assets),
                'assets': assets
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Failed to get story status for {story_id}: {e}")
            return {
                'story_id': story_id,
                'status': 'error',
                'error': str(e)
            }


# Global story service instance
story_service = StoryService()
