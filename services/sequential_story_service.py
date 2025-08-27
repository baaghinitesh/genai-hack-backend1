"""
Sequential story generation service for reliable panel-by-panel content creation.
This replaces the streaming approach to ensure complete, high-quality content.
"""

import asyncio
import random
from typing import List, Dict, Any, Optional
from loguru import logger
from models.schemas import StoryInputs, StoryGenerationResponse
from services.story_service import story_service
from services.panel_processor import panel_processor
from utils.retry_helpers import exponential_backoff_async
from utils.helpers import create_user_context


class SequentialStoryService:
    """
    Generate story panels sequentially for reliable, complete content.
    """
    
    def __init__(self):
        self.story_service = story_service
    
    async def generate_sequential_story(
        self,
        inputs: StoryInputs,
        emit_progress,
        user_age: int = 16,
        user_gender: str = "non-binary"
    ) -> StoryGenerationResponse:
        """
        Generate a complete story using sequential panel-by-panel processing.
        
        This method generates each panel's content individually to ensure
        complete, high-quality dialogue and proper TTS generation.
        
        Args:
            inputs: Story generation inputs
            emit_progress: Function to emit progress updates to clients
            user_age: User age for voice selection
            user_gender: User gender for voice selection
            
        Returns:
            StoryGenerationResponse with all panels and assets
        """
        try:
            story_id = f"story_{asyncio.get_event_loop().time():.0f}"
            # Generate random seed (1-1000) for character consistency across panels
            story_seed = random.randint(1, 1000)
            logger.info(f"Starting sequential story generation for ID: {story_id} (seed: {story_seed})")

            # Emit story generation start
            await emit_progress(
                event_type='story_generation_start',
                data={
                    'story_id': story_id,
                    'user_inputs': inputs.dict()
                }
            )

            # Step 1: Generate the basic story structure first
            logger.info("Generating story structure...")
            basic_panels = await self._generate_story_structure(inputs)
            
            # Step 2: Generate detailed content for each panel sequentially
            processed_panels = []
            
            # Set story context for panel processor (once for all panels)
            story_context = {
                'mood': inputs.mood,
                'animeGenre': inputs.vibe,
                'archetype': inputs.archetype,
                'supportSystem': inputs.supportSystem,
                'coreValue': inputs.coreValue,
                'pastResilience': inputs.dream,
                'innerDemon': inputs.innerDemon,
                'age': inputs.age,
                'gender': inputs.gender
            }
            panel_processor.set_story_context(story_context)
            panel_processor.user_age = user_age
            panel_processor.user_gender = user_gender
            
            # Process panel 1 first to start slideshow immediately
            logger.info("Processing panel 1 to start slideshow...")
            detailed_panel_1 = await self._generate_panel_content(
                basic_panels[0], inputs, 1
            )
            
            # Process panel 1 and start slideshow
            complete_panel_1 = await panel_processor.process_panel(
                detailed_panel_1, story_id, emit_progress, story_seed
            )
            processed_panels.append(complete_panel_1)
            
            # Emit slideshow start event
            await emit_progress(
                event_type='slideshow_start',
                data={
                    'story_id': story_id,
                    'first_panel': complete_panel_1
                }
            )
            
            logger.info("Panel 1 completed - slideshow started!")
            
            # Now process remaining panels asynchronously
            async def process_remaining_panel(panel_index: int, basic_panel: dict):
                panel_number = panel_index + 1
                logger.info(f"Processing panel {panel_number}/6 asynchronously...")
                
                # Emit progress update for this panel
                await emit_progress(
                    event_type='panel_processing_start',
                    data={
                        'panel_number': panel_number,
                        'story_id': story_id,
                        'message': f'Generating panel {panel_number} of 6...'
                    }
                )
                
                # Generate detailed content for this specific panel
                detailed_panel = await self._generate_panel_content(
                    basic_panel, inputs, panel_number
                )
                
                # Process panel to generate all assets
                complete_panel = await panel_processor.process_panel(
                    detailed_panel, story_id, emit_progress, story_seed
                )
                
                # Emit panel ready event
                await emit_progress(
                    event_type='panel_ready',
                    data={
                        'panel_number': panel_number,
                        'story_id': story_id,
                        'message': f'Panel {panel_number} is ready!'
                    }
                )
                
                logger.info(f"Panel {panel_number} completed asynchronously")
                return complete_panel
            
            # Start async processing for panels 2-6 with staggered delays to avoid rate limits
            remaining_tasks = []
            for i, basic_panel in enumerate(basic_panels[1:], 1):
                # Stagger panel processing to avoid API rate limits
                # Panel 2: 0s delay, Panel 3: 2s delay, Panel 4: 4s delay, etc.
                delay = (i - 1) * 2  # 2 second intervals
                
                async def process_with_delay(panel_index, panel_data, delay_seconds):
                    if delay_seconds > 0:
                        logger.info(f"Waiting {delay_seconds}s before processing panel {panel_index + 2}")
                        await asyncio.sleep(delay_seconds)
                    return await process_remaining_panel(panel_index, panel_data)
                
                task = process_with_delay(i, basic_panel, delay)
                remaining_tasks.append(task)
            
            # Wait for all remaining panels to complete
            remaining_panels = await asyncio.gather(*remaining_tasks, return_exceptions=True)
            
            # Add remaining panels to processed list
            for i, result in enumerate(remaining_panels):
                if isinstance(result, Exception):
                    logger.error(f"Panel {i+2} failed: {result}")
                    # Add fallback panel
                    processed_panels.append(self._create_fallback_panel(i+2))
                else:
                    processed_panels.append(result)

            # Convert processed panels to frontend-expected format
            frontend_panels = []
            for i, panel in enumerate(processed_panels):
                frontend_panel = {
                    'id': str(i + 1),
                    'imageUrl': panel.get('image_url', ''),
                    'narrationUrl': panel.get('tts_url', ''),
                    'backgroundMusicUrl': panel.get('music_url', ''),
                    # Include original panel data for debugging
                    'original_data': {
                        'panel_number': panel['panel_number'],
                        'dialogue_text': panel['dialogue_text'],
                        'emotional_tone': panel['emotional_tone']
                    }
                }
                frontend_panels.append(frontend_panel)

            # Create response data in frontend-expected format
            response_data = {
                'story_id': story_id,
                'panels': frontend_panels,
                'status': 'completed',
                'created_at': asyncio.get_event_loop().time(),
                'total_panels': len(processed_panels)
            }

            # Emit story generation completion
            await emit_progress(
                event_type='story_generation_complete',
                data={
                    'story_id': story_id,
                    'story': response_data,
                    'total_panels': len(processed_panels)
                }
            )

            logger.info(f"Sequential story generation completed: {story_id}")
            
            # Create proper response object
            response = StoryGenerationResponse(
                story_id=story_id,
                status="completed",
                message=f"Manga story '{inputs.mangaTitle}' generated successfully with sequential processing!",
                story=None  # All data sent via Socket.IO events
            )
            return response

        except Exception as e:
            logger.error(f"Failed to generate sequential story: {e}")

            # Emit error event
            await emit_progress(
                event_type='story_generation_error',
                data={
                    'story_id': story_id if 'story_id' in locals() else '',
                    'error': str(e)
                }
            )
            raise
    
    async def _generate_story_structure(self, inputs: StoryInputs) -> List[Dict[str, Any]]:
        """Generate the basic story structure with character sheets and basic content."""
        try:
            # Use the existing story service to generate basic structure
            panels = await self.story_service.generate_story_plan(inputs)
            logger.info(f"Generated basic structure for {len(panels)} panels")
            return panels
            
        except Exception as e:
            logger.error(f"Failed to generate story structure: {e}")
            # Return fallback structure
            return self._create_fallback_structure(inputs)
    
    async def _generate_panel_content(
        self, 
        basic_panel: Dict[str, Any], 
        inputs: StoryInputs, 
        panel_number: int
    ) -> Dict[str, Any]:
        """
        Generate detailed content for a specific panel using targeted AI prompts.
        """
        try:
            logger.info(f"Generating detailed content for panel {panel_number}")
            
            # Create a focused prompt for this specific panel
            panel_prompt = self._create_panel_specific_prompt(basic_panel, inputs, panel_number)
            
            # Generate content with exponential backoff
            response = await exponential_backoff_async(
                asyncio.to_thread,
                self.story_service.llm.invoke,
                panel_prompt,
                max_retries=3,
                initial_delay=2.0,
                max_delay=30.0
            )
            
            # Extract content from response
            if hasattr(response, 'content'):
                response_text = response.content
            else:
                response_text = str(response)
            
            # Parse the response to extract clean dialogue
            clean_dialogue = self._extract_clean_dialogue(response_text, panel_number)
            
            # Update the basic panel with detailed content
            detailed_panel = basic_panel.copy()
            detailed_panel.update({
                'dialogue_text': clean_dialogue,
                'tts_text': clean_dialogue,  # Same as dialogue for TTS
            })
            
            logger.info(f"Panel {panel_number} detailed content: {clean_dialogue[:50]}...")
            return detailed_panel
            
        except Exception as e:
            logger.error(f"Failed to generate detailed content for panel {panel_number}: {e}")
            # Return basic panel with enhanced fallback
            return self._enhance_basic_panel(basic_panel, inputs, panel_number)
    
    def _create_panel_specific_prompt(
        self, 
        basic_panel: Dict[str, Any], 
        inputs: StoryInputs, 
        panel_number: int
    ) -> str:
        """Create a focused prompt for generating content for a specific panel."""
        
        character = basic_panel.get('character_sheet', {})
        emotional_tone = basic_panel.get('emotional_tone', 'neutral')
        
        # Create standardized user context
        user_context = create_user_context(inputs)
        
        prompt = f"""
You are creating narration content for Panel {panel_number} of a 6-panel manga story.

CHARACTER: {character.get('name', inputs.nickname)} 

USER CONTEXT:
{user_context}

PANEL EMOTIONAL TONE: {emotional_tone}

STORY ARC POSITION:
{self._get_panel_arc_description(panel_number)}

CURRENT PANEL FOCUS: {basic_panel.get('dialogue_text', '')}

Create natural, flowing narration for this panel that:
1. Sounds excellent when read by text-to-speech
2. Is 25-35 words long
3. Captures the emotional tone: {emotional_tone}
4. Continues the character's journey naturally
5. Uses conversational, natural language
6. References the user's hobby ({inputs.hobby}) and dream ({inputs.dream}) when appropriate

CRITICAL TTS REQUIREMENTS:
- Do NOT start with "Panel {panel_number}:" or any numbering
- Do NOT use dashes (-), asterisks (*), or formatting symbols
- Do NOT include stage directions like [pause] or (sighs)
- Write as if speaking directly to the listener
- Use proper punctuation for natural speech flow
- Make it sound natural and engaging when spoken

Return ONLY the clean narration text, nothing else:
"""
        return prompt
    
    def _get_panel_arc_description(self, panel_number: int) -> str:
        """Get the story arc description for a specific panel."""
        arc_map = {
            1: "Introduction - Establish the character and their current state",
            2: "Challenge - Present the obstacle or difficulty they face", 
            3: "Reflection - Character processes their situation and feelings",
            4: "Discovery - Character finds inner strength or new perspective",
            5: "Transformation - Character takes positive action or grows",
            6: "Resolution - Character emerges stronger with hope for the future"
        }
        return arc_map.get(panel_number, "Story continues")
    
    def _extract_clean_dialogue(self, response_text: str, panel_number: int) -> str:
        """Extract clean dialogue from AI response, removing any formatting."""
        try:
            # Remove any panel numbering at the start
            text = response_text.strip()
            
            # Remove common prefixes
            prefixes_to_remove = [
                f"panel {panel_number}:",
                f"panel_{panel_number}:",
                "dialogue_text:",
                "narration:",
                "-",
                "*"
            ]
            
            for prefix in prefixes_to_remove:
                if text.lower().startswith(prefix):
                    text = text[len(prefix):].strip()
            
            # Remove any quotation marks at start/end
            text = text.strip('"\'')
            
            # Remove any remaining formatting
            text = text.replace('*', '').replace('-', '').replace('[', '').replace(']', '')
            
            # Ensure proper sentence structure
            if text and not text[0].isupper():
                text = text[0].upper() + text[1:]
            
            if text and not text.endswith('.'):
                text += '.'
            
            # Validate length and quality
            if len(text.split()) < 10:
                logger.warning(f"Panel {panel_number} dialogue too short, using fallback")
                return self._get_fallback_dialogue(panel_number)
            
            return text
            
        except Exception as e:
            logger.error(f"Error extracting dialogue for panel {panel_number}: {e}")
            return self._get_fallback_dialogue(panel_number)
    
    def _get_fallback_dialogue(self, panel_number: int) -> str:
        """Get high-quality fallback dialogue for a panel."""
        fallbacks = {
            1: "Every journey begins with a single step. Today feels uncertain, but there's something stirring inside, a quiet determination waiting to emerge.",
            2: "The path ahead seems challenging, filled with obstacles that feel overwhelming. Yet deep down, there's a voice whispering that this struggle has meaning.",
            3: "Taking a moment to breathe and reflect on how far the journey has already come. Even in uncertainty, there are small victories worth acknowledging.",
            4: "A spark of clarity emerges. This challenge isn't just about reaching the destination, it's about discovering the strength that was always there.",
            5: "With newfound understanding comes the courage to take action. Each step forward is a choice to believe in the possibility of growth and change.",
            6: "Looking back on this journey, it's clear how much has changed. The path continues ahead, but now it's illuminated by hope and self-belief."
        }
        return fallbacks.get(panel_number, "The journey continues with hope and determination.")
    
    def _enhance_basic_panel(
        self, 
        basic_panel: Dict[str, Any], 
        inputs: StoryInputs, 
        panel_number: int
    ) -> Dict[str, Any]:
        """Enhance a basic panel with better fallback content."""
        enhanced_dialogue = self._get_fallback_dialogue(panel_number)
        
        enhanced_panel = basic_panel.copy()
        enhanced_panel.update({
            'dialogue_text': enhanced_dialogue,
            'tts_text': enhanced_dialogue,
        })
        
        return enhanced_panel
    
    def _create_fallback_structure(self, inputs: StoryInputs) -> List[Dict[str, Any]]:
        """Create fallback structure when AI generation fails."""
        panels = []
        
        for i in range(1, 7):
            panel = {
                'panel_number': i,
                'character_sheet': {
                    'name': inputs.nickname,
                    'age': str(inputs.age),
                    'appearance': f"determined {inputs.gender} with expressive eyes",
                    'personality': 'hopeful and resilient',
                    'goals': inputs.dream,
                    'fears': f'struggles with {inputs.mood}',
                    'strengths': 'inner determination'
                },
                'prop_sheet': {
                    'items': [inputs.hobby],
                    'environment': f'{inputs.vibe} setting',
                    'lighting': 'warm and hopeful',
                    'mood_elements': ['growth', 'hope']
                },
                'style_guide': {
                    'art_style': 'modern manga style',
                    'visual_elements': ['emotional expression', 'dynamic composition'],
                    'framing': 'cinematic panel layout'
                },
                'dialogue_text': self._get_fallback_dialogue(i),
                'emotional_tone': ['neutral', 'tense', 'contemplative', 'hopeful', 'determined', 'uplifting'][i-1],
                'image_prompt': '',
                'music_prompt': '',
                'tts_text': self._get_fallback_dialogue(i)
            }
            panels.append(panel)
        
        return panels
    
    def _create_fallback_panel(self, panel_number: int) -> Dict[str, Any]:
        """Create a fallback panel when processing fails."""
        return {
            'panel_number': panel_number,
            'image_url': '',
            'tts_url': '',
            'music_url': '/src/assets/audio/background-music.mp3',
            'dialogue_text': self._get_fallback_dialogue(panel_number),
            'emotional_tone': 'neutral'
        }


# Global sequential story service instance
sequential_story_service = SequentialStoryService()
